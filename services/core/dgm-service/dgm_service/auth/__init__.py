"""
Authentication and authorization for DGM Service.

Integrates with ACGS Auth Service for JWT validation,
user management, and permission checking.
"""

from .auth_client import AuthClient
from .permissions import PermissionChecker, DGMPermissions
from .dependencies import get_current_user, require_permission
from .models import User, UserRole, Permission

__all__ = [
    "AuthClient",
    "PermissionChecker",
    "DGMPermissions",
    "get_current_user", 
    "require_permission",
    "User",
    "UserRole",
    "Permission"
]
