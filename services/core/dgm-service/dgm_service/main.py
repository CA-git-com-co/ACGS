"""
Main FastAPI application for the Darwin Gödel Machine (DGM) Service.
"""

import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from .api.v1 import constitutional_router, dgm_router, health_router, integration_router
from .config import settings
from .core.archive_manager import ArchiveManager
from .core.constitutional_validator import ConstitutionalValidator
from .core.dgm_engine import DGMEngine
from .core.performance_monitor import PerformanceMonitor
from .database import database_manager
from .integrations.gs_service_integration import GSServiceIntegration
from .integrations.performance_monitor import CrossServicePerformanceMonitor
from .integrations.trigger_manager import ImprovementTriggerManager
from .middleware.auth import AuthMiddleware
from .middleware.logging import LoggingMiddleware
from .middleware.security import SecurityMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting DGM Service...")

    # Initialize database
    await database_manager.initialize()

    # Initialize core components
    app.state.dgm_engine = DGMEngine()
    app.state.constitutional_validator = ConstitutionalValidator()
    app.state.performance_monitor = PerformanceMonitor()
    app.state.archive_manager = ArchiveManager()

    # Initialize integration components
    app.state.gs_integration = GSServiceIntegration(app.state.performance_monitor)
    app.state.cross_service_monitor = CrossServicePerformanceMonitor()
    app.state.trigger_manager = ImprovementTriggerManager()

    # Initialize integrations
    await app.state.gs_integration.initialize()
    await app.state.trigger_manager.start()

    # Start background tasks
    app.state.monitor_task = asyncio.create_task(
        app.state.performance_monitor.start_monitoring()
    )
    app.state.gs_monitor_task = asyncio.create_task(
        app.state.gs_integration.start_monitoring()
    )
    app.state.cross_service_task = asyncio.create_task(
        app.state.cross_service_monitor.start_monitoring()
    )

    logger.info("DGM Service started successfully")
    yield

    # Cleanup
    logger.info("Shutting down DGM Service...")
    app.state.monitor_task.cancel()
    app.state.gs_monitor_task.cancel()
    app.state.cross_service_task.cancel()
    await app.state.gs_integration.cleanup()
    await app.state.cross_service_monitor.stop_monitoring()
    await app.state.trigger_manager.stop()
    await database_manager.close()
    logger.info("DGM Service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Darwin Gödel Machine Service",
    description="Self-improving AI system with constitutional governance compliance",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT == "development" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT == "development" else None,
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.ALLOWED_HOSTS)

app.add_middleware(SecurityMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(LoggingMiddleware)

# Initialize Prometheus metrics
instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=["/health", "/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="dgm_requests_inprogress",
    inprogress_labels=True,
)

instrumentator.instrument(app).expose(app)

# Include routers
app.include_router(health_router, prefix="", tags=["Health"])
app.include_router(dgm_router, prefix="/api/v1/dgm", tags=["DGM Operations"])
app.include_router(
    constitutional_router, prefix="/api/v1/constitutional", tags=["Constitutional"]
)
app.include_router(
    integration_router, prefix="/api/v1/integration", tags=["Service Integration"]
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": getattr(request.state, "request_id", None),
        },
    )


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Darwin Gödel Machine Service",
        "version": "1.0.0",
        "status": "operational",
        "description": "Self-improving AI system with constitutional governance compliance",
        "endpoints": {
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs" if settings.ENVIRONMENT == "development" else "disabled",
            "api": "/api/v1",
        },
    }


def main():
    """Main entry point for the service."""
    uvicorn.run(
        "dgm_service.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.ENVIRONMENT == "development",
        log_level=settings.LOG_LEVEL.lower(),
        access_log=True,
        workers=1 if settings.ENVIRONMENT == "development" else settings.WORKERS,
    )


if __name__ == "__main__":
    main()
