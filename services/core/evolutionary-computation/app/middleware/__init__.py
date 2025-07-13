"""
Middleware modules for ACGS Evolutionary Computation Service.

This package contains middleware components for constitutional compliance,
performance monitoring, and security enforcement.
"""

from .constitutional import (
    ConstitutionalComplianceMiddleware,
    PerformanceMonitoringMiddleware,
)
from .enhanced_security import EnhancedSecurityMiddleware

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

__all__ = [
    "ConstitutionalComplianceMiddleware",
    "EnhancedSecurityMiddleware",
    "PerformanceMonitoringMiddleware",
]
