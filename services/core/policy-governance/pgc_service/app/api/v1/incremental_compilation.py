"""
API endpoints for Enhanced Incremental Policy Compilation (Task 8)

Provides endpoints for zero-downtime policy deployment, rollback operations,
and integration with constitutional amendment workflows.
"""

import logging
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field

# Fix import path for shared modules
import sys
sys.path.append('/home/dislove/ACGS-1/services/shared')

from auth import get_current_user, User

from ...core.incremental_compiler import IncrementalCompiler, get_incremental_compiler
from ...services.integrity_client import IntegrityPolicyRule

logger = logging.getLogger(__name__)

router = APIRouter()


# ===== Request/Response Models =====


class PolicyDeploymentRequest(BaseModel):
    """Request model for policy deployment."""

    policies: list[dict[str, Any]] = Field(..., description="Policy rules to deploy")
    amendment_id: int | None = Field(None, description="Constitutional amendment ID")
    force_hot_swap: bool = Field(
        False, description="Force hot-swap deployment strategy"
    )
    deployment_notes: str | None = Field(None, description="Deployment notes")


class PolicyRollbackRequest(BaseModel):
    """Request model for policy rollback."""

    policy_id: str = Field(..., description="Policy ID to rollback")
    target_version: int | None = Field(
        None, description="Target version (defaults to previous)"
    )
    rollback_reason: str = Field("Manual rollback", description="Reason for rollback")


class DeploymentStatusResponse(BaseModel):
    """Response model for deployment status."""

    success: bool
    deployment_id: str | None = None
    policies_deployed: int | None = None
    deployment_time_ms: float | None = None
    deployment_strategy: str | None = None
    error: str | None = None
    health_status: dict[str, bool] | None = None


class RollbackStatusResponse(BaseModel):
    """Response model for rollback status."""

    success: bool
    policy_id: str | None = None
    previous_version: int | None = None
    rollback_version: int | None = None
    rollback_time_ms: float | None = None
    error: str | None = None


class CompilationMetricsResponse(BaseModel):
    """Response model for compilation metrics."""

    total_compilations: int
    hot_swap_deployments: int
    rollback_operations: int
    validation_failures: int
    deployment_failures: int
    average_compilation_time_ms: float
    average_deployment_time_ms: float
    active_deployments: int
    version_history_size: int
    rollback_points_count: int


# ===== API Endpoints =====


@router.post("/deploy", response_model=DeploymentStatusResponse)
async def deploy_policy_update(
    request: PolicyDeploymentRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    compiler: IncrementalCompiler = Depends(get_incremental_compiler),
) -> DeploymentStatusResponse:
    """
    Deploy policy update with zero-downtime hot-swapping.

    Supports:
    - Constitutional amendment integration
    - Parallel validation pipeline integration
    - Automatic rollback on failure
    - Performance monitoring
    """
    try:
        # Validate user permissions
        if current_user.role not in ["admin", "policy_manager"]:
            raise HTTPException(
                status_code=403, detail="Insufficient permissions for policy deployment"
            )

        # Convert request policies to IntegrityPolicyRule objects
        policies = []
        for policy_data in request.policies:
            policy = IntegrityPolicyRule(
                rule_content=policy_data.get("rule_content", ""),
                # Add other required fields based on IntegrityPolicyRule structure
            )
            policies.append(policy)

        # Execute deployment
        result = await compiler.deploy_policy_update(
            policies=policies,
            amendment_id=request.amendment_id,
            force_hot_swap=request.force_hot_swap,
        )

        # Log deployment activity
        logger.info(
            f"Policy deployment initiated by user {current_user.id}: "
            f"{len(policies)} policies, amendment_id={request.amendment_id}"
        )

        return DeploymentStatusResponse(**result)

    except Exception as e:
        logger.error(f"Policy deployment failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rollback", response_model=RollbackStatusResponse)
async def rollback_policy(
    request: PolicyRollbackRequest,
    current_user: User = Depends(get_current_user),
    compiler: IncrementalCompiler = Depends(get_incremental_compiler),
) -> RollbackStatusResponse:
    """
    Rollback policy to a previous version.

    Supports:
    - Automatic version detection
    - Rollback validation
    - Audit trail maintenance
    """
    try:
        # Validate user permissions
        if current_user.role not in ["admin", "policy_manager"]:
            raise HTTPException(
                status_code=403, detail="Insufficient permissions for policy rollback"
            )

        # Execute rollback
        result = await compiler.rollback_policy(
            policy_id=request.policy_id,
            target_version=request.target_version,
            rollback_reason=request.rollback_reason,
        )

        # Log rollback activity
        logger.info(
            f"Policy rollback initiated by user {current_user.id}: "
            f"policy_id={request.policy_id}, target_version={request.target_version}"
        )

        return RollbackStatusResponse(**result)

    except Exception as e:
        logger.error(f"Policy rollback failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics", response_model=CompilationMetricsResponse)
async def get_compilation_metrics(
    current_user: User = Depends(get_current_user),
    compiler: IncrementalCompiler = Depends(get_incremental_compiler),
) -> CompilationMetricsResponse:
    """
    Get compilation and deployment performance metrics.

    Provides insights into:
    - Compilation performance
    - Deployment success rates
    - Rollback frequency
    - System health indicators
    """
    try:
        # Validate user permissions
        if current_user.role not in ["admin", "policy_manager", "auditor"]:
            raise HTTPException(
                status_code=403, detail="Insufficient permissions to view metrics"
            )

        metrics = compiler.get_metrics()

        return CompilationMetricsResponse(**metrics)

    except Exception as e:
        logger.error(f"Failed to retrieve compilation metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_deployment_status(
    current_user: User = Depends(get_current_user),
    compiler: IncrementalCompiler = Depends(get_incremental_compiler),
) -> dict[str, Any]:
    """
    Get current deployment status and active operations.
    """
    try:
        # Validate user permissions
        if current_user.role not in ["admin", "policy_manager", "auditor"]:
            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions to view deployment status",
            )

        return {
            "active_deployments": len(compiler.active_deployments),
            "max_concurrent_deployments": compiler.max_concurrent_deployments,
            "target_compilation_time_ms": compiler.target_compilation_time_ms,
            "deployment_capacity_available": (
                compiler.max_concurrent_deployments - len(compiler.active_deployments)
            ),
            "version_tracking_enabled": True,
            "rollback_points_available": sum(
                len(points) for points in compiler.rollback_points.values()
            ),
        }

    except Exception as e:
        logger.error(f"Failed to retrieve deployment status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for incremental compilation service."""
    return {
        "status": "healthy",
        "service": "incremental_compilation",
        "version": "1.0.0",
    }
