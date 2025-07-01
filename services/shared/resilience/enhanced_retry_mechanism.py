"""
Enhanced Retry Mechanism for ACGS
Implements advanced retry patterns with exponential backoff, jitter, and constitutional compliance integration.
"""

import asyncio
import logging
import random
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from prometheus_client import Counter, Histogram

logger = logging.getLogger(__name__)


class RetryStrategy(Enum):
    """Retry strategy types."""

    EXPONENTIAL_BACKOFF = "exponential_backoff"
    LINEAR_BACKOFF = "linear_backoff"
    FIXED_DELAY = "fixed_delay"
    FIBONACCI_BACKOFF = "fibonacci_backoff"


@dataclass
class RetryConfig:
    """Configuration for retry mechanism."""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    jitter: bool = True
    jitter_factor: float = 0.1

    # Exception handling
    retryable_exceptions: tuple = (Exception,)
    non_retryable_exceptions: tuple = ()

    # Constitutional compliance
    constitutional_compliance_threshold: float = 0.95
    retry_on_compliance_failure: bool = True

    # Circuit breaker integration
    circuit_breaker_name: str | None = None

    # Timeout configuration
    timeout_per_attempt: float | None = None
    total_timeout: float | None = None


@dataclass
class RetryAttempt:
    """Information about a retry attempt."""

    attempt_number: int
    delay: float
    exception: Exception | None = None
    constitutional_compliance_score: float | None = None
    timestamp: float = field(default_factory=time.time)
    duration: float = 0.0


