"""
ACGS-1 Phase A3: Standardized Middleware Components

This module provides production-grade middleware for all ACGS-1 services
including request correlation, performance monitoring, error handling,
and security features.
"""

import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .api_models import APIError, APIMetadata, APIResponse, APIStatus, ErrorCode

logger = logging.getLogger(__name__)


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add correlation IDs to all requests for distributed tracing.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())

        # Add to request state
        request.state.correlation_id = correlation_id

        # Process request
        response = await call_next(request)

        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id

        return response


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """
    Middleware to monitor API performance and add timing headers.
    """

    def __init__(self, app: ASGIApp, service_name: str):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate response time
        response_time_ms = (time.time() - start_time) * 1000

        # Add performance headers
        response.headers["X-Response-Time"] = f"{response_time_ms:.2f}ms"
        response.headers["X-Service"] = self.service_name
        response.headers["X-Timestamp"] = datetime.now(timezone.utc).isoformat()

        # Log performance metrics
        logger.info(
            f"API Request: {request.method} {request.url.path} - "
            f"{response.status_code} - {response_time_ms:.2f}ms"
        )

        # Store in request state for use in response creation
        request.state.response_time_ms = response_time_ms

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle exceptions and return standardized error responses.
    """

    def __init__(self, app: ASGIApp, service_name: str):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
        except HTTPException as exc:
            return await self._create_http_exception_response(request, exc)
        except Exception as exc:
            return await self._create_internal_error_response(request, exc)

    async def _create_http_exception_response(
        self, request: Request, exc: HTTPException
    ) -> JSONResponse:
        """Create standardized response for HTTP exceptions."""
        correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
        response_time_ms = getattr(request.state, "response_time_ms", None)

        # Map HTTP status codes to error codes
        error_code_map = {
            400: ErrorCode.VALIDATION_ERROR,
            401: ErrorCode.AUTHENTICATION_ERROR,
            403: ErrorCode.AUTHORIZATION_ERROR,
            404: ErrorCode.NOT_FOUND,
            409: ErrorCode.CONFLICT,
            429: ErrorCode.RATE_LIMIT_EXCEEDED,
            503: ErrorCode.SERVICE_UNAVAILABLE,
        }

        error_code = error_code_map.get(exc.status_code, ErrorCode.INTERNAL_ERROR)

        api_response = APIResponse(
            status=APIStatus.ERROR,
            error=APIError(
                code=error_code, message=exc.detail, correlation_id=correlation_id
            ),
            metadata=APIMetadata(
                service_name=self.service_name,
                correlation_id=correlation_id,
                response_time_ms=response_time_ms,
            ),
        )

        return JSONResponse(
            status_code=exc.status_code,
            content=api_response.dict(),
            headers={"X-Correlation-ID": correlation_id},
        )

    async def _create_internal_error_response(
        self, request: Request, exc: Exception
    ) -> JSONResponse:
        """Create standardized response for internal errors."""
        correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
        response_time_ms = getattr(request.state, "response_time_ms", None)

        # Log the actual error for debugging
        logger.error(
            f"Internal error in {self.service_name}: {str(exc)}",
            extra={"correlation_id": correlation_id},
            exc_info=True,
        )

        api_response = APIResponse(
            status=APIStatus.ERROR,
            error=APIError(
                code=ErrorCode.INTERNAL_ERROR,
                message="An internal error occurred. Please try again later.",
                details={"error_type": type(exc).__name__},
                correlation_id=correlation_id,
            ),
            metadata=APIMetadata(
                service_name=self.service_name,
                correlation_id=correlation_id,
                response_time_ms=response_time_ms,
            ),
        )

        return JSONResponse(
            status_code=500,
            content=api_response.dict(),
            headers={"X-Correlation-ID": correlation_id},
        )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all API requests with structured logging.
    """

    def __init__(self, app: ASGIApp, service_name: str):
        super().__init__(app)
        self.service_name = service_name

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))

        # Log request
        request_data = {
            "service": self.service_name,
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "query_params": str(request.query_params),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"API Request: {json.dumps(request_data)}")

        # Process request
        response = await call_next(request)

        # Log response
        response_data = {
            "service": self.service_name,
            "correlation_id": correlation_id,
            "status_code": response.status_code,
            "response_time_ms": getattr(request.state, "response_time_ms", None),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        logger.info(f"API Response: {json.dumps(response_data)}")

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    """

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
        }

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add security headers
        for header, value in self.security_headers.items():
            response.headers[header] = value

        return response


def add_production_middleware(app, service_name: str):
    """
    Add all production-grade middleware to a FastAPI application.

    Args:
        app: FastAPI application instance
        service_name: Name of the service for logging and monitoring
    """
    # Add middleware in reverse order (last added is executed first)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware, service_name=service_name)
    app.add_middleware(ErrorHandlingMiddleware, service_name=service_name)
    app.add_middleware(PerformanceMonitoringMiddleware, service_name=service_name)
    app.add_middleware(CorrelationIDMiddleware)

    logger.info(f"Production middleware added to {service_name}")


def create_exception_handlers(service_name: str) -> Dict[Any, Callable]:
    """
    Create standardized exception handlers for FastAPI applications.

    Args:
        service_name: Name of the service for error responses

    Returns:
        Dictionary of exception handlers
    """

    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions with standardized responses."""
        correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))
        response_time_ms = getattr(request.state, "response_time_ms", None)

        error_code_map = {
            400: ErrorCode.VALIDATION_ERROR,
            401: ErrorCode.AUTHENTICATION_ERROR,
            403: ErrorCode.AUTHORIZATION_ERROR,
            404: ErrorCode.NOT_FOUND,
            409: ErrorCode.CONFLICT,
            429: ErrorCode.RATE_LIMIT_EXCEEDED,
            503: ErrorCode.SERVICE_UNAVAILABLE,
        }

        error_code = error_code_map.get(exc.status_code, ErrorCode.INTERNAL_ERROR)

        api_response = APIResponse(
            status=APIStatus.ERROR,
            error=APIError(
                code=error_code, message=exc.detail, correlation_id=correlation_id
            ),
            metadata=APIMetadata(
                service_name=service_name,
                correlation_id=correlation_id,
                response_time_ms=response_time_ms,
            ),
        )

        return JSONResponse(status_code=exc.status_code, content=api_response.dict())

    async def validation_exception_handler(request: Request, exc):
        """Handle validation exceptions."""
        correlation_id = getattr(request.state, "correlation_id", str(uuid.uuid4()))

        api_response = APIResponse(
            status=APIStatus.ERROR,
            error=APIError(
                code=ErrorCode.VALIDATION_ERROR,
                message="Validation error",
                details={"validation_errors": exc.errors()},
                correlation_id=correlation_id,
            ),
            metadata=APIMetadata(
                service_name=service_name, correlation_id=correlation_id
            ),
        )

        return JSONResponse(status_code=422, content=api_response.dict())

    return {
        HTTPException: http_exception_handler,
        # Add more exception types as needed
    }
