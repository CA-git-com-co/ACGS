"""
ACGS Prometheus Metrics Middleware
Constitutional Hash: cdd01ef066bc6cf2

This module provides standardized Prometheus metrics integration for all FastAPI services.
Includes request/response metrics, database connection pool metrics, and service health metrics.
"""

import asyncio
import logging
import time
from functools import wraps
from typing import Any, Callable, Dict

from fastapi import Request, Response
from fastapi.routing import APIRoute
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    Counter,
    Gauge,
    Histogram,
    Info,
    generate_latest,
)

from ..config.infrastructure_config import (
    CONSTITUTIONAL_HASH,
    get_acgs_config,
    get_database_manager,
    get_redis_manager,
)

logger = logging.getLogger(__name__)

# Prometheus Metrics
REQUEST_COUNT = Counter(
    "acgs_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code", "service"],
)

REQUEST_DURATION = Histogram(
    "acgs_http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint", "service"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

REQUEST_SIZE = Histogram(
    "acgs_http_request_size_bytes",
    "HTTP request size in bytes",
    ["method", "endpoint", "service"],
)

RESPONSE_SIZE = Histogram(
    "acgs_http_response_size_bytes",
    "HTTP response size in bytes",
    ["method", "endpoint", "service"],
)

# Database metrics
DB_CONNECTIONS_ACTIVE = Gauge(
    "acgs_db_connections_active", "Active database connections", ["service"]
)

DB_CONNECTIONS_IDLE = Gauge(
    "acgs_db_connections_idle", "Idle database connections", ["service"]
)

DB_QUERY_DURATION = Histogram(
    "acgs_db_query_duration_seconds",
    "Database query duration in seconds",
    ["service", "query_type"],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0],
)

# Redis metrics
REDIS_CONNECTIONS_ACTIVE = Gauge(
    "acgs_redis_connections_active", "Active Redis connections", ["service"]
)

REDIS_COMMAND_DURATION = Histogram(
    "acgs_redis_command_duration_seconds",
    "Redis command duration in seconds",
    ["service", "command"],
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5],
)

# Service health metrics
SERVICE_HEALTH = Gauge(
    "acgs_service_health",
    "Service health status (1=healthy, 0=unhealthy)",
    ["service", "component"],
)

SERVICE_INFO = Info("acgs_service_info", "Service information", ["service"])

# Constitutional compliance metric
CONSTITUTIONAL_COMPLIANCE = Gauge(
    "acgs_constitutional_compliance",
    "Constitutional compliance status (1=compliant, 0=non-compliant)",
    ["service", "hash"],
)


class PrometheusMiddleware:
    """
    FastAPI middleware for Prometheus metrics collection.
    """

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.config = get_acgs_config()

        # Initialize service info
        SERVICE_INFO.labels(service=service_name).info(
            {
                "version": "1.0.0",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "auth_port": str(self.config.AUTH_PORT),
                "postgres_port": str(self.config.POSTGRES_PORT),
                "redis_port": str(self.config.REDIS_PORT),
            }
        )

        # Set constitutional compliance
        CONSTITUTIONAL_COMPLIANCE.labels(
            service=service_name, hash=CONSTITUTIONAL_HASH
        ).set(1)

        logger.info(f"Initialized Prometheus metrics for service: {service_name}")

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """Process request and collect metrics"""
        # Start timing
        start_time = time.time()

        # Get request details
        method = request.method
        endpoint = self._get_endpoint_name(request)

        # Measure request size
        request_size = len(await request.body()) if hasattr(request, "body") else 0
        REQUEST_SIZE.labels(
            method=method, endpoint=endpoint, service=self.service_name
        ).observe(request_size)

        # Process request
        try:
            response = await call_next(request)
            status_code = response.status_code

            # Measure response size
            response_size = 0
            if hasattr(response, "body"):
                response_size = len(response.body)

            RESPONSE_SIZE.labels(
                method=method, endpoint=endpoint, service=self.service_name
            ).observe(response_size)

        except Exception as e:
            logger.error(f"Request processing error: {e}")
            status_code = 500
            response = Response(content="Internal Server Error", status_code=500)

        # Record metrics
        duration = time.time() - start_time

        REQUEST_COUNT.labels(
            method=method,
            endpoint=endpoint,
            status_code=status_code,
            service=self.service_name,
        ).inc()

        REQUEST_DURATION.labels(
            method=method, endpoint=endpoint, service=self.service_name
        ).observe(duration)

        return response

    def _get_endpoint_name(self, request: Request) -> str:
        """Extract endpoint name from request"""
        route = request.url.path

        # Handle FastAPI route parameters
        if hasattr(request, "path_info"):
            route = request.path_info

        # Remove query parameters
        if "?" in route:
            route = route.split("?")[0]

        # Normalize endpoint name
        if route.endswith("/"):
            route = route[:-1]

        return route or "/"


