"""
Resilience Patterns for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive error handling and resilience patterns for production reliability.
"""

from .circuit_breaker import CircuitBreaker, CircuitBreakerError
from .error_handlers import (
    DomainErrorHandler,
    ErrorHandler,
    GlobalErrorHandler,
    InfrastructureErrorHandler,
)
from .exceptions import (
    ACGSError,
    ConfigurationError,
    DomainError,
    InfrastructureError,
    PerformanceError,
    SecurityError,
    ValidationError,
)
from .retry import ExponentialBackoff, RetryError, RetryPolicy
from .timeout import TimeoutError, TimeoutManager

__all__ = [
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitBreakerError",
    # Retry
    "RetryPolicy",
    "ExponentialBackoff",
    "RetryError",
    # Timeout
    "TimeoutManager",
    "TimeoutError",
    # Exceptions
    "ACGSError",
    "DomainError",
    "InfrastructureError",
    "ValidationError",
    "ConfigurationError",
    "SecurityError",
    "PerformanceError",
    # Error Handlers
    "ErrorHandler",
    "DomainErrorHandler",
    "InfrastructureErrorHandler",
    "GlobalErrorHandler",
]
