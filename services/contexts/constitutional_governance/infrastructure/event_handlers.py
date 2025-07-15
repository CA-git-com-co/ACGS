"""
Constitutional Governance Event Handlers
Constitutional Hash: cdd01ef066bc6cf2

Event handlers for constitutional governance domain events with
constitutional compliance validation and cross-context integration.
"""

import logging
from typing import Any

from services.shared.domain.base import CONSTITUTIONAL_HASH
from services.shared.domain.events import DomainEvent, DomainEventHandler
from services.contexts.integration.anti_corruption_layer import (
    get_cross_context_coordinator,
)

from ..domain.events import (
    AmendmentProposalCreated,
    AmendmentProposalApproved,
    AmendmentProposalRejected,
    ConstitutionAmended,
    PrincipleAdded,
    PrincipleUpdated,
)

logger = logging.getLogger(__name__)


class ConstitutionEventHandler(DomainEventHandler):
    """Handles events related to Constitution aggregate."""

    def __init__(self):
        """Initialize constitution event handler."""
        self.coordinator = get_cross_context_coordinator()

    async def handle(self, event: DomainEvent) -> None:
        """Handle constitution domain events."""
        if isinstance(event, ConstitutionAmended):
            await self._handle_constitution_amended(event)
        else:
            logger.warning(f"Unhandled constitution event: {type(event).__name__}")

    async def _handle_constitution_amended(self, event: ConstitutionAmended) -> None:
        """Handle constitution amendment event."""
        logger.info(f"Constitution amended: {event.amendment_id}")
        
        # Validate constitutional compliance
        if event.constitutional_hash != CONSTITUTIONAL_HASH:
            logger.error(f"Constitutional hash mismatch in event: {event.constitutional_hash}")
            return

        # Notify audit & integrity context
        audit_request = {
            "type": "create_audit_entry",
            "event_type": "constitution_amended",
            "source": "constitutional_governance",
            "session_id": str(event.aggregate_id),
            "activity_data": {
                "amendment_id": event.amendment_id,
                "changes": event.changes,
                "effective_date": event.effective_date.isoformat(),
            },
            "level": "critical",
        }

        try:
            await self.coordinator.send_request(
                target_context="audit_integrity",
                request=audit_request,
                tenant_id=event.tenant_id,
            )
            logger.info(f"Audit entry created for constitution amendment: {event.amendment_id}")
        except Exception as e:
            logger.error(f"Failed to create audit entry: {e}")

        # Notify policy management context for compliance check
        policy_request = {
            "type": "policy_impact_analysis",
            "subject_id": event.amendment_id,
            "context_data": {
                "scope": "constitutional_change",
                "domains": ["governance", "compliance"],
                "time_horizon": "immediate",
            },
        }

        try:
            await self.coordinator.send_request(
                target_context="policy_management",
                request=policy_request,
                tenant_id=event.tenant_id,
            )
            logger.info(f"Policy impact analysis requested for amendment: {event.amendment_id}")
        except Exception as e:
            logger.error(f"Failed to request policy impact analysis: {e}")


