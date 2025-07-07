"""
Prometheus metrics middleware for FastAPI with constitutional compliance.
Constitutional Hash: cdd01ef066bc6cf2
"""

import time
from typing import Callable

from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Gauge, Histogram, make_asgi_app
from starlette.middleware.base import BaseHTTPMiddleware

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Metrics
REQUEST_DURATION = Histogram(
    "acgs_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["service", "endpoint", "method", "status_code"],
)

REQUEST_COUNT = Counter(
    "acgs_http_request_count_total",
    "Total HTTP request count",
    ["service", "endpoint", "method", "status_code"],
)

ACTIVE_REQUESTS = Gauge(
    "acgs_http_active_requests", "Number of active HTTP requests", ["service"]
)

REQUEST_SIZE = Histogram(
    "acgs_http_request_size_bytes",
    "HTTP request size in bytes",
    ["service", "endpoint", "method"],
)

RESPONSE_SIZE = Histogram(
    "acgs_http_response_size_bytes",
    "HTTP response size in bytes",
    ["service", "endpoint", "method", "status_code"],
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """Middleware for capturing Prometheus metrics with constitutional compliance."""

    def __init__(self, app: FastAPI, service_name: str):
        super().__init__(app)
        self.service_name = service_name
        self.constitutional_hash = CONSTITUTIONAL_HASH

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip metrics endpoint to avoid recursion
        if request.url.path == "/metrics":
            return await call_next(request)

        # Extract endpoint for metrics
        endpoint = request.url.path
        method = request.method

        # Track active requests
        ACTIVE_REQUESTS.labels(self.service_name).inc()

        # Track request duration
        start_time = time.time()

        # Track request size
        content_length = request.headers.get("content-length")
        if content_length:
            request_size = int(content_length)
            REQUEST_SIZE.labels(self.service_name, endpoint, method).observe(
                request_size
            )

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time
            status_code = str(response.status_code)

            # Record metrics
            REQUEST_DURATION.labels(
                self.service_name, endpoint, method, status_code
            ).observe(duration)

            REQUEST_COUNT.labels(self.service_name, endpoint, method, status_code).inc()

            # Track response size
            response_content = getattr(response, "body", b"")
            if response_content:
                response_size = len(response_content)
                RESPONSE_SIZE.labels(
                    self.service_name, endpoint, method, status_code
                ).observe(response_size)

            # Add constitutional hash to response headers
            response.headers["X-Constitutional-Hash"] = self.constitutional_hash
            response.headers["X-Service-Name"] = self.service_name
            response.headers["X-Response-Time"] = str(round(duration * 1000, 2))

            return response

        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            REQUEST_DURATION.labels(self.service_name, endpoint, method, "500").observe(
                duration
            )

            REQUEST_COUNT.labels(self.service_name, endpoint, method, "500").inc()

            raise
        finally:
            # Decrement active requests
            ACTIVE_REQUESTS.labels(self.service_name).dec()


def setup_prometheus_middleware(app: FastAPI, service_name: str):
    """
    Set up Prometheus middleware for a FastAPI application.

    Args:
        app: FastAPI application instance
        service_name: Name of the service for metrics labeling
    """
    # Add Prometheus middleware
    app.add_middleware(PrometheusMiddleware, service_name=service_name)

    # Mount metrics endpoint
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    return {
        "service_name": service_name,
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "metrics_endpoint": "/metrics",
    }


def get_service_metrics(service_name: str) -> dict:
    """
    Get current metrics for a service.

    Args:
        service_name: Name of the service

    Returns:
        Dictionary with current metrics
    """
    # This would typically query the metrics registry
    # For now, return placeholder data
    return {
        "service_name": service_name,
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "active_requests": 0,  # Would get from ACTIVE_REQUESTS gauge
        "total_requests": 0,  # Would get from REQUEST_COUNT counter
        "avg_response_time": 0.0,  # Would calculate from REQUEST_DURATION
        "metrics_available": [
            "acgs_http_request_duration_seconds",
            "acgs_http_request_count_total",
            "acgs_http_active_requests",
            "acgs_http_request_size_bytes",
            "acgs_http_response_size_bytes",
        ],
    }


"""
ACGS Comprehensive Prometheus Metrics Middleware
Constitutional Hash: cdd01ef066bc6cf2

Standardized Prometheus metrics collection for all ACGS services with:
- Request/response metrics
- Constitutional compliance metrics
- Performance metrics
- Business metrics
- System metrics
- Custom metrics support
"""

import logging
import time
import traceback
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

import psutil
from fastapi import FastAPI, Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    CollectorRegistry,
    Counter,
)
from prometheus_client import Enum as PrometheusEnum
from prometheus_client import (
    Gauge,
    Histogram,
    generate_latest,
    multiprocess,
)

logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class MetricType(str, Enum):
    """Types of metrics for categorization."""

    SYSTEM = "system"
    BUSINESS = "business"
    CONSTITUTIONAL = "constitutional"
    PERFORMANCE = "performance"
    SECURITY = "security"
    CUSTOM = "custom"


class ACGSPrometheusMetrics:
    """Comprehensive Prometheus metrics for ACGS services."""

    def __init__(self, service_name: str, enable_multiprocess: bool = False):
        self.service_name = service_name
        self.constitutional_hash = CONSTITUTIONAL_HASH

        # Setup registry
        if enable_multiprocess:
            self.registry = CollectorRegistry()
            multiprocess.MultiProcessCollector(self.registry)
        else:
            self.registry = REGISTRY

        # Core HTTP metrics
        self.http_requests_total = Counter(
            "acgs_http_requests_total",
            "Total number of HTTP requests",
            ["service", "method", "endpoint", "status"],
            registry=self.registry,
        )

        self.http_request_duration_seconds = Histogram(
            "acgs_http_request_duration_seconds",
            "HTTP request duration in seconds",
            ["service", "method", "endpoint"],
            buckets=[
                0.001,
                0.005,
                0.01,
                0.025,
                0.05,
                0.1,
                0.25,
                0.5,
                1.0,
                2.5,
                5.0,
                10.0,
            ],
            registry=self.registry,
        )

        self.http_request_size_bytes = Histogram(
            "acgs_http_request_size_bytes",
            "HTTP request size in bytes",
            ["service", "method", "endpoint"],
            registry=self.registry,
        )

        self.http_response_size_bytes = Histogram(
            "acgs_http_response_size_bytes",
            "HTTP response size in bytes",
            ["service", "method", "endpoint"],
            registry=self.registry,
        )

        # Constitutional compliance metrics
        self.constitutional_validations_total = Counter(
            "acgs_constitutional_validations_total",
            "Total constitutional validations performed",
            ["service", "validation_type", "result"],
            registry=self.registry,
        )

        self.constitutional_compliance_score = Gauge(
            "acgs_constitutional_compliance_score",
            "Current constitutional compliance score (0-1)",
            ["service"],
            registry=self.registry,
        )

        self.constitutional_hash_validations = Counter(
            "acgs_constitutional_hash_validations_total",
            "Constitutional hash validation attempts",
            ["service", "hash", "valid"],
            registry=self.registry,
        )

        # Performance metrics
        self.cache_operations_total = Counter(
            "acgs_cache_operations_total",
            "Total cache operations",
            ["service", "operation", "result"],
            registry=self.registry,
        )

        self.cache_hit_rate = Gauge(
            "acgs_cache_hit_rate",
            "Cache hit rate percentage",
            ["service", "cache_type"],
            registry=self.registry,
        )

        self.database_operations_total = Counter(
            "acgs_database_operations_total",
            "Total database operations",
            ["service", "operation", "table", "result"],
            registry=self.registry,
        )

        self.database_operation_duration_seconds = Histogram(
            "acgs_database_operation_duration_seconds",
            "Database operation duration in seconds",
            ["service", "operation", "table"],
            registry=self.registry,
        )

        # System metrics
        self.system_cpu_usage_percent = Gauge(
            "acgs_system_cpu_usage_percent",
            "System CPU usage percentage",
            ["service"],
            registry=self.registry,
        )

        self.system_memory_usage_bytes = Gauge(
            "acgs_system_memory_usage_bytes",
            "System memory usage in bytes",
            ["service", "type"],
            registry=self.registry,
        )

        self.system_disk_usage_bytes = Gauge(
            "acgs_system_disk_usage_bytes",
            "System disk usage in bytes",
            ["service", "type"],
            registry=self.registry,
        )

        # Service health metrics
        self.service_health_status = PrometheusEnum(
            "acgs_service_health_status",
            "Service health status",
            ["service"],
            states=["healthy", "unhealthy", "degraded", "starting", "shutting_down"],
            registry=self.registry,
        )

        self.service_uptime_seconds = Gauge(
            "acgs_service_uptime_seconds",
            "Service uptime in seconds",
            ["service"],
            registry=self.registry,
        )

        self.dependency_health_status = Gauge(
            "acgs_dependency_health_status",
            "Dependency health status (1=healthy, 0=unhealthy)",
            ["service", "dependency"],
            registry=self.registry,
        )

        # Business metrics
        self.governance_decisions_total = Counter(
            "acgs_governance_decisions_total",
            "Total governance decisions made",
            ["service", "decision_type", "outcome"],
            registry=self.registry,
        )

        self.policy_evaluations_total = Counter(
            "acgs_policy_evaluations_total",
            "Total policy evaluations",
            ["service", "policy_type", "result"],
            registry=self.registry,
        )

        self.ai_model_requests_total = Counter(
            "acgs_ai_model_requests_total",
            "Total AI model requests",
            ["service", "model", "provider"],
            registry=self.registry,
        )

        self.ai_model_response_time_seconds = Histogram(
            "acgs_ai_model_response_time_seconds",
            "AI model response time in seconds",
            ["service", "model", "provider"],
            registry=self.registry,
        )

        # Security metrics
        self.auth_attempts_total = Counter(
            "acgs_auth_attempts_total",
            "Total authentication attempts",
            ["service", "result"],
            registry=self.registry,
        )

        self.rate_limit_hits_total = Counter(
            "acgs_rate_limit_hits_total",
            "Total rate limit hits",
            ["service", "endpoint"],
            registry=self.registry,
        )

        self.security_violations_total = Counter(
            "acgs_security_violations_total",
            "Total security violations detected",
            ["service", "violation_type"],
            registry=self.registry,
        )

        # Error metrics
        self.errors_total = Counter(
            "acgs_errors_total",
            "Total errors by type",
            ["service", "error_type", "severity"],
            registry=self.registry,
        )

        # Custom metrics registry
        self.custom_metrics: Dict[str, Any] = {}

        # Initialize service-specific metrics
        self.service_uptime_seconds.labels(service=self.service_name).set_function(
            lambda: time.time() - self._start_time
        )
        self._start_time = time.time()

        logger.info(f"Prometheus metrics initialized for {self.service_name}")

    def record_http_request(
        self,
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
        request_size: int = 0,
        response_size: int = 0,
    ):
        """Record HTTP request metrics."""
        self.http_requests_total.labels(
            service=self.service_name,
            method=method,
            endpoint=endpoint,
            status=str(status_code),
        ).inc()

        self.http_request_duration_seconds.labels(
            service=self.service_name, method=method, endpoint=endpoint
        ).observe(duration)

        if request_size > 0:
            self.http_request_size_bytes.labels(
                service=self.service_name, method=method, endpoint=endpoint
            ).observe(request_size)

        if response_size > 0:
            self.http_response_size_bytes.labels(
                service=self.service_name, method=method, endpoint=endpoint
            ).observe(response_size)

    def record_constitutional_validation(
        self, validation_type: str, result: str, score: Optional[float] = None
    ):
        """Record constitutional compliance validation."""
        self.constitutional_validations_total.labels(
            service=self.service_name, validation_type=validation_type, result=result
        ).inc()

        if score is not None:
            self.constitutional_compliance_score.labels(service=self.service_name).set(
                score
            )

    def record_constitutional_hash_validation(self, hash_value: str, is_valid: bool):
        """Record constitutional hash validation."""
        self.constitutional_hash_validations.labels(
            service=self.service_name, hash=hash_value, valid=str(is_valid).lower()
        ).inc()

    def record_cache_operation(
        self, operation: str, result: str, cache_type: str = "default"
    ):
        """Record cache operation metrics."""
        self.cache_operations_total.labels(
            service=self.service_name, operation=operation, result=result
        ).inc()

    def update_cache_hit_rate(self, hit_rate: float, cache_type: str = "default"):
        """Update cache hit rate."""
        self.cache_hit_rate.labels(
            service=self.service_name, cache_type=cache_type
        ).set(hit_rate)

    def record_database_operation(
        self, operation: str, table: str, result: str, duration: Optional[float] = None
    ):
        """Record database operation metrics."""
        self.database_operations_total.labels(
            service=self.service_name, operation=operation, table=table, result=result
        ).inc()

        if duration is not None:
            self.database_operation_duration_seconds.labels(
                service=self.service_name, operation=operation, table=table
            ).observe(duration)

    def update_system_metrics(self):
        """Update system resource metrics."""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent()
            self.system_cpu_usage_percent.labels(service=self.service_name).set(
                cpu_percent
            )

            # Memory usage
            memory = psutil.virtual_memory()
            self.system_memory_usage_bytes.labels(
                service=self.service_name, type="used"
            ).set(memory.used)
            self.system_memory_usage_bytes.labels(
                service=self.service_name, type="available"
            ).set(memory.available)

            # Disk usage
            disk = psutil.disk_usage("/")
            self.system_disk_usage_bytes.labels(
                service=self.service_name, type="used"
            ).set(disk.used)
            self.system_disk_usage_bytes.labels(
                service=self.service_name, type="free"
            ).set(disk.free)

        except Exception as e:
            logger.warning(f"Failed to update system metrics: {e}")

    def update_service_health(self, status: str):
        """Update service health status."""
        self.service_health_status.labels(service=self.service_name).state(status)

    def update_dependency_health(self, dependency: str, is_healthy: bool):
        """Update dependency health status."""
        self.dependency_health_status.labels(
            service=self.service_name, dependency=dependency
        ).set(1 if is_healthy else 0)

    def record_governance_decision(self, decision_type: str, outcome: str):
        """Record governance decision metrics."""
        self.governance_decisions_total.labels(
            service=self.service_name, decision_type=decision_type, outcome=outcome
        ).inc()

    def record_policy_evaluation(self, policy_type: str, result: str):
        """Record policy evaluation metrics."""
        self.policy_evaluations_total.labels(
            service=self.service_name, policy_type=policy_type, result=result
        ).inc()

    def record_ai_model_request(
        self, model: str, provider: str, response_time: Optional[float] = None
    ):
        """Record AI model request metrics."""
        self.ai_model_requests_total.labels(
            service=self.service_name, model=model, provider=provider
        ).inc()

        if response_time is not None:
            self.ai_model_response_time_seconds.labels(
                service=self.service_name, model=model, provider=provider
            ).observe(response_time)

    def record_auth_attempt(self, result: str):
        """Record authentication attempt."""
        self.auth_attempts_total.labels(service=self.service_name, result=result).inc()

    def record_rate_limit_hit(self, endpoint: str):
        """Record rate limit hit."""
        self.rate_limit_hits_total.labels(
            service=self.service_name, endpoint=endpoint
        ).inc()

    def record_security_violation(self, violation_type: str):
        """Record security violation."""
        self.security_violations_total.labels(
            service=self.service_name, violation_type=violation_type
        ).inc()

    def record_error(self, error_type: str, severity: str = "error"):
        """Record error metrics."""
        self.errors_total.labels(
            service=self.service_name, error_type=error_type, severity=severity
        ).inc()

    def add_custom_metric(
        self, name: str, metric_type: str, help_text: str, labels: List[str] = None
    ):
        """Add a custom metric."""
        labels = labels or []
        full_name = f"acgs_{name}"

        if metric_type == "counter":
            metric = Counter(
                full_name, help_text, labels + ["service"], registry=self.registry
            )
        elif metric_type == "gauge":
            metric = Gauge(
                full_name, help_text, labels + ["service"], registry=self.registry
            )
        elif metric_type == "histogram":
            metric = Histogram(
                full_name, help_text, labels + ["service"], registry=self.registry
            )
        else:
            raise ValueError(f"Unsupported metric type: {metric_type}")

        self.custom_metrics[name] = metric
        return metric

    def get_metrics_data(self) -> str:
        """Get formatted metrics data."""
        return generate_latest(self.registry)


class PrometheusMetricsMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for automatic Prometheus metrics collection."""

    def __init__(self, app: FastAPI, metrics: ACGSPrometheusMetrics):
        super().__init__(app)
        self.metrics = metrics
        self.service_name = metrics.service_name

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics."""
        start_time = time.time()

        # Get request info
        method = request.method
        path = str(request.url.path)
        endpoint = self._normalize_endpoint(path)

        # Get request size
        request_size = 0
        if hasattr(request, "headers") and "content-length" in request.headers:
            try:
                request_size = int(request.headers["content-length"])
            except (ValueError, TypeError):
                pass

        try:
            # Process request
            response = await call_next(request)

            # Calculate metrics
            duration = time.time() - start_time
            status_code = response.status_code

            # Get response size
            response_size = 0
            if hasattr(response, "headers") and "content-length" in response.headers:
                try:
                    response_size = int(response.headers["content-length"])
                except (ValueError, TypeError):
                    pass

            # Record metrics
            self.metrics.record_http_request(
                method=method,
                endpoint=endpoint,
                status_code=status_code,
                duration=duration,
                request_size=request_size,
                response_size=response_size,
            )

            # Add constitutional hash header
            response.headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH

            return response

        except Exception as e:
            # Record error
            duration = time.time() - start_time
            error_type = type(e).__name__

            self.metrics.record_error(error_type, "error")
            self.metrics.record_http_request(
                method=method,
                endpoint=endpoint,
                status_code=500,
                duration=duration,
                request_size=request_size,
                response_size=0,
            )

            raise

    def _normalize_endpoint(self, path: str) -> str:
        """Normalize endpoint path for metrics."""
        # Remove query parameters
        if "?" in path:
            path = path.split("?")[0]

        # Replace dynamic path segments with placeholders
        # This is a simple implementation - you might want to use FastAPI's route info
        import re

        # Replace UUIDs with {id}
        path = re.sub(
            r"/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
            "/{id}",
            path,
        )

        # Replace numeric IDs with {id}
        path = re.sub(r"/\d+", "/{id}", path)

        return path


