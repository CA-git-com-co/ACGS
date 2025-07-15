"""
Policy Management Domain Events
Constitutional Hash: cdd01ef066bc6cf2

Domain events for policy management operations with constitutional compliance.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from services.shared.domain.base import EntityId
from services.shared.domain.events import DomainEvent, EventMetadata

from .value_objects import ComplianceLevel, PolicyStatus, ViolationSeverity


@dataclass
class PolicyCreatedEvent(DomainEvent):
    """Event: New policy has been created."""

    def __init__(
        self,
        aggregate_id: EntityId,
        policy_type: str,
        title: str,
        description: str,
        created_by: str,
        scope_domains: list[str],
        occurred_at: datetime | None = None,
        metadata: EventMetadata | None = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.policy_type = policy_type
        self.title = title
        self.description = description
        self.created_by = created_by
        self.scope_domains = scope_domains

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> dict[str, Any]:
        return {
            "policy_type": self.policy_type,
            "title": self.title,
            "description": self.description,
            "created_by": self.created_by,
            "scope_domains": self.scope_domains,
        }


@dataclass
class PolicyUpdatedEvent(DomainEvent):
    """Event: Policy has been updated."""

    def __init__(
        self,
        aggregate_id: EntityId,
        updated_by: str,
        changes: dict[str, Any],
        version: str,
        occurred_at: datetime | None = None,
        metadata: EventMetadata | None = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.updated_by = updated_by
        self.changes = changes
        self.version = version

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> dict[str, Any]:
        return {
            "updated_by": self.updated_by,
            "changes": self.changes,
            "version": self.version,
        }


@dataclass
class PolicyActivatedEvent(DomainEvent):
    """Event: Policy has been activated."""

    def __init__(
        self,
        aggregate_id: EntityId,
        activated_by: str,
        effective_date: datetime,
        activation_reason: str,
        occurred_at: datetime | None = None,
        metadata: EventMetadata | None = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.activated_by = activated_by
        self.effective_date = effective_date
        self.activation_reason = activation_reason

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> dict[str, Any]:
        return {
            "activated_by": self.activated_by,
            "effective_date": self.effective_date.isoformat(),
            "activation_reason": self.activation_reason,
        }


@dataclass
class PolicyDeactivatedEvent(DomainEvent):
    """Event: Policy has been deactivated."""

    def __init__(
        self,
        aggregate_id: EntityId,
        deactivated_by: str,
        deactivation_date: datetime,
        deactivation_reason: str,
        occurred_at: datetime | None = None,
        metadata: EventMetadata | None = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.deactivated_by = deactivated_by
        self.deactivation_date = deactivation_date
        self.deactivation_reason = deactivation_reason

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> dict[str, Any]:
        return {
            "deactivated_by": self.deactivated_by,
            "deactivation_date": self.deactivation_date.isoformat(),
            "deactivation_reason": self.deactivation_reason,
        }


@dataclass
class ComplianceEvaluatedEvent(DomainEvent):
    """Event: Policy compliance has been evaluated."""

    def __init__(
        self,
        aggregate_id: EntityId,
        evaluation_id: str,
        compliance_level: ComplianceLevel,
        compliance_score: float,
        violations_count: int,
        evaluated_by: str,
        occurred_at: datetime | None = None,
        metadata: EventMetadata | None = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.evaluation_id = evaluation_id
        self.compliance_level = compliance_level
        self.compliance_score = compliance_score
        self.violations_count = violations_count
        self.evaluated_by = evaluated_by

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> dict[str, Any]:
        return {
            "evaluation_id": self.evaluation_id,
            "compliance_level": self.compliance_level.value,
            "compliance_score": self.compliance_score,
            "violations_count": self.violations_count,
            "evaluated_by": self.evaluated_by,
        }


@dataclass
class PolicyViolationDetectedEvent(DomainEvent):
    """Event: Policy violation has been detected."""

    def __init__(
        self,
        aggregate_id: EntityId,
        violation_id: str,
        rule_id: str,
        severity: ViolationSeverity,
        description: str,
        detected_by: str,
        context: dict[str, Any],
        occurred_at: datetime | None = None,
        metadata: EventMetadata | None = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.violation_id = violation_id
        self.rule_id = rule_id
        self.severity = severity
        self.description = description
        self.detected_by = detected_by
        self.context = context

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> dict[str, Any]:
        return {
            "violation_id": self.violation_id,
            "rule_id": self.rule_id,
            "severity": self.severity.value,
            "description": self.description,
            "detected_by": self.detected_by,
            "context": self.context,
        }


@dataclass
class PolicyApprovedEvent(DomainEvent):
    """Event: Policy has been approved."""

    def __init__(
        self,
        aggregate_id: EntityId,
        approval_id: str,
        approver_id: str,
        approval_notes: str | None,
        occurred_at: datetime | None = None,
        metadata: EventMetadata | None = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.approval_id = approval_id
        self.approver_id = approver_id
        self.approval_notes = approval_notes

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> dict[str, Any]:
        return {
            "approval_id": self.approval_id,
            "approver_id": self.approver_id,
            "approval_notes": self.approval_notes,
        }


@dataclass
class PolicyRejectedEvent(DomainEvent):
    """Event: Policy has been rejected."""

    def __init__(
        self,
        aggregate_id: EntityId,
        rejection_id: str,
        rejector_id: str,
        rejection_reason: str,
        rejection_notes: str | None,
        occurred_at: datetime | None = None,
        metadata: EventMetadata | None = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.rejection_id = rejection_id
        self.rejector_id = rejector_id
        self.rejection_reason = rejection_reason
        self.rejection_notes = rejection_notes

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> dict[str, Any]:
        return {
            "rejection_id": self.rejection_id,
            "rejector_id": self.rejector_id,
            "rejection_reason": self.rejection_reason,
            "rejection_notes": self.rejection_notes,
        }


@dataclass
class PolicyConflictDetectedEvent(DomainEvent):
    """Event: Conflict between policies has been detected."""

    def __init__(
        self,
        aggregate_id: EntityId,
        conflict_id: str,
        conflicting_policy_ids: list[str],
        conflict_type: str,
        severity: ViolationSeverity,
        detected_by: str,
        occurred_at: datetime | None = None,
        metadata: EventMetadata | None = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.conflict_id = conflict_id
        self.conflicting_policy_ids = conflicting_policy_ids
        self.conflict_type = conflict_type
        self.severity = severity
        self.detected_by = detected_by

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "conflicting_policy_ids": self.conflicting_policy_ids,
            "conflict_type": self.conflict_type,
            "severity": self.severity.value,
            "detected_by": self.detected_by,
        }


@dataclass
class PolicyConflictResolvedEvent(DomainEvent):
    """Event: Policy conflict has been resolved."""

    def __init__(
        self,
        aggregate_id: EntityId,
        conflict_id: str,
        resolution_strategy: str,
        resolved_by: str,
        resolution_details: dict[str, Any],
        occurred_at: datetime | None = None,
        metadata: EventMetadata | None = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.conflict_id = conflict_id
        self.resolution_strategy = resolution_strategy
        self.resolved_by = resolved_by
        self.resolution_details = resolution_details

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> dict[str, Any]:
        return {
            "conflict_id": self.conflict_id,
            "resolution_strategy": self.resolution_strategy,
            "resolved_by": self.resolved_by,
            "resolution_details": self.resolution_details,
        }


@dataclass
class PolicyVersionCreatedEvent(DomainEvent):
    """Event: New version of policy has been created."""

    def __init__(
        self,
        aggregate_id: EntityId,
        version_number: str,
        created_by: str,
        change_summary: str,
        previous_version: str | None,
        occurred_at: datetime | None = None,
        metadata: EventMetadata | None = None,
    ):
        super().__init__(aggregate_id, occurred_at, metadata)
        self.version_number = version_number
        self.created_by = created_by
        self.change_summary = change_summary
        self.previous_version = previous_version

    def _get_event_version(self) -> str:
        return "1.0"

    def get_event_data(self) -> dict[str, Any]:
        return {
            "version_number": self.version_number,
            "created_by": self.created_by,
            "change_summary": self.change_summary,
            "previous_version": self.previous_version,
        }
