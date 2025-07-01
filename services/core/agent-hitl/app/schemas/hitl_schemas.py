"""
Agent HITL API Schemas

Pydantic schemas for the Agent Human-in-the-Loop oversight system.
Provides validation and serialization for API requests and responses.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel, Field, validator

from ..models.hitl_models import (
    EscalationLevel,
    DecisionStatus,
    ReviewTaskStatus,
    OperationRiskLevel,
)


class AgentOperationRequestCreate(BaseModel):
    """Schema for creating an agent operation request."""
    
    agent_id: str = Field(..., description="Agent identifier")
    operation_type: str = Field(..., description="Type of operation being requested")
    operation_data: Dict[str, Any] = Field(..., description="Operation-specific data")
    operation_context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    
    # Risk assessment
    risk_level: OperationRiskLevel = Field(default=OperationRiskLevel.MEDIUM, description="Operation risk level")
    risk_factors: Optional[Dict[str, Any]] = Field(None, description="Detailed risk factors")
    
    # Constitutional compliance
    constitutional_principles: Optional[List[str]] = Field(None, description="Relevant constitutional principles")
    requires_constitutional_review: bool = Field(default=False, description="Requires Constitutional Council review")
    
    # Timing
    expires_at: Optional[datetime] = Field(None, description="Request expiration time")
    
    # Client context
    client_ip: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    
    @validator('operation_type')
    def validate_operation_type(cls, v):
        """Validate operation type format."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Operation type cannot be empty')
        return v.strip().lower()


class HITLEvaluationRequest(BaseModel):
    """Schema for HITL evaluation request."""
    
    operation_request: AgentOperationRequestCreate
    force_escalation_level: Optional[EscalationLevel] = Field(None, description="Force specific escalation level")
    bypass_cache: bool = Field(default=False, description="Bypass decision cache")
    include_reasoning: bool = Field(default=True, description="Include decision reasoning")
    
    class Config:
        use_enum_values = True


class HITLDecisionResponse(BaseModel):
    """Schema for HITL decision response."""
    
    decision_id: str
    operation_request_id: str
    escalation_level: EscalationLevel
    decision_status: DecisionStatus
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Decision confidence (0.0-1.0)")
    
    # Decision details
    decision_reasoning: Optional[str] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    constitutional_compliance_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Processing metrics
    processing_time_ms: Optional[float] = None
    cache_hit: bool = False
    decision_algorithm: Optional[str] = None
    
    # Human involvement
    requires_human_review: bool = False
    human_reviewer_id: Optional[int] = None
    human_decision_at: Optional[datetime] = None
    
    # Timing
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    # Constitutional compliance
    constitutional_hash: str = "cdd01ef066bc6cf2"
    compliance_verified: bool = False
    
    class Config:
        from_attributes = True
        use_enum_values = True


class AgentConfidenceProfileResponse(BaseModel):
    """Schema for agent confidence profile response."""
    
    agent_id: str
    overall_confidence_score: float = Field(..., ge=0.0, le=1.0)
    total_operations: int = Field(..., ge=0)
    successful_operations: int = Field(..., ge=0)
    failed_operations: int = Field(..., ge=0)
    
    # Operation-specific scores
    operation_type_scores: Dict[str, float] = Field(default_factory=dict)
    risk_level_scores: Dict[str, float] = Field(default_factory=dict)
    
    # Learning parameters
    learning_rate: float = Field(..., ge=0.0, le=1.0)
    adaptation_rate: float = Field(..., ge=0.0, le=1.0)
    
    # Constitutional compliance
    constitutional_compliance_score: float = Field(..., ge=0.0, le=1.0)
    constitutional_violations: int = Field(..., ge=0)
    
    # Timing
    created_at: datetime
    updated_at: datetime
    last_decision_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AgentConfidenceUpdate(BaseModel):
    """Schema for updating agent confidence."""
    
    operation_type: str
    success: bool
    learning_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    constitutional_compliant: Optional[bool] = None
    feedback_notes: Optional[str] = None


class HumanReviewTaskResponse(BaseModel):
    """Schema for human review task response."""
    
    task_id: str
    decision_id: str
    task_type: str
    priority: int = Field(..., ge=1, le=10)
    status: ReviewTaskStatus
    
    # Assignment
    assigned_reviewer_id: Optional[int] = None
    assigned_at: Optional[datetime] = None
    reviewer_expertise: Optional[Dict[str, Any]] = None
    
    # Task context
    operation_summary: str
    risk_factors: Optional[Dict[str, Any]] = None
    constitutional_concerns: Optional[Dict[str, Any]] = None
    agent_context: Optional[Dict[str, Any]] = None
    
    # Review details
    review_started_at: Optional[datetime] = None
    review_completed_at: Optional[datetime] = None
    review_decision: Optional[str] = None
    review_reasoning: Optional[str] = None
    review_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Timing
    created_at: datetime
    due_at: datetime
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True


