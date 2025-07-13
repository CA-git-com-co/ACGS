"""
Tenant-Aware Repository Pattern for ACGS Multi-Tenant Architecture

This module provides base repository classes that automatically handle
tenant isolation and filtering for all database operations.

Constitutional Hash: cdd01ef066bc6cf2
"""

import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

from ..database import Base
from ..models.multi_tenant import Tenant, TenantMultiBase

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Type variables for generic repository
ModelType = TypeVar("ModelType", bound=Base)
TenantModelType = TypeVar("TenantModelType", bound=TenantMultiBase)


@dataclass
class TenantContext:
    """
    Context object containing tenant information for database operations.

    This context is passed to repository methods to ensure proper
    tenant isolation and security validation.
    """

    tenant_id: uuid.UUID
    user_id: int | None = None
    organization_id: uuid.UUID | None = None
    security_level: str | None = None
    constitutional_compliance_required: bool = True

    def __post_init__(self):
        """Validate tenant context after initialization."""
        if not isinstance(self.tenant_id, uuid.UUID):
            if isinstance(self.tenant_id, str):
                self.tenant_id = uuid.UUID(self.tenant_id)
            else:
                raise ValueError("tenant_id must be a UUID")


class TenantIsolationError(Exception):
    """Raised when tenant isolation is violated."""


class ConstitutionalComplianceError(Exception):
    """Raised when constitutional compliance requirements are not met."""


class BaseTenantRepository(Generic[TenantModelType]):
    """
    Base repository class for tenant-aware database operations.

    Automatically applies tenant filtering to all queries and ensures
    constitutional compliance and security validation.
    """

    def __init__(self, model_class: type[TenantModelType], session: AsyncSession):
        self.model_class = model_class
        self.session = session
        self._tenant_context: TenantContext | None = None

    def set_tenant_context(self, context: TenantContext) -> None:
        """Set the tenant context for all subsequent operations."""
        self._tenant_context = context

    def get_tenant_context(self) -> TenantContext:
        """Get the current tenant context."""
        if self._tenant_context is None:
            raise TenantIsolationError("Tenant context not set")
        return self._tenant_context

    @contextmanager
    def with_tenant_context(self, context: TenantContext):
        """Context manager for temporary tenant context."""
        old_context = self._tenant_context
        self._tenant_context = context
        try:
            yield
        finally:
            self._tenant_context = old_context

    def _apply_tenant_filter(self, query: Select) -> Select:
        """Apply tenant filtering to a query."""
        context = self.get_tenant_context()

        # Add tenant filter
        query = query.where(self.model_class.tenant_id == context.tenant_id)

        # Add soft delete filter if model has deleted_at
        if hasattr(self.model_class, "deleted_at"):
            query = query.where(self.model_class.deleted_at.is_(None))

        return query

    def _validate_constitutional_compliance(self, instance: TenantModelType) -> None:
        """Validate constitutional compliance for an instance."""
        context = self.get_tenant_context()

        if not context.constitutional_compliance_required:
            return

        # Check constitutional hash if model has it
        if hasattr(instance, "constitutional_hash"):
            if instance.constitutional_hash != CONSTITUTIONAL_HASH:
                raise ConstitutionalComplianceError(
                    f"Constitutional hash mismatch: expected {CONSTITUTIONAL_HASH}, "
                    f"got {instance.constitutional_hash}"
                )

    def _prepare_instance_for_save(self, instance: TenantModelType) -> None:
        """Prepare an instance for saving by setting tenant context."""
        context = self.get_tenant_context()

        # Set tenant_id
        instance.tenant_id = context.tenant_id

        # Set audit fields if available
        if hasattr(instance, "created_by_user_id") and context.user_id:
            if not instance.created_by_user_id:
                instance.created_by_user_id = context.user_id
            instance.updated_by_user_id = context.user_id

        # Set constitutional hash if model has it
        if hasattr(instance, "constitutional_hash"):
            instance.constitutional_hash = CONSTITUTIONAL_HASH

    async def create(self, **kwargs) -> TenantModelType:
        """Create a new instance with automatic tenant context."""
        instance = self.model_class(**kwargs)
        self._prepare_instance_for_save(instance)
        self._validate_constitutional_compliance(instance)

        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: int | uuid.UUID) -> TenantModelType | None:
        """Get an instance by ID with tenant filtering."""
        query = select(self.model_class).where(self.model_class.id == id)
        query = self._apply_tenant_filter(query)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self, offset: int = 0, limit: int = 100, order_by: str | None = None
    ) -> list[TenantModelType]:
        """Get all instances for the current tenant."""
        query = select(self.model_class)
        query = self._apply_tenant_filter(query)

        # Apply ordering
        if order_by:
            if hasattr(self.model_class, order_by):
                query = query.order_by(getattr(self.model_class, order_by))
        # Default ordering by created_at if available
        elif hasattr(self.model_class, "created_at"):
            query = query.order_by(self.model_class.created_at.desc())

        # Apply pagination
        query = query.offset(offset).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def count(self, **filters) -> int:
        """Count instances for the current tenant."""
        query = select(func.count(self.model_class.id))
        query = self._apply_tenant_filter(query)

        # Apply additional filters
        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(self.model_class, key):
                    conditions.append(getattr(self.model_class, key) == value)
            if conditions:
                query = query.where(and_(*conditions))

        result = await self.session.execute(query)
        return result.scalar()

    async def filter_by(self, **filters) -> list[TenantModelType]:
        """Filter instances by given criteria with tenant isolation."""
        query = select(self.model_class)
        query = self._apply_tenant_filter(query)

        # Apply filters
        conditions = []
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                if isinstance(value, list):
                    conditions.append(getattr(self.model_class, key).in_(value))
                else:
                    conditions.append(getattr(self.model_class, key) == value)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, id: int | uuid.UUID, **updates) -> TenantModelType | None:
        """Update an instance with tenant validation."""
        # First, get the instance to ensure it belongs to the tenant
        instance = await self.get_by_id(id)
        if not instance:
            return None

        # Apply updates
        for key, value in updates.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        # Update audit fields
        context = self.get_tenant_context()
        if hasattr(instance, "updated_by_user_id") and context.user_id:
            instance.updated_by_user_id = context.user_id

        self._validate_constitutional_compliance(instance)

        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def soft_delete(self, id: int | uuid.UUID) -> bool:
        """Soft delete an instance (if model supports it)."""
        instance = await self.get_by_id(id)
        if not instance:
            return False

        if hasattr(instance, "deleted_at"):
            from datetime import datetime, timezone

            instance.deleted_at = datetime.now(timezone.utc)

            # Set deleted_by if available
            context = self.get_tenant_context()
            if hasattr(instance, "deleted_by_user_id") and context.user_id:
                instance.deleted_by_user_id = context.user_id

            await self.session.flush()
            return True
        # Model doesn't support soft delete, perform hard delete
        return await self.hard_delete(id)

    async def hard_delete(self, id: int | uuid.UUID) -> bool:
        """Hard delete an instance."""
        instance = await self.get_by_id(id)
        if not instance:
            return False

        await self.session.delete(instance)
        await self.session.flush()
        return True

    async def exists(self, **filters) -> bool:
        """Check if an instance exists with given criteria."""
        query = select(func.count(self.model_class.id))
        query = self._apply_tenant_filter(query)

        # Apply filters
        conditions = []
        for key, value in filters.items():
            if hasattr(self.model_class, key):
                conditions.append(getattr(self.model_class, key) == value)

        if conditions:
            query = query.where(and_(*conditions))

        result = await self.session.execute(query)
        return result.scalar() > 0


