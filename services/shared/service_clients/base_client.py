"""
Base service client for ACGS inter-service communication
Constitutional Hash: cdd01ef066bc6cf2

This module provides a base client that all services can use to communicate
with each other, preventing circular dependencies.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import httpx
from pydantic import BaseModel


class ServiceClientConfig(BaseModel):
    """Configuration for service clients"""

    base_url: str
    timeout: float = 30.0
    retries: int = 3
    constitutional_hash: str = "cdd01ef066bc6cf2"


class BaseServiceClient(ABC):
    """
    Base class for all ACGS service clients.

    This provides a common interface for inter-service communication
    while maintaining constitutional compliance.
    """

    def __init__(self, config: ServiceClientConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.disconnect()

    async def connect(self):
        """Initialize the HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
                headers={
                    "X-Constitutional-Hash": self.config.constitutional_hash,
                    "Content-Type": "application/json",
                },
            )

    async def disconnect(self):
        """Close the HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make a request to another service with retry logic
        """
        if not self._client:
            await self.connect()

        for attempt in range(self.config.retries):
            try:
                response = await self._client.request(
                    method=method, url=endpoint, json=data, params=params
                )
                response.raise_for_status()
                return response.json()

            except httpx.RequestError as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt == self.config.retries - 1:
                    raise
                await asyncio.sleep(2**attempt)  # Exponential backoff

            except httpx.HTTPStatusError as e:
                self.logger.error(
                    f"HTTP error {e.response.status_code}: {e.response.text}"
                )
                raise

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the target service is healthy"""
        pass


class ConstitutionalCoreClient(BaseServiceClient):
    """Client for unified Constitutional Core service"""

    async def health_check(self) -> bool:
        try:
            await self.request("GET", "/health")
            return True
        except Exception:
            return False

    async def validate_constitutional_compliance(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate constitutional compliance"""
        return await self.request(
            "POST", "/api/v1/constitutional/validate", data=request_data
        )

    async def verify_formal_specification(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Verify formal specification using Z3 SMT solver"""
        return await self.request(
            "POST", "/api/v1/verification/verify", data=request_data
        )

    async def evaluate_unified_compliance(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evaluate both constitutional and formal compliance"""
        return await self.request(
            "POST", "/api/v1/unified/compliance", data=request_data
        )

    async def list_constitutional_principles(self) -> Dict[str, Any]:
        """List all constitutional principles"""
        return await self.request("GET", "/api/v1/constitutional/principles")

    async def get_constitutional_principle(self, principle_id: str) -> Dict[str, Any]:
        """Get a specific constitutional principle"""
        return await self.request(
            "GET", f"/api/v1/constitutional/principles/{principle_id}"
        )

    async def get_verification_capabilities(self) -> Dict[str, Any]:
        """Get formal verification capabilities"""
        return await self.request("GET", "/api/v1/verification/capabilities")


class GovernanceEngineClient(BaseServiceClient):
    """Client for unified Governance Engine service"""

    async def health_check(self) -> bool:
        try:
            await self.request("GET", "/health")
            return True
        except Exception:
            return False

    async def synthesize_policy(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize a policy"""
        return await self.request(
            "POST", "/api/v1/synthesis/synthesize", data=request_data
        )

    async def enforce_policy(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce a policy"""
        return await self.request(
            "POST", "/api/v1/enforcement/enforce", data=request_data
        )

    async def check_compliance(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance"""
        return await self.request("POST", "/api/v1/compliance/check", data=request_data)

    async def list_workflows(self) -> Dict[str, Any]:
        """List available workflows"""
        return await self.request("GET", "/api/v1/workflows")

    async def execute_workflow(
        self, workflow_id: str, parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a workflow"""
        return await self.request(
            "POST", f"/api/v1/workflows/{workflow_id}/execute", data=parameters
        )


# Factory function to create clients
def create_client(service_name: str, base_url: str, **kwargs) -> BaseServiceClient:
    """Factory function to create service clients"""
    config = ServiceClientConfig(base_url=base_url, **kwargs)

    clients = {
        "constitutional-core": ConstitutionalCoreClient,
        "governance-engine": GovernanceEngineClient,
    }

    client_class = clients.get(service_name)
    if not client_class:
        raise ValueError(f"Unknown service: {service_name}")

    return client_class(config)
