"""
ACGS Service Registry
Centralized service discovery and health monitoring for all ACGS services
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Service status enumeration."""

    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"
    UNKNOWN = "unknown"


@dataclass
class ServiceInfo:
    """Information about a registered service."""

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

    @property
    def base_url(self) -> str:
        """Get the base URL for the service."""
        return f"http://{self.host}:{self.port}"

    @property
    def health_url(self) -> str:
        """Get the health check URL for the service."""
        return f"{self.base_url}{self.health_endpoint}"


class ServiceRegistry:
    """Centralized service registry for ACGS services."""

    def __init__(self, health_check_interval: int = 30, max_failures: int = 3):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.services: dict[str, ServiceInfo] = {}
        self.health_check_interval = health_check_interval
        self.max_failures = max_failures
        self._health_check_task: asyncio.Task | None = None
        self._running = False

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
                "metadata": {"description": "Authentication and authorization service"},
            },
            {
                "name": "ac_service",
                "host": "localhost",
                "port": 8001,
                "tags": ["core", "constitutional"],
                "metadata": {"description": "Constitutional AI and compliance service"},
            },
            {
                "name": "integrity_service",
                "host": "localhost",
                "port": 8002,
                "tags": ["core", "security"],
                "metadata": {
                    "description": "Cryptographic integrity and verification service"
                },
            },
            {
                "name": "fv_service",
                "host": "localhost",
                "port": 8003,
                "tags": ["core", "verification"],
                "metadata": {"description": "Formal verification service"},
            },
            {
                "name": "gs_service",
                "host": "localhost",
                "port": 8004,
                "tags": ["core", "governance"],
                "metadata": {"description": "Governance synthesis service"},
            },
            {
                "name": "pgc_service",
                "host": "localhost",
                "port": 8005,
                "tags": ["core", "policy"],
                "metadata": {"description": "Policy governance and compliance service"},
            },
            {
                "name": "ec_service",
                "host": "localhost",
                "port": 8006,
                "tags": ["core", "executive"],
                "metadata": {"description": "Executive council and oversight service"},
            },
            {
                "name": "workflow_service",
                "host": "localhost",
                "port": 9007,
                "tags": ["platform", "orchestration"],
                "metadata": {"description": "Workflow orchestration service"},
            },
            {
                "name": "blockchain_bridge",
                "host": "localhost",
                "port": 9008,
                "tags": ["integration", "blockchain"],
                "metadata": {"description": "Blockchain event bridge service"},
            },
            {
                "name": "performance_optimizer",
                "host": "localhost",
                "port": 9009,
                "tags": ["platform", "optimization"],
                "metadata": {"description": "Performance optimization service"},
            },
            {
                "name": "external_apis_service",
                "host": "localhost",
                "port": 9010,
                "tags": ["integration", "external"],
                "metadata": {"description": "External APIs connector service"},
            },
            {
                "name": "federated_evaluation",
                "host": "localhost",
                "port": 8007,
                "tags": ["research", "evaluation"],
                "metadata": {"description": "Federated evaluation service"},
            },
        ]

        for service_config in acgs_services:
            service_info = ServiceInfo(**service_config)
            self.services[service_info.name] = service_info

    async def start(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Start the service registry and health checking."""
        if self._running:
            return

        self._running = True
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        logger.info("Service registry started")

    async def stop(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Stop the service registry."""
        self._running = False
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
        logger.info("Service registry stopped")

    def register_service(
        self,
        name: str,
        host: str,
        port: int,
        health_endpoint: str = "/health",
        version: str = "1.0.0",
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ServiceInfo:
        """Register a new service."""
        service_info = ServiceInfo(
            name=name,
            host=host,
            port=port,
            health_endpoint=health_endpoint,
            version=version,
            tags=tags or [],
            metadata=metadata or {},
        )

        self.services[name] = service_info
        logger.info(f"Registered service: {name} at {service_info.base_url}")
        return service_info

    def unregister_service(self, name: str) -> bool:
        """Unregister a service."""
        if name in self.services:
            del self.services[name]
            logger.info(f"Unregistered service: {name}")
            return True
        return False

    def get_service(self, name: str) -> ServiceInfo | None:
        """Get service information by name."""
        return self.services.get(name)

    def get_services_by_tag(self, tag: str) -> list[ServiceInfo]:
        """Get all services with a specific tag."""
        return [service for service in self.services.values() if tag in service.tags]

    def get_healthy_services(self) -> list[ServiceInfo]:
        """Get all healthy services."""
        return [
            service
            for service in self.services.values()
            if service.status == ServiceStatus.HEALTHY
        ]

    def get_all_services(self) -> dict[str, ServiceInfo]:
        """Get all registered services."""
        return self.services.copy()

    async def check_service_health(self, service: ServiceInfo) -> bool:
        """Check health of a specific service."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(service.health_url)
                is_healthy = response.status_code == 200

                if is_healthy:
                    service.status = ServiceStatus.HEALTHY
                    service.health_check_failures = 0
                else:
                    service.health_check_failures += 1
                    if service.health_check_failures >= self.max_failures:
                        service.status = ServiceStatus.UNHEALTHY

                service.last_health_check = datetime.now(timezone.utc)
                return is_healthy

        except Exception as e:
            logger.debug(f"Health check failed for {service.name}: {e}")
            service.health_check_failures += 1
            service.last_health_check = datetime.now(timezone.utc)

            if service.health_check_failures >= self.max_failures:
                service.status = ServiceStatus.UNHEALTHY

            return False

    async def check_all_services_health(self) -> dict[str, bool]:
        """Check health of all registered services."""
        tasks = []
        service_names = []

        for service in self.services.values():
            tasks.append(self.check_service_health(service))
            service_names.append(service.name)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        health_status = {}
        for i, service_name in enumerate(service_names):
            if isinstance(results[i], Exception):
                health_status[service_name] = False
            else:
                health_status[service_name] = results[i]

        return health_status

    async def _health_check_loop(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Background health checking loop."""
        while self._running:
            try:
                await self.check_all_services_health()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check loop error: {e}")
                await asyncio.sleep(5)  # Short delay before retry

    def get_service_url(self, service_name: str, endpoint: str = "") -> str | None:
        """Get full URL for a service endpoint."""
        service = self.get_service(service_name)
        if service and service.status == ServiceStatus.HEALTHY:
            return f"{service.base_url}{endpoint}"
        return None

    def get_registry_status(self) -> dict[str, Any]:
        """Get overall registry status."""
        total_services = len(self.services)
        healthy_services = len(self.get_healthy_services())

        return {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "unhealthy_services": total_services - healthy_services,
            "health_percentage": (
                (healthy_services / total_services * 100) if total_services > 0 else 0
            ),
            "last_check": datetime.now(timezone.utc).isoformat(),
            "services": {
                name: {
                    "status": service.status.value,
                    "last_health_check": (
                        service.last_health_check.isoformat()
                        if service.last_health_check
                        else None
                    ),
                    "failures": service.health_check_failures,
                    "url": service.base_url,
                }
                for name, service in self.services.items()
            },
        }


# Global service registry instance
service_registry = ServiceRegistry()


async def get_service_url(service_name: str, endpoint: str = "") -> str | None:
    """Convenience function to get service URL."""
    return service_registry.get_service_url(service_name, endpoint)


async def call_service(
    service_name: str,
    endpoint: str,
    method: str = "GET",
    data: dict[str, Any] | None = None,
    timeout: float = 30.0,
) -> dict[str, Any] | None:
    """Make a call to another ACGS service."""
    service_url = await get_service_url(service_name, endpoint)
    if not service_url:
        logger.error(f"Service {service_name} not available")
        return None

    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            if method.upper() == "GET":
                response = await client.get(service_url)
            elif method.upper() == "POST":
                response = await client.post(service_url, json=data)
            elif method.upper() == "PUT":
                response = await client.put(service_url, json=data)
            elif method.upper() == "DELETE":
                response = await client.delete(service_url)
            else:
                logger.error(f"Unsupported HTTP method: {method}")
                return None

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(
                    f"Service call failed: {response.status_code} - {response.text}"
                )
                return None

    except Exception as e:
        logger.error(f"Error calling service {service_name}: {e}")
        return None


# Export main functions and classes
__all__ = [
    "ServiceRegistry",
    "ServiceInfo",
    "ServiceStatus",
    "service_registry",
    "get_service_url",
    "call_service",
]
