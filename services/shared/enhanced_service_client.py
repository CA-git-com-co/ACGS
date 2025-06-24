"""
Enhanced ACGS Service Client
High-performance service-to-service communication with retry, circuit breakers, and connection pooling
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .enhanced_service_registry import (
    CircuitBreaker,
    enhanced_service_registry,
)

logger = logging.getLogger(__name__)


class RequestMethod(Enum):
    """HTTP request methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    PATCH = "PATCH"


@dataclass
class ServiceCallResult:
    """Result of a service call."""

    success: bool
    data: dict[str, Any] | None = None
    error: str | None = None
    status_code: int | None = None
    response_time: float = 0.0
    service_name: str | None = None
    endpoint: str | None = None
    retries_attempted: int = 0


class EnhancedServiceClient:
    """High-performance service client with advanced reliability patterns."""

    def __init__(
        self,
        connection_pool_size: int = 100,
        timeout: float = 30.0,
        connect_timeout: float = 5.0,
        max_retries: int = 3,
        retry_backoff_factor: float = 1.0,
    ):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.connection_pool_size = connection_pool_size
        self.timeout = timeout
        self.connect_timeout = connect_timeout
        self.max_retries = max_retries
        self.retry_backoff_factor = retry_backoff_factor

        # HTTP client with connection pooling
        self.http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(timeout, connect=connect_timeout),
            limits=httpx.Limits(max_connections=connection_pool_size, max_keepalive_connections=20),
            http2=True,
            follow_redirects=True,
        )

        # Circuit breakers for each service
        self.circuit_breakers: dict[str, CircuitBreaker] = {}

        # Performance metrics
        self.call_metrics = {
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "avg_response_time": 0.0,
            "circuit_breaker_trips": 0,
        }

    async def __aenter__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Async context manager exit."""
        await self.close()

    async def close(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Close the HTTP client."""
        await self.http_client.aclose()

    def _get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for a service."""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker(
                failure_threshold=5, recovery_timeout=60, half_open_max_calls=3
            )
        return self.circuit_breakers[service_name]

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type(
            (httpx.TimeoutException, httpx.ConnectError, httpx.HTTPStatusError)
        ),
    )
    async def _make_http_request(
        self,
        method: RequestMethod,
        url: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Make HTTP request with retry logic."""
        request_kwargs = {"url": url, "headers": headers or {}, "params": params}

        if data and method in [
            RequestMethod.POST,
            RequestMethod.PUT,
            RequestMethod.PATCH,
        ]:
            request_kwargs["json"] = data

        if method == RequestMethod.GET:
            return await self.http_client.get(**request_kwargs)
        elif method == RequestMethod.POST:
            return await self.http_client.post(**request_kwargs)
        elif method == RequestMethod.PUT:
            return await self.http_client.put(**request_kwargs)
        elif method == RequestMethod.DELETE:
            return await self.http_client.delete(**request_kwargs)
        elif method == RequestMethod.PATCH:
            return await self.http_client.patch(**request_kwargs)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    async def call_service(
        self,
        service_name: str,
        endpoint: str,
        method: RequestMethod = RequestMethod.GET,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        use_fallback: bool = True,
        timeout_override: float | None = None,
    ) -> ServiceCallResult:
        """Make a call to another ACGS service with enhanced reliability."""
        start_time = time.time()
        retries_attempted = 0

        # Get service info with fallback
        service_info = (
            enhanced_service_registry.get_service_with_fallback(service_name)
            if use_fallback
            else enhanced_service_registry.get_service(service_name)
        )

        if not service_info:
            return ServiceCallResult(
                success=False,
                error=f"Service {service_name} not found or unavailable",
                service_name=service_name,
                endpoint=endpoint,
            )

        # Check circuit breaker
        circuit_breaker = self._get_circuit_breaker(service_name)
        if not circuit_breaker.can_execute():
            self.call_metrics["circuit_breaker_trips"] += 1
            return ServiceCallResult(
                success=False,
                error=f"Circuit breaker open for service {service_name}",
                service_name=service_name,
                endpoint=endpoint,
            )

        # Construct URL
        url = f"{service_info.base_url}{endpoint}"

        # Add default headers
        default_headers = {
            "Content-Type": "application/json",
            "X-ACGS-Client": "enhanced_service_client",
            "X-ACGS-Source-Service": "unknown",  # Should be set by calling service
            "X-ACGS-Request-ID": f"req_{int(time.time() * 1000)}",
        }

        if headers:
            default_headers.update(headers)

        # Override timeout if specified
        if timeout_override:
            original_timeout = self.http_client.timeout
            self.http_client.timeout = httpx.Timeout(timeout_override, connect=self.connect_timeout)

        try:
            # Make the request with retry logic
            response = await self._make_http_request(
                method=method,
                url=url,
                data=data,
                headers=default_headers,
                params=params,
            )

            response_time = time.time() - start_time

            # Update metrics
            self._update_call_metrics(response_time, True)
            service_info.update_metrics(response_time, True)
            circuit_breaker.record_success()

            # Parse response
            try:
                response_data = response.json() if response.content else {}
            except json.JSONDecodeError:
                response_data = {"raw_response": response.text}

            return ServiceCallResult(
                success=True,
                data=response_data,
                status_code=response.status_code,
                response_time=response_time,
                service_name=service_name,
                endpoint=endpoint,
                retries_attempted=retries_attempted,
            )

        except Exception as e:
            response_time = time.time() - start_time

            # Update metrics
            self._update_call_metrics(response_time, False)
            service_info.update_metrics(response_time, False)
            circuit_breaker.record_failure()

            error_message = f"Service call failed: {str(e)}"
            logger.error(f"Failed to call {service_name}{endpoint}: {error_message}")

            return ServiceCallResult(
                success=False,
                error=error_message,
                response_time=response_time,
                service_name=service_name,
                endpoint=endpoint,
                retries_attempted=retries_attempted,
            )

        finally:
            # Restore original timeout
            if timeout_override:
                self.http_client.timeout = original_timeout

    async def call_service_with_fallback_chain(
        self,
        primary_service: str,
        fallback_services: list[str],
        endpoint: str,
        method: RequestMethod = RequestMethod.GET,
        data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
    ) -> ServiceCallResult:
        """Call service with a chain of fallbacks."""
        services_to_try = [primary_service] + fallback_services

        for service_name in services_to_try:
            result = await self.call_service(
                service_name=service_name,
                endpoint=endpoint,
                method=method,
                data=data,
                headers=headers,
                params=params,
                use_fallback=False,  # We're managing fallback manually
            )

            if result.success:
                if service_name != primary_service:
                    logger.warning(
                        f"Used fallback service {service_name} instead of {primary_service}"
                    )
                return result

            logger.debug(f"Service {service_name} failed, trying next fallback")

        return ServiceCallResult(
            success=False,
            error=f"All services failed: {services_to_try}",
            service_name=primary_service,
            endpoint=endpoint,
        )

    async def batch_call_services(
        self, calls: list[dict[str, Any]], max_concurrent: int = 10
    ) -> list[ServiceCallResult]:
        """Make multiple service calls concurrently."""
        semaphore = asyncio.Semaphore(max_concurrent)

        async def limited_call(call_config):
            # requires: Valid input parameters
            # ensures: Correct function execution
            # sha256: func_hash
            async with semaphore:
                return await self.call_service(**call_config)

        tasks = [limited_call(call) for call in calls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to failed results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    ServiceCallResult(
                        success=False,
                        error=f"Batch call exception: {str(result)}",
                        service_name=calls[i].get("service_name", "unknown"),
                        endpoint=calls[i].get("endpoint", "unknown"),
                    )
                )
            else:
                processed_results.append(result)

        return processed_results

    def _update_call_metrics(self, response_time: float, success: bool):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update call metrics."""
        self.call_metrics["total_calls"] += 1

        if success:
            self.call_metrics["successful_calls"] += 1
        else:
            self.call_metrics["failed_calls"] += 1

        # Update average response time (exponential moving average)
        alpha = 0.1
        self.call_metrics["avg_response_time"] = (
            alpha * response_time + (1 - alpha) * self.call_metrics["avg_response_time"]
        )

    def get_performance_metrics(self) -> dict[str, Any]:
        """Get client performance metrics."""
        total_calls = self.call_metrics["total_calls"]
        success_rate = (
            self.call_metrics["successful_calls"] / total_calls if total_calls > 0 else 1.0
        )

        return {
            "total_calls": total_calls,
            "success_rate": success_rate,
            "avg_response_time": self.call_metrics["avg_response_time"],
            "circuit_breaker_trips": self.call_metrics["circuit_breaker_trips"],
            "active_circuit_breakers": len(self.circuit_breakers),
            "circuit_breaker_states": {
                service: cb.state.value for service, cb in self.circuit_breakers.items()
            },
        }


# Global enhanced service client instance
enhanced_service_client = EnhancedServiceClient()


# Convenience functions
async def call_service(
    service_name: str,
    endpoint: str,
    method: str = "GET",
    data: dict[str, Any] | None = None,
    headers: dict[str, str] | None = None,
    timeout: float | None = None,
) -> dict[str, Any] | None:
    """Convenience function for service calls."""
    method_enum = RequestMethod(method.upper())

    result = await enhanced_service_client.call_service(
        service_name=service_name,
        endpoint=endpoint,
        method=method_enum,
        data=data,
        headers=headers,
        timeout_override=timeout,
    )

    return result.data if result.success else None


# Export main functions and classes
__all__ = [
    "EnhancedServiceClient",
    "ServiceCallResult",
    "RequestMethod",
    "enhanced_service_client",
    "call_service",
]
