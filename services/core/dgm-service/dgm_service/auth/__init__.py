"""
Authentication and authorization for DGM Service.

Integrates with ACGS Auth Service for JWT validation,
user management, and permission checking.
"""

from .auth_client import AuthClient
from .dependencies import get_current_user, require_permission
from .models import Permission, User, UserRole
from .permissions import DGMPermissions, PermissionChecker

__all__ = [
    "AuthClient",
    "DGMPermissions",
    "Permission",
    "PermissionChecker",
    "User",
    "UserRole",
    "get_current_user",
    "require_permission",
]
