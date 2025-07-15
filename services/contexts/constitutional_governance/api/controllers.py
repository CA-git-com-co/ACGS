"""
Constitutional Governance API Controllers
Constitutional Hash: cdd01ef066bc6cf2

FastAPI controllers for constitutional governance operations with
constitutional compliance validation and performance monitoring.
"""

import logging
from datetime import datetime
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse

from services.shared.domain.base import CONSTITUTIONAL_HASH, EntityId, TenantId

from ..application.queries import (
    GetActiveAmendmentProposalsQuery,
    GetActivePrinciplesQuery,
    GetAmendmentProposalQuery,
    GetConstitutionalComplianceReportQuery,
    GetConstitutionalMetricsQuery,
    GetCurrentConstitutionQuery,
    GetPrincipleQuery,
)
from ..application.services import ConstitutionalGovernanceApplicationService
from .dependencies import (
    get_constitutional_governance_service,
    get_constitutional_query_service,
    get_tenant_id,
)
from .schemas import (
    AmendmentProposalCreateRequest,
    AmendmentProposalListResponse,
    AmendmentProposalResponse,
    AmendmentProposalReviewRequest,
    ComplianceReportResponse,
    ConstitutionalComplianceReportRequest,
    ConstitutionalMetricsResponse,
    ConstitutionalOverviewResponse,
    ConstitutionResponse,
    ErrorResponse,
    PrincipleCreateRequest,
    PrincipleListResponse,
    PrincipleResponse,
    PrincipleUpdateRequest,
)

logger = logging.getLogger(__name__)

# Create routers for different resource groups
constitution_router = APIRouter(prefix="/constitution", tags=["Constitution"])
amendment_router = APIRouter(prefix="/amendments", tags=["Amendment Proposals"])
principle_router = APIRouter(prefix="/principles", tags=["Principles"])
governance_router = APIRouter(prefix="/governance", tags=["Governance"])


class ConstitutionController:
    """Controller for constitution-related operations."""

    @staticmethod
    @constitution_router.get("/current", response_model=ConstitutionResponse)
    async def get_current_constitution(
        tenant_id: TenantId = Depends(get_tenant_id),
        query_service=Depends(get_constitutional_query_service),
    ):
        """Get the current active constitution."""
        try:
            constitution = await query_service.get_current_constitution(
                GetCurrentConstitutionQuery(tenant_id=tenant_id)
            )
            
            if not constitution:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No current constitution found"
                )
            
            return ConstitutionResponse(
                id=constitution.id.value,
                version=constitution.version,
                status="active",
                created_at=constitution.created_at,
                updated_at=constitution.updated_at,
                constitutional_hash=CONSTITUTIONAL_HASH,
            )
            
        except Exception as e:
            logger.error(f"Error getting current constitution: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve current constitution"
            )

    @staticmethod
    @constitution_router.get("/history")
    async def get_constitution_history(
        tenant_id: TenantId = Depends(get_tenant_id),
        limit: int = Query(50, ge=1, le=100),
        query_service=Depends(get_constitutional_query_service),
    ):
        """Get constitution version history."""
        try:
            # This would use a specific query for history
            # For now, return basic response
            return {
                "history": [],
                "total": 0,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "generated_at": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error getting constitution history: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve constitution history"
            )


