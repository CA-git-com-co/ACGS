"""
Syndrome Diagnostic Engine Models

Diagnostic data models with audit trail integration, error classification,
and recovery recommendation engine models.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for classification."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ErrorCategory(Enum):
    """Error categories for classification."""

    CONSTITUTIONAL_VIOLATION = "constitutional_violation"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    SECURITY_BREACH = "security_breach"
    DATA_CORRUPTION = "data_corruption"
    NETWORK_FAILURE = "network_failure"
    RESOURCE_EXHAUSTION = "resource_exhaustion"
    LOGIC_ERROR = "logic_error"
    CONFIGURATION_ERROR = "configuration_error"
    EXTERNAL_DEPENDENCY = "external_dependency"
    UNKNOWN = "unknown"


class RecoveryStrategy(Enum):
    """Recovery strategy types."""

    AUTOMATIC_RETRY = "automatic_retry"
    CIRCUIT_BREAKER = "circuit_breaker"
    FALLBACK_MODE = "fallback_mode"
    MANUAL_INTERVENTION = "manual_intervention"
    SYSTEM_RESTART = "system_restart"
    DATA_RECOVERY = "data_recovery"
    CONFIGURATION_RESET = "configuration_reset"
    ESCALATION = "escalation"


@dataclass
class ErrorClassification:
    """
    Error classification with severity assessment and categorization.

    Provides comprehensive error analysis with constitutional compliance
    considerations and recovery strategy recommendations.
    """

    error_id: str
    severity: ErrorSeverity
    category: ErrorCategory
    confidence_score: float = 0.0
    constitutional_impact: bool = False

    # Error details
    error_message: str = ""
    error_context: dict[str, Any] = field(default_factory=dict)
    stack_trace: str | None = None

    # Classification metadata
    classification_timestamp: datetime = field(default_factory=datetime.now)
    classifier_model: str = "rule_based"
    classification_features: dict[str, float] = field(default_factory=dict)

    # Constitutional compliance
    constitutional_hash: str = "cdd01ef066bc6cf2"
    compliance_violation_details: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize classification after creation."""
        if not self.error_id:
            self.error_id = (
                f"err_{int(datetime.now().timestamp())}_{hash(self.error_message) % 10000:04d}"
            )

    def is_critical(self) -> bool:
        """Check if error is critical severity."""
        return self.severity == ErrorSeverity.CRITICAL

    def requires_immediate_action(self) -> bool:
        """Check if error requires immediate action."""
        return (
            self.severity in [ErrorSeverity.CRITICAL, ErrorSeverity.HIGH]
            or self.constitutional_impact
        )

    def get_priority_score(self) -> float:
        """Calculate priority score for error handling."""
        severity_weights = {
            ErrorSeverity.CRITICAL: 1.0,
            ErrorSeverity.HIGH: 0.8,
            ErrorSeverity.MEDIUM: 0.6,
            ErrorSeverity.LOW: 0.4,
            ErrorSeverity.INFO: 0.2,
        }

        base_score = severity_weights.get(self.severity, 0.5)

        # Boost score for constitutional violations
        if self.constitutional_impact:
            base_score = min(1.0, base_score + 0.3)

        # Adjust by confidence
        return base_score * self.confidence_score

    def to_dict(self) -> dict[str, Any]:
        """Convert classification to dictionary."""
        return {
            "error_id": self.error_id,
            "severity": self.severity.value,
            "category": self.category.value,
            "confidence_score": self.confidence_score,
            "constitutional_impact": self.constitutional_impact,
            "error_message": self.error_message,
            "error_context": self.error_context,
            "stack_trace": self.stack_trace,
            "classification_timestamp": self.classification_timestamp.isoformat(),
            "classifier_model": self.classifier_model,
            "classification_features": self.classification_features,
            "constitutional_hash": self.constitutional_hash,
            "compliance_violation_details": self.compliance_violation_details,
            "priority_score": self.get_priority_score(),
        }


