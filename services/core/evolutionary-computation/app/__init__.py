"""
ACGS Evolutionary Computation Service Application

Main application package for the evolutionary computation service with
constitutional compliance, WINA optimization, and ACGS integration.
"""

from .api.v1 import v1_router
from .core import (
    ConstitutionalValidator,
    EvolutionEngine,
    WINAECOversightCoordinator,
)
from .middleware import (
    ConstitutionalComplianceMiddleware,
    PerformanceMonitoringMiddleware,
)
from .models import EvolutionRequest, EvolutionResult, Individual, Population
from .services import EvolutionService, FitnessService, HITLService

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

__all__ = [
    "ConstitutionalComplianceMiddleware",
    "ConstitutionalValidator",
    "EvolutionEngine",
    "EvolutionRequest",
    "EvolutionResult",
    "EvolutionService",
    "FitnessService",
    "HITLService",
    "Individual",
    "PerformanceMonitoringMiddleware",
    "Population",
    "WINAECOversightCoordinator",
    "v1_router",
]
