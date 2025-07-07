"""Enhance Row-Level Security with comprehensive tenant isolation

Revision ID: 002_enhance_rls
Revises: 001_multi_tenant
Create Date: 2025-07-07 10:00:00.000000

Constitutional Hash: cdd01ef066bc6cf2
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "002_enhance_rls"
down_revision = "001_multi_tenant"
branch_labels = None
depends_on = None

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def upgrade():
    """Enhance Row-Level Security with comprehensive tenant isolation."""

    # Create enhanced audit table for RLS violations
    op.create_table(
        "rls_audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("table_name", sa.String(255), nullable=False),
        sa.Column("operation_type", sa.String(50), nullable=False),
        sa.Column("attempted_action", sa.Text(), nullable=True),
        sa.Column("policy_violated", sa.String(255), nullable=True),
        sa.Column("severity", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("client_ip", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("session_id", sa.String(255), nullable=True),
        sa.Column("constitutional_hash", sa.String(64), nullable=False, server_default=CONSTITUTIONAL_HASH),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes for RLS audit events
    op.create_index("idx_rls_audit_tenant", "rls_audit_events", ["tenant_id"])
    op.create_index("idx_rls_audit_user", "rls_audit_events", ["user_id"])
    op.create_index("idx_rls_audit_table", "rls_audit_events", ["table_name"])
    op.create_index("idx_rls_audit_severity", "rls_audit_events", ["severity"])
    op.create_index("idx_rls_audit_created", "rls_audit_events", ["created_at"])

    # Create comprehensive policy management table
    op.create_table(
        "tenant_security_policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("policy_name", sa.String(255), nullable=False),
        sa.Column("policy_type", sa.String(50), nullable=False),
        sa.Column("table_name", sa.String(255), nullable=False),
        sa.Column("policy_definition", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("enforcement_level", sa.String(20), nullable=False, server_default="strict"),
        sa.Column("bypass_conditions", sa.JSON(), nullable=True),
        sa.Column("violation_actions", sa.JSON(), nullable=True),
        sa.Column("constitutional_hash", sa.String(64), nullable=False, server_default=CONSTITUTIONAL_HASH),
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
        sa.Column("created_by_user_id", sa.Integer(), nullable=True),
        sa.Column("updated_by_user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "policy_name", name="uq_tenant_policy_name"),
    )

    # Create indexes for tenant security policies
    op.create_index("idx_tenant_policy_active", "tenant_security_policies", ["tenant_id", "is_active"])
    op.create_index("idx_tenant_policy_table", "tenant_security_policies", ["table_name", "is_active"])
    op.create_index("idx_tenant_policy_type", "tenant_security_policies", ["policy_type"])

    # Enable RLS on the new tables
    op.execute("ALTER TABLE rls_audit_events ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE tenant_security_policies ENABLE ROW LEVEL SECURITY")

    # Create enhanced RLS policies with constitutional compliance validation

    # RLS audit events policy (users can only see their tenant's audit events)
    op.execute("""
        CREATE POLICY rls_audit_events_isolation_policy ON rls_audit_events
        USING (
            tenant_id IN (
                SELECT tenant_id FROM tenant_users
                WHERE user_id = current_setting('app.current_user_id')::integer
                AND is_active = true
            )
            OR current_setting('app.bypass_rls', true) = 'true'
            OR current_setting('app.admin_access', true) = 'true'
        )
    """)

    # Tenant security policies access (only tenant admins can manage their policies)
    op.execute("""
        CREATE POLICY tenant_security_policies_isolation_policy ON tenant_security_policies
        USING (
            tenant_id IN (
                SELECT tenant_id FROM tenant_users
                WHERE user_id = current_setting('app.current_user_id')::integer
                AND is_active = true
                AND (role = 'admin' OR role = 'security_admin')
            )
            OR current_setting('app.bypass_rls', true) = 'true'
            OR current_setting('app.admin_access', true) = 'true'
        )
    """)

    # Create enhanced tenant context management with security validation
    op.execute("""
        CREATE OR REPLACE FUNCTION set_secure_tenant_context(
            user_id integer,
            tenant_id uuid DEFAULT NULL,
            bypass_rls boolean DEFAULT false,
            admin_access boolean DEFAULT false,
            session_id text DEFAULT NULL,
            client_ip text DEFAULT NULL
        )
        RETURNS void AS $$
        DECLARE
            tenant_exists boolean := false;
            user_authorized boolean := false;
            constitutional_valid boolean := false;
        BEGIN
            -- Validate constitutional hash consistency
            SELECT EXISTS(
                SELECT 1 FROM tenants 
                WHERE id = tenant_id 
                AND constitutional_hash = current_setting('app.constitutional_hash', true)
            ) INTO constitutional_valid;
            
            IF NOT constitutional_valid AND tenant_id IS NOT NULL THEN
                RAISE EXCEPTION 'Constitutional hash validation failed for tenant context';
            END IF;
            
            -- Validate user authorization for tenant
            IF tenant_id IS NOT NULL AND NOT bypass_rls THEN
                SELECT EXISTS(
                    SELECT 1 FROM tenant_users 
                    WHERE user_id = set_secure_tenant_context.user_id 
                    AND tenant_id = set_secure_tenant_context.tenant_id
                    AND is_active = true
                ) INTO user_authorized;
                
                IF NOT user_authorized THEN
                    -- Log unauthorized access attempt
                    INSERT INTO rls_audit_events (
                        id, tenant_id, user_id, table_name, operation_type,
                        attempted_action, policy_violated, severity, client_ip, session_id
                    ) VALUES (
                        gen_random_uuid(), tenant_id, user_id, 'tenant_context', 'unauthorized_access',
                        'Attempted to set context for unauthorized tenant', 'tenant_authorization', 'high',
                        client_ip, session_id
                    );
                    
                    RAISE EXCEPTION 'User % not authorized for tenant %', user_id, tenant_id;
                END IF;
            END IF;
            
            -- Set context variables
            PERFORM set_config('app.current_user_id', user_id::text, true);
            PERFORM set_config('app.session_id', COALESCE(session_id, gen_random_uuid()::text), true);
            PERFORM set_config('app.client_ip', COALESCE(client_ip, 'unknown'), true);
            
            IF tenant_id IS NOT NULL THEN
                PERFORM set_config('app.current_tenant_id', tenant_id::text, true);
            END IF;
            
            PERFORM set_config('app.bypass_rls', bypass_rls::text, true);
            PERFORM set_config('app.admin_access', admin_access::text, true);
            PERFORM set_config('app.constitutional_hash', '""" + CONSTITUTIONAL_HASH + """', true);
            
            -- Log successful context setting
            INSERT INTO rls_audit_events (
                id, tenant_id, user_id, table_name, operation_type,
                attempted_action, severity, client_ip, session_id
            ) VALUES (
                gen_random_uuid(), tenant_id, user_id, 'tenant_context', 'context_set',
                'Successfully set tenant context', 'info', client_ip, session_id
            );
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)

    # Create function to validate cross-tenant operations
    op.execute("""
        CREATE OR REPLACE FUNCTION validate_cross_tenant_operation(
            source_tenant_id uuid,
            target_tenant_id uuid,
            operation_type text,
            user_id integer
        )
        RETURNS boolean AS $$
        DECLARE
            is_authorized boolean := false;
            same_organization boolean := false;
        BEGIN
            -- Check if both tenants belong to the same organization
            SELECT EXISTS(
                SELECT 1 FROM tenants t1, tenants t2
                WHERE t1.id = source_tenant_id
                AND t2.id = target_tenant_id
                AND t1.organization_id = t2.organization_id
            ) INTO same_organization;
            
            -- Check if user has cross-tenant permissions
            SELECT EXISTS(
                SELECT 1 FROM tenant_users tu1, tenant_users tu2
                WHERE tu1.user_id = validate_cross_tenant_operation.user_id
                AND tu2.user_id = validate_cross_tenant_operation.user_id
                AND tu1.tenant_id = source_tenant_id
                AND tu2.tenant_id = target_tenant_id
                AND tu1.is_active = true
                AND tu2.is_active = true
                AND (tu1.role = 'admin' OR tu1.role = 'cross_tenant_user')
                AND (tu2.role = 'admin' OR tu2.role = 'cross_tenant_user')
            ) INTO is_authorized;
            
            -- Log the validation attempt
            INSERT INTO rls_audit_events (
                id, tenant_id, user_id, table_name, operation_type,
                attempted_action, severity
            ) VALUES (
                gen_random_uuid(), source_tenant_id, user_id, 'cross_tenant_validation', operation_type,
                format('Cross-tenant operation validation: %s -> %s', source_tenant_id, target_tenant_id),
                CASE WHEN is_authorized THEN 'info' ELSE 'warning' END
            );
            
            RETURN is_authorized AND same_organization;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)

    # Create function for RLS policy monitoring
    op.execute("""
        CREATE OR REPLACE FUNCTION monitor_rls_violations()
        RETURNS void AS $$
        DECLARE
            violation_count integer;
            recent_violations integer;
        BEGIN
            -- Count total violations in the last hour
            SELECT COUNT(*) INTO recent_violations
            FROM rls_audit_events
            WHERE created_at > NOW() - INTERVAL '1 hour'
            AND severity IN ('high', 'critical');
            
            -- If violations exceed threshold, take action
            IF recent_violations > 10 THEN
                -- Log critical security event
                INSERT INTO rls_audit_events (
                    id, table_name, operation_type, attempted_action, severity
                ) VALUES (
                    gen_random_uuid(), 'system_monitoring', 'security_alert',
                    format('High violation rate detected: %s violations in last hour', recent_violations),
                    'critical'
                );
                
                -- Could trigger additional security measures here
                RAISE WARNING 'High RLS violation rate detected: % violations in last hour', recent_violations;
            END IF;
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)

    # Create enhanced constitutional compliance validation trigger
    op.execute(f"""
        CREATE OR REPLACE FUNCTION enhanced_constitutional_compliance_check()
        RETURNS TRIGGER AS $$
        DECLARE
            expected_hash text := '{CONSTITUTIONAL_HASH}';
            table_config jsonb;
            compliance_required boolean := true;
        BEGIN
            -- Check if constitutional compliance is required for this table
            SELECT EXISTS(
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = TG_TABLE_NAME 
                AND column_name = 'constitutional_hash'
            ) INTO compliance_required;
            
            IF compliance_required THEN
                -- Validate constitutional hash
                IF NEW.constitutional_hash IS NULL OR NEW.constitutional_hash != expected_hash THEN
                    -- Log violation
                    INSERT INTO rls_audit_events (
                        id, tenant_id, user_id, table_name, operation_type,
                        attempted_action, policy_violated, severity
                    ) VALUES (
                        gen_random_uuid(),
                        CASE WHEN TG_TABLE_NAME = 'tenants' THEN NEW.id ELSE NEW.tenant_id END,
                        current_setting('app.current_user_id', true)::integer,
                        TG_TABLE_NAME,
                        TG_OP,
                        'Constitutional hash validation failure',
                        'constitutional_compliance',
                        'critical'
                    );
                    
                    RAISE EXCEPTION 'Constitutional hash validation failed for table %. Expected: %, Got: %', 
                        TG_TABLE_NAME, expected_hash, COALESCE(NEW.constitutional_hash, 'NULL');
                END IF;
                
                -- Update timestamp for compliance tracking
                IF TG_OP = 'UPDATE' AND OLD.constitutional_hash = NEW.constitutional_hash THEN
                    NEW.updated_at = NOW();
                END IF;
            END IF;
            
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create triggers for constitutional compliance on all relevant tables
    for table_name in ['tenants', 'tenant_users', 'tenant_settings', 'tenant_invitations', 'tenant_security_policies']:
        op.execute(f"""
            DROP TRIGGER IF EXISTS constitutional_compliance_trigger ON {table_name};
            CREATE TRIGGER constitutional_compliance_trigger
                BEFORE INSERT OR UPDATE ON {table_name}
                FOR EACH ROW
                EXECUTE FUNCTION enhanced_constitutional_compliance_check();
        """)

    # Create view for tenant security dashboard
    op.execute("""
        CREATE OR REPLACE VIEW tenant_security_dashboard AS
        SELECT 
            t.id as tenant_id,
            t.name as tenant_name,
            t.security_level,
            COUNT(tsp.id) as active_policies,
            COUNT(CASE WHEN rae.severity = 'critical' AND rae.created_at > NOW() - INTERVAL '24 hours' THEN 1 END) as critical_violations_24h,
            COUNT(CASE WHEN rae.severity = 'high' AND rae.created_at > NOW() - INTERVAL '24 hours' THEN 1 END) as high_violations_24h,
            COUNT(CASE WHEN rae.severity = 'medium' AND rae.created_at > NOW() - INTERVAL '24 hours' THEN 1 END) as medium_violations_24h,
            MAX(rae.created_at) as last_violation,
            t.constitutional_compliance_score,
            t.constitutional_hash
        FROM tenants t
        LEFT JOIN tenant_security_policies tsp ON t.id = tsp.tenant_id AND tsp.is_active = true
        LEFT JOIN rls_audit_events rae ON t.id = rae.tenant_id
        GROUP BY t.id, t.name, t.security_level, t.constitutional_compliance_score, t.constitutional_hash;
    """)

    # Enable RLS on the view
    op.execute("ALTER VIEW tenant_security_dashboard SET (security_barrier = true)")

    # Create monitoring job function (to be called by external scheduler)
    op.execute("""
        CREATE OR REPLACE FUNCTION rls_maintenance_job()
        RETURNS void AS $$
        BEGIN
            -- Clean up old audit events (keep 90 days)
            DELETE FROM rls_audit_events 
            WHERE created_at < NOW() - INTERVAL '90 days';
            
            -- Run violation monitoring
            PERFORM monitor_rls_violations();
            
            -- Update statistics
            ANALYZE rls_audit_events;
            ANALYZE tenant_security_policies;
            
            -- Log maintenance completion
            INSERT INTO rls_audit_events (
                id, table_name, operation_type, attempted_action, severity
            ) VALUES (
                gen_random_uuid(), 'system_maintenance', 'cleanup',
                'RLS maintenance job completed successfully', 'info'
            );
        END;
        $$ LANGUAGE plpgsql SECURITY DEFINER;
    """)

    # Insert default security policies for new tenants
    op.execute(f"""
        INSERT INTO tenant_security_policies (
            id, tenant_id, policy_name, policy_type, table_name, policy_definition,
            enforcement_level, constitutional_hash
        )
        SELECT 
            gen_random_uuid(),
            t.id,
            'strict_tenant_isolation',
            'isolation',
            'all_tables',
            'USING (tenant_id = current_setting(''app.current_tenant_id'')::uuid OR current_setting(''app.bypass_rls'', true) = ''true'')',
            'strict',
            '{CONSTITUTIONAL_HASH}'
        FROM tenants t
        WHERE NOT EXISTS (
            SELECT 1 FROM tenant_security_policies tsp 
            WHERE tsp.tenant_id = t.id 
            AND tsp.policy_name = 'strict_tenant_isolation'
        );
    """)


def downgrade():
    """Remove enhanced RLS security features."""
    
    # Drop triggers
    for table_name in ['tenants', 'tenant_users', 'tenant_settings', 'tenant_invitations', 'tenant_security_policies']:
        op.execute(f"DROP TRIGGER IF EXISTS constitutional_compliance_trigger ON {table_name}")
    
    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS enhanced_constitutional_compliance_check()")
    op.execute("DROP FUNCTION IF EXISTS rls_maintenance_job()")
    op.execute("DROP FUNCTION IF EXISTS monitor_rls_violations()")
    op.execute("DROP FUNCTION IF EXISTS validate_cross_tenant_operation(uuid, uuid, text, integer)")
    op.execute("DROP FUNCTION IF EXISTS set_secure_tenant_context(integer, uuid, boolean, boolean, text, text)")
    
    # Drop view
    op.execute("DROP VIEW IF EXISTS tenant_security_dashboard")
    
    # Drop policies
    op.execute("DROP POLICY IF EXISTS rls_audit_events_isolation_policy ON rls_audit_events")
    op.execute("DROP POLICY IF EXISTS tenant_security_policies_isolation_policy ON tenant_security_policies")
    
    # Drop tables
    op.drop_table("tenant_security_policies")
    op.drop_table("rls_audit_events")