"""
Multi-Agent Coordination Domain Entities
Constitutional Hash: cdd01ef066bc6cf2

Core entities for agent coordination and orchestration.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from services.shared.domain.base import (
    Entity,
    EntityId,
    MultiTenantAggregateRoot,
    TenantId,
)

from .events import (
    AgentRegisteredEvent,
    CoordinationSessionStartedEvent,
    TaskAssignedEvent,
    TaskCompletedEvent,
)
from .value_objects import (
    AgentCapability,
    AgentStatus,
    CoordinationObjective,
    TaskRequirements,
    TaskStatus,
)


class Agent(MultiTenantAggregateRoot):
    """
    Aggregate root representing an AI agent in the coordination system.

    Agents have capabilities, can be assigned tasks, and participate in
    multi-agent coordination sessions.
    """

    def __init__(
        self,
        agent_id: EntityId,
        tenant_id: TenantId,
        agent_type: str,
        capabilities: List[AgentCapability],
        status: AgentStatus,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(agent_id, tenant_id)
        self.agent_type = agent_type
        self._capabilities = capabilities.copy()
        self._status = status
        self.metadata = metadata or {}
        self._current_tasks: List[EntityId] = []
        self._performance_history: List[Dict[str, Any]] = []

    @property
    def capabilities(self) -> List[AgentCapability]:
        """Get agent capabilities."""
        return self._capabilities.copy()

    @property
    def status(self) -> AgentStatus:
        """Get current agent status."""
        return self._status

    @property
    def current_tasks(self) -> List[EntityId]:
        """Get currently assigned tasks."""
        return self._current_tasks.copy()

    @property
    def is_available(self) -> bool:
        """Check if agent is available for new tasks."""
        return (
            self._status == AgentStatus.AVAILABLE
            and len(self._current_tasks) < self._get_max_concurrent_tasks()
        )

    def register_capability(self, capability: AgentCapability) -> None:
        """Add new capability to agent."""
        if capability not in self._capabilities:
            self._capabilities.append(capability)
            self._add_domain_event(
                AgentRegisteredEvent(
                    aggregate_id=self.id,
                    agent_id=self.id,
                    agent_type=self.agent_type,
                    new_capability=capability.to_dict(),
                    occurred_at=datetime.utcnow(),
                )
            )

    def assign_task(
        self, task_id: EntityId, task_requirements: TaskRequirements
    ) -> None:
        """Assign task to agent."""
        if not self.is_available:
            raise ValueError(f"Agent {self.id} is not available for new tasks")

        if not self._can_handle_task(task_requirements):
            raise ValueError(f"Agent {self.id} cannot handle task requirements")

        self._current_tasks.append(task_id)
        self._status = AgentStatus.BUSY

        self._add_domain_event(
            TaskAssignedEvent(
                aggregate_id=self.id,
                agent_id=self.id,
                task_id=task_id,
                task_requirements=task_requirements.to_dict(),
                occurred_at=datetime.utcnow(),
            )
        )

    def complete_task(
        self, task_id: EntityId, result: Dict[str, Any], performance_score: float
    ) -> None:
        """Mark task as completed and record performance."""
        if task_id not in self._current_tasks:
            raise ValueError(f"Task {task_id} not assigned to agent {self.id}")

        self._current_tasks.remove(task_id)

        # Record performance
        performance_record = {
            "task_id": str(task_id),
            "completed_at": datetime.utcnow().isoformat(),
            "performance_score": performance_score,
            "result_quality": result.get("quality_score", 0.0),
        }
        self._performance_history.append(performance_record)

        # Update status
        if not self._current_tasks:
            self._status = AgentStatus.AVAILABLE

        self._add_domain_event(
            TaskCompletedEvent(
                aggregate_id=self.id,
                agent_id=self.id,
                task_id=task_id,
                result=result,
                performance_score=performance_score,
                occurred_at=datetime.utcnow(),
            )
        )

    def set_status(self, status: AgentStatus) -> None:
        """Update agent status."""
        old_status = self._status
        self._status = status

        # Clear tasks if going offline
        if status == AgentStatus.OFFLINE:
            self._current_tasks.clear()

    def get_performance_metrics(self) -> Dict[str, float]:
        """Calculate performance metrics from history."""
        if not self._performance_history:
            return {"average_performance": 0.0, "task_count": 0, "success_rate": 0.0}

        total_performance = sum(
            record["performance_score"] for record in self._performance_history
        )
        task_count = len(self._performance_history)

        return {
            "average_performance": total_performance / task_count,
            "task_count": task_count,
            "success_rate": sum(
                1
                for record in self._performance_history
                if record["performance_score"] >= 0.7
            )
            / task_count,
        }

    def _can_handle_task(self, requirements: TaskRequirements) -> bool:
        """Check if agent can handle task requirements."""
        required_capabilities = set(requirements.required_capabilities)
        agent_capabilities = set(cap.capability_type for cap in self._capabilities)
        return required_capabilities.issubset(agent_capabilities)

    def _get_max_concurrent_tasks(self) -> int:
        """Get maximum concurrent tasks based on agent type."""
        max_tasks_by_type = {"ethics": 2, "legal": 3, "operational": 5, "specialist": 1}
        return max_tasks_by_type.get(self.agent_type, 2)


class CoordinationSession(MultiTenantAggregateRoot):
    """
    Aggregate root representing a multi-agent coordination session.

    Manages the coordination of multiple agents working towards a common objective.
    """

    def __init__(
        self,
        session_id: EntityId,
        tenant_id: TenantId,
        objective: CoordinationObjective,
        initiator_id: str,
        required_agents: List[str],
    ):
        super().__init__(session_id, tenant_id)
        self.objective = objective
        self.initiator_id = initiator_id
        self.required_agents = required_agents.copy()
        self._participating_agents: List[EntityId] = []
        self._tasks: List["CoordinationTask"] = []
        self._status = "pending"
        self._results: Dict[str, Any] = {}
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    @property
    def participating_agents(self) -> List[EntityId]:
        """Get participating agents."""
        return self._participating_agents.copy()

    @property
    def tasks(self) -> List["CoordinationTask"]:
        """Get coordination tasks."""
        return self._tasks.copy()

    @property
    def status(self) -> str:
        """Get session status."""
        return self._status

    @property
    def results(self) -> Dict[str, Any]:
        """Get session results."""
        return self._results.copy()

    def start_session(self, participating_agents: List[EntityId]) -> None:
        """Start the coordination session."""
        if self._status != "pending":
            raise ValueError(f"Session {self.id} already started")

        self._participating_agents = participating_agents.copy()
        self._status = "active"
        self.started_at = datetime.utcnow()

        self._add_domain_event(
            CoordinationSessionStartedEvent(
                aggregate_id=self.id,
                session_id=self.id,
                objective=self.objective.to_dict(),
                participating_agents=[
                    str(agent_id) for agent_id in participating_agents
                ],
                occurred_at=datetime.utcnow(),
            )
        )

    def add_task(self, task: "CoordinationTask") -> None:
        """Add task to coordination session."""
        if self._status not in ["active", "pending"]:
            raise ValueError(f"Cannot add tasks to {self._status} session")

        self._tasks.append(task)

    def complete_session(self, final_results: Dict[str, Any]) -> None:
        """Complete the coordination session."""
        if self._status != "active":
            raise ValueError(f"Session {self.id} is not active")

        self._status = "completed"
        self._results = final_results.copy()
        self.completed_at = datetime.utcnow()

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of coordination session."""
        return {
            "session_id": str(self.id),
            "objective": self.objective.to_dict(),
            "status": self._status,
            "agent_count": len(self._participating_agents),
            "task_count": len(self._tasks),
            "duration_minutes": self._calculate_duration_minutes(),
            "results": self._results,
        }

    def _calculate_duration_minutes(self) -> Optional[float]:
        """Calculate session duration in minutes."""
        if not self.started_at:
            return None

        end_time = self.completed_at or datetime.utcnow()
        duration = end_time - self.started_at
        return duration.total_seconds() / 60


