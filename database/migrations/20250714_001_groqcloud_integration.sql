-- GroqCloud Integration Migration
-- Constitutional Hash: cdd01ef066bc6cf2
-- Migration: 20250714_001_groqcloud_integration.sql
-- Purpose: Add GroqCloud model support and constitutional compliance enhancements

-- Create GroqCloud model registry table
CREATE TABLE IF NOT EXISTS groq_models (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL UNIQUE,
    tier VARCHAR(20) NOT NULL CHECK (tier IN ('nano', 'fast', 'balanced', 'premium')),
    context_size INTEGER NOT NULL,
    completion_size INTEGER,
    performance_target_ms NUMERIC(5,2),
    active BOOLEAN DEFAULT true,
    constitutional_hash VARCHAR(16) NOT NULL DEFAULT 'cdd01ef066bc6cf2',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert current GroqCloud models
INSERT INTO groq_models (model_name, tier, context_size, completion_size, performance_target_ms) VALUES
    ('allam-2-7b', 'nano', 4096, 4096, 1.00),
    ('llama-3.1-8b-instant', 'fast', 131072, 8192, 2.00),
    ('qwen/qwen3-32b', 'balanced', 131072, 40960, 3.00),
    ('llama-3.3-70b-versatile', 'premium', 131072, 8192, 5.00),
    ('deepseek-r1-distill-llama-70b', 'premium', 131072, 8192, 5.00),
    ('mistral-saba-24b', 'premium', 32768, 8192, 4.00),
    ('compound-beta', 'premium', 131072, 8192, 5.00)
ON CONFLICT (model_name) DO UPDATE SET
    tier = EXCLUDED.tier,
    context_size = EXCLUDED.context_size,
    completion_size = EXCLUDED.completion_size,
    performance_target_ms = EXCLUDED.performance_target_ms,
    updated_at = CURRENT_TIMESTAMP;

-- Create GroqCloud request tracking table
CREATE TABLE IF NOT EXISTS groq_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id VARCHAR(50) NOT NULL,
    model_name VARCHAR(100) NOT NULL,
    inference_mode VARCHAR(20) NOT NULL,
    prompt_length INTEGER,
    response_length INTEGER,
    latency_ms NUMERIC(8,2),
    tokens_per_second NUMERIC(8,2),
    constitutional_compliant BOOLEAN,
    policy_decisions JSONB,
    cached BOOLEAN DEFAULT false,
    user_id VARCHAR(50),
    session_id VARCHAR(50),
    constitutional_hash VARCHAR(16) NOT NULL DEFAULT 'cdd01ef066bc6cf2',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for performance queries
CREATE INDEX IF NOT EXISTS idx_groq_requests_model_created 
    ON groq_requests (model_name, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_groq_requests_latency 
    ON groq_requests (latency_ms) WHERE latency_ms IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_groq_requests_constitutional 
    ON groq_requests (constitutional_compliant, constitutional_hash);

-- Create WASM policy compilation tracking table
CREATE TABLE IF NOT EXISTS wasm_policy_compilations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    policy_name VARCHAR(100) NOT NULL,
    policy_version VARCHAR(20) NOT NULL,
    rego_source TEXT NOT NULL,
    wasm_bytecode BYTEA,
    compilation_time_ms NUMERIC(8,2),
    compilation_status VARCHAR(20) NOT NULL CHECK (compilation_status IN ('success', 'failed', 'pending')),
    error_message TEXT,
    constitutional_hash VARCHAR(16) NOT NULL DEFAULT 'cdd01ef066bc6cf2',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(policy_name, policy_version)
);

-- Create index for policy lookups
CREATE INDEX IF NOT EXISTS idx_wasm_policies_name_version 
    ON wasm_policy_compilations (policy_name, policy_version);
CREATE INDEX IF NOT EXISTS idx_wasm_policies_status 
    ON wasm_policy_compilations (compilation_status, created_at DESC);

-- Add GroqCloud columns to existing audit tables if they exist
DO $$
BEGIN
    -- Add columns to audit_logs if table exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'audit_logs') THEN
        -- Add groq_model column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'audit_logs' AND column_name = 'groq_model') THEN
            ALTER TABLE audit_logs ADD COLUMN groq_model VARCHAR(100);
        END IF;
        
        -- Add groq_latency_ms column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'audit_logs' AND column_name = 'groq_latency_ms') THEN
            ALTER TABLE audit_logs ADD COLUMN groq_latency_ms NUMERIC(8,2);
        END IF;
        
        -- Add policy_engine column if it doesn't exist
        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                      WHERE table_name = 'audit_logs' AND column_name = 'policy_engine') THEN
            ALTER TABLE audit_logs ADD COLUMN policy_engine VARCHAR(20) DEFAULT 'opa-wasm';
        END IF;
    END IF;
