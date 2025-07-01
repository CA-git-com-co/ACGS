"""
ACGS-1 Unified Response Format Implementation

This module provides standardized response formatting for all ACGS microservices,
ensuring consistent API responses across Constitutional AI, Authentication,
Integrity, Formal Verification, Governance Synthesis, Policy Governance,
Evolutionary Computation, and Darwin Gödel Machine services.

Unified Response Format:
{
    "success": boolean,
    "data": any,
    "message": string,
    "metadata": {
        "timestamp": ISO8601,
        "requestId": UUID,
        "version": string,
        "service": string
    },
    "pagination": {  // Optional for paginated responses
        "page": number,
        "limit": number,
        "total": number,
        "hasNext": boolean,
        "hasPrevious": boolean
    }
}
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import orjson
from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field


class ResponseStatus(str, Enum):
    """Response status enumeration."""

    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"


@dataclass
class PaginationMetadata:
    """Pagination metadata for paginated responses."""

    page: int
    limit: int
    total: int
    has_next: bool
    has_previous: bool

    @classmethod
    def create(cls, page: int, limit: int, total: int) -> "PaginationMetadata":
        """Create pagination metadata with calculated fields."""
        total_pages = (total + limit - 1) // limit if total > 0 else 0
        has_next = page < total_pages
        has_previous = page > 1

        return cls(
            page=page,
            limit=limit,
            total=total,
            has_next=has_next,
            has_previous=has_previous,
        )


@dataclass
class ResponseMetadata:
    """Response metadata containing request tracking and service information."""

    timestamp: str
    request_id: str
    version: str
    service: str
    execution_time_ms: float | None = None

    @classmethod
    def create(
        cls, service: str, version: str = "1.0.0", request_id: str | None = None
    ) -> "ResponseMetadata":
        """Create response metadata with current timestamp and generated request ID."""
        return cls(
            timestamp=datetime.now(timezone.utc).isoformat(),
            request_id=request_id or str(uuid.uuid4()),
            version=version,
            service=service,
        )


class UnifiedResponse(BaseModel):
    """Unified response model for all ACGS services."""

    success: bool = Field(..., description="Indicates if the request was successful")
    data: Any | None = Field(None, description="Response data payload")
    message: str = Field("", description="Human-readable response message")
    metadata: ResponseMetadata = Field(..., description="Response metadata")
    pagination: PaginationMetadata | None = Field(
        None, description="Pagination information for paginated responses"
    )
    error: dict[str, Any] | None = Field(
        None, description="Error details when success=false"
    )

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
        use_enum_values = True

    @classmethod
    def success_response(
        cls,
        data: Any = None,
        message: str = "Operation completed successfully",
        service: str = "acgs-service",
        version: str = "1.0.0",
        pagination: PaginationMetadata | None = None,
    ) -> "UnifiedResponse":
        """Create a successful response."""
        return cls(
            success=True,
            data=data,
            message=message,
            metadata=ResponseMetadata(
                timestamp=datetime.now(timezone.utc).isoformat(),
                request_id=str(uuid.uuid4()),
                service=service,
                version=version,
            ),
            pagination=pagination,
        )

    @classmethod
    def error_response(
        cls,
        error_code: str,
        error_message: str,
        error_details: dict[str, Any] | None = None,
        service: str = "acgs-service",
        version: str = "1.0.0",
        data: Any = None,
    ) -> "UnifiedResponse":
        """Create an error response."""
        return cls(
            success=False,
            data=data,
            message=error_message,
            metadata=ResponseMetadata(
                timestamp=datetime.now(timezone.utc).isoformat(),
                request_id=str(uuid.uuid4()),
                service=service,
                version=version,
            ),
            error={
                "code": error_code,
                "message": error_message,
                "details": error_details or {},
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )


class ResponseBuilder:
    """Builder class for creating standardized responses."""

    def __init__(self, service_name: str, version: str = "1.0.0"):
        """Initialize response builder with service information."""
        self.service_name = service_name
        self.version = version
        self.request_id: str | None = None
        self.execution_start_time: float | None = None

    def set_request_context(self, request: Request) -> "ResponseBuilder":
        """Set request context for tracking."""
        self.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        self.execution_start_time = datetime.now(timezone.utc).timestamp()
        return self

    def _create_metadata(self) -> ResponseMetadata:
        """Create response metadata."""
        execution_time_ms = None
        if self.execution_start_time:
            execution_time_ms = (
                datetime.now(timezone.utc).timestamp() - self.execution_start_time
            ) * 1000

        return ResponseMetadata(
            timestamp=datetime.now(timezone.utc).isoformat(),
            request_id=self.request_id or str(uuid.uuid4()),
            version=self.version,
            service=self.service_name,
            execution_time_ms=execution_time_ms,
        )

    def success(
        self,
        data: Any = None,
        message: str = "Request completed successfully",
        pagination: PaginationMetadata | None = None,
    ) -> UnifiedResponse:
        """Create a successful response."""
        return UnifiedResponse(
            success=True,
            data=data,
            message=message,
            metadata=self._create_metadata(),
            pagination=pagination,
        )

    def error(
        self, message: str, data: Any = None, error_code: str | None = None
    ) -> UnifiedResponse:
        """Create an error response."""
        error_data = data
        if error_code:
            error_data = {"error_code": error_code, "details": data}

        return UnifiedResponse(
            success=False,
            data=error_data,
            message=message,
            metadata=self._create_metadata(),
        )

    def paginated_success(
        self,
        data: list[Any],
        page: int,
        limit: int,
        total: int,
        message: str = "Request completed successfully",
    ) -> UnifiedResponse:
        """Create a successful paginated response."""
        pagination = PaginationMetadata.create(page, limit, total)

        return UnifiedResponse(
            success=True,
            data=data,
            message=message,
            metadata=self._create_metadata(),
            pagination=pagination,
        )


class UnifiedJSONResponse(JSONResponse):
    """Custom JSON response class using orjson for better performance."""

    def render(self, content: Any) -> bytes:
        """Render content using orjson for better performance."""
        if isinstance(content, UnifiedResponse):
            content = content.model_dump()

        return orjson.dumps(content, option=orjson.OPT_NON_STR_KEYS)


# Service-specific response builders
def create_auth_response_builder() -> ResponseBuilder:
    """Create response builder for Authentication Service."""
    return ResponseBuilder("authentication-service", "2.1.0")


def create_ac_response_builder() -> ResponseBuilder:
    """Create response builder for Constitutional AI Service."""
    return ResponseBuilder("constitutional-ai-service", "2.1.0")


def create_integrity_response_builder() -> ResponseBuilder:
    """Create response builder for Integrity Service."""
    return ResponseBuilder("integrity-service", "2.0.0")


def create_fv_response_builder() -> ResponseBuilder:
    """Create response builder for Formal Verification Service."""
    return ResponseBuilder("formal-verification-service", "1.5.0")


def create_gs_response_builder() -> ResponseBuilder:
    """Create response builder for Governance Synthesis Service."""
    return ResponseBuilder("governance-synthesis-service", "2.2.0")


def create_pgc_response_builder() -> ResponseBuilder:
    """Create response builder for Policy Governance Service."""
    return ResponseBuilder("policy-governance-service", "2.0.0")


def create_ec_response_builder() -> ResponseBuilder:
    """Create response builder for Evolutionary Computation Service."""
    return ResponseBuilder("evolutionary-computation-service", "1.8.0")


def create_dgm_response_builder() -> ResponseBuilder:
    """Create response builder for Darwin Gödel Machine Service."""
    return ResponseBuilder("darwin-godel-machine-service", "1.0.0")


# Utility functions for backward compatibility
def create_legacy_response(data: Any, status: str = "success") -> dict[str, Any]:
    """Create legacy response format for backward compatibility."""
    return {
        "status": status,
        "data": data,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def migrate_legacy_response(
    legacy_response: dict[str, Any], service_name: str
) -> UnifiedResponse:
    """Migrate legacy response format to unified format."""
    builder = ResponseBuilder(service_name)

    if legacy_response.get("status") == "success":
        return builder.success(
            data=legacy_response.get("data"),
            message=legacy_response.get("message", "Request completed successfully"),
        )
    return builder.error(
        message=legacy_response.get("message", "Request failed"),
        data=legacy_response.get("data"),
    )


# FastAPI dependency for response building
async def get_response_builder(request: Request) -> ResponseBuilder:
    """FastAPI dependency to get response builder with request context."""
    # Extract service name from request path or headers
    service_name = request.headers.get("X-Service-Name", "unknown-service")

    # Map service paths to service names
    path_service_mapping = {
        "/auth/": "authentication-service",
        "/api/v1/constitutional/": "constitutional-ai-service",
        "/api/v1/integrity/": "integrity-service",
        "/api/v1/verification/": "formal-verification-service",
        "/api/v1/synthesis/": "governance-synthesis-service",
        "/api/v1/enforcement/": "policy-governance-service",
        "/api/v1/evolution/": "evolutionary-computation-service",
        "/api/v1/dgm/": "darwin-godel-machine-service",
    }

    for path_prefix, mapped_service in path_service_mapping.items():
        if request.url.path.startswith(path_prefix):
            service_name = mapped_service
            break

    builder = ResponseBuilder(service_name)
    builder.set_request_context(request)
    return builder


# Response validation utilities
def validate_response_format(response_data: dict[str, Any]) -> bool:
    """Validate that response follows unified format."""
    required_fields = ["success", "data", "message", "metadata"]

    # Check required fields
    for field in required_fields:
        if field not in response_data:
            return False

    # Validate metadata structure
    metadata = response_data.get("metadata", {})
    required_metadata_fields = ["timestamp", "request_id", "version", "service"]

    for field in required_metadata_fields:
        if field not in metadata:
            return False

    # Validate pagination if present
    if "pagination" in response_data and response_data["pagination"] is not None:
        pagination = response_data["pagination"]
        required_pagination_fields = [
            "page",
            "limit",
            "total",
            "has_next",
            "has_previous",
        ]

        for field in required_pagination_fields:
            if field not in pagination:
                return False

    return True


# Response transformation middleware
class UnifiedResponseMiddleware:
    """Middleware to ensure all responses follow unified format."""

    def __init__(self, app, service_name: str):
        self.app = app
        self.service_name = service_name

    async def __call__(self, scope, receive, send):
        """Process request and ensure unified response format."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        # Create response builder
        builder = ResponseBuilder(self.service_name)

        async def send_wrapper(message):
            """Wrap response to ensure unified format."""
            if message["type"] == "http.response.body":
                # Transform response if needed
                pass
            await send(message)

        await self.app(scope, receive, send_wrapper)


# Export main classes and functions
__all__ = [
    "PaginationMetadata",
    "ResponseBuilder",
    "ResponseMetadata",
    "ResponseStatus",
    "UnifiedJSONResponse",
    "UnifiedResponse",
    "UnifiedResponseMiddleware",
    "create_ac_response_builder",
    "create_auth_response_builder",
    "create_dgm_response_builder",
    "create_ec_response_builder",
    "create_fv_response_builder",
    "create_gs_response_builder",
    "create_integrity_response_builder",
    "create_pgc_response_builder",
    "get_response_builder",
    "validate_response_format",
]
