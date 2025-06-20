"""
ACGS-1 Phase A3: Governance Workflow API Endpoints

This module provides comprehensive API endpoints for the governance workflow
orchestration system, supporting all 5 core governance workflows with
enterprise-grade capabilities and performance monitoring.

API Endpoints:
- POST /workflows - Create new governance workflow
- GET /workflows - List workflows with filtering
- GET /workflows/{workflow_id} - Get workflow status
- POST /workflows/{workflow_id}/start - Start workflow execution
- POST /workflows/{workflow_id}/cancel - Cancel workflow
- GET /workflows/types - Get available workflow types
- GET /workflows/metrics - Get performance metrics
"""

import logging
import sys
from datetime import timezone, datetime
from typing import Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from pydantic import BaseModel, Field

# Import shared components
sys.path.append("/home/dislove/ACGS-1/services/shared")
try:
    from api_models import ErrorCode, create_error_response, create_success_response
    from validation_helpers import handle_validation_errors

    SHARED_COMPONENTS_AVAILABLE = True
except ImportError:
    SHARED_COMPONENTS_AVAILABLE = False

# Import workflow orchestrator
try:
    from ...workflows.phase_a3_governance_orchestrator import (
        PhaseA3GovernanceOrchestrator,
        WorkflowStatus,
        WorkflowType,
    )

    ORCHESTRATOR_AVAILABLE = True
except ImportError:
    ORCHESTRATOR_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter()


class CreateWorkflowRequest(BaseModel):
    """Request model for creating a new governance workflow."""

    workflow_type: str = Field(
        ...,
        regex=r"^(policy_creation|constitutional_compliance|policy_enforcement|wina_oversight|audit_transparency)$",
        description="Type of governance workflow",
        example="policy_creation",
    )
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Workflow name",
        example="Environmental Policy Creation",
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="Workflow description",
        example="Create new environmental protection policy for urban areas",
    )
    context: dict[str, Any] = Field(
        ...,
        description="Workflow context data",
        example={
            "policy_domain": "environmental",
            "stakeholders": [
                "environmental_team",
                "legal_team",
                "public_representatives",
            ],
            "urgency": "medium",
            "target_implementation": "2024-Q2",
        },
    )
    priority: str = Field(
        "medium",
        regex=r"^(low|medium|high|critical)$",
        description="Workflow priority",
        example="medium",
    )
    auto_start: bool = Field(
        False, description="Automatically start workflow after creation", example=False
    )


class WorkflowResponse(BaseModel):
    """Response model for workflow operations."""

    workflow_id: str = Field(..., description="Unique workflow identifier")
    workflow_type: str = Field(..., description="Type of governance workflow")
    name: str = Field(..., description="Workflow name")
    status: str = Field(..., description="Current workflow status")
    progress_percentage: float = Field(..., description="Completion percentage")
    completed_steps: int = Field(..., description="Number of completed steps")
    total_steps: int = Field(..., description="Total number of steps")
    current_step: dict[str, Any] | None = Field(None, description="Current step information")
    created_at: str = Field(..., description="Creation timestamp")
    started_at: str | None = Field(None, description="Start timestamp")
    completed_at: str | None = Field(None, description="Completion timestamp")
    total_execution_time_ms: float = Field(..., description="Total execution time in milliseconds")
    created_by: str = Field(..., description="User who created the workflow")
    priority: str = Field(..., description="Workflow priority")


class WorkflowListResponse(BaseModel):
    """Response model for workflow list operations."""

    workflows: list[WorkflowResponse] = Field(..., description="List of workflows")
    total_count: int = Field(..., description="Total number of workflows")
    filtered_count: int = Field(..., description="Number of workflows after filtering")
    filters_applied: dict[str, Any] = Field(..., description="Applied filters")


class WorkflowMetricsResponse(BaseModel):
    """Response model for workflow performance metrics."""

    workflow_metrics: dict[str, Any] = Field(
        ..., description="Performance metrics by workflow type"
    )
    active_workflows: int = Field(..., description="Number of active workflows")
    service_endpoints: int = Field(..., description="Number of configured service endpoints")
    workflow_templates: int = Field(..., description="Number of workflow templates")
    timestamp: str = Field(..., description="Metrics timestamp")


# Global orchestrator instance
orchestrator = None

if ORCHESTRATOR_AVAILABLE:
    orchestrator = PhaseA3GovernanceOrchestrator()


