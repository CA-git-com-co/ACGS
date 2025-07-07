"""
Advanced Metrics Collection System for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Production-grade metrics collection with multiple metric types and backends.
"""

import asyncio
import logging
import statistics
import threading
import time
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Types of metrics supported."""

    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    TIMER = "timer"
    SUMMARY = "summary"


@dataclass
class MetricValue:
    """Represents a single metric measurement."""

    name: str
    value: Union[int, float]
    timestamp: datetime
    tags: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.name,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "tags": self.tags,
            "type": self.metric_type.value,
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


@dataclass
class HistogramBucket:
    """Histogram bucket for distribution metrics."""

    upper_bound: float
    count: int = 0


class Metric(ABC):
    """Abstract base class for metrics."""

    def __init__(self, name: str, description: str = None, tags: Dict[str, str] = None):
        self.name = name
        self.description = description or name
        self.tags = tags or {}
        self.created_at = datetime.utcnow()
        self._lock = threading.Lock()

    @abstractmethod
    def get_value(self) -> MetricValue:
        """Get current metric value."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset metric to initial state."""
        pass


class Counter(Metric):
    """Counter metric that only increases."""

    def __init__(self, name: str, description: str = None, tags: Dict[str, str] = None):
        super().__init__(name, description, tags)
        self._value = 0

    def increment(self, value: Union[int, float] = 1) -> None:
        """Increment counter by value."""
        if value < 0:
            raise ValueError("Counter value must be non-negative")

        with self._lock:
            self._value += value

    def get_value(self) -> MetricValue:
        """Get current counter value."""
        with self._lock:
            return MetricValue(
                name=self.name,
                value=self._value,
                timestamp=datetime.utcnow(),
                tags=self.tags,
                metric_type=MetricType.COUNTER,
            )

    def reset(self) -> None:
        """Reset counter to zero."""
        with self._lock:
            self._value = 0


class Gauge(Metric):
    """Gauge metric that can increase or decrease."""

    def __init__(self, name: str, description: str = None, tags: Dict[str, str] = None):
        super().__init__(name, description, tags)
        self._value = 0

    def set(self, value: Union[int, float]) -> None:
        """Set gauge to specific value."""
        with self._lock:
            self._value = value

    def increment(self, value: Union[int, float] = 1) -> None:
        """Increment gauge by value."""
        with self._lock:
            self._value += value

    def decrement(self, value: Union[int, float] = 1) -> None:
        """Decrement gauge by value."""
        with self._lock:
            self._value -= value

    def get_value(self) -> MetricValue:
        """Get current gauge value."""
        with self._lock:
            return MetricValue(
                name=self.name,
                value=self._value,
                timestamp=datetime.utcnow(),
                tags=self.tags,
                metric_type=MetricType.GAUGE,
            )

    def reset(self) -> None:
        """Reset gauge to zero."""
        with self._lock:
            self._value = 0


class Histogram(Metric):
    """Histogram metric for distribution measurements."""

    def __init__(
        self,
        name: str,
        description: str = None,
        tags: Dict[str, str] = None,
        buckets: List[float] = None,
    ):
        super().__init__(name, description, tags)

        # Default buckets if none provided
        if buckets is None:
            buckets = [
                0.005,
                0.01,
                0.025,
                0.05,
                0.075,
                0.1,
                0.25,
                0.5,
                0.75,
                1.0,
                2.5,
                5.0,
                7.5,
                10.0,
                float("inf"),
            ]

        self._buckets = [HistogramBucket(bound) for bound in sorted(buckets)]
        self._sum = 0.0
        self._count = 0
        self._samples = deque(maxlen=1000)  # Keep last 1000 samples for percentiles

    def observe(self, value: Union[int, float]) -> None:
        """Record an observation."""
        with self._lock:
            self._sum += value
            self._count += 1
            self._samples.append(value)

            # Update buckets
            for bucket in self._buckets:
                if value <= bucket.upper_bound:
                    bucket.count += 1

    def get_value(self) -> MetricValue:
        """Get histogram statistics."""
        with self._lock:
            percentiles = {}
            if self._samples:
                sorted_samples = sorted(self._samples)
                percentiles = {
                    "p50": statistics.median(sorted_samples),
                    "p90": (
                        statistics.quantiles(sorted_samples, n=10)[8]
                        if len(sorted_samples) >= 10
                        else sorted_samples[-1]
                    ),
                    "p95": (
                        statistics.quantiles(sorted_samples, n=20)[18]
                        if len(sorted_samples) >= 20
                        else sorted_samples[-1]
                    ),
                    "p99": (
                        statistics.quantiles(sorted_samples, n=100)[98]
                        if len(sorted_samples) >= 100
                        else sorted_samples[-1]
                    ),
                }

            bucket_data = [
                {"upper_bound": bucket.upper_bound, "count": bucket.count}
                for bucket in self._buckets
            ]

            return MetricValue(
                name=self.name,
                value={
                    "count": self._count,
                    "sum": self._sum,
                    "average": self._sum / max(self._count, 1),
                    "buckets": bucket_data,
                    "percentiles": percentiles,
                },
                timestamp=datetime.utcnow(),
                tags=self.tags,
                metric_type=MetricType.HISTOGRAM,
            )

    def reset(self) -> None:
        """Reset histogram."""
        with self._lock:
            for bucket in self._buckets:
                bucket.count = 0
            self._sum = 0.0
            self._count = 0
            self._samples.clear()


