# backend/auth_service/app/api/v1/__init__.py
from . import api_router, deps, endpoints

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


__all__ = ["api_router", "deps", "endpoints"]
