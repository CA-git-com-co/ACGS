"""
Multi-Tenant Authentication and Authorization for ACGS

This module extends the existing authentication system to support
multi-tenant operations with tenant-scoped JWT tokens and RBAC.

Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import pathlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from shared.repositories.tenant_repository import TenantContext, TenantRepository
from sqlalchemy.ext.asyncio import AsyncSession

# Import user service client (use relative import or environment-based import)
try:
    from ...platform_services.authentication.auth_service.app.services.user_service import (
        UserServiceClient,
    )
except ImportError:
    # Fallback for different deployment structures
    import os
    import sys

    sys.path.append(os.path.join(pathlib.Path(__file__).parent, "../../../.."))
    from services.platform_services.authentication.auth_service.app.services.user_service import (
        UserServiceClient,
    )

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class TenantAuthError(Exception):
    """Base exception for tenant authentication errors."""


class TenantAccessDeniedError(TenantAuthError):
    """Raised when user is denied access to a tenant."""


class InvalidTenantTokenError(TenantAuthError):
    """Raised when tenant token is invalid or expired."""


class TenantTokenPayload(BaseModel):
    """Structure for tenant-aware JWT token payload."""

    sub: str  # User ID
    tenant_id: str | None = None
    organization_id: str | None = None
    role: str | None = None
    permissions: list[str] = Field(default_factory=list)
    access_level: str = "standard"
    security_level: str = "basic"
    constitutional_compliance: bool = True
    constitutional_hash: str = CONSTITUTIONAL_HASH
    exp: datetime
    iat: datetime
    jti: str  # JWT ID for revocation

    class Config:
        json_encoders = {datetime: lambda v: int(v.timestamp())}


class TenantUserInfo(BaseModel):
    """Extended user information with tenant context."""

    user_id: int
    username: str
    email: str
    tenant_id: uuid.UUID | None = None
    organization_id: uuid.UUID | None = None
    role: str = "user"
    permissions: list[str] = Field(default_factory=list)
    access_level: str = "standard"
    security_level: str = "basic"
    is_active: bool = True
    constitutional_compliance_required: bool = True
    last_login: datetime | None = None
    tenant_name: str | None = None
    organization_name: str | None = None


class TenantAuthenticationService:
    """
    Multi-tenant authentication service that extends the base auth
    with tenant-aware operations and constitutional compliance.
    """

    def __init__(
        self,
        secret_key: str,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30,
        refresh_token_expire_days: int = 30,
        user_service_url: str = "http://auth-service:8000/api/v1",
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.user_service = UserServiceClient(user_service_url)

    async def authenticate_user_for_tenant(
        self,
        session: AsyncSession,
        username: str,
        password: str,
        tenant_id: uuid.UUID | None = None,
    ) -> TenantUserInfo | None:
        """
        Authenticate a user and validate access to a specific tenant.

        If no tenant_id is provided, returns user info for the first
        available tenant. If tenant_id is provided, validates access.
        """
        # Authenticate the user using real user service
        user_auth_result = await self.user_service.authenticate_user(username, password)
        if not user_auth_result:
            raise TenantAccessDeniedError(f"Authentication failed for user {username}")

        user_data = user_auth_result.get("user")
        if not user_data:
            raise TenantAccessDeniedError(f"User data not found for {username}")

        real_user_id = user_data["id"]
        real_email = user_data["email"]
        real_username = user_data["username"]

        # Get user's tenant access
        tenant_repo = TenantRepository(session)

        if tenant_id:
            # Validate access to specific tenant
            access_info = await tenant_repo.validate_tenant_access(tenant_id, username)
            if not access_info["access"]:
                raise TenantAccessDeniedError(
                    f"User {username} cannot access tenant {tenant_id}"
                )

            tenant = access_info["tenant"]
            return TenantUserInfo(
                user_id=real_user_id,
                username=real_username,
                email=real_email,
                tenant_id=tenant.id,
                organization_id=tenant.organization_id,
                role=access_info["role"],
                permissions=access_info["permissions"],
                access_level=access_info["access_level"],
                security_level=access_info["security_level"],
                constitutional_compliance_required=access_info[
                    "constitutional_compliance_required"
                ],
                tenant_name=tenant.name,
                organization_name="Organization Name",  # Would be fetched from org service
            )
        # Get first available tenant for user
        user_tenants = await tenant_repo.get_user_tenants(real_user_id)
        if not user_tenants:
            raise TenantAccessDeniedError(f"User {username} has no tenant access")

        first_tenant_info = user_tenants[0]
        tenant = first_tenant_info["tenant"]

        return TenantUserInfo(
            user_id=real_user_id,
            username=real_username,
            email=real_email,
            tenant_id=tenant.id,
            organization_id=tenant.organization_id,
            role=first_tenant_info["role"],
            permissions=first_tenant_info["permissions"],
            access_level=first_tenant_info["access_level"],
            security_level=tenant.security_level,
            constitutional_compliance_required=tenant.constitutional_hash
            == CONSTITUTIONAL_HASH,
            tenant_name=tenant.name,
            organization_name="Organization Name",
        )

    def create_tenant_access_token(
        self, user_info: TenantUserInfo, expires_delta: timedelta | None = None
    ) -> str:
        """Create a JWT access token with tenant context."""

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=self.access_token_expire_minutes
            )

        payload = TenantTokenPayload(
            sub=str(user_info.user_id),
            tenant_id=str(user_info.tenant_id) if user_info.tenant_id else None,
            organization_id=(
                str(user_info.organization_id) if user_info.organization_id else None
            ),
            role=user_info.role,
            permissions=user_info.permissions,
            access_level=user_info.access_level,
            security_level=user_info.security_level,
            constitutional_compliance=user_info.constitutional_compliance_required,
            constitutional_hash=CONSTITUTIONAL_HASH,
            exp=expire,
            iat=datetime.now(timezone.utc),
            jti=str(uuid.uuid4()),
        ).dict()

        # Convert datetime objects to timestamps for JWT encoding
        payload["exp"] = int(expire.timestamp())
        payload["iat"] = int(datetime.now(timezone.utc).timestamp())

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def create_tenant_refresh_token(
        self, user_info: TenantUserInfo, expires_delta: timedelta | None = None
    ) -> str:
        """Create a JWT refresh token with tenant context."""

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                days=self.refresh_token_expire_days
            )

        payload = {
            "sub": str(user_info.user_id),
            "tenant_id": str(user_info.tenant_id) if user_info.tenant_id else None,
            "type": "refresh",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "exp": int(expire.timestamp()),
            "iat": int(datetime.now(timezone.utc).timestamp()),
            "jti": str(uuid.uuid4()),
        }

        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)

    def verify_tenant_token(self, token: str) -> TenantTokenPayload:
        """
        Verify and decode a tenant-aware JWT token.

        Returns the token payload with tenant context.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Validate constitutional hash
            if payload.get("constitutional_hash") != CONSTITUTIONAL_HASH:
                raise InvalidTenantTokenError("Constitutional hash validation failed")

            # Convert timestamps back to datetime objects
            exp_timestamp = payload.get("exp")
            iat_timestamp = payload.get("iat")

            if exp_timestamp:
                payload["exp"] = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
            if iat_timestamp:
                payload["iat"] = datetime.fromtimestamp(iat_timestamp, tz=timezone.utc)

            return TenantTokenPayload(**payload)

        except jwt.ExpiredSignatureError:
            raise InvalidTenantTokenError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise InvalidTenantTokenError(f"Invalid token: {e}")
        except Exception as e:
            raise InvalidTenantTokenError(f"Token validation failed: {e}")

    async def refresh_tenant_access_token(
        self, session: AsyncSession, refresh_token: str
    ) -> dict[str, str]:
        """
        Refresh an access token using a valid refresh token.

        Returns new access and refresh tokens.
        """
        try:
            # Verify refresh token
            payload = jwt.decode(
                refresh_token, self.secret_key, algorithms=[self.algorithm]
            )

            if payload.get("type") != "refresh":
                raise InvalidTenantTokenError("Invalid refresh token type")

            if payload.get("constitutional_hash") != CONSTITUTIONAL_HASH:
                raise InvalidTenantTokenError("Constitutional hash validation failed")

            user_id = int(payload.get("sub"))
            tenant_id_str = payload.get("tenant_id")
            tenant_id = uuid.UUID(tenant_id_str) if tenant_id_str else None

            # Get current user info for the tenant
            tenant_repo = TenantRepository(session)
            if tenant_id:
                access_info = await tenant_repo.validate_tenant_access(
                    tenant_id, user_id
                )
                if not access_info["access"]:
                    raise TenantAccessDeniedError("User no longer has access to tenant")

                tenant = access_info["tenant"]
                # Fetch real user data from user service
                user_profile = await self.user_service.get_user_profile(user_id)
                if not user_profile:
                    raise TenantAccessDeniedError("User profile not found")

                user_info = TenantUserInfo(
                    user_id=user_id,
                    username=user_profile["username"],
                    email=user_profile["email"],
                    tenant_id=tenant.id,
                    organization_id=tenant.organization_id,
                    role=access_info["role"],
                    permissions=access_info["permissions"],
                    access_level=access_info["access_level"],
                    security_level=access_info["security_level"],
                    constitutional_compliance_required=access_info[
                        "constitutional_compliance_required"
                    ],
                    tenant_name=tenant.name,
                )
            else:
                # Handle case where user has no specific tenant
                user_tenants = await tenant_repo.get_user_tenants(user_id)
                if not user_tenants:
                    raise TenantAccessDeniedError("User has no tenant access")

                first_tenant_info = user_tenants[0]
                tenant = first_tenant_info["tenant"]

                # Fetch real user data from user service
                user_profile = await self.user_service.get_user_profile(user_id)
                if not user_profile:
                    raise TenantAccessDeniedError("User profile not found")

                user_info = TenantUserInfo(
                    user_id=user_id,
                    username=user_profile["username"],
                    email=user_profile["email"],
                    tenant_id=tenant.id,
                    organization_id=tenant.organization_id,
                    role=first_tenant_info["role"],
                    permissions=first_tenant_info["permissions"],
                    access_level=first_tenant_info["access_level"],
                    security_level=tenant.security_level,
                    constitutional_compliance_required=tenant.constitutional_hash
                    == CONSTITUTIONAL_HASH,
                    tenant_name=tenant.name,
                )

            # Create new tokens
            new_access_token = self.create_tenant_access_token(user_info)
            new_refresh_token = self.create_tenant_refresh_token(user_info)

            return {
                "access_token": new_access_token,
                "refresh_token": new_refresh_token,
                "token_type": "bearer",
            }

        except jwt.ExpiredSignatureError:
            raise InvalidTenantTokenError("Refresh token has expired")
        except jwt.InvalidTokenError as e:
            raise InvalidTenantTokenError(f"Invalid refresh token: {e}")

    async def switch_tenant_context(
        self, session: AsyncSession, current_token: str, new_tenant_id: uuid.UUID
    ) -> dict[str, str]:
        """
        Switch user's tenant context by creating new tokens for a different tenant.

        Validates that the user has access to the new tenant.
        """
        # Verify current token
        current_payload = self.verify_tenant_token(current_token)
        user_id = int(current_payload.sub)

        # Validate access to new tenant
        tenant_repo = TenantRepository(session)
        access_info = await tenant_repo.validate_tenant_access(new_tenant_id, user_id)

        if not access_info["access"]:
            raise TenantAccessDeniedError(f"User cannot access tenant {new_tenant_id}")

        # Create user info for new tenant
        tenant = access_info["tenant"]
        # Fetch real user data from user service
        user_profile = await self.user_service.get_user_profile(user_id)
        if not user_profile:
            raise TenantAccessDeniedError("User profile not found")

        user_info = TenantUserInfo(
            user_id=user_id,
            username=user_profile["username"],
            email=user_profile["email"],
            tenant_id=tenant.id,
            organization_id=tenant.organization_id,
            role=access_info["role"],
            permissions=access_info["permissions"],
            access_level=access_info["access_level"],
            security_level=access_info["security_level"],
            constitutional_compliance_required=access_info[
                "constitutional_compliance_required"
            ],
            tenant_name=tenant.name,
        )

        # Create new tokens for the new tenant
        new_access_token = self.create_tenant_access_token(user_info)
        new_refresh_token = self.create_tenant_refresh_token(user_info)

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "tenant_id": str(tenant.id),
            "tenant_name": tenant.name,
            "organization_id": str(tenant.organization_id),
        }

    async def get_user_tenants(
        self, session: AsyncSession, token: str
    ) -> list[dict[str, Any]]:
        """
        Get all tenants that the authenticated user has access to.
        """
        # Verify token
        payload = self.verify_tenant_token(token)
        user_id = int(payload.sub)

        # Get user's tenants
        tenant_repo = TenantRepository(session)
        user_tenants = await tenant_repo.get_user_tenants(user_id)

        result = []
        for tenant_info in user_tenants:
            tenant = tenant_info["tenant"]
            result.append(
                {
                    "tenant_id": str(tenant.id),
                    "tenant_name": tenant.name,
                    "tenant_slug": tenant.slug,
                    "organization_id": str(tenant.organization_id),
                    "role": tenant_info["role"],
                    "access_level": tenant_info["access_level"],
                    "security_level": tenant.security_level,
                    "status": tenant.status,
                    "last_accessed_at": tenant_info["last_accessed_at"],
                }
            )

        return result


