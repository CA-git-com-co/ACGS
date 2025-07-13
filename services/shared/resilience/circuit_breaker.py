"""
Circuit Breaker Pattern Implementation
Constitutional Hash: cdd01ef066bc6cf2

Implements circuit breaker pattern for resilient external service calls.
"""

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .exceptions import InfrastructureError

logger = logging.getLogger(__name__)


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit breaker tripped
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring."""

    total_requests: int = 0
    failed_requests: int = 0
    success_requests: int = 0
    timeouts: int = 0
    circuit_opens: int = 0
    last_failure_time: float | None = None
    last_success_time: float | None = None

    @property
    def failure_rate(self) -> float:
        """Calculate current failure rate."""
        if self.total_requests == 0:
            return 0.0
        return self.failed_requests / self.total_requests

    @property
    def success_rate(self) -> float:
        """Calculate current success rate."""
        return 1.0 - self.failure_rate

    def reset(self) -> None:
        """Reset metrics for new window."""
        self.total_requests = 0
        self.failed_requests = 0
        self.success_requests = 0
        self.timeouts = 0


class CircuitBreakerError(InfrastructureError):
    """Raised when circuit breaker prevents operation execution."""

    def __init__(self, circuit_name: str, state: CircuitState, **kwargs):
        message = (
            f"Circuit breaker '{circuit_name}' is {state.value} - operation rejected"
        )
        super().__init__(message, **kwargs)
        self.circuit_name = circuit_name
        self.state = state
        self.details.update({"circuit_name": circuit_name, "state": state.value})


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5  # Failures before opening
    failure_rate_threshold: float = 0.5  # Failure rate threshold (0.0-1.0)
    recovery_timeout: float = 60.0  # Seconds before half-open attempt
    success_threshold: int = 3  # Successes to close from half-open
    timeout: float = 30.0  # Operation timeout in seconds
    minimum_requests: int = 10  # Minimum requests before rate calculation
    sliding_window_size: int = 100  # Size of metrics sliding window


class CircuitBreaker:
    """
    Circuit breaker implementation for resilient service calls.

    Monitors service health and prevents cascade failures by failing fast
    when service is unhealthy.
    """

    def __init__(self, name: str, config: CircuitBreakerConfig = None):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitState.CLOSED
        self._metrics = CircuitBreakerMetrics()
        self._last_state_change = time.time()
        self._consecutive_successes = 0
        self._lock = asyncio.Lock()

        logger.info(
            f"Circuit breaker '{name}' initialized in {self._state.value} state"
        )

    @property
    def state(self) -> CircuitState:
        """Get current circuit state."""
        return self._state

    @property
    def metrics(self) -> CircuitBreakerMetrics:
        """Get current metrics."""
        return self._metrics

    async def call(
        self, func: Callable, *args, fallback: Callable | None = None, **kwargs
    ) -> Any:
        """
        Execute function through circuit breaker.

        Args:
            func: Function to execute
            *args: Function arguments
            fallback: Optional fallback function
            **kwargs: Function keyword arguments

        Returns:
            Function result or fallback result

        Raises:
            CircuitBreakerError: When circuit is open
        """
        async with self._lock:
            await self._update_state()

            if self._state == CircuitState.OPEN:
                logger.warning(
                    f"Circuit breaker '{self.name}' is open - rejecting call"
                )
                if fallback:
                    return await self._execute_fallback(fallback, *args, **kwargs)
                raise CircuitBreakerError(self.name, self._state)

            # Allow call in CLOSED or HALF_OPEN state
            return await self._execute_call(func, *args, **kwargs)

    async def _execute_call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute the actual function call with monitoring."""
        time.time()

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                self._ensure_coroutine(func(*args, **kwargs)),
                timeout=self.config.timeout,
            )

            # Record success
            await self._record_success()
            return result

        except asyncio.TimeoutError:
            logger.exception(f"Circuit breaker '{self.name}' - call timed out")
            self._metrics.timeouts += 1
            await self._record_failure()
            raise

        except Exception as e:
            logger.exception(f"Circuit breaker '{self.name}' - call failed: {e}")
            await self._record_failure()
            raise

    async def _execute_fallback(self, fallback: Callable, *args, **kwargs) -> Any:
        """Execute fallback function."""
        try:
            logger.info(f"Circuit breaker '{self.name}' - executing fallback")
            return await self._ensure_coroutine(fallback(*args, **kwargs))
        except Exception as e:
            logger.exception(f"Circuit breaker '{self.name}' - fallback failed: {e}")
            raise

    async def _ensure_coroutine(self, result: Any) -> Any:
        """Ensure result is awaitable."""
        if asyncio.iscoroutine(result):
            return await result
        return result

    async def _record_success(self) -> None:
        """Record successful operation."""
        self._metrics.total_requests += 1
        self._metrics.success_requests += 1
        self._metrics.last_success_time = time.time()

        if self._state == CircuitState.HALF_OPEN:
            self._consecutive_successes += 1
            logger.debug(
                f"Circuit breaker '{self.name}' - consecutive successes: "
                f"{self._consecutive_successes}/{self.config.success_threshold}"
            )

            if self._consecutive_successes >= self.config.success_threshold:
                await self._close_circuit()

    async def _record_failure(self) -> None:
        """Record failed operation."""
        self._metrics.total_requests += 1
        self._metrics.failed_requests += 1
        self._metrics.last_failure_time = time.time()
        self._consecutive_successes = 0

        await self._evaluate_circuit_state()

    async def _evaluate_circuit_state(self) -> None:
        """Evaluate if circuit should be opened."""
        if self._state == CircuitState.OPEN:
            return

        # Check failure threshold
        if self._metrics.failed_requests >= self.config.failure_threshold:
            await self._open_circuit()
            return

        # Check failure rate (only if minimum requests met)
        if (
            self._metrics.total_requests >= self.config.minimum_requests
            and self._metrics.failure_rate >= self.config.failure_rate_threshold
        ):
            await self._open_circuit()

    async def _update_state(self) -> None:
        """Update circuit state based on time and conditions."""
        if self._state == CircuitState.OPEN:
            time_since_open = time.time() - self._last_state_change
            if time_since_open >= self.config.recovery_timeout:
                await self._half_open_circuit()

    async def _open_circuit(self) -> None:
        """Open the circuit breaker."""
        if self._state != CircuitState.OPEN:
            self._state = CircuitState.OPEN
            self._last_state_change = time.time()
            self._metrics.circuit_opens += 1
            self._consecutive_successes = 0

            logger.warning(
                f"Circuit breaker '{self.name}' opened - "
                f"failure rate: {self._metrics.failure_rate:.2f}, "
                f"failures: {self._metrics.failed_requests}"
            )

    async def _half_open_circuit(self) -> None:
        """Transition to half-open state."""
        self._state = CircuitState.HALF_OPEN
        self._last_state_change = time.time()
        self._consecutive_successes = 0

        logger.info(f"Circuit breaker '{self.name}' transitioned to half-open")

    async def _close_circuit(self) -> None:
        """Close the circuit breaker."""
        self._state = CircuitState.CLOSED
        self._last_state_change = time.time()
        self._metrics.reset()
        self._consecutive_successes = 0

        logger.info(f"Circuit breaker '{self.name}' closed - service recovered")

    async def force_open(self) -> None:
        """Manually open the circuit."""
        async with self._lock:
            await self._open_circuit()
            logger.warning(f"Circuit breaker '{self.name}' manually opened")

    async def force_close(self) -> None:
        """Manually close the circuit."""
        async with self._lock:
            await self._close_circuit()
            logger.info(f"Circuit breaker '{self.name}' manually closed")

    def get_status(self) -> dict[str, Any]:
        """Get detailed circuit breaker status."""
        return {
            "name": self.name,
            "state": self._state.value,
            "metrics": {
                "total_requests": self._metrics.total_requests,
                "failed_requests": self._metrics.failed_requests,
                "success_requests": self._metrics.success_requests,
                "timeouts": self._metrics.timeouts,
                "failure_rate": self._metrics.failure_rate,
                "success_rate": self._metrics.success_rate,
                "circuit_opens": self._metrics.circuit_opens,
            },
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "failure_rate_threshold": self.config.failure_rate_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "timeout": self.config.timeout,
            },
            "state_info": {
                "last_state_change": self._last_state_change,
                "consecutive_successes": self._consecutive_successes,
                "time_in_current_state": time.time() - self._last_state_change,
            },
            "constitutional_hash": "cdd01ef066bc6cf2",
        }


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""

    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}
        self._configs: dict[str, CircuitBreakerConfig] = {}

    def register(
        self, name: str, config: CircuitBreakerConfig = None
    ) -> CircuitBreaker:
        """Register a new circuit breaker."""
        if name in self._breakers:
            return self._breakers[name]

        breaker = CircuitBreaker(name, config)
        self._breakers[name] = breaker
        self._configs[name] = config or CircuitBreakerConfig()

        logger.info(f"Registered circuit breaker: {name}")
        return breaker

    def get(self, name: str) -> CircuitBreaker | None:
        """Get circuit breaker by name."""
        return self._breakers.get(name)

    def get_all_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all circuit breakers."""
        return {name: breaker.get_status() for name, breaker in self._breakers.items()}

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on all circuit breakers."""
        total_breakers = len(self._breakers)
        open_breakers = sum(
            1
            for breaker in self._breakers.values()
            if breaker.state == CircuitState.OPEN
        )
        half_open_breakers = sum(
            1
            for breaker in self._breakers.values()
            if breaker.state == CircuitState.HALF_OPEN
        )

        health_status = "healthy"
        if open_breakers > 0:
            health_status = (
                "degraded" if open_breakers < total_breakers else "unhealthy"
            )

        return {
            "status": health_status,
            "total_breakers": total_breakers,
            "open_breakers": open_breakers,
            "half_open_breakers": half_open_breakers,
            "closed_breakers": total_breakers - open_breakers - half_open_breakers,
            "breaker_details": self.get_all_status(),
        }


# Global registry instance
_circuit_breaker_registry = CircuitBreakerRegistry()


def get_circuit_breaker(
    name: str, config: CircuitBreakerConfig = None
) -> CircuitBreaker:
    """Get or create a circuit breaker."""
    return _circuit_breaker_registry.register(name, config)


def get_circuit_breaker_registry() -> CircuitBreakerRegistry:
    """Get the global circuit breaker registry."""
    return _circuit_breaker_registry
