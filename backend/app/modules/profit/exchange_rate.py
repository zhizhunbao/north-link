"""Exchange rate service with Redis cache (TTL 4h) — PROFIT-001."""

import structlog
from sqlalchemy.ext.asyncio import AsyncSession


logger = structlog.get_logger()

# Redis TTL for exchange rate cache: 4 hours
CACHE_TTL_SECONDS = 4 * 60 * 60

# Fallback rate if API and Redis both fail (manually updated)
FALLBACK_RATE_CAD_TO_CNY = 5.20


async def get_exchange_rate(
    db: AsyncSession,
    from_currency: str = "CAD",
    to_currency: str = "CNY",
) -> float:
    """Get the current exchange rate. Priority: Redis → API → DB fallback.

    For MVP, we use a hardcoded fallback since Redis is not mandatory.
    Future: integrate with ExchangeRate-API.com and Redis caching.
    """
    # TODO: Integrate Redis cache lookup in production
    # TODO: Integrate ExchangeRate-API.com for live rates

    # For MVP: use the fallback rate directly
    logger.info(
        "exchange_rate_lookup",
        from_currency=from_currency,
        to_currency=to_currency,
        rate=FALLBACK_RATE_CAD_TO_CNY,
        source="fallback",
    )
    return FALLBACK_RATE_CAD_TO_CNY
