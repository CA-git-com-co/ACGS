"""
Agent HITL Data Models

Database models for the Agent Human-in-the-Loop oversight system.
Provides comprehensive tracking of decisions, reviews, and feedback.
"""

import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class EscalationLevel(str, Enum):
    """HITL escalation levels."""

    LEVEL_1_AUTO_APPROVE = "level_1_auto_approve"  # <5ms automated approval
    LEVEL_2_AUTO_NOTIFY = "level_2_auto_notify"  # <100ms automated with notification
    LEVEL_3_HUMAN_REVIEW = "level_3_human_review"  # <30s human approval required
    LEVEL_4_COUNCIL_REVIEW = (
        "level_4_council_review"  # <24h Constitutional Council review
    )


class DecisionStatus(str, Enum):
    """Decision processing status."""

    PENDING = "pending"  # Decision being processed
    APPROVED = "approved"  # Operation approved
    REJECTED = "rejected"  # Operation rejected
    ESCALATED = "escalated"  # Escalated to higher level
    TIMEOUT = "timeout"  # Decision timed out
    ERROR = "error"  # Processing error


class ReviewTaskStatus(str, Enum):
    """Human review task status."""

    ASSIGNED = "assigned"  # Task assigned to reviewer
    IN_PROGRESS = "in_progress"  # Reviewer working on task
    COMPLETED = "completed"  # Review completed
    ESCALATED = "escalated"  # Escalated to higher authority
    EXPIRED = "expired"  # Task expired without review


class OperationRiskLevel(str, Enum):
    """Operation risk classification."""

    LOW = "low"  # Routine operations
    MEDIUM = "medium"  # Standard operations with some risk
    HIGH = "high"  # Operations requiring careful review
    CRITICAL = "critical"  # Operations affecting core systems


