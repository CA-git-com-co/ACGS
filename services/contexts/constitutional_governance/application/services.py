"""
Constitutional Governance Application Services
Constitutional Hash: cdd01ef066bc6cf2

Application services orchestrating constitutional governance business logic
with constitutional compliance validation and cross-context coordination.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from services.shared.domain.base import EntityId, TenantId

from .command_handlers import ConstitutionalGovernanceService
from .commands import (
    AmendConstitutionCommand,
    ApproveAmendmentProposalCommand,
    CreateAmendmentProposalCommand,
    CreatePrincipleCommand,
    RejectAmendmentProposalCommand,
    UpdatePrincipleCommand,
)
from .queries import (
    GetActiveAmendmentProposalsQuery,
    GetActivePrinciplesQuery,
    GetAmendmentProposalQuery,
    GetConstitutionalComplianceReportQuery,
    GetConstitutionalMetricsQuery,
    GetCurrentConstitutionQuery,
    GetPrincipleQuery,
)
from .query_handlers import ConstitutionalGovernanceQueryService

logger = logging.getLogger(__name__)


class ConstitutionalGovernanceApplicationService:
    """
    Main application service for constitutional governance operations.
    
    Orchestrates commands and queries while maintaining constitutional
    compliance and coordinating with other bounded contexts.
    """

    def __init__(
        self,
        command_service: ConstitutionalGovernanceService,
        query_service: ConstitutionalGovernanceQueryService,
    ):
        self.command_service = command_service
        self.query_service = query_service

    # Amendment Proposal Operations
    async def propose_constitutional_amendment(
        self,
        tenant_id: TenantId,
        proposer_id: str,
        title: str,
        description: str,
        affected_principles: list[str],
        justification: dict[str, Any],
        stakeholder_groups: list[str],
        consultation_required: bool = True,
        review_deadline_days: int = 30,
    ) -> EntityId:
        """
        Propose a new constitutional amendment with validation and stakeholder notification.
        
        Args:
            tenant_id: Tenant identifier
            proposer_id: ID of the proposer
            title: Amendment title
            description: Amendment description
            affected_principles: List of affected principle IDs
            justification: Justification for the amendment
            stakeholder_groups: Groups to notify
            consultation_required: Whether public consultation is required
            review_deadline_days: Days until review deadline
            
        Returns:
            EntityId: ID of the created amendment proposal
        """
        logger.info(f"Proposing constitutional amendment: {title}")

        # Calculate review deadline
        review_deadline = datetime.utcnow() + timedelta(days=review_deadline_days)

        # Validate affected principles exist
        for principle_id in affected_principles:
            principle = await self.query_service.get_principle(
                GetPrincipleQuery(tenant_id=tenant_id, principle_id=EntityId.from_str(principle_id))
            )
            if not principle:
                raise ValueError(f"Principle not found: {principle_id}")

        # Create amendment proposal
        command = CreateAmendmentProposalCommand(
            tenant_id=tenant_id,
            proposer_id=proposer_id,
            title=title,
            description=description,
            affected_principles=affected_principles,
            justification=justification,
            stakeholder_groups=stakeholder_groups,
            consultation_required=consultation_required,
            review_deadline=review_deadline,
        )

        proposal_id = await self.command_service.create_amendment_proposal(command)
        
        logger.info(f"Constitutional amendment proposed: {proposal_id}")
        return proposal_id

    async def review_amendment_proposal(
        self,
        tenant_id: TenantId,
        proposal_id: EntityId,
        reviewer_id: str,
        decision: str,  # "approve" or "reject"
        notes: str | None = None,
        rejection_reason: str | None = None,
    ) -> None:
        """
        Review an amendment proposal with approval or rejection.
        
        Args:
            tenant_id: Tenant identifier
            proposal_id: Amendment proposal ID
            reviewer_id: ID of the reviewer
            decision: "approve" or "reject"
            notes: Review notes
            rejection_reason: Reason for rejection (if applicable)
        """
        logger.info(f"Reviewing amendment proposal: {proposal_id} - {decision}")

        # Validate proposal exists
        proposal = await self.query_service.get_amendment_proposal(
            GetAmendmentProposalQuery(tenant_id=tenant_id, proposal_id=proposal_id)
        )
        if not proposal:
            raise ValueError(f"Amendment proposal not found: {proposal_id}")

        if decision.lower() == "approve":
            command = ApproveAmendmentProposalCommand(
                tenant_id=tenant_id,
                proposal_id=proposal_id,
                approver_id=reviewer_id,
                approval_notes=notes,
            )
            await self.command_service.approve_amendment_proposal(command)
            
        elif decision.lower() == "reject":
            if not rejection_reason:
                raise ValueError("Rejection reason is required for rejected proposals")
                
            command = RejectAmendmentProposalCommand(
                tenant_id=tenant_id,
                proposal_id=proposal_id,
                rejector_id=reviewer_id,
                rejection_reason=rejection_reason,
                rejection_notes=notes,
            )
            await self.command_service.reject_amendment_proposal(command)
            
        else:
            raise ValueError(f"Invalid decision: {decision}. Must be 'approve' or 'reject'")

        logger.info(f"Amendment proposal review completed: {proposal_id}")

    async def implement_approved_amendment(
        self,
        tenant_id: TenantId,
        amendment_id: EntityId,
        implementation_date: datetime | None = None,
        implementing_authority: str | None = None,
    ) -> None:
        """
        Implement an approved constitutional amendment.
        
        Args:
            tenant_id: Tenant identifier
            amendment_id: Amendment proposal ID
            implementation_date: When to implement (defaults to now)
            implementing_authority: Authority implementing the change
        """
        logger.info(f"Implementing constitutional amendment: {amendment_id}")

        # Get current constitution
        constitution = await self.query_service.get_current_constitution(
            GetCurrentConstitutionQuery(tenant_id=tenant_id)
        )
        if not constitution:
            raise ValueError("No current constitution found")

        # Get amendment proposal
        proposal = await self.query_service.get_amendment_proposal(
            GetAmendmentProposalQuery(tenant_id=tenant_id, proposal_id=amendment_id)
        )
        if not proposal:
            raise ValueError(f"Amendment proposal not found: {amendment_id}")

        # Implement amendment
        effective_date = implementation_date or datetime.utcnow()
        approved_by = [implementing_authority] if implementing_authority else ["system"]

        command = AmendConstitutionCommand(
            tenant_id=tenant_id,
            constitution_id=constitution.id,
            amendment_id=amendment_id,
            amended_principles=proposal.affected_principles,
            effective_date=effective_date,
            approved_by=approved_by,
        )

        await self.command_service.amend_constitution(command)
        
        logger.info(f"Constitutional amendment implemented: {amendment_id}")

    # Principle Management Operations
    async def create_constitutional_principle(
        self,
        tenant_id: TenantId,
        name: str,
        description: str,
        category: str,
        priority: int = 5,
        is_active: bool = True,
    ) -> EntityId:
        """
        Create a new constitutional principle.
        
        Args:
            tenant_id: Tenant identifier
            name: Principle name
            description: Principle description
            category: Principle category
            priority: Priority level (1-10)
            is_active: Whether principle is active
            
        Returns:
            EntityId: ID of the created principle
        """
        logger.info(f"Creating constitutional principle: {name}")

        # Validate priority range
        if not 1 <= priority <= 10:
            raise ValueError("Priority must be between 1 and 10")

        command = CreatePrincipleCommand(
            tenant_id=tenant_id,
            name=name,
            description=description,
            category=category,
            priority=priority,
            is_active=is_active,
        )

        principle_id = await self.command_service.create_principle(command)
        
        logger.info(f"Constitutional principle created: {principle_id}")
        return principle_id

    async def update_constitutional_principle(
        self,
        tenant_id: TenantId,
        principle_id: EntityId,
        name: str | None = None,
        description: str | None = None,
        category: str | None = None,
        priority: int | None = None,
        is_active: bool | None = None,
        update_reason: str | None = None,
    ) -> None:
        """
        Update an existing constitutional principle.
        
        Args:
            tenant_id: Tenant identifier
            principle_id: Principle ID to update
            name: New name (optional)
            description: New description (optional)
            category: New category (optional)
            priority: New priority (optional)
            is_active: New active status (optional)
            update_reason: Reason for update
        """
        logger.info(f"Updating constitutional principle: {principle_id}")

        # Validate principle exists
        principle = await self.query_service.get_principle(
            GetPrincipleQuery(tenant_id=tenant_id, principle_id=principle_id)
        )
        if not principle:
            raise ValueError(f"Principle not found: {principle_id}")

        # Validate priority if provided
        if priority is not None and not 1 <= priority <= 10:
            raise ValueError("Priority must be between 1 and 10")

        command = UpdatePrincipleCommand(
            tenant_id=tenant_id,
            principle_id=principle_id,
            name=name,
            description=description,
            category=category,
            priority=priority,
            is_active=is_active,
            update_reason=update_reason,
        )

        await self.command_service.update_principle(command)
        
        logger.info(f"Constitutional principle updated: {principle_id}")

    # Query Operations
    async def get_constitutional_overview(self, tenant_id: TenantId) -> dict[str, Any]:
        """
        Get comprehensive constitutional governance overview.
        
        Args:
            tenant_id: Tenant identifier
            
        Returns:
            dict: Constitutional overview data
        """
        logger.debug(f"Getting constitutional overview for tenant: {tenant_id}")

        # Get current constitution
        constitution = await self.query_service.get_current_constitution(
            GetCurrentConstitutionQuery(tenant_id=tenant_id)
        )

        # Get active principles
        principles = await self.query_service.get_active_principles(
            GetActivePrinciplesQuery(tenant_id=tenant_id)
        )

        # Get active amendment proposals
        proposals = await self.query_service.get_active_amendment_proposals(
            GetActiveAmendmentProposalsQuery(tenant_id=tenant_id)
        )

        # Get metrics
        metrics = await self.query_service.get_constitutional_metrics(
            GetConstitutionalMetricsQuery(tenant_id=tenant_id)
        )

        overview = {
            "constitution": {
                "id": str(constitution.id) if constitution else None,
                "version": constitution.version if constitution else None,
                "status": "active" if constitution else "none",
            },
            "principles": {
                "total_active": len(principles),
                "by_category": self._group_principles_by_category(principles),
            },
            "amendment_proposals": {
                "total_active": len(proposals),
                "pending_review": len([p for p in proposals if p.status == "pending"]),
                "in_consultation": len([p for p in proposals if p.status == "consultation"]),
            },
            "metrics": metrics.get("governance_metrics", {}),
            "constitutional_hash": "cdd01ef066bc6cf2",
            "generated_at": datetime.utcnow().isoformat(),
        }

        logger.info(f"Constitutional overview generated for tenant: {tenant_id}")
        return overview

    async def generate_compliance_report(
        self,
        tenant_id: TenantId,
        period_days: int = 30,
        include_violations: bool = True,
        include_amendments: bool = True,
        include_principles: bool = True,
    ) -> dict[str, Any]:
        """
        Generate constitutional compliance report.
        
        Args:
            tenant_id: Tenant identifier
            period_days: Report period in days
            include_violations: Include violation data
            include_amendments: Include amendment data
            include_principles: Include principle data
            
        Returns:
            dict: Compliance report data
        """
        logger.info(f"Generating compliance report for tenant: {tenant_id}")

        period_end = datetime.utcnow()
        period_start = period_end - timedelta(days=period_days)

        query = GetConstitutionalComplianceReportQuery(
            tenant_id=tenant_id,
            report_period_start=period_start,
            report_period_end=period_end,
            include_violations=include_violations,
            include_amendments=include_amendments,
            include_principles=include_principles,
        )

        report = await self.query_service.get_constitutional_compliance_report(query)
        
        logger.info(f"Compliance report generated: {report['report_id']}")
        return report

    def _group_principles_by_category(self, principles: list[Any]) -> dict[str, int]:
        """Group principles by category for overview."""
        categories = {}
        for principle in principles:
            category = principle.category
            categories[category] = categories.get(category, 0) + 1
        return categories
