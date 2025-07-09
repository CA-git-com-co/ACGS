"""
Constitutional validation middleware for FastAPI with
FastConstitutionalValidator.
Constitutional Hash: cdd01ef066bc6cf2

Enhanced with O(1) validation performance using FastConstitutionalValidator.
"""

import logging
import time
from typing import Any, Callable, Dict

from fastapi import HTTPException, Request, Response
from prometheus_client import Counter
from starlette.middleware.base import BaseHTTPMiddleware

# Import the fast validator
from .fast_constitutional_validator import (
    get_fast_validator,
    add_constitutional_headers_fast
)

# Import performance metrics
from .constitutional_performance_metrics import (
    ConstitutionalPerformanceTracker,
    get_performance_collector,
    setup_constitutional_metrics_endpoint,
)

# Constitutional compliance hash
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Metrics
CONSTITUTIONAL_FAILURES = Counter(
    "acgs_constitutional_compliance_failures_total",
    "Total constitutional compliance failures",
    ["service", "endpoint", "method"],
)

CONSTITUTIONAL_VALIDATIONS = Counter(
    "acgs_constitutional_validations_total",
    "Total constitutional validations",
    ["service", "endpoint", "method", "result"],
)

CONSTITUTIONAL_HASH_VIOLATIONS = Counter(
    "acgs_constitutional_hash_violations_total",
    "Constitutional hash violations",
    ["service", "endpoint", "violation_type"],
)

logger = logging.getLogger(__name__)


class ConstitutionalValidationMiddleware(BaseHTTPMiddleware):
    """Enhanced middleware using FastConstitutionalValidator for O(1)
    validation performance."""

    def __init__(
        self,
        app,
        constitutional_hash: str = CONSTITUTIONAL_HASH,
        performance_target_ms: float = 5.0,
        enable_strict_validation: bool = True,
        exempt_paths: list = None,
    ):
        super().__init__(app)
        self.constitutional_hash = constitutional_hash
        self.performance_target_ms = performance_target_ms
        self.enable_strict_validation = enable_strict_validation
        self.exempt_paths = exempt_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
        ]

        # Initialize fast validator for O(1) performance
        self.fast_validator = get_fast_validator()

        # Initialize performance collector
        self.performance_collector = get_performance_collector(
            f"constitutional-middleware-{hash(app) % 10000}"
        )

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        # Skip validation for exempt paths
        if request.url.path in self.exempt_paths:
            return await call_next(request)

        # Extract endpoint and method for metrics
        endpoint = request.url.path
        method = request.method
        service_name = getattr(request.state, "service_name", "unknown")

        # Use performance tracker for comprehensive metrics
        with ConstitutionalPerformanceTracker(
            service_name=service_name,
            validation_type="middleware",
            endpoint=endpoint,
            method=method
        ) as tracker:
            # Start timing for internal metrics
            start_time = time.time()

            # Validate request headers
            await self._validate_request_headers(
                request, service_name, endpoint, method, tracker
            )

            # Validate request body if present
            if hasattr(request, "_body"):
                await self._validate_request_body(
                    request, service_name, endpoint, method, tracker
                )

        try:
            # Process request
            response = await call_next(request)

            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000

            # Check performance compliance
            if processing_time > self.performance_target_ms:
                logger.warning(
                    f"Performance target exceeded: {service_name}.{endpoint} "
                    f"took {processing_time:.2f}ms "
                    f"(target: {self.performance_target_ms}ms)"
                )

            # Validate response
            await self._validate_response(
                response, service_name, endpoint, method
            )

            # Add constitutional headers to response using fast validator
            add_constitutional_headers_fast(
                response,
                self.constitutional_hash,
                processing_time,
                self.performance_target_ms
            )

            # Record successful validation
            CONSTITUTIONAL_VALIDATIONS.labels(
                service_name, endpoint, method, "success"
            ).inc()

            return response

        except HTTPException:
            # Record validation failure
            CONSTITUTIONAL_FAILURES.labels(
                service_name, endpoint, method
            ).inc()
            CONSTITUTIONAL_VALIDATIONS.labels(
                service_name, endpoint, method, "failure"
            ).inc()
            raise
        except Exception as e:
            # Record unexpected error
            logger.error(f"Constitutional validation error: {e}")
            CONSTITUTIONAL_FAILURES.labels(
                service_name, endpoint, method
            ).inc()
            CONSTITUTIONAL_VALIDATIONS.labels(
                service_name, endpoint, method, "error"
            ).inc()
            raise HTTPException(
                status_code=500,
                detail="Constitutional validation service error"
            )

    async def _validate_request_headers(
        self, request: Request, service_name: str, endpoint: str, method: str,
        tracker=None
    ):
        """Fast validation of constitutional compliance in request headers."""
        if not self.enable_strict_validation:
            return

        # Use fast validator for O(1) header validation
        request_hash = request.headers.get("X-Constitutional-Hash")
        if request_hash:
            is_valid = self.fast_validator.validate_hash_fast(request_hash)

            # Record cache hit/miss
            if tracker:
                if is_valid:
                    tracker.record_cache_hit("header_hash")
                else:
                    tracker.record_cache_miss("header_hash")
                tracker.record_compliance_result(is_valid)

            if not is_valid:
                CONSTITUTIONAL_HASH_VIOLATIONS.labels(
                    service_name, endpoint, "invalid_request_hash"
                ).inc()

                logger.warning(
                    f"Invalid constitutional hash in request: {request_hash} "
                    f"(expected: {self.constitutional_hash})"
                )

                if self.enable_strict_validation:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid constitutional hash. "
                        f"Expected: {self.constitutional_hash}",
                    )
        else:
            # Record compliance for missing hash
            if tracker:
                # Missing hash is allowed
                tracker.record_compliance_result(True)

    async def _validate_request_body(
        self, request: Request, service_name: str, endpoint: str, method: str,
        tracker=None
    ):
        """Fast validation of constitutional compliance in request body."""
        if not self.enable_strict_validation:
            return

        try:
            # Only validate JSON requests
            content_type = request.headers.get("content-type", "")
            if "application/json" not in content_type:
                return

            # Get request body (if already read)
            body = getattr(request, "_body", None)
            if not body:
                return

            # Use fast validator for optimized body validation
            is_valid = self.fast_validator._validate_body_fast(body)

            # Record performance metrics
            if tracker:
                if is_valid:
                    tracker.record_cache_hit("body_hash")
                else:
                    tracker.record_cache_miss("body_hash")
                tracker.record_compliance_result(is_valid)

            if not is_valid:
                CONSTITUTIONAL_HASH_VIOLATIONS.labels(
                    service_name, endpoint, "invalid_body_hash"
                ).inc()

                if self.enable_strict_validation:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid constitutional hash in body. "
                        f"Expected: {self.constitutional_hash}",
                    )

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error validating request body: {e}")

    async def _validate_response(
        self, response: Response, service_name: str, endpoint: str, method: str
    ):
        """Validate constitutional compliance in response."""
        # Ensure response has constitutional hash header
        if "X-Constitutional-Hash" not in response.headers:
            CONSTITUTIONAL_HASH_VIOLATIONS.labels(
                service_name, endpoint, "missing_response_hash"
            ).inc()

            logger.warning(
                f"Missing constitutional hash in response headers for "
                f"{service_name}.{endpoint}"
            )


