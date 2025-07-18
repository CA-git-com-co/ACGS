"""
Circuit Breaker Pattern Implementation for ACGS-2
Constitutional Hash: cdd01ef066bc6cf2

This module provides fault tolerance and performance optimization
through circuit breaker patterns for service communication.
"""

import asyncio
import logging
import time
from enum import Enum
from typing import Any, Callable, Optional, Dict
from dataclasses import dataclass
from functools import wraps
import threading

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing recovery


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""

    failure_threshold: int = 5
    recovery_timeout: int = 60
    success_threshold: int = 3
    timeout: float = 30.0
    constitutional_hash: str = "cdd01ef066bc6cf2"


class CircuitBreakerError(Exception):
    """Exception raised when circuit breaker is open."""

    pass


class CircuitBreaker:
    """
    Circuit breaker implementation for fault tolerance.

    Features:
    - Constitutional compliance validation
    - Automatic failure detection
    - Configurable recovery timeouts
    - Metrics collection
    - Thread-safe operation
    """

    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = 0
        self.lock = threading.Lock()

        # Metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "circuit_opens": 0,
            "circuit_closes": 0,
            "constitutional_violations": 0,
        }

        logger.info(f"Circuit breaker initialized with config: {config}")

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Args:
            func: Function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Any: Function result

        Raises:
            CircuitBreakerError: If circuit is open
        """
        with self.lock:
            self.metrics["total_requests"] += 1

            # Check constitutional compliance
            if not self._validate_constitutional_compliance(kwargs):
                self.metrics["constitutional_violations"] += 1
                raise CircuitBreakerError("Constitutional compliance violation")

            # Check circuit state
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker transitioning to HALF_OPEN")
                else:
                    raise CircuitBreakerError("Circuit breaker is OPEN")

            try:
                # Execute function with timeout
                result = self._execute_with_timeout(func, *args, **kwargs)
                self._on_success()
                return result

            except Exception as e:
                self._on_failure(e)
                raise

    async def acall(self, func: Callable, *args, **kwargs) -> Any:
        """
        Async version of call method.

        Args:
            func: Async function to execute
            *args: Function arguments
            **kwargs: Function keyword arguments

        Returns:
            Any: Function result
        """
        with self.lock:
            self.metrics["total_requests"] += 1

            # Check constitutional compliance
            if not self._validate_constitutional_compliance(kwargs):
                self.metrics["constitutional_violations"] += 1
                raise CircuitBreakerError("Constitutional compliance violation")

            # Check circuit state
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self.state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker transitioning to HALF_OPEN")
                else:
                    raise CircuitBreakerError("Circuit breaker is OPEN")

        try:
            # Execute async function with timeout
            result = await asyncio.wait_for(
                func(*args, **kwargs), timeout=self.config.timeout
            )
            self._on_success()
            return result

        except Exception as e:
            self._on_failure(e)
            raise

    def _execute_with_timeout(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with timeout protection."""
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError("Function execution timed out")

        # Set up timeout
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(int(self.config.timeout))

        try:
            result = func(*args, **kwargs)
            signal.alarm(0)  # Cancel timeout
            return result
        except:
            signal.alarm(0)  # Cancel timeout
            raise

    def _validate_constitutional_compliance(self, kwargs: Dict[str, Any]) -> bool:
        """Validate constitutional compliance in request."""
        constitutional_hash = kwargs.get("constitutional_hash")
        if not constitutional_hash:
            return False
        return constitutional_hash == self.config.constitutional_hash

    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt reset."""
        return (time.time() - self.last_failure_time) >= self.config.recovery_timeout

    def _on_success(self):
        """Handle successful execution."""
        with self.lock:
            self.metrics["successful_requests"] += 1

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self.state = CircuitState.CLOSED
                    self.failure_count = 0
                    self.success_count = 0
                    self.metrics["circuit_closes"] += 1
                    logger.info("Circuit breaker CLOSED - service recovered")

    def _on_failure(self, exception: Exception):
        """Handle failed execution."""
        with self.lock:
            self.metrics["failed_requests"] += 1
            self.failure_count += 1
            self.last_failure_time = time.time()

            logger.warning(f"Circuit breaker failure: {exception}")

            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.OPEN
                self.success_count = 0
                logger.warning("Circuit breaker OPEN - service still failing")

            elif self.failure_count >= self.config.failure_threshold:
                self.state = CircuitState.OPEN
                self.metrics["circuit_opens"] += 1
                logger.error("Circuit breaker OPEN - failure threshold exceeded")

    def get_metrics(self) -> Dict[str, Any]:
        """Get circuit breaker metrics."""
        with self.lock:
            return {
                **self.metrics,
                "state": self.state.value,
                "failure_count": self.failure_count,
                "success_count": self.success_count,
                "constitutional_hash": self.config.constitutional_hash,
            }

    def reset(self):
        """Manually reset circuit breaker."""
        with self.lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            logger.info("Circuit breaker manually reset")


# Global circuit breakers for services
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(
    service_name: str, config: Optional[CircuitBreakerConfig] = None
) -> CircuitBreaker:
    """Get or create circuit breaker for service."""
    global _circuit_breakers

    if service_name not in _circuit_breakers:
        if config is None:
            config = CircuitBreakerConfig()
        _circuit_breakers[service_name] = CircuitBreaker(config)

    return _circuit_breakers[service_name]


def circuit_breaker(service_name: str, config: Optional[CircuitBreakerConfig] = None):
    """
    Decorator for circuit breaker protection.

    Args:
        service_name: Name of the service
        config: Circuit breaker configuration
    """

    def decorator(func):
        breaker = get_circuit_breaker(service_name, config)

        @wraps(func)
        def wrapper(*args, **kwargs):
            return breaker.call(func, *args, **kwargs)

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await breaker.acall(func, *args, **kwargs)

        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper

    return decorator


# Service-specific circuit breakers
constitutional_ai_breaker = get_circuit_breaker("constitutional-ai")
governance_synthesis_breaker = get_circuit_breaker("governance-synthesis")
formal_verification_breaker = get_circuit_breaker("formal-verification")
policy_governance_breaker = get_circuit_breaker("policy-governance")


# Convenience decorators
def constitutional_ai_circuit_breaker(func):
    """Circuit breaker for Constitutional AI service."""
    return circuit_breaker("constitutional-ai")(func)


def governance_synthesis_circuit_breaker(func):
    """Circuit breaker for Governance Synthesis service."""
    return circuit_breaker("governance-synthesis")(func)


def formal_verification_circuit_breaker(func):
    """Circuit breaker for Formal Verification service."""
    return circuit_breaker("formal-verification")(func)


def policy_governance_circuit_breaker(func):
    """Circuit breaker for Policy Governance service."""
    return circuit_breaker("policy-governance")(func)
