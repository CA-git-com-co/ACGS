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
    # Exceptions
    "ACGSError",
    # Circuit Breaker
    "CircuitBreaker",
    "CircuitBreakerError",
    "ConfigurationError",
    "DomainError",
    "DomainErrorHandler",
    # Error Handlers
    "ErrorHandler",
    "ExponentialBackoff",
    "GlobalErrorHandler",
    "InfrastructureError",
    "InfrastructureErrorHandler",
    "PerformanceError",
    "RetryError",
    # Retry
    "RetryPolicy",
    "SecurityError",
    "TimeoutError",
    # Timeout
    "TimeoutManager",
    "ValidationError",
]