class HumanReviewSubmission(BaseModel):
    """Schema for submitting human review."""
    
    review_decision: str = Field(..., description="Review decision: approve, reject, escalate")
    review_reasoning: str = Field(..., min_length=10, description="Reasoning for the decision")
    review_confidence: float = Field(..., ge=0.0, le=1.0, description="Reviewer confidence in decision")
    
    # Additional feedback
    suggested_confidence_adjustment: Optional[float] = Field(None, ge=-1.0, le=1.0)
    constitutional_concerns: Optional[List[str]] = None
    recommendations: Optional[str] = None
    
    @validator('review_decision')
    def validate_review_decision(cls, v):
        """Validate review decision."""
        valid_decisions = ['approve', 'reject', 'escalate']
        if v.lower() not in valid_decisions:
            raise ValueError(f'Review decision must be one of: {valid_decisions}')
        return v.lower()


class HITLFeedbackCreate(BaseModel):
    """Schema for creating HITL feedback."""
    
    decision_id: str
    feedback_type: str = Field(..., description="Type of feedback: human_review, outcome_validation, performance_feedback")
    feedback_source: str = Field(..., description="Source of feedback: human_reviewer, system_monitoring, agent_outcome")
    
    # Confidence feedback
    suggested_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Human feedback
    human_agreed_with_decision: Optional[bool] = None
    human_reasoning: Optional[str] = None
    human_confidence_rating: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Outcome validation
    actual_outcome: Optional[str] = None
    outcome_details: Optional[Dict[str, Any]] = None
    constitutional_compliance_actual: Optional[bool] = None
    
    # Learning parameters
    learning_weight: float = Field(default=1.0, ge=0.0, le=10.0)


class HITLDashboardData(BaseModel):
    """Schema for HITL dashboard data."""
    
    # Summary statistics
    total_decisions_today: int
    automated_decisions_today: int
    human_reviews_today: int
    escalations_today: int
    
    # Performance metrics
    average_decision_time_ms: float
    p99_decision_time_ms: float
    cache_hit_rate: float
    
    # Queue status
    pending_reviews: int
    overdue_reviews: int
    available_reviewers: int
    
    # Agent statistics
    active_agents: int
    agents_requiring_attention: int
    average_agent_confidence: float
    
    # Constitutional compliance
    constitutional_compliance_rate: float
    constitutional_violations_today: int
    
    # Recent activity
    recent_decisions: List[HITLDecisionResponse]
    recent_reviews: List[HumanReviewTaskResponse]
    
    # Alerts
    active_alerts: List[Dict[str, Any]]


class HITLMetrics(BaseModel):
    """Schema for HITL system metrics."""
    
    # Decision metrics
    decisions_per_minute: float
    automated_approval_rate: float
    human_review_rate: float
    escalation_rate: float
    
    # Performance metrics
    decision_latency_p50: float
    decision_latency_p95: float
    decision_latency_p99: float
    cache_hit_rate: float
    
    # Quality metrics
    false_positive_rate: float
    false_negative_rate: float
    human_agreement_rate: float
    confidence_accuracy: float
    
    # Agent metrics
    agent_confidence_distribution: Dict[str, int]  # confidence_range -> count
    top_performing_agents: List[str]
    agents_needing_attention: List[str]
    
    # Constitutional compliance
    constitutional_compliance_rate: float
    constitutional_violations_per_day: float
    
    # System health
    service_availability: float
    error_rate: float
    queue_depth: int


class HITLConfigUpdate(BaseModel):
    """Schema for updating HITL configuration."""
    
    # Escalation thresholds
    level_1_confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    level_2_confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    level_3_confidence_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Risk factors
    operation_risk_weights: Optional[Dict[str, float]] = None
    agent_compliance_weights: Optional[Dict[str, float]] = None
    
    # Performance tuning
    cache_ttl_seconds: Optional[int] = Field(None, ge=60, le=86400)
    max_concurrent_reviews: Optional[int] = Field(None, ge=1, le=1000)
    decision_timeout_ms: Optional[int] = Field(None, ge=1000, le=300000)
    
    # Learning parameters
    global_learning_rate: Optional[float] = Field(None, ge=0.0, le=1.0)
    confidence_decay_rate: Optional[float] = Field(None, ge=0.0, le=1.0)


class HITLSearchRequest(BaseModel):
    """Schema for searching HITL records."""
    
    # Filters
    agent_ids: Optional[List[str]] = None
    operation_types: Optional[List[str]] = None
    escalation_levels: Optional[List[EscalationLevel]] = None
    decision_statuses: Optional[List[DecisionStatus]] = None
    
    # Date range
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
    # Confidence range
    min_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    max_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    
    # Human involvement
    human_reviewed_only: Optional[bool] = None
    constitutional_reviewed_only: Optional[bool] = None
    
    # Pagination
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    
    # Sorting
    sort_by: str = Field(default="created_at")
    sort_order: str = Field(default="desc")
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        """Validate sort order."""
        if v not in ['asc', 'desc']:
            raise ValueError('Sort order must be asc or desc')
        return v
    
    class Config:
        use_enum_values = True
