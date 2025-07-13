"""
APGF (Agentic Policy Generation Feature) FastAPI endpoints.

Provides RESTful API for managing dynamic agents, policy generation workflows,
and tool execution within the ACGS constitutional AI framework.
"""

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field, validator
from starlette.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)

from services.shared.agents.apgf_orchestrator import APGFOrchestrator
from services.shared.agents.tool_router import ToolSafetyLevel
from services.shared.constitutional_safety_framework import (
    ConstitutionalSafetyFramework,
)
from services.shared.monitoring.intelligent_alerting_system import AlertingSystem
from services.shared.security.enhanced_audit_logging import AuditLogger
from services.shared.security.unified_input_validation import UnifiedInputValidator
from services.shared.service_mesh.service_orchestrator import ServiceOrchestrator

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


# Pydantic models for API requests/responses
class WorkflowRequest(BaseModel):
    """Request model for creating policy generation workflows"""

    name: str = Field(..., min_length=1, max_length=100, description="Workflow name")
    description: str | None = Field(
        None, max_length=500, description="Workflow description"
    )
    requirements: dict[str, Any] = Field(
        ..., description="Policy requirements and constraints"
    )
    coordination_strategy: str = Field(
        default="sequential", description="Agent coordination strategy"
    )
    priority: str = Field(default="medium", description="Workflow priority level")

    @validator("coordination_strategy")
    def validate_coordination_strategy(self, v):
        valid_strategies = [
            "sequential",
            "parallel",
            "hierarchical",
            "consensus",
            "competitive",
        ]
        if v not in valid_strategies:
            raise ValueError(
                f"Invalid coordination strategy. Must be one of: {valid_strategies}"
            )
        return v

    @validator("priority")
    def validate_priority(self, v):
        valid_priorities = ["low", "medium", "high", "critical"]
        if v not in valid_priorities:
            raise ValueError(f"Invalid priority. Must be one of: {valid_priorities}")
        return v


class AgentRequest(BaseModel):
    """Request model for creating dynamic agents"""

    name: str = Field(..., min_length=1, max_length=100, description="Agent name")
    role: str = Field(..., min_length=1, max_length=50, description="Agent role")
    capabilities: list[str] = Field(
        ..., min_items=1, description="List of agent capabilities"
    )
    domain: str | None = Field(None, max_length=50, description="Domain specialization")
    priority: str = Field(default="medium", description="Agent priority level")
    reporting_level: str = Field(
        default="standard", description="Reporting detail level"
    )
    escalation_threshold: float = Field(
        default=0.8, ge=0.0, le=1.0, description="Escalation threshold"
    )


class ToolExecutionRequest(BaseModel):
    """Request model for tool execution"""

    agent_id: str = Field(..., description="ID of the agent executing the tool")
    tool_id: str = Field(..., description="ID of the tool to execute")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Tool parameters"
    )
    priority: int = Field(
        default=5, ge=1, le=10, description="Execution priority (1-10)"
    )
    timeout_seconds: int | None = Field(
        None, ge=1, le=3600, description="Execution timeout"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


class WorkflowResponse(BaseModel):
    """Response model for workflow operations"""

    workflow_id: str
    name: str
    state: str
    current_step: int
    total_steps: int
    progress_percentage: float
    assigned_agents: int
    generated_policies: int
    start_time: str
    estimated_completion: str | None
    actual_completion: str | None
    success_metrics: dict[str, Any]
    errors: int
    constitutional_hash: str = CONSTITUTIONAL_HASH


class AgentResponse(BaseModel):
    """Response model for agent operations"""

    agent_id: str
    name: str
    role: str
    state: str
    capabilities: list[str]
    uptime_seconds: float
    tasks_in_queue: int
    active_tasks: int
    completed_tasks: int
    failed_tasks: int
    error_rate: float
    constitutional_compliance_score: float
    resource_efficiency_score: float
    last_activity: str
    compliance_violations: int
    constitutional_hash: str = CONSTITUTIONAL_HASH


class ToolExecutionResponse(BaseModel):
    """Response model for tool execution"""

    request_id: str
    tool_id: str
    agent_id: str
    status: str
    result: dict[str, Any] | None
    error_message: str | None
    execution_time_seconds: float
    resource_usage: dict[str, Any]
    started_at: str
    completed_at: str | None
    audit_trail: list[dict[str, Any]]
    constitutional_hash: str = CONSTITUTIONAL_HASH


# Global APGF orchestrator instance
_apgf_orchestrator: APGFOrchestrator | None = None


async def get_apgf_orchestrator() -> APGFOrchestrator:
    """Dependency to get APGF orchestrator instance"""
    global _apgf_orchestrator

    if _apgf_orchestrator is None:
        # Initialize APGF components
        constitutional_framework = ConstitutionalSafetyFramework()
        audit_logger = AuditLogger()
        alerting_system = AlertingSystem()
        input_validator = UnifiedInputValidator()
        service_orchestrator = ServiceOrchestrator()

        _apgf_orchestrator = APGFOrchestrator(
            constitutional_framework=constitutional_framework,
            audit_logger=audit_logger,
            alerting_system=alerting_system,
            input_validator=input_validator,
            service_orchestrator=service_orchestrator,
        )

        await _apgf_orchestrator.initialize()
        logger.info("APGF orchestrator initialized successfully")

    return _apgf_orchestrator


# Create API router
router = APIRouter(prefix="/api/v1/apgf", tags=["APGF"])


@router.post("/workflows", response_model=WorkflowResponse)
async def create_workflow(
    request: WorkflowRequest,
    background_tasks: BackgroundTasks,
    orchestrator: APGFOrchestrator = Depends(get_apgf_orchestrator),
) -> WorkflowResponse:
    """
    Create a new policy generation workflow.

    This endpoint creates a dynamic agent-based workflow for generating
    constitutional AI policies with specified requirements and constraints.
    """
    try:
        # Convert request to orchestrator format
        workflow_request = {
            "name": request.name,
            "description": request.description,
            "requirements": request.requirements,
            "coordination_strategy": request.coordination_strategy,
            "priority": request.priority,
        }

        # Initiate workflow
        workflow_id = await orchestrator.initiate_policy_generation_workflow(
            workflow_request
        )

        # Get workflow status for response
        workflow_status = await orchestrator.get_workflow_status(workflow_id)

        return WorkflowResponse(**workflow_status)

    except ValueError as e:
        logger.exception(f"Invalid workflow request: {e!s}")
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Failed to create workflow: {e!s}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )


@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_status(
    workflow_id: str, orchestrator: APGFOrchestrator = Depends(get_apgf_orchestrator)
) -> WorkflowResponse:
    """
    Get the status of a policy generation workflow.

    Returns detailed information about workflow progress, assigned agents,
    generated policies, and constitutional compliance metrics.
    """
    try:
        workflow_status = await orchestrator.get_workflow_status(workflow_id)
        return WorkflowResponse(**workflow_status)

    except ValueError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Workflow not found")
    except Exception as e:
        logger.exception(f"Failed to get workflow status: {e!s}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )


@router.delete("/workflows/{workflow_id}")
async def cancel_workflow(
    workflow_id: str, orchestrator: APGFOrchestrator = Depends(get_apgf_orchestrator)
) -> dict[str, Any]:
    """
    Cancel an active policy generation workflow.

    Cancels the workflow and all associated agent tasks while maintaining
    audit trails and constitutional compliance records.
    """
    try:
        await orchestrator.cancel_workflow(workflow_id)

        return {
            "workflow_id": workflow_id,
            "status": "cancelled",
            "message": "Workflow cancelled successfully",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except ValueError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Workflow not found")
    except Exception as e:
        logger.exception(f"Failed to cancel workflow: {e!s}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )


@router.post("/agents", response_model=AgentResponse)
async def create_agent(
    request: AgentRequest,
    orchestrator: APGFOrchestrator = Depends(get_apgf_orchestrator),
) -> AgentResponse:
    """
    Create a new dynamic agent for policy generation.

    Creates an autonomous AI agent with specified capabilities and
    constitutional constraints for safe policy generation tasks.
    """
    try:
        # Convert request to orchestrator format
        agent_spec = {
            "name": request.name,
            "role": request.role,
            "capabilities": request.capabilities,
            "domain": request.domain,
            "priority": request.priority,
            "reporting_level": request.reporting_level,
            "escalation_threshold": request.escalation_threshold,
        }

        # Create agent
        agent_id = await orchestrator.create_dynamic_agent(agent_spec)

        # Get agent status for response
        agent_status = await orchestrator.get_agent_status(agent_id)

        return AgentResponse(**agent_status)

    except ValueError as e:
        logger.exception(f"Invalid agent request: {e!s}")
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Failed to create agent: {e!s}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent_status(
    agent_id: str, orchestrator: APGFOrchestrator = Depends(get_apgf_orchestrator)
) -> AgentResponse:
    """
    Get the status of a dynamic agent.

    Returns detailed information about agent state, performance metrics,
    task execution status, and constitutional compliance scores.
    """
    try:
        agent_status = await orchestrator.get_agent_status(agent_id)
        return AgentResponse(**agent_status)

    except ValueError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Agent not found")
    except Exception as e:
        logger.exception(f"Failed to get agent status: {e!s}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )


@router.delete("/agents/{agent_id}")
async def shutdown_agent(
    agent_id: str, orchestrator: APGFOrchestrator = Depends(get_apgf_orchestrator)
) -> dict[str, Any]:
    """
    Shutdown a dynamic agent.

    Gracefully shuts down the agent, completing active tasks and
    maintaining full audit trails for constitutional compliance.
    """
    try:
        await orchestrator.shutdown_agent(agent_id)

        return {
            "agent_id": agent_id,
            "status": "shutdown",
            "message": "Agent shutdown successfully",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except ValueError:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Agent not found")
    except Exception as e:
        logger.exception(f"Failed to shutdown agent: {e!s}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )


@router.post("/tools/execute", response_model=ToolExecutionResponse)
async def execute_tool(
    request: ToolExecutionRequest,
    orchestrator: APGFOrchestrator = Depends(get_apgf_orchestrator),
) -> ToolExecutionResponse:
    """
    Execute a tool via a dynamic agent.

    Safely executes external tools through the agent's ToolRouter with
    comprehensive security controls and constitutional compliance validation.
    """
    try:
        # Get the agent to execute the tool
        if request.agent_id not in orchestrator.active_agents:
            raise ValueError(f"Agent {request.agent_id} not found or not active")

        agent = orchestrator.active_agents[request.agent_id]

        # Create tool execution request
        import uuid

        from services.shared.agents.tool_router import (
            ToolExecutionRequest as InternalToolRequest,
        )

        tool_request = InternalToolRequest(
            request_id=str(uuid.uuid4()),
            agent_id=request.agent_id,
            tool_id=request.tool_id,
            parameters=request.parameters,
            priority=request.priority,
            timeout_seconds=request.timeout_seconds,
            callback_url=None,
            metadata=request.metadata,
            requested_at=datetime.utcnow(),
        )

        # Execute tool via agent's tool router
        result = await agent.tool_router.route_tool_request(tool_request)

        # Convert result to response format
        response_data = {
            "request_id": result.request_id,
            "tool_id": result.tool_id,
            "agent_id": result.agent_id,
            "status": result.status.value,
            "result": result.result,
            "error_message": result.error_message,
            "execution_time_seconds": result.execution_time_seconds,
            "resource_usage": result.resource_usage,
            "started_at": result.started_at.isoformat(),
            "completed_at": (
                result.completed_at.isoformat() if result.completed_at else None
            ),
            "audit_trail": result.audit_trail,
        }

        return ToolExecutionResponse(**response_data)

    except ValueError as e:
        logger.exception(f"Invalid tool execution request: {e!s}")
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Failed to execute tool: {e!s}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )


@router.get("/tools/available")
async def get_available_tools(
    agent_id: str | None = None,
    safety_level: str | None = None,
    orchestrator: APGFOrchestrator = Depends(get_apgf_orchestrator),
) -> dict[str, Any]:
    """
    Get list of available tools for agents.

    Returns tools that can be safely executed by agents, filtered by
    agent permissions and safety level requirements.
    """
    try:
        # Convert safety level string to enum if provided
        safety_level_enum = None
        if safety_level:
            safety_level_enum = ToolSafetyLevel(safety_level.lower())

        # Get available tools from tool router
        tools = orchestrator.tool_router.get_available_tools(
            agent_id, safety_level_enum
        )

        # Convert to response format
        tools_data = [
            {
                "tool_id": tool.tool_id,
                "name": tool.name,
                "description": tool.description,
                "safety_level": tool.safety_level.value,
                "required_permissions": [
                    perm.value for perm in tool.required_permissions
                ],
                "rate_limit_per_hour": tool.rate_limit_per_hour,
                "max_execution_time_seconds": tool.max_execution_time_seconds,
                "tags": tool.tags,
                "version": tool.version,
            }
            for tool in tools
        ]

        return {
            "tools": tools_data,
            "total_count": len(tools_data),
            "agent_id": agent_id,
            "safety_level_filter": safety_level,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except ValueError as e:
        logger.exception(f"Invalid tools request: {e!s}")
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        logger.exception(f"Failed to get available tools: {e!s}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )


@router.get("/status")
async def get_apgf_status(
    orchestrator: APGFOrchestrator = Depends(get_apgf_orchestrator),
) -> dict[str, Any]:
    """
    Get overall APGF system status.

    Returns system-wide metrics including active workflows, agents,
    performance indicators, and constitutional compliance status.
    """
    try:
        return {
            "service": "APGF",
            "status": "operational",
            "active_workflows": len(orchestrator.active_workflows),
            "completed_workflows": len(orchestrator.completed_workflows),
            "active_agents": len(orchestrator.active_agents),
            "performance_metrics": orchestrator.performance_metrics,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.exception(f"Failed to get APGF status: {e!s}")
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error"
        )


# Health check endpoint for APGF
@router.get("/health")
async def apgf_health_check() -> dict[str, Any]:
    """APGF health check endpoint"""
    return {
        "service": "APGF",
        "status": "healthy",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
