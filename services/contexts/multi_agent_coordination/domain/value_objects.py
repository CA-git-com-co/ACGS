"""
Multi-Agent Coordination Value Objects
Constitutional Hash: cdd01ef066bc6cf2

Immutable value objects for the multi-agent coordination domain.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from services.shared.domain.base import ValueObject


class AgentStatus(str, Enum):
    """Status of an agent in the coordination system."""

    AVAILABLE = "available"
    BUSY = "busy"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"


class TaskStatus(str, Enum):
    """Status of a coordination task."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CoordinationStrategy(str, Enum):
    """Coordination strategy for multi-agent sessions."""

    HIERARCHICAL = "hierarchical"
    PEER_TO_PEER = "peer_to_peer"
    CONSENSUS = "consensus"
    COMPETITIVE = "competitive"


@dataclass(frozen=True)
class AgentCapability(ValueObject):
    """Represents a capability that an agent possesses."""

    capability_type: str
    proficiency_level: float  # 0.0 to 1.0
    domain_knowledge: list[str]
    resource_requirements: dict[str, Any]
    performance_indicators: dict[str, float]

    def __post_init__(self):
        """Validate capability data."""
        if not 0.0 <= self.proficiency_level <= 1.0:
            raise ValueError("Proficiency level must be between 0.0 and 1.0")

        if not self.capability_type:
            raise ValueError("Capability type cannot be empty")

    def is_compatible_with(self, other: "AgentCapability") -> bool:
        """Check if this capability is compatible with another."""
        return (
            self.capability_type == other.capability_type
            and len(set(self.domain_knowledge) & set(other.domain_knowledge)) > 0
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "capability_type": self.capability_type,
            "proficiency_level": self.proficiency_level,
            "domain_knowledge": self.domain_knowledge,
            "resource_requirements": self.resource_requirements,
            "performance_indicators": self.performance_indicators,
        }


@dataclass(frozen=True)
class TaskRequirements(ValueObject):
    """Requirements for executing a coordination task."""

    required_capabilities: list[str]
    minimum_proficiency: float
    estimated_duration_minutes: int
    resource_limits: dict[str, Any]
    priority_level: int  # 1-5, 5 being highest
    complexity_score: float  # 0.0 to 1.0

    def __post_init__(self):
        """Validate task requirements."""
        if not 0.0 <= self.minimum_proficiency <= 1.0:
            raise ValueError("Minimum proficiency must be between 0.0 and 1.0")

        if not 1 <= self.priority_level <= 5:
            raise ValueError("Priority level must be between 1 and 5")

        if not 0.0 <= self.complexity_score <= 1.0:
            raise ValueError("Complexity score must be between 0.0 and 1.0")

    def is_satisfied_by(self, capability: AgentCapability) -> bool:
        """Check if requirements are satisfied by agent capability."""
        return (
            capability.capability_type in self.required_capabilities
            and capability.proficiency_level >= self.minimum_proficiency
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "required_capabilities": self.required_capabilities,
            "minimum_proficiency": self.minimum_proficiency,
            "estimated_duration_minutes": self.estimated_duration_minutes,
            "resource_limits": self.resource_limits,
            "priority_level": self.priority_level,
            "complexity_score": self.complexity_score,
        }


@dataclass(frozen=True)
class CoordinationObjective(ValueObject):
    """Objective of a multi-agent coordination session."""

    objective_type: str
    description: str
    success_criteria: list[str]
    quality_thresholds: dict[str, float]
    time_constraints: dict[str, int]  # in minutes
    stakeholder_requirements: list[str]

    def __post_init__(self):
        """Validate coordination objective."""
        if not self.objective_type:
            raise ValueError("Objective type cannot be empty")

        if not self.description:
            raise ValueError("Description cannot be empty")

        if not self.success_criteria:
            raise ValueError("Success criteria must be specified")

    def is_achieved(self, results: dict[str, Any]) -> bool:
        """Check if objective is achieved based on results."""
        # Check quality thresholds
        for metric, threshold in self.quality_thresholds.items():
            if results.get(metric, 0.0) < threshold:
                return False

        # Check if all success criteria are met
        achieved_criteria = results.get("achieved_criteria", [])
        return all(
            criterion in achieved_criteria for criterion in self.success_criteria
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "objective_type": self.objective_type,
            "description": self.description,
            "success_criteria": self.success_criteria,
            "quality_thresholds": self.quality_thresholds,
            "time_constraints": self.time_constraints,
            "stakeholder_requirements": self.stakeholder_requirements,
        }


