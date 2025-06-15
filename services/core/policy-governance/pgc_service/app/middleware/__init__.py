"""
Middleware package for ACGS-1 PGC Service Enterprise Implementation.

This package contains middleware components for constitutional validation,
performance monitoring, and enterprise compliance.
"""

from .constitutional_validation import ConstitutionalValidationMiddleware

__all__ = [
    "ConstitutionalValidationMiddleware",
]