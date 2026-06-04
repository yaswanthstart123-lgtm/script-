"""
SecureHub — Rate Limiter Middleware
Redis-based sliding window rate limiting per IP address.
"""

import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.config import get_settings

settings = get_settings()


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Redis-based sliding window rate limiter.
    Limits requests per IP address per minute.
    Returns 429 Too Many Requests when exceeded.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health checks
        if request.url.path in ("/api/health", "/docs", "/openapi.json", "/redoc"):
            return await call_next(request)

        try:
            from app.redis_client import get_redis
            redis = get_redis()

            if redis is None:
                # If Redis is unavailable, allow the request through
                return await call_next(request)

            # Get client IP
            client_ip = request.client.host if request.client else "unknown"

            # Stricter limit for auth endpoints
            if request.url.path.startswith("/api/auth/"):
                limit = 20  # 20 requests per minute for auth
                window = 60
            else:
                limit = settings.RATE_LIMIT_PER_MINUTE
                window = 60

            # Sliding window key
            key = f"rate_limit:{client_ip}:{request.url.path}"
            now = time.time()

            # Use Redis pipeline for atomic operations
            pipe = redis.pipeline()

            # Remove old entries outside the window
            pipe.zremrangebyscore(key, 0, now - window)

            # Count current requests in window
            pipe.zcard(key)

            # Add current request
            pipe.zadd(key, {str(now): now})

            # Set expiry on the key
            pipe.expire(key, window)

            results = await pipe.execute()
            request_count = results[1]

            if request_count >= limit:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Too many requests. Please slow down.",
                        "retry_after": window,
                    },
                    headers={
                        "Retry-After": str(window),
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                    },
                )

            # Process the request
            response = await call_next(request)

            # Add rate limit headers
            remaining = max(0, limit - request_count - 1)
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)

            return response

        except Exception:
            # If rate limiting fails, allow the request through
            return await call_next(request)
