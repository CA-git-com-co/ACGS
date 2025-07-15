"""
Constitutional Governance API Layer
Constitutional Hash: cdd01ef066bc6cf2

API layer for constitutional governance bounded context providing
REST endpoints for constitutional management operations.
"""

from .controllers import (
    AmendmentProposalController,
    ConstitutionController,
    PrincipleController,
)
from .dependencies import (
    get_constitutional_governance_service,
    get_constitutional_query_service,
)
from .schemas import (
    AmendmentProposalCreateRequest,
    AmendmentProposalResponse,
    ConstitutionResponse,
    PrincipleCreateRequest,
    PrincipleResponse,
)

__all__ = [
    # Controllers
    "AmendmentProposalController",
    "ConstitutionController",
    "PrincipleController",
    # Dependencies
    "get_constitutional_governance_service",
    "get_constitutional_query_service",
    # Schemas
    "AmendmentProposalCreateRequest",
    "AmendmentProposalResponse",
    "ConstitutionResponse",
    "PrincipleCreateRequest",
    "PrincipleResponse",
]
