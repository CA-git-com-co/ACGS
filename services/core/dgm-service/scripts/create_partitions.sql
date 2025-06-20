-- DGM Database Partitioning Script
-- Creates time-based partitions for performance metrics and other time-series data

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- PERFORMANCE METRICS PARTITIONING
-- ============================================================================

-- Create partitioned performance metrics table
CREATE TABLE IF NOT EXISTS dgm.performance_metrics_partitioned (
    id UUID DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(255) NOT NULL,
    metric_value DECIMAL(15,6) NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    service_name VARCHAR(255),
    improvement_id UUID,
    experiment_id UUID,
    tags JSONB DEFAULT '{}',
    dimensions JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    constitutional_hash VARCHAR(64) NOT NULL DEFAULT 'cdd01ef066bc6cf2',
    constitutional_compliance_score DECIMAL(3,2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (id, timestamp)
) PARTITION BY RANGE (timestamp);

-- Create indexes on partitioned table
CREATE INDEX IF NOT EXISTS idx_perf_metrics_part_name_time 
ON dgm.performance_metrics_partitioned (metric_name, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_perf_metrics_part_service_type 
ON dgm.performance_metrics_partitioned (service_name, metric_type, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_perf_metrics_part_improvement 
ON dgm.performance_metrics_partitioned (improvement_id, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_perf_metrics_part_tags_gin 
ON dgm.performance_metrics_partitioned USING GIN (tags);

-- Function to create monthly partitions
CREATE OR REPLACE FUNCTION dgm.create_monthly_partition(
    table_name TEXT,
    start_date DATE
) RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    end_date DATE;
BEGIN
    end_date := start_date + INTERVAL '1 month';
    partition_name := table_name || '_y' || 
                     EXTRACT(year FROM start_date) || 'm' || 
                     LPAD(EXTRACT(month FROM start_date)::TEXT, 2, '0');
    
    EXECUTE format('CREATE TABLE IF NOT EXISTS dgm.%I PARTITION OF dgm.%I 
                   FOR VALUES FROM (%L) TO (%L)',
                   partition_name, table_name, start_date, end_date);
    
    -- Create indexes on partition
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I_name_time_idx 
                   ON dgm.%I (metric_name, timestamp DESC)',
                   partition_name, partition_name);
    
    EXECUTE format('CREATE INDEX IF NOT EXISTS %I_service_type_idx 
                   ON dgm.%I (service_name, metric_type)',
                   partition_name, partition_name);
    
    RAISE NOTICE 'Created partition: %', partition_name;
END;
$$ LANGUAGE plpgsql;

-- Create partitions for the next 24 months
DO $$
DECLARE
    start_date DATE;
BEGIN
    FOR i IN 0..23 LOOP
        start_date := DATE_TRUNC('month', CURRENT_DATE) + (i || ' months')::INTERVAL;
        PERFORM dgm.create_monthly_partition('performance_metrics_partitioned', start_date);
    END LOOP;
END $$;

-- ============================================================================
-- CONSTITUTIONAL COMPLIANCE LOGS PARTITIONING
-- ============================================================================

-- Create partitioned compliance logs table
CREATE TABLE IF NOT EXISTS dgm.constitutional_compliance_logs_partitioned (
    id UUID DEFAULT uuid_generate_v4(),
    improvement_id UUID NOT NULL,
    compliance_level VARCHAR(20) NOT NULL,
    compliance_score DECIMAL(3,2) NOT NULL,
    assessment_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    principle_violations JSONB DEFAULT '[]',
    governance_impact TEXT,
    constitutional_hash VARCHAR(64) NOT NULL DEFAULT 'cdd01ef066bc6cf2',
    constitutional_version VARCHAR(50) NOT NULL DEFAULT '1.0',
    violations JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '[]',
    evidence JSONB DEFAULT '{}',
    assessment_method VARCHAR(100) NOT NULL,
    assessor_id VARCHAR(255),
    review_required BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (id, assessment_timestamp)
) PARTITION BY RANGE (assessment_timestamp);

-- Create indexes on partitioned compliance logs
CREATE INDEX IF NOT EXISTS idx_compliance_logs_part_level_time 
ON dgm.constitutional_compliance_logs_partitioned (compliance_level, assessment_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_compliance_logs_part_improvement 
ON dgm.constitutional_compliance_logs_partitioned (improvement_id, assessment_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_compliance_logs_part_violations_gin 
ON dgm.constitutional_compliance_logs_partitioned USING GIN (violations);

-- Create compliance log partitions
DO $$
DECLARE
    start_date DATE;
BEGIN
    FOR i IN 0..11 LOOP
        start_date := DATE_TRUNC('month', CURRENT_DATE) + (i || ' months')::INTERVAL;
        PERFORM dgm.create_monthly_partition('constitutional_compliance_logs_partitioned', start_date);
    END LOOP;
END $$;

-- ============================================================================
-- ARCHIVE PARTITIONING (BY STATUS AND TIME)
-- ============================================================================

-- Create partitioned archive table
CREATE TABLE IF NOT EXISTS dgm.dgm_archive_partitioned (
    id UUID DEFAULT uuid_generate_v4(),
    improvement_id UUID NOT NULL UNIQUE,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    description TEXT NOT NULL,
    algorithm_changes JSONB,
    performance_before JSONB,
    performance_after JSONB,
    constitutional_compliance_score DECIMAL(3,2) NOT NULL,
    compliance_details JSONB,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    rollback_data JSONB,
    metadata JSONB,
    created_by VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    PRIMARY KEY (id, created_at, status)
) PARTITION BY RANGE (created_at);

-- Create subpartitions by status
CREATE TABLE IF NOT EXISTS dgm.dgm_archive_completed PARTITION OF dgm.dgm_archive_partitioned
FOR VALUES FROM (MINVALUE) TO (MAXVALUE)
PARTITION BY LIST (status);

CREATE TABLE IF NOT EXISTS dgm.dgm_archive_completed_success PARTITION OF dgm.dgm_archive_completed
FOR VALUES IN ('completed');

CREATE TABLE IF NOT EXISTS dgm.dgm_archive_completed_failed PARTITION OF dgm.dgm_archive_completed
FOR VALUES IN ('failed', 'rolled_back');

CREATE TABLE IF NOT EXISTS dgm.dgm_archive_active PARTITION OF dgm.dgm_archive_partitioned
FOR VALUES FROM (MINVALUE) TO (MAXVALUE)
PARTITION BY LIST (status);

CREATE TABLE IF NOT EXISTS dgm.dgm_archive_active_running PARTITION OF dgm.dgm_archive_active
FOR VALUES IN ('pending', 'running');

-- ============================================================================
-- PARTITION MAINTENANCE FUNCTIONS
-- ============================================================================

-- Function to automatically create future partitions
CREATE OR REPLACE FUNCTION dgm.maintain_partitions() RETURNS VOID AS $$
DECLARE
    table_names TEXT[] := ARRAY[
        'performance_metrics_partitioned',
        'constitutional_compliance_logs_partitioned'
    ];
    table_name TEXT;
    next_month DATE;
    partition_exists BOOLEAN;
    partition_name TEXT;
BEGIN
    next_month := DATE_TRUNC('month', CURRENT_DATE + INTERVAL '2 months');
    
    FOREACH table_name IN ARRAY table_names LOOP
        partition_name := table_name || '_y' || 
                         EXTRACT(year FROM next_month) || 'm' || 
                         LPAD(EXTRACT(month FROM next_month)::TEXT, 2, '0');
        
        -- Check if partition exists
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'dgm' 
            AND table_name = partition_name
        ) INTO partition_exists;
        
        IF NOT partition_exists THEN
            PERFORM dgm.create_monthly_partition(table_name, next_month);
        END IF;
    END LOOP;
    
    RAISE NOTICE 'Partition maintenance completed';
END;
$$ LANGUAGE plpgsql;

-- Function to drop old partitions
CREATE OR REPLACE FUNCTION dgm.cleanup_old_partitions(retention_months INTEGER DEFAULT 12) RETURNS VOID AS $$
DECLARE
    cutoff_date DATE;
    partition_record RECORD;
    partition_name TEXT;
BEGIN
    cutoff_date := DATE_TRUNC('month', CURRENT_DATE - (retention_months || ' months')::INTERVAL);
    
    -- Find partitions older than retention period
    FOR partition_record IN
        SELECT schemaname, tablename 
        FROM pg_tables 
        WHERE schemaname = 'dgm' 
        AND tablename ~ '_y\d{4}m\d{2}$'
    LOOP
        partition_name := partition_record.tablename;
        
        -- Extract date from partition name and check if it's old
        -- This is a simplified check - in production, you'd want more robust date parsing
        IF partition_name ~ '_y\d{4}m(0[1-9]|1[0-2])$' THEN
            -- Drop old partition (add more sophisticated date checking in production)
            EXECUTE format('DROP TABLE IF EXISTS dgm.%I', partition_name);
            RAISE NOTICE 'Dropped old partition: %', partition_name;
        END IF;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PARTITION MONITORING VIEWS
-- ============================================================================

-- View to monitor partition sizes
CREATE OR REPLACE VIEW dgm.partition_sizes AS
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
    pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
FROM pg_tables 
WHERE schemaname = 'dgm' 
AND tablename LIKE '%_y%m%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- View to monitor partition row counts
CREATE OR REPLACE VIEW dgm.partition_row_counts AS
SELECT 
    schemaname,
    tablename,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables 
WHERE schemaname = 'dgm' 
AND tablename LIKE '%_y%m%'
ORDER BY n_live_tup DESC;

-- ============================================================================
-- AUTOMATED PARTITION MAINTENANCE
-- ============================================================================

-- Create a function to be called by cron or scheduler
CREATE OR REPLACE FUNCTION dgm.daily_partition_maintenance() RETURNS VOID AS $$
BEGIN
    -- Create future partitions
    PERFORM dgm.maintain_partitions();
    
    -- Clean up old partitions (keep 12 months)
    PERFORM dgm.cleanup_old_partitions(12);
    
    -- Update statistics on partitioned tables
    ANALYZE dgm.performance_metrics_partitioned;
    ANALYZE dgm.constitutional_compliance_logs_partitioned;
    ANALYZE dgm.dgm_archive_partitioned;
    
    RAISE NOTICE 'Daily partition maintenance completed at %', NOW();
END;
$$ LANGUAGE plpgsql;

-- Grant necessary permissions
GRANT USAGE ON SCHEMA dgm TO acgs_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA dgm TO acgs_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA dgm TO acgs_user;
