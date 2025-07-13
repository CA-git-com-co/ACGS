"""
Security Headers Middleware for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Adds comprehensive security headers to all responses.
"""

from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers to all responses."""

    def __init__(self, app, constitutional_hash: str = CONSTITUTIONAL_HASH):
        super().__init__(app)
        self.constitutional_hash = constitutional_hash

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)

        # Security headers
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "X-Constitutional-Hash": self.constitutional_hash,
        }

        for header, value in security_headers.items():
            response.headers[header] = value

        return response
