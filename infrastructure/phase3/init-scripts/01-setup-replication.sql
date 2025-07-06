-- ACGS Phase 3A PostgreSQL Primary Initialization
-- Constitutional Hash: cdd01ef066bc6cf2

-- Create replication user
CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD 'acgs_replication_password_2025';

-- Create Grafana database and user
CREATE DATABASE grafana;
CREATE USER grafana WITH ENCRYPTED PASSWORD 'acgs_grafana_db_2025';
GRANT ALL PRIVILEGES ON DATABASE grafana TO grafana;

-- Create monitoring user
CREATE USER postgres_exporter WITH ENCRYPTED PASSWORD 'acgs_exporter_password_2025';
GRANT CONNECT ON DATABASE acgs_production TO postgres_exporter;
GRANT pg_monitor TO postgres_exporter;

-- Create replication slots for replicas
SELECT pg_create_physical_replication_slot('replica_a_slot');
SELECT pg_create_physical_replication_slot('replica_b_slot');

-- Constitutional compliance table
CREATE TABLE IF NOT EXISTS constitutional_compliance (
    id SERIAL PRIMARY KEY,
    hash VARCHAR(16) NOT NULL DEFAULT 'cdd01ef066bc6cf2',
    component VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(50) NOT NULL DEFAULT 'compliant',
    zone VARCHAR(50),
    metadata JSONB
);

-- Insert initial compliance records
INSERT INTO constitutional_compliance (component, status, zone) VALUES 
    ('postgresql_primary', 'compliant', 'zone-a'),
    ('database_ha_setup', 'compliant', 'multi-zone'),
    ('replication_setup', 'compliant', 'multi-zone');

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_constitutional_hash ON constitutional_compliance(hash);
CREATE INDEX IF NOT EXISTS idx_constitutional_timestamp ON constitutional_compliance(timestamp);
CREATE INDEX IF NOT EXISTS idx_constitutional_component ON constitutional_compliance(component);
CREATE INDEX IF NOT EXISTS idx_constitutional_zone ON constitutional_compliance(zone);

-- Create performance monitoring tables
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(255) NOT NULL,
    metric_value NUMERIC NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    component VARCHAR(255),
    zone VARCHAR(50),
    constitutional_hash VARCHAR(16) DEFAULT 'cdd01ef066bc6cf2'
);

CREATE INDEX IF NOT EXISTS idx_performance_timestamp ON performance_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_performance_component ON performance_metrics(component);

-- Create ACGS service tables
CREATE TABLE IF NOT EXISTS acgs_services (
    id SERIAL PRIMARY KEY,
    service_name VARCHAR(255) NOT NULL,
    service_version VARCHAR(50),
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    zone VARCHAR(50),
    endpoint VARCHAR(255),
    health_check_url VARCHAR(255),
    constitutional_hash VARCHAR(16) DEFAULT 'cdd01ef066bc6cf2',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert initial service records
INSERT INTO acgs_services (service_name, status, zone, constitutional_hash) VALUES
    ('auth-service', 'active', 'multi-zone', 'cdd01ef066bc6cf2'),
    ('constitutional-ai', 'active', 'multi-zone', 'cdd01ef066bc6cf2'),
    ('policy-governance', 'active', 'multi-zone', 'cdd01ef066bc6cf2'),
    ('governance-synthesis', 'active', 'multi-zone', 'cdd01ef066bc6cf2'),
    ('database-ha', 'active', 'multi-zone', 'cdd01ef066bc6cf2');

-- Create audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id SERIAL PRIMARY KEY,
    action VARCHAR(255) NOT NULL,
    component VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    details JSONB,
    constitutional_hash VARCHAR(16) DEFAULT 'cdd01ef066bc6cf2',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_component ON audit_log(component);

-- Create function to update constitutional compliance
CREATE OR REPLACE FUNCTION update_constitutional_compliance(
    p_component VARCHAR(255),
    p_status VARCHAR(50),
    p_zone VARCHAR(50) DEFAULT NULL,
    p_metadata JSONB DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    INSERT INTO constitutional_compliance (component, status, zone, metadata)
    VALUES (p_component, p_status, p_zone, p_metadata);
END;
$$ LANGUAGE plpgsql;

-- Create function to log audit events
CREATE OR REPLACE FUNCTION log_audit_event(
    p_action VARCHAR(255),
    p_component VARCHAR(255),
    p_user_id VARCHAR(255) DEFAULT NULL,
    p_details JSONB DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    INSERT INTO audit_log (action, component, user_id, details)
    VALUES (p_action, p_component, p_user_id, p_details);
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT SELECT ON constitutional_compliance TO postgres_exporter;
GRANT SELECT ON performance_metrics TO postgres_exporter;
GRANT SELECT ON acgs_services TO postgres_exporter;
GRANT SELECT ON audit_log TO postgres_exporter;

-- Log the initialization
SELECT log_audit_event('database_initialization', 'postgresql_primary', 'system', '{"constitutional_hash": "cdd01ef066bc6cf2", "phase": "3A", "setup": "database_ha"}');

-- Update pg_hba.conf for replication
-- Add replication entries to pg_hba.conf
\! echo "host replication replicator 172.33.0.0/24 md5" >> /var/lib/postgresql/data/pg_hba.conf
\! echo "host acgs_production acgs_admin 172.33.0.0/24 md5" >> /var/lib/postgresql/data/pg_hba.conf

-- Reload configuration
SELECT pg_reload_conf();
