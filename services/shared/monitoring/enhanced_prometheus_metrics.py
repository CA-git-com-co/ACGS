"""
Enhanced Prometheus Metrics Collection for ACGS-1

Provides comprehensive business and technical metrics for all 7 core services:
- Custom business metrics
- Performance metrics
- Security metrics
- Governance workflow metrics
- Resource utilization metrics
"""

import time
from typing import Dict

from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Counter,
    Gauge,
    Histogram,
    generate_latest,
)

# Global metrics registry
REGISTRY = CollectorRegistry()

# Core service metrics
SERVICE_REQUEST_COUNT = Counter(
    "acgs_service_requests_total",
    "Total number of requests per service",
    ["service", "method", "endpoint", "status_code"],
    registry=REGISTRY,
)

SERVICE_REQUEST_DURATION = Histogram(
    "acgs_service_request_duration_seconds",
    "Request duration in seconds",
    ["service", "method", "endpoint"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    registry=REGISTRY,
)

SERVICE_ACTIVE_CONNECTIONS = Gauge(
    "acgs_service_active_connections",
    "Number of active connections per service",
    ["service"],
    registry=REGISTRY,
)

# Business metrics
GOVERNANCE_ACTIONS_TOTAL = Counter(
    "acgs_governance_actions_total",
    "Total governance actions processed",
    ["action_type", "service", "status"],
    registry=REGISTRY,
)

POLICY_ENFORCEMENT_DURATION = Histogram(
    "acgs_policy_enforcement_duration_seconds",
    "Time taken for policy enforcement",
    ["policy_type", "enforcement_result"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0],
    registry=REGISTRY,
)

CONSTITUTIONAL_COMPLIANCE_SCORE = Gauge(
    "acgs_constitutional_compliance_score",
    "Constitutional compliance score (0-1)",
    ["policy_id", "validation_type"],
    registry=REGISTRY,
)

WORKFLOW_EXECUTION_TIME = Histogram(
    "acgs_workflow_execution_seconds",
    "Workflow execution time",
    ["workflow_type", "status"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0],
    registry=REGISTRY,
)

# Security metrics
SECURITY_EVENTS_TOTAL = Counter(
    "acgs_security_events_total",
    "Total security events detected",
    ["event_type", "severity", "service"],
    registry=REGISTRY,
)

AUTHENTICATION_ATTEMPTS = Counter(
    "acgs_authentication_attempts_total",
    "Authentication attempts",
    ["method", "result", "user_type"],
    registry=REGISTRY,
)

RATE_LIMIT_VIOLATIONS = Counter(
    "acgs_rate_limit_violations_total",
    "Rate limit violations",
    ["service", "client_ip", "endpoint"],
    registry=REGISTRY,
)

# Database metrics
DATABASE_CONNECTIONS_ACTIVE = Gauge(
    "acgs_database_connections_active",
    "Active database connections",
    ["database", "service"],
    registry=REGISTRY,
)

DATABASE_QUERY_DURATION = Histogram(
    "acgs_database_query_duration_seconds",
    "Database query execution time",
    ["database", "operation", "table"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.0],
    registry=REGISTRY,
)

DATABASE_CONNECTION_ERRORS = Counter(
    "acgs_database_connection_errors_total",
    "Database connection errors",
    ["database", "error_type"],
    registry=REGISTRY,
)

# Cache metrics
CACHE_OPERATIONS_TOTAL = Counter(
    "acgs_cache_operations_total",
    "Total cache operations",
    ["operation", "result", "cache_type"],
    registry=REGISTRY,
)

CACHE_HIT_RATIO = Gauge(
    "acgs_cache_hit_ratio",
    "Cache hit ratio (0-1)",
    ["cache_type", "service"],
    registry=REGISTRY,
)

CACHE_RESPONSE_TIME = Histogram(
    "acgs_cache_response_time_seconds",
    "Cache operation response time",
    ["operation", "cache_type"],
    buckets=[0.0001, 0.0005, 0.001, 0.005, 0.01, 0.025, 0.05, 0.1],
    registry=REGISTRY,
)

# Resource utilization metrics
CPU_USAGE_PERCENT = Gauge(
    "acgs_cpu_usage_percent",
    "CPU usage percentage",
    ["service", "instance"],
    registry=REGISTRY,
)

MEMORY_USAGE_BYTES = Gauge(
    "acgs_memory_usage_bytes",
    "Memory usage in bytes",
    ["service", "instance", "type"],
    registry=REGISTRY,
)

DISK_USAGE_BYTES = Gauge(
    "acgs_disk_usage_bytes",
    "Disk usage in bytes",
    ["service", "instance", "mount_point"],
    registry=REGISTRY,
)

# Blockchain metrics (for Quantumagi integration)
BLOCKCHAIN_TRANSACTIONS_TOTAL = Counter(
    "acgs_blockchain_transactions_total",
    "Total blockchain transactions",
    ["transaction_type", "status", "program"],
    registry=REGISTRY,
)

BLOCKCHAIN_TRANSACTION_COST = Histogram(
    "acgs_blockchain_transaction_cost_sol",
    "Blockchain transaction cost in SOL",
    ["transaction_type", "program"],
    buckets=[0.0001, 0.0005, 0.001, 0.005, 0.01, 0.025, 0.05, 0.1],
    registry=REGISTRY,
)

SOLANA_ACCOUNT_BALANCE = Gauge(
    "acgs_solana_account_balance_sol",
    "Solana account balance in SOL",
    ["account_type", "program"],
    registry=REGISTRY,
)

# Service health metrics
SERVICE_HEALTH_STATUS = Gauge(
    "acgs_service_health_status",
    "Service health status (1=healthy, 0=unhealthy)",
    ["service", "component"],
    registry=REGISTRY,
)

SERVICE_UPTIME_SECONDS = Gauge(
    "acgs_service_uptime_seconds",
    "Service uptime in seconds",
    ["service"],
    registry=REGISTRY,
)

# AI/LLM metrics
LLM_REQUEST_DURATION = Histogram(
    "acgs_llm_request_duration_seconds",
    "LLM request processing time",
    ["model", "operation", "service"],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
    registry=REGISTRY,
)

LLM_TOKEN_USAGE = Counter(
    "acgs_llm_tokens_total",
    "Total LLM tokens used",
    ["model", "token_type", "service"],
    registry=REGISTRY,
)

LLM_RESPONSE_QUALITY_SCORE = Gauge(
    "acgs_llm_response_quality_score",
    "LLM response quality score (0-1)",
    ["model", "operation"],
    registry=REGISTRY,
)


class EnhancedMetricsCollector:
    """Enhanced metrics collector for ACGS-1 services."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.start_time = time.time()

    def record_request(
        self, method: str, endpoint: str, status_code: int, duration: float
    ):
        """Record HTTP request metrics."""
        SERVICE_REQUEST_COUNT.labels(
            service=self.service_name,
            method=method,
            endpoint=endpoint,
            status_code=status_code,
        ).inc()

        SERVICE_REQUEST_DURATION.labels(
            service=self.service_name, method=method, endpoint=endpoint
        ).observe(duration)

    def record_governance_action(self, action_type: str, status: str):
        """Record governance action metrics."""
        GOVERNANCE_ACTIONS_TOTAL.labels(
            action_type=action_type, service=self.service_name, status=status
        ).inc()

    def record_policy_enforcement(
        self, policy_type: str, enforcement_result: str, duration: float
    ):
        """Record policy enforcement metrics."""
        POLICY_ENFORCEMENT_DURATION.labels(
            policy_type=policy_type, enforcement_result=enforcement_result
        ).observe(duration)

    def update_compliance_score(
        self, policy_id: str, validation_type: str, score: float
    ):
        """Update constitutional compliance score."""
        CONSTITUTIONAL_COMPLIANCE_SCORE.labels(
            policy_id=policy_id, validation_type=validation_type
        ).set(score)

    def record_workflow_execution(
        self, workflow_type: str, status: str, duration: float
    ):
        """Record workflow execution metrics."""
        WORKFLOW_EXECUTION_TIME.labels(
            workflow_type=workflow_type, status=status
        ).observe(duration)

    def record_security_event(self, event_type: str, severity: str):
        """Record security event."""
        SECURITY_EVENTS_TOTAL.labels(
            event_type=event_type, severity=severity, service=self.service_name
        ).inc()

    def record_authentication_attempt(self, method: str, result: str, user_type: str):
        """Record authentication attempt."""
        AUTHENTICATION_ATTEMPTS.labels(
            method=method, result=result, user_type=user_type
        ).inc()

    def record_database_operation(
        self, database: str, operation: str, table: str, duration: float
    ):
        """Record database operation metrics."""
        DATABASE_QUERY_DURATION.labels(
            database=database, operation=operation, table=table
        ).observe(duration)

    def update_database_connections(self, database: str, active_connections: int):
        """Update active database connections."""
        DATABASE_CONNECTIONS_ACTIVE.labels(
            database=database, service=self.service_name
        ).set(active_connections)

    def record_cache_operation(
        self, operation: str, result: str, cache_type: str, duration: float
    ):
        """Record cache operation metrics."""
        CACHE_OPERATIONS_TOTAL.labels(
            operation=operation, result=result, cache_type=cache_type
        ).inc()

        CACHE_RESPONSE_TIME.labels(operation=operation, cache_type=cache_type).observe(
            duration
        )

    def update_cache_hit_ratio(self, cache_type: str, hit_ratio: float):
        """Update cache hit ratio."""
        CACHE_HIT_RATIO.labels(cache_type=cache_type, service=self.service_name).set(
            hit_ratio
        )

    def update_resource_usage(
        self, cpu_percent: float, memory_bytes: int, disk_bytes: int
    ):
        """Update resource usage metrics."""
        CPU_USAGE_PERCENT.labels(service=self.service_name, instance="default").set(
            cpu_percent
        )

        MEMORY_USAGE_BYTES.labels(
            service=self.service_name, instance="default", type="used"
        ).set(memory_bytes)

        DISK_USAGE_BYTES.labels(
            service=self.service_name, instance="default", mount_point="/"
        ).set(disk_bytes)

    def record_blockchain_transaction(
        self, transaction_type: str, status: str, program: str, cost_sol: float
    ):
        """Record blockchain transaction metrics."""
        BLOCKCHAIN_TRANSACTIONS_TOTAL.labels(
            transaction_type=transaction_type, status=status, program=program
        ).inc()

        BLOCKCHAIN_TRANSACTION_COST.labels(
            transaction_type=transaction_type, program=program
        ).observe(cost_sol)

    def update_service_health(self, component: str, is_healthy: bool):
        """Update service health status."""
        SERVICE_HEALTH_STATUS.labels(
            service=self.service_name, component=component
        ).set(1 if is_healthy else 0)

    def update_uptime(self):
        """Update service uptime."""
        uptime = time.time() - self.start_time
        SERVICE_UPTIME_SECONDS.labels(service=self.service_name).set(uptime)

    def record_llm_request(
        self,
        model: str,
        operation: str,
        duration: float,
        tokens_used: int,
        quality_score: float,
    ):
        """Record LLM request metrics."""
        LLM_REQUEST_DURATION.labels(
            model=model, operation=operation, service=self.service_name
        ).observe(duration)

        LLM_TOKEN_USAGE.labels(
            model=model, token_type="total", service=self.service_name
        ).inc(tokens_used)

        LLM_RESPONSE_QUALITY_SCORE.labels(model=model, operation=operation).set(
            quality_score
        )

    def get_metrics(self) -> str:
        """Get all metrics in Prometheus format."""
        return generate_latest(REGISTRY).decode("utf-8")


# Global metrics collector instances
_metrics_collectors: Dict[str, EnhancedMetricsCollector] = {}


def get_metrics_collector(service_name: str) -> EnhancedMetricsCollector:
    """Get or create metrics collector for service."""
    if service_name not in _metrics_collectors:
        _metrics_collectors[service_name] = EnhancedMetricsCollector(service_name)
    return _metrics_collectors[service_name]


def get_all_metrics() -> str:
    """Get all metrics from all services."""
    return generate_latest(REGISTRY).decode("utf-8")


def get_metrics_content_type() -> str:
    """Get Prometheus metrics content type."""
    return CONTENT_TYPE_LATEST


# Distributed tracing integration
class TracingIntegration:
    """Integration with OpenTelemetry for distributed tracing."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.tracer = None
        self._initialize_tracing()

    def _initialize_tracing(self):
        """Initialize OpenTelemetry tracing."""
        try:
            from opentelemetry import trace
            from opentelemetry.exporter.jaeger.thrift import JaegerExporter
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
            from opentelemetry.instrumentation.requests import RequestsInstrumentor
            from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor

            # Set up tracer provider
            trace.set_tracer_provider(TracerProvider())

            # Configure Jaeger exporter
            jaeger_exporter = JaegerExporter(
                agent_host_name="localhost",
                agent_port=6831,
            )

            # Add span processor
            span_processor = BatchSpanProcessor(jaeger_exporter)
            trace.get_tracer_provider().add_span_processor(span_processor)

            # Get tracer
            self.tracer = trace.get_tracer(self.service_name)

            # Auto-instrument common libraries
            FastAPIInstrumentor.instrument()
            RequestsInstrumentor.instrument()
            SQLAlchemyInstrumentor.instrument()

        except ImportError:
            # OpenTelemetry not available
            pass

    def start_span(self, name: str, attributes: dict = None):
        """Start a new span."""
        if self.tracer:
            return self.tracer.start_span(name, attributes=attributes or {})
        return None

    def add_span_attribute(self, span, key: str, value):
        """Add attribute to span."""
        if span:
            span.set_attribute(key, value)

    def record_exception(self, span, exception: Exception):
        """Record exception in span."""
        if span:
            span.record_exception(exception)
            span.set_status(trace.Status(trace.StatusCode.ERROR, str(exception)))
