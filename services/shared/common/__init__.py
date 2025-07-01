"""
Consolidated common utilities for ACGS-PGP services.

This module provides shared utilities that eliminate code duplication
across the ACGS microservices architecture.
"""

from .error_handling import ACGSException, handle_service_error, log_error
from .formatting import format_error, format_response, standardize_timestamps

# Temporarily commented out due to httpx import issues
# from .http_clients import ACGSHttpClient, ServiceClient
from .validation import ValidationError, validate_request, validate_response

__all__ = [
    "ACGSException",
    "ACGSHttpClient",
    "ServiceClient",
    "ValidationError",
    "format_error",
    "format_response",
    "handle_service_error",
    "log_error",
    "standardize_timestamps",
    "validate_request",
    "validate_response",
]
