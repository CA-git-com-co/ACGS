-- Migration: Create Sandbox Execution Tables
-- Description: Creates tables for secure code execution tracking and audit
-- Version: 1.0.0
-- Date: 2025-06-30

-- Create sandbox_executions table
CREATE TABLE IF NOT EXISTS sandbox_executions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- Agent and request information
    agent_id VARCHAR(100) NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    request_id VARCHAR(100),
    session_id VARCHAR(100),
    
    -- Execution details
    environment VARCHAR(50) NOT NULL,
    code TEXT NOT NULL,
    language VARCHAR(50) NOT NULL,
    entry_point VARCHAR(500),
    
    -- Execution context and parameters
    execution_context JSONB DEFAULT '{}',
    environment_variables JSONB DEFAULT '{}',
    input_files JSONB DEFAULT '[]',
    command_args JSONB DEFAULT '[]',
    
    -- Resource limits and configuration
    memory_limit_mb INTEGER DEFAULT 512,
    cpu_limit FLOAT DEFAULT 0.5,
    timeout_seconds INTEGER DEFAULT 300,
    disk_limit_mb INTEGER DEFAULT 1024,
    network_enabled BOOLEAN DEFAULT FALSE,
    
    -- Docker/container configuration
    container_id VARCHAR(100),
    container_image VARCHAR(200),
    container_config JSONB DEFAULT '{}',
    
    -- Execution status and results
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    exit_code INTEGER,
    stdout TEXT,
    stderr TEXT,
    output_files JSONB DEFAULT '[]',
    
    -- Performance metrics
    execution_time_ms INTEGER,
    memory_usage_mb FLOAT,
    cpu_usage_percent FLOAT,
    disk_usage_mb FLOAT,
    
    -- Timing information
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Security and compliance
    constitutional_hash VARCHAR(64) NOT NULL,
    policy_violations JSONB DEFAULT '[]',
    security_violations JSONB DEFAULT '[]',
    
    -- Error and debugging information
    error_message TEXT,
    debug_info JSONB DEFAULT '{}',
    
    -- Cleanup information
    cleaned_up BOOLEAN DEFAULT FALSE,
    cleanup_at TIMESTAMPTZ,
    
    -- Additional metadata
    metadata JSONB DEFAULT '{}',
    tags JSONB DEFAULT '[]'
);

-- Create indexes for sandbox_executions
CREATE INDEX IF NOT EXISTS idx_sandbox_executions_execution_id ON sandbox_executions(execution_id);
CREATE INDEX IF NOT EXISTS idx_sandbox_executions_agent_id ON sandbox_executions(agent_id);
CREATE INDEX IF NOT EXISTS idx_sandbox_executions_status ON sandbox_executions(status);
CREATE INDEX IF NOT EXISTS idx_sandbox_executions_environment ON sandbox_executions(environment);
CREATE INDEX IF NOT EXISTS idx_sandbox_executions_created_at ON sandbox_executions(created_at);
CREATE INDEX IF NOT EXISTS idx_sandbox_executions_completed_at ON sandbox_executions(completed_at);
CREATE INDEX IF NOT EXISTS idx_sandbox_executions_container_id ON sandbox_executions(container_id);
CREATE INDEX IF NOT EXISTS idx_sandbox_executions_request_id ON sandbox_executions(request_id);
CREATE INDEX IF NOT EXISTS idx_sandbox_executions_session_id ON sandbox_executions(session_id);

-- Create GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_sandbox_executions_execution_context_gin ON sandbox_executions USING GIN(execution_context);
CREATE INDEX IF NOT EXISTS idx_sandbox_executions_metadata_gin ON sandbox_executions USING GIN(metadata);
CREATE INDEX IF NOT EXISTS idx_sandbox_executions_tags_gin ON sandbox_executions USING GIN(tags);
CREATE INDEX IF NOT EXISTS idx_sandbox_executions_policy_violations_gin ON sandbox_executions USING GIN(policy_violations);

