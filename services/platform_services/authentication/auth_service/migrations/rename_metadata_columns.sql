-- Migration: Rename metadata columns to avoid SQLAlchemy reserved name conflicts
-- Date: 2025-01-03
-- Description: Rename 'metadata' columns to 'agent_metadata' and 'audit_metadata' 
--              to avoid conflicts with SQLAlchemy's reserved 'metadata' attribute

-- Constitutional compliance hash for ACGS
-- Hash: cdd01ef066bc6cf2

BEGIN;

-- Rename metadata column in agents table to agent_metadata
ALTER TABLE agents 
RENAME COLUMN metadata TO agent_metadata;

-- Rename metadata column in agent_audit_logs table to audit_metadata  
ALTER TABLE agent_audit_logs 
RENAME COLUMN metadata TO audit_metadata;

-- Update comments to reflect new column names
COMMENT ON COLUMN agents.agent_metadata IS 'Additional metadata for the agent (JSON format)';
COMMENT ON COLUMN agent_audit_logs.audit_metadata IS 'Additional context metadata for the audit log entry (JSON format)';

COMMIT;
