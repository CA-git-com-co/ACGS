"""
Circuit Breaker Implementation for ACGS-1 Service Resilience

Implements circuit breaker pattern for inter-service communication to prevent
cascade failures and improve system resilience with automatic recovery.
"""

import asyncio
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Circuit is open, calls fail fast
    HALF_OPEN = "half_open"  # Testing if service has recovered


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker configuration."""

    failure_threshold: int = 5  # Number of failures before opening
    recovery_timeout: int = 60  # Seconds before trying half-open
    success_threshold: int = 3  # Successes needed to close from half-open
    timeout: float = 10.0  # Request timeout in seconds
    expected_exceptions: tuple = (Exception,)  # Exceptions that count as failures


class CircuitBreakerError(Exception):
    """Raised when circuit breaker is open."""

    pass


class CircuitBreaker:
    """
    Circuit breaker for service resilience.

    Implements the circuit breaker pattern to prevent cascade failures
    and provide automatic recovery for inter-service communication.
    """

    def __init__(self, name: str, config: CircuitBreakerConfig | None = None):
        """
        Initialize circuit breaker.

        Args:
            name: Unique name for this circuit breaker
            config: Circuit breaker configuration
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()

        # State management
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: float | None = None
        self.last_success_time: float | None = None

        # Statistics
        self.total_requests = 0
        self.total_failures = 0
        self.total_successes = 0
        self.total_timeouts = 0

        logger.info(f"Circuit breaker '{name}' initialized with config: {self.config}")

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Function result

        Raises:
            CircuitBreakerError: When circuit is open
            Exception: Original function exceptions
        """
        self.total_requests += 1

        # Check if circuit should be opened or closed
        self._update_state()

        if self.state == CircuitState.OPEN:
            self._record_failure("Circuit breaker is OPEN")
            raise CircuitBreakerError(f"Circuit breaker '{self.name}' is OPEN")

        try:
            # Execute function with timeout
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(*args, **kwargs), timeout=self.config.timeout
                )
            else:
                result = func(*args, **kwargs)

            self._record_success()
            return result

        except TimeoutError as e:
            self.total_timeouts += 1
            self._record_failure(f"Timeout after {self.config.timeout}s")
            raise e

        except self.config.expected_exceptions as e:
            self._record_failure(str(e))
            raise e

    def _update_state(self):
        """Update circuit breaker state based on current conditions."""
        current_time = time.time()

        if self.state == CircuitState.OPEN:
            # Check if we should transition to half-open
            if (
                self.last_failure_time
                and current_time - self.last_failure_time > self.config.recovery_timeout
            ):
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                logger.info(f"Circuit breaker '{self.name}' transitioned to HALF_OPEN")

        elif self.state == CircuitState.HALF_OPEN:
            # Check if we should close the circuit
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
                logger.info(f"Circuit breaker '{self.name}' transitioned to CLOSED")

    def _record_success(self):
        """Record a successful operation."""
        self.total_successes += 1
        self.last_success_time = time.time()

        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            self.failure_count = 0

        logger.debug(f"Circuit breaker '{self.name}' recorded success")

    def _record_failure(self, error_msg: str):
        """Record a failed operation."""
        self.total_failures += 1
        self.failure_count += 1
        self.last_failure_time = time.time()

        # Reset success count on failure
        self.success_count = 0

        # Check if we should open the circuit
        if (
            self.state == CircuitState.CLOSED
            and self.failure_count >= self.config.failure_threshold
        ):
            self.state = CircuitState.OPEN
            logger.warning(
                f"Circuit breaker '{self.name}' OPENED after {self.failure_count} failures. "
                f"Last error: {error_msg}"
            )
        elif self.state == CircuitState.HALF_OPEN:
            # Go back to open on any failure in half-open state
            self.state = CircuitState.OPEN
            logger.warning(
                f"Circuit breaker '{self.name}' returned to OPEN from HALF_OPEN. "
                f"Error: {error_msg}"
            )

        logger.debug(f"Circuit breaker '{self.name}' recorded failure: {error_msg}")

    def get_state(self) -> dict[str, Any]:
        """
        Get current circuit breaker state and statistics.

        Returns:
            Circuit breaker state information
        """
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "total_requests": self.total_requests,
            "total_failures": self.total_failures,
            "total_successes": self.total_successes,
            "total_timeouts": self.total_timeouts,
            "failure_rate": (
                self.total_failures / self.total_requests
                if self.total_requests > 0
                else 0.0
            ),
            "last_failure_time": self.last_failure_time,
            "last_success_time": self.last_success_time,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "success_threshold": self.config.success_threshold,
                "timeout": self.config.timeout,
            },
        }

    def reset(self):
        """Reset circuit breaker to initial state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.last_success_time = None
        logger.info(f"Circuit breaker '{self.name}' reset to initial state")

    def force_open(self):
        """Force circuit breaker to open state."""
        self.state = CircuitState.OPEN
        self.last_failure_time = time.time()
        logger.warning(f"Circuit breaker '{self.name}' forced to OPEN state")

    def force_close(self):
        """Force circuit breaker to closed state."""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        logger.info(f"Circuit breaker '{self.name}' forced to CLOSED state")


