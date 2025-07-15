"""
Constitutional Governance Infrastructure Layer
Constitutional Hash: cdd01ef066bc6cf2

Infrastructure implementations for constitutional governance bounded context
including repositories, event handlers, and external service adapters.
"""

from .event_handlers import (
    AmendmentProposalEventHandler,
    ConstitutionEventHandler,
    PrincipleEventHandler,
)
from .external_services import (
    ConstitutionalAnalysisService,
    LegalComplianceService,
    StakeholderNotificationService,
)
from .repositories import (
    AmendmentProposalRepository,
    ConstitutionRepository,
    PrincipleRepository,
)

__all__ = [
    # Event Handlers
    "AmendmentProposalEventHandler",
    "ConstitutionEventHandler",
    "PrincipleEventHandler",
    # External Services
    "ConstitutionalAnalysisService",
    "LegalComplianceService",
    "StakeholderNotificationService",
    # Repositories
    "AmendmentProposalRepository",
    "ConstitutionRepository",
    "PrincipleRepository",
]
