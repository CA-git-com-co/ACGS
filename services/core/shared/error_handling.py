"""
Standardized Error Handling for ACGS-2 Services
Constitutional Hash: cdd01ef066bc6cf2

This module provides consistent error handling patterns across all ACGS-2 services
with constitutional compliance validation and structured error responses.
"""

import logging
import traceback
from typing import Any, Dict, Optional, Union
from datetime import datetime
from enum import Enum
import uuid
from functools import wraps

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification."""

    VALIDATION = "validation"
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    CONSTITUTIONAL = "constitutional"
    PERFORMANCE = "performance"
    SYSTEM = "system"
    EXTERNAL = "external"


class ACGSError(Exception):
    """Base exception for ACGS-2 system errors."""

    def __init__(
        self,
        message: str,
        error_code: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        details: Optional[Dict[str, Any]] = None,
        constitutional_hash: str = "cdd01ef066bc6cf2",
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.severity = severity
        self.category = category
        self.details = details or {}
        self.constitutional_hash = constitutional_hash
        self.timestamp = datetime.utcnow()
        self.request_id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary for JSON serialization."""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "severity": self.severity.value,
                "category": self.category.value,
                "details": self.details,
                "constitutional_hash": self.constitutional_hash,
                "timestamp": self.timestamp.isoformat(),
                "request_id": self.request_id,
            }
        }


class ConstitutionalComplianceError(ACGSError):
    """Error for constitutional compliance violations."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONSTITUTIONAL_VIOLATION",
            severity=ErrorSeverity.CRITICAL,
            category=ErrorCategory.CONSTITUTIONAL,
            details=details,
        )


class ValidationError(ACGSError):
    """Error for input validation failures."""

    def __init__(
        self, message: str, field: str, details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["field"] = field
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            severity=ErrorSeverity.MEDIUM,
            category=ErrorCategory.VALIDATION,
            details=details,
        )


class AuthenticationError(ACGSError):
    """Error for authentication failures."""

    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHENTICATION,
            details=details,
        )


class AuthorizationError(ACGSError):
    """Error for authorization failures."""

    def __init__(
        self,
        message: str = "Authorization failed",
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.AUTHORIZATION,
            details=details,
        )


class PerformanceError(ACGSError):
    """Error for performance-related issues."""

    def __init__(self, message: str, metric: str, value: float, threshold: float):
        super().__init__(
            message=message,
            error_code="PERFORMANCE_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.PERFORMANCE,
            details={"metric": metric, "value": value, "threshold": threshold},
        )


class ExternalServiceError(ACGSError):
    """Error for external service failures."""

    def __init__(
        self, message: str, service_name: str, details: Optional[Dict[str, Any]] = None
    ):
        details = details or {}
        details["service_name"] = service_name
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.EXTERNAL,
            details=details,
        )


class ErrorHandler:
    """Centralized error handling with constitutional compliance."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.constitutional_hash = "cdd01ef066bc6cf2"

    def handle_error(
        self, error: Exception, request: Optional[Request] = None
    ) -> JSONResponse:
        """
        Handle errors with consistent formatting and logging.

        Args:
            error: Exception to handle
            request: Optional FastAPI request object

        Returns:
            JSONResponse: Formatted error response
        """
        # Generate request ID if not available
        request_id = getattr(request, "state", {}).get("request_id", str(uuid.uuid4()))

        # Handle ACGS custom errors
        if isinstance(error, ACGSError):
            return self._handle_acgs_error(error, request_id)

        # Handle HTTP exceptions
        if isinstance(error, HTTPException):
            return self._handle_http_error(error, request_id)

        # Handle unknown errors
        return self._handle_unknown_error(error, request_id)

    def _handle_acgs_error(self, error: ACGSError, request_id: str) -> JSONResponse:
        """Handle ACGS custom errors."""
        error_dict = error.to_dict()
        error_dict["error"]["request_id"] = request_id
        error_dict["error"]["service_name"] = self.service_name

        # Log error based on severity
        log_message = f"ACGS Error [{error.error_code}]: {error.message}"

        if error.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message, extra=error_dict)
        elif error.severity == ErrorSeverity.HIGH:
            logger.error(log_message, extra=error_dict)
        elif error.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message, extra=error_dict)
        else:
            logger.info(log_message, extra=error_dict)

        # Determine HTTP status code
        status_code = self._get_http_status_for_error(error)

        return JSONResponse(status_code=status_code, content=error_dict)

    def _handle_http_error(self, error: HTTPException, request_id: str) -> JSONResponse:
        """Handle FastAPI HTTP exceptions."""
        error_dict = {
            "error": {
                "code": f"HTTP_{error.status_code}",
                "message": error.detail,
                "severity": ErrorSeverity.MEDIUM.value,
                "category": ErrorCategory.SYSTEM.value,
                "details": {},
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id,
                "service_name": self.service_name,
            }
        }

        logger.warning(
            f"HTTP Error [{error.status_code}]: {error.detail}", extra=error_dict
        )

        return JSONResponse(status_code=error.status_code, content=error_dict)

    def _handle_unknown_error(self, error: Exception, request_id: str) -> JSONResponse:
        """Handle unknown/unexpected errors."""
        error_dict = {
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "severity": ErrorSeverity.CRITICAL.value,
                "category": ErrorCategory.SYSTEM.value,
                "details": {
                    "error_type": type(error).__name__,
                    "error_message": str(error),
                },
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id,
                "service_name": self.service_name,
            }
        }

        # Log full traceback for debugging
        logger.critical(
            f"Unknown Error [{type(error).__name__}]: {str(error)}\n{traceback.format_exc()}",
            extra=error_dict,
        )

        return JSONResponse(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR, content=error_dict
        )

    def _get_http_status_for_error(self, error: ACGSError) -> int:
        """Get appropriate HTTP status code for ACGS error."""
        status_map = {
            ErrorCategory.VALIDATION: 400,
            ErrorCategory.AUTHENTICATION: 401,
            ErrorCategory.AUTHORIZATION: 403,
            ErrorCategory.CONSTITUTIONAL: 403,
            ErrorCategory.PERFORMANCE: 503,
            ErrorCategory.EXTERNAL: 502,
            ErrorCategory.SYSTEM: 500,
        }
        return status_map.get(error.category, 500)


