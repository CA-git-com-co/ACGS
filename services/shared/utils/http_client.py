"""
Shared HTTP Client Utilities
Constitutional Hash: cdd01ef066bc6cf2

This module provides reusable HTTP client functionality to eliminate duplication
across services and ensure consistent behavior for circuit breakers, retries,
authentication, and error handling.
"""

import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
from typing import Any
from urllib.parse import urljoin

import aiohttp

from ..constants import (
    CONSTITUTIONAL_HASH,
    MESSAGES,
    SERVICE_USER_AGENT,
    ErrorCodes,
    HeaderNames,
    HttpStatusCodes,
    TimeoutValues,
)

logger = logging.getLogger(__name__)


class HTTPMethod(Enum):
    """Supported HTTP methods."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    HEAD = "HEAD"
    OPTIONS = "OPTIONS"


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 30.0
    exponential_base: float = 2.0
    jitter: bool = True


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior."""

    failure_threshold: int = 5
    timeout: int = TimeoutValues.CIRCUIT_BREAKER_TIMEOUT
    expected_exception: type = Exception


@dataclass
class HTTPClientConfig:
    """Configuration for HTTP client behavior."""

    base_url: str
    timeout: int = TimeoutValues.HTTP_TOTAL_TIMEOUT
    connect_timeout: int = TimeoutValues.HTTP_CONNECT_TIMEOUT
    read_timeout: int = TimeoutValues.HTTP_READ_TIMEOUT
    retry_config: RetryConfig | None = None
    circuit_breaker_config: CircuitBreakerConfig | None = None
    enable_constitutional_validation: bool = True
    enable_rate_limiting: bool = True
    max_concurrent_requests: int = 50


class HTTPClientError(Exception):
    """Base exception for HTTP client errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        error_code: str | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code


class HTTPTimeoutError(HTTPClientError):
    """Exception raised when HTTP request times out."""


class HTTPRetryExhaustedError(HTTPClientError):
    """Exception raised when all retry attempts are exhausted."""


class CircuitBreakerOpenError(HTTPClientError):
    """Exception raised when circuit breaker is open."""


class ConstitutionalValidationError(HTTPClientError):
    """Exception raised when constitutional validation fails."""


class CircuitBreaker:
    """Circuit breaker implementation for HTTP clients."""

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open

    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection."""
        if self.state == "open":
            if time.time() - self.last_failure_time < self.config.timeout:
                raise CircuitBreakerOpenError("Circuit breaker is open")
            self.state = "half_open"

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.config.expected_exception:
            self._on_failure()
            raise

    def _on_success(self):
        """Handle successful request."""
        self.failure_count = 0
        self.state = "closed"

    def _on_failure(self):
        """Handle failed request."""
        self.failure_count += 1
        if self.failure_count >= self.config.failure_threshold:
            self.state = "open"
            self.last_failure_time = time.time()


class RateLimiter:
    """Token bucket rate limiter for HTTP clients."""

    def __init__(self, rate: float = 100.0, capacity: int = 100):
        self.rate = rate  # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = asyncio.Lock()

    async def acquire(self, tokens: int = 1) -> bool:
        """Acquire tokens from the bucket."""
        async with self._lock:
            now = time.time()
            # Add tokens based on elapsed time
            elapsed = now - self.last_refill
            self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
            self.last_refill = now

            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False


