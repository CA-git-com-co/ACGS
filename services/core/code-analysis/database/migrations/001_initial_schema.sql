-- ACGS Code Analysis Engine - Initial Database Schema
-- Migration: 001_initial_schema.sql
-- Description: Creates core tables for code analysis, symbols, dependencies, and embeddings
-- Constitutional Hash: cdd01ef066bc6cf2

-- Enable required PostgreSQL extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "vector"; -- pgvector for embeddings

-- Create schema for code analysis engine
CREATE SCHEMA IF NOT EXISTS code_analysis;

-- Set search path
SET search_path TO code_analysis, public;

-- Table: code_symbols
-- Stores all code symbols (functions, classes, variables, imports) extracted from source files
CREATE TABLE code_symbols (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_path VARCHAR(512) NOT NULL,
    relative_path VARCHAR(512) NOT NULL, -- Path relative to project root
    symbol_name VARCHAR(256) NOT NULL,
    symbol_type VARCHAR(50) NOT NULL CHECK (symbol_type IN ('function', 'class', 'variable', 'import', 'method', 'property')),
    language VARCHAR(20) NOT NULL CHECK (language IN ('python', 'javascript', 'typescript', 'yaml', 'json', 'sql', 'markdown')),
    start_line INTEGER NOT NULL CHECK (start_line > 0),
    end_line INTEGER NOT NULL CHECK (end_line >= start_line),
    signature TEXT, -- Function/method signature
    docstring TEXT, -- Documentation string
    source_code TEXT, -- Actual source code of the symbol
    complexity_score INTEGER DEFAULT 0, -- Cyclomatic complexity
    is_public BOOLEAN DEFAULT true, -- Whether symbol is publicly accessible
    is_deprecated BOOLEAN DEFAULT false, -- Whether symbol is marked as deprecated
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    constitutional_hash VARCHAR(64) DEFAULT 'cdd01ef066bc6cf2' NOT NULL,

    -- Constraints
    CONSTRAINT unique_symbol_location UNIQUE (file_path, symbol_name, start_line),
    CONSTRAINT valid_line_numbers CHECK (end_line >= start_line)
);

-- Table: code_dependencies
-- Stores relationships between code symbols (imports, function calls, inheritance)
CREATE TABLE code_dependencies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_symbol_id UUID NOT NULL REFERENCES code_symbols(id) ON DELETE CASCADE,
    target_symbol_id UUID REFERENCES code_symbols(id) ON DELETE CASCADE, -- NULL for external dependencies
    dependency_type VARCHAR(50) NOT NULL CHECK (dependency_type IN ('import', 'call', 'inheritance', 'composition', 'reference')),
    target_name VARCHAR(256), -- For external dependencies not in our codebase
    target_module VARCHAR(256), -- Module/package name for external dependencies
    is_external BOOLEAN DEFAULT false, -- Whether dependency is external to our codebase
    confidence_score FLOAT DEFAULT 1.0 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    constitutional_hash VARCHAR(64) DEFAULT 'cdd01ef066bc6cf2' NOT NULL,

    -- Constraints
    CONSTRAINT valid_dependency CHECK (
        (target_symbol_id IS NOT NULL AND NOT is_external) OR
        (target_name IS NOT NULL AND is_external)
    )
);

-- Table: code_embeddings
-- Stores vector embeddings for semantic search using pgvector
CREATE TABLE code_embeddings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol_id UUID NOT NULL REFERENCES code_symbols(id) ON DELETE CASCADE,
    embedding vector(768), -- CodeBERT embedding dimension (768)
    embedding_model VARCHAR(100) NOT NULL DEFAULT 'microsoft/codebert-base',
    embedding_version VARCHAR(20) NOT NULL DEFAULT '1.0',
    chunk_text TEXT NOT NULL, -- The text that was embedded
    chunk_type VARCHAR(50) NOT NULL CHECK (chunk_type IN ('function_body', 'class_definition', 'docstring', 'signature')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    constitutional_hash VARCHAR(64) DEFAULT 'cdd01ef066bc6cf2' NOT NULL,

    -- Constraints
    CONSTRAINT unique_symbol_embedding UNIQUE (symbol_id, chunk_type, embedding_model)
);

-- Table: code_context_links
-- Links code symbols with the existing ACGS Context Service for bidirectional integration
CREATE TABLE code_context_links (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code_symbol_id UUID NOT NULL REFERENCES code_symbols(id) ON DELETE CASCADE,
    context_id UUID NOT NULL, -- References context in the Context Service (port 8012)
    context_type VARCHAR(50) NOT NULL CHECK (context_type IN ('DomainContext', 'PolicyContext', 'ConstitutionalContext', 'AgentContext')),
    relationship_type VARCHAR(50) NOT NULL CHECK (relationship_type IN ('implements', 'uses', 'related_to', 'validates', 'enforces')),
    confidence_score FLOAT DEFAULT 1.0 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
    metadata JSONB, -- Additional relationship metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    constitutional_hash VARCHAR(64) DEFAULT 'cdd01ef066bc6cf2' NOT NULL,

    -- Constraints
    CONSTRAINT unique_code_context_link UNIQUE (code_symbol_id, context_id, relationship_type)
);