class ConstitutionalComplianceChecker:
    """Utility class for checking constitutional compliance."""

    def __init__(self, constitutional_hash: str = CONSTITUTIONAL_HASH):
        self.constitutional_hash = constitutional_hash

    def validate_hash(self, hash_value: str) -> bool:
        """Validate a constitutional hash value."""
        return hash_value == self.constitutional_hash

    def validate_request_data(self, data: Dict[str, Any]) -> bool:
        """Validate constitutional compliance in request data."""
        if not isinstance(data, dict):
            return True  # Skip validation for non-dict data

        hash_value = data.get("constitutional_hash")
        if hash_value is None:
            return True  # Hash is optional in requests

        return self.validate_hash(hash_value)

    def validate_response_data(self, data: Dict[str, Any]) -> bool:
        """Validate constitutional compliance in response data."""
        if not isinstance(data, dict):
            return True  # Skip validation for non-dict data

        hash_value = data.get("constitutional_hash")
        if hash_value is None:
            # Response should include constitutional hash
            logger.warning("Missing constitutional hash in response data")
            return False

        return self.validate_hash(hash_value)

    def ensure_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure constitutional compliance by adding hash if missing."""
        if isinstance(data, dict):
            data["constitutional_hash"] = self.constitutional_hash
        return data

    def get_compliance_report(self) -> Dict[str, Any]:
        """Get constitutional compliance report."""
        return {
            "constitutional_hash": self.constitutional_hash,
            "validation_enabled": True,
            "compliance_status": "active",
            "last_check": time.time(),
        }


def setup_constitutional_validation(
    app,
    service_name: str,
    performance_target_ms: float = 5.0,
    enable_strict_validation: bool = True,
    enable_metrics_endpoint: bool = True,
):
    """
    Set up constitutional validation middleware for a FastAPI application.

    Args:
        app: FastAPI application instance
        service_name: Name of the service
        performance_target_ms: Performance target in milliseconds
        enable_strict_validation: Whether to enable strict validation
        enable_metrics_endpoint: Whether to enable metrics endpoint
    """
    # Add constitutional validation middleware
    app.add_middleware(
        ConstitutionalValidationMiddleware,
        constitutional_hash=CONSTITUTIONAL_HASH,
        performance_target_ms=performance_target_ms,
        enable_strict_validation=enable_strict_validation,
    )

    # Setup performance metrics endpoint
    if enable_metrics_endpoint:
        setup_constitutional_metrics_endpoint(app)

    logger.info(
        f"Constitutional validation middleware initialized for {service_name} "
        f"[hash: {CONSTITUTIONAL_HASH}, target: {performance_target_ms}ms]"
    )

    return {
        "service_name": service_name,
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "performance_target_ms": performance_target_ms,
        "strict_validation": enable_strict_validation,
        "metrics_enabled": enable_metrics_endpoint,
    }
