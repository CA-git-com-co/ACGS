"""
Reliability Framework Data Models

Extracted from LLM Reliability Framework for better code organization
Constitutional Hash: cdd01ef066bc6cf2
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .reliability_enums import (
    CONSTITUTIONAL_HASH,
    ReliabilityLevel,
    RecoveryStrategy,
    RecoveryTrigger,
    RecoveryStatus,
    CriticalFailureMode,
)


@dataclass
class RecoveryAction:
    """Represents a recovery action to be executed."""

    strategy: RecoveryStrategy
    trigger: RecoveryTrigger
    priority: int  # 1 = highest priority
    target_component: str  # Model name, service, or "system"
    parameters: Dict[str, Any] = field(default_factory=dict)
    estimated_recovery_time: float = 30.0  # seconds
    success_probability: float = 0.8
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class RecoveryExecution:
    """Tracks the execution of a recovery action."""

    action: RecoveryAction
    status: RecoveryStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metrics_before: Optional[Dict[str, float]] = None
    metrics_after: Optional[Dict[str, float]] = None
    effectiveness_score: Optional[float] = None  # 0.0 to 1.0


@dataclass
class LLMReliabilityConfig:
    """Enhanced configuration for LLM reliability framework."""

    # Core reliability settings
    target_reliability: ReliabilityLevel = ReliabilityLevel.SAFETY_CRITICAL
    ensemble_size: int = 5  # Number of models in ensemble (1 primary + 4 validators)
    consensus_threshold: float = 0.8  # Agreement threshold for intermediate consensus steps
    bias_detection_enabled: bool = True
    semantic_validation_enabled: bool = True
    fallback_strategy: str = "conservative"  # "conservative", "majority", "expert"
    rule_based_fallback_enabled: bool = True  # Enable rule-based fallback
    max_retries: int = 3
    llm_failure_threshold: int = 5  # Threshold for consecutive LLM failures
    
    # Performance settings
    response_timeout: float = 30.0
    max_concurrent_requests: int = 100
    cache_enabled: bool = True
    cache_ttl: int = 3600  # seconds
    
    # Monitoring and metrics
    metrics_enabled: bool = True
    detailed_logging: bool = True
    alert_threshold: float = 0.95  # Alert when reliability drops below this
    
    # Constitutional compliance
    constitutional_hash: str = CONSTITUTIONAL_HASH
    constitutional_validation_enabled: bool = True


@dataclass
class ReliabilityMetrics:
    """Comprehensive metrics for reliability tracking."""

    # Core reliability metrics
    overall_reliability_score: float = 0.0
    consensus_success_rate: float = 0.0
    bias_detection_rate: float = 0.0
    semantic_faithfulness_score: float = 0.0
    
    # Performance metrics
    average_response_time: float = 0.0
    p95_response_time: float = 0.0
    p99_response_time: float = 0.0
    throughput_rps: float = 0.0
    
    # Failure tracking
    total_requests: int = 0
    failed_requests: int = 0
    fallback_activations: int = 0
    escalations: int = 0
    recoveries: int = 0
    
    # Model-specific metrics
    model_failures: Dict[str, int] = field(default_factory=dict)
    model_response_times: Dict[str, List[float]] = field(default_factory=dict)
    
    # Timestamp tracking
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    measurement_window_start: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class UltraReliableResult:
    """Result from ultra-reliable LLM processing."""

    content: str
    confidence: float
    reliability_score: float
    consensus_achieved: bool
    models_used: List[str]
    processing_time: float
    bias_score: float
    semantic_faithfulness: float
    fallback_used: bool
    recovery_actions: List[RecoveryAction] = field(default_factory=list)
    
    # Metadata
    request_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    constitutional_hash: str = CONSTITUTIONAL_HASH
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "content": self.content,
            "confidence": self.confidence,
            "reliability_score": self.reliability_score,
            "consensus_achieved": self.consensus_achieved,
            "models_used": self.models_used,
            "processing_time": self.processing_time,
            "bias_score": self.bias_score,
            "semantic_faithfulness": self.semantic_faithfulness,
            "fallback_used": self.fallback_used,
            "recovery_actions": [
                {
                    "strategy": action.strategy.value,
                    "trigger": action.trigger.value,
                    "priority": action.priority,
                    "target_component": action.target_component,
                }
                for action in self.recovery_actions
            ],
            "request_id": self.request_id,
            "timestamp": self.timestamp.isoformat(),
            "constitutional_hash": self.constitutional_hash,
        }