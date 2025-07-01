"""
ACGS-1 Version-Aware Routing Middleware

Provides intelligent version detection and routing for API requests,
integrating seamlessly with existing ACGS middleware stack.
"""

import logging
import time
from typing import Any, Callable, Dict, Optional
from urllib.parse import parse_qs, urlparse

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from ..api_models import APIError, APIResponse, APIStatus, ErrorCode
from ..versioning.response_transformers import VersionedResponseBuilder
from ..versioning.version_manager import (
    APIVersion,
    DeprecatedVersionError,
    UnsupportedVersionError,
    VersionManager,
    VersionValidationError,
)

logger = logging.getLogger(__name__)


class VersionRoutingMiddleware(BaseHTTPMiddleware):
    """
    Version-aware routing middleware for ACGS-1 services.

    Features:
    - Multi-source version detection (headers, URL, query params)
    - Automatic version validation and compatibility checking
    - Deprecation warnings with RFC 8594 compliance
    - Performance monitoring with <5ms additional latency
    - Seamless integration with existing middleware stack
    """

    def __init__(
        self,
        app: ASGIApp,
        service_name: str,
        version_manager: Optional[VersionManager] = None,
        response_builder: Optional[VersionedResponseBuilder] = None,
        enable_strict_validation: bool = True,
        enable_deprecation_warnings: bool = True,
        performance_target_ms: float = 5.0,
        bypass_paths: Optional[list] = None,
    ):
        """
        Initialize version routing middleware.

        Args:
            app: ASGI application
            service_name: Name of the service
            version_manager: Version manager instance
            response_builder: Versioned response builder
            enable_strict_validation: Enable strict version validation
            enable_deprecation_warnings: Enable deprecation warnings
            performance_target_ms: Target middleware latency in milliseconds
            bypass_paths: Paths to bypass version checking
        """
        super().__init__(app)
        self.service_name = service_name
        self.enable_strict_validation = enable_strict_validation
        self.enable_deprecation_warnings = enable_deprecation_warnings
        self.performance_target_ms = performance_target_ms

        # Default bypass paths
        self.bypass_paths = bypass_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
            "/favicon.ico",
            "/static/",
        ]

        # Initialize version manager if not provided
        self.version_manager = version_manager or VersionManager(
            service_name=service_name, current_version="v1.0.0"
        )

        # Initialize response builder if not provided
        self.response_builder = response_builder or VersionedResponseBuilder(
            service_name=service_name
        )

        # Performance tracking
        self.request_count = 0
        self.total_latency_ms = 0.0

        logger.info(f"VersionRoutingMiddleware initialized for {service_name}")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request with version-aware routing."""
        start_time = time.time()

        # Skip version processing for bypass paths
        if self._should_bypass_path(request.url.path):
            return await call_next(request)

        try:
            # Detect and validate API version
            detected_version = self._detect_version(request)
            compatibility_info = None

            if self.enable_strict_validation:
                try:
                    compatibility_info = self.version_manager.validate_version(
                        detected_version
                    )
                except UnsupportedVersionError as e:
                    return self._create_error_response(
                        error_code=ErrorCode.VALIDATION_ERROR,
                        message=str(e),
                        status_code=400,
                        request=request,
                    )
                except DeprecatedVersionError as e:
                    # Log deprecation but continue processing
                    logger.warning(f"Deprecated version accessed: {e}")

            # Store version information in request state
            request.state.api_version = detected_version
            request.state.version_compatibility = compatibility_info

            # Process the request
            response = await call_next(request)

            # Add version headers to response
            self._add_version_headers(response, detected_version, compatibility_info)

            # Track performance
            self._track_performance(start_time)

            return response

        except Exception as e:
            logger.error(f"Version routing middleware error: {e}")
            return self._create_error_response(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="Version processing failed",
                status_code=500,
                request=request,
            )

    def _detect_version(self, request: Request) -> APIVersion:
        """Detect API version from request using multiple sources."""
        # Convert headers to dict for compatibility
        headers = dict(request.headers)

        # Parse query parameters
        query_params = dict(request.query_params)

        # Use version manager's detection logic
        return self.version_manager.detect_version_from_request(
            request_headers=headers,
            url_path=request.url.path,
            query_params=query_params,
        )

    def _should_bypass_path(self, path: str) -> bool:
        """Check if path should bypass version processing."""
        return any(path.startswith(bypass_path) for bypass_path in self.bypass_paths)

    def _add_version_headers(
        self,
        response: Response,
        version: APIVersion,
        compatibility_info: Optional[Any] = None,
    ):
        """Add version-related headers to response."""
        # Standard version headers
        response.headers["API-Version"] = str(version)
        response.headers["X-API-Version"] = str(version)
        response.headers["X-Service-Name"] = self.service_name

        # Add deprecation headers if applicable
        if compatibility_info and self.enable_deprecation_warnings:
            deprecation_headers = self.version_manager.create_deprecation_headers(
                version
            )
            for header_name, header_value in deprecation_headers.items():
                response.headers[header_name] = header_value

        # Add supported versions header
        supported_versions = [
            str(comp.version) for comp in self.version_manager.get_supported_versions()
        ]
        response.headers["X-Supported-Versions"] = ",".join(supported_versions)

    def _create_error_response(
        self,
        error_code: ErrorCode,
        message: str,
        status_code: int,
        request: Request,
        details: Optional[Dict[str, Any]] = None,
    ) -> JSONResponse:
        """Create standardized error response."""
        # Get correlation ID from request state if available
        correlation_id = getattr(request.state, "correlation_id", None)

        # Build error response using existing API models
        api_response = self.response_builder.build_response(
            status=APIStatus.ERROR,
            error=APIError(code=error_code, message=message, details=details or {}),
            correlation_id=correlation_id,
        )

        return JSONResponse(content=api_response.dict(), status_code=status_code)

    def _track_performance(self, start_time: float):
        """Track middleware performance metrics."""
        latency_ms = (time.time() - start_time) * 1000

        self.request_count += 1
        self.total_latency_ms += latency_ms

        # Log performance warning if exceeding target
        if latency_ms > self.performance_target_ms:
            logger.warning(
                f"Version middleware latency exceeded target: "
                f"{latency_ms:.2f}ms > {self.performance_target_ms}ms"
            )

        # Log average performance every 100 requests
        if self.request_count % 100 == 0:
            avg_latency = self.total_latency_ms / self.request_count
            logger.info(
                f"Version middleware average latency: {avg_latency:.2f}ms "
                f"(target: {self.performance_target_ms}ms)"
            )

    def get_performance_stats(self) -> Dict[str, Any]:
        """Get middleware performance statistics."""
        avg_latency = (
            self.total_latency_ms / self.request_count if self.request_count > 0 else 0
        )

        return {
            "service_name": self.service_name,
            "request_count": self.request_count,
            "average_latency_ms": round(avg_latency, 2),
            "target_latency_ms": self.performance_target_ms,
            "performance_ratio": round(avg_latency / self.performance_target_ms, 2),
            "supported_versions": [
                str(comp.version)
                for comp in self.version_manager.get_supported_versions()
            ],
        }


# Factory function for easy middleware creation
def create_version_routing_middleware(
    app: ASGIApp,
    service_name: str,
    current_version: str = "v1.0.0",
    supported_versions: Optional[list] = None,
    **kwargs,
) -> VersionRoutingMiddleware:
    """
    Factory function to create version routing middleware with sensible defaults.

    Args:
        app: ASGI application
        service_name: Name of the service
        current_version: Current API version
        supported_versions: List of supported versions
        **kwargs: Additional middleware configuration

    Returns:
        Configured VersionRoutingMiddleware instance
    """
    # Create version manager
    version_manager = VersionManager(
        service_name=service_name, current_version=current_version
    )

    # Register additional supported versions
    if supported_versions:
        for version_str in supported_versions:
            version_manager.register_version(version_str)

    # Create response builder
    response_builder = VersionedResponseBuilder(service_name)

    return VersionRoutingMiddleware(
        app=app,
        service_name=service_name,
        version_manager=version_manager,
        response_builder=response_builder,
        **kwargs,
    )
