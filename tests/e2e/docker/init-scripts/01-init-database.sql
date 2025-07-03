-- ACGS E2E Test Database Initialization
-- Creates necessary schemas, tables, and test data for E2E testing

-- Create schemas
CREATE SCHEMA IF NOT EXISTS acgs_test;
CREATE SCHEMA IF NOT EXISTS acgs_audit;
CREATE SCHEMA IF NOT EXISTS acgs_governance;

-- Set search path
SET search_path TO acgs_test, acgs_audit, acgs_governance, public;

-- =============================================================================
-- Core Tables
-- =============================================================================

-- Policies table
CREATE TABLE IF NOT EXISTS acgs_test.policies (
    id SERIAL PRIMARY KEY,
    policy_id VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(500) NOT NULL,
    version VARCHAR(50) NOT NULL DEFAULT '1.0.0',
    description TEXT,
    content JSONB NOT NULL,
    constitutional_hash VARCHAR(64) NOT NULL DEFAULT 'cdd01ef066bc6cf2',
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by VARCHAR(255),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Policy rules table
CREATE TABLE IF NOT EXISTS acgs_test.policy_rules (
    id SERIAL PRIMARY KEY,
    policy_id VARCHAR(255) REFERENCES acgs_test.policies(policy_id),
    rule_id VARCHAR(255) NOT NULL,
    condition TEXT NOT NULL,
    action TEXT NOT NULL,
    priority INTEGER DEFAULT 1,
    enabled BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Constitutional validations table
CREATE TABLE IF NOT EXISTS acgs_test.constitutional_validations (
    id SERIAL PRIMARY KEY,
    validation_id VARCHAR(255) UNIQUE NOT NULL,
    policy_id VARCHAR(255),
    constitutional_hash VARCHAR(64) NOT NULL,
    compliance_score DECIMAL(5,4),
    is_compliant BOOLEAN NOT NULL,
    validation_result JSONB,
    validated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    validator_service VARCHAR(100)
);

-- HITL assessments table
CREATE TABLE IF NOT EXISTS acgs_test.hitl_assessments (
    id SERIAL PRIMARY KEY,
    assessment_id VARCHAR(255) UNIQUE NOT NULL,
    request_context JSONB NOT NULL,
    uncertainty_score DECIMAL(5,4),
    confidence_level DECIMAL(5,4),
    requires_human_review BOOLEAN DEFAULT false,
    assessment_result JSONB,
    assessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    response_time_ms INTEGER
);

-- =============================================================================
-- Audit Tables
-- =============================================================================

-- Audit log table
CREATE TABLE IF NOT EXISTS acgs_audit.audit_log (
    id SERIAL PRIMARY KEY,
    event_id VARCHAR(255) UNIQUE NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    user_id VARCHAR(255),
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    action VARCHAR(100) NOT NULL,
    event_data JSONB,
    constitutional_hash VARCHAR(64),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    ip_address INET,
    user_agent TEXT
);

-- Performance metrics table
CREATE TABLE IF NOT EXISTS acgs_audit.performance_metrics (
    id SERIAL PRIMARY KEY,
    metric_id VARCHAR(255) UNIQUE NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    operation_name VARCHAR(100) NOT NULL,
    latency_ms INTEGER NOT NULL,
    success BOOLEAN NOT NULL,
    error_message TEXT,
    metadata JSONB,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- =============================================================================
-- Governance Tables
-- =============================================================================

-- Agent coordination table
CREATE TABLE IF NOT EXISTS acgs_governance.agent_coordination (
    id SERIAL PRIMARY KEY,
    coordination_id VARCHAR(255) UNIQUE NOT NULL,
    scenario_type VARCHAR(100) NOT NULL,
    participants JSONB NOT NULL,
    consensus_threshold DECIMAL(3,2),
    consensus_reached BOOLEAN DEFAULT false,
    final_score DECIMAL(5,4),
    coordination_result JSONB,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    duration_ms INTEGER
);

-- Blackboard state table
CREATE TABLE IF NOT EXISTS acgs_governance.blackboard_state (
    id SERIAL PRIMARY KEY,
    state_key VARCHAR(255) UNIQUE NOT NULL,
    state_data JSONB NOT NULL,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- =============================================================================
-- Indexes for Performance
-- =============================================================================

-- Policies indexes
CREATE INDEX IF NOT EXISTS idx_policies_policy_id ON acgs_test.policies(policy_id);
CREATE INDEX IF NOT EXISTS idx_policies_constitutional_hash ON acgs_test.policies(constitutional_hash);
CREATE INDEX IF NOT EXISTS idx_policies_status ON acgs_test.policies(status);
CREATE INDEX IF NOT EXISTS idx_policies_created_at ON acgs_test.policies(created_at);

-- Constitutional validations indexes
CREATE INDEX IF NOT EXISTS idx_constitutional_validations_policy_id ON acgs_test.constitutional_validations(policy_id);
CREATE INDEX IF NOT EXISTS idx_constitutional_validations_hash ON acgs_test.constitutional_validations(constitutional_hash);
CREATE INDEX IF NOT EXISTS idx_constitutional_validations_validated_at ON acgs_test.constitutional_validations(validated_at);

-- HITL assessments indexes
CREATE INDEX IF NOT EXISTS idx_hitl_assessments_assessed_at ON acgs_test.hitl_assessments(assessed_at);
CREATE INDEX IF NOT EXISTS idx_hitl_assessments_requires_review ON acgs_test.hitl_assessments(requires_human_review);

-- Audit log indexes
CREATE INDEX IF NOT EXISTS idx_audit_log_event_type ON acgs_audit.audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_log_service_name ON acgs_audit.audit_log(service_name);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON acgs_audit.audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_log_constitutional_hash ON acgs_audit.audit_log(constitutional_hash);

-- Performance metrics indexes
CREATE INDEX IF NOT EXISTS idx_performance_metrics_service ON acgs_audit.performance_metrics(service_name);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_operation ON acgs_audit.performance_metrics(operation_name);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_recorded_at ON acgs_audit.performance_metrics(recorded_at);

-- =============================================================================
-- Test Data
-- =============================================================================

-- Insert sample policies for testing
INSERT INTO acgs_test.policies (policy_id, name, description, content, constitutional_hash) VALUES
('test_policy_001', 'Test Access Control Policy', 'Basic access control policy for testing', 
 '{"type": "access_control", "rules": [{"condition": "user.role == admin", "action": "allow"}]}', 
 'cdd01ef066bc6cf2'),
('test_policy_002', 'Test Data Governance Policy', 'Data governance policy for testing',
 '{"type": "data_governance", "rules": [{"condition": "data.classification == sensitive", "action": "encrypt"}]}',
 'cdd01ef066bc6cf2'),
('test_policy_003', 'Test AI Ethics Policy', 'AI ethics policy for testing',
 '{"type": "ai_ethics", "rules": [{"condition": "ai.decision.confidence < 0.8", "action": "require_human_review"}]}',
 'cdd01ef066bc6cf2')
ON CONFLICT (policy_id) DO NOTHING;

-- Insert sample policy rules
INSERT INTO acgs_test.policy_rules (policy_id, rule_id, condition, action, priority) VALUES
('test_policy_001', 'rule_001_1', 'user.role == admin', 'allow', 1),
('test_policy_001', 'rule_001_2', 'user.role == user', 'allow_limited', 2),
('test_policy_002', 'rule_002_1', 'data.classification == sensitive', 'encrypt', 1),
('test_policy_003', 'rule_003_1', 'ai.decision.confidence < 0.8', 'require_human_review', 1)
ON CONFLICT DO NOTHING;

-- Insert sample constitutional validations
INSERT INTO acgs_test.constitutional_validations (validation_id, policy_id, constitutional_hash, compliance_score, is_compliant, validation_result) VALUES
('validation_001', 'test_policy_001', 'cdd01ef066bc6cf2', 0.95, true, '{"status": "compliant", "issues": []}'),
('validation_002', 'test_policy_002', 'cdd01ef066bc6cf2', 0.92, true, '{"status": "compliant", "issues": []}'),
('validation_003', 'test_policy_003', 'cdd01ef066bc6cf2', 0.88, true, '{"status": "compliant", "issues": []}')
ON CONFLICT (validation_id) DO NOTHING;

-- Insert sample HITL assessments
INSERT INTO acgs_test.hitl_assessments (assessment_id, request_context, uncertainty_score, confidence_level, requires_human_review, response_time_ms) VALUES
('hitl_001', '{"policy_id": "test_policy_001", "action": "validation"}', 0.15, 0.85, false, 3),
('hitl_002', '{"policy_id": "test_policy_002", "action": "validation"}', 0.25, 0.75, false, 4),
('hitl_003', '{"policy_id": "test_policy_003", "action": "validation"}', 0.65, 0.35, true, 2)
ON CONFLICT (assessment_id) DO NOTHING;

-- Insert sample blackboard state
INSERT INTO acgs_governance.blackboard_state (state_key, state_data) VALUES
('governance_state', '{"current_policy": "test_policy_001", "validation_status": "completed", "compliance_score": 0.95}'),
('coordination_state', '{"active_agents": 3, "consensus_threshold": 0.7, "current_score": 0.85}')
ON CONFLICT (state_key) DO NOTHING;

-- =============================================================================
-- Functions and Triggers
-- =============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for policies table
DROP TRIGGER IF EXISTS update_policies_updated_at ON acgs_test.policies;
CREATE TRIGGER update_policies_updated_at
    BEFORE UPDATE ON acgs_test.policies
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger for blackboard state table
DROP TRIGGER IF EXISTS update_blackboard_state_updated_at ON acgs_governance.blackboard_state;
CREATE TRIGGER update_blackboard_state_updated_at
    BEFORE UPDATE ON acgs_governance.blackboard_state
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- =============================================================================
-- Permissions
-- =============================================================================

-- Grant permissions to test user
GRANT USAGE ON SCHEMA acgs_test TO test_user;
GRANT USAGE ON SCHEMA acgs_audit TO test_user;
GRANT USAGE ON SCHEMA acgs_governance TO test_user;

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA acgs_test TO test_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA acgs_audit TO test_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA acgs_governance TO test_user;

GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA acgs_test TO test_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA acgs_audit TO test_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA acgs_governance TO test_user;

-- =============================================================================
-- Completion
-- =============================================================================

-- Log initialization completion
INSERT INTO acgs_audit.audit_log (event_id, event_type, service_name, action, event_data, constitutional_hash) VALUES
('init_001', 'database_initialization', 'e2e_test_setup', 'initialize_database', 
 '{"schemas_created": ["acgs_test", "acgs_audit", "acgs_governance"], "tables_created": 8, "test_data_inserted": true}',
 'cdd01ef066bc6cf2');

-- Analyze tables for better query performance
ANALYZE;
