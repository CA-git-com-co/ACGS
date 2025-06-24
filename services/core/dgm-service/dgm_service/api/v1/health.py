"""
Health check endpoints for DGM Service.
"""

import time
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from ...config import settings
from ...database import database_manager
from ...network.service_client import ACGSServiceClient
from .models import HealthResponse, SystemStatus

router = APIRouter()

# Track service start time for uptime calculation
_start_time = time.time()


async def get_service_client() -> ACGSServiceClient:
    """Dependency to get service client."""
    return ACGSServiceClient()


@router.get("/health", response_model=HealthResponse)
async def health_check(service_client: ACGSServiceClient = Depends(get_service_client)):
    """
    Comprehensive health check endpoint.

    Checks:
    - Service availability
    - Database connectivity
    - Redis connectivity
    - ACGS service dependencies
    """
    try:
        # Calculate uptime
        uptime = time.time() - _start_time

        # Check database health
        db_healthy = await database_manager.health_check()

        # Check ACGS services health
        acgs_health = await service_client.check_all_services_health()

        # Determine overall health status
        all_dependencies_healthy = db_healthy and all(acgs_health.values())
        overall_status = "healthy" if all_dependencies_healthy else "degraded"

        # Prepare dependency status
        dependencies = {"database": db_healthy, **acgs_health}

        response = HealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            version="1.0.0",
            uptime=uptime,
            dependencies=dependencies,
        )

        # Return appropriate HTTP status
        status_code = (
            status.HTTP_200_OK if all_dependencies_healthy else status.HTTP_503_SERVICE_UNAVAILABLE
        )

        return JSONResponse(content=response.dict(), status_code=status_code)

    except Exception as e:
        # Return unhealthy status on any exception
        return JSONResponse(
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0.0",
                "uptime": time.time() - _start_time,
                "error": str(e),
                "dependencies": {},
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


@router.get("/health/live")
async def liveness_probe():
    """
    Kubernetes liveness probe endpoint.

    Simple check that the service is running.
    """
    return {"status": "alive", "timestamp": datetime.utcnow()}


@router.get("/health/ready")
async def readiness_probe():
    """
    Kubernetes readiness probe endpoint.

    Checks if the service is ready to accept traffic.
    """
    try:
        # Check critical dependencies
        db_healthy = await database_manager.health_check()

        if not db_healthy:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Database not available"
            )

        return {"status": "ready", "timestamp": datetime.utcnow()}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Service not ready: {str(e)}"
        )


@router.get("/status", response_model=SystemStatus)
async def system_status():
    """
    Detailed system status endpoint.

    Provides comprehensive information about the DGM service state.
    """
    try:
        # Get basic system info
        uptime = time.time() - _start_time

        # TODO: Get actual metrics from database
        # For now, return mock data
        active_improvements = 0
        total_improvements = 0
        average_compliance_score = 0.85
        last_improvement = None

        # Get system health details
        db_healthy = await database_manager.health_check()

        system_health = {
            "database": {
                "status": "healthy" if db_healthy else "unhealthy",
                "connection_pool": await _get_db_pool_stats(),
            },
            "memory": await _get_memory_stats(),
            "cpu": await _get_cpu_stats(),
        }

        return SystemStatus(
            service_name="dgm-service",
            version="1.0.0",
            status="operational",
            uptime=uptime,
            active_improvements=active_improvements,
            total_improvements=total_improvements,
            average_compliance_score=average_compliance_score,
            last_improvement=last_improvement,
            system_health=system_health,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system status: {str(e)}",
        )


async def _get_db_pool_stats() -> Dict[str, Any]:
    """Get database connection pool statistics."""
    try:
        if database_manager.engine and database_manager.engine.pool:
            pool = database_manager.engine.pool
            return {
                "size": pool.size(),
                "checked_in": pool.checkedin(),
                "checked_out": pool.checkedout(),
                "overflow": pool.overflow(),
                "invalid": pool.invalid(),
            }
    except Exception:
        pass

    return {"status": "unavailable"}


async def _get_memory_stats() -> Dict[str, Any]:
    """Get memory usage statistics."""
    try:
        import psutil

        process = psutil.Process()
        memory_info = process.memory_info()

        return {"rss": memory_info.rss, "vms": memory_info.vms, "percent": process.memory_percent()}
    except ImportError:
        return {"status": "psutil not available"}
    except Exception:
        return {"status": "unavailable"}


async def _get_cpu_stats() -> Dict[str, Any]:
    """Get CPU usage statistics."""
    try:
        import psutil

        process = psutil.Process()

        return {"percent": process.cpu_percent(), "num_threads": process.num_threads()}
    except ImportError:
        return {"status": "psutil not available"}
    except Exception:
        return {"status": "unavailable"}
