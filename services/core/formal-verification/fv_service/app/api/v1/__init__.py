
from fastapi import APIRouter
from .formal_verification import router as formal_verification_router
from .proof_pipeline import router as proof_pipeline_router
from .verify import router as verify_router
from .cross_domain_testing import router as cross_domain_router

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Create main v1 API router
v1_router = APIRouter(prefix="/v1")

# Include all routers
v1_router.include_router(formal_verification_router)
v1_router.include_router(proof_pipeline_router)
v1_router.include_router(verify_router)
v1_router.include_router(cross_domain_router)

# FV Service API v1 Package
