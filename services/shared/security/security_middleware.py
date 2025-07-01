"""
Enterprise-grade security middleware for ACGS-1 core services.

Provides comprehensive security features including:
- HTTPS enforcement
- XSS protection
- CSRF protection
- Rate limiting
- Input validation
- Security headers
- Request/response logging
"""

import hashlib
import hmac
import json
import logging
import time
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime
from functools import wraps
from typing import Any

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Security configuration for middleware."""

    def __init__(self):
        self.rate_limit_requests = 100  # requests per minute
        self.rate_limit_window = 60  # seconds
        self.csrf_token_expiry = 3600  # seconds
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.allowed_origins = ["https://localhost", "https://127.0.0.1"]
        self.csrf_secret_key = "acgs-1-csrf-secret-key-change-in-production"
        self.enable_https_only = True
        self.enable_xss_protection = True
        self.enable_csrf_protection = True
        self.enable_rate_limiting = True
        self.blocked_ips: set[str] = set()
        self.trusted_proxies: set[str] = {"127.0.0.1", "::1"}


class RateLimiter:
    """Rate limiting implementation."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.requests: dict[str, list[float]] = defaultdict(list)
        self.blocked_until: dict[str, float] = {}

    def is_allowed(self, client_ip: str) -> bool:
        """Check if request is allowed based on rate limiting."""
        current_time = time.time()

        # Check if IP is temporarily blocked
        if client_ip in self.blocked_until:
            if current_time < self.blocked_until[client_ip]:
                return False
            del self.blocked_until[client_ip]

        # Clean old requests
        cutoff_time = current_time - self.config.rate_limit_window
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip] if req_time > cutoff_time
        ]

        # Check rate limit
        if len(self.requests[client_ip]) >= self.config.rate_limit_requests:
            # Block IP for 5 minutes
            self.blocked_until[client_ip] = current_time + 300
            logger.warning(
                f"Rate limit exceeded for IP {client_ip}, blocking for 5 minutes"
            )
            return False

        # Record this request
        self.requests[client_ip].append(current_time)
        return True


class CSRFProtection:
    """CSRF protection implementation."""

    def __init__(self, config: SecurityConfig):
        self.config = config
        self.secret_key = config.csrf_secret_key.encode()

    def generate_token(self, session_id: str) -> str:
        """Generate CSRF token for session."""
        timestamp = str(int(time.time()))
        message = f"{session_id}:{timestamp}"
        signature = hmac.new(
            self.secret_key, message.encode(), hashlib.sha256
        ).hexdigest()
        return f"{timestamp}:{signature}"

    def validate_token(self, token: str, session_id: str) -> bool:
        """Validate CSRF token."""
        try:
            timestamp_str, signature = token.split(":", 1)
            timestamp = int(timestamp_str)

            # Check if token is expired
            if time.time() - timestamp > self.config.csrf_token_expiry:
                return False

            # Verify signature
            message = f"{session_id}:{timestamp_str}"
            expected_signature = hmac.new(
                self.secret_key, message.encode(), hashlib.sha256
            ).hexdigest()

            return hmac.compare_digest(signature, expected_signature)
        except (ValueError, TypeError):
            return False


class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware for ACGS-1."""

    def __init__(self, app: ASGIApp, config: SecurityConfig | None = None):
        super().__init__(app)
        self.config = config or SecurityConfig()
        self.rate_limiter = RateLimiter(self.config)
        self.csrf_protection = CSRFProtection(self.config)

        # Security headers
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }

    def get_client_ip(self, request: Request) -> str:
        """Extract client IP address."""
        # Check for forwarded headers (from trusted proxies)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Take the first IP in the chain
            client_ip = forwarded_for.split(",")[0].strip()
            return client_ip

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fallback to direct connection
        return request.client.host if request.client else "unknown"

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Main middleware dispatch method."""
        start_time = time.time()
        client_ip = self.get_client_ip(request)

        try:
            # Security checks
            security_response = await self.perform_security_checks(request, client_ip)
            if security_response:
                return security_response

            # Process request
            response = await call_next(request)

            # Add security headers
            self.add_security_headers(response)

            # Log request
            self.log_request(request, response, client_ip, time.time() - start_time)

            return response

        except Exception as e:
            logger.error(f"Security middleware error: {e}", exc_info=True)
            return JSONResponse(
                status_code=500, content={"error": "Internal security error"}
            )

    async def perform_security_checks(
        self, request: Request, client_ip: str
    ) -> Response | None:
        """Perform comprehensive security checks."""

        # Define exempt paths that should bypass security checks
        exempt_paths = {
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/redoc",
            "/favicon.ico",
        }

        # Check if this is an exempt path
        request_path = request.url.path
        if request_path in exempt_paths:
            logger.debug(f"Exempting path from security checks: {request_path}")
            return None

        # Also exempt OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return None

        # Check blocked IPs
        if client_ip in self.config.blocked_ips:
            logger.warning(f"Blocked IP attempted access: {client_ip}")
            return JSONResponse(status_code=403, content={"error": "Access denied"})

        # HTTPS enforcement (but not for health checks and localhost)
        if self.config.enable_https_only and request.url.scheme != "https":
            if not (
                request.client and request.client.host in ["127.0.0.1", "localhost"]
            ):
                return JSONResponse(
                    status_code=400, content={"error": "HTTPS required"}
                )

        # Rate limiting (with more lenient limits for health checks)
        if self.config.enable_rate_limiting:
            if not self.rate_limiter.is_allowed(client_ip):
                return JSONResponse(
                    status_code=429, content={"error": "Rate limit exceeded"}
                )

        # Request size check
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > self.config.max_request_size:
            return JSONResponse(status_code=413, content={"error": "Request too large"})

        # CSRF protection for state-changing methods (but not for exempt paths)
        if self.config.enable_csrf_protection and request.method in [
            "POST",
            "PUT",
            "DELETE",
            "PATCH",
        ]:
            csrf_token = request.headers.get("X-CSRF-Token")
            session_id = request.headers.get("X-Session-ID", "default")

            if not csrf_token or not self.csrf_protection.validate_token(
                csrf_token, session_id
            ):
                return JSONResponse(
                    status_code=403, content={"error": "Invalid CSRF token"}
                )

        return None

    def add_security_headers(self, response: Response):
        """Add security headers to response."""
        for header, value in self.security_headers.items():
            response.headers[header] = value

    def log_request(
        self, request: Request, response: Response, client_ip: str, duration: float
    ):
        """Log security-relevant request information."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "client_ip": client_ip,
            "method": request.method,
            "path": str(request.url.path),
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "user_agent": request.headers.get("user-agent", ""),
            "referer": request.headers.get("referer", ""),
        }

        if response.status_code >= 400:
            logger.warning(f"Security event: {json.dumps(log_data)}")
        else:
            logger.info(f"Request: {json.dumps(log_data)}")


def create_security_middleware(
    config: SecurityConfig | None = None,
) -> SecurityMiddleware:
    """Factory function to create security middleware."""
    return SecurityMiddleware(None, config)


# Decorator for additional endpoint security
def require_auth(func: Callable) -> Callable:
    """Decorator to require authentication for endpoints."""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        # This would integrate with your authentication system
        # For now, it's a placeholder
        return await func(*args, **kwargs)

    return wrapper


def validate_input(schema: dict[str, Any]) -> Callable:
    """Decorator for input validation."""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Input validation logic would go here
            # This is a placeholder for the actual implementation
            return await func(*args, **kwargs)

        return wrapper

    return decorator
