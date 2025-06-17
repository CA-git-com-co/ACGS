"""
FV Service Client for Policy Governance Compiler

Provides integration with the Formal Verification (FV) service to validate
policy correctness through formal verification techniques.
"""

import asyncio
import logging
import time
from typing import Any

import httpx
from httpx import AsyncClient, Timeout

from ..config.service_config import get_service_config

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker implementation for resilient service calls."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout_ms: int = 30000,
        half_open_max_calls: int = 3,
    ):
        """Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout_ms: Time in milliseconds before attempting recovery
            half_open_max_calls: Max calls in half-open state
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout_ms = recovery_timeout_ms
        self.half_open_max_calls = half_open_max_calls

        self.failures = 0
        self.state = "closed"  # closed, open, half-open
        self.last_failure_time = 0
        self.half_open_calls = 0

    async def execute(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection.

        Args:
            func: Async function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result of func execution

        Raises:
            Exception: If circuit is open or function execution fails
        """
        if self.state == "open":
            # Check if recovery timeout has elapsed
            if (time.time() * 1000 - self.last_failure_time) > self.recovery_timeout_ms:
                logger.info("Circuit transitioning from open to half-open")
                self.state = "half-open"
                self.half_open_calls = 0
            else:
                raise Exception("Circuit breaker is open")

        if (
            self.state == "half-open"
            and self.half_open_calls >= self.half_open_max_calls
        ):
            raise Exception("Circuit breaker is half-open and max calls reached")

        try:
            if self.state == "half-open":
                self.half_open_calls += 1

            result = await func(*args, **kwargs)

            # Success - reset or close circuit
            if self.state == "half-open":
                logger.info("Circuit recovered, transitioning to closed")
                self.state = "closed"
                self.failures = 0
            elif self.state == "closed":
                self.failures = 0

            return result

        except Exception as e:
            # Failure - increment counter or open circuit
            self.failures += 1
            self.last_failure_time = time.time() * 1000

            if self.state == "half-open" or self.failures >= self.failure_threshold:
                logger.warning(f"Circuit transitioning to open due to: {str(e)}")
                self.state = "open"

            raise


class FVServiceClient:
    """Client for Formal Verification Service integration."""

    def __init__(self):
        """Initialize FV service client."""
        config = get_service_config()
        fv_config = config.get_section("integrations").get("fv_service", {})

        self.base_url = fv_config.get("url", "http://fv_service:8083")
        self.timeout_ms = fv_config.get("timeout_ms", 5000)
        self.retry_attempts = fv_config.get("retry_attempts", 3)
        self.retry_delay_ms = fv_config.get("retry_delay_ms", 500)

        self.circuit_breaker_enabled = fv_config.get("circuit_breaker_enabled", True)
        if self.circuit_breaker_enabled:
            self.circuit_breaker = CircuitBreaker()

        self.client: AsyncClient | None = None

    async def initialize(self) -> None:
        """Initialize HTTP client if not already initialized."""
        if self.client is None:
            timeout = Timeout(timeout=self.timeout_ms / 1000)
            self.client = AsyncClient(
                base_url=self.base_url,
                timeout=timeout,
                headers={"Content-Type": "application/json"},
                follow_redirects=True,
            )

    async def close(self) -> None:
        """Close HTTP client."""
        if self.client:
            await self.client.aclose()
            self.client = None

    async def _make_request(
        self, method: str, endpoint: str, data: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Make HTTP request to FV service with retry logic.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request data (for POST, PUT, etc.)

        Returns:
            Response data

        Raises:
            Exception: If request fails after retries
        """
        await self.initialize()

        method = method.upper()
        url = f"{self.base_url}{endpoint}"

        for attempt in range(self.retry_attempts):
            try:
                def exec_func():
                    return self._execute_request(method, url, data)

                if self.circuit_breaker_enabled:
                    response = await self.circuit_breaker.execute(exec_func)
                else:
                    response = await exec_func()

                return response

            except Exception as e:
                logger.warning(
                    f"Request to {url} failed (attempt {attempt+1}/{self.retry_attempts}): {str(e)}"
                )
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay_ms / 1000)
                else:
                    logger.error(
                        f"Request to {url} failed after {self.retry_attempts} attempts"
                    )
                    raise

    async def _execute_request(
        self, method: str, url: str, data: dict[str, Any] | None
    ) -> dict[str, Any]:
        """Execute HTTP request.

        Args:
            method: HTTP method
            url: Full URL
            data: Request data

        Returns:
            Response data

        Raises:
            Exception: If request fails
        """
        start_time = time.time()

        try:
            if method == "GET":
                response = await self.client.get(url)
            elif method == "POST":
                response = await self.client.post(url, json=data)
            elif method == "PUT":
                response = await self.client.put(url, json=data)
            elif method == "DELETE":
                response = await self.client.delete(url)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise
        finally:
            duration_ms = (time.time() - start_time) * 1000
            logger.debug(f"{method} {url} completed in {duration_ms:.2f}ms")

    async def verify_policy(
        self, policy_content: str, policy_id: str, verification_level: str = "standard"
    ) -> dict[str, Any]:
        """Verify policy using formal verification techniques.

        Args:
            policy_content: Policy content to verify
            policy_id: Policy identifier
            verification_level: Verification level (basic, standard, comprehensive)

        Returns:
            Verification results
        """
        endpoint = "/api/v1/verification/policy"
        data = {
            "policy_content": policy_content,
            "policy_id": policy_id,
            "verification_level": verification_level,
            "source": "pgc_service",
        }

        return await self._make_request("POST", endpoint, data)

    async def verify_policy_batch(
        self, policies: list[dict[str, str]], verification_level: str = "standard"
    ) -> dict[str, Any]:
        """Verify multiple policies in a single batch request.

        Args:
            policies: List of policies with content and ID
            verification_level: Verification level (basic, standard, comprehensive)

        Returns:
            Batch verification results
        """
        endpoint = "/api/v1/verification/policy/batch"
        data = {
            "policies": policies,
            "verification_level": verification_level,
            "source": "pgc_service",
        }

        return await self._make_request("POST", endpoint, data)

    async def verify_constitutional_compliance(
        self, policy_content: str, principle_ids: list[str]
    ) -> dict[str, Any]:
        """Verify policy's compliance with constitutional principles.

        Args:
            policy_content: Policy content to verify
            principle_ids: List of principle IDs to check against

        Returns:
            Constitutional compliance results
        """
        endpoint = "/api/v1/verification/constitutional"
        data = {
            "policy_content": policy_content,
            "principle_ids": principle_ids,
            "source": "pgc_service",
        }

        return await self._make_request("POST", endpoint, data)

    async def get_verification_status(self, verification_id: str) -> dict[str, Any]:
        """Get status of an asynchronous verification request.

        Args:
            verification_id: Verification request ID

        Returns:
            Verification status
        """
        endpoint = f"/api/v1/verification/status/{verification_id}"
        return await self._make_request("GET", endpoint)

    async def get_service_health(self) -> dict[str, Any]:
        """Get FV service health status.

        Returns:
            Health status information
        """
        endpoint = "/health"
        return await self._make_request("GET", endpoint)


# Singleton instance
_fv_service_client = None


async def get_fv_service_client() -> FVServiceClient:
    """Get or create FV service client singleton.

    Returns:
        FVServiceClient instance
    """
    global _fv_service_client
    if _fv_service_client is None:
        _fv_service_client = FVServiceClient()
        await _fv_service_client.initialize()

    return _fv_service_client