@dataclass
class RecoveryRecommendation:
    """
    Recovery recommendation with implementation details and success probability.

    Provides actionable recovery strategies with constitutional compliance
    considerations and implementation guidance.
    """

    recommendation_id: str
    strategy: RecoveryStrategy
    description: str
    implementation_steps: list[str] = field(default_factory=list)

    # Success estimation
    success_probability: float = 0.0
    estimated_recovery_time_minutes: int = 0
    resource_requirements: dict[str, Any] = field(default_factory=dict)

    # Risk assessment
    risk_level: ErrorSeverity = ErrorSeverity.LOW
    side_effects: list[str] = field(default_factory=list)
    rollback_plan: list[str] = field(default_factory=list)

    # Constitutional compliance
    constitutional_compliance: bool = True
    compliance_notes: list[str] = field(default_factory=list)

    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    created_by: str = "syndrome_diagnostic_engine"

    def __post_init__(self):
        """Initialize recommendation after creation."""
        if not self.recommendation_id:
            self.recommendation_id = (
                f"rec_{int(datetime.now().timestamp())}_{hash(self.description) % 10000:04d}"
            )

    def is_safe_to_execute(self) -> bool:
        """Check if recommendation is safe to execute automatically."""
        return (
            self.constitutional_compliance
            and self.risk_level in [ErrorSeverity.LOW, ErrorSeverity.INFO]
            and self.success_probability >= 0.8
        )

    def get_execution_priority(self) -> float:
        """Calculate execution priority for recommendation."""
        priority_factors = [
            self.success_probability,
            1.0 if self.constitutional_compliance else 0.0,
            1.0 - (self.estimated_recovery_time_minutes / 120.0),  # Prefer faster recovery
            1.0 if self.risk_level == ErrorSeverity.LOW else 0.5,
        ]

        return sum(priority_factors) / len(priority_factors)

    def to_dict(self) -> dict[str, Any]:
        """Convert recommendation to dictionary."""
        return {
            "recommendation_id": self.recommendation_id,
            "strategy": self.strategy.value,
            "description": self.description,
            "implementation_steps": self.implementation_steps,
            "success_probability": self.success_probability,
            "estimated_recovery_time_minutes": self.estimated_recovery_time_minutes,
            "resource_requirements": self.resource_requirements,
            "risk_level": self.risk_level.value,
            "side_effects": self.side_effects,
            "rollback_plan": self.rollback_plan,
            "constitutional_compliance": self.constitutional_compliance,
            "compliance_notes": self.compliance_notes,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
            "is_safe_to_execute": self.is_safe_to_execute(),
            "execution_priority": self.get_execution_priority(),
        }


