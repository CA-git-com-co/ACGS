"""
Performance monitoring framework with latency tracking and cache monitoring.
Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import functools
import logging
import time
from typing import Any, Callable, Dict, List, Optional

import redis.asyncio as redis
from prometheus_client import Counter, Gauge, Histogram

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Performance targets
P99_LATENCY_TARGET_MS = 5.0
THROUGHPUT_TARGET_RPS = 100.0
CACHE_HIT_RATE_TARGET = 85.0

# Prometheus metrics
REQUEST_DURATION = Histogram(
    "acgs_request_duration_seconds",
    "Request duration in seconds",
    ["service", "endpoint", "method"],
)

REQUEST_COUNT = Counter(
    "acgs_request_count_total",
    "Total request count",
    ["service", "endpoint", "method", "status"],
)

THROUGHPUT_GAUGE = Gauge(
    "acgs_throughput_requests_per_second",
    "Throughput in requests per second",
    ["service", "endpoint"],
)

CACHE_HIT_RATE = Gauge(
    "acgs_cache_hit_rate_percent",
    "Cache hit rate percentage",
    ["service", "cache_type"],
)

CACHE_OPERATIONS = Counter(
    "acgs_cache_operations_total",
    "Total cache operations",
    ["service", "cache_type", "operation", "result"],
)

P99_LATENCY_VIOLATIONS = Counter(
    "acgs_p99_latency_violations_total",
    "P99 latency violations",
    ["service", "endpoint"],
)

logger = logging.getLogger(__name__)


def track_performance_metrics(service_name: str, endpoint: str, method: str = "POST"):
    """
    Track performance metrics for an operation.

    Args:
        service_name: Name of the service
        endpoint: API endpoint
        method: HTTP method
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            status = "success"

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time

                # Record metrics
                REQUEST_DURATION.labels(service_name, endpoint, method).observe(
                    duration
                )
                REQUEST_COUNT.labels(service_name, endpoint, method, status).inc()

                # Update throughput gauge (approximation)
                THROUGHPUT_GAUGE.labels(service_name, endpoint).set(
                    1.0 / max(duration, 0.001)
                )

                # Alert on slow requests
                if duration * 1000 > P99_LATENCY_TARGET_MS:
                    P99_LATENCY_VIOLATIONS.labels(service_name, endpoint).inc()
                    logger.warning(
                        f"Performance alert: {service_name}.{endpoint} took {duration*1000:.2f}ms "
                        f"(threshold: {P99_LATENCY_TARGET_MS}ms) [hash: {CONSTITUTIONAL_HASH}]"
                    )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            status = "success"

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time

                # Record metrics
                REQUEST_DURATION.labels(service_name, endpoint, method).observe(
                    duration
                )
                REQUEST_COUNT.labels(service_name, endpoint, method, status).inc()

                # Update throughput gauge
                THROUGHPUT_GAUGE.labels(service_name, endpoint).set(
                    1.0 / max(duration, 0.001)
                )

                # Alert on slow requests
                if duration * 1000 > P99_LATENCY_TARGET_MS:
                    P99_LATENCY_VIOLATIONS.labels(service_name, endpoint).inc()
                    logger.warning(
                        f"Performance alert: {service_name}.{endpoint} took {duration*1000:.2f}ms "
                        f"(threshold: {P99_LATENCY_TARGET_MS}ms) [hash: {CONSTITUTIONAL_HASH}]"
                    )

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class CachePerformanceMonitor:
    """Monitor cache performance with hit rate tracking."""

    def __init__(self, service_name: str, cache_type: str = "redis"):
        self.service_name = service_name
        self.cache_type = cache_type
        self.hits = 0
        self.misses = 0
        self.constitutional_hash = CONSTITUTIONAL_HASH

    def record_hit(self):
        """Record a cache hit."""
        self.hits += 1
        CACHE_OPERATIONS.labels(self.service_name, self.cache_type, "get", "hit").inc()
        self._update_hit_rate()

    def record_miss(self):
        """Record a cache miss."""
        self.misses += 1
        CACHE_OPERATIONS.labels(self.service_name, self.cache_type, "get", "miss").inc()
        self._update_hit_rate()

    def record_set(self):
        """Record a cache set operation."""
        CACHE_OPERATIONS.labels(
            self.service_name, self.cache_type, "set", "success"
        ).inc()

    def record_delete(self):
        """Record a cache delete operation."""
        CACHE_OPERATIONS.labels(
            self.service_name, self.cache_type, "delete", "success"
        ).inc()

    def _update_hit_rate(self):
        """Update the hit rate gauge."""
        total_operations = self.hits + self.misses
        if total_operations > 0:
            hit_rate = (self.hits / total_operations) * 100
            CACHE_HIT_RATE.labels(self.service_name, self.cache_type).set(hit_rate)

            # Alert if hit rate is below target
            if hit_rate < CACHE_HIT_RATE_TARGET:
                logger.warning(
                    f"Cache hit rate alert: {self.service_name}.{self.cache_type} "
                    f"hit rate is {hit_rate:.2f}% (target: {CACHE_HIT_RATE_TARGET}%) "
                    f"[hash: {CONSTITUTIONAL_HASH}]"
                )

    def get_hit_rate(self) -> float:
        """Get current hit rate percentage."""
        total_operations = self.hits + self.misses
        if total_operations == 0:
            return 0.0
        return (self.hits / total_operations) * 100

    def reset_stats(self):
        """Reset hit/miss statistics."""
        self.hits = 0
        self.misses = 0


