"""
Oversight API Schemas

Request and response schemas for oversight and governance API endpoints.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from ..models.oversight import DecisionStatus, OversightLevel, RiskLevel

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class OversightRequestCreate(BaseModel):
    """Schema for creating oversight requests."""

    evolution_id: str = Field(..., description="Evolution request ID")
    oversight_level: OversightLevel = Field(..., description="Required oversight level")

    # Request details
    reason: str = Field(..., description="Reason for oversight request")
    urgency: str = Field(default="normal", description="Urgency level")
    deadline_hours: int | None = Field(
        None, ge=1, le=168, description="Deadline in hours"
    )

    # Context
    context_data: dict[str, Any] = Field(
        default_factory=dict, description="Additional context"
    )
    risk_factors: list[str] = Field(
        default_factory=list, description="Identified risk factors"
    )

    # Assignment preferences
    preferred_reviewer: str | None = Field(None, description="Preferred reviewer ID")
    expertise_required: list[str] = Field(
        default_factory=list, description="Required expertise"
    )


class OversightRequestResponse(BaseModel):
    """Schema for oversight request responses."""

    request_id: str = Field(..., description="Oversight request ID")
    evolution_id: str = Field(..., description="Evolution request ID")
    oversight_level: OversightLevel = Field(..., description="Oversight level")

    # Request details
    reason: str = Field(..., description="Reason for oversight")
    urgency: str = Field(..., description="Urgency level")
    deadline: datetime | None = Field(None, description="Deadline")

    # Status
    status: str = Field(..., description="Request status")
    assigned_to: str | None = Field(None, description="Assigned reviewer")
    assigned_at: datetime | None = Field(None, description="Assignment timestamp")

    # Progress
    estimated_completion: datetime | None = Field(
        None, description="Estimated completion"
    )
    progress_notes: str = Field(default="", description="Progress notes")

    # Metadata
    requested_by: str = Field(..., description="Requester ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class OversightDecisionCreate(BaseModel):
    """Schema for creating oversight decisions."""

    request_id: str = Field(..., description="Oversight request ID")

    # Decision
    status: DecisionStatus = Field(..., description="Decision status")
    decision: str = Field(..., description="Decision description")
    reasoning: str = Field(..., description="Decision reasoning")

    # Conditions and requirements
    conditions: list[str] = Field(
        default_factory=list, description="Approval conditions"
    )
    requirements: list[str] = Field(
        default_factory=list, description="Additional requirements"
    )

    # Constitutional compliance
    constitutional_compliance_verified: bool = Field(
        default=False, description="Constitutional compliance verified"
    )
    constitutional_notes: str = Field(
        default="", description="Constitutional compliance notes"
    )

    # Follow-up actions
    follow_up_required: bool = Field(default=False, description="Follow-up required")
    follow_up_deadline_hours: int | None = Field(
        None, ge=1, le=168, description="Follow-up deadline"
    )


class OversightDecisionResponse(BaseModel):
    """Schema for oversight decision responses."""

    decision_id: str = Field(..., description="Decision ID")
    request_id: str = Field(..., description="Oversight request ID")
    evolution_id: str = Field(..., description="Evolution request ID")

    # Decision
    status: DecisionStatus = Field(..., description="Decision status")
    decision: str = Field(..., description="Decision description")
    reasoning: str = Field(..., description="Decision reasoning")

    # Conditions and requirements
    conditions: list[str] = Field(..., description="Approval conditions")
    requirements: list[str] = Field(..., description="Additional requirements")

    # Constitutional compliance
    constitutional_compliance_verified: bool = Field(
        ..., description="Constitutional compliance verified"
    )
    constitutional_notes: str = Field(
        ..., description="Constitutional compliance notes"
    )

    # Decision maker
    decided_by: str = Field(..., description="Decision maker ID")
    decided_at: datetime = Field(..., description="Decision timestamp")

    # Metadata
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class RiskAssessmentResponse(BaseModel):
    """Schema for risk assessment responses."""

    assessment_id: str = Field(..., description="Assessment ID")
    evolution_id: str = Field(..., description="Evolution request ID")

    # Risk levels
    safety_risk: RiskLevel = Field(..., description="Safety risk level")
    constitutional_risk: RiskLevel = Field(..., description="Constitutional risk level")
    performance_risk: RiskLevel = Field(..., description="Performance risk level")
    security_risk: RiskLevel = Field(..., description="Security risk level")
    ethical_risk: RiskLevel = Field(..., description="Ethical risk level")

    # Overall assessment
    overall_risk: RiskLevel = Field(..., description="Overall risk level")
    risk_score: float = Field(
        ..., ge=0.0, le=1.0, description="Quantitative risk score"
    )

    # Details
    risk_factors: list[str] = Field(..., description="Identified risk factors")
    mitigation_strategies: list[str] = Field(..., description="Recommended mitigations")

    # Constitutional compliance
    constitutional_compliance_score: float = Field(
        ..., ge=0.0, le=1.0, description="Constitutional compliance score"
    )

    # Recommendations
    recommended_oversight_level: OversightLevel = Field(
        ..., description="Recommended oversight level"
    )
    immediate_actions_required: list[str] = Field(
        default_factory=list, description="Immediate actions required"
    )

    # Metadata
    assessed_by: str = Field(..., description="Assessor ID")
    assessed_at: datetime = Field(..., description="Assessment timestamp")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
