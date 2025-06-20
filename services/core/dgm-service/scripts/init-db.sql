-- DGM Service Database Initialization Script
-- Creates tables and indexes for Darwin Gödel Machine Service

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create DGM schema
CREATE SCHEMA IF NOT EXISTS dgm;

-- Set search path
SET search_path TO dgm, public;

-- Create enum types
CREATE TYPE improvement_status AS ENUM (
    'pending',
    'running',
    'completed',
    'failed',
    'rolled_back'
);

CREATE TYPE constitutional_compliance_level AS ENUM (
    'compliant',
    'warning',
    'violation',
    'critical'
);

CREATE TYPE bandit_algorithm_type AS ENUM (
    'ucb',
    'epsilon_greedy',
    'thompson_sampling',
    'exp3'
);

-- DGM Archive Table
CREATE TABLE IF NOT EXISTS dgm_archive (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    improvement_id UUID NOT NULL UNIQUE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    description TEXT NOT NULL,
    algorithm_changes JSONB,
    performance_before JSONB,
    performance_after JSONB,
    constitutional_compliance_score DECIMAL(3,2) NOT NULL CHECK (constitutional_compliance_score >= 0 AND constitutional_compliance_score <= 1),
    compliance_details JSONB,
    status improvement_status NOT NULL DEFAULT 'pending',
    rollback_data JSONB,
    metadata JSONB,
    created_by VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Performance Metrics Table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    service_name VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,6) NOT NULL,
    metric_unit VARCHAR(50),
    tags JSONB,
    improvement_id UUID REFERENCES dgm_archive(improvement_id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Constitutional Compliance Log
CREATE TABLE IF NOT EXISTS constitutional_compliance_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    improvement_id UUID REFERENCES dgm_archive(improvement_id),
    compliance_level constitutional_compliance_level NOT NULL,
    compliance_score DECIMAL(3,2) NOT NULL CHECK (compliance_score >= 0 AND compliance_score <= 1),
    violated_principles TEXT[],
    compliance_details JSONB,
    validator_version VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Bandit Algorithm State
CREATE TABLE IF NOT EXISTS bandit_state (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    algorithm_type bandit_algorithm_type NOT NULL,
    arm_id VARCHAR(100) NOT NULL,
    arm_description TEXT,
    total_pulls INTEGER NOT NULL DEFAULT 0,
    total_reward DECIMAL(15,6) NOT NULL DEFAULT 0,
    average_reward DECIMAL(15,6) NOT NULL DEFAULT 0,
    confidence_bound DECIMAL(15,6),
    last_pulled_at TIMESTAMPTZ,
    metadata JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(algorithm_type, arm_id)
);

-- Improvement Workspace
CREATE TABLE IF NOT EXISTS improvement_workspace (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    improvement_id UUID NOT NULL UNIQUE,
    workspace_path VARCHAR(500) NOT NULL,
    status improvement_status NOT NULL DEFAULT 'pending',
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    resource_usage JSONB,
    logs TEXT,
    artifacts JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- System Configuration
CREATE TABLE IF NOT EXISTS system_configuration (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    config_key VARCHAR(100) NOT NULL UNIQUE,
    config_value JSONB NOT NULL,
    description TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_dgm_archive_timestamp ON dgm_archive(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_dgm_archive_status ON dgm_archive(status);
CREATE INDEX IF NOT EXISTS idx_dgm_archive_compliance_score ON dgm_archive(constitutional_compliance_score);
CREATE INDEX IF NOT EXISTS idx_dgm_archive_created_at ON dgm_archive(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_service_metric ON performance_metrics(service_name, metric_name);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_improvement_id ON performance_metrics(improvement_id);

CREATE INDEX IF NOT EXISTS idx_compliance_log_timestamp ON constitutional_compliance_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_compliance_log_improvement_id ON constitutional_compliance_log(improvement_id);
CREATE INDEX IF NOT EXISTS idx_compliance_log_level ON constitutional_compliance_log(compliance_level);

CREATE INDEX IF NOT EXISTS idx_bandit_state_algorithm_arm ON bandit_state(algorithm_type, arm_id);
CREATE INDEX IF NOT EXISTS idx_bandit_state_last_pulled ON bandit_state(last_pulled_at DESC);

CREATE INDEX IF NOT EXISTS idx_workspace_improvement_id ON improvement_workspace(improvement_id);
CREATE INDEX IF NOT EXISTS idx_workspace_status ON improvement_workspace(status);

CREATE INDEX IF NOT EXISTS idx_system_config_key ON system_configuration(config_key);
CREATE INDEX IF NOT EXISTS idx_system_config_active ON system_configuration(is_active);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_dgm_archive_updated_at BEFORE UPDATE ON dgm_archive
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_bandit_state_updated_at BEFORE UPDATE ON bandit_state
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workspace_updated_at BEFORE UPDATE ON improvement_workspace
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_config_updated_at BEFORE UPDATE ON system_configuration
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default system configuration
INSERT INTO system_configuration (config_key, config_value, description) VALUES
('constitutional_compliance_threshold', '0.8', 'Minimum constitutional compliance score required for improvements'),
('improvement_cycle_interval', '3600', 'Interval between improvement cycles in seconds'),
('max_improvement_attempts', '5', 'Maximum number of improvement attempts per cycle'),
('safety_exploration_rate', '0.1', 'Rate of exploration for safety-critical improvements'),
('archive_retention_days', '365', 'Number of days to retain improvement archive entries'),
('bandit_algorithm', '"ucb"', 'Default bandit algorithm for exploration'),
('bandit_exploration_parameter', '2.0', 'Exploration parameter for bandit algorithms'),
('performance_monitoring_enabled', 'true', 'Enable performance monitoring'),
('performance_metrics_interval', '60', 'Interval for collecting performance metrics in seconds')
ON CONFLICT (config_key) DO NOTHING;

-- Create views for common queries
CREATE OR REPLACE VIEW recent_improvements AS
SELECT 
    improvement_id,
    timestamp,
    description,
    status,
    constitutional_compliance_score,
    performance_before->>'overall_score' as performance_before_score,
    performance_after->>'overall_score' as performance_after_score
FROM dgm_archive
WHERE timestamp >= NOW() - INTERVAL '30 days'
ORDER BY timestamp DESC;

CREATE OR REPLACE VIEW compliance_summary AS
SELECT 
    DATE_TRUNC('day', timestamp) as date,
    compliance_level,
    COUNT(*) as count,
    AVG(compliance_score) as avg_score
FROM constitutional_compliance_log
WHERE timestamp >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', timestamp), compliance_level
ORDER BY date DESC, compliance_level;

CREATE OR REPLACE VIEW bandit_performance AS
SELECT 
    algorithm_type,
    arm_id,
    arm_description,
    total_pulls,
    average_reward,
    confidence_bound,
    last_pulled_at
FROM bandit_state
ORDER BY algorithm_type, average_reward DESC;

-- Grant permissions
GRANT USAGE ON SCHEMA dgm TO acgs_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA dgm TO acgs_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA dgm TO acgs_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA dgm TO acgs_user;
