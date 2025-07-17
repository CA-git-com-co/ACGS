"""
Human Review Interface Service - Data Models and Schemas
Constitutional Hash: cdd01ef066bc6cf2
"""

from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from enum import Enum
import uuid
from datetime import datetime

# Constitutional compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ReviewStatus(str, Enum):
    """Review task status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ESCALATED = "escalated"
    REJECTED = "rejected"
    APPROVED = "approved"


class ContentType(str, Enum):
    """Types of content for review"""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    CONVERSATION = "conversation"
    RECOMMENDATION = "recommendation"


class ReviewPriority(str, Enum):
    """Review priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class ReviewDecision(str, Enum):
    """Review decision types"""
    APPROVE = "approve"
    REJECT = "reject"
    NEEDS_REVISION = "needs_revision"
    ESCALATE = "escalate"
    FLAG = "flag"


class ReviewerRole(str, Enum):
    """Reviewer role types"""
    JUNIOR_REVIEWER = "junior_reviewer"
    SENIOR_REVIEWER = "senior_reviewer"
    SUBJECT_EXPERT = "subject_expert"
    CONSTITUTIONAL_EXPERT = "constitutional_expert"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"


class ReviewTask(BaseModel):
    """Review task model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(description="Review task title")
    description: Optional[str] = Field(None, description="Task description")
    content_type: ContentType = Field(description="Type of content to review")
    content_data: Dict[str, Any] = Field(default_factory=dict, description="Content data")
    priority: ReviewPriority = Field(default=ReviewPriority.MEDIUM)
    status: ReviewStatus = Field(default=ReviewStatus.PENDING)
    assigned_to: Optional[str] = Field(None, description="Assigned reviewer ID")
    assigned_role: Optional[ReviewerRole] = Field(None, description="Required reviewer role")
    created_by: str = Field(description="Creator user ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    due_date: Optional[datetime] = Field(None, description="Due date for review")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    constitutional_requirements: Dict[str, Any] = Field(default_factory=dict)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class ReviewSubmission(BaseModel):
    """Review submission model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = Field(description="Review task ID")
    reviewer_id: str = Field(description="Reviewer user ID")
    decision: ReviewDecision = Field(description="Review decision")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence in decision")
    reasoning: str = Field(description="Review reasoning")
    detailed_feedback: Optional[str] = Field(None, description="Detailed feedback")
    constitutional_compliance: Dict[str, Any] = Field(default_factory=dict)
    flags: List[str] = Field(default_factory=list, description="Content flags")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    time_spent_minutes: Optional[int] = Field(None, ge=0, description="Time spent reviewing")
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    @validator('constitutional_hash')
    def validate_constitutional_hash(cls, v):
        if v != CONSTITUTIONAL_HASH:
            raise ValueError(f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}")
        return v