@dataclass(frozen=True)
class CoordinationMetrics(ValueObject):
    """Metrics for evaluating coordination effectiveness."""

    efficiency_score: float  # 0.0 to 1.0
    communication_overhead: float  # seconds
    resource_utilization: float  # 0.0 to 1.0
    quality_score: float  # 0.0 to 1.0
    collaboration_index: float  # 0.0 to 1.0
    time_to_completion: int  # minutes

    def __post_init__(self):
        """Validate coordination metrics."""
        for score in [
            self.efficiency_score,
            self.resource_utilization,
            self.quality_score,
            self.collaboration_index,
        ]:
            if not 0.0 <= score <= 1.0:
                raise ValueError("Scores must be between 0.0 and 1.0")

        if self.communication_overhead < 0:
            raise ValueError("Communication overhead cannot be negative")

        if self.time_to_completion < 0:
            raise ValueError("Time to completion cannot be negative")

    def get_overall_score(self) -> float:
        """Calculate overall coordination effectiveness score."""
        weights = {
            "efficiency": 0.25,
            "quality": 0.30,
            "collaboration": 0.20,
            "resource_utilization": 0.15,
            "time_factor": 0.10,
        }

        # Time factor: better scores for faster completion
        time_factor = max(
            0.0, 1.0 - (self.time_to_completion / 1440)
        )  # Normalize to 24 hours

        overall_score = (
            weights["efficiency"] * self.efficiency_score
            + weights["quality"] * self.quality_score
            + weights["collaboration"] * self.collaboration_index
            + weights["resource_utilization"] * self.resource_utilization
            + weights["time_factor"] * time_factor
        )

        return min(1.0, max(0.0, overall_score))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "efficiency_score": self.efficiency_score,
            "communication_overhead": self.communication_overhead,
            "resource_utilization": self.resource_utilization,
            "quality_score": self.quality_score,
            "collaboration_index": self.collaboration_index,
            "time_to_completion": self.time_to_completion,
            "overall_score": self.get_overall_score(),
        }


@dataclass(frozen=True)
class AgentProfile(ValueObject):
    """Profile information for an agent."""

    agent_name: str
    agent_version: str
    specializations: list[str]
    performance_history: dict[str, float]
    trust_level: float  # 0.0 to 1.0
    reputation_score: float  # 0.0 to 1.0
    last_active: datetime

    def __post_init__(self):
        """Validate agent profile."""
        if not self.agent_name:
            raise ValueError("Agent name cannot be empty")

        if not 0.0 <= self.trust_level <= 1.0:
            raise ValueError("Trust level must be between 0.0 and 1.0")

        if not 0.0 <= self.reputation_score <= 1.0:
            raise ValueError("Reputation score must be between 0.0 and 1.0")

    def is_trustworthy(self, minimum_trust: float = 0.7) -> bool:
        """Check if agent meets minimum trust requirements."""
        return self.trust_level >= minimum_trust

    def get_experience_level(self) -> str:
        """Get experience level based on performance history."""
        if not self.performance_history:
            return "novice"

        avg_performance = sum(self.performance_history.values()) / len(
            self.performance_history
        )
        task_count = self.performance_history.get("task_count", 0)

        if avg_performance >= 0.9 and task_count >= 100:
            return "expert"
        if avg_performance >= 0.8 and task_count >= 50:
            return "advanced"
        if avg_performance >= 0.7 and task_count >= 20:
            return "intermediate"
        return "novice"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "agent_name": self.agent_name,
            "agent_version": self.agent_version,
            "specializations": self.specializations,
            "performance_history": self.performance_history,
            "trust_level": self.trust_level,
            "reputation_score": self.reputation_score,
            "last_active": self.last_active.isoformat(),
            "experience_level": self.get_experience_level(),
        }


@dataclass(frozen=True)
class CoordinationContext(ValueObject):
    """Context information for coordination sessions."""

    context_type: str
    environment_constraints: dict[str, Any]
    available_resources: dict[str, int]
    time_constraints: dict[str, datetime]
    regulatory_requirements: list[str]
    stakeholder_preferences: dict[str, Any]

    def __post_init__(self):
        """Validate coordination context."""
        if not self.context_type:
            raise ValueError("Context type cannot be empty")

    def is_resource_available(self, resource_type: str, required_amount: int) -> bool:
        """Check if required resource is available."""
        available = self.available_resources.get(resource_type, 0)
        return available >= required_amount

    def meets_constraints(self, requirements: TaskRequirements) -> bool:
        """Check if context meets task requirements."""
        # Check resource constraints
        for resource, amount in requirements.resource_limits.items():
            if not self.is_resource_available(resource, amount):
                return False

        return True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "context_type": self.context_type,
            "environment_constraints": selfconfig/environments/development.environment_constraints,
            "available_resources": self.available_resources,
            "time_constraints": {
                k: v.isoformat() for k, v in self.time_constraints.items()
            },
            "regulatory_requirements": self.regulatory_requirements,
            "stakeholder_preferences": self.stakeholder_preferences,
        }
