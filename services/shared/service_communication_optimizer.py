"""
Service Communication & Load Balancing Enhancement for ACGS-1

Implements intelligent load balancing, circuit breaker patterns,
service discovery, and optimized inter-service communication
to support >1000 concurrent governance actions.
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import aiohttp

from .circuit_breaker import CircuitBreakerConfig, get_circuit_breaker

logger = logging.getLogger(__name__)


class LoadBalancingStrategy(Enum):
    """Load balancing strategies."""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    CONSISTENT_HASH = "consistent_hash"
    HEALTH_BASED = "health_based"


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration."""

    host: str
    port: int
    weight: int = 1
    health_check_path: str = "/health"
    max_connections: int = 100
    current_connections: int = 0
    is_healthy: bool = True
    last_health_check: float = 0
    response_time_avg: float = 0.0
    error_count: int = 0

    @property
    def url(self) -> str:
        """Get full URL for the endpoint."""
        return f"http://{self.host}:{self.port}"

    @property
    def health_url(self) -> str:
        """Get health check URL."""
        return f"{self.url}{self.health_check_path}"


@dataclass
class ServiceConfig:
    """Service configuration for load balancing."""

    name: str
    endpoints: list[ServiceEndpoint] = field(default_factory=list)
    strategy: LoadBalancingStrategy = LoadBalancingStrategy.HEALTH_BASED
    health_check_interval: int = 30
    timeout: float = 10.0
    retry_attempts: int = 3
    circuit_breaker_config: CircuitBreakerConfig | None = None


