"""
Evolution API endpoints for ACGS-1 Self-Evolving AI Architecture Foundation.

This module provides REST API endpoints for managing evolution cycles,
including initiation, approval, status tracking, and rollback operations.
"""

import logging
from datetime import UTC
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field

from ...core.evolution_engine import EvolutionEngine, EvolutionRequest, EvolutionType
from ...dependencies import get_evolution_engine

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models
class EvolutionInitiationRequest(BaseModel):
    """Request model for evolution initiation."""

    evolution_type: str = Field(
        ...,
        description="Type of evolution (policy_refinement, rule_optimization, etc.)",
    )
    description: str = Field(..., description="Description of the evolution")
    target_policies: list[str] = Field(
        default_factory=list, description="List of target policy IDs"
    )
    proposed_changes: dict[str, Any] = Field(
        default_factory=dict, description="Proposed changes"
    )
    justification: str = Field(..., description="Justification for the evolution")
    requester_id: str = Field(..., description="ID of the requesting user")
    priority: str = Field(
        default="medium", description="Priority level (low, medium, high, critical)"
    )
    estimated_duration_minutes: int = Field(
        default=10, description="Estimated duration in minutes"
    )
    requires_constitutional_validation: bool = Field(
        default=True, description="Whether constitutional validation is required"
    )
    requires_formal_verification: bool = Field(
        default=True, description="Whether formal verification is required"
    )


class EvolutionApprovalRequest(BaseModel):
    """Request model for evolution approval."""

    approver_id: str = Field(..., description="ID of the approving user")
    approval_notes: str = Field(default="", description="Optional approval notes")


class EvolutionRollbackRequest(BaseModel):
    """Request model for evolution rollback."""

    rollback_reason: str = Field(..., description="Reason for rollback")


class EvolutionResponse(BaseModel):
    """Response model for evolution operations."""

    success: bool
    evolution_id: str | None = None
    message: str
    data: dict[str, Any] | None = None


class EvolutionStatusResponse(BaseModel):
    """Response model for evolution status."""

    found: bool
    evolution_id: str | None = None
    status: str | None = None
    data: dict[str, Any] | None = None


# API Endpoints
@router.post("/initiate", response_model=EvolutionResponse)
async def initiate_evolution(
    request: EvolutionInitiationRequest,
    background_tasks: BackgroundTasks,
    evolution_engine: EvolutionEngine = Depends(get_evolution_engine),
):
    """
    Initiate a new evolution cycle.

    This endpoint starts a new evolution cycle with manual policy evolution
    and comprehensive safety controls. All evolutions require human approval
    unless specifically configured otherwise.
    """
    try:
        # Create evolution request
        evolution_request = EvolutionRequest(
            evolution_type=EvolutionType(request.evolution_type),
            description=request.description,
            target_policies=request.target_policies,
            proposed_changes=request.proposed_changes,
            justification=request.justification,
            requester_id=request.requester_id,
            priority=request.priority,
            estimated_duration_minutes=request.estimated_duration_minutes,
            requires_constitutional_validation=request.requires_constitutional_validation,
            requires_formal_verification=request.requires_formal_verification,
        )

        # Initiate evolution
        success, evolution_id, status_info = await evolution_engine.initiate_evolution(
            evolution_request
        )

        if success:
            return EvolutionResponse(
                success=True,
                evolution_id=evolution_id,
                message="Evolution initiated successfully",
                data=status_info,
            )
        else:
            return EvolutionResponse(
                success=False, message="Failed to initiate evolution", data=status_info
            )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Evolution initiation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{evolution_id}/approve", response_model=EvolutionResponse)
async def approve_evolution(
    evolution_id: str,
    request: EvolutionApprovalRequest,
    evolution_engine: EvolutionEngine = Depends(get_evolution_engine),
):
    """
    Approve a pending evolution cycle.

    This endpoint provides human-in-the-loop control for evolution approval.
    Only authorized users can approve evolution cycles, ensuring human oversight
    of all autonomous policy modifications.
    """
    try:
        success, status_info = await evolution_engine.approve_evolution(
            evolution_id, request.approver_id, request.approval_notes
        )

        if success:
            return EvolutionResponse(
                success=True,
                evolution_id=evolution_id,
                message="Evolution approved successfully",
                data=status_info,
            )
        else:
            return EvolutionResponse(
                success=False,
                evolution_id=evolution_id,
                message="Failed to approve evolution",
                data=status_info,
            )

    except Exception as e:
        logger.error(f"Evolution approval failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{evolution_id}/status", response_model=EvolutionStatusResponse)
