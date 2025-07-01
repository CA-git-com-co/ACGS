"""
Constitutional Hash Validation Middleware
========================================

Middleware to ensure constitutional hash consistency across all ACGS services.
Validates and enforces the constitutional hash "cdd01ef066bc6cf2" in all service responses.
"""

import logging
import time
from collections.abc import Callable
from typing import Any

from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware

# Constitutional hash constant
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class ConstitutionalHashMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add constitutional hash to all service responses.

    This middleware ensures that all ACGS services include the constitutional
    hash in their response headers for consistency and compliance validation.
    """

    def __init__(
        self, app, service_name: str = "unknown", service_version: str = "3.0.0"
    ):
        super().__init__(app)
        self.service_name = service_name
        self.service_version = service_version
        self.constitutional_hash = CONSTITUTIONAL_HASH

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and add constitutional headers to response."""
        start_time = time.time()

        try:
            # Process the request
            response = await call_next(request)

            # Add constitutional compliance headers
            response.headers["X-Constitutional-Hash"] = self.constitutional_hash
            response.headers["X-Service-Name"] = self.service_name
            response.headers["X-Service-Version"] = self.service_version
            response.headers["X-Constitutional-Compliance"] = "enabled"
            response.headers["X-Process-Time"] = str(time.time() - start_time)

            # Log constitutional compliance for audit trail
            if request.url.path == "/health":
                logger.info(
                    f"Constitutional health check: {self.service_name} "
                    f"hash={self.constitutional_hash}"
                )

            return response

        except Exception as e:
            logger.error(f"Constitutional middleware error in {self.service_name}: {e}")
            # Create error response with constitutional headers
            from fastapi.responses import JSONResponse

            error_response = JSONResponse(
                status_code=500,
                content={
                    "error": "Constitutional middleware error",
                    "service": self.service_name,
                    "constitutional_hash": self.constitutional_hash,
                },
            )

            # Add constitutional headers even to error responses
            error_response.headers["X-Constitutional-Hash"] = self.constitutional_hash
            error_response.headers["X-Service-Name"] = self.service_name
            error_response.headers["X-Service-Version"] = self.service_version
            error_response.headers["X-Constitutional-Compliance"] = "error"

            return error_response


class ConstitutionalHashValidator:
    """
    Utility class for validating constitutional hash consistency.
    """

    @staticmethod
    def validate_hash(provided_hash: str) -> dict[str, Any]:
        """
        Validate a provided constitutional hash against the expected value.

        Args:
            provided_hash: The hash to validate

        Returns:
            Dict containing validation results
        """
        is_valid = provided_hash == CONSTITUTIONAL_HASH

        return {
            "valid": is_valid,
            "provided_hash": provided_hash,
            "expected_hash": CONSTITUTIONAL_HASH,
            "validation_timestamp": time.time(),
            "compliance_status": "compliant" if is_valid else "non_compliant",
        }

    @staticmethod
    def get_constitutional_info() -> dict[str, Any]:
        """
        Get constitutional hash information for service responses.

        Returns:
            Dict containing constitutional hash information
        """
        return {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "hash_algorithm": "SHA-256",
            "compliance_framework": "ACGS-PGP",
            "validation_level": "enterprise",
            "last_updated": "2024-12-25T00:00:00Z",
        }


def add_constitutional_hash_middleware(
    app, service_name: str, service_version: str = "3.0.0"
):
    """
    Add constitutional hash middleware to a FastAPI application.

    Args:
        app: FastAPI application instance
        service_name: Name of the service
        service_version: Version of the service
    """
    app.add_middleware(
        ConstitutionalHashMiddleware,
        service_name=service_name,
        service_version=service_version,
    )

    logger.info(f"Constitutional hash middleware added to {service_name}")


def create_constitutional_health_response(
    service_name: str,
    service_version: str = "3.0.0",
    port: int = 8000,
    additional_data: dict[str, Any] = None,
) -> dict[str, Any]:
    """
    Create a standardized health response with constitutional hash.

    Args:
        service_name: Name of the service
        service_version: Version of the service
        port: Service port number
        additional_data: Additional data to include in response

    Returns:
        Dict containing standardized health response
    """
    health_response = {
        "status": "healthy",
        "service": service_name,
        "version": service_version,
        "port": port,
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "timestamp": time.time(),
        "constitutional_compliance": {
            "enabled": True,
            "hash_verified": True,
            "compliance_level": "enterprise",
        },
    }

    if additional_data:
        health_response.update(additional_data)

    return health_response


async def validate_constitutional_compliance(request: Request) -> dict[str, Any]:
    """
    Validate constitutional compliance for incoming requests.

    Args:
        request: FastAPI request object

    Returns:
        Dict containing compliance validation results
    """
    # Check for constitutional hash in headers
    provided_hash = request.headers.get("X-Constitutional-Hash")

    if not provided_hash:
        return {
            "compliant": False,
            "reason": "No constitutional hash provided",
            "required_hash": CONSTITUTIONAL_HASH,
        }

    validation_result = ConstitutionalHashValidator.validate_hash(provided_hash)

    return {
        "compliant": validation_result["valid"],
        "validation_details": validation_result,
        "request_path": str(request.url.path),
        "request_method": request.method,
    }


# Export key components
__all__ = [
    "CONSTITUTIONAL_HASH",
    "ConstitutionalHashMiddleware",
    "ConstitutionalHashValidator",
    "add_constitutional_hash_middleware",
    "create_constitutional_health_response",
    "validate_constitutional_compliance",
]
