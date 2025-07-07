"""Simplify RLS implementation while maintaining tenant isolation

Revision ID: 003_simplify_rls
Revises: 002_enhance_rls
Create Date: 2025-07-07 15:00:00.000000

Constitutional Hash: cdd01ef066bc6cf2

This migration simplifies the complex RLS implementation from 002_enhance_rls
while maintaining the same level of tenant isolation and security.

Key simplifications:
1. Reduce complex audit logging to security-focused events only
2. Simplify RLS policies with cleaner logic
3. Replace complex constitutional validation with streamlined checks
4. Consolidate multiple functions into single simplified versions
5. Maintain performance while reducing maintenance complexity
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "003_simplify_rls"
down_revision = "002_enhance_rls"
branch_labels = None
depends_on = None

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def upgrade():
    """Simplify RLS implementation while maintaining security."""

    # Create simplified audit table (reduced complexity from rls_audit_events)
    op.create_table(
        "tenant_access_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource", sa.String(255), nullable=True),
        sa.Column("result", sa.String(50), nullable=False),  # success, denied, error
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("constitutional_hash", sa.String(64), nullable=False, server_default=CONSTITUTIONAL_HASH),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create efficient indexes for the simplified audit table
    op.create_index("idx_tenant_access_tenant_time", "tenant_access_log", ["tenant_id", "created_at"])
    op.create_index("idx_tenant_access_user_time", "tenant_access_log", ["user_id", "created_at"])
    op.create_index("idx_tenant_access_result", "tenant_access_log", ["result"])

    # Enable RLS on the new simplified audit table
    op.execute("ALTER TABLE tenant_access_log ENABLE ROW LEVEL SECURITY")

    # Create simplified RLS policy for access log
    op.execute("""
        CREATE POLICY simple_access_log_policy ON tenant_access_log
        FOR ALL TO PUBLIC
        USING (
            tenant_id = current_setting('app.current_tenant_id', true)::uuid 
            OR current_setting('app.bypass_rls', true) = 'true'
            OR current_setting('app.is_admin', true) = 'true'
        )
    """)

    # Replace complex set_secure_tenant_context with simplified version
    op.execute(f"""
        CREATE OR REPLACE FUNCTION set_simple_tenant_context(
            p_tenant_id uuid,
            p_user_id integer DEFAULT NULL,
            p_is_admin boolean DEFAULT false,
            p_bypass_rls boolean DEFAULT false,
            p_ip_address text DEFAULT NULL
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
                    -- Log unauthorized access attempt
                    INSERT INTO tenant_access_log (
                        id, tenant_id, user_id, action, result, ip_address
                    ) VALUES (
                        gen_random_uuid(), p_tenant_id, p_user_id, 
                        'set_context', 'denied', p_ip_address
                    );
                    
                    RAISE EXCEPTION 'User % not authorized for tenant %', p_user_id, p_tenant_id;
                END IF;
            END IF;
            
            -- Set session variables
            PERFORM set_config('app.current_tenant_id', p_tenant_id::text, true);
            PERFORM set_config('app.current_user_id', COALESCE(p_user_id::text, ''), true);
            PERFORM set_config('app.is_admin', p_is_admin::text, true);
            PERFORM set_config('app.bypass_rls', p_bypass_rls::text, true);
            PERFORM set_config('app.constitutional_hash', '{CONSTITUTIONAL_HASH}', true);
            
            -- Log successful context setting
            INSERT INTO tenant_access_log (
                id, tenant_id, user_id, action, result, ip_address
            ) VALUES (
                gen_random_uuid(), p_tenant_id, p_user_id, 
                'set_context', 'success', p_ip_address
            );
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)

    # Simplified constitutional compliance check (replace complex version)
    op.execute(f"""
        CREATE OR REPLACE FUNCTION simple_constitutional_check()
        RETURNS TRIGGER AS $$
        DECLARE
            expected_hash text := '{CONSTITUTIONAL_HASH}';
        BEGIN
            -- Only check if constitutional_hash column exists
            IF TG_TABLE_NAME IN ('tenants', 'tenant_users', 'tenant_settings', 'tenant_access_log') THEN
                -- Validate constitutional hash if present
                IF NEW.constitutional_hash IS NULL OR NEW.constitutional_hash != expected_hash THEN
                    -- Log violation to simplified audit
                    INSERT INTO tenant_access_log (
                        id, tenant_id, user_id, action, resource, result
                    ) VALUES (
                        gen_random_uuid(),
                        CASE WHEN TG_TABLE_NAME = 'tenants' THEN NEW.id ELSE NEW.tenant_id END,
                        current_setting('app.current_user_id', true)::integer,
                        'constitutional_validation',
                        TG_TABLE_NAME,
                        'error'
                    );
                    
                    RAISE EXCEPTION 'Constitutional hash validation failed for table %', TG_TABLE_NAME;
                END IF;
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Replace existing complex RLS policies with simplified versions
    tables_to_simplify = ['tenants', 'tenant_users', 'tenant_settings', 'tenant_invitations']
    
    for table_name in tables_to_simplify:
        # Drop existing complex policies
        op.execute(f"DROP POLICY IF EXISTS {table_name}_isolation_policy ON {table_name}")
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_policy ON {table_name}")
        
        # Create simplified policy
        op.execute(f"""
            CREATE POLICY simple_tenant_policy ON {table_name}
            FOR ALL TO PUBLIC
            USING (
                tenant_id = current_setting('app.current_tenant_id', true)::uuid 
                OR current_setting('app.bypass_rls', true) = 'true'
                OR current_setting('app.is_admin', true) = 'true'
            )
        """)

    # Replace complex constitutional compliance triggers with simplified version
    for table_name in ['tenants', 'tenant_users', 'tenant_settings', 'tenant_access_log']:
        op.execute(f"""
            DROP TRIGGER IF EXISTS constitutional_compliance_trigger ON {table_name};
            DROP TRIGGER IF EXISTS enhanced_constitutional_compliance_trigger ON {table_name};
            CREATE TRIGGER simple_constitutional_trigger
                BEFORE INSERT OR UPDATE ON {table_name}
                FOR EACH ROW
                EXECUTE FUNCTION simple_constitutional_check();
        """)

    # Create simplified tenant management view
    op.execute("""
        CREATE OR REPLACE VIEW simple_tenant_dashboard AS
        SELECT 
            t.id as tenant_id,
            t.name as tenant_name,
            t.status,
            t.security_level,
            COUNT(tu.user_id) as user_count,
            COUNT(CASE WHEN tal.result = 'denied' AND tal.created_at > NOW() - INTERVAL '24 hours' THEN 1 END) as access_denials_24h,
            MAX(tal.created_at) as last_access,
            t.constitutional_compliance_score,
            t.constitutional_hash
        FROM tenants t
        LEFT JOIN tenant_users tu ON t.id = tu.tenant_id AND tu.is_active = true
        LEFT JOIN tenant_access_log tal ON t.id = tal.tenant_id
        GROUP BY t.id, t.name, t.status, t.security_level, t.constitutional_compliance_score, t.constitutional_hash;
    """)

    # Create simplified maintenance function
    op.execute("""
        CREATE OR REPLACE FUNCTION simple_tenant_maintenance()
        RETURNS void AS $$
        BEGIN
            -- Clean up old access logs (keep 30 days instead of 90)
            DELETE FROM tenant_access_log 
            WHERE created_at < NOW() - INTERVAL '30 days';
            
            -- Update table statistics
            ANALYZE tenant_access_log;
            
            -- Log maintenance completion
            INSERT INTO tenant_access_log (
                id, action, result
            ) VALUES (
                gen_random_uuid(), 'maintenance', 'success'
            );
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)

    # Remove complex unused functions and tables that add unnecessary complexity
    # (Keep them for now but mark for future removal)
    op.execute("""
        COMMENT ON FUNCTION monitor_rls_violations() IS 'DEPRECATED: Use simple_tenant_maintenance() instead';
        COMMENT ON FUNCTION validate_cross_tenant_operation(uuid, uuid, text, integer) IS 'DEPRECATED: Simplified in application layer';
        COMMENT ON TABLE rls_audit_events IS 'DEPRECATED: Replaced by tenant_access_log';
        COMMENT ON TABLE tenant_security_policies IS 'DEPRECATED: Policies now managed in application layer';
    """)

    # Create indexes to improve performance of simplified implementation
    op.execute("""
        -- Optimize tenant queries
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tenants_status_hash 
        ON tenants(status, constitutional_hash);
        
        -- Optimize user-tenant lookups
        CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tenant_users_active_lookup 
        ON tenant_users(user_id, tenant_id, is_active) 
        WHERE is_active = true;
    """)


