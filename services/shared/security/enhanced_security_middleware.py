"""
Enhanced Security Middleware for ACGS Production Deployment

This middleware integrates with the advanced security hardening module to provide:
- Real-time threat detection and blocking
- Advanced rate limiting with adaptive thresholds
- Comprehensive security headers
- Input validation and sanitization
- Security event logging and monitoring
- Constitutional compliance validation

Constitutional Hash: cdd01ef066bc6cf2
"""

import ipaddress
import json
import logging
import re
import time
from typing import Any

from fastapi import Request, Response
from fastapi.security import HTTPBearer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .advanced_security_hardening import SecurityLevel, ThreatLevel, security_hardening

logger = logging.getLogger(__name__)


class EnhancedSecurityMiddleware(BaseHTTPMiddleware):
    """Enhanced security middleware with advanced threat protection."""

    def __init__(self, app, config: dict[str, Any] = None):
        super().__init__(app)
        self.config = config or self._get_default_config()
        self.blocked_ips: set[str] = set()
        self.rate_limits: dict[str, dict] = {}
        self.suspicious_patterns: dict[str, int] = {}
        self.security_bearer = HTTPBearer(auto_error=False)

    def _get_default_config(self) -> dict[str, Any]:
        """Get default security configuration."""
        return {
            "enable_rate_limiting": True,
            "enable_input_validation": True,
            "enable_threat_detection": True,
            "enable_constitutional_validation": True,
            "max_request_size": 10 * 1024 * 1024,  # 10MB
            "rate_limit_requests": 100,
            "rate_limit_window": 60,
            "block_duration": 3600,  # 1 hour
            "constitutional_hash": "cdd01ef066bc6cf2",
            "trusted_proxies": {"127.0.0.1", "::1"},
            "security_headers": {
                "X-Content-Type-Options": "nosniff",
                "X-Frame-Options": "DENY",
                "X-XSS-Protection": "1; mode=block",
                "Referrer-Policy": "strict-origin-when-cross-origin",
                "Content-Security-Policy": (
                    "default-src 'self'; "
                    "script-src 'self' 'unsafe-inline'; "
                    "style-src 'self' 'unsafe-inline'; "
                    "img-src 'self' data: https:; "
                    "font-src 'self' https:; "
                    "connect-src 'self' https:; "
                    "frame-ancestors 'none'"
                ),
                "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
                "Permissions-Policy": (
                    "geolocation=(), microphone=(), camera=(), "
                    "payment=(), usb=(), magnetometer=(), gyroscope=()"
                ),
            },
        }

    async def dispatch(self, request: Request, call_next):
        """Main middleware dispatch method."""
        start_time = time.time()
        client_ip = self._get_client_ip(request)

        try:
            # 1. IP Blocking Check
            if await self._is_ip_blocked(client_ip):
                return await self._create_blocked_response(client_ip, "IP blocked")

            # 2. Rate Limiting
            if self.config["enable_rate_limiting"]:
                rate_limit_result = await self._check_rate_limit(client_ip, request)
                if not rate_limit_result["allowed"]:
                    return await self._create_rate_limit_response(client_ip)

            # 3. Request Size Validation
            content_length = request.headers.get("content-length")
            if content_length and int(content_length) > self.config["max_request_size"]:
                await self._log_security_event(
                    "request_size_exceeded",
                    SecurityLevel.MEDIUM,
                    client_ip,
                    None,
                    str(request.url.path),
                    "POST",
                    "blocked",
                )
                return await self._create_error_response(413, "Request too large")

            # 4. Input Validation (for POST/PUT requests)
            if self.config["enable_input_validation"] and request.method in [
                "POST",
                "PUT",
                "PATCH",
            ]:
                validation_result = await self._validate_request_input(request)
                if not validation_result["valid"]:
                    return await self._create_validation_error_response(
                        client_ip, validation_result
                    )

            # 5. Threat Detection
            if self.config["enable_threat_detection"]:
                threat_result = await self._detect_threats(request, client_ip)
                if threat_result["threat_level"] in [
                    ThreatLevel.HIGH,
                    ThreatLevel.CRITICAL,
                ]:
                    return await self._create_threat_response(client_ip, threat_result)

            # 6. Constitutional Compliance Check
            if self.config["enable_constitutional_validation"]:
                compliance_result = await self._validate_constitutional_compliance(
                    request
                )
                if not compliance_result["compliant"]:
                    return await self._create_compliance_error_response(
                        client_ip, compliance_result
                    )

            # Process request
            response = await call_next(request)

            # 7. Add Security Headers
            response = await self._add_security_headers(response)

            # 8. Log successful request
            processing_time = (time.time() - start_time) * 1000
            await self._log_security_event(
                "request_processed",
                SecurityLevel.LOW,
                client_ip,
                None,
                str(request.url.path),
                request.method,
                "success",
                {"processing_time_ms": processing_time},
            )

            return response

        except Exception as e:
            logger.error(f"Security middleware error: {e}")
            await self._log_security_event(
                "middleware_error",
                SecurityLevel.HIGH,
                client_ip,
                None,
                str(request.url.path),
                request.method,
                "error",
                {"error": str(e)},
            )
            return await self._create_error_response(500, "Internal security error")

    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP address considering proxies."""
        # Check X-Forwarded-For header (from trusted proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            # Take the first IP (original client)
            client_ip = forwarded_for.split(",")[0].strip()
            try:
                ipaddress.ip_address(client_ip)
                return client_ip
            except ValueError:
                pass

        # Check X-Real-IP header
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            try:
                ipaddress.ip_address(real_ip)
                return real_ip
            except ValueError:
                pass

        # Fall back to direct connection IP
        return request.client.host

    async def _is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is blocked."""
        return ip in self.blocked_ips

    async def _check_rate_limit(self, ip: str, request: Request) -> dict[str, Any]:
        """Check rate limiting for IP."""
        now = time.time()
        window = self.config["rate_limit_window"]
        limit = self.config["rate_limit_requests"]

        # Clean old entries
        if ip in self.rate_limits:
            self.rate_limits[ip]["requests"] = [
                req_time
                for req_time in self.rate_limits[ip]["requests"]
                if now - req_time < window
            ]
        else:
            self.rate_limits[ip] = {"requests": [], "blocked_until": 0}

        # Check if currently blocked
        if now < self.rate_limits[ip]["blocked_until"]:
            return {"allowed": False, "reason": "rate_limited"}

        # Check rate limit
        request_count = len(self.rate_limits[ip]["requests"])
        if request_count >= limit:
            # Block IP temporarily
            self.rate_limits[ip]["blocked_until"] = now + self.config["block_duration"]
            await self._log_security_event(
                "rate_limit_exceeded",
                SecurityLevel.MEDIUM,
                ip,
                None,
                str(request.url.path),
                request.method,
                "blocked",
            )
            return {"allowed": False, "reason": "rate_limit_exceeded"}

        # Add current request
        self.rate_limits[ip]["requests"].append(now)
        return {"allowed": True}

    async def _validate_request_input(self, request: Request) -> dict[str, Any]:
        """Validate request input for malicious content."""
        try:
            # Get request body
            body = await request.body()
            if not body:
                return {"valid": True}

            # Try to parse as JSON
            try:
                json_data = json.loads(body.decode("utf-8"))
                # Validate JSON data
                return security_hardening.input_validator.validate_input(
                    json.dumps(json_data), "json"
                )
            except (json.JSONDecodeError, UnicodeDecodeError):
                # Validate as raw text
                return security_hardening.input_validator.validate_input(
                    body.decode("utf-8", errors="ignore"), "text"
                )

        except Exception as e:
            logger.error(f"Input validation error: {e}")
            return {
                "valid": False,
                "threats": ["validation_error"],
                "risk_level": ThreatLevel.MEDIUM,
            }

    async def _detect_threats(self, request: Request, client_ip: str) -> dict[str, Any]:
        """Advanced threat detection."""
        threats = []
        threat_level = ThreatLevel.NONE

        # Check for suspicious patterns in URL
        url_path = str(request.url.path)
        suspicious_url_patterns = [
            r"\.\./",  # Path traversal
            r"<script",  # XSS in URL
            r"union.*select",  # SQL injection
            r"exec\(",  # Command injection
            r"/admin",  # Admin access attempts
            r"/config",  # Config access attempts
        ]

        for pattern in suspicious_url_patterns:
            if re.search(pattern, url_path, re.IGNORECASE):
                threats.append(f"suspicious_url_{pattern}")
                threat_level = ThreatLevel.HIGH

        # Check User-Agent for known attack tools
        user_agent = request.headers.get("user-agent", "").lower()
        malicious_agents = [
            "sqlmap",
            "nikto",
            "nmap",
            "masscan",
            "zap",
            "burp",
            "w3af",
            "skipfish",
            "dirb",
            "gobuster",
        ]

        for agent in malicious_agents:
            if agent in user_agent:
                threats.append(f"malicious_user_agent_{agent}")
                threat_level = ThreatLevel.CRITICAL

        # Check for rapid requests from same IP (potential bot)
        if client_ip in self.rate_limits:
            recent_requests = len(
                [
                    req_time
                    for req_time in self.rate_limits[client_ip]["requests"]
                    if time.time() - req_time < 10  # Last 10 seconds
                ]
            )
            if recent_requests > 20:
                threats.append("rapid_requests")
                threat_level = ThreatLevel.HIGH

        return {
            "threats": threats,
            "threat_level": threat_level,
            "details": {
                "url_path": url_path,
                "user_agent": user_agent,
                "client_ip": client_ip,
            },
        }

    async def _validate_constitutional_compliance(
        self, request: Request
    ) -> dict[str, Any]:
        """Validate constitutional compliance."""
        # Check for constitutional hash in headers
        constitutional_hash = request.headers.get("x-constitutional-hash")
        expected_hash = self.config["constitutional_hash"]

        if constitutional_hash != expected_hash:
            return {
                "compliant": False,
                "reason": "invalid_constitutional_hash",
                "expected": expected_hash,
                "received": constitutional_hash,
            }

        return {"compliant": True}

    async def _add_security_headers(self, response: Response) -> Response:
        """Add comprehensive security headers."""
        for header, value in self.config["security_headers"].items():
            response.headers[header] = value

        # Add constitutional compliance headers
        response.headers["X-Constitutional-Hash"] = self.config["constitutional_hash"]
        response.headers["X-Security-Framework"] = "ACGS-Enhanced-v2.0"
        response.headers["X-Response-Time"] = f"{time.time():.3f}"

        return response

    async def _log_security_event(
        self,
        event_type: str,
        severity: SecurityLevel,
        source_ip: str,
        user_id: str | None,
        resource: str,
        action: str,
        result: str,
        details: dict[str, Any] = None,
    ):
        """Log security event."""
        security_hardening.log_security_event(
            event_type, severity, source_ip, user_id, resource, action, result, details
        )

    async def _create_blocked_response(self, ip: str, reason: str) -> JSONResponse:
        """Create response for blocked requests."""
        await self._log_security_event(
            "request_blocked",
            SecurityLevel.HIGH,
            ip,
            None,
            "middleware",
            "block",
            "blocked",
            {"reason": reason},
        )

        return JSONResponse(
            status_code=403,
            content={
                "error": "Access denied",
                "message": "Your request has been blocked by security policies",
                "constitutional_hash": self.config["constitutional_hash"],
            },
            headers={"X-Security-Block-Reason": reason},
        )

    async def _create_rate_limit_response(self, ip: str) -> JSONResponse:
        """Create response for rate limited requests."""
        return JSONResponse(
            status_code=429,
            content={
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later.",
                "constitutional_hash": self.config["constitutional_hash"],
            },
            headers={
                "Retry-After": str(self.config["block_duration"]),
                "X-RateLimit-Limit": str(self.config["rate_limit_requests"]),
                "X-RateLimit-Window": str(self.config["rate_limit_window"]),
            },
        )

    async def _create_validation_error_response(
        self, ip: str, validation_result: dict[str, Any]
    ) -> JSONResponse:
        """Create response for validation errors."""
        await self._log_security_event(
            "input_validation_failed",
            SecurityLevel.HIGH,
            ip,
            None,
            "middleware",
            "validate",
            "blocked",
            {"threats": validation_result["threats"]},
        )

        return JSONResponse(
            status_code=400,
            content={
                "error": "Invalid input detected",
                "message": "Your request contains potentially malicious content",
                "threats_detected": validation_result["threats"],
                "constitutional_hash": self.config["constitutional_hash"],
            },
        )

    async def _create_threat_response(
        self, ip: str, threat_result: dict[str, Any]
    ) -> JSONResponse:
        """Create response for detected threats."""
        await self._log_security_event(
            "threat_detected",
            SecurityLevel.CRITICAL,
            ip,
            None,
            "middleware",
            "threat_detection",
            "blocked",
            threat_result,
        )

        # Block IP for critical threats
        if threat_result["threat_level"] == ThreatLevel.CRITICAL:
            self.blocked_ips.add(ip)

        return JSONResponse(
            status_code=403,
            content={
                "error": "Security threat detected",
                "message": "Your request has been identified as a potential security threat",
                "constitutional_hash": self.config["constitutional_hash"],
            },
            headers={"X-Threat-Level": threat_result["threat_level"].value},
        )

    async def _create_compliance_error_response(
        self, ip: str, compliance_result: dict[str, Any]
    ) -> JSONResponse:
        """Create response for compliance errors."""
        await self._log_security_event(
            "constitutional_compliance_failed",
            SecurityLevel.HIGH,
            ip,
            None,
            "middleware",
            "compliance_check",
            "blocked",
            compliance_result,
        )

        return JSONResponse(
            status_code=403,
            content={
                "error": "Constitutional compliance violation",
                "message": "Request does not meet constitutional governance requirements",
                "expected_hash": compliance_result.get("expected"),
                "constitutional_hash": self.config["constitutional_hash"],
            },
        )

    async def _create_error_response(
        self, status_code: int, message: str
    ) -> JSONResponse:
        """Create generic error response."""
        return JSONResponse(
            status_code=status_code,
            content={
                "error": message,
                "constitutional_hash": self.config["constitutional_hash"],
            },
        )