class AmendmentProposalController:
    """Controller for amendment proposal operations."""

    @staticmethod
    @amendment_router.post("/", response_model=AmendmentProposalResponse, status_code=status.HTTP_201_CREATED)
    async def create_amendment_proposal(
        request: AmendmentProposalCreateRequest,
        tenant_id: TenantId = Depends(get_tenant_id),
        app_service: ConstitutionalGovernanceApplicationService = Depends(get_constitutional_governance_service),
    ):
        """Create a new constitutional amendment proposal."""
        try:
            proposal_id = await app_service.propose_constitutional_amendment(
                tenant_id=tenant_id,
                proposer_id=request.proposer_id,
                title=request.title,
                description=request.description,
                affected_principles=request.affected_principles,
                justification=request.justification,
                stakeholder_groups=request.stakeholder_groups,
                consultation_required=request.consultation_required,
                review_deadline_days=request.review_deadline_days,
            )
            
            # Return created proposal (would typically fetch from query service)
            return AmendmentProposalResponse(
                id=proposal_id.value,
                proposer_id=request.proposer_id,
                title=request.title,
                description=request.description,
                status="pending",
                affected_principles=request.affected_principles,
                stakeholder_groups=request.stakeholder_groups,
                consultation_required=request.consultation_required,
                review_deadline=None,  # Would be calculated
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                constitutional_hash=CONSTITUTIONAL_HASH,
            )
            
        except ValueError as e:
            logger.warning(f"Invalid amendment proposal request: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error creating amendment proposal: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create amendment proposal"
            )

    @staticmethod
    @amendment_router.get("/{proposal_id}", response_model=AmendmentProposalResponse)
    async def get_amendment_proposal(
        proposal_id: UUID,
        tenant_id: TenantId = Depends(get_tenant_id),
        query_service=Depends(get_constitutional_query_service),
    ):
        """Get a specific amendment proposal."""
        try:
            proposal = await query_service.get_amendment_proposal(
                GetAmendmentProposalQuery(
                    tenant_id=tenant_id,
                    proposal_id=EntityId(proposal_id)
                )
            )
            
            if not proposal:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Amendment proposal not found: {proposal_id}"
                )
            
            return AmendmentProposalResponse(
                id=proposal.id.value,
                proposer_id=proposal.proposer_id,
                title=proposal.title,
                description=proposal.description,
                status=proposal.status.value,
                affected_principles=proposal.affected_principles,
                stakeholder_groups=proposal.stakeholder_groups,
                consultation_required=proposal.consultation_required,
                review_deadline=proposal.review_deadline,
                created_at=proposal.created_at,
                updated_at=proposal.updated_at,
                constitutional_hash=CONSTITUTIONAL_HASH,
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting amendment proposal: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve amendment proposal"
            )

    @staticmethod
    @amendment_router.get("/", response_model=AmendmentProposalListResponse)
    async def get_amendment_proposals(
        tenant_id: TenantId = Depends(get_tenant_id),
        status_filter: str | None = Query(None, description="Filter by status"),
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0),
        query_service=Depends(get_constitutional_query_service),
    ):
        """Get amendment proposals with optional filtering."""
        try:
            if status_filter == "active":
                proposals = await query_service.get_active_amendment_proposals(
                    GetActiveAmendmentProposalsQuery(tenant_id=tenant_id, limit=limit)
                )
            else:
                # Would use GetAmendmentProposalsQuery with filters
                proposals = []
            
            proposal_responses = [
                AmendmentProposalResponse(
                    id=p.id.value,
                    proposer_id=p.proposer_id,
                    title=p.title,
                    description=p.description,
                    status=p.status.value,
                    affected_principles=p.affected_principles,
                    stakeholder_groups=p.stakeholder_groups,
                    consultation_required=p.consultation_required,
                    review_deadline=p.review_deadline,
                    created_at=p.created_at,
                    updated_at=p.updated_at,
                    constitutional_hash=CONSTITUTIONAL_HASH,
                )
                for p in proposals
            ]
            
            return AmendmentProposalListResponse(
                proposals=proposal_responses,
                total=len(proposals),
                offset=offset,
                limit=limit,
                constitutional_hash=CONSTITUTIONAL_HASH,
            )
            
        except Exception as e:
            logger.error(f"Error getting amendment proposals: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve amendment proposals"
            )

    @staticmethod
    @amendment_router.post("/{proposal_id}/review")
    async def review_amendment_proposal(
        proposal_id: UUID,
        request: AmendmentProposalReviewRequest,
        tenant_id: TenantId = Depends(get_tenant_id),
        app_service: ConstitutionalGovernanceApplicationService = Depends(get_constitutional_governance_service),
    ):
        """Review an amendment proposal (approve or reject)."""
        try:
            await app_service.review_amendment_proposal(
                tenant_id=tenant_id,
                proposal_id=EntityId(proposal_id),
                reviewer_id=request.reviewer_id,
                decision=request.decision,
                notes=request.notes,
                rejection_reason=request.rejection_reason,
            )
            
            return {
                "message": f"Amendment proposal {request.decision}d successfully",
                "proposal_id": str(proposal_id),
                "decision": request.decision,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": datetime.utcnow().isoformat(),
            }
            
        except ValueError as e:
            logger.warning(f"Invalid amendment review request: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error reviewing amendment proposal: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to review amendment proposal"
            )


