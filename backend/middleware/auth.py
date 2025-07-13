"""
Authentication Middleware

Middleware for handling authentication in the Amauta system.
"""

import logging
import jwt
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from backend.config import settings

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for the Amauta system"""

    async def dispatch(self, request: Request, call_next):
        """Process the request through authentication middleware"""

        # Skip authentication for certain endpoints
        if self._should_skip_auth(request.url.path):
            return await call_next(request)

        # TODO: Implement actual authentication logic
        # For now, just log the request
        logger.info(f"Processing request: {request.method} {request.url.path}")

        # Continue with the request
        response = await call_next(request)
        return response

    def _should_skip_auth(self, path: str) -> bool:
        """Check if authentication should be skipped for this path"""
        skip_paths = ["/", "/health", "/docs", "/openapi.json", "/auth/login"]
        return any(path.startswith(skip_path) for skip_path in skip_paths)
