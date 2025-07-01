"""
Message types for DGM Service event-driven communication.

Defines structured message types for different categories of events
in the Darwin Gödel Machine Service ecosystem.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class EventType(Enum):
    """Types of DGM events."""

    # Improvement events
    IMPROVEMENT_PROPOSED = "improvement.proposed"
    IMPROVEMENT_APPROVED = "improvement.approved"
    IMPROVEMENT_REJECTED = "improvement.rejected"
    IMPROVEMENT_EXECUTED = "improvement.executed"
    IMPROVEMENT_COMPLETED = "improvement.completed"
    IMPROVEMENT_FAILED = "improvement.failed"
    IMPROVEMENT_ROLLED_BACK = "improvement.rolled_back"

    # Performance events
    PERFORMANCE_METRICS_UPDATED = "performance.metrics.updated"
    PERFORMANCE_BASELINE_ESTABLISHED = "performance.baseline.established"
    PERFORMANCE_DEGRADATION_DETECTED = "performance.degradation.detected"
    PERFORMANCE_IMPROVEMENT_DETECTED = "performance.improvement.detected"
    PERFORMANCE_ALERT_TRIGGERED = "performance.alert.triggered"

    # Constitutional events
    CONSTITUTIONAL_ASSESSMENT_STARTED = "constitutional.assessment.started"
    CONSTITUTIONAL_ASSESSMENT_COMPLETED = "constitutional.assessment.completed"
    CONSTITUTIONAL_VIOLATION_DETECTED = "constitutional.violation.detected"
    CONSTITUTIONAL_COMPLIANCE_VERIFIED = "constitutional.compliance.verified"
    CONSTITUTIONAL_REMEDIATION_REQUIRED = "constitutional.remediation.required"

    # Bandit algorithm events
    BANDIT_ARM_SELECTED = "bandit.arm.selected"
    BANDIT_REWARD_UPDATED = "bandit.reward.updated"
    BANDIT_STATE_UPDATED = "bandit.state.updated"
    BANDIT_EXPLORATION_TRIGGERED = "bandit.exploration.triggered"
    BANDIT_EXPLOITATION_TRIGGERED = "bandit.exploitation.triggered"


class EventPriority(Enum):
    """Event priority levels."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class DGMEvent:
    """Base class for all DGM events."""

    event_id: str = field(default_factory=lambda: str(uuid4()))
    event_type: EventType = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    source_service: str = "dgm-service"
    priority: EventPriority = EventPriority.NORMAL
    correlation_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value if self.event_type else None,
            "timestamp": self.timestamp,
            "source_service": self.source_service,
            "priority": self.priority.value,
            "correlation_id": self.correlation_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "metadata": self.metadata,
            "data": self._get_data(),
        }

    def _get_data(self) -> Dict[str, Any]:
        """Get event-specific data. Override in subclasses."""
        return {}


@dataclass
class ImprovementEvent(DGMEvent):
    """Events related to improvement proposals and execution."""

    improvement_id: str = None
    strategy: str = None
    target_services: List[str] = field(default_factory=list)
    expected_improvement: Optional[float] = None
    actual_improvement: Optional[float] = None
    risk_level: str = None
    execution_time: Optional[float] = None
    rollback_available: bool = False
    constitutional_compliance_score: Optional[float] = None

    def _get_data(self) -> Dict[str, Any]:
        return {
            "improvement_id": self.improvement_id,
            "strategy": self.strategy,
            "target_services": self.target_services,
            "expected_improvement": self.expected_improvement,
            "actual_improvement": self.actual_improvement,
            "risk_level": self.risk_level,
            "execution_time": self.execution_time,
            "rollback_available": self.rollback_available,
            "constitutional_compliance_score": self.constitutional_compliance_score,
        }


@dataclass
class PerformanceEvent(DGMEvent):
    """Events related to performance monitoring and metrics."""

    metric_name: str = None
    metric_value: float = None
    service_name: str = None
    baseline_value: Optional[float] = None
    threshold_value: Optional[float] = None
    improvement_percentage: Optional[float] = None
    alert_level: str = None
    measurement_window: str = None
    tags: Dict[str, str] = field(default_factory=dict)

    def _get_data(self) -> Dict[str, Any]:
        return {
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "service_name": self.service_name,
            "baseline_value": self.baseline_value,
            "threshold_value": self.threshold_value,
            "improvement_percentage": self.improvement_percentage,
            "alert_level": self.alert_level,
            "measurement_window": self.measurement_window,
            "tags": self.tags,
        }


@dataclass
class ConstitutionalEvent(DGMEvent):
    """Events related to constitutional compliance and governance."""

    improvement_id: str = None
    compliance_score: float = None
    constitutional_hash: str = None
    validator_version: str = None
    assessment_type: str = None  # proposal, execution, monitoring
    violations: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    remediation_required: bool = False
    governance_principles: List[str] = field(default_factory=list)

    def _get_data(self) -> Dict[str, Any]:
        return {
            "improvement_id": self.improvement_id,
            "compliance_score": self.compliance_score,
            "constitutional_hash": self.constitutional_hash,
            "validator_version": self.validator_version,
            "assessment_type": self.assessment_type,
            "violations": self.violations,
            "recommendations": self.recommendations,
            "remediation_required": self.remediation_required,
            "governance_principles": self.governance_principles,
        }


