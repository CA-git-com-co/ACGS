"""
FastAPI dependencies for authentication and authorization.
"""

import logging
from typing import List, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from .auth_client import AuthClient
from .models import (
    AuthContext,
    AuthenticationError,
    AuthorizationError,
    DGMPermissions,
    InsufficientPermissionsError,
    User,
)

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer(auto_error=False)

# Global auth client instance
auth_client = AuthClient()


async def get_auth_client() -> AuthClient:
    """Dependency to get auth client."""
    return auth_client


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    auth_client: AuthClient = Depends(get_auth_client),
) -> User:
    """
    Get current authenticated user.

    This dependency validates the JWT token and returns the user object.
    Raises HTTPException if authentication fails.
    """
    # Skip authentication for health endpoints
    if request.url.path in ["/health", "/health/live", "/health/ready", "/metrics"]:
        # Return a system user for health checks
        return User(id="system", username="system", is_active=True, roles=[], permissions=[])

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        # Validate token with auth service
        validation_result = await auth_client.validate_token(credentials.credentials)

        if not validation_result.get("valid", False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Get user information
        user_id = validation_result.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await auth_client.get_user_info(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is disabled",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_auth_context(
    user: User = Depends(get_current_user),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> AuthContext:
    """
    Get authentication context with user and permissions.
    """
    token = credentials.credentials if credentials else ""

    return AuthContext(
        user=user,
        token=token,
        permissions=user.get_all_permissions(),
        roles=[role.name for role in user.roles],
        is_service_account=user.username.startswith("service_"),
        service_name=user.username if user.username.startswith("service_") else None,
    )


def require_permission(permission: str):
    """
    Dependency factory for requiring specific permissions.

    Usage:
        @app.get("/admin")
        async def admin_endpoint(user: User = Depends(require_permission("dgm:admin"))):
            ...
    """

    async def permission_dependency(auth_context: AuthContext = Depends(get_auth_context)) -> User:
        if not auth_context.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"Permission required: {permission}"
            )
        return auth_context.user

    return permission_dependency


def require_dgm_permission(permission: DGMPermissions):
    """
    Dependency factory for requiring DGM-specific permissions.

    Usage:
        @app.post("/improve")
        async def improve(user: User = Depends(require_dgm_permission(DGMPermissions.DGM_IMPROVE))):
            ...
    """
    return require_permission(permission.value)


def require_any_permission(permissions: List[str]):
    """
    Dependency factory for requiring any of the specified permissions.
    """

    async def permission_dependency(auth_context: AuthContext = Depends(get_auth_context)) -> User:
        if not any(auth_context.has_permission(perm) for perm in permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these permissions required: {', '.join(permissions)}",
            )
        return auth_context.user

    return permission_dependency


def require_role(role_name: str):
    """
    Dependency factory for requiring specific roles.
    """

    async def role_dependency(user: User = Depends(get_current_user)) -> User:
        if not user.has_role(role_name):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=f"Role required: {role_name}"
            )
        return user

    return role_dependency


def require_admin():
    """
    Dependency for requiring admin permissions.
    """
    return require_any_permission([DGMPermissions.DGM_ADMIN.value, "admin"])


def optional_auth():
    """
    Optional authentication dependency.
    Returns None if no valid authentication is provided.
    """

    async def optional_auth_dependency(
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
        auth_client: AuthClient = Depends(get_auth_client),
    ) -> Optional[User]:
        if not credentials:
            return None

        try:
            validation_result = await auth_client.validate_token(credentials.credentials)

            if not validation_result.get("valid", False):
                return None

            user_id = validation_result.get("user_id")
            if not user_id:
                return None

            user = await auth_client.get_user_info(user_id)
            return user if user and user.is_active else None

        except Exception as e:
            logger.warning(f"Optional auth failed: {e}")
            return None

    return optional_auth_dependency


# Convenience dependencies for common permission checks
require_dgm_read = require_dgm_permission(DGMPermissions.DGM_READ)
require_dgm_improve = require_dgm_permission(DGMPermissions.DGM_IMPROVE)
require_dgm_rollback = require_dgm_permission(DGMPermissions.DGM_ROLLBACK)
require_constitutional_validate = require_dgm_permission(DGMPermissions.CONSTITUTIONAL_VALIDATE)
