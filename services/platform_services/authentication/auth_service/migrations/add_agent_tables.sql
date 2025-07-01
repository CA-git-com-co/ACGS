-- Migration: Add Agent Identity Management Tables
-- Description: Creates tables for autonomous agent identity management
-- Version: 1.0.0
-- Date: 2025-06-30

-- Create agents table
CREATE TABLE IF NOT EXISTS agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    agent_type VARCHAR(50) NOT NULL DEFAULT 'coding_agent',
    version VARCHAR(50) NOT NULL DEFAULT '1.0.0',
    
    -- Status and lifecycle
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    activated_at TIMESTAMPTZ,
    suspended_at TIMESTAMPTZ,
    retired_at TIMESTAMPTZ,
    last_activity_at TIMESTAMPTZ,
    
    -- Ownership and responsibility
    owner_user_id INTEGER NOT NULL REFERENCES auth_users(id),
    responsible_team VARCHAR(100),
    contact_email VARCHAR(255),
    
    -- Capabilities and permissions
    capabilities JSONB NOT NULL DEFAULT '[]',
    permissions JSONB NOT NULL DEFAULT '[]',
    role_assignments JSONB NOT NULL DEFAULT '[]',
    
    -- Security and access control
    api_key_hash VARCHAR(255),
    allowed_services JSONB NOT NULL DEFAULT '[]',
    allowed_operations JSONB NOT NULL DEFAULT '[]',
    ip_whitelist JSONB,
    
    -- Resource limits and constraints
    max_requests_per_minute INTEGER NOT NULL DEFAULT 100,
    max_concurrent_operations INTEGER NOT NULL DEFAULT 5,
    resource_quota JSONB,
    
    -- Constitutional compliance
    constitutional_hash VARCHAR(64) NOT NULL DEFAULT 'cdd01ef066bc6cf2',
    compliance_level VARCHAR(20) NOT NULL DEFAULT 'standard',
    requires_human_approval BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Monitoring and metrics
    total_operations INTEGER NOT NULL DEFAULT 0,
    successful_operations INTEGER NOT NULL DEFAULT 0,
    failed_operations INTEGER NOT NULL DEFAULT 0,
    last_error TEXT,
    last_error_at TIMESTAMPTZ,
    
    -- Metadata and configuration
    configuration JSONB,
    metadata JSONB,
    tags JSONB NOT NULL DEFAULT '[]'
);

-- Create indexes for agents table
CREATE INDEX IF NOT EXISTS idx_agents_agent_id ON agents(agent_id);
CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status);
CREATE INDEX IF NOT EXISTS idx_agents_owner_user_id ON agents(owner_user_id);
CREATE INDEX IF NOT EXISTS idx_agents_agent_type ON agents(agent_type);
CREATE INDEX IF NOT EXISTS idx_agents_created_at ON agents(created_at);
CREATE INDEX IF NOT EXISTS idx_agents_last_activity_at ON agents(last_activity_at);

-- Create GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_agents_capabilities_gin ON agents USING GIN(capabilities);
CREATE INDEX IF NOT EXISTS idx_agents_permissions_gin ON agents USING GIN(permissions);
CREATE INDEX IF NOT EXISTS idx_agents_tags_gin ON agents USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_agents_allowed_services_gin ON agents USING GIN(allowed_services);
CREATE INDEX IF NOT EXISTS idx_agents_allowed_operations_gin ON agents USING GIN(allowed_operations);

-- Create agent_sessions table
CREATE TABLE IF NOT EXISTS agent_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    
    -- Session details
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    
    -- Session context
    client_ip VARCHAR(45),
    user_agent VARCHAR(500),
    service_context JSONB,
    
    -- Session status
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    termination_reason VARCHAR(100)
);

-- Create indexes for agent_sessions table
CREATE INDEX IF NOT EXISTS idx_agent_sessions_agent_id ON agent_sessions(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_session_token ON agent_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_started_at ON agent_sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_agent_sessions_is_active ON agent_sessions(is_active);

-- Create agent_audit_logs table
CREATE TABLE IF NOT EXISTS agent_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID NOT NULL REFERENCES agents(id) ON DELETE CASCADE,
    
    -- Audit details
    event_type VARCHAR(50) NOT NULL,
    event_description TEXT NOT NULL,
    performed_by_user_id INTEGER REFERENCES auth_users(id),
    performed_by_system VARCHAR(100),
    
    -- Change tracking
    old_values JSONB,
    new_values JSONB,
    
    -- Context and metadata
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    client_ip VARCHAR(45),
    user_agent VARCHAR(500),
    request_id VARCHAR(100),
    
    -- Constitutional compliance
    constitutional_hash VARCHAR(64) NOT NULL,
    compliance_verified BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Additional context
    metadata JSONB
);

