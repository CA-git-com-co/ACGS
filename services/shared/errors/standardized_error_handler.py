"""
ACGS-1 Standardized Error Handler Implementation

This module provides comprehensive error handling standardization across all ACGS-1
microservices, ensuring consistent error responses, proper HTTP status codes, and
actionable debugging information.

Features:
- Standardized error response format
- Hierarchical error code system
- HTTP status code mapping
- Request correlation tracking
- Error severity classification
- Retry guidance and resolution steps
- Integration with monitoring and logging
"""

import traceback
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union

import structlog
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from ..response.unified_response import ResponseMetadata, UnifiedResponse
from .error_catalog import ErrorCatalog, ErrorCategory, ErrorSeverity, ServiceCode

logger = structlog.get_logger(__name__)


class HTTPStatusCode(int, Enum):
    """Standard HTTP status codes for error responses."""

    # Client Errors (4xx)
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429

    # Server Errors (5xx)
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504


class ErrorDetail(BaseModel):
    """Detailed error information."""

    code: str = Field(..., description="Standardized error code")
    message: str = Field(..., description="Human-readable error message")
    user_message: str = Field(..., description="User-friendly error message")
    category: str = Field(..., description="Error category")
    severity: str = Field(..., description="Error severity level")
    retryable: bool = Field(..., description="Whether the operation can be retried")
    resolution_guidance: str = Field(..., description="How to resolve this error")
    context: Dict[str, Any] = Field(default_factory=dict, description="Error context")
    timestamp: str = Field(..., description="Error occurrence timestamp")
    request_id: str = Field(..., description="Request correlation ID")
    service: str = Field(..., description="Service where error occurred")
    stack_trace: Optional[str] = Field(None, description="Stack trace for debugging")


class StandardizedErrorResponse(BaseModel):
    """Standardized error response model."""

    success: bool = Field(False, description="Always false for error responses")
    error: ErrorDetail = Field(..., description="Error details")
    data: Optional[Any] = Field(None, description="Additional error data")
    metadata: ResponseMetadata = Field(..., description="Response metadata")


