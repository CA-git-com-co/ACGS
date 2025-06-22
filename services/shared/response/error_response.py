"""
ACGS-1 Standardized Error Response Format

This module provides consistent error response formatting that integrates with
the unified response format. It ensures all error responses across ACGS services
follow the same structure and include actionable debugging information.

Error Response Format:
{
    "success": false,
    "error": {
        "code": "SERVICE_CATEGORY_NUMBER",
        "message": "Human-readable error message",
        "details": {},
        "timestamp": "ISO8601",
        "requestId": "UUID",
        "service": "service-name",
        "category": "ERROR_CATEGORY",
        "severity": "error|warning|critical|info",
        "retryable": boolean,
        "resolution_guidance": "How to fix this error"
    },
    "data": null,
    "metadata": {
        "timestamp": "ISO8601",
        "requestId": "UUID", 
        "version": "string",
        "service": "string"
    }
}
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict

from pydantic import BaseModel, Field
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

# Import unified response components
from .unified_response import (
    UnifiedResponse, 
    ResponseBuilder, 
    UnifiedJSONResponse,
    ResponseMetadata
)

# Import error catalog components
from ..errors.error_catalog import (
    ErrorDefinition,
    ErrorSeverity,
    ErrorCategory,
    ServiceCode,
    get_error_definition
)


@dataclass
class ErrorDetails:
    """Detailed error information for debugging and resolution."""
    code: str
    message: str
    details: Dict[str, Any]
    timestamp: str
    request_id: str
    service: str
    category: str
    severity: str
    retryable: bool
    resolution_guidance: str
    context: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "code": self.code,
            "message": self.message,
            "details": self.details,
            "timestamp": self.timestamp,
            "request_id": self.request_id,
            "service": self.service,
            "category": self.category,
            "severity": self.severity,
            "retryable": self.retryable,
            "resolution_guidance": self.resolution_guidance
        }
        
        if self.context:
            result["context"] = self.context
            
        return result


class ErrorResponse(BaseModel):
    """Standardized error response model."""
    success: bool = Field(False, description="Always false for error responses")
    error: ErrorDetails = Field(..., description="Detailed error information")
    data: Optional[Any] = Field(None, description="Always null for error responses")
    metadata: ResponseMetadata = Field(..., description="Response metadata")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ErrorDetails: lambda v: v.to_dict()
        }
        use_enum_values = True


class MultipleErrorResponse(BaseModel):
    """Response format for multiple errors (e.g., validation errors)."""
    success: bool = Field(False, description="Always false for error responses")
    errors: List[ErrorDetails] = Field(..., description="List of error details")
    data: Optional[Any] = Field(None, description="Always null for error responses")
    metadata: ResponseMetadata = Field(..., description="Response metadata")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ErrorDetails: lambda v: v.to_dict()
        }
        use_enum_values = True


class ErrorResponseBuilder:
    """Builder for creating standardized error responses."""
    
    def __init__(self, service_name: str, version: str = "1.0.0"):
        """Initialize error response builder."""
        self.service_name = service_name
        self.version = version
        self.request_id: Optional[str] = None
        self.request_context: Optional[Dict[str, Any]] = None
    
    def set_request_context(self, request: Request) -> "ErrorResponseBuilder":
        """Set request context for error tracking."""
        self.request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        self.request_context = {
            "method": request.method,
            "url": str(request.url),
            "user_agent": request.headers.get("User-Agent"),
            "ip_address": request.client.host if request.client else None
        }
        return self
    
    def _create_metadata(self) -> ResponseMetadata:
        """Create response metadata for error response."""
        from .unified_response import ResponseMetadata
        return ResponseMetadata(
            timestamp=datetime.now(timezone.utc).isoformat(),
            request_id=self.request_id or str(uuid.uuid4()),
            version=self.version,
            service=self.service_name
        )
    
    def from_error_code(
        self,
        error_code: str,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        override_message: Optional[str] = None
    ) -> ErrorResponse:
        """Create error response from error catalog code."""
        error_def = get_error_definition(error_code)
        
        if not error_def:
            # Fallback for unknown error codes
            return self.generic_error(
                message=f"Unknown error code: {error_code}",
                details=details or {},
                context=context
            )
        
        error_details = ErrorDetails(
            code=error_def.code,
            message=override_message or error_def.message,
            details=details or {},
            timestamp=datetime.now(timezone.utc).isoformat(),
            request_id=self.request_id or str(uuid.uuid4()),
            service=self.service_name,
            category=error_def.category.value,
            severity=error_def.severity.value,
            retryable=error_def.retryable,
            resolution_guidance=error_def.resolution_guidance,
            context=context
        )
        
        return ErrorResponse(
            error=error_details,
            metadata=self._create_metadata()
        )
    
    def validation_error(
        self,
        validation_errors: List[Dict[str, Any]],
        message: str = "Request validation failed"
    ) -> ErrorResponse:
        """Create validation error response."""
        return self.from_error_code(
            "SHARED_VALIDATION_002",
            details={"validation_errors": validation_errors},
            override_message=message
        )
    
    def authentication_error(
        self,
        reason: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ) -> ErrorResponse:
        """Create authentication error response."""
        return self.from_error_code(
            "AUTH_AUTHENTICATION_002",
            details=details or {"reason": reason},
            override_message=reason
        )
    
    def authorization_error(
        self,
        required_permission: str,
        user_role: Optional[str] = None
    ) -> ErrorResponse:
        """Create authorization error response."""
        return self.from_error_code(
            "AUTH_AUTHORIZATION_001",
            details={
                "required_permission": required_permission,
                "user_role": user_role
            }
        )
    
    def business_logic_error(
        self,
        error_code: str,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> ErrorResponse:
        """Create business logic error response."""
        return self.from_error_code(error_code, details, context)
    
    def external_service_error(
        self,
        service_name: str,
        error_details: str,
        retryable: bool = True
    ) -> ErrorResponse:
        """Create external service error response."""
        return self.from_error_code(
            "SHARED_SYSTEM_ERROR_002",
            details={
                "external_service": service_name,
                "error_details": error_details,
                "retryable": retryable
            }
        )
    
    def system_error(
        self,
        error_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> ErrorResponse:
        """Create system error response."""
        error_id = error_id or str(uuid.uuid4())
        return self.from_error_code(
            "SHARED_SYSTEM_ERROR_001",
            details=details or {},
            context={"error_id": error_id}
        )
    
    def generic_error(
        self,
        message: str,
        details: Dict[str, Any],
        http_status: int = 500,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        retryable: bool = False,
        context: Optional[Dict[str, Any]] = None
    ) -> ErrorResponse:
        """Create generic error response for unknown errors."""
        error_details = ErrorDetails(
            code="UNKNOWN_ERROR",
            message=message,
            details=details,
            timestamp=datetime.now(timezone.utc).isoformat(),
            request_id=self.request_id or str(uuid.uuid4()),
            service=self.service_name,
            category="SYSTEM_ERROR",
            severity=severity.value,
            retryable=retryable,
            resolution_guidance="Contact system administrator for assistance",
            context=context
        )
        
        return ErrorResponse(
            error=error_details,
            metadata=self._create_metadata()
        )
    
    def multiple_errors(
        self,
        errors: List[Dict[str, Any]],
        primary_message: str = "Multiple errors occurred"
    ) -> MultipleErrorResponse:
        """Create response for multiple errors."""
        error_details_list = []
        
        for error_info in errors:
            error_code = error_info.get("code", "UNKNOWN_ERROR")
            error_def = get_error_definition(error_code)
            
            if error_def:
                error_details = ErrorDetails(
                    code=error_def.code,
                    message=error_info.get("message", error_def.message),
                    details=error_info.get("details", {}),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    request_id=self.request_id or str(uuid.uuid4()),
                    service=self.service_name,
                    category=error_def.category.value,
                    severity=error_def.severity.value,
                    retryable=error_def.retryable,
                    resolution_guidance=error_def.resolution_guidance,
                    context=error_info.get("context")
                )
            else:
                error_details = ErrorDetails(
                    code=error_code,
                    message=error_info.get("message", "Unknown error"),
                    details=error_info.get("details", {}),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    request_id=self.request_id or str(uuid.uuid4()),
                    service=self.service_name,
                    category="SYSTEM_ERROR",
                    severity="error",
                    retryable=False,
                    resolution_guidance="Contact system administrator",
                    context=error_info.get("context")
                )
            
            error_details_list.append(error_details)
        
        return MultipleErrorResponse(
            errors=error_details_list,
            metadata=self._create_metadata()
        )


class ErrorJSONResponse(UnifiedJSONResponse):
    """JSON response class for error responses."""
    
    def __init__(
        self,
        error_response: Union[ErrorResponse, MultipleErrorResponse],
        status_code: int = 500,
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize error JSON response."""
        
        # Determine status code from error if not provided
        if status_code == 500 and hasattr(error_response, 'error'):
            error_def = get_error_definition(error_response.error.code)
            if error_def:
                status_code = error_def.http_status
        
        # Add error-specific headers
        error_headers = {
            "X-Error-Code": getattr(error_response, 'error', {}).code if hasattr(error_response, 'error') else "UNKNOWN",
            "X-Error-Severity": getattr(error_response, 'error', {}).severity if hasattr(error_response, 'error') else "error"
        }
        
        if headers:
            error_headers.update(headers)
        
        super().__init__(
            content=error_response,
            status_code=status_code,
            headers=error_headers
        )


