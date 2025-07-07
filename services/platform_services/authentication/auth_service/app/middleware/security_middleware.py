"""
Enhanced Security Middleware for ACGS Auth Service

Provides comprehensive security controls including rate limiting,
input validation, security headers, and attack prevention.
"""

import ipaddress
import json
import logging
import time
from collections import defaultdict, deque
from typing import Any, Dict, Optional

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from ..core.input_validation import InputValidator, log_security_event

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = logging.getLogger(__name__)


class RateLimiter:
    """Rate limiting implementation with sliding window."""

    def __init__(self):
        self.requests = defaultdict(deque)
        self.blocked_ips = {}

    def is_allowed(
        self, client_ip: str, endpoint: str, limit: int, window: int
    ) -> bool:
        """Check if request is allowed based on rate limits."""
        now = time.time()
        key = f"{client_ip}:{endpoint}"

        # Clean old requests
        while self.requests[key] and self.requests[key][0] < now - window:
            self.requests[key].popleft()

        # Check if blocked
        if client_ip in self.blocked_ips:
            if now < self.blocked_ips[client_ip]:
                return False
            else:
                del self.blocked_ips[client_ip]

        # Check rate limit
        if len(self.requests[key]) >= limit:
            # Block IP for 5 minutes on rate limit violation
            self.blocked_ips[client_ip] = now + 300
            log_security_event(
                "rate_limit_exceeded",
                {
                    "client_ip": client_ip,
                    "endpoint": endpoint,
                    "requests_count": len(self.requests[key]),
                },
                client_ip,
            )
            return False

        # Add current request
        self.requests[key].append(now)
        return True


class SecurityMiddleware(BaseHTTPMiddleware):
    """Comprehensive security middleware for Auth service."""

    def __init__(self, app, config: Optional[Dict[str, Any]] = None):
        super().__init__(app)
        self.config = config or {}
        self.rate_limiter = RateLimiter()

        # Security configuration
        self.rate_limits = {
            "/api/v1/auth/login": {
                "limit": 5,
                "window": 300,
            },  # 5 requests per 5 minutes
            "/api/v1/auth/token": {"limit": 5, "window": 300},
            "/api/v1/auth/validate": {"limit": 100, "window": 60},  # 100 per minute
            "/api/v1/auth/refresh": {"limit": 10, "window": 300},
            "default": {"limit": 20, "window": 60},
        }

        # Blocked IP ranges (example)
        self.blocked_networks = [
            # Add known malicious IP ranges here
        ]

    async def dispatch(self, request: Request, call_next):
        """Process request through security middleware."""
        start_time = time.time()
        client_ip = self._get_client_ip(request)

        try:
            # 1. IP blocking check
            if self._is_ip_blocked(client_ip):
                log_security_event(
                    "blocked_ip_access",
                    {"client_ip": client_ip, "path": request.url.path},
                    client_ip,
                )
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"error": "Access denied"},
                )

            # 2. Rate limiting
            endpoint = request.url.path
            rate_config = self.rate_limits.get(endpoint, self.rate_limits["default"])

            if not self.rate_limiter.is_allowed(
                client_ip, endpoint, rate_config["limit"], rate_config["window"]
            ):
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "error": "Rate limit exceeded",
                        "retry_after": rate_config["window"],
                    },
                )

            # 3. Request size validation
            if hasattr(request, "headers"):
                content_length = request.headers.get("content-length")
                if content_length and int(content_length) > 1024 * 1024:  # 1MB limit
                    log_security_event(
                        "large_request",
                        {"client_ip": client_ip, "content_length": content_length},
                        client_ip,
                    )
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={"error": "Request too large"},
                    )

            # 4. Input validation for POST requests
            if request.method == "POST" and endpoint in [
                "/api/v1/auth/login",
                "/api/v1/auth/token",
            ]:
                await self._validate_login_request(request, client_ip)

            # Process request
            response = await call_next(request)

            # 5. Add security headers
            self._add_security_headers(response)

            # 6. Log successful request
            process_time = time.time() - start_time
            if process_time > 5.0:  # Log slow requests
                log_security_event(
                    "slow_request",
                    {
                        "client_ip": client_ip,
                        "path": endpoint,
                        "process_time": process_time,
                    },
                    client_ip,
                )

            return response

        except HTTPException:
            raise
        except Exception as e:
            log_security_event(
                "middleware_error",
                {"client_ip": client_ip, "error": str(e), "path": request.url.path},
                client_ip,
            )
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"error": "Internal server error"},
            )

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip

        # Fallback to direct connection
        if hasattr(request, "client") and request.client:
            return request.client.host

        return "unknown"

    def _is_ip_blocked(self, client_ip: str) -> bool:
        """Check if IP address is in blocked networks."""
        if client_ip == "unknown":
            return False

        try:
            ip = ipaddress.ip_address(client_ip)
            for network in self.blocked_networks:
                if ip in ipaddress.ip_network(network):
                    return True
        except ValueError:
            # Invalid IP format
            return True

        return False

    async def _validate_login_request(self, request: Request, client_ip: str):
        """Validate login request data."""
        try:
            # Read request body
            body = await request.body()
            if not body:
                return

            # Parse JSON if content-type is application/json
            content_type = request.headers.get("content-type", "")
            if "application/json" in content_type:
                try:
                    data = json.loads(body)

                    # Validate username
                    if "username" in data:
                        InputValidator.validate_username(data["username"])

                    # Validate password (basic check, not full validation)
                    if "password" in data and len(data["password"]) > 128:
                        raise ValueError("Password too long")

                except json.JSONDecodeError:
                    log_security_event(
                        "invalid_json",
                        {"client_ip": client_ip, "path": request.url.path},
                        client_ip,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid JSON format",
                    )
                except ValueError as e:
                    log_security_event(
                        "input_validation_failed",
                        {"client_ip": client_ip, "error": str(e)},
                        client_ip,
                    )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                    )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating login request: {e}")

    def _add_security_headers(self, response: Response):
        """Add security headers to response."""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }

        for header, value in security_headers.items():
            response.headers[header] = value
