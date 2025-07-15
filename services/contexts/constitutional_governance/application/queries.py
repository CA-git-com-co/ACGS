"""
Constitutional Governance Queries
Constitutional Hash: cdd01ef066bc6cf2

Query objects for constitutional governance read operations following CQRS pattern.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from services.shared.domain.base import EntityId, TenantId


@dataclass
class GetCurrentConstitutionQuery:
    """Query to get the current active constitution."""
    
    tenant_id: TenantId


@dataclass
class GetConstitutionByIdQuery:
    """Query to get a specific constitution by ID."""
    
    tenant_id: TenantId
    constitution_id: EntityId


@dataclass
class GetConstitutionHistoryQuery:
    """Query to get constitution version history."""
    
    tenant_id: TenantId
    constitution_id: EntityId | None = None
    limit: int = 50


@dataclass
class GetAmendmentProposalQuery:
    """Query to get a specific amendment proposal."""
    
    tenant_id: TenantId
    proposal_id: EntityId


@dataclass
class GetAmendmentProposalsQuery:
    """Query to get amendment proposals with filtering."""
    
    tenant_id: TenantId
    status: str | None = None
    proposer_id: str | None = None
    affected_principles: list[str] | None = None
    created_after: datetime | None = None
    created_before: datetime | None = None
    limit: int = 50
    offset: int = 0


@dataclass
class GetActiveAmendmentProposalsQuery:
    """Query to get all active amendment proposals."""
    
    tenant_id: TenantId
    limit: int = 50


@dataclass
class GetPrincipleQuery:
    """Query to get a specific principle by ID."""
    
    tenant_id: TenantId
    principle_id: EntityId


@dataclass
class GetPrinciplesQuery:
    """Query to get principles with filtering."""
    
    tenant_id: TenantId
    category: str | None = None
    is_active: bool | None = None
    search_term: str | None = None
    limit: int = 100
    offset: int = 0


@dataclass
class GetPrinciplesByCategoryQuery:
    """Query to get principles by category."""
    
    tenant_id: TenantId
    category: str


@dataclass
class GetActivePrinciplesQuery:
    """Query to get all active principles."""
    
    tenant_id: TenantId


@dataclass
class GetPrincipleViolationsQuery:
    """Query to get principle violations."""
    
    tenant_id: TenantId
    principle_id: str | None = None
    severity: str | None = None
    detected_after: datetime | None = None
    detected_before: datetime | None = None
    limit: int = 50
    offset: int = 0


@dataclass
class GetConstitutionalComplianceReportQuery:
    """Query to get constitutional compliance report."""
    
    tenant_id: TenantId
    report_period_start: datetime
    report_period_end: datetime
    include_violations: bool = True
    include_amendments: bool = True
    include_principles: bool = True


@dataclass
class GetAmendmentImpactAnalysisQuery:
    """Query to get impact analysis for an amendment."""
    
    tenant_id: TenantId
    amendment_id: EntityId
    analysis_type: str = "comprehensive"


@dataclass
class GetStakeholderConsultationSummaryQuery:
    """Query to get stakeholder consultation summary."""
    
    tenant_id: TenantId
    consultation_id: EntityId


@dataclass
class GetConflictResolutionHistoryQuery:
    """Query to get conflict resolution history."""
    
    tenant_id: TenantId
    principle_ids: list[str] | None = None
    resolved_after: datetime | None = None
    resolved_before: datetime | None = None
    limit: int = 50


@dataclass
class SearchConstitutionalContentQuery:
    """Query to search constitutional content."""
    
    tenant_id: TenantId
    search_term: str
    content_types: list[str] | None = None  # ["constitution", "amendment", "principle"]
    search_fields: list[str] | None = None  # ["title", "description", "content"]
    limit: int = 50
    offset: int = 0


@dataclass
class GetConstitutionalMetricsQuery:
    """Query to get constitutional governance metrics."""
    
    tenant_id: TenantId
    metric_types: list[str] | None = None
    period_start: datetime | None = None
    period_end: datetime | None = None


@dataclass
class GetAmendmentApprovalWorkflowQuery:
    """Query to get amendment approval workflow status."""
    
    tenant_id: TenantId
    amendment_id: EntityId


@dataclass
class GetConstitutionalTimelineQuery:
    """Query to get constitutional timeline/history."""
    
    tenant_id: TenantId
    event_types: list[str] | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    limit: int = 100