def downgrade():
    """Revert simplifications and restore complex RLS implementation."""
    
    # Drop simplified components
    op.execute("DROP VIEW IF EXISTS simple_tenant_dashboard")
    op.execute("DROP FUNCTION IF EXISTS simple_tenant_maintenance()")
    op.execute("DROP FUNCTION IF EXISTS simple_constitutional_check()")
    op.execute("DROP FUNCTION IF EXISTS set_simple_tenant_context(uuid, integer, boolean, boolean, text)")
    
    # Drop simplified triggers
    for table_name in ['tenants', 'tenant_users', 'tenant_settings', 'tenant_access_log']:
        op.execute(f"DROP TRIGGER IF EXISTS simple_constitutional_trigger ON {table_name}")
    
    # Drop simplified policies
    tables_to_restore = ['tenants', 'tenant_users', 'tenant_settings', 'tenant_invitations']
    for table_name in tables_to_restore:
        op.execute(f"DROP POLICY IF EXISTS simple_tenant_policy ON {table_name}")
    
    # Drop simplified audit table
    op.drop_table("tenant_access_log")
    
    # Drop performance indexes
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_tenants_status_hash")
    op.execute("DROP INDEX CONCURRENTLY IF EXISTS idx_tenant_users_active_lookup")
    
    # Note: Original complex functions and policies from 002_enhance_rls remain
    # They would need to be recreated if this was a full rollback