"""
Service Registry for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Centralized service discovery and client management to prevent circular dependencies.
"""

import os
from typing import Dict, Optional

from .base_client import BaseServiceClient, create_client


class ServiceRegistry:
    """
    Centralized registry for all ACGS services.

    This eliminates the need for services to directly import each other,
    preventing circular dependencies.
    """

    def __init__(self):
        self._clients: Dict[str, BaseServiceClient] = {}
        self._service_urls = {
            "constitutional-core": os.getenv(
                "CONSTITUTIONAL_CORE_URL", "http://localhost:8001"
            ),
            "governance-engine": os.getenv(
                "GOVERNANCE_ENGINE_URL", "http://localhost:8004"
            ),
            "integrity": os.getenv("INTEGRITY_SERVICE_URL", "http://localhost:8002"),
            "authentication": os.getenv("AUTH_SERVICE_URL", "http://localhost:8016"),
            "api-gateway": os.getenv("API_GATEWAY_URL", "http://localhost:8080"),
        }

    async def get_client(self, service_name: str) -> Optional[BaseServiceClient]:
        """Get a client for the specified service"""
        if service_name not in self._clients:
            url = self._service_urls.get(service_name)
            if not url:
                return None

            self._clients[service_name] = create_client(service_name, url)
            await self._clients[service_name].connect()

        return self._clients[service_name]

    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all registered services"""
        results = {}
        for service_name in self._service_urls:
            try:
                client = await self.get_client(service_name)
                if client:
                    results[service_name] = await client.health_check()
                else:
                    results[service_name] = False
            except Exception:
                results[service_name] = False

        return results

    async def disconnect_all(self):
        """Disconnect all clients"""
        for client in self._clients.values():
            await client.disconnect()
        self._clients.clear()


# Global registry instance
_registry = ServiceRegistry()


async def get_service_client(service_name: str) -> Optional[BaseServiceClient]:
    """Get a client for the specified service from the global registry"""
    return await _registry.get_client(service_name)


async def health_check_services() -> Dict[str, bool]:
    """Check health of all services"""
    return await _registry.health_check_all()


async def shutdown_registry():
    """Shutdown the global registry"""
    await _registry.disconnect_all()