-- Table: file_metadata
-- Stores metadata about analyzed files for tracking and optimization
CREATE TABLE file_metadata (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_path VARCHAR(512) NOT NULL UNIQUE,
    relative_path VARCHAR(512) NOT NULL,
    file_size BIGINT NOT NULL CHECK (file_size >= 0),
    file_hash VARCHAR(64) NOT NULL, -- SHA-256 hash of file content
    language VARCHAR(20) NOT NULL,
    last_modified TIMESTAMP WITH TIME ZONE NOT NULL,
    last_analyzed TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    analysis_version VARCHAR(20) DEFAULT '1.0',
    symbol_count INTEGER DEFAULT 0 CHECK (symbol_count >= 0),
    dependency_count INTEGER DEFAULT 0 CHECK (dependency_count >= 0),
    complexity_total INTEGER DEFAULT 0 CHECK (complexity_total >= 0),
    is_test_file BOOLEAN DEFAULT false,
    is_configuration BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    constitutional_hash VARCHAR(64) DEFAULT 'cdd01ef066bc6cf2' NOT NULL
);

-- Table: analysis_jobs
-- Tracks background analysis jobs for monitoring and debugging
CREATE TABLE analysis_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_type VARCHAR(50) NOT NULL CHECK (job_type IN ('full_scan', 'incremental_update', 'file_analysis', 'dependency_update')),
    status VARCHAR(20) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    file_path VARCHAR(512), -- NULL for full scan jobs
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    files_processed INTEGER DEFAULT 0,
    symbols_created INTEGER DEFAULT 0,
    symbols_updated INTEGER DEFAULT 0,
    dependencies_created INTEGER DEFAULT 0,
    embeddings_created INTEGER DEFAULT 0,
    processing_time_ms BIGINT, -- Processing time in milliseconds
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    constitutional_hash VARCHAR(64) DEFAULT 'cdd01ef066bc6cf2' NOT NULL,

    -- Constraints
    CONSTRAINT valid_job_timing CHECK (
        (started_at IS NULL AND completed_at IS NULL) OR
        (started_at IS NOT NULL AND (completed_at IS NULL OR completed_at >= started_at))
    )
);

-- Table: search_analytics
-- Tracks search queries for analytics and optimization
CREATE TABLE search_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    query_text TEXT NOT NULL,
    query_type VARCHAR(50) NOT NULL CHECK (query_type IN ('semantic', 'symbol', 'dependency', 'hybrid')),
    query_hash VARCHAR(64) NOT NULL, -- Hash of normalized query for deduplication
    user_id UUID, -- From Auth Service, nullable for anonymous queries
    results_count INTEGER DEFAULT 0 CHECK (results_count >= 0),
    response_time_ms INTEGER NOT NULL CHECK (response_time_ms >= 0),
    cache_hit BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    constitutional_hash VARCHAR(64) DEFAULT 'cdd01ef066bc6cf2' NOT NULL
);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers to relevant tables
CREATE TRIGGER update_code_symbols_updated_at
    BEFORE UPDATE ON code_symbols
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_code_context_links_updated_at
    BEFORE UPDATE ON code_context_links
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_file_metadata_updated_at
    BEFORE UPDATE ON file_metadata
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create constitutional compliance validation function
CREATE OR REPLACE FUNCTION validate_constitutional_hash()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.constitutional_hash != 'cdd01ef066bc6cf2' THEN
        RAISE EXCEPTION 'Invalid constitutional hash. Expected: cdd01ef066bc6cf2, Got: %', NEW.constitutional_hash;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply constitutional compliance triggers
CREATE TRIGGER validate_code_symbols_constitutional_hash
    BEFORE INSERT OR UPDATE ON code_symbols
    FOR EACH ROW EXECUTE FUNCTION validate_constitutional_hash();

CREATE TRIGGER validate_code_dependencies_constitutional_hash
    BEFORE INSERT OR UPDATE ON code_dependencies
    FOR EACH ROW EXECUTE FUNCTION validate_constitutional_hash();

CREATE TRIGGER validate_code_embeddings_constitutional_hash
    BEFORE INSERT OR UPDATE ON code_embeddings
    FOR EACH ROW EXECUTE FUNCTION validate_constitutional_hash();

CREATE TRIGGER validate_code_context_links_constitutional_hash
    BEFORE INSERT OR UPDATE ON code_context_links
    FOR EACH ROW EXECUTE FUNCTION validate_constitutional_hash();

-- Grant permissions to ACGS user
GRANT USAGE ON SCHEMA code_analysis TO acgs_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA code_analysis TO acgs_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA code_analysis TO acgs_user;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA code_analysis TO acgs_user;

-- Add comments for documentation
COMMENT ON SCHEMA code_analysis IS 'ACGS Code Analysis Engine schema for storing code symbols, dependencies, and embeddings';
COMMENT ON TABLE code_symbols IS 'Core table storing all extracted code symbols with metadata and constitutional compliance';
COMMENT ON TABLE code_dependencies IS 'Relationships between code symbols including imports, calls, and inheritance';
COMMENT ON TABLE code_embeddings IS 'Vector embeddings for semantic search using pgvector extension';
COMMENT ON TABLE code_context_links IS 'Integration links with ACGS Context Service for bidirectional context sharing';
COMMENT ON TABLE file_metadata IS 'Metadata about analyzed files for tracking and optimization';
COMMENT ON TABLE analysis_jobs IS 'Background job tracking for monitoring and debugging analysis operations';
COMMENT ON TABLE search_analytics IS 'Search query analytics for performance optimization and usage insights';
