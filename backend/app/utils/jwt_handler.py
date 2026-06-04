"""
SecureHub — JWT Token Handler
Token creation, verification, and blacklisting.
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.config import get_settings
from app.redis_client import get_redis

settings = get_settings()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Payload data (must include 'sub' for user ID)
        expires_delta: Optional custom expiry duration

    Returns:
        Encoded JWT string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "access",
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict | None:
    """
    Decode and verify a JWT access token.

    Args:
        token: The JWT string to decode

    Returns:
        Decoded payload dict, or None if invalid/expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        return payload
    except JWTError:
        return None


async def blacklist_token(token: str, expires_in: int | None = None) -> None:
    """
    Add a token to the Redis blacklist (for logout).

    Args:
        token: The JWT token to blacklist
        expires_in: TTL in seconds (defaults to token expiry time)
    """
    redis = get_redis()
    if redis is None:
        return

    if expires_in is None:
        expires_in = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60

    await redis.setex(
        f"blacklist:{token}",
        expires_in,
        "1",
    )


async def is_token_blacklisted(token: str) -> bool:
    """Check if a token has been blacklisted (logged out)."""
    redis = get_redis()
    if redis is None:
        return False

    result = await redis.get(f"blacklist:{token}")
    return result is not None
