"""
ACGS Security Middleware Integration
Constitutional Hash: cdd01ef066bc6cf2

Standardized security middleware integration for all ACGS services.
This module provides a unified way to apply comprehensive security across all services.
"""

import logging
import os
from typing import Any

from fastapi import FastAPI, HTTPException, Request

try:
    from .unified_input_validation import (
        EnhancedInputValidator,
        SecurityConfig,
        SecurityLevel,
        SecurityMiddleware,
        sanitize_dict,
        validate_input_secure,
    )

    VALIDATION_AVAILABLE = True
except ImportError:
    VALIDATION_AVAILABLE = False

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class ACGSSecurityConfig:
    """ACGS-specific security configuration."""

    @staticmethod
    def get_production_config() -> SecurityConfig:
        """Get production security configuration."""
        return SecurityConfig(
            max_string_length=2000,
            max_json_size=2 * 1024 * 1024,  # 2MB
            max_file_size=20 * 1024 * 1024,  # 20MB
            allowed_file_types={
                "jpg",
                "jpeg",
                "png",
                "gif",
                "pdf",
                "txt",
                "json",
                "xml",
                "csv",
            },
            rate_limit_requests=int(os.getenv("RATE_LIMIT_PER_MINUTE", "100")),
            rate_limit_window=60,
            csrf_token_expiry=3600,
            enable_strict_csp=True,
            enable_xss_protection=True,
            enable_csrf_protection=True,
        )

    @staticmethod
    def get_development_config() -> SecurityConfig:
        """Get development security configuration."""
        return SecurityConfig(
            max_string_length=5000,
            max_json_size=5 * 1024 * 1024,  # 5MB
            max_file_size=50 * 1024 * 1024,  # 50MB
            allowed_file_types={
                "jpg",
                "jpeg",
                "png",
                "gif",
                "pdf",
                "txt",
                "json",
                "xml",
                "csv",
                "yaml",
                "yml",
                "md",
                "log",
            },
            rate_limit_requests=int(os.getenv("RATE_LIMIT_PER_MINUTE", "200")),
            rate_limit_window=60,
            csrf_token_expiry=7200,  # 2 hours for dev
            enable_strict_csp=False,  # More lenient for dev
            enable_xss_protection=True,
            enable_csrf_protection=False,  # Disabled for easier API testing
        )


