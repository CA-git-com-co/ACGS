"""
ACGS Service Discovery Middleware
Constitutional Hash: cdd01ef066bc6cf2

FastAPI middleware for automatic service registration and discovery.
"""

import asyncio
import logging
import os
import socket
import uuid
from contextlib import asynccontextmanager
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.base import BaseHTTPMiddleware

from services.shared.service_registry import (
    ACGSServiceRegistry,
    ServiceStatus,
    register_current_service,
    send_heartbeat,
)

logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ServiceDiscoveryMiddleware(BaseHTTPMiddleware):
    """
    Middleware that automatically handles service registration and heartbeats.
    """

    def __init__(
        self,
        app: FastAPI,
        service_name: str,
        service_version: str = "1.0.0",
        capabilities: Optional[list] = None,
        heartbeat_interval: int = 15,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(app)
        self.service_name = service_name
        self.service_version = service_version
        self.capabilities = capabilities or []
        self.heartbeat_interval = heartbeat_interval
        self.metadata = metadata or {}
        self.instance_id = str(uuid.uuid4())
        self.host = self._get_host()
        self.port = self._get_port()
        self.heartbeat_task: Optional[asyncio.Task] = None
        self.registry: Optional[ACGSServiceRegistry] = None

    def _get_host(self) -> str:
        """Get the host address for this service."""
        # Try container hostname first, then local IP
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "localhost"

    def _get_port(self) -> int:
        """Get the port for this service."""
        # Try to get from environment or default to 8000
        return int(os.getenv("PORT", "8000"))

    async def startup(self) -> None:
        """Service startup - register with service registry."""
        try:
            self.registry = ACGSServiceRegistry()
            await self.registry.initialize()

            # Register service
            success = await register_current_service(
                service_name=self.service_name,
                instance_id=self.instance_id,
                host=self.host,
                port=self.port,
                version=self.service_version,
                capabilities=self.capabilities,
                metadata=self.metadata,
            )

            if success:
                logger.info(
                    f"Service registered: {self.service_name}/{self.instance_id} "
                    f"(Constitutional Hash: {CONSTITUTIONAL_HASH})"
                )

                # Start heartbeat task
                self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
            else:
                logger.error(f"Failed to register service: {self.service_name}")

        except Exception as e:
            logger.error(f"Service registration failed: {e}")

    async def shutdown(self) -> None:
        """Service shutdown - unregister from service registry."""
        try:
            # Stop heartbeat task
            if self.heartbeat_task:
                self.heartbeat_task.cancel()
                try:
                    await self.heartbeat_task
                except asyncio.CancelledError:
                    pass

            # Unregister service
            if self.registry:
                await self.registry.unregister_service(
                    self.service_name, self.instance_id
                )
                await self.registry.close()

            logger.info(f"Service unregistered: {self.service_name}/{self.instance_id}")

        except Exception as e:
            logger.error(f"Service unregistration failed: {e}")

    async def _heartbeat_loop(self) -> None:
        """Background task to send regular heartbeats."""
        while True:
            try:
                await asyncio.sleep(self.heartbeat_interval)

                # Send heartbeat with current metadata
                success = await send_heartbeat(
                    service_name=self.service_name,
                    instance_id=self.instance_id,
                    status=ServiceStatus.HEALTHY,
                    metadata=self.metadata,
                )

                if not success:
                    logger.warning(
                        f"Heartbeat failed for {self.service_name}/{self.instance_id}"
                    )

            except asyncio.CancelledError:
                logger.info("Heartbeat task cancelled")
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")

    async def dispatch(self, request: Request, call_next):
        """Process requests and add service discovery headers."""
        # Add service identification headers
        response = await call_next(request)

        response.headers["X-Service-Name"] = self.service_name
        response.headers["X-Service-Instance"] = self.instance_id
        response.headers["X-Service-Version"] = self.service_version
        response.headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH

        return response


def setup_service_discovery(
    app: FastAPI,
    service_name: str,
    service_version: str = "1.0.0",
    capabilities: Optional[list] = None,
    heartbeat_interval: int = 15,
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Setup service discovery for a FastAPI application.

    Args:
        app: FastAPI application instance
        service_name: Name of the service
        service_version: Version of the service
        capabilities: List of service capabilities
        heartbeat_interval: Heartbeat interval in seconds
        metadata: Additional service metadata
    """

    # Create middleware instance
    middleware = ServiceDiscoveryMiddleware(
        app=app,
        service_name=service_name,
        service_version=service_version,
        capabilities=capabilities,
        heartbeat_interval=heartbeat_interval,
        metadata=metadata,
    )

    # Add middleware to app
    app.add_middleware(ServiceDiscoveryMiddleware)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        """Application lifespan for service registration."""
        # Startup
        await middleware.startup()
        yield
        # Shutdown
        await middleware.shutdown()

    # Set lifespan if not already set
    if not hasattr(app, "router") or not app.router.lifespan_context:
        app = FastAPI(lifespan=lifespan)

    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint for service discovery."""
        return {
            "status": "healthy",
            "service": service_name,
            "instance_id": middleware.instance_id,
            "version": service_version,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "capabilities": capabilities or [],
        }

    # Add service discovery endpoints
    @app.get("/service/discovery/info")
    async def service_discovery_info():
        """Get service discovery information."""
        return {
            "service_name": service_name,
            "instance_id": middleware.instance_id,
            "host": middleware.host,
            "port": middleware.port,
            "version": service_version,
            "capabilities": capabilities or [],
            "metadata": metadata or {},
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }

    @app.get("/service/discovery/peers")
    async def get_service_peers():
        """Get other instances of the same service."""
        if not middleware.registry:
            raise HTTPException(
                status_code=503, detail="Service registry not available"
            )

        instances = await middleware.registry.discover_services(service_name)
        return [
            {
                "instance_id": instance.instance_id,
                "host": instance.host,
                "port": instance.port,
                "status": instance.status.value,
                "version": instance.version,
                "capabilities": instance.capabilities,
                "last_heartbeat": instance.last_heartbeat.isoformat(),
            }
            for instance in instances
            if instance.instance_id != middleware.instance_id
        ]

    @app.get("/service/discovery/all")
    async def get_all_services():
        """Get all registered services."""
        if not middleware.registry:
            raise HTTPException(
                status_code=503, detail="Service registry not available"
            )

        stats = await middleware.registry.get_registry_stats()
        return stats

    logger.info(
        f"Service discovery configured for {service_name} (Constitutional Hash: {CONSTITUTIONAL_HASH})"
    )


class ServiceDiscoveryClient:
    """
    Client for discovering and communicating with other services.
    """

    def __init__(self, redis_url: str = "redis://localhost:6389"):
        self.registry = ACGSServiceRegistry(redis_url)

    async def initialize(self) -> None:
        """Initialize the service discovery client."""
        await self.registry.initialize()

    async def close(self) -> None:
        """Close the service discovery client."""
        await self.registry.close()

    async def discover_service(self, service_name: str) -> Optional[str]:
        """
        Discover a service and return its URL.

        Args:
            service_name: Name of the service to discover

        Returns:
            Service URL if found, None otherwise
        """
        instances = await self.registry.get_healthy_instances(service_name)
        if instances:
            # Simple round-robin selection (could be enhanced with load balancing)
            instance = instances[0]
            return f"http://{instance.host}:{instance.port}"
        return None

    async def discover_all_services(self) -> Dict[str, str]:
        """
        Discover all services and return their URLs.

        Returns:
            Dictionary mapping service names to URLs
        """
        services = {}
        all_instances = await self.registry.discover_services()

        for instance in all_instances:
            if instance.status == ServiceStatus.HEALTHY:
                services[instance.service_name] = (
                    f"http://{instance.host}:{instance.port}"
                )

        return services

    async def get_service_capabilities(self, service_name: str) -> list:
        """
        Get capabilities for a service.

        Args:
            service_name: Name of the service

        Returns:
            List of service capabilities
        """
        capabilities = await self.registry.get_service_capabilities(service_name)
        return list(capabilities)


# Global service discovery client
_discovery_client: Optional[ServiceDiscoveryClient] = None


async def get_discovery_client() -> ServiceDiscoveryClient:
    """Get the global service discovery client."""
    global _discovery_client
    if _discovery_client is None:
        _discovery_client = ServiceDiscoveryClient()
        await _discovery_client.initialize()
    return _discovery_client
