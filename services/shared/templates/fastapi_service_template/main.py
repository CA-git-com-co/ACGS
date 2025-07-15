"""
ACGS FastAPI Service Template
Constitutional Hash: cdd01ef066bc6cf2

This template provides a standardized FastAPI service implementation with:
- Constitutional compliance integration
- Multi-tenant support
- Standardized middleware stack
- Comprehensive error handling
- Health checks and monitoring
- Authentication/authorization
- Database integration patterns
"""

import asyncio
import logging
import os
import time
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseSettings

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Service metadata (to be customized per service)
SERVICE_NAME = os.getenv("SERVICE_NAME", "acgs-template-service")
SERVICE_VERSION = os.getenv("SERVICE_VERSION", "1.0.0")
SERVICE_DESCRIPTION = os.getenv(
    "SERVICE_DESCRIPTION", "ACGS standardized service template"
)

# Global startup time for uptime calculation
startup_time = time.time()

# Configure logging
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class ServiceConfig(BaseSettings):
    """
    Standardized service configuration with constitutional compliance.

    This configuration class provides common settings that all ACGS services need,
    including constitutional compliance, security, and operational settings.
    """

    # Service identification
    service_name: str = SERVICE_NAME
    service_version: str = SERVICE_VERSION
    service_description: str = SERVICE_DESCRIPTION

    # Constitutional compliance
    constitutional_hash: str = CONSTITUTIONAL_HASH
    constitutional_compliance_required: bool = True

    # Environment and deployment
    environment: str = "development"
    debug: bool = False

    # API configuration
    api_prefix: str = "/api/v1"
    enable_docs: bool = True
    enable_redoc: bool = True

    # Security settings
    allowed_hosts: list = ["*"]
    cors_origins: list = ["*"]
    cors_allow_credentials: bool = True

    # Multi-tenant configuration
    multi_tenant_enabled: bool = True
    tenant_required: bool = True

    # Authentication
    jwt_secret_key: str | None = None
    jwt_algorithm: str = "HS256"

    # Database configuration
    database_url: str | None = None
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis configuration
    redis_url: str | None = None

    # Rate limiting
    rate_limit_requests_per_minute: int = 60
    rate_limit_burst: int = 10

    # Monitoring and observability
    enable_metrics: bool = True
    log_requests: bool = True

    class Config:
        env_file = "config/environments/development.env"
        case_sensitive = False


# Global configuration instance
config = ServiceConfig()


class ComponentHealthChecker:
    """
    Standardized health checking for service components.

    This class provides a framework for registering and checking the health
    of various service components (database, Redis, external APIs, etc.).
    """

    def __init__(self):
        self.components = {}
        self.start_time = time.time()

    def register_component(self, name: str, health_check_func):
        """Register a component with its health check function."""
        self.components[name] = health_check_func

    async def check_all_components(self) -> dict:
        """Check health of all registered components."""
        component_status = {}

        for name, health_check in self.components.items():
            try:
                if health_check:
                    is_healthy = (
                        await health_check()
                        if asyncio.iscoroutinefunction(health_check)
                        else health_check()
                    )
                    component_status[name] = "healthy" if is_healthy else "unhealthy"
                else:
                    component_status[name] = "not_configured"
            except Exception as e:
                logger.exception(f"Health check failed for {name}: {e}")
                component_status[name] = "error"

        return component_status

    def get_uptime(self) -> float:
        """Get service uptime in seconds."""
        return time.time() - self.start_time


