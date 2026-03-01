"""Health check endpoints for monitoring and deployment readiness."""

import redis.asyncio as aioredis
import structlog
from fastapi import APIRouter
from sqlalchemy import text

from app.config import settings
from app.database import engine

logger = structlog.get_logger()

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check() -> dict:
    """Basic liveness check — always returns OK if the app is running."""
    return {"status": "ok", "service": settings.app_name}


@router.get("/health/ready")
async def readiness_check() -> dict:
    """Readiness check — verifies database and Redis connectivity."""
    checks: dict[str, str] = {}

    # Database check
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        logger.warning("health_db_failed", error=str(exc))
        checks["database"] = "unavailable"

    # Redis check
    try:
        client = aioredis.from_url(settings.redis_url, decode_responses=True)
        await client.ping()
        await client.aclose()
        checks["redis"] = "ok"
    except Exception as exc:
        logger.warning("health_redis_failed", error=str(exc))
        checks["redis"] = "unavailable"

    all_ok = all(v == "ok" for v in checks.values())
    return {"status": "ok" if all_ok else "degraded", "checks": checks}
