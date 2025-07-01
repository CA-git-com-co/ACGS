"""
ACGS-1 Standardized Error Handling
==================================

This module provides consistent error handling patterns across all ACGS services,
implementing the error handling requirements from the ACGS-1 Lite architecture.

Features:
- Standardized exception hierarchy
- Consistent error response formats
- Structured error logging
- Error code mapping
- Circuit breaker integration
- Audit trail for errors
"""

import json
import logging
import traceback
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from fastapi import HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorSeverity(str, Enum):
    """Error severity levels for ACGS services."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(str, Enum):
    """Error categories for classification."""

    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    DATABASE = "database"
    NETWORK = "network"
    SYSTEM = "system"
    CONSTITUTIONAL = "constitutional"


class ACGSError(Exception):
    """Base exception class for all ACGS errors."""

    def __init__(
        self,
        message: str,
        error_code: str,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.cause = cause
        self.timestamp = datetime.now(timezone.utc)


class ValidationError(ACGSError):
    """Validation error for input validation failures."""

    def __init__(self, message: str, field: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.LOW,
            **kwargs,
        )
        if field:
            self.details["field"] = field


class AuthenticationError(ACGSError):
    """Authentication error for auth failures."""

    def __init__(self, message: str = "Authentication failed", **kwargs):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            category=ErrorCategory.AUTHENTICATION,
            severity=ErrorSeverity.HIGH,
            **kwargs,
        )


class AuthorizationError(ACGSError):
    """Authorization error for permission failures."""

    def __init__(self, message: str = "Access denied", **kwargs):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            category=ErrorCategory.AUTHORIZATION,
            severity=ErrorSeverity.HIGH,
            **kwargs,
        )


class ConstitutionalError(ACGSError):
    """Constitutional compliance error."""

    def __init__(self, message: str, compliance_score: float = None, **kwargs):
        super().__init__(
            message=message,
            error_code="CONSTITUTIONAL_ERROR",
            category=ErrorCategory.CONSTITUTIONAL,
            severity=ErrorSeverity.CRITICAL,
            **kwargs,
        )
        if compliance_score is not None:
            self.details["compliance_score"] = compliance_score


class ExternalServiceError(ACGSError):
    """External service error for third-party service failures."""

    def __init__(self, message: str, service_name: str, **kwargs):
        super().__init__(
            message=message,
            error_code="EXTERNAL_SERVICE_ERROR",
            category=ErrorCategory.EXTERNAL_SERVICE,
            severity=ErrorSeverity.MEDIUM,
            **kwargs,
        )
        self.details["service_name"] = service_name


class DatabaseError(ACGSError):
    """Database error for database operation failures."""

    def __init__(self, message: str, operation: str = None, **kwargs):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            category=ErrorCategory.DATABASE,
            severity=ErrorSeverity.HIGH,
            **kwargs,
        )
        if operation:
            self.details["operation"] = operation


class ErrorResponse(BaseModel):
    """Standardized error response model."""

    error: bool = True
    error_code: str
    message: str
    category: ErrorCategory
    severity: ErrorSeverity
    timestamp: datetime
    details: Dict[str, Any] = {}
    trace_id: Optional[str] = None
    service: Optional[str] = None


class ErrorHandler:
    """Centralized error handler for ACGS services."""

    def __init__(self, service_name: str = "acgs_service"):
        self.service_name = service_name
        self.logger = logging.getLogger(f"{service_name}.error_handler")

    def handle_error(
        self,
        error: Union[Exception, ACGSError],
        request: Optional[Request] = None,
        trace_id: Optional[str] = None,
    ) -> JSONResponse:
        """Handle and format errors consistently."""

        # Convert to ACGSError if needed
        if isinstance(error, ACGSError):
            acgs_error = error
        else:
            acgs_error = self._convert_to_acgs_error(error)

        # Create error response
        error_response = ErrorResponse(
            error_code=acgs_error.error_code,
            message=acgs_error.message,
            category=acgs_error.category,
            severity=acgs_error.severity,
            timestamp=acgs_error.timestamp,
            details=acgs_error.details,
            trace_id=trace_id,
            service=self.service_name,
        )

        # Log error
        self._log_error(acgs_error, request, trace_id)

        # Determine HTTP status code
        status_code = self._get_http_status_code(acgs_error)

        return JSONResponse(
            status_code=status_code, content=error_response.model_dump()
        )

    def _convert_to_acgs_error(self, error: Exception) -> ACGSError:
        """Convert standard exceptions to ACGSError."""

        if isinstance(error, HTTPException):
            return ACGSError(
                message=error.detail,
                error_code="HTTP_ERROR",
                category=ErrorCategory.SYSTEM,
                severity=ErrorSeverity.MEDIUM,
                details={"status_code": error.status_code},
            )

        return ACGSError(
            message=str(error),
            error_code="UNKNOWN_ERROR",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.MEDIUM,
            details={"exception_type": type(error).__name__},
            cause=error,
        )

    def _log_error(
        self,
        error: ACGSError,
        request: Optional[Request] = None,
        trace_id: Optional[str] = None,
    ):
        """Log error with structured format."""

        log_data = {
            "error_code": error.error_code,
            "message": error.message,
            "category": error.category.value,
            "severity": error.severity.value,
            "timestamp": error.timestamp.isoformat(),
            "service": self.service_name,
            "trace_id": trace_id,
            "details": error.details,
        }

        if request:
            log_data["request"] = {
                "method": request.method,
                "url": str(request.url),
                "headers": dict(request.headers),
                "client": request.client.host if request.client else None,
            }

        if error.cause:
            log_data["traceback"] = traceback.format_exception(
                type(error.cause), error.cause, error.cause.__traceback__
            )

        # Log at appropriate level based on severity
        if error.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(json.dumps(log_data))
        elif error.severity == ErrorSeverity.HIGH:
            self.logger.error(json.dumps(log_data))
        elif error.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(json.dumps(log_data))
        else:
            self.logger.info(json.dumps(log_data))

    def _get_http_status_code(self, error: ACGSError) -> int:
        """Map error types to HTTP status codes."""

        error_code_mapping = {
            "VALIDATION_ERROR": status.HTTP_400_BAD_REQUEST,
            "AUTHENTICATION_ERROR": status.HTTP_401_UNAUTHORIZED,
            "AUTHORIZATION_ERROR": status.HTTP_403_FORBIDDEN,
            "CONSTITUTIONAL_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
            "EXTERNAL_SERVICE_ERROR": status.HTTP_502_BAD_GATEWAY,
            "DATABASE_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "NETWORK_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
        }

        return error_code_mapping.get(
            error.error_code, status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Global error handler instance
global_error_handler = ErrorHandler()


def create_error_handler(service_name: str) -> ErrorHandler:
    """Create a service-specific error handler."""
    return ErrorHandler(service_name)