-- Create execution_policies table
CREATE TABLE IF NOT EXISTS execution_policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- Policy scope
    agent_id VARCHAR(100),
    agent_type VARCHAR(50),
    environment VARCHAR(50),
    
    -- Policy definition
    policy_name VARCHAR(200) NOT NULL,
    policy_description TEXT,
    policy_rules JSONB NOT NULL,
    
    -- Policy status
    is_active BOOLEAN DEFAULT TRUE,
    priority INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    
    -- Constitutional compliance
    constitutional_hash VARCHAR(64) NOT NULL,
    
    -- Metadata
    created_by VARCHAR(100),
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for execution_policies
CREATE INDEX IF NOT EXISTS idx_execution_policies_policy_id ON execution_policies(policy_id);
CREATE INDEX IF NOT EXISTS idx_execution_policies_agent_id ON execution_policies(agent_id);
CREATE INDEX IF NOT EXISTS idx_execution_policies_agent_type ON execution_policies(agent_type);
CREATE INDEX IF NOT EXISTS idx_execution_policies_environment ON execution_policies(environment);
CREATE INDEX IF NOT EXISTS idx_execution_policies_is_active ON execution_policies(is_active);
CREATE INDEX IF NOT EXISTS idx_execution_policies_priority ON execution_policies(priority);

-- Create GIN index for policy rules
CREATE INDEX IF NOT EXISTS idx_execution_policies_rules_gin ON execution_policies USING GIN(policy_rules);

-- Create execution_audit_logs table
CREATE TABLE IF NOT EXISTS execution_audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID NOT NULL,
    
    -- Audit event details
    event_type VARCHAR(50) NOT NULL,
    event_description TEXT NOT NULL,
    event_data JSONB DEFAULT '{}',
    
    -- Timing and context
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    container_id VARCHAR(100),
    
    -- Security context
    security_level VARCHAR(20) DEFAULT 'standard',
    violations_detected JSONB DEFAULT '[]',
    
    -- Constitutional compliance
    constitutional_hash VARCHAR(64) NOT NULL,
    
    -- Additional context
    metadata JSONB DEFAULT '{}'
);

-- Create indexes for execution_audit_logs
CREATE INDEX IF NOT EXISTS idx_execution_audit_logs_execution_id ON execution_audit_logs(execution_id);
CREATE INDEX IF NOT EXISTS idx_execution_audit_logs_event_type ON execution_audit_logs(event_type);
CREATE INDEX IF NOT EXISTS idx_execution_audit_logs_timestamp ON execution_audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_execution_audit_logs_container_id ON execution_audit_logs(container_id);

-- Add constraints and checks
ALTER TABLE sandbox_executions ADD CONSTRAINT chk_execution_status 
    CHECK (status IN ('pending', 'running', 'completed', 'failed', 'timeout', 'killed', 'error'));

ALTER TABLE sandbox_executions ADD CONSTRAINT chk_execution_environment 
    CHECK (environment IN ('python', 'bash', 'node', 'docker'));

ALTER TABLE sandbox_executions ADD CONSTRAINT chk_memory_limit_positive 
    CHECK (memory_limit_mb > 0);

ALTER TABLE sandbox_executions ADD CONSTRAINT chk_timeout_positive 
    CHECK (timeout_seconds > 0);

ALTER TABLE sandbox_executions ADD CONSTRAINT chk_cpu_limit_range 
    CHECK (cpu_limit > 0 AND cpu_limit <= 8.0);

ALTER TABLE execution_policies ADD CONSTRAINT chk_policy_priority_range 
    CHECK (priority >= 0 AND priority <= 1000);

-- Add comments for documentation
COMMENT ON TABLE sandbox_executions IS 'Records of code executions in secure sandbox environments';
COMMENT ON TABLE execution_policies IS 'Security and execution policies for different agents and environments';
COMMENT ON TABLE execution_audit_logs IS 'Audit trail for all execution events and security violations';

COMMENT ON COLUMN sandbox_executions.execution_id IS 'Human-readable unique identifier for the execution';
COMMENT ON COLUMN sandbox_executions.constitutional_hash IS 'Hash of constitutional principles used for security validation';
COMMENT ON COLUMN sandbox_executions.policy_violations IS 'Array of policy violations detected before execution';
COMMENT ON COLUMN sandbox_executions.security_violations IS 'Array of security violations detected during/after execution';

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_execution_policy_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic timestamp updates
CREATE TRIGGER trigger_update_execution_policy_updated_at
    BEFORE UPDATE ON execution_policies
    FOR EACH ROW
    EXECUTE FUNCTION update_execution_policy_updated_at();

