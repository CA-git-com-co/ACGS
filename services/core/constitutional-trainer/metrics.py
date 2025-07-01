"""
Constitutional Metrics Collection
Prometheus metrics and monitoring for constitutional AI training.

Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import time
from dataclasses import asdict, dataclass
from typing import Any

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)

logger = logging.getLogger(__name__)


@dataclass
class ConstitutionalTrainingMetrics:
    """Data class for constitutional training metrics."""

    # Training metrics
    training_sessions_total: int = 0
    training_sessions_successful: int = 0
    training_sessions_failed: int = 0

    # Constitutional compliance metrics
    avg_compliance_score: float = 0.0
    min_compliance_score: float = 1.0
    max_compliance_score: float = 0.0
    compliance_violations_total: int = 0

    # Performance metrics
    avg_training_duration: float = 0.0
    avg_critique_revision_cycles: float = 0.0

    # Privacy metrics
    privacy_budget_utilization: float = 0.0
    privacy_violations_total: int = 0

    # System metrics
    active_sessions: int = 0
    cache_hit_rate: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class ConstitutionalMetrics:
    """Prometheus metrics collector for constitutional AI training."""

    def __init__(self, constitutional_hash: str = "cdd01ef066bc6cf2"):
        self.constitutional_hash = constitutional_hash
        self.registry = CollectorRegistry()

        # Initialize Prometheus metrics
        self._init_prometheus_metrics()

        # Internal state tracking
        self.training_sessions = {}
        self.compliance_scores = []
        self.training_durations = []
        self.critique_cycles = []

    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics."""

        # Training session metrics
        self.training_sessions_total = Counter(
            "constitutional_training_sessions_total",
            "Total constitutional training sessions",
            ["status", "model_type", "constitutional_hash"],
            registry=self.registry,
        )

        self.training_duration = Histogram(
            "constitutional_training_duration_seconds",
            "Duration of constitutional training sessions",
            ["model_type", "training_phase", "constitutional_hash"],
            buckets=[30, 60, 300, 600, 1800, 3600, 7200, float("inf")],
            registry=self.registry,
        )

        # Constitutional compliance metrics
        self.constitutional_compliance_score = Histogram(
            "constitutional_compliance_score",
            "Constitutional compliance scores",
            ["model_id", "evaluation_type", "constitutional_hash"],
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0],
            registry=self.registry,
        )

        self.constitutional_violations_total = Counter(
            "constitutional_violations_total",
            "Total constitutional violations detected",
            ["violation_type", "severity", "model_id", "constitutional_hash"],
            registry=self.registry,
        )

        self.constitutional_compliance_rate = Gauge(
            "constitutional_compliance_rate",
            "Current constitutional compliance rate",
            ["constitutional_hash"],
            registry=self.registry,
        )

        # Critique-revision cycle metrics
        self.critique_revision_cycles = Histogram(
            "constitutional_critique_revision_cycles",
            "Number of critique-revision cycles per training item",
            ["model_type", "constitutional_hash"],
            buckets=[1, 2, 3, 4, 5, float("inf")],
            registry=self.registry,
        )

        self.critique_revision_success_rate = Gauge(
            "constitutional_critique_revision_success_rate",
            "Success rate of critique-revision cycles",
            ["constitutional_hash"],
            registry=self.registry,
        )

        # Privacy metrics
        self.privacy_budget_utilization = Gauge(
            "constitutional_privacy_budget_utilization",
            "Current privacy budget utilization",
            ["model_id", "training_session", "constitutional_hash"],
            registry=self.registry,
        )

        self.privacy_epsilon_current = Gauge(
            "constitutional_privacy_epsilon_current",
            "Current privacy epsilon value",
            ["model_id", "training_session", "constitutional_hash"],
            registry=self.registry,
        )

        self.privacy_violations_total = Counter(
            "constitutional_privacy_violations_total",
            "Total privacy violations detected",
            ["violation_type", "model_id", "constitutional_hash"],
            registry=self.registry,
        )

        # Performance metrics
        self.active_training_sessions = Gauge(
            "constitutional_training_sessions_active",
            "Number of active constitutional training sessions",
            ["constitutional_hash"],
            registry=self.registry,
        )

        self.policy_evaluation_duration = Histogram(
            "constitutional_policy_evaluation_duration_seconds",
            "Duration of policy evaluations",
            ["evaluation_type", "cache_hit", "constitutional_hash"],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0, float("inf")],
            registry=self.registry,
        )

        self.cache_hit_rate = Gauge(
            "constitutional_cache_hit_rate",
            "Cache hit rate for policy evaluations",
            ["cache_type", "constitutional_hash"],
            registry=self.registry,
        )

        # System health metrics
        self.system_health_score = Gauge(
            "constitutional_trainer_health_score",
            "Overall system health score",
            ["component", "constitutional_hash"],
            registry=self.registry,
        )

        # Model quality metrics
        self.model_accuracy = Gauge(
            "constitutional_model_accuracy",
            "Model accuracy after constitutional training",
            ["model_id", "metric_type", "constitutional_hash"],
            registry=self.registry,
        )

        self.model_perplexity = Gauge(
            "constitutional_model_perplexity",
            "Model perplexity after constitutional training",
            ["model_id", "dataset", "constitutional_hash"],
            registry=self.registry,
        )

        # Constitutional info metric
        self.constitutional_info = Info(
            "constitutional_trainer_info",
            "Constitutional trainer information",
            registry=self.registry,
        )

        # Set constitutional info
        self.constitutional_info.info(
            {
                "constitutional_hash": self.constitutional_hash,
                "version": "1.0.0",
                "service": "constitutional-trainer",
            }
        )

    def record_training_session_start(self, session_id: str, model_type: str):
        """Record the start of a training session."""
        self.training_sessions[session_id] = {
            "start_time": time.time(),
            "model_type": model_type,
            "status": "running",
        }

        self.training_sessions_total.labels(
            status="started",
            model_type=model_type,
            constitutional_hash=self.constitutional_hash,
        ).inc()

        self.active_training_sessions.labels(
            constitutional_hash=self.constitutional_hash
        ).set(
            len(
                [s for s in self.training_sessions.values() if s["status"] == "running"]
            )
        )

    def record_training_session_end(
        self, session_id: str, success: bool, final_metrics: dict[str, Any]
    ):
        """Record the end of a training session."""
        if session_id not in self.training_sessions:
            logger.warning(f"Training session {session_id} not found in metrics")
            return

        session = self.training_sessions[session_id]
        duration = time.time() - session["start_time"]
        status = "completed" if success else "failed"

        # Update session status
        session["status"] = status
        session["duration"] = duration
        session["final_metrics"] = final_metrics

        # Record metrics
        self.training_sessions_total.labels(
            status=status,
            model_type=session["model_type"],
            constitutional_hash=self.constitutional_hash,
        ).inc()

        self.training_duration.labels(
            model_type=session["model_type"],
            training_phase="complete",
            constitutional_hash=self.constitutional_hash,
        ).observe(duration)

        # Record compliance metrics if available
        if "constitutional_compliance_score" in final_metrics:
            compliance_score = final_metrics["constitutional_compliance_score"]
            self.compliance_scores.append(compliance_score)

            self.constitutional_compliance_score.labels(
                model_id=session_id,
                evaluation_type="final",
                constitutional_hash=self.constitutional_hash,
            ).observe(compliance_score)

        # Update active sessions count
        self.active_training_sessions.labels(
            constitutional_hash=self.constitutional_hash
        ).set(
            len(
                [s for s in self.training_sessions.values() if s["status"] == "running"]
            )
        )

        # Update compliance rate
        if self.compliance_scores:
            avg_compliance = sum(self.compliance_scores) / len(self.compliance_scores)
            self.constitutional_compliance_rate.labels(
                constitutional_hash=self.constitutional_hash
            ).set(avg_compliance)

    def record_constitutional_violation(
        self, violation_type: str, severity: str, model_id: str
    ):
        """Record a constitutional violation."""
        self.constitutional_violations_total.labels(
            violation_type=violation_type,
            severity=severity,
            model_id=model_id,
            constitutional_hash=self.constitutional_hash,
        ).inc()

    def record_critique_revision_cycle(
        self, model_type: str, cycles: int, success: bool
    ):
        """Record critique-revision cycle metrics."""
        self.critique_revision_cycles.labels(
            model_type=model_type, constitutional_hash=self.constitutional_hash
        ).observe(cycles)

        self.critique_cycles.append(cycles)

        # Update success rate
        successful_cycles = sum(
            1 for c in self.critique_cycles if c <= 3
        )  # Success if ≤3 cycles
        success_rate = (
            successful_cycles / len(self.critique_cycles)
            if self.critique_cycles
            else 0.0
        )

        self.critique_revision_success_rate.labels(
            constitutional_hash=self.constitutional_hash
        ).set(success_rate)

    def record_privacy_metrics(
        self, model_id: str, training_session: str, privacy_metrics: dict[str, float]
    ):
        """Record privacy-related metrics."""

        if "budget_utilization" in privacy_metrics:
            self.privacy_budget_utilization.labels(
                model_id=model_id,
                training_session=training_session,
                constitutional_hash=self.constitutional_hash,
            ).set(privacy_metrics["budget_utilization"])

        if "epsilon" in privacy_metrics:
            self.privacy_epsilon_current.labels(
                model_id=model_id,
                training_session=training_session,
                constitutional_hash=self.constitutional_hash,
            ).set(privacy_metrics["epsilon"])

    def record_privacy_violation(self, violation_type: str, model_id: str):
        """Record a privacy violation."""
        self.privacy_violations_total.labels(
            violation_type=violation_type,
            model_id=model_id,
            constitutional_hash=self.constitutional_hash,
        ).inc()

    def record_policy_evaluation(
        self, evaluation_type: str, duration: float, cache_hit: bool
    ):
        """Record policy evaluation metrics."""
        self.policy_evaluation_duration.labels(
            evaluation_type=evaluation_type,
            cache_hit="true" if cache_hit else "false",
            constitutional_hash=self.constitutional_hash,
        ).observe(duration)

    def update_cache_hit_rate(self, cache_type: str, hit_rate: float):
        """Update cache hit rate metrics."""
        self.cache_hit_rate.labels(
            cache_type=cache_type, constitutional_hash=self.constitutional_hash
        ).set(hit_rate)

    def update_system_health(self, component: str, health_score: float):
        """Update system health metrics."""
        self.system_health_score.labels(
            component=component, constitutional_hash=self.constitutional_hash
        ).set(health_score)

    def record_model_quality(self, model_id: str, accuracy: float, perplexity: float):
        """Record model quality metrics."""
        self.model_accuracy.labels(
            model_id=model_id,
            metric_type="accuracy",
            constitutional_hash=self.constitutional_hash,
        ).set(accuracy)

        self.model_perplexity.labels(
            model_id=model_id,
            dataset="validation",
            constitutional_hash=self.constitutional_hash,
        ).set(perplexity)

    def get_current_metrics(self) -> ConstitutionalTrainingMetrics:
        """Get current metrics summary."""

        total_sessions = len(self.training_sessions)
        successful_sessions = len(
            [s for s in self.training_sessions.values() if s["status"] == "completed"]
        )
        failed_sessions = len(
            [s for s in self.training_sessions.values() if s["status"] == "failed"]
        )
        active_sessions = len(
            [s for s in self.training_sessions.values() if s["status"] == "running"]
        )

        # Calculate averages
        avg_compliance = (
            sum(self.compliance_scores) / len(self.compliance_scores)
            if self.compliance_scores
            else 0.0
        )
        min_compliance = min(self.compliance_scores) if self.compliance_scores else 1.0
        max_compliance = max(self.compliance_scores) if self.compliance_scores else 0.0

        completed_durations = [
            s["duration"] for s in self.training_sessions.values() if "duration" in s
        ]
        avg_duration = (
            sum(completed_durations) / len(completed_durations)
            if completed_durations
            else 0.0
        )

        avg_cycles = (
            sum(self.critique_cycles) / len(self.critique_cycles)
            if self.critique_cycles
            else 0.0
        )

        return ConstitutionalTrainingMetrics(
            training_sessions_total=total_sessions,
            training_sessions_successful=successful_sessions,
            training_sessions_failed=failed_sessions,
            avg_compliance_score=avg_compliance,
            min_compliance_score=min_compliance,
            max_compliance_score=max_compliance,
            avg_training_duration=avg_duration,
            avg_critique_revision_cycles=avg_cycles,
            active_sessions=active_sessions,
        )

    def generate_prometheus_metrics(self) -> str:
        """Generate Prometheus metrics output."""
        return generate_latest(self.registry)

    def get_metrics_content_type(self) -> str:
        """Get content type for Prometheus metrics."""
        return CONTENT_TYPE_LATEST

    def reset_metrics(self):
        """Reset all metrics (use with caution)."""
        logger.warning("Resetting all constitutional training metrics")

        self.training_sessions.clear()
        self.compliance_scores.clear()
        self.training_durations.clear()
        self.critique_cycles.clear()

        # Reset gauges to 0
        self.constitutional_compliance_rate.labels(
            constitutional_hash=self.constitutional_hash
        ).set(0)

        self.active_training_sessions.labels(
            constitutional_hash=self.constitutional_hash
        ).set(0)

        self.critique_revision_success_rate.labels(
            constitutional_hash=self.constitutional_hash
        ).set(0)
