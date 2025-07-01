"""
Security middleware for DGM Service.
"""

import logging
import time
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class SecurityMiddleware(BaseHTTPMiddleware):
    """Security middleware for adding security headers and protections."""

    def __init__(self, app):
        super().__init__(app)
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; "
                "connect-src 'self'; "
                "font-src 'self'; "
                "object-src 'none'; "
                "media-src 'self'; "
                "frame-src 'none';"
            ),
            "Permissions-Policy": (
                "geolocation=(), "
                "microphone=(), "
                "camera=(), "
                "payment=(), "
                "usb=(), "
                "magnetometer=(), "
                "gyroscope=(), "
                "speaker=()"
            ),
        }

    async def dispatch(self, request: Request, call_next):
        """Process request with security enhancements."""
        start_time = time.time()

        # Log security-relevant request information
        self._log_security_info(request)

        # Check for suspicious patterns
        if self._is_suspicious_request(request):
            logger.warning(f"Suspicious request detected: {request.url}")
            return Response(
                content='{"error": "Request blocked for security reasons"}',
                status_code=403,
                headers={"Content-Type": "application/json"},
            )

        # Process request
        response = await call_next(request)

        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value

        # Add custom security headers
        response.headers["X-Service-Name"] = "dgm-service"
        response.headers["X-Response-Time"] = str(
            round((time.time() - start_time) * 1000, 2)
        )

        # Remove sensitive headers that might leak information
        sensitive_headers = [
            "Server",
            "X-Powered-By",
            "X-AspNet-Version",
            "X-AspNetMvc-Version",
        ]

        for header in sensitive_headers:
            if header in response.headers:
                del response.headers[header]

        return response

    def _log_security_info(self, request: Request):
        """Log security-relevant request information."""
        security_info = {
            "method": request.method,
            "path": request.url.path,
            "user_agent": request.headers.get("User-Agent", ""),
            "x_forwarded_for": request.headers.get("X-Forwarded-For", ""),
            "x_real_ip": request.headers.get("X-Real-IP", ""),
            "referer": request.headers.get("Referer", ""),
            "content_type": request.headers.get("Content-Type", ""),
            "content_length": request.headers.get("Content-Length", "0"),
        }

        # Log suspicious patterns
        if self._has_suspicious_patterns(security_info):
            logger.warning(f"Request with suspicious patterns: {security_info}")

    def _is_suspicious_request(self, request: Request) -> bool:
        """Check if request has suspicious characteristics."""
        # Check for common attack patterns in URL
        suspicious_patterns = [
            "../",
            "..\\",
            "<script",
            "javascript:",
            "vbscript:",
            "onload=",
            "onerror=",
            "eval(",
            "exec(",
            "union select",
            "drop table",
            "insert into",
            "delete from",
            "update set",
        ]

        url_path = request.url.path.lower()
        query_string = str(request.url.query).lower()

        for pattern in suspicious_patterns:
            if pattern in url_path or pattern in query_string:
                return True

        # Check for suspicious headers
        user_agent = request.headers.get("User-Agent", "").lower()
        suspicious_user_agents = [
            "sqlmap",
            "nikto",
            "nessus",
            "openvas",
            "nmap",
            "masscan",
            "zap",
            "burp",
        ]

        for suspicious_ua in suspicious_user_agents:
            if suspicious_ua in user_agent:
                return True

        # Check for excessive header count (potential header injection)
        if len(request.headers) > 50:
            return True

        # Check for suspicious content length
        content_length = request.headers.get("Content-Length")
        if content_length and int(content_length) > 10 * 1024 * 1024:  # 10MB
            return True

        return False

    def _has_suspicious_patterns(self, security_info: dict[str, Any]) -> bool:
        """Check if security info contains suspicious patterns."""
        # Check for empty or missing User-Agent
        if not security_info.get("user_agent"):
            return True

        # Check for suspicious referers
        referer = security_info.get("referer", "").lower()
        if referer and any(
            domain in referer for domain in ["malware", "phishing", "spam"]
        ):
            return True

        # Check for multiple forwarded IPs (potential proxy abuse)
        x_forwarded_for = security_info.get("x_forwarded_for", "")
        if x_forwarded_for.count(",") > 5:  # More than 5 proxy hops
            return True

        return False
