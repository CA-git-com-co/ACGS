"""
Simplified Row-Level Security Implementation for ACGS
Constitutional Hash: cdd01ef066bc6cf2

This module provides a streamlined RLS implementation that maintains tenant isolation
while reducing complexity and improving performance.
"""

import logging
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass

from sqlalchemy import Column, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_mixin, declared_attr

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class SimpleTenantContext:
    """Simplified tenant context for RLS operations."""

    tenant_id: uuid.UUID
    user_id: int | None = None
    is_admin: bool = False
    bypass_rls: bool = False

    def __post_init__(self):
        """Validate context after initialization."""
        if isinstance(self.tenant_id, str):
            self.tenant_id = uuid.UUID(self.tenant_id)


@declarative_mixin
class SimpleTenantMixin:
    """
    Simplified mixin for tenant isolation.

    This provides the core tenant_id field and basic RLS setup
    without complex audit trails or constitutional validation.
    """

    @declared_attr
    def tenant_id(self):
        return Column(
            UUID(as_uuid=True),
            ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        )


class SimplifiedRLSManager:
    """
    Simplified RLS Manager that reduces complexity while maintaining security.

    Key simplifications:
    1. Single function for setting tenant context
    2. Reduced audit logging (only security violations)
    3. Simplified policy structure
    4. Constitutional validation only when required
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self._context: SimpleTenantContext | None = None

    async def set_tenant_context(
        self,
        tenant_id: uuid.UUID,
        user_id: int | None = None,
        is_admin: bool = False,
        bypass_rls: bool = False,
    ) -> None:
        """
        Set simplified tenant context for the database session.

        This replaces the complex set_secure_tenant_context function
        with a streamlined version that still maintains security.
        """
        context = SimpleTenantContext(
            tenant_id=tenant_id,
            user_id=user_id,
            is_admin=is_admin,
            bypass_rls=bypass_rls,
        )

        # Validate user access to tenant (simplified check)
        if not bypass_rls and user_id is not None:
            result = await self.session.execute(
                text(
                    """
                SELECT EXISTS(
                    SELECT 1 FROM tenant_users
                    WHERE user_id = :user_id
                    AND tenant_id = :tenant_id
                    AND is_active = true
                )
            """
                ),
                {"user_id": user_id, "tenant_id": tenant_id},
            )

            if not result.scalar():
                logger.warning(
                    f"User {user_id} attempted unauthorized access to tenant {tenant_id}"
                )
                raise PermissionError(
                    f"User {user_id} not authorized for tenant {tenant_id}"
                )

        # Set PostgreSQL session variables for RLS
        await self.session.execute(
            text("SELECT set_config('app.current_tenant_id', :tenant_id, true)"),
            {"tenant_id": str(tenant_id)},
        )
        await self.session.execute(
            text("SELECT set_config('app.current_user_id', :user_id, true)"),
            {"user_id": str(user_id) if user_id else ""},
        )
        await self.session.execute(
            text("SELECT set_config('app.bypass_rls', :bypass, true)"),
            {"bypass": str(bypass_rls).lower()},
        )
        await self.session.execute(
            text("SELECT set_config('app.is_admin', :is_admin, true)"),
            {"is_admin": str(is_admin).lower()},
        )
        await self.session.execute(
            text("SELECT set_config('app.constitutional_hash', :hash, true)"),
            {"hash": CONSTITUTIONAL_HASH},
        )

        self._context = context
        logger.debug(
            f"Set tenant context: tenant={tenant_id}, user={user_id}, admin={is_admin}"
        )

    async def clear_context(self) -> None:
        """Clear tenant context from session."""
        await self.session.execute(
            text("SELECT set_config('app.current_tenant_id', '', true)")
        )
        await self.session.execute(
            text("SELECT set_config('app.current_user_id', '', true)")
        )
        await self.session.execute(
            text("SELECT set_config('app.bypass_rls', 'false', true)")
        )
        await self.session.execute(
            text("SELECT set_config('app.is_admin', 'false', true)")
        )
        self._context = None

    @asynccontextmanager
    async def tenant_context(
        self,
        tenant_id: uuid.UUID,
        user_id: int | None = None,
        is_admin: bool = False,
        bypass_rls: bool = False,
    ):
        """Context manager for temporary tenant context."""
        old_context = self._context
        try:
            await self.set_tenant_context(tenant_id, user_id, is_admin, bypass_rls)
            yield
        finally:
            if old_context:
                await self.set_tenant_context(
                    old_context.tenant_id,
                    old_context.user_id,
                    old_context.is_admin,
                    old_context.bypass_rls,
                )
            else:
                await self.clear_context()

    @property
    def current_context(self) -> SimpleTenantContext | None:
        """Get current tenant context."""
        return self._context


async def setup_simplified_rls_policies(session: AsyncSession) -> None:
    """
    Set up simplified RLS policies that are easier to understand and maintain.

    This replaces the complex policy setup with streamlined policies that
    provide the same security guarantees.
    """

    # Drop existing complex policies if they exist
    await session.execute(
        text(
            """
        DO $$
        DECLARE
            pol_name text;
        BEGIN
            FOR pol_name IN
                SELECT policyname FROM pg_policies
                WHERE schemaname = 'public' AND policyname LIKE '%_isolation_policy'
            LOOP
                EXECUTE 'DROP POLICY IF EXISTS ' || pol_name || ' ON ' ||
                        (SELECT tablename FROM pg_policies WHERE policyname = pol_name LIMIT 1);
            END LOOP;
        END $$;
    """
        )
    )

    # Create simplified RLS policies for tenant isolation
    policies = [
        (
            "tenants",
            """
            USING (
                id = current_setting('app.current_tenant_id', true)::uuid
                OR current_setting('app.bypass_rls', true) = 'true'
                OR current_setting('app.is_admin', true) = 'true'
            )
        """,
        ),
        (
            "tenant_users",
            """
            USING (
                tenant_id = current_setting('app.current_tenant_id', true)::uuid
                OR current_setting('app.bypass_rls', true) = 'true'
                OR current_setting('app.is_admin', true) = 'true'
            )
        """,
        ),
        (
            "tenant_settings",
            """
            USING (
                tenant_id = current_setting('app.current_tenant_id', true)::uuid
                OR current_setting('app.bypass_rls', true) = 'true'
                OR current_setting('app.is_admin', true) = 'true'
            )
        """,
        ),
    ]

    for table_name, policy_condition in policies:
        # Enable RLS on table if not already enabled
        await session.execute(
            text(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY")
        )

        # Create simplified policy
        await session.execute(
            text(
                f"""
            CREATE POLICY simple_tenant_policy ON {table_name}
            FOR ALL TO PUBLIC
            {policy_condition}
        """
            )
        )

    await session.commit()
    logger.info("Simplified RLS policies created successfully")


async def create_simplified_tenant_function(session: AsyncSession) -> None:
    """
    Create a simplified tenant context function that replaces the complex
    set_secure_tenant_context function.
    """

    await session.execute(
        text(
            f"""
        CREATE OR REPLACE FUNCTION set_simple_tenant_context(
            p_tenant_id uuid,
            p_user_id integer DEFAULT NULL,
            p_is_admin boolean DEFAULT false,
            p_bypass_rls boolean DEFAULT false
        )
        RETURNS void AS $$
        DECLARE
            user_authorized boolean := false;
        BEGIN
            -- Validate user authorization if not bypassing RLS
            IF p_tenant_id IS NOT NULL AND NOT p_bypass_rls AND p_user_id IS NOT NULL THEN
                SELECT EXISTS(
                    SELECT 1 FROM tenant_users
                    WHERE user_id = p_user_id
                    AND tenant_id = p_tenant_id
                    AND is_active = true
                ) INTO user_authorized;

                IF NOT user_authorized THEN
                    RAISE EXCEPTION 'User % not authorized for tenant %', p_user_id, p_tenant_id;
                END IF;
            END IF;

            -- Set session variables
            PERFORM set_config('app.current_tenant_id', p_tenant_id::text, true);
            PERFORM set_config('app.current_user_id', COALESCE(p_user_id::text, ''), true);
            PERFORM set_config('app.is_admin', p_is_admin::text, true);
            PERFORM set_config('app.bypass_rls', p_bypass_rls::text, true);
            PERFORM set_config('app.constitutional_hash', '{CONSTITUTIONAL_HASH}', true);
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """
        )
    )

    await session.commit()
    logger.info("Simplified tenant context function created")


class SimpleTenantRepository:
    """
    Simplified tenant-aware repository that reduces complexity while
    maintaining security and constitutional compliance.
    """

    def __init__(self, model_class, session: AsyncSession):
        self.model_class = model_class
        self.session = session
        self.rls_manager = SimplifiedRLSManager(session)

    async def with_tenant(
        self,
        tenant_id: uuid.UUID,
        user_id: int | None = None,
        is_admin: bool = False,
    ):
        """Set tenant context for this repository."""
        await self.rls_manager.set_tenant_context(tenant_id, user_id, is_admin)
        return self

    async def find_all(self, **filters):
        """Find all records for current tenant."""
        table_name = self.model_class.__tablename__
        query = text("SELECT * FROM :table_name").bindparam(table_name=table_name)
        if filters:
            conditions = [f"{k} = :{k}" for k in filters]
            query = text(
                "SELECT * FROM :table_name WHERE " + " AND ".join(conditions)
            ).bindparam(table_name=table_name)

        result = await self.session.execute(query, filters)
        return result.fetchall()

    async def find_by_id(self, id: uuid.UUID):
        """Find record by ID within current tenant."""
        table_name = self.model_class.__tablename__
        query = text("SELECT * FROM :table_name WHERE id = :id").bindparam(table_name=table_name)
        result = await self.session.execute(query, {"id": id})
        return result.fetchone()

    async def create(self, **data):
        """Create new record in current tenant."""
        if not self.rls_manager.current_context:
            raise PermissionError("Tenant context not set")

        # Add tenant_id to data
        data["tenant_id"] = self.rls_manager.current_context.tenant_id

        # Add constitutional hash if model supports it
        if hasattr(self.model_class, "constitutional_hash"):
            data["constitutional_hash"] = CONSTITUTIONAL_HASH

        # Build insert query dynamically
        columns = ", ".join(data.keys())
        placeholders = ", ".join(f":{k}" for k in data)
        table_name = self.model_class.__tablename__
        query = text(
            "INSERT INTO :table_name (" + columns + ") VALUES (" + placeholders + ")"
        ).bindparam(table_name=table_name)

        await self.session.execute(query, data)
        await self.session.commit()

    async def update(self, id: uuid.UUID, **data):
        """Update record by ID within current tenant."""
        # Add constitutional hash if model supports it
        if hasattr(self.model_class, "constitutional_hash"):
            data["constitutional_hash"] = CONSTITUTIONAL_HASH

        set_clause = ", ".join(f"{k} = :{k}" for k in data)
        query = text(
            f"UPDATE {self.model_class.__tablename__} SET {set_clause} WHERE id = :id"
        )
        data["id"] = id

        await self.session.execute(query, data)
        await self.session.commit()

    async def delete(self, id: uuid.UUID):
        """Delete record by ID within current tenant."""
        query = text(f"DELETE FROM {self.model_class.__tablename__} WHERE id = :id")
        await self.session.execute(query, {"id": id})
        await self.session.commit()


# Utility function for easy tenant context management
async def get_simple_tenant_repository(
    model_class,
    session: AsyncSession,
    tenant_id: uuid.UUID,
    user_id: int | None = None,
    is_admin: bool = False,
) -> SimpleTenantRepository:
    """Get a simplified tenant repository with context already set."""
    repo = SimpleTenantRepository(model_class, session)
    await repo.with_tenant(tenant_id, user_id, is_admin)
    return repo
