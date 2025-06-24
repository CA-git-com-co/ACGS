"""
Authentication models for DGM Service.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional


class DGMPermissions(Enum):
    """DGM-specific permissions."""

    # Read permissions
    DGM_READ = "dgm:read"
    DGM_STATUS = "dgm:status"
    DGM_ARCHIVE_READ = "dgm:archive:read"
    DGM_METRICS_READ = "dgm:metrics:read"

    # Write permissions
    DGM_IMPROVE = "dgm:improve"
    DGM_CANCEL = "dgm:cancel"
    DGM_ROLLBACK = "dgm:rollback"
    DGM_ARCHIVE_WRITE = "dgm:archive:write"

    # Administrative permissions
    DGM_ADMIN = "dgm:admin"
    DGM_CONFIG = "dgm:config"
    DGM_SYSTEM = "dgm:system"

    # Constitutional permissions
    CONSTITUTIONAL_READ = "constitutional:read"
    CONSTITUTIONAL_VALIDATE = "constitutional:validate"
    CONSTITUTIONAL_REPORT = "constitutional:report"

    # Bandit algorithm permissions
    BANDIT_READ = "bandit:read"
    BANDIT_CONFIGURE = "bandit:configure"

    # Service management
    SERVICE_HEALTH = "service:health"
    SERVICE_METRICS = "service:metrics"


@dataclass
class Permission:
    """Permission model."""

    name: str
    description: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None


@dataclass
class UserRole:
    """User role model."""

    name: str
    permissions: List[str]
    description: Optional[str] = None
    is_system_role: bool = False


@dataclass
class User:
    """User model."""

    id: str
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    roles: List[UserRole] = None
    permissions: List[Permission] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    cached_at: Optional[datetime] = None

    def __post_init__(self):
        if self.roles is None:
            self.roles = []
        if self.permissions is None:
            self.permissions = []

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        # Check direct permissions
        for perm in self.permissions:
            if perm.name == permission:
                return True

        # Check role permissions
        for role in self.roles:
            if permission in role.permissions:
                return True

        # Admin users have all permissions
        if self.is_admin:
            return True

        return False

    def has_role(self, role_name: str) -> bool:
        """Check if user has a specific role."""
        return any(role.name == role_name for role in self.roles)

    def get_all_permissions(self) -> List[str]:
        """Get all permissions from roles and direct assignments."""
        all_permissions = set()

        # Add direct permissions
        for perm in self.permissions:
            all_permissions.add(perm.name)

        # Add role permissions
        for role in self.roles:
            all_permissions.update(role.permissions)

        return list(all_permissions)

    def is_dgm_user(self) -> bool:
        """Check if user has any DGM permissions."""
        dgm_permissions = [perm.value for perm in DGMPermissions]
        user_permissions = self.get_all_permissions()

        return any(perm in dgm_permissions for perm in user_permissions)

    def can_improve(self) -> bool:
        """Check if user can trigger improvements."""
        return self.has_permission(DGMPermissions.DGM_IMPROVE.value)

    def can_rollback(self) -> bool:
        """Check if user can rollback improvements."""
        return self.has_permission(DGMPermissions.DGM_ROLLBACK.value)

    def can_admin(self) -> bool:
        """Check if user has admin permissions."""
        return self.is_admin or self.has_permission(DGMPermissions.DGM_ADMIN.value)

    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "roles": [{"name": role.name, "permissions": role.permissions} for role in self.roles],
            "permissions": [
                {"name": perm.name, "description": perm.description} for perm in self.permissions
            ],
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "all_permissions": self.get_all_permissions(),
            "is_dgm_user": self.is_dgm_user(),
            "can_improve": self.can_improve(),
            "can_rollback": self.can_rollback(),
            "can_admin": self.can_admin(),
        }


@dataclass
class AuthContext:
    """Authentication context for requests."""

    user: User
    token: str
    permissions: List[str]
    roles: List[str]
    is_service_account: bool = False
    service_name: Optional[str] = None

    def has_permission(self, permission: str) -> bool:
        """Check if context has permission."""
        return permission in self.permissions or self.user.has_permission(permission)

    def require_permission(self, permission: str) -> bool:
        """Require specific permission, raise exception if not present."""
        if not self.has_permission(permission):
            raise PermissionError(f"Permission required: {permission}")
        return True


class AuthenticationError(Exception):
    """Authentication failed."""

    pass


class AuthorizationError(Exception):
    """Authorization failed."""

    pass


class TokenExpiredError(AuthenticationError):
    """Token has expired."""

    pass


class InvalidTokenError(AuthenticationError):
    """Token is invalid."""

    pass


class InsufficientPermissionsError(AuthorizationError):
    """User lacks required permissions."""

    pass
