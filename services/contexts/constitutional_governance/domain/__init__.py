"""
Constitutional Governance Domain Models
Constitutional Hash: cdd01ef066bc6cf2

Core domain models for constitutional AI governance.
"""

from .entities import (
    Amendment,
    AmendmentProposal,
    ApprovalWorkflow,
    Constitution,
    MetaRule,
    Principle,
    PublicConsultation,
    StakeholderInput,
)
from .events import (
    AmendmentApproved,
    AmendmentProposed,
    AmendmentRejected,
    ConflictDetected,
    ConflictResolved,
    ConstitutionAmended,
    PrincipleViolationDetected,
    PublicConsultationCompleted,
)
from .services import (
    AmendmentOrchestrationService,
    ConflictResolutionService,
    ConstitutionalComplianceService,
    PrincipleEvaluationService,
)
from .specifications import (
    ActiveConstitutionSpec,
    ApplicablePrincipleSpec,
    ConflictingPrinciplesSpec,
    HighPriorityPrincipleSpec,
    ValidAmendmentSpec,
)
from .value_objects import (
    AmendmentStatus,
    ApplicationScope,
    ComplianceScore,
    ConstitutionalHash,
    ConstitutionStatus,
    FormalConstraints,
    PriorityWeight,
    ValidationCriteria,
    VersionNumber,
    ViolationSeverity,
)

__all__ = [
    # Entities
    "Constitution",
    "Principle",
    "MetaRule",
    "Amendment",
    "AmendmentProposal",
    "PublicConsultation",
    "StakeholderInput",
    "ApprovalWorkflow",
    # Value Objects
    "ConstitutionalHash",
    "PriorityWeight",
    "ComplianceScore",
    "ApplicationScope",
    "ValidationCriteria",
    "FormalConstraints",
    "VersionNumber",
    "ConstitutionStatus",
    "AmendmentStatus",
    "ViolationSeverity",
    # Events
    "ConstitutionAmended",
    "PrincipleViolationDetected",
    "AmendmentProposed",
    "PublicConsultationCompleted",
    "AmendmentApproved",
    "AmendmentRejected",
    "ConflictDetected",
    "ConflictResolved",
    # Specifications
    "ActiveConstitutionSpec",
    "ApplicablePrincipleSpec",
    "ValidAmendmentSpec",
    "ConflictingPrinciplesSpec",
    "HighPriorityPrincipleSpec",
    # Domain Services
    "ConstitutionalComplianceService",
    "AmendmentOrchestrationService",
    "ConflictResolutionService",
    "PrincipleEvaluationService",
]
