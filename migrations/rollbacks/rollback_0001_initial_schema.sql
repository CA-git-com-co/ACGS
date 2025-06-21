-- Rollback script for 0001_initial_schema.sql
-- This script reverses all changes made in the initial schema migration

-- Set search path
SET search_path TO acgs, public;

-- Drop triggers first
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
DROP TRIGGER IF EXISTS update_constitutional_documents_updated_at ON constitutional_documents;
DROP TRIGGER IF EXISTS update_governance_proposals_updated_at ON governance_proposals;
DROP TRIGGER IF EXISTS update_policy_rules_updated_at ON policy_rules;

-- Drop trigger function
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS verification_results;
DROP TABLE IF EXISTS audit_log;
DROP TABLE IF EXISTS policy_rules;
DROP TABLE IF EXISTS votes;
DROP TABLE IF EXISTS governance_proposals;
DROP TABLE IF EXISTS constitutional_documents;
DROP TABLE IF EXISTS users;

-- Drop schema
DROP SCHEMA IF EXISTS acgs CASCADE;
