"""
Multi-Agent Coordination Application Commands
Constitutional Hash: cdd01ef066bc6cf2

Command objects for multi-agent coordination operations.
"""

from dataclasses import dataclass
from typing import Any

from services.shared.domain.base import EntityId, TenantId

from ..domain.value_objects import (
    AgentCapability,
    AgentStatus,
    CoordinationObjective,
    TaskRequirements,
)


@dataclass
class RegisterAgentCommand:
    """Command to register a new agent in the coordination system."""

    tenant_id: TenantId
    agent_id: EntityId
    agent_type: str
    capabilities: list[AgentCapability]
    metadata: dict[str, Any] | None = None


@dataclass
class UpdateAgentStatusCommand:
    """Command to update agent status."""

    tenant_id: TenantId
    agent_id: EntityId
    new_status: AgentStatus
    reason: str


@dataclass
class AddAgentCapabilityCommand:
    """Command to add capability to an existing agent."""

    tenant_id: TenantId
    agent_id: EntityId
    capability: AgentCapability


@dataclass
class AssignTaskCommand:
    """Command to assign a task to an agent."""

    tenant_id: TenantId
    agent_id: EntityId
    task_id: EntityId
    task_requirements: TaskRequirements
    session_id: EntityId | None = None


@dataclass
class CompleteTaskCommand:
    """Command to mark a task as completed."""

    tenant_id: TenantId
    agent_id: EntityId
    task_id: EntityId
    result: dict[str, Any]
    performance_score: float


@dataclass
class StartCoordinationSessionCommand:
    """Command to start a multi-agent coordination session."""

    tenant_id: TenantId
    session_id: EntityId
    objective: CoordinationObjective
    initiator_id: str
    required_agents: list[str]
    participating_agents: list[EntityId]


@dataclass
class CompleteCoordinationSessionCommand:
    """Command to complete a coordination session."""

    tenant_id: TenantId
    session_id: EntityId
    final_results: dict[str, Any]


@dataclass
class RequestAgentCollaborationCommand:
    """Command to request collaboration between agents."""

    tenant_id: TenantId
    primary_agent_id: EntityId
    collaborating_agents: list[EntityId]
    collaboration_type: str
    shared_context: dict[str, Any]
    session_id: EntityId


@dataclass
class ResolveCoordinationConflictCommand:
    """Command to resolve conflicts in coordination."""

    tenant_id: TenantId
    session_id: EntityId
    conflict_id: str
    resolution_strategy: str
    resolution_parameters: dict[str, Any]


@dataclass
class AllocateResourcesCommand:
    """Command to allocate resources to agents."""

    tenant_id: TenantId
    agent_id: EntityId
    resource_allocations: dict[str, int]  # resource_type -> amount
    allocation_duration: int  # minutes


@dataclass
class UpdatePerformanceMetricsCommand:
    """Command to update agent performance metrics."""

    tenant_id: TenantId
    agent_id: EntityId
    metrics: dict[str, float]
    measurement_period: str


@dataclass
class CreateCoordinationTaskCommand:
    """Command to create a new coordination task."""

    tenant_id: TenantId
    task_id: EntityId
    session_id: EntityId
    task_type: str
    requirements: TaskRequirements
    assigned_agent_id: EntityId
    dependencies: list[EntityId]


@dataclass
class StartTaskExecutionCommand:
    """Command to start task execution."""

    tenant_id: TenantId
    task_id: EntityId
    agent_id: EntityId


@dataclass
class FailTaskCommand:
    """Command to mark a task as failed."""

    tenant_id: TenantId
    task_id: EntityId
    agent_id: EntityId
    error_message: str
    retry_count: int


@dataclass
class RequestImpactAnalysisCommand:
    """Command to request impact analysis from multi-agent system."""

    tenant_id: TenantId
    analysis_id: EntityId
    subject_id: str  # ID of what needs analysis
    analysis_type: str
    required_agents: list[str]
    context_data: dict[str, Any]
    deadline: str | None = None


@dataclass
class OptimizeAgentAllocationCommand:
    """Command to optimize agent allocation for better performance."""

    tenant_id: TenantId
    session_id: EntityId
    optimization_criteria: dict[str, float]  # criteria -> weight
    constraints: dict[str, Any]


@dataclass
class ScaleCoordinationCapacityCommand:
    """Command to scale coordination capacity up or down."""

    tenant_id: TenantId
    target_capacity: int  # number of concurrent sessions
    scaling_strategy: str  # "horizontal", "vertical", "adaptive"
    resource_constraints: dict[str, Any]
