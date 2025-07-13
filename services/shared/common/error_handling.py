"""
Error handling utilities for ACGS services.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ACGSException(Exception):
    """Base exception for ACGS services."""


class AuthenticationError(ACGSException):
    """Authentication-related errors."""


class ServiceUnavailableError(ACGSException):
    """Service unavailability errors."""


def handle_service_error(error: Exception, service_name: str = "unknown") -> None:
    """Handle service errors with logging."""
    logger.error(f"Service error in {service_name}: {error}")


def log_error(error: Exception, context: dict[str, Any] | None = None) -> None:
    """Log error with optional context."""
    context_str = f" Context: {context}" if context else ""
    logger.error(f"Error: {error}{context_str}")


def log_error_with_context(
    error: Exception,
    service_name: str = "unknown",
    operation: str = "unknown",
    context: dict[str, Any] | None = None,
    constitutional_hash: str = CONSTITUTIONAL_HASH,
) -> None:
    """
    Enhanced error logging with structured context for ACGS services.

    Args:
        error: The exception that occurred
        service_name: Name of the service where error occurred
        operation: Operation that was being performed
        context: Additional context information
        constitutional_hash: Constitutional hash for compliance validation
    """
    # Build structured context for logging
    error_context = {
        "service": service_name,
        "operation": operation,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "constitutional_hash": constitutional_hash,
    }

    # Add any additional context provided
    if context:
        error_context.update(context)

    # Log the error with structured context
    logger.error(
        f"ACGS Service Error in {service_name} during {operation}: {error}",
        extra={"context": error_context},
    )

    # Also log to error handler for service-specific handling
    handle_service_error(error, service_name)
