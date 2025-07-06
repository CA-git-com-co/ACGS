-- ACGS Code Analysis Engine - Performance Indexes
-- Migration: 002_indexes.sql
-- Description: Creates optimized indexes for high-performance queries and constitutional compliance
-- Constitutional Hash: cdd01ef066bc6cf2

-- Set search path
SET search_path TO code_analysis, public;

-- ============================================================================
-- PRIMARY INDEXES FOR CORE QUERIES
-- ============================================================================

-- code_symbols table indexes
-- Primary lookup by file path (most common query pattern)
CREATE INDEX CONCURRENTLY idx_code_symbols_file_path
    ON code_symbols(file_path);

-- Symbol name lookup for exact matches
CREATE INDEX CONCURRENTLY idx_code_symbols_name
    ON code_symbols(symbol_name);

-- Symbol type filtering (functions, classes, etc.)
CREATE INDEX CONCURRENTLY idx_code_symbols_type
    ON code_symbols(symbol_type);

-- Language-based filtering
CREATE INDEX CONCURRENTLY idx_code_symbols_language
    ON code_symbols(language);

-- Composite index for file + type queries (common pattern)
CREATE INDEX CONCURRENTLY idx_code_symbols_file_type
    ON code_symbols(file_path, symbol_type);

-- Composite index for name + type queries
CREATE INDEX CONCURRENTLY idx_code_symbols_name_type
    ON code_symbols(symbol_name, symbol_type);

-- Public symbols index for API exposure
CREATE INDEX CONCURRENTLY idx_code_symbols_public
    ON code_symbols(is_public) WHERE is_public = true;

-- Recently updated symbols for incremental processing
CREATE INDEX CONCURRENTLY idx_code_symbols_updated_at
    ON code_symbols(updated_at DESC);

-- Constitutional compliance index
CREATE INDEX CONCURRENTLY idx_code_symbols_constitutional
    ON code_symbols(constitutional_hash);

-- ============================================================================
-- DEPENDENCY RELATIONSHIP INDEXES
-- ============================================================================

-- code_dependencies table indexes
-- Source symbol lookup (most common for dependency traversal)
CREATE INDEX CONCURRENTLY idx_code_dependencies_source
    ON code_dependencies(source_symbol_id);

-- Target symbol lookup (reverse dependency queries)
CREATE INDEX CONCURRENTLY idx_code_dependencies_target
    ON code_dependencies(target_symbol_id);

-- Dependency type filtering
CREATE INDEX CONCURRENTLY idx_code_dependencies_type
    ON code_dependencies(dependency_type);

-- External dependencies lookup
CREATE INDEX CONCURRENTLY idx_code_dependencies_external
    ON code_dependencies(is_external, target_name, target_module)
    WHERE is_external = true;

-- Composite index for source + type queries (common pattern)
CREATE INDEX CONCURRENTLY idx_code_dependencies_source_type
    ON code_dependencies(source_symbol_id, dependency_type);

-- Composite index for target + type queries
CREATE INDEX CONCURRENTLY idx_code_dependencies_target_type
    ON code_dependencies(target_symbol_id, dependency_type);

-- High confidence dependencies for reliable analysis
CREATE INDEX CONCURRENTLY idx_code_dependencies_confidence
    ON code_dependencies(confidence_score DESC)
    WHERE confidence_score >= 0.8;

-- Constitutional compliance index
CREATE INDEX CONCURRENTLY idx_code_dependencies_constitutional
    ON code_dependencies(constitutional_hash);

-- ============================================================================
-- VECTOR SEARCH INDEXES (PGVECTOR)
-- ============================================================================

-- code_embeddings table indexes
-- Vector similarity search index (primary semantic search)
CREATE INDEX CONCURRENTLY idx_code_embeddings_vector
    ON code_embeddings USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Alternative vector index for different distance metrics
CREATE INDEX CONCURRENTLY idx_code_embeddings_vector_l2
    ON code_embeddings USING ivfflat (embedding vector_l2_ops)
    WITH (lists = 100);

-- Symbol lookup for embedding retrieval
CREATE INDEX CONCURRENTLY idx_code_embeddings_symbol
    ON code_embeddings(symbol_id);

-- Model and version filtering
CREATE INDEX CONCURRENTLY idx_code_embeddings_model
    ON code_embeddings(embedding_model, embedding_version);

-- Chunk type filtering for specific embedding types
CREATE INDEX CONCURRENTLY idx_code_embeddings_chunk_type
    ON code_embeddings(chunk_type);

-- Composite index for symbol + chunk type
CREATE INDEX CONCURRENTLY idx_code_embeddings_symbol_chunk
    ON code_embeddings(symbol_id, chunk_type);

-- Constitutional compliance index
CREATE INDEX CONCURRENTLY idx_code_embeddings_constitutional
    ON code_embeddings(constitutional_hash);

-- ============================================================================
-- CONTEXT INTEGRATION INDEXES
-- ============================================================================

