"""
ACGS FastAPI Service Schemas Template
Constitutional Hash: cdd01ef066bc6cf2

This module provides standardized Pydantic schemas for ACGS services including:
- Base response models with constitutional compliance
- Common request/response patterns
- Pagination and filtering models
- Error response standardization
- Multi-tenant aware schemas
"""

import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, field_validator

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Type variable for generic responses
DataType = TypeVar("DataType")


class ResponseStatus(str, Enum):
    """Standard response status values."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PARTIAL = "partial"


class ConstitutionalBaseModel(BaseModel):
    """
    Base model with constitutional compliance built-in.

    All ACGS API models should inherit from this base class to ensure
    constitutional compliance is maintained throughout the system.
    """

    constitutional_hash: str = Field(
        default=CONSTITUTIONAL_HASH,
        description="Constitutional compliance hash for ACGS governance",
        example=CONSTITUTIONAL_HASH,
    )

    model_config = ConfigDict(
        # Allow population by field name and alias
        validate_by_name=True,
        # Use enum values instead of names
        use_enum_values=True,
        # Validate assignment to ensure constitutional compliance
        validate_assignment=True,
        # JSON schema customization
        json_schema_extra={"example": {"constitutional_hash": CONSTITUTIONAL_HASH}},
    )


class APIResponse(ConstitutionalBaseModel, Generic[DataType]):
    """
    Standardized API response wrapper with constitutional compliance.

    This generic response model ensures consistent response format across
    all ACGS services while maintaining constitutional compliance.
    """

    status: ResponseStatus = Field(
        description="Response status indicator", example=ResponseStatus.SUCCESS
    )

    message: str | None = Field(
        None,
        description="Human-readable response message",
        example="Operation completed successfully",
    )

    data: DataType | None = Field(None, description="Response payload data")

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Response timestamp in UTC",
        example="2024-01-01T12:00:00Z",
    )

    request_id: str | None = Field(
        None,
        description="Unique request identifier for tracing",
        example="req_123456789",
    )

    service_name: str | None = Field(
        None,
        description="Name of the service that generated this response",
        example="constitutional-core",
    )


class SuccessResponse(APIResponse[DataType]):
    """Convenience class for successful responses."""

    status: ResponseStatus = ResponseStatus.SUCCESS


class ErrorResponse(APIResponse[None]):
    """
    Standardized error response model.

    This model provides consistent error reporting across all ACGS services
    with constitutional compliance and detailed error information.
    """

    status: ResponseStatus = ResponseStatus.ERROR

    error_code: str | None = Field(
        None, description="Machine-readable error code", example="VALIDATION_ERROR"
    )

    error_details: dict[str, Any] | None = Field(
        None, description="Additional error context and details"
    )

    trace_id: str | None = Field(
        None,
        description="Unique trace identifier for debugging",
        example="trace_987654321",
    )


class PaginationParams(BaseModel):
    """Standardized pagination parameters."""

    page: int = Field(default=1, ge=1, description="Page number (1-based)", example=1)

    page_size: int = Field(
        default=20, ge=1, le=100, description="Number of items per page", example=20
    )

    @property
    def offset(self) -> int:
        """Calculate offset for database queries."""
        return (self.page - 1) * self.page_size


class PaginationMeta(BaseModel):
    """Pagination metadata for responses."""

    page: int = Field(description="Current page number")
    page_size: int = Field(description="Items per page")
    total_items: int = Field(description="Total number of items")
    total_pages: int = Field(description="Total number of pages")
    has_next: bool = Field(description="Whether there are more pages")
    has_previous: bool = Field(description="Whether there are previous pages")


class PaginatedResponse(APIResponse[list[DataType]]):
    """Response model for paginated data with metadata."""

    pagination: PaginationMeta = Field(description="Pagination metadata")


class FilterParams(BaseModel):
    """Base class for filtering parameters."""

    search: str | None = Field(
        None, description="General search term", min_length=1, max_length=100
    )

    sort_by: str | None = Field(
        None, description="Field to sort by", example="created_at"
    )

    sort_order: str | None = Field(
        default="desc",
        pattern="^(asc|desc)$",
        description="Sort order: asc or desc",
        example="desc",
    )


class TenantAwareModel(ConstitutionalBaseModel):
    """
    Base model for tenant-aware resources.

    This model includes tenant identification and is used for all
    resources that belong to a specific tenant in the multi-tenant system.
    """

    tenant_id: uuid.UUID = Field(
        description="Tenant identifier for multi-tenant isolation",
        example="123e4567-e89b-12d3-a456-426614174000",
    )


class UserContextModel(BaseModel):
    """Model representing user context in requests."""

    user_id: int | None = Field(None, description="User identifier", example=12345)

    is_admin: bool = Field(
        default=False, description="Whether user has admin privileges"
    )

    roles: list[str] = Field(
        default_factory=list,
        description="User roles and permissions",
        example=["user", "tenant_admin"],
    )


class HealthCheckResponse(ConstitutionalBaseModel):
    """Standardized health check response model."""

    status: str = Field(description="Overall health status", example="healthy")

    service: str = Field(description="Service name", example="constitutional-core")

    version: str = Field(description="Service version", example="1.0.0")

    constitutional_compliance: str = Field(
        default="verified",
        description="Constitutional compliance status",
        example="verified",
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="Health check timestamp"
    )

    uptime_seconds: float = Field(
        description="Service uptime in seconds", example=3600.0
    )

    environment: str = Field(description="Deployment environment", example="production")

    components: dict[str, str] = Field(
        default_factory=dict,
        description="Component health status",
        example={"database": "healthy", "redis": "healthy", "external_api": "healthy"},
    )


class ConstitutionalValidationRequest(ConstitutionalBaseModel):
    """Request model for constitutional validation operations."""

    content: str = Field(
        description="Content to validate for constitutional compliance",
        min_length=1,
        max_length=10000,
    )

    context: dict[str, Any] | None = Field(
        default_factory=dict, description="Additional context for validation"
    )

    validation_level: str = Field(
        default="standard",
        pattern="^(basic|standard|strict|maximum)$",
        description="Level of constitutional validation to perform",
    )


class ConstitutionalValidationResponse(ConstitutionalBaseModel):
    """Response model for constitutional validation operations."""

    compliant: bool = Field(
        description="Whether content meets constitutional requirements"
    )

    compliance_score: float = Field(
        ge=0.0, le=1.0, description="Constitutional compliance score (0.0 to 1.0)"
    )

    violations: list[str] = Field(
        default_factory=list, description="List of constitutional violations found"
    )

    recommendations: list[str] = Field(
        default_factory=list, description="Recommendations for improving compliance"
    )

    validation_timestamp: datetime = Field(
        default_factory=datetime.utcnow, description="When validation was performed"
    )


class TenantInfo(TenantAwareModel):
    """Tenant information model for responses."""

    id: uuid.UUID = Field(description="Tenant unique identifier")

    name: str = Field(description="Tenant display name", min_length=1, max_length=255)

    status: str = Field(description="Tenant status", example="active")

    security_level: str = Field(
        description="Security level for this tenant", example="standard"
    )

    constitutional_compliance_score: float = Field(
        ge=0.0, le=100.0, description="Tenant's constitutional compliance score"
    )

    created_at: datetime = Field(description="Tenant creation timestamp")

    updated_at: datetime = Field(description="Last update timestamp")


# Validation utilities
def validate_constitutional_hash(cls, v):
    """Validator for constitutional hash fields."""
    if v != CONSTITUTIONAL_HASH:
        raise ValueError(
            f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}"
        )
    return v


def validate_uuid_string(cls, v):
    """Validator for UUID string fields."""
    if isinstance(v, str):
        try:
            return uuid.UUID(v)
        except ValueError:
            raise ValueError("Invalid UUID format")
    return v


# Example usage patterns for service-specific schemas
class ExampleCreateRequest(TenantAwareModel):
    """Example of a service-specific create request model."""

    name: str = Field(
        description="Resource name",
        min_length=1,
        max_length=255,
        example="Example Resource",
    )

    description: str | None = Field(
        None, description="Resource description", max_length=1000
    )

    metadata: dict[str, Any] | None = Field(
        default_factory=dict, description="Additional metadata"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v):
        """Custom validation for name field."""
        if not v.strip():
            raise ValueError("Name cannot be empty or whitespace only")
        return v.strip()


class ExampleResponse(TenantAwareModel):
    """Example of a service-specific response model."""

    id: uuid.UUID = Field(description="Resource unique identifier")

    name: str = Field(description="Resource name")

    description: str | None = Field(None, description="Resource description")

    status: str = Field(description="Resource status", example="active")

    created_at: datetime = Field(description="Creation timestamp")

    updated_at: datetime = Field(description="Last update timestamp")

    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata"
    )


# Export commonly used response types
SuccessResponseWithData = SuccessResponse[DataType]
PaginatedSuccessResponse = PaginatedResponse[DataType]