# Service-specific error response builders
def create_auth_error_builder() -> ErrorResponseBuilder:
    """Create error response builder for Authentication Service."""
    return ErrorResponseBuilder("authentication-service", "2.1.0")


def create_ac_error_builder() -> ErrorResponseBuilder:
    """Create error response builder for Constitutional AI Service."""
    return ErrorResponseBuilder("constitutional-ai-service", "2.1.0")


def create_integrity_error_builder() -> ErrorResponseBuilder:
    """Create error response builder for Integrity Service."""
    return ErrorResponseBuilder("integrity-service", "2.0.0")


def create_fv_error_builder() -> ErrorResponseBuilder:
    """Create error response builder for Formal Verification Service."""
    return ErrorResponseBuilder("formal-verification-service", "1.5.0")


def create_gs_error_builder() -> ErrorResponseBuilder:
    """Create error response builder for Governance Synthesis Service."""
    return ErrorResponseBuilder("governance-synthesis-service", "2.2.0")


def create_pgc_error_builder() -> ErrorResponseBuilder:
    """Create error response builder for Policy Governance Service."""
    return ErrorResponseBuilder("policy-governance-service", "2.0.0")


def create_ec_error_builder() -> ErrorResponseBuilder:
    """Create error response builder for Evolutionary Computation Service."""
    return ErrorResponseBuilder("evolutionary-computation-service", "1.8.0")


