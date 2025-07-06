-- ACGS Code Analysis Engine - Simple Database Schema
-- Migration: 001_simple_schema.sql
-- Description: Creates basic tables for staging deployment validation
-- Constitutional Hash: cdd01ef066bc6cf2

-- Enable required PostgreSQL extensions (excluding vector for now)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create schema for code analysis engine
CREATE SCHEMA IF NOT EXISTS code_analysis;

-- Set search path
SET search_path TO code_analysis, public;

-- Table: service_health
-- Stores service health check information
CREATE TABLE service_health (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    constitutional_hash VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Table: audit_log
-- Stores audit trail for constitutional compliance
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255),
    user_id VARCHAR(255),
    constitutional_hash VARCHAR(255) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    details JSONB DEFAULT '{}'::jsonb
);

-- Table: configuration
-- Stores service configuration
CREATE TABLE configuration (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(255) UNIQUE NOT NULL,
    value TEXT NOT NULL,
    constitutional_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Insert initial configuration
INSERT INTO configuration (key, value, constitutional_hash) VALUES
('service_name', 'acgs-code-analysis-engine', 'cdd01ef066bc6cf2'),
('service_version', '1.0.0', 'cdd01ef066bc6cf2'),
('constitutional_hash', 'cdd01ef066bc6cf2', 'cdd01ef066bc6cf2');

-- Create indexes for performance
CREATE INDEX idx_service_health_timestamp ON service_health(timestamp);
CREATE INDEX idx_service_health_constitutional_hash ON service_health(constitutional_hash);
CREATE INDEX idx_audit_log_timestamp ON audit_log(timestamp);
CREATE INDEX idx_audit_log_constitutional_hash ON audit_log(constitutional_hash);
CREATE INDEX idx_configuration_key ON configuration(key);

-- Insert initial health check record
INSERT INTO service_health (service_name, status, constitutional_hash, metadata) VALUES
('acgs-code-analysis-engine', 'healthy', 'cdd01ef066bc6cf2', '{"deployment": "staging", "phase": "2"}');

-- Insert initial audit log entry
INSERT INTO audit_log (action, resource_type, resource_id, constitutional_hash, details) VALUES
('database_migration', 'schema', '001_simple_schema', 'cdd01ef066bc6cf2', '{"migration": "001_simple_schema.sql", "status": "completed"}');

-- Grant permissions (if needed)
-- GRANT ALL PRIVILEGES ON SCHEMA code_analysis TO acgs_user;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA code_analysis TO acgs_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA code_analysis TO acgs_user;
