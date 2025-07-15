"""
Constitutional Governance Command Handlers
Constitutional Hash: cdd01ef066bc6cf2

Command handlers for constitutional governance operations with
constitutional compliance validation and event sourcing.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

from services.shared.domain.base import EntityId
from services.shared.infrastructure.unit_of_work import UnitOfWorkManager

from ..domain.entities import AmendmentProposal, Constitution, Principle
from ..domain.value_objects import (
    AmendmentStatus,
    ConsultationSummary,
    ViolationDetail,
    ViolationSeverity,
)
from ..infrastructure.external_services import (
    ConstitutionalAnalysisService,
    LegalComplianceService,
    StakeholderNotificationService,
)
from ..infrastructure.repositories import (
    AmendmentProposalRepository,
    ConstitutionRepository,
    PrincipleRepository,
)
from .commands import (
    AmendConstitutionCommand,
    ApproveAmendmentProposalCommand,
    CompletePublicConsultationCommand,
    CreateAmendmentProposalCommand,
    CreatePrincipleCommand,
    DetectPrincipleViolationCommand,
    NotifyStakeholdersCommand,
    RejectAmendmentProposalCommand,
    RequestLegalReviewCommand,
    StartPublicConsultationCommand,
    UpdatePrincipleCommand,
    ValidateConstitutionalComplianceCommand,
)

logger = logging.getLogger(__name__)


class AmendmentProposalCommandHandler:
    """Handles commands related to amendment proposals."""

    def __init__(
        self,
        uow_manager: UnitOfWorkManager,
        amendment_repository: AmendmentProposalRepository,
        constitution_repository: ConstitutionRepository,
        analysis_service: ConstitutionalAnalysisService,
        notification_service: StakeholderNotificationService,
    ):
        self.uow_manager = uow_manager
        self.amendment_repository = amendment_repository
        self.constitution_repository = constitution_repository
        self.analysis_service = analysis_service
        self.notification_service = notification_service

    async def handle_create_amendment_proposal(
        self, command: CreateAmendmentProposalCommand
    ) -> EntityId:
        """Handle creation of new amendment proposal."""
        logger.info(f"Creating amendment proposal for tenant: {command.tenant_id}")

        async with self.uow_manager.begin() as uow:
            # Create new amendment proposal
            proposal = AmendmentProposal.create_new(
                tenant_id=command.tenant_id,
                proposer_id=command.proposer_id,
                title=command.title,
                description=command.description,
                affected_principles=command.affected_principles,
                justification=command.justification,
                stakeholder_groups=command.stakeholder_groups,
                consultation_required=command.consultation_required,
                review_deadline=command.review_deadline,
            )

            # Save proposal
            await self.amendment_repository.save(proposal)

            # Request constitutional analysis
            try:
                analysis_result = await self.analysis_service.analyze_amendment_impact(
                    tenant_id=command.tenant_id,
                    amendment_id=str(proposal.id),
                    amendment_text=command.description,
                    affected_principles=command.affected_principles,
                )
                logger.info(f"Constitutional analysis completed: {analysis_result['analysis_id']}")
            except Exception as e:
                logger.error(f"Failed to request constitutional analysis: {e}")

            # Notify stakeholders
            try:
                await self.notification_service.notify_amendment_proposal(
                    tenant_id=command.tenant_id,
                    proposal_id=str(proposal.id),
                    stakeholder_groups=command.stakeholder_groups,
                    notification_data={
                        "title": command.title,
                        "description": command.description,
                        "proposer": command.proposer_id,
                        "review_deadline": command.review_deadline.isoformat() if command.review_deadline else None,
                    },
                )
            except Exception as e:
                logger.error(f"Failed to notify stakeholders: {e}")

            await uow.commit()
            return proposal.id

    async def handle_approve_amendment_proposal(
        self, command: ApproveAmendmentProposalCommand
    ) -> None:
        """Handle approval of amendment proposal."""
        logger.info(f"Approving amendment proposal: {command.proposal_id}")

        async with self.uow_manager.begin() as uow:
            proposal = await self.amendment_repository.get_by_id(
                command.proposal_id, command.tenant_id
            )
            if not proposal:
                raise ValueError(f"Amendment proposal not found: {command.proposal_id}")

            proposal.approve(
                approver_id=command.approver_id,
                approval_notes=command.approval_notes,
            )

            await self.amendment_repository.save(proposal)
            await uow.commit()

    async def handle_reject_amendment_proposal(
        self, command: RejectAmendmentProposalCommand
    ) -> None:
        """Handle rejection of amendment proposal."""
        logger.info(f"Rejecting amendment proposal: {command.proposal_id}")

        async with self.uow_manager.begin() as uow:
            proposal = await self.amendment_repository.get_by_id(
                command.proposal_id, command.tenant_id
            )
            if not proposal:
                raise ValueError(f"Amendment proposal not found: {command.proposal_id}")

            proposal.reject(
                rejector_id=command.rejector_id,
                rejection_reason=command.rejection_reason,
                rejection_notes=command.rejection_notes,
            )

            await self.amendment_repository.save(proposal)
            await uow.commit()

    async def handle_start_public_consultation(
        self, command: StartPublicConsultationCommand
    ) -> EntityId:
        """Handle starting public consultation."""
        logger.info(f"Starting public consultation for proposal: {command.proposal_id}")

        async with self.uow_manager.begin() as uow:
            proposal = await self.amendment_repository.get_by_id(
                command.proposal_id, command.tenant_id
            )
            if not proposal:
                raise ValueError(f"Amendment proposal not found: {command.proposal_id}")

            consultation_id = proposal.start_public_consultation(
                duration_days=command.consultation_duration_days,
                stakeholder_groups=command.stakeholder_groups,
                consultation_methods=command.consultation_methods,
            )

            await self.amendment_repository.save(proposal)
            await uow.commit()
            return consultation_id

    async def handle_complete_public_consultation(
        self, command: CompletePublicConsultationCommand
    ) -> None:
        """Handle completion of public consultation."""
        logger.info(f"Completing public consultation: {command.consultation_id}")

        async with self.uow_manager.begin() as uow:
            proposal = await self.amendment_repository.get_by_id(
                command.proposal_id, command.tenant_id
            )
            if not proposal:
                raise ValueError(f"Amendment proposal not found: {command.proposal_id}")

            consultation_summary = ConsultationSummary(
                stakeholder_input_count=command.stakeholder_input_count,
                public_comment_count=command.public_comment_count,
                expert_review_count=command.expert_review_count,
                summary_data=command.consultation_summary,
            )

            proposal.complete_public_consultation(
                consultation_id=command.consultation_id,
                consultation_summary=consultation_summary,
            )

            await self.amendment_repository.save(proposal)
            await uow.commit()


class ConstitutionCommandHandler:
    """Handles commands related to constitution management."""

    def __init__(
        self,
        uow_manager: UnitOfWorkManager,
        constitution_repository: ConstitutionRepository,
        amendment_repository: AmendmentProposalRepository,
        notification_service: StakeholderNotificationService,
    ):
        self.uow_manager = uow_manager
        self.constitution_repository = constitution_repository
        self.amendment_repository = amendment_repository
        self.notification_service = notification_service

    async def handle_amend_constitution(self, command: AmendConstitutionCommand) -> None:
        """Handle formal amendment of constitution."""
        logger.info(f"Amending constitution: {command.constitution_id}")

        async with self.uow_manager.begin() as uow:
            # Get constitution and amendment proposal
            constitution = await self.constitution_repository.get_by_id(
                command.constitution_id, command.tenant_id
            )
            if not constitution:
                raise ValueError(f"Constitution not found: {command.constitution_id}")

            amendment = await self.amendment_repository.get_by_id(
                command.amendment_id, command.tenant_id
            )
            if not amendment:
                raise ValueError(f"Amendment not found: {command.amendment_id}")

            # Apply amendment to constitution
            constitution.apply_amendment(
                amendment_id=command.amendment_id,
                amended_principles=command.amended_principles,
                effective_date=command.effective_date,
                approved_by=command.approved_by,
            )

            # Save updated constitution
            await self.constitution_repository.save(constitution)

            # Notify stakeholders about constitutional change
            try:
                await self.notification_service.notify_constitution_change(
                    tenant_id=command.tenant_id,
                    change_id=str(command.amendment_id),
                    stakeholder_groups=amendment.stakeholder_groups,
                    change_data={
                        "amended_principles": command.amended_principles,
                        "effective_date": command.effective_date.isoformat(),
                        "approved_by": command.approved_by,
                    },
                )
            except Exception as e:
                logger.error(f"Failed to notify stakeholders about constitutional change: {e}")

            await uow.commit()


class PrincipleCommandHandler:
    """Handles commands related to principle management."""

    def __init__(
        self,
        uow_manager: UnitOfWorkManager,
        principle_repository: PrincipleRepository,
    ):
        self.uow_manager = uow_manager
        self.principle_repository = principle_repository

    async def handle_create_principle(self, command: CreatePrincipleCommand) -> EntityId:
        """Handle creation of new principle."""
        logger.info(f"Creating principle: {command.name}")

        async with self.uow_manager.begin() as uow:
            principle = Principle.create_new(
                tenant_id=command.tenant_id,
                name=command.name,
                description=command.description,
                category=command.category,
                priority=command.priority,
                is_active=command.is_active,
            )

            await self.principle_repository.save(principle)
            await uow.commit()
            return principle.id

    async def handle_update_principle(self, command: UpdatePrincipleCommand) -> None:
        """Handle update of existing principle."""
        logger.info(f"Updating principle: {command.principle_id}")

        async with self.uow_manager.begin() as uow:
            principle = await self.principle_repository.get_by_id(
                command.principle_id, command.tenant_id
            )
            if not principle:
                raise ValueError(f"Principle not found: {command.principle_id}")

            # Update principle fields
            changes = {}
            if command.name is not None:
                principle.update_name(command.name)
                changes["name"] = command.name
            if command.description is not None:
                principle.update_description(command.description)
                changes["description"] = command.description
            if command.category is not None:
                principle.update_category(command.category)
                changes["category"] = command.category
            if command.priority is not None:
                principle.update_priority(command.priority)
                changes["priority"] = command.priority
            if command.is_active is not None:
                principle.set_active(command.is_active)
                changes["is_active"] = command.is_active

            await self.principle_repository.save(principle)
            await uow.commit()


# Service class to coordinate all command handlers
class ConstitutionalGovernanceService:
    """Main service coordinating all constitutional governance command handlers."""

    def __init__(
        self,
        uow_manager: UnitOfWorkManager,
        amendment_repository: AmendmentProposalRepository,
        constitution_repository: ConstitutionRepository,
        principle_repository: PrincipleRepository,
        analysis_service: ConstitutionalAnalysisService,
        legal_service: LegalComplianceService,
        notification_service: StakeholderNotificationService,
    ):
        self.amendment_handler = AmendmentProposalCommandHandler(
            uow_manager, amendment_repository, constitution_repository,
            analysis_service, notification_service
        )
        self.constitution_handler = ConstitutionCommandHandler(
            uow_manager, constitution_repository, amendment_repository, notification_service
        )
        self.principle_handler = PrincipleCommandHandler(
            uow_manager, principle_repository
        )

    # Amendment proposal operations
    async def create_amendment_proposal(self, command: CreateAmendmentProposalCommand) -> EntityId:
        return await self.amendment_handler.handle_create_amendment_proposal(command)

    async def approve_amendment_proposal(self, command: ApproveAmendmentProposalCommand) -> None:
        await self.amendment_handler.handle_approve_amendment_proposal(command)

    async def reject_amendment_proposal(self, command: RejectAmendmentProposalCommand) -> None:
        await self.amendment_handler.handle_reject_amendment_proposal(command)

    # Constitution operations
    async def amend_constitution(self, command: AmendConstitutionCommand) -> None:
        await self.constitution_handler.handle_amend_constitution(command)

    # Principle operations
    async def create_principle(self, command: CreatePrincipleCommand) -> EntityId:
        return await self.principle_handler.handle_create_principle(command)

    async def update_principle(self, command: UpdatePrincipleCommand) -> None:
        await self.principle_handler.handle_update_principle(command)
