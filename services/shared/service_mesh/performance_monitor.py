"""
Performance Monitoring and Alerting for ACGS-1 Load Balancing
Real-time monitoring with alerting for >99.9% availability and <500ms response times
"""

import asyncio
import logging
import statistics
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class MetricType(Enum):
    """Types of performance metrics."""

    RESPONSE_TIME = "response_time"
    AVAILABILITY = "availability"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    CONCURRENT_USERS = "concurrent_users"
    RESOURCE_USAGE = "resource_usage"


@dataclass
class PerformanceThreshold:
    """Performance threshold configuration."""

    metric_type: MetricType
    warning_threshold: float
    critical_threshold: float
    emergency_threshold: float
    measurement_window_seconds: int = 300  # 5 minutes
    min_samples: int = 10


@dataclass
class PerformanceAlert:
    """Performance alert data."""

    alert_id: str
    service_type: str
    instance_id: str | None
    metric_type: MetricType
    severity: AlertSeverity
    current_value: float
    threshold_value: float
    message: str
    timestamp: float
    resolved: bool = False
    resolved_at: float | None = None


@dataclass
class PerformanceMetrics:
    """Performance metrics snapshot."""

    timestamp: float
    service_type: str
    instance_id: str | None

    # Core performance metrics
    response_time_ms: float
    availability_percent: float
    throughput_rps: float  # requests per second
    error_rate_percent: float
    concurrent_connections: int

    # Resource metrics
    cpu_usage_percent: float | None = None
    memory_usage_percent: float | None = None
    disk_usage_percent: float | None = None

    # Load balancing metrics
    active_instances: int = 0
    healthy_instances: int = 0
    total_requests: int = 0
    failed_requests: int = 0


