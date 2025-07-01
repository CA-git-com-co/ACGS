"""
Authentication middleware for DGM Service.
"""

import logging
import uuid
from typing import Optional

from fastapi import HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from ..config import settings
from ..network.service_client import ACGSServiceClient

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Authentication middleware for validating JWT tokens."""

    def __init__(self, app, exclude_paths: Optional[list] = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/health/live",
            "/health/ready",
            "/metrics",
            "/docs",
            "/redoc",
            "/openapi.json",
        ]
        self.service_client = ACGSServiceClient()

    async def dispatch(self, request: Request, call_next):
        """Process request with authentication."""
        # Generate request ID for tracking
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id

        # Skip authentication for excluded paths
        if request.url.path in self.exclude_paths:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response

        # Extract authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return self._unauthorized_response(
                "Missing Authorization header", request_id
            )

        # Validate Bearer token format
        if not auth_header.startswith("Bearer "):
            return self._unauthorized_response(
                "Invalid Authorization header format", request_id
            )

        token = auth_header[7:]  # Remove "Bearer " prefix

        try:
            # Validate token with Auth Service
            validation_result = await self.service_client.validate_token(token)

            if not validation_result.get("valid", False):
                return self._unauthorized_response("Invalid token", request_id)

            # Store user information in request state
            request.state.user_id = validation_result.get("user_id")
            request.state.username = validation_result.get("username")
            request.state.roles = validation_result.get("roles", [])
            request.state.permissions = validation_result.get("permissions", [])

            # Check if user has required permissions for DGM operations
            if not self._has_dgm_permissions(
                request.state.roles, request.state.permissions
            ):
                return self._forbidden_response(
                    "Insufficient permissions for DGM operations", request_id
                )

            logger.info(
                f"Authenticated user {request.state.username} "
                f"for {request.method} {request.url.path}"
            )

        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return self._unauthorized_response(
                "Authentication service error", request_id
            )

        # Process request
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id

        return response

    def _has_dgm_permissions(self, roles: list, permissions: list) -> bool:
        """Check if user has required permissions for DGM operations."""
        # Check for admin role
        if "admin" in roles or "dgm_admin" in roles:
            return True

        # Check for specific DGM permissions
        required_permissions = ["dgm:read", "dgm:improve", "constitutional:validate"]

        # User needs at least read permission
        if "dgm:read" not in permissions:
            return False

        return True

    def _unauthorized_response(self, message: str, request_id: str) -> Response:
        """Create unauthorized response."""
        return Response(
            content=f'{{"error": "Unauthorized", "message": "{message}", "request_id": "{request_id}"}}',
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={
                "Content-Type": "application/json",
                "X-Request-ID": request_id,
                "WWW-Authenticate": "Bearer",
            },
        )

    def _forbidden_response(self, message: str, request_id: str) -> Response:
        """Create forbidden response."""
        return Response(
            content=f'{{"error": "Forbidden", "message": "{message}", "request_id": "{request_id}"}}',
            status_code=status.HTTP_403_FORBIDDEN,
            headers={"Content-Type": "application/json", "X-Request-ID": request_id},
        )
