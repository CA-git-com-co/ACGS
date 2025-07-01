"""
Service Template for ACGS-1 Services

Provides standardized FastAPI service creation with all enhancement patterns applied.
Ensures consistent configuration across all ACGS-1 services.
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from .cache_enhancer import CacheEnhancer
from .constitutional_validator import ConstitutionalValidationMiddleware
from .monitoring_integrator import MonitoringIntegrator
from .performance_optimizer import PerformanceEnhancer

logger = logging.getLogger(__name__)


class ACGSServiceTemplate:
    """
    Standardized service template for ACGS-1 services.

    Features:
    - Consistent FastAPI configuration
    - Constitutional compliance validation
    - Performance optimization
    - Monitoring integration
    - Redis caching
    - Standardized middleware stack
    """

    def __init__(
        self,
        service_name: str,
        port: int,
        version: str = "3.0.0",
        description: str | None = None,
    ):
        self.service_name = service_name
        self.port = port
        self.version = version
        self.description = (
            description or f"ACGS-1 Production {service_name.title()} Service"
        )

        # Enhancement components
        self.performance_enhancer = PerformanceEnhancer(service_name)
        self.monitoring_integrator = MonitoringIntegrator(service_name)
        self.cache_enhancer = CacheEnhancer(service_name)

        # Configuration
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.enable_constitutional_validation = True
        self.enable_performance_optimization = True
        self.enable_monitoring = True
        self.enable_caching = True

        logger.info(f"Service template initialized for {service_name}")

    @asynccontextmanager
    async def create_lifespan(self):
        """Create lifespan context manager for service initialization."""
        logger.info(f"🚀 Starting ACGS-1 {self.service_name} Service")

        try:
            # Initialize cache enhancer
            if self.enable_caching:
                await self.cache_enhancer.initialize()
                logger.info("✅ Cache enhancer initialized")

            # Initialize monitoring
            if self.enable_monitoring:
                self.monitoring_integrator.update_service_health(True)
                logger.info("✅ Monitoring integrator initialized")

            # Service-specific initialization can be added here
            logger.info(f"✅ {self.service_name} service initialized successfully")

            yield

        except Exception as e:
            logger.error(f"❌ Service initialization failed: {e}")
            if self.enable_monitoring:
                self.monitoring_integrator.update_service_health(False)
            yield

        finally:
            logger.info(f"🔄 Shutting down {self.service_name} service")

            # Cleanup
            if self.enable_caching:
                await self.cache_enhancer.close()

    async def create_enhanced_app(self) -> FastAPI:
        """Create FastAPI application with all enhancements applied."""
        # Create FastAPI app with standardized configuration
        app = FastAPI(
            title=f"ACGS-1 Production {self.service_name.title()} Service",
            description=self.description,
            version=self.version,
            docs_url="/docs",
            redoc_url="/redoc",
            openapi_url="/openapi.json",
            lifespan=self.create_lifespan(),
        )

        # Apply middleware stack (in reverse order - last added is executed first)
        await self._apply_middleware_stack(app)

        # Apply enhancements
        await self._apply_enhancements(app)

        # Add standard endpoints
        self._add_standard_endpoints(app)

        logger.info(f"Enhanced FastAPI application created for {self.service_name}")
        return app

    async def _apply_middleware_stack(self, app: FastAPI):
        """Apply standardized middleware stack."""
        # Security middleware (applied last, executed first)
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

        # CORS middleware with production settings
        app.add_middleware(
            CORSMiddleware,
            allow_origins=self._get_cors_origins(),
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["*"],
            expose_headers=[
                "X-Request-ID",
                "X-Response-Time",
                "X-Constitutional-Hash",
                "X-Service-Performance",
                "X-Monitoring",
            ],
        )

        # Constitutional validation middleware
        if self.enable_constitutional_validation:
            app.add_middleware(
                ConstitutionalValidationMiddleware,
                service_name=self.service_name,
                enable_strict_validation=True,
            )

        logger.info("Middleware stack applied")

    async def _apply_enhancements(self, app: FastAPI):
        """Apply all enhancement components."""
        # Performance optimization
        if self.enable_performance_optimization:
            await self.performance_enhancer.optimize_service(app)

        # Monitoring integration
        if self.enable_monitoring:
            await self.monitoring_integrator.integrate_monitoring(app)

        logger.info("Enhancement components applied")

    def _add_standard_endpoints(self, app: FastAPI):
        """Add standard endpoints to the service."""

        @app.get("/")
        async def root():
            """Root endpoint with service information."""
            return {
                "service": f"ACGS-1 Production {self.service_name.title()} Service",
                "version": self.version,
                "status": "operational",
                "port": self.port,
                "phase": "Phase 3 - Production Implementation",
                "constitutional_hash": self.constitutional_hash,
                "enhancements": {
                    "constitutional_validation": self.enable_constitutional_validation,
                    "performance_optimization": self.enable_performance_optimization,
                    "monitoring": self.enable_monitoring,
                    "caching": self.enable_caching,
                },
                "capabilities": [
                    "Constitutional Compliance Validation",
                    "Performance Optimization",
                    "Prometheus Metrics",
                    "Redis Caching",
                    "Circuit Breaker Protection",
                ],
            }

        @app.get("/status")
        async def status():
            """Enhanced status endpoint with performance metrics."""
            status_data = {
                "service": self.service_name,
                "status": "healthy",
                "version": self.version,
                "constitutional_hash": self.constitutional_hash,
            }

            # Add performance metrics if available
            if self.enable_performance_optimization:
                status_data["performance"] = (
                    self.performance_enhancer.get_performance_metrics()
                )

            # Add cache statistics if available
            if self.enable_caching:
                status_data["cache"] = self.cache_enhancer.get_cache_stats()

            return status_data

        logger.info("Standard endpoints added")

    def _get_cors_origins(self) -> list[str]:
        """Get CORS origins from environment or use defaults."""
        cors_origins = os.getenv("CORS_ORIGINS", "").split(",")
        if cors_origins == [""]:
            # Default CORS origins for development
            cors_origins = [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "https://localhost:3000",
                "https://127.0.0.1:3000",
            ]

        # Add wildcard for development (configure appropriately for production)
        cors_origins.append("*")

        return cors_origins

    def configure_constitutional_validation(
        self,
        enabled: bool = True,
        strict_mode: bool = True,
        bypass_paths: list[str] | None = None,
    ):
        """Configure constitutional validation settings."""
        self.enable_constitutional_validation = enabled
        # Additional configuration can be stored and applied during app creation

    def configure_performance_optimization(
        self,
        enabled: bool = True,
        response_time_target: float = 0.5,
        availability_target: float = 0.995,
    ):
        """Configure performance optimization settings."""
        self.enable_performance_optimization = enabled
        if enabled:
            self.performance_enhancer.performance_targets.update(
                {
                    "response_time_p95": response_time_target,
                    "availability": availability_target,
                }
            )

    def configure_caching(
        self,
        enabled: bool = True,
        redis_url: str | None = None,
        default_ttl: int = 300,
    ):
        """Configure caching settings."""
        self.enable_caching = enabled
        if enabled and redis_url:
            self.cache_enhancer.redis_url = redis_url
            self.cache_enhancer.default_ttl = default_ttl
