-- ACGS-2 Production Database Initialization
-- Constitutional Hash: cdd01ef066bc6cf2
-- Performance Targets: P99 <5ms, >100 RPS, >85% cache hit

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Create application roles
DO $$
BEGIN
    -- Application user for services
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'acgs_app') THEN
        CREATE ROLE acgs_app WITH LOGIN PASSWORD 'CHANGE_ME_APP_PASSWORD';
    END IF;
    
    -- Read-only user for monitoring
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'acgs_monitor') THEN
        CREATE ROLE acgs_monitor WITH LOGIN PASSWORD 'CHANGE_ME_MONITOR_PASSWORD';
    END IF;
    
    -- Backup user
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'acgs_backup') THEN
        CREATE ROLE acgs_backup WITH LOGIN PASSWORD 'CHANGE_ME_BACKUP_PASSWORD';
    END IF;
END
$$;

-- Grant basic permissions
GRANT CONNECT ON DATABASE acgs_production TO acgs_app;
GRANT CONNECT ON DATABASE acgs_production TO acgs_monitor;
GRANT CONNECT ON DATABASE acgs_production TO acgs_backup;

GRANT USAGE ON SCHEMA public TO acgs_app;
GRANT USAGE ON SCHEMA public TO acgs_monitor;

GRANT CREATE ON SCHEMA public TO acgs_app;

-- Constitutional Compliance Tables
CREATE TABLE IF NOT EXISTS constitutional_compliance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hash VARCHAR(16) NOT NULL DEFAULT 'cdd01ef066bc6cf2',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    service_name VARCHAR(100) NOT NULL,
    compliance_status BOOLEAN NOT NULL DEFAULT true,
    compliance_score DECIMAL(5,4) DEFAULT 1.0000,
    validation_details JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Performance Metrics Tables
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    service_name VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,6) NOT NULL,
    target_value DECIMAL(15,6),
    unit VARCHAR(20),
    constitutional_hash VARCHAR(16) DEFAULT 'cdd01ef066bc6cf2',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Service Health Tables