class EnhancedRetryMechanism:
    """Enhanced retry mechanism with constitutional compliance integration."""

    def __init__(self, name: str, config: RetryConfig):
        self.name = name
        self.config = config
        self.setup_metrics()

        # Fibonacci sequence for fibonacci backoff
        self.fibonacci_sequence = [1, 1]

        logger.info(f"Enhanced retry mechanism '{name}' initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics."""
        self.retry_attempts_total = Counter(
            "retry_attempts_total",
            "Total retry attempts",
            ["name", "attempt_number", "result"],
        )

        self.retry_duration = Histogram(
            "retry_duration_seconds", "Duration of retry operations", ["name", "result"]
        )

        self.constitutional_compliance_retries = Counter(
            "constitutional_compliance_retries_total",
            "Retries due to constitutional compliance failures",
            ["name"],
        )

    async def execute_with_retry(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        start_time = time.time()
        attempts: list[RetryAttempt] = []
        last_exception = None

        for attempt_number in range(1, self.config.max_attempts + 1):
            attempt_start = time.time()

            try:
                # Check total timeout
                if (
                    self.config.total_timeout
                    and time.time() - start_time >= self.config.total_timeout
                ):
                    raise TimeoutError(
                        f"Total timeout {self.config.total_timeout}s exceeded"
                    )

                # Execute function with per-attempt timeout
                if self.config.timeout_per_attempt:
                    result = await asyncio.wait_for(
                        self._execute_function(func, *args, **kwargs),
                        timeout=self.config.timeout_per_attempt,
                    )
                else:
                    result = await self._execute_function(func, *args, **kwargs)

                attempt_duration = time.time() - attempt_start

                # Check constitutional compliance
                compliance_score = self._extract_compliance_score(result)

                if (
                    compliance_score is not None
                    and compliance_score
                    < self.config.constitutional_compliance_threshold
                    and self.config.retry_on_compliance_failure
                    and attempt_number < self.config.max_attempts
                ):
                    # Record compliance retry
                    self.constitutional_compliance_retries.labels(name=self.name).inc()

                    attempt = RetryAttempt(
                        attempt_number=attempt_number,
                        delay=0,
                        constitutional_compliance_score=compliance_score,
                        duration=attempt_duration,
                    )
                    attempts.append(attempt)

                    logger.warning(
                        f"Constitutional compliance failure (score: {compliance_score:.2%}) "
                        f"on attempt {attempt_number}, retrying..."
                    )

                    # Calculate delay and wait
                    delay = self._calculate_delay(attempt_number)
                    await asyncio.sleep(delay)
                    continue

                # Success - record metrics and return
                total_duration = time.time() - start_time

                self.retry_attempts_total.labels(
                    name=self.name, attempt_number=attempt_number, result="success"
                ).inc()

                self.retry_duration.labels(name=self.name, result="success").observe(
                    total_duration
                )

                if attempt_number > 1:
                    logger.info(
                        f"Retry successful on attempt {attempt_number} "
                        f"after {total_duration:.2f}s"
                    )

                return result

            except Exception as e:
                attempt_duration = time.time() - attempt_start
                last_exception = e

                # Check if exception is retryable
                if not self._is_retryable_exception(e):
                    logger.error(f"Non-retryable exception: {e}")
                    break

                attempt = RetryAttempt(
                    attempt_number=attempt_number,
                    delay=0,
                    exception=e,
                    duration=attempt_duration,
                )
                attempts.append(attempt)

                # Record attempt metrics
                self.retry_attempts_total.labels(
                    name=self.name, attempt_number=attempt_number, result="failure"
                ).inc()

                # If this is the last attempt, don't wait
                if attempt_number >= self.config.max_attempts:
                    break

                # Calculate delay and wait
                delay = self._calculate_delay(attempt_number)
                attempt.delay = delay

                logger.warning(
                    f"Attempt {attempt_number} failed: {e}. Retrying in {delay:.2f}s..."
                )

                await asyncio.sleep(delay)

        # All attempts failed
        total_duration = time.time() - start_time

        self.retry_duration.labels(name=self.name, result="failure").observe(
            total_duration
        )

        logger.error(
            f"All {self.config.max_attempts} retry attempts failed "
            f"after {total_duration:.2f}s"
        )

        # Raise the last exception
        if last_exception:
            raise last_exception
        raise RuntimeError("All retry attempts failed")

    async def _execute_function(self, func: Callable, *args, **kwargs) -> Any:
        """Execute the function, handling both sync and async functions."""
        if asyncio.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        return func(*args, **kwargs)

    def _extract_compliance_score(self, result: Any) -> float | None:
        """Extract constitutional compliance score from result."""
        if hasattr(result, "constitutional_compliance_score"):
            return result.constitutional_compliance_score
        if isinstance(result, dict) and "constitutional_compliance_score" in result:
            return result["constitutional_compliance_score"]
        return None

    def _is_retryable_exception(self, exception: Exception) -> bool:
        """Check if an exception is retryable."""
        # Check non-retryable exceptions first
        if isinstance(exception, self.config.non_retryable_exceptions):
            return False

        # Check retryable exceptions
        return isinstance(exception, self.config.retryable_exceptions)

    def _calculate_delay(self, attempt_number: int) -> float:
        """Calculate delay for the given attempt number."""
        if self.config.strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            delay = self.config.base_delay * (2 ** (attempt_number - 1))
        elif self.config.strategy == RetryStrategy.LINEAR_BACKOFF:
            delay = self.config.base_delay * attempt_number
        elif self.config.strategy == RetryStrategy.FIXED_DELAY:
            delay = self.config.base_delay
        elif self.config.strategy == RetryStrategy.FIBONACCI_BACKOFF:
            delay = self.config.base_delay * self._get_fibonacci_number(attempt_number)
        else:
            delay = self.config.base_delay

        # Apply maximum delay limit
        delay = min(delay, self.config.max_delay)

        # Apply jitter if enabled
        if self.config.jitter:
            jitter_amount = delay * self.config.jitter_factor
            delay += random.uniform(-jitter_amount, jitter_amount)
            delay = max(0, delay)  # Ensure delay is not negative

        return delay

    def _get_fibonacci_number(self, n: int) -> int:
        """Get the nth Fibonacci number."""
        while len(self.fibonacci_sequence) < n:
            next_fib = self.fibonacci_sequence[-1] + self.fibonacci_sequence[-2]
            self.fibonacci_sequence.append(next_fib)

        return self.fibonacci_sequence[n - 1]

    def get_stats(self) -> dict[str, Any]:
        """Get retry mechanism statistics."""
        return {
            "name": self.name,
            "config": {
                "max_attempts": self.config.max_attempts,
                "base_delay": self.config.base_delay,
                "max_delay": self.config.max_delay,
                "strategy": self.config.strategy.value,
                "jitter": self.config.jitter,
                "constitutional_compliance_threshold": self.config.constitutional_compliance_threshold,
            },
        }


class RetryManager:
    """Manages multiple retry mechanisms."""

    def __init__(self):
        self.retry_mechanisms: dict[str, EnhancedRetryMechanism] = {}

    def get_retry_mechanism(
        self, name: str, config: RetryConfig | None = None
    ) -> EnhancedRetryMechanism:
        """Get or create retry mechanism."""
        if name not in self.retry_mechanisms:
            if config is None:
                config = RetryConfig()
            self.retry_mechanisms[name] = EnhancedRetryMechanism(name, config)

        return self.retry_mechanisms[name]

    def get_all_stats(self) -> dict[str, dict[str, Any]]:
        """Get statistics for all retry mechanisms."""
        return {name: rm.get_stats() for name, rm in self.retry_mechanisms.items()}


# Decorator for easy retry functionality
def retry_with_config(config: RetryConfig, name: str | None = None):
    """Decorator to add retry functionality to a function."""

    def decorator(func: Callable):
        retry_name = name or f"{func.__module__}.{func.__name__}"
        retry_mechanism = EnhancedRetryMechanism(retry_name, config)

        async def async_wrapper(*args, **kwargs):
            return await retry_mechanism.execute_with_retry(func, *args, **kwargs)

        def sync_wrapper(*args, **kwargs):
            return asyncio.run(
                retry_mechanism.execute_with_retry(func, *args, **kwargs)
            )

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


# Predefined retry configurations for common scenarios
ACGS_RETRY_CONFIGS = {
    "database_operations": RetryConfig(
        max_attempts=3,
        base_delay=1.0,
        max_delay=10.0,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        retryable_exceptions=(ConnectionError, TimeoutError),
        timeout_per_attempt=30.0,
    ),
    "api_calls": RetryConfig(
        max_attempts=5,
        base_delay=0.5,
        max_delay=30.0,
        strategy=RetryStrategy.EXPONENTIAL_BACKOFF,
        jitter=True,
        timeout_per_attempt=10.0,
        total_timeout=60.0,
    ),
    "constitutional_validation": RetryConfig(
        max_attempts=3,
        base_delay=2.0,
        max_delay=15.0,
        strategy=RetryStrategy.LINEAR_BACKOFF,
        constitutional_compliance_threshold=0.95,
        retry_on_compliance_failure=True,
        timeout_per_attempt=20.0,
    ),
    "critical_operations": RetryConfig(
        max_attempts=5,
        base_delay=1.0,
        max_delay=60.0,
        strategy=RetryStrategy.FIBONACCI_BACKOFF,
        jitter=True,
        timeout_per_attempt=45.0,
        total_timeout=300.0,
    ),
}

# Global retry manager
retry_manager = RetryManager()
