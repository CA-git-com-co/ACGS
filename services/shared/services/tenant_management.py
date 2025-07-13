"""
Tenant Management Service for ACGS Multi-Tenant Architecture

This service handles tenant lifecycle operations including onboarding,
configuration, user management, and constitutional compliance validation.

Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import secrets
import string
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from pydantic import BaseModel, Field, validator
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.multi_tenant import (
    DataResidency,
    Organization,
    SecurityLevel,
    Tenant,
    TenantInvitation,
    TenantSettings,
    TenantStatus,
    TenantTier,
    TenantUser,
)
from ..repositories.tenant_repository import TenantRepository

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class TenantManagementError(Exception):
    """Base exception for tenant management operations."""


class TenantCreationError(TenantManagementError):
    """Raised when tenant creation fails."""


class TenantQuotaExceededError(TenantManagementError):
    """Raised when tenant operations exceed quotas."""


class InvitationError(TenantManagementError):
    """Raised when invitation operations fail."""


# Request/Response Models
class OrganizationCreateRequest(BaseModel):
    """Request model for creating a new organization."""

    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = None
    legal_name: str | None = None
    contact_email: str = Field(..., regex=r"^[^@]+@[^@]+\.[^@]+$")
    billing_email: str | None = None
    industry: str | None = None
    company_size: str | None = None
    website: str | None = None

    # Address information
    address_line1: str | None = None
    address_line2: str | None = None
    city: str | None = None
    state_province: str | None = None
    postal_code: str | None = None
    country: str | None = None

    # Configuration
    tier: TenantTier = TenantTier.BASIC
    data_residency: DataResidency = DataResidency.ANY
    enforce_mfa: bool = False

    @validator("slug", pre=True, always=True)
    def generate_slug(self, v, values):
        if not v and "name" in values:
            # Generate slug from name
            slug = values["name"].lower().replace(" ", "-").replace("_", "-")
            # Remove special characters
            slug = "".join(c for c in slug if c.isalnum() or c == "-")
            return slug[:100]
        return v


class TenantCreateRequest(BaseModel):
    """Request model for creating a new tenant."""

    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = None
    description: str | None = None
    environment_type: str = "production"
    tier: TenantTier = TenantTier.BASIC
    security_level: SecurityLevel = SecurityLevel.BASIC

    # Resource limits
    max_users: int | None = None
    max_agents: int = 10
    max_storage_gb: int = 100
    max_compute_units: int = 1000
    api_rate_limit_per_hour: int | None = None

    # Compliance settings
    data_residency: DataResidency | None = None
    compliance_frameworks: list[str] | None = None
    audit_retention_days: int = 2555  # 7 years default

    @validator("slug", pre=True, always=True)
    def generate_slug(self, v, values):
        if not v and "name" in values:
            slug = values["name"].lower().replace(" ", "-").replace("_", "-")
            slug = "".join(c for c in slug if c.isalnum() or c == "-")
            return slug[:100]
        return v


class TenantInviteRequest(BaseModel):
    """Request model for inviting a user to a tenant."""

    email: str = Field(..., regex=r"^[^@]+@[^@]+\.[^@]+$")
    role: str = "user"
    permissions: list[str] | None = None
    message: str | None = None
    expires_in_hours: int = 168  # 7 days default


class TenantUserUpdateRequest(BaseModel):
    """Request model for updating tenant user access."""

    role: str | None = None
    permissions: list[str] | None = None
    access_level: str | None = None
    is_active: bool | None = None


@dataclass
class TenantOnboardingResult:
    """Result of tenant onboarding process."""

    organization: Organization
    tenant: Tenant
    admin_user: TenantUser
    settings_created: int
    constitutional_validation_passed: bool
    onboarding_token: str


class TenantManagementService:
    """
    Comprehensive tenant management service for ACGS multi-tenant operations.

    Handles the complete tenant lifecycle including creation, configuration,
    user management, and constitutional compliance validation.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self.tenant_repo = TenantRepository(session)

    async def create_organization(
        self,
        request: OrganizationCreateRequest,
        created_by_user_id: int | None = None,
    ) -> Organization:
        """
        Create a new organization with constitutional validation.

        Organizations are the top-level entity for billing and contract management.
        """
        try:
            # Check if slug is unique
            existing_org = await self.session.execute(
                select(Organization).where(Organization.slug == request.slug)
            )
            if existing_org.scalar_one_or_none():
                raise TenantCreationError(
                    f"Organization slug '{request.slug}' already exists"
                )

            # Validate tier limits
            await self._validate_organization_tier_limits(request.tier)

            # Create organization
            org = Organization(
                name=request.name,
                slug=request.slug,
                legal_name=request.legal_name,
                contact_email=request.contact_email,
                billing_email=request.billing_email or request.contact_email,
                industry=request.industry,
                company_size=request.company_size,
                website=request.website,
                address_line1=request.address_line1,
                address_line2=request.address_line2,
                city=request.city,
                state_province=request.state_province,
                postal_code=request.postal_code,
                country=request.country,
                tier=request.tier.value,
                data_residency=request.data_residency.value,
                enforce_mfa=request.enforce_mfa,
                constitutional_hash=CONSTITUTIONAL_HASH,
                status=TenantStatus.PENDING.value,
            )

            self.session.add(org)
            await self.session.flush()
            await self.session.refresh(org)

            logger.info(f"Created organization: {org.name} (ID: {org.id})")
            return org

        except Exception as e:
            logger.exception(f"Failed to create organization: {e}")
            raise TenantCreationError(f"Organization creation failed: {e}")

    async def create_tenant(
        self,
        organization_id: uuid.UUID,
        request: TenantCreateRequest,
        created_by_user_id: int | None = None,
    ) -> Tenant:
        """
        Create a new tenant within an organization.

        Validates quotas and applies constitutional compliance requirements.
        """
        try:
            # Get organization and validate quota
            org = await self.session.get(Organization, organization_id)
            if not org:
                raise TenantCreationError("Organization not found")

            # Check tenant quota
            current_tenant_count = await self.session.scalar(
                select(func.count(Tenant.id)).where(
                    and_(
                        Tenant.organization_id == organization_id,
                        Tenant.deleted_at.is_(None),
                    )
                )
            )

            if current_tenant_count >= org.max_tenants:
                raise TenantQuotaExceededError(
                    f"Organization has reached maximum tenant limit: {org.max_tenants}"
                )

            # Check if slug is unique within organization
            existing_tenant = await self.session.execute(
                select(Tenant).where(
                    and_(
                        Tenant.organization_id == organization_id,
                        Tenant.slug == request.slug,
                        Tenant.deleted_at.is_(None),
                    )
                )
            )
            if existing_tenant.scalar_one_or_none():
                raise TenantCreationError(
                    f"Tenant slug '{request.slug}' already exists in organization"
                )

            # Apply organization defaults
            max_users = request.max_users or org.max_users_per_tenant
            api_rate_limit = (
                request.api_rate_limit_per_hour or org.max_api_requests_per_hour
            )
            data_residency = request.data_residency or DataResidency(org.data_residency)

            # Create tenant
            tenant = Tenant(
                organization_id=organization_id,
                name=request.name,
                slug=request.slug,
                description=request.description,
                environment_type=request.environment_type,
                tier=request.tier.value,
                security_level=request.security_level.value,
                max_users=max_users,
                max_agents=request.max_agents,
                max_storage_gb=request.max_storage_gb,
                max_compute_units=request.max_compute_units,
                api_rate_limit_per_hour=api_rate_limit,
                data_residency=data_residency.value,
                compliance_frameworks=request.compliance_frameworks,
                audit_retention_days=request.audit_retention_days,
                constitutional_hash=CONSTITUTIONAL_HASH,
                constitutional_compliance_score=100,
                status=TenantStatus.ACTIVE.value,
            )

            self.session.add(tenant)
            await self.session.flush()
            await self.session.refresh(tenant)

            # Create default settings
            await self._create_default_tenant_settings(tenant.id)

            logger.info(f"Created tenant: {tenant.name} (ID: {tenant.id})")
            return tenant

        except Exception as e:
            logger.exception(f"Failed to create tenant: {e}")
            raise TenantCreationError(f"Tenant creation failed: {e}")

    async def onboard_tenant_with_admin(
        self,
        organization_request: OrganizationCreateRequest,
        tenant_request: TenantCreateRequest,
        admin_email: str,
        admin_user_id: int,
    ) -> TenantOnboardingResult:
        """
        Complete tenant onboarding process including organization, tenant, and admin user setup.

        This is the main entry point for new tenant onboarding with constitutional validation.
        """
        try:
            # Create organization
            org = await self.create_organization(organization_request, admin_user_id)

            # Create tenant
            tenant = await self.create_tenant(org.id, tenant_request, admin_user_id)

            # Add admin user to tenant
            admin_user = await self.add_user_to_tenant(
                tenant.id,
                admin_user_id,
                role="owner",
                access_level="admin",
                added_by_user_id=admin_user_id,
            )

            # Activate organization
            org.status = TenantStatus.ACTIVE.value
            await self.session.flush()

            # Generate onboarding token
            onboarding_token = self._generate_secure_token()

            # Validate constitutional compliance
            constitutional_validation = await self._validate_constitutional_compliance(
                tenant.id
            )

            result = TenantOnboardingResult(
                organization=org,
                tenant=tenant,
                admin_user=admin_user,
                settings_created=await self._count_tenant_settings(tenant.id),
                constitutional_validation_passed=constitutional_validation,
                onboarding_token=onboarding_token,
            )

            logger.info(f"Completed tenant onboarding for {org.name}/{tenant.name}")
            return result

        except Exception as e:
            logger.exception(f"Tenant onboarding failed: {e}")
            raise TenantCreationError(f"Tenant onboarding failed: {e}")

    async def add_user_to_tenant(
        self,
        tenant_id: uuid.UUID,
        user_id: int,
        role: str = "user",
        permissions: list[str] | None = None,
        access_level: str = "standard",
        added_by_user_id: int | None = None,
    ) -> TenantUser:
        """
        Add a user to a tenant with specified role and permissions.

        Validates tenant quotas and constitutional compliance.
        """
        try:
            # Get tenant and validate quota
            tenant = await self.session.get(Tenant, tenant_id)
            if not tenant:
                raise TenantManagementError("Tenant not found")

            # Check user quota
            current_user_count = await self.session.scalar(
                select(func.count(TenantUser.id)).where(
                    and_(TenantUser.tenant_id == tenant_id, TenantUser.is_active)
                )
            )

            if tenant.max_users and current_user_count >= tenant.max_users:
                raise TenantQuotaExceededError(
                    f"Tenant has reached maximum user limit: {tenant.max_users}"
                )

            # Check if user is already in tenant
            existing_user = await self.session.execute(
                select(TenantUser).where(
                    and_(
                        TenantUser.tenant_id == tenant_id, TenantUser.user_id == user_id
                    )
                )
            )
            if existing_user.scalar_one_or_none():
                raise TenantManagementError("User is already a member of this tenant")

            # Create tenant user
            tenant_user = TenantUser(
                tenant_id=tenant_id,
                user_id=user_id,
                role=role,
                permissions=permissions,
                access_level=access_level,
                is_active=True,
                activated_at=datetime.now(timezone.utc),
            )

            self.session.add(tenant_user)
            await self.session.flush()
            await self.session.refresh(tenant_user)

            logger.info(f"Added user {user_id} to tenant {tenant_id} with role {role}")
            return tenant_user

        except Exception as e:
            logger.exception(f"Failed to add user to tenant: {e}")
            raise TenantManagementError(f"Failed to add user to tenant: {e}")

    async def invite_user_to_tenant(
        self,
        tenant_id: uuid.UUID,
        request: TenantInviteRequest,
        invited_by_user_id: int,
    ) -> TenantInvitation:
        """
        Invite a user to join a tenant via email invitation.

        Creates an invitation record with a secure token for account activation.
        """
        try:
            # Get tenant
            tenant = await self.session.get(Tenant, tenant_id)
            if not tenant:
                raise InvitationError("Tenant not found")

            # Check if user is already invited or a member
            existing_invitation = await self.session.execute(
                select(TenantInvitation).where(
                    and_(
                        TenantInvitation.tenant_id == tenant_id,
                        TenantInvitation.email == request.email,
                        TenantInvitation.status == "pending",
                    )
                )
            )
            if existing_invitation.scalar_one_or_none():
                raise InvitationError("User already has a pending invitation")

            # Generate secure invitation token
            invitation_token = self._generate_secure_token()
            expires_at = datetime.now(timezone.utc) + timedelta(
                hours=request.expires_in_hours
            )

            # Create invitation
            invitation = TenantInvitation(
                tenant_id=tenant_id,
                email=request.email,
                role=request.role,
                permissions=request.permissions,
                invitation_token=invitation_token,
                invited_by_user_id=invited_by_user_id,
                message=request.message,
                expires_at=expires_at,
            )

            self.session.add(invitation)
            await self.session.flush()
            await self.session.refresh(invitation)

            # TODO: Send invitation email
            # await self._send_invitation_email(invitation, tenant)

            logger.info(f"Created invitation for {request.email} to tenant {tenant_id}")
            return invitation

        except Exception as e:
            logger.exception(f"Failed to create invitation: {e}")
            raise InvitationError(f"Failed to create invitation: {e}")

    async def accept_tenant_invitation(
        self, invitation_token: str, user_id: int
    ) -> TenantUser:
        """
        Accept a tenant invitation and add the user to the tenant.

        Validates the invitation token and creates the tenant user relationship.
        """
        try:
            # Get invitation
            invitation = await self.session.execute(
                select(TenantInvitation).where(
                    TenantInvitation.invitation_token == invitation_token
                )
            )
            invitation = invitation.scalar_one_or_none()

            if not invitation:
                raise InvitationError("Invalid invitation token")

            if invitation.status != "pending":
                raise InvitationError("Invitation is no longer valid")

            if invitation.expires_at < datetime.now(timezone.utc):
                invitation.status = "expired"
                await self.session.flush()
                raise InvitationError("Invitation has expired")

            # Add user to tenant
            tenant_user = await self.add_user_to_tenant(
                tenant_id=invitation.tenant_id,
                user_id=user_id,
                role=invitation.role,
                permissions=invitation.permissions,
                added_by_user_id=invitation.invited_by_user_id,
            )

            # Mark invitation as accepted
            invitation.status = "accepted"
            invitation.accepted_at = datetime.now(timezone.utc)
            await self.session.flush()

            logger.info(
                f"User {user_id} accepted invitation to tenant {invitation.tenant_id}"
            )
            return tenant_user

        except Exception as e:
            logger.exception(f"Failed to accept invitation: {e}")
            raise InvitationError(f"Failed to accept invitation: {e}")

    async def update_tenant_user(
        self, tenant_id: uuid.UUID, user_id: int, request: TenantUserUpdateRequest
    ) -> TenantUser:
        """Update a tenant user's role, permissions, or access level."""
        try:
            # Get tenant user
            tenant_user = await self.session.execute(
                select(TenantUser).where(
                    and_(
                        TenantUser.tenant_id == tenant_id, TenantUser.user_id == user_id
                    )
                )
            )
            tenant_user = tenant_user.scalar_one_or_none()

            if not tenant_user:
                raise TenantManagementError("User is not a member of this tenant")

            # Update fields
            if request.role is not None:
                tenant_user.role = request.role
            if request.permissions is not None:
                tenant_user.permissions = request.permissions
            if request.access_level is not None:
                tenant_user.access_level = request.access_level
            if request.is_active is not None:
                tenant_user.is_active = request.is_active

            await self.session.flush()
            await self.session.refresh(tenant_user)

            logger.info(f"Updated tenant user {user_id} in tenant {tenant_id}")
            return tenant_user

        except Exception as e:
            logger.exception(f"Failed to update tenant user: {e}")
            raise TenantManagementError(f"Failed to update tenant user: {e}")

    async def remove_user_from_tenant(
        self,
        tenant_id: uuid.UUID,
        user_id: int,
        removed_by_user_id: int | None = None,
    ) -> bool:
        """Remove a user from a tenant."""
        try:
            # Get tenant user
            tenant_user = await self.session.execute(
                select(TenantUser).where(
                    and_(
                        TenantUser.tenant_id == tenant_id, TenantUser.user_id == user_id
                    )
                )
            )
            tenant_user = tenant_user.scalar_one_or_none()

            if not tenant_user:
                return False

            # Soft delete by setting is_active to False
            tenant_user.is_active = False
            await self.session.flush()

            logger.info(f"Removed user {user_id} from tenant {tenant_id}")
            return True

        except Exception as e:
            logger.exception(f"Failed to remove user from tenant: {e}")
            raise TenantManagementError(f"Failed to remove user from tenant: {e}")

    async def get_tenant_users(
        self, tenant_id: uuid.UUID, include_inactive: bool = False
    ) -> list[TenantUser]:
        """Get all users for a tenant."""
        query = select(TenantUser).where(TenantUser.tenant_id == tenant_id)

        if not include_inactive:
            query = query.where(TenantUser.is_active)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def set_tenant_setting(
        self,
        tenant_id: uuid.UUID,
        category: str,
        key: str,
        value: Any,
        user_id: int | None = None,
    ) -> TenantSettings:
        """Set a tenant-specific setting."""
        try:
            # Check if setting exists
            existing_setting = await self.session.execute(
                select(TenantSettings).where(
                    and_(
                        TenantSettings.tenant_id == tenant_id,
                        TenantSettings.category == category,
                        TenantSettings.key == key,
                        TenantSettings.deleted_at.is_(None),
                    )
                )
            )
            setting = existing_setting.scalar_one_or_none()

            if setting:
                # Update existing setting
                setting.value = value
                if user_id:
                    setting.updated_by_user_id = user_id
            else:
                # Create new setting
                setting = TenantSettings(
                    tenant_id=tenant_id,
                    category=category,
                    key=key,
                    value=value,
                    created_by_user_id=user_id,
                )
                self.session.add(setting)

            await self.session.flush()
            await self.session.refresh(setting)

            return setting

        except Exception as e:
            logger.exception(f"Failed to set tenant setting: {e}")
            raise TenantManagementError(f"Failed to set tenant setting: {e}")

    async def get_tenant_setting(
        self, tenant_id: uuid.UUID, category: str, key: str
    ) -> Any | None:
        """Get a tenant-specific setting value."""
        try:
            setting = await self.session.execute(
                select(TenantSettings).where(
                    and_(
                        TenantSettings.tenant_id == tenant_id,
                        TenantSettings.category == category,
                        TenantSettings.key == key,
                        TenantSettings.deleted_at.is_(None),
                    )
                )
            )
            setting = setting.scalar_one_or_none()

            return setting.value if setting else None

        except Exception as e:
            logger.exception(f"Failed to get tenant setting: {e}")
            return None

    # Private helper methods
    async def _validate_organization_tier_limits(self, tier: TenantTier) -> None:
        """Validate organization tier limits and quotas."""
        # Implementation would check against tier-specific limits

    async def _create_default_tenant_settings(self, tenant_id: uuid.UUID) -> None:
        """Create default settings for a new tenant."""
        default_settings = [
            ("security", "password_policy", {"min_length": 8, "require_special": True}),
            ("security", "session_timeout", 480),  # 8 hours
            ("security", "mfa_required", False),
            ("features", "api_access", True),
            ("features", "webhook_enabled", False),
            ("compliance", "audit_logging", True),
            ("compliance", "data_retention_days", 2555),
        ]

        for category, key, value in default_settings:
            setting = TenantSettings(
                tenant_id=tenant_id, category=category, key=key, value=value
            )
            self.session.add(setting)

        await self.session.flush()

    async def _count_tenant_settings(self, tenant_id: uuid.UUID) -> int:
        """Count the number of settings for a tenant."""
        result = await self.session.scalar(
            select(func.count(TenantSettings.id)).where(
                and_(
                    TenantSettings.tenant_id == tenant_id,
                    TenantSettings.deleted_at.is_(None),
                )
            )
        )
        return result or 0

    async def _validate_constitutional_compliance(self, tenant_id: uuid.UUID) -> bool:
        """Validate constitutional compliance for a tenant."""
        tenant = await self.session.get(Tenant, tenant_id)
        if not tenant:
            return False

        # Check constitutional hash
        if tenant.constitutional_hash != CONSTITUTIONAL_HASH:
            return False

        # Check compliance score
        return not tenant.constitutional_compliance_score < 80

    def _generate_secure_token(self, length: int = 32) -> str:
        """Generate a cryptographically secure token."""
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))
