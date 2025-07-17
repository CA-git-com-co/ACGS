"""
Reliability Framework Enums and Constants

Extracted from LLM Reliability Framework for better code organization
Constitutional Hash: cdd01ef066bc6cf2
"""

from enum import Enum

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ReliabilityLevel(Enum):
    """Reliability levels for different application contexts."""

    STANDARD = "standard"  # 95% reliability
    HIGH = "high"  # 99% reliability
    SAFETY_CRITICAL = "safety_critical"  # 99.9% reliability
    MISSION_CRITICAL = "mission_critical"  # 99.99% reliability


class RecoveryStrategy(Enum):
    """Recovery strategies for automatic reliability recovery."""

    MODEL_REROUTING = "model_rerouting"
    MODEL_RETRAINING = "model_retraining"
    TRAFFIC_REDISTRIBUTION = "traffic_redistribution"
    CONFIGURATION_ADJUSTMENT = "configuration_adjustment"
    CIRCUIT_BREAKER = "circuit_breaker"
    FALLBACK_ACTIVATION = "fallback_activation"
    EMERGENCY_SAFEGUARDS = "emergency_safeguards"
    HUMAN_ESCALATION = "human_escalation"


class RecoveryTrigger(Enum):
    """Triggers that initiate automatic recovery procedures."""

    RELIABILITY_THRESHOLD_BREACH = "reliability_threshold_breach"
    MODEL_FAILURE_RATE_HIGH = "model_failure_rate_high"
    RESPONSE_TIME_DEGRADATION = "response_time_degradation"
    CONSENSUS_FAILURE = "consensus_failure"
    BIAS_DETECTION_SPIKE = "bias_detection_spike"
    SEMANTIC_FAITHFULNESS_DROP = "semantic_faithfulness_drop"
    SYSTEM_OVERLOAD = "system_overload"
    PREDICTIVE_FAILURE = "predictive_failure"


class RecoveryStatus(Enum):
    """Status of recovery operations."""

    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    SUCCESSFUL = "successful"
    FAILED = "failed"
    PARTIALLY_SUCCESSFUL = "partially_successful"
    CANCELLED = "cancelled"


class CriticalFailureMode(Enum):
    """Enumerates documented critical failure modes."""

    SEMANTIC_MISALIGNMENT = "semantic_misalignment"
    LOGICAL_INCONSISTENCY = "logical_inconsistency"
    CONTEXT_INTERPRETATION_ERROR = "context_interpretation_error"
    EDGE_CASE_FAILURE = "edge_case_failure"