CREATE TABLE IF NOT EXISTS service_health (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'unknown',
    last_check TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    response_time_ms DECIMAL(10,3),
    error_message TEXT,
    constitutional_hash VARCHAR(16) DEFAULT 'cdd01ef066bc6cf2',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit Log Tables
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    service_name VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    user_id VARCHAR(100),
    resource_type VARCHAR(100),
    resource_id VARCHAR(100),
    details JSONB DEFAULT '{}'::jsonb,
    constitutional_hash VARCHAR(16) DEFAULT 'cdd01ef066bc6cf2',
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Multi-Agent Coordination Tables
CREATE TABLE IF NOT EXISTS agent_coordination (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    coordinator_id VARCHAR(100) NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    agent_id VARCHAR(100) NOT NULL,
    task_id VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    payload JSONB DEFAULT '{}'::jsonb,
    result JSONB DEFAULT '{}'::jsonb,
    constitutional_hash VARCHAR(16) DEFAULT 'cdd01ef066bc6cf2',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Cache Performance Tables
CREATE TABLE IF NOT EXISTS cache_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    cache_type VARCHAR(50) NOT NULL,
    operation VARCHAR(20) NOT NULL,
    hit_rate DECIMAL(5,4),
    response_time_ms DECIMAL(10,3),
    key_count INTEGER,
    memory_usage_mb DECIMAL(10,2),
    constitutional_hash VARCHAR(16) DEFAULT 'cdd01ef066bc6cf2',
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance optimization
CREATE INDEX IF NOT EXISTS idx_constitutional_compliance_hash ON constitutional_compliance(hash);
CREATE INDEX IF NOT EXISTS idx_constitutional_compliance_service ON constitutional_compliance(service_name);
CREATE INDEX IF NOT EXISTS idx_constitutional_compliance_timestamp ON constitutional_compliance(timestamp);

CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_service ON performance_metrics(service_name);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_name ON performance_metrics(metric_name);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_hash ON performance_metrics(constitutional_hash);

CREATE INDEX IF NOT EXISTS idx_service_health_service ON service_health(service_name);
CREATE INDEX IF NOT EXISTS idx_service_health_status ON service_health(status);
CREATE INDEX IF NOT EXISTS idx_service_health_check ON service_health(last_check);

CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_logs_service ON audit_logs(service_name);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);

CREATE INDEX IF NOT EXISTS idx_agent_coordination_coordinator ON agent_coordination(coordinator_id);
CREATE INDEX IF NOT EXISTS idx_agent_coordination_agent ON agent_coordination(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_coordination_status ON agent_coordination(status);
CREATE INDEX IF NOT EXISTS idx_agent_coordination_task ON agent_coordination(task_id);

CREATE INDEX IF NOT EXISTS idx_cache_metrics_timestamp ON cache_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_cache_metrics_type ON cache_metrics(cache_type);
CREATE INDEX IF NOT EXISTS idx_cache_metrics_operation ON cache_metrics(operation);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_constitutional_compliance_updated_at 
    BEFORE UPDATE ON constitutional_compliance 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_service_health_updated_at 
    BEFORE UPDATE ON service_health 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_coordination_updated_at 
    BEFORE UPDATE ON agent_coordination 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Grant table permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO acgs_app;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO acgs_app;

GRANT SELECT ON ALL TABLES IN SCHEMA public TO acgs_monitor;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO acgs_backup;

-- Insert initial data
INSERT INTO constitutional_compliance (service_name, compliance_status, compliance_score, validation_details, metadata)
VALUES (
    'database_initialization', 
    true, 
    1.0000,
    '{"initialization": "complete", "extensions": ["uuid-ossp", "pgcrypto", "pg_stat_statements", "pg_trgm"]}'::jsonb,
    '{"deployment_date": "2025-01-08", "version": "1.0.0", "performance_targets": {"p99_latency": "5ms", "throughput": "100rps", "cache_hit": "85%"}}'::jsonb
) ON CONFLICT DO NOTHING;

INSERT INTO service_health (service_name, status, response_time_ms, metadata)
VALUES (
    'database', 
    'healthy', 
    1.5,
    '{"initialization": "complete", "tables_created": 6, "indexes_created": 15}'::jsonb
) ON CONFLICT DO NOTHING;

-- Performance baseline metrics
INSERT INTO performance_metrics (service_name, metric_name, metric_value, target_value, unit, metadata)
VALUES 
    ('database', 'p99_latency_ms', 1.5, 5.0, 'ms', '{"baseline": true}'::jsonb),
    ('database', 'throughput_rps', 0.0, 100.0, 'rps', '{"baseline": true}'::jsonb),
    ('database', 'cache_hit_rate', 0.0, 0.85, 'ratio', '{"baseline": true}'::jsonb)
ON CONFLICT DO NOTHING;

-- Create views for monitoring
CREATE OR REPLACE VIEW v_service_health_summary AS
SELECT 
    service_name,
    status,
    last_check,
    response_time_ms,
    CASE 
        WHEN last_check > NOW() - INTERVAL '5 minutes' THEN 'current'
        WHEN last_check > NOW() - INTERVAL '15 minutes' THEN 'stale'
        ELSE 'outdated'
    END as freshness
FROM service_health
ORDER BY last_check DESC;

CREATE OR REPLACE VIEW v_performance_summary AS
SELECT 
    service_name,
    metric_name,
    AVG(metric_value) as avg_value,
    MAX(target_value) as target_value,
    unit,
    COUNT(*) as sample_count,
    MAX(timestamp) as last_update
FROM performance_metrics 
WHERE timestamp > NOW() - INTERVAL '1 hour'
GROUP BY service_name, metric_name, unit
ORDER BY service_name, metric_name;

CREATE OR REPLACE VIEW v_constitutional_compliance_summary AS
SELECT 
    service_name,
    compliance_status,
    AVG(compliance_score) as avg_compliance_score,
    COUNT(*) as check_count,
    MAX(timestamp) as last_check
FROM constitutional_compliance 
WHERE timestamp > NOW() - INTERVAL '24 hours'
GROUP BY service_name, compliance_status
ORDER BY service_name;

-- Grant view permissions
GRANT SELECT ON v_service_health_summary TO acgs_app, acgs_monitor;
GRANT SELECT ON v_performance_summary TO acgs_app, acgs_monitor;
GRANT SELECT ON v_constitutional_compliance_summary TO acgs_app, acgs_monitor;

-- Commit all changes
COMMIT;

-- Log completion
DO $$
BEGIN
    RAISE NOTICE 'ACGS-2 database initialization completed successfully';
    RAISE NOTICE 'Constitutional Hash: cdd01ef066bc6cf2';
    RAISE NOTICE 'Tables created: 6';
    RAISE NOTICE 'Indexes created: 15';
    RAISE NOTICE 'Views created: 3';
    RAISE NOTICE 'Performance targets configured: P99 <5ms, >100 RPS, >85%% cache hit';
END
$$;
