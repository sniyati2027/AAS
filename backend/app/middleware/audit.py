import time
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.database import get_db
from app.core.dependencies import get_optional_user
from app.services.audit import audit


class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically log all HTTP requests."""

    EXCLUDED_PATHS = {"/health", "/docs", "/redoc", "/openapi.json"}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip audit logging for excluded paths
        if request.url.path in self.EXCLUDED_PATHS:
            return await call_next(request)

        start_time = time.time()

        # Try to get current user (may be None for public endpoints)
        user = None
        try:
            async for db in get_db():
                user = await get_optional_user(None, db)
                break
        except Exception:
            pass

        # Process request
        response = await call_next(request)
        
        duration_ms = (time.time() - start_time) * 1000

        # Log the request (fire and forget - don't block response)
        try:
            async for db in get_db():
                await audit.log_request(
                    db=db,
                    user=user,
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    ip_address=request.client.host if request.client else None,
                    duration_ms=duration_ms,
                )
                break
        except Exception as e:
            # Don't fail request if audit logging fails
            print(f"Audit logging failed: {e}")

        return response