-- code_context_links table indexes
-- Code symbol lookup (primary integration query)
CREATE INDEX CONCURRENTLY idx_code_context_links_symbol
    ON code_context_links(code_symbol_id);

-- Context ID lookup for reverse queries
CREATE INDEX CONCURRENTLY idx_code_context_links_context
    ON code_context_links(context_id);

-- Context type filtering
CREATE INDEX CONCURRENTLY idx_code_context_links_context_type
    ON code_context_links(context_type);

-- Relationship type filtering
CREATE INDEX CONCURRENTLY idx_code_context_links_relationship
    ON code_context_links(relationship_type);

-- Composite index for symbol + context type
CREATE INDEX CONCURRENTLY idx_code_context_links_symbol_context_type
    ON code_context_links(code_symbol_id, context_type);

-- High confidence links for reliable integration
CREATE INDEX CONCURRENTLY idx_code_context_links_confidence
    ON code_context_links(confidence_score DESC)
    WHERE confidence_score >= 0.8;

-- Recently updated links for synchronization
CREATE INDEX CONCURRENTLY idx_code_context_links_updated_at
    ON code_context_links(updated_at DESC);

-- Constitutional compliance index
CREATE INDEX CONCURRENTLY idx_code_context_links_constitutional
    ON code_context_links(constitutional_hash);

-- ============================================================================
-- FILE METADATA INDEXES
-- ============================================================================

-- file_metadata table indexes
-- File path lookup (primary file query)
CREATE INDEX CONCURRENTLY idx_file_metadata_path
    ON file_metadata(file_path);

-- File hash for change detection
CREATE INDEX CONCURRENTLY idx_file_metadata_hash
    ON file_metadata(file_hash);

-- Language filtering
CREATE INDEX CONCURRENTLY idx_file_metadata_language
    ON file_metadata(language);

-- Last modified for incremental processing
CREATE INDEX CONCURRENTLY idx_file_metadata_last_modified
    ON file_metadata(last_modified DESC);

-- Last analyzed for processing queue
CREATE INDEX CONCURRENTLY idx_file_metadata_last_analyzed
    ON file_metadata(last_analyzed DESC);

-- Test files filtering
CREATE INDEX CONCURRENTLY idx_file_metadata_test_files
    ON file_metadata(is_test_file) WHERE is_test_file = true;

-- Configuration files filtering
CREATE INDEX CONCURRENTLY idx_file_metadata_config_files
    ON file_metadata(is_configuration) WHERE is_configuration = true;

-- Constitutional compliance index
CREATE INDEX CONCURRENTLY idx_file_metadata_constitutional
    ON file_metadata(constitutional_hash);

-- ============================================================================
-- ANALYSIS JOBS INDEXES
-- ============================================================================

-- analysis_jobs table indexes
-- Job status for monitoring
CREATE INDEX CONCURRENTLY idx_analysis_jobs_status
    ON analysis_jobs(status);

-- Job type filtering
CREATE INDEX CONCURRENTLY idx_analysis_jobs_type
    ON analysis_jobs(job_type);

-- File path for file-specific jobs
CREATE INDEX CONCURRENTLY idx_analysis_jobs_file_path
    ON analysis_jobs(file_path) WHERE file_path IS NOT NULL;

-- Recent jobs for monitoring dashboard
CREATE INDEX CONCURRENTLY idx_analysis_jobs_created_at
    ON analysis_jobs(created_at DESC);

-- Running jobs for active monitoring
CREATE INDEX CONCURRENTLY idx_analysis_jobs_running
    ON analysis_jobs(started_at DESC) WHERE status = 'running';

-- Failed jobs for error analysis
CREATE INDEX CONCURRENTLY idx_analysis_jobs_failed
    ON analysis_jobs(completed_at DESC) WHERE status = 'failed';

-- Performance analysis index
CREATE INDEX CONCURRENTLY idx_analysis_jobs_performance
    ON analysis_jobs(job_type, processing_time_ms DESC)
    WHERE processing_time_ms IS NOT NULL;

-- Constitutional compliance index
CREATE INDEX CONCURRENTLY idx_analysis_jobs_constitutional
    ON analysis_jobs(constitutional_hash);

-- ============================================================================
-- SEARCH ANALYTICS INDEXES
-- ============================================================================

-- search_analytics table indexes
-- Query hash for deduplication and caching
CREATE INDEX CONCURRENTLY idx_search_analytics_query_hash
    ON search_analytics(query_hash);

-- Query type for analytics
CREATE INDEX CONCURRENTLY idx_search_analytics_type
    ON search_analytics(query_type);

-- User ID for user-specific analytics
CREATE INDEX CONCURRENTLY idx_search_analytics_user
    ON search_analytics(user_id) WHERE user_id IS NOT NULL;

-- Recent queries for real-time analytics
CREATE INDEX CONCURRENTLY idx_search_analytics_created_at
    ON search_analytics(created_at DESC);

-- Performance analysis index
CREATE INDEX CONCURRENTLY idx_search_analytics_performance
    ON search_analytics(query_type, response_time_ms DESC);