@router.post("/workflows", response_model=WorkflowResponse)
@handle_validation_errors("gs_service")
async def create_workflow(
    request: CreateWorkflowRequest,
    background_tasks: BackgroundTasks,
    http_request: Request,
):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Create a new governance workflow.

    This endpoint creates a new instance of one of the 5 core governance workflows:
    - policy_creation: Draft → Review → Voting → Implementation
    - constitutional_compliance: Validation → Assessment → Enforcement
    - policy_enforcement: Monitoring → Violation Detection → Remediation
    - wina_oversight: Performance Monitoring → Optimization → Reporting
    - audit_transparency: Data Collection → Analysis → Public Reporting
    """
    correlation_id = getattr(http_request.state, "correlation_id", None)

    try:
        if not orchestrator:
            if SHARED_COMPONENTS_AVAILABLE:
                return create_error_response(
                    error_code=ErrorCode.SERVICE_UNAVAILABLE,
                    message="Workflow orchestrator not available",
                    service_name="gs_service",
                    correlation_id=correlation_id,
                )
            else:
                raise HTTPException(status_code=503, detail="Workflow orchestrator not available")

        # Convert string workflow type to enum
        try:
            workflow_type = WorkflowType(request.workflow_type)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid workflow type: {request.workflow_type}",
            )

        # Create workflow
        workflow_id = await orchestrator.create_workflow(
            workflow_type=workflow_type,
            name=request.name,
            description=request.description,
            context=request.context,
            created_by="api_user",  # Would get from authentication in production
            priority=request.priority,
        )

        # Auto-start if requested
        if request.auto_start:
            await orchestrator.start_workflow(workflow_id)

        # Get workflow status
        workflow_status = await orchestrator.get_workflow_status(workflow_id)

        if not workflow_status:
            raise HTTPException(
                status_code=500, detail="Failed to retrieve created workflow status"
            )

        # Add background monitoring task
        background_tasks.add_task(
            _log_workflow_creation, workflow_id, request.workflow_type, correlation_id
        )

        response_data = WorkflowResponse(**workflow_status)

        if SHARED_COMPONENTS_AVAILABLE:
            return create_success_response(
                data=response_data.dict(),
                service_name="gs_service",
                correlation_id=correlation_id,
            )
        else:
            return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow creation failed: {e}", extra={"correlation_id": correlation_id})

        if SHARED_COMPONENTS_AVAILABLE:
            return create_error_response(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Workflow creation failed",
                service_name="gs_service",
                details={"error": str(e)},
                correlation_id=correlation_id,
            )
        else:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows", response_model=WorkflowListResponse)
async def list_workflows(
    http_request: Request,
    status: str | None = Query(
        None, regex=r"^(pending|running|paused|completed|failed|cancelled)$"
    ),
    workflow_type: str | None = Query(
        None,
        regex=r"^(policy_creation|constitutional_compliance|policy_enforcement|wina_oversight|audit_transparency)$",
    ),
    limit: int = Query(100, ge=1, le=1000),
    created_by: str | None = Query(None),
):
    """
    List governance workflows with optional filtering.

    Supports filtering by:
    - status: Workflow execution status
    - workflow_type: Type of governance workflow
    - created_by: User who created the workflow
    - limit: Maximum number of results
    """
    correlation_id = getattr(http_request.state, "correlation_id", None)

    try:
        if not orchestrator:
            if SHARED_COMPONENTS_AVAILABLE:
                return create_error_response(
                    error_code=ErrorCode.SERVICE_UNAVAILABLE,
                    message="Workflow orchestrator not available",
                    service_name="gs_service",
                    correlation_id=correlation_id,
                )
            else:
                raise HTTPException(status_code=503, detail="Workflow orchestrator not available")

        # Convert string filters to enums
        status_filter = None
        if status:
            try:
                status_filter = WorkflowStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid status filter: {status}")

        workflow_type_filter = None
        if workflow_type:
            try:
                workflow_type_filter = WorkflowType(workflow_type)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid workflow type filter: {workflow_type}",
                )

        # Get workflows
        workflows = await orchestrator.list_workflows(
            status_filter=status_filter,
            workflow_type_filter=workflow_type_filter,
            limit=limit,
        )

        # Apply additional filters
        if created_by:
            workflows = [w for w in workflows if w.get("created_by") == created_by]

        # Prepare response
        workflow_responses = [WorkflowResponse(**w) for w in workflows]

        response_data = WorkflowListResponse(
            workflows=workflow_responses,
            total_count=len(orchestrator.active_workflows),
            filtered_count=len(workflow_responses),
            filters_applied={
                "status": status,
                "workflow_type": workflow_type,
                "created_by": created_by,
                "limit": limit,
            },
        )

        if SHARED_COMPONENTS_AVAILABLE:
            return create_success_response(
                data=response_data.dict(),
                service_name="gs_service",
                correlation_id=correlation_id,
            )
        else:
            return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Workflow listing failed: {e}", extra={"correlation_id": correlation_id})

        if SHARED_COMPONENTS_AVAILABLE:
            return create_error_response(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Workflow listing failed",
                service_name="gs_service",
                details={"error": str(e)},
                correlation_id=correlation_id,
            )
        else:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_status(workflow_id: str, http_request: Request):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Get detailed status of a specific governance workflow."""
    correlation_id = getattr(http_request.state, "correlation_id", None)

    try:
        if not orchestrator:
            if SHARED_COMPONENTS_AVAILABLE:
                return create_error_response(
                    error_code=ErrorCode.SERVICE_UNAVAILABLE,
                    message="Workflow orchestrator not available",
                    service_name="gs_service",
                    correlation_id=correlation_id,
                )
            else:
                raise HTTPException(status_code=503, detail="Workflow orchestrator not available")

        workflow_status = await orchestrator.get_workflow_status(workflow_id)

        if not workflow_status:
            raise HTTPException(status_code=404, detail=f"Workflow {workflow_id} not found")

        response_data = WorkflowResponse(**workflow_status)

        if SHARED_COMPONENTS_AVAILABLE:
            return create_success_response(
                data=response_data.dict(),
                service_name="gs_service",
                correlation_id=correlation_id,
            )
        else:
            return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get workflow status failed: {e}", extra={"correlation_id": correlation_id})

        if SHARED_COMPONENTS_AVAILABLE:
            return create_error_response(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Get workflow status failed",
                service_name="gs_service",
                details={"error": str(e)},
                correlation_id=correlation_id,
            )
        else:
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/start")
async def start_workflow(workflow_id: str, http_request: Request):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Start execution of a pending governance workflow."""
    correlation_id = getattr(http_request.state, "correlation_id", None)

    try:
        if not orchestrator:
            if SHARED_COMPONENTS_AVAILABLE:
                return create_error_response(
                    error_code=ErrorCode.SERVICE_UNAVAILABLE,
                    message="Workflow orchestrator not available",
                    service_name="gs_service",
                    correlation_id=correlation_id,
                )
            else:
                raise HTTPException(status_code=503, detail="Workflow orchestrator not available")

        success = await orchestrator.start_workflow(workflow_id)

        if not success:
            raise HTTPException(status_code=400, detail=f"Failed to start workflow {workflow_id}")

        response_data = {
            "workflow_id": workflow_id,
            "status": "started",
            "message": "Workflow started successfully",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if SHARED_COMPONENTS_AVAILABLE:
            return create_success_response(
                data=response_data,
                service_name="gs_service",
                correlation_id=correlation_id,
            )
        else:
            return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Start workflow failed: {e}", extra={"correlation_id": correlation_id})

        if SHARED_COMPONENTS_AVAILABLE:
            return create_error_response(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Start workflow failed",
                service_name="gs_service",
                details={"error": str(e)},
                correlation_id=correlation_id,
            )
        else:
            raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflows/{workflow_id}/cancel")
async def cancel_workflow(workflow_id: str, http_request: Request):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Cancel a running governance workflow."""
    correlation_id = getattr(http_request.state, "correlation_id", None)

    try:
        if not orchestrator:
            if SHARED_COMPONENTS_AVAILABLE:
                return create_error_response(
                    error_code=ErrorCode.SERVICE_UNAVAILABLE,
                    message="Workflow orchestrator not available",
                    service_name="gs_service",
                    correlation_id=correlation_id,
                )
            else:
                raise HTTPException(status_code=503, detail="Workflow orchestrator not available")

        success = await orchestrator.cancel_workflow(workflow_id)

        if not success:
            raise HTTPException(status_code=400, detail=f"Failed to cancel workflow {workflow_id}")

        response_data = {
            "workflow_id": workflow_id,
            "status": "cancelled",
            "message": "Workflow cancelled successfully",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        if SHARED_COMPONENTS_AVAILABLE:
            return create_success_response(
                data=response_data,
                service_name="gs_service",
                correlation_id=correlation_id,
            )
        else:
            return response_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Cancel workflow failed: {e}", extra={"correlation_id": correlation_id})

        if SHARED_COMPONENTS_AVAILABLE:
            return create_error_response(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Cancel workflow failed",
                service_name="gs_service",
                details={"error": str(e)},
                correlation_id=correlation_id,
            )
        else:
            raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/types")
async def get_workflow_types():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Get available governance workflow types and their descriptions."""
    workflow_types = {
        "policy_creation": {
            "name": "Policy Creation",
            "description": "Complete policy creation workflow from draft to implementation",
            "steps": [
                "Draft Policy",
                "Stakeholder Review",
                "Constitutional Validation",
                "Democratic Voting",
                "Policy Implementation",
            ],
            "estimated_duration": "2-8 hours",
            "services_involved": ["gs", "pgc", "ac"],
        },
        "constitutional_compliance": {
            "name": "Constitutional Compliance",
            "description": "Validate and enforce constitutional compliance",
            "steps": [
                "Compliance Assessment",
                "Violation Detection",
                "Remediation Planning",
                "Enforcement Action",
            ],
            "estimated_duration": "30 minutes - 2 hours",
            "services_involved": ["ac", "integrity", "pgc"],
        },
        "policy_enforcement": {
            "name": "Policy Enforcement",
            "description": "Monitor and enforce policy compliance",
            "steps": [
                "Monitoring Setup",
                "Violation Monitoring",
                "Incident Response",
                "Corrective Action",
            ],
            "estimated_duration": "1-4 hours",
            "services_involved": ["integrity", "pgc"],
        },
        "wina_oversight": {
            "name": "WINA Oversight",
            "description": "Monitor and optimize WINA performance",
            "steps": [
                "Performance Monitoring",
                "Optimization Analysis",
                "Recommendation Generation",
                "Implementation Coordination",
            ],
            "estimated_duration": "20-60 minutes",
            "services_involved": ["fv", "gs", "ec"],
        },
        "audit_transparency": {
            "name": "Audit & Transparency",
            "description": "Generate transparency reports and audit trails",
            "steps": [
                "Data Collection",
                "Analysis Processing",
                "Report Generation",
                "Public Disclosure",
            ],
            "estimated_duration": "30 minutes - 2 hours",
            "services_involved": ["integrity", "fv", "gs", "ec"],
        },
    }

    return {
        "workflow_types": workflow_types,
        "total_types": len(workflow_types),
        "services": {
            "gs": "Governance Synthesis (port 8004)",
            "pgc": "Policy Governance Control (port 8001)",
            "ac": "Access Control (port 8002)",
            "integrity": "Integrity Service (port 8003)",
            "fv": "Formal Verification (port 8005)",
            "ec": "External Coordination (port 8006)",
        },
    }


@router.get("/workflows/metrics", response_model=WorkflowMetricsResponse)
async def get_workflow_metrics(http_request: Request):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Get comprehensive workflow performance metrics."""
    correlation_id = getattr(http_request.state, "correlation_id", None)

    try:
        if not orchestrator:
            if SHARED_COMPONENTS_AVAILABLE:
                return create_error_response(
                    error_code=ErrorCode.SERVICE_UNAVAILABLE,
                    message="Workflow orchestrator not available",
                    service_name="gs_service",
                    correlation_id=correlation_id,
                )
            else:
                raise HTTPException(status_code=503, detail="Workflow orchestrator not available")

        metrics = await orchestrator.get_performance_metrics()

        response_data = WorkflowMetricsResponse(**metrics)

        if SHARED_COMPONENTS_AVAILABLE:
            return create_success_response(
                data=response_data.dict(),
                service_name="gs_service",
                correlation_id=correlation_id,
            )
        else:
            return response_data

    except Exception as e:
        logger.error(
            f"Get workflow metrics failed: {e}",
            extra={"correlation_id": correlation_id},
        )

        if SHARED_COMPONENTS_AVAILABLE:
            return create_error_response(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Get workflow metrics failed",
                service_name="gs_service",
                details={"error": str(e)},
                correlation_id=correlation_id,
            )
        else:
            raise HTTPException(status_code=500, detail=str(e))


async def _log_workflow_creation(
    workflow_id: str, workflow_type: str, correlation_id: str | None = None
):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Background task to log workflow creation metrics."""
    metrics = {
        "workflow_id": workflow_id,
        "workflow_type": workflow_type,
        "action": "created",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "correlation_id": correlation_id,
    }

    logger.info(f"Workflow creation metrics: {metrics}")