class DiagnosticResult(BaseModel):
    """
    Comprehensive diagnostic result with error analysis and recovery recommendations.

    Provides complete diagnostic information including error classification,
    recovery recommendations, and constitutional compliance assessment.
    """

    diagnostic_id: str = Field(..., description="Unique diagnostic identifier")
    target_system: str = Field(..., description="System being diagnosed")

    # Error analysis
    errors_detected: list[ErrorClassification] = Field(default_factory=list)
    error_count: int = Field(default=0, description="Total number of errors")
    critical_error_count: int = Field(default=0, description="Number of critical errors")

    # Recovery recommendations
    recommendations: list[RecoveryRecommendation] = Field(default_factory=list)
    auto_executable_recommendations: int = Field(
        default=0, description="Safe auto-executable recommendations"
    )

    # System health assessment
    overall_health_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Overall health score"
    )
    constitutional_compliance_score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Compliance score"
    )

    # Diagnostic metadata
    diagnostic_timestamp: datetime = Field(default_factory=datetime.now)
    diagnostic_duration_ms: float = Field(default=0.0, description="Diagnostic duration")
    constitutional_hash: str = Field(default="cdd01ef066bc6cf2", description="Constitution hash")

    # Audit trail
    audit_trail: list[str] = Field(default_factory=list, description="Diagnostic audit trail")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ErrorClassification: lambda v: v.to_dict(),
            RecoveryRecommendation: lambda v: v.to_dict(),
        }

    def add_error(self, error: ErrorClassification) -> None:
        """Add error classification to diagnostic result."""
        self.errors_detected.append(error)
        self.error_count = len(self.errors_detected)
        self.critical_error_count = sum(
            1 for err in self.errors_detected if err.severity == ErrorSeverity.CRITICAL
        )

        # Update health scores
        self._update_health_scores()

    def add_recommendation(self, recommendation: RecoveryRecommendation) -> None:
        """Add recovery recommendation to diagnostic result."""
        self.recommendations.append(recommendation)
        self.auto_executable_recommendations = sum(
            1 for rec in self.recommendations if rec.is_safe_to_execute()
        )

    def _update_health_scores(self) -> None:
        """Update health and compliance scores based on errors."""
        if not self.errors_detected:
            self.overall_health_score = 1.0
            self.constitutional_compliance_score = 1.0
            return

        # Calculate health score based on error severity
        severity_weights = {
            ErrorSeverity.CRITICAL: 0.0,
            ErrorSeverity.HIGH: 0.3,
            ErrorSeverity.MEDIUM: 0.6,
            ErrorSeverity.LOW: 0.8,
            ErrorSeverity.INFO: 0.9,
        }

        health_scores = [severity_weights.get(err.severity, 0.5) for err in self.errors_detected]
        self.overall_health_score = sum(health_scores) / len(health_scores)

        # Calculate constitutional compliance score
        constitutional_violations = sum(
            1 for err in self.errors_detected if err.constitutional_impact
        )

        if constitutional_violations == 0:
            self.constitutional_compliance_score = 1.0
        else:
            violation_penalty = constitutional_violations / len(self.errors_detected)
            self.constitutional_compliance_score = max(0.0, 1.0 - violation_penalty)

    def get_priority_errors(self) -> list[ErrorClassification]:
        """Get errors sorted by priority score."""
        return sorted(self.errors_detected, key=lambda err: err.get_priority_score(), reverse=True)

    def get_priority_recommendations(self) -> list[RecoveryRecommendation]:
        """Get recommendations sorted by execution priority."""
        return sorted(
            self.recommendations,
            key=lambda rec: rec.get_execution_priority(),
            reverse=True,
        )

    def is_system_healthy(self) -> bool:
        """Check if system is considered healthy."""
        return (
            self.overall_health_score >= 0.8
            and self.constitutional_compliance_score >= 0.9
            and self.critical_error_count == 0
        )

    def requires_immediate_attention(self) -> bool:
        """Check if system requires immediate attention."""
        return (
            self.critical_error_count > 0
            or self.overall_health_score < 0.5
            or self.constitutional_compliance_score < 0.8
        )


class DiagnosticMetrics(BaseModel):
    """Metrics for diagnostic engine performance and effectiveness."""

    total_diagnostics: int = Field(default=0, description="Total diagnostics performed")
    successful_diagnostics: int = Field(default=0, description="Successful diagnostics")

    # Error detection metrics
    total_errors_detected: int = Field(default=0, description="Total errors detected")
    critical_errors_detected: int = Field(default=0, description="Critical errors detected")
    false_positive_rate: float = Field(default=0.0, description="False positive rate")

    # Recovery metrics
    total_recommendations: int = Field(default=0, description="Total recommendations generated")
    successful_recoveries: int = Field(default=0, description="Successful recoveries")
    auto_recovery_rate: float = Field(default=0.0, description="Automatic recovery rate")

    # Performance metrics
    average_diagnostic_time_ms: float = Field(default=0.0, description="Average diagnostic time")
    average_health_score: float = Field(default=0.0, description="Average health score")
    average_compliance_score: float = Field(default=0.0, description="Average compliance score")

    # Constitutional compliance
    constitutional_violations_detected: int = Field(
        default=0, description="Constitutional violations"
    )
    constitutional_hash: str = Field(default="cdd01ef066bc6cf2", description="Constitution hash")

    last_updated: datetime = Field(
        default_factory=datetime.now, description="Last update timestamp"
    )

    def calculate_success_rate(self) -> float:
        """Calculate diagnostic success rate."""
        if self.total_diagnostics == 0:
            return 0.0
        return self.successful_diagnostics / self.total_diagnostics

    def calculate_recovery_success_rate(self) -> float:
        """Calculate recovery success rate."""
        if self.total_recommendations == 0:
            return 0.0
        return self.successful_recoveries / self.total_recommendations
