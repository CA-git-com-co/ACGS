"""
Multi-Agent Coordination API Controllers
Constitutional Hash: cdd01ef066bc6cf2

FastAPI controllers for multi-agent coordination bounded context.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import ValidationError

from services.shared.domain.base import EntityId, TenantId
from services.shared.infrastructure.unit_of_work import get_unit_of_work_manager
from services.shared.middleware.tenant_middleware import get_tenant_context

from ..application.command_handlers import MultiAgentCoordinationService
from ..application.commands import (
    AssignTaskCommand,
    CompleteCoordinationSessionCommand,
    CompleteTaskCommand,
    RegisterAgentCommand,
    RequestImpactAnalysisCommand,
    StartCoordinationSessionCommand,
    UpdateAgentStatusCommand,
)
from ..domain.value_objects import (
    AgentCapability,
    AgentStatus,
    CoordinationObjective,
    TaskRequirements,
)
from .schemas import (
    AgentRegistrationRequest,
    AgentResponse,
    AgentStatusUpdateRequest,
    AnalysisResponse,
    CoordinationSessionRequest,
    ImpactAnalysisRequest,
    SessionCompletionRequest,
    SessionResponse,
    TaskAssignmentRequest,
    TaskCompletionRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/coordination", tags=["Multi-Agent Coordination"])


def get_coordination_service() -> MultiAgentCoordinationService:
    """Get multi-agent coordination service instance."""
    uow_manager = get_unit_of_work_manager()
    return MultiAgentCoordinationService(uow_manager)


@router.post(
    "/agents", response_model=AgentResponse, status_code=status.HTTP_201_CREATED
)
async def register_agent(
    request: AgentRegistrationRequest,
    tenant_context=Depends(get_tenant_context),
    service: MultiAgentCoordinationService = Depends(get_coordination_service),
) -> AgentResponse:
    """Register a new agent in the coordination system."""
    try:
        # Convert request to domain objects
        capabilities = [
            AgentCapability(
                capability_type=cap.capability_type,
                proficiency_level=cap.proficiency_level,
                domain_knowledge=cap.domain_knowledge,
                resource_requirements=cap.resource_requirements,
                performance_indicators=cap.performance_indicators,
            )
            for cap in request.capabilities
        ]

        # Create command
        command = RegisterAgentCommand(
            tenant_id=tenant_context.tenant_id,
            agent_id=EntityId(),
            agent_type=request.agent_type,
            capabilities=capabilities,
            metadata=request.metadata,
        )

        # Execute command
        agent_id = await service.register_agent(command)

        logger.info(
            f"Registered agent {agent_id} for tenant {tenant_context.tenant_id}"
        )

        return AgentResponse(
            agent_id=agent_id,
            agent_type=request.agent_type,
            status="available",
            capabilities=[cap.dict() for cap in request.capabilities],
            metadata=request.metadata or {},
        )

    except ValidationError as e:
        logger.error(f"Validation error in agent registration: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {e}",
        )
    except Exception as e:
        logger.error(f"Error registering agent: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register agent",
        )


@router.put("/agents/{agent_id}/status", status_code=status.HTTP_204_NO_CONTENT)
async def update_agent_status(
    agent_id: str,
    request: AgentStatusUpdateRequest,
    tenant_context=Depends(get_tenant_context),
    service: MultiAgentCoordinationService = Depends(get_coordination_service),
) -> None:
    """Update agent status."""
    try:
        # Create command
        command = UpdateAgentStatusCommand(
            tenant_id=tenant_context.tenant_id,
            agent_id=EntityId.from_string(agent_id),
            new_status=AgentStatus(request.new_status),
            reason=request.reason,
        )

        # Execute command
        await service.update_agent_status(command)

        logger.info(f"Updated agent {agent_id} status to {request.new_status}")

    except ValueError as e:
        logger.error(f"Invalid agent ID or status: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid input: {e}"
        )
    except Exception as e:
        logger.error(f"Error updating agent status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update agent status",
        )


@router.post("/agents/{agent_id}/tasks", status_code=status.HTTP_201_CREATED)
async def assign_task(
    agent_id: str,
    request: TaskAssignmentRequest,
    tenant_context=Depends(get_tenant_context),
    service: MultiAgentCoordinationService = Depends(get_coordination_service),
) -> Dict[str, str]:
    """Assign a task to an agent."""
    try:
        # Convert request to domain objects
        task_requirements = TaskRequirements(
            required_capabilities=request.required_capabilities,
            minimum_proficiency=request.minimum_proficiency,
            estimated_duration_minutes=request.estimated_duration_minutes,
            resource_limits=request.resource_limits,
            priority_level=request.priority_level,
            complexity_score=request.complexity_score,
        )

        # Create command
        command = AssignTaskCommand(
            tenant_id=tenant_context.tenant_id,
            agent_id=EntityId.from_string(agent_id),
            task_id=EntityId(),
            task_requirements=task_requirements,
        )

        # Execute command
        await service.assign_task(command)

        logger.info(f"Assigned task to agent {agent_id}")

        return {"task_id": str(command.task_id), "agent_id": agent_id}

    except ValueError as e:
        logger.error(f"Invalid task assignment request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid input: {e}"
        )
    except Exception as e:
        logger.error(f"Error assigning task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to assign task",
        )


@router.put(
    "/agents/{agent_id}/tasks/{task_id}/complete",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def complete_task(
    agent_id: str,
    task_id: str,
    request: TaskCompletionRequest,
    tenant_context=Depends(get_tenant_context),
    service: MultiAgentCoordinationService = Depends(get_coordination_service),
) -> None:
    """Mark a task as completed."""
    try:
        # Create command
        command = CompleteTaskCommand(
            tenant_id=tenant_context.tenant_id,
            agent_id=EntityId.from_string(agent_id),
            task_id=EntityId.from_string(task_id),
            result=request.result,
            performance_score=request.performance_score,
        )

        # Execute command
        await service.complete_task(command)

        logger.info(f"Completed task {task_id} for agent {agent_id}")

    except ValueError as e:
        logger.error(f"Invalid task completion request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid input: {e}"
        )
    except Exception as e:
        logger.error(f"Error completing task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete task",
        )


@router.post(
    "/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED
)
async def start_coordination_session(
    request: CoordinationSessionRequest,
    tenant_context=Depends(get_tenant_context),
    service: MultiAgentCoordinationService = Depends(get_coordination_service),
) -> SessionResponse:
    """Start a new coordination session."""
    try:
        # Convert request to domain objects
        objective = CoordinationObjective(
            objective_type=request.objective.objective_type,
            description=request.objective.description,
            success_criteria=request.objective.success_criteria,
            quality_thresholds=request.objective.quality_thresholds,
            time_constraints=request.objective.time_constraints,
            stakeholder_requirements=request.objective.stakeholder_requirements,
        )

        participating_agents = [
            EntityId.from_string(agent_id) for agent_id in request.participating_agents
        ]

        # Create command
        command = StartCoordinationSessionCommand(
            tenant_id=tenant_context.tenant_id,
            session_id=EntityId(),
            objective=objective,
            initiator_id=request.initiator_id,
            required_agents=request.required_agents,
            participating_agents=participating_agents,
        )

        # Execute command
        session_id = await service.start_coordination_session(command)

        logger.info(f"Started coordination session {session_id}")

        return SessionResponse(
            session_id=session_id,
            objective=request.objective.dict(),
            status="active",
            participating_agents=request.participating_agents,
            started_at=None,  # Would be set from actual session
        )

    except ValidationError as e:
        logger.error(f"Validation error in session creation: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {e}",
        )
    except Exception as e:
        logger.error(f"Error starting coordination session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start coordination session",
        )


@router.put("/sessions/{session_id}/complete", status_code=status.HTTP_204_NO_CONTENT)
async def complete_coordination_session(
    session_id: str,
    request: SessionCompletionRequest,
    tenant_context=Depends(get_tenant_context),
    service: MultiAgentCoordinationService = Depends(get_coordination_service),
) -> None:
    """Complete a coordination session."""
    try:
        # Create command
        command = CompleteCoordinationSessionCommand(
            tenant_id=tenant_context.tenant_id,
            session_id=EntityId.from_string(session_id),
            final_results=request.final_results,
        )

        # Execute command
        await service.complete_coordination_session(command)

        logger.info(f"Completed coordination session {session_id}")

    except ValueError as e:
        logger.error(f"Invalid session completion request: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid input: {e}"
        )
    except Exception as e:
        logger.error(f"Error completing coordination session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete coordination session",
        )


@router.post(
    "/analysis/impact",
    response_model=AnalysisResponse,
    status_code=status.HTTP_201_CREATED,
)
async def request_impact_analysis(
    request: ImpactAnalysisRequest,
    tenant_context=Depends(get_tenant_context),
    service: MultiAgentCoordinationService = Depends(get_coordination_service),
) -> AnalysisResponse:
    """Request impact analysis from multi-agent system."""
    try:
        # Create command
        command = RequestImpactAnalysisCommand(
            tenant_id=tenant_context.tenant_id,
            analysis_id=EntityId(),
            subject_id=request.subject_id,
            analysis_type=request.analysis_type,
            required_agents=request.required_agents,
            context_data=request.context_data,
            deadline=request.deadline,
        )

        # Execute command
        result = await service.request_impact_analysis(command)

        logger.info(f"Completed impact analysis {command.analysis_id}")

        return AnalysisResponse(
            analysis_id=str(command.analysis_id),
            subject_id=request.subject_id,
            analysis_type=request.analysis_type,
            result=result,
            status="completed",
        )

    except ValidationError as e:
        logger.error(f"Validation error in impact analysis request: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {e}",
        )
    except Exception as e:
        logger.error(f"Error requesting impact analysis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to request impact analysis",
        )


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "multi-agent-coordination",
        "constitutional_hash": "cdd01ef066bc6cf2",
    }
