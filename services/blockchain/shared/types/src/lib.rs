// Constitutional Hash: cdd01ef066bc6cf2
//! ACGS-2 Shared Data Types and Interfaces
//! 
//! This library provides common data types used across both the expert service
//! and blockchain components of the ACGS-2 governance system.

use acgs_constitutional::{ConstitutionalCompliance, ConstitutionalError, ConstitutionalMetadata, CONSTITUTIONAL_HASH};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use thiserror::Error;
use uuid::Uuid;

#[cfg(feature = "blockchain")]
use solana_sdk::{pubkey::Pubkey, signature::Signature};

/// Common errors across ACGS-2 components
#[derive(Error, Debug, Clone)]
pub enum AcgsError {
    #[error("Constitutional compliance error: {0}")]
    Constitutional(#[from] ConstitutionalError),
    
    #[error("Governance decision error: {0}")]
    GovernanceDecision(String),
    
    #[error("Policy validation error: {0}")]
    PolicyValidation(String),
    
    #[error("Blockchain operation error: {0}")]
    BlockchainOperation(String),
    
    #[error("Configuration error: {0}")]
    Configuration(String),
    
    #[error("Serialization error: {0}")]
    Serialization(String),
}

/// Governance decision types
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[cfg_attr(feature = "utoipa", derive(utoipa::ToSchema))]
pub enum Decision {
    Comply,
    Violate,
    Uncertain { explanation: String },
}

impl std::fmt::Display for Decision {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Decision::Comply => write!(f, "Comply"),
            Decision::Violate => write!(f, "Violate"),
            Decision::Uncertain { explanation } => write!(f, "Uncertain: {}", explanation),
        }
    }
}

/// Working memory for governance decisions
#[derive(Debug, Clone, Serialize, Deserialize, Default)]
pub struct WorkingMemory {
    pub facts: HashMap<String, String>,
    pub rules_applied: Vec<String>,
    pub confidence_scores: HashMap<String, f64>,
    pub constitutional_metadata: Option<ConstitutionalMetadata>,
}

impl WorkingMemory {
    /// Create new working memory with constitutional compliance
    pub fn new() -> Self {
        Self {
            facts: HashMap::new(),
            rules_applied: Vec::new(),
            confidence_scores: HashMap::new(),
            constitutional_metadata: Some(ConstitutionalMetadata::new("acgs-working-memory")),
        }
    }
    
    /// Add a fact to working memory
    pub fn add_fact(&mut self, key: impl Into<String>, value: impl Into<String>) {
        self.facts.insert(key.into(), value.into());
    }
    
    /// Add a rule that was applied
    pub fn add_rule(&mut self, rule: impl Into<String>) {
        self.rules_applied.push(rule.into());
    }
    
    /// Set confidence score for a decision component
    pub fn set_confidence(&mut self, component: impl Into<String>, score: f64) {
        self.confidence_scores.insert(component.into(), score);
    }
    
    /// Get overall confidence score
    pub fn overall_confidence(&self) -> f64 {
        if self.confidence_scores.is_empty() {
            0.0
        } else {
            self.confidence_scores.values().sum::<f64>() / self.confidence_scores.len() as f64
        }
    }
}

impl ConstitutionalCompliance for WorkingMemory {
    fn validate_constitutional_compliance(&self) -> Result<(), ConstitutionalError> {
        match &self.constitutional_metadata {
            Some(metadata) => metadata.validate_constitutional_compliance(),
            None => Err(ConstitutionalError::HashMissing),
        }
    }
    
    fn constitutional_hash(&self) -> &str {
        self.constitutional_metadata
            .as_ref()
            .map(|m| m.constitutional_hash())
            .unwrap_or("")
    }
}

/// Governance query for decision making
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GovernanceQuery {
    pub id: Uuid,
    pub actor_role: String,
    pub data_sensitivity: String,
    pub context: HashMap<String, String>,
    pub timestamp: i64,
    pub constitutional_metadata: ConstitutionalMetadata,
}

impl GovernanceQuery {
    /// Create a new governance query
    pub fn new(actor_role: impl Into<String>, data_sensitivity: impl Into<String>) -> Self {
        Self {
            id: Uuid::new_v4(),
            actor_role: actor_role.into(),
            data_sensitivity: data_sensitivity.into(),
            context: HashMap::new(),
            timestamp: chrono::Utc::now().timestamp(),
            constitutional_metadata: ConstitutionalMetadata::new("governance-query"),
        }
    }
    
    /// Add context to the query
    pub fn with_context(mut self, key: impl Into<String>, value: impl Into<String>) -> Self {
        self.context.insert(key.into(), value.into());
        self
    }
}

impl ConstitutionalCompliance for GovernanceQuery {
    fn validate_constitutional_compliance(&self) -> Result<(), ConstitutionalError> {
        self.constitutional_metadata.validate_constitutional_compliance()
    }
    
    fn constitutional_hash(&self) -> &str {
        self.constitutional_metadata.constitutional_hash()
    }
}

/// Governance decision response
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GovernanceResponse {
    pub query_id: Uuid,
    pub decision: Decision,
    pub confidence: f64,
    pub reasoning: Vec<String>,
    pub working_memory: WorkingMemory,
    pub timestamp: i64,
    pub constitutional_hash: String,
}

impl GovernanceResponse {
    /// Create a new governance response
    pub fn new(
        query_id: Uuid,
        decision: Decision,
        confidence: f64,
        working_memory: WorkingMemory,
    ) -> Self {
        Self {
            query_id,
            decision,
            confidence,
            reasoning: Vec::new(),
            working_memory,
            timestamp: chrono::Utc::now().timestamp(),
            constitutional_hash: CONSTITUTIONAL_HASH.to_string(),
        }
    }
    
