"""
ACGS-1 Phase A3: Validation Helpers and Utilities

This module provides helper functions and utilities for integrating
production-grade Pydantic validation models with FastAPI endpoints
across all ACGS-1 services.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, ValidationError

from .api_models import APIResponse, ErrorCode, create_error_response

logger = logging.getLogger(__name__)


class ValidationHelper:
    """Helper class for handling validation across ACGS-1 services."""

    @staticmethod
    def create_validation_error_response(
        exc: ValidationError | RequestValidationError,
        service_name: str,
        correlation_id: str | None = None,
    ) -> APIResponse:
        """
        Create standardized validation error response from Pydantic validation errors.

        Args:
            exc: Validation exception from Pydantic
            service_name: Name of the service for error response
            correlation_id: Request correlation ID

        Returns:
            Standardized API error response
        """
        errors = []

        if isinstance(exc, RequestValidationError):
            # FastAPI validation error
            for error in exc.errors():
                field_path = " -> ".join(str(loc) for loc in error["loc"])
                errors.append(
                    {
                        "field": field_path,
                        "message": error["msg"],
                        "type": error["type"],
                        "input": error.get("input"),
                    }
                )
        elif isinstance(exc, ValidationError):
            # Direct Pydantic validation error
            for error in exc.errors():
                field_path = " -> ".join(str(loc) for loc in error["loc"])
                errors.append(
                    {
                        "field": field_path,
                        "message": error["msg"],
                        "type": error["type"],
                        "input": error.get("input"),
                    }
                )

        return create_error_response(
            error_code=ErrorCode.VALIDATION_ERROR,
            message="Input validation failed",
            service_name=service_name,
            details={"validation_errors": errors, "error_count": len(errors)},
            correlation_id=correlation_id,
        )

    @staticmethod
    def validate_model_data(
        model_class: type[BaseModel],
        data: dict[str, Any],
        service_name: str,
        correlation_id: str | None = None,
    ) -> BaseModel | APIResponse:
        """
        Validate data against a Pydantic model and return either the validated model
        or an error response.

        Args:
            model_class: Pydantic model class to validate against
            data: Data to validate
            service_name: Name of the service for error response
            correlation_id: Request correlation ID

        Returns:
            Either validated model instance or error response
        """
        try:
            return model_class(**data)
        except ValidationError as e:
            logger.warning(
                f"Validation error in {service_name}: {e}",
                extra={"correlation_id": correlation_id},
            )
            return ValidationHelper.create_validation_error_response(
                e, service_name, correlation_id
            )

    @staticmethod
    def validate_query_params(
        params: dict[str, Any],
        allowed_params: dict[str, type],
        service_name: str,
        correlation_id: str | None = None,
    ) -> dict[str, Any] | APIResponse:
        """
        Validate query parameters against allowed types.

        Args:
            params: Query parameters to validate
            allowed_params: Dictionary of allowed parameter names and their types
            service_name: Name of the service for error response
            correlation_id: Request correlation ID

        Returns:
            Either validated parameters or error response
        """
        validated_params = {}
        errors = []

        for param_name, param_value in params.items():
            if param_name not in allowed_params:
                errors.append(
                    {
                        "field": param_name,
                        "message": f"Unknown query parameter: {param_name}",
                        "type": "unknown_parameter",
                        "input": param_value,
                    }
                )
                continue

            expected_type = allowed_params[param_name]

            try:
                # Type conversion based on expected type
                if expected_type == int:
                    validated_params[param_name] = int(param_value)
                elif expected_type == float:
                    validated_params[param_name] = float(param_value)
                elif expected_type == bool:
                    validated_params[param_name] = param_value.lower() in (
                        "true",
                        "1",
                        "yes",
                        "on",
                    )
                elif expected_type == str:
                    validated_params[param_name] = str(param_value)
                else:
                    validated_params[param_name] = param_value

            except (ValueError, TypeError):
                errors.append(
                    {
                        "field": param_name,
                        "message": f"Invalid type for parameter {param_name}: expected {expected_type.__name__}",
                        "type": "type_error",
                        "input": param_value,
                    }
                )

        if errors:
            return create_error_response(
                error_code=ErrorCode.VALIDATION_ERROR,
                message="Query parameter validation failed",
                service_name=service_name,
                details={"validation_errors": errors, "error_count": len(errors)},
                correlation_id=correlation_id,
            )

        return validated_params

    @staticmethod
    def validate_pagination_params(
        page: int | None = None, size: int | None = None, max_size: int = 100
    ) -> dict[str, int]:
        """
        Validate and normalize pagination parameters.

        Args:
            page: Page number (1-based)
            size: Items per page
            max_size: Maximum allowed page size

        Returns:
            Validated pagination parameters

        Raises:
            HTTPException: If parameters are invalid
        """
        # Default values
        validated_page = page if page is not None else 1
        validated_size = size if size is not None else 20

        # Validation
        if validated_page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page number must be >= 1",
            )

        if validated_size < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Page size must be >= 1"
            )

        if validated_size > max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Page size must be <= {max_size}",
            )

        return {
            "page": validated_page,
            "size": validated_size,
            "offset": (validated_page - 1) * validated_size,
        }

    @staticmethod
    def validate_date_range(
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        max_range_days: int = 365,
    ) -> dict[str, datetime | None]:
        """
        Validate date range parameters.

        Args:
            start_date: Start date
            end_date: End date
            max_range_days: Maximum allowed range in days

        Returns:
            Validated date range

        Raises:
            HTTPException: If date range is invalid
        """
        if start_date and end_date:
            if end_date <= start_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="End date must be after start date",
                )

            # Check range limit
            range_days = (end_date - start_date).days
            if range_days > max_range_days:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Date range cannot exceed {max_range_days} days",
                )

        return {"start_date": start_date, "end_date": end_date}

    @staticmethod
    def sanitize_input(
        text: str,
        max_length: int | None = None,
        allow_html: bool = False,
        strip_whitespace: bool = True,
    ) -> str:
        """
        Sanitize text input for security and consistency.

        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length
            allow_html: Whether to allow HTML tags
            strip_whitespace: Whether to strip leading/trailing whitespace

        Returns:
            Sanitized text

        Raises:
            HTTPException: If input is invalid
        """
        if strip_whitespace:
            text = text.strip()

        if max_length and len(text) > max_length:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Input text exceeds maximum length of {max_length} characters",
            )

        if not allow_html:
            # Basic HTML tag removal (for production, use a proper HTML sanitizer)
            import re

            text = re.sub(r"<[^>]+>", "", text)

        # Remove null bytes and other control characters
        text = "".join(char for char in text if ord(char) >= 32 or char in "\t\n\r")

        return text

    @staticmethod
    def validate_file_upload(
        file_content: bytes, allowed_types: list[str], max_size_mb: int = 10
    ) -> bool:
        """
        Validate file upload content.

        Args:
            file_content: File content as bytes
            allowed_types: List of allowed MIME types
            max_size_mb: Maximum file size in MB

        Returns:
            True if valid

        Raises:
            HTTPException: If file is invalid
        """
        # Check file size
        file_size_mb = len(file_content) / (1024 * 1024)
        if file_size_mb > max_size_mb:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size ({file_size_mb:.2f}MB) exceeds maximum allowed size ({max_size_mb}MB)",
            )

        # Basic file type detection (for production, use python-magic)
        file_signatures = {
            "application/pdf": b"%PDF",
            "text/plain": None,  # No specific signature
            "application/json": None,  # No specific signature
            "text/csv": None,  # No specific signature
        }

        if allowed_types:
            valid_type = False
            for mime_type in allowed_types:
                if mime_type in file_signatures:
                    signature = file_signatures[mime_type]
                    if signature is None or file_content.startswith(signature):
                        valid_type = True
                        break

            if not valid_type:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File type not allowed. Allowed types: {', '.join(allowed_types)}",
                )

        return True


# Decorator for automatic validation error handling
def handle_validation_errors(service_name: str):
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Decorator to automatically handle validation errors in FastAPI endpoints.

    Args:
        service_name: Name of the service for error responses
    """

    def decorator(func):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        async def wrapper(*args, **kwargs):
            # requires: Valid input parameters
            # ensures: Correct function execution
            # sha256: func_hash
            try:
                return await func(*args, **kwargs)
            except (ValidationError, RequestValidationError) as e:
                # Extract correlation ID from request if available
                correlation_id = None
                for arg in args:
                    if isinstance(arg, Request):
                        correlation_id = getattr(arg.state, "correlation_id", None)
                        break

                return ValidationHelper.create_validation_error_response(
                    e, service_name, correlation_id
                )

        return wrapper

    return decorator
