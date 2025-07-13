"""
Constitutional Middleware Performance Metrics Collection
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive performance monitoring for constitutional validation middleware
with Prometheus metrics integration and real-time performance tracking.
"""

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)

# Prometheus metrics for constitutional validation performance
CONSTITUTIONAL_VALIDATION_TIME = Histogram(
    "acgs_constitutional_validation_seconds",
    "Time spent on constitutional validation",
    ["service", "validation_type", "result"],
    buckets=[0.0001, 0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0],
)

CONSTITUTIONAL_CACHE_HITS = Counter(
    "acgs_constitutional_cache_hits_total",
    "Constitutional validation cache hits",
    ["service", "cache_type"],
)

CONSTITUTIONAL_CACHE_MISSES = Counter(
    "acgs_constitutional_cache_misses_total",
    "Constitutional validation cache misses",
    ["service", "cache_type"],
)

CONSTITUTIONAL_COMPLIANCE_RATE = Gauge(
    "acgs_constitutional_compliance_rate",
    "Constitutional compliance rate percentage",
    ["service"],
)

CONSTITUTIONAL_VALIDATION_ERRORS = Counter(
    "acgs_constitutional_validation_errors_total",
    "Constitutional validation errors",
    ["service", "error_type"],
)

CONSTITUTIONAL_THROUGHPUT = Counter(
    "acgs_constitutional_requests_total",
    "Total constitutional validation requests",
    ["service", "endpoint", "method"],
)

CONSTITUTIONAL_PERFORMANCE_TARGET = Gauge(
    "acgs_constitutional_performance_target_ms",
    "Constitutional validation performance target in milliseconds",
    ["service"],
)

CONSTITUTIONAL_PERFORMANCE_ACHIEVED = Gauge(
    "acgs_constitutional_performance_achieved_ms",
    "Actual constitutional validation performance in milliseconds",
    ["service"],
)

# System info metric
CONSTITUTIONAL_SYSTEM_INFO = Info(
    "acgs_constitutional_system", "Constitutional validation system information"
)

# Set system info
CONSTITUTIONAL_SYSTEM_INFO.info(
    {
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "validation_type": "fast_validator",
        "performance_target": "0.5ms",
        "cache_enabled": "true",
    }
)


@dataclass
class PerformanceWindow:
    """Rolling window for performance metrics."""

    window_size: int = 1000
    values: deque = field(default_factory=deque)
    lock: threading.Lock = field(default_factory=threading.Lock)

    def add_value(self, value: float):
        """Add a value to the rolling window."""
        with self.lock:
            self.values.append(value)
            if len(self.values) > self.window_size:
                self.values.popleft()

    def get_average(self) -> float:
        """Get average of values in window."""
        with self.lock:
            if not self.values:
                return 0.0
            return sum(self.values) / len(self.values)

    def get_percentile(self, percentile: float) -> float:
        """Get percentile of values in window."""
        with self.lock:
            if not self.values:
                return 0.0
            sorted_values = sorted(self.values)
            index = int(len(sorted_values) * percentile / 100)
            return sorted_values[min(index, len(sorted_values) - 1)]


