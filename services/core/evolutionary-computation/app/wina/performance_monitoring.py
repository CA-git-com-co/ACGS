"""
WINA Performance Monitoring

Comprehensive performance monitoring for WINA optimization components
with constitutional compliance tracking and system health metrics.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = logging.getLogger(__name__)


class WINAMonitoringLevel(Enum):
    """WINA monitoring detail levels."""

    BASIC = "basic"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"
    DEBUG = "debug"


class WINAComponentType(Enum):
    """Types of WINA components being monitored."""

    CORE = "core"
    GATING = "gating"
    CONSTITUTIONAL = "constitutional"
    METRICS = "metrics"
    LEARNING = "learning"


@dataclass
class WINASystemHealthMetrics:
    """System health metrics for WINA components."""

    component_type: WINAComponentType
    cpu_usage_percent: float
    memory_usage_mb: float
    response_time_ms: float
    error_rate: float
    availability: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WINANeuronActivationMetrics:
    """Neural activation metrics for WINA optimization."""

    layer_id: str
    activation_count: int
    average_activation_strength: float
    gating_efficiency: float
    constitutional_compliance_score: float
    optimization_impact: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WINADynamicGatingMetrics:
    """Dynamic gating performance metrics."""

    gating_strategy: str
    decisions_per_second: float
    allow_rate: float
    throttle_rate: float
    block_rate: float
    average_decision_time_ms: float
    constitutional_violations: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WINAIntegrationPerformanceMetrics:
    """Integration performance metrics with other services."""

    service_name: str
    request_count: int
    success_rate: float
    average_latency_ms: float
    error_count: int
    timeout_count: int
    constitutional_compliance_rate: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WINAConstitutionalComplianceMetrics:
    """Constitutional compliance specific metrics."""

    total_checks: int
    compliance_rate: float
    violation_count: int
    average_compliance_score: float
    principle_scores: dict[str, float]
    enforcement_actions: int
    timestamp: datetime = field(default_factory=datetime.now)


class WINAPerformanceCollector:
    """
    Comprehensive performance monitoring and collection for WINA components.

    Collects, aggregates, and analyzes performance metrics across all WINA
    components with focus on constitutional compliance and system health.
    """

    def __init__(
        self, monitoring_level: WINAMonitoringLevel = WINAMonitoringLevel.STANDARD
    ):
        """
        Initialize WINA performance collector.

        Args:
            monitoring_level: Level of monitoring detail to collect
        """
        self.monitoring_level = monitoring_level
        self.collection_interval = self._get_collection_interval()

        # Metrics storage
        self.system_health_metrics: list[WINASystemHealthMetrics] = []
        self.neuron_activation_metrics: list[WINANeuronActivationMetrics] = []
        self.gating_metrics: list[WINADynamicGatingMetrics] = []
        self.integration_metrics: list[WINAIntegrationPerformanceMetrics] = []
        self.constitutional_metrics: list[WINAConstitutionalComplianceMetrics] = []

        # Performance tracking
        self.collection_start_time = datetime.now()
        self.total_collections = 0
        self.last_collection_time = None

        # Alerting thresholds
        self.alert_thresholds = {
            "cpu_usage_percent": 80.0,
            "memory_usage_mb": 1024.0,
            "response_time_ms": 200.0,
            "error_rate": 0.05,
            "constitutional_compliance_rate": 0.85,
        }

        logger.info(
            f"WINA Performance Collector initialized with {monitoring_level.value} monitoring"
        )

    def _get_collection_interval(self) -> int:
        """Get collection interval based on monitoring level."""
        intervals = {
            WINAMonitoringLevel.BASIC: 60,  # 1 minute
            WINAMonitoringLevel.STANDARD: 30,  # 30 seconds
            WINAMonitoringLevel.COMPREHENSIVE: 10,  # 10 seconds
            WINAMonitoringLevel.DEBUG: 5,  # 5 seconds
        }
        return intervals.get(self.monitoring_level, 30)

    async def collect_system_health(
        self, component_type: WINAComponentType
    ) -> WINASystemHealthMetrics:
        """
        Collect system health metrics for a WINA component.

        Args:
            component_type: Type of component to monitor

        Returns:
            WINASystemHealthMetrics with current health data
        """
        try:
            # Simulate system health collection
            # In real implementation, this would collect actual system metrics

            import random

            import psutil

            # Get actual system metrics where possible
            cpu_usage = psutil.cpu_percent(interval=0.1)
            memory_info = psutil.virtual_memory()
            memory_usage_mb = memory_info.used / (1024 * 1024)

            # Simulate component-specific metrics
            response_time_ms = random.uniform(10, 100)
            error_rate = random.uniform(0.001, 0.02)
            availability = random.uniform(0.95, 1.0)

            metrics = WINASystemHealthMetrics(
                component_type=component_type,
                cpu_usage_percent=cpu_usage,
                memory_usage_mb=memory_usage_mb,
                response_time_ms=response_time_ms,
                error_rate=error_rate,
                availability=availability,
            )

            self.system_health_metrics.append(metrics)
            self._check_health_alerts(metrics)
            self._cleanup_old_metrics()

            return metrics

        except Exception as e:
            logger.exception(f"Failed to collect system health metrics: {e}")
            # Return default metrics on error
            return WINASystemHealthMetrics(
                component_type=component_type,
                cpu_usage_percent=0.0,
                memory_usage_mb=0.0,
                response_time_ms=0.0,
                error_rate=1.0,
                availability=0.0,
            )

    def record_neuron_activation(
        self,
        layer_id: str,
        activation_count: int,
        activation_strength: float,
        gating_efficiency: float,
        constitutional_score: float,
        optimization_impact: float,
    ):
        """Record neural activation metrics."""
        try:
            metrics = WINANeuronActivationMetrics(
                layer_id=layer_id,
                activation_count=activation_count,
                average_activation_strength=activation_strength,
                gating_efficiency=gating_efficiency,
                constitutional_compliance_score=constitutional_score,
                optimization_impact=optimization_impact,
            )

            self.neuron_activation_metrics.append(metrics)

        except Exception as e:
            logger.exception(f"Failed to record neuron activation metrics: {e}")

    def record_gating_performance(
        self,
        strategy: str,
        decisions_per_second: float,
        allow_rate: float,
        throttle_rate: float,
        block_rate: float,
        decision_time_ms: float,
        violations: int,
    ):
        """Record gating performance metrics."""
        try:
            metrics = WINADynamicGatingMetrics(
                gating_strategy=strategy,
                decisions_per_second=decisions_per_second,
                allow_rate=allow_rate,
                throttle_rate=throttle_rate,
                block_rate=block_rate,
                average_decision_time_ms=decision_time_ms,
                constitutional_violations=violations,
            )

            self.gating_metrics.append(metrics)

        except Exception as e:
            logger.exception(f"Failed to record gating performance metrics: {e}")

    def record_integration_performance(
        self,
        service_name: str,
        request_count: int,
        success_rate: float,
        latency_ms: float,
        error_count: int,
        timeout_count: int,
        compliance_rate: float,
    ):
        """Record service integration performance metrics."""
        try:
            metrics = WINAIntegrationPerformanceMetrics(
                service_name=service_name,
                request_count=request_count,
                success_rate=success_rate,
                average_latency_ms=latency_ms,
                error_count=error_count,
                timeout_count=timeout_count,
                constitutional_compliance_rate=compliance_rate,
            )

            self.integration_metrics.append(metrics)

        except Exception as e:
            logger.exception(f"Failed to record integration performance metrics: {e}")

    def record_constitutional_compliance(
        self,
        total_checks: int,
        compliance_rate: float,
        violation_count: int,
        average_score: float,
        principle_scores: dict[str, float],
        enforcement_actions: int,
    ):
        """Record constitutional compliance metrics."""
        try:
            metrics = WINAConstitutionalComplianceMetrics(
                total_checks=total_checks,
                compliance_rate=compliance_rate,
                violation_count=violation_count,
                average_compliance_score=average_score,
                principle_scores=principle_scores,
                enforcement_actions=enforcement_actions,
            )

            self.constitutional_metrics.append(metrics)

        except Exception as e:
            logger.exception(f"Failed to record constitutional compliance metrics: {e}")

    def get_performance_summary(
        self, time_range: timedelta | None = None
    ) -> dict[str, Any]:
        """
        Get comprehensive performance summary.

        Args:
            time_range: Time range for metrics (default: last hour)

        Returns:
            Performance summary dictionary
        """
        try:
            if time_range is None:
                time_range = timedelta(hours=1)

            cutoff_time = datetime.now() - time_range

            # Filter metrics by time range
            recent_health = [
                m for m in self.system_health_metrics if m.timestamp >= cutoff_time
            ]
            recent_gating = [
                m for m in self.gating_metrics if m.timestamp >= cutoff_time
            ]
            recent_constitutional = [
                m for m in self.constitutional_metrics if m.timestamp >= cutoff_time
            ]
            recent_integration = [
                m for m in self.integration_metrics if m.timestamp >= cutoff_time
            ]

            return {
                "monitoring_level": self.monitoring_level.value,
                "collection_interval": self.collection_interval,
                "total_collections": self.total_collections,
                "uptime_hours": (
                    datetime.now() - self.collection_start_time
                ).total_seconds()
                / 3600,
                "system_health": self._summarize_health_metrics(recent_health),
                "gating_performance": self._summarize_gating_metrics(recent_gating),
                "constitutional_compliance": self._summarize_constitutional_metrics(
                    recent_constitutional
                ),
                "service_integration": self._summarize_integration_metrics(
                    recent_integration
                ),
                "alert_status": self._get_alert_status(),
                "recommendations": self._generate_performance_recommendations(),
            }

        except Exception as e:
            logger.exception(f"Failed to generate performance summary: {e}")
            return {"error": str(e)}

    def _summarize_health_metrics(
        self, metrics: list[WINASystemHealthMetrics]
    ) -> dict[str, Any]:
        """Summarize system health metrics."""
        if not metrics:
            return {"status": "no_data"}

        avg_cpu = sum(m.cpu_usage_percent for m in metrics) / len(metrics)
        avg_memory = sum(m.memory_usage_mb for m in metrics) / len(metrics)
        avg_response_time = sum(m.response_time_ms for m in metrics) / len(metrics)
        avg_error_rate = sum(m.error_rate for m in metrics) / len(metrics)
        avg_availability = sum(m.availability for m in metrics) / len(metrics)

        return {
            "average_cpu_usage": avg_cpu,
            "average_memory_usage_mb": avg_memory,
            "average_response_time_ms": avg_response_time,
            "average_error_rate": avg_error_rate,
            "average_availability": avg_availability,
            "sample_count": len(metrics),
        }

    def _summarize_gating_metrics(
        self, metrics: list[WINADynamicGatingMetrics]
    ) -> dict[str, Any]:
        """Summarize gating performance metrics."""
        if not metrics:
            return {"status": "no_data"}

        avg_decisions_per_sec = sum(m.decisions_per_second for m in metrics) / len(
            metrics
        )
        avg_allow_rate = sum(m.allow_rate for m in metrics) / len(metrics)
        avg_decision_time = sum(m.average_decision_time_ms for m in metrics) / len(
            metrics
        )
        total_violations = sum(m.constitutional_violations for m in metrics)

        return {
            "average_decisions_per_second": avg_decisions_per_sec,
            "average_allow_rate": avg_allow_rate,
            "average_decision_time_ms": avg_decision_time,
            "total_constitutional_violations": total_violations,
            "sample_count": len(metrics),
        }

    def _summarize_constitutional_metrics(
        self, metrics: list[WINAConstitutionalComplianceMetrics]
    ) -> dict[str, Any]:
        """Summarize constitutional compliance metrics."""
        if not metrics:
            return {"status": "no_data"}

        total_checks = sum(m.total_checks for m in metrics)
        avg_compliance_rate = sum(m.compliance_rate for m in metrics) / len(metrics)
        total_violations = sum(m.violation_count for m in metrics)
        avg_score = sum(m.average_compliance_score for m in metrics) / len(metrics)

        return {
            "total_compliance_checks": total_checks,
            "average_compliance_rate": avg_compliance_rate,
            "total_violations": total_violations,
            "average_compliance_score": avg_score,
            "sample_count": len(metrics),
        }

    def _summarize_integration_metrics(
        self, metrics: list[WINAIntegrationPerformanceMetrics]
    ) -> dict[str, Any]:
        """Summarize service integration metrics."""
        if not metrics:
            return {"status": "no_data"}

        total_requests = sum(m.request_count for m in metrics)
        avg_success_rate = sum(m.success_rate for m in metrics) / len(metrics)
        avg_latency = sum(m.average_latency_ms for m in metrics) / len(metrics)
        total_errors = sum(m.error_count for m in metrics)

        return {
            "total_requests": total_requests,
            "average_success_rate": avg_success_rate,
            "average_latency_ms": avg_latency,
            "total_errors": total_errors,
            "sample_count": len(metrics),
        }

    def _check_health_alerts(self, metrics: WINASystemHealthMetrics):
        """Check for alert conditions in health metrics."""
        try:
            if metrics.cpu_usage_percent > self.alert_thresholds["cpu_usage_percent"]:
                logger.warning(
                    f"High CPU usage alert: {metrics.cpu_usage_percent:.1f}%"
                )

            if metrics.memory_usage_mb > self.alert_thresholds["memory_usage_mb"]:
                logger.warning(
                    f"High memory usage alert: {metrics.memory_usage_mb:.1f}MB"
                )

            if metrics.response_time_ms > self.alert_thresholds["response_time_ms"]:
                logger.warning(
                    f"High response time alert: {metrics.response_time_ms:.1f}ms"
                )

            if metrics.error_rate > self.alert_thresholds["error_rate"]:
                logger.warning(f"High error rate alert: {metrics.error_rate:.3f}")

        except Exception as e:
            logger.exception(f"Failed to check health alerts: {e}")

    def _get_alert_status(self) -> dict[str, Any]:
        """Get current alert status."""
        # This would integrate with actual alerting system
        return {
            "active_alerts": 0,
            "alert_thresholds": self.alert_thresholds,
            "last_alert_time": None,
        }

    def _generate_performance_recommendations(self) -> list[str]:
        """Generate performance improvement recommendations."""
        recommendations = []

        # Analyze recent metrics and generate recommendations
        if self.system_health_metrics:
            recent_health = self.system_health_metrics[-10:]
            avg_cpu = sum(m.cpu_usage_percent for m in recent_health) / len(
                recent_health
            )

            if avg_cpu > 70:
                recommendations.append("Consider optimizing CPU-intensive operations")

            avg_response_time = sum(m.response_time_ms for m in recent_health) / len(
                recent_health
            )
            if avg_response_time > 150:
                recommendations.append(
                    "Response times are elevated - review optimization strategies"
                )

        if not recommendations:
            recommendations.append("System performance is within acceptable parameters")

        return recommendations

    def _cleanup_old_metrics(self):
        """Remove old metrics to prevent memory growth."""
        try:
            retention_period = timedelta(hours=24)  # Keep 24 hours of data
            cutoff_time = datetime.now() - retention_period

            self.system_health_metrics = [
                m for m in self.system_health_metrics if m.timestamp >= cutoff_time
            ]
            self.neuron_activation_metrics = [
                m for m in self.neuron_activation_metrics if m.timestamp >= cutoff_time
            ]
            self.gating_metrics = [
                m for m in self.gating_metrics if m.timestamp >= cutoff_time
            ]
            self.integration_metrics = [
                m for m in self.integration_metrics if m.timestamp >= cutoff_time
            ]
            self.constitutional_metrics = [
                m for m in self.constitutional_metrics if m.timestamp >= cutoff_time
            ]

        except Exception as e:
            logger.exception(f"Failed to cleanup old metrics: {e}")