class TenantPermissionChecker:
    """
    Service for checking tenant-specific permissions and access control.
    """

    def __init__(self):
        self.permission_hierarchy = {
            "owner": ["admin", "write", "read"],
            "admin": ["write", "read"],
            "write": ["read"],
            "read": [],
        }

    def has_permission(
        self,
        user_permissions: list[str],
        required_permission: str,
        user_role: str | None = None,
    ) -> bool:
        """
        Check if user has the required permission.

        Supports both explicit permissions and role-based permissions.
        """
        # Check explicit permissions
        if required_permission in user_permissions:
            return True

        # Check role-based permissions
        if user_role and user_role in self.permission_hierarchy:
            role_permissions = self.permission_hierarchy[user_role]
            if required_permission in role_permissions:
                return True

        return False

    def can_access_resource(
        self,
        user_context: TenantContext,
        resource_type: str,
        resource_action: str,
        resource_tenant_id: uuid.UUID | None = None,
    ) -> bool:
        """
        Check if user can access a specific resource.

        Enforces tenant isolation by ensuring users can only access
        resources within their tenant context.
        """
        # Ensure resource belongs to user's tenant
        if resource_tenant_id and resource_tenant_id != user_context.tenant_id:
            return False

        # Check permission for resource action
        required_permission = f"{resource_type}:{resource_action}"
        return required_permission in (user_context.permissions or [])

    def get_effective_permissions(
        self, user_role: str, explicit_permissions: list[str]
    ) -> list[str]:
        """
        Get all effective permissions for a user including role-based permissions.
        """
        all_permissions = set(explicit_permissions)

        # Add role-based permissions
        if user_role in self.permission_hierarchy:
            all_permissions.update(self.permission_hierarchy[user_role])

        return list(all_permissions)


# Utility functions for tenant authentication
async def create_tenant_context_from_token(
    session: AsyncSession, token: str, auth_service: TenantAuthenticationService
) -> TenantContext:
    """
    Create a TenantContext from a JWT token.

    Validates the token and creates the appropriate context for database operations.
    """
    payload = auth_service.verify_tenant_token(token)

    if not payload.tenant_id:
        raise TenantAccessDeniedError("Token does not contain tenant context")

    tenant_id = uuid.UUID(payload.tenant_id)
    user_id = int(payload.sub)
    organization_id = (
        uuid.UUID(payload.organization_id) if payload.organization_id else None
    )

    return TenantContext(
        tenant_id=tenant_id,
        user_id=user_id,
        organization_id=organization_id,
        security_level=payload.security_level,
        constitutional_compliance_required=payload.constitutional_compliance,
    )


def get_tenant_auth_service(
    secret_key: str, user_service_url: str = "http://auth-service:8000/api/v1"
) -> TenantAuthenticationService:
    """Factory function to create a tenant authentication service."""
    return TenantAuthenticationService(
        secret_key=secret_key,
        algorithm="HS256",
        access_token_expire_minutes=30,
        refresh_token_expire_days=30,
        user_service_url=user_service_url,
    )
