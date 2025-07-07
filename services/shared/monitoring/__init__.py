"""
Comprehensive Monitoring & Observability for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Production-grade monitoring, metrics, tracing, and health checks.
"""

from .alerts import (
    Alert,
    AlertChannel,
    AlertManager,
    AlertRule,
    AlertSeverity,
    send_alert,
)
from .dashboard import (
    BusinessMetrics,
    DashboardMetrics,
    PerformanceMetrics,
    SystemMetrics,
    get_dashboard_data,
)
from .health_checks import (
    CacheHealthCheck,
    DatabaseHealthCheck,
    ExternalServiceHealthCheck,
    HealthCheck,
    HealthCheckRegistry,
    HealthStatus,
    SystemHealthCheck,
)
from .metrics import (
    Counter,
    Gauge,
    Histogram,
    MetricsCollector,
    Timer,
    metric_counter,
    metric_gauge,
    metric_histogram,
    metric_timer,
)
from .tracing import (
    Span,
    SpanContext,
    TraceLogger,
    TracingManager,
    get_current_span,
    trace_operation,
)

__all__ = [
    # Metrics
    "MetricsCollector",
    "Counter",
    "Gauge",
    "Histogram",
    "Timer",
    "metric_counter",
    "metric_gauge",
    "metric_histogram",
    "metric_timer",
    # Health Checks
    "HealthCheck",
    "HealthStatus",
    "SystemHealthCheck",
    "DatabaseHealthCheck",
    "CacheHealthCheck",
    "ExternalServiceHealthCheck",
    "HealthCheckRegistry",
    # Tracing
    "TracingManager",
    "Span",
    "SpanContext",
    "TraceLogger",
    "trace_operation",
    "get_current_span",
    # Alerts
    "AlertManager",
    "Alert",
    "AlertSeverity",
    "AlertChannel",
    "AlertRule",
    "send_alert",
    # Dashboard
    "DashboardMetrics",
    "SystemMetrics",
    "PerformanceMetrics",
    "BusinessMetrics",
    "get_dashboard_data",
]
