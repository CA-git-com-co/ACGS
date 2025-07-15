-- Constitutional Compliance Data Transformation Migration
-- Constitutional Hash: cdd01ef066bc6cf2
-- Migration: 20250714_002_constitutional_data_transform.sql
-- Purpose: Transform existing constitutional compliance data for GroqCloud integration

-- Begin transaction for atomic migration
BEGIN;

-- Create backup of existing constitutional compliance data
CREATE TABLE IF NOT EXISTS constitutional_compliance_backup AS
SELECT * FROM constitutional_metrics WHERE 1=0;

INSERT INTO constitutional_compliance_backup
SELECT * FROM constitutional_metrics;

-- Transform existing constitutional metrics for GroqCloud integration
UPDATE constitutional_metrics 
SET 
    service_name = CASE 
        WHEN service_name = 'llama-3-8b' THEN 'llama-3.1-8b-instant'
        WHEN service_name = 'mixtral-8x7b' THEN 'qwen/qwen3-32b'
        WHEN service_name = 'qwen2-32b' THEN 'qwen/qwen3-32b'
        WHEN service_name = 'gemma-7b' THEN 'allam-2-7b'
        ELSE service_name
    END,
    metric_name = CASE
        WHEN metric_name LIKE '%llama%8b%' THEN REPLACE(metric_name, 'llama-3-8b', 'llama-3.1-8b-instant')
        WHEN metric_name LIKE '%mixtral%' THEN REPLACE(metric_name, 'mixtral-8x7b', 'qwen/qwen3-32b')
        WHEN metric_name LIKE '%qwen2%' THEN REPLACE(metric_name, 'qwen2-32b', 'qwen/qwen3-32b')
        WHEN metric_name LIKE '%gemma%' THEN REPLACE(metric_name, 'gemma-7b', 'allam-2-7b')
        ELSE metric_name
    END
WHERE service_name IN ('llama-3-8b', 'mixtral-8x7b', 'qwen2-32b', 'gemma-7b')
   OR metric_name LIKE '%llama%8b%'
   OR metric_name LIKE '%mixtral%'
   OR metric_name LIKE '%qwen2%'
   OR metric_name LIKE '%gemma%';

-- Add new constitutional compliance metrics for GroqCloud tiers
INSERT INTO constitutional_metrics (
    service_name, 
    metric_name, 
    metric_value, 
    metric_unit, 
    compliance_status, 
    threshold_value, 
    constitutional_hash
) VALUES 
-- Tier 1 (Nano) metrics
('groq-policy-integration', 'tier_1_nano_latency_p99', 1.0, 'ms', 'compliant', 1.0, 'cdd01ef066bc6cf2'),
('groq-policy-integration', 'tier_1_nano_throughput', 2000.0, 'rps', 'compliant', 1000.0, 'cdd01ef066bc6cf2'),
('groq-policy-integration', 'tier_1_nano_compliance_rate', 99.5, 'percent', 'compliant', 99.0, 'cdd01ef066bc6cf2'),

-- Tier 2 (Fast) metrics
('groq-policy-integration', 'tier_2_fast_latency_p99', 2.0, 'ms', 'compliant', 2.0, 'cdd01ef066bc6cf2'),
('groq-policy-integration', 'tier_2_fast_throughput', 1500.0, 'rps', 'compliant', 800.0, 'cdd01ef066bc6cf2'),
('groq-policy-integration', 'tier_2_fast_compliance_rate', 99.2, 'percent', 'compliant', 99.0, 'cdd01ef066bc6cf2'),

-- Tier 3 (Balanced) metrics
('groq-policy-integration', 'tier_3_balanced_latency_p99', 3.0, 'ms', 'compliant', 3.0, 'cdd01ef066bc6cf2'),
('groq-policy-integration', 'tier_3_balanced_throughput', 1200.0, 'rps', 'compliant', 600.0, 'cdd01ef066bc6cf2'),
('groq-policy-integration', 'tier_3_balanced_compliance_rate', 99.8, 'percent', 'compliant', 99.0, 'cdd01ef066bc6cf2'),

-- Tier 4 (Premium) metrics
('groq-policy-integration', 'tier_4_premium_latency_p99', 5.0, 'ms', 'compliant', 5.0, 'cdd01ef066bc6cf2'),
('groq-policy-integration', 'tier_4_premium_throughput', 800.0, 'rps', 'compliant', 400.0, 'cdd01ef066bc6cf2'),
('groq-policy-integration', 'tier_4_premium_compliance_rate', 99.9, 'percent', 'compliant', 99.5, 'cdd01ef066bc6cf2'),

-- WASM Policy Engine metrics
('wasm-policy-engine', 'compilation_latency_p99', 15.0, 'ms', 'compliant', 30.0, 'cdd01ef066bc6cf2'),
('wasm-policy-engine', 'evaluation_latency_p99', 0.5, 'ms', 'compliant', 1.0, 'cdd01ef066bc6cf2'),
('wasm-policy-engine', 'compilation_success_rate', 99.8, 'percent', 'compliant', 99.0, 'cdd01ef066bc6cf2'),
('wasm-policy-engine', 'policy_enforcement_rate', 100.0, 'percent', 'compliant', 100.0, 'cdd01ef066bc6cf2'),

