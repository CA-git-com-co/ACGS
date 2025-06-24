"""
Base model client for foundation model integration.
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, List, Optional

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


@dataclass
class ModelRequest:
    """Model request data structure."""

    prompt: str
    system_prompt: Optional[str] = None
    max_tokens: int = 1000
    temperature: float = 0.7
    top_p: float = 0.9
    stop_sequences: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ModelResponse:
    """Model response data structure."""

    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    response_time: float
    metadata: Optional[Dict[str, Any]] = None


class ModelClient(ABC):
    """
    Abstract base class for foundation model clients.

    Provides common functionality for rate limiting, retries,
    and error handling across different model providers.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str,
        timeout: int = 30,
        max_retries: int = 3,
        rate_limit_requests: int = 100,
        rate_limit_window: int = 60,
    ):
        self.api_key = api_key
        self.model_name = model_name
        self.timeout = timeout
        self.max_retries = max_retries

        # Rate limiting
        self.rate_limit_requests = rate_limit_requests
        self.rate_limit_window = rate_limit_window
        self.request_times: List[float] = []

        # Usage tracking
        self.total_requests = 0
        self.total_tokens = 0
        self.total_cost = 0.0

        # Circuit breaker state
        self.consecutive_failures = 0
        self.max_consecutive_failures = 5
        self.circuit_open_until = 0

    @abstractmethod
    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate response from the model."""
        pass

    @abstractmethod
    async def generate_stream(self, request: ModelRequest) -> AsyncGenerator[str, None]:
        """Generate streaming response from the model."""
        pass

    async def _check_rate_limit(self):
        """Check and enforce rate limiting."""
        current_time = time.time()

        # Remove old requests outside the window
        self.request_times = [
            req_time
            for req_time in self.request_times
            if current_time - req_time < self.rate_limit_window
        ]

        # Check if we're at the limit
        if len(self.request_times) >= self.rate_limit_requests:
            sleep_time = self.rate_limit_window - (current_time - self.request_times[0])
            if sleep_time > 0:
                logger.warning(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                await asyncio.sleep(sleep_time)

        # Record this request
        self.request_times.append(current_time)

    def _check_circuit_breaker(self):
        """Check circuit breaker state."""
        if self.circuit_open_until > time.time():
            raise Exception("Circuit breaker is open - too many consecutive failures")

    def _record_success(self):
        """Record successful request."""
        self.consecutive_failures = 0
        self.total_requests += 1

    def _record_failure(self):
        """Record failed request."""
        self.consecutive_failures += 1
        if self.consecutive_failures >= self.max_consecutive_failures:
            # Open circuit breaker for 5 minutes
            self.circuit_open_until = time.time() + 300
            logger.error("Circuit breaker opened due to consecutive failures")

    def _validate_request(self, request: ModelRequest):
        """Validate request parameters."""
        if not request.prompt:
            raise ValueError("Prompt cannot be empty")

        if request.max_tokens <= 0:
            raise ValueError("max_tokens must be positive")

        if not 0 <= request.temperature <= 2:
            raise ValueError("temperature must be between 0 and 2")

        if not 0 <= request.top_p <= 1:
            raise ValueError("top_p must be between 0 and 1")

    def _calculate_cost(self, usage: Dict[str, int]) -> float:
        """Calculate cost based on token usage."""
        # This would be implemented by subclasses with provider-specific pricing
        return 0.0

    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics."""
        return {
            "total_requests": self.total_requests,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "consecutive_failures": self.consecutive_failures,
            "circuit_breaker_open": self.circuit_open_until > time.time(),
            "rate_limit_remaining": max(0, self.rate_limit_requests - len(self.request_times)),
        }


class ModelClientError(Exception):
    """Base exception for model client errors."""

    pass


class RateLimitError(ModelClientError):
    """Rate limit exceeded error."""

    pass


class AuthenticationError(ModelClientError):
    """Authentication error."""

    pass


class ModelUnavailableError(ModelClientError):
    """Model unavailable error."""

    pass


class TokenLimitError(ModelClientError):
    """Token limit exceeded error."""

    pass
