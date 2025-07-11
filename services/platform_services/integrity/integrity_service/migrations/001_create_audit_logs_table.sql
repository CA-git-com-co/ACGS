-- ACGS-2 Persistent Audit Logs Table Migration
-- Constitutional Hash: cdd01ef066bc6cf2
-- 
-- This migration creates the audit_logs table with:
-- - Hash chaining for tamper detection
-- - Multi-tenant Row Level Security (RLS)
-- - Performance-optimized indexing for <5ms queries
-- - Constitutional compliance validation

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create audit_logs table with hash chaining
CREATE TABLE IF NOT EXISTS audit_logs (
    -- Primary key and sequencing
    id SERIAL PRIMARY KEY,
    
    -- Timestamp information
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Event data (JSONB for flexible structure and indexing)
    event_data JSONB NOT NULL,
    
    -- Hash chaining for tamper detection
    prev_hash TEXT,
    current_hash TEXT NOT NULL,
    
    -- Multi-tenant support
    tenant_id UUID,
    user_id TEXT,
    
    -- Service and event classification
    service_name TEXT NOT NULL,
    event_type TEXT NOT NULL,
    
    -- Constitutional compliance
    constitutional_hash TEXT NOT NULL DEFAULT 'cdd01ef066bc6cf2',
    
    -- Constraints
    CONSTRAINT audit_logs_hash_not_empty CHECK (length(current_hash) > 0),
    CONSTRAINT audit_logs_constitutional_hash_valid CHECK (constitutional_hash = 'cdd01ef066bc6cf2'),
    CONSTRAINT audit_logs_service_name_not_empty CHECK (length(service_name) > 0),
    CONSTRAINT audit_logs_event_type_not_empty CHECK (length(event_type) > 0)
);

-- Enable Row Level Security for multi-tenant isolation
ALTER TABLE audit_logs ENABLE ROW LEVEL SECURITY;

-- Create RLS policy for multi-tenant isolation
-- Users can only access audit logs for their tenant
DROP POLICY IF EXISTS audit_logs_tenant_isolation ON audit_logs;
CREATE POLICY audit_logs_tenant_isolation ON audit_logs
    FOR ALL TO PUBLIC
    USING (
        -- Allow access if tenant matches current session tenant
        tenant_id = COALESCE(
            current_setting('app.current_tenant_id', true)::UUID,
            '00000000-0000-0000-0000-000000000000'::UUID
        )
        -- Or if RLS is bypassed (for system operations)
        OR current_setting('app.bypass_rls', true) = 'true'
        -- Or if user has admin privileges
        OR current_setting('app.user_role', true) = 'admin'
    );

-- Create performance-optimized indexes for <5ms query performance

-- Primary timestamp index (most common query pattern)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_timestamp_desc 
    ON audit_logs(timestamp DESC);

-- Multi-tenant timestamp index (tenant-specific queries)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_tenant_timestamp 
    ON audit_logs(tenant_id, timestamp DESC)
    WHERE tenant_id IS NOT NULL;

-- Event type classification index
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_event_type_timestamp 
    ON audit_logs(event_type, timestamp DESC);

-- Service name index for service-specific queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_service_timestamp 
    ON audit_logs(service_name, timestamp DESC);

-- Hash chain integrity index
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_current_hash 
    ON audit_logs(current_hash);

-- Previous hash lookup index (for chain verification)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_prev_hash 
    ON audit_logs(prev_hash)
    WHERE prev_hash IS NOT NULL;

-- Constitutional compliance index
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_constitutional_hash 
    ON audit_logs(constitutional_hash);

-- User activity index
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_user_timestamp 
    ON audit_logs(user_id, timestamp DESC)
    WHERE user_id IS NOT NULL;

-- Composite index for tenant + event type queries
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_tenant_event_timestamp 
    ON audit_logs(tenant_id, event_type, timestamp DESC)
    WHERE tenant_id IS NOT NULL;

-- GIN index for JSONB event_data (flexible querying)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_event_data_gin 
    ON audit_logs USING GIN(event_data);

-- Partial index for recent critical events (performance optimization)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_recent_critical 
    ON audit_logs(timestamp DESC, event_type)
    WHERE timestamp > NOW() - INTERVAL '30 days' 
    AND event_data->>'severity' IN ('high', 'critical');

-- Create function to automatically calculate hash chain on insert
CREATE OR REPLACE FUNCTION calculate_audit_hash_chain()
RETURNS TRIGGER AS $$
DECLARE
    previous_hash TEXT;
    event_str TEXT;
    chain_input TEXT;
    calculated_hash TEXT;
BEGIN
    -- Get the previous hash from the most recent record for this tenant
    SELECT current_hash INTO previous_hash
    FROM audit_logs
    WHERE tenant_id = NEW.tenant_id OR (NEW.tenant_id IS NULL AND tenant_id IS NULL)
    ORDER BY timestamp DESC, id DESC
    LIMIT 1;
    
    -- Use 'genesis' if no previous hash exists
    IF previous_hash IS NULL THEN
        previous_hash := 'genesis';
    END IF;
    
    -- Create deterministic string representation of event data
    event_str := NEW.event_data::text;
    
    -- Create chain input for hashing
    chain_input := previous_hash || ':' || event_str || ':' || NEW.constitutional_hash;
    
    -- Calculate SHA-256 hash
    calculated_hash := encode(digest(chain_input, 'sha256'), 'hex');
    
    -- Set the hash values
    NEW.prev_hash := previous_hash;
    NEW.current_hash := calculated_hash;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically calculate hash chain