def setup_prometheus_metrics(
    app: FastAPI,
    service_name: str,
    enable_multiprocess: bool = False,
    metrics_endpoint: str = "/metrics",
    enable_system_metrics: bool = True,
    system_metrics_interval: int = 30,
) -> ACGSPrometheusMetrics:
    """
    Setup Prometheus metrics for a FastAPI application.

    Args:
        app: FastAPI application instance
        service_name: Name of the service
        enable_multiprocess: Enable multiprocess metrics collection
        metrics_endpoint: Endpoint path for metrics
        enable_system_metrics: Enable automatic system metrics collection
        system_metrics_interval: Interval for system metrics collection (seconds)

    Returns:
        ACGSPrometheusMetrics instance
    """

    # Create metrics instance
    metrics = ACGSPrometheusMetrics(service_name, enable_multiprocess)

    # Add middleware
    app.add_middleware(PrometheusMetricsMiddleware, metrics=metrics)

    # Add metrics endpoint
    @app.get(metrics_endpoint)
    async def get_metrics():
        """Prometheus metrics endpoint."""
        metrics_data = metrics.get_metrics_data()
        return Response(content=metrics_data, media_type=CONTENT_TYPE_LATEST)

    # Store metrics in app state
    app.state.metrics = metrics

    # Setup system metrics collection
    if enable_system_metrics:
        import asyncio

        async def collect_system_metrics():
            """Periodically collect system metrics."""
            while True:
                try:
                    metrics.update_system_metrics()
                    await asyncio.sleep(system_metrics_interval)
                except Exception as e:
                    logger.error(f"System metrics collection error: {e}")
                    await asyncio.sleep(system_metrics_interval)

        @app.on_event("startup")
        async def start_system_metrics():
            asyncio.create_task(collect_system_metrics())

    # Startup event to record constitutional hash validation
    @app.on_event("startup")
    async def validate_constitutional_metrics():
        """Validate constitutional compliance on startup."""
        is_valid = CONSTITUTIONAL_HASH == "cdd01ef066bc6cf2"
        metrics.record_constitutional_hash_validation(CONSTITUTIONAL_HASH, is_valid)

        if is_valid:
            metrics.record_constitutional_validation("startup", "valid", 1.0)
            metrics.update_service_health("healthy")
        else:
            metrics.record_constitutional_validation("startup", "invalid", 0.0)
            metrics.update_service_health("unhealthy")

    logger.info(
        f"Prometheus metrics configured for {service_name} (Constitutional Hash: {CONSTITUTIONAL_HASH})"
    )
    return metrics
