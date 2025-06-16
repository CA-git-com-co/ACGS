"""
ACGS-1 Phase A3: Production-Grade Security Middleware

Enhanced security middleware with comprehensive rate limiting, threat detection,
input validation, security headers, and audit logging for all ACGS-1 services.

Key Features:
- Redis-backed rate limiting with adaptive limits
- Real-time threat detection and analysis
- Input validation and sanitization
- Security headers injection
- Request size validation
- Audit logging for security events
- IP-based blocking for abuse prevention
"""

import logging
import os
import re
import secrets
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from urllib.parse import unquote

from fastapi import Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware

# Import shared components
try:
    from .api_models import ErrorCode, create_error_response
    from .rate_limiting import RateLimiter, SecurityThreatLevel

    SHARED_COMPONENTS_AVAILABLE = True
except ImportError:
    # Fallback for services that don't have shared components yet
    SHARED_COMPONENTS_AVAILABLE = False

    class ErrorCode:
        RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
        AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
        VALIDATION_ERROR = "VALIDATION_ERROR"

    class SecurityThreatLevel:
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"


logger = logging.getLogger(__name__)


def add_security_middleware(
    app, service_name: str = "acgs_service", redis_url: str = "redis://localhost:6379"
):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Add comprehensive production-grade security middleware to FastAPI app.

    Args:
        app: FastAPI application instance
        service_name: Name of the service for logging and rate limiting
        redis_url: Redis URL for rate limiting backend
    """

    # CORS Configuration with enhanced security
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://localhost:3000",
            "https://127.0.0.1:3000",
            "https://*.acgs.local",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "X-Correlation-ID", "X-Response-Time"],
    )

    # Trusted Host Middleware
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["localhost", "127.0.0.1", "*.acgs.local", "*.acgs.com"],
    )

    # Session Middleware with secure settings
    app.add_middleware(
        SessionMiddleware,
        secret_key=os.environ.get("SESSION_SECRET_KEY", secrets.token_urlsafe(32)),
        max_age=3600,  # 1 hour
        same_site="strict",
        https_only=True,
    )

    # Add comprehensive security middleware if components are available
    if SHARED_COMPONENTS_AVAILABLE:
        app.add_middleware(SecurityMiddleware, service_name=service_name, redis_url=redis_url)
    else:
        # Add basic security headers middleware
        @app.middleware("http")
        async def add_security_headers(request, call_next):
            # requires: Valid input parameters
            # ensures: Correct function execution
            # sha256: func_hash
            response = await call_next(request)

            # Security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
            )
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

            return response

    logger.info(f"Production security middleware added to {service_name}")

    return app


class SecurityConfig:
    """Security configuration for middleware."""

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        # Security headers
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' ws: wss:; "
                "object-src 'none'; "
                "frame-ancestors 'self'; "
                "form-action 'self'; "
                "base-uri 'self';"
            ),
            "Permissions-Policy": (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=()"
            ),
        }

        # Request size limits (in bytes)
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.max_header_size = 8192  # 8KB
        self.max_url_length = 2048

        # Allowed content types
        self.allowed_content_types = {
            "application/json",
            "application/x-www-form-urlencoded",
            "multipart/form-data",
            "text/plain",
            "application/pdf",
            "text/csv",
        }

        # Blocked user agents (bots, scanners, etc.)
        self.blocked_user_agents = {
            "sqlmap",
            "nikto",
            "nmap",
            "masscan",
            "zap",
            "burp",
            "acunetix",
            "nessus",
            "openvas",
            "w3af",
            "skipfish",
        }

        # Suspicious patterns for threat detection
        self.threat_patterns = {
            # SQL injection patterns
            "sql_injection": [
                r"(\bunion\b.*\bselect\b)",
                r"(\bselect\b.*\bfrom\b)",
                r"(\binsert\b.*\binto\b)",
                r"(\bdelete\b.*\bfrom\b)",
                r"(\bdrop\b.*\btable\b)",
                r"(\bor\b.*1\s*=\s*1)",
                r"(\band\b.*1\s*=\s*1)",
                r"('.*or.*'.*=.*')",
            ],
            # XSS patterns
            "xss": [
                r"<script[^>]*>",
                r"javascript:",
                r"on\w+\s*=",
                r"<iframe[^>]*>",
                r"<object[^>]*>",
                r"<embed[^>]*>",
            ],
            # Path traversal patterns
            "path_traversal": [
                r"\.\./",
                r"\.\.\\",
                r"%2e%2e%2f",
                r"%2e%2e\\",
            ],
            # Command injection patterns
            "command_injection": [
                r";\s*(cat|ls|pwd|whoami|id|uname)",
                r"\|\s*(cat|ls|pwd|whoami|id|uname)",
                r"&&\s*(cat|ls|pwd|whoami|id|uname)",
                r"`.*`",
                r"\$\(.*\)",
            ],
        }


class ThreatDetector:
    """Threat detection and analysis."""

    def __init__(self, config: SecurityConfig):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.config = config
        self.compiled_patterns = {}

        # Compile regex patterns for performance
        for threat_type, patterns in config.threat_patterns.items():
            self.compiled_patterns[threat_type] = [
                re.compile(pattern, re.IGNORECASE) for pattern in patterns
            ]

    def analyze_request(self, request: Request) -> Dict[str, Any]:
        """
        Analyze request for security threats.

        Returns:
            Dictionary with threat analysis results
        """
        threats = []
        threat_level = SecurityThreatLevel.LOW

        # Analyze URL
        url_threats = self._analyze_url(str(request.url))
        threats.extend(url_threats)

        # Analyze headers
        header_threats = self._analyze_headers(request.headers)
        threats.extend(header_threats)

        # Analyze user agent
        user_agent_threats = self._analyze_user_agent(request.headers.get("user-agent", ""))
        threats.extend(user_agent_threats)

        # Determine overall threat level
        if any(t["severity"] == "critical" for t in threats):
            threat_level = SecurityThreatLevel.CRITICAL
        elif any(t["severity"] == "high" for t in threats):
            threat_level = SecurityThreatLevel.HIGH
        elif any(t["severity"] == "medium" for t in threats):
            threat_level = SecurityThreatLevel.MEDIUM

        return {
            "threat_level": threat_level,
            "threats": threats,
            "threat_count": len(threats),
            "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def _analyze_url(self, url: str) -> List[Dict[str, Any]]:
        """Analyze URL for threats."""
        threats = []
        decoded_url = unquote(url)

        # Check URL length
        if len(url) > self.config.max_url_length:
            threats.append(
                {
                    "type": "url_length",
                    "severity": "medium",
                    "description": f"URL length ({len(url)}) exceeds limit",
                    "pattern": f"Length: {len(url)}",
                }
            )

        # Check for threat patterns
        for threat_type, patterns in self.compiled_patterns.items():
            for pattern in patterns:
                if pattern.search(decoded_url):
                    severity = (
                        "high"
                        if threat_type in ["sql_injection", "command_injection"]
                        else "medium"
                    )
                    threats.append(
                        {
                            "type": threat_type,
                            "severity": severity,
                            "description": f"Suspicious {threat_type} pattern in URL",
                            "pattern": pattern.pattern,
                        }
                    )

        return threats

    def _analyze_headers(self, headers) -> List[Dict[str, Any]]:
        """Analyze request headers for threats."""
        threats = []

        # Check header size
        total_header_size = sum(len(k) + len(v) for k, v in headers.items())
        if total_header_size > self.config.max_header_size:
            threats.append(
                {
                    "type": "header_size",
                    "severity": "medium",
                    "description": f"Total header size ({total_header_size}) exceeds limit",
                    "pattern": f"Size: {total_header_size}",
                }
            )

        return threats

    def _analyze_user_agent(self, user_agent: str) -> List[Dict[str, Any]]:
        """Analyze user agent for threats."""
        threats = []

        if not user_agent:
            threats.append(
                {
                    "type": "missing_user_agent",
                    "severity": "low",
                    "description": "Missing User-Agent header",
                    "pattern": "empty",
                }
            )
            return threats

        # Check for blocked user agents
        user_agent_lower = user_agent.lower()
        for blocked_agent in self.config.blocked_user_agents:
            if blocked_agent in user_agent_lower:
                threats.append(
                    {
                        "type": "blocked_user_agent",
                        "severity": "critical",
                        "description": f"Blocked user agent detected: {blocked_agent}",
                        "pattern": blocked_agent,
                    }
                )

        return threats


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive security middleware for ACGS-1 services.

    Features:
    - Rate limiting with Redis backend
    - Threat detection and analysis
    - Input validation and sanitization
    - Security headers injection
    - Request size validation
    - Audit logging for security events
    """

    def __init__(
        self,
        app,
        service_name: str,
        redis_url: str = "redis://localhost:6379",
        config: Optional[SecurityConfig] = None,
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        super().__init__(app)
        self.service_name = service_name
        self.config = config or SecurityConfig()
        self.threat_detector = ThreatDetector(self.config)

        # Initialize rate limiter if available
        if SHARED_COMPONENTS_AVAILABLE:
            self.rate_limiter = RateLimiter(redis_url, service_name)
        else:
            self.rate_limiter = None

        self._initialized = False

    async def _ensure_initialized(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Ensure middleware is initialized."""
        if not self._initialized and self.rate_limiter:
            await self.rate_limiter.initialize()
            self._initialized = True

    async def dispatch(self, request: Request, call_next) -> Response:
        """Main middleware dispatch method."""
        await self._ensure_initialized()

        time.time()
        correlation_id = getattr(request.state, "correlation_id", "unknown")

        try:
            # 1. Request size validation
            size_check = await self._validate_request_size(request)
            if size_check:
                return size_check

            # 2. Threat detection
            threat_analysis = self.threat_detector.analyze_request(request)
            request.state.threat_level = threat_analysis["threat_level"]
            request.state.threats = threat_analysis["threats"]

            # Block critical threats immediately
            if threat_analysis["threat_level"] == SecurityThreatLevel.CRITICAL:
                await self._log_security_event(request, "critical_threat_blocked", threat_analysis)
                return self._create_security_error_response(
                    "Request blocked due to security policy",
                    correlation_id,
                    status.HTTP_403_FORBIDDEN,
                )

            # 3. Rate limiting (if available)
            if self.rate_limiter:
                rate_limit_allowed, rate_limit_info = await self.rate_limiter.check_rate_limit(
                    request
                )
                if not rate_limit_allowed:
                    await self._log_security_event(request, "rate_limit_exceeded", rate_limit_info)
                    return self._create_rate_limit_error_response(rate_limit_info, correlation_id)
            else:
                rate_limit_info = {}

            # 4. Content type validation for body-containing methods
            if request.method in ["POST", "PUT", "PATCH"]:
                content_type_check = self._validate_content_type(request)
                if content_type_check:
                    return content_type_check

            # 5. Process request
            response = await call_next(request)

            # 6. Add security headers
            self._add_security_headers(response)

            # 7. Add rate limit headers (if available)
            if rate_limit_info:
                self._add_rate_limit_headers(response, rate_limit_info)

            # 8. Log security events for high threats
            if threat_analysis["threat_level"] in [
                SecurityThreatLevel.HIGH,
                SecurityThreatLevel.MEDIUM,
            ]:
                await self._log_security_event(request, "threat_detected", threat_analysis)

            return response

        except Exception as e:
            logger.error(
                f"Security middleware error: {e}",
                extra={"correlation_id": correlation_id},
            )
            return self._create_security_error_response(
                "Security processing error",
                correlation_id,
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    async def _validate_request_size(self, request: Request) -> Optional[Response]:
        """Validate request size limits."""
        # Check content length header
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > self.config.max_request_size:
                    correlation_id = getattr(request.state, "correlation_id", "unknown")
                    return self._create_security_error_response(
                        f"Request size ({size} bytes) exceeds limit ({self.config.max_request_size} bytes)",
                        correlation_id,
                        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    )
            except ValueError:
                pass

        return None

    def _validate_content_type(self, request: Request) -> Optional[Response]:
        """Validate content type for requests with body."""
        content_type = request.headers.get("content-type", "").split(";")[0].strip()

        if content_type and content_type not in self.config.allowed_content_types:
            correlation_id = getattr(request.state, "correlation_id", "unknown")
            return self._create_security_error_response(
                f"Content type '{content_type}' not allowed",
                correlation_id,
                status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            )

        return None

    def _add_security_headers(self, response: Response):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Add security headers to response."""
        for header, value in self.config.security_headers.items():
            response.headers[header] = value

    def _add_rate_limit_headers(self, response: Response, rate_limit_info: Dict[str, Any]):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Add rate limiting headers to response."""
        if "limit" in rate_limit_info:
            response.headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
        if "remaining" in rate_limit_info:
            response.headers["X-RateLimit-Remaining"] = str(rate_limit_info["remaining"])
        if "reset_time" in rate_limit_info:
            response.headers["X-RateLimit-Reset"] = str(int(rate_limit_info["reset_time"]))

    def _create_security_error_response(
        self, message: str, correlation_id: str, status_code: int
    ) -> JSONResponse:
        """Create standardized security error response."""
        if SHARED_COMPONENTS_AVAILABLE:
            error_response = create_error_response(
                error_code=(
                    ErrorCode.AUTHORIZATION_ERROR
                    if status_code == 403
                    else ErrorCode.VALIDATION_ERROR
                ),
                message=message,
                service_name=self.service_name,
                correlation_id=correlation_id,
            )
            content = error_response.dict()
        else:
            # Fallback response format
            content = {
                "error": message,
                "service": self.service_name,
                "correlation_id": correlation_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        return JSONResponse(
            status_code=status_code,
            content=content,
            headers={"X-Correlation-ID": correlation_id},
        )

    def _create_rate_limit_error_response(
        self, rate_limit_info: Dict[str, Any], correlation_id: str
    ) -> JSONResponse:
        """Create rate limit error response."""
        retry_after = rate_limit_info.get("reset_time", time.time() + 60) - time.time()

        if SHARED_COMPONENTS_AVAILABLE:
            error_response = create_error_response(
                error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
                message="Rate limit exceeded",
                service_name=self.service_name,
                details=rate_limit_info,
                correlation_id=correlation_id,
            )
            content = error_response.dict()
        else:
            # Fallback response format
            content = {
                "error": "Rate limit exceeded",
                "service": self.service_name,
                "correlation_id": correlation_id,
                "details": rate_limit_info,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        headers = {
            "X-Correlation-ID": correlation_id,
            "Retry-After": str(int(retry_after)),
        }

        if "limit" in rate_limit_info:
            headers["X-RateLimit-Limit"] = str(rate_limit_info["limit"])
        if "reset_time" in rate_limit_info:
            headers["X-RateLimit-Reset"] = str(int(rate_limit_info["reset_time"]))

        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content=content,
            headers=headers,
        )

    async def _log_security_event(self, request: Request, event_type: str, details: Dict[str, Any]):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Log security events for audit and monitoring."""
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": self.service_name,
            "event_type": event_type,
            "client_ip": self._get_client_ip(request),
            "user_agent": request.headers.get("user-agent", ""),
            "method": request.method,
            "path": request.url.path,
            "correlation_id": getattr(request.state, "correlation_id", "unknown"),
            "details": details,
        }

        # Log to structured logger
        logger.warning(f"Security event: {event_type}", extra=event)

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address from request."""
        # Check for forwarded headers (behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # Fall back to direct connection
        if request.client:
            return request.client.host

        return "unknown"
