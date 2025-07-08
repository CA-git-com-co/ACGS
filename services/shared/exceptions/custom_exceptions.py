"""
Custom Exception Hierarchy with FastAPI Integration
Constitutional Hash: cdd01ef066bc6cf2

This module provides a comprehensive exception hierarchy aligned with
FastAPI exception handlers to improve error handling across all services.
"""

import logging
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

from ..constants import CONSTITUTIONAL_HASH, MESSAGES, ErrorCodes, HttpStatusCodes

logger = logging.getLogger(__name__)


class ACGSBaseException(Exception):
    """Base exception for all ACGS custom exceptions."""

    def __init__(
        self,
        message: str,
        error_code: str = ErrorCodes.SERVICE_ERROR.value,
        status_code: int = HttpStatusCodes.INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}


class ValidationError(ACGSBaseException):
    """Exception raised for validation errors."""

    def __init__(
        self,
        message: str = MESSAGES["VALIDATION_ERROR"],
        field_errors: list[dict[str, str]] | None = None,
        **kwargs,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.INVALID_INPUT.value,
            status_code=HttpStatusCodes.UNPROCESSABLE_ENTITY,
            **kwargs,
        )
        self.field_errors = field_errors or []


class AuthenticationError(ACGSBaseException):
    """Exception raised for authentication failures."""

    def __init__(self, message: str = MESSAGES["UNAUTHORIZED"], **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCodes.INVALID_CREDENTIALS.value,
            status_code=HttpStatusCodes.UNAUTHORIZED,
            **kwargs,
        )


class AuthorizationError(ACGSBaseException):
    """Exception raised for authorization failures."""

    def __init__(
        self,
        message: str = MESSAGES["FORBIDDEN"],
        required_permissions: list[str] | None = None,
        **kwargs,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.INSUFFICIENT_PERMISSIONS.value,
            status_code=HttpStatusCodes.FORBIDDEN,
            **kwargs,
        )
        if required_permissions:
            self.details["required_permissions"] = required_permissions


class ResourceNotFoundError(ACGSBaseException):
    """Exception raised when a resource is not found."""

    def __init__(
        self, resource_type: str, resource_id: str, message: str | None = None, **kwargs
    ):
        if message is None:
            message = f"{resource_type} with ID '{resource_id}' not found"

        super().__init__(
            message=message,
            error_code=ErrorCodes.SERVICE_ERROR.value,
            status_code=HttpStatusCodes.NOT_FOUND,
            **kwargs,
        )
        self.details.update({
            "resource_type": resource_type, "resource_id": resource_id
        })


class ConflictError(ACGSBaseException):
    """Exception raised for resource conflicts."""

    def __init__(self, message: str, conflicting_resource: str | None = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCodes.SERVICE_ERROR.value,
            status_code=HttpStatusCodes.CONFLICT,
            **kwargs,
        )
        if conflicting_resource:
            self.details["conflicting_resource"] = conflicting_resource


class RateLimitExceededError(ACGSBaseException):
    """Exception raised when rate limits are exceeded."""

    def __init__(
        self,
        message: str = MESSAGES["RATE_LIMIT_EXCEEDED"],
        retry_after: int | None = None,
        **kwargs,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.SERVICE_TIMEOUT.value,
            status_code=HttpStatusCodes.TOO_MANY_REQUESTS,
            **kwargs,
        )
        if retry_after:
            self.details["retry_after"] = retry_after


class ServiceUnavailableError(ACGSBaseException):
    """Exception raised when a service is unavailable."""

    def __init__(self, service_name: str, message: str | None = None, **kwargs):
        if message is None:
            message = f"Service '{service_name}' is temporarily unavailable"

        super().__init__(
            message=message,
            error_code=ErrorCodes.SERVICE_UNAVAILABLE.value,
            status_code=HttpStatusCodes.SERVICE_UNAVAILABLE,
            **kwargs,
        )
        self.details["service_name"] = service_name