DROP TRIGGER IF EXISTS audit_logs_hash_chain_trigger ON audit_logs;
CREATE TRIGGER audit_logs_hash_chain_trigger
    BEFORE INSERT ON audit_logs
    FOR EACH ROW
    EXECUTE FUNCTION calculate_audit_hash_chain();

-- Create function to verify hash chain integrity
CREATE OR REPLACE FUNCTION verify_audit_hash_chain(
    p_tenant_id UUID DEFAULT NULL,
    p_limit INTEGER DEFAULT 1000
)
RETURNS TABLE(
    integrity_verified BOOLEAN,
    total_records INTEGER,
    violations JSONB
) AS $$
DECLARE
    record_count INTEGER := 0;
    violation_count INTEGER := 0;
    violations_array JSONB := '[]'::JSONB;
    audit_record RECORD;
    expected_hash TEXT;
    prev_hash_check TEXT := NULL;
BEGIN
    -- Iterate through audit records in chronological order
    FOR audit_record IN
        SELECT id, event_data, prev_hash, current_hash, timestamp
        FROM audit_logs
        WHERE tenant_id = p_tenant_id OR (p_tenant_id IS NULL AND tenant_id IS NULL)
        ORDER BY timestamp ASC, id ASC
        LIMIT p_limit
    LOOP
        record_count := record_count + 1;
        
        -- Calculate expected hash
        expected_hash := encode(
            digest(
                COALESCE(prev_hash_check, 'genesis') || ':' || 
                audit_record.event_data::text || ':' || 
                'cdd01ef066bc6cf2',
                'sha256'
            ),
            'hex'
        );
        
        -- Check hash integrity
        IF expected_hash != audit_record.current_hash THEN
            violation_count := violation_count + 1;
            violations_array := violations_array || jsonb_build_object(
                'record_id', audit_record.id,
                'violation_type', 'hash_mismatch',
                'expected_hash', expected_hash,
                'actual_hash', audit_record.current_hash,
                'timestamp', audit_record.timestamp
            );
        END IF;
        
        -- Check previous hash linkage
        IF audit_record.prev_hash != prev_hash_check THEN
            violation_count := violation_count + 1;
            violations_array := violations_array || jsonb_build_object(
                'record_id', audit_record.id,
                'violation_type', 'prev_hash_mismatch',
                'expected_prev_hash', prev_hash_check,
                'actual_prev_hash', audit_record.prev_hash,
                'timestamp', audit_record.timestamp
            );
        END IF;
        
        prev_hash_check := audit_record.current_hash;
    END LOOP;
    
    RETURN QUERY SELECT 
        violation_count = 0,
        record_count,
        violations_array;
END;
$$ LANGUAGE plpgsql;

-- Create function to get audit statistics
CREATE OR REPLACE FUNCTION get_audit_statistics(
    p_tenant_id UUID DEFAULT NULL,
    p_time_window INTERVAL DEFAULT '24 hours'
)
RETURNS TABLE(
    total_events INTEGER,
    events_by_type JSONB,
    events_by_service JSONB,
    constitutional_compliance_rate NUMERIC,
    avg_events_per_hour NUMERIC
) AS $$
DECLARE
    start_time TIMESTAMPTZ := NOW() - p_time_window;
BEGIN
    RETURN QUERY
    WITH stats AS (
        SELECT 
            COUNT(*) as total_count,
            jsonb_object_agg(event_type, type_count) as type_stats,
            jsonb_object_agg(service_name, service_count) as service_stats,
            COUNT(*) FILTER (WHERE constitutional_hash = 'cdd01ef066bc6cf2') as compliant_count
        FROM (
            SELECT 
                event_type,
                service_name,
                constitutional_hash,
                COUNT(*) OVER (PARTITION BY event_type) as type_count,
                COUNT(*) OVER (PARTITION BY service_name) as service_count
            FROM audit_logs
            WHERE timestamp >= start_time
            AND (tenant_id = p_tenant_id OR (p_tenant_id IS NULL AND tenant_id IS NULL))
        ) sub
    )
    SELECT 
        total_count::INTEGER,
        type_stats,
        service_stats,
        CASE 
            WHEN total_count > 0 THEN (compliant_count::NUMERIC / total_count * 100)
            ELSE 100.0
        END,
        (total_count::NUMERIC / EXTRACT(EPOCH FROM p_time_window) * 3600)
    FROM stats;
END;
$$ LANGUAGE plpgsql;

-- Grant appropriate permissions
GRANT SELECT, INSERT ON audit_logs TO acgs_user;
GRANT USAGE ON SEQUENCE audit_logs_id_seq TO acgs_user;
GRANT EXECUTE ON FUNCTION calculate_audit_hash_chain() TO acgs_user;
GRANT EXECUTE ON FUNCTION verify_audit_hash_chain(UUID, INTEGER) TO acgs_user;
GRANT EXECUTE ON FUNCTION get_audit_statistics(UUID, INTERVAL) TO acgs_user;

-- Create initial comment for documentation
COMMENT ON TABLE audit_logs IS 'ACGS-2 persistent audit logs with hash chaining and multi-tenant RLS. Constitutional Hash: cdd01ef066bc6cf2';
COMMENT ON COLUMN audit_logs.current_hash IS 'SHA-256 hash of prev_hash + event_data + constitutional_hash for tamper detection';
COMMENT ON COLUMN audit_logs.prev_hash IS 'Previous hash in the chain for integrity verification';
COMMENT ON COLUMN audit_logs.constitutional_hash IS 'ACGS constitutional compliance hash (cdd01ef066bc6cf2)';
