-- ACGS Persistent Audit Trail Database Schema Migration
-- Constitutional Hash: cdd01ef066bc6cf2

-- Create audit_blocks table first (referenced by audit_events)
CREATE TABLE IF NOT EXISTS audit_blocks (
    block_id UUID PRIMARY KEY,
    block_number INTEGER UNIQUE NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL,
    previous_hash VARCHAR(64) NOT NULL,
    merkle_root VARCHAR(64) NOT NULL,
    block_hash VARCHAR(64) UNIQUE NOT NULL,
    signature TEXT NOT NULL,
    constitutional_hash VARCHAR(64) NOT NULL,
    event_count INTEGER DEFAULT 0,
    finalized BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create audit_events table
CREATE TABLE IF NOT EXISTS audit_events (
    event_id UUID PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    service_name VARCHAR(100) NOT NULL,
    user_id VARCHAR(255),
    session_id VARCHAR(255),
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(255),
    description TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    severity VARCHAR(20) DEFAULT 'medium',
    constitutional_hash VARCHAR(64) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    request_id VARCHAR(255),
    block_id UUID REFERENCES audit_blocks(block_id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_audit_events_timestamp ON audit_events(timestamp);
CREATE INDEX IF NOT EXISTS idx_audit_events_service ON audit_events(service_name);
CREATE INDEX IF NOT EXISTS idx_audit_events_type ON audit_events(event_type);
CREATE INDEX IF NOT EXISTS idx_audit_events_user ON audit_events(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_events_block ON audit_events(block_id);
CREATE INDEX IF NOT EXISTS idx_audit_blocks_number ON audit_blocks(block_number);
CREATE INDEX IF NOT EXISTS idx_audit_blocks_hash ON audit_blocks(block_hash);
CREATE INDEX IF NOT EXISTS idx_audit_blocks_finalized ON audit_blocks(finalized);

-- Create sequence for block numbers
CREATE SEQUENCE IF NOT EXISTS audit_block_sequence START 1;

-- Insert initial genesis block
INSERT INTO audit_blocks (
    block_id,
    block_number,
    timestamp,
    previous_hash,
    merkle_root,
    block_hash,
    signature,
    constitutional_hash,
    event_count,
    finalized
) VALUES (
    gen_random_uuid(),
    0,
    NOW(),
    'genesis_block_hash',
    'genesis_merkle_root',
    encode(sha256('genesis_block:cdd01ef066bc6cf2'::bytea), 'hex'),
    'genesis_signature',
    'cdd01ef066bc6cf2',
    0,
    TRUE
) ON CONFLICT (block_number) DO NOTHING;

-- Create audit trail statistics view
CREATE OR REPLACE VIEW audit_trail_stats AS
SELECT
    'cdd01ef066bc6cf2' as constitutional_hash,
    (SELECT COUNT(*) FROM audit_blocks) as total_blocks,
    (SELECT COUNT(*) FROM audit_events) as total_events,
    (SELECT COUNT(*) FROM audit_events WHERE timestamp > NOW() - INTERVAL '24 hours') as recent_events_24h,
    (SELECT COUNT(*) FROM audit_events WHERE timestamp > NOW() - INTERVAL '1 hour') as recent_events_1h,
    (SELECT MAX(block_number) FROM audit_blocks) as latest_block_number,
    (SELECT MIN(timestamp) FROM audit_events) as first_event_timestamp,
    (SELECT MAX(timestamp) FROM audit_events) as last_event_timestamp,
    NOW() as query_timestamp;

-- Grant permissions (adjust as needed for your deployment)
-- GRANT SELECT, INSERT, UPDATE ON audit_events TO acgs_user;
-- GRANT SELECT, INSERT, UPDATE ON audit_blocks TO acgs_user;
-- GRANT SELECT ON audit_trail_stats TO acgs_user;
