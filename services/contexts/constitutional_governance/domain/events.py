"""
Domain Events for Constitutional Governance
Constitutional Hash: cdd01ef066bc6cf2

Events representing important occurrences in the constitutional domain.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from services.shared.domain.base import EntityId
from services.shared.domain.events import DomainEvent, EventMetadata

from .value_objects import (
    ConstitutionalHash,
    ConsultationSummary,
    ViolationDetail,
    ViolationSeverity,
)


@dataclass
class ConstitutionAmended(DomainEvent):
    """Event: Constitution has been formally amended."""

    def __init__(
        self,
        aggregate_id: EntityId,
        constitution_version: str,
        amended_principles: List[str],
        new_hash: str,
        effective_date: datetime,
        approved_by: List[str],
        occurred_at: Optional[datetime] = None,
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.constitution_version = constitution_version
        self.amended_principles = amended_principles
        self.new_hash = new_hash
        self.effective_date = effective_date
        self.approved_by = approved_by

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "constitution_version": self.constitution_version,
            "amended_principles": self.amended_principles,
            "new_hash": self.new_hash,
            "effective_date": self.effective_date.isoformat(),
            "approved_by": self.approved_by,
        }


@dataclass
class PrincipleViolationDetected(DomainEvent):
    """Event: A constitutional principle violation was detected."""

    def __init__(
        self,
        aggregate_id: EntityId,
        principle_id: str,
        violation_details: ViolationDetail,
        severity: ViolationSeverity,
        detected_by: str,
        context: Dict[str, Any],
        occurred_at: Optional[datetime] = None,
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.principle_id = principle_id
        self.violation_details = violation_details
        self.severity = severity
        self.detected_by = detected_by
        self.context = context

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "principle_id": self.principle_id,
            "violation_details": self.violation_details.to_dict(),
            "severity": self.severity.value,
            "detected_by": self.detected_by,
            "context": self.context,
        }


@dataclass
class AmendmentProposed(DomainEvent):
    """Event: New constitutional amendment has been proposed."""

    def __init__(
        self,
        aggregate_id: EntityId,
        amendment_id: EntityId,
        proposer: str,
        affected_principles: List[str],
        justification: Dict[str, Any],
        consultation_required: bool,
        occurred_at: Optional[datetime] = None,
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.amendment_id = amendment_id
        self.proposer = proposer
        self.affected_principles = affected_principles
        self.justification = justification
        self.consultation_required = consultation_required

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "amendment_id": str(self.amendment_id),
            "proposer": self.proposer,
            "affected_principles": self.affected_principles,
            "justification": self.justification,
            "consultation_required": self.consultation_required,
        }


@dataclass
class PublicConsultationCompleted(DomainEvent):
    """Event: Public consultation phase completed."""

    def __init__(
        self,
        aggregate_id: EntityId,
        amendment_id: EntityId,
        consultation_id: EntityId,
        stakeholder_input_count: int,
        public_comment_count: int,
        expert_review_count: int,
        consultation_summary: ConsultationSummary,
        occurred_at: Optional[datetime] = None,
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.amendment_id = amendment_id
        self.consultation_id = consultation_id
        self.stakeholder_input_count = stakeholder_input_count
        self.public_comment_count = public_comment_count
        self.expert_review_count = expert_review_count
        self.consultation_summary = consultation_summary

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "amendment_id": str(self.amendment_id),
            "consultation_id": str(self.consultation_id),
            "stakeholder_input_count": self.stakeholder_input_count,
            "public_comment_count": self.public_comment_count,
            "expert_review_count": self.expert_review_count,
            "consultation_summary": self.consultation_summary.to_dict(),
        }


@dataclass
class AmendmentApproved(DomainEvent):
    """Event: Amendment has been approved."""

    def __init__(
        self,
        aggregate_id: EntityId,
        amendment_id: EntityId,
        approved_at: datetime,
        approval_details: Dict[str, Any],
        occurred_at: Optional[datetime] = None,
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.amendment_id = amendment_id
        self.approved_at = approved_at
        self.approval_details = approval_details

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "amendment_id": str(self.amendment_id),
            "approved_at": self.approved_at.isoformat(),
            "approval_details": self.approval_details,
        }


@dataclass
class AmendmentRejected(DomainEvent):
    """Event: Amendment has been rejected."""

    def __init__(
        self,
        aggregate_id: EntityId,
        amendment_id: EntityId,
        rejected_at: datetime,
        rejection_reason: str,
        occurred_at: Optional[datetime] = None,
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.amendment_id = amendment_id
        self.rejected_at = rejected_at
        self.rejection_reason = rejection_reason

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "amendment_id": str(self.amendment_id),
            "rejected_at": self.rejected_at.isoformat(),
            "rejection_reason": self.rejection_reason,
        }


@dataclass
class ConflictDetected(DomainEvent):
    """Event: Conflict detected between principles."""

    def __init__(
        self,
        aggregate_id: EntityId,
        conflicting_principles: List[tuple[str, str]],
        conflict_type: str,
        severity: ViolationSeverity,
        resolution_options: List[str],
        occurred_at: Optional[datetime] = None,
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.conflicting_principles = conflicting_principles
        self.conflict_type = conflict_type
        self.severity = severity
        self.resolution_options = resolution_options

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "conflicting_principles": [
                {"principle1": p[0], "principle2": p[1]}
                for p in self.conflicting_principles
            ],
            "conflict_type": self.conflict_type,
            "severity": self.severity.value,
            "resolution_options": self.resolution_options,
        }


@dataclass
class ConflictResolved(DomainEvent):
    """Event: Conflict between principles has been resolved."""

    def __init__(
        self,
        aggregate_id: EntityId,
        conflict_id: str,
        resolution_strategy: str,
        resolved_by: str,
        resolution_details: Dict[str, Any],
        occurred_at: Optional[datetime] = None,
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.conflict_id = conflict_id
        self.resolution_strategy = resolution_strategy
        self.resolved_by = resolved_by
        self.resolution_details = resolution_details

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "resolution_strategy": self.resolution_strategy,
            "resolved_by": self.resolved_by,
            "resolution_details": self.resolution_details,
        }


@dataclass
class ConstitutionActivated(DomainEvent):
    """Event: Constitution version has been activated."""

    def __init__(
        self,
        aggregate_id: EntityId,
        constitution_version: str,
        previous_version: Optional[str],
        activated_by: str,
        activation_reason: str,
        occurred_at: Optional[datetime] = None,
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.constitution_version = constitution_version
        self.previous_version = previous_version
        self.activated_by = activated_by
        self.activation_reason = activation_reason

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "constitution_version": self.constitution_version,
            "previous_version": self.previous_version,
            "activated_by": self.activated_by,
            "activation_reason": self.activation_reason,
        }


@dataclass
class ConstitutionSuperseded(DomainEvent):
    """Event: Constitution has been superseded by a newer version."""

    def __init__(
        self,
        aggregate_id: EntityId,
        old_version: str,
        new_version: str,
        superseded_by: str,
        superseded_reason: str,
        occurred_at: Optional[datetime] = None,
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.old_version = old_version
        self.new_version = new_version
        self.superseded_by = superseded_by
        self.superseded_reason = superseded_reason

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "old_version": self.old_version,
            "new_version": self.new_version,
            "superseded_by": self.superseded_by,
            "superseded_reason": self.superseded_reason,
        }


@dataclass
class ComplianceEvaluationPerformed(DomainEvent):
    """Event: Compliance evaluation has been performed."""

    def __init__(
        self,
        aggregate_id: EntityId,
        action: Dict[str, Any],
        context: Dict[str, Any],
        compliance_score: float,
        evaluated_principles: List[str],
        violations_found: List[ViolationDetail],
        occurred_at: Optional[datetime] = None,
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.action = action
        self.context = context
        self.compliance_score = compliance_score
        self.evaluated_principles = evaluated_principles
        self.violations_found = violations_found

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "context": self.context,
            "compliance_score": self.compliance_score,
            "evaluated_principles": self.evaluated_principles,
            "violations_found": [v.to_dict() for v in self.violations_found],
        }


@dataclass
class PrincipleDeactivated(DomainEvent):
    """Event: A principle has been deactivated."""

    def __init__(
        self,
        aggregate_id: EntityId,
        principle_id: str,
        deactivation_reason: str,
        deactivated_by: str,
        replacement_principle_id: Optional[str] = None,
        occurred_at: Optional[datetime] = None,
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.principle_id = principle_id
        self.deactivation_reason = deactivation_reason
        self.deactivated_by = deactivated_by
        self.replacement_principle_id = replacement_principle_id

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "principle_id": self.principle_id,
            "deactivation_reason": self.deactivation_reason,
            "deactivated_by": self.deactivated_by,
            "replacement_principle_id": self.replacement_principle_id,
        }


@dataclass
class MetaRuleApplied(DomainEvent):
    """Event: A meta-rule has been applied to resolve a conflict."""

    def __init__(
        self,
        aggregate_id: EntityId,
        meta_rule_id: str,
        conflict_id: str,
        resolution_outcome: str,
        affected_principles: List[str],
        occurred_at: Optional[datetime] = None,
        metadata: Optional[EventMetadata] = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.meta_rule_id = meta_rule_id
        self.conflict_id = conflict_id
        self.resolution_outcome = resolution_outcome
        self.affected_principles = affected_principles

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> Dict[str, Any]:
        return {
            "meta_rule_id": self.meta_rule_id,
            "conflict_id": self.conflict_id,
            "resolution_outcome": self.resolution_outcome,
            "affected_principles": self.affected_principles,
        }
