"""Add multi-tenant support to ACGS

Revision ID: 001_multi_tenant
Revises:
Create Date: 2024-01-20 10:00:00.000000

Constitutional Hash: cdd01ef066bc6cf2
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "001_multi_tenant"
down_revision = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def upgrade():
    """Add multi-tenant support to the database."""

    # Create organizations table
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("legal_name", sa.String(500), nullable=True),
        sa.Column("contact_email", sa.String(255), nullable=False),
        sa.Column("billing_email", sa.String(255), nullable=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("company_size", sa.String(50), nullable=True),
        sa.Column("website", sa.String(500), nullable=True),
        sa.Column("address_line1", sa.String(255), nullable=True),
        sa.Column("address_line2", sa.String(255), nullable=True),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("state_province", sa.String(100), nullable=True),
        sa.Column("postal_code", sa.String(20), nullable=True),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("tier", sa.String(20), nullable=False, server_default="basic"),
        sa.Column(
            "constitutional_hash",
            sa.String(64),
            nullable=False,
            server_default=CONSTITUTIONAL_HASH,
        ),
        sa.Column(
            "constitutional_compliance_required",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
        sa.Column(
            "data_residency", sa.String(20), nullable=False, server_default="any"
        ),
        sa.Column("max_tenants", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "max_users_per_tenant", sa.Integer(), nullable=False, server_default="100"
        ),
        sa.Column(
            "max_api_requests_per_hour",
            sa.Integer(),
            nullable=False,
            server_default="10000",
        ),
        sa.Column("enforce_mfa", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "session_timeout_minutes",
            sa.Integer(),
            nullable=False,
            server_default="480",
        ),
        sa.Column("password_policy", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("max_tenants > 0", name="check_max_tenants_positive"),
        sa.CheckConstraint("max_users_per_tenant > 0", name="check_max_users_positive"),
        sa.CheckConstraint(
            "max_api_requests_per_hour > 0", name="check_max_api_requests_positive"
        ),
        sa.CheckConstraint(
            "session_timeout_minutes > 0", name="check_session_timeout_positive"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )

    # Create indexes for organizations
    op.create_index("idx_org_status_tier", "organizations", ["status", "tier"])
    op.create_index("idx_org_created", "organizations", ["created_at"])
    op.create_index(op.f("ix_organizations_id"), "organizations", ["id"])
    op.create_index(op.f("ix_organizations_name"), "organizations", ["name"])
    op.create_index(op.f("ix_organizations_slug"), "organizations", ["slug"])

    # Create tenants table
    op.create_table(
        "tenants",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "environment_type",
            sa.String(20),
            nullable=False,
            server_default="production",
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("tier", sa.String(20), nullable=False, server_default="basic"),
        sa.Column(
            "security_level", sa.String(20), nullable=False, server_default="basic"
        ),
        sa.Column(
            "constitutional_hash",
            sa.String(64),
            nullable=False,
            server_default=CONSTITUTIONAL_HASH,
        ),
        sa.Column(
            "constitutional_compliance_score",
            sa.Integer(),
            nullable=False,
            server_default="100",
        ),
        sa.Column("governance_policies", sa.JSON(), nullable=True),
        sa.Column("max_users", sa.Integer(), nullable=True),
        sa.Column("max_agents", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("max_storage_gb", sa.Integer(), nullable=False, server_default="100"),
        sa.Column(
            "max_compute_units", sa.Integer(), nullable=False, server_default="1000"
        ),
        sa.Column("api_rate_limit_per_hour", sa.Integer(), nullable=True),
        sa.Column(
            "api_burst_limit", sa.Integer(), nullable=False, server_default="100"
        ),
        sa.Column("encryption_key_id", sa.String(255), nullable=True),
        sa.Column(
            "data_encryption_required",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
        sa.Column(
            "network_isolation_required",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "audit_retention_days", sa.Integer(), nullable=False, server_default="2555"
        ),
        sa.Column("data_residency", sa.String(20), nullable=True),
        sa.Column("compliance_frameworks", sa.JSON(), nullable=True),
        sa.Column("feature_flags", sa.JSON(), nullable=True),
        sa.Column("tenant_settings", sa.JSON(), nullable=True),
        sa.Column("integration_settings", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_accessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "max_users IS NULL OR max_users > 0", name="check_tenant_max_users_positive"
        ),
        sa.CheckConstraint("max_agents > 0", name="check_max_agents_positive"),
        sa.CheckConstraint("max_storage_gb > 0", name="check_max_storage_positive"),
        sa.CheckConstraint("max_compute_units > 0", name="check_max_compute_positive"),
        sa.CheckConstraint(
            "constitutional_compliance_score >= 0 AND constitutional_compliance_score"
            " <= 100",
            name="check_compliance_score_range",
        ),
        sa.CheckConstraint(
            "audit_retention_days > 0", name="check_audit_retention_positive"
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "slug", name="uq_tenant_org_slug"),
    )

    # Create indexes for tenants
    op.create_index("idx_tenant_status_tier", "tenants", ["status", "tier"])
    op.create_index("idx_tenant_org_status", "tenants", ["organization_id", "status"])
    op.create_index("idx_tenant_created", "tenants", ["created_at"])
    op.create_index("idx_tenant_accessed", "tenants", ["last_accessed_at"])
    op.create_index(op.f("ix_tenants_id"), "tenants", ["id"])
    op.create_index(op.f("ix_tenants_organization_id"), "tenants", ["organization_id"])
    op.create_index(op.f("ix_tenants_slug"), "tenants", ["slug"])

    # Create tenant_users table
    op.create_table(
        "tenant_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="user"),
        sa.Column("permissions", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "access_level", sa.String(20), nullable=False, server_default="standard"
        ),
        sa.Column("invited_by_user_id", sa.Integer(), nullable=True),
        sa.Column("invitation_token", sa.String(255), nullable=True),
        sa.Column("invitation_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("last_accessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "user_id", name="uq_tenant_user"),
        sa.UniqueConstraint("invitation_token"),
    )

    # Create indexes for tenant_users
    op.create_index("idx_tenant_user_role", "tenant_users", ["tenant_id", "role"])
    op.create_index(
        "idx_tenant_user_active", "tenant_users", ["tenant_id", "is_active"]
    )
    op.create_index("idx_user_tenants", "tenant_users", ["user_id", "is_active"])
    op.create_index(op.f("ix_tenant_users_tenant_id"), "tenant_users", ["tenant_id"])
    op.create_index(op.f("ix_tenant_users_user_id"), "tenant_users", ["user_id"])

    # Create tenant_settings table
    op.create_table(
        "tenant_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category", sa.String(100), nullable=False),
        sa.Column("key", sa.String(255), nullable=False),
        sa.Column("value", sa.JSON(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("data_type", sa.String(50), nullable=False, server_default="string"),
        sa.Column("is_sensitive", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_readonly", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("validation_rules", sa.JSON(), nullable=True),
        sa.Column("default_value", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("deleted_by_user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "category", "key", name="uq_tenant_setting"),
    )

    # Create indexes for tenant_settings
    op.create_index(
        "idx_tenant_settings_category", "tenant_settings", ["tenant_id", "category"]
    )
    op.create_index("idx_tenant_settings_tenant", "tenant_settings", ["tenant_id"])
    op.create_index(
        op.f("ix_tenant_settings_category"), "tenant_settings", ["category"]
    )
    op.create_index(op.f("ix_tenant_settings_key"), "tenant_settings", ["key"])

    # Create tenant_invitations table
    op.create_table(
        "tenant_invitations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
        sa.Column("permissions", sa.JSON(), nullable=True),
        sa.Column("invitation_token", sa.String(255), nullable=False),
        sa.Column("invited_by_user_id", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accepted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.Column("deleted_by_user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invitation_token"),
    )

    # Create indexes for tenant_invitations
    op.create_index(
        "idx_tenant_invitation_email", "tenant_invitations", ["tenant_id", "email"]
    )
    op.create_index(
        "idx_tenant_invitation_status", "tenant_invitations", ["tenant_id", "status"]
    )
    op.create_index("idx_invitation_token", "tenant_invitations", ["invitation_token"])
    op.create_index(
        op.f("ix_tenant_invitations_email"), "tenant_invitations", ["email"]
    )

    # Enable Row Level Security (RLS) on tenant-aware tables
    # This provides an additional layer of tenant isolation at the database level
    op.execute("ALTER TABLE tenants ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE tenant_users ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE tenant_settings ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE tenant_invitations ENABLE ROW LEVEL SECURITY")

    # Create RLS policies for tenant isolation
    # These policies ensure that even if application-level filtering fails,
    # the database will enforce tenant boundaries

    # Tenant access policy (users can only see tenants they belong to)
    op.execute(
        """
        CREATE POLICY tenant_isolation_policy ON tenants
        USING (
            id IN (
                SELECT tenant_id FROM tenant_users
                WHERE user_id = current_setting('app.current_user_id')::integer
                AND is_active = true
            )
            OR current_setting('app.bypass_rls', true) = 'true'
        )
    """
    )

    # Tenant users access policy
    op.execute(
        """
        CREATE POLICY tenant_users_isolation_policy ON tenant_users
        USING (
            tenant_id IN (
                SELECT tenant_id FROM tenant_users AS tu
                WHERE tu.user_id = current_setting('app.current_user_id')::integer
                AND tu.is_active = true
            )
            OR current_setting('app.bypass_rls', true) = 'true'
        )
    """
    )

    # Tenant settings access policy
    op.execute(
        """
        CREATE POLICY tenant_settings_isolation_policy ON tenant_settings
        USING (
            tenant_id IN (
                SELECT tenant_id FROM tenant_users
                WHERE user_id = current_setting('app.current_user_id')::integer
                AND is_active = true
            )
            OR current_setting('app.bypass_rls', true) = 'true'
        )
    """
    )

    # Tenant invitations access policy
    op.execute(
        """
        CREATE POLICY tenant_invitations_isolation_policy ON tenant_invitations
        USING (
            tenant_id IN (
                SELECT tenant_id FROM tenant_users
                WHERE user_id = current_setting('app.current_user_id')::integer
                AND is_active = true
            )
            OR current_setting('app.bypass_rls', true) = 'true'
        )
    """
    )

    # Create a default organization for existing data migration
    op.execute(
        f"""
        INSERT INTO organizations (
            id, name, slug, contact_email, status, tier,
            constitutional_hash, constitutional_compliance_required,
            max_tenants, max_users_per_tenant, max_api_requests_per_hour
        ) VALUES (
            gen_random_uuid(),
            'Default Organization',
            'default-org',
            'admin@acgs.local',
            'active',
            'constitutional',
            '{CONSTITUTIONAL_HASH}',
            true,
            1000,
            10000,
            1000000
        )
        ON CONFLICT DO NOTHING
    """
    )

    # Create a default tenant for existing data migration
    op.execute(
        f"""
        INSERT INTO tenants (
            id, organization_id, name, slug, description,
            status, tier, security_level, constitutional_hash,
            constitutional_compliance_score
        )
        SELECT
            gen_random_uuid(),
            o.id,
            'Default Tenant',
            'default-tenant',
            'Default tenant for legacy data migration',
            'active',
            'constitutional',
            'strict',
            '{CONSTITUTIONAL_HASH}',
            100
        FROM organizations o
        WHERE o.slug = 'default-org'
        AND NOT EXISTS (SELECT 1 FROM tenants WHERE slug = 'default-tenant')
    """
    )

    # Create stored procedure for tenant context management
    op.execute(
        """
        CREATE OR REPLACE FUNCTION set_tenant_context(user_id integer, tenant_id uuid DEFAULT NULL, bypass_rls boolean DEFAULT false)
        RETURNS void AS $$
        BEGIN
            PERFORM set_config('app.current_user_id', user_id::text, true);
            IF tenant_id IS NOT NULL THEN
                PERFORM set_config('app.current_tenant_id', tenant_id::text, true);
            END IF;
            PERFORM set_config('app.bypass_rls', bypass_rls::text, true);
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    # Create function to validate constitutional compliance
    op.execute(
        f"""
        CREATE OR REPLACE FUNCTION validate_constitutional_compliance()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.constitutional_hash IS NULL OR NEW.constitutional_hash != '{CONSTITUTIONAL_HASH}' THEN
                RAISE EXCEPTION 'Constitutional hash validation failed. Expected: {CONSTITUTIONAL_HASH}';
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    # Create triggers for constitutional compliance validation
    op.execute(
        """
        CREATE TRIGGER trigger_validate_org_constitutional_compliance
            BEFORE INSERT OR UPDATE ON organizations
            FOR EACH ROW
            EXECUTE FUNCTION validate_constitutional_compliance();
    """
    )

    op.execute(
        """
        CREATE TRIGGER trigger_validate_tenant_constitutional_compliance
            BEFORE INSERT OR UPDATE ON tenants
            FOR EACH ROW
            EXECUTE FUNCTION validate_constitutional_compliance();
    """
    )

    # Create trigger to update timestamps
    op.execute(
        """
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    # Add update triggers to all tables with updated_at
    for table in [
        "organizations",
        "tenants",
        "tenant_users",
        "tenant_settings",
        "tenant_invitations",
    ]:
        op.execute(
            f"""
            CREATE TRIGGER trigger_update_{table}_updated_at
                BEFORE UPDATE ON {table}
                FOR EACH ROW
                EXECUTE FUNCTION update_updated_at_column();
        """
        )


def downgrade():
    """Remove multi-tenant support from the database."""

    # Drop triggers
    for table in [
        "organizations",
        "tenants",
        "tenant_users",
        "tenant_settings",
        "tenant_invitations",
    ]:
        op.execute(
            f"DROP TRIGGER IF EXISTS trigger_update_{table}_updated_at ON {table}"
        )

    op.execute(
        "DROP TRIGGER IF EXISTS trigger_validate_org_constitutional_compliance ON"
        " organizations"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS trigger_validate_tenant_constitutional_compliance ON"
        " tenants"
    )

    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column()")
    op.execute("DROP FUNCTION IF EXISTS validate_constitutional_compliance()")
    op.execute("DROP FUNCTION IF EXISTS set_tenant_context(integer, uuid, boolean)")

    # Drop tables in reverse order (due to foreign keys)
    op.drop_table("tenant_invitations")
    op.drop_table("tenant_settings")
    op.drop_table("tenant_users")
    op.drop_table("tenants")
    op.drop_table("organizations")
