-- Description: Initial ACGS-1 database schema for constitutional governance system
-- Version: 0001
-- Author: ACGS Development Team
-- Date: 2024-01-15

-- Create ACGS schema
CREATE SCHEMA IF NOT EXISTS acgs;

-- Set search path
SET search_path TO acgs, public;

-- Users table for authentication
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'citizen',
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE
);

-- Constitutional documents table
CREATE TABLE constitutional_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    document_type VARCHAR(100) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    hash_value VARCHAR(64) NOT NULL,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    effective_date TIMESTAMP WITH TIME ZONE,
    expiry_date TIMESTAMP WITH TIME ZONE
);

-- Governance proposals table
CREATE TABLE governance_proposals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    proposal_type VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    constitutional_document_id UUID REFERENCES constitutional_documents(id),
    proposed_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    voting_start_date TIMESTAMP WITH TIME ZONE,
    voting_end_date TIMESTAMP WITH TIME ZONE,
    approval_threshold DECIMAL(5,4) DEFAULT 0.5000
);

-- Votes table
CREATE TABLE votes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID REFERENCES governance_proposals(id),
    user_id UUID REFERENCES users(id),
    vote_value VARCHAR(20) NOT NULL CHECK (vote_value IN ('approve', 'reject', 'abstain')),
    reasoning TEXT,
    cast_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(proposal_id, user_id)
);

-- Policy rules table
CREATE TABLE policy_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    rule_type VARCHAR(100) NOT NULL,
    rule_content JSONB NOT NULL,
    constitutional_document_id UUID REFERENCES constitutional_documents(id),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Audit log table
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID NOT NULL,
    action VARCHAR(100) NOT NULL,
    old_values JSONB,
    new_values JSONB,
    user_id UUID REFERENCES users(id),
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Formal verification results table
CREATE TABLE verification_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES constitutional_documents(id),
    verification_type VARCHAR(100) NOT NULL,
    result VARCHAR(50) NOT NULL,
    details JSONB,
    verified_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    verified_by VARCHAR(255)
);

-- Create indexes for performance
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_created_at ON users(created_at);

CREATE INDEX idx_constitutional_documents_type ON constitutional_documents(document_type);
CREATE INDEX idx_constitutional_documents_status ON constitutional_documents(status);
CREATE INDEX idx_constitutional_documents_created_at ON constitutional_documents(created_at);
CREATE INDEX idx_constitutional_documents_hash ON constitutional_documents(hash_value);

CREATE INDEX idx_governance_proposals_type ON governance_proposals(proposal_type);
CREATE INDEX idx_governance_proposals_status ON governance_proposals(status);
CREATE INDEX idx_governance_proposals_created_at ON governance_proposals(created_at);
CREATE INDEX idx_governance_proposals_voting_dates ON governance_proposals(voting_start_date, voting_end_date);

CREATE INDEX idx_votes_proposal_id ON votes(proposal_id);
CREATE INDEX idx_votes_user_id ON votes(user_id);
CREATE INDEX idx_votes_cast_at ON votes(cast_at);

CREATE INDEX idx_policy_rules_type ON policy_rules(rule_type);
CREATE INDEX idx_policy_rules_active ON policy_rules(is_active);
CREATE INDEX idx_policy_rules_document_id ON policy_rules(constitutional_document_id);

CREATE INDEX idx_audit_log_entity ON audit_log(entity_type, entity_id);
CREATE INDEX idx_audit_log_user_id ON audit_log(user_id);
CREATE INDEX idx_audit_log_created_at ON audit_log(created_at);
CREATE INDEX idx_audit_log_action ON audit_log(action);

CREATE INDEX idx_verification_results_document_id ON verification_results(document_id);
CREATE INDEX idx_verification_results_type ON verification_results(verification_type);
CREATE INDEX idx_verification_results_verified_at ON verification_results(verified_at);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_constitutional_documents_updated_at BEFORE UPDATE ON constitutional_documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_governance_proposals_updated_at BEFORE UPDATE ON governance_proposals
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_policy_rules_updated_at BEFORE UPDATE ON policy_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial data
INSERT INTO users (username, email, password_hash, first_name, last_name, role) VALUES
('admin', 'admin@acgs-pgp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uDjO', 'System', 'Administrator', 'admin'),
('constitutional_ai', 'ai@acgs-pgp.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj/RK.s5uDjO', 'Constitutional', 'AI', 'system');

-- Grant permissions
GRANT USAGE ON SCHEMA acgs TO acgs_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA acgs TO acgs_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA acgs TO acgs_user;
