#!/usr/bin/env python3
"""
ACGS Code Analysis Engine - Main Application
FastAPI application providing intelligent code analysis, semantic search, and dependency mapping.

Constitutional Hash: cdd01ef066bc6cf2
Service Port: 8007
"""

import logging
import pathlib
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

# Add the service directory to Python path
sys.path.insert(0, pathlib.Path(pathlib.Path(__file__).resolve()).parent)

from app.api.v1.router import api_router
from app.core.file_watcher import FileWatcherService
from app.core.indexer import IndexerService
from app.middleware.auth import AuthenticationMiddleware
from app.middleware.constitutional import ConstitutionalComplianceMiddleware
from app.middleware.performance import PerformanceMiddleware
from app.services.cache_service import CacheService
from app.services.registry_service import ServiceRegistryClient
from app.utils.constitutional import CONSTITUTIONAL_HASH
from app.utils.logging import setup_logging
from config.database import DatabaseManager
from config.settings import get_settings

# Initialize settings
settings = get_settings()

# Setup logging
setup_logging(
    log_level=settings.log_level,
    log_format="json" if settings.structured_logging else "text",
)

logger = logging.getLogger(__name__)

# Global service instances
db_manager: DatabaseManager = None
cache_service: CacheService = None
registry_client: ServiceRegistryClient = None
file_watcher: FileWatcherService = None
indexer_service: IndexerService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global db_manager, cache_service, registry_client, file_watcher, indexer_service

    logger.info("Starting ACGS Code Analysis Engine...")

    try:
        # Initialize database manager
        try:
            db_manager = DatabaseManager(
                host=settings.postgresql_host,
                port=settings.postgresql_port,
                database=settings.postgresql_database,
                username=settings.postgresql_user,
                password=settings.postgresql_password,
            )
            await db_manager.connect()
            logger.info("Database connection established")
        except Exception as e:
            logger.warning(f"Database connection failed: {e}")
            db_manager = None

        # Initialize cache service
        try:
            cache_service = CacheService(redis_url=settings.redis_url)
            await cache_service.connect()
            logger.info("Cache service connected")
        except Exception as e:
            logger.warning(f"Cache service connection failed: {e}")
            cache_service = None

        # Initialize service registry client
        try:
            registry_client = ServiceRegistryClient(
                registry_url=str(settings.service_registry_url),
                service_name="acgs-code-analysis-engine",
                service_port=settings.port,
            )
            logger.info("Service registry client initialized")

            # Register this service
            await registry_client.register_service()
            logger.info(f"Service registered on port {settings.port}")
        except Exception as e:
            logger.warning(f"Service registry connection failed: {e}")
            registry_client = None

        # Initialize indexer service
        try:
            if db_manager and cache_service:
                indexer_service = IndexerService(
                    db_manager=db_manager, cache_service=cache_service
                )
                await indexer_service.initialize()
                logger.info("Indexer service initialized")
            else:
                logger.warning("Indexer service skipped - missing dependencies")
                indexer_service = None
        except Exception as e:
            logger.warning(f"Indexer service initialization failed: {e}")
            indexer_service = None

        # Initialize and start file watcher
        try:
            if indexer_service:
                file_watcher = FileWatcherService(
                    watch_paths=settings.watch_paths, indexer_service=indexer_service
                )
                await file_watcher.start()
                logger.info(f"File watcher started for paths: {settings.watch_paths}")
            else:
                logger.warning("File watcher skipped - missing indexer service")
                file_watcher = None
        except Exception as e:
            logger.warning(f"File watcher initialization failed: {e}")
            file_watcher = None

        # Store services in app state for access in endpoints
        app.state.db_manager = db_manager
        app.state.cache_service = cache_service
        app.state.registry_client = registry_client
        app.state.indexer_service = indexer_service
        app.state.file_watcher = file_watcher

        logger.info("ACGS Code Analysis Engine startup completed successfully")

        yield

    except Exception as e:
        logger.exception(f"Failed to start ACGS Code Analysis Engine: {e}")
        raise

    finally:
        # Cleanup on shutdown
        logger.info("Shutting down ACGS Code Analysis Engine...")

        try:
            if file_watcher:
                await file_watcher.stop()
                logger.info("File watcher stopped")

            if registry_client:
                await registry_client.deregister_service()
                await registry_client.http_client.aclose()
                logger.info("Service deregistered")

            if cache_service:
                await cache_service.disconnect()
                logger.info("Cache service closed")

            if db_manager:
                await db_manager.disconnect()
                logger.info("Database connections closed")

        except Exception as e:
            logger.exception(f"Error during shutdown: {e}")

        logger.info("ACGS Code Analysis Engine shutdown completed")


