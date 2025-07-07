"""
ACGS API Gateway Service Router

Constitutional AI-enhanced service routing with load balancing,
circuit breaking, and tenant-aware request forwarding.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional

import httpx
from fastapi import HTTPException, Request, status

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service health status."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


class CircuitBreakerState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class ServiceInstance:
    """Service instance configuration."""

    name: str
    url: str
    weight: int = 1
    status: ServiceStatus = ServiceStatus.UNKNOWN
    last_health_check: Optional[datetime] = None
    failure_count: int = 0
    response_time_ms: float = 0.0
    constitutional_compliance_verified: bool = False


@dataclass
class CircuitBreaker:
    """Circuit breaker for service instances."""

    state: CircuitBreakerState = CircuitBreakerState.CLOSED
    failure_count: int = 0
    failure_threshold: int = 5
    reset_timeout_seconds: int = 60
    last_failure_time: Optional[datetime] = None
    next_attempt_time: Optional[datetime] = None


class ServiceRouter:
    """
    Constitutional AI-enhanced service router.

    Provides intelligent request routing with constitutional compliance,
    load balancing, circuit breaking, and health monitoring.
    """

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.services: dict[str, list[ServiceInstance]] = {}
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        self.load_balancing_strategy = (  # round_robin, least_connections, weighted_random
            "round_robin"
        )
        self.round_robin_counters: dict[str, int] = {}
        self.health_check_interval = 30  # seconds
        self.health_check_task: Optional[asyncio.Task] = None
        self.request_timeout = 30  # seconds
        self.service_discovery_client = None

        # Static service registry configuration (fallback)
        self.static_service_registry = {
            "auth": {
                "instances": ["http://auth-service:8000"],
                "health_path": "/health",
                "weight": 1,
                "constitutional_required": True,
            },
            "constitutional-ai": {
                "instances": ["http://constitutional-ai-service:8001"],
                "health_path": "/health",
                "weight": 1,
                "constitutional_required": True,
            },
            "integrity": {
                "instances": ["http://integrity-service:8002"],
                "health_path": "/health",
                "weight": 1,
                "constitutional_required": True,
            },
            "governance-synthesis": {
                "instances": ["http://governance-synthesis-service:8004"],
                "health_path": "/health",
                "weight": 1,
                "constitutional_required": True,
            },
            "policy-governance": {
                "instances": ["http://policy-governance-service:8005"],
                "health_path": "/health",
                "weight": 1,
                "constitutional_required": True,
            },
            "formal-verification": {
                "instances": ["http://formal-verification-service:8006"],
                "health_path": "/health",
                "weight": 1,
                "constitutional_required": True,
            },
        }

        logger.info("Service router initialized with constitutional compliance and service discovery")

    async def initialize(self):
        """Initialize service router."""

        # Initialize service discovery client
        try:
            from services.shared.middleware.service_discovery_middleware import get_discovery_client
            self.service_discovery_client = await get_discovery_client()
            logger.info("Service discovery client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize service discovery client: {e}")
            logger.info("Falling back to static service registry")

        # Register services from discovery or static config
        await self._discover_and_register_services()

        # Start health check monitoring
        self.health_check_task = asyncio.create_task(self._health_check_loop())

        logger.info("Service router initialization completed")

    async def _discover_and_register_services(self):
        """Discover and register services from service registry or static config."""
        
        if self.service_discovery_client:
            try:
                # Get services from dynamic service discovery
                discovered_services = await self.service_discovery_client.discover_all_services()
                
                # Convert discovered services to our format
                for service_name, service_url in discovered_services.items():
                    config = {
                        "instances": [service_url],
                        "health_path": "/health",
                        "weight": 1,
                        "constitutional_required": True,
                    }
                    await self._register_service(service_name, config)
                
                logger.info(f"Registered {len(discovered_services)} services from service discovery")
                
                # Also get service capabilities
                for service_name in discovered_services.keys():
                    try:
                        capabilities = await self.service_discovery_client.get_service_capabilities(service_name)
                        logger.info(f"Service {service_name} capabilities: {capabilities}")
                    except Exception as e:
                        logger.debug(f"Could not get capabilities for {service_name}: {e}")
                
            except Exception as e:
                logger.error(f"Failed to discover services: {e}")
                # Fall back to static config
                await self._register_static_services()
        else:
            # Use static service registry
            await self._register_static_services()

    async def _register_static_services(self):
        """Register services from static configuration."""
        for service_name, config in self.static_service_registry.items():
            await self._register_service(service_name, config)
        logger.info(f"Registered {len(self.static_service_registry)} services from static config")

    async def cleanup(self):
        """Cleanup resources."""

        if self.health_check_task:
            self.health_check_task.cancel()
            try:
                await self.health_check_task
            except asyncio.CancelledError:
                pass

        logger.info("Service router cleanup completed")

    async def _register_service(self, service_name: str, config: dict[str, Any]):
        """Register a service with its instances."""

        instances = []
        for instance_url in config["instances"]:
            instance = ServiceInstance(
                name=f"{service_name}-{len(instances)}",
                url=instance_url,
                weight=config.get("weight", 1),
                constitutional_compliance_verified=config.get(
                    "constitutional_required", True
                ),
            )
            instances.append(instance)

        self.services[service_name] = instances
        self.circuit_breakers[service_name] = CircuitBreaker()
        self.round_robin_counters[service_name] = 0

        logger.info(
            f"Registered service {service_name} with {len(instances)} instances"
        )

    async def route_request(
        self,
        service_name: str,
        request: Request,
        tenant_context: Optional[dict[str, Any]] = None,
        user_context: Optional[dict[str, Any]] = None,
    ) -> httpx.Response:
        """Route request to appropriate service instance."""

        # Extract service name from path
        actual_service_name = self._extract_service_name(service_name)

        if actual_service_name not in self.services:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service not found: {actual_service_name}",
            )

        # Check circuit breaker
        circuit_breaker = self.circuit_breakers[actual_service_name]
        if circuit_breaker.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset(circuit_breaker):
                circuit_breaker.state = CircuitBreakerState.HALF_OPEN
                logger.info(
                    f"Circuit breaker for {actual_service_name} moved to HALF_OPEN"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=(
                        "Service unavailable due to circuit breaker:"
                        f" {actual_service_name}"
                    ),
                )

        # Select service instance
        instance = await self._select_service_instance(actual_service_name)
        if not instance:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    f"No healthy instances available for service: {actual_service_name}"
                ),
            )

        # Verify constitutional compliance for instance
        if instance.constitutional_compliance_verified:
            compliance_check = await self._verify_instance_constitutional_compliance(
                instance
            )
            if not compliance_check["compliant"]:
                logger.warning(
                    f"Constitutional compliance failed for {instance.name}:"
                    f" {compliance_check}"
                )
                # Try another instance
                return await self._try_fallback_instance(
                    actual_service_name, request, tenant_context, user_context
                )

        # Forward request
        try:
            start_time = time.time()

            response = await self._forward_request(
                instance, request, tenant_context, user_context
            )

            response_time = (time.time() - start_time) * 1000  # ms

            # Update instance metrics
            await self._update_instance_metrics(instance, response_time, True)

            # Update circuit breaker on success
            await self._record_success(circuit_breaker)

            return response

        except Exception as e:
            logger.error(f"Request failed for {instance.name}: {e}")

            # Update instance metrics
            await self._update_instance_metrics(instance, 0, False)

            # Update circuit breaker on failure
            await self._record_failure(circuit_breaker)

            # Try fallback instance
            if circuit_breaker.state != CircuitBreakerState.OPEN:
                return await self._try_fallback_instance(
                    actual_service_name, request, tenant_context, user_context
                )

            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Service request failed: {e!s}",
            )

    def _extract_service_name(self, path: str) -> str:
        """Extract actual service name from request path."""

        # Handle paths like "auth/login" -> "auth"
        path_parts = path.strip("/").split("/")
        if path_parts:
            service_name = path_parts[0]

            # Map common path patterns to service names
            service_mapping = {
                "auth": "auth",
                "constitutional": "constitutional-ai",
                "integrity": "integrity",
                "governance": "governance-synthesis",
                "policy": "policy-governance",
                "verification": "formal-verification",
            }

            return service_mapping.get(service_name, service_name)

        return path

    async def _select_service_instance(
        self, service_name: str
    ) -> Optional[ServiceInstance]:
        """Select service instance based on load balancing strategy."""

        instances = self.services.get(service_name, [])
        healthy_instances = [i for i in instances if i.status == ServiceStatus.HEALTHY]

        if not healthy_instances:
            # Fallback to degraded instances if no healthy ones
            degraded_instances = [
                i for i in instances if i.status == ServiceStatus.DEGRADED
            ]
            if degraded_instances:
                healthy_instances = degraded_instances

        if not healthy_instances:
            return None

        if self.load_balancing_strategy == "round_robin":
            return self._round_robin_selection(service_name, healthy_instances)
        elif self.load_balancing_strategy == "least_connections":
            return self._least_connections_selection(healthy_instances)
        elif self.load_balancing_strategy == "weighted_random":
            return self._weighted_random_selection(healthy_instances)
        else:
            return random.choice(healthy_instances)

    def _round_robin_selection(
        self, service_name: str, instances: list[ServiceInstance]
    ) -> ServiceInstance:
        """Round-robin load balancing."""

        counter = self.round_robin_counters[service_name]
        selected = instances[counter % len(instances)]
        self.round_robin_counters[service_name] = (counter + 1) % len(instances)
        return selected

    def _least_connections_selection(
        self, instances: list[ServiceInstance]
    ) -> ServiceInstance:
        """Least connections load balancing (simplified)."""

        # In a real implementation, this would track active connections
        # For now, use the instance with best response time as a proxy
        return min(instances, key=lambda i: i.response_time_ms)

    def _weighted_random_selection(
        self, instances: list[ServiceInstance]
    ) -> ServiceInstance:
        """Weighted random load balancing."""

        total_weight = sum(i.weight for i in instances)
        if total_weight == 0:
            return random.choice(instances)

        r = random.uniform(0, total_weight)
        cumulative_weight = 0

        for instance in instances:
            cumulative_weight += instance.weight
            if r <= cumulative_weight:
                return instance

        return instances[-1]  # Fallback

    async def _verify_instance_constitutional_compliance(
        self, instance: ServiceInstance
    ) -> dict[str, Any]:
        """Verify constitutional compliance for service instance."""

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                # Check for constitutional compliance endpoint
                compliance_url = f"{instance.url}/constitutional/compliance"

                try:
                    response = await client.get(compliance_url)
                    if response.status_code == 200:
                        compliance_data = response.json()
                        constitutional_hash = compliance_data.get("constitutional_hash")

                        return {
                            "compliant": (
                                constitutional_hash == self.constitutional_hash
                            ),
                            "hash_verified": (
                                constitutional_hash == self.constitutional_hash
                            ),
                            "instance": instance.name,
                            "verified_at": datetime.now(timezone.utc).isoformat(),
                        }
                except httpx.RequestError:
                    # Compliance endpoint not available, assume compliant for basic services
                    pass

            # Fallback: assume compliant if service is responsive
            return {
                "compliant": True,
                "fallback_verification": True,
                "instance": instance.name,
                "verified_at": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(
                "Constitutional compliance verification failed for"
                f" {instance.name}: {e}"
            )
            return {
                "compliant": False,
                "error": str(e),
                "instance": instance.name,
                "verified_at": datetime.now(timezone.utc).isoformat(),
            }

    async def _forward_request(
        self,
        instance: ServiceInstance,
        request: Request,
        tenant_context: Optional[dict[str, Any]] = None,
        user_context: Optional[dict[str, Any]] = None,
    ) -> httpx.Response:
        """Forward request to service instance."""

        # Build target URL
        path = str(request.url.path)
        query = str(request.url.query)

        # Remove /api/ prefix and service name from path
        path_parts = path.strip("/").split("/")[2:]  # Remove 'api' and service name
        target_path = "/" + "/".join(path_parts) if path_parts else "/"

        target_url = f"{instance.url}{target_path}"
        if query:
            target_url += f"?{query}"

        # Prepare headers
        headers = dict(request.headers)

        # Add constitutional compliance headers
        headers["X-Constitutional-Hash"] = self.constitutional_hash
        headers["X-Gateway-Routed"] = "true"
        headers["X-Service-Instance"] = instance.name

        # Add tenant context headers
        if tenant_context:
            headers["X-Tenant-ID"] = tenant_context.get("tenant_id", "")
            headers["X-Tenant-Context"] = str(tenant_context)

        # Add user context headers
        if user_context:
            headers["X-User-ID"] = user_context.get("user_id", "")
            headers["X-User-Context"] = str(user_context)

        # Remove hop-by-hop headers
        hop_by_hop_headers = [
            "connection",
            "keep-alive",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailers",
            "transfer-encoding",
            "upgrade",
        ]
        for header in hop_by_hop_headers:
            headers.pop(header, None)

        # Get request body
        body = None
        if request.method in ["POST", "PUT", "PATCH"]:
            body = await request.body()

        # Forward request
        async with httpx.AsyncClient(timeout=self.request_timeout) as client:
            response = await client.request(
                method=request.method, url=target_url, headers=headers, content=body
            )

        return response

    async def _try_fallback_instance(
        self,
        service_name: str,
        request: Request,
        tenant_context: Optional[dict[str, Any]] = None,
        user_context: Optional[dict[str, Any]] = None,
    ) -> httpx.Response:
        """Try another instance as fallback."""

        instances = self.services.get(service_name, [])
        available_instances = [
            i for i in instances if i.status != ServiceStatus.UNHEALTHY
        ]

        if not available_instances:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"No available instances for service: {service_name}",
            )

        # Try each available instance
        for instance in available_instances:
            try:
                start_time = time.time()
                response = await self._forward_request(
                    instance, request, tenant_context, user_context
                )
                response_time = (time.time() - start_time) * 1000

                await self._update_instance_metrics(instance, response_time, True)
                return response

            except Exception as e:
                logger.warning(f"Fallback instance {instance.name} also failed: {e}")
                await self._update_instance_metrics(instance, 0, False)
                continue

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"All instances failed for service: {service_name}",
        )

    async def _update_instance_metrics(
        self, instance: ServiceInstance, response_time: float, success: bool
    ):
        """Update instance performance metrics."""

        if success:
            instance.response_time_ms = response_time
            instance.failure_count = max(0, instance.failure_count - 1)

            # Update status based on performance
            if response_time < 1000:  # < 1 second
                instance.status = ServiceStatus.HEALTHY
            elif response_time < 5000:  # < 5 seconds
                instance.status = ServiceStatus.DEGRADED
            else:
                instance.status = ServiceStatus.UNHEALTHY
        else:
            instance.failure_count += 1

            # Mark as unhealthy after multiple failures
            if instance.failure_count >= 3:
                instance.status = ServiceStatus.UNHEALTHY

    def _should_attempt_reset(self, circuit_breaker: CircuitBreaker) -> bool:
        """Check if circuit breaker should attempt reset."""

        if circuit_breaker.next_attempt_time is None:
            circuit_breaker.next_attempt_time = datetime.now(timezone.utc) + timedelta(
                seconds=circuit_breaker.reset_timeout_seconds
            )
            return False

        return datetime.now(timezone.utc) >= circuit_breaker.next_attempt_time

    async def _record_success(self, circuit_breaker: CircuitBreaker):
        """Record successful request for circuit breaker."""

        if circuit_breaker.state == CircuitBreakerState.HALF_OPEN:
            circuit_breaker.state = CircuitBreakerState.CLOSED
            circuit_breaker.failure_count = 0
            circuit_breaker.next_attempt_time = None
            logger.info("Circuit breaker reset to CLOSED after successful request")

    async def _record_failure(self, circuit_breaker: CircuitBreaker):
        """Record failed request for circuit breaker."""

        circuit_breaker.failure_count += 1
        circuit_breaker.last_failure_time = datetime.now(timezone.utc)

        if circuit_breaker.failure_count >= circuit_breaker.failure_threshold:
            circuit_breaker.state = CircuitBreakerState.OPEN
            circuit_breaker.next_attempt_time = datetime.now(timezone.utc) + timedelta(
                seconds=circuit_breaker.reset_timeout_seconds
            )
            logger.warning(
                "Circuit breaker opened due to"
                f" {circuit_breaker.failure_count} failures"
            )

    async def _health_check_loop(self):
        """Continuous health checking of service instances."""

        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")

    async def _perform_health_checks(self):
        """Perform health checks on all service instances."""

        health_check_tasks = []

        for service_name, instances in self.services.items():
            for instance in instances:
                task = asyncio.create_task(
                    self._check_instance_health(service_name, instance)
                )
                health_check_tasks.append(task)

        if health_check_tasks:
            await asyncio.gather(*health_check_tasks, return_exceptions=True)

    async def _check_instance_health(
        self, service_name: str, instance: ServiceInstance
    ):
        """Check health of a specific service instance."""

        try:
            config = self.service_registry.get(service_name, {})
            health_path = config.get("health_path", "/health")
            health_url = f"{instance.url}{health_path}"

            start_time = time.time()

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(health_url)

                response_time = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    instance.status = ServiceStatus.HEALTHY
                    instance.response_time_ms = response_time
                    instance.failure_count = 0

                    # Verify constitutional compliance in health response
                    try:
                        health_data = response.json()
                        constitutional_hash = health_data.get("constitutional_hash")
                        instance.constitutional_compliance_verified = (
                            constitutional_hash == self.constitutional_hash
                        )
                    except:
                        instance.constitutional_compliance_verified = (
                            True  # Assume compliant for basic health checks
                        )

                else:
                    instance.status = ServiceStatus.DEGRADED
                    instance.failure_count += 1

                instance.last_health_check = datetime.now(timezone.utc)

        except Exception as e:
            logger.debug(f"Health check failed for {instance.name}: {e}")
            instance.status = ServiceStatus.UNHEALTHY
            instance.failure_count += 1
            instance.last_health_check = datetime.now(timezone.utc)

    async def health_check(self) -> dict[str, Any]:
        """Get router health status."""

        total_instances = sum(len(instances) for instances in self.services.values())
        healthy_instances = sum(
            len([i for i in instances if i.status == ServiceStatus.HEALTHY])
            for instances in self.services.values()
        )

        return {
            "healthy": healthy_instances > 0,
            "total_instances": total_instances,
            "healthy_instances": healthy_instances,
            "services": {
                name: {
                    "instances": len(instances),
                    "healthy": len([
                        i for i in instances if i.status == ServiceStatus.HEALTHY
                    ]),
                    "circuit_breaker_state": self.circuit_breakers[name].state.value,
                }
                for name, instances in self.services.items()
            },
            "constitutional_hash": self.constitutional_hash,
        }

    async def verify_constitutional_compliance(self) -> bool:
        """Verify constitutional compliance of the router."""

        return self.constitutional_hash == CONSTITUTIONAL_HASH

    async def get_registered_services(self) -> list[str]:
        """Get list of registered services."""

        return list(self.services.keys())

    async def refresh_services(self):
        """Refresh service registry."""

        logger.info("Refreshing service registry")

        # Clear existing services
        self.services.clear()
        self.circuit_breakers.clear()
        self.round_robin_counters.clear()

        # Re-discover and register services
        await self._discover_and_register_services()

        # Perform immediate health checks
        await self._perform_health_checks()

        logger.info("Service registry refresh completed")