class DatabaseError(ACGSBaseException):
    """Exception raised for database-related errors."""

    def __init__(self, message: str, operation: str | None = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCodes.SERVICE_ERROR.value,
            status_code=HttpStatusCodes.INTERNAL_SERVER_ERROR,
            **kwargs,
        )
        if operation:
            self.details["operation"] = operation


class ExternalServiceError(ACGSBaseException):
    """Exception raised for external service communication errors."""

    def __init__(
        self,
        service_name: str,
        message: str,
        upstream_status_code: int | None = None,
        **kwargs,
    ):
        super().__init__(
            message=f"External service '{service_name}' error: {message}",
            error_code=ErrorCodes.SERVICE_ERROR.value,
            status_code=HttpStatusCodes.BAD_GATEWAY,
            **kwargs,
        )
        self.details.update({
            "service_name": service_name, "upstream_status_code": upstream_status_code
        })


class ConstitutionalViolationError(ACGSBaseException):
    """Exception raised for constitutional compliance violations."""

    def __init__(
        self,
        message: str = MESSAGES["CONSTITUTIONAL_VIOLATION"],
        violations: list[dict[str, Any]] | None = None,
        constitutional_hash: str = CONSTITUTIONAL_HASH,
        **kwargs,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCodes.CONSTITUTIONAL_HASH_MISMATCH.value,
            status_code=HttpStatusCodes.FORBIDDEN,
            **kwargs,
        )
        self.details.update({
            "constitutional_hash": constitutional_hash, "violations": violations or []
        })


class BusinessLogicError(ACGSBaseException):
    """Exception raised for business logic violations."""

    def __init__(self, message: str, rule_name: str | None = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCodes.INVALID_INPUT.value,
            status_code=HttpStatusCodes.UNPROCESSABLE_ENTITY,
            **kwargs,
        )
        if rule_name:
            self.details["rule_name"] = rule_name


class ConfigurationError(ACGSBaseException):
    """Exception raised for configuration-related errors."""

    def __init__(self, message: str, config_key: str | None = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCodes.SERVICE_ERROR.value,
            status_code=HttpStatusCodes.INTERNAL_SERVER_ERROR,
            **kwargs,
        )
        if config_key:
            self.details["config_key"] = config_key


class TimeoutError(ACGSBaseException):
    """Exception raised for operation timeouts."""

    def __init__(self, operation: str, timeout_seconds: float, **kwargs):
        message = f"Operation '{operation}' timed out after {timeout_seconds} seconds"
        super().__init__(
            message=message,
            error_code=ErrorCodes.SERVICE_TIMEOUT.value,
            status_code=HttpStatusCodes.GATEWAY_TIMEOUT,
            **kwargs,
        )
        self.details.update({
            "operation": operation, "timeout_seconds": timeout_seconds
        })


class ConcurrencyError(ACGSBaseException):
    """Exception raised for concurrency-related errors."""

    def __init__(self, message: str, resource_type: str | None = None, **kwargs):
        super().__init__(
            message=message,
            error_code=ErrorCodes.SERVICE_ERROR.value,
            status_code=HttpStatusCodes.CONFLICT,
            **kwargs,
        )
        if resource_type:
            self.details["resource_type"] = resource_type


