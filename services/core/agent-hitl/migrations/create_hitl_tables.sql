-- Migration: Create Agent HITL Tables
-- Description: Creates tables for Agent Human-in-the-Loop oversight system
-- Version: 1.0.0
-- Date: 2025-06-30

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS agent_hitl;

-- Use the agent_hitl database
\c agent_hitl;

-- Create agent_operation_requests table
CREATE TABLE IF NOT EXISTS agent_operation_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    request_id VARCHAR(100) UNIQUE NOT NULL,
    agent_id VARCHAR(100) NOT NULL,
    operation_type VARCHAR(100) NOT NULL,
    operation_data JSONB NOT NULL,
    operation_context JSONB,
    
    -- Risk assessment
    risk_level VARCHAR(20) NOT NULL DEFAULT 'medium',
    risk_factors JSONB,
    
    -- Constitutional compliance
    constitutional_hash VARCHAR(64) NOT NULL DEFAULT 'cdd01ef066bc6cf2',
    constitutional_principles JSONB,
    requires_constitutional_review BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Timing and metadata
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    client_ip VARCHAR(45),
    user_agent VARCHAR(500)
);

-- Create hitl_decisions table
CREATE TABLE IF NOT EXISTS hitl_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_id VARCHAR(100) UNIQUE NOT NULL,
    operation_request_id UUID NOT NULL REFERENCES agent_operation_requests(id) ON DELETE CASCADE,
    
    -- Decision details
    escalation_level VARCHAR(30) NOT NULL,
    decision_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    confidence_score FLOAT NOT NULL,
    
    -- Decision reasoning
    decision_reasoning TEXT,
    risk_assessment JSONB,
    constitutional_compliance_score FLOAT,
    
    -- Processing details
    processing_time_ms FLOAT,
    cache_hit BOOLEAN NOT NULL DEFAULT FALSE,
    decision_algorithm VARCHAR(50),
    
    -- Human involvement
    requires_human_review BOOLEAN NOT NULL DEFAULT FALSE,
    human_reviewer_id INTEGER,
    human_decision_at TIMESTAMPTZ,
    human_feedback TEXT,
    
    -- Timing
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    
    -- Constitutional compliance
    constitutional_hash VARCHAR(64) NOT NULL DEFAULT 'cdd01ef066bc6cf2',
    compliance_verified BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Metadata
    metadata JSONB
);

-- Create agent_confidence_profiles table
CREATE TABLE IF NOT EXISTS agent_confidence_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id VARCHAR(100) UNIQUE NOT NULL,
    
    -- Overall confidence metrics
    overall_confidence_score FLOAT NOT NULL DEFAULT 0.5,
    total_operations INTEGER NOT NULL DEFAULT 0,
    successful_operations INTEGER NOT NULL DEFAULT 0,
    failed_operations INTEGER NOT NULL DEFAULT 0,
    
    -- Operation-specific confidence scores
    operation_type_scores JSONB NOT NULL DEFAULT '{}',
    risk_level_scores JSONB NOT NULL DEFAULT '{}',
    
    -- Learning parameters
    learning_rate FLOAT NOT NULL DEFAULT 0.1,
    adaptation_rate FLOAT NOT NULL DEFAULT 0.05,
    confidence_decay_rate FLOAT NOT NULL DEFAULT 0.01,
    
    -- Historical performance
    performance_history JSONB,
    last_performance_update TIMESTAMPTZ,
    
    -- Constitutional compliance
    constitutional_compliance_score FLOAT NOT NULL DEFAULT 0.8,
    constitutional_violations INTEGER NOT NULL DEFAULT 0,
    
    -- Timing
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_decision_at TIMESTAMPTZ,
    
    -- Metadata
    metadata JSONB
);

-- Create human_review_tasks table
CREATE TABLE IF NOT EXISTS human_review_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id VARCHAR(100) UNIQUE NOT NULL,
    decision_id UUID NOT NULL REFERENCES hitl_decisions(id) ON DELETE CASCADE,
    
    -- Task details
    task_type VARCHAR(50) NOT NULL,
    priority INTEGER NOT NULL DEFAULT 5,
    status VARCHAR(20) NOT NULL DEFAULT 'assigned',
    
    -- Assignment
    assigned_reviewer_id INTEGER,
    assigned_at TIMESTAMPTZ,
    reviewer_expertise JSONB,
    
    -- Task context
    operation_summary TEXT NOT NULL,
    risk_factors JSONB,
    constitutional_concerns JSONB,
    agent_context JSONB,
    
    -- Review details
    review_started_at TIMESTAMPTZ,
    review_completed_at TIMESTAMPTZ,
    review_decision VARCHAR(20),
    review_reasoning TEXT,
    review_confidence FLOAT,
    
    -- Timing constraints
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    due_at TIMESTAMPTZ NOT NULL,
    expires_at TIMESTAMPTZ,
    
    -- Metadata
    metadata JSONB
);

