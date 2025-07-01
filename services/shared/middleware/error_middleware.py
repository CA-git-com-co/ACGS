"""
ACGS-1 Centralized Error Handling Middleware

This module provides centralized error handling middleware for FastAPI applications
across all ACGS microservices. It automatically catches exceptions, assigns error codes,
formats responses, and provides request correlation tracking.

Features:
- Automatic exception catching and error code assignment
- Request correlation tracking across distributed services
- Service-specific error handlers for domain exceptions
- Integration with security middleware
- Error rate limiting and circuit breaker patterns
- Structured error logging with context
"""

import asyncio
import logging
import time
import traceback
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Import error handling components
from ..response.error_response import (
    ErrorJSONResponse,
    ErrorResponseBuilder,
    create_http_exception_error_response,
)

# Configure structured logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class CircuitBreakerState:
    """Circuit breaker state for error rate limiting."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def record_success(self):
        """Record successful operation."""
        self.failure_count = 0
        self.state = "CLOSED"

    def record_failure(self):
        """Record failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"

    def can_execute(self) -> bool:
        """Check if operation can be executed."""
        if self.state == "CLOSED":
            return True

        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                return True
            return False

        # HALF_OPEN state
        return True

    def is_open(self) -> bool:
        """Check if circuit breaker is open."""
        return self.state == "OPEN"


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Centralized error handling middleware for ACGS services."""

    def __init__(
        self,
        app: ASGIApp,
        service_name: str,
        service_version: str = "1.0.0",
        enable_circuit_breaker: bool = True,
        enable_rate_limiting: bool = True,
        debug_mode: bool = False,
    ):
        super().__init__(app)
        self.service_name = service_name
        self.service_version = service_version
        self.enable_circuit_breaker = enable_circuit_breaker
        self.enable_rate_limiting = enable_rate_limiting
        self.debug_mode = debug_mode

        # Error handling components
        self.error_builder = ErrorResponseBuilder(service_name, service_version)
        self.circuit_breaker = CircuitBreakerState() if enable_circuit_breaker else None

        # Error rate tracking
        self.error_rates: dict[str, list[float]] = {}
        self.rate_limit_window = 300  # 5 minutes
        self.rate_limit_threshold = 100  # errors per window

        # Custom exception handlers
        self.exception_handlers: dict[type[Exception], Callable] = {}

        # Request correlation tracking
        self.active_requests: dict[str, dict[str, Any]] = {}

        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default exception handlers."""

        # HTTP exceptions
        self.register_exception_handler(HTTPException, self._handle_http_exception)

        # Validation errors
        try:
            from pydantic import ValidationError

            self.register_exception_handler(
                ValidationError, self._handle_validation_error
            )
        except ImportError:
            pass

        # Database errors
        try:
            from sqlalchemy.exc import SQLAlchemyError

            self.register_exception_handler(
                SQLAlchemyError, self._handle_database_error
            )
        except ImportError:
            pass

        # External service errors
        try:
            import httpx

            self.register_exception_handler(
                httpx.RequestError, self._handle_external_service_error
            )
            self.register_exception_handler(
                httpx.HTTPStatusError, self._handle_external_service_error
            )
        except ImportError:
            pass

        # Timeout errors
        self.register_exception_handler(
            asyncio.TimeoutError, self._handle_timeout_error
        )
        self.register_exception_handler(TimeoutError, self._handle_timeout_error)

    def register_exception_handler(
        self,
        exception_type: type[Exception],
        handler: Callable[[Exception, Request], ErrorJSONResponse],
    ):
        """Register custom exception handler."""
        self.exception_handlers[exception_type] = handler

    async def dispatch(self, request: Request, call_next) -> Response:
        """Main middleware dispatch method."""

        # Generate request ID for correlation
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        request.state.request_id = request_id

        # Check circuit breaker
        if self.circuit_breaker and self.circuit_breaker.is_open():
            return await self._handle_circuit_breaker_open(request)

        # Check rate limiting
        if self.enable_rate_limiting and await self._is_rate_limited(request):
            return await self._handle_rate_limit_exceeded(request)

        # Track request start
        start_time = time.time()
        self.active_requests[request_id] = {
            "start_time": start_time,
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None,
        }

        try:
            # Process request
            response = await call_next(request)

            # Record success for circuit breaker
            if self.circuit_breaker:
                self.circuit_breaker.record_success()

            # Add correlation headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Service"] = self.service_name

            return response

        except Exception as exc:
            # Handle exception
            error_response = await self._handle_exception(exc, request)

            # Record failure for circuit breaker
            if self.circuit_breaker:
                self.circuit_breaker.record_failure()

            # Log error with context
            await self._log_error(exc, request, error_response)

            return error_response

        finally:
            # Clean up request tracking
            processing_time = time.time() - start_time
            if request_id in self.active_requests:
                self.active_requests[request_id]["processing_time"] = processing_time
                del self.active_requests[request_id]

    async def _handle_exception(
        self, exc: Exception, request: Request
    ) -> ErrorJSONResponse:
        """Handle exception and create appropriate error response."""

        # Set request context
        self.error_builder.set_request_context(request)

        # Find specific handler
        for exception_type, handler in self.exception_handlers.items():
            if isinstance(exc, exception_type):
                return await handler(exc, request)

        # Default handler for unhandled exceptions
        return await self._handle_generic_exception(exc, request)

    async def _handle_http_exception(
        self, exc: HTTPException, request: Request
    ) -> ErrorJSONResponse:
        """Handle FastAPI HTTP exceptions."""
        return create_http_exception_error_response(
            exc, self.service_name, request.state.request_id
        )

    async def _handle_validation_error(
        self, exc, request: Request
    ) -> ErrorJSONResponse:
        """Handle Pydantic validation errors."""
        validation_errors = []

        for error in exc.errors():
            validation_errors.append(
                {
                    "field": ".".join(str(loc) for loc in error["loc"]),
                    "message": error["msg"],
                    "type": error["type"],
                }
            )

        error_response = self.error_builder.validation_error(
            validation_errors=validation_errors, message="Request validation failed"
        )

        return ErrorJSONResponse(error_response, status_code=422)

    async def _handle_database_error(self, exc, request: Request) -> ErrorJSONResponse:
        """Handle database errors."""
        error_response = self.error_builder.system_error(
            details={
                "database_error": True,
                "error_type": type(exc).__name__,
                "error_message": (
                    str(exc) if self.debug_mode else "Database operation failed"
                ),
            }
        )

        return ErrorJSONResponse(error_response, status_code=500)

    async def _handle_external_service_error(
        self, exc, request: Request
    ) -> ErrorJSONResponse:
        """Handle external service errors."""
        service_name = "unknown"
        error_details = str(exc)

        # Extract service name from URL if possible
        if hasattr(exc, "request") and exc.request:
            service_name = exc.request.url.host

        error_response = self.error_builder.external_service_error(
            service_name=service_name, error_details=error_details, retryable=True
        )

        return ErrorJSONResponse(error_response, status_code=503)

    async def _handle_timeout_error(
        self, exc: Exception, request: Request
    ) -> ErrorJSONResponse:
        """Handle timeout errors."""
        error_response = self.error_builder.from_error_code(
            "SHARED_SYSTEM_ERROR_002",
            details={"timeout_error": True, "error_type": type(exc).__name__},
            override_message="Request timeout - operation took too long",
        )

        return ErrorJSONResponse(error_response, status_code=408)

    async def _handle_generic_exception(
        self, exc: Exception, request: Request
    ) -> ErrorJSONResponse:
        """Handle generic unhandled exceptions."""
        error_id = str(uuid.uuid4())

        error_details = {"error_id": error_id, "error_type": type(exc).__name__}

        if self.debug_mode:
            error_details.update(
                {"error_message": str(exc), "traceback": traceback.format_exc()}
            )

        error_response = self.error_builder.system_error(
            error_id=error_id, details=error_details
        )

        return ErrorJSONResponse(error_response, status_code=500)

    async def _handle_circuit_breaker_open(self, request: Request) -> ErrorJSONResponse:
        """Handle requests when circuit breaker is open."""
        self.error_builder.set_request_context(request)

        error_response = self.error_builder.from_error_code(
            "SHARED_SYSTEM_ERROR_002",
            details={
                "circuit_breaker": "open",
                "reason": "Service temporarily unavailable due to high error rate",
            },
            override_message="Service temporarily unavailable",
        )

        return ErrorJSONResponse(error_response, status_code=503)

    async def _is_rate_limited(self, request: Request) -> bool:
        """Check if request should be rate limited."""
        if not self.enable_rate_limiting:
            return False

        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()

        # Clean old entries
        if client_ip in self.error_rates:
            self.error_rates[client_ip] = [
                timestamp
                for timestamp in self.error_rates[client_ip]
                if current_time - timestamp < self.rate_limit_window
            ]

        # Check rate limit
        error_count = len(self.error_rates.get(client_ip, []))
        return error_count >= self.rate_limit_threshold

    async def _handle_rate_limit_exceeded(self, request: Request) -> ErrorJSONResponse:
        """Handle rate limit exceeded."""
        self.error_builder.set_request_context(request)

        error_response = self.error_builder.from_error_code(
            "SHARED_SYSTEM_ERROR_002",
            details={
                "rate_limit": "exceeded",
                "window_seconds": self.rate_limit_window,
                "threshold": self.rate_limit_threshold,
            },
            override_message="Too many requests",
        )

        headers = {"Retry-After": "300"}  # 5 minutes
        return ErrorJSONResponse(error_response, status_code=429, headers=headers)

    async def _log_error(
        self, exc: Exception, request: Request, error_response: ErrorJSONResponse
    ):
        """Log error with structured context."""

        # Extract error details
        error_data = (
            error_response.body.decode() if hasattr(error_response, "body") else "{}"
        )

        log_context = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": self.service_name,
            "request_id": getattr(request.state, "request_id", "unknown"),
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("User-Agent"),
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "status_code": error_response.status_code,
            "error_response": error_data,
        }

        # Add stack trace for server errors
        if error_response.status_code >= 500:
            log_context["stack_trace"] = traceback.format_exc()

        # Log at appropriate level
        if error_response.status_code >= 500:
            logger.error("Server error occurred", extra=log_context)
        elif error_response.status_code >= 400:
            logger.warning("Client error occurred", extra=log_context)
        else:
            logger.info("Request processed with error", extra=log_context)

        # Record error rate for rate limiting
        if self.enable_rate_limiting:
            client_ip = request.client.host if request.client else "unknown"
            current_time = time.time()

            if client_ip not in self.error_rates:
                self.error_rates[client_ip] = []

            self.error_rates[client_ip].append(current_time)


