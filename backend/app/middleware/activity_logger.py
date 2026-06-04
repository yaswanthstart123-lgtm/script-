"""
SecureHub — Activity Logger Middleware
Logs every API request to MongoDB for security auditing.
"""

import time
from datetime import datetime, timezone

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.utils.jwt_handler import decode_access_token


class ActivityLoggerMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs all API requests to MongoDB.
    Captures: method, path, IP, user agent, user ID, status code, duration.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()

        # Process the request
        response = await call_next(request)

        # Calculate duration
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Extract user ID from JWT (if present)
        user_id = None
        auth_header = request.headers.get("authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = decode_access_token(token)
            if payload:
                user_id = payload.get("sub")

        # Build log entry
        log_entry = {
            "timestamp": datetime.now(timezone.utc),
            "method": request.method,
            "path": str(request.url.path),
            "query_params": str(request.query_params) if request.query_params else None,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "user_id": user_id,
            "content_type": request.headers.get("content-type"),
        }

        # Log to MongoDB (non-blocking, fire-and-forget)
        try:
            from app.mongodb import get_mongo_db
            mongo_db = get_mongo_db()
            if mongo_db is not None:
                await mongo_db.activity_logs.insert_one(log_entry)
        except Exception:
            # Don't let logging failures break the request
            pass

        return response
