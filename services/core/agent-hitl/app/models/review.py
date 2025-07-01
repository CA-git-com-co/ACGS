"""
Agent HITL Review Models

Database models for agent operation reviews and decisions.
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from sqlalchemy import (
    JSON,
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


class ReviewStatus(str, Enum):
    """Status of a review request."""

    PENDING = "pending"
    AUTO_APPROVED = "auto_approved"
    HUMAN_APPROVED = "human_approved"
    HUMAN_REJECTED = "human_rejected"
    ESCALATED = "escalated"
    TIMEOUT = "timeout"
    ERROR = "error"


class EscalationLevel(int, Enum):
    """Escalation levels for review."""

    LEVEL_1_AUTO = 1  # Automated approval
    LEVEL_2_TEAM_LEAD = 2  # Team lead review
    LEVEL_3_DOMAIN_EXPERT = 3  # Domain expert review
    LEVEL_4_CONSTITUTIONAL_COUNCIL = 4  # Constitutional Council review


class RiskLevel(str, Enum):
    """Risk assessment levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AgentOperationReview(Base):
    """Model for agent operation review requests."""

    __tablename__ = "agent_operation_reviews"

    # Primary identifiers
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(String(100), unique=True, nullable=False, index=True)

    # Agent information
    agent_id = Column(String(100), nullable=False, index=True)
    agent_type = Column(String(50), nullable=False)
    agent_version = Column(String(50))

    # Operation details
    operation_type = Column(String(100), nullable=False, index=True)
    operation_description = Column(Text, nullable=False)
    operation_context = Column(JSON, nullable=False, default={})
    operation_target = Column(String(500))  # e.g., file path, API endpoint

    # Confidence and risk assessment
    confidence_score = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_level = Column(String(20), nullable=False, default=RiskLevel.LOW.value)
    confidence_factors = Column(JSON, default={})
    risk_factors = Column(JSON, default={})

    # Constitutional compliance
    constitutional_hash = Column(String(64), nullable=False)
    policy_violations = Column(JSON, default=[])
    applicable_principles = Column(JSON, default=[])

    # Review status and decision
    status = Column(
        String(20), nullable=False, default=ReviewStatus.PENDING.value, index=True
    )
    escalation_level = Column(
        Integer, nullable=False, default=EscalationLevel.LEVEL_1_AUTO.value
    )
    decision = Column(String(20))  # approved, rejected
    decision_reason = Column(Text)
    decision_metadata = Column(JSON, default={})

    # Timing information
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    decided_at = Column(DateTime, index=True)
    processing_time_ms = Column(Integer)

    # Human review information
    reviewed_by_user_id = Column(Integer)
    reviewed_by_username = Column(String(255))
    reviewer_notes = Column(Text)

    # Request metadata
    request_id = Column(String(100), index=True)
    session_id = Column(String(100))
    client_ip = Column(String(45))

    # Additional metadata
    review_metadata = Column(JSON, default={})
    tags = Column(JSON, default=[])

    # Relationships
    feedbacks = relationship(
        "ReviewFeedback", back_populates="review", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {
            "id": str(self.id),
            "review_id": self.review_id,
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "operation_type": self.operation_type,
            "operation_description": self.operation_description,
            "confidence_score": self.confidence_score,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "status": self.status,
            "escalation_level": self.escalation_level,
            "decision": self.decision,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "decided_at": self.decided_at.isoformat() if self.decided_at else None,
        }


class ReviewFeedback(Base):
    """Model for feedback on review decisions."""

    __tablename__ = "review_feedbacks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(
        UUID(as_uuid=True), ForeignKey("agent_operation_reviews.id"), nullable=False
    )

    # Feedback details
    feedback_type = Column(
        String(50), nullable=False
    )  # approval, correction, policy_update
    feedback_value = Column(String(20), nullable=False)  # correct, incorrect
    feedback_reason = Column(Text)

    # Suggestions for improvement
    suggested_confidence = Column(Float)
    suggested_risk_score = Column(Float)
    suggested_decision = Column(String(20))
    improvement_notes = Column(Text)

    # Metadata
    provided_by_user_id = Column(Integer, nullable=False)
    provided_by_username = Column(String(255))
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationship
    review = relationship("AgentOperationReview", back_populates="feedbacks")


class AgentConfidenceProfile(Base):
    """Model for tracking agent-specific confidence patterns."""

    __tablename__ = "agent_confidence_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id = Column(String(100), unique=True, nullable=False, index=True)

    # Operation-specific confidence adjustments
    operation_confidence_adjustments = Column(JSON, default={})

    # Historical performance metrics
    total_operations = Column(Integer, default=0)
    auto_approved_operations = Column(Integer, default=0)
    human_approved_operations = Column(Integer, default=0)
    rejected_operations = Column(Integer, default=0)

    # Accuracy metrics
    correct_auto_approvals = Column(Integer, default=0)
    incorrect_auto_approvals = Column(Integer, default=0)

    # Adaptive confidence parameters
    base_confidence_adjustment = Column(Float, default=0.0)
    risk_tolerance_factor = Column(Float, default=1.0)

    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Profile metadata
    profile_version = Column(Integer, default=1)
    profile_metadata = Column(JSON, default={})
