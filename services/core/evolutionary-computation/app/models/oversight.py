"""
Oversight Data Models

Data models for human oversight, risk assessment, and governance decisions
in the evolutionary computation framework.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class OversightLevel(str, Enum):
    """Levels of human oversight required."""
    NONE = "none"
    AUTOMATED = "automated"
    HUMAN_REVIEW = "human_review"
    EXPERT_PANEL = "expert_panel"
    CONSTITUTIONAL_COUNCIL = "constitutional_council"


class RiskLevel(str, Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionStatus(str, Enum):
    """Status of oversight decisions."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    TIMEOUT = "timeout"


class RiskAssessment(BaseModel):
    """Risk assessment for evolutionary computation processes."""
    
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evolution_id: str = Field(..., description="Associated evolution request ID")
    
    # Risk factors
    safety_risk: RiskLevel = Field(..., description="Safety risk level")
    constitutional_risk: RiskLevel = Field(..., description="Constitutional compliance risk")
    performance_risk: RiskLevel = Field(..., description="Performance degradation risk")
    security_risk: RiskLevel = Field(..., description="Security vulnerability risk")
    ethical_risk: RiskLevel = Field(..., description="Ethical concern risk")
    
    # Overall assessment
    overall_risk: RiskLevel = Field(..., description="Overall risk level")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Quantitative risk score")
    
    # Risk factors details
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Recommended mitigations")
    
    # Constitutional compliance
    constitutional_compliance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Metadata
    assessed_by: str = Field(..., description="Assessor ID")
    assessed_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OversightRequest(BaseModel):
    """Request for human oversight of evolutionary computation."""
    
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evolution_id: str = Field(..., description="Evolution request ID")
    oversight_level: OversightLevel = Field(..., description="Required oversight level")
    
    # Request details
    reason: str = Field(..., description="Reason for oversight request")
    urgency: str = Field(default="normal", description="Urgency level")
    deadline: Optional[datetime] = None
    
    # Context
    risk_assessment: Optional[RiskAssessment] = None
    context_data: Dict[str, Any] = Field(default_factory=dict)
    
    # Assignment
    assigned_to: Optional[str] = None
    assigned_at: Optional[datetime] = None
    
    # Metadata
    requested_by: str = Field(..., description="Requester ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OversightDecision(BaseModel):
    """Decision made during human oversight process."""
    
    decision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = Field(..., description="Oversight request ID")
    evolution_id: str = Field(..., description="Evolution request ID")
    
    # Decision
    status: DecisionStatus = Field(..., description="Decision status")
    decision: str = Field(..., description="Decision description")
    reasoning: str = Field(..., description="Decision reasoning")
    
    # Conditions and requirements
    conditions: List[str] = Field(default_factory=list, description="Approval conditions")
    requirements: List[str] = Field(default_factory=list, description="Additional requirements")
    
    # Constitutional compliance
    constitutional_compliance_verified: bool = Field(default=False)
    constitutional_notes: str = Field(default="", description="Constitutional compliance notes")
    
    # Decision maker
    decided_by: str = Field(..., description="Decision maker ID")
    decided_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Metadata
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class HumanReviewTask(BaseModel):
    """Task for human review in evolutionary computation oversight."""
    
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evolution_id: str = Field(..., description="Evolution request ID")
    oversight_request_id: str = Field(..., description="Oversight request ID")
    
    # Task details
    task_type: str = Field(..., description="Type of review task")
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    priority: str = Field(default="medium", description="Task priority")
    
    # Review context
    review_data: Dict[str, Any] = Field(default_factory=dict, description="Data for review")
    evaluation_criteria: List[str] = Field(default_factory=list, description="Evaluation criteria")
    
    # Assignment and status
    assigned_to: Optional[str] = None
    status: str = Field(default="pending", description="Task status")
    
    # Timeline
    created_at: datetime = Field(default_factory=datetime.utcnow)
    assigned_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Results
    review_decision: Optional[OversightDecision] = None
    reviewer_notes: str = Field(default="", description="Reviewer notes")
    
    # Constitutional compliance
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
