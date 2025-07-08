"""
Multi-Agent Coordination Domain Events
Constitutional Hash: cdd01ef066bc6cf2

Domain events for multi-agent coordination activities.
"""

from datetime import datetime
from typing import Dict, Any, List
from services.shared.domain.events import DomainEvent
from services.shared.domain.base import EntityId


class AgentRegisteredEvent(DomainEvent):
    """Event raised when an agent is registered or capability is added."""
    
    def __init__(
        self,
        aggregate_id: EntityId,
        agent_id: EntityId,
        agent_type: str,
        new_capability: Dict[str, Any],
        **kwargs
    ):
        super().__init__(aggregate_id=aggregate_id, **kwargs)
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.new_capability = new_capability
    
    def _get_event_version(self) -> str:
        return "1.0"
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            "agent_id": str(self.agent_id),
            "agent_type": self.agent_type,
            "new_capability": self.new_capability
        }


class AgentStatusChangedEvent(DomainEvent):
    """Event raised when agent status changes."""
    
    def __init__(
        self,
        aggregate_id: EntityId,
        agent_id: EntityId,
        old_status: str,
        new_status: str,
        reason: str,
        **kwargs
    ):
        super().__init__(aggregate_id=aggregate_id, **kwargs)
        self.agent_id = agent_id
        self.old_status = old_status
        self.new_status = new_status
        self.reason = reason
    
    def _get_event_version(self) -> str:
        return "1.0"
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            "agent_id": str(self.agent_id),
            "old_status": self.old_status,
            "new_status": self.new_status,
            "reason": self.reason
        }


class TaskAssignedEvent(DomainEvent):
    """Event raised when a task is assigned to an agent."""
    
    def __init__(
        self,
        aggregate_id: EntityId,
        agent_id: EntityId,
        task_id: EntityId,
        task_requirements: Dict[str, Any],
        **kwargs
    ):
        super().__init__(aggregate_id=aggregate_id, **kwargs)
        self.agent_id = agent_id
        self.task_id = task_id
        self.task_requirements = task_requirements
    
    def _get_event_version(self) -> str:
        return "1.0"
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            "agent_id": str(self.agent_id),
            "task_id": str(self.task_id),
            "task_requirements": self.task_requirements
        }


class TaskStartedEvent(DomainEvent):
    """Event raised when a task execution starts."""
    
    def __init__(
        self,
        aggregate_id: EntityId,
        task_id: EntityId,
        agent_id: EntityId,
        session_id: EntityId,
        estimated_duration: int,
        **kwargs
    ):
        super().__init__(aggregate_id=aggregate_id, **kwargs)
        self.task_id = task_id
        self.agent_id = agent_id
        self.session_id = session_id
        self.estimated_duration = estimated_duration
    
    def _get_event_version(self) -> str:
        return "1.0"
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            "task_id": str(self.task_id),
            "agent_id": str(self.agent_id),
            "session_id": str(self.session_id),
            "estimated_duration": self.estimated_duration
        }


class TaskCompletedEvent(DomainEvent):
    """Event raised when a task is completed."""
    
    def __init__(
        self,
        aggregate_id: EntityId,
        agent_id: EntityId,
        task_id: EntityId,
        result: Dict[str, Any],
        performance_score: float,
        **kwargs
    ):
        super().__init__(aggregate_id=aggregate_id, **kwargs)
        self.agent_id = agent_id
        self.task_id = task_id
        self.result = result
        self.performance_score = performance_score
    
    def _get_event_version(self) -> str:
        return "1.0"
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            "agent_id": str(self.agent_id),
            "task_id": str(self.task_id),
            "result": self.result,
            "performance_score": self.performance_score
        }


class TaskFailedEvent(DomainEvent):
    """Event raised when a task fails."""
    
    def __init__(
        self,
        aggregate_id: EntityId,
        task_id: EntityId,
        agent_id: EntityId,
        error_message: str,
        retry_count: int,
        **kwargs
    ):
        super().__init__(aggregate_id=aggregate_id, **kwargs)
        self.task_id = task_id
        self.agent_id = agent_id
        self.error_message = error_message
        self.retry_count = retry_count
    
    def _get_event_version(self) -> str:
        return "1.0"
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            "task_id": str(self.task_id),
            "agent_id": str(self.agent_id),
            "error_message": self.error_message,
            "retry_count": self.retry_count
        }


