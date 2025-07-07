"""
Constitutional Governance Domain Models
Constitutional Hash: cdd01ef066bc6cf2

Core domain models for constitutional AI governance.
"""

from .entities import (
    Constitution,
    Principle,
    MetaRule,
    Amendment,
    AmendmentProposal,
    PublicConsultation,
    StakeholderInput,
    ApprovalWorkflow
)

from .value_objects import (
    ConstitutionalHash,
    PriorityWeight,
    ComplianceScore,
    ApplicationScope,
    ValidationCriteria,
    FormalConstraints,
    VersionNumber,
    ConstitutionStatus,
    AmendmentStatus,
    ViolationSeverity
)

from .events import (
    ConstitutionAmended,
    PrincipleViolationDetected,
    AmendmentProposed,
    PublicConsultationCompleted,
    AmendmentApproved,
    AmendmentRejected,
    ConflictDetected,
    ConflictResolved
)

from .specifications import (
    ActiveConstitutionSpec,
    ApplicablePrincipleSpec,
    ValidAmendmentSpec,
    ConflictingPrinciplesSpec,
    HighPriorityPrincipleSpec
)

from .services import (
    ConstitutionalComplianceService,
    AmendmentOrchestrationService,
    ConflictResolutionService,
    PrincipleEvaluationService
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
    "PrincipleEvaluationService"
]