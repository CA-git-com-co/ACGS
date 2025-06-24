"""
Standardized Error Handling Middleware for ACGS Services

This module provides comprehensive error handling middleware that can be used
across all ACGS services to ensure consistent error responses and proper logging.
"""

import logging
import time
import traceback
import uuid
from typing import Any, Dict

from fastapi import HTTPException, Request, Response, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger(__name__)


class StandardErrorResponse:
    """Standard error response structure for all ACGS services."""
    
    def __init__(
        self,
        error_code: str,
        message: str,
        details: str | None = None,
        timestamp: str | None = None,
        request_id: str | None = None,
        service: str | None = None,
    ):
        self.error_code = error_code
        self.message = message
        self.details = details
        self.timestamp = timestamp or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.request_id = request_id
        self.service = service
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON response."""
        response = {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "timestamp": self.timestamp,
            }
        }
        
        if self.details:
            response["error"]["details"] = self.details
        
        if self.request_id:
            response["error"]["request_id"] = self.request_id
            
        if self.service:
            response["error"]["service"] = self.service
            
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Comprehensive error handling middleware for ACGS services."""
    
    def __init__(self, app, service_name: str = "acgs-service"):
        super().__init__(app)
        self.service_name = service_name
    
    async def dispatch(self, request: Request, call_next):
        """Process request and handle any errors that occur."""
        # Generate unique request ID for tracing
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Add request ID to response headers
        start_time = time.time()
        
        try:
            response = await call_next(request)
            
            # Add request tracking headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Response-Time"] = str(int((time.time() - start_time) * 1000))
            
            return response
            
        except Exception as exc:
            # Log the error with context
            processing_time = int((time.time() - start_time) * 1000)
            
            logger.error(
                f"Request failed: {request.method} {request.url.path} "
                f"[{request_id}] - {str(exc)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "url": str(request.url),
                    "processing_time_ms": processing_time,
                    "service": self.service_name,
                    "error": str(exc),
                    "traceback": traceback.format_exc(),
                }
            )
            
            # Handle different types of exceptions
            if isinstance(exc, ValidationError):
                error_response = StandardErrorResponse(
                    error_code="VALIDATION_ERROR",
                    message="Request validation failed",
                    details=str(exc),
                    request_id=request_id,
                    service=self.service_name,
                )
                return JSONResponse(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    content=error_response.to_dict(),
                    headers={"X-Request-ID": request_id}
                )
            
            elif isinstance(exc, HTTPException):
                error_response = StandardErrorResponse(
                    error_code=f"HTTP_{exc.status_code}",
                    message=exc.detail,
                    request_id=request_id,
                    service=self.service_name,
                )
                return JSONResponse(
                    status_code=exc.status_code,
                    content=error_response.to_dict(),
                    headers={"X-Request-ID": request_id}
                )
            
            elif isinstance(exc, KeyError):
                error_response = StandardErrorResponse(
                    error_code="MISSING_FIELD",
                    message="Required field missing from request",
                    details=f"Missing field: {str(exc)}",
                    request_id=request_id,
                    service=self.service_name,
                )
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=error_response.to_dict(),
                    headers={"X-Request-ID": request_id}
                )
            
            elif isinstance(exc, ValueError):
                error_response = StandardErrorResponse(
                    error_code="INVALID_VALUE",
                    message="Invalid value provided in request",
                    details=str(exc),
                    request_id=request_id,
                    service=self.service_name,
                )
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content=error_response.to_dict(),
                    headers={"X-Request-ID": request_id}
                )
            
            elif isinstance(exc, ConnectionError):
                error_response = StandardErrorResponse(
                    error_code="SERVICE_UNAVAILABLE",
                    message="External service unavailable",
                    details="Unable to connect to required service",
                    request_id=request_id,
                    service=self.service_name,
                )
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content=error_response.to_dict(),
                    headers={"X-Request-ID": request_id}
                )
            
            elif isinstance(exc, TimeoutError):
                error_response = StandardErrorResponse(
                    error_code="REQUEST_TIMEOUT",
                    message="Request processing timeout",
                    details="The request took too long to process",
                    request_id=request_id,
                    service=self.service_name,
                )
                return JSONResponse(
                    status_code=status.HTTP_408_REQUEST_TIMEOUT,
                    content=error_response.to_dict(),
                    headers={"X-Request-ID": request_id}
                )
            
            else:
                # Generic internal server error
                error_response = StandardErrorResponse(
                    error_code="INTERNAL_ERROR",
                    message="An internal server error occurred",
                    details="Please contact system administrator if the problem persists",
                    request_id=request_id,
                    service=self.service_name,
                )
                return JSONResponse(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    content=error_response.to_dict(),
                    headers={"X-Request-ID": request_id}
                )


def setup_error_handlers(app, service_name: str = "acgs-service"):
    """
    Set up comprehensive error handling for a FastAPI application.
    
    Args:
        app: FastAPI application instance
        service_name: Name of the service for logging and identification
    """
    
    # Add error handling middleware
    app.add_middleware(ErrorHandlingMiddleware, service_name=service_name)
    
    # Custom exception handlers
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        """Handle Pydantic validation errors."""
        request_id = getattr(request.state, "request_id", "unknown")
        
        error_response = StandardErrorResponse(
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            details=str(exc),
            request_id=request_id,
            service=service_name,
        )
        
        logger.warning(
            f"Validation error: {str(exc)}",
            extra={
                "request_id": request_id,
                "error_type": "validation",
                "service": service_name,
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.to_dict(),
            headers={"X-Request-ID": request_id}
        )
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler_custom(request: Request, exc: HTTPException):
        """Handle HTTP exceptions with consistent formatting."""
        request_id = getattr(request.state, "request_id", "unknown")
        
        error_response = StandardErrorResponse(
            error_code=f"HTTP_{exc.status_code}",
            message=exc.detail,
            request_id=request_id,
            service=service_name,
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.to_dict(),
            headers={"X-Request-ID": request_id}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle any unhandled exceptions."""
        request_id = getattr(request.state, "request_id", "unknown")
        
        logger.error(
            f"Unhandled exception: {str(exc)}",
            extra={
                "request_id": request_id,
                "error_type": "unhandled",
                "service": service_name,
                "traceback": traceback.format_exc(),
            }
        )
        
        error_response = StandardErrorResponse(
            error_code="INTERNAL_ERROR",
            message="An internal server error occurred",
            details="Please contact system administrator if the problem persists",
            request_id=request_id,
            service=service_name,
        )
        
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.to_dict(),
            headers={"X-Request-ID": request_id}
        )


# Health check exception for monitoring
class HealthCheckError(Exception):
    """Exception raised when health check fails."""
    
    def __init__(self, message: str, component: str | None = None):
        self.message = message
        self.component = component
        super().__init__(message)


# Constitutional compliance exception
class ConstitutionalComplianceError(Exception):
    """Exception raised when constitutional compliance validation fails."""
    
    def __init__(self, message: str, violations: list | None = None):
        self.message = message
        self.violations = violations or []
        super().__init__(message)


# Security exception
class SecurityValidationError(Exception):
    """Exception raised when security validation fails."""
    
    def __init__(self, message: str, threat_type: str | None = None):
        self.message = message
        self.threat_type = threat_type
        super().__init__(message)