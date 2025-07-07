"""
ACGS Shared API Models and Response Utilities
Constitutional Hash: cdd01ef066bc6cf2

Provides standardized API response models and utilities for all ACGS services.
"""

import time
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ErrorCode(str, Enum):
    """Standardized error codes for ACGS services."""

    # General errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"

    # Service-specific errors
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"

    # Constitutional compliance errors
    CONSTITUTIONAL_VIOLATION = "CONSTITUTIONAL_VIOLATION"
    COMPLIANCE_CHECK_FAILED = "COMPLIANCE_CHECK_FAILED"

    # Data integrity errors
    INTEGRITY_VIOLATION = "INTEGRITY_VIOLATION"
    SIGNATURE_INVALID = "SIGNATURE_INVALID"
    HASH_MISMATCH = "HASH_MISMATCH"


class APIResponse(BaseModel):
    """Base API response model with constitutional compliance."""

    success: bool = Field(..., description="Whether the request was successful")
    message: str = Field(..., description="Human-readable message")
    data: Optional[Any] = Field(None, description="Response data")
    error_code: Optional[ErrorCode] = Field(
        None, description="Error code if applicable"
    )
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    constitutional_hash: str = Field(
        default=CONSTITUTIONAL_HASH, description="Constitutional compliance hash"
    )
    service_name: Optional[str] = Field(
        None, description="Name of the responding service"
    )


class ErrorResponse(APIResponse):
    """Standardized error response model."""

    success: bool = Field(default=False, description="Always false for error responses")
    error_details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )
    validation_errors: Optional[List[Dict[str, str]]] = Field(
        None, description="Field validation errors"
    )


class SuccessResponse(APIResponse):
    """Standardized success response model."""

    success: bool = Field(default=True, description="Always true for success responses")


def create_success_response(
    message: str = "Operation completed successfully",
    data: Optional[Any] = None,
    service_name: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a standardized success response."""

    response = SuccessResponse(
        message=message,
        data=data,
        service_name=service_name,
        correlation_id=correlation_id or str(uuid.uuid4()),
    )

    return response.model_dump()


def create_error_response(
    message: str,
    error_code: ErrorCode = ErrorCode.INTERNAL_ERROR,
    error_details: Optional[Dict[str, Any]] = None,
    validation_errors: Optional[List[Dict[str, str]]] = None,
    service_name: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a standardized error response."""

    response = ErrorResponse(
        message=message,
        error_code=error_code,
        error_details=error_details,
        validation_errors=validation_errors,
        service_name=service_name,
        correlation_id=correlation_id or str(uuid.uuid4()),
    )

    return response.model_dump()


def create_validation_error_response(
    validation_errors: List[Dict[str, str]],
    message: str = "Validation failed",
    service_name: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a standardized validation error response."""

    return create_error_response(
        message=message,
        error_code=ErrorCode.VALIDATION_ERROR,
        validation_errors=validation_errors,
        service_name=service_name,
        correlation_id=correlation_id,
    )


def create_not_found_response(
    resource: str,
    resource_id: Optional[str] = None,
    service_name: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a standardized not found error response."""

    message = f"{resource} not found"
    if resource_id:
        message += f" (ID: {resource_id})"

    return create_error_response(
        message=message,
        error_code=ErrorCode.NOT_FOUND,
        service_name=service_name,
        correlation_id=correlation_id,
    )


def create_unauthorized_response(
    message: str = "Authentication required",
    service_name: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a standardized unauthorized error response."""

    return create_error_response(
        message=message,
        error_code=ErrorCode.UNAUTHORIZED,
        service_name=service_name,
        correlation_id=correlation_id,
    )


def create_forbidden_response(
    message: str = "Access denied",
    service_name: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a standardized forbidden error response."""

    return create_error_response(
        message=message,
        error_code=ErrorCode.FORBIDDEN,
        service_name=service_name,
        correlation_id=correlation_id,
    )


def create_constitutional_violation_response(
    violation_details: str,
    service_name: Optional[str] = None,
    correlation_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a standardized constitutional violation error response."""

    return create_error_response(
        message=f"Constitutional compliance violation: {violation_details}",
        error_code=ErrorCode.CONSTITUTIONAL_VIOLATION,
        error_details={
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "violation": violation_details,
        },
        service_name=service_name,
        correlation_id=correlation_id,
    )


def ensure_constitutional_compliance(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure response includes constitutional compliance hash."""

    if "constitutional_hash" not in response_data:
        response_data["constitutional_hash"] = CONSTITUTIONAL_HASH

    return response_data


# Health check models
class HealthStatus(str, Enum):
    """Health status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class DependencyHealth(BaseModel):
    """Health status of a service dependency."""

    name: str
    status: HealthStatus
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None


class HealthCheckResponse(BaseModel):
    """Standardized health check response."""

    status: HealthStatus
    service: str
    version: str
    port: int
    uptime_seconds: float
    constitutional_hash: str = CONSTITUTIONAL_HASH
    dependencies: Dict[str, str] = Field(default_factory=dict)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# Status models
class ServiceStatus(BaseModel):
    """Service status information."""

    api_version: str
    service: str
    status: str
    phase: str
    routers_available: bool
    endpoints: Dict[str, List[str]]
    capabilities: Dict[str, Any]
    constitutional_hash: str = CONSTITUTIONAL_HASH
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