class PerformanceMonitor:
    """
    Real-time performance monitoring for ACGS-1 load balancing.

    Monitors key performance indicators and triggers alerts when
    thresholds are exceeded to ensure >99.9% availability.
    """

    def __init__(self, monitoring_interval: float = 30.0):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Initialize performance monitor.

        Args:
            monitoring_interval: Monitoring interval in seconds
        """
        self.monitoring_interval = monitoring_interval

        # Performance data storage
        self.metrics_history: dict[str, list[PerformanceMetrics]] = {}
        self.active_alerts: dict[str, PerformanceAlert] = {}
        self.alert_history: list[PerformanceAlert] = []

        # Thresholds for ACGS-1 targets
        self.thresholds = self._initialize_thresholds()

        # Alert callbacks
        self.alert_callbacks: list[Callable[[PerformanceAlert], None]] = []

        # Monitoring state
        self._monitoring_task: asyncio.Task | None = None
        self._running = False

        # Performance targets
        self.targets = {
            "response_time_ms": 500,
            "availability_percent": 99.9,
            "concurrent_users": 1000,
            "error_rate_percent": 1.0,
        }

    def _initialize_thresholds(self) -> dict[MetricType, PerformanceThreshold]:
        """Initialize performance thresholds for ACGS-1."""
        return {
            MetricType.RESPONSE_TIME: PerformanceThreshold(
                metric_type=MetricType.RESPONSE_TIME,
                warning_threshold=400.0,  # 400ms
                critical_threshold=500.0,  # 500ms (target)
                emergency_threshold=1000.0,  # 1s
            ),
            MetricType.AVAILABILITY: PerformanceThreshold(
                metric_type=MetricType.AVAILABILITY,
                warning_threshold=99.5,  # 99.5%
                critical_threshold=99.0,  # 99.0%
                emergency_threshold=95.0,  # 95.0%
            ),
            MetricType.ERROR_RATE: PerformanceThreshold(
                metric_type=MetricType.ERROR_RATE,
                warning_threshold=1.0,  # 1%
                critical_threshold=5.0,  # 5%
                emergency_threshold=10.0,  # 10%
            ),
            MetricType.CONCURRENT_USERS: PerformanceThreshold(
                metric_type=MetricType.CONCURRENT_USERS,
                warning_threshold=800.0,  # 800 users
                critical_threshold=1000.0,  # 1000 users (target)
                emergency_threshold=1200.0,  # 1200 users
            ),
            MetricType.RESOURCE_USAGE: PerformanceThreshold(
                metric_type=MetricType.RESOURCE_USAGE,
                warning_threshold=70.0,  # 70% CPU/Memory
                critical_threshold=85.0,  # 85% CPU/Memory
                emergency_threshold=95.0,  # 95% CPU/Memory
            ),
        }

    async def start_monitoring(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Start performance monitoring."""
        if self._running:
            return

        self._running = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())

        logger.info("Performance monitoring started")

    async def stop_monitoring(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Stop performance monitoring."""
        if not self._running:
            return

        self._running = False

        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        logger.info("Performance monitoring stopped")

    async def _monitoring_loop(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Main monitoring loop."""
        while self._running:
            try:
                await self._collect_and_analyze_metrics()
                await asyncio.sleep(self.monitoring_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(5)

    async def _collect_and_analyze_metrics(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Collect metrics and analyze for alerts."""
        # This would be called by the service discovery system
        # For now, we'll create a placeholder
        logger.debug("Collecting performance metrics...")

    def record_metrics(self, metrics: PerformanceMetrics):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Record performance metrics.

        Args:
            metrics: Performance metrics to record
        """
        key = f"{metrics.service_type}:{metrics.instance_id or 'all'}"

        if key not in self.metrics_history:
            self.metrics_history[key] = []

        # Add metrics and maintain history size
        self.metrics_history[key].append(metrics)

        # Keep only last 1000 entries (configurable)
        if len(self.metrics_history[key]) > 1000:
            self.metrics_history[key] = self.metrics_history[key][-1000:]

        # Analyze metrics for alerts
        self._analyze_metrics_for_alerts(metrics)

    def _analyze_metrics_for_alerts(self, metrics: PerformanceMetrics):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Analyze metrics and trigger alerts if needed."""
        # Check response time
        if metrics.response_time_ms > 0:
            self._check_threshold(
                MetricType.RESPONSE_TIME,
                metrics.response_time_ms,
                metrics.service_type,
                metrics.instance_id,
            )

        # Check availability
        self._check_threshold(
            MetricType.AVAILABILITY,
            metrics.availability_percent,
            metrics.service_type,
            metrics.instance_id,
        )

        # Check error rate
        self._check_threshold(
            MetricType.ERROR_RATE,
            metrics.error_rate_percent,
            metrics.service_type,
            metrics.instance_id,
        )

        # Check concurrent connections
        self._check_threshold(
            MetricType.CONCURRENT_USERS,
            metrics.concurrent_connections,
            metrics.service_type,
            metrics.instance_id,
        )

        # Check resource usage
        if metrics.cpu_usage_percent:
            self._check_threshold(
                MetricType.RESOURCE_USAGE,
                metrics.cpu_usage_percent,
                metrics.service_type,
                metrics.instance_id,
                metric_name="CPU",
            )

        if metrics.memory_usage_percent:
            self._check_threshold(
                MetricType.RESOURCE_USAGE,
                metrics.memory_usage_percent,
                metrics.service_type,
                metrics.instance_id,
                metric_name="Memory",
            )

    def _check_threshold(
        self,
        metric_type: MetricType,
        value: float,
        service_type: str,
        instance_id: str | None,
        metric_name: str | None = None,
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Check if metric value exceeds thresholds."""
        threshold = self.thresholds.get(metric_type)
        if not threshold:
            return

        severity = None
        threshold_value = None

        # Determine severity based on thresholds
        if metric_type == MetricType.AVAILABILITY:
            # For availability, lower values are worse
            if value <= threshold.emergency_threshold:
                severity = AlertSeverity.EMERGENCY
                threshold_value = threshold.emergency_threshold
            elif value <= threshold.critical_threshold:
                severity = AlertSeverity.CRITICAL
                threshold_value = threshold.critical_threshold
            elif value <= threshold.warning_threshold:
                severity = AlertSeverity.WARNING
                threshold_value = threshold.warning_threshold
        else:
            # For other metrics, higher values are worse
            if value >= threshold.emergency_threshold:
                severity = AlertSeverity.EMERGENCY
                threshold_value = threshold.emergency_threshold
            elif value >= threshold.critical_threshold:
                severity = AlertSeverity.CRITICAL
                threshold_value = threshold.critical_threshold
            elif value >= threshold.warning_threshold:
                severity = AlertSeverity.WARNING
                threshold_value = threshold.warning_threshold

        if severity:
            self._trigger_alert(
                metric_type,
                severity,
                value,
                threshold_value,
                service_type,
                instance_id,
                metric_name,
            )

    def _trigger_alert(
        self,
        metric_type: MetricType,
        severity: AlertSeverity,
        current_value: float,
        threshold_value: float,
        service_type: str,
        instance_id: str | None,
        metric_name: str | None = None,
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Trigger performance alert."""
        alert_id = f"{service_type}:{instance_id or 'all'}:{metric_type.value}:{int(time.time())}"

        # Check if similar alert already exists
        existing_alert_key = f"{service_type}:{instance_id}:{metric_type.value}"
        if existing_alert_key in self.active_alerts:
            # Update existing alert if severity increased
            existing_alert = self.active_alerts[existing_alert_key]
            if self._severity_level(severity) > self._severity_level(
                existing_alert.severity
            ):
                existing_alert.severity = severity
                existing_alert.current_value = current_value
                existing_alert.timestamp = time.time()
            return

        # Create new alert
        metric_display = metric_name or metric_type.value.replace("_", " ").title()

        alert = PerformanceAlert(
            alert_id=alert_id,
            service_type=service_type,
            instance_id=instance_id,
            metric_type=metric_type,
            severity=severity,
            current_value=current_value,
            threshold_value=threshold_value,
            message=f"{metric_display} {severity.value}: {current_value:.2f} exceeds threshold {threshold_value:.2f}",
            timestamp=time.time(),
        )

        # Store alert
        self.active_alerts[existing_alert_key] = alert
        self.alert_history.append(alert)

        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")

        logger.warning(f"Performance alert triggered: {alert.message}")

    def _severity_level(self, severity: AlertSeverity) -> int:
        """Get numeric severity level for comparison."""
        levels = {
            AlertSeverity.INFO: 1,
            AlertSeverity.WARNING: 2,
            AlertSeverity.CRITICAL: 3,
            AlertSeverity.EMERGENCY: 4,
        }
        return levels.get(severity, 0)

    def resolve_alert(self, alert_id: str):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Resolve an active alert."""
        for key, alert in self.active_alerts.items():
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.resolved_at = time.time()
                del self.active_alerts[key]
                logger.info(f"Alert resolved: {alert.message}")
                break

    def register_alert_callback(self, callback: Callable[[PerformanceAlert], None]):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Register callback for alert notifications."""
        self.alert_callbacks.append(callback)

    def get_current_performance_summary(self) -> dict[str, Any]:
        """Get current performance summary."""
        if not self.metrics_history:
            return {"status": "no_data"}

        # Calculate aggregate metrics from recent data
        recent_metrics = []
        cutoff_time = time.time() - 300  # Last 5 minutes

        for metrics_list in self.metrics_history.values():
            recent_metrics.extend(
                [m for m in metrics_list if m.timestamp > cutoff_time]
            )

        if not recent_metrics:
            return {"status": "no_recent_data"}

        # Calculate averages
        avg_response_time = statistics.mean(
            [m.response_time_ms for m in recent_metrics if m.response_time_ms > 0]
        )
        avg_availability = statistics.mean(
            [m.availability_percent for m in recent_metrics]
        )
        avg_error_rate = statistics.mean([m.error_rate_percent for m in recent_metrics])
        total_connections = sum([m.concurrent_connections for m in recent_metrics])

        # Determine overall health
        health_score = 100.0
        if avg_response_time > self.targets["response_time_ms"]:
            health_score -= 20
        if avg_availability < self.targets["availability_percent"]:
            health_score -= 30
        if avg_error_rate > self.targets["error_rate_percent"]:
            health_score -= 25
        if total_connections > self.targets["concurrent_users"]:
            health_score -= 15

        return {
            "status": (
                "healthy"
                if health_score >= 80
                else "degraded" if health_score >= 60 else "unhealthy"
            ),
            "health_score": max(0, health_score),
            "metrics": {
                "avg_response_time_ms": avg_response_time,
                "avg_availability_percent": avg_availability,
                "avg_error_rate_percent": avg_error_rate,
                "total_concurrent_connections": total_connections,
                "active_alerts": len(self.active_alerts),
                "measurement_window_minutes": 5,
            },
            "targets": self.targets,
            "timestamp": time.time(),
        }

    def get_alert_summary(self) -> dict[str, Any]:
        """Get alert summary."""
        severity_counts = {severity.value: 0 for severity in AlertSeverity}

        for alert in self.active_alerts.values():
            severity_counts[alert.severity.value] += 1

        return {
            "active_alerts": len(self.active_alerts),
            "severity_breakdown": severity_counts,
            "recent_alerts": len(
                [
                    a for a in self.alert_history if time.time() - a.timestamp < 3600
                ]  # Last hour
            ),
            "total_alerts_today": len(
                [
                    a
                    for a in self.alert_history
                    if time.time() - a.timestamp < 86400  # Last 24 hours
                ]
            ),
        }


# Global performance monitor
_performance_monitor: PerformanceMonitor | None = None


class AlertingSystem:
    """
    Alerting system for ACGS-1 performance monitoring.

    Handles alert notifications, escalation, and integration
    with external monitoring systems.
    """

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize alerting system."""
        self.notification_channels: list[Callable[[PerformanceAlert], None]] = []
        self.escalation_rules: dict[AlertSeverity, dict[str, Any]] = {}
        self.alert_suppression: dict[str, float] = {}  # alert_key -> suppress_until

        # Default escalation rules
        self._setup_default_escalation()

    def _setup_default_escalation(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Setup default alert escalation rules."""
        self.escalation_rules = {
            AlertSeverity.WARNING: {
                "immediate_notify": True,
                "escalate_after_minutes": 15,
                "max_notifications": 3,
            },
            AlertSeverity.CRITICAL: {
                "immediate_notify": True,
                "escalate_after_minutes": 5,
                "max_notifications": 5,
            },
            AlertSeverity.EMERGENCY: {
                "immediate_notify": True,
                "escalate_after_minutes": 1,
                "max_notifications": 10,
            },
        }

    def add_notification_channel(self, channel: Callable[[PerformanceAlert], None]):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Add notification channel."""
        self.notification_channels.append(channel)

    def handle_alert(self, alert: PerformanceAlert):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Handle incoming alert."""
        alert_key = (
            f"{alert.service_type}:{alert.instance_id}:{alert.metric_type.value}"
        )

        # Check if alert is suppressed
        if self._is_alert_suppressed(alert_key):
            return

        # Send notifications
        self._send_notifications(alert)

        # Set suppression period to avoid spam
        self._set_alert_suppression(alert_key, alert.severity)

    def _is_alert_suppressed(self, alert_key: str) -> bool:
        """Check if alert is currently suppressed."""
        suppress_until = self.alert_suppression.get(alert_key, 0)
        return time.time() < suppress_until

    def _set_alert_suppression(self, alert_key: str, severity: AlertSeverity):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Set alert suppression period."""
        suppression_periods = {
            AlertSeverity.WARNING: 300,  # 5 minutes
            AlertSeverity.CRITICAL: 180,  # 3 minutes
            AlertSeverity.EMERGENCY: 60,  # 1 minute
        }

        period = suppression_periods.get(severity, 300)
        self.alert_suppression[alert_key] = time.time() + period

    def _send_notifications(self, alert: PerformanceAlert):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Send alert notifications to all channels."""
        for channel in self.notification_channels:
            try:
                channel(alert)
            except Exception as e:
                logger.error(f"Failed to send alert notification: {e}")


def console_alert_handler(alert: PerformanceAlert):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Console alert handler for development."""
    severity_emoji = {
        AlertSeverity.INFO: "ℹ️",
        AlertSeverity.WARNING: "⚠️",
        AlertSeverity.CRITICAL: "🚨",
        AlertSeverity.EMERGENCY: "🔥",
    }

    emoji = severity_emoji.get(alert.severity, "❓")
    print(f"\n{emoji} ACGS-1 ALERT [{alert.severity.value.upper()}]")
    print(f"Service: {alert.service_type}")
    if alert.instance_id:
        print(f"Instance: {alert.instance_id}")
    print(f"Message: {alert.message}")
    print(
        f"Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert.timestamp))}"
    )
    print("-" * 50)


async def get_performance_monitor() -> PerformanceMonitor:
    """Get the global performance monitor."""
    global _performance_monitor

    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()

        # Setup alerting system
        alerting_system = AlertingSystem()
        alerting_system.add_notification_channel(console_alert_handler)
        _performance_monitor.register_alert_callback(alerting_system.handle_alert)

        await _performance_monitor.start_monitoring()

    return _performance_monitor
