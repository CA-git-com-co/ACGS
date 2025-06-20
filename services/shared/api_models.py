"""
ACGS-1 Phase A3: Standardized API Models and Response Structures

This module provides standardized API response structures, error handling,
and common Pydantic models for all ACGS-1 services to ensure consistency
and production-grade API implementation.
"""

import uuid
from datetime import timezone, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


class APIStatus(str, Enum):
    """Standard API response status values."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PARTIAL = "partial"


class ErrorCode(str, Enum):
    """Standard error codes for consistent error handling."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    CONSTITUTIONAL_VIOLATION = "CONSTITUTIONAL_VIOLATION"
    POLICY_VIOLATION = "POLICY_VIOLATION"


class APIError(BaseModel):
    """Standardized error structure for API responses."""

    code: ErrorCode
    message: str
    details: dict[str, Any] | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str | None = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class APIMetadata(BaseModel):
    """Metadata for API responses including performance and tracing information."""

    correlation_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    response_time_ms: float | None = None
    service_name: str
    service_version: str = "3.0.0"
    api_version: str = "v1"
    request_id: str | None = None

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class APIResponse(BaseModel):
    """
    Standardized API response structure for all ACGS-1 services.

    This ensures consistent response format across all services and
    provides proper error handling, metadata, and performance tracking.
    """

    status: APIStatus
    data: dict[str, Any] | list[Any] | str | int | bool | None = None
    error: APIError | None = None
    metadata: APIMetadata

    @validator("error")
    def error_required_for_error_status(cls, v, values):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Ensure error is provided when status is error."""
        if values.get("status") == APIStatus.ERROR and v is None:
            raise ValueError("Error details required when status is error")
        return v

    @validator("data")
    def data_required_for_success_status(cls, v, values):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Ensure data is provided when status is success."""
        if values.get("status") == APIStatus.SUCCESS and v is None:
            # Allow empty data for success responses
            return {}
        return v


class HealthCheckResponse(BaseModel):
    """Standardized health check response for all services."""

    status: str = "healthy"
    service: str
    version: str = "3.0.0"
    port: int
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    uptime_seconds: float | None = None
    dependencies: dict[str, str] = Field(default_factory=dict)
    performance_metrics: dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class ServiceInfo(BaseModel):
    """Service information for root endpoints."""

    service: str
    version: str = "3.0.0"
    status: str = "operational"
    port: int
    phase: str = "Phase A3 - Production Implementation"
    capabilities: list[str] = Field(default_factory=list)
    api_documentation: str = "/docs"
    health_check: str = "/health"


class PaginationParams(BaseModel):
    """Standard pagination parameters."""

    page: int = Field(1, ge=1, description="Page number (1-based)")
    size: int = Field(20, ge=1, le=100, description="Items per page")
    sort_by: str | None = Field(None, description="Field to sort by")
    sort_order: str = Field("asc", pattern="^(asc|desc)$", description="Sort order")


class PaginatedResponse(BaseModel):
    """Standardized paginated response structure."""

    items: list[Any]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool

    @validator("pages", pre=True, always=True)
    def calculate_pages(cls, v, values):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Calculate total pages based on total items and page size."""
        total = values.get("total", 0)
        size = values.get("size", 20)
        return max(1, (total + size - 1) // size)

    @validator("has_next", pre=True, always=True)
    def calculate_has_next(cls, v, values):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Calculate if there's a next page."""
        page = values.get("page", 1)
        pages = values.get("pages", 1)
        return page < pages

    @validator("has_prev", pre=True, always=True)
    def calculate_has_prev(cls, v, values):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Calculate if there's a previous page."""
        page = values.get("page", 1)
        return page > 1


class ConstitutionalComplianceInfo(BaseModel):
    """Constitutional compliance information for governance-related responses."""

    is_compliant: bool
    compliance_score: float = Field(ge=0.0, le=1.0)
    violations: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    validation_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PerformanceMetrics(BaseModel):
    """Performance metrics for API responses."""

    response_time_ms: float
    cpu_usage_percent: float | None = None
    memory_usage_mb: float | None = None
    database_query_time_ms: float | None = None
    cache_hit_rate: float | None = None


# Common validation schemas
class IDParam(BaseModel):
    """Standard ID parameter validation."""

    id: int | str = Field(..., description="Resource identifier")


class TimestampRange(BaseModel):
    """Standard timestamp range for filtering."""

    start: datetime | None = Field(None, description="Start timestamp")
    end: datetime | None = Field(None, description="End timestamp")

    @validator("end")
    def end_after_start(cls, v, values):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Ensure end timestamp is after start timestamp."""
        start = values.get("start")
        if start and v and v <= start:
            raise ValueError("End timestamp must be after start timestamp")
        return v


def create_success_response(
    data: Any,
    service_name: str,
    correlation_id: str | None = None,
    response_time_ms: float | None = None,
) -> APIResponse:
    """Helper function to create standardized success responses."""
    metadata = APIMetadata(
        service_name=service_name,
        correlation_id=correlation_id or str(uuid.uuid4()),
        response_time_ms=response_time_ms,
    )

    return APIResponse(status=APIStatus.SUCCESS, data=data, metadata=metadata)


def create_error_response(
    error_code: ErrorCode,
    message: str,
    service_name: str,
    details: dict[str, Any] | None = None,
    correlation_id: str | None = None,
    response_time_ms: float | None = None,
) -> APIResponse:
    """Helper function to create standardized error responses."""
    metadata = APIMetadata(
        service_name=service_name,
        correlation_id=correlation_id or str(uuid.uuid4()),
        response_time_ms=response_time_ms,
    )

    error = APIError(
        code=error_code,
        message=message,
        details=details,
        correlation_id=metadata.correlation_id,
    )

    return APIResponse(status=APIStatus.ERROR, error=error, metadata=metadata)