# Create FastAPI application
app = FastAPI(
    title="ACGS Code Analysis Engine",
    description="""
    Intelligent code analysis, semantic search, and dependency mapping service
    for the AI Constitutional Governance System (ACGS).

    ## Features
    - **Semantic Code Search**: Vector-based similarity search using CodeBERT
    - **Symbol Analysis**: Comprehensive code symbol extraction and metadata
    - **Dependency Mapping**: Real-time dependency graph construction
    - **Context Integration**: Bidirectional integration with ACGS Context Service
    - **Constitutional Compliance**: Full ACGS governance framework integration

    ## Performance Targets
    - P99 Latency: <10ms for cached queries
    - Throughput: >100 RPS sustained load
    - Cache Hit Rate: >85% for repeated queries

    Constitutional Hash: cdd01ef066bc6cf2
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url=(
        "/docs"
        if settingsconfig / environments / development.environment != "production"
        else None
    ),
    redoc_url=(
        "/redoc"
        if settingsconfig / environments / development.environment != "production"
        else None
    ),
    openapi_url=(
        "/openapi.json"
        if settingsconfig / environments / development.environment != "production"
        else None
    ),
)

# Add middleware in correct order (last added = first executed)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Constitutional compliance middleware
app.add_middleware(ConstitutionalComplianceMiddleware)

# Performance monitoring middleware
app.add_middleware(PerformanceMiddleware)

# Authentication middleware (applied to protected routes)
app.add_middleware(
    AuthenticationMiddleware,
    auth_service_url=str(settings.auth_service_url),
    excluded_paths=["/health", "/metrics", "/docs", "/redoc", "/openapi.json"],
)

# Prometheus metrics
if settings.prometheus_enabled:
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics"],
        env_var_name="ENABLE_METRICS",
        inprogress_name="acgs_code_analysis_inprogress",
        inprogress_labels=True,
    )

    instrumentator.instrument(app).expose(app, endpoint="/metrics")

# Include API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Service health check endpoint.
    Returns the health status of the Code Analysis Engine and its dependencies.
    """
    try:
        health_status = {
            "status": "healthy",
            "service": "acgs-code-analysis-engine",
            "version": "1.0.0",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "checks": {},
            "uptime_seconds": 0,
            "last_analysis_job": None,
        }

        # Check database connectivity
        if hasattr(app.state, "db_manager") and app.state.db_manager:
            db_healthy = await app.state.db_manager.health_check()
            health_status["checks"]["database"] = "ok" if db_healthy else "failed"
        else:
            health_status["checks"]["database"] = "not_initialized"

        # Check cache connectivity
        if hasattr(app.state, "cache_service") and app.state.cache_service:
            cache_healthy = await app.state.cache_service.health_check()
            health_status["checks"]["cache"] = "ok" if cache_healthy else "failed"
        else:
            health_status["checks"]["cache"] = "not_initialized"

        # Check service registry
        if hasattr(app.state, "registry_client") and app.state.registry_client:
            registry_healthy = await app.state.registry_client.health_check()
            health_status["checks"]["service_registry"] = (
                "ok" if registry_healthy else "failed"
            )
        else:
            health_status["checks"]["service_registry"] = "not_initialized"

        # Check file watcher
        if hasattr(app.state, "file_watcher") and app.state.file_watcher:
            watcher_healthy = app.state.file_watcher.is_running()
            health_status["checks"]["file_watcher"] = (
                "ok" if watcher_healthy else "failed"
            )
        else:
            health_status["checks"]["file_watcher"] = "not_initialized"

        # Determine overall health
        failed_checks = [k for k, v in health_status["checks"].items() if v == "failed"]
        not_initialized_checks = [
            k for k, v in health_status["checks"].items() if v == "not_initialized"
        ]

        if failed_checks:
            health_status["status"] = (
                "degraded"
                if len(failed_checks) < len(health_status["checks"])
                else "unhealthy"
            )
            return JSONResponse(
                status_code=503 if health_status["status"] == "unhealthy" else 200,
                content=health_status,
            )
        if not_initialized_checks:
            health_status["status"] = "degraded"
            health_status["message"] = (
                f"Some services not initialized: {', '.join(not_initialized_checks)}"
            )

        return JSONResponse(status_code=200, content=health_status)

    except Exception as e:
        logger.exception(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "service": "acgs-code-analysis-engine",
                "error": str(e),
                "constitutional_hash": CONSTITUTIONAL_HASH,
            },
        )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with constitutional compliance"""
    logger.error(f"Unhandled exception: {exc}")

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An internal server error occurred",
            "details": (
                {"type": type(exc).__name__}
                if settingsconfig / environments / development.environment
                != "production"
                else {}
            ),
            "timestamp": "2024-01-15T10:30:00Z",  # Would use actual timestamp
            "request_id": getattr(request.state, "request_id", "unknown"),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        },
    )


def main():
    """Main entry point for the application"""
    # Configure uvicorn
    uvicorn_config = {
        "app": "main:app",
        "host": settings.host,
        "port": settings.port,
        "workers": (
            settings.workers
            if settingsconfig / environments / development.environment == "production"
            else 1
        ),
        "log_level": settings.log_level.lower(),
        "access_log": settings.access_log,
        "reload": settingsconfig / environments / development.environment
        == "development",
        "reload_dirs": (
            ["app", "config"]
            if settingsconfig / environments / development.environment == "development"
            else None
        ),
    }

    # Add SSL configuration for production
    if (
        settingsconfig / environments / development.environment == "production"
        and settings.ssl_cert_file
    ):
        uvicorn_config.update(
            {
                "ssl_certfile": settings.ssl_cert_file,
                "ssl_keyfile": settings.ssl_key_file,
            }
        )

    logger.info(
        f"Starting ACGS Code Analysis Engine on {settings.host}:{settings.port}"
    )
    logger.info(f"Environment: {settingsconfig/environments/development.environment}")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")

    # Start the server
    uvicorn.run(**uvicorn_config)


if __name__ == "__main__":
    main()
