"""Seed script — create initial admin user.

Usage:
    uv run python -m app.seed
"""

import asyncio

from sqlalchemy import select

from app.database import async_session_factory, engine, Base

# Import ALL model modules so Base.metadata knows about every table
from app.modules.auth.models import User  # noqa: F401
from app.modules.logistics.models import FreightAgent, FreightQuote, Shipment, TrackingEvent  # noqa: F401
from app.modules.merchant.models import Merchant, MerchantCategory, MerchantQuote  # noqa: F401
from app.modules.order.models import Order  # noqa: F401
from app.modules.price.models import Category, Product, PriceRecord, ProductFavorite  # noqa: F401
from app.modules.profit.models import ExchangeRate  # noqa: F401
from app.modules.settings.models import Setting  # noqa: F401

from app.modules.auth.service import AuthService

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "123123"


async def seed() -> None:
    """Create the default admin user if it doesn't exist."""
    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as session:
        result = await session.execute(
            select(User).where(User.username == ADMIN_USERNAME)
        )
        existing = result.scalar_one_or_none()

        if existing:
            print(f"✅ Admin user '{ADMIN_USERNAME}' already exists, skipping.")
            return

        admin = User(
            username=ADMIN_USERNAME,
            password_hash=AuthService.hash_password(ADMIN_PASSWORD),
            role="admin",
            is_active=True,
        )
        session.add(admin)
        await session.commit()
        print(f"✅ Admin user created: {ADMIN_USERNAME} / {ADMIN_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(seed())