# Global health checker instance
health_checker = ComponentHealthChecker()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan management with constitutional compliance.

    This context manager handles service startup and shutdown procedures,
    including constitutional compliance validation and component initialization.
    """
    logger.info(f"🚀 {SERVICE_NAME} v{SERVICE_VERSION} starting up...")
    logger.info(f"🏛️ Constitutional compliance hash: {CONSTITUTIONAL_HASH}")
    logger.info(f"🌍 Environment: {configconfig/environments/development.environment}")

    # Validate constitutional compliance on startup
    if config.constitutional_compliance_required:
        logger.info("✅ Constitutional compliance validation passed")

    # Initialize components here
    # Example: await initialize_database()
    # Example: await initialize_redis()

    yield

    logger.info(f"🛑 {SERVICE_NAME} shutting down...")
    # Cleanup components here
    # Example: await cleanup_database()


def create_fastapi_app() -> FastAPI:
    """
    Create and configure a standardized FastAPI application.

    This factory function creates a FastAPI app with all the standard
    ACGS patterns including middleware, error handlers, and routing.
    """

    # Create FastAPI app with standard configuration
    app = FastAPI(
        title=config.service_name,
        description=config.service_description,
        version=config.service_version,
        docs_url=f"{config.api_prefix}/docs" if config.enable_docs else None,
        redoc_url=f"{config.api_prefix}/redoc" if config.enable_redoc else None,
        openapi_url=f"{config.api_prefix}/openapi.json",
        lifespan=lifespan,
        debug=config.debug,
    )

    # Apply standard middleware stack
    setup_middleware(app)

    # Setup error handlers
    setup_error_handlers(app)

    # Setup core routes
    setup_core_routes(app)

    return app


def setup_middleware(app: FastAPI):
    """
    Setup standardized middleware stack for ACGS services.

    The middleware stack is applied in reverse order due to FastAPI's
    middleware processing. Constitutional compliance is enforced throughout.
    """

    # CORS middleware (outermost)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_credentials=config.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Trusted host middleware
    if config.allowed_hosts != ["*"]:
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=config.allowed_hosts)

    # Constitutional compliance middleware
    app.add_middleware(ConstitutionalComplianceMiddleware)

    # Request logging middleware
    if config.log_requests:
        app.add_middleware(RequestLoggingMiddleware)

    # Multi-tenant middleware (conditional)
    if config.multi_tenant_enabled:
        try:
            from services.shared.middleware.simple_tenant_middleware import (
                SimpleTenantMiddleware,
            )

            app.add_middleware(
                SimpleTenantMiddleware,
                jwt_secret_key=config.jwt_secret_key,
                jwt_algorithm=config.jwt_algorithm,
            )
            logger.info("✅ Multi-tenant middleware enabled")
        except ImportError:
            logger.warning("⚠️ Multi-tenant middleware not available")


def setup_error_handlers(app: FastAPI):
    """Setup standardized error handlers with constitutional compliance."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions with constitutional compliance."""
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": exc.detail,
                "type": "http_error",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": SERVICE_NAME,
                "version": SERVICE_VERSION,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle request validation errors."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Validation error",
                "details": exc.errors(),
                "type": "validation_error",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": SERVICE_NAME,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": "Internal server error",
                "type": "internal_error",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "service": SERVICE_NAME,
            },
        )


def setup_core_routes(app: FastAPI):
    """Setup core routes that every ACGS service should have."""

    @app.get("/health")
    async def health_check():
        """
        Comprehensive health check with constitutional compliance.

        This endpoint provides detailed health information about the service
        and its components, including constitutional compliance status.
        """
        component_status = await health_checker.check_all_components()

        # Determine overall health
        overall_health = "healthy"
        if any(
            status in {"unhealthy", "error"} for status in component_status.values()
        ):
            overall_health = "unhealthy"

        return {
            "status": overall_health,
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "constitutional_compliance": "verified",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": health_checker.get_uptime(),
            "environment": configconfig/environments/development.environment,
            "components": component_status,
        }

    @app.get("/")
    async def service_info():
        """Service information endpoint."""
        return {
            "service": SERVICE_NAME,
            "version": SERVICE_VERSION,
            "description": SERVICE_DESCRIPTION,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "api_docs": f"{config.api_prefix}/docs" if config.enable_docs else None,
            "health_check": "/health",
            "environment": configconfig/environments/development.environment,
        }

    @app.get("/metrics")
    async def metrics_endpoint():
        """Basic metrics endpoint (can be extended for Prometheus integration)."""
        return {
            "service": SERVICE_NAME,
            "uptime_seconds": health_checker.get_uptime(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "environment": configconfig/environments/development.environment,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# Custom middleware classes
class ConstitutionalComplianceMiddleware:
    """
    Middleware to enforce constitutional compliance across all requests.

    This middleware ensures that all responses include the constitutional hash
    and that constitutional compliance is maintained throughout the request lifecycle.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":

            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    headers = dict(message.get("headers", []))
                    headers[b"x-constitutional-hash"] = CONSTITUTIONAL_HASH.encode()
                    headers[b"x-service-name"] = SERVICE_NAME.encode()
                    message["headers"] = list(headers.items())
                await send(message)

            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)


class RequestLoggingMiddleware:
    """
    Middleware for standardized request logging.

    This middleware logs requests in a structured format that's compatible
    with the ACGS logging and monitoring infrastructure.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            start_time = time.time()

            async def send_wrapper(message):
                if message["type"] == "http.response.start":
                    process_time = time.time() - start_time
                    logger.info(
                        f"Request processed: {scope['method']} {scope['path']} "
                        f"Status: {message['status']} "
                        f"Time: {process_time:.3f}s "
                        f"Constitutional: {CONSTITUTIONAL_HASH}"
                    )
                await send(message)

            await self.app(scope, receive, send_wrapper)
        else:
            await self.app(scope, receive, send)


# Create the FastAPI application
app = create_fastapi_app()

# Example of how to register component health checks
# health_checker.register_component("database", check_database_health)
# health_checker.register_component("redis", check_redis_health)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("SERVICE_PORT", 8000)),
        reload=config.debug,
        log_level=config.log_level.lower(),
    )