# FastAPI Exception Handlers
async def acgs_base_exception_handler(
    request: Request, exc: ACGSBaseException
) -> JSONResponse:
    """Handle ACGS base exceptions."""
    logger.error(
        f"ACGS Exception: {exc.__class__.__name__} - {exc.message}",
        extra={
            "error_code": exc.error_code,
            "status_code": exc.status_code,
            "details": exc.details,
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": "2024-01-01T00:00:00Z",  # Would use actual timestamp
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )


async def validation_exception_handler(
    request: Request, exc: ValidationError
) -> JSONResponse:
    """Handle validation exceptions with field-specific errors."""
    logger.warning(
        f"Validation Error: {exc.message}",
        extra={
            "field_errors": exc.field_errors,
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error_code": exc.error_code,
            "message": exc.message,
            "field_errors": exc.field_errors,
            "details": exc.details,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": "2024-01-01T00:00:00Z",
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )


async def constitutional_violation_handler(
    request: Request, exc: ConstitutionalViolationError
) -> JSONResponse:
    """Handle constitutional violation exceptions."""
    logger.critical(
        f"Constitutional Violation: {exc.message}",
        extra={
            "violations": exc.details.get("violations", []),
            "constitutional_hash": exc.details.get("constitutional_hash"),
            "path": request.url.path,
            "method": request.method,
        },
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "error_code": exc.error_code,
            "message": exc.message,
            "violations": exc.details.get("violations", []),
            "constitutional_hash": exc.details.get(
                "constitutional_hash", CONSTITUTIONAL_HASH
            ),
            "timestamp": "2024-01-01T00:00:00Z",
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )


async def rate_limit_exception_handler(
    request: Request, exc: RateLimitExceededError
) -> JSONResponse:
    """Handle rate limit exceptions with retry-after header."""
    logger.warning(
        f"Rate Limit Exceeded: {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "retry_after": exc.details.get("retry_after"),
        },
    )

    headers = {}
    if "retry_after" in exc.details:
        headers["Retry-After"] = str(exc.details["retry_after"])

    return JSONResponse(
        status_code=exc.status_code,
        headers=headers,
        content={
            "status": "error",
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": "2024-01-01T00:00:00Z",
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions."""
    logger.error(
        f"Unexpected Error: {exc.__class__.__name__} - {exc!s}",
        extra={"path": request.url.path, "method": request.method},
        exc_info=True,
    )

    return JSONResponse(
        status_code=HttpStatusCodes.INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "error_code": ErrorCodes.SERVICE_ERROR.value,
            "message": MESSAGES["SERVICE_ERROR"],
            "details": {},
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": "2024-01-01T00:00:00Z",
            "request_id": getattr(request.state, "request_id", "unknown"),
        },
    )


def setup_exception_handlers(app):
    """Setup all exception handlers for a FastAPI application."""
    app.add_exception_handler(ACGSBaseException, acgs_base_exception_handler)
    app.add_exception_handler(ValidationError, validation_exception_handler)
    app.add_exception_handler(
        ConstitutionalViolationError, constitutional_violation_handler
    )
    app.add_exception_handler(RateLimitExceededError, rate_limit_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)


# Utility functions for raising common exceptions
def raise_not_found(resource_type: str, resource_id: str) -> None:
    """Convenience function to raise ResourceNotFoundError."""
    raise ResourceNotFoundError(resource_type, resource_id)


def raise_unauthorized(message: str = MESSAGES["UNAUTHORIZED"]) -> None:
    """Convenience function to raise AuthenticationError."""
    raise AuthenticationError(message)


def raise_forbidden(
    message: str = MESSAGES["FORBIDDEN"], required_permissions: list[str] | None = None
) -> None:
    """Convenience function to raise AuthorizationError."""
    raise AuthorizationError(message, required_permissions)


def raise_validation_error(
    message: str, field_errors: list[dict[str, str]] | None = None
) -> None:
    """Convenience function to raise ValidationError."""
    raise ValidationError(message, field_errors)


def raise_constitutional_violation(
    message: str = MESSAGES["CONSTITUTIONAL_VIOLATION"],
    violations: list[dict[str, Any]] | None = None,
) -> None:
    """Convenience function to raise ConstitutionalViolationError."""
    raise ConstitutionalViolationError(message, violations)


def raise_service_unavailable(service_name: str, message: str | None = None) -> None:
    """Convenience function to raise ServiceUnavailableError."""
    raise ServiceUnavailableError(service_name, message)
