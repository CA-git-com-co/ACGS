"""
Sandbox Execution Service Main Application

FastAPI application for secure code execution in isolated environments.
"""

import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.execution import router as execution_router
from .core.config import settings
from .services.sandbox_manager import SandboxManager

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global sandbox manager instance
sandbox_manager = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global sandbox_manager

    # Startup
    logger.info(f"Starting {settings.SERVICE_NAME} v{settings.SERVICE_VERSION}")
    sandbox_manager = SandboxManager()

    # Verify Docker is available
    try:
        sandbox_manager.docker_client.ping()
        logger.info("Docker connection verified")
    except Exception as e:
        logger.error(f"Docker connection failed: {e}")
        raise RuntimeError("Docker is not available - cannot start sandbox service")

    yield

    # Shutdown
    if sandbox_manager:
        sandbox_manager.close()
    logger.info("Sandbox Execution Service shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Sandbox Execution Service",
    description="Secure code execution service for autonomous agents with Docker-based isolation",
    version=settings.SERVICE_VERSION,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": (
                str(request.state.timestamp)
                if hasattr(request.state, "timestamp")
                else None
            ),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """General exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "status_code": 500,
        },
    )


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    request.state.timestamp = start_time

    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)

    return response


# Include routers
app.include_router(execution_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "status": "healthy",
        "constitutional_hash": settings.CONSTITUTIONAL_HASH,
        "supported_environments": ["python", "bash", "node"],
        "docker_available": True,
        "endpoints": {
            "create_execution": "/api/v1/executions",
            "list_executions": "/api/v1/executions",
            "get_execution": "/api/v1/executions/{execution_id}",
            "kill_execution": "/api/v1/executions/{execution_id}/kill",
            "execution_stats": "/api/v1/executions/stats/summary",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health_status = {
        "status": "healthy",
        "timestamp": str(time.time()),
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "checks": {
            "docker": False,
            "disk_space": False,
            "memory": False,
        },
    }

    # Check Docker connectivity
    try:
        if sandbox_manager:
            sandbox_manager.docker_client.ping()
            health_status["checks"]["docker"] = True
    except Exception as e:
        logger.warning(f"Docker health check failed: {e}")

    # Check disk space (simplified)
    try:
        import shutil

        disk_usage = shutil.disk_usage("/tmp")
        free_gb = disk_usage.free / (1024**3)
        health_status["checks"]["disk_space"] = free_gb > 1.0  # At least 1GB free
        health_status["disk_free_gb"] = round(free_gb, 2)
    except Exception as e:
        logger.warning(f"Disk space check failed: {e}")

    # Check memory (simplified)
    try:
        import psutil

        memory = psutil.virtual_memory()
        health_status["checks"]["memory"] = memory.percent < 90  # Less than 90% used
        health_status["memory_usage_percent"] = memory.percent
    except Exception as e:
        logger.warning(f"Memory check failed: {e}")

    # Overall health status
    all_checks_pass = all(health_status["checks"].values())
    if not all_checks_pass:
        health_status["status"] = "degraded"

    status_code = 200 if all_checks_pass else 503
    return JSONResponse(content=health_status, status_code=status_code)


@app.get("/metrics")
async def get_metrics():
    """Get service metrics."""
    metrics = {
        "service": settings.SERVICE_NAME,
        "metrics": {
            "active_containers": (
                len(sandbox_manager.active_containers) if sandbox_manager else 0
            ),
            "total_executions": 0,  # Would come from database
            "successful_executions": 0,
            "failed_executions": 0,
            "avg_execution_time_ms": 0.0,
        },
        "docker_info": {},
    }

    # Get Docker system info
    try:
        if sandbox_manager:
            docker_info = sandbox_manager.docker_client.info()
            metrics["docker_info"] = {
                "containers_running": docker_info.get("ContainersRunning", 0),
                "containers_paused": docker_info.get("ContainersPaused", 0),
                "containers_stopped": docker_info.get("ContainersStopped", 0),
                "images": docker_info.get("Images", 0),
                "server_version": docker_info.get("ServerVersion", "unknown"),
            }
    except Exception as e:
        logger.warning(f"Failed to get Docker info: {e}")

    return metrics


@app.get("/environments")
async def get_supported_environments():
    """Get information about supported execution environments."""
    environments = {
        "python": {
            "image": settings.PYTHON_BASE_IMAGE,
            "description": "Python 3.11 execution environment",
            "supported_extensions": [".py"],
            "default_timeout": 120,
            "default_memory_limit_mb": 256,
        },
        "bash": {
            "image": settings.BASH_BASE_IMAGE,
            "description": "Bash shell execution environment",
            "supported_extensions": [".sh", ".bash"],
            "default_timeout": 60,
            "default_memory_limit_mb": 128,
        },
        "node": {
            "image": settings.NODE_BASE_IMAGE,
            "description": "Node.js execution environment",
            "supported_extensions": [".js", ".mjs"],
            "default_timeout": 90,
            "default_memory_limit_mb": 256,
        },
    }

    return {
        "environments": environments,
        "security_features": [
            "Network isolation",
            "File system restrictions",
            "Resource limits",
            "Read-only root filesystem",
            "Dropped capabilities",
            "Seccomp filtering",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
