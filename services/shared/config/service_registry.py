"""
Service Registry - Central service discovery and configuration
"""

import os
from dataclasses import dataclass


@dataclass
class ServiceConfig:
    name: str
    url: str
    health_endpoint: str
    version: str


class ServiceRegistry:
    """Central registry for all ACGS services"""

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self._services: dict[str, ServiceConfig] = {}
        self._load_from_environment()

    def _load_from_environment(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Load service configurations from environment variables"""
        services = {
            "constitutional-ai": ServiceConfig(
                name="constitutional-ai",
                url=os.getenv("CONSTITUTIONAL_AI_URL", "http://localhost:8001"),
                health_endpoint="/health",
                version="1.0.0",
            ),
            "governance-synthesis": ServiceConfig(
                name="governance-synthesis",
                url=os.getenv("GOVERNANCE_SYNTHESIS_URL", "http://localhost:8003"),
                health_endpoint="/health",
                version="1.0.0",
            ),
            "policy-governance": ServiceConfig(
                name="policy-governance",
                url=os.getenv("POLICY_GOVERNANCE_URL", "http://localhost:8004"),
                health_endpoint="/health",
                version="1.0.0",
            ),
            "formal-verification": ServiceConfig(
                name="formal-verification",
                url=os.getenv("FORMAL_VERIFICATION_URL", "http://localhost:8005"),
                health_endpoint="/health",
                version="1.0.0",
            ),
            "authentication": ServiceConfig(
                name="authentication",
                url=os.getenv("AUTHENTICATION_URL", "http://localhost:8002"),
                health_endpoint="/health",
                version="1.0.0",
            ),
            "integrity": ServiceConfig(
                name="integrity",
                url=os.getenv("INTEGRITY_URL", "http://localhost:8006"),
                health_endpoint="/health",
                version="1.0.0",
            ),
        }
        self._services.update(services)

    def get_service_url(self, service_name: str) -> str | None:
        """Get service URL by name"""
        service = self._services.get(service_name)
        return service.url if service else None

    def get_service_config(self, service_name: str) -> ServiceConfig | None:
        """Get full service configuration"""
        return self._services.get(service_name)


# Global registry instance
service_registry = ServiceRegistry()
