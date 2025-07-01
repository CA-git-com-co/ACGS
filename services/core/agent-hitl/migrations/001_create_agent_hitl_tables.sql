-- Migration: Create Agent HITL Tables
-- Description: Creates tables for agent operation reviews and human oversight
-- Version: 1.0.0
-- Date: 2025-06-30

-- Create agent_operation_reviews table
CREATE TABLE IF NOT EXISTS agent_operation_reviews (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- Agent information
    agent_id VARCHAR(100) NOT NULL,
    agent_type VARCHAR(50) NOT NULL,
    agent_version VARCHAR(50),
    
    -- Operation details
    operation_type VARCHAR(100) NOT NULL,
    operation_description TEXT NOT NULL,
    operation_context JSONB NOT NULL DEFAULT '{}',
    operation_target VARCHAR(500),
    
    -- Confidence and risk assessment
    confidence_score FLOAT NOT NULL,
    risk_score FLOAT NOT NULL,
    risk_level VARCHAR(20) NOT NULL DEFAULT 'low',
    confidence_factors JSONB DEFAULT '{}',
    risk_factors JSONB DEFAULT '{}',
    
    -- Constitutional compliance
    constitutional_hash VARCHAR(64) NOT NULL,
    policy_violations JSONB DEFAULT '[]',
    applicable_principles JSONB DEFAULT '[]',
    
    -- Review status and decision
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    escalation_level INTEGER NOT NULL DEFAULT 1,
    decision VARCHAR(20),
    decision_reason TEXT,
    decision_metadata JSONB DEFAULT '{}',
    
    -- Timing information
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    decided_at TIMESTAMPTZ,
    processing_time_ms INTEGER,
    
    -- Human review information
    reviewed_by_user_id INTEGER,
    reviewed_by_username VARCHAR(255),
    reviewer_notes TEXT,
    
    -- Request metadata
    request_id VARCHAR(100),
    session_id VARCHAR(100),
    client_ip VARCHAR(45),
    
    -- Additional metadata
    additional_metadata JSONB DEFAULT '{}',
    tags JSONB DEFAULT '[]'
);

-- Create indexes for agent_operation_reviews
CREATE INDEX IF NOT EXISTS idx_agent_operation_reviews_review_id ON agent_operation_reviews(review_id);
CREATE INDEX IF NOT EXISTS idx_agent_operation_reviews_agent_id ON agent_operation_reviews(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_operation_reviews_status ON agent_operation_reviews(status);
CREATE INDEX IF NOT EXISTS idx_agent_operation_reviews_escalation_level ON agent_operation_reviews(escalation_level);
CREATE INDEX IF NOT EXISTS idx_agent_operation_reviews_created_at ON agent_operation_reviews(created_at);
CREATE INDEX IF NOT EXISTS idx_agent_operation_reviews_decided_at ON agent_operation_reviews(decided_at);
CREATE INDEX IF NOT EXISTS idx_agent_operation_reviews_operation_type ON agent_operation_reviews(operation_type);
CREATE INDEX IF NOT EXISTS idx_agent_operation_reviews_risk_level ON agent_operation_reviews(risk_level);

-- Create GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_agent_operation_reviews_operation_context_gin ON agent_operation_reviews USING GIN(operation_context);
CREATE INDEX IF NOT EXISTS idx_agent_operation_reviews_additional_metadata_gin ON agent_operation_reviews USING GIN(additional_metadata);
CREATE INDEX IF NOT EXISTS idx_agent_operation_reviews_tags_gin ON agent_operation_reviews USING GIN(tags);

-- Create review_feedbacks table
CREATE TABLE IF NOT EXISTS review_feedbacks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    review_id UUID NOT NULL REFERENCES agent_operation_reviews(id) ON DELETE CASCADE,
    
    -- Feedback details
    feedback_type VARCHAR(50) NOT NULL,
    feedback_value VARCHAR(20) NOT NULL,
    feedback_reason TEXT,
    
    -- Suggestions for improvement
    suggested_confidence FLOAT,
    suggested_risk_score FLOAT,
    suggested_decision VARCHAR(20),
    improvement_notes TEXT,
    
    -- Metadata
    provided_by_user_id INTEGER NOT NULL,
    provided_by_username VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create indexes for review_feedbacks
CREATE INDEX IF NOT EXISTS idx_review_feedbacks_review_id ON review_feedbacks(review_id);
CREATE INDEX IF NOT EXISTS idx_review_feedbacks_feedback_type ON review_feedbacks(feedback_type);
CREATE INDEX IF NOT EXISTS idx_review_feedbacks_provided_by_user_id ON review_feedbacks(provided_by_user_id);
CREATE INDEX IF NOT EXISTS idx_review_feedbacks_created_at ON review_feedbacks(created_at);

-- Create agent_confidence_profiles table
CREATE TABLE IF NOT EXISTS agent_confidence_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- Operation-specific confidence adjustments
    operation_confidence_adjustments JSONB DEFAULT '{}',
    
    -- Historical performance metrics
    total_operations INTEGER DEFAULT 0,
    auto_approved_operations INTEGER DEFAULT 0,
    human_approved_operations INTEGER DEFAULT 0,
    rejected_operations INTEGER DEFAULT 0,
    
    -- Accuracy metrics
    correct_auto_approvals INTEGER DEFAULT 0,
    incorrect_auto_approvals INTEGER DEFAULT 0,
    
    -- Adaptive confidence parameters
    base_confidence_adjustment FLOAT DEFAULT 0.0,
    risk_tolerance_factor FLOAT DEFAULT 1.0,
    
    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Profile metadata
    profile_version INTEGER DEFAULT 1,
    profile_metadata JSONB DEFAULT '{}'
);