@dataclass
class BanditEvent(DGMEvent):
    """Events related to bandit algorithm operations."""

    algorithm_type: str = None  # UCB1, epsilon-greedy, Thompson sampling
    arm_name: str = None
    arm_pulls: int = None
    arm_rewards: float = None
    arm_success_rate: float = None
    exploration_parameter: Optional[float] = None
    confidence_bound: Optional[float] = None
    total_pulls: int = None
    average_reward: float = None
    action_taken: str = None  # explore, exploit

    def _get_data(self) -> Dict[str, Any]:
        return {
            "algorithm_type": self.algorithm_type,
            "arm_name": self.arm_name,
            "arm_pulls": self.arm_pulls,
            "arm_rewards": self.arm_rewards,
            "arm_success_rate": self.arm_success_rate,
            "exploration_parameter": self.exploration_parameter,
            "confidence_bound": self.confidence_bound,
            "total_pulls": self.total_pulls,
            "average_reward": self.average_reward,
            "action_taken": self.action_taken,
        }


# Subject patterns for NATS routing
SUBJECT_PATTERNS = {
    # Improvement events
    EventType.IMPROVEMENT_PROPOSED: "dgm.improvement.proposed",
    EventType.IMPROVEMENT_APPROVED: "dgm.improvement.approved",
    EventType.IMPROVEMENT_REJECTED: "dgm.improvement.rejected",
    EventType.IMPROVEMENT_EXECUTED: "dgm.improvement.executed",
    EventType.IMPROVEMENT_COMPLETED: "dgm.improvement.completed",
    EventType.IMPROVEMENT_FAILED: "dgm.improvement.failed",
    EventType.IMPROVEMENT_ROLLED_BACK: "dgm.improvement.rolled_back",
    # Performance events
    EventType.PERFORMANCE_METRICS_UPDATED: "dgm.performance.metrics.updated",
    EventType.PERFORMANCE_BASELINE_ESTABLISHED: "dgm.performance.baseline.established",
    EventType.PERFORMANCE_DEGRADATION_DETECTED: "dgm.performance.degradation.detected",
    EventType.PERFORMANCE_IMPROVEMENT_DETECTED: "dgm.performance.improvement.detected",
    EventType.PERFORMANCE_ALERT_TRIGGERED: "dgm.performance.alert.triggered",
    # Constitutional events
    EventType.CONSTITUTIONAL_ASSESSMENT_STARTED: "dgm.constitutional.assessment.started",
    EventType.CONSTITUTIONAL_ASSESSMENT_COMPLETED: "dgm.constitutional.assessment.completed",
    EventType.CONSTITUTIONAL_VIOLATION_DETECTED: "dgm.constitutional.violation.detected",
    EventType.CONSTITUTIONAL_COMPLIANCE_VERIFIED: "dgm.constitutional.compliance.verified",
    EventType.CONSTITUTIONAL_REMEDIATION_REQUIRED: "dgm.constitutional.remediation.required",
    # Bandit events
    EventType.BANDIT_ARM_SELECTED: "dgm.bandit.arm.selected",
    EventType.BANDIT_REWARD_UPDATED: "dgm.bandit.reward.updated",
    EventType.BANDIT_STATE_UPDATED: "dgm.bandit.state.updated",
    EventType.BANDIT_EXPLORATION_TRIGGERED: "dgm.bandit.exploration.triggered",
    EventType.BANDIT_EXPLOITATION_TRIGGERED: "dgm.bandit.exploitation.triggered",
}


def get_subject_for_event(event_type: EventType) -> str:
    """Get NATS subject for event type."""
    return SUBJECT_PATTERNS.get(event_type, f"dgm.unknown.{event_type.value}")


def create_improvement_event(
    event_type: EventType, improvement_id: str, **kwargs
) -> ImprovementEvent:
    """Create improvement event with common fields."""
    return ImprovementEvent(
        event_type=event_type, improvement_id=improvement_id, **kwargs
    )


def create_performance_event(
    event_type: EventType,
    metric_name: str,
    metric_value: float,
    service_name: str,
    **kwargs,
) -> PerformanceEvent:
    """Create performance event with common fields."""
    return PerformanceEvent(
        event_type=event_type,
        metric_name=metric_name,
        metric_value=metric_value,
        service_name=service_name,
        **kwargs,
    )


def create_constitutional_event(
    event_type: EventType, improvement_id: str, compliance_score: float, **kwargs
) -> ConstitutionalEvent:
    """Create constitutional event with common fields."""
    return ConstitutionalEvent(
        event_type=event_type,
        improvement_id=improvement_id,
        compliance_score=compliance_score,
        **kwargs,
    )


def create_bandit_event(
    event_type: EventType, algorithm_type: str, arm_name: str, **kwargs
) -> BanditEvent:
    """Create bandit event with common fields."""
    return BanditEvent(
        event_type=event_type,
        algorithm_type=algorithm_type,
        arm_name=arm_name,
        **kwargs,
    )
