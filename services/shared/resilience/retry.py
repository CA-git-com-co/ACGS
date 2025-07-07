"""
Retry Pattern Implementation
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive retry mechanisms with various backoff strategies.
"""

import asyncio
import logging
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Callable, List, Optional, Type, Union

from .exceptions import InfrastructureError, TimeoutError

logger = logging.getLogger(__name__)


class RetryError(InfrastructureError):
    """Raised when all retry attempts are exhausted."""

    def __init__(self, operation: str, attempts: int, last_error: Exception, **kwargs):
        message = f"Retry exhausted for '{operation}' after {attempts} attempts"
        super().__init__(message, **kwargs)
        self.operation = operation
        self.attempts = attempts
        self.last_error = last_error
        self.details.update(
            {
                "operation": operation,
                "attempts": attempts,
                "last_error": str(last_error),
                "last_error_type": type(last_error).__name__,
            }
        )


class BackoffStrategy(ABC):
    """Abstract base class for backoff strategies."""

    @abstractmethod
    def get_delay(self, attempt: int) -> float:
        """Get delay in seconds for the given attempt number."""
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset strategy state."""
        pass


class FixedBackoff(BackoffStrategy):
    """Fixed delay backoff strategy."""

    def __init__(self, delay: float = 1.0):
        self.delay = delay

    def get_delay(self, attempt: int) -> float:
        return self.delay

    def reset(self) -> None:
        pass


class LinearBackoff(BackoffStrategy):
    """Linear backoff strategy with optional jitter."""

    def __init__(
        self, base_delay: float = 1.0, increment: float = 1.0, jitter: bool = True
    ):
        self.base_delay = base_delay
        self.increment = increment
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        delay = self.base_delay + (attempt * self.increment)
        if self.jitter:
            delay += random.uniform(0, delay * 0.1)  # Add up to 10% jitter
        return delay

    def reset(self) -> None:
        pass


class ExponentialBackoff(BackoffStrategy):
    """Exponential backoff strategy with optional jitter and max delay."""

    def __init__(
        self,
        base_delay: float = 1.0,
        multiplier: float = 2.0,
        max_delay: float = 60.0,
        jitter: bool = True,
    ):
        self.base_delay = base_delay
        self.multiplier = multiplier
        self.max_delay = max_delay
        self.jitter = jitter

    def get_delay(self, attempt: int) -> float:
        delay = self.base_delay * (self.multiplier**attempt)
        delay = min(delay, self.max_delay)

        if self.jitter:
            # Full jitter: random between 0 and calculated delay
            delay = random.uniform(0, delay)

        return delay

    def reset(self) -> None:
        pass


class DecorrelatedJitterBackoff(BackoffStrategy):
    """Decorrelated jitter backoff to avoid thundering herd."""

    def __init__(self, base_delay: float = 1.0, max_delay: float = 60.0):
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.previous_delay = base_delay

    def get_delay(self, attempt: int) -> float:
        delay = random.uniform(self.base_delay, self.previous_delay * 3)
        delay = min(delay, self.max_delay)
        self.previous_delay = delay
        return delay

    def reset(self) -> None:
        self.previous_delay = self.base_delay


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    backoff_strategy: BackoffStrategy = None
    retryable_exceptions: List[Type[Exception]] = None
    timeout: Optional[float] = None
    on_retry: Optional[Callable[[int, Exception], None]] = None

    def __post_init__(self):
        if self.backoff_strategy is None:
            self.backoff_strategy = ExponentialBackoff()

        if self.retryable_exceptions is None:
            self.retryable_exceptions = [
                InfrastructureError,
                TimeoutError,
                ConnectionError,
                asyncio.TimeoutError,
            ]


class RetryPolicy:
    """
    Retry policy implementation with configurable strategies.

    Provides resilient execution of operations with various backoff strategies
    and customizable retry conditions.
    """

    def __init__(self, config: RetryConfig = None):
        self.config = config or RetryConfig()
        logger.debug(
            f"Retry policy created with max_attempts={self.config.max_attempts}"
        )

    async def execute(
        self, func: Callable, *args, operation_name: str = None, **kwargs
    ) -> Any:
        """
        Execute function with retry logic.

        Args:
            func: Function to execute
            *args: Function arguments
            operation_name: Name for logging/errors
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            RetryError: When all attempts are exhausted
        """
        operation_name = operation_name or func.__name__
        last_error = None
        self.config.backoff_strategy.reset()

        for attempt in range(self.config.max_attempts):
            try:
                logger.debug(
                    f"Attempting '{operation_name}' - attempt {attempt + 1}/{self.config.max_attempts}"
                )

                if self.config.timeout:
                    result = await asyncio.wait_for(
                        self._ensure_coroutine(func(*args, **kwargs)),
                        timeout=self.config.timeout,
                    )
                else:
                    result = await self._ensure_coroutine(func(*args, **kwargs))

                if attempt > 0:
                    logger.info(
                        f"'{operation_name}' succeeded on attempt {attempt + 1}"
                    )

                return result

            except Exception as e:
                last_error = e

                # Check if exception is retryable
                if not self._is_retryable(e):
                    logger.error(
                        f"'{operation_name}' failed with non-retryable error: {e}"
                    )
                    raise e

                # Check if we have more attempts
                if attempt == self.config.max_attempts - 1:
                    logger.error(
                        f"'{operation_name}' exhausted all {self.config.max_attempts} attempts"
                    )
                    break

                # Calculate delay and wait
                delay = self.config.backoff_strategy.get_delay(attempt)
                logger.warning(
                    f"'{operation_name}' attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {delay:.2f}s"
                )

                # Call retry callback if provided
                if self.config.on_retry:
                    try:
                        self.config.on_retry(attempt + 1, e)
                    except Exception as callback_error:
                        logger.error(f"Retry callback failed: {callback_error}")

                await asyncio.sleep(delay)

        # All attempts exhausted
        raise RetryError(operation_name, self.config.max_attempts, last_error)

    def _is_retryable(self, exception: Exception) -> bool:
        """Check if exception is retryable based on configuration."""
        return any(
            isinstance(exception, exc_type)
            for exc_type in self.config.retryable_exceptions
        )

    async def _ensure_coroutine(self, result: Any) -> Any:
        """Ensure result is awaitable."""
        if asyncio.iscoroutine(result):
            return await result
        return result


def retry(
    max_attempts: int = 3,
    backoff_strategy: BackoffStrategy = None,
    retryable_exceptions: List[Type[Exception]] = None,
    timeout: Optional[float] = None,
    operation_name: str = None,
):
    """
    Decorator for adding retry behavior to functions.

    Args:
        max_attempts: Maximum number of retry attempts
        backoff_strategy: Backoff strategy to use
        retryable_exceptions: List of retryable exception types
        timeout: Timeout for each attempt
        operation_name: Name for logging/errors
    """

    def decorator(func: Callable) -> Callable:
        config = RetryConfig(
            max_attempts=max_attempts,
            backoff_strategy=backoff_strategy,
            retryable_exceptions=retryable_exceptions,
            timeout=timeout,
        )
        policy = RetryPolicy(config)

        async def wrapper(*args, **kwargs):
            return await policy.execute(
                func, *args, operation_name=operation_name or func.__name__, **kwargs
            )

        return wrapper

    return decorator


class CircuitBreakerRetryPolicy(RetryPolicy):
    """Retry policy that integrates with circuit breaker."""

    def __init__(self, config: RetryConfig = None, circuit_breaker=None):
        super().__init__(config)
        self.circuit_breaker = circuit_breaker

    async def execute(
        self, func: Callable, *args, operation_name: str = None, **kwargs
    ) -> Any:
        """Execute with circuit breaker integration."""
        if self.circuit_breaker:
            # Use circuit breaker for execution
            return await self.circuit_breaker.call(
                lambda: super().execute(
                    func, *args, operation_name=operation_name, **kwargs
                )
            )
        else:
            # Fallback to normal retry
            return await super().execute(
                func, *args, operation_name=operation_name, **kwargs
            )


# Convenience functions for common retry patterns


async def retry_with_exponential_backoff(
    func: Callable,
    *args,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    operation_name: str = None,
    **kwargs,
) -> Any:
    """Retry with exponential backoff strategy."""
    config = RetryConfig(
        max_attempts=max_attempts,
        backoff_strategy=ExponentialBackoff(base_delay=base_delay, max_delay=max_delay),
    )
    policy = RetryPolicy(config)
    return await policy.execute(func, *args, operation_name=operation_name, **kwargs)


async def retry_with_linear_backoff(
    func: Callable,
    *args,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    increment: float = 1.0,
    operation_name: str = None,
    **kwargs,
) -> Any:
    """Retry with linear backoff strategy."""
    config = RetryConfig(
        max_attempts=max_attempts,
        backoff_strategy=LinearBackoff(base_delay=base_delay, increment=increment),
    )
    policy = RetryPolicy(config)
    return await policy.execute(func, *args, operation_name=operation_name, **kwargs)


async def retry_with_fixed_delay(
    func: Callable,
    *args,
    max_attempts: int = 3,
    delay: float = 1.0,
    operation_name: str = None,
    **kwargs,
) -> Any:
    """Retry with fixed delay strategy."""
    config = RetryConfig(
        max_attempts=max_attempts, backoff_strategy=FixedBackoff(delay)
    )
    policy = RetryPolicy(config)
    return await policy.execute(func, *args, operation_name=operation_name, **kwargs)
