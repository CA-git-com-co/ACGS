"""
ACGS Standardized Error Handling Middleware
Constitutional Hash: cdd01ef066bc6cf2

This module provides standardized error handling across all ACGS services.
It ensures consistent error responses, proper logging, and constitutional compliance.
"""

import logging
import time
import traceback
import uuid
from datetime import datetime
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class ACGSException(Exception):
    """Base exception for ACGS services."""

    def __init__(
        self,
        message: str,
        error_code: str = "ACGS_ERROR",
        status_code: int = 500,
        details: dict[str, Any] | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        self.constitutional_hash = CONSTITUTIONAL_HASH
        super().__init__(message)


class ConstitutionalComplianceError(ACGSException):
    """Constitutional compliance violation errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code="CONSTITUTIONAL_VIOLATION",
            status_code=403,
            details=details,
        )


class SecurityValidationError(ACGSException):
    """Security validation errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code="SECURITY_VALIDATION_FAILED",
            status_code=400,
            details=details,
        )


class AuthenticationError(ACGSException):
    """Authentication-related errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_FAILED",
            status_code=401,
            details=details,
        )


class AuthorizationError(ACGSException):
    """Authorization-related errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_FAILED",
            status_code=403,
            details=details,
        )


class ServiceUnavailableError(ACGSException):
    """Service unavailability errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code="SERVICE_UNAVAILABLE",
            status_code=503,
            details=details,
        )


class ValidationError(ACGSException):
    """Validation errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_FAILED",
            status_code=422,
            details=details,
        )


class RateLimitError(ACGSException):
    """Rate limiting errors."""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            status_code=429,
            details=details,
        )


