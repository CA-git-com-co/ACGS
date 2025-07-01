"""
Performance Monitoring for ACGS-1 Services

Implements comprehensive performance monitoring with Prometheus metrics,
response time tracking, and constitutional compliance scoring for all services.
"""

import asyncio
import logging
import time
from functools import wraps
from typing import Any

from prometheus_client import REGISTRY, CollectorRegistry, Counter, Gauge, Histogram

logger = logging.getLogger(__name__)


class ServiceMetrics:
    """
    Service-specific performance metrics for ACGS-1.

    Provides comprehensive metrics collection for response times,
    constitutional compliance, and service health monitoring.
    """

    def __init__(self, service_name: str, registry: CollectorRegistry | None = None):
        """
        Initialize service metrics.

        Args:
            service_name: Name of the service (e.g., 'pgc_service', 'ac_service')
            registry: Prometheus registry (uses default if None)
        """
        self.service_name = service_name
        self.registry = registry or REGISTRY

        # Response time metrics
        self.response_time_histogram = Histogram(
            f"{service_name}_response_time_seconds",
            "Response time for service endpoints",
            ["endpoint", "method", "status"],
            registry=self.registry,
        )

        # Request counter
        self.request_counter = Counter(
            f"{service_name}_requests_total",
            "Total number of requests",
            ["endpoint", "method", "status"],
            registry=self.registry,
        )

        # Error counter
        self.error_counter = Counter(
            f"{service_name}_errors_total",
            "Total number of errors",
            ["error_type", "endpoint"],
            registry=self.registry,
        )

        # Constitutional compliance metrics
        self.constitutional_compliance_gauge = Gauge(
            f"{service_name}_constitutional_compliance_score",
            "Current constitutional compliance score",
            registry=self.registry,
        )

        self.constitutional_validations_counter = Counter(
            f"{service_name}_constitutional_validations_total",
            "Total constitutional validations performed",
            ["validation_type", "result"],
            registry=self.registry,
        )

        # Service health metrics
        self.service_health_gauge = Gauge(
            f"{service_name}_health_status",
            "Service health status (1=healthy, 0=unhealthy)",
            registry=self.registry,
        )

        # Active connections
        self.active_connections_gauge = Gauge(
            f"{service_name}_active_connections",
            "Number of active connections",
            registry=self.registry,
        )

        # Cache metrics
        self.cache_hits_counter = Counter(
            f"{service_name}_cache_hits_total",
            "Total cache hits",
            ["cache_type"],
            registry=self.registry,
        )

        self.cache_misses_counter = Counter(
            f"{service_name}_cache_misses_total",
            "Total cache misses",
            ["cache_type"],
            registry=self.registry,
        )

        logger.info(f"Service metrics initialized for {service_name}")

    def record_request(
        self, endpoint: str, method: str, status_code: int, duration: float
    ):
        """
        Record request metrics.

        Args:
            endpoint: API endpoint
            method: HTTP method
            status_code: HTTP status code
            duration: Request duration in seconds
        """
        status = str(status_code)

        # Record response time
        self.response_time_histogram.labels(
            endpoint=endpoint, method=method, status=status
        ).observe(duration)

        # Record request count
        self.request_counter.labels(
            endpoint=endpoint, method=method, status=status
        ).inc()

        # Record errors for 4xx and 5xx status codes
        if status_code >= 400:
            error_type = "client_error" if status_code < 500 else "server_error"
            self.error_counter.labels(error_type=error_type, endpoint=endpoint).inc()

    def record_constitutional_validation(
        self, validation_type: str, result: str, score: float
    ):
        """
        Record constitutional validation metrics.

        Args:
            validation_type: Type of validation performed
            result: Validation result (valid/invalid/error)
            score: Compliance score (0.0-1.0)
        """
        self.constitutional_validations_counter.labels(
            validation_type=validation_type, result=result
        ).inc()

        # Update compliance score
        self.constitutional_compliance_gauge.set(score)

    def record_cache_operation(self, cache_type: str, hit: bool):
        """
        Record cache operation metrics.

        Args:
            cache_type: Type of cache (constitutional, policy, etc.)
            hit: Whether it was a cache hit or miss
        """
        if hit:
            self.cache_hits_counter.labels(cache_type=cache_type).inc()
        else:
            self.cache_misses_counter.labels(cache_type=cache_type).inc()

    def set_health_status(self, healthy: bool):
        """
        Set service health status.

        Args:
            healthy: Whether the service is healthy
        """
        self.service_health_gauge.set(1 if healthy else 0)

    def set_active_connections(self, count: int):
        """
        Set number of active connections.

        Args:
            count: Number of active connections
        """
        self.active_connections_gauge.set(count)

    def get_metrics_summary(self) -> dict[str, Any]:
        """
        Get summary of current metrics.

        Returns:
            Dictionary with current metric values
        """
        try:
            # Get current values from metrics
            total_requests = sum(
                sample.value for sample in self.request_counter.collect()[0].samples
            )

            total_errors = sum(
                sample.value for sample in self.error_counter.collect()[0].samples
            )

            error_rate = total_errors / total_requests if total_requests > 0 else 0.0

            return {
                "service_name": self.service_name,
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate": error_rate,
                "constitutional_compliance_score": self.constitutional_compliance_gauge._value._value,
                "health_status": bool(self.service_health_gauge._value._value),
                "active_connections": self.active_connections_gauge._value._value,
            }
        except Exception as e:
            logger.error(f"Failed to get metrics summary: {e}")
            return {"service_name": self.service_name, "error": str(e)}


