"""
Observability Framework for ACGS-1 Self-Evolving AI Architecture Foundation.

This module implements comprehensive observability with OpenTelemetry distributed
tracing, metrics collection, and monitoring for the self-evolving AI architecture.

Key Features:
- OpenTelemetry distributed tracing
- Metrics collection and aggregation
- Performance monitoring
- Evolution workflow tracking
- Integration with ACGS-1 monitoring infrastructure
- Real-time alerting and notifications
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

try:
    from opentelemetry import metrics, trace
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import (
        OTLPMetricExporter,
    )
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.metrics import MeterProvider
    from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
    from opentelemetry.sdk.resources import Resource
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.semconv.resource import ResourceAttributes

    OPENTELEMETRY_AVAILABLE = True
except ImportError:
    OPENTELEMETRY_AVAILABLE = False
    metrics = None
    trace = None

logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Metric type enumeration."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"


class AlertLevel(Enum):
    """Alert level enumeration."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class PerformanceMetric:
    """Performance metric data structure."""

    metric_name: str
    metric_type: MetricType
    value: float
    unit: str = ""
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TraceSpan:
    """Trace span data structure."""

    span_id: str
    trace_id: str
    operation_name: str
    start_time: datetime
    end_time: datetime | None = None
    duration_ms: float | None = None
    status: str = "ok"
    tags: dict[str, str] = field(default_factory=dict)
    logs: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class Alert:
    """Alert data structure."""

    alert_id: str
    alert_level: AlertLevel
    title: str
    description: str
    source: str
    metric_name: str | None = None
    threshold_value: float | None = None
    current_value: float | None = None
    triggered_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    resolved_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ObservabilityFramework:
    """
    Comprehensive observability framework for self-evolving AI architecture.

    This framework provides distributed tracing, metrics collection, and
    monitoring capabilities with OpenTelemetry integration.
    """

    def __init__(self, settings):
        self.settings = settings

        # OpenTelemetry configuration
        self.otlp_endpoint = settings.OTLP_ENDPOINT
        self.otlp_version = settings.OTLP_VERSION
        self.tracing_enabled = settings.TRACING_ENABLED
        self.metrics_enabled = settings.METRICS_ENABLED

        # Service information
        self.service_name = settings.SERVICE_NAME
        self.service_version = settings.VERSION
        self.environment = settings.ENVIRONMENT

        # Observability state
        self.active_spans: dict[str, TraceSpan] = {}
        self.metrics_buffer: list[PerformanceMetric] = []
        self.active_alerts: dict[str, Alert] = {}
        self.observability_metrics: dict[str, Any] = {
            "spans_created": 0,
            "spans_completed": 0,
            "metrics_collected": 0,
            "alerts_triggered": 0,
            "alerts_resolved": 0,
        }

        # OpenTelemetry components
        self.tracer_provider: TracerProvider | None = None
        self.meter_provider: MeterProvider | None = None
        self.tracer = None
        self.meter = None

        # Performance targets
        self.performance_targets = {
            "response_time_ms": 500,
            "availability_percent": 99.9,
            "error_rate_percent": 1.0,
            "evolution_cycle_minutes": 10,
        }

        logger.info("Observability framework initialized with OpenTelemetry")

    async def initialize(self):
        """Initialize the observability framework."""
        try:
            if not OPENTELEMETRY_AVAILABLE:
                logger.warning(
                    "OpenTelemetry not available - observability features limited"
                )
                return

            # Initialize OpenTelemetry components
            await self._initialize_opentelemetry()

            # Start metrics collection
            asyncio.create_task(self._collect_metrics_periodically())

            # Start alert monitoring
            asyncio.create_task(self._monitor_alerts())

            logger.info("✅ Observability framework initialization complete")

        except Exception as e:
            logger.error(f"❌ Observability framework initialization failed: {e}")
            raise

    async def start_span(self, operation_name: str, tags: dict[str, str] = None) -> str:
        """
        Start a new trace span.

        Args:
            operation_name: Name of the operation being traced
            tags: Optional tags for the span

        Returns:
            Span ID
        """
        try:
            span_id = f"span_{int(time.time())}_{len(self.active_spans)}"
            trace_id = f"trace_{int(time.time())}"

            span = TraceSpan(
                span_id=span_id,
                trace_id=trace_id,
                operation_name=operation_name,
                start_time=datetime.now(UTC),
                tags=tags or {},
            )

            self.active_spans[span_id] = span

            # Create OpenTelemetry span if available
            if self.tracer:
                otel_span = self.tracer.start_span(operation_name)
                if tags:
                    for key, value in tags.items():
                        otel_span.set_attribute(key, value)
                span.metadata["otel_span"] = otel_span

            # Update metrics
            self.observability_metrics["spans_created"] += 1

            logger.debug(f"Span started: {operation_name} ({span_id})")

            return span_id

        except Exception as e:
            logger.error(f"Failed to start span: {e}")
            return ""

    async def finish_span(
        self, span_id: str, status: str = "ok", logs: list[dict[str, Any]] = None
    ):
        """
        Finish a trace span.

        Args:
            span_id: Span identifier
            status: Span status (ok, error, timeout)
            logs: Optional log entries for the span
        """
        try:
            if span_id not in self.active_spans:
                logger.warning(f"Span not found: {span_id}")
                return

            span = self.active_spans[span_id]
            span.end_time = datetime.now(UTC)
            span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
            span.status = status
            span.logs = logs or []

            # Finish OpenTelemetry span if available
            if "otel_span" in span.metadata:
                otel_span = span.metadata["otel_span"]
                if status == "error":
                    otel_span.set_status(trace.Status(trace.StatusCode.ERROR))
                otel_span.end()

            # Remove from active spans
            del self.active_spans[span_id]

            # Update metrics
            self.observability_metrics["spans_completed"] += 1

            logger.debug(
                f"Span finished: {span.operation_name} ({span_id}) - {span.duration_ms:.2f}ms"
            )

        except Exception as e:
            logger.error(f"Failed to finish span: {e}")

    async def record_metric(
        self,
        metric_name: str,
        value: float,
        metric_type: MetricType = MetricType.GAUGE,
        unit: str = "",
        labels: dict[str, str] = None,
    ):
        """
        Record a performance metric.

        Args:
            metric_name: Name of the metric
            value: Metric value
            metric_type: Type of metric
            unit: Unit of measurement
            labels: Optional labels for the metric
        """
        try:
            metric = PerformanceMetric(
                metric_name=metric_name,
                metric_type=metric_type,
                value=value,
                unit=unit,
                labels=labels or {},
            )

            self.metrics_buffer.append(metric)

            # Record with OpenTelemetry if available
            if self.meter:
                if metric_type == MetricType.COUNTER:
                    counter = self.meter.create_counter(metric_name, unit=unit)
                    counter.add(value, labels or {})
                elif metric_type == MetricType.GAUGE:
                    gauge = self.meter.create_gauge(metric_name, unit=unit)
                    gauge.set(value, labels or {})
                elif metric_type == MetricType.HISTOGRAM:
                    histogram = self.meter.create_histogram(metric_name, unit=unit)
                    histogram.record(value, labels or {})

            # Update metrics
            self.observability_metrics["metrics_collected"] += 1

            # Check for alert conditions
            await self._check_metric_alerts(metric)

            logger.debug(f"Metric recorded: {metric_name} = {value} {unit}")

        except Exception as e:
            logger.error(f"Failed to record metric: {e}")

    async def trigger_alert(
        self,
        title: str,
        description: str,
        alert_level: AlertLevel = AlertLevel.WARNING,
        source: str = "observability_framework",
        metric_name: str = None,
        threshold_value: float = None,
        current_value: float = None,
    ) -> str:
        """
        Trigger an alert.

        Args:
            title: Alert title
            description: Alert description
            alert_level: Severity level
            source: Source of the alert
            metric_name: Related metric name
            threshold_value: Threshold that was exceeded
            current_value: Current metric value

        Returns:
            Alert ID
        """
        try:
            alert_id = f"alert_{int(time.time())}_{len(self.active_alerts)}"

            alert = Alert(
                alert_id=alert_id,
                alert_level=alert_level,
                title=title,
                description=description,
                source=source,
                metric_name=metric_name,
                threshold_value=threshold_value,
                current_value=current_value,
            )

            self.active_alerts[alert_id] = alert

            # Update metrics
            self.observability_metrics["alerts_triggered"] += 1

            logger.warning(
                f"Alert triggered: {title} ({alert_level.value}) - {description}"
            )

            return alert_id

        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
            return ""

    async def resolve_alert(self, alert_id: str):
        """
        Resolve an active alert.

        Args:
            alert_id: Alert identifier
        """
        try:
            if alert_id not in self.active_alerts:
                logger.warning(f"Alert not found: {alert_id}")
                return

            alert = self.active_alerts[alert_id]
            alert.resolved_at = datetime.now(UTC)

            # Remove from active alerts
            del self.active_alerts[alert_id]

            # Update metrics
            self.observability_metrics["alerts_resolved"] += 1

            logger.info(f"Alert resolved: {alert.title} ({alert_id})")

        except Exception as e:
            logger.error(f"Failed to resolve alert: {e}")

    async def record_evolution_completion(self, evolution_result):
        """Record completion of an evolution cycle."""
        try:
            await self.record_metric(
                "evolution_completion_total",
                1,
                MetricType.COUNTER,
                labels={
                    "evolution_id": evolution_result.evolution_id,
                    "status": evolution_result.status.value,
                    "success": str(evolution_result.success),
                },
            )

            if evolution_result.performance_metrics:
                duration = evolution_result.performance_metrics.get(
                    "duration_minutes", 0
                )
                await self.record_metric(
                    "evolution_duration_minutes",
                    duration,
                    MetricType.HISTOGRAM,
                    unit="minutes",
                    labels={"evolution_id": evolution_result.evolution_id},
                )

            logger.info(
                f"Evolution completion recorded: {evolution_result.evolution_id}"
            )

        except Exception as e:
            logger.error(f"Failed to record evolution completion: {e}")

    async def record_evolution_failure(self, evolution_result):
        """Record failure of an evolution cycle."""
        try:
            await self.record_metric(
                "evolution_failure_total",
                1,
                MetricType.COUNTER,
                labels={
                    "evolution_id": evolution_result.evolution_id,
                    "error_type": "evolution_failure",
                },
            )

            # Trigger alert for evolution failure
            await self.trigger_alert(
                "Evolution Cycle Failed",
                f"Evolution {evolution_result.evolution_id} failed: {evolution_result.error_message}",
                AlertLevel.ERROR,
                "evolution_engine",
                "evolution_failure_total",
            )

            logger.error(f"Evolution failure recorded: {evolution_result.evolution_id}")

        except Exception as e:
            logger.error(f"Failed to record evolution failure: {e}")

    async def record_evolution_warning(
        self, evolution_id: str, warning_type: str, details: Any
    ):
        """Record a warning for an evolution cycle."""
        try:
            await self.record_metric(
                "evolution_warning_total",
                1,
                MetricType.COUNTER,
                labels={
                    "evolution_id": evolution_id,
                    "warning_type": warning_type,
                },
            )

            # Trigger alert for evolution warning
            await self.trigger_alert(
                "Evolution Cycle Warning",
                f"Evolution {evolution_id} warning: {warning_type} - {details}",
                AlertLevel.WARNING,
                "evolution_engine",
                "evolution_warning_total",
            )

            logger.warning(
                f"Evolution warning recorded: {evolution_id} - {warning_type}"
            )

        except Exception as e:
            logger.error(f"Failed to record evolution warning: {e}")

    # Private helper methods
    async def _initialize_opentelemetry(self):
        """Initialize OpenTelemetry components."""
        try:
            # Create resource
            resource = Resource.create(
                {
                    ResourceAttributes.SERVICE_NAME: self.service_name,
                    ResourceAttributes.SERVICE_VERSION: self.service_version,
                    ResourceAttributes.DEPLOYMENT_ENVIRONMENT: self.environment,
                }
            )

            # Initialize tracing
            if self.tracing_enabled:
                self.tracer_provider = TracerProvider(resource=resource)
                trace.set_tracer_provider(self.tracer_provider)

                # Add OTLP exporter
                otlp_span_exporter = OTLPSpanExporter(endpoint=self.otlp_endpoint)
                self.tracer_provider.add_span_processor(
                    BatchSpanProcessor(otlp_span_exporter)
                )

                self.tracer = trace.get_tracer(self.service_name, self.service_version)
                logger.info("OpenTelemetry tracing initialized")

            # Initialize metrics
            if self.metrics_enabled:
                otlp_metric_exporter = OTLPMetricExporter(endpoint=self.otlp_endpoint)
                metric_reader = PeriodicExportingMetricReader(otlp_metric_exporter)

                self.meter_provider = MeterProvider(
                    resource=resource,
                    metric_readers=[metric_reader],
                )
                metrics.set_meter_provider(self.meter_provider)

                self.meter = metrics.get_meter(self.service_name, self.service_version)
                logger.info("OpenTelemetry metrics initialized")

        except Exception as e:
            logger.error(f"OpenTelemetry initialization failed: {e}")
            raise

    async def _collect_metrics_periodically(self):
        """Background task to collect system metrics."""
        while True:
            try:
                # Collect system performance metrics
                await self._collect_system_metrics()

                # Collect evolution metrics
                await self._collect_evolution_metrics()

                # Collect security metrics
                await self._collect_security_metrics()

                # Clean up old metrics
                await self._cleanup_old_metrics()

                # Sleep for collection interval
                await asyncio.sleep(30)  # Collect every 30 seconds

            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(30)

    async def _collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            import psutil

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            await self.record_metric(
                "system_cpu_usage_percent",
                cpu_percent,
                MetricType.GAUGE,
                unit="percent",
            )

            # Memory usage
            memory = psutil.virtual_memory()
            await self.record_metric(
                "system_memory_usage_percent",
                memory.percent,
                MetricType.GAUGE,
                unit="percent",
            )

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            await self.record_metric(
                "system_disk_usage_percent",
                disk_percent,
                MetricType.GAUGE,
                unit="percent",
            )

        except ImportError:
            # psutil not available
            pass
        except Exception as e:
            logger.error(f"System metrics collection failed: {e}")

    async def _collect_evolution_metrics(self):
        """Collect evolution-specific metrics."""
        try:
            # Active spans count
            await self.record_metric(
                "active_spans_count",
                len(self.active_spans),
                MetricType.GAUGE,
                unit="count",
            )

            # Active alerts count
            await self.record_metric(
                "active_alerts_count",
                len(self.active_alerts),
                MetricType.GAUGE,
                unit="count",
            )

            # Metrics buffer size
            await self.record_metric(
                "metrics_buffer_size",
                len(self.metrics_buffer),
                MetricType.GAUGE,
                unit="count",
            )

        except Exception as e:
            logger.error(f"Evolution metrics collection failed: {e}")

    async def _collect_security_metrics(self):
        """Collect security-related metrics."""
        try:
            # Security events count (would integrate with security manager)
            await self.record_metric(
                "security_events_total",
                self.observability_metrics.get("security_events", 0),
                MetricType.COUNTER,
                unit="count",
            )

        except Exception as e:
            logger.error(f"Security metrics collection failed: {e}")

    async def _cleanup_old_metrics(self):
        """Clean up old metrics from buffer."""
        try:
            current_time = datetime.now(UTC)
            old_metrics = []

            for metric in self.metrics_buffer:
                # Remove metrics older than 1 hour
                if (current_time - metric.timestamp).total_seconds() > 3600:
                    old_metrics.append(metric)

            for metric in old_metrics:
                self.metrics_buffer.remove(metric)

            if old_metrics:
                logger.debug(f"Cleaned up {len(old_metrics)} old metrics")

        except Exception as e:
            logger.error(f"Metrics cleanup failed: {e}")

    async def _monitor_alerts(self):
        """Background task to monitor alert conditions."""
        while True:
            try:
                # Check for alert resolution conditions
                await self._check_alert_resolution()

                # Check for escalation conditions
                await self._check_alert_escalation()

                # Sleep for monitoring interval
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Alert monitoring error: {e}")
                await asyncio.sleep(60)

    async def _check_metric_alerts(self, metric: PerformanceMetric):
        """Check if a metric triggers any alert conditions."""
        try:
            # Response time alerts
            if metric.metric_name == "response_time_ms":
                if metric.value > self.performance_targets["response_time_ms"]:
                    await self.trigger_alert(
                        "High Response Time",
                        f"Response time {metric.value}ms exceeds target {self.performance_targets['response_time_ms']}ms",
                        AlertLevel.WARNING,
                        "performance_monitor",
                        metric.metric_name,
                        self.performance_targets["response_time_ms"],
                        metric.value,
                    )

            # Error rate alerts
            elif metric.metric_name == "error_rate_percent":
                if metric.value > self.performance_targets["error_rate_percent"]:
                    await self.trigger_alert(
                        "High Error Rate",
                        f"Error rate {metric.value}% exceeds target {self.performance_targets['error_rate_percent']}%",
                        AlertLevel.ERROR,
                        "performance_monitor",
                        metric.metric_name,
                        self.performance_targets["error_rate_percent"],
                        metric.value,
                    )

            # Evolution cycle time alerts
            elif metric.metric_name == "evolution_duration_minutes":
                if metric.value > self.performance_targets["evolution_cycle_minutes"]:
                    await self.trigger_alert(
                        "Long Evolution Cycle",
                        f"Evolution cycle {metric.value} minutes exceeds target {self.performance_targets['evolution_cycle_minutes']} minutes",
                        AlertLevel.WARNING,
                        "evolution_monitor",
                        metric.metric_name,
                        self.performance_targets["evolution_cycle_minutes"],
                        metric.value,
                    )

        except Exception as e:
            logger.error(f"Metric alert check failed: {e}")

    async def _check_alert_resolution(self):
        """Check if any active alerts can be resolved."""
        try:
            for alert_id, alert in list(self.active_alerts.items()):
                # Auto-resolve alerts older than 1 hour (simplified logic)
                if (
                    datetime.now(UTC) - alert.triggered_at
                ).total_seconds() > 3600:
                    await self.resolve_alert(alert_id)

        except Exception as e:
            logger.error(f"Alert resolution check failed: {e}")

    async def _check_alert_escalation(self):
        """Check if any alerts need escalation."""
        try:
            for alert in self.active_alerts.values():
                # Escalate critical alerts that have been active for more than 15 minutes
                if (
                    alert.alert_level == AlertLevel.CRITICAL
                    and (
                        datetime.now(UTC) - alert.triggered_at
                    ).total_seconds()
                    > 900
                ):

                    logger.critical(
                        f"ESCALATION: Critical alert {alert.alert_id} has been active for >15 minutes"
                    )
                    # In production, this would trigger escalation procedures

        except Exception as e:
            logger.error(f"Alert escalation check failed: {e}")

    async def get_observability_status(self) -> dict[str, Any]:
        """Get current observability framework status."""
        try:
            return {
                "opentelemetry": {
                    "available": OPENTELEMETRY_AVAILABLE,
                    "tracing_enabled": self.tracing_enabled,
                    "metrics_enabled": self.metrics_enabled,
                    "endpoint": self.otlp_endpoint,
                    "version": self.otlp_version,
                },
                "service_info": {
                    "name": self.service_name,
                    "version": self.service_version,
                    "environment": self.environment,
                },
                "current_state": {
                    "active_spans": len(self.active_spans),
                    "metrics_buffer_size": len(self.metrics_buffer),
                    "active_alerts": len(self.active_alerts),
                },
                "metrics": self.observability_metrics,
                "performance_targets": self.performance_targets,
                "last_updated": datetime.now(UTC).isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get observability status: {e}")
            return {"error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """Perform health check for the observability framework."""
        try:
            health_status = {
                "healthy": True,
                "timestamp": time.time(),
                "checks": {},
            }

            # Check OpenTelemetry availability
            health_status["checks"]["opentelemetry_availability"] = {
                "healthy": OPENTELEMETRY_AVAILABLE,
                "tracing_enabled": self.tracing_enabled,
                "metrics_enabled": self.metrics_enabled,
            }
            if not OPENTELEMETRY_AVAILABLE:
                health_status["healthy"] = False

            # Check metrics collection
            health_status["checks"]["metrics_collection"] = {
                "healthy": True,
                "buffer_size": len(self.metrics_buffer),
                "collection_rate": "normal",
            }

            # Check alerting
            health_status["checks"]["alerting"] = {
                "healthy": True,
                "active_alerts": len(self.active_alerts),
                "critical_alerts": len(
                    [
                        alert
                        for alert in self.active_alerts.values()
                        if alert.alert_level == AlertLevel.CRITICAL
                    ]
                ),
            }

            return health_status

        except Exception as e:
            logger.error(f"Observability framework health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": time.time(),
            }

    async def shutdown(self):
        """Shutdown the observability framework gracefully."""
        try:
            logger.info("Shutting down observability framework...")

            # Finish any active spans
            for span_id in list(self.active_spans.keys()):
                await self.finish_span(span_id, status="cancelled")

            # Flush metrics
            if self.meter_provider:
                # Force flush metrics
                pass

            logger.info("✅ Observability framework shutdown complete")

        except Exception as e:
            logger.error(f"Error during observability framework shutdown: {e}")