def setup_error_handlers(app, service_name: str):
    """
    Set up error handlers for FastAPI application.

    Args:
        app: FastAPI application instance
        service_name: Name of the service
    """
    error_handler = ErrorHandler(service_name)

    @app.exception_handler(ACGSError)
    async def acgs_error_handler(request: Request, exc: ACGSError):
        return error_handler.handle_error(exc, request)

    @app.exception_handler(HTTPException)
    async def http_error_handler(request: Request, exc: HTTPException):
        return error_handler.handle_error(exc, request)

    @app.exception_handler(Exception)
    async def general_error_handler(request: Request, exc: Exception):
        return error_handler.handle_error(exc, request)


def handle_errors(service_name: str):
    """
    Decorator for error handling in functions.

    Args:
        service_name: Name of the service
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handler = ErrorHandler(service_name)
                raise ACGSError(
                    message=f"Error in {func.__name__}: {str(e)}",
                    error_code="FUNCTION_ERROR",
                    severity=ErrorSeverity.HIGH,
                    category=ErrorCategory.SYSTEM,
                    details={"function": func.__name__, "args": str(args)[:100]},
                )

        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                handler = ErrorHandler(service_name)
                raise ACGSError(
                    message=f"Error in {func.__name__}: {str(e)}",
                    error_code="FUNCTION_ERROR",
                    severity=ErrorSeverity.HIGH,
                    category=ErrorCategory.SYSTEM,
                    details={"function": func.__name__, "args": str(args)[:100]},
                )

        return async_wrapper if asyncio.iscoroutinefunction(func) else wrapper

    return decorator


# Convenience functions for common error scenarios
def raise_constitutional_violation(
    message: str, details: Optional[Dict[str, Any]] = None
):
    """Raise constitutional compliance violation."""
    raise ConstitutionalComplianceError(message, details)


def raise_validation_error(
    message: str, field: str, details: Optional[Dict[str, Any]] = None
):
    """Raise validation error."""
    raise ValidationError(message, field, details)


def raise_authentication_error(
    message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None
):
    """Raise authentication error."""
    raise AuthenticationError(message, details)


def raise_authorization_error(
    message: str = "Authorization failed", details: Optional[Dict[str, Any]] = None
):
    """Raise authorization error."""
    raise AuthorizationError(message, details)


def raise_performance_error(message: str, metric: str, value: float, threshold: float):
    """Raise performance error."""
    raise PerformanceError(message, metric, value, threshold)


def raise_external_service_error(
    message: str, service_name: str, details: Optional[Dict[str, Any]] = None
):
    """Raise external service error."""
    raise ExternalServiceError(message, service_name, details)


import asyncio
