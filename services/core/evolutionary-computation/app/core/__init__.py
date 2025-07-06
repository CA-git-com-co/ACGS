"""
Core modules for ACGS Evolutionary Computation Service.

This package contains the core components for evolutionary computation,
including evolution engine, constitutional validation, WINA oversight coordination,
and performance optimization with sub-5ms P99 latency targets.
"""

from .constitutional_validator import ConstitutionalValidator
from .evolution_engine import EvolutionEngine
from .wina_oversight_coordinator import WINAECOversightCoordinator

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

__all__ = [
    "ConstitutionalValidator",
    "EvolutionEngine",
    "WINAECOversightCoordinator",
]
