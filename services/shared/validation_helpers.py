"""
ACGS Shared Validation Helpers
Constitutional Hash: cdd01ef066bc6cf2

Provides validation decorators and utilities for all ACGS services.
"""

import functools
import logging
import traceback
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, Request, status
from pydantic import ValidationError

from .api_models import (
    ErrorCode,
    create_error_response,
    create_validation_error_response,
    ensure_constitutional_compliance,
)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


def handle_validation_errors(service_name: str):
    """
    Decorator to handle validation errors and return standardized responses.

    Args:
        service_name: Name of the service for error tracking
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                # Extract request object for correlation ID
                request = None
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break

                correlation_id = None
                if request and hasattr(request.state, "correlation_id"):
                    correlation_id = request.state.correlation_id

                # Execute the original function
                result = await func(*args, **kwargs)

                # Ensure constitutional compliance in response
                if isinstance(result, dict):
                    result = ensure_constitutional_compliance(result)

                return result

            except ValidationError as e:
                logger.warning(f"Validation error in {service_name}: {e}")

                # Convert Pydantic validation errors to our format
                validation_errors = []
                for error in e.errors():
                    field_path = " -> ".join(str(loc) for loc in error["loc"])
                    validation_errors.append(
                        {
                            "field": field_path,
                            "message": error["msg"],
                            "type": error["type"],
                        }
                    )

                response = create_validation_error_response(
                    validation_errors=validation_errors,
                    service_name=service_name,
                    correlation_id=correlation_id,
                )

                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=response
                )

            except HTTPException:
                # Re-raise HTTP exceptions as-is
                raise

            except Exception as e:
                logger.exception(f"Unexpected error in {service_name}: {e}")
                logger.exception(f"Traceback: {traceback.format_exc()}")

                response = create_error_response(
                    message="Internal server error",
                    error_code=ErrorCode.INTERNAL_ERROR,
                    error_details={"exception": str(e)},
                    service_name=service_name,
                    correlation_id=correlation_id,
                )

                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=response
                )

        return wrapper

    return decorator


def validate_constitutional_compliance(data: dict[str, Any]) -> bool:
    """
    Validate that data includes proper constitutional compliance.

    Args:
        data: Data to validate

    Returns:
        True if compliant, False otherwise
    """
    return data.get("constitutional_hash") == CONSTITUTIONAL_HASH


def validate_required_fields(
    data: dict[str, Any], required_fields: list[str]
) -> list[str]:
    """
    Validate that all required fields are present in data.

    Args:
        data: Data to validate
        required_fields: List of required field names

    Returns:
        List of missing field names
    """
    return [
        field for field in required_fields if field not in data or data[field] is None
    ]


def validate_field_types(
    data: dict[str, Any], field_types: dict[str, type]
) -> list[str]:
    """
    Validate that fields have the correct types.

    Args:
        data: Data to validate
        field_types: Dictionary mapping field names to expected types

    Returns:
        List of validation error messages
    """
    errors = []
    for field, expected_type in field_types.items():
        if field in data and data[field] is not None:
            if not isinstance(data[field], expected_type):
                errors.append(
                    f"Field '{field}' must be of type {expected_type.__name__}"
                )

    return errors


def sanitize_string_input(value: str, max_length: int | None = None) -> str:
    """
    Sanitize string input for security.

    Args:
        value: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        raise ValueError("Value must be a string")

    # Strip whitespace
    sanitized = value.strip()

    # Truncate if necessary
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", '"', "'", "&", "\x00"]
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")

    return sanitized


def validate_correlation_id(correlation_id: str | None) -> bool:
    """
    Validate correlation ID format.

    Args:
        correlation_id: Correlation ID to validate

    Returns:
        True if valid, False otherwise
    """
    if not correlation_id:
        return False

    # Should be a valid UUID-like string
    import re

    uuid_pattern = re.compile(
        r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE
    )

    return bool(uuid_pattern.match(correlation_id))


def create_correlation_id() -> str:
    """
    Create a new correlation ID.

    Returns:
        New correlation ID string
    """
    import uuid

    return str(uuid.uuid4())


def validate_service_response(response: dict[str, Any]) -> bool:
    """
    Validate that a service response has the expected structure.

    Args:
        response: Response to validate

    Returns:
        True if valid, False otherwise
    """
    required_fields = ["success", "message", "constitutional_hash"]

    for field in required_fields:
        if field not in response:
            return False

    # Validate constitutional compliance
    return response.get("constitutional_hash") == CONSTITUTIONAL_HASH


def log_validation_error(
    service_name: str,
    error_type: str,
    details: dict[str, Any],
    correlation_id: str | None = None,
) -> None:
    """
    Log validation errors with structured information.

    Args:
        service_name: Name of the service
        error_type: Type of validation error
        details: Error details
        correlation_id: Request correlation ID
    """
    log_data = {
        "service": service_name,
        "error_type": error_type,
        "details": details,
        "constitutional_hash": CONSTITUTIONAL_HASH,
    }

    if correlation_id:
        log_data["correlation_id"] = correlation_id

    logger.warning(f"Validation error: {log_data}")


def validate_pagination_params(
    page: int, size: int, max_size: int = 100
) -> dict[str, Any]:
    """
    Validate pagination parameters.

    Args:
        page: Page number (1-based)
        size: Page size
        max_size: Maximum allowed page size

    Returns:
        Dictionary with validated parameters or error details
    """
    errors = []

    if page < 1:
        errors.append("Page number must be >= 1")

    if size < 1:
        errors.append("Page size must be >= 1")

    if size > max_size:
        errors.append(f"Page size must be <= {max_size}")

    if errors:
        return {"valid": False, "errors": errors}

    return {"valid": True, "page": page, "size": size, "offset": (page - 1) * size}


class ValidationContext:
    """Context for validation operations."""

    def __init__(self, service_name: str, correlation_id: str | None = None):
        self.service_name = service_name
        self.correlation_id = correlation_id or create_correlation_id()
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def add_error(self, message: str) -> None:
        """Add a validation error."""
        self.errors.append(message)
        log_validation_error(
            self.service_name,
            "validation_error",
            {"message": message},
            self.correlation_id,
        )

    def add_warning(self, message: str) -> None:
        """Add a validation warning."""
        self.warnings.append(message)
        logger.warning(f"Validation warning in {self.service_name}: {message}")

    def is_valid(self) -> bool:
        """Check if validation passed."""
        return len(self.errors) == 0

    def get_error_response(self) -> dict[str, Any]:
        """Get standardized error response."""
        return create_validation_error_response(
            validation_errors=[
                {"field": "general", "message": error} for error in self.errors
            ],
            service_name=self.service_name,
            correlation_id=self.correlation_id,
        )