-- Create indexes for agent_audit_logs table
CREATE INDEX IF NOT EXISTS idx_agent_audit_logs_agent_id ON agent_audit_logs(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_audit_logs_event_type ON agent_audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_agent_audit_logs_timestamp ON agent_audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_agent_audit_logs_performed_by_user_id ON agent_audit_logs(performed_by_user_id);

-- Add agent-related permissions to the permissions table
INSERT INTO auth_permissions (name, description) VALUES
    ('agent:create', 'Create new agents'),
    ('agent:create_any', 'Create agents for any user (admin)'),
    ('agent:read', 'Read own agents'),
    ('agent:read_all', 'Read all agents (admin)'),
    ('agent:update', 'Update own agents'),
    ('agent:update_any', 'Update any agent (admin)'),
    ('agent:delete', 'Delete own agents'),
    ('agent:delete_any', 'Delete any agent (admin)'),
    ('agent:manage_status', 'Manage status of own agents'),
    ('agent:manage_status_any', 'Manage status of any agent (admin)'),
    ('agent:audit', 'View audit logs for own agents'),
    ('agent:audit_all', 'View all agent audit logs (admin)'),
    ('agent:authenticate', 'Authenticate as agent'),
    ('agent:impersonate', 'Impersonate agents (admin)')
ON CONFLICT (name) DO NOTHING;

-- Create agent_manager role with appropriate permissions
INSERT INTO auth_roles (name, description) VALUES
    ('agent_manager', 'Can manage autonomous agents')
ON CONFLICT (name) DO NOTHING;

-- Assign permissions to agent_manager role
INSERT INTO auth_role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM auth_roles r, auth_permissions p
WHERE r.name = 'agent_manager'
AND p.name IN (
    'agent:create',
    'agent:read',
    'agent:update',
    'agent:manage_status',
    'agent:audit'
)
ON CONFLICT DO NOTHING;

-- Create agent_admin role with full permissions
INSERT INTO auth_roles (name, description) VALUES
    ('agent_admin', 'Full administrative access to agent management')
ON CONFLICT (name) DO NOTHING;

-- Assign all agent permissions to agent_admin role
INSERT INTO auth_role_permissions (role_id, permission_id)
SELECT r.id, p.id
FROM auth_roles r, auth_permissions p
WHERE r.name = 'agent_admin'
AND p.name LIKE 'agent:%'
ON CONFLICT DO NOTHING;

-- Add constraints and checks
ALTER TABLE agents ADD CONSTRAINT chk_agent_status 
    CHECK (status IN ('pending', 'active', 'suspended', 'retired', 'compromised'));

ALTER TABLE agents ADD CONSTRAINT chk_agent_type 
    CHECK (agent_type IN ('coding_agent', 'policy_agent', 'monitoring_agent', 'analysis_agent', 'integration_agent', 'custom_agent'));

ALTER TABLE agents ADD CONSTRAINT chk_compliance_level 
    CHECK (compliance_level IN ('standard', 'high', 'critical'));

ALTER TABLE agents ADD CONSTRAINT chk_max_requests_positive 
    CHECK (max_requests_per_minute > 0);

ALTER TABLE agents ADD CONSTRAINT chk_max_operations_positive 
    CHECK (max_concurrent_operations > 0);

-- Add comments for documentation
COMMENT ON TABLE agents IS 'Autonomous agent identity and configuration management';
COMMENT ON TABLE agent_sessions IS 'Active agent authentication sessions';
COMMENT ON TABLE agent_audit_logs IS 'Comprehensive audit trail for all agent operations';

COMMENT ON COLUMN agents.agent_id IS 'Human-readable unique identifier for the agent';
COMMENT ON COLUMN agents.constitutional_hash IS 'Hash of constitutional principles the agent must follow';
COMMENT ON COLUMN agents.compliance_level IS 'Level of constitutional compliance required: standard, high, critical';
COMMENT ON COLUMN agents.requires_human_approval IS 'Whether agent actions require human approval';

-- Create function to automatically update last_activity_at
CREATE OR REPLACE FUNCTION update_agent_last_activity()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE agents 
    SET last_activity_at = NOW() 
    WHERE id = NEW.agent_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to update last_activity_at when sessions are created
CREATE TRIGGER trigger_update_agent_last_activity
    AFTER INSERT ON agent_sessions
    FOR EACH ROW
    EXECUTE FUNCTION update_agent_last_activity();

-- Grant appropriate permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON agents TO auth_service_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON agent_sessions TO auth_service_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON agent_audit_logs TO auth_service_user;

-- Create view for active agents (commonly used query)
CREATE OR REPLACE VIEW active_agents AS
SELECT 
    a.*,
    u.username as owner_username,
    u.email as owner_email
FROM agents a
JOIN auth_users u ON a.owner_user_id = u.id
WHERE a.status = 'active';

GRANT SELECT ON active_agents TO auth_service_user;