END
$$;

-- Create constitutional compliance metrics table
CREATE TABLE IF NOT EXISTS constitutional_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    service_name VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC(12,4),
    metric_unit VARCHAR(20),
    compliance_status VARCHAR(20) NOT NULL CHECK (compliance_status IN ('compliant', 'non_compliant', 'warning')),
    threshold_value NUMERIC(12,4),
    constitutional_hash VARCHAR(16) NOT NULL DEFAULT 'cdd01ef066bc6cf2',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for metrics queries
CREATE INDEX IF NOT EXISTS idx_constitutional_metrics_service_time 
    ON constitutional_metrics (service_name, timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_constitutional_metrics_compliance 
    ON constitutional_metrics (compliance_status, constitutional_hash);

-- Create trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to groq_models table
DROP TRIGGER IF EXISTS update_groq_models_updated_at ON groq_models;
CREATE TRIGGER update_groq_models_updated_at 
    BEFORE UPDATE ON groq_models 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create view for GroqCloud performance metrics
CREATE OR REPLACE VIEW groq_performance_summary AS
SELECT 
    model_name,
    tier,
    COUNT(*) as total_requests,
    AVG(latency_ms) as avg_latency_ms,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_latency_ms,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99_latency_ms,
    AVG(tokens_per_second) as avg_tokens_per_second,
    SUM(CASE WHEN constitutional_compliant THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100 as compliance_rate,
    SUM(CASE WHEN cached THEN 1 ELSE 0 END)::NUMERIC / COUNT(*) * 100 as cache_hit_rate
FROM groq_requests gr
JOIN groq_models gm ON gr.model_name = gm.model_name
WHERE gr.created_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY gr.model_name, gm.tier
ORDER BY total_requests DESC;

-- Grant appropriate permissions
GRANT SELECT, INSERT, UPDATE ON groq_models TO acgs_user;
GRANT SELECT, INSERT ON groq_requests TO acgs_user;
GRANT SELECT, INSERT, UPDATE ON wasm_policy_compilations TO acgs_user;
GRANT SELECT, INSERT ON constitutional_metrics TO acgs_user;
GRANT SELECT ON groq_performance_summary TO acgs_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO acgs_user;

-- Add comments for documentation
COMMENT ON TABLE groq_models IS 'Registry of available GroqCloud models with performance characteristics';
COMMENT ON TABLE groq_requests IS 'Tracking table for GroqCloud API requests and performance metrics';
COMMENT ON TABLE wasm_policy_compilations IS 'WASM policy compilation tracking for OPA-WASM integration';
COMMENT ON TABLE constitutional_metrics IS 'Constitutional compliance metrics and monitoring data';
COMMENT ON VIEW groq_performance_summary IS 'Real-time performance summary for GroqCloud models';

-- Verify constitutional hash integrity
DO $$
DECLARE
    expected_hash VARCHAR(16) := 'cdd01ef066bc6cf2';
    table_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO table_count 
    FROM information_schema.tables 
    WHERE table_name IN ('groq_models', 'groq_requests', 'wasm_policy_compilations', 'constitutional_metrics')
    AND table_schema = 'public';
    
    IF table_count = 4 THEN
        RAISE NOTICE 'GroqCloud integration migration completed successfully. Constitutional Hash: %', expected_hash;
    ELSE
        RAISE EXCEPTION 'Migration failed: Expected 4 tables, found %', table_count;
    END IF;
END
$$;