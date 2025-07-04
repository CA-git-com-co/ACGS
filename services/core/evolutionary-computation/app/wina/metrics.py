"""
WINA Metrics Collection and Analysis

Provides comprehensive metrics collection for WINA optimization performance,
constitutional compliance, and system health monitoring.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = logging.getLogger(__name__)


class MetricType(Enum):
    """Types of WINA metrics."""

    PERFORMANCE = "performance"
    CONSTITUTIONAL = "constitutional"
    OPTIMIZATION = "optimization"
    SYSTEM_HEALTH = "system_health"


@dataclass
class WINAMetric:
    """Individual WINA metric data point."""

    metric_id: str
    metric_type: MetricType
    value: float
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class MetricsSummary:
    """Summary of WINA metrics over a time period."""

    metric_type: MetricType
    count: int
    mean: float
    min_value: float
    max_value: float
    std_dev: float
    time_range: timedelta


class WINAMetrics:
    """
    WINA metrics collection and analysis system.

    Collects, stores, and analyzes metrics from WINA optimization operations
    to provide insights into performance and constitutional compliance.
    """

    def __init__(self, config: dict[str, Any]):
        """
        Initialize WINA metrics system.

        Args:
            config: WINA configuration dictionary
        """
        self.config = config
        self.metrics_storage: list[WINAMetric] = []
        self.collection_interval = config.get("monitoring", {}).get(
            "metrics_collection_interval", 10
        )
        self.retention_period = timedelta(days=7)  # Keep metrics for 7 days

        # Performance tracking
        self.performance_metrics: dict[str, list[float]] = {
            "gflops_reduction": [],
            "accuracy_preservation": [],
            "constitutional_compliance": [],
            "optimization_time_ms": [],
            "success_rate": [],
        }

        # Alert thresholds
        self.alert_thresholds = config.get("monitoring", {}).get("alert_thresholds", {})

        logger.info("WINA Metrics system initialized")

    def record_metric(
        self,
        metric_id: str,
        metric_type: MetricType,
        value: float,
        metadata: dict[str, Any] = None,
    ):
        """
        Record a new WINA metric.

        Args:
            metric_id: Unique identifier for the metric
            metric_type: Type of metric being recorded
            value: Metric value
            metadata: Additional metadata for the metric
        """
        try:
            metric = WINAMetric(
                metric_id=metric_id,
                metric_type=metric_type,
                value=value,
                timestamp=datetime.now(),
                metadata=metadata or {},
            )

            self.metrics_storage.append(metric)

            # Update performance tracking
            if metric_type == MetricType.OPTIMIZATION:
                self._update_performance_tracking(metric)

            # Check for alerts
            self._check_alert_conditions(metric)

            # Cleanup old metrics
            self._cleanup_old_metrics()

        except Exception as e:
            logger.error(f"Failed to record metric {metric_id}: {e}")

    def record_optimization_metrics(self, optimization_result: Any):
        """
        Record metrics from a WINA optimization result.

        Args:
            optimization_result: WINAOptimizationResult object
        """
        try:
            base_id = optimization_result.optimization_id

            self.record_metric(
                f"{base_id}_gflops_reduction",
                MetricType.OPTIMIZATION,
                optimization_result.gflops_reduction,
                {"strategy": optimization_result.strategy_used},
            )

            self.record_metric(
                f"{base_id}_accuracy",
                MetricType.PERFORMANCE,
                optimization_result.accuracy_preservation,
                {"strategy": optimization_result.strategy_used},
            )

            self.record_metric(
                f"{base_id}_constitutional",
                MetricType.CONSTITUTIONAL,
                optimization_result.constitutional_compliance,
                {"strategy": optimization_result.strategy_used},
            )

            self.record_metric(
                f"{base_id}_time",
                MetricType.PERFORMANCE,
                optimization_result.optimization_time_ms,
                {"strategy": optimization_result.strategy_used},
            )

        except Exception as e:
            logger.error(f"Failed to record optimization metrics: {e}")

    def get_metrics_summary(
        self, metric_type: MetricType = None, time_range: timedelta = None
    ) -> dict[str, MetricsSummary]:
        """
        Get summary of metrics for analysis.

        Args:
            metric_type: Filter by specific metric type
            time_range: Time range for metrics (default: last 24 hours)

        Returns:
            Dictionary of metric summaries by type
        """
        try:
            if time_range is None:
                time_range = timedelta(hours=24)

            cutoff_time = datetime.now() - time_range

            # Filter metrics
            filtered_metrics = [
                m
                for m in self.metrics_storage
                if m.timestamp >= cutoff_time
                and (metric_type is None or m.metric_type == metric_type)
            ]

            # Group by metric type
            grouped_metrics: dict[MetricType, list[WINAMetric]] = {}
            for metric in filtered_metrics:
                if metric.metric_type not in grouped_metrics:
                    grouped_metrics[metric.metric_type] = []
                grouped_metrics[metric.metric_type].append(metric)

            # Generate summaries
            summaries = {}
            for mtype, metrics in grouped_metrics.items():
                if metrics:
                    values = [m.value for m in metrics]
                    mean_val = sum(values) / len(values)
                    variance = sum((x - mean_val) ** 2 for x in values) / len(values)
                    std_dev = variance**0.5

                    summaries[mtype.value] = MetricsSummary(
                        metric_type=mtype,
                        count=len(metrics),
                        mean=mean_val,
                        min_value=min(values),
                        max_value=max(values),
                        std_dev=std_dev,
                        time_range=time_range,
                    )

            return summaries

        except Exception as e:
            logger.error(f"Failed to generate metrics summary: {e}")
            return {}

    def get_performance_trends(self) -> dict[str, Any]:
        """
        Get performance trends for WINA optimization.

        Returns:
            Dictionary with trend analysis
        """
        try:
            recent_metrics = self.get_metrics_summary(time_range=timedelta(hours=24))

            trends = {
                "optimization_efficiency": 0.0,
                "constitutional_compliance_trend": 0.0,
                "performance_stability": 0.0,
                "alert_frequency": 0.0,
            }

            # Calculate optimization efficiency trend
            if MetricType.OPTIMIZATION.value in recent_metrics:
                opt_summary = recent_metrics[MetricType.OPTIMIZATION.value]
                trends["optimization_efficiency"] = opt_summary.mean

            # Calculate constitutional compliance trend
            if MetricType.CONSTITUTIONAL.value in recent_metrics:
                const_summary = recent_metrics[MetricType.CONSTITUTIONAL.value]
                trends["constitutional_compliance_trend"] = const_summary.mean

            # Calculate performance stability (inverse of std dev)
            if MetricType.PERFORMANCE.value in recent_metrics:
                perf_summary = recent_metrics[MetricType.PERFORMANCE.value]
                trends["performance_stability"] = max(0, 1.0 - perf_summary.std_dev)

            return trends

        except Exception as e:
            logger.error(f"Failed to calculate performance trends: {e}")
            return {}

    def _update_performance_tracking(self, metric: WINAMetric):
        """Update internal performance tracking."""
        try:
            # Extract metric category from metadata
            if "gflops" in metric.metric_id.lower():
                self.performance_metrics["gflops_reduction"].append(metric.value)
            elif "accuracy" in metric.metric_id.lower():
                self.performance_metrics["accuracy_preservation"].append(metric.value)
            elif "constitutional" in metric.metric_id.lower():
                self.performance_metrics["constitutional_compliance"].append(
                    metric.value
                )
            elif "time" in metric.metric_id.lower():
                self.performance_metrics["optimization_time_ms"].append(metric.value)

            # Keep only recent values (last 100)
            for key in self.performance_metrics:
                if len(self.performance_metrics[key]) > 100:
                    self.performance_metrics[key] = self.performance_metrics[key][-100:]

        except Exception as e:
            logger.error(f"Failed to update performance tracking: {e}")

    def _check_alert_conditions(self, metric: WINAMetric):
        """Check if metric triggers any alert conditions."""
        try:
            # Check against configured thresholds
            if metric.metric_type == MetricType.PERFORMANCE:
                if (
                    "response_time" in metric.metric_id
                    and metric.value
                    > self.alert_thresholds.get("response_time_ms", 200)
                ):
                    logger.warning(
                        f"Performance alert: Response time {metric.value}ms exceeds threshold"
                    )

            elif metric.metric_type == MetricType.CONSTITUTIONAL:
                if metric.value < self.alert_thresholds.get("compliance_score", 0.85):
                    logger.warning(
                        f"Constitutional compliance alert: Score {metric.value:.3f} below threshold"
                    )

        except Exception as e:
            logger.error(f"Failed to check alert conditions: {e}")

    def _cleanup_old_metrics(self):
        """Remove metrics older than retention period."""
        try:
            cutoff_time = datetime.now() - self.retention_period
            self.metrics_storage = [
                m for m in self.metrics_storage if m.timestamp >= cutoff_time
            ]
        except Exception as e:
            logger.error(f"Failed to cleanup old metrics: {e}")

    def export_metrics(self, format_type: str = "json") -> str:
        """
        Export metrics in specified format.

        Args:
            format_type: Export format ("json", "csv")

        Returns:
            Exported metrics as string
        """
        try:
            if format_type == "json":
                import json

                metrics_data = [
                    {
                        "id": m.metric_id,
                        "type": m.metric_type.value,
                        "value": m.value,
                        "timestamp": m.timestamp.isoformat(),
                        "metadata": m.metadata,
                    }
                    for m in self.metrics_storage
                ]
                return json.dumps(metrics_data, indent=2)

            if format_type == "csv":
                lines = ["metric_id,metric_type,value,timestamp"]
                for m in self.metrics_storage:
                    lines.append(
                        f"{m.metric_id},{m.metric_type.value},{m.value},{m.timestamp.isoformat()}"
                    )
                return "\n".join(lines)

            raise ValueError(f"Unsupported export format: {format_type}")

        except Exception as e:
            logger.error(f"Failed to export metrics: {e}")
            return ""
