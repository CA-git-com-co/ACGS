"""
API v1 modules for ACGS Evolutionary Computation Service.

This package contains API v1 endpoints for evolutionary computation operations,
oversight management, monitoring, and reporting with constitutional compliance.
"""

from fastapi import APIRouter

from . import (
    alphaevolve,
    evolution,
    monitoring,
    oversight,
    reporting,
    wina_oversight,
)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Create main v1 router
v1_router = APIRouter(prefix="/api/v1")

# Include all sub-routers
v1_router.include_router(evolution.router)
v1_router.include_router(oversight.router)
v1_router.include_router(monitoring.router)
v1_router.include_router(reporting.router)
v1_router.include_router(alphaevolve.router)
v1_router.include_router(wina_oversight.router)

__all__ = [
    "v1_router",
    "alphaevolve",
    "evolution",
    "monitoring",
    "oversight",
    "reporting",
    "wina_oversight",
]
