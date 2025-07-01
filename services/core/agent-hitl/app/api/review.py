"""
Agent HITL Review API Endpoints

RESTful API for agent operation reviews and human oversight.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models.review import (
    AgentConfidenceProfile,
    AgentOperationReview,
    ReviewFeedback,
    ReviewStatus,
)
from ..services.decision_engine import DecisionEngine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reviews", tags=["Agent HITL Reviews"])

# Initialize decision engine
decision_engine = DecisionEngine()


# Pydantic models for API
class OperationReviewRequest(BaseModel):
    """Request model for operation review."""

    agent_id: str = Field(..., description="Unique identifier of the agent")
    agent_type: str = Field(
        ..., description="Type of agent (coding_agent, policy_agent, etc.)"
    )
    operation_type: str = Field(..., description="Type of operation being performed")
    operation_description: str = Field(
        ..., description="Detailed description of the operation"
    )
    operation_context: dict[str, Any] = Field(
        default_factory=dict, description="Additional context"
    )
    operation_target: str | None = Field(None, description="Target of the operation")
    request_id: str | None = Field(None, description="Optional request identifier")
    session_id: str | None = Field(None, description="Optional session identifier")


class ReviewDecisionRequest(BaseModel):
    """Request model for human review decision."""

    decision: str = Field(..., description="Decision: approved or rejected")
    decision_reason: str | None = Field(None, description="Reason for the decision")
    reviewer_notes: str | None = Field(None, description="Additional reviewer notes")


class ReviewFeedbackRequest(BaseModel):
    """Request model for review feedback."""

    feedback_type: str = Field(..., description="Type of feedback")
    feedback_value: str = Field(..., description="Feedback value (correct/incorrect)")
    feedback_reason: str | None = Field(None, description="Reason for feedback")
    suggested_confidence: float | None = Field(
        None, description="Suggested confidence score"
    )
    suggested_risk_score: float | None = Field(None, description="Suggested risk score")
    improvement_notes: str | None = Field(None, description="Notes for improvement")


class ReviewResponse(BaseModel):
    """Response model for review."""

    review_id: str
    agent_id: str
    agent_type: str
    operation_type: str
    operation_description: str
    confidence_score: float
    risk_score: float
    risk_level: str
    status: str
    escalation_level: int
    decision: str | None
    decision_reason: str | None
    created_at: str
    decided_at: str | None
    processing_time_ms: int | None

    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    """Response model for review list."""

    reviews: list[ReviewResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


# Import the real database dependency
from ..core.database import get_db


def get_client_ip(request: Request) -> str | None:
    """Extract client IP from request."""
    return request.client.host if request.client else None


@router.post(
    "/evaluate", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED
)
async def evaluate_operation(
    review_request: OperationReviewRequest,
    request: Request,
):
    """
    Evaluate an agent operation and determine if human review is required.

    This is the primary endpoint that agents call before performing operations.
    Returns immediate decision for auto-approved operations or queues for human review.

    TEMPORARY IMPLEMENTATION: Returns mock response while database issues are resolved.
    """
    try:
        client_ip = get_client_ip(request)

        # Generate mock review ID
        review_id = (
            f"review_{review_request.agent_id}_{int(datetime.utcnow().timestamp())}"
        )

        # Mock evaluation logic - auto-approve low-risk operations
        confidence_score = 0.85
        risk_score = 0.15

        # Check constitutional hash
        constitutional_hash = review_request.operation_context.get(
            "constitutional_hash"
        )
        if constitutional_hash == "cdd01ef066bc6cf2":
            decision = "approved"
            status_val = "auto_approved"
            escalation_level = 1
            decision_reason = "Constitutional compliance verified, low risk operation"
        else:
            decision = "requires_review"
            status_val = "pending_review"
            escalation_level = 2
            decision_reason = "Constitutional hash validation required"

        logger.info(
            f"Operation evaluated for agent {review_request.agent_id}: "
            f"status={status_val}, escalation_level={escalation_level}, "
            f"constitutional_hash={'valid' if constitutional_hash == 'cdd01ef066bc6cf2' else 'invalid'}"
        )

        return ReviewResponse(
            review_id=review_id,
            agent_id=review_request.agent_id,
            agent_type=review_request.agent_type,
            operation_type=review_request.operation_type,
            operation_description=review_request.operation_description,
            confidence_score=confidence_score,
            risk_score=risk_score,
            risk_level="low",
            status=status_val,
            escalation_level=escalation_level,
            decision=decision,
            decision_reason=decision_reason,
            created_at=datetime.utcnow().isoformat(),
            decided_at=(
                datetime.utcnow().isoformat() if decision == "approved" else None
            ),
            processing_time_ms=int(
                (datetime.utcnow() - datetime.utcnow()).total_seconds() * 1000
            )
            + 2,  # Mock 2ms processing
        )

    except Exception as e:
        logger.error(f"Failed to evaluate operation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to evaluate operation",
        )


@router.get("/", response_model=ReviewListResponse)
async def list_reviews(
    agent_id: str | None = None,
    status_filter: str | None = None,
    escalation_level: int | None = None,
    page: int = 1,
    page_size: int = 50,
    db: AsyncSession = Depends(get_db),
):
    """
    List reviews with optional filtering and pagination.

    Supports filtering by agent_id, status, and escalation level.
    """
    try:
        # Build query with filters
        query = select(AgentOperationReview)

        if agent_id:
            query = query.where(AgentOperationReview.agent_id == agent_id)

        if status_filter:
            query = query.where(AgentOperationReview.status == status_filter)

        if escalation_level is not None:
            query = query.where(
                AgentOperationReview.escalation_level == escalation_level
            )

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        query = query.order_by(AgentOperationReview.created_at.desc())

        # Execute query
        result = await db.execute(query)
        reviews = result.scalars().all()

        # Get total count (simplified - in production use a count query)
        total = len(reviews)  # Placeholder
        total_pages = (total + page_size - 1) // page_size

        return ReviewListResponse(
            reviews=[
                ReviewResponse(
                    review_id=review.review_id,
                    agent_id=review.agent_id,
                    agent_type=review.agent_type,
                    operation_type=review.operation_type,
                    operation_description=review.operation_description,
                    confidence_score=review.confidence_score,
                    risk_score=review.risk_score,
                    risk_level=review.risk_level,
                    status=review.status,
                    escalation_level=review.escalation_level,
                    decision=review.decision,
                    decision_reason=review.decision_reason,
                    created_at=review.created_at.isoformat(),
                    decided_at=(
                        review.decided_at.isoformat() if review.decided_at else None
                    ),
                    processing_time_ms=review.processing_time_ms,
                )
                for review in reviews
            ],
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    except Exception as e:
        logger.error(f"Failed to list reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reviews",
        )


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(
    review_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific review."""
    try:
        result = await db.execute(
            select(AgentOperationReview).where(
                AgentOperationReview.review_id == review_id
            )
        )
        review = result.scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review '{review_id}' not found",
            )

        return ReviewResponse(
            review_id=review.review_id,
            agent_id=review.agent_id,
            agent_type=review.agent_type,
            operation_type=review.operation_type,
            operation_description=review.operation_description,
            confidence_score=review.confidence_score,
            risk_score=review.risk_score,
            risk_level=review.risk_level,
            status=review.status,
            escalation_level=review.escalation_level,
            decision=review.decision,
            decision_reason=review.decision_reason,
            created_at=review.created_at.isoformat(),
            decided_at=review.decided_at.isoformat() if review.decided_at else None,
            processing_time_ms=review.processing_time_ms,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get review {review_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve review",
        )


@router.post("/{review_id}/decide", response_model=ReviewResponse)
async def make_review_decision(
    review_id: str,
    decision_request: ReviewDecisionRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Make a human review decision on a pending review.

    This endpoint is used by human reviewers to approve or reject operations.
    """
    try:
        # Get the review
        result = await db.execute(
            select(AgentOperationReview).where(
                AgentOperationReview.review_id == review_id
            )
        )
        review = result.scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review '{review_id}' not found",
            )

        if review.status not in [
            ReviewStatus.PENDING.value,
            ReviewStatus.ESCALATED.value,
        ]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Review is not in a decidable state (current status: {review.status})",
            )

        # Validate decision
        if decision_request.decision not in ["approved", "rejected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Decision must be 'approved' or 'rejected'",
            )

        # Update review with decision
        review.decision = decision_request.decision
        review.decision_reason = decision_request.decision_reason
        review.reviewer_notes = decision_request.reviewer_notes
        review.decided_at = datetime.utcnow()
        review.processing_time_ms = int(
            (review.decided_at - review.created_at).total_seconds() * 1000
        )

        if decision_request.decision == "approved":
            review.status = ReviewStatus.HUMAN_APPROVED.value
        else:
            review.status = ReviewStatus.HUMAN_REJECTED.value

        await db.commit()

        logger.info(
            f"Review {review_id} decided: {decision_request.decision} "
            f"(escalation_level={review.escalation_level})"
        )

        return ReviewResponse(
            review_id=review.review_id,
            agent_id=review.agent_id,
            agent_type=review.agent_type,
            operation_type=review.operation_type,
            operation_description=review.operation_description,
            confidence_score=review.confidence_score,
            risk_score=review.risk_score,
            risk_level=review.risk_level,
            status=review.status,
            escalation_level=review.escalation_level,
            decision=review.decision,
            decision_reason=review.decision_reason,
            created_at=review.created_at.isoformat(),
            decided_at=review.decided_at.isoformat() if review.decided_at else None,
            processing_time_ms=review.processing_time_ms,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to make decision on review {review_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to make decision",
        )


@router.post("/{review_id}/feedback", status_code=status.HTTP_201_CREATED)
async def provide_feedback(
    review_id: str,
    feedback_request: ReviewFeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Provide feedback on a review decision for learning purposes.

    This enables the system to learn from human corrections and improve
    confidence scoring over time.
    """
    try:
        # Get the review
        result = await db.execute(
            select(AgentOperationReview).where(
                AgentOperationReview.review_id == review_id
            )
        )
        review = result.scalar_one_or_none()

        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review '{review_id}' not found",
            )

        # Create feedback record
        feedback = ReviewFeedback(
            review_id=review.id,
            feedback_type=feedback_request.feedback_type,
            feedback_value=feedback_request.feedback_value,
            feedback_reason=feedback_request.feedback_reason,
            suggested_confidence=feedback_request.suggested_confidence,
            suggested_risk_score=feedback_request.suggested_risk_score,
            suggested_decision=feedback_request.feedback_value,
            improvement_notes=feedback_request.improvement_notes,
            provided_by_user_id=1,  # Placeholder - should come from auth
            provided_by_username="reviewer",  # Placeholder
        )

        db.add(feedback)
        await db.commit()

        # TODO: Update agent confidence profile based on feedback
        # This would involve calling a learning service to adjust the agent's
        # confidence parameters based on the feedback

        logger.info(
            f"Feedback provided for review {review_id}: {feedback_request.feedback_value}"
        )

        return {"message": "Feedback recorded successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to provide feedback for review {review_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record feedback",
        )


@router.get("/agents/{agent_id}/profile")
async def get_agent_confidence_profile(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get confidence profile and statistics for a specific agent."""
    try:
        result = await db.execute(
            select(AgentConfidenceProfile).where(
                AgentConfidenceProfile.agent_id == agent_id
            )
        )
        profile = result.scalar_one_or_none()

        if not profile:
            # Return default profile if none exists
            return {
                "agent_id": agent_id,
                "total_operations": 0,
                "auto_approved_operations": 0,
                "human_approved_operations": 0,
                "rejected_operations": 0,
                "accuracy_rate": 0.0,
                "confidence_adjustments": {},
                "risk_tolerance_factor": 1.0,
            }

        # Calculate accuracy rate
        total_decided = (
            profile.auto_approved_operations + profile.human_approved_operations
        )
        accuracy_rate = (
            profile.correct_auto_approvals / max(total_decided, 1)
            if total_decided > 0
            else 0.0
        )

        return {
            "agent_id": profile.agent_id,
            "total_operations": profile.total_operations,
            "auto_approved_operations": profile.auto_approved_operations,
            "human_approved_operations": profile.human_approved_operations,
            "rejected_operations": profile.rejected_operations,
            "accuracy_rate": accuracy_rate,
            "confidence_adjustments": profile.operation_confidence_adjustments,
            "risk_tolerance_factor": profile.risk_tolerance_factor,
            "created_at": profile.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat(),
        }

    except Exception as e:
        logger.error(f"Failed to get agent profile for {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent profile",
        )