class AsyncHTTPClient:
    """Async HTTP client with constitutional validation, retries, and circuit breaker."""

    def __init__(self, config: HTTPClientConfig):
        self.config = config
        self.session: aiohttp.ClientSession | None = None
        self.circuit_breaker = None
        self.rate_limiter = None

        if config.circuit_breaker_config:
            self.circuit_breaker = CircuitBreaker(config.circuit_breaker_config)

        if config.enable_rate_limiting:
            self.rate_limiter = RateLimiter()

        # Initialize retry config if not provided
        if config.retry_config is None:
            config.retry_config = RetryConfig()

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def _ensure_session(self):
        """Ensure HTTP session is created."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(
                total=self.config.timeout,
                connect=self.config.connect_timeout,
                sock_read=self.config.read_timeout,
            )

            connector = aiohttp.TCPConnector(
                limit=self.config.max_concurrent_requests,
                limit_per_host=self.config.max_concurrent_requests,
            )

            self.session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={
                    HeaderNames.USER_AGENT.value: SERVICE_USER_AGENT,
                    HeaderNames.X_CONSTITUTIONAL_HASH.value: CONSTITUTIONAL_HASH,
                },
            )

    async def close(self):
        """Close the HTTP session."""
        if self.session and not self.session.closed:
            await self.session.close()

    def _build_url(self, endpoint: str) -> str:
        """Build full URL from endpoint."""
        return urljoin(self.config.base_url, endpoint)

    def _prepare_headers(self, headers: dict[str, str] | None = None) -> dict[str, str]:
        """Prepare request headers with constitutional validation."""
        final_headers = {
            HeaderNames.X_CONSTITUTIONAL_HASH.value: CONSTITUTIONAL_HASH,
            HeaderNames.USER_AGENT.value: SERVICE_USER_AGENT,
        }

        if headers:
            final_headers.update(headers)

        return final_headers

    def _validate_constitutional_compliance(self, headers: dict[str, str]):
        """Validate constitutional compliance in headers."""
        if not self.config.enable_constitutional_validation:
            return

        constitutional_hash = headers.get(HeaderNames.X_CONSTITUTIONAL_HASH.value)
        if constitutional_hash != CONSTITUTIONAL_HASH:
            raise ConstitutionalValidationError(
                f"Constitutional hash mismatch: expected {CONSTITUTIONAL_HASH}, got"
                f" {constitutional_hash}",
                error_code=ErrorCodes.CONSTITUTIONAL_HASH_MISMATCH.value,
            )

    async def _calculate_delay(self, attempt: int) -> float:
        """Calculate retry delay with exponential backoff and jitter."""
        config = self.config.retry_config
        delay = min(
            config.base_delay * (config.exponential_base**attempt), config.max_delay
        )

        if config.jitter:
            # Add ±25% jitter
            import random

            delay *= 0.75 + 0.5 * random.random()

        return delay

    async def _make_request_with_retries(
        self, method: HTTPMethod, url: str, **kwargs
    ) -> aiohttp.ClientResponse:
        """Make HTTP request with retry logic."""
        last_exception = None

        for attempt in range(self.config.retry_config.max_retries + 1):
            try:
                if self.rate_limiter:
                    if not await self.rate_limiter.acquire():
                        raise HTTPClientError(
                            MESSAGES["RATE_LIMIT_EXCEEDED"],
                            status_code=HttpStatusCodes.TOO_MANY_REQUESTS,
                            error_code=ErrorCodes.SERVICE_TIMEOUT.value,
                        )

                await self._ensure_session()

                async with self.session.request(
                    method.value, url, **kwargs
                ) as response:
                    if response.status < 500:  # Don't retry client errors
                        return response

                    if attempt < self.config.retry_config.max_retries:
                        delay = await self._calculate_delay(attempt)
                        logger.warning(
                            f"Request failed with status {response.status}, "
                            f"retrying in {delay:.2f}s (attempt {attempt + 1})"
                        )
                        await asyncio.sleep(delay)
                        continue

                    return response

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                if attempt < self.config.retry_config.max_retries:
                    delay = await self._calculate_delay(attempt)
                    logger.warning(
                        f"Request failed with {type(e).__name__}: {e}, "
                        f"retrying in {delay:.2f}s (attempt {attempt + 1})"
                    )
                    await asyncio.sleep(delay)
                    continue
                break

        if last_exception:
            raise HTTPRetryExhaustedError(
                f"Request failed after {self.config.retry_config.max_retries} retries:"
                f" {last_exception}",
                error_code=ErrorCodes.SERVICE_TIMEOUT.value,
            )

    async def request(
        self,
        method: HTTPMethod,
        endpoint: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        data: str | bytes | None = None,
        **kwargs,
    ) -> dict[str, Any]:
        """Make HTTP request with full error handling and constitutional validation."""
        url = self._build_url(endpoint)
        final_headers = self._prepare_headers(headers)

        # Validate constitutional compliance
        self._validate_constitutional_compliance(final_headers)

        request_kwargs = {"headers": final_headers, "params": params, **kwargs}

        if json_data is not None:
            request_kwargs["json"] = json_data
        elif data is not None:
            request_kwargs["data"] = data

        try:
            if self.circuit_breaker:
                response = self.circuit_breaker.call(
                    self._make_request_with_retries, method, url, **request_kwargs
                )
            else:
                response = await self._make_request_with_retries(
                    method, url, **request_kwargs
                )

            # Handle response
            if response.status >= 400:
                error_text = await response.text()
                raise HTTPClientError(
                    f"HTTP {response.status}: {error_text}",
                    status_code=response.status,
                    error_code=self._map_status_to_error_code(response.status),
                )

            # Parse JSON response
            try:
                return await response.json()
            except (aiohttp.ContentTypeError, json.JSONDecodeError):
                return {"data": await response.text()}

        except CircuitBreakerOpenError:
            raise HTTPClientError(
                "Service temporarily unavailable",
                status_code=HttpStatusCodes.SERVICE_UNAVAILABLE,
                error_code=ErrorCodes.SERVICE_UNAVAILABLE.value,
            )

    def _map_status_to_error_code(self, status_code: int) -> str:
        """Map HTTP status code to application error code."""
        if status_code == HttpStatusCodes.UNAUTHORIZED:
            return ErrorCodes.INVALID_CREDENTIALS.value
        if status_code == HttpStatusCodes.FORBIDDEN:
            return ErrorCodes.INSUFFICIENT_PERMISSIONS.value
        if status_code == HttpStatusCodes.UNPROCESSABLE_ENTITY:
            return ErrorCodes.INVALID_INPUT.value
        if status_code >= 500:
            return ErrorCodes.SERVICE_ERROR.value
        return ErrorCodes.SERVICE_ERROR.value

    # Convenience methods
    async def get(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make GET request."""
        return await self.request(HTTPMethod.GET, endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make POST request."""
        return await self.request(HTTPMethod.POST, endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make PUT request."""
        return await self.request(HTTPMethod.PUT, endpoint, **kwargs)

    async def patch(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make PATCH request."""
        return await self.request(HTTPMethod.PATCH, endpoint, **kwargs)

    async def delete(self, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make DELETE request."""
        return await self.request(HTTPMethod.DELETE, endpoint, **kwargs)


class ServiceHTTPClient:
    """High-level HTTP client for inter-service communication."""

    def __init__(self, service_name: str, base_url: str, **config_kwargs):
        self.service_name = service_name

        config = HTTPClientConfig(base_url=base_url, **config_kwargs)
        self.client = AsyncHTTPClient(config)

    async def __aenter__(self):
        """Async context manager entry."""
        return await self.client.__aenter__()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        return await self.client.__aexit__(exc_type, exc_val, exc_tb)

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on the service."""
        try:
            return await self.client.get("/health")
        except HTTPClientError as e:
            logger.error(f"Health check failed for {self.service_name}: {e}")
            return {
                "status": "unhealthy",
                "service": self.service_name,
                "error": str(e),
            }

    async def constitutional_validate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Validate data against constitutional compliance."""
        return await self.client.post("/v1/constitutional/validate", json_data=data)

    async def close(self):
        """Close the client."""
        await self.client.close()


# Factory functions for creating commonly used clients
def create_auth_client(base_url: str) -> ServiceHTTPClient:
    """Create HTTP client for authentication service."""
    return ServiceHTTPClient(
        "auth-service",
        base_url,
        retry_config=RetryConfig(max_retries=2),
        circuit_breaker_config=CircuitBreakerConfig(failure_threshold=3),
    )


def create_constitutional_ai_client(base_url: str) -> ServiceHTTPClient:
    """Create HTTP client for constitutional AI service."""
    return ServiceHTTPClient(
        "constitutional-ai",
        base_url,
        retry_config=RetryConfig(max_retries=3),
        circuit_breaker_config=CircuitBreakerConfig(failure_threshold=5),
    )


def create_governance_synthesis_client(base_url: str) -> ServiceHTTPClient:
    """Create HTTP client for governance synthesis service."""
    return ServiceHTTPClient(
        "governance-synthesis",
        base_url,
        retry_config=RetryConfig(max_retries=2),
        circuit_breaker_config=CircuitBreakerConfig(failure_threshold=3),
    )


@asynccontextmanager
async def managed_http_client(config: HTTPClientConfig):
    """Context manager for HTTP client lifecycle."""
    client = AsyncHTTPClient(config)
    try:
        yield client
    finally:
        await client.close()