class CoordinationTask(Entity):
    """
    Entity representing a task within a coordination session.

    Tasks are assigned to specific agents and contribute to the overall objective.
    """

    def __init__(
        self,
        task_id: EntityId,
        session_id: EntityId,
        assigned_agent_id: EntityId,
        task_type: str,
        requirements: TaskRequirements,
        dependencies: List[EntityId] = None,
    ):
        super().__init__(task_id)
        self.session_id = session_id
        self.assigned_agent_id = assigned_agent_id
        self.task_type = task_type
        self.requirements = requirements
        self.dependencies = dependencies or []
        self._status = TaskStatus.PENDING
        self._result: Optional[Dict[str, Any]] = None
        self.assigned_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    @property
    def status(self) -> TaskStatus:
        """Get task status."""
        return self._status

    @property
    def result(self) -> Optional[Dict[str, Any]]:
        """Get task result."""
        return self._result.copy() if self._result else None

    def start_execution(self) -> None:
        """Mark task as started."""
        if self._status != TaskStatus.PENDING:
            raise ValueError(
                f"Task {self.id} cannot be started from {self._status} status"
            )

        self._status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()

    def complete_task(self, result: Dict[str, Any]) -> None:
        """Complete the task with results."""
        if self._status != TaskStatus.IN_PROGRESS:
            raise ValueError(f"Task {self.id} is not in progress")

        self._status = TaskStatus.COMPLETED
        self._result = result.copy()
        self.completed_at = datetime.utcnow()

    def fail_task(self, error: str) -> None:
        """Mark task as failed."""
        self._status = TaskStatus.FAILED
        self._result = {"error": error}
        self.completed_at = datetime.utcnow()

    def can_execute(self, completed_tasks: List[EntityId]) -> bool:
        """Check if task can be executed based on dependencies."""
        if self._status != TaskStatus.PENDING:
            return False

        # All dependencies must be completed
        return all(dep_id in completed_tasks for dep_id in self.dependencies)

    def get_task_duration(self) -> Optional[float]:
        """Get task execution duration in minutes."""
        if not self.started_at or not self.completed_at:
            return None

        duration = self.completed_at - self.started_at
        return duration.total_seconds() / 60
