"""
Monitoring Integrator for ACGS-1 Services

Provides Prometheus metrics integration and comprehensive monitoring capabilities.
Integrates with existing ACGS monitoring infrastructure.
"""

import logging
import time
from typing import Any, Dict, Optional

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Try to import Prometheus client
try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Gauge,
        Histogram,
        generate_latest,
    )

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

logger = logging.getLogger(__name__)


class MonitoringIntegrator:
    """
    Lightweight monitoring integration for ACGS-1 services.

    Features:
    - Prometheus metrics collection
    - Service health monitoring
    - Constitutional compliance tracking
    - Performance metrics
    - Integration with existing monitoring infrastructure
    """

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.metrics_enabled = PROMETHEUS_AVAILABLE

        if self.metrics_enabled:
            self._setup_prometheus_metrics()
        else:
            logger.warning("Prometheus client not available - metrics disabled")

        # Fallback metrics storage
        self.fallback_metrics = {
            "requests_total": 0,
            "requests_duration_sum": 0.0,
            "constitutional_compliance_checks": 0,
            "constitutional_compliance_failures": 0,
            "service_health": 1.0,
        }

        logger.info(f"Monitoring integrator initialized for {service_name}")

    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics collectors."""
        if not self.metrics_enabled:
            return

        # Request metrics
        self.requests_total = Counter(
            "acgs_requests_total",
            "Total number of requests",
            ["service", "method", "endpoint", "status_code"],
        )

        self.request_duration = Histogram(
            "acgs_request_duration_seconds",
            "Request duration in seconds",
            ["service", "method", "endpoint"],
        )

        # Constitutional compliance metrics
        self.constitutional_compliance_checks = Counter(
            "acgs_constitutional_compliance_checks_total",
            "Total constitutional compliance checks",
            ["service", "result"],
        )

        self.constitutional_compliance_score = Gauge(
            "acgs_constitutional_compliance_score",
            "Constitutional compliance score",
            ["service"],
        )

        # Service health metrics
        self.service_health = Gauge(
            "acgs_service_health",
            "Service health status (1=healthy, 0=unhealthy)",
            ["service"],
        )

        self.service_uptime = Gauge(
            "acgs_service_uptime_seconds", "Service uptime in seconds", ["service"]
        )

        # Performance metrics
        self.response_time_p95 = Gauge(
            "acgs_response_time_p95_seconds",
            "95th percentile response time",
            ["service"],
        )

        self.availability = Gauge(
            "acgs_service_availability", "Service availability percentage", ["service"]
        )

        # Initialize service health as healthy
        self.service_health.labels(service=self.service_name).set(1.0)

        logger.info("Prometheus metrics initialized")

    async def integrate_monitoring(self, app: FastAPI):
        """Integrate monitoring with FastAPI application."""
        # Add monitoring middleware
        app.add_middleware(MonitoringMiddleware, integrator=self)

        # Add metrics endpoint
        @app.get("/metrics")
        async def metrics_endpoint():
            """Prometheus metrics endpoint."""
            if self.metrics_enabled:
                return Response(
                    content=generate_latest(), media_type=CONTENT_TYPE_LATEST
                )
            else:
                return {"metrics": self.fallback_metrics}

        # Add enhanced health endpoint
        @app.get("/health")
        async def health_endpoint():
            """Enhanced health check with monitoring data."""
            health_data = {
                "status": "healthy",
                "service": self.service_name,
                "timestamp": time.time(),
                "metrics": self.get_health_metrics(),
            }

            return health_data

        logger.info(f"Monitoring endpoints added to {self.service_name}")

    def record_request(
        self, method: str, endpoint: str, status_code: int, duration: float
    ):
        """Record request metrics."""
        if self.metrics_enabled:
            # Record Prometheus metrics
            self.requests_total.labels(
                service=self.service_name,
                method=method,
                endpoint=endpoint,
                status_code=status_code,
            ).inc()

            self.request_duration.labels(
                service=self.service_name, method=method, endpoint=endpoint
            ).observe(duration)

        # Update fallback metrics
        self.fallback_metrics["requests_total"] += 1
        self.fallback_metrics["requests_duration_sum"] += duration

    def record_constitutional_compliance(
        self, result: str, score: Optional[float] = None
    ):
        """Record constitutional compliance metrics."""
        if self.metrics_enabled:
            self.constitutional_compliance_checks.labels(
                service=self.service_name, result=result
            ).inc()

            if score is not None:
                self.constitutional_compliance_score.labels(
                    service=self.service_name
                ).set(score)

        # Update fallback metrics
        self.fallback_metrics["constitutional_compliance_checks"] += 1
        if result == "failure":
            self.fallback_metrics["constitutional_compliance_failures"] += 1

    def update_service_health(self, healthy: bool):
        """Update service health status."""
        health_value = 1.0 if healthy else 0.0

        if self.metrics_enabled:
            self.service_health.labels(service=self.service_name).set(health_value)

        self.fallback_metrics["service_health"] = health_value

    def update_performance_metrics(self, metrics: Dict[str, Any]):
        """Update performance metrics."""
        if not self.metrics_enabled:
            return

        if "p95_response_time" in metrics:
            self.response_time_p95.labels(service=self.service_name).set(
                metrics["p95_response_time"]
            )

        if "availability" in metrics:
            self.availability.labels(service=self.service_name).set(
                metrics["availability"]
            )

    def get_health_metrics(self) -> Dict[str, Any]:
        """Get current health and performance metrics."""
        if self.metrics_enabled:
            # In a real implementation, we would collect current metric values
            # For now, return basic health information
            return {
                "prometheus_enabled": True,
                "metrics_endpoint": "/metrics",
                "service_health": "healthy",
            }
        else:
            return self.fallback_metrics


class MonitoringMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for monitoring integration.
    """

    def __init__(self, app, integrator: MonitoringIntegrator):
        super().__init__(app)
        self.integrator = integrator

    async def dispatch(self, request: Request, call_next):
        """Process request with monitoring."""
        start_time = time.time()
        method = request.method
        endpoint = request.url.path

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Record metrics
            self.integrator.record_request(
                method=method,
                endpoint=endpoint,
                status_code=response.status_code,
                duration=duration,
            )

            # Add monitoring headers
            response.headers["X-Monitoring"] = "enabled"
            response.headers["X-Service"] = self.integrator.service_name

            return response

        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            self.integrator.record_request(
                method=method, endpoint=endpoint, status_code=500, duration=duration
            )

            logger.error(f"Request processing error: {e}")
            raise