# Service-specific middleware factories
def create_auth_error_middleware(
    app: FastAPI, debug_mode: bool = False
) -> ErrorHandlingMiddleware:
    """Create error middleware for Authentication Service."""
    return ErrorHandlingMiddleware(
        app=app,
        service_name="authentication-service",
        service_version="2.1.0",
        debug_mode=debug_mode,
    )


def create_ac_error_middleware(
    app: FastAPI, debug_mode: bool = False
) -> ErrorHandlingMiddleware:
    """Create error middleware for Constitutional AI Service."""
    middleware = ErrorHandlingMiddleware(
        app=app,
        service_name="constitutional-ai-service",
        service_version="2.1.0",
        debug_mode=debug_mode,
    )

    # Register AC-specific handlers
    # Add LLM-specific error handling here

    return middleware


def create_fv_error_middleware(
    app: FastAPI, debug_mode: bool = False
) -> ErrorHandlingMiddleware:
    """Create error middleware for Formal Verification Service."""
    middleware = ErrorHandlingMiddleware(
        app=app,
        service_name="formal-verification-service",
        service_version="1.5.0",
        debug_mode=debug_mode,
    )

    # Register Z3-specific error handlers
    try:
        import z3

        async def handle_z3_error(
            exc: Exception, request: Request
        ) -> ErrorJSONResponse:
            error_response = middleware.error_builder.from_error_code(
                "FV_EXTERNAL_SERVICE_001",
                details={"z3_error": True, "error_message": str(exc)},
                override_message="Z3 solver error occurred",
            )
            return ErrorJSONResponse(error_response, status_code=422)

        middleware.register_exception_handler(z3.Z3Exception, handle_z3_error)
    except ImportError:
        pass

    return middleware


# Utility functions
def add_error_middleware_to_app(
    app: FastAPI,
    service_name: str,
    service_version: str = "1.0.0",
    debug_mode: bool = False,
):
    """Add error handling middleware to FastAPI app."""
    middleware = ErrorHandlingMiddleware(
        app=app,
        service_name=service_name,
        service_version=service_version,
        debug_mode=debug_mode,
    )

    app.add_middleware(ErrorHandlingMiddleware, **middleware.__dict__)
    return middleware


# Export main classes and functions
__all__ = [
    "CircuitBreakerState",
    "ErrorHandlingMiddleware",
    "add_error_middleware_to_app",
    "create_ac_error_middleware",
    "create_auth_error_middleware",
    "create_fv_error_middleware",
]
