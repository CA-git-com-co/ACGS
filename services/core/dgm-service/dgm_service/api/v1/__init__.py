"""
API v1 package for DGM Service.
"""

from fastapi import APIRouter

from .dgm import router as dgm_router
from .constitutional import router as constitutional_router
from .health import router as health_router
from .integration import router as integration_router

# Create main API router
api_router = APIRouter(prefix="/api/v1")

# Include sub-routers
api_router.include_router(dgm_router, prefix="/dgm", tags=["DGM Operations"])
api_router.include_router(constitutional_router, prefix="/constitutional", tags=["Constitutional"])
api_router.include_router(health_router, prefix="", tags=["Health"])
api_router.include_router(integration_router, prefix="/integration", tags=["Service Integration"])

__all__ = ["api_router", "dgm_router", "constitutional_router", "health_router", "integration_router"]