def add_prometheus_metrics_endpoint(app, service_name: str):
    """
    Add Prometheus metrics endpoint to FastAPI app.
    """

    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        """Prometheus metrics endpoint"""
        try:
            # Update database metrics
            await _update_database_metrics(service_name)

            # Update Redis metrics
            await _update_redis_metrics(service_name)

            # Update service health
            await _update_service_health(service_name)

            # Generate metrics response
            return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

        except Exception as e:
            logger.error(f"Error generating metrics: {e}")
            return Response(content="Error generating metrics", status_code=500)

    logger.info(f"Added Prometheus metrics endpoint for service: {service_name}")


async def _update_database_metrics(service_name: str):
    """Update database connection metrics"""
    try:
        db_manager = get_database_manager()

        if db_manager.pool:
            # Get pool statistics
            pool = db_manager.pool

            # Active connections (approximate)
            active_connections = pool._queue.qsize() if hasattr(pool, "_queue") else 0
            DB_CONNECTIONS_ACTIVE.labels(service=service_name).set(active_connections)

            # Idle connections (approximate)
            max_size = db_manager.config.POSTGRES_POOL_MAX_SIZE
            idle_connections = max_size - active_connections
            DB_CONNECTIONS_IDLE.labels(service=service_name).set(idle_connections)

        # Check database health
        health_status = await db_manager.health_check()
        SERVICE_HEALTH.labels(service=service_name, component="database").set(
            1 if health_status else 0
        )

    except Exception as e:
        logger.error(f"Error updating database metrics: {e}")
        SERVICE_HEALTH.labels(service=service_name, component="database").set(0)


async def _update_redis_metrics(service_name: str):
    """Update Redis connection metrics"""
    try:
        redis_manager = get_redis_manager()

        if redis_manager.redis:
            # Get Redis info
            info = await redis_manager.redis.info()
            connected_clients = info.get("connected_clients", 0)

            REDIS_CONNECTIONS_ACTIVE.labels(service=service_name).set(connected_clients)

        # Check Redis health
        health_status = await redis_manager.health_check()
        SERVICE_HEALTH.labels(service=service_name, component="redis").set(
            1 if health_status else 0
        )

    except Exception as e:
        logger.error(f"Error updating Redis metrics: {e}")
        SERVICE_HEALTH.labels(service=service_name, component="redis").set(0)


async def _update_service_health(service_name: str):
    """Update overall service health"""
    try:
        # Overall service health (simplified)
        SERVICE_HEALTH.labels(service=service_name, component="service").set(1)

    except Exception as e:
        logger.error(f"Error updating service health: {e}")
        SERVICE_HEALTH.labels(service=service_name, component="service").set(0)


def instrument_database_queries(service_name: str):
    """
    Decorator to instrument database queries with metrics.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            query_type = func.__name__

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                DB_QUERY_DURATION.labels(
                    service=service_name, query_type=query_type
                ).observe(duration)

                return result

            except Exception as e:
                duration = time.time() - start_time
                DB_QUERY_DURATION.labels(
                    service=service_name, query_type=f"{query_type}_error"
                ).observe(duration)
                raise

        return wrapper

    return decorator


def instrument_redis_commands(service_name: str):
    """
    Decorator to instrument Redis commands with metrics.
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            command = func.__name__

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                REDIS_COMMAND_DURATION.labels(
                    service=service_name, command=command
                ).observe(duration)

                return result

            except Exception as e:
                duration = time.time() - start_time
                REDIS_COMMAND_DURATION.labels(
                    service=service_name, command=f"{command}_error"
                ).observe(duration)
                raise

        return wrapper

    return decorator


# Export key components
__all__ = [
    "PrometheusMiddleware",
    "add_prometheus_metrics_endpoint",
    "instrument_database_queries",
    "instrument_redis_commands",
    "REQUEST_COUNT",
    "REQUEST_DURATION",
    "DB_CONNECTIONS_ACTIVE",
    "REDIS_CONNECTIONS_ACTIVE",
    "SERVICE_HEALTH",
    "CONSTITUTIONAL_COMPLIANCE",
]
