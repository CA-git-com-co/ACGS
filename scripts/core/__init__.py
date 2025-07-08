"""
ACGS Scripts Core Library
Constitutional Hash: cdd01ef066bc6cf2

Core utilities and shared functionality for ACGS scripts.
"""

from .config import Config, get_config
from .logger import Logger, get_logger
from .http_client import HTTPClient
from .exceptions import ACGSError, ValidationError, ConfigurationError
from .utils import (
    ensure_constitutional_hash,
    validate_service_response,
    retry_async,
    format_duration,
    get_timestamp,
)

__all__ = [
    "Config",
    "get_config", 
    "Logger",
    "get_logger",
    "HTTPClient",
    "ACGSError",
    "ValidationError", 
    "ConfigurationError",
    "ensure_constitutional_hash",
    "validate_service_response",
    "retry_async",
    "format_duration",
    "get_timestamp",
]

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

__version__ = "1.0.0"