-- Cache hit analysis
CREATE INDEX CONCURRENTLY idx_search_analytics_cache_hit
    ON search_analytics(cache_hit, created_at DESC);

-- Slow queries for optimization
CREATE INDEX CONCURRENTLY idx_search_analytics_slow_queries
    ON search_analytics(response_time_ms DESC)
    WHERE response_time_ms > 100; -- Queries slower than 100ms

-- Constitutional compliance index
CREATE INDEX CONCURRENTLY idx_search_analytics_constitutional
    ON search_analytics(constitutional_hash);

-- ============================================================================
-- COMPOSITE INDEXES FOR COMPLEX QUERIES
-- ============================================================================

-- Symbol search with file context
CREATE INDEX CONCURRENTLY idx_symbols_search_context
    ON code_symbols(symbol_name, file_path, symbol_type, is_public);

-- Dependency graph traversal optimization
CREATE INDEX CONCURRENTLY idx_dependency_traversal
    ON code_dependencies(source_symbol_id, target_symbol_id, dependency_type, confidence_score);

-- Context integration with confidence
CREATE INDEX CONCURRENTLY idx_context_integration
    ON code_context_links(code_symbol_id, context_type, relationship_type, confidence_score);

-- File analysis status tracking
CREATE INDEX CONCURRENTLY idx_file_analysis_status
    ON file_metadata(last_modified, last_analyzed, analysis_version);

-- Performance monitoring composite
CREATE INDEX CONCURRENTLY idx_performance_monitoring
    ON search_analytics(created_at, query_type, response_time_ms, cache_hit);

-- ============================================================================
-- PARTIAL INDEXES FOR OPTIMIZATION
-- ============================================================================

-- Active symbols only (non-deprecated)
CREATE INDEX CONCURRENTLY idx_active_symbols
    ON code_symbols(symbol_name, symbol_type)
    WHERE NOT is_deprecated;

-- Recent file changes for incremental processing
CREATE INDEX CONCURRENTLY idx_recent_file_changes
    ON file_metadata(file_path, last_modified)
    WHERE last_modified > NOW() - INTERVAL '24 hours';

-- High-value embeddings for quality search
CREATE INDEX CONCURRENTLY idx_quality_embeddings
    ON code_embeddings(symbol_id, embedding)
    WHERE chunk_type IN ('function_body', 'class_definition');

-- Critical dependencies for impact analysis
CREATE INDEX CONCURRENTLY idx_critical_dependencies
    ON code_dependencies(source_symbol_id, target_symbol_id)
    WHERE dependency_type IN ('import', 'inheritance') AND confidence_score >= 0.9;

-- ============================================================================
-- STATISTICS AND MAINTENANCE
-- ============================================================================

-- Update table statistics for query optimization
ANALYZE code_symbols;
ANALYZE code_dependencies;
ANALYZE code_embeddings;
ANALYZE code_context_links;
ANALYZE file_metadata;
ANALYZE analysis_jobs;
ANALYZE search_analytics;

-- Create maintenance function for index health monitoring
CREATE OR REPLACE FUNCTION monitor_index_health()
RETURNS TABLE(
    schema_name text,
    table_name text,
    index_name text,
    index_size text,
    index_scans bigint,
    tuples_read bigint,
    tuples_fetched bigint
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        schemaname::text,
        tablename::text,
        indexname::text,
        pg_size_pretty(pg_relation_size(indexrelid))::text as index_size,
        idx_scan,
        idx_tup_read,
        idx_tup_fetch
    FROM pg_stat_user_indexes
    WHERE schemaname = 'code_analysis'
    ORDER BY idx_scan DESC;
END;
$$ LANGUAGE plpgsql;

-- Grant execute permission on monitoring function
GRANT EXECUTE ON FUNCTION monitor_index_health() TO acgs_user;

-- Add index comments for documentation
COMMENT ON INDEX idx_code_symbols_file_path IS 'Primary index for file-based symbol lookups';
COMMENT ON INDEX idx_code_embeddings_vector IS 'Vector similarity search index using IVFFlat algorithm';
COMMENT ON INDEX idx_code_dependencies_source IS 'Primary index for dependency traversal queries';
COMMENT ON INDEX idx_code_context_links_symbol IS 'Primary index for Context Service integration';

-- Performance monitoring view
CREATE VIEW index_performance_summary AS
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan as scans,
    idx_tup_read as tuples_read,
    idx_tup_fetch as tuples_fetched,
    CASE
        WHEN idx_scan = 0 THEN 'UNUSED'
        WHEN idx_scan < 100 THEN 'LOW_USAGE'
        WHEN idx_scan < 1000 THEN 'MODERATE_USAGE'
        ELSE 'HIGH_USAGE'
    END as usage_category
FROM pg_stat_user_indexes
WHERE schemaname = 'code_analysis'
ORDER BY idx_scan DESC;

-- Grant access to performance view
GRANT SELECT ON index_performance_summary TO acgs_user;