class Timer(Metric):
    """Timer metric for measuring durations."""

    def __init__(self, name: str, description: str = None, tags: Dict[str, str] = None):
        super().__init__(name, description, tags)
        self._histogram = Histogram(f"{name}_duration", f"{description} duration")
        self._active_timers: Dict[str, float] = {}

    def start(self, timer_id: str = "default") -> None:
        """Start timing operation."""
        with self._lock:
            self._active_timers[timer_id] = time.time()

    def stop(self, timer_id: str = "default") -> float:
        """Stop timing operation and record duration."""
        with self._lock:
            start_time = self._active_timers.pop(timer_id, None)
            if start_time is None:
                raise ValueError(f"Timer '{timer_id}' was not started")

            duration = time.time() - start_time
            self._histogram.observe(duration)
            return duration

    def time_operation(self, operation_id: str = None):
        """Context manager for timing operations."""
        return TimerContext(self, operation_id or "default")

    def get_value(self) -> MetricValue:
        """Get timer statistics."""
        histogram_value = self._histogram.get_value()
        return MetricValue(
            name=self.name,
            value=histogram_value.value,
            timestamp=datetime.utcnow(),
            tags=self.tags,
            metric_type=MetricType.TIMER,
        )

    def reset(self) -> None:
        """Reset timer."""
        with self._lock:
            self._histogram.reset()
            self._active_timers.clear()