class ErrorHandler:
    """Centralized error handler for ACGS-1 services."""

    def __init__(
        self, service_name: str, service_code: ServiceCode, version: str = "1.0.0"
    ):
        """Initialize error handler for specific service."""
        self.service_name = service_name
        self.service_code = service_code
        self.version = version
        self.error_catalog = ErrorCatalog()

        # Register common errors for this service
        self._register_common_errors()

    def _register_common_errors(self):
        """Register common errors for all services."""
        common_errors = [
            {
                "category": ErrorCategory.VALIDATION,
                "message": "Invalid request data",
                "description": "Request validation failed",
                "http_status": HTTPStatusCode.BAD_REQUEST,
                "severity": ErrorSeverity.LOW,
                "resolution_guidance": "Check request format and required fields",
                "user_message": "Please check your request and try again",
                "retryable": False,
            },
            {
                "category": ErrorCategory.AUTHENTICATION,
                "message": "Authentication required",
                "description": "Valid authentication token required",
                "http_status": HTTPStatusCode.UNAUTHORIZED,
                "severity": ErrorSeverity.MEDIUM,
                "resolution_guidance": "Provide valid authentication token",
                "user_message": "Please log in to access this resource",
                "retryable": False,
            },
            {
                "category": ErrorCategory.AUTHORIZATION,
                "message": "Insufficient permissions",
                "description": "User lacks required permissions",
                "http_status": HTTPStatusCode.FORBIDDEN,
                "severity": ErrorSeverity.MEDIUM,
                "resolution_guidance": "Contact administrator for access",
                "user_message": "You don't have permission to perform this action",
                "retryable": False,
            },
            {
                "category": ErrorCategory.RATE_LIMIT,
                "message": "Rate limit exceeded",
                "description": "Too many requests in time window",
                "http_status": HTTPStatusCode.TOO_MANY_REQUESTS,
                "severity": ErrorSeverity.LOW,
                "resolution_guidance": "Wait before retrying request",
                "user_message": "Too many requests. Please wait and try again",
                "retryable": True,
            },
            {
                "category": ErrorCategory.INTERNAL,
                "message": "Internal server error",
                "description": "Unexpected internal error occurred",
                "http_status": HTTPStatusCode.INTERNAL_SERVER_ERROR,
                "severity": ErrorSeverity.HIGH,
                "resolution_guidance": "Contact support if error persists",
                "user_message": "An unexpected error occurred. Please try again",
                "retryable": True,
            },
        ]

        for error_config in common_errors:
            try:
                self.error_catalog.register_error(
                    service=self.service_code, **error_config
                )
            except ValueError:
                # Error already registered
                pass

    def create_error_response(
        self,
        error_code: str,
        context: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
        include_stack_trace: bool = False,
    ) -> StandardizedErrorResponse:
        """Create standardized error response."""

        # Get error definition from catalog
        error_def = self.error_catalog.get_error_definition(error_code)
        if not error_def:
            # Fallback to generic internal error
            error_def = self.error_catalog.get_error_definition(
                f"{self.service_code.value}_INTERNAL_001"
            )

        # Create error detail
        error_detail = ErrorDetail(
            code=error_code,
            message=error_def["message"],
            user_message=error_def["user_message"],
            category=error_def["category"],
            severity=error_def["severity"],
            retryable=error_def["retryable"],
            resolution_guidance=error_def["resolution_guidance"],
            context=context or {},
            timestamp=datetime.now(timezone.utc).isoformat(),
            request_id=request_id or str(uuid.uuid4()),
            service=self.service_name,
            stack_trace=traceback.format_exc() if include_stack_trace else None,
        )

        # Create response metadata
        metadata = ResponseMetadata(
            timestamp=datetime.now(timezone.utc).isoformat(),
            request_id=error_detail.request_id,
            version=self.version,
            service=self.service_name,
        )

        return StandardizedErrorResponse(error=error_detail, metadata=metadata)

    def handle_exception(
        self,
        exception: Exception,
        request: Optional[Request] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> JSONResponse:
        """Handle exception and return standardized error response."""

        request_id = None
        if request:
            request_id = getattr(request.state, "request_id", None) or str(uuid.uuid4())

        # Determine error code based on exception type
        error_code = self._map_exception_to_error_code(exception)

        # Add exception details to context
        error_context = context or {}
        error_context.update(
            {
                "exception_type": type(exception).__name__,
                "exception_message": str(exception),
            }
        )

        # Create error response
        error_response = self.create_error_response(
            error_code=error_code,
            context=error_context,
            request_id=request_id,
            include_stack_trace=True,  # Include in development/debug mode
        )

        # Log error
        logger.error(
            "Error handled",
            error_code=error_code,
            exception_type=type(exception).__name__,
            exception_message=str(exception),
            request_id=request_id,
            service=self.service_name,
            context=error_context,
        )

        # Get HTTP status code
        http_status = self._get_http_status_for_error(error_code)

        return JSONResponse(
            status_code=http_status, content=error_response.model_dump()
        )

    def _map_exception_to_error_code(self, exception: Exception) -> str:
        """Map exception type to standardized error code."""

        exception_mapping = {
            ValueError: f"{self.service_code.value}_VALIDATION_001",
            KeyError: f"{self.service_code.value}_VALIDATION_002",
            TypeError: f"{self.service_code.value}_VALIDATION_003",
            PermissionError: f"{self.service_code.value}_AUTHORIZATION_001",
            ConnectionError: f"{self.service_code.value}_EXTERNAL_001",
            TimeoutError: f"{self.service_code.value}_EXTERNAL_002",
            HTTPException: f"{self.service_code.value}_HTTP_{exception.status_code:03d}",
        }

        exception_type = type(exception)
        return exception_mapping.get(
            exception_type, f"{self.service_code.value}_INTERNAL_001"
        )

    def _get_http_status_for_error(self, error_code: str) -> int:
        """Get HTTP status code for error code."""

        error_def = self.error_catalog.get_error_definition(error_code)
        if error_def:
            return error_def["http_status"]

        return HTTPStatusCode.INTERNAL_SERVER_ERROR


# Service-specific error handlers
def create_auth_error_handler() -> ErrorHandler:
    """Create error handler for Authentication Service."""
    return ErrorHandler("authentication-service", ServiceCode.AUTH, "2.1.0")


def create_ac_error_handler() -> ErrorHandler:
    """Create error handler for Constitutional AI Service."""
    return ErrorHandler("constitutional-ai-service", ServiceCode.AC, "2.1.0")


def create_integrity_error_handler() -> ErrorHandler:
    """Create error handler for Integrity Service."""
    return ErrorHandler("integrity-service", ServiceCode.INTEGRITY, "2.0.0")


def create_fv_error_handler() -> ErrorHandler:
    """Create error handler for Formal Verification Service."""
    return ErrorHandler("formal-verification-service", ServiceCode.FV, "1.5.0")


def create_gs_error_handler() -> ErrorHandler:
    """Create error handler for Governance Synthesis Service."""
    return ErrorHandler("governance-synthesis-service", ServiceCode.GS, "2.2.0")


def create_pgc_error_handler() -> ErrorHandler:
    """Create error handler for Policy Governance Service."""
    return ErrorHandler("policy-governance-service", ServiceCode.PGC, "2.0.0")


def create_ec_error_handler() -> ErrorHandler:
    """Create error handler for Evolutionary Computation Service."""
    return ErrorHandler("evolutionary-computation-service", ServiceCode.EC, "1.8.0")


def create_dgm_error_handler() -> ErrorHandler:
    """Create error handler for Darwin Gödel Machine Service."""
    return ErrorHandler("darwin-godel-machine-service", ServiceCode.DGM, "1.0.0")


# Export main classes and functions
__all__ = [
    "ErrorHandler",
    "StandardizedErrorResponse",
    "ErrorDetail",
    "HTTPStatusCode",
    "create_auth_error_handler",
    "create_ac_error_handler",
    "create_integrity_error_handler",
    "create_fv_error_handler",
    "create_gs_error_handler",
    "create_pgc_error_handler",
    "create_ec_error_handler",
    "create_dgm_error_handler",
]
