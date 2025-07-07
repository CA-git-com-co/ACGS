"""
Timeout Management Module for ACGS Services
Constitutional hash: cdd01ef066bc6cf2

Provides timeout handling and management for constitutional compliance operations.
"""

import asyncio
import signal
import threading
import time
from contextlib import contextmanager
from typing import Any, Callable, Optional, TypeVar

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

T = TypeVar("T")


class TimeoutError(Exception):
    """Constitutional timeout error with compliance context."""

    def __init__(self, message: str, constitutional_hash: str = CONSTITUTIONAL_HASH):
        self.constitutional_hash = constitutional_hash
        super().__init__(f"{message} (Constitutional: {constitutional_hash})")


class TimeoutManager:
    """
    Constitutional timeout manager for ACGS operations.

    Provides timeout functionality with constitutional compliance tracking.
    """

    def __init__(self, default_timeout: float = 30.0):
        self.default_timeout = default_timeout
        self.constitutional_hash = CONSTITUTIONAL_HASH

    @contextmanager
    def timeout(self, seconds: Optional[float] = None):
        """
        Context manager for timeout operations with constitutional compliance.

        Args:
            seconds: Timeout in seconds (uses default if None)

        Raises:
            TimeoutError: If operation times out
        """
        timeout_duration = seconds or self.default_timeout

        def timeout_handler(signum, frame):
            raise TimeoutError(
                f"Operation timed out after {timeout_duration}s",
                self.constitutional_hash,
            )

        # Set the signal handler
        old_handler = signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(timeout_duration))

        try:
            yield
        finally:
            # Restore the old signal handler
            signal.alarm(0)
            signal.signal(signal.SIGALRM, old_handler)

    async def async_timeout(self, coro, seconds: Optional[float] = None):
        """
        Async timeout wrapper with constitutional compliance.

        Args:
            coro: Coroutine to execute
            seconds: Timeout in seconds

        Returns:
            Result of the coroutine

        Raises:
            TimeoutError: If operation times out
        """
        timeout_duration = seconds or self.default_timeout

        try:
            return await asyncio.wait_for(coro, timeout=timeout_duration)
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"Async operation timed out after {timeout_duration}s",
                self.constitutional_hash,
            )

    def threaded_timeout(
        self, func: Callable[[], T], seconds: Optional[float] = None
    ) -> T:
        """
        Execute function with timeout in separate thread.

        Args:
            func: Function to execute
            seconds: Timeout in seconds

        Returns:
            Result of the function

        Raises:
            TimeoutError: If operation times out
        """
        timeout_duration = seconds or self.default_timeout
        result = [None]
        exception = [None]

        def target():
            try:
                result[0] = func()
            except Exception as e:
                exception[0] = e

        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout_duration)

        if thread.is_alive():
            # Note: We can't actually kill the thread in Python
            raise TimeoutError(
                f"Threaded operation timed out after {timeout_duration}s",
                self.constitutional_hash,
            )

        if exception[0]:
            raise exception[0]

        return result[0]


class ConstitutionalTimeoutMixin:
    """
    Mixin class for adding constitutional timeout functionality to services.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timeout_manager = TimeoutManager()
        self.constitutional_hash = CONSTITUTIONAL_HASH

    async def with_constitutional_timeout(self, coro, timeout: Optional[float] = None):
        """Execute coroutine with constitutional timeout."""
        return await self.timeout_manager.async_timeout(coro, timeout)

    @contextmanager
    def constitutional_timeout(self, timeout: Optional[float] = None):
        """Context manager for constitutional timeout."""
        with self.timeout_manager.timeout(timeout):
            yield


# Global timeout manager instance
default_timeout_manager = TimeoutManager()


def with_timeout(seconds: float):
    """
    Decorator for adding timeout to functions with constitutional compliance.

    Args:
        seconds: Timeout duration in seconds
    """

    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            return default_timeout_manager.threaded_timeout(
                lambda: func(*args, **kwargs), seconds
            )

        return wrapper

    return decorator


async def async_with_timeout(coro, seconds: float):
    """
    Async function wrapper with constitutional timeout.

    Args:
        coro: Coroutine to execute
        seconds: Timeout duration

    Returns:
        Result of coroutine
    """
    return await default_timeout_manager.async_timeout(coro, seconds)


# Performance testing utilities
class PerformanceTimeoutManager(TimeoutManager):
    """
    Specialized timeout manager for performance testing with constitutional compliance.
    """

    def __init__(
        self, default_timeout: float = 5.0
    ):  # Shorter default for performance tests
        super().__init__(default_timeout)
        self.performance_thresholds = {
            "constitutional_validation": 0.005,  # 5ms P99 target
            "cache_operations": 0.001,  # 1ms for cache
            "database_queries": 0.010,  # 10ms for DB
        }

    def get_performance_timeout(self, operation_type: str) -> float:
        """Get performance timeout for specific operation type."""
        return self.performance_thresholds.get(operation_type, self.default_timeout)

    async def measure_performance(self, coro, operation_type: str = "default"):
        """
        Measure performance of operation with constitutional compliance.

        Returns:
            Tuple of (result, execution_time)
        """
        start_time = time.perf_counter()
        timeout_duration = self.get_performance_timeout(operation_type)

        try:
            result = await self.async_timeout(coro, timeout_duration)
            execution_time = time.perf_counter() - start_time
            return result, execution_time
        except TimeoutError as e:
            execution_time = time.perf_counter() - start_time
            raise TimeoutError(
                f"Performance test failed: {operation_type} took >{timeout_duration}s "
                f"(actual: {execution_time:.3f}s) - Constitutional: {self.constitutional_hash}"
            )


# Export for backward compatibility
__all__ = [
    "TimeoutError",
    "TimeoutManager",
    "ConstitutionalTimeoutMixin",
    "PerformanceTimeoutManager",
    "with_timeout",
    "async_with_timeout",
    "default_timeout_manager",
    "CONSTITUTIONAL_HASH",
]
