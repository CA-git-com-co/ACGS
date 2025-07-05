"""
Error handling utilities for ACGS services.
"""

import logging
from typing import Any, Optional

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


def log_error(error: Exception, context: Optional[dict[str, Any]] = None) -> None:
    """Log error with optional context."""
    context_str = f" Context: {context}" if context else ""
    logger.error(f"Error: {error}{context_str}")