class ReviewerProfile(BaseModel):
    """Reviewer profile model"""
    user_id: str = Field(description="User identifier")
    name: str = Field(description="Reviewer name")
    email: str = Field(description="Reviewer email")
    role: ReviewerRole = Field(description="Reviewer role")
    specializations: List[str] = Field(default_factory=list, description="Areas of expertise")
    certification_level: Optional[str] = Field(None, description="Certification level")
    active: bool = Field(default=True, description="Whether reviewer is active")
    availability: Dict[str, Any] = Field(default_factory=dict, description="Availability schedule")
    performance_metrics: Dict[str, float] = Field(default_factory=dict)
    constitutional_training: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class ReviewTaskRequest(BaseModel):
    """Request to create a review task"""
    title: str = Field(min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    content_type: ContentType = Field(description="Type of content")
    content_data: Dict[str, Any] = Field(description="Content to review")
    priority: ReviewPriority = Field(default=ReviewPriority.MEDIUM)
    required_role: Optional[ReviewerRole] = Field(None, description="Required reviewer role")
    due_date: Optional[datetime] = Field(None, description="Due date")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    constitutional_requirements: Dict[str, Any] = Field(default_factory=dict)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    
    @validator('constitutional_hash')
    def validate_constitutional_hash(cls, v):
        if v != CONSTITUTIONAL_HASH:
            raise ValueError(f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}")
        return v


class ReviewTaskResponse(BaseModel):
    """Response for review task operations"""
    task: ReviewTask = Field(description="Review task")
    submissions: List[ReviewSubmission] = Field(default_factory=list, description="Review submissions")
    assignee_info: Optional[ReviewerProfile] = Field(None, description="Assignee information")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class ReviewWorkloadRequest(BaseModel):
    """Request for reviewer workload"""
    reviewer_id: Optional[str] = Field(None, description="Specific reviewer ID")
    role: Optional[ReviewerRole] = Field(None, description="Reviewer role filter")
    status: Optional[ReviewStatus] = Field(None, description="Status filter")
    priority: Optional[ReviewPriority] = Field(None, description="Priority filter")
    limit: int = Field(default=10, ge=1, le=100, description="Number of tasks to return")
    offset: int = Field(default=0, ge=0, description="Offset for pagination")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class ReviewWorkloadResponse(BaseModel):
    """Response for reviewer workload"""
    tasks: List[ReviewTask] = Field(description="Review tasks")
    total: int = Field(ge=0, description="Total number of tasks")
    reviewer_stats: Dict[str, Any] = Field(default_factory=dict, description="Reviewer statistics")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class ReviewAnalytics(BaseModel):
    """Analytics for review system"""
    total_tasks: int = Field(ge=0, description="Total review tasks")
    pending_tasks: int = Field(ge=0, description="Pending tasks")
    completed_tasks: int = Field(ge=0, description="Completed tasks")
    avg_completion_time_hours: float = Field(ge=0.0, description="Average completion time")
    approval_rate: float = Field(ge=0.0, le=1.0, description="Approval rate")
    constitutional_compliance_rate: float = Field(ge=0.0, le=1.0, description="Constitutional compliance rate")
    reviewer_performance: Dict[str, Any] = Field(default_factory=dict)
    priority_distribution: Dict[str, int] = Field(default_factory=dict)
    content_type_distribution: Dict[str, int] = Field(default_factory=dict)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class ReviewerAssignmentRequest(BaseModel):
    """Request for reviewer assignment"""
    task_id: str = Field(description="Task ID to assign")
    reviewer_id: Optional[str] = Field(None, description="Specific reviewer ID")
    auto_assign: bool = Field(default=True, description="Whether to auto-assign")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class NotificationRequest(BaseModel):
    """Request for sending notifications"""
    recipient_id: str = Field(description="Recipient user ID")
    type: str = Field(description="Notification type")
    title: str = Field(description="Notification title")
    message: str = Field(description="Notification message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Additional data")
    urgent: bool = Field(default=False, description="Whether urgent")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class ReviewerTrainingRequest(BaseModel):
    """Request for reviewer training"""
    reviewer_id: str = Field(description="Reviewer ID")
    training_module: str = Field(description="Training module")
    completion_data: Dict[str, Any] = Field(default_factory=dict)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class ReviewEscalationRequest(BaseModel):
    """Request for review escalation"""
    task_id: str = Field(description="Task ID to escalate")
    reviewer_id: str = Field(description="Reviewer requesting escalation")
    reason: str = Field(description="Escalation reason")
    target_role: ReviewerRole = Field(description="Target reviewer role")
    urgency: ReviewPriority = Field(default=ReviewPriority.HIGH)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class ReviewAuditLog(BaseModel):
    """Audit log for review actions"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = Field(description="Review task ID")
    user_id: str = Field(description="User performing action")
    action: str = Field(description="Action performed")
    details: Dict[str, Any] = Field(default_factory=dict, description="Action details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    constitutional_compliance: bool = Field(default=True)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class ReviewQualityMetrics(BaseModel):
    """Quality metrics for reviews"""
    task_id: str = Field(description="Review task ID")
    reviewer_id: str = Field(description="Reviewer ID")
    accuracy_score: float = Field(ge=0.0, le=1.0, description="Review accuracy")
    consistency_score: float = Field(ge=0.0, le=1.0, description="Review consistency")
    thoroughness_score: float = Field(ge=0.0, le=1.0, description="Review thoroughness")
    constitutional_alignment: float = Field(ge=0.0, le=1.0, description="Constitutional alignment")
    timeliness_score: float = Field(ge=0.0, le=1.0, description="Timeliness score")
    overall_quality: float = Field(ge=0.0, le=1.0, description="Overall quality score")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(default="healthy")
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    version: str = Field(default="1.0.0")
    services: Dict[str, str] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(description="Error message")
    error_code: str = Field(description="Error code")
    details: Optional[Dict[str, Any]] = None
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ReviewTemplateRequest(BaseModel):
    """Request for review template"""
    name: str = Field(description="Template name")
    content_type: ContentType = Field(description="Content type")
    criteria: List[Dict[str, Any]] = Field(description="Review criteria")
    constitutional_requirements: Dict[str, Any] = Field(default_factory=dict)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)


class ReviewBatch(BaseModel):
    """Batch review request"""
    tasks: List[ReviewTaskRequest] = Field(description="Tasks to review")
    batch_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    priority: ReviewPriority = Field(default=ReviewPriority.MEDIUM)
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)