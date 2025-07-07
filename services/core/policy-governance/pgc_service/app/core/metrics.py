"""
Metrics collection and monitoring for ACGS-1 PGC Service

Provides basic metrics collection functionality for performance monitoring
and system health tracking.
"""

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


@dataclass
class MetricsData:
    """Container for metrics data."""

    counters: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    gauges: dict[str, float] = field(default_factory=dict)
    histograms: dict[str, list] = field(default_factory=lambda: defaultdict(list))
    timestamps: dict[str, float] = field(default_factory=dict)


class MetricsCollector:
    """Basic metrics collector for PGC service."""

    def __init__(self):
        self.metrics = MetricsData()
        self.start_time = time.time()

    def increment_counter(self, name: str, value: int = 1) -> None:
        """Increment a counter metric."""
        self.metrics.counters[name] += value
        self.metrics.timestamps[name] = time.time()

    def set_gauge(self, name: str, value: float) -> None:
        """Set a gauge metric."""
        self.metrics.gauges[name] = value
        self.metrics.timestamps[name] = time.time()

    def record_histogram(self, name: str, value: float) -> None:
        """Record a histogram value."""
        self.metrics.histograms[name].append(value)
        self.metrics.timestamps[name] = time.time()

    def get_metrics(self) -> dict[str, Any]:
        """Get all collected metrics."""
        return {
            "counters": dict(self.metrics.counters),
            "gauges": dict(self.metrics.gauges),
            "histograms": {k: list(v) for k, v in self.metrics.histograms.items()},
            "timestamps": dict(self.metrics.timestamps),
            "uptime_seconds": time.time() - self.start_time,
        }

    def reset_metrics(self) -> None:
        """Reset all metrics."""
        self.metrics = MetricsData()


# Global metrics collector instance
_metrics_collector = MetricsCollector()


def get_metrics() -> dict[str, Any]:
    """Get current metrics data."""
    return _metrics_collector.get_metrics()


def increment_counter(name: str, value: int = 1) -> None:
    """Increment a counter metric."""
    _metrics_collector.increment_counter(name, value)


def set_gauge(name: str, value: float) -> None:
    """Set a gauge metric."""
    _metrics_collector.set_gauge(name, value)


def record_histogram(name: str, value: float) -> None:
    """Record a histogram value."""
    _metrics_collector.record_histogram(name, value)


def reset_metrics() -> None:
    """Reset all metrics."""
    _metrics_collector.reset_metrics()


def track_execution_time(metric_name: str):
    """Decorator to track function execution time."""

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000  # Convert to ms
                record_histogram(f"{metric_name}_execution_time_ms", execution_time)
                increment_counter(f"{metric_name}_success_count")
                return result
            except Exception:
                execution_time = (time.time() - start_time) * 1000  # Convert to ms
                record_histogram(f"{metric_name}_execution_time_ms", execution_time)
                increment_counter(f"{metric_name}_error_count")
                raise

        return wrapper

    return decorator


def track_async_execution_time(metric_name: str):
    """Decorator to track async function execution time."""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000  # Convert to ms
                record_histogram(f"{metric_name}_execution_time_ms", execution_time)
                increment_counter(f"{metric_name}_success_count")
                return result
            except Exception:
                execution_time = (time.time() - start_time) * 1000  # Convert to ms
                record_histogram(f"{metric_name}_execution_time_ms", execution_time)
                increment_counter(f"{metric_name}_error_count")
                raise

        return wrapper

    return decorator
