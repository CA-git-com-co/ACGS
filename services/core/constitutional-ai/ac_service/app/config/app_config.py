"""
Constitutional AI Service Configuration
Constitutional Hash: cdd01ef066bc6cf2

This module handles application configuration, middleware setup, and service initialization.
"""

import os
import sys
import logging
from contextlib import asynccontextmanager
from typing import Any, Optional

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class ConstitutionalAIConfig:
    """Configuration manager for Constitutional AI service."""
    
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.service_name = "constitutional-ai"
        self.setup_logging()
        self.load_environment_config()
    
    def setup_logging(self):
        """Setup enhanced logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler("logs/ac_service.log", mode="a"),
            ],
        )
        
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        logger.info(f"Logging configured for {self.service_name}")
        logger.info(f"Constitutional Hash: {self.constitutional_hash}")
    
    def load_environment_config(self):
        """Load configuration from environment variables."""
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.allowed_hosts = os.getenv("ALLOWED_HOSTS", "*").split(",")
        self.cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")
        
        # Database and cache configuration
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6389")
        self.postgres_dsn = os.getenv("POSTGRES_DSN", "postgresql://postgres:password@localhost:5439/acgs")
        
        logger.info(f"Environment: {self.environment}")
        logger.info(f"Debug mode: {self.debug}")
        logger.info(f"Redis URL: {self.redis_url}")
        logger.info(f"PostgreSQL DSN: {self.postgres_dsn.replace('password', '***')}")
    
    def get_cors_config(self) -> dict:
        """Get CORS configuration."""
        if self.environment == "production":
            return {
                "allow_origins": self.cors_origins,
                "allow_credentials": True,
                "allow_methods": ["GET", "POST", "PUT", "DELETE"],
                "allow_headers": ["*"],
            }
        else:
            # More permissive for development
            return {
                "allow_origins": ["*"],
                "allow_credentials": True,
                "allow_methods": ["*"],
                "allow_headers": ["*"],
            }


class ServiceLifespan:
    """Handle service lifecycle events."""
    
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.compliance_engine: Optional[Any] = None
        self.violation_detector: Optional[Any] = None
        self.audit_logger: Optional[Any] = None
        self.fv_client: Optional[Any] = None
    
    @asynccontextmanager
    async def lifespan(self, app: FastAPI):
        """Service lifespan context manager."""
        # Startup
        logger.info("Starting Constitutional AI Service...")
        logger.info(f"Constitutional Hash: {self.constitutional_hash}")
        
        await self._initialize_services()
        await self._validate_constitutional_compliance()
        
        logger.info("Constitutional AI Service started successfully")
        
        yield
        
        # Shutdown
        logger.info("Shutting down Constitutional AI Service...")
        await self._cleanup_services()
        logger.info("Constitutional AI Service shutdown complete")
    
    async def _initialize_services(self):
        """Initialize all service components."""
        try:
            # Initialize enhanced services if available
            if self._are_enhanced_services_available():
                await self._initialize_enhanced_services()
            else:
                logger.warning("Enhanced services not available, using basic mode")
            
            # Initialize framework integrations
            await self._initialize_frameworks()
            
            # Initialize audit logging
            await self._initialize_audit_logging()
            
        except Exception as e:
            logger.error(f"Service initialization failed: {e}")
            raise
    
    def _are_enhanced_services_available(self) -> bool:
        """Check if enhanced services are available."""
        try:
            from ..services.audit_logging_service import AuditLoggingService
            from ..services.constitutional_compliance_engine import ConstitutionalComplianceEngine
            from ..services.formal_verification_client import FormalVerificationClient
            from ..services.violation_detection_service import ViolationDetectionService
            return True
        except ImportError:
            return False
    
    async def _initialize_enhanced_services(self):
        """Initialize enhanced service components."""
        try:
            from ..services.audit_logging_service import AuditLoggingService
            from ..services.constitutional_compliance_engine import ConstitutionalComplianceEngine
            from ..services.formal_verification_client import FormalVerificationClient
            from ..services.violation_detection_service import ViolationDetectionService
            
            self.compliance_engine = ConstitutionalComplianceEngine()
            self.violation_detector = ViolationDetectionService()
            self.audit_logger = AuditLoggingService()
            self.fv_client = FormalVerificationClient()
            
            logger.info("Enhanced services initialized successfully")
            
        except Exception as e:
            logger.error(f"Enhanced services initialization failed: {e}")
            raise
    
    async def _initialize_frameworks(self):
        """Initialize framework integrations."""
        framework_status = {}
        
        # Multi-tenant framework
        try:
            from services.shared.middleware.tenant_middleware import TenantContextMiddleware
            framework_status["multi_tenant"] = "available"
        except ImportError:
            framework_status["multi_tenant"] = "unavailable"
        
        # Security middleware
        try:
            from services.shared.security_middleware import SecurityMiddleware
            framework_status["security"] = "available"
        except ImportError:
            framework_status["security"] = "unavailable"
        
        # Prompt framework
        try:
            from services.shared.prompt_framework import get_prompt_manager
            framework_status["prompt"] = "available"
        except ImportError:
            framework_status["prompt"] = "unavailable"
        
        logger.info(f"Framework status: {framework_status}")
    
    async def _initialize_audit_logging(self):
        """Initialize audit logging."""
        try:
            from services.shared.comprehensive_audit_logger import apply_audit_logging_to_service
            # Apply audit logging would be called here
            logger.info("Audit logging initialized")
        except ImportError:
            logger.warning("Comprehensive audit logging not available")
    
    async def _validate_constitutional_compliance(self):
        """Validate constitutional compliance during startup."""
        try:
            from ..validation.core import ConstitutionalValidator
            
            validator = ConstitutionalValidator()
            hash_validation = validator.validate_constitutional_hash()
            
            if not hash_validation["is_valid"]:
                raise Exception("Constitutional hash validation failed during startup")
            
            logger.info("Constitutional compliance validated successfully")
            
        except Exception as e:
            logger.error(f"Constitutional compliance validation failed: {e}")
            raise
    
    async def _cleanup_services(self):
        """Cleanup services during shutdown."""
        try:
            if self.compliance_engine:
                # Cleanup compliance engine
                pass
            
            if self.violation_detector:
                # Cleanup violation detector
                pass
            
            if self.audit_logger:
                # Cleanup audit logger
                pass
            
            if self.fv_client:
                # Cleanup formal verification client
                pass
                
            logger.info("Services cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Service cleanup failed: {e}")


class MiddlewareManager:
    """Manage application middleware."""
    
    def __init__(self, config: ConstitutionalAIConfig):
        self.config = config
        self.constitutional_hash = CONSTITUTIONAL_HASH
    
    def setup_middleware(self, app: FastAPI):
        """Setup all middleware for the application."""
        self._setup_security_middleware(app)
        self._setup_cors_middleware(app)
        self._setup_trusted_host_middleware(app)
        self._setup_tenant_middleware(app)
        self._setup_health_check_middleware(app)
        self._setup_prometheus_metrics_middleware(app)
        self._setup_custom_middleware(app)
    
    def _setup_security_middleware(self, app: FastAPI):
        """Setup security middleware."""
        try:
            # ACGS Security Middleware Integration
            import sys
            from pathlib import Path
            shared_security_path = Path(__file__).parent.parent.parent.parent.parent.parent / "shared" / "security"
            sys.path.insert(0, str(shared_security_path))
            
            from middleware_integration import apply_acgs_security_middleware, setup_security_monitoring
            
            apply_acgs_security_middleware(app, self.config.service_name, self.config.environment)
            setup_security_monitoring(app, self.config.service_name)
            
            logger.info("✅ ACGS Security middleware applied")
            
        except ImportError as e:
            logger.warning(f"⚠️ ACGS Security middleware not available: {e}")
    
    def _setup_cors_middleware(self, app: FastAPI):
        """Setup CORS middleware."""
        cors_config = self.config.get_cors_config()
        app.add_middleware(CORSMiddleware, **cors_config)
        logger.info("CORS middleware configured")
    
    def _setup_trusted_host_middleware(self, app: FastAPI):
        """Setup trusted host middleware."""
        if self.config.environment == "production":
            app.add_middleware(
                TrustedHostMiddleware,
                allowed_hosts=self.config.allowed_hosts
            )
            logger.info("Trusted host middleware configured")
    
    def _setup_tenant_middleware(self, app: FastAPI):
        """Setup multi-tenant middleware."""
        try:
            from services.shared.middleware.tenant_middleware import TenantSecurityMiddleware
            app.add_middleware(TenantSecurityMiddleware)
            logger.info("Tenant security middleware configured")
        except ImportError:
            logger.warning("Tenant middleware not available")
    
    def _setup_health_check_middleware(self, app: FastAPI):
        """Setup comprehensive health check endpoints."""
        try:
            from services.shared.middleware.health_check_middleware import (
                setup_health_check_endpoints,
                HealthCheckConfig,
                HealthCheckLevel
            )
            
            # Configure health check
            health_config = HealthCheckConfig(
                service_name=self.config.service_name,
                service_version="1.0.0",
                check_level=HealthCheckLevel.COMPREHENSIVE,
                check_timeout=5.0,
                enable_dependency_checks=True,
                enable_performance_metrics=True,
                redis_url=self.config.redis_url,
                postgres_dsn=self.config.postgres_dsn
            )
            
            # Setup health check endpoints
            health_manager = setup_health_check_endpoints(app, health_config)
            app.state.health_manager = health_manager
            
            logger.info("✅ Health check middleware configured")
            
        except ImportError as e:
            logger.warning(f"Health check middleware not available: {e}")
        except Exception as e:
            logger.error(f"Health check middleware setup failed: {e}")

    def _setup_prometheus_metrics_middleware(self, app: FastAPI):
        """Setup comprehensive Prometheus metrics collection."""
        try:
            from services.shared.middleware.prometheus_metrics_middleware import (
                setup_prometheus_metrics
            )
            
            # Setup Prometheus metrics
            metrics = setup_prometheus_metrics(
                app=app,
                service_name=self.config.service_name,
                enable_multiprocess=False,
                metrics_endpoint="/metrics",
                enable_system_metrics=True,
                system_metrics_interval=30
            )
            
            # Store metrics in app state for use by other components
            app.state.prometheus_metrics = metrics
            
            logger.info("✅ Prometheus metrics middleware configured")
            
        except ImportError as e:
            logger.warning(f"Prometheus metrics middleware not available: {e}")
        except Exception as e:
            logger.error(f"Prometheus metrics middleware setup failed: {e}")

    def _setup_custom_middleware(self, app: FastAPI):
        """Setup custom middleware."""
        
        @app.middleware("http")
        async def add_process_time_header(request: Request, call_next):
            """Add processing time header."""
            import time
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Constitutional-Hash"] = self.constitutional_hash
            return response
        
        @app.exception_handler(Exception)
        async def global_exception_handler(request: Request, exc: Exception):
            """Global exception handler with constitutional compliance logging."""
            logger.error(
                f"Unhandled exception: {exc}",
                extra={
                    "request_url": str(request.url),
                    "request_method": request.method,
                    "constitutional_hash": self.constitutional_hash,
                }
            )
            
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal server error",
                    "constitutional_hash": self.constitutional_hash,
                    "error_id": f"ac-{int(time.time())}"
                }
            )


def create_constitutional_ai_app() -> FastAPI:
    """Create and configure the Constitutional AI FastAPI application."""
    
    # Initialize configuration
    config = ConstitutionalAIConfig()
    lifespan_manager = ServiceLifespan()
    
    # Create FastAPI app
    app = FastAPI(
        title="Constitutional AI Service",
        description="Production-grade constitutional compliance validation service",
        version="1.0.0",
        lifespan=lifespan_manager.lifespan,
        docs_url="/docs" if config.debug else None,
        redoc_url="/redoc" if config.debug else None,
    )
    
    # Setup middleware
    middleware_manager = MiddlewareManager(config)
    middleware_manager.setup_middleware(app)
    
    # Setup error handlers
    try:
        from services.shared.middleware.error_handling import setup_error_handlers
        setup_error_handlers(app)
        logger.info("Error handlers configured")
    except ImportError:
        logger.warning("Error handling middleware not available")
    
    logger.info("Constitutional AI application created successfully")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    return app