    /// Add reasoning to the response
    pub fn with_reasoning(mut self, reason: impl Into<String>) -> Self {
        self.reasoning.push(reason.into());
        self
    }
}

impl ConstitutionalCompliance for GovernanceResponse {
    fn validate_constitutional_compliance(&self) -> Result<(), ConstitutionalError> {
        if self.constitutional_hash != CONSTITUTIONAL_HASH {
            return Err(ConstitutionalError::HashMismatch {
                expected: CONSTITUTIONAL_HASH.to_string(),
                actual: self.constitutional_hash.clone(),
            });
        }
        self.working_memory.validate_constitutional_compliance()
    }
    
    fn constitutional_hash(&self) -> &str {
        &self.constitutional_hash
    }
}

/// Policy proposal status
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
pub enum ProposalStatus {
    Active,
    Approved,
    Rejected,
    Emergency,
    Expired,
}

/// Policy proposal
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyProposal {
    pub id: u64,
    pub title: String,
    pub description: String,
    pub policy_text: String,
    pub status: ProposalStatus,
    pub created_at: i64,
    pub voting_ends_at: i64,
    pub votes_for: u64,
    pub votes_against: u64,
    pub constitutional_metadata: ConstitutionalMetadata,
}

impl PolicyProposal {
    /// Create a new policy proposal
    pub fn new(
        id: u64,
        title: impl Into<String>,
        description: impl Into<String>,
        policy_text: impl Into<String>,
        voting_period_seconds: i64,
    ) -> Self {
        let now = chrono::Utc::now().timestamp();
        Self {
            id,
            title: title.into(),
            description: description.into(),
            policy_text: policy_text.into(),
            status: ProposalStatus::Active,
            created_at: now,
            voting_ends_at: now + voting_period_seconds,
            votes_for: 0,
            votes_against: 0,
            constitutional_metadata: ConstitutionalMetadata::new("policy-proposal"),
        }
    }
    
    /// Check if proposal is still active
    pub fn is_active(&self) -> bool {
        matches!(self.status, ProposalStatus::Active) 
            && chrono::Utc::now().timestamp() < self.voting_ends_at
    }
    
    /// Get vote ratio (for / total)
    pub fn vote_ratio(&self) -> f64 {
        let total = self.votes_for + self.votes_against;
        if total == 0 {
            0.0
        } else {
            self.votes_for as f64 / total as f64
        }
    }
}

impl ConstitutionalCompliance for PolicyProposal {
    fn validate_constitutional_compliance(&self) -> Result<(), ConstitutionalError> {
        self.constitutional_metadata.validate_constitutional_compliance()
    }
    
    fn constitutional_hash(&self) -> &str {
        self.constitutional_metadata.constitutional_hash()
    }
}

/// Blockchain governance decision (when blockchain integration is enabled)
#[cfg(feature = "blockchain")]
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BlockchainGovernanceDecision {
    pub decision: Decision,
    pub confidence: f64,
    pub policy_id: u64,
    pub constitutional_hash: String,
    pub timestamp: i64,
    pub proposer: Pubkey,
    pub transaction_signature: Option<Signature>,
}

#[cfg(feature = "blockchain")]
impl BlockchainGovernanceDecision {
    /// Create a new blockchain governance decision
    pub fn new(
        decision: Decision,
        confidence: f64,
        policy_id: u64,
        proposer: Pubkey,
    ) -> Self {
        Self {
            decision,
            confidence,
            policy_id,
            constitutional_hash: CONSTITUTIONAL_HASH.to_string(),
            timestamp: chrono::Utc::now().timestamp(),
            proposer,
            transaction_signature: None,
        }
    }
    
    /// Set the transaction signature after blockchain submission
    pub fn with_signature(mut self, signature: Signature) -> Self {
        self.transaction_signature = Some(signature);
        self
    }
}

#[cfg(feature = "blockchain")]
impl ConstitutionalCompliance for BlockchainGovernanceDecision {
    fn validate_constitutional_compliance(&self) -> Result<(), ConstitutionalError> {
        if self.constitutional_hash != CONSTITUTIONAL_HASH {
            return Err(ConstitutionalError::HashMismatch {
                expected: CONSTITUTIONAL_HASH.to_string(),
                actual: self.constitutional_hash.clone(),
            });
        }
        Ok(())
    }
    
    fn constitutional_hash(&self) -> &str {
        &self.constitutional_hash
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_working_memory() {
        let mut memory = WorkingMemory::new();
        memory.add_fact("test", "value");
        memory.add_rule("test-rule");
        memory.set_confidence("test", 0.8);
        
        assert!(memory.is_constitutionally_compliant());
        assert_eq!(memory.overall_confidence(), 0.8);
    }

    #[test]
    fn test_governance_query() {
        let query = GovernanceQuery::new("Researcher", "AnonymizedAggregate")
            .with_context("department", "AI Research");
        
        assert!(query.is_constitutionally_compliant());
        assert_eq!(query.actor_role, "Researcher");
    }

    #[test]
    fn test_policy_proposal() {
        let proposal = PolicyProposal::new(
            1,
            "Test Policy",
            "A test policy proposal",
            "Policy text here",
            3600, // 1 hour voting period
        );
        
        assert!(proposal.is_constitutionally_compliant());
        assert!(proposal.is_active());
        assert_eq!(proposal.vote_ratio(), 0.0);
    }
}
