"""
Enhanced Role-Based Access Control (RBAC) for ACGS

This module provides fine-grained permission management with hierarchical roles,
dynamic permissions, and constitutional compliance validation.
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Any, Union
from enum import Enum
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

import structlog
from pydantic import BaseModel

logger = structlog.get_logger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class PermissionLevel(Enum):
    """Permission access levels."""
    NONE = "none"
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    CONSTITUTIONAL = "constitutional"  # Highest level for constitutional changes


class ResourceType(Enum):
    """ACGS resource types."""
    USER = "user"
    POLICY = "policy"
    CONSTITUTIONAL_RULE = "constitutional_rule"
    GOVERNANCE_DECISION = "governance_decision"
    AUDIT_LOG = "audit_log"
    SYSTEM_CONFIG = "system_config"
    API_KEY = "api_key"
    VOTING_SESSION = "voting_session"
    SYNTHESIS_RESULT = "synthesis_result"
    VERIFICATION_PROOF = "verification_proof"
    STAKEHOLDER_INPUT = "stakeholder_input"


class ActionType(Enum):
    """Available actions on resources."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    APPROVE = "approve"
    REJECT = "reject"
    VOTE = "vote"
    SYNTHESIZE = "synthesize"
    VERIFY = "verify"
    ESCALATE = "escalate"


@dataclass
class Permission:
    """Individual permission definition."""
    resource: ResourceType
    action: ActionType
    level: PermissionLevel
    conditions: Dict[str, Any] = field(default_factory=dict)
    expires_at: Optional[datetime] = None
    granted_by: Optional[str] = None
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class Role:
    """Role definition with permissions and hierarchy."""
    name: str
    description: str
    permissions: Set[Permission] = field(default_factory=set)
    parent_roles: Set[str] = field(default_factory=set)
    is_system_role: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    constitutional_hash: str = CONSTITUTIONAL_HASH


@dataclass
class UserPermissions:
    """User's effective permissions combining role and direct permissions."""
    user_id: str
    roles: Set[str] = field(default_factory=set)
    direct_permissions: Set[Permission] = field(default_factory=set)
    effective_permissions: Set[Permission] = field(default_factory=set)
    last_calculated: datetime = field(default_factory=datetime.now)
    context: Dict[str, Any] = field(default_factory=dict)


class PermissionEvaluationContext:
    """Context for permission evaluation."""
    
    def __init__(
        self,
        user_id: str,
        resource_id: Optional[str] = None,
        resource_owner: Optional[str] = None,
        request_time: Optional[datetime] = None,
        client_ip: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ):
        self.user_id = user_id
        self.resource_id = resource_id
        self.resource_owner = resource_owner
        self.request_time = request_time or datetime.now()
        self.client_ip = client_ip
        self.additional_context = additional_context or {}
        self.constitutional_hash = CONSTITUTIONAL_HASH


class PermissionConditionEvaluator(ABC):
    """Abstract base class for permission condition evaluation."""
    
    @abstractmethod
    async def evaluate(
        self,
        permission: Permission,
        context: PermissionEvaluationContext
    ) -> bool:
        """Evaluate if permission conditions are met."""
        pass


class TimeBasedConditionEvaluator(PermissionConditionEvaluator):
    """Evaluates time-based permission conditions."""
    
    async def evaluate(
        self,
        permission: Permission,
        context: PermissionEvaluationContext
    ) -> bool:
        """Check time-based conditions like working hours, expiry."""
        conditions = permission.conditions
        
        # Check expiry
        if permission.expires_at and context.request_time > permission.expires_at:
            return False
        
        # Check time windows
        if "allowed_hours" in conditions:
            current_hour = context.request_time.hour
            allowed_hours = conditions["allowed_hours"]
            if current_hour not in allowed_hours:
                return False
        
        # Check date ranges
        if "valid_from" in conditions:
            valid_from = datetime.fromisoformat(conditions["valid_from"])
            if context.request_time < valid_from:
                return False
        
        if "valid_until" in conditions:
            valid_until = datetime.fromisoformat(conditions["valid_until"])
            if context.request_time > valid_until:
                return False
        
        return True


class OwnershipConditionEvaluator(PermissionConditionEvaluator):
    """Evaluates ownership-based permission conditions."""
    
    async def evaluate(
        self,
        permission: Permission,
        context: PermissionEvaluationContext
    ) -> bool:
        """Check ownership conditions."""
        conditions = permission.conditions
        
        # Owner-only access
        if conditions.get("owner_only", False):
            if not context.resource_owner or context.user_id != context.resource_owner:
                return False
        
        # Department/team-based access
        if "allowed_departments" in conditions:
            user_department = context.additional_context.get("user_department")
            if user_department not in conditions["allowed_departments"]:
                return False
        
        return True


