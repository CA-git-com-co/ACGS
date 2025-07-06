"""
Evolutionary Computation Service API Schemas

Request and response schemas for the evolutionary computation service API endpoints,
including validation, serialization, and constitutional compliance integration.
"""

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

from .evolution import (
    EvolutionRequestCreate,
    EvolutionRequestResponse,
    EvolutionResultResponse,
    FitnessEvaluationRequest,
    FitnessEvaluationResponse,
    PopulationResponse,
)
from .oversight import (
    OversightDecisionCreate,
    OversightDecisionResponse,
    OversightRequestCreate,
    OversightRequestResponse,
    RiskAssessmentResponse,
)
from .responses import (
    ErrorResponse,
    HealthResponse,
    StatusResponse,
    SuccessResponse,
)

__all__ = [
    "EvolutionRequestCreate",
    "EvolutionRequestResponse",
    "EvolutionResultResponse",
    "FitnessEvaluationRequest",
    "FitnessEvaluationResponse",
    "PopulationResponse",
    "OversightDecisionCreate",
    "OversightDecisionResponse",
    "OversightRequestCreate",
    "OversightRequestResponse",
    "RiskAssessmentResponse",
    "ErrorResponse",
    "HealthResponse",
    "StatusResponse",
    "SuccessResponse",
]
