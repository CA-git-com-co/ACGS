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
    "Alert",
    "AlertChannel",
    # Alerts
    "AlertManager",
    "AlertRule",
    "AlertSeverity",
    "BusinessMetrics",
    "CacheHealthCheck",
    "Counter",
    # Dashboard
    "DashboardMetrics",
    "DatabaseHealthCheck",
    "ExternalServiceHealthCheck",
    "Gauge",
    # Health Checks
    "HealthCheck",
    "HealthCheckRegistry",
    "HealthStatus",
    "Histogram",
    # Metrics
    "MetricsCollector",
    "PerformanceMetrics",
    "Span",
    "SpanContext",
    "SystemHealthCheck",
    "SystemMetrics",
    "Timer",
    "TraceLogger",
    # Tracing
    "TracingManager",
    "get_current_span",
    "get_dashboard_data",
    "metric_counter",
    "metric_gauge",
    "metric_histogram",
    "metric_timer",
    "send_alert",
    "trace_operation",
]