class AgentOperationRequest(Base):
    """
    Agent operation request requiring HITL evaluation.
    """

    __tablename__ = "agent_operation_requests"

    # Primary identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    request_id = Column(String(100), unique=True, nullable=False, index=True)

    # Agent and operation details
    agent_id = Column(
        String(100), nullable=False, index=True
    )  # From Agent Identity Management
    operation_type = Column(String(100), nullable=False, index=True)
    operation_data = Column(JSON, nullable=False)
    operation_context = Column(JSON, nullable=True)

    # Risk assessment
    risk_level = Column(
        String(20), nullable=False, default=OperationRiskLevel.MEDIUM.value
    )
    risk_factors = Column(JSON, nullable=True)  # Detailed risk analysis

    # Constitutional compliance
    constitutional_hash = Column(String(64), nullable=False, default="cdd01ef066bc6cf2")
    constitutional_principles = Column(JSON, nullable=True)
    requires_constitutional_review = Column(Boolean, default=False, nullable=False)

    # Timing and metadata
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    expires_at = Column(DateTime(timezone=True), nullable=True)
    client_ip = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)

    # Relationships
    decisions = relationship(
        "HITLDecision", back_populates="operation_request", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<AgentOperationRequest(id={self.id}, agent_id='{self.agent_id}', operation_type='{self.operation_type}')>"


class HITLDecision(Base):
    """
    HITL decision record for agent operations.
    """

    __tablename__ = "hitl_decisions"

    # Primary identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    decision_id = Column(String(100), unique=True, nullable=False, index=True)

    # Request reference
    operation_request_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agent_operation_requests.id"),
        nullable=False,
        index=True,
    )

    # Decision details
    escalation_level = Column(String(30), nullable=False, index=True)
    decision_status = Column(
        String(20), nullable=False, default=DecisionStatus.PENDING.value, index=True
    )
    confidence_score = Column(Float, nullable=False)  # 0.0 to 1.0

    # Decision reasoning
    decision_reasoning = Column(Text, nullable=True)
    risk_assessment = Column(JSON, nullable=True)
    constitutional_compliance_score = Column(Float, nullable=True)  # 0.0 to 1.0

    # Processing details
    processing_time_ms = Column(Float, nullable=True)  # Processing time in milliseconds
    cache_hit = Column(Boolean, default=False, nullable=False)
    decision_algorithm = Column(
        String(50), nullable=True
    )  # Algorithm used for decision

    # Human involvement
    requires_human_review = Column(Boolean, default=False, nullable=False)
    human_reviewer_id = Column(Integer, nullable=True)  # User ID from auth system
    human_decision_at = Column(DateTime(timezone=True), nullable=True)
    human_feedback = Column(Text, nullable=True)

    # Timing
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Constitutional compliance
    constitutional_hash = Column(String(64), nullable=False, default="cdd01ef066bc6cf2")
    compliance_verified = Column(Boolean, default=False, nullable=False)

    # Metadata
    decision_metadata = Column(JSON, nullable=True)

    # Relationships
    operation_request = relationship(
        "AgentOperationRequest", back_populates="decisions"
    )
    review_tasks = relationship(
        "HumanReviewTask", back_populates="decision", cascade="all, delete-orphan"
    )
    feedback_records = relationship(
        "HITLFeedback", back_populates="decision", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<HITLDecision(id={self.id}, decision_id='{self.decision_id}', status='{self.decision_status}')>"


class AgentConfidenceProfile(Base):
    """
    Agent confidence profile for HITL decision making.
    """

    __tablename__ = "agent_confidence_profiles"

    # Primary identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String(100), unique=True, nullable=False, index=True)

    # Overall confidence metrics
    overall_confidence_score = Column(Float, nullable=False, default=0.5)  # 0.0 to 1.0
    total_operations = Column(Integer, nullable=False, default=0)
    successful_operations = Column(Integer, nullable=False, default=0)
    failed_operations = Column(Integer, nullable=False, default=0)

    # Operation-specific confidence scores
    operation_type_scores = Column(
        JSON, nullable=False, default=dict
    )  # operation_type -> confidence
    risk_level_scores = Column(
        JSON, nullable=False, default=dict
    )  # risk_level -> confidence

    # Learning parameters
    learning_rate = Column(Float, nullable=False, default=0.1)
    adaptation_rate = Column(Float, nullable=False, default=0.05)
    confidence_decay_rate = Column(Float, nullable=False, default=0.01)

    # Historical performance
    performance_history = Column(JSON, nullable=True)  # Time-series performance data
    last_performance_update = Column(DateTime(timezone=True), nullable=True)

    # Constitutional compliance
    constitutional_compliance_score = Column(Float, nullable=False, default=0.8)
    constitutional_violations = Column(Integer, nullable=False, default=0)

    # Timing
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    last_decision_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    profile_metadata = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<AgentConfidenceProfile(agent_id='{self.agent_id}', confidence={self.overall_confidence_score:.3f})>"

    def get_operation_confidence(self, operation_type: str) -> float:
        """Get confidence score for specific operation type."""
        return self.operation_type_scores.get(
            operation_type, self.overall_confidence_score
        )

    def update_confidence(
        self, operation_type: str, success: bool, learning_rate: float | None = None
    ) -> None:
        """Update confidence scores based on operation outcome."""
        lr = learning_rate or self.learning_rate

        # Update operation-specific confidence
        current_confidence = self.get_operation_confidence(operation_type)
        if success:
            new_confidence = current_confidence + lr * (1.0 - current_confidence)
        else:
            new_confidence = current_confidence - lr * current_confidence

        self.operation_type_scores[operation_type] = max(0.0, min(1.0, new_confidence))

        # Update overall confidence
        total_ops = self.total_operations + 1
        if success:
            self.successful_operations += 1
        else:
            self.failed_operations += 1

        self.total_operations = total_ops
        self.overall_confidence_score = (
            self.successful_operations / total_ops if total_ops > 0 else 0.5
        )
        self.updated_at = datetime.now(timezone.utc)


class HumanReviewTask(Base):
    """
    Human review task for agent operations requiring manual oversight.
    """

    __tablename__ = "human_review_tasks"

    # Primary identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    task_id = Column(String(100), unique=True, nullable=False, index=True)

    # Decision reference
    decision_id = Column(
        UUID(as_uuid=True), ForeignKey("hitl_decisions.id"), nullable=False, index=True
    )

    # Task details
    task_type = Column(
        String(50), nullable=False
    )  # review, escalation, constitutional_review
    priority = Column(Integer, nullable=False, default=5)  # 1 (highest) to 10 (lowest)
    status = Column(
        String(20), nullable=False, default=ReviewTaskStatus.ASSIGNED.value, index=True
    )

    # Assignment
    assigned_reviewer_id = Column(
        Integer, nullable=True, index=True
    )  # User ID from auth system
    assigned_at = Column(DateTime(timezone=True), nullable=True)
    reviewer_expertise = Column(JSON, nullable=True)  # Required expertise for task

    # Task context
    operation_summary = Column(Text, nullable=False)
    risk_factors = Column(JSON, nullable=True)
    constitutional_concerns = Column(JSON, nullable=True)
    agent_context = Column(JSON, nullable=True)  # Agent history and profile

    # Review details
    review_started_at = Column(DateTime(timezone=True), nullable=True)
    review_completed_at = Column(DateTime(timezone=True), nullable=True)
    review_decision = Column(String(20), nullable=True)  # approve, reject, escalate
    review_reasoning = Column(Text, nullable=True)
    review_confidence = Column(
        Float, nullable=True
    )  # Reviewer's confidence in decision

    # Timing constraints
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    due_at = Column(DateTime(timezone=True), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    task_metadata = Column(JSON, nullable=True)

    # Relationships
    decision = relationship("HITLDecision", back_populates="review_tasks")

    def __repr__(self):
        return f"<HumanReviewTask(id={self.id}, task_id='{self.task_id}', status='{self.status}')>"


class HITLFeedback(Base):
    """
    Feedback record for HITL decisions to improve system performance.
    """

    __tablename__ = "hitl_feedback"

    # Primary identity
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feedback_id = Column(String(100), unique=True, nullable=False, index=True)

    # Decision reference
    decision_id = Column(
        UUID(as_uuid=True), ForeignKey("hitl_decisions.id"), nullable=False, index=True
    )

    # Feedback details
    feedback_type = Column(
        String(50), nullable=False
    )  # human_review, outcome_validation, performance_feedback
    feedback_source = Column(
        String(50), nullable=False
    )  # human_reviewer, system_monitoring, agent_outcome

    # Feedback content
    original_confidence = Column(Float, nullable=False)
    suggested_confidence = Column(Float, nullable=True)
    confidence_adjustment = Column(Float, nullable=True)  # Calculated adjustment

    # Human feedback
    human_reviewer_id = Column(Integer, nullable=True)
    human_agreed_with_decision = Column(Boolean, nullable=True)
    human_reasoning = Column(Text, nullable=True)
    human_confidence_rating = Column(Float, nullable=True)  # 0.0 to 1.0

    # Outcome validation
    actual_outcome = Column(
        String(50), nullable=True
    )  # success, failure, partial_success
    outcome_details = Column(JSON, nullable=True)
    constitutional_compliance_actual = Column(Boolean, nullable=True)

    # Learning impact
    learning_weight = Column(Float, nullable=False, default=1.0)
    applied_to_agent = Column(Boolean, default=False, nullable=False)
    confidence_impact = Column(
        Float, nullable=True
    )  # Actual impact on confidence scores

    # Timing
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Metadata
    feedback_metadata = Column(JSON, nullable=True)

    # Relationships
    decision = relationship("HITLDecision", back_populates="feedback_records")

    def __repr__(self):
        return f"<HITLFeedback(id={self.id}, feedback_type='{self.feedback_type}', source='{self.feedback_source}')>"
