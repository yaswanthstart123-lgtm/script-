"""
SecureHub — Redis Connection
Used for caching, rate limiting, and JWT token blacklisting.
"""

import redis.asyncio as aioredis

from app.config import get_settings

settings = get_settings()

# ── Redis Client ─────────────────────────────────
redis_client: aioredis.Redis = None


async def connect_redis():
    """Initialize Redis connection pool on app startup."""
    global redis_client
    redis_client = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        max_connections=20,
    )
    # Verify connection
    await redis_client.ping()


async def close_redis():
    """Close Redis connection on app shutdown."""
    global redis_client
    if redis_client:
        await redis_client.close()


def get_redis() -> aioredis.Redis:
    """Get the Redis client instance."""
    return redis_client
