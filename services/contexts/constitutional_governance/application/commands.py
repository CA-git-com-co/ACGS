"""
Constitutional Governance Commands
Constitutional Hash: cdd01ef066bc6cf2

Command objects for constitutional governance operations following CQRS pattern.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from services.shared.domain.base import EntityId, TenantId


@dataclass
class CreateAmendmentProposalCommand:
    """Command to create a new constitutional amendment proposal."""
    
    tenant_id: TenantId
    proposer_id: str
    title: str
    description: str
    affected_principles: list[str]
    justification: dict[str, Any]
    stakeholder_groups: list[str]
    consultation_required: bool = True
    review_deadline: datetime | None = None


@dataclass
class ApproveAmendmentProposalCommand:
    """Command to approve an amendment proposal."""
    
    tenant_id: TenantId
    proposal_id: EntityId
    approver_id: str
    approval_notes: str | None = None


@dataclass
class RejectAmendmentProposalCommand:
    """Command to reject an amendment proposal."""
    
    tenant_id: TenantId
    proposal_id: EntityId
    rejector_id: str
    rejection_reason: str
    rejection_notes: str | None = None


@dataclass
class StartPublicConsultationCommand:
    """Command to start public consultation for an amendment."""
    
    tenant_id: TenantId
    proposal_id: EntityId
    consultation_duration_days: int
    stakeholder_groups: list[str]
    consultation_methods: list[str]


@dataclass
class CompletePublicConsultationCommand:
    """Command to complete public consultation phase."""
    
    tenant_id: TenantId
    proposal_id: EntityId
    consultation_id: EntityId
    stakeholder_input_count: int
    public_comment_count: int
    expert_review_count: int
    consultation_summary: dict[str, Any]


@dataclass
class AmendConstitutionCommand:
    """Command to formally amend the constitution."""
    
    tenant_id: TenantId
    constitution_id: EntityId
    amendment_id: EntityId
    amended_principles: list[str]
    effective_date: datetime
    approved_by: list[str]


@dataclass
class CreatePrincipleCommand:
    """Command to create a new constitutional principle."""
    
    tenant_id: TenantId
    name: str
    description: str
    category: str
    priority: int
    is_active: bool = True


@dataclass
class UpdatePrincipleCommand:
    """Command to update an existing principle."""
    
    tenant_id: TenantId
    principle_id: EntityId
    name: str | None = None
    description: str | None = None
    category: str | None = None
    priority: int | None = None
    is_active: bool | None = None
    update_reason: str | None = None


@dataclass
class DeactivatePrincipleCommand:
    """Command to deactivate a principle."""
    
    tenant_id: TenantId
    principle_id: EntityId
    deactivation_reason: str
    deactivated_by: str


@dataclass
class DetectPrincipleViolationCommand:
    """Command to detect and record a principle violation."""
    
    tenant_id: TenantId
    principle_id: str
    violation_description: str
    violation_severity: str
    detected_by: str
    context: dict[str, Any]
    evidence: dict[str, Any] | None = None


@dataclass
class ResolveConflictCommand:
    """Command to resolve conflicts between principles."""
    
    tenant_id: TenantId
    conflict_id: str
    resolution_strategy: str
    resolved_by: str
    resolution_details: dict[str, Any]


@dataclass
class ActivateConstitutionCommand:
    """Command to activate a constitution version."""
    
    tenant_id: TenantId
    constitution_id: EntityId
    constitution_version: str
    activated_by: str
    activation_reason: str


@dataclass
class ValidateConstitutionalComplianceCommand:
    """Command to validate constitutional compliance of content."""
    
    tenant_id: TenantId
    content: str
    content_type: str
    validation_context: dict[str, Any]
    validator_id: str


@dataclass
class RequestLegalReviewCommand:
    """Command to request legal review of constitutional content."""
    
    tenant_id: TenantId
    document_id: EntityId
    document_type: str
    content: str
    jurisdiction: str = "default"
    urgency_level: str = "normal"
    reviewer_requirements: list[str] | None = None


@dataclass
class NotifyStakeholdersCommand:
    """Command to notify stakeholders about constitutional changes."""
    
    tenant_id: TenantId
    notification_type: str
    subject_id: str
    stakeholder_groups: list[str]
    notification_data: dict[str, Any]
    delivery_method: str = "email"
    urgent: bool = False