class TimerContext:
    """Context manager for timer operations."""

    def __init__(self, timer: Timer, operation_id: str):
        self.timer = timer
        self.operation_id = operation_id
        self.start_time = None

    def __enter__(self):
        self.timer.start(self.operation_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.timer.stop(self.operation_id)


class MetricsCollector:
    """Central metrics collection and management system."""

    def __init__(self, name: str = "acgs_metrics"):
        self.name = name
        self._metrics: Dict[str, Metric] = {}
        self._exporters: List[Callable[[List[MetricValue]], None]] = []
        self._export_interval = 60.0  # Export every minute
        self._export_task: Optional[asyncio.Task] = None
        self._running = False
        self._lock = threading.Lock()

    def register_metric(self, metric: Metric) -> None:
        """Register a metric for collection."""
        with self._lock:
            self._metrics[metric.name] = metric
            logger.info(f"Registered metric: {metric.name}")

    def get_metric(self, name: str) -> Optional[Metric]:
        """Get metric by name."""
        return self._metrics.get(name)

    def counter(
        self, name: str, description: str = None, tags: Dict[str, str] = None
    ) -> Counter:
        """Create or get a counter metric."""
        with self._lock:
            if name in self._metrics:
                metric = self._metrics[name]
                if not isinstance(metric, Counter):
                    raise ValueError(f"Metric {name} exists but is not a Counter")
                return metric

            counter = Counter(name, description, tags)
            self._metrics[name] = counter
            return counter

    def gauge(
        self, name: str, description: str = None, tags: Dict[str, str] = None
    ) -> Gauge:
        """Create or get a gauge metric."""
        with self._lock:
            if name in self._metrics:
                metric = self._metrics[name]
                if not isinstance(metric, Gauge):
                    raise ValueError(f"Metric {name} exists but is not a Gauge")
                return metric

            gauge = Gauge(name, description, tags)
            self._metrics[name] = gauge
            return gauge

    def histogram(
        self,
        name: str,
        description: str = None,
        tags: Dict[str, str] = None,
        buckets: List[float] = None,
    ) -> Histogram:
        """Create or get a histogram metric."""
        with self._lock:
            if name in self._metrics:
                metric = self._metrics[name]
                if not isinstance(metric, Histogram):
                    raise ValueError(f"Metric {name} exists but is not a Histogram")
                return metric

            histogram = Histogram(name, description, tags, buckets)
            self._metrics[name] = histogram
            return histogram

    def timer(
        self, name: str, description: str = None, tags: Dict[str, str] = None
    ) -> Timer:
        """Create or get a timer metric."""
        with self._lock:
            if name in self._metrics:
                metric = self._metrics[name]
                if not isinstance(metric, Timer):
                    raise ValueError(f"Metric {name} exists but is not a Timer")
                return metric

            timer = Timer(name, description, tags)
            self._metrics[name] = timer
            return timer

    def add_exporter(self, exporter: Callable[[List[MetricValue]], None]) -> None:
        """Add a metrics exporter."""
        self._exporters.append(exporter)
        logger.info("Added metrics exporter")

    def collect_all(self) -> List[MetricValue]:
        """Collect all current metric values."""
        with self._lock:
            values = []
            for metric in self._metrics.values():
                try:
                    values.append(metric.get_value())
                except Exception as e:
                    logger.error(f"Error collecting metric {metric.name}: {e}")
            return values

    async def export_metrics(self) -> None:
        """Export metrics to all registered exporters."""
        if not self._exporters:
            return

        try:
            values = self.collect_all()
            for exporter in self._exporters:
                try:
                    exporter(values)
                except Exception as e:
                    logger.error(f"Error in metrics exporter: {e}")
        except Exception as e:
            logger.error(f"Error collecting metrics for export: {e}")

    async def start_export_loop(self) -> None:
        """Start automatic metrics export loop."""
        if self._running:
            return

        self._running = True
        logger.info(
            f"Starting metrics export loop (interval: {self._export_interval}s)"
        )

        while self._running:
            try:
                await self.export_metrics()
                await asyncio.sleep(self._export_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in metrics export loop: {e}")
                await asyncio.sleep(self._export_interval)

    def stop_export_loop(self) -> None:
        """Stop automatic metrics export loop."""
        self._running = False
        if self._export_task:
            self._export_task.cancel()

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of all metrics."""
        with self._lock:
            return {
                "collector_name": self.name,
                "total_metrics": len(self._metrics),
                "metric_types": {
                    metric_type.value: sum(
                        1
                        for m in self._metrics.values()
                        if m.get_value().metric_type == metric_type
                    )
                    for metric_type in MetricType
                },
                "metrics": {
                    name: {
                        "type": metric.get_value().metric_type.value,
                        "description": metric.description,
                        "tags": metric.tags,
                    }
                    for name, metric in self._metrics.items()
                },
                "exporters_count": len(self._exporters),
                "constitutional_hash": "cdd01ef066bc6cf2",
            }


# Global metrics collector
_global_collector = MetricsCollector()


def get_metrics_collector() -> MetricsCollector:
    """Get the global metrics collector."""
    return _global_collector


# Convenience functions for common metrics
def metric_counter(
    name: str, description: str = None, tags: Dict[str, str] = None
) -> Counter:
    """Create or get a counter metric."""
    return _global_collector.counter(name, description, tags)


def metric_gauge(
    name: str, description: str = None, tags: Dict[str, str] = None
) -> Gauge:
    """Create or get a gauge metric."""
    return _global_collector.gauge(name, description, tags)


def metric_histogram(
    name: str,
    description: str = None,
    tags: Dict[str, str] = None,
    buckets: List[float] = None,
) -> Histogram:
    """Create or get a histogram metric."""
    return _global_collector.histogram(name, description, tags, buckets)


def metric_timer(
    name: str, description: str = None, tags: Dict[str, str] = None
) -> Timer:
    """Create or get a timer metric."""
    return _global_collector.timer(name, description, tags)


# Common exporters
def prometheus_exporter(metrics: List[MetricValue]) -> None:
    """Export metrics in Prometheus format (to stdout)."""
    logger.info(f"Exporting {len(metrics)} metrics to Prometheus format")
    for metric in metrics:
        # This is a basic implementation - in production, use prometheus_client
        print(f"# HELP {metric.name} {metric.metric_type.value}")
        print(f"# TYPE {metric.name} {metric.metric_type.value}")

        if metric.metric_type == MetricType.HISTOGRAM:
            value_dict = metric.value
            print(f"{metric.name}_count {value_dict['count']}")
            print(f"{metric.name}_sum {value_dict['sum']}")
        else:
            print(f"{metric.name} {metric.value}")


def json_exporter(metrics: List[MetricValue]) -> None:
    """Export metrics in JSON format (to log)."""
    import json

    logger.info("Metrics export (JSON):")
    for metric in metrics:
        logger.info(json.dumps(metric.to_dict(), indent=2))


# Setup default metrics
def setup_default_metrics() -> None:
    """Set up common system metrics."""
    collector = get_metrics_collector()

    # System metrics
    collector.gauge("system_cpu_usage", "System CPU usage percentage")
    collector.gauge("system_memory_usage", "System memory usage percentage")
    collector.gauge("system_disk_usage", "System disk usage percentage")

    # Application metrics
    collector.counter("http_requests_total", "Total HTTP requests")
    collector.histogram("http_request_duration", "HTTP request duration")
    collector.counter("database_queries_total", "Total database queries")
    collector.histogram("database_query_duration", "Database query duration")

    # Cache metrics
    collector.counter("cache_hits_total", "Total cache hits")
    collector.counter("cache_misses_total", "Total cache misses")

    # Constitutional compliance metrics
    collector.counter(
        "constitutional_validations_total", "Total constitutional validations"
    )
    collector.counter(
        "constitutional_violations_total", "Total constitutional violations"
    )

    logger.info("Default metrics configured")