class ServiceCommunicationOptimizer:
    """
    Advanced service communication optimizer for ACGS-1.

    Provides intelligent load balancing, health monitoring,
    and optimized inter-service communication patterns.
    """

    def __init__(self):
        """Initialize service communication optimizer."""
        self.services: dict[str, ServiceConfig] = {}
        self.round_robin_counters: dict[str, int] = {}
        self.session: aiohttp.ClientSession | None = None
        self.health_check_tasks: dict[str, asyncio.Task] = {}
        self.is_running = False

    async def initialize(self):
        """Initialize the service communication optimizer."""
        # Create aiohttp session with optimized settings
        connector = aiohttp.TCPConnector(
            limit=200,  # Total connection pool size
            limit_per_host=50,  # Connections per host
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True,
        )

        timeout = aiohttp.ClientTimeout(total=30, connect=10)

        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={"User-Agent": "ACGS-ServiceOptimizer/1.0"},
        )

        self.is_running = True
        logger.info("Service communication optimizer initialized")

    def register_service(self, config: ServiceConfig):
        """
        Register a service for load balancing.

        Args:
            config: Service configuration
        """
        self.services[config.name] = config
        self.round_robin_counters[config.name] = 0

        # Start health checking for this service
        if self.is_running:
            self._start_health_checking(config.name)

        logger.info(
            f"Registered service: {config.name} with {len(config.endpoints)} endpoints"
        )

    def add_acgs_services(self):
        """Add standard ACGS-1 services configuration."""
        acgs_services = [
            ServiceConfig(
                name="auth_service",
                endpoints=[ServiceEndpoint("localhost", 8000)],
                strategy=LoadBalancingStrategy.HEALTH_BASED,
            ),
            ServiceConfig(
                name="ac_service",
                endpoints=[ServiceEndpoint("localhost", 8001)],
                strategy=LoadBalancingStrategy.HEALTH_BASED,
            ),
            ServiceConfig(
                name="integrity_service",
                endpoints=[ServiceEndpoint("localhost", 8002)],
                strategy=LoadBalancingStrategy.HEALTH_BASED,
            ),
            ServiceConfig(
                name="fv_service",
                endpoints=[ServiceEndpoint("localhost", 8003)],
                strategy=LoadBalancingStrategy.HEALTH_BASED,
            ),
            ServiceConfig(
                name="gs_service",
                endpoints=[ServiceEndpoint("localhost", 8004)],
                strategy=LoadBalancingStrategy.HEALTH_BASED,
            ),
            ServiceConfig(
                name="pgc_service",
                endpoints=[ServiceEndpoint("localhost", 8005)],
                strategy=LoadBalancingStrategy.HEALTH_BASED,
            ),
            ServiceConfig(
                name="ec_service",
                endpoints=[ServiceEndpoint("localhost", 8006)],
                strategy=LoadBalancingStrategy.HEALTH_BASED,
            ),
            ServiceConfig(
                name="research_service",
                endpoints=[ServiceEndpoint("localhost", 8007)],
                strategy=LoadBalancingStrategy.HEALTH_BASED,
            ),
        ]

        for service_config in acgs_services:
            self.register_service(service_config)

    async def make_request(
        self,
        service_name: str,
        path: str,
        method: str = "GET",
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        timeout: float | None = None,
    ) -> tuple[int, dict[str, Any]]:
        """
        Make optimized request to a service with load balancing.

        Args:
            service_name: Name of the target service
            path: API path
            method: HTTP method
            data: Request data
            headers: Request headers
            timeout: Request timeout

        Returns:
            Tuple of (status_code, response_data)
        """
        if not self.session:
            await self.initialize()

        service_config = self.services.get(service_name)
        if not service_config:
            raise ValueError(f"Service not registered: {service_name}")

        # Get circuit breaker for this service
        circuit_breaker = get_circuit_breaker(
            f"service_{service_name}", service_config.circuit_breaker_config
        )

        # Select endpoint using load balancing
        endpoint = await self._select_endpoint(service_config)
        if not endpoint:
            raise RuntimeError(
                f"No healthy endpoints available for service: {service_name}"
            )

        # Make request through circuit breaker
        return await circuit_breaker.call(
            self._make_http_request,
            endpoint,
            path,
            method,
            data,
            headers,
            timeout or service_config.timeout,
        )

    async def _make_http_request(
        self,
        endpoint: ServiceEndpoint,
        path: str,
        method: str,
        data: dict[str, Any] | None,
        headers: dict[str, str] | None,
        timeout: float,
    ) -> tuple[int, dict[str, Any]]:
        """Make HTTP request to specific endpoint."""
        url = f"{endpoint.url}{path}"
        start_time = time.time()

        try:
            endpoint.current_connections += 1

            request_kwargs = {
                "timeout": aiohttp.ClientTimeout(total=timeout),
                "headers": headers or {},
            }

            if data:
                if method.upper() in ["POST", "PUT", "PATCH"]:
                    request_kwargs["json"] = data
                else:
                    request_kwargs["params"] = data

            async with self.session.request(method, url, **request_kwargs) as response:
                response_data = {}

                try:
                    response_data = await response.json()
                except Exception:
                    response_data = {"text": await response.text()}

                # Update endpoint metrics
                response_time = time.time() - start_time
                endpoint.response_time_avg = (
                    (endpoint.response_time_avg + response_time) / 2
                    if endpoint.response_time_avg > 0
                    else response_time
                )

                if response.status >= 400:
                    endpoint.error_count += 1

                return response.status, response_data

        except Exception as e:
            endpoint.error_count += 1
            logger.error(f"Request failed to {url}: {e}")
            raise
        finally:
            endpoint.current_connections -= 1

    async def _select_endpoint(
        self, service_config: ServiceConfig
    ) -> ServiceEndpoint | None:
        """Select endpoint based on load balancing strategy."""
        healthy_endpoints = [ep for ep in service_config.endpoints if ep.is_healthy]

        if not healthy_endpoints:
            # Fallback to any endpoint if none are healthy
            healthy_endpoints = service_config.endpoints
            if not healthy_endpoints:
                return None

        if service_config.strategy == LoadBalancingStrategy.ROUND_ROBIN:
            return self._round_robin_select(service_config.name, healthy_endpoints)
        elif service_config.strategy == LoadBalancingStrategy.LEAST_CONNECTIONS:
            return min(healthy_endpoints, key=lambda ep: ep.current_connections)
        elif service_config.strategy == LoadBalancingStrategy.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin_select(healthy_endpoints)
        elif service_config.strategy == LoadBalancingStrategy.HEALTH_BASED:
            return self._health_based_select(healthy_endpoints)
        else:
            return random.choice(healthy_endpoints)

    def _round_robin_select(
        self, service_name: str, endpoints: list[ServiceEndpoint]
    ) -> ServiceEndpoint:
        """Round robin endpoint selection."""
        counter = self.round_robin_counters[service_name]
        selected = endpoints[counter % len(endpoints)]
        self.round_robin_counters[service_name] = (counter + 1) % len(endpoints)
        return selected

    def _weighted_round_robin_select(
        self, endpoints: list[ServiceEndpoint]
    ) -> ServiceEndpoint:
        """Weighted round robin endpoint selection."""
        total_weight = sum(ep.weight for ep in endpoints)
        random_weight = random.randint(1, total_weight)

        current_weight = 0
        for endpoint in endpoints:
            current_weight += endpoint.weight
            if random_weight <= current_weight:
                return endpoint

        return endpoints[0]  # Fallback

    def _health_based_select(self, endpoints: list[ServiceEndpoint]) -> ServiceEndpoint:
        """Health-based endpoint selection considering response time and error rate."""

        def health_score(ep: ServiceEndpoint) -> float:
            # Lower is better
            base_score = ep.response_time_avg * 1000  # Convert to ms
            error_penalty = ep.error_count * 100
            connection_penalty = ep.current_connections * 10
            return base_score + error_penalty + connection_penalty

        return min(endpoints, key=health_score)

    def _start_health_checking(self, service_name: str):
        """Start health checking task for a service."""
        if service_name in self.health_check_tasks:
            self.health_check_tasks[service_name].cancel()

        task = asyncio.create_task(self._health_check_loop(service_name))
        self.health_check_tasks[service_name] = task

    async def _health_check_loop(self, service_name: str):
        """Health check loop for a service."""
        service_config = self.services[service_name]

        while self.is_running:
            try:
                for endpoint in service_config.endpoints:
                    await self._check_endpoint_health(endpoint)

                await asyncio.sleep(service_config.health_check_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error for {service_name}: {e}")
                await asyncio.sleep(5)  # Short delay on error

    async def _check_endpoint_health(self, endpoint: ServiceEndpoint):
        """Check health of a specific endpoint."""
        try:
            start_time = time.time()

            async with self.session.get(
                endpoint.health_url, timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                endpoint.is_healthy = response.status == 200
                endpoint.last_health_check = time.time()

                # Update response time
                response_time = time.time() - start_time
                endpoint.response_time_avg = (
                    (endpoint.response_time_avg + response_time) / 2
                    if endpoint.response_time_avg > 0
                    else response_time
                )

        except Exception as e:
            endpoint.is_healthy = False
            endpoint.last_health_check = time.time()
            logger.debug(f"Health check failed for {endpoint.url}: {e}")

    async def get_service_health(self) -> dict[str, Any]:
        """Get health status of all registered services."""
        health_status = {}

        for service_name, service_config in self.services.items():
            healthy_endpoints = sum(
                1 for ep in service_config.endpoints if ep.is_healthy
            )
            total_endpoints = len(service_config.endpoints)

            health_status[service_name] = {
                "healthy_endpoints": healthy_endpoints,
                "total_endpoints": total_endpoints,
                "availability": (
                    healthy_endpoints / total_endpoints if total_endpoints > 0 else 0
                ),
                "strategy": service_config.strategy.value,
                "endpoints": [
                    {
                        "url": ep.url,
                        "healthy": ep.is_healthy,
                        "connections": ep.current_connections,
                        "response_time_avg": ep.response_time_avg,
                        "error_count": ep.error_count,
                    }
                    for ep in service_config.endpoints
                ],
            }

        return health_status

    async def close(self):
        """Close the service communication optimizer."""
        self.is_running = False

        # Cancel health check tasks
        for task in self.health_check_tasks.values():
            task.cancel()

        # Wait for tasks to complete
        if self.health_check_tasks:
            await asyncio.gather(
                *self.health_check_tasks.values(), return_exceptions=True
            )

        # Close HTTP session
        if self.session:
            await self.session.close()

        logger.info("Service communication optimizer closed")


# Global service optimizer instance
_service_optimizer = None


async def get_service_optimizer() -> ServiceCommunicationOptimizer:
    """Get global service communication optimizer."""
    global _service_optimizer

    if _service_optimizer is None:
        _service_optimizer = ServiceCommunicationOptimizer()
        await _service_optimizer.initialize()
        _service_optimizer.add_acgs_services()

    return _service_optimizer


# Convenience functions for service communication
async def call_service(
    service_name: str,
    path: str,
    method: str = "GET",
    data: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
) -> tuple[int, dict[str, Any]]:
    """Make optimized call to ACGS service."""
    optimizer = await get_service_optimizer()
    return await optimizer.make_request(service_name, path, method, data, headers)