async def get_evolution_status(
    evolution_id: str, evolution_engine: EvolutionEngine = Depends(get_evolution_engine)
):
    """
    Get the status of an evolution cycle.

    This endpoint provides real-time status information for evolution cycles,
    including progress, current phase, and estimated completion time.
    """
    try:
        found, status_info = await evolution_engine.get_evolution_status(evolution_id)

        return EvolutionStatusResponse(
            found=found,
            evolution_id=evolution_id if found else None,
            status=status_info.get("status") if found else None,
            data=status_info if found else {"error": "Evolution not found"},
        )

    except Exception as e:
        logger.error(f"Get evolution status failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{evolution_id}/rollback", response_model=EvolutionResponse)
async def rollback_evolution(
    evolution_id: str,
    request: EvolutionRollbackRequest,
    evolution_engine: EvolutionEngine = Depends(get_evolution_engine),
):
    """
    Rollback a completed evolution cycle.

    This endpoint provides the ability to rollback evolution changes if issues
    are discovered after deployment. Rollback operations are logged and audited
    for compliance and traceability.
    """
    try:
        success, rollback_info = await evolution_engine.rollback_evolution(
            evolution_id, request.rollback_reason
        )

        if success:
            return EvolutionResponse(
                success=True,
                evolution_id=evolution_id,
                message="Evolution rolled back successfully",
                data=rollback_info,
            )
        else:
            return EvolutionResponse(
                success=False,
                evolution_id=evolution_id,
                message="Failed to rollback evolution",
                data=rollback_info,
            )

    except Exception as e:
        logger.error(f"Evolution rollback failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/metrics")
async def get_evolution_metrics(
    evolution_engine: EvolutionEngine = Depends(get_evolution_engine),
):
    """
    Get evolution engine performance metrics.

    This endpoint provides comprehensive metrics about evolution cycles,
    including success rates, average duration, and performance indicators.
    """
    try:
        metrics = await evolution_engine.get_evolution_metrics()
        return {
            "success": True,
            "message": "Evolution metrics retrieved successfully",
            "data": metrics,
        }

    except Exception as e:
        logger.error(f"Get evolution metrics failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/active")
async def get_active_evolutions(
    evolution_engine: EvolutionEngine = Depends(get_evolution_engine),
):
    """
    Get all active evolution cycles.

    This endpoint returns information about all currently active evolution
    cycles, including their status, progress, and estimated completion times.
    """
    try:
        active_evolutions = []

        for evolution_id in evolution_engine.active_evolutions.keys():
            found, status_info = await evolution_engine.get_evolution_status(
                evolution_id
            )
            if found:
                active_evolutions.append({"evolution_id": evolution_id, **status_info})

        return {
            "success": True,
            "message": f"Retrieved {len(active_evolutions)} active evolutions",
            "data": {
                "active_evolutions": active_evolutions,
                "total_count": len(active_evolutions),
            },
        }

    except Exception as e:
        logger.error(f"Get active evolutions failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{evolution_id}")
async def cancel_evolution(
    evolution_id: str, evolution_engine: EvolutionEngine = Depends(get_evolution_engine)
):
    """
    Cancel an active evolution cycle.

    This endpoint allows cancellation of active evolution cycles that are
    no longer needed or have encountered issues. Cancelled evolutions are
    logged for audit purposes.
    """
    try:
        if evolution_id not in evolution_engine.active_evolutions:
            raise HTTPException(status_code=404, detail="Evolution not found")

        # Update evolution status to cancelled
        evolution = evolution_engine.active_evolutions[evolution_id]
        evolution.status = evolution_engine.EvolutionStatus.CANCELLED

        # Move to history
        from datetime import datetime

        from ...core.evolution_engine import EvolutionResult, EvolutionStatus

        result = EvolutionResult(
            evolution_id=evolution_id,
            status=EvolutionStatus.CANCELLED,
            success=False,
            error_message="Evolution cancelled by user request",
            completed_at=datetime.now(UTC),
            rollback_available=False,
        )

        evolution_engine.evolution_history.append(result)
        del evolution_engine.active_evolutions[evolution_id]

        return {
            "success": True,
            "message": "Evolution cancelled successfully",
            "data": {
                "evolution_id": evolution_id,
                "status": "cancelled",
                "cancelled_at": result.completed_at.isoformat(),
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Evolution cancellation failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/health")
async def evolution_health_check(
    evolution_engine: EvolutionEngine = Depends(get_evolution_engine),
):
    """
    Health check for the evolution engine.

    This endpoint provides health status information for the evolution engine,
    including service integrations and operational status.
    """
    try:
        health_status = await evolution_engine.health_check()

        if health_status.get("healthy", False):
            return {
                "status": "healthy",
                "message": "Evolution engine is operational",
                "data": health_status,
            }
        else:
            return {
                "status": "unhealthy",
                "message": "Evolution engine has issues",
                "data": health_status,
            }

    except Exception as e:
        logger.error(f"Evolution health check failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
