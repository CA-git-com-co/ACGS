"""
Tenant-Aware Service Client for ACGS Multi-Tenant Architecture

This module provides HTTP clients for service-to-service communication
with automatic tenant context propagation and constitutional compliance.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

import httpx
from fastapi import Request

from ..repositories.tenant_repository import TenantContext

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class ServiceEndpoint:
    """Configuration for a service endpoint."""

    name: str
    base_url: str
    timeout: int = 30
    retries: int = 3
    circuit_breaker_threshold: int = 5


class TenantServiceClient:
    """
    HTTP client for service-to-service communication with tenant context.

    Automatically includes tenant context in requests and handles
    constitutional compliance validation.
    """

    def __init__(
        self, service_name: str, base_url: str, timeout: int = 30, retries: int = 3
    ):
        self.service_name = service_name
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.client = httpx.AsyncClient(timeout=timeout)

        # Circuit breaker state
        self.failure_count = 0
        self.circuit_open = False
        self.last_failure_time = None
        self.circuit_breaker_threshold = 5
        self.circuit_breaker_timeout = 60  # seconds

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

    def _prepare_headers(
        self,
        tenant_context: TenantContext | None = None,
        additional_headers: dict[str, str] | None = None,
        jwt_token: str | None = None,
    ) -> dict[str, str]:
        """Prepare headers with tenant context and constitutional compliance."""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": f"ACGS-ServiceClient/{self.service_name}",
            "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
            "X-Service-Name": self.service_name,
        }

        # Add tenant context headers
        if tenant_context:
            headers["X-Tenant-ID"] = str(tenant_context.tenant_id)
            headers["X-User-ID"] = (
                str(tenant_context.user_id) if tenant_context.user_id else ""
            )
            headers["X-Organization-ID"] = (
                str(tenant_context.organization_id)
                if tenant_context.organization_id
                else ""
            )
            headers["X-Security-Level"] = tenant_context.security_level or "basic"

        # Add JWT token if provided
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"

        # Add additional headers
        if additional_headers:
            headers.update(additional_headers)

        return headers

    def _check_circuit_breaker(self) -> bool:
        """Check if circuit breaker should prevent the request."""
        if not self.circuit_open:
            return True

        # Check if enough time has passed to try again
        if self.last_failure_time:
            import time

            if time.time() - self.last_failure_time > self.circuit_breaker_timeout:
                self.circuit_open = False
                self.failure_count = 0
                return True

        return False

    def _record_success(self):
        """Record a successful request."""
        self.failure_count = 0
        self.circuit_open = False

    def _record_failure(self):
        """Record a failed request and update circuit breaker state."""
        self.failure_count += 1
        if self.failure_count >= self.circuit_breaker_threshold:
            self.circuit_open = True
            import time

            self.last_failure_time = time.time()
            logger.warning(f"Circuit breaker opened for service {self.service_name}")

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        tenant_context: TenantContext | None = None,
        jwt_token: str | None = None,
        json_data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make an HTTP request with tenant context and retry logic."""

        # Check circuit breaker
        if not self._check_circuit_breaker():
            raise Exception(f"Circuit breaker is open for service {self.service_name}")

        url = f"{self.base_url}{endpoint}"
        request_headers = self._prepare_headers(tenant_context, headers, jwt_token)

        for attempt in range(self.retries + 1):
            try:
                logger.debug(
                    f"Making {method} request to {url} (attempt {attempt + 1})"
                )

                response = await self.client.request(
                    method=method,
                    url=url,
                    json=json_data,
                    params=params,
                    headers=request_headers,
                )

                # Check for constitutional compliance in response
                response_hash = response.headers.get("X-Constitutional-Hash")
                if response_hash and response_hash != CONSTITUTIONAL_HASH:
                    logger.warning(
                        f"Constitutional hash mismatch from {self.service_name}:"
                        f" {response_hash}"
                    )

                response.raise_for_status()
                self._record_success()

                return response.json() if response.content else {}

            except httpx.HTTPStatusError as e:
                logger.exception(
                    f"HTTP error from {self.service_name}: {e.response.status_code} -"
                    f" {e.response.text}"
                )
                if attempt == self.retries:
                    self._record_failure()
                    raise Exception(
                        f"HTTP {e.response.status_code} from {self.service_name}:"
                        f" {e.response.text}"
                    )

            except httpx.RequestError as e:
                logger.exception(f"Request error to {self.service_name}: {e}")
                if attempt == self.retries:
                    self._record_failure()
                    raise Exception(f"Request failed to {self.service_name}: {e}")

            except Exception as e:
                logger.exception(f"Unexpected error calling {self.service_name}: {e}")
                if attempt == self.retries:
                    self._record_failure()
                    raise Exception(
                        f"Unexpected error calling {self.service_name}: {e}"
                    )

            # Wait before retry (exponential backoff)
            if attempt < self.retries:
                wait_time = (2**attempt) * 0.5  # 0.5, 1, 2 seconds
                await asyncio.sleep(wait_time)

        self._record_failure()
        raise Exception(f"All retry attempts failed for {self.service_name}")

    async def get(
        self,
        endpoint: str,
        tenant_context: TenantContext | None = None,
        jwt_token: str | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a GET request with tenant context."""
        return await self._make_request(
            "GET", endpoint, tenant_context, jwt_token, None, params, headers
        )

    async def post(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        tenant_context: TenantContext | None = None,
        jwt_token: str | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a POST request with tenant context."""
        return await self._make_request(
            "POST", endpoint, tenant_context, jwt_token, data, params, headers
        )

    async def put(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        tenant_context: TenantContext | None = None,
        jwt_token: str | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a PUT request with tenant context."""
        return await self._make_request(
            "PUT", endpoint, tenant_context, jwt_token, data, params, headers
        )

    async def delete(
        self,
        endpoint: str,
        tenant_context: TenantContext | None = None,
        jwt_token: str | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make a DELETE request with tenant context."""
        return await self._make_request(
            "DELETE", endpoint, tenant_context, jwt_token, None, params, headers
        )

    async def health_check(self) -> dict[str, Any]:
        """Check service health."""
        try:
            return await self.get("/health")
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


class TenantServiceRegistry:
    """
    Registry for managing service endpoints and client connections
    in a multi-tenant environment.
    """

    def __init__(self):
        self.services: dict[str, ServiceEndpoint] = {}
        self.clients: dict[str, TenantServiceClient] = {}

    def register_service(
        self,
        name: str,
        base_url: str,
        timeout: int = 30,
        retries: int = 3,
        circuit_breaker_threshold: int = 5,
    ):
        """Register a service endpoint."""
        self.services[name] = ServiceEndpoint(
            name=name,
            base_url=base_url,
            timeout=timeout,
            retries=retries,
            circuit_breaker_threshold=circuit_breaker_threshold,
        )
        logger.info(f"Registered service: {name} at {base_url}")

    def get_client(self, service_name: str) -> TenantServiceClient:
        """Get or create a client for a service."""
        if service_name not in self.clients:
            if service_name not in self.services:
                raise ValueError(f"Service {service_name} not registered")

            endpoint = self.services[service_name]
            self.clients[service_name] = TenantServiceClient(
                service_name=endpoint.name,
                base_url=endpoint.base_url,
                timeout=endpoint.timeout,
                retries=endpoint.retries,
            )

        return self.clients[service_name]

    async def health_check_all(self) -> dict[str, dict[str, Any]]:
        """Check health of all registered services."""
        results = {}

        for service_name in self.services:
            try:
                client = self.get_client(service_name)
                health = await client.health_check()
                results[service_name] = health
            except Exception as e:
                results[service_name] = {"status": "unhealthy", "error": str(e)}

        return results

    async def close_all_clients(self):
        """Close all client connections."""
        for client in self.clients.values():
            await client.client.aclose()
        self.clients.clear()


# Global service registry instance
service_registry = TenantServiceRegistry()


# Helper functions for FastAPI dependency injection
def get_service_client(service_name: str) -> TenantServiceClient:
    """FastAPI dependency to get a service client."""
    return service_registry.get_client(service_name)


def extract_tenant_context_from_request(request: Request) -> TenantContext | None:
    """Extract tenant context from FastAPI request object."""
    return getattr(request.state, "tenant_context", None)


async def call_service_with_context(
    service_name: str,
    endpoint: str,
    method: str = "GET",
    data: dict[str, Any] | None = None,
    request: Request | None = None,
    tenant_context: TenantContext | None = None,
    jwt_token: str | None = None,
) -> dict[str, Any]:
    """
    Convenience function to call a service with tenant context.

    Automatically extracts tenant context from request if not provided.
    """
    client = service_registry.get_client(service_name)

    # Extract tenant context from request if not provided
    if not tenant_context and request:
        tenant_context = extract_tenant_context_from_request(request)

    # Extract JWT token from request if not provided
    if not jwt_token and request:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            jwt_token = auth_header[7:]

    # Make the request
    if method.upper() == "GET":
        return await client.get(endpoint, tenant_context, jwt_token)
    if method.upper() == "POST":
        return await client.post(endpoint, data, tenant_context, jwt_token)
    if method.upper() == "PUT":
        return await client.put(endpoint, data, tenant_context, jwt_token)
    if method.upper() == "DELETE":
        return await client.delete(endpoint, tenant_context, jwt_token)
    raise ValueError(f"Unsupported HTTP method: {method}")


# Initialize default service endpoints
def initialize_default_services():
    """Initialize default ACGS service endpoints."""
    import os

    # Register core ACGS services
    service_registry.register_service(
        "auth_service", os.getenv("AUTH_SERVICE_URL", "http://localhost:8000")
    )

    service_registry.register_service(
        "constitutional_ai_service",
        os.getenv("CONSTITUTIONAL_AI_SERVICE_URL", "http://localhost:8001"),
    )

    service_registry.register_service(
        "integrity_service", os.getenv("INTEGRITY_SERVICE_URL", "http://localhost:8002")
    )

    service_registry.register_service(
        "governance_synthesis_service",
        os.getenv("GOVERNANCE_SYNTHESIS_SERVICE_URL", "http://localhost:8004"),
    )

    service_registry.register_service(
        "policy_governance_service",
        os.getenv("POLICY_GOVERNANCE_SERVICE_URL", "http://localhost:8005"),
    )

    service_registry.register_service(
        "formal_verification_service",
        os.getenv("FORMAL_VERIFICATION_SERVICE_URL", "http://localhost:8006"),
    )

    service_registry.register_service(
        "unified_evolution_compiler_service",
        os.getenv("UNIFIED_EVOLUTION_COMPILER_SERVICE_URL", "http://localhost:8006"),
    )

    logger.info("Initialized default ACGS service endpoints")


# Auto-initialize on module import
initialize_default_services()
