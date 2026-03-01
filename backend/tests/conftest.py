"""Pytest configuration and shared fixtures.

Architecture:
- Unit tests  → mock_db fixture (no real DB needed)
- Integration tests → async_client fixture (real DB on port 5433)
"""

import os

# ── Environment must be set BEFORE any app imports ─────────────────────────
os.environ.setdefault("APP_ENV", "testing")
os.environ.setdefault("JWT_SECRET", "test-secret-key-for-testing-only")
os.environ.setdefault("ENCRYPTION_KEY", "test-encryption-key-32bytes!!xx")
os.environ.setdefault(
    "DATABASE_URL",
    "postgresql+asyncpg://northlink:northlink@localhost:5433/northlink_test",
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from unittest.mock import AsyncMock, MagicMock

# Import ALL models so SQLAlchemy mapper registry is fully initialized.
import app.modules.auth.models  # noqa: F401
import app.modules.price.models  # noqa: F401
import app.modules.merchant.models  # noqa: F401
import app.modules.order.models  # noqa: F401
import app.modules.logistics.models  # noqa: F401
import app.modules.profit.models  # noqa: F401
import app.modules.settings.models  # noqa: F401

from app.database import Base, get_db
from app.main import app as fastapi_app

TEST_DATABASE_URL = os.environ["DATABASE_URL"]


# ════════════════════════════════════════════════════════════════════════════
# UNIT TEST FIXTURE — no real DB
# ════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def mock_db():
    """Mock async database session for unit tests."""
    db = AsyncMock()
    db.add = MagicMock()
    db.delete = MagicMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.flush = AsyncMock()
    db.rollback = AsyncMock()
    return db


# ════════════════════════════════════════════════════════════════════════════
# INTEGRATION TEST FIXTURES — real DB (db-test container on port 5433)
# ════════════════════════════════════════════════════════════════════════════

@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Per-test transactional session that rolls back after each test."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create schema on first use
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Each test gets a connection + savepoint for isolation
    connection = await engine.connect()
    await connection.begin()

    session_factory = async_sessionmaker(
        bind=connection,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    session = session_factory()

    yield session

    await session.close()
    await connection.rollback()
    await connection.close()
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def async_client(db_session):
    """HTTP test client — DB dependency overridden with the test session."""
    async def override_get_db():
        yield db_session

    fastapi_app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    fastapi_app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def auth_headers(async_client, db_session):
    """Create a test user directly in test DB, then login via HTTP."""
    from app.modules.auth.models import User
    from app.modules.auth.service import AuthService

    # Insert user directly — avoids needing a /register endpoint
    test_user = User(
        username="testuser",
        password_hash=AuthService.hash_password("Test1234!"),
        role="admin",
        is_active=True,
    )
    db_session.add(test_user)
    await db_session.flush()

    # Login via HTTP using the same async_client (which shares db_session)
    resp = await async_client.post("/api/v1/auth/login", json={
        "username": "testuser",
        "password": "Test1234!",
    })
    data = resp.json()
    token = data.get("access_token") or data.get("data", {}).get("access_token", "")
    return {"Authorization": f"Bearer {token}"}