def monitor_performance(metrics: ServiceMetrics, endpoint: str = None):
    """
    Decorator for monitoring function/endpoint performance.

    Args:
        metrics: ServiceMetrics instance
        endpoint: Endpoint name (auto-detected if None)
    """

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            endpoint_name = endpoint or func.__name__
            method = "ASYNC"
            status_code = 200

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = 500
                logger.error(f"Error in {endpoint_name}: {e}")
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_request(endpoint_name, method, status_code, duration)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            endpoint_name = endpoint or func.__name__
            method = "SYNC"
            status_code = 200

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                status_code = 500
                logger.error(f"Error in {endpoint_name}: {e}")
                raise
            finally:
                duration = time.time() - start_time
                metrics.record_request(endpoint_name, method, status_code, duration)

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


class PerformanceMonitor:
    """
    Centralized performance monitoring for ACGS-1 services.

    Provides system-wide performance monitoring, alerting,
    and constitutional compliance tracking.
    """

    def __init__(self):
        """Initialize performance monitor."""
        self.service_metrics: dict[str, ServiceMetrics] = {}
        self.performance_targets = {
            "response_time_p95": 0.5,  # 500ms
            "error_rate": 0.01,  # 1%
            "constitutional_compliance": 0.95,  # 95%
            "uptime": 0.995,  # 99.5%
        }
        logger.info("Performance monitor initialized")

    def register_service(self, service_name: str) -> ServiceMetrics:
        """
        Register a service for monitoring.

        Args:
            service_name: Name of the service

        Returns:
            ServiceMetrics instance for the service
        """
        if service_name not in self.service_metrics:
            self.service_metrics[service_name] = ServiceMetrics(service_name)
            logger.info(f"Registered service for monitoring: {service_name}")

        return self.service_metrics[service_name]

    def get_service_metrics(self, service_name: str) -> ServiceMetrics | None:
        """
        Get metrics for a specific service.

        Args:
            service_name: Name of the service

        Returns:
            ServiceMetrics instance or None
        """
        return self.service_metrics.get(service_name)

    def get_system_health(self) -> dict[str, Any]:
        """
        Get overall system health status.

        Returns:
            System health summary
        """
        total_services = len(self.service_metrics)
        healthy_services = 0
        total_requests = 0
        total_errors = 0
        compliance_scores = []

        service_summaries = {}

        for service_name, metrics in self.service_metrics.items():
            summary = metrics.get_metrics_summary()
            service_summaries[service_name] = summary

            if summary.get("health_status", False):
                healthy_services += 1

            total_requests += summary.get("total_requests", 0)
            total_errors += summary.get("total_errors", 0)

            compliance_score = summary.get("constitutional_compliance_score", 0)
            if compliance_score > 0:
                compliance_scores.append(compliance_score)

        # Calculate system-wide metrics
        system_error_rate = total_errors / total_requests if total_requests > 0 else 0.0
        avg_compliance = (
            sum(compliance_scores) / len(compliance_scores)
            if compliance_scores
            else 0.0
        )
        system_uptime = healthy_services / total_services if total_services > 0 else 0.0

        # Determine overall health
        health_status = "healthy"
        if system_uptime < self.performance_targets["uptime"]:
            health_status = "critical"
        elif (
            system_error_rate > self.performance_targets["error_rate"]
            or avg_compliance < self.performance_targets["constitutional_compliance"]
        ):
            health_status = "degraded"

        return {
            "overall_health": health_status,
            "system_metrics": {
                "total_services": total_services,
                "healthy_services": healthy_services,
                "system_uptime": system_uptime,
                "total_requests": total_requests,
                "total_errors": total_errors,
                "system_error_rate": system_error_rate,
                "avg_constitutional_compliance": avg_compliance,
            },
            "performance_targets": self.performance_targets,
            "service_summaries": service_summaries,
            "timestamp": time.time(),
        }


# Global performance monitor instance
_performance_monitor = PerformanceMonitor()


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    return _performance_monitor


def get_service_metrics(service_name: str) -> ServiceMetrics:
    """
    Get or create service metrics.

    Args:
        service_name: Name of the service

    Returns:
        ServiceMetrics instance
    """
    return _performance_monitor.register_service(service_name)