class CircuitBreakerManager:
    """
    Manager for multiple circuit breakers.

    Provides centralized management and monitoring of circuit breakers
    across the ACGS-1 system.
    """

    def __init__(self):
        """Initialize circuit breaker manager."""
        self.circuit_breakers: dict[str, CircuitBreaker] = {}
        logger.info("Circuit breaker manager initialized")

    def get_circuit_breaker(
        self, name: str, config: CircuitBreakerConfig | None = None
    ) -> CircuitBreaker:
        """
        Get or create a circuit breaker.

        Args:
            name: Circuit breaker name
            config: Configuration for new circuit breakers

        Returns:
            Circuit breaker instance
        """
        if name not in self.circuit_breakers:
            self.circuit_breakers[name] = CircuitBreaker(name, config)
            logger.info(f"Created new circuit breaker: {name}")

        return self.circuit_breakers[name]

    def get_all_states(self) -> dict[str, dict[str, Any]]:
        """
        Get states of all circuit breakers.

        Returns:
            Dictionary of circuit breaker states
        """
        return {name: cb.get_state() for name, cb in self.circuit_breakers.items()}

    def reset_all(self):
        """Reset all circuit breakers."""
        for cb in self.circuit_breakers.values():
            cb.reset()
        logger.info("All circuit breakers reset")

    def get_health_summary(self) -> dict[str, Any]:
        """
        Get health summary of all circuit breakers.

        Returns:
            Health summary with overall status
        """
        total_breakers = len(self.circuit_breakers)
        open_breakers = sum(
            1 for cb in self.circuit_breakers.values() if cb.state == CircuitState.OPEN
        )
        half_open_breakers = sum(
            1
            for cb in self.circuit_breakers.values()
            if cb.state == CircuitState.HALF_OPEN
        )

        overall_health = "healthy"
        if open_breakers > 0:
            overall_health = (
                "degraded" if open_breakers < total_breakers else "critical"
            )
        elif half_open_breakers > 0:
            overall_health = "recovering"

        return {
            "overall_health": overall_health,
            "total_circuit_breakers": total_breakers,
            "open_breakers": open_breakers,
            "half_open_breakers": half_open_breakers,
            "closed_breakers": total_breakers - open_breakers - half_open_breakers,
            "circuit_breakers": list(self.circuit_breakers.keys()),
        }


# Global circuit breaker manager
_circuit_breaker_manager = CircuitBreakerManager()


def get_circuit_breaker(
    name: str, config: CircuitBreakerConfig | None = None
) -> CircuitBreaker:
    """
    Get circuit breaker from global manager.

    Args:
        name: Circuit breaker name
        config: Configuration for new circuit breakers

    Returns:
        Circuit breaker instance
    """
    return _circuit_breaker_manager.get_circuit_breaker(name, config)


def get_circuit_breaker_manager() -> CircuitBreakerManager:
    """Get global circuit breaker manager."""
    return _circuit_breaker_manager