class ErrorResponse:
    """Standardized error response format."""

    @staticmethod
    def create_error_response(
        error: Exception,
        request: Request,
        error_id: str | None = None,
        include_traceback: bool = False,
    ) -> dict[str, Any]:
        """Create standardized error response."""

        error_id = error_id or str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Base error response
        response = {
            "error": {
                "id": error_id,
                "timestamp": timestamp,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "request": {
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": dict(request.query_params),
                },
            }
        }

        # Handle ACGS custom exceptions
        if isinstance(error, ACGSException):
            response["error"].update(
                {
                    "code": error.error_code,
                    "message": error.message,
                    "status_code": error.status_code,
                    "details": error.details,
                }
            )

        # Handle FastAPI HTTP exceptions
        elif isinstance(error, HTTPException):
            response["error"].update(
                {
                    "code": f"HTTP_{error.status_code}",
                    "message": error.detail,
                    "status_code": error.status_code,
                    "details": {},
                }
            )

        # Handle validation errors
        elif isinstance(error, RequestValidationError):
            response["error"].update(
                {
                    "code": "VALIDATION_ERROR",
                    "message": "Request validation failed",
                    "status_code": 422,
                    "details": {"validation_errors": error.errors()},
                }
            )

        # Handle generic exceptions
        else:
            response["error"].update(
                {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "An unexpected error occurred",
                    "status_code": 500,
                    "details": {
                        "error_type": type(error).__name__,
                        "error_message": str(error),
                    },
                }
            )

        # Add traceback for debugging (only in development)
        if include_traceback:
            response["error"]["traceback"] = traceback.format_exc()

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Error handling middleware for ACGS services."""

    def __init__(
        self, app, service_name: str = "unknown", include_traceback: bool = False
    ):
        super().__init__(app)
        self.service_name = service_name
        self.include_traceback = include_traceback
        self.constitutional_hash = CONSTITUTIONAL_HASH

    async def dispatch(self, request: Request, call_next):
        """Handle request and catch any errors."""
        error_id = str(uuid.uuid4())
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Log successful requests
            duration = time.time() - start_time
            logger.info(
                "Request processed successfully",
                extra={
                    "service": self.service_name,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": round(duration * 1000, 2),
                    "constitutional_hash": self.constitutional_hash,
                    "request_id": error_id,
                },
            )

            return response

        except Exception as error:
            # Log error with full context
            duration = time.time() - start_time

            logger.error(
                f"Request failed: {error!s}",
                extra={
                    "service": self.service_name,
                    "method": request.method,
                    "path": request.url.path,
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                    "duration_ms": round(duration * 1000, 2),
                    "constitutional_hash": self.constitutional_hash,
                    "request_id": error_id,
                    "client_ip": request.client.host if request.client else None,
                    "user_agent": request.headers.get("user-agent"),
                },
                exc_info=True,
            )

            # Create standardized error response
            error_response = ErrorResponse.create_error_response(
                error=error,
                request=request,
                error_id=error_id,
                include_traceback=self.include_traceback,
            )

            # Determine status code
            if isinstance(error, (ACGSException, HTTPException)):
                status_code = error.status_code
            elif isinstance(error, RequestValidationError):
                status_code = 422
            else:
                status_code = 500

            return JSONResponse(
                status_code=status_code,
                content=error_response,
                headers={
                    "X-Error-ID": error_id,
                    "X-Constitutional-Hash": self.constitutional_hash,
                    "X-Service": self.service_name,
                },
            )


def setup_error_handlers(
    app: FastAPI, service_name: str = "unknown", include_traceback: bool = False
):
    """Setup comprehensive error handlers for a FastAPI application."""

    # Add error handling middleware
    app.add_middleware(
        ErrorHandlingMiddleware,
        service_name=service_name,
        include_traceback=include_traceback,
    )

    # Custom exception handlers
    @app.exception_handler(ACGSException)
    async def acgs_exception_handler(request: Request, exc: ACGSException):
        """Handle ACGS custom exceptions."""
        error_id = str(uuid.uuid4())

        logger.warning(
            f"ACGS Exception: {exc.message}",
            extra={
                "service": service_name,
                "error_code": exc.error_code,
                "error_details": exc.details,
                "constitutional_hash": exc.constitutional_hash,
                "request_id": error_id,
                "path": request.url.path,
                "method": request.method,
            },
        )

        error_response = ErrorResponse.create_error_response(
            error=exc,
            request=request,
            error_id=error_id,
            include_traceback=include_traceback,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers={
                "X-Error-ID": error_id,
                "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
                "X-Service": service_name,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle FastAPI HTTP exceptions."""
        error_id = str(uuid.uuid4())

        logger.warning(
            f"HTTP Exception: {exc.detail}",
            extra={
                "service": service_name,
                "status_code": exc.status_code,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "request_id": error_id,
                "path": request.url.path,
                "method": request.method,
            },
        )

        error_response = ErrorResponse.create_error_response(
            error=exc,
            request=request,
            error_id=error_id,
            include_traceback=include_traceback,
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=error_response,
            headers={
                "X-Error-ID": error_id,
                "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
                "X-Service": service_name,
            },
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        """Handle request validation errors."""
        error_id = str(uuid.uuid4())

        logger.warning(
            f"Validation Error: {exc.errors()}",
            extra={
                "service": service_name,
                "validation_errors": exc.errors(),
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "request_id": error_id,
                "path": request.url.path,
                "method": request.method,
            },
        )

        error_response = ErrorResponse.create_error_response(
            error=exc,
            request=request,
            error_id=error_id,
            include_traceback=include_traceback,
        )

        return JSONResponse(
            status_code=422,
            content=error_response,
            headers={
                "X-Error-ID": error_id,
                "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
                "X-Service": service_name,
            },
        )

    @app.exception_handler(500)
    async def internal_server_error_handler(request: Request, exc: Exception):
        """Handle internal server errors."""
        error_id = str(uuid.uuid4())

        logger.error(
            f"Internal Server Error: {exc!s}",
            extra={
                "service": service_name,
                "error_type": type(exc).__name__,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "request_id": error_id,
                "path": request.url.path,
                "method": request.method,
            },
        )

        error_response = ErrorResponse.create_error_response(
            error=exc,
            request=request,
            error_id=error_id,
            include_traceback=include_traceback,
        )

        return JSONResponse(
            status_code=500,
            content=error_response,
            headers={
                "X-Error-ID": error_id,
                "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
                "X-Service": service_name,
            },
        )

    logger.info(f"Error handlers configured for service: {service_name}")


def create_error_middleware(service_name: str, development_mode: bool = False):
    """Create error handling middleware with appropriate configuration."""
    return ErrorHandlingMiddleware(
        app=None,  # Will be set by FastAPI
        service_name=service_name,
        include_traceback=development_mode,
    )


def log_error_with_context(
    error: Exception,
    context: dict[str, Any],
    service_name: str = "unknown",
    level: str = "error",
):
    """Log error with additional context information."""

    log_data = {
        "service": service_name,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "constitutional_hash": CONSTITUTIONAL_HASH,
        **context,
    }

    if level == "error":
        logger.error(f"Error in {service_name}: {error!s}", extra=log_data)
    elif level == "warning":
        logger.warning(f"Warning in {service_name}: {error!s}", extra=log_data)
    else:
        logger.info(f"Info in {service_name}: {error!s}", extra=log_data)


def raise_constitutional_error(message: str, details: dict[str, Any] | None = None):
    """Raise a constitutional compliance error."""
    raise ConstitutionalComplianceError(message=message, details=details)


def raise_security_error(message: str, details: dict[str, Any] | None = None):
    """Raise a security validation error."""
    raise SecurityValidationError(message=message, details=details)


def raise_auth_error(message: str, details: dict[str, Any] | None = None):
    """Raise an authentication error."""
    raise AuthenticationError(message=message, details=details)


def raise_validation_error(message: str, details: dict[str, Any] | None = None):
    """Raise a validation error."""
    raise ValidationError(message=message, details=details)


# Error context manager for graceful error handling
class ErrorContext:
    """Context manager for graceful error handling."""

    def __init__(
        self,
        operation: str,
        service_name: str = "unknown",
        raise_on_error: bool = True,
        log_level: str = "error",
    ):
        self.operation = operation
        self.service_name = service_name
        self.raise_on_error = raise_on_error
        self.log_level = log_level
        self.constitutional_hash = CONSTITUTIONAL_HASH

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            context = {
                "operation": self.operation,
                "constitutional_hash": self.constitutional_hash,
            }

            log_error_with_context(
                error=exc_val,
                context=context,
                service_name=self.service_name,
                level=self.log_level,
            )

            if not self.raise_on_error:
                return True  # Suppress the exception

        return False  # Let the exception propagate


# Utility functions for common error scenarios
def handle_database_error(error: Exception, operation: str = "database_operation"):
    """Handle database-related errors."""
    if "connection" in str(error).lower():
        raise ServiceUnavailableError(
            message="Database connection unavailable",
            details={"operation": operation, "original_error": str(error)},
        )
    raise ACGSException(
        message=f"Database operation failed: {operation}",
        error_code="DATABASE_ERROR",
        status_code=500,
        details={"operation": operation, "original_error": str(error)},
    )


def handle_external_service_error(error: Exception, service: str = "external_service"):
    """Handle external service errors."""
    raise ServiceUnavailableError(
        message=f"External service unavailable: {service}",
        details={"service": service, "original_error": str(error)},
    )


def handle_timeout_error(error: Exception, operation: str = "operation"):
    """Handle timeout errors."""
    raise ACGSException(
        message=f"Operation timed out: {operation}",
        error_code="TIMEOUT_ERROR",
        status_code=408,
        details={"operation": operation, "original_error": str(error)},
    )
