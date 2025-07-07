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
    "v1_router",
    "ConstitutionalValidator",
    "EvolutionEngine",
    "WINAECOversightCoordinator",
    "ConstitutionalComplianceMiddleware",
    "PerformanceMonitoringMiddleware",
    "EvolutionRequest",
    "EvolutionResult",
    "Individual",
    "Population",
    "EvolutionService",
    "FitnessService",
    "HITLService",
]