class ConstitutionalConditionEvaluator(PermissionConditionEvaluator):
    """Evaluates constitutional compliance conditions."""
    
    async def evaluate(
        self,
        permission: Permission,
        context: PermissionEvaluationContext
    ) -> bool:
        """Check constitutional compliance conditions."""
        conditions = permission.conditions
        
        # Verify constitutional hash
        if permission.constitutional_hash != CONSTITUTIONAL_HASH:
            logger.warning(
                "Constitutional hash mismatch in permission",
                permission_hash=permission.constitutional_hash,
                expected_hash=CONSTITUTIONAL_HASH
            )
            return False
        
        # Check constitutional approval requirements
        if conditions.get("requires_constitutional_approval", False):
            approval_status = context.additional_context.get("constitutional_approval")
            if not approval_status:
                return False
        
        # Check multi-party approval for critical actions
        if conditions.get("requires_multi_party_approval", False):
            approvals = context.additional_context.get("approvals", [])
            required_approvals = conditions.get("required_approval_count", 3)
            if len(approvals) < required_approvals:
                return False
        
        return True


class EnhancedRBACManager:
    """Enhanced RBAC manager with fine-grained permissions."""
    
    def __init__(self):
        self.roles: Dict[str, Role] = {}
        self.user_permissions: Dict[str, UserPermissions] = {}
        self.permission_cache: Dict[str, Dict[str, bool]] = {}
        self.condition_evaluators: Dict[str, PermissionConditionEvaluator] = {
            "time": TimeBasedConditionEvaluator(),
            "ownership": OwnershipConditionEvaluator(),
            "constitutional": ConstitutionalConditionEvaluator()
        }
        self._initialize_system_roles()
    
    def _initialize_system_roles(self):
        """Initialize system-defined roles."""
        
        # Constitutional Administrator - Highest level
        constitutional_admin = Role(
            name="constitutional_admin",
            description="Constitutional administrator with full system access",
            is_system_role=True
        )
        constitutional_admin.permissions.add(Permission(
            resource=ResourceType.CONSTITUTIONAL_RULE,
            action=ActionType.CREATE,
            level=PermissionLevel.CONSTITUTIONAL
        ))
        constitutional_admin.permissions.add(Permission(
            resource=ResourceType.CONSTITUTIONAL_RULE,
            action=ActionType.UPDATE,
            level=PermissionLevel.CONSTITUTIONAL,
            conditions={"requires_multi_party_approval": True, "required_approval_count": 5}
        ))
        
        # Governance Administrator
        governance_admin = Role(
            name="governance_admin",
            description="Governance administrator with policy management access",
            is_system_role=True
        )
        governance_admin.permissions.add(Permission(
            resource=ResourceType.POLICY,
            action=ActionType.CREATE,
            level=PermissionLevel.ADMIN
        ))
        governance_admin.permissions.add(Permission(
            resource=ResourceType.GOVERNANCE_DECISION,
            action=ActionType.APPROVE,
            level=PermissionLevel.ADMIN
        ))
        
        # Stakeholder Representative
        stakeholder_rep = Role(
            name="stakeholder_representative",
            description="Stakeholder representative with voting and input rights",
            is_system_role=True
        )
        stakeholder_rep.permissions.add(Permission(
            resource=ResourceType.VOTING_SESSION,
            action=ActionType.VOTE,
            level=PermissionLevel.WRITE
        ))
        stakeholder_rep.permissions.add(Permission(
            resource=ResourceType.STAKEHOLDER_INPUT,
            action=ActionType.CREATE,
            level=PermissionLevel.WRITE
        ))
        
        # Policy Analyst
        policy_analyst = Role(
            name="policy_analyst",
            description="Policy analyst with synthesis and analysis rights",
            is_system_role=True
        )
        policy_analyst.permissions.add(Permission(
            resource=ResourceType.SYNTHESIS_RESULT,
            action=ActionType.CREATE,
            level=PermissionLevel.WRITE
        ))
        policy_analyst.permissions.add(Permission(
            resource=ResourceType.POLICY,
            action=ActionType.READ,
            level=PermissionLevel.READ
        ))
        
        # Auditor
        auditor = Role(
            name="auditor",
            description="System auditor with read-only access to audit logs",
            is_system_role=True
        )
        auditor.permissions.add(Permission(
            resource=ResourceType.AUDIT_LOG,
            action=ActionType.READ,
            level=PermissionLevel.READ
        ))
        auditor.permissions.add(Permission(
            resource=ResourceType.VERIFICATION_PROOF,
            action=ActionType.READ,
            level=PermissionLevel.READ
        ))
        
        # Regular User
        user_role = Role(
            name="user",
            description="Regular user with basic access rights",
            is_system_role=True
        )
        user_role.permissions.add(Permission(
            resource=ResourceType.USER,
            action=ActionType.READ,
            level=PermissionLevel.READ,
            conditions={"owner_only": True}
        ))
        
        # Store system roles
        for role in [constitutional_admin, governance_admin, stakeholder_rep, 
                    policy_analyst, auditor, user_role]:
            self.roles[role.name] = role
        
        logger.info(
            "System roles initialized",
            role_count=len(self.roles),
            constitutional_hash=CONSTITUTIONAL_HASH
        )
    
    async def assign_role_to_user(
        self,
        user_id: str,
        role_name: str,
        granted_by: str,
        expires_at: Optional[datetime] = None
    ) -> bool:
        """Assign a role to a user."""
        try:
            if role_name not in self.roles:
                raise ValueError(f"Role {role_name} does not exist")
            
            if user_id not in self.user_permissions:
                self.user_permissions[user_id] = UserPermissions(user_id=user_id)
            
            user_perms = self.user_permissions[user_id]
            user_perms.roles.add(role_name)
            
            # Recalculate effective permissions
            await self._recalculate_user_permissions(user_id)
            
            logger.info(
                "Role assigned to user",
                user_id=user_id,
                role=role_name,
                granted_by=granted_by,
                expires_at=expires_at,
                constitutional_hash=CONSTITUTIONAL_HASH
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to assign role to user",
                user_id=user_id,
                role=role_name,
                error=str(e)
            )
            return False
    
    async def grant_direct_permission(
        self,
        user_id: str,
        permission: Permission,
        granted_by: str
    ) -> bool:
        """Grant a direct permission to a user."""
        try:
            if user_id not in self.user_permissions:
                self.user_permissions[user_id] = UserPermissions(user_id=user_id)
            
            permission.granted_by = granted_by
            user_perms = self.user_permissions[user_id]
            user_perms.direct_permissions.add(permission)
            
            # Recalculate effective permissions
            await self._recalculate_user_permissions(user_id)
            
            logger.info(
                "Direct permission granted to user",
                user_id=user_id,
                resource=permission.resource.value,
                action=permission.action.value,
                level=permission.level.value,
                granted_by=granted_by,
                constitutional_hash=CONSTITUTIONAL_HASH
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to grant direct permission to user",
                user_id=user_id,
                error=str(e)
            )
            return False
    
    async def check_permission(
        self,
        user_id: str,
        resource: ResourceType,
        action: ActionType,
        context: Optional[PermissionEvaluationContext] = None
    ) -> bool:
        """Check if user has permission for a specific action on a resource."""
        try:
            if context is None:
                context = PermissionEvaluationContext(user_id=user_id)
            
            # Check cache first
            cache_key = f"{user_id}:{resource.value}:{action.value}"
            if cache_key in self.permission_cache.get(user_id, {}):
                cached_result = self.permission_cache[user_id][cache_key]
                logger.debug(
                    "Permission check from cache",
                    user_id=user_id,
                    resource=resource.value,
                    action=action.value,
                    result=cached_result
                )
                return cached_result
            
            # Get user permissions
            if user_id not in self.user_permissions:
                self._initialize_user_permissions(user_id)
                await self._recalculate_user_permissions(user_id)
            
            user_perms = self.user_permissions[user_id]
            
            # Check if permissions need recalculation
            if self._permissions_need_recalculation(user_perms):
                await self._recalculate_user_permissions(user_id)
                user_perms = self.user_permissions[user_id]
            
            # Find matching permissions
            matching_permissions = [
                perm for perm in user_perms.effective_permissions
                if perm.resource == resource and perm.action == action
            ]
            
            if not matching_permissions:
                result = False
            else:
                # Evaluate conditions for all matching permissions
                result = False
                for permission in matching_permissions:
                    if await self._evaluate_permission_conditions(permission, context):
                        result = True
                        break
            
            # Cache result
            if user_id not in self.permission_cache:
                self.permission_cache[user_id] = {}
            self.permission_cache[user_id][cache_key] = result
            
            logger.debug(
                "Permission check completed",
                user_id=user_id,
                resource=resource.value,
                action=action.value,
                result=result,
                matching_permissions=len(matching_permissions),
                constitutional_hash=CONSTITUTIONAL_HASH
            )
            
            return result
            
        except Exception as e:
            logger.error(
                "Permission check failed",
                user_id=user_id,
                resource=resource.value,
                action=action.value,
                error=str(e)
            )
            return False
    
    async def _recalculate_user_permissions(self, user_id: str):
        """Recalculate effective permissions for a user."""
        if user_id not in self.user_permissions:
            return
        
        user_perms = self.user_permissions[user_id]
        effective_permissions = set()
        
        # Add permissions from roles (including inherited)
        processed_roles = set()
        for role_name in user_perms.roles:
            await self._add_role_permissions(
                role_name, effective_permissions, processed_roles
            )
        
        # Add direct permissions
        effective_permissions.update(user_perms.direct_permissions)
        
        # Remove expired permissions
        current_time = datetime.now()
        valid_permissions = {
            perm for perm in effective_permissions
            if not perm.expires_at or perm.expires_at > current_time
        }
        
        user_perms.effective_permissions = valid_permissions
        user_perms.last_calculated = current_time
        
        # Clear cache for this user
        if user_id in self.permission_cache:
            del self.permission_cache[user_id]
        
        logger.debug(
            "User permissions recalculated",
            user_id=user_id,
            effective_permissions=len(valid_permissions),
            roles=len(user_perms.roles),
            direct_permissions=len(user_perms.direct_permissions)
        )
    
    async def _add_role_permissions(
        self,
        role_name: str,
        effective_permissions: Set[Permission],
        processed_roles: Set[str]
    ):
        """Recursively add permissions from role and parent roles."""
        if role_name in processed_roles or role_name not in self.roles:
            return
        
        processed_roles.add(role_name)
        role = self.roles[role_name]
        
        # Add role's permissions
        effective_permissions.update(role.permissions)
        
        # Add parent role permissions
        for parent_role in role.parent_roles:
            await self._add_role_permissions(
                parent_role, effective_permissions, processed_roles
            )
    
    async def _evaluate_permission_conditions(
        self,
        permission: Permission,
        context: PermissionEvaluationContext
    ) -> bool:
        """Evaluate all conditions for a permission."""
        if not permission.conditions:
            return True
        
        for condition_type, evaluator in self.condition_evaluators.items():
            if not await evaluator.evaluate(permission, context):
                return False
        
        return True
    
    def _initialize_user_permissions(self, user_id: str):
        """Initialize user permissions with default user role."""
        self.user_permissions[user_id] = UserPermissions(
            user_id=user_id,
            roles={"user"}  # Default role
        )
    
    def _permissions_need_recalculation(self, user_perms: UserPermissions) -> bool:
        """Check if user permissions need recalculation."""
        # Recalculate if older than 1 hour
        return (datetime.now() - user_perms.last_calculated) > timedelta(hours=1)
    
    def get_user_roles(self, user_id: str) -> Set[str]:
        """Get user's assigned roles."""
        if user_id not in self.user_permissions:
            return {"user"}  # Default role
        return self.user_permissions[user_id].roles.copy()
    
    def get_role_permissions(self, role_name: str) -> Set[Permission]:
        """Get permissions for a specific role."""
        if role_name not in self.roles:
            return set()
        return self.roles[role_name].permissions.copy()
    
    async def create_custom_role(
        self,
        name: str,
        description: str,
        permissions: List[Permission],
        parent_roles: Optional[List[str]] = None,
        created_by: str = "system"
    ) -> bool:
        """Create a custom role."""
        try:
            if name in self.roles:
                raise ValueError(f"Role {name} already exists")
            
            role = Role(
                name=name,
                description=description,
                permissions=set(permissions),
                parent_roles=set(parent_roles or []),
                is_system_role=False
            )
            
            self.roles[name] = role
            
            logger.info(
                "Custom role created",
                role_name=name,
                permissions_count=len(permissions),
                parent_roles=parent_roles or [],
                created_by=created_by,
                constitutional_hash=CONSTITUTIONAL_HASH
            )
            
            return True
            
        except Exception as e:
            logger.error(
                "Failed to create custom role",
                role_name=name,
                error=str(e)
            )
            return False


# Utility functions for easy integration
async def check_user_permission(
    rbac_manager: EnhancedRBACManager,
    user_id: str,
    resource: str,
    action: str,
    context: Optional[Dict[str, Any]] = None
) -> bool:
    """Utility function to check user permission with string parameters."""
    try:
        resource_type = ResourceType(resource)
        action_type = ActionType(action)
        
        evaluation_context = None
        if context:
            evaluation_context = PermissionEvaluationContext(
                user_id=user_id,
                **context
            )
        
        return await rbac_manager.check_permission(
            user_id, resource_type, action_type, evaluation_context
        )
    except ValueError as e:
        logger.error(f"Invalid resource or action type: {e}")
        return False


def create_permission(
    resource: str,
    action: str,
    level: str = "read",
    conditions: Optional[Dict[str, Any]] = None,
    expires_at: Optional[datetime] = None
) -> Permission:
    """Utility function to create permission with string parameters."""
    return Permission(
        resource=ResourceType(resource),
        action=ActionType(action),
        level=PermissionLevel(level),
        conditions=conditions or {},
        expires_at=expires_at
    )