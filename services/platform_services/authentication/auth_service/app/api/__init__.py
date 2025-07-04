# backend/auth_service/app/api/__init__.py
from . import v1

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


__all__ = ["v1"]