class PerformanceAnalyzer:
    """Analyze performance metrics and provide insights."""

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH

    def analyze_latency_distribution(self, durations: List[float]) -> Dict[str, float]:
        """
        Analyze latency distribution and calculate percentiles.

        Args:
            durations: List of request durations in seconds

        Returns:
            Dictionary with percentile analysis
        """
        if not durations:
            return {}

        sorted_durations = sorted(durations)
        count = len(sorted_durations)

        percentiles = {
            "p50": self._percentile(sorted_durations, 50),
            "p90": self._percentile(sorted_durations, 90),
            "p95": self._percentile(sorted_durations, 95),
            "p99": self._percentile(sorted_durations, 99),
            "mean": sum(durations) / count,
            "min": min(durations),
            "max": max(durations),
            "count": count,
        }

        # Check P99 compliance
        p99_ms = percentiles["p99"] * 1000
        percentiles["p99_compliant"] = p99_ms <= P99_LATENCY_TARGET_MS

        return percentiles

    def _percentile(self, sorted_list: List[float], percentile: float) -> float:
        """Calculate percentile from sorted list."""
        if not sorted_list:
            return 0.0

        index = (percentile / 100) * (len(sorted_list) - 1)
        if index.is_integer():
            return sorted_list[int(index)]
        else:
            lower = sorted_list[int(index)]
            upper = sorted_list[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))

    def check_performance_compliance(
        self, latency_p99_ms: float, throughput_rps: float, cache_hit_rate: float
    ) -> Dict[str, Any]:
        """
        Check if performance metrics meet compliance targets.

        Args:
            latency_p99_ms: P99 latency in milliseconds
            throughput_rps: Throughput in requests per second
            cache_hit_rate: Cache hit rate percentage

        Returns:
            Compliance check results
        """
        compliance = {
            "latency_compliant": latency_p99_ms <= P99_LATENCY_TARGET_MS,
            "throughput_compliant": throughput_rps >= THROUGHPUT_TARGET_RPS,
            "cache_hit_compliant": cache_hit_rate >= CACHE_HIT_RATE_TARGET,
            "constitutional_hash": self.constitutional_hash,
            "targets": {
                "p99_latency_ms": P99_LATENCY_TARGET_MS,
                "throughput_rps": THROUGHPUT_TARGET_RPS,
                "cache_hit_rate": CACHE_HIT_RATE_TARGET,
            },
            "actual": {
                "p99_latency_ms": latency_p99_ms,
                "throughput_rps": throughput_rps,
                "cache_hit_rate": cache_hit_rate,
            },
        }

        compliance["overall_compliant"] = all(
            [
                compliance["latency_compliant"],
                compliance["throughput_compliant"],
                compliance["cache_hit_compliant"],
            ]
        )

        return compliance


def setup_performance_monitoring(service_name: str) -> Dict[str, Any]:
    """
    Set up performance monitoring for a service.

    Args:
        service_name: Name of the service

    Returns:
        Monitoring configuration
    """
    cache_monitor = CachePerformanceMonitor(service_name)
    analyzer = PerformanceAnalyzer()

    logger.info(
        f"Performance monitoring initialized for {service_name} "
        f"[hash: {CONSTITUTIONAL_HASH}]"
    )

    return {
        "service_name": service_name,
        "cache_monitor": cache_monitor,
        "analyzer": analyzer,
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "targets": {
            "p99_latency_ms": P99_LATENCY_TARGET_MS,
            "throughput_rps": THROUGHPUT_TARGET_RPS,
            "cache_hit_rate": CACHE_HIT_RATE_TARGET,
        },
    }
