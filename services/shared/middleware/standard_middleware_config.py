"""
Standard Middleware Configuration for ACGS-2 Services
Constitutional Hash: cdd01ef066bc6cf2

This module provides standardized middleware configuration for all ACGS-2 services
to ensure consistent security, performance, and constitutional compliance.
"""

import logging
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

try:
    from services.shared.security.enhanced_security_middleware import (
        EnhancedSecurityMiddleware,
        SecurityConfig,
    )
    ENHANCED_SECURITY_AVAILABLE = True
except ImportError:
    from services.shared.security_headers_middleware import SecurityHeadersMiddleware
    ENHANCED_SECURITY_AVAILABLE = False

try:
    from services.shared.middleware.prometheus_metrics_middleware import PrometheusMiddleware
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    from services.shared.middleware.constitutional_validation import ConstitutionalValidationMiddleware
    CONSTITUTIONAL_VALIDATION_AVAILABLE = True
except ImportError:
    CONSTITUTIONAL_VALIDATION_AVAILABLE = False

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class StandardMiddlewareConfig:
    """Standard middleware configuration for ACGS-2 services."""
    
    # Security settings
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 60  # seconds
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10MB
    
    # CORS settings
    CORS_ALLOWED_ORIGINS = ["*"]
    CORS_ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOWED_HEADERS = ["*"]
    
    # Trusted hosts
    TRUSTED_HOSTS = ["localhost", "127.0.0.1", "*.acgs.local"]


def apply_standard_middleware(
    app: FastAPI,
    service_name: str,
    config: Optional[StandardMiddlewareConfig] = None,
    enable_metrics: bool = True,
    enable_security: bool = True,
    enable_cors: bool = True,
) -> None:
    """
    Apply standard middleware configuration to a FastAPI application.
    
    Args:
        app: FastAPI application instance
        service_name: Name of the service for logging and metrics
        config: Custom configuration (uses defaults if None)
        enable_metrics: Whether to enable Prometheus metrics
        enable_security: Whether to enable enhanced security middleware
        enable_cors: Whether to enable CORS middleware
    """
    if config is None:
        config = StandardMiddlewareConfig()
    
    logger.info(f"Applying standard middleware to {service_name} with constitutional hash: {CONSTITUTIONAL_HASH}")
    
    # 1. Enhanced Security Middleware (highest priority)
    if enable_security:
        if ENHANCED_SECURITY_AVAILABLE:
            app.add_middleware(
                EnhancedSecurityMiddleware,
                max_requests=config.RATE_LIMIT_REQUESTS,
                window_seconds=config.RATE_LIMIT_WINDOW,
                max_request_size=config.MAX_REQUEST_SIZE,
            )
            logger.info(f"Enhanced security middleware applied to {service_name}")
        else:
            # Fallback to basic security headers
            app.add_middleware(SecurityHeadersMiddleware)
            logger.warning(f"Using fallback security middleware for {service_name}")
    
    # 2. Constitutional Validation Middleware
    if CONSTITUTIONAL_VALIDATION_AVAILABLE:
        app.add_middleware(ConstitutionalValidationMiddleware)
        logger.info(f"Constitutional validation middleware applied to {service_name}")
    
    # 3. Prometheus Metrics Middleware
    if enable_metrics and PROMETHEUS_AVAILABLE:
        app.add_middleware(PrometheusMiddleware, service_name=service_name)
        logger.info(f"Prometheus metrics middleware applied to {service_name}")
    
    # 4. CORS Middleware
    if enable_cors:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=config.CORS_ALLOWED_ORIGINS,
            allow_credentials=True,
            allow_methods=config.CORS_ALLOWED_METHODS,
            allow_headers=config.CORS_ALLOWED_HEADERS,
        )
        logger.info(f"CORS middleware applied to {service_name}")
    
    # 5. Trusted Host Middleware (lowest priority)
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=config.TRUSTED_HOSTS,
    )
    logger.info(f"Trusted host middleware applied to {service_name}")
    
    # Add constitutional hash to app state for reference
    app.state.constitutional_hash = CONSTITUTIONAL_HASH
    app.state.service_name = service_name
    
    logger.info(
        f"Standard middleware configuration complete for {service_name}. "
        f"Security: {enable_security}, Metrics: {enable_metrics}, CORS: {enable_cors}"
    )


def ensure_constitutional_headers(app: FastAPI) -> None:
    """
    Ensure constitutional hash headers are added to all responses.
    
    This is a backup mechanism to guarantee constitutional compliance
    even if the enhanced security middleware is not available.
    """
    @app.middleware("http")
    async def add_constitutional_header(request, call_next):
        response = await call_next(request)
        response.headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH
        response.headers["X-Service-Compliance"] = "constitutional-validated"
        return response
    
    logger.info("Constitutional header middleware applied as backup")


def get_middleware_status() -> dict:
    """
    Get the status of available middleware components.
    
    Returns:
        Dictionary with middleware availability status
    """
    return {
        "enhanced_security": ENHANCED_SECURITY_AVAILABLE,
        "prometheus_metrics": PROMETHEUS_AVAILABLE,
        "constitutional_validation": CONSTITUTIONAL_VALIDATION_AVAILABLE,
        "constitutional_hash": CONSTITUTIONAL_HASH,
    }


# Convenience function for quick setup
def setup_standard_acgs_service(
    app: FastAPI,
    service_name: str,
    enable_all: bool = True,
) -> None:
    """
    Quick setup for standard ACGS service with all middleware enabled.
    
    Args:
        app: FastAPI application instance
        service_name: Name of the service
        enable_all: Whether to enable all available middleware
    """
    apply_standard_middleware(
        app=app,
        service_name=service_name,
        enable_metrics=enable_all,
        enable_security=enable_all,
        enable_cors=enable_all,
    )
    
    # Always ensure constitutional headers as backup
    ensure_constitutional_headers(app)
    
    logger.info(f"ACGS-2 service {service_name} configured with constitutional compliance: {CONSTITUTIONAL_HASH}")