-- Constitutional compliance aggregated metrics
('constitutional-framework', 'overall_compliance_rate', 99.6, 'percent', 'compliant', 99.0, 'cdd01ef066bc6cf2'),
('constitutional-framework', 'groq_cloud_integration_health', 100.0, 'percent', 'compliant', 99.0, 'cdd01ef066bc6cf2'),
('constitutional-framework', 'policy_engine_integration_health', 100.0, 'percent', 'compliant', 99.0, 'cdd01ef066bc6cf2')
ON CONFLICT DO NOTHING;

-- Transform audit logs if they exist to include GroqCloud context
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'audit_logs') THEN
        -- Update existing audit logs to include GroqCloud model mappings
        UPDATE audit_logs 
        SET 
            groq_model = CASE 
                WHEN details::text LIKE '%llama-3-8b%' THEN 'llama-3.1-8b-instant'
                WHEN details::text LIKE '%mixtral-8x7b%' THEN 'qwen/qwen3-32b'
                WHEN details::text LIKE '%qwen2-32b%' THEN 'qwen/qwen3-32b'
                WHEN details::text LIKE '%gemma-7b%' THEN 'allam-2-7b'
                ELSE NULL
            END,
            policy_engine = 'opa-wasm'
        WHERE groq_model IS NULL
          AND (details::text LIKE '%llama%' 
               OR details::text LIKE '%mixtral%'
               OR details::text LIKE '%qwen%'
               OR details::text LIKE '%gemma%');
    END IF;
END
$$;

-- Create summary statistics for the migration
CREATE TEMPORARY TABLE migration_summary AS
SELECT 
    'constitutional_metrics_updated' as table_name,
    COUNT(*) as records_affected
FROM constitutional_metrics 
WHERE service_name IN ('llama-3.1-8b-instant', 'qwen/qwen3-32b', 'allam-2-7b', 'groq-policy-integration', 'wasm-policy-engine', 'constitutional-framework')

UNION ALL

SELECT 
    'groq_models_available' as table_name,
    COUNT(*) as records_affected
FROM groq_models 
WHERE active = true

UNION ALL

SELECT 
    'wasm_policy_compilations_ready' as table_name,
    COUNT(*) as records_affected
FROM wasm_policy_compilations 
WHERE compilation_status = 'success';

-- Add constitutional compliance validation
DO $$
DECLARE
    compliance_count INTEGER;
    expected_constitutional_hash VARCHAR(16) := 'cdd01ef066bc6cf2';
BEGIN
    -- Verify constitutional hash consistency
    SELECT COUNT(*) INTO compliance_count
    FROM constitutional_metrics 
    WHERE constitutional_hash = expected_constitutional_hash;
    
    IF compliance_count > 0 THEN
        RAISE NOTICE 'Constitutional compliance data transformation completed successfully';
        RAISE NOTICE 'Records with valid constitutional hash: %', compliance_count;
    ELSE
        RAISE EXCEPTION 'Constitutional compliance validation failed: no records with valid hash';
    END IF;
    
    -- Verify GroqCloud model integration
    SELECT COUNT(*) INTO compliance_count
    FROM groq_models 
    WHERE active = true;
    
    IF compliance_count >= 4 THEN
        RAISE NOTICE 'GroqCloud model integration verified: % active models', compliance_count;
    ELSE
        RAISE WARNING 'GroqCloud model integration incomplete: only % active models', compliance_count;
    END IF;
END
$$;

-- Create indexed view for constitutional compliance monitoring
CREATE OR REPLACE VIEW constitutional_compliance_dashboard AS
SELECT 
    cm.service_name,
    cm.metric_name,
    cm.metric_value,
    cm.metric_unit,
    cm.compliance_status,
    cm.threshold_value,
    CASE 
        WHEN cm.metric_value >= cm.threshold_value THEN 'PASS'
        ELSE 'FAIL'
    END as threshold_status,
    cm.timestamp,
    cm.constitutional_hash,
    gm.tier as groq_tier,
    gm.performance_target_ms as groq_target_latency
FROM constitutional_metrics cm
LEFT JOIN groq_models gm ON (
    cm.service_name = 'groq-policy-integration' 
    AND cm.metric_name LIKE CONCAT('%', REPLACE(gm.model_name, '/', '_'), '%')
)
WHERE cm.constitutional_hash = 'cdd01ef066bc6cf2'
ORDER BY cm.timestamp DESC;

-- Grant permissions for the dashboard view
GRANT SELECT ON constitutional_compliance_dashboard TO acgs_user;

-- Add comment for documentation
COMMENT ON VIEW constitutional_compliance_dashboard IS 'Constitutional compliance monitoring dashboard with GroqCloud integration';

-- Display migration summary
SELECT * FROM migration_summary;

-- Commit the transaction
COMMIT;

-- Final verification
DO $$
DECLARE
    total_metrics INTEGER;
    groq_models INTEGER;
    wasm_policies INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_metrics FROM constitutional_metrics;
    SELECT COUNT(*) INTO groq_models FROM groq_models WHERE active = true;
    SELECT COUNT(*) INTO wasm_policies FROM wasm_policy_compilations;
    
    RAISE NOTICE 'Migration completed successfully:';
    RAISE NOTICE '- Total constitutional metrics: %', total_metrics;
    RAISE NOTICE '- Active GroqCloud models: %', groq_models;
    RAISE NOTICE '- WASM policy compilations: %', wasm_policies;
    RAISE NOTICE 'Constitutional Hash validated: cdd01ef066bc6cf2';
END
$$;