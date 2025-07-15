"""
Constitutional Governance API Schemas
Constitutional Hash: cdd01ef066bc6cf2

Pydantic schemas for constitutional governance API requests and responses
with constitutional compliance validation.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, validator

from services.shared.domain.base import CONSTITUTIONAL_HASH


# Request Schemas

class AmendmentProposalCreateRequest(BaseModel):
    """Request schema for creating amendment proposals."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    proposer_id: str = Field(description="ID of the proposer")
    title: str = Field(description="Amendment title", min_length=1, max_length=200)
    description: str = Field(description="Amendment description", min_length=10, max_length=5000)
    affected_principles: list[str] = Field(description="List of affected principle IDs")
    justification: dict[str, Any] = Field(description="Justification for the amendment")
    stakeholder_groups: list[str] = Field(description="Stakeholder groups to notify")
    consultation_required: bool = Field(default=True, description="Whether public consultation is required")
    review_deadline_days: int = Field(default=30, description="Days until review deadline", ge=1, le=365)

    @validator("affected_principles")
    def validate_affected_principles(cls, v):
        if not v:
            raise ValueError("At least one affected principle must be specified")
        return v

    @validator("stakeholder_groups")
    def validate_stakeholder_groups(cls, v):
        if not v:
            raise ValueError("At least one stakeholder group must be specified")
        return v


class AmendmentProposalReviewRequest(BaseModel):
    """Request schema for reviewing amendment proposals."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    reviewer_id: str = Field(description="ID of the reviewer")
    decision: str = Field(description="Review decision", regex="^(approve|reject)$")
    notes: str | None = Field(None, description="Review notes", max_length=2000)
    rejection_reason: str | None = Field(None, description="Reason for rejection", max_length=1000)

    @validator("rejection_reason")
    def validate_rejection_reason(cls, v, values):
        if values.get("decision") == "reject" and not v:
            raise ValueError("Rejection reason is required for rejected proposals")
        return v


class PrincipleCreateRequest(BaseModel):
    """Request schema for creating principles."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: str = Field(description="Principle name", min_length=1, max_length=100)
    description: str = Field(description="Principle description", min_length=10, max_length=2000)
    category: str = Field(description="Principle category", min_length=1, max_length=50)
    priority: int = Field(default=5, description="Priority level", ge=1, le=10)
    is_active: bool = Field(default=True, description="Whether principle is active")


class PrincipleUpdateRequest(BaseModel):
    """Request schema for updating principles."""
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: str | None = Field(None, description="New principle name", max_length=100)
    description: str | None = Field(None, description="New principle description", max_length=2000)
    category: str | None = Field(None, description="New principle category", max_length=50)
    priority: int | None = Field(None, description="New priority level", ge=1, le=10)
    is_active: bool | None = Field(None, description="New active status")
    update_reason: str | None = Field(None, description="Reason for update", max_length=500)


class ConstitutionalComplianceReportRequest(BaseModel):
    """Request schema for compliance reports."""
    
    period_days: int = Field(default=30, description="Report period in days", ge=1, le=365)
    include_violations: bool = Field(default=True, description="Include violation data")
    include_amendments: bool = Field(default=True, description="Include amendment data")
    include_principles: bool = Field(default=True, description="Include principle data")


# Response Schemas

class ConstitutionResponse(BaseModel):
    """Response schema for constitution data."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(description="Constitution ID")
    version: str = Field(description="Constitution version")
    status: str = Field(description="Constitution status")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH, description="Constitutional hash")


class AmendmentProposalResponse(BaseModel):
    """Response schema for amendment proposal data."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(description="Amendment proposal ID")
    proposer_id: str = Field(description="Proposer ID")
    title: str = Field(description="Amendment title")
    description: str = Field(description="Amendment description")
    status: str = Field(description="Proposal status")
    affected_principles: list[str] = Field(description="Affected principle IDs")
    stakeholder_groups: list[str] = Field(description="Stakeholder groups")
    consultation_required: bool = Field(description="Whether consultation is required")
    review_deadline: datetime | None = Field(description="Review deadline")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH, description="Constitutional hash")


class PrincipleResponse(BaseModel):
    """Response schema for principle data."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(description="Principle ID")
    name: str = Field(description="Principle name")
    description: str = Field(description="Principle description")
    category: str = Field(description="Principle category")
    priority: int = Field(description="Priority level")
    is_active: bool = Field(description="Whether principle is active")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last update timestamp")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH, description="Constitutional hash")


class ConstitutionalOverviewResponse(BaseModel):
    """Response schema for constitutional overview."""
    
    constitution: dict[str, Any] = Field(description="Constitution information")
    principles: dict[str, Any] = Field(description="Principles summary")
    amendment_proposals: dict[str, Any] = Field(description="Amendment proposals summary")
    metrics: dict[str, Any] = Field(description="Governance metrics")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH, description="Constitutional hash")
    generated_at: datetime = Field(description="Generation timestamp")


class ComplianceReportResponse(BaseModel):
    """Response schema for compliance reports."""
    
    report_id: str = Field(description="Report ID")
    tenant_id: str = Field(description="Tenant ID")
    period_start: datetime = Field(description="Report period start")
    period_end: datetime = Field(description="Report period end")
    summary: dict[str, Any] = Field(description="Report summary")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH, description="Constitutional hash")
    generated_at: datetime = Field(description="Generation timestamp")


class ConstitutionalMetricsResponse(BaseModel):
    """Response schema for constitutional metrics."""
    
    metrics_id: str = Field(description="Metrics ID")
    tenant_id: str = Field(description="Tenant ID")
    governance_metrics: dict[str, Any] = Field(description="Governance metrics")
    compliance_metrics: dict[str, Any] = Field(description="Compliance metrics")
    performance_metrics: dict[str, Any] = Field(description="Performance metrics")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH, description="Constitutional hash")
    generated_at: datetime = Field(description="Generation timestamp")


# List Response Schemas

class AmendmentProposalListResponse(BaseModel):
    """Response schema for amendment proposal lists."""
    
    proposals: list[AmendmentProposalResponse] = Field(description="Amendment proposals")
    total: int = Field(description="Total number of proposals")
    offset: int = Field(description="Offset used")
    limit: int = Field(description="Limit used")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH, description="Constitutional hash")


class PrincipleListResponse(BaseModel):
    """Response schema for principle lists."""
    
    principles: list[PrincipleResponse] = Field(description="Principles")
    total: int = Field(description="Total number of principles")
    offset: int = Field(description="Offset used")
    limit: int = Field(description="Limit used")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH, description="Constitutional hash")


# Error Response Schemas

class ErrorResponse(BaseModel):
    """Standard error response schema."""
    
    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    details: dict[str, Any] | None = Field(None, description="Error details")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH, description="Constitutional hash")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