-- Create hitl_feedback table
CREATE TABLE IF NOT EXISTS hitl_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    feedback_id VARCHAR(100) UNIQUE NOT NULL,
    decision_id UUID NOT NULL REFERENCES hitl_decisions(id) ON DELETE CASCADE,
    
    -- Feedback details
    feedback_type VARCHAR(50) NOT NULL,
    feedback_source VARCHAR(50) NOT NULL,
    
    -- Feedback content
    original_confidence FLOAT NOT NULL,
    suggested_confidence FLOAT,
    confidence_adjustment FLOAT,
    
    -- Human feedback
    human_reviewer_id INTEGER,
    human_agreed_with_decision BOOLEAN,
    human_reasoning TEXT,
    human_confidence_rating FLOAT,
    
    -- Outcome validation
    actual_outcome VARCHAR(50),
    outcome_details JSONB,
    constitutional_compliance_actual BOOLEAN,
    
    -- Learning impact
    learning_weight FLOAT NOT NULL DEFAULT 1.0,
    applied_to_agent BOOLEAN NOT NULL DEFAULT FALSE,
    confidence_impact FLOAT,
    
    -- Timing
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    
    -- Metadata
    metadata JSONB
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_agent_operation_requests_agent_id ON agent_operation_requests(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_operation_requests_operation_type ON agent_operation_requests(operation_type);
CREATE INDEX IF NOT EXISTS idx_agent_operation_requests_created_at ON agent_operation_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_agent_operation_requests_risk_level ON agent_operation_requests(risk_level);

CREATE INDEX IF NOT EXISTS idx_hitl_decisions_decision_id ON hitl_decisions(decision_id);
CREATE INDEX IF NOT EXISTS idx_hitl_decisions_escalation_level ON hitl_decisions(escalation_level);
CREATE INDEX IF NOT EXISTS idx_hitl_decisions_decision_status ON hitl_decisions(decision_status);
CREATE INDEX IF NOT EXISTS idx_hitl_decisions_created_at ON hitl_decisions(created_at);
CREATE INDEX IF NOT EXISTS idx_hitl_decisions_confidence_score ON hitl_decisions(confidence_score);

CREATE INDEX IF NOT EXISTS idx_agent_confidence_profiles_agent_id ON agent_confidence_profiles(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_confidence_profiles_updated_at ON agent_confidence_profiles(updated_at);

CREATE INDEX IF NOT EXISTS idx_human_review_tasks_task_id ON human_review_tasks(task_id);
CREATE INDEX IF NOT EXISTS idx_human_review_tasks_status ON human_review_tasks(status);
CREATE INDEX IF NOT EXISTS idx_human_review_tasks_priority ON human_review_tasks(priority);
CREATE INDEX IF NOT EXISTS idx_human_review_tasks_assigned_reviewer_id ON human_review_tasks(assigned_reviewer_id);
CREATE INDEX IF NOT EXISTS idx_human_review_tasks_created_at ON human_review_tasks(created_at);

CREATE INDEX IF NOT EXISTS idx_hitl_feedback_decision_id ON hitl_feedback(decision_id);
CREATE INDEX IF NOT EXISTS idx_hitl_feedback_feedback_type ON hitl_feedback(feedback_type);
CREATE INDEX IF NOT EXISTS idx_hitl_feedback_created_at ON hitl_feedback(created_at);

-- Create GIN indexes for JSONB columns
CREATE INDEX IF NOT EXISTS idx_agent_operation_requests_operation_data_gin ON agent_operation_requests USING GIN(operation_data);
CREATE INDEX IF NOT EXISTS idx_agent_operation_requests_constitutional_principles_gin ON agent_operation_requests USING GIN(constitutional_principles);
CREATE INDEX IF NOT EXISTS idx_hitl_decisions_risk_assessment_gin ON hitl_decisions USING GIN(risk_assessment);
CREATE INDEX IF NOT EXISTS idx_agent_confidence_profiles_operation_type_scores_gin ON agent_confidence_profiles USING GIN(operation_type_scores);

-- Add constraints
ALTER TABLE agent_operation_requests ADD CONSTRAINT chk_risk_level 
    CHECK (risk_level IN ('low', 'medium', 'high', 'critical'));

ALTER TABLE hitl_decisions ADD CONSTRAINT chk_escalation_level 
    CHECK (escalation_level IN ('level_1_auto_approve', 'level_2_auto_notify', 'level_3_human_review', 'level_4_council_review'));

ALTER TABLE hitl_decisions ADD CONSTRAINT chk_decision_status 
    CHECK (decision_status IN ('pending', 'approved', 'rejected', 'escalated', 'timeout', 'error'));

ALTER TABLE hitl_decisions ADD CONSTRAINT chk_confidence_score 
    CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0);

ALTER TABLE agent_confidence_profiles ADD CONSTRAINT chk_overall_confidence_score 
    CHECK (overall_confidence_score >= 0.0 AND overall_confidence_score <= 1.0);

ALTER TABLE agent_confidence_profiles ADD CONSTRAINT chk_constitutional_compliance_score 
    CHECK (constitutional_compliance_score >= 0.0 AND constitutional_compliance_score <= 1.0);

ALTER TABLE human_review_tasks ADD CONSTRAINT chk_task_status 
    CHECK (status IN ('assigned', 'in_progress', 'completed', 'escalated', 'expired'));

ALTER TABLE human_review_tasks ADD CONSTRAINT chk_priority 
    CHECK (priority >= 1 AND priority <= 10);

-- Add comments for documentation
COMMENT ON TABLE agent_operation_requests IS 'Agent operation requests requiring HITL evaluation';
COMMENT ON TABLE hitl_decisions IS 'HITL decisions for agent operations';
COMMENT ON TABLE agent_confidence_profiles IS 'Agent confidence profiles for decision making';
COMMENT ON TABLE human_review_tasks IS 'Human review tasks for agent operations';
COMMENT ON TABLE hitl_feedback IS 'Feedback on HITL decisions for system improvement';

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger for agent_confidence_profiles
CREATE TRIGGER update_agent_confidence_profiles_updated_at
    BEFORE UPDATE ON agent_confidence_profiles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant permissions (adjust user as needed)
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO hitl_service_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO hitl_service_user;