-- Create indexes for agent_confidence_profiles
CREATE INDEX IF NOT EXISTS idx_agent_confidence_profiles_agent_id ON agent_confidence_profiles(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_confidence_profiles_created_at ON agent_confidence_profiles(created_at);
CREATE INDEX IF NOT EXISTS idx_agent_confidence_profiles_updated_at ON agent_confidence_profiles(updated_at);

-- Create GIN index for operation confidence adjustments
CREATE INDEX IF NOT EXISTS idx_agent_confidence_profiles_adjustments_gin ON agent_confidence_profiles USING GIN(operation_confidence_adjustments);

-- Add constraints and checks
ALTER TABLE agent_operation_reviews ADD CONSTRAINT chk_review_status 
    CHECK (status IN ('pending', 'auto_approved', 'human_approved', 'human_rejected', 'escalated', 'timeout', 'error'));

ALTER TABLE agent_operation_reviews ADD CONSTRAINT chk_escalation_level 
    CHECK (escalation_level IN (1, 2, 3, 4));

ALTER TABLE agent_operation_reviews ADD CONSTRAINT chk_risk_level 
    CHECK (risk_level IN ('low', 'medium', 'high', 'critical'));

ALTER TABLE agent_operation_reviews ADD CONSTRAINT chk_decision 
    CHECK (decision IS NULL OR decision IN ('approved', 'rejected'));

ALTER TABLE agent_operation_reviews ADD CONSTRAINT chk_confidence_score_range 
    CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0);

ALTER TABLE agent_operation_reviews ADD CONSTRAINT chk_risk_score_range 
    CHECK (risk_score >= 0.0 AND risk_score <= 1.0);

ALTER TABLE review_feedbacks ADD CONSTRAINT chk_feedback_value 
    CHECK (feedback_value IN ('correct', 'incorrect', 'partial'));

ALTER TABLE agent_confidence_profiles ADD CONSTRAINT chk_base_confidence_range 
    CHECK (base_confidence_adjustment >= -1.0 AND base_confidence_adjustment <= 1.0);

ALTER TABLE agent_confidence_profiles ADD CONSTRAINT chk_risk_tolerance_positive 
    CHECK (risk_tolerance_factor > 0.0);

-- Add comments for documentation
COMMENT ON TABLE agent_operation_reviews IS 'Records of agent operation evaluations and human reviews';
COMMENT ON TABLE review_feedbacks IS 'Feedback on review decisions for learning and improvement';
COMMENT ON TABLE agent_confidence_profiles IS 'Agent-specific confidence profiles and historical performance';

COMMENT ON COLUMN agent_operation_reviews.review_id IS 'Human-readable unique identifier for the review';
COMMENT ON COLUMN agent_operation_reviews.confidence_score IS 'AI confidence score for the operation (0.0-1.0)';
COMMENT ON COLUMN agent_operation_reviews.risk_score IS 'Risk assessment score for the operation (0.0-1.0)';
COMMENT ON COLUMN agent_operation_reviews.escalation_level IS 'Review escalation level: 1=auto, 2=team_lead, 3=expert, 4=council';
COMMENT ON COLUMN agent_operation_reviews.constitutional_hash IS 'Hash of constitutional principles used for evaluation';

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_agent_confidence_profile_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for automatic timestamp updates
CREATE TRIGGER trigger_update_agent_confidence_profile_updated_at
    BEFORE UPDATE ON agent_confidence_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_agent_confidence_profile_updated_at();

-- Create view for pending reviews by escalation level
CREATE OR REPLACE VIEW pending_reviews_by_level AS
SELECT 
    escalation_level,
    COUNT(*) as pending_count,
    AVG(confidence_score) as avg_confidence,
    AVG(risk_score) as avg_risk,
    MIN(created_at) as oldest_review,
    MAX(created_at) as newest_review
FROM agent_operation_reviews 
WHERE status IN ('pending', 'escalated')
GROUP BY escalation_level
ORDER BY escalation_level;

-- Create view for agent performance summary
CREATE OR REPLACE VIEW agent_performance_summary AS
SELECT 
    r.agent_id,
    r.agent_type,
    COUNT(*) as total_reviews,
    COUNT(CASE WHEN r.status = 'auto_approved' THEN 1 END) as auto_approved,
    COUNT(CASE WHEN r.status = 'human_approved' THEN 1 END) as human_approved,
    COUNT(CASE WHEN r.status = 'human_rejected' THEN 1 END) as rejected,
    AVG(r.confidence_score) as avg_confidence,
    AVG(r.risk_score) as avg_risk,
    AVG(r.processing_time_ms) as avg_processing_time_ms,
    p.base_confidence_adjustment,
    p.risk_tolerance_factor
FROM agent_operation_reviews r
LEFT JOIN agent_confidence_profiles p ON r.agent_id = p.agent_id
GROUP BY r.agent_id, r.agent_type, p.base_confidence_adjustment, p.risk_tolerance_factor
ORDER BY total_reviews DESC;

-- Grant appropriate permissions (adjust user names as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON agent_operation_reviews TO agent_hitl_service_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON review_feedbacks TO agent_hitl_service_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON agent_confidence_profiles TO agent_hitl_service_user;
-- GRANT SELECT ON pending_reviews_by_level TO agent_hitl_service_user;
-- GRANT SELECT ON agent_performance_summary TO agent_hitl_service_user;

-- Insert some initial test data (remove in production)
-- This creates a sample agent confidence profile
INSERT INTO agent_confidence_profiles (agent_id, operation_confidence_adjustments, profile_metadata) VALUES
    ('test-coding-agent-001', '{"code_execution": 0.05, "code_modification": -0.1}', '{"test_profile": true}')
ON CONFLICT (agent_id) DO NOTHING;