class TenantRepository(BaseTenantRepository[Tenant]):
    """
    Specialized repository for Tenant operations.

    Provides additional methods specific to tenant management
    and cross-tenant operations that require special permissions.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Tenant, session)

    async def get_by_slug(self, org_id: uuid.UUID, slug: str) -> Tenant | None:
        """Get a tenant by organization and slug."""
        query = select(Tenant).where(
            and_(
                Tenant.organization_id == org_id,
                Tenant.slug == slug,
                Tenant.deleted_at.is_(None),
            )
        )

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_organization(self, org_id: uuid.UUID) -> list[Tenant]:
        """Get all tenants for an organization."""
        query = (
            select(Tenant)
            .where(and_(Tenant.organization_id == org_id, Tenant.deleted_at.is_(None)))
            .order_by(Tenant.created_at.desc())
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def validate_tenant_access(
        self, tenant_id: uuid.UUID, user_id: int
    ) -> dict[str, Any]:
        """
        Validate if a user has access to a tenant and return access details.

        Returns a dictionary with access information including role,
        permissions, and security level.
        """
        from ..models.multi_tenant import TenantUser

        # Get tenant information
        tenant = await self.get_by_id(tenant_id)
        if not tenant or tenant.status != "active":
            return {"access": False, "reason": "tenant_not_found_or_inactive"}

        # Get user-tenant relationship
        query = select(TenantUser).where(
            and_(
                TenantUser.tenant_id == tenant_id,
                TenantUser.user_id == user_id,
                TenantUser.is_active,
            )
        )

        result = await self.session.execute(query)
        tenant_user = result.scalar_one_or_none()

        if not tenant_user:
            return {"access": False, "reason": "user_not_member_of_tenant"}

        return {
            "access": True,
            "tenant": tenant,
            "role": tenant_user.role,
            "permissions": tenant_user.permissions or [],
            "access_level": tenant_user.access_level,
            "security_level": tenant.security_level,
            "constitutional_compliance_required": (
                tenant.constitutional_hash == CONSTITUTIONAL_HASH
            ),
        }

    async def get_user_tenants(self, user_id: int) -> list[dict[str, Any]]:
        """Get all tenants that a user has access to."""
        from ..models.multi_tenant import TenantUser

        query = (
            select(Tenant, TenantUser)
            .join(TenantUser, Tenant.id == TenantUser.tenant_id)
            .where(
                and_(
                    TenantUser.user_id == user_id,
                    TenantUser.is_active,
                    Tenant.deleted_at.is_(None),
                    Tenant.status == "active",
                )
            )
            .order_by(Tenant.name)
        )

        result = await self.session.execute(query)

        tenants = []
        for tenant, tenant_user in result.all():
            tenants.append(
                {
                    "tenant": tenant,
                    "role": tenant_user.role,
                    "permissions": tenant_user.permissions or [],
                    "access_level": tenant_user.access_level,
                    "last_accessed_at": tenant_user.last_accessed_at,
                }
            )

        return tenants

    async def update_constitutional_compliance(
        self, tenant_id: uuid.UUID, compliance_score: int
    ) -> bool:
        """Update tenant constitutional compliance score."""
        if not (0 <= compliance_score <= 100):
            raise ValueError("Compliance score must be between 0 and 100")

        query = (
            update(Tenant)
            .where(Tenant.id == tenant_id)
            .values(
                constitutional_compliance_score=compliance_score, updated_at=func.now()
            )
        )

        result = await self.session.execute(query)
        return result.rowcount > 0


class CrossTenantRepository:
    """
    Repository for operations that require cross-tenant access.

    Used for administrative operations and system-level queries
    that need to operate across tenant boundaries with proper
    authorization and constitutional compliance.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_tenant_statistics(self, org_id: uuid.UUID) -> dict[str, Any]:
        """Get statistics across all tenants in an organization."""
        from sqlalchemy import text

        query = text(
            """
            SELECT
                COUNT(*) as total_tenants,
                COUNT(CASE WHEN status = 'active' THEN 1 END) as active_tenants,
                COUNT(CASE WHEN status = 'suspended' THEN 1 END) as suspended_tenants,
                AVG(constitutional_compliance_score) as avg_compliance_score,
                MIN(constitutional_compliance_score) as min_compliance_score,
                COUNT(CASE WHEN constitutional_compliance_score < 80 THEN 1 END) as low_compliance_tenants
            FROM tenants
            WHERE organization_id = :org_id
            AND deleted_at IS NULL
        """
        )

        result = await self.session.execute(query, {"org_id": org_id})
        row = result.fetchone()

        return {
            "total_tenants": row.total_tenants or 0,
            "active_tenants": row.active_tenants or 0,
            "suspended_tenants": row.suspended_tenants or 0,
            "average_compliance_score": float(row.avg_compliance_score or 0),
            "minimum_compliance_score": row.min_compliance_score or 0,
            "low_compliance_tenants": row.low_compliance_tenants or 0,
        }

    async def find_constitutional_violations(
        self, threshold: int = 80
    ) -> list[dict[str, Any]]:
        """Find tenants with constitutional compliance issues."""
        query = (
            select(Tenant)
            .where(
                and_(
                    Tenant.constitutional_compliance_score < threshold,
                    Tenant.deleted_at.is_(None),
                    Tenant.status == "active",
                )
            )
            .order_by(Tenant.constitutional_compliance_score.asc())
        )

        result = await self.session.execute(query)
        tenants = result.scalars().all()

        return [
            {
                "tenant_id": tenant.id,
                "tenant_name": tenant.name,
                "organization_id": tenant.organization_id,
                "compliance_score": tenant.constitutional_compliance_score,
                "security_level": tenant.security_level,
                "status": tenant.status,
            }
            for tenant in tenants
        ]