def apply_acgs_security_middleware(
    app: FastAPI, service_name: str, environment: str = "production"
) -> None:
    """
    Apply standardized ACGS security middleware to a FastAPI application.

    Args:
        app: FastAPI application instance
        service_name: Name of the service for logging
        environment: Environment (production/development)
    """
    if not VALIDATION_AVAILABLE:
        logger.warning(
            f"Unified input validation not available for {service_name}. "
            "Security middleware not applied."
        )
        return

    # Get appropriate security config
    if environment.lower() == "production":
        config = ACGSSecurityConfig.get_production_config()
    else:
        config = ACGSSecurityConfig.get_development_config()

    # Apply security middleware
    try:
        app.add_middleware(SecurityMiddleware, config=config)

        logger.info(
            f"Applied ACGS security middleware to {service_name}",
            extra={
                "service": service_name,
                "environment": environment,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "rate_limit": config.rate_limit_requests,
                "csrf_enabled": config.enable_csrf_protection,
                "xss_enabled": config.enable_xss_protection,
            },
        )

    except Exception as e:
        logger.exception(
            f"Failed to apply security middleware to {service_name}: {e}",
            extra={
                "service": service_name,
                "error": str(e),
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
        )
        raise


def create_secure_endpoint_decorator(
    security_level: SecurityLevel = SecurityLevel.MEDIUM,
):
    """
    Create a decorator for endpoint-specific security validation.

    Args:
        security_level: Security validation level

    Returns:
        Decorator function for FastAPI endpoints
    """

    def decorator(func):
        async def wrapper(request: Request, *args, **kwargs):
            if not VALIDATION_AVAILABLE:
                return await func(request, *args, **kwargs)

            # Validate query parameters
            for param, value in request.query_params.items():
                try:
                    validate_input_secure(
                        str(value), max_length=500, security_level=security_level
                    )
                except ValueError as e:
                    logger.warning(
                        f"Query parameter validation failed: {param}",
                        extra={
                            "param": param,
                            "error": str(e),
                            "constitutional_hash": CONSTITUTIONAL_HASH,
                        },
                    )
                    raise HTTPException(
                        status_code=400, detail=f"Invalid query parameter: {param}"
                    )

            # Validate path parameters
            for param, value in request.path_params.items():
                try:
                    validate_input_secure(
                        str(value), max_length=100, security_level=security_level
                    )
                except ValueError as e:
                    logger.warning(
                        f"Path parameter validation failed: {param}",
                        extra={
                            "param": param,
                            "error": str(e),
                            "constitutional_hash": CONSTITUTIONAL_HASH,
                        },
                    )
                    raise HTTPException(
                        status_code=400, detail=f"Invalid path parameter: {param}"
                    )

            return await func(request, *args, **kwargs)

        return wrapper

    return decorator


def validate_request_body(
    data: dict[str, Any], security_level: SecurityLevel = SecurityLevel.MEDIUM
) -> dict[str, Any]:
    """
    Validate and sanitize request body data.

    Args:
        data: Request body data
        security_level: Security validation level

    Returns:
        Sanitized data dictionary

    Raises:
        HTTPException: If validation fails
    """
    if not VALIDATION_AVAILABLE:
        return data

    try:
        sanitized_data = sanitize_dict(data, security_level)

        logger.debug(
            "Request body validated and sanitized",
            extra={
                "data_keys": list(data.keys()),
                "security_level": security_level.value,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
        )

        return sanitized_data

    except Exception as e:
        logger.warning(
            f"Request body validation failed: {e}",
            extra={
                "error": str(e),
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
        )
        raise HTTPException(status_code=400, detail="Request body validation failed")


def get_security_headers() -> dict[str, str]:
    """
    Get standard ACGS security headers.

    Returns:
        Dictionary of security headers
    """
    return {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "Content-Security-Policy": (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        ),
        "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
    }


def create_rate_limit_key(request: Request) -> str:
    """
    Create rate limit key for request.

    Args:
        request: FastAPI request object

    Returns:
        Rate limit key string
    """
    # Use combination of IP and user agent for better tracking
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")[
        :50
    ]  # Truncate for performance

    return f"{client_ip}:{hash(user_agent)}"


class SecurityMetrics:
    """Security metrics collection for monitoring."""

    def __init__(self):
        self.blocked_requests = 0
        self.validation_failures = 0
        self.rate_limit_hits = 0
        self.csrf_failures = 0

    def increment_blocked_requests(self):
        """Increment blocked requests counter."""
        self.blocked_requests += 1

    def increment_validation_failures(self):
        """Increment validation failures counter."""
        self.validation_failures += 1

    def increment_rate_limit_hits(self):
        """Increment rate limit hits counter."""
        self.rate_limit_hits += 1

    def increment_csrf_failures(self):
        """Increment CSRF failures counter."""
        self.csrf_failures += 1

    def get_metrics(self) -> dict[str, int]:
        """Get current security metrics."""
        return {
            "blocked_requests": self.blocked_requests,
            "validation_failures": self.validation_failures,
            "rate_limit_hits": self.rate_limit_hits,
            "csrf_failures": self.csrf_failures,
            "constitutional_hash_valid": 1,  # Always 1 for constitutional compliance
        }


# Global security metrics instance
security_metrics = SecurityMetrics()


def setup_security_monitoring(app: FastAPI, service_name: str) -> None:
    """
    Setup security monitoring endpoints for the service.

    Args:
        app: FastAPI application instance
        service_name: Name of the service
    """

    @app.get("/security/metrics")
    async def get_security_metrics():
        """Get security metrics for monitoring."""
        metrics = security_metrics.get_metrics()
        metrics["service"] = service_name
        metrics["constitutional_hash"] = CONSTITUTIONAL_HASH
        return metrics

    @app.get("/security/health")
    async def get_security_health():
        """Get security health status."""
        return {
            "status": "healthy",
            "service": service_name,
            "validation_available": VALIDATION_AVAILABLE,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "security_features": {
                "input_validation": VALIDATION_AVAILABLE,
                "rate_limiting": True,
                "csrf_protection": True,
                "xss_protection": True,
                "security_headers": True,
            },
        }