class AmendmentProposalEventHandler(DomainEventHandler):
    """Handles events related to AmendmentProposal aggregate."""

    def __init__(self):
        """Initialize amendment proposal event handler."""
        self.coordinator = get_cross_context_coordinator()

    async def handle(self, event: DomainEvent) -> None:
        """Handle amendment proposal domain events."""
        if isinstance(event, AmendmentProposalCreated):
            await self._handle_proposal_created(event)
        elif isinstance(event, AmendmentProposalApproved):
            await self._handle_proposal_approved(event)
        elif isinstance(event, AmendmentProposalRejected):
            await self._handle_proposal_rejected(event)
        else:
            logger.warning(f"Unhandled amendment proposal event: {type(event).__name__}")

    async def _handle_proposal_created(self, event: AmendmentProposalCreated) -> None:
        """Handle amendment proposal creation event."""
        logger.info(f"Amendment proposal created: {event.proposal_id}")

        # Request multi-agent impact analysis
        analysis_request = {
            "type": "constitutional_impact_analysis",
            "subject_id": event.proposal_id,
            "session_id": f"amendment-analysis-{event.proposal_id}",
            "required_agents": ["ethics", "legal", "operational"],
            "context_data": {
                "affected_principles": event.affected_principles,
                "stakeholder_groups": event.stakeholder_groups,
                "affected_systems": ["governance", "compliance"],
            },
            "deadline": event.review_deadline.isoformat() if event.review_deadline else None,
        }

        try:
            await self.coordinator.send_request(
                target_context="constitutional_governance",
                request=analysis_request,
                tenant_id=event.tenant_id,
            )
            logger.info(f"Impact analysis requested for proposal: {event.proposal_id}")
        except Exception as e:
            logger.error(f"Failed to request impact analysis: {e}")

    async def _handle_proposal_approved(self, event: AmendmentProposalApproved) -> None:
        """Handle amendment proposal approval event."""
        logger.info(f"Amendment proposal approved: {event.proposal_id}")

        # Create audit entry for approval
        audit_request = {
            "type": "create_audit_entry",
            "event_type": "amendment_proposal_approved",
            "source": "constitutional_governance",
            "activity_data": {
                "proposal_id": event.proposal_id,
                "approval_score": event.approval_score,
                "approver_count": event.approver_count,
            },
            "level": "info",
        }

        try:
            await self.coordinator.send_request(
                target_context="audit_integrity",
                request=audit_request,
                tenant_id=event.tenant_id,
            )
        except Exception as e:
            logger.error(f"Failed to create audit entry for approval: {e}")

    async def _handle_proposal_rejected(self, event: AmendmentProposalRejected) -> None:
        """Handle amendment proposal rejection event."""
        logger.info(f"Amendment proposal rejected: {event.proposal_id}")

        # Create audit entry for rejection
        audit_request = {
            "type": "create_audit_entry",
            "event_type": "amendment_proposal_rejected",
            "source": "constitutional_governance",
            "activity_data": {
                "proposal_id": event.proposal_id,
                "rejection_reasons": event.rejection_reasons,
            },
            "level": "info",
        }

        try:
            await self.coordinator.send_request(
                target_context="audit_integrity",
                request=audit_request,
                tenant_id=event.tenant_id,
            )
        except Exception as e:
            logger.error(f"Failed to create audit entry for rejection: {e}")


class PrincipleEventHandler(DomainEventHandler):
    """Handles events related to Principle entities."""

    def __init__(self):
        """Initialize principle event handler."""
        self.coordinator = get_cross_context_coordinator()

    async def handle(self, event: DomainEvent) -> None:
        """Handle principle domain events."""
        if isinstance(event, PrincipleAdded):
            await self._handle_principle_added(event)
        elif isinstance(event, PrincipleUpdated):
            await self._handle_principle_updated(event)
        else:
            logger.warning(f"Unhandled principle event: {type(event).__name__}")

    async def _handle_principle_added(self, event: PrincipleAdded) -> None:
        """Handle principle addition event."""
        logger.info(f"Principle added: {event.principle_name}")

        # Create audit entry
        audit_request = {
            "type": "create_audit_entry",
            "event_type": "principle_added",
            "source": "constitutional_governance",
            "activity_data": {
                "principle_id": str(event.aggregate_id),
                "principle_name": event.principle_name,
                "category": event.category,
            },
            "level": "info",
        }

        try:
            await self.coordinator.send_request(
                target_context="audit_integrity",
                request=audit_request,
                tenant_id=event.tenant_id,
            )
        except Exception as e:
            logger.error(f"Failed to create audit entry for principle addition: {e}")

    async def _handle_principle_updated(self, event: PrincipleUpdated) -> None:
        """Handle principle update event."""
        logger.info(f"Principle updated: {event.principle_name}")

        # Create audit entry
        audit_request = {
            "type": "create_audit_entry",
            "event_type": "principle_updated",
            "source": "constitutional_governance",
            "activity_data": {
                "principle_id": str(event.aggregate_id),
                "principle_name": event.principle_name,
                "changes": event.changes,
            },
            "level": "info",
        }

        try:
            await self.coordinator.send_request(
                target_context="audit_integrity",
                request=audit_request,
                tenant_id=event.tenant_id,
            )
        except Exception as e:
            logger.error(f"Failed to create audit entry for principle update: {e}")


# Event handler factory functions
def create_constitution_event_handler() -> ConstitutionEventHandler:
    """Create constitution event handler instance."""
    return ConstitutionEventHandler()


def create_amendment_proposal_event_handler() -> AmendmentProposalEventHandler:
    """Create amendment proposal event handler instance."""
    return AmendmentProposalEventHandler()


def create_principle_event_handler() -> PrincipleEventHandler:
    """Create principle event handler instance."""
    return PrincipleEventHandler()