# Utility functions for repository management
def create_tenant_repository(
    model_class: type[TenantModelType], session: AsyncSession
) -> BaseTenantRepository[TenantModelType]:
    """Factory function to create a tenant-aware repository."""
    return BaseTenantRepository(model_class, session)


async def validate_tenant_context(
    session: AsyncSession, tenant_id: uuid.UUID, user_id: int | None = None
) -> TenantContext:
    """
    Validate and create a tenant context for database operations.

    Ensures the tenant exists, is active, and the user has access.
    """
    tenant_repo = TenantRepository(session)

    # Get tenant
    tenant = await tenant_repo.get_by_id(tenant_id)
    if not tenant:
        raise TenantIsolationError("Tenant not found")

    if tenant.status != "active":
        raise TenantIsolationError("Tenant is not active")

    # If user_id is provided, validate access
    if user_id:
        access_info = await tenant_repo.validate_tenant_access(tenant_id, user_id)
        if not access_info["access"]:
            raise TenantIsolationError(f"User access denied: {access_info['reason']}")

    return TenantContext(
        tenant_id=tenant_id,
        user_id=user_id,
        organization_id=tenant.organization_id,
        security_level=tenant.security_level,
        constitutional_compliance_required=tenant.constitutional_hash
        == CONSTITUTIONAL_HASH,
    )
