"""
Middleware package for ACGS-1 PGC Service Enterprise Implementation.

This package contains middleware components for constitutional validation,
performance monitoring, and enterprise compliance.
"""

from .constitutional_validation import ConstitutionalValidationMiddleware

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


__all__ = [
    "ConstitutionalValidationMiddleware",
]
