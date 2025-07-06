"""
Evolutionary Computation Service Data Models

Core data models for evolution requests, fitness evaluation, oversight coordination,
and constitutional compliance in the ACGS evolutionary computation framework.
"""

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

from .evolution import (
    EvolutionRequest,
    EvolutionResult,
    EvolutionStatus,
    EvolutionType,
    FitnessMetrics,
    Individual,
    Population,
)
from .oversight import (
    HumanReviewTask,
    OversightDecision,
    OversightLevel,
    OversightRequest,
    RiskAssessment,
)

__all__ = [
    "EvolutionRequest",
    "EvolutionResult", 
    "EvolutionStatus",
    "EvolutionType",
    "FitnessMetrics",
    "Individual",
    "Population",
    "HumanReviewTask",
    "OversightDecision",
    "OversightLevel",
    "OversightRequest",
    "RiskAssessment",
]