class CoordinationSessionStartedEvent(DomainEvent):
    """Event raised when a coordination session starts."""
    
    def __init__(
        self,
        aggregate_id: EntityId,
        session_id: EntityId,
        objective: Dict[str, Any],
        participating_agents: List[str],
        **kwargs
    ):
        super().__init__(aggregate_id=aggregate_id, **kwargs)
        self.session_id = session_id
        self.objective = objective
        self.participating_agents = participating_agents
    
    def _get_event_version(self) -> str:
        return "1.0"
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            "session_id": str(self.session_id),
            "objective": self.objective,
            "participating_agents": self.participating_agents
        }


class CoordinationSessionCompletedEvent(DomainEvent):
    """Event raised when a coordination session completes."""
    
    def __init__(
        self,
        aggregate_id: EntityId,
        session_id: EntityId,
        results: Dict[str, Any],
        metrics: Dict[str, float],
        duration_minutes: float,
        **kwargs
    ):
        super().__init__(aggregate_id=aggregate_id, **kwargs)
        self.session_id = session_id
        self.results = results
        self.metrics = metrics
        self.duration_minutes = duration_minutes
    
    def _get_event_version(self) -> str:
        return "1.0"
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            "session_id": str(self.session_id),
            "results": self.results,
            "metrics": self.metrics,
            "duration_minutes": self.duration_minutes
        }


class AgentCollaborationEvent(DomainEvent):
    """Event raised when agents collaborate on a task."""
    
    def __init__(
        self,
        aggregate_id: EntityId,
        primary_agent_id: EntityId,
        collaborating_agents: List[EntityId],
        collaboration_type: str,
        shared_context: Dict[str, Any],
        **kwargs
    ):
        super().__init__(aggregate_id=aggregate_id, **kwargs)
        self.primary_agent_id = primary_agent_id
        self.collaborating_agents = collaborating_agents
        self.collaboration_type = collaboration_type
        self.shared_context = shared_context
    
    def _get_event_version(self) -> str:
        return "1.0"
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            "primary_agent_id": str(self.primary_agent_id),
            "collaborating_agents": [str(agent_id) for agent_id in self.collaborating_agents],
            "collaboration_type": self.collaboration_type,
            "shared_context": self.shared_context
        }


class CoordinationConflictEvent(DomainEvent):
    """Event raised when there's a conflict in coordination."""
    
    def __init__(
        self,
        aggregate_id: EntityId,
        session_id: EntityId,
        conflicting_agents: List[EntityId],
        conflict_type: str,
        conflict_description: str,
        resolution_strategy: str,
        **kwargs
    ):
        super().__init__(aggregate_id=aggregate_id, **kwargs)
        self.session_id = session_id
        self.conflicting_agents = conflicting_agents
        self.conflict_type = conflict_type
        self.conflict_description = conflict_description
        self.resolution_strategy = resolution_strategy
    
    def _get_event_version(self) -> str:
        return "1.0"
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            "session_id": str(self.session_id),
            "conflicting_agents": [str(agent_id) for agent_id in self.conflicting_agents],
            "conflict_type": self.conflict_type,
            "conflict_description": self.conflict_description,
            "resolution_strategy": self.resolution_strategy
        }


class ResourceAllocationEvent(DomainEvent):
    """Event raised when resources are allocated to agents."""
    
    def __init__(
        self,
        aggregate_id: EntityId,
        agent_id: EntityId,
        resource_type: str,
        allocated_amount: int,
        allocation_duration: int,
        **kwargs
    ):
        super().__init__(aggregate_id=aggregate_id, **kwargs)
        self.agent_id = agent_id
        self.resource_type = resource_type
        self.allocated_amount = allocated_amount
        self.allocation_duration = allocation_duration
    
    def _get_event_version(self) -> str:
        return "1.0"
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            "agent_id": str(self.agent_id),
            "resource_type": self.resource_type,
            "allocated_amount": self.allocated_amount,
            "allocation_duration": self.allocation_duration
        }


class PerformanceMetricsUpdatedEvent(DomainEvent):
    """Event raised when agent performance metrics are updated."""
    
    def __init__(
        self,
        aggregate_id: EntityId,
        agent_id: EntityId,
        metrics: Dict[str, float],
        measurement_period: str,
        **kwargs
    ):
        super().__init__(aggregate_id=aggregate_id, **kwargs)
        self.agent_id = agent_id
        self.metrics = metrics
        self.measurement_period = measurement_period
    
    def _get_event_version(self) -> str:
        return "1.0"
    
    def get_event_data(self) -> Dict[str, Any]:
        return {
            "agent_id": str(self.agent_id),
            "metrics": self.metrics,
            "measurement_period": self.measurement_period
        }