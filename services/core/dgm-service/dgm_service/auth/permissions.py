"""
Permission system for DGM Service.

Implements role-based access control (RBAC) with fine-grained
permissions for DGM operations and constitutional compliance.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .models import DGMPermissions, User

logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """Types of resources that can be protected."""

    IMPROVEMENT = "improvement"
    ARCHIVE = "archive"
    METRICS = "metrics"
    CONSTITUTIONAL = "constitutional"
    BANDIT = "bandit"
    SYSTEM = "system"
    SERVICE = "service"


class ActionType(Enum):
    """Types of actions that can be performed."""

    READ = "read"
    WRITE = "write"
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    ADMIN = "admin"


@dataclass
class PermissionRule:
    """Permission rule definition."""

    resource: ResourceType
    action: ActionType
    conditions: dict[str, Any] | None = None
    description: str | None = None


class PermissionChecker:
    """
    Permission checker for DGM operations.

    Provides fine-grained access control with support for
    resource-based permissions and conditional access.
    """

    def __init__(self):
        # Define permission rules
        self.permission_rules = self._define_permission_rules()

        # Define role hierarchies
        self.role_hierarchy = {
            "dgm_admin": ["dgm_operator", "dgm_viewer"],
            "dgm_operator": ["dgm_viewer"],
            "dgm_viewer": [],
            "constitutional_admin": [
                "constitutional_operator",
                "constitutional_viewer",
            ],
            "constitutional_operator": ["constitutional_viewer"],
            "constitutional_viewer": [],
            "system_admin": ["dgm_admin", "constitutional_admin"],
            "admin": ["system_admin"],
        }

    def _define_permission_rules(self) -> dict[str, PermissionRule]:
        """Define all permission rules."""
        rules = {}

        # DGM permissions
        rules[DGMPermissions.DGM_READ.value] = PermissionRule(
            ResourceType.IMPROVEMENT,
            ActionType.READ,
            description="Read DGM improvement data",
        )

        rules[DGMPermissions.DGM_STATUS.value] = PermissionRule(
            ResourceType.IMPROVEMENT,
            ActionType.READ,
            description="View DGM status and progress",
        )

        rules[DGMPermissions.DGM_IMPROVE.value] = PermissionRule(
            ResourceType.IMPROVEMENT,
            ActionType.CREATE,
            description="Trigger new improvements",
        )

        rules[DGMPermissions.DGM_CANCEL.value] = PermissionRule(
            ResourceType.IMPROVEMENT,
            ActionType.UPDATE,
            description="Cancel running improvements",
        )

        rules[DGMPermissions.DGM_ROLLBACK.value] = PermissionRule(
            ResourceType.IMPROVEMENT,
            ActionType.EXECUTE,
            description="Rollback completed improvements",
        )

        rules[DGMPermissions.DGM_ADMIN.value] = PermissionRule(
            ResourceType.IMPROVEMENT,
            ActionType.ADMIN,
            description="Full DGM administrative access",
        )

        # Archive permissions
        rules[DGMPermissions.DGM_ARCHIVE_READ.value] = PermissionRule(
            ResourceType.ARCHIVE,
            ActionType.READ,
            description="Read improvement archive",
        )

        rules[DGMPermissions.DGM_ARCHIVE_WRITE.value] = PermissionRule(
            ResourceType.ARCHIVE,
            ActionType.WRITE,
            description="Modify improvement archive",
        )

        # Metrics permissions
        rules[DGMPermissions.DGM_METRICS_READ.value] = PermissionRule(
            ResourceType.METRICS,
            ActionType.READ,
            description="Read performance metrics",
        )

        # Constitutional permissions
        rules[DGMPermissions.CONSTITUTIONAL_READ.value] = PermissionRule(
            ResourceType.CONSTITUTIONAL,
            ActionType.READ,
            description="Read constitutional compliance data",
        )

        rules[DGMPermissions.CONSTITUTIONAL_VALIDATE.value] = PermissionRule(
            ResourceType.CONSTITUTIONAL,
            ActionType.EXECUTE,
            description="Validate constitutional compliance",
        )

        rules[DGMPermissions.CONSTITUTIONAL_REPORT.value] = PermissionRule(
            ResourceType.CONSTITUTIONAL,
            ActionType.CREATE,
            description="Report constitutional violations",
        )

        # Bandit algorithm permissions
        rules[DGMPermissions.BANDIT_READ.value] = PermissionRule(
            ResourceType.BANDIT,
            ActionType.READ,
            description="Read bandit algorithm data",
        )

        rules[DGMPermissions.BANDIT_CONFIGURE.value] = PermissionRule(
            ResourceType.BANDIT,
            ActionType.UPDATE,
            description="Configure bandit algorithms",
        )

        # System permissions
        rules[DGMPermissions.DGM_CONFIG.value] = PermissionRule(
            ResourceType.SYSTEM,
            ActionType.UPDATE,
            description="Configure DGM system settings",
        )

        rules[DGMPermissions.DGM_SYSTEM.value] = PermissionRule(
            ResourceType.SYSTEM,
            ActionType.ADMIN,
            description="System-level DGM operations",
        )

        # Service permissions
        rules[DGMPermissions.SERVICE_HEALTH.value] = PermissionRule(
            ResourceType.SERVICE, ActionType.READ, description="Check service health"
        )

        rules[DGMPermissions.SERVICE_METRICS.value] = PermissionRule(
            ResourceType.SERVICE, ActionType.READ, description="Read service metrics"
        )

        return rules

    def check_permission(
        self,
        user: User,
        permission: str,
        resource_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> bool:
        """
        Check if user has permission for a specific action.

        Args:
            user: User to check permissions for
            permission: Permission name to check
            resource_id: Optional specific resource ID
            context: Optional context for conditional permissions

        Returns:
            True if user has permission, False otherwise
        """
        try:
            # Admin users have all permissions
            if user.is_admin or user.has_permission("admin"):
                return True

            # Check direct permission
            if user.has_permission(permission):
                return self._check_conditions(user, permission, resource_id, context)

            # Check inherited permissions from role hierarchy
            user_roles = [role.name for role in user.roles]
            for role in user_roles:
                if self._role_has_permission(role, permission):
                    return self._check_conditions(
                        user, permission, resource_id, context
                    )

            return False

        except Exception as e:
            logger.error(f"Permission check failed: {e}")
            return False

    def _role_has_permission(self, role: str, permission: str) -> bool:
        """Check if role has permission through hierarchy."""
        # This would typically query a role-permission mapping
        # For now, implement basic role-based permissions

        role_permissions = {
            "dgm_viewer": [
                DGMPermissions.DGM_READ.value,
                DGMPermissions.DGM_STATUS.value,
                DGMPermissions.DGM_ARCHIVE_READ.value,
                DGMPermissions.DGM_METRICS_READ.value,
                DGMPermissions.SERVICE_HEALTH.value,
            ],
            "dgm_operator": [
                DGMPermissions.DGM_IMPROVE.value,
                DGMPermissions.DGM_CANCEL.value,
                DGMPermissions.CONSTITUTIONAL_VALIDATE.value,
                DGMPermissions.BANDIT_READ.value,
            ],
            "dgm_admin": [
                DGMPermissions.DGM_ROLLBACK.value,
                DGMPermissions.DGM_ADMIN.value,
                DGMPermissions.DGM_ARCHIVE_WRITE.value,
                DGMPermissions.DGM_CONFIG.value,
                DGMPermissions.DGM_SYSTEM.value,
                DGMPermissions.BANDIT_CONFIGURE.value,
            ],
            "constitutional_viewer": [DGMPermissions.CONSTITUTIONAL_READ.value],
            "constitutional_operator": [
                DGMPermissions.CONSTITUTIONAL_VALIDATE.value,
                DGMPermissions.CONSTITUTIONAL_REPORT.value,
            ],
        }

        # Check direct role permissions
        if role in role_permissions and permission in role_permissions[role]:
            return True

        # Check inherited permissions
        if role in self.role_hierarchy:
            for inherited_role in self.role_hierarchy[role]:
                if self._role_has_permission(inherited_role, permission):
                    return True

        return False

    def _check_conditions(
        self,
        user: User,
        permission: str,
        resource_id: str | None,
        context: dict[str, Any] | None,
    ) -> bool:
        """Check conditional permissions."""
        if permission not in self.permission_rules:
            return True  # No conditions defined

        rule = self.permission_rules[permission]
        if not rule.conditions:
            return True  # No conditions to check

        # Implement condition checking logic
        # For example: time-based access, resource ownership, etc.

        # Check resource ownership
        if "owner_only" in rule.conditions and resource_id:
            # This would check if user owns the resource
            # For now, return True
            pass

        # Check time-based conditions
        if "time_restriction" in rule.conditions:
            # This would check time-based access rules
            # For now, return True
            pass

        return True

    def get_user_permissions(self, user: User) -> set[str]:
        """Get all permissions for a user."""
        permissions = set()

        # Add direct permissions
        permissions.update(user.get_all_permissions())

        # Add role-based permissions
        for role in user.roles:
            role_perms = self._get_role_permissions(role.name)
            permissions.update(role_perms)

        return permissions

    def _get_role_permissions(self, role: str) -> set[str]:
        """Get all permissions for a role."""
        permissions = set()

        # Get direct role permissions
        for permission, rule in self.permission_rules.items():
            if self._role_has_permission(role, permission):
                permissions.add(permission)

        return permissions

    def get_resource_permissions(
        self, user: User, resource_type: ResourceType
    ) -> dict[ActionType, bool]:
        """Get user permissions for a specific resource type."""
        permissions = {}

        for permission, rule in self.permission_rules.items():
            if rule.resource == resource_type:
                permissions[rule.action] = self.check_permission(user, permission)

        return permissions

    def can_access_improvement(self, user: User, improvement_id: str) -> bool:
        """Check if user can access a specific improvement."""
        return self.check_permission(
            user, DGMPermissions.DGM_READ.value, resource_id=improvement_id
        )

    def can_trigger_improvement(self, user: User) -> bool:
        """Check if user can trigger improvements."""
        return self.check_permission(user, DGMPermissions.DGM_IMPROVE.value)

    def can_rollback_improvement(self, user: User, improvement_id: str) -> bool:
        """Check if user can rollback a specific improvement."""
        return self.check_permission(
            user, DGMPermissions.DGM_ROLLBACK.value, resource_id=improvement_id
        )

    def can_validate_constitutional(self, user: User) -> bool:
        """Check if user can validate constitutional compliance."""
        return self.check_permission(user, DGMPermissions.CONSTITUTIONAL_VALIDATE.value)

    def can_admin_dgm(self, user: User) -> bool:
        """Check if user has DGM admin permissions."""
        return self.check_permission(user, DGMPermissions.DGM_ADMIN.value)

    def get_permission_summary(self, user: User) -> dict[str, Any]:
        """Get a summary of user permissions."""
        all_permissions = self.get_user_permissions(user)

        # Categorize permissions
        categories = {
            "dgm": [],
            "constitutional": [],
            "bandit": [],
            "system": [],
            "service": [],
        }

        for permission in all_permissions:
            if permission.startswith("dgm:"):
                categories["dgm"].append(permission)
            elif permission.startswith("constitutional:"):
                categories["constitutional"].append(permission)
            elif permission.startswith("bandit:"):
                categories["bandit"].append(permission)
            elif permission.startswith("service:"):
                categories["service"].append(permission)
            else:
                categories["system"].append(permission)

        return {
            "user_id": user.id,
            "username": user.username,
            "is_admin": user.is_admin,
            "total_permissions": len(all_permissions),
            "categories": categories,
            "roles": [role.name for role in user.roles],
            "can_improve": self.can_trigger_improvement(user),
            "can_rollback": self.can_rollback_improvement(user, "any"),
            "can_validate": self.can_validate_constitutional(user),
            "can_admin": self.can_admin_dgm(user),
        }
