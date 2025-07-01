"""
Enhanced ACGS Service Registry
High-performance service discovery with circuit breakers, connection pooling, and graceful degradation
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import aioredis
import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Enhanced service status enumeration."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    STARTING = "starting"
    STOPPING = "stopping"
    CIRCUIT_OPEN = "circuit_open"
    UNKNOWN = "unknown"


class CircuitBreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    """Circuit breaker for service health checks."""

    failure_threshold: int = 5
    recovery_timeout: int = 60
    half_open_max_calls: int = 3

    failure_count: int = 0
    last_failure_time: float = 0
    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    half_open_calls: int = 0

    def can_execute(self) -> bool:
        """Check if operation can be executed."""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitBreakerState.HALF_OPEN
                self.half_open_calls = 0
                return True
            return False
        else:  # HALF_OPEN
            return self.half_open_calls < self.half_open_max_calls

    def record_success(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record successful operation."""
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.half_open_calls = 0

    def record_failure(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.OPEN
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN


@dataclass
class ServiceInfo:
    """Enhanced service information with performance metrics."""

    name: str
    host: str
    port: int
    health_endpoint: str = "/health"
    version: str = "1.0.0"
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Runtime information
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_health_check: datetime | None = None
    health_check_failures: int = 0
    registered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    # Performance metrics
    avg_response_time: float = 0.0
    last_response_time: float = 0.0
    success_rate: float = 1.0
    total_requests: int = 0
    successful_requests: int = 0

    # Circuit breaker
    circuit_breaker: CircuitBreaker = field(default_factory=CircuitBreaker)

    @property
    def base_url(self) -> str:
        """Get the base URL for the service."""
        return f"http://{self.host}:{self.port}"

    @property
    def health_url(self) -> str:
        """Get the health check URL for the service."""
        return f"{self.base_url}{self.health_endpoint}"

    def update_metrics(self, response_time: float, success: bool):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update performance metrics."""
        self.total_requests += 1
        self.last_response_time = response_time

        if success:
            self.successful_requests += 1

        # Update average response time (exponential moving average)
        alpha = 0.1  # Smoothing factor
        self.avg_response_time = (alpha * response_time) + (
            (1 - alpha) * self.avg_response_time
        )

        # Update success rate
        self.success_rate = (
            self.successful_requests / self.total_requests
            if self.total_requests > 0
            else 1.0
        )


class EnhancedServiceRegistry:
    """High-performance service registry with advanced reliability patterns."""

    def __init__(
        self,
        health_check_interval: int = 30,
        max_failures: int = 3,
        connection_pool_size: int = 100,
        redis_url: str | None = None,
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.services: dict[str, ServiceInfo] = {}
        self.health_check_interval = health_check_interval
        self.max_failures = max_failures
        self.redis_url = redis_url

        # HTTP client with connection pooling
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=5.0),
            limits=httpx.Limits(
                max_connections=connection_pool_size, max_keepalive_connections=20
            ),
            http2=True,
        )

        # Redis client for caching
        self.redis_client: aioredis.Redis | None = None

        # Background tasks
        self._health_check_task: asyncio.Task | None = None
        self._metrics_task: asyncio.Task | None = None
        self._running = False

        # Performance tracking
        self.health_check_metrics = {
            "total_checks": 0,
            "successful_checks": 0,
            "failed_checks": 0,
            "avg_check_time": 0.0,
        }

        # Initialize with known ACGS services
        self._initialize_acgs_services()

    def _initialize_acgs_services(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize registry with known ACGS services."""
        acgs_services = [
            {
                "name": "auth_service",
                "host": "localhost",
                "port": 8000,
                "tags": ["core", "authentication"],
            },
            {
                "name": "ac_service",
                "host": "localhost",
                "port": 8001,
                "tags": ["core", "constitutional"],
            },
            {
                "name": "integrity_service",
                "host": "localhost",
                "port": 8002,
                "tags": ["core", "security"],
            },
            {
                "name": "fv_service",
                "host": "localhost",
                "port": 8003,
                "tags": ["core", "verification"],
            },
            {
                "name": "gs_service",
                "host": "localhost",
                "port": 8004,
                "tags": ["core", "governance"],
            },
            {
                "name": "pgc_service",
                "host": "localhost",
                "port": 8005,
                "tags": ["core", "policy"],
            },
            {
                "name": "ec_service",
                "host": "localhost",
                "port": 8006,
                "tags": ["core", "executive"],
            },
            {
                "name": "workflow_service",
                "host": "localhost",
                "port": 9007,
                "tags": ["platform", "orchestration"],
            },
            {
                "name": "blockchain_bridge",
                "host": "localhost",
                "port": 9008,
                "tags": ["integration", "blockchain"],
            },
            {
                "name": "performance_optimizer",
                "host": "localhost",
                "port": 9009,
                "tags": ["platform", "optimization"],
            },
            {
                "name": "external_apis_service",
                "host": "localhost",
                "port": 9010,
                "tags": ["integration", "external"],
            },
            {
                "name": "federated_evaluation",
                "host": "localhost",
                "port": 8007,
                "tags": ["research", "evaluation"],
            },
        ]

        for service_config in acgs_services:
            service_info = ServiceInfo(**service_config)
            self.services[service_info.name] = service_info

    async def start(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Start the enhanced service registry."""
        if self._running:
            return

        self._running = True

        # Initialize Redis if configured
        if self.redis_url:
            try:
                self.redis_client = await aioredis.from_url(self.redis_url)
                logger.info("Redis cache initialized for service registry")
            except Exception as e:
                logger.warning(f"Failed to initialize Redis cache: {e}")

        # Start background tasks
        self._health_check_task = asyncio.create_task(
            self._enhanced_health_check_loop()
        )
        self._metrics_task = asyncio.create_task(self._metrics_collection_loop())

        logger.info("Enhanced service registry started")

    async def stop(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Stop the service registry."""
        self._running = False

        # Cancel background tasks
        if self._health_check_task:
            self._health_check_task.cancel()
        if self._metrics_task:
            self._metrics_task.cancel()

        # Close HTTP client
        await self.http_client.aclose()

        # Close Redis client
        if self.redis_client:
            await self.redis_client.close()

        logger.info("Enhanced service registry stopped")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.ConnectError)),
    )
    async def check_service_health(self, service: ServiceInfo) -> bool:
        """Enhanced health check with circuit breaker and metrics."""
        if not service.circuit_breaker.can_execute():
            service.status = ServiceStatus.CIRCUIT_OPEN
            return False

        start_time = time.time()

        try:
            response = await self.http_client.get(service.health_url)
            response_time = time.time() - start_time

            is_healthy = response.status_code == 200

            # Update metrics
            service.update_metrics(response_time, is_healthy)

            if is_healthy:
                service.status = ServiceStatus.HEALTHY
                service.health_check_failures = 0
                service.circuit_breaker.record_success()
            else:
                service.health_check_failures += 1
                service.circuit_breaker.record_failure()
                if service.health_check_failures >= self.max_failures:
                    service.status = ServiceStatus.UNHEALTHY
                else:
                    service.status = ServiceStatus.DEGRADED

            service.last_health_check = datetime.now(timezone.utc)

            # Cache result in Redis
            if self.redis_client:
                await self._cache_service_health(
                    service.name, is_healthy, response_time
                )

            return is_healthy

        except Exception as e:
            response_time = time.time() - start_time
            logger.debug(f"Health check failed for {service.name}: {e}")

            service.update_metrics(response_time, False)
            service.health_check_failures += 1
            service.last_health_check = datetime.now(timezone.utc)
            service.circuit_breaker.record_failure()

            if service.health_check_failures >= self.max_failures:
                service.status = ServiceStatus.UNHEALTHY

            return False

    async def _cache_service_health(
        self, service_name: str, is_healthy: bool, response_time: float
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Cache service health status in Redis."""
        if not self.redis_client:
            return

        try:
            cache_data = {
                "healthy": is_healthy,
                "response_time": response_time,
                "timestamp": time.time(),
            }
            await self.redis_client.setex(
                f"service_health:{service_name}", 300, str(cache_data)  # 5 minutes TTL
            )
        except Exception as e:
            logger.debug(f"Failed to cache health status for {service_name}: {e}")

    async def check_all_services_health_parallel(self) -> dict[str, bool]:
        """Parallel health checks for all services with improved performance."""
        start_time = time.time()

        # Execute health checks in parallel with semaphore for rate limiting
        semaphore = asyncio.Semaphore(10)  # Limit concurrent checks

        async def limited_health_check(service):
            # requires: Valid input parameters
            # ensures: Correct function execution
            # sha256: func_hash
            async with semaphore:
                return await self.check_service_health(service)

        # Create tasks for parallel execution
        tasks = []
        service_names = []

        for service in self.services.values():
            if service.circuit_breaker.can_execute():
                tasks.append(limited_health_check(service))
                service_names.append(service.name)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        health_status = {}
        successful_checks = 0

        for i, service_name in enumerate(service_names):
            if isinstance(results[i], Exception):
                health_status[service_name] = False
                logger.error(f"Health check exception for {service_name}: {results[i]}")
            else:
                health_status[service_name] = results[i]
                if results[i]:
                    successful_checks += 1

        # Update metrics
        total_time = time.time() - start_time
        self.health_check_metrics["total_checks"] += len(service_names)
        self.health_check_metrics["successful_checks"] += successful_checks
        self.health_check_metrics["failed_checks"] += (
            len(service_names) - successful_checks
        )

        # Update average check time (exponential moving average)
        alpha = 0.1
        self.health_check_metrics["avg_check_time"] = (
            alpha * total_time
            + (1 - alpha) * self.health_check_metrics["avg_check_time"]
        )

        return health_status

    async def _enhanced_health_check_loop(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Enhanced background health checking loop."""
        while self._running:
            try:
                await self.check_all_services_health_parallel()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(5)  # Short delay before retry

    async def _metrics_collection_loop(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Background metrics collection and aggregation."""
        while self._running:
            try:
                await self._collect_and_aggregate_metrics()
                await asyncio.sleep(60)  # Collect metrics every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(10)

    async def _collect_and_aggregate_metrics(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Collect and aggregate service metrics."""
        if not self.redis_client:
            return

        try:
            # Aggregate service metrics
            total_services = len(self.services)
            healthy_services = len(
                [s for s in self.services.values() if s.status == ServiceStatus.HEALTHY]
            )
            degraded_services = len(
                [
                    s
                    for s in self.services.values()
                    if s.status == ServiceStatus.DEGRADED
                ]
            )

            metrics_data = {
                "timestamp": time.time(),
                "total_services": total_services,
                "healthy_services": healthy_services,
                "degraded_services": degraded_services,
                "unhealthy_services": total_services
                - healthy_services
                - degraded_services,
                "avg_response_time": sum(
                    s.avg_response_time for s in self.services.values()
                )
                / total_services,
                "overall_success_rate": sum(
                    s.success_rate for s in self.services.values()
                )
                / total_services,
                "health_check_metrics": self.health_check_metrics,
            }

            # Store aggregated metrics
            await self.redis_client.setex(
                "service_registry_metrics", 3600, str(metrics_data)  # 1 hour TTL
            )

        except Exception as e:
            logger.error(f"Failed to collect metrics: {e}")

    def get_healthy_services_with_load_balancing(
        self, tag: str | None = None
    ) -> list[ServiceInfo]:
        """Get healthy services with load balancing based on performance metrics."""
        services = self.services.values()

        if tag:
            services = [s for s in services if tag in s.tags]

        # Filter healthy and degraded services
        available_services = [
            s
            for s in services
            if s.status in [ServiceStatus.HEALTHY, ServiceStatus.DEGRADED]
        ]

        # Sort by performance metrics (response time and success rate)
        available_services.sort(
            key=lambda s: (
                s.avg_response_time * (2 - s.success_rate)
            )  # Lower is better
        )

        return available_services

    def get_service_with_fallback(self, service_name: str) -> ServiceInfo | None:
        """Get service with automatic fallback to similar services."""
        primary_service = self.services.get(service_name)

        if primary_service and primary_service.status == ServiceStatus.HEALTHY:
            return primary_service

        # Find fallback services with same tags
        if primary_service:
            fallback_services = self.get_healthy_services_with_load_balancing()
            for service in fallback_services:
                if (
                    any(tag in primary_service.tags for tag in service.tags)
                    and service.name != service_name
                ):
                    logger.warning(
                        f"Using fallback service {service.name} for {service_name}"
                    )
                    return service

        return None

    def get_all_services(self) -> dict[str, ServiceInfo]:
        """Get all registered services."""
        return self.services.copy()

    def get_service(self, name: str) -> ServiceInfo | None:
        """Get service information by name."""
        return self.services.get(name)

    def get_services_by_tag(self, tag: str) -> list[ServiceInfo]:
        """Get all services with a specific tag."""
        return [service for service in self.services.values() if tag in service.tags]

    async def get_registry_performance_report(self) -> dict[str, Any]:
        """Get comprehensive performance report."""
        total_services = len(self.services)
        healthy_count = len(
            [s for s in self.services.values() if s.status == ServiceStatus.HEALTHY]
        )

        service_performance = {}
        for name, service in self.services.items():
            service_performance[name] = {
                "status": service.status.value,
                "avg_response_time": service.avg_response_time,
                "success_rate": service.success_rate,
                "total_requests": service.total_requests,
                "circuit_breaker_state": service.circuit_breaker.state.value,
                "last_health_check": (
                    service.last_health_check.isoformat()
                    if service.last_health_check
                    else None
                ),
            }

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_health_percentage": (
                (healthy_count / total_services * 100) if total_services > 0 else 0
            ),
            "total_services": total_services,
            "healthy_services": healthy_count,
            "registry_metrics": self.health_check_metrics,
            "service_performance": service_performance,
        }


# Global enhanced service registry instance
enhanced_service_registry = EnhancedServiceRegistry()


# Export main functions and classes
__all__ = [
    "EnhancedServiceRegistry",
    "ServiceInfo",
    "ServiceStatus",
    "CircuitBreaker",
    "enhanced_service_registry",
]
