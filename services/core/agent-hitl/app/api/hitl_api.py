"""
Agent HITL API Endpoints

RESTful API for Human-in-the-Loop agent oversight operations.
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..schemas.hitl_schemas import (
    HITLEvaluationRequest,
    HITLDecisionResponse,
    AgentConfidenceProfileResponse,
    AgentConfidenceUpdate,
    HumanReviewTaskResponse,
    HumanReviewSubmission,
    HITLFeedbackCreate,
    HITLDashboardData,
    HITLMetrics,
    HITLSearchRequest,
)
from ..services.hitl_decision_engine import HITLDecisionEngine
from ..services.hitl_service import HITLService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/hitl", tags=["Agent HITL"])

# Initialize services
hitl_service = HITLService()


def get_decision_engine() -> HITLDecisionEngine:
    """Get HITL decision engine instance."""
    # This would be injected from the main app
    from ..main import decision_engine

    if decision_engine is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="HITL decision engine not available",
        )
    return decision_engine


@router.post(
    "/evaluate",
    response_model=HITLDecisionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def evaluate_agent_operation(
    evaluation_request: HITLEvaluationRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    decision_engine: HITLDecisionEngine = Depends(get_decision_engine),
):
    """
    Evaluate an agent operation for HITL decision.

    This is the core endpoint for agent oversight - determines whether an operation
    should be automatically approved, escalated for human review, or sent to
    Constitutional Council.

    Target: <5ms P99 latency for Level 1 (automated approval) decisions.
    """
    try:
        logger.info(
            f"Evaluating operation for agent {evaluation_request.operation_request.agent_id}"
        )

        # Evaluate the operation
        decision = await decision_engine.evaluate_operation(
            db=db,
            operation_request=evaluation_request.operation_request,
            force_escalation_level=evaluation_request.force_escalation_level,
            bypass_cache=evaluation_request.bypass_cache,
        )

        logger.info(
            f"Decision made for agent {evaluation_request.operation_request.agent_id}: "
            f"{decision.escalation_level} (confidence: {decision.confidence_score:.3f}, "
            f"time: {decision.processing_time_ms:.2f}ms)"
        )

        return decision

    except Exception as e:
        logger.error(f"Operation evaluation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate operation: {str(e)}",
        )


@router.get("/decision/{decision_id}", response_model=HITLDecisionResponse)
async def get_decision(
    decision_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get details of a specific HITL decision."""
    try:
        decision = await hitl_service.get_decision(db, decision_id)
        if not decision:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Decision '{decision_id}' not found",
            )

        return decision

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get decision {decision_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve decision",
        )


@router.get(
    "/agents/{agent_id}/confidence", response_model=AgentConfidenceProfileResponse
)
async def get_agent_confidence(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get confidence profile for a specific agent."""
    try:
        confidence_profile = await hitl_service.get_agent_confidence_profile(
            db, agent_id
        )
        if not confidence_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Confidence profile for agent '{agent_id}' not found",
            )

        return confidence_profile

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent confidence {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve agent confidence",
        )


@router.post("/agents/{agent_id}/confidence")
async def update_agent_confidence(
    agent_id: str,
    confidence_update: AgentConfidenceUpdate,
    db: AsyncSession = Depends(get_db),
):
    """Update agent confidence based on operation outcome."""
    try:
        updated_profile = await hitl_service.update_agent_confidence(
            db, agent_id, confidence_update
        )

        if not updated_profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent '{agent_id}' not found",
            )

        return {
            "message": "Agent confidence updated successfully",
            "agent_id": agent_id,
            "new_confidence": updated_profile.overall_confidence_score,
            "operation_type": confidence_update.operation_type,
            "success": confidence_update.success,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update agent confidence {agent_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update agent confidence",
        )


@router.get("/tasks", response_model=List[HumanReviewTaskResponse])
async def get_pending_review_tasks(
    limit: int = 50,
    assigned_to_me: bool = False,
    priority_min: int = 1,
    db: AsyncSession = Depends(get_db),
):
    """Get pending human review tasks."""
    try:
        tasks = await hitl_service.get_pending_review_tasks(
            db, limit=limit, assigned_to_me=assigned_to_me, priority_min=priority_min
        )

        return tasks

    except Exception as e:
        logger.error(f"Failed to get review tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve review tasks",
        )


@router.post("/tasks/{task_id}/review")
async def submit_human_review(
    task_id: str,
    review_submission: HumanReviewSubmission,
    db: AsyncSession = Depends(get_db),
):
    """Submit human review for a task."""
    try:
        result = await hitl_service.submit_human_review(db, task_id, review_submission)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Review task '{task_id}' not found",
            )

        return {
            "message": "Review submitted successfully",
            "task_id": task_id,
            "decision": review_submission.review_decision,
            "confidence": review_submission.review_confidence,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to submit review for task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit review",
        )


@router.post("/feedback")
async def submit_feedback(
    feedback: HITLFeedbackCreate,
    db: AsyncSession = Depends(get_db),
):
    """Submit feedback on HITL decisions for system improvement."""
    try:
        result = await hitl_service.submit_feedback(db, feedback)

        return {
            "message": "Feedback submitted successfully",
            "feedback_id": result.feedback_id,
            "decision_id": feedback.decision_id,
            "feedback_type": feedback.feedback_type,
        }

    except Exception as e:
        logger.error(f"Failed to submit feedback: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback",
        )


@router.get("/dashboard", response_model=HITLDashboardData)
async def get_dashboard_data(
    db: AsyncSession = Depends(get_db),
):
    """Get dashboard data for HITL system monitoring."""
    try:
        dashboard_data = await hitl_service.get_dashboard_data(db)
        return dashboard_data

    except Exception as e:
        logger.error(f"Failed to get dashboard data: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dashboard data",
        )


@router.get("/metrics", response_model=HITLMetrics)
async def get_hitl_metrics(
    db: AsyncSession = Depends(get_db),
):
    """Get HITL system performance metrics."""
    try:
        metrics = await hitl_service.get_metrics(db)
        return metrics

    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve metrics",
        )


@router.post("/search", response_model=List[HITLDecisionResponse])
async def search_decisions(
    search_request: HITLSearchRequest,
    db: AsyncSession = Depends(get_db),
):
    """Search HITL decisions with filtering and pagination."""
    try:
        decisions = await hitl_service.search_decisions(db, search_request)
        return decisions

    except Exception as e:
        logger.error(f"Failed to search decisions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search decisions",
        )
