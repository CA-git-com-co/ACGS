"""
Prometheus metrics collection for DGM Service.

Implements comprehensive metrics for DGM operations, performance,
constitutional compliance, and system health.
"""

import time
from enum import Enum

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)

from ..config import settings


class MetricType(Enum):
    """Types of metrics."""

    COUNTER = "counter"
    HISTOGRAM = "histogram"
    GAUGE = "gauge"
    SUMMARY = "summary"
    INFO = "info"


class DGMMetrics:
    """
    DGM-specific Prometheus metrics.

    Provides comprehensive metrics for monitoring DGM service
    operations, performance, and constitutional compliance.
    """

    def __init__(self, registry: CollectorRegistry | None = None):
        self.registry = registry or CollectorRegistry()
        self._initialize_metrics()

    def _initialize_metrics(self):
        """Initialize all DGM metrics."""

        # Service Health Metrics
        self.service_info = Info(
            "dgm_service_info", "DGM Service information", registry=self.registry
        )

        self.service_up = Gauge(
            "dgm_service_up", "DGM Service availability", registry=self.registry
        )

        # Request Metrics
        self.http_requests_total = Counter(
            "dgm_http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status_code"],
            registry=self.registry,
        )

        self.http_request_duration = Histogram(
            "dgm_http_request_duration_seconds",
            "HTTP request duration",
            ["method", "endpoint"],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
            registry=self.registry,
        )

        # Improvement Metrics
        self.improvements_total = Counter(
            "dgm_improvements_total",
            "Total number of improvements",
            ["status", "priority"],
            registry=self.registry,
        )

        self.improvement_duration = Histogram(
            "dgm_improvement_duration_seconds",
            "Improvement execution duration",
            ["status", "strategy"],
            buckets=[60, 300, 900, 1800, 3600, 7200, 14400],
            registry=self.registry,
        )

        self.active_improvements = Gauge(
            "dgm_active_improvements",
            "Number of currently active improvements",
            registry=self.registry,
        )

        self.improvement_success_rate = Gauge(
            "dgm_improvement_success_rate",
            "Success rate of improvements (0-1)",
            registry=self.registry,
        )

        # Constitutional Compliance Metrics
        self.constitutional_validations_total = Counter(
            "dgm_constitutional_validations_total",
            "Total constitutional validations",
            ["result", "principle"],
            registry=self.registry,
        )

        self.constitutional_compliance_score = Histogram(
            "dgm_constitutional_compliance_score",
            "Constitutional compliance scores",
            buckets=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
            registry=self.registry,
        )

        self.constitutional_violations_total = Counter(
            "dgm_constitutional_violations_total",
            "Total constitutional violations",
            ["principle", "severity"],
            registry=self.registry,
        )

        self.average_compliance_score = Gauge(
            "dgm_average_compliance_score",
            "Average constitutional compliance score",
            registry=self.registry,
        )

        # Performance Metrics
        self.performance_score = Gauge(
            "dgm_performance_score",
            "Current system performance score",
            ["service"],
            registry=self.registry,
        )

        self.performance_improvement = Histogram(
            "dgm_performance_improvement_percent",
            "Performance improvement percentage",
            ["service", "metric"],
            buckets=[-50, -25, -10, -5, 0, 5, 10, 25, 50, 100],
            registry=self.registry,
        )

        # Bandit Algorithm Metrics
        self.bandit_arm_pulls = Counter(
            "dgm_bandit_arm_pulls_total",
            "Total pulls for bandit arms",
            ["algorithm", "arm_id"],
            registry=self.registry,
        )

        self.bandit_arm_reward = Histogram(
            "dgm_bandit_arm_reward",
            "Rewards for bandit arms",
            ["algorithm", "arm_id"],
            buckets=[-1.0, -0.5, -0.1, 0, 0.1, 0.5, 1.0],
            registry=self.registry,
        )

        self.bandit_exploration_rate = Gauge(
            "dgm_bandit_exploration_rate",
            "Current exploration rate",
            ["algorithm"],
            registry=self.registry,
        )

        # Archive Metrics
        self.archive_entries_total = Gauge(
            "dgm_archive_entries_total",
            "Total entries in DGM archive",
            registry=self.registry,
        )

        self.archive_size_bytes = Gauge(
            "dgm_archive_size_bytes",
            "Size of DGM archive in bytes",
            registry=self.registry,
        )

        # Database Metrics
        self.database_connections = Gauge(
            "dgm_database_connections",
            "Number of database connections",
            ["state"],
            registry=self.registry,
        )

        self.database_query_duration = Histogram(
            "dgm_database_query_duration_seconds",
            "Database query duration",
            ["operation"],
            buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
            registry=self.registry,
        )

        # Cache Metrics
        self.cache_operations_total = Counter(
            "dgm_cache_operations_total",
            "Total cache operations",
            ["operation", "result"],
            registry=self.registry,
        )

        self.cache_hit_rate = Gauge(
            "dgm_cache_hit_rate", "Cache hit rate (0-1)", registry=self.registry
        )

        # Foundation Model Metrics
        self.model_requests_total = Counter(
            "dgm_model_requests_total",
            "Total foundation model requests",
            ["provider", "model", "status"],
            registry=self.registry,
        )

        self.model_request_duration = Histogram(
            "dgm_model_request_duration_seconds",
            "Foundation model request duration",
            ["provider", "model"],
            buckets=[1, 5, 10, 30, 60, 120, 300],
            registry=self.registry,
        )

        self.model_tokens_total = Counter(
            "dgm_model_tokens_total",
            "Total tokens used",
            ["provider", "model", "type"],
            registry=self.registry,
        )

        self.model_cost_total = Counter(
            "dgm_model_cost_total",
            "Total model usage cost",
            ["provider", "model"],
            registry=self.registry,
        )

        # Error Metrics
        self.errors_total = Counter(
            "dgm_errors_total",
            "Total errors",
            ["component", "error_type"],
            registry=self.registry,
        )

        # Workflow Metrics
        self.workflows_total = Counter(
            "dgm_workflows_total",
            "Total workflows",
            ["type", "status"],
            registry=self.registry,
        )

        self.workflow_duration = Histogram(
            "dgm_workflow_duration_seconds",
            "Workflow execution duration",
            ["type", "status"],
            buckets=[60, 300, 900, 1800, 3600, 7200],
            registry=self.registry,
        )

        # Security Metrics
        self.auth_attempts_total = Counter(
            "dgm_auth_attempts_total",
            "Total authentication attempts",
            ["result"],
            registry=self.registry,
        )

        self.permission_checks_total = Counter(
            "dgm_permission_checks_total",
            "Total permission checks",
            ["permission", "result"],
            registry=self.registry,
        )

        # Set service info
        self.service_info.info(
            {
                "version": "1.0.0",
                "service": "dgm-service",
                "environment": settings.ENVIRONMENT,
            }
        )

        # Set initial values
        self.service_up.set(1)