-- Create view for active executions
CREATE OR REPLACE VIEW active_executions AS
SELECT 
    execution_id,
    agent_id,
    environment,
    status,
    created_at,
    started_at,
    execution_time_ms,
    memory_usage_mb,
    container_id
FROM sandbox_executions 
WHERE status IN ('pending', 'running')
ORDER BY created_at DESC;

-- Create view for execution statistics by environment
CREATE OR REPLACE VIEW execution_stats_by_environment AS
SELECT 
    environment,
    COUNT(*) as total_executions,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_executions,
    COUNT(CASE WHEN status IN ('failed', 'error', 'timeout') THEN 1 END) as failed_executions,
    AVG(execution_time_ms) as avg_execution_time_ms,
    AVG(memory_usage_mb) as avg_memory_usage_mb,
    MAX(execution_time_ms) as max_execution_time_ms,
    MIN(CASE WHEN execution_time_ms > 0 THEN execution_time_ms END) as min_execution_time_ms
FROM sandbox_executions 
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY environment
ORDER BY total_executions DESC;

-- Create view for execution statistics by agent
CREATE OR REPLACE VIEW execution_stats_by_agent AS
SELECT 
    agent_id,
    agent_type,
    COUNT(*) as total_executions,
    COUNT(CASE WHEN status = 'completed' THEN 1 END) as successful_executions,
    COUNT(CASE WHEN status IN ('failed', 'error', 'timeout') THEN 1 END) as failed_executions,
    COUNT(CASE WHEN array_length(policy_violations, 1) > 0 THEN 1 END) as policy_violations_count,
    COUNT(CASE WHEN array_length(security_violations, 1) > 0 THEN 1 END) as security_violations_count,
    AVG(execution_time_ms) as avg_execution_time_ms,
    MAX(created_at) as last_execution_at
FROM sandbox_executions 
WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY agent_id, agent_type
ORDER BY total_executions DESC;

-- Grant appropriate permissions (adjust user names as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON sandbox_executions TO sandbox_service_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON execution_policies TO sandbox_service_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON execution_audit_logs TO sandbox_service_user;
-- GRANT SELECT ON active_executions TO sandbox_service_user;
-- GRANT SELECT ON execution_stats_by_environment TO sandbox_service_user;
-- GRANT SELECT ON execution_stats_by_agent TO sandbox_service_user;

-- Insert some default execution policies
INSERT INTO execution_policies (
    policy_id, 
    environment, 
    policy_name, 
    policy_description, 
    policy_rules, 
    constitutional_hash, 
    created_by
) VALUES 
(
    'default-python-policy',
    'python',
    'Default Python Execution Policy',
    'Standard security policy for Python code execution',
    '{
        "allowed_imports": ["os", "sys", "json", "datetime", "math", "re", "urllib", "requests", "numpy", "pandas"],
        "blocked_imports": ["subprocess", "multiprocessing", "socket", "threading"],
        "max_execution_time": 120,
        "max_memory_mb": 256,
        "network_access": false,
        "file_write_access": false
    }',
    'cdd01ef066bc6cf2',
    'system'
),
(
    'default-bash-policy',
    'bash',
    'Default Bash Execution Policy',
    'Standard security policy for Bash script execution',
    '{
        "allowed_commands": ["ls", "cat", "grep", "awk", "sed", "sort", "head", "tail", "wc", "cut"],
        "blocked_commands": ["rm", "curl", "wget", "ssh", "nc", "netcat", "dd", "mount"],
        "max_execution_time": 60,
        "max_memory_mb": 128,
        "network_access": false,
        "file_write_access": false
    }',
    'cdd01ef066bc6cf2',
    'system'
),
(
    'default-node-policy',
    'node',
    'Default Node.js Execution Policy',
    'Standard security policy for Node.js code execution',
    '{
        "allowed_modules": ["fs", "path", "crypto", "util", "os"],
        "blocked_modules": ["child_process", "cluster", "net", "http", "https"],
        "max_execution_time": 90,
        "max_memory_mb": 256,
        "network_access": false,
        "file_write_access": false
    }',
    'cdd01ef066bc6cf2',
    'system'
)
ON CONFLICT (policy_id) DO NOTHING;