class ConstitutionalPerformanceCollector:
    """Performance metrics collector for constitutional validation."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.performance_windows = {
            "validation_time": PerformanceWindow(),
            "cache_hit_rate": PerformanceWindow(),
            "compliance_rate": PerformanceWindow(),
        }

        # Performance counters
        self.total_validations = 0
        self.successful_validations = 0
        self.cache_hits = 0
        self.cache_requests = 0

        # Performance targets
        self.performance_target_ms = 0.5

        # Set initial metrics
        CONSTITUTIONAL_PERFORMANCE_TARGET.labels(service=service_name).set(
            self.performance_target_ms
        )

        logger.info(
            f"Constitutional performance collector initialized for {service_name}"
        )

    def record_validation_time(
        self,
        validation_time_ms: float,
        validation_type: str = "full",
        result: str = "success",
    ):
        """Record validation time metrics."""
        # Update Prometheus histogram
        CONSTITUTIONAL_VALIDATION_TIME.labels(
            service=self.service_name, validation_type=validation_type, result=result
        ).observe(
            validation_time_ms / 1000
        )  # Convert to seconds

        # Update rolling window
        self.performance_windows["validation_time"].add_value(validation_time_ms)

        # Update performance gauge
        avg_time = self.performance_windows["validation_time"].get_average()
        CONSTITUTIONAL_PERFORMANCE_ACHIEVED.labels(service=self.service_name).set(
            avg_time
        )

        # Update counters
        self.total_validations += 1
        if result == "success":
            self.successful_validations += 1

    def record_cache_hit(self, cache_type: str = "hash"):
        """Record cache hit."""
        CONSTITUTIONAL_CACHE_HITS.labels(
            service=self.service_name, cache_type=cache_type
        ).inc()

        self.cache_hits += 1
        self.cache_requests += 1
        self._update_cache_hit_rate()

    def record_cache_miss(self, cache_type: str = "hash"):
        """Record cache miss."""
        CONSTITUTIONAL_CACHE_MISSES.labels(
            service=self.service_name, cache_type=cache_type
        ).inc()

        self.cache_requests += 1
        self._update_cache_hit_rate()

    def _update_cache_hit_rate(self):
        """Update cache hit rate metrics."""
        if self.cache_requests > 0:
            hit_rate = (self.cache_hits / self.cache_requests) * 100
            self.performance_windows["cache_hit_rate"].add_value(hit_rate)

    def record_compliance_result(self, is_compliant: bool):
        """Record constitutional compliance result."""
        compliance_value = 100.0 if is_compliant else 0.0
        self.performance_windows["compliance_rate"].add_value(compliance_value)

        # Update compliance rate gauge
        avg_compliance = self.performance_windows["compliance_rate"].get_average()
        CONSTITUTIONAL_COMPLIANCE_RATE.labels(service=self.service_name).set(
            avg_compliance
        )

    def record_validation_error(self, error_type: str):
        """Record validation error."""
        CONSTITUTIONAL_VALIDATION_ERRORS.labels(
            service=self.service_name, error_type=error_type
        ).inc()

    def record_request(self, endpoint: str, method: str):
        """Record constitutional validation request."""
        CONSTITUTIONAL_THROUGHPUT.labels(
            service=self.service_name, endpoint=endpoint, method=method
        ).inc()

    def get_performance_summary(self) -> dict[str, Any]:
        """Get comprehensive performance summary."""
        validation_window = self.performance_windows["validation_time"]
        cache_window = self.performance_windows["cache_hit_rate"]
        compliance_window = self.performance_windows["compliance_rate"]

        return {
            "service": self.service_name,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "performance": {
                "average_validation_time_ms": validation_window.get_average(),
                "p95_validation_time_ms": validation_window.get_percentile(95),
                "p99_validation_time_ms": validation_window.get_percentile(99),
                "target_time_ms": self.performance_target_ms,
                "target_met": validation_window.get_average()
                <= self.performance_target_ms,
            },
            "cache": {
                "hit_rate_percent": cache_window.get_average(),
                "total_requests": self.cache_requests,
                "total_hits": self.cache_hits,
            },
            "compliance": {
                "rate_percent": compliance_window.get_average(),
                "total_validations": self.total_validations,
                "successful_validations": self.successful_validations,
            },
            "timestamp": time.time(),
        }


# Global performance collectors
_performance_collectors: dict[str, ConstitutionalPerformanceCollector] = {}
_collectors_lock = threading.Lock()


def get_performance_collector(service_name: str) -> ConstitutionalPerformanceCollector:
    """Get or create performance collector for service."""
    with _collectors_lock:
        if service_name not in _performance_collectors:
            _performance_collectors[service_name] = ConstitutionalPerformanceCollector(
                service_name
            )
        return _performance_collectors[service_name]


def setup_constitutional_metrics_endpoint(app, path: str = "/constitutional/metrics"):
    """Setup constitutional metrics endpoint for FastAPI app."""

    @app.get(path)
    async def constitutional_metrics():
        """Get constitutional validation metrics in Prometheus format."""
        return generate_latest()

    @app.get(f"{path}/summary")
    async def constitutional_metrics_summary():
        """Get constitutional validation metrics summary."""
        summaries = {}
        with _collectors_lock:
            for service_name, collector in _performance_collectors.items():
                summaries[service_name] = collector.get_performance_summary()

        return {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "services": summaries,
            "system_status": {
                "total_services": len(summaries),
                "performance_targets_met": sum(
                    1 for s in summaries.values() if s["performance"]["target_met"]
                ),
                "average_compliance_rate": (
                    sum(s["compliance"]["rate_percent"] for s in summaries.values())
                    / len(summaries)
                    if summaries
                    else 0
                ),
            },
        }

    logger.info(f"Constitutional metrics endpoints configured at {path}")


# Context manager for performance tracking
class ConstitutionalPerformanceTracker:
    """Context manager for tracking constitutional validation performance."""

    def __init__(
        self,
        service_name: str,
        validation_type: str = "full",
        endpoint: str = "/",
        method: str = "GET",
    ):
        self.service_name = service_name
        self.validation_type = validation_type
        self.endpoint = endpoint
        self.method = method
        self.collector = get_performance_collector(service_name)
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        self.collector.record_request(self.endpoint, self.method)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (time.perf_counter() - self.start_time) * 1000
            result = "success" if exc_type is None else "error"

            self.collector.record_validation_time(
                duration_ms, self.validation_type, result
            )

            if exc_type:
                self.collector.record_validation_error(str(exc_type.__name__))

    def record_cache_hit(self, cache_type: str = "hash"):
        """Record cache hit during validation."""
        self.collector.record_cache_hit(cache_type)

    def record_cache_miss(self, cache_type: str = "hash"):
        """Record cache miss during validation."""
        self.collector.record_cache_miss(cache_type)

    def record_compliance_result(self, is_compliant: bool):
        """Record compliance result during validation."""
        self.collector.record_compliance_result(is_compliant)