class MetricsCollector:
    """
    Metrics collector for DGM Service.

    Provides methods to record metrics and generate Prometheus
    exposition format output.
    """

    def __init__(self):
        self.registry = CollectorRegistry()
        self.dgm_metrics = DGMMetrics(self.registry)
        self._start_time = time.time()

    def record_http_request(
        self, method: str, endpoint: str, status_code: int, duration: float
    ):
        """Record HTTP request metrics."""
        self.dgm_metrics.http_requests_total.labels(
            method=method, endpoint=endpoint, status_code=str(status_code)
        ).inc()

        self.dgm_metrics.http_request_duration.labels(
            method=method, endpoint=endpoint
        ).observe(duration)

    def record_improvement(
        self,
        status: str,
        priority: str,
        duration: float | None = None,
        strategy: str | None = None,
    ):
        """Record improvement metrics."""
        self.dgm_metrics.improvements_total.labels(
            status=status, priority=priority
        ).inc()

        if duration is not None and strategy:
            self.dgm_metrics.improvement_duration.labels(
                status=status, strategy=strategy
            ).observe(duration)

    def update_active_improvements(self, count: int):
        """Update active improvements count."""
        self.dgm_metrics.active_improvements.set(count)

    def update_improvement_success_rate(self, rate: float):
        """Update improvement success rate."""
        self.dgm_metrics.improvement_success_rate.set(rate)

    def record_constitutional_validation(
        self, result: str, principle: str, score: float, violations: list[str]
    ):
        """Record constitutional validation metrics."""
        self.dgm_metrics.constitutional_validations_total.labels(
            result=result, principle=principle
        ).inc()

        self.dgm_metrics.constitutional_compliance_score.observe(score)

        for violation in violations:
            self.dgm_metrics.constitutional_violations_total.labels(
                principle=principle,
                severity="high",  # Could be parameterized
            ).inc()

    def update_average_compliance_score(self, score: float):
        """Update average compliance score."""
        self.dgm_metrics.average_compliance_score.set(score)

    def update_performance_score(self, service: str, score: float):
        """Update performance score."""
        self.dgm_metrics.performance_score.labels(service=service).set(score)

    def record_performance_improvement(
        self, service: str, metric: str, improvement_percent: float
    ):
        """Record performance improvement."""
        self.dgm_metrics.performance_improvement.labels(
            service=service, metric=metric
        ).observe(improvement_percent)

    def record_bandit_operation(
        self, algorithm: str, arm_id: str, reward: float, exploration_rate: float
    ):
        """Record bandit algorithm metrics."""
        self.dgm_metrics.bandit_arm_pulls.labels(
            algorithm=algorithm, arm_id=arm_id
        ).inc()

        self.dgm_metrics.bandit_arm_reward.labels(
            algorithm=algorithm, arm_id=arm_id
        ).observe(reward)

        self.dgm_metrics.bandit_exploration_rate.labels(algorithm=algorithm).set(
            exploration_rate
        )

    def record_model_request(
        self,
        provider: str,
        model: str,
        status: str,
        duration: float,
        input_tokens: int,
        output_tokens: int,
        cost: float,
    ):
        """Record foundation model request metrics."""
        self.dgm_metrics.model_requests_total.labels(
            provider=provider, model=model, status=status
        ).inc()

        self.dgm_metrics.model_request_duration.labels(
            provider=provider, model=model
        ).observe(duration)

        self.dgm_metrics.model_tokens_total.labels(
            provider=provider, model=model, type="input"
        ).inc(input_tokens)

        self.dgm_metrics.model_tokens_total.labels(
            provider=provider, model=model, type="output"
        ).inc(output_tokens)

        self.dgm_metrics.model_cost_total.labels(provider=provider, model=model).inc(
            cost
        )

    def record_error(self, component: str, error_type: str):
        """Record error metrics."""
        self.dgm_metrics.errors_total.labels(
            component=component, error_type=error_type
        ).inc()

    def record_auth_attempt(self, result: str):
        """Record authentication attempt."""
        self.dgm_metrics.auth_attempts_total.labels(result=result).inc()

    def record_permission_check(self, permission: str, result: str):
        """Record permission check."""
        self.dgm_metrics.permission_checks_total.labels(
            permission=permission, result=result
        ).inc()

    def get_metrics(self) -> str:
        """Get metrics in Prometheus exposition format."""
        return generate_latest(self.registry).decode("utf-8")

    def get_content_type(self) -> str:
        """Get content type for metrics endpoint."""
        return CONTENT_TYPE_LATEST


# Global metrics collector instance
metrics_collector = MetricsCollector()
