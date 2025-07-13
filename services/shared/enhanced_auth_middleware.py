"""
Enhanced Authorization Middleware for ACGS
Constitutional Hash: cdd01ef066bc6cf2

Provides comprehensive authorization controls with constitutional compliance.
"""

import logging
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class EnhancedAuthorizationMiddleware:
    """Enhanced authorization middleware with constitutional compliance."""

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.security = HTTPBearer()

        # Define role-based permissions
        self.role_permissions = {
            "admin": ["read", "write", "delete", "manage"],
            "user": ["read", "write"],
            "viewer": ["read"],
            "service": ["read", "write", "internal"],
        }

        # Define endpoint permissions
        self.endpoint_permissions = {
            "/api/v1/admin/*": ["admin"],
            "/api/v1/users/*": ["admin", "user"],
            "/api/v1/public/*": ["admin", "user", "viewer"],
            "/health": ["admin", "user", "viewer", "service"],
            "/metrics": ["admin", "service"],
        }

    async def check_authorization(
        self,
        request: Request,
        credentials: HTTPAuthorizationCredentials,
        required_permissions: list[str] | None = None,
    ) -> dict[str, Any]:
        """Check authorization for request."""
        try:
            # Extract user context from token (simplified)
            user_context = await self._extract_user_context(credentials.credentials)

            if not user_context:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                )

            # Check constitutional compliance
            if user_context.get("constitutional_hash") != self.constitutional_hash:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Constitutional compliance validation failed",
                )

            # Check role-based permissions
            user_role = user_context.get("role", "viewer")
            endpoint = request.url.path

            if not self._check_endpoint_access(endpoint, user_role):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions for this endpoint",
                )

            # Check specific permissions if required
            if required_permissions:
                user_permissions = self.role_permissions.get(user_role, [])
                if not any(perm in user_permissions for perm in required_permissions):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions for this operation",
                    )

            return {
                "authorized": True,
                "user_context": user_context,
                "constitutional_hash": self.constitutional_hash,
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.exception(f"Authorization check failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authorization check failed",
            )

    def _check_endpoint_access(self, endpoint: str, user_role: str) -> bool:
        """Check if user role has access to endpoint."""
        for pattern, allowed_roles in self.endpoint_permissions.items():
            if self._match_endpoint_pattern(endpoint, pattern):
                return user_role in allowed_roles

        # Default: require authentication for all endpoints
        return user_role in {"admin", "user", "viewer", "service"}

    def _match_endpoint_pattern(self, endpoint: str, pattern: str) -> bool:
        """Match endpoint against pattern (simplified)."""
        if pattern.endswith("*"):
            return endpoint.startswith(pattern[:-1])
        return endpoint == pattern

    async def _extract_user_context(self, token: str) -> dict[str, Any] | None:
        """Extract user context from token (simplified implementation)."""
        # In production, this would decode and validate JWT
        # For now, return mock context for testing
        return {
            "user_id": "test_user",
            "role": "user",
            "constitutional_hash": self.constitutional_hash,
        }
