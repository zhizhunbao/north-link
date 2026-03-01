"""Scraper result cache using Redis - BE-008."""

import hashlib
import json
import logging

import redis.asyncio as redis

from app.config import settings

logger = logging.getLogger(__name__)

# Cache TTL in seconds (default 1 hour)
CACHE_TTL = 3600


def _cache_key(platform: str, keywords: str) -> str:
    """Build a deterministic cache key from platform + keywords."""
    keywords_hash = hashlib.md5(keywords.lower().strip().encode()).hexdigest()
    return f"scraper:cache:{platform}:{keywords_hash}"


async def _get_redis() -> redis.Redis:
    """Get an async Redis client."""
    return redis.from_url(settings.redis_url, decode_responses=True)


async def get_cached_result(
    platform: str, keywords: str
) -> list[dict] | None:
    """Look up cached scraper results. Returns None on cache miss."""
    try:
        r = await _get_redis()
        key = _cache_key(platform, keywords)
        cached = await r.get(key)
        await r.aclose()
        if cached:
            return json.loads(cached)
    except Exception:
        logger.debug("Cache lookup failed for %s:%s", platform, keywords)
    return None


async def set_cached_result(
    platform: str, keywords: str, data: list[dict]
) -> None:
    """Store scraper results in cache with TTL."""
    try:
        r = await _get_redis()
        key = _cache_key(platform, keywords)
        await r.setex(key, CACHE_TTL, json.dumps(data, default=str))
        await r.aclose()
    except Exception:
        logger.debug("Cache write failed for %s:%s", platform, keywords)