def create_dgm_error_builder() -> ErrorResponseBuilder:
    """Create error response builder for Darwin Gödel Machine Service."""
    return ErrorResponseBuilder("darwin-godel-machine-service", "1.0.0")


# FastAPI dependency for error response building
async def get_error_response_builder(request: Request) -> ErrorResponseBuilder:
    """FastAPI dependency to get error response builder with request context."""
    
    # Map service paths to service names
    path_service_mapping = {
        "/auth/": "authentication-service",
        "/api/v1/constitutional/": "constitutional-ai-service",
        "/api/v1/integrity/": "integrity-service",
        "/api/v1/verification/": "formal-verification-service",
        "/api/v1/synthesis/": "governance-synthesis-service",
        "/api/v1/enforcement/": "policy-governance-service",
        "/api/v1/evolution/": "evolutionary-computation-service",
        "/api/v1/dgm/": "darwin-godel-machine-service"
    }
    
    service_name = "unknown-service"
    for path_prefix, mapped_service in path_service_mapping.items():
        if request.url.path.startswith(path_prefix):
            service_name = mapped_service
            break
    
    builder = ErrorResponseBuilder(service_name)
    builder.set_request_context(request)
    return builder


# Utility functions for common error scenarios
def create_http_exception_error_response(
    exc: HTTPException,
    service_name: str,
    request_id: Optional[str] = None
) -> ErrorJSONResponse:
    """Create error response from HTTPException."""
    builder = ErrorResponseBuilder(service_name)
    if request_id:
        builder.request_id = request_id
    
    # Map HTTP status to appropriate error code
    status_code_mapping = {
        400: "SHARED_VALIDATION_001",
        401: "AUTH_AUTHENTICATION_001", 
        403: "AUTH_AUTHORIZATION_001",
        404: "SHARED_VALIDATION_001",
        422: "SHARED_VALIDATION_002",
        500: "SHARED_SYSTEM_ERROR_001",
        503: "SHARED_SYSTEM_ERROR_002"
    }
    
    error_code = status_code_mapping.get(exc.status_code, "SHARED_SYSTEM_ERROR_001")
    
    error_response = builder.from_error_code(
        error_code,
        details={"http_exception": True, "original_detail": exc.detail},
        override_message=str(exc.detail)
    )
    
    return ErrorJSONResponse(error_response, status_code=exc.status_code)


# Export main classes and functions
__all__ = [
    "ErrorDetails",
    "ErrorResponse", 
    "MultipleErrorResponse",
    "ErrorResponseBuilder",
    "ErrorJSONResponse",
    "get_error_response_builder",
    "create_auth_error_builder",
    "create_ac_error_builder",
    "create_integrity_error_builder",
    "create_fv_error_builder",
    "create_gs_error_builder",
    "create_pgc_error_builder",
    "create_ec_error_builder",
    "create_dgm_error_builder",
    "create_http_exception_error_response"
]