class PrincipleController:
    """Controller for principle management operations."""

    @staticmethod
    @principle_router.post("/", response_model=PrincipleResponse, status_code=status.HTTP_201_CREATED)
    async def create_principle(
        request: PrincipleCreateRequest,
        tenant_id: TenantId = Depends(get_tenant_id),
        app_service: ConstitutionalGovernanceApplicationService = Depends(get_constitutional_governance_service),
    ):
        """Create a new constitutional principle."""
        try:
            principle_id = await app_service.create_constitutional_principle(
                tenant_id=tenant_id,
                name=request.name,
                description=request.description,
                category=request.category,
                priority=request.priority,
                is_active=request.is_active,
            )
            
            return PrincipleResponse(
                id=principle_id.value,
                name=request.name,
                description=request.description,
                category=request.category,
                priority=request.priority,
                is_active=request.is_active,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                constitutional_hash=CONSTITUTIONAL_HASH,
            )
            
        except ValueError as e:
            logger.warning(f"Invalid principle request: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error creating principle: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create principle"
            )

    @staticmethod
    @principle_router.get("/{principle_id}", response_model=PrincipleResponse)
    async def get_principle(
        principle_id: UUID,
        tenant_id: TenantId = Depends(get_tenant_id),
        query_service=Depends(get_constitutional_query_service),
    ):
        """Get a specific principle."""
        try:
            principle = await query_service.get_principle(
                GetPrincipleQuery(
                    tenant_id=tenant_id,
                    principle_id=EntityId(principle_id)
                )
            )
            
            if not principle:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Principle not found: {principle_id}"
                )
            
            return PrincipleResponse(
                id=principle.id.value,
                name=principle.name,
                description=principle.description,
                category=principle.category,
                priority=principle.priority,
                is_active=principle.is_active,
                created_at=principle.created_at,
                updated_at=principle.updated_at,
                constitutional_hash=CONSTITUTIONAL_HASH,
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting principle: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve principle"
            )

    @staticmethod
    @principle_router.get("/", response_model=PrincipleListResponse)
    async def get_principles(
        tenant_id: TenantId = Depends(get_tenant_id),
        category: str | None = Query(None, description="Filter by category"),
        active_only: bool = Query(True, description="Show only active principles"),
        limit: int = Query(100, ge=1, le=200),
        offset: int = Query(0, ge=0),
        query_service=Depends(get_constitutional_query_service),
    ):
        """Get principles with optional filtering."""
        try:
            if active_only:
                principles = await query_service.get_active_principles(
                    GetActivePrinciplesQuery(tenant_id=tenant_id)
                )
            else:
                # Would use GetPrinciplesQuery with filters
                principles = []
            
            # Apply category filter if specified
            if category:
                principles = [p for p in principles if p.category == category]
            
            # Apply pagination
            total = len(principles)
            principles = principles[offset:offset + limit]
            
            principle_responses = [
                PrincipleResponse(
                    id=p.id.value,
                    name=p.name,
                    description=p.description,
                    category=p.category,
                    priority=p.priority,
                    is_active=p.is_active,
                    created_at=p.created_at,
                    updated_at=p.updated_at,
                    constitutional_hash=CONSTITUTIONAL_HASH,
                )
                for p in principles
            ]
            
            return PrincipleListResponse(
                principles=principle_responses,
                total=total,
                offset=offset,
                limit=limit,
                constitutional_hash=CONSTITUTIONAL_HASH,
            )
            
        except Exception as e:
            logger.error(f"Error getting principles: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve principles"
            )


class GovernanceController:
    """Controller for governance overview and reporting operations."""

    @staticmethod
    @governance_router.get("/overview", response_model=ConstitutionalOverviewResponse)
    async def get_constitutional_overview(
        tenant_id: TenantId = Depends(get_tenant_id),
        app_service: ConstitutionalGovernanceApplicationService = Depends(get_constitutional_governance_service),
    ):
        """Get comprehensive constitutional governance overview."""
        try:
            overview = await app_service.get_constitutional_overview(tenant_id)
            
            return ConstitutionalOverviewResponse(
                constitution=overview["constitution"],
                principles=overview["principles"],
                amendment_proposals=overview["amendment_proposals"],
                metrics=overview["metrics"],
                constitutional_hash=CONSTITUTIONAL_HASH,
                generated_at=datetime.fromisoformat(overview["generated_at"]),
            )
            
        except Exception as e:
            logger.error(f"Error getting constitutional overview: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve constitutional overview"
            )

    @staticmethod
    @governance_router.post("/compliance-report", response_model=ComplianceReportResponse)
    async def generate_compliance_report(
        request: ConstitutionalComplianceReportRequest,
        tenant_id: TenantId = Depends(get_tenant_id),
        app_service: ConstitutionalGovernanceApplicationService = Depends(get_constitutional_governance_service),
    ):
        """Generate constitutional compliance report."""
        try:
            report = await app_service.generate_compliance_report(
                tenant_id=tenant_id,
                period_days=request.period_days,
                include_violations=request.include_violations,
                include_amendments=request.include_amendments,
                include_principles=request.include_principles,
            )
            
            return ComplianceReportResponse(
                report_id=report["report_id"],
                tenant_id=report["tenant_id"],
                period_start=datetime.fromisoformat(report["period_start"]),
                period_end=datetime.fromisoformat(report["period_end"]),
                summary=report["summary"],
                constitutional_hash=CONSTITUTIONAL_HASH,
                generated_at=datetime.fromisoformat(report["generated_at"]),
            )
            
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate compliance report"
            )

    @staticmethod
    @governance_router.get("/metrics", response_model=ConstitutionalMetricsResponse)
    async def get_constitutional_metrics(
        tenant_id: TenantId = Depends(get_tenant_id),
        query_service=Depends(get_constitutional_query_service),
    ):
        """Get constitutional governance metrics."""
        try:
            metrics = await query_service.get_constitutional_metrics(
                GetConstitutionalMetricsQuery(tenant_id=tenant_id)
            )
            
            return ConstitutionalMetricsResponse(
                metrics_id=metrics["metrics_id"],
                tenant_id=metrics["tenant_id"],
                governance_metrics=metrics["governance_metrics"],
                compliance_metrics=metrics["compliance_metrics"],
                performance_metrics=metrics["performance_metrics"],
                constitutional_hash=CONSTITUTIONAL_HASH,
                generated_at=datetime.fromisoformat(metrics["generated_at"]),
            )
            
        except Exception as e:
            logger.error(f"Error getting constitutional metrics: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve constitutional metrics"
            )


# Export router instances for inclusion in main app
routers = [constitution_router, amendment_router, principle_router, governance_router]
