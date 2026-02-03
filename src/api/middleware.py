"""
Middleware for rate limiting and security
"""
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from datetime import datetime, timedelta
from typing import Dict, Tuple
from collections import defaultdict
import os
import json

from src.utils.logger import get_logger
from src.database.connection import get_db_session
from src.database.crud.client_crud import get_client_by_api_key

logger = get_logger("middleware")

# In-memory rate limit storage (use Redis in production)
_rate_limit_store: Dict[str, Tuple[int, datetime]] = defaultdict(lambda: (0, datetime.now()))

# Default rate limits per plan type (requests per hour)
DEFAULT_RATE_LIMITS = {
    "free": 100,
    "basic": 500,
    "premium": 2000,
}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware based on API key"""

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)

        # Skip rate limiting for health checks and docs
        if request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)

        # Get API key from header
        api_key = request.headers.get("X-API-Key")
        
        if api_key:
            limit_per_hour = 100
            try:
                db = get_db_session()
                client = get_client_by_api_key(db, api_key)
                if client:
                    limit_per_hour = self._get_rate_limit_for_plan(client.plan_type)
            except Exception as e:
                logger.error(f"Rate limit plan lookup failed: {e}")
            finally:
                try:
                    db.close()
                except Exception:
                    pass

            allowed = self._check_rate_limit(api_key, limit_per_hour=limit_per_hour)
            if not allowed:
                logger.warning(f"Rate limit exceeded for API key: {api_key[:10]}...")
                now = datetime.now()
                count, reset_time = _rate_limit_store[api_key]
                remaining = max(int((reset_time - now).total_seconds()), 0)
                body = json.dumps({
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after_seconds": remaining,
                    "reset_at": reset_time.isoformat()
                })
                return Response(
                    content=body,
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    media_type="application/json",
                    headers={"Retry-After": str(remaining)}
                )

        response = await call_next(request)
        return response

    def _check_rate_limit(self, api_key: str, limit_per_hour: int = 100) -> bool:
        """Check if API key has exceeded rate limit"""
        now = datetime.now()
        count, reset_time = _rate_limit_store[api_key]

        # Reset counter if an hour has passed
        if now > reset_time:
            _rate_limit_store[api_key] = (1, now + timedelta(hours=1))
            return True

        # Check if limit exceeded
        if count >= limit_per_hour:
            return False

        # Increment counter
        _rate_limit_store[api_key] = (count + 1, reset_time)
        return True

    def _get_rate_limit_for_plan(self, plan_type: str) -> int:
        """Get rate limit based on plan type"""
        return DEFAULT_RATE_LIMITS.get(plan_type, 100)


def get_allowed_origins() -> list:
    """Get allowed CORS origins from environment or default"""
    origins_env = os.getenv("CORS_ORIGINS", "")
    if origins_env:
        return [origin.strip() for origin in origins_env.split(",")]
    
    # Default: allow localhost for development
    # In production, set CORS_ORIGINS environment variable
    return [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]
