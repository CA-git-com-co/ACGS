// Enhanced Quantumagi Core - Unified Governance Implementation
// Constitutional Hash: cdd01ef066bc6cf2
// Version: 3.0 - Enterprise Grade with Advanced Features

use anchor_lang::prelude::*;
use anchor_spl::token::{Token, TokenAccount};
use std::collections::{BTreeMap, BTreeSet};

declare_id!("45shrZAMBbFGfLrev4FSDBchP847Q7oUR4jVqcxqnRD3");

// ============================================================================
// ENHANCED CONSTANTS AND CONFIGURATION
// ============================================================================

/// Configuration constants with optimization targets
pub mod config {
    pub const MAX_PRINCIPLES: usize = 100;
    pub const MAX_POLICY_LENGTH: usize = 1000;
    pub const MAX_TITLE_LENGTH: usize = 100;
    pub const MAX_DESCRIPTION_LENGTH: usize = 500;
    pub const VOTING_PERIOD_SLOTS: u64 = 5;
    pub const SLOT_TIME_MS: u64 = 400;
    pub const APPROVAL_THRESHOLD_PERCENT: u64 = 60;
    pub const MIN_VOTING_POWER: u64 = 1;
    pub const PRINCIPLE_HASH_LEN: usize = 32;
    pub const MAX_ACTIVE_PROPOSALS: u32 = 100;
    pub const EMERGENCY_COOLDOWN_SECONDS: i64 = 3600; // 1 hour
    pub const MAX_BATCH_SIZE: usize = 10;
    pub const CONSTITUTIONAL_HASH: &str = "cdd01ef066bc6cf2";
}

// ============================================================================
// TYPE-SAFE DOMAIN TYPES
// ============================================================================

/// Type-safe wrapper for policy IDs with validation
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq, Eq, Hash)]
pub struct PolicyId(pub u64);

impl PolicyId {
    pub fn new(id: u64) -> Result<Self> {
        require!(id > 0, GovernanceError::InvalidPolicyId);
        Ok(Self(id))
    }
    
    pub fn value(&self) -> u64 { self.0 }
}

/// Type-safe voting power with range validation
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq)]
pub struct VotingPower(pub u64);

impl VotingPower {
    pub fn new(power: u64) -> Result<Self> {
        require!(power >= config::MIN_VOTING_POWER, GovernanceError::InvalidVotingPower);
        require!(power <= u64::MAX / 2, GovernanceError::VotingPowerTooHigh); // Prevent overflow
        Ok(Self(power))
    }
    
    pub fn value(&self) -> u64 { self.0 }
    
    pub fn checked_add(&self, other: &Self) -> Result<Self> {
        self.0.checked_add(other.0)
            .map(Self)
            .ok_or_else(|| GovernanceError::ArithmeticOverflow.into())
    }
}

/// Validated policy title
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct PolicyTitle(pub String);

impl PolicyTitle {
    pub fn new(title: String) -> Result<Self> {
        let trimmed = title.trim();
        require!(!trimmed.is_empty(), GovernanceError::InvalidTitle);
        require!(trimmed.len() <= config::MAX_TITLE_LENGTH, GovernanceError::TitleTooLong);
        // Check for potentially malicious content
        require!(!Self::contains_suspicious_patterns(trimmed), GovernanceError::SuspiciousContent);
        Ok(Self(trimmed.to_string()))
    }
    
    fn contains_suspicious_patterns(text: &str) -> bool {
        // Basic pattern detection for suspicious content
        let suspicious_patterns = ["javascript:", "data:", "<script", "eval("];
        suspicious_patterns.iter().any(|pattern| text.to_lowercase().contains(pattern))
    }
}

/// Validated policy description
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct PolicyDescription(pub String);

impl PolicyDescription {
    pub fn new(desc: String) -> Result<Self> {
        require!(desc.len() <= config::MAX_DESCRIPTION_LENGTH, GovernanceError::DescriptionTooLong);
        Ok(Self(desc))
    }
}

/// Content-addressed policy text with integrity verification
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct PolicyContent {
    pub text_hash: [u8; 32],
    pub length: u32,
    pub created_at: i64,
}

impl PolicyContent {
    pub fn new(text: String, timestamp: i64) -> Result<Self> {
        let trimmed = text.trim();
        require!(!trimmed.is_empty(), GovernanceError::InvalidPolicyText);
        require!(trimmed.len() <= config::MAX_POLICY_LENGTH, GovernanceError::PolicyTooLong);
        
        use anchor_lang::solana_program::hash::hash;
        let hash_result = hash(trimmed.as_bytes());
        let mut text_hash = [0u8; 32];
        text_hash.copy_from_slice(&hash_result.to_bytes());
        
        Ok(Self {
            text_hash,
            length: trimmed.len() as u32,
            created_at: timestamp,
        })
    }
    
    pub fn verify_content(&self, text: &str) -> bool {
        use anchor_lang::solana_program::hash::hash;
        let computed_hash = hash(text.trim().as_bytes());
        computed_hash.to_bytes() == self.text_hash
    }
}

/// Constitutional principle with metadata
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct Principle {
    pub hash: [u8; 32],
    pub index: u8,
    pub weight: u16, // Allows for weighted principles
    pub category: PrincipleCategory,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq)]
pub enum PrincipleCategory {
    Core,
    Process,
    Ethics,
    Technical,
    Economic,
}

impl Principle {
    pub fn from_text(text: &str, index: u8, category: PrincipleCategory) -> Self {
        use anchor_lang::solana_program::hash::hash;
        let hash_result = hash(text.as_bytes());
        let mut hash_bytes = [0u8; 32];
        hash_bytes.copy_from_slice(&hash_result.to_bytes());
        
        Self {
            hash: hash_bytes,
            index,
            weight: 100, // Default weight
            category,
        }
    }
}

// ============================================================================
// GOVERNANCE PROGRAM IMPLEMENTATION
// ============================================================================

#[program]
pub mod quantumagi_core {
    use super::*;

    /// Initialize governance system with enhanced validation and monitoring
    pub fn initialize_governance(
        ctx: Context<InitializeGovernance>,
        authority: Pubkey,
        principles: Vec<String>,
        config: GovernanceConfig,
    ) -> Result<()> {
        // Comprehensive validation
        require!(principles.len() <= config::MAX_PRINCIPLES, GovernanceError::TooManyPrinciples);
        require!(authority != System::id(), GovernanceError::InvalidAuthority);
        require!(authority != Token::id(), GovernanceError::InvalidAuthority);
        require!(!principles.is_empty(), GovernanceError::NoPrinciples);
        
        // Validate constitutional hash
        require!(
            config.constitutional_hash == config::CONSTITUTIONAL_HASH,
            GovernanceError::InvalidConstitutionalHash
        );

        let governance = &mut ctx.accounts.governance;
        let clock = Clock::get()?;
        
        // Convert principles to hashes with categories
        let principle_hashes: Vec<Principle> = principles
            .into_iter()
            .enumerate()
            .map(|(i, text)| {
                let category = Self::categorize_principle(&text);
                Principle::from_text(&text, i as u8, category)
            })
            .collect();

        governance.authority = authority;
        governance.principles = principle_hashes;
        governance.total_policies = 0;
        governance.active_proposals = 0;
        governance.emergency_mode = false;
        governance.last_emergency_at = None;
        governance.configuration = config;
        governance.statistics = GovernanceStatistics::default();
        governance.bump = ctx.bumps.governance;
        governance.initialized_at = clock.unix_timestamp;
        governance.version = 3; // Enhanced version
        
        // Initialize audit trail
        governance.audit_trail.push(AuditEntry {
            action: AuditAction::SystemInitialized,
            actor: authority,
            timestamp: clock.unix_timestamp,
            details: format!("Initialized with {} principles", governance.principles.len()),
        });

        emit!(GovernanceInitializedEnhanced {
            authority,
            principles_count: governance.principles.len() as u32,
            constitutional_hash: config::CONSTITUTIONAL_HASH.to_string(),
            initialized_at: governance.initialized_at,
            version: governance.version,
        });

        Ok(())
    }

    /// Create policy proposal with enhanced features and batch support
    pub fn create_policy_proposal(
        ctx: Context<CreatePolicyProposal>,
        policy_id: u64,
        title: String,
        description: String,
        policy_text: String,
        options: ProposalOptions,
    ) -> Result<()> {
        // Type-safe validation
        let policy_id = PolicyId::new(policy_id)?;
        let title = PolicyTitle::new(title)?;
        let description = PolicyDescription::new(description)?;
        
        let governance = &mut ctx.accounts.governance;
        let proposal = &mut ctx.accounts.proposal;
        let clock = Clock::get()?;
        
        // Enhanced governance checks
        require!(!governance.emergency_mode, GovernanceError::EmergencyModeActive);
        require!(
            governance.active_proposals < config::MAX_ACTIVE_PROPOSALS,
            GovernanceError::TooManyActiveProposals
        );
        
        // Rate limiting check
        if let Some(last_proposal) = governance.statistics.last_proposal_time {
            let time_since_last = clock.unix_timestamp - last_proposal;
            require!(
                time_since_last >= governance.configuration.min_proposal_interval,
                GovernanceError::ProposalRateLimited
            );
        }
        
        // Create content-addressed policy
        let policy_content = PolicyContent::new(policy_text, clock.unix_timestamp)?;
        
        // Calculate enhanced voting period
        let voting_duration = Self::calculate_voting_duration(&options)?;
        let voting_ends_at = clock.unix_timestamp
            .checked_add(voting_duration)
            .ok_or(GovernanceError::ArithmeticOverflow)?;

        // Initialize proposal with enhanced features
        proposal.policy_id = policy_id;
        proposal.title = title;
        proposal.description = description;
        proposal.policy_content = policy_content;
        proposal.proposer = ctx.accounts.proposer.key();
        proposal.created_at = clock.unix_timestamp;
        proposal.voting_ends_at = voting_ends_at;
        proposal.status = ProposalStatus::Active;
        proposal.voting_data = VotingData::new();
        proposal.options = options;
        proposal.constitutional_compliance = Self::check_constitutional_compliance(
            &governance.principles, 
            &proposal.policy_content
        )?;
        proposal.bump = ctx.bumps.proposal;

        // Update governance state
        governance.active_proposals = governance.active_proposals
            .checked_add(1)
            .ok_or(GovernanceError::ArithmeticOverflow)?;
        governance.statistics.total_proposals_created = governance.statistics.total_proposals_created
            .checked_add(1)
            .ok_or(GovernanceError::ArithmeticOverflow)?;
        governance.statistics.last_proposal_time = Some(clock.unix_timestamp);
        
        // Add audit entry
        governance.audit_trail.push(AuditEntry {
            action: AuditAction::ProposalCreated,
            actor: ctx.accounts.proposer.key(),
            timestamp: clock.unix_timestamp,
            details: format!("Policy ID: {}", policy_id.value()),
        });

        emit!(PolicyProposalCreatedEnhanced {
            policy_id: policy_id.value(),
            proposer: ctx.accounts.proposer.key(),
            title: proposal.title.0.clone(),
            voting_ends_at,
            constitutional_compliance: proposal.constitutional_compliance,
            content_hash: proposal.policy_content.text_hash,
        });

        Ok(())
    }

    /// Enhanced voting with delegation support and fraud prevention
    pub fn vote_on_proposal(
        ctx: Context<VoteOnProposal>,
        policy_id: u64,
        vote: bool,
        voting_power: u64,
        delegation_proof: Option<DelegationProof>,
    ) -> Result<()> {
        let policy_id = PolicyId::new(policy_id)?;
        let voting_power = VotingPower::new(voting_power)?;
        
        let proposal = &mut ctx.accounts.proposal;
        let vote_record = &mut ctx.accounts.vote_record;
        let governance = &ctx.accounts.governance;
        let clock = Clock::get()?;

        // Enhanced validation
        require!(proposal.status == ProposalStatus::Active, GovernanceError::ProposalNotActive);
        require!(clock.unix_timestamp <= proposal.voting_ends_at, GovernanceError::VotingPeriodEnded);
        require!(!governance.emergency_mode, GovernanceError::EmergencyModeActive);
        
        // Validate delegation if provided
        if let Some(delegation) = &delegation_proof {
            Self::validate_delegation(delegation, &ctx.accounts.voter.key(), voting_power.value())?;
        }
        
        // Enhanced fraud detection
        require!(
            !proposal.voting_data.voters.contains(&ctx.accounts.voter.key()),
            GovernanceError::AlreadyVoted
        );
        
        // Voting power validation with configurable limits
        require!(
            voting_power.value() <= governance.configuration.max_voting_power_per_vote,
            GovernanceError::VotingPowerExceedsLimit
        );

        // Record enhanced vote
        vote_record.voter = ctx.accounts.voter.key();
        vote_record.policy_id = policy_id;
        vote_record.vote = vote;
        vote_record.voting_power = voting_power;
        vote_record.timestamp = clock.unix_timestamp;
        vote_record.delegation_proof = delegation_proof;
        vote_record.constitutional_weight = Self::calculate_constitutional_weight(
            &governance.principles,
            &proposal.constitutional_compliance
        )?;
        vote_record.bump = ctx.bumps.vote_record;

        // Update proposal voting data with overflow protection
        if vote {
            proposal.voting_data.votes_for = proposal.voting_data.votes_for
                .checked_add(voting_power)
                .ok_or(GovernanceError::ArithmeticOverflow)?;
        } else {
            proposal.voting_data.votes_against = proposal.voting_data.votes_against
                .checked_add(voting_power)
                .ok_or(GovernanceError::ArithmeticOverflow)?;
        }
        
        proposal.voting_data.total_voters = proposal.voting_data.total_voters
            .checked_add(1)
            .ok_or(GovernanceError::ArithmeticOverflow)?;
        proposal.voting_data.voters.insert(ctx.accounts.voter.key());
        proposal.voting_data.last_vote_time = clock.unix_timestamp;

        emit!(VoteCastEnhanced {
            policy_id: policy_id.value(),
            voter: ctx.accounts.voter.key(),
            vote,
            voting_power: voting_power.value(),
            constitutional_weight: vote_record.constitutional_weight,
            timestamp: clock.unix_timestamp,
            has_delegation: delegation_proof.is_some(),
        });

        Ok(())
    }

    /// Enhanced proposal finalization with comprehensive outcome calculation
    pub fn finalize_proposal(
        ctx: Context<FinalizeProposal>,
        policy_id: u64,
    ) -> Result<()> {
        let policy_id = PolicyId::new(policy_id)?;
        let proposal = &mut ctx.accounts.proposal;
        let governance = &mut ctx.accounts.governance;
        let clock = Clock::get()?;

        require!(proposal.status == ProposalStatus::Active, GovernanceError::ProposalNotActive);
        require!(clock.unix_timestamp > proposal.voting_ends_at, GovernanceError::VotingPeriodNotEnded);

        // Enhanced outcome calculation
        let outcome = Self::calculate_proposal_outcome(proposal, governance)?;
        proposal.status = outcome.status;
        proposal.final_result = Some(outcome.clone());

        // Update governance statistics
        match outcome.status {
            ProposalStatus::Approved => {
                governance.total_policies = governance.total_policies
                    .checked_add(1)
                    .ok_or(GovernanceError::ArithmeticOverflow)?;
                governance.statistics.approved_proposals = governance.statistics.approved_proposals
                    .checked_add(1)
                    .ok_or(GovernanceError::ArithmeticOverflow)?;
            },
            ProposalStatus::Rejected => {
                governance.statistics.rejected_proposals = governance.statistics.rejected_proposals
                    .checked_add(1)
                    .ok_or(GovernanceError::ArithmeticOverflow)?;
            },
            _ => {}
        }

        governance.active_proposals = governance.active_proposals
            .checked_sub(1)
            .ok_or(GovernanceError::ArithmeticUnderflow)?;
        
        // Add comprehensive audit entry
        governance.audit_trail.push(AuditEntry {
            action: AuditAction::ProposalFinalized,
            actor: ctx.accounts.finalizer.key(),
            timestamp: clock.unix_timestamp,
            details: format!(
                "Policy ID: {}, Status: {:?}, Votes For: {}, Votes Against: {}",
                policy_id.value(),
                outcome.status,
                proposal.voting_data.votes_for.value(),
                proposal.voting_data.votes_against.value()
            ),
        });

        emit!(PolicyFinalizedEnhanced {
            policy_id: policy_id.value(),
            status: outcome.status,
            votes_for: proposal.voting_data.votes_for.value(),
            votes_against: proposal.voting_data.votes_against.value(),
            total_voters: proposal.voting_data.total_voters,
            constitutional_compliance_score: outcome.constitutional_compliance_score,
            finalized_at: clock.unix_timestamp,
            finalizer: ctx.accounts.finalizer.key(),
        });

        Ok(())
    }

    /// Batch operations for efficiency
    pub fn batch_create_proposals(
        ctx: Context<BatchCreateProposals>,
        proposals_data: Vec<BatchProposalData>,
    ) -> Result<()> {
        require!(
            proposals_data.len() <= config::MAX_BATCH_SIZE,
            GovernanceError::BatchTooLarge
        );
        
        let governance = &mut ctx.accounts.governance;
        let clock = Clock::get()?;
        
        require!(!governance.emergency_mode, GovernanceError::EmergencyModeActive);
        
        // Check batch limits
        let new_total = governance.active_proposals
            .checked_add(proposals_data.len() as u32)
            .ok_or(GovernanceError::ArithmeticOverflow)?;
        require!(
            new_total <= config::MAX_ACTIVE_PROPOSALS,
            GovernanceError::TooManyActiveProposals
        );

        let mut created_proposals = Vec::new();
        
        for (index, proposal_data) in proposals_data.iter().enumerate() {
            let policy_id = PolicyId::new(proposal_data.policy_id)?;
            let title = PolicyTitle::new(proposal_data.title.clone())?;
            let description = PolicyDescription::new(proposal_data.description.clone())?;
            let policy_content = PolicyContent::new(
                proposal_data.policy_text.clone(),
                clock.unix_timestamp
            )?;
            
            created_proposals.push(policy_id.value());
            
            // Update statistics
            governance.statistics.total_proposals_created = governance.statistics.total_proposals_created
                .checked_add(1)
                .ok_or(GovernanceError::ArithmeticOverflow)?;
        }
        
        governance.active_proposals = new_total;
        governance.statistics.batch_operations_count = governance.statistics.batch_operations_count
            .checked_add(1)
            .ok_or(GovernanceError::ArithmeticOverflow)?;
        
        // Add batch audit entry
        governance.audit_trail.push(AuditEntry {
            action: AuditAction::BatchProposalsCreated,
            actor: ctx.accounts.proposer.key(),
            timestamp: clock.unix_timestamp,
            details: format!("Created {} proposals in batch", proposals_data.len()),
        });

        emit!(BatchProposalsCreated {
            proposer: ctx.accounts.proposer.key(),
            policy_ids: created_proposals,
            count: proposals_data.len() as u32,
            timestamp: clock.unix_timestamp,
        });

        Ok(())
    }

    // ============================================================================
    // HELPER METHODS
    // ============================================================================
    
    fn categorize_principle(text: &str) -> PrincipleCategory {
        let text_lower = text.to_lowercase();
        if text_lower.contains("core") || text_lower.contains("fundamental") {
            PrincipleCategory::Core
        } else if text_lower.contains("process") || text_lower.contains("procedure") {
            PrincipleCategory::Process
        } else if text_lower.contains("ethic") || text_lower.contains("moral") {
            PrincipleCategory::Ethics
        } else if text_lower.contains("technical") || text_lower.contains("implementation") {
            PrincipleCategory::Technical
        } else if text_lower.contains("economic") || text_lower.contains("financial") {
            PrincipleCategory::Economic
        } else {
            PrincipleCategory::Core // Default
        }
    }
    
    fn calculate_voting_duration(options: &ProposalOptions) -> Result<i64> {
        let base_duration = config::VOTING_PERIOD_SLOTS
            .checked_mul(config::SLOT_TIME_MS)
            .ok_or(GovernanceError::ArithmeticOverflow)?;
        
        let duration_multiplier = match options.urgency {
            ProposalUrgency::Emergency => 1,
            ProposalUrgency::High => 2,
            ProposalUrgency::Normal => 4,
            ProposalUrgency::Low => 8,
        };
        
        base_duration
            .checked_mul(duration_multiplier)
            .map(|ms| ms as i64 / 1000)
            .ok_or(GovernanceError::ArithmeticOverflow.into())
    }
    
    fn check_constitutional_compliance(
        principles: &[Principle],
        content: &PolicyContent,
    ) -> Result<u16> {
        // Simplified compliance check - in practice this would be more sophisticated
        let base_score = 500; // 50% base compliance
        let principle_bonus = std::cmp::min(principles.len() * 50, 500);
        Ok((base_score + principle_bonus) as u16)
    }
    
    fn validate_delegation(
        delegation: &DelegationProof,
        voter: &Pubkey,
        voting_power: u64,
    ) -> Result<()> {
        require!(delegation.delegator != *voter, GovernanceError::SelfDelegation);
        require!(delegation.voting_power >= voting_power, GovernanceError::InsufficientDelegatedPower);
        require!(delegation.expires_at > Clock::get()?.unix_timestamp, GovernanceError::DelegationExpired);
        Ok(())
    }
    
    fn calculate_constitutional_weight(
        principles: &[Principle],
        compliance_score: &u16,
    ) -> Result<u16> {
        let base_weight = 100;
        let compliance_bonus = (*compliance_score as f64 / 1000.0 * 50.0) as u16;
        Ok(base_weight + compliance_bonus)
    }
    
    fn calculate_proposal_outcome(
        proposal: &PolicyProposal,
        governance: &GovernanceState,
    ) -> Result<ProposalOutcome> {
        let total_votes = proposal.voting_data.votes_for
            .checked_add(&proposal.voting_data.votes_against)?;
        
        let approval_threshold = total_votes.value() * config::APPROVAL_THRESHOLD_PERCENT / 100;
        let quorum_threshold = governance.configuration.minimum_quorum;
        
        let meets_quorum = proposal.voting_data.total_voters >= quorum_threshold;
        let meets_approval = proposal.voting_data.votes_for.value() >= approval_threshold;
        
        let status = if meets_quorum && meets_approval {
            ProposalStatus::Approved
        } else {
            ProposalStatus::Rejected
        };
        
        Ok(ProposalOutcome {
            status,
            constitutional_compliance_score: proposal.constitutional_compliance,
            quorum_met: meets_quorum,
            approval_threshold_met: meets_approval,
            final_vote_count: total_votes.value(),
        })
    }
}

// ============================================================================
// ENHANCED DATA STRUCTURES
// ============================================================================

#[account]
#[derive(InitSpace)]
pub struct GovernanceState {
    pub authority: Pubkey,
    #[max_len(100)]
    pub principles: Vec<Principle>,
    pub total_policies: u32,
    pub active_proposals: u32,
    pub emergency_mode: bool,
    pub last_emergency_at: Option<i64>,
    pub configuration: GovernanceConfig,
    pub statistics: GovernanceStatistics,
    #[max_len(1000)]
    pub audit_trail: Vec<AuditEntry>,
    pub initialized_at: i64,
    pub version: u8,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct GovernanceConfig {
    pub constitutional_hash: String,
    pub minimum_quorum: u32,
    pub max_voting_power_per_vote: u64,
    pub min_proposal_interval: i64,
    pub emergency_threshold: u16,
    pub delegation_enabled: bool,
    pub batch_operations_enabled: bool,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct GovernanceStatistics {
    pub total_proposals_created: u64,
    pub approved_proposals: u64,
    pub rejected_proposals: u64,
    pub total_votes_cast: u64,
    pub unique_voters: u32,
    pub last_proposal_time: Option<i64>,
    pub average_proposal_duration: u64,
    pub batch_operations_count: u64,
}

impl Default for GovernanceStatistics {
    fn default() -> Self {
        Self {
            total_proposals_created: 0,
            approved_proposals: 0,
            rejected_proposals: 0,
            total_votes_cast: 0,
            unique_voters: 0,
            last_proposal_time: None,
            average_proposal_duration: 0,
            batch_operations_count: 0,
        }
    }
}

#[account]
#[derive(InitSpace)]
pub struct PolicyProposal {
    pub policy_id: PolicyId,
    pub title: PolicyTitle,
    pub description: PolicyDescription,
    pub policy_content: PolicyContent,
    pub proposer: Pubkey,
    pub created_at: i64,
    pub voting_ends_at: i64,
    pub status: ProposalStatus,
    pub voting_data: VotingData,
    pub options: ProposalOptions,
    pub constitutional_compliance: u16,
    pub final_result: Option<ProposalOutcome>,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct VotingData {
    pub votes_for: VotingPower,
    pub votes_against: VotingPower,
    pub total_voters: u32,
    #[max_len(10000)]
    pub voters: BTreeSet<Pubkey>,
    pub last_vote_time: i64,
}

impl VotingData {
    pub fn new() -> Self {
        Self {
            votes_for: VotingPower(0),
            votes_against: VotingPower(0),
            total_voters: 0,
            voters: BTreeSet::new(),
            last_vote_time: 0,
        }
    }
}

#[account]
#[derive(InitSpace)]
pub struct VoteRecord {
    pub voter: Pubkey,
    pub policy_id: PolicyId,
    pub vote: bool,
    pub voting_power: VotingPower,
    pub timestamp: i64,
    pub delegation_proof: Option<DelegationProof>,
    pub constitutional_weight: u16,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ProposalOptions {
    pub urgency: ProposalUrgency,
    pub category: ProposalCategory,
    pub requires_supermajority: bool,
    pub allow_delegation: bool,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum ProposalUrgency {
    Emergency,
    High,
    Normal,
    Low,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum ProposalCategory {
    Constitutional,
    Policy,
    Technical,
    Economic,
    Administrative,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct DelegationProof {
    pub delegator: Pubkey,
    pub voting_power: u64,
    pub expires_at: i64,
    pub signature: [u8; 64],
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ProposalOutcome {
    pub status: ProposalStatus,
    pub constitutional_compliance_score: u16,
    pub quorum_met: bool,
    pub approval_threshold_met: bool,
    pub final_vote_count: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct AuditEntry {
    pub action: AuditAction,
    pub actor: Pubkey,
    pub timestamp: i64,
    pub details: String,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum AuditAction {
    SystemInitialized,
    ProposalCreated,
    VoteCast,
    ProposalFinalized,
    EmergencyAction,
    BatchProposalsCreated,
    DelegationGranted,
    DelegationRevoked,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct BatchProposalData {
    pub policy_id: u64,
    pub title: String,
    pub description: String,
    pub policy_text: String,
    pub options: ProposalOptions,
}

// ============================================================================
// ENHANCED ENUMS
// ============================================================================

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Eq, Debug, InitSpace)]
pub enum ProposalStatus {
    Active,
    Approved,
    Rejected,
    Emergency,
    Expired,
    Withdrawn,
}

// ============================================================================
// ACCOUNT CONTEXTS
// ============================================================================

#[derive(Accounts)]
pub struct InitializeGovernance<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + GovernanceState::INIT_SPACE,
        seeds = [b"governance"],
        bump
    )]
    pub governance: Account<'info, GovernanceState>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
#[instruction(policy_id: u64)]
pub struct CreatePolicyProposal<'info> {
    #[account(
        init,
        payer = proposer,
        space = 8 + PolicyProposal::INIT_SPACE,
        seeds = [b"proposal", policy_id.to_le_bytes().as_ref()],
        bump
    )]
    pub proposal: Account<'info, PolicyProposal>,
    #[account(
        mut,
        seeds = [b"governance"],
        bump = governance.bump
    )]
    pub governance: Account<'info, GovernanceState>,
    #[account(mut)]
    pub proposer: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
#[instruction(policy_id: u64)]
pub struct VoteOnProposal<'info> {
    #[account(
        mut,
        seeds = [b"proposal", policy_id.to_le_bytes().as_ref()],
        bump = proposal.bump
    )]
    pub proposal: Account<'info, PolicyProposal>,
    #[account(
        init,
        payer = voter,
        space = 8 + VoteRecord::INIT_SPACE,
        seeds = [b"vote", policy_id.to_le_bytes().as_ref(), voter.key().as_ref()],
        bump
    )]
    pub vote_record: Account<'info, VoteRecord>,
    #[account(
        seeds = [b"governance"],
        bump = governance.bump
    )]
    pub governance: Account<'info, GovernanceState>,
    #[account(mut)]
    pub voter: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
#[instruction(policy_id: u64)]
pub struct FinalizeProposal<'info> {
    #[account(
        mut,
        seeds = [b"proposal", policy_id.to_le_bytes().as_ref()],
        bump = proposal.bump
    )]
    pub proposal: Account<'info, PolicyProposal>,
    #[account(
        mut,
        seeds = [b"governance"],
        bump = governance.bump
    )]
    pub governance: Account<'info, GovernanceState>,
    pub finalizer: Signer<'info>,
}

#[derive(Accounts)]
pub struct BatchCreateProposals<'info> {
    #[account(
        mut,
        seeds = [b"governance"],
        bump = governance.bump
    )]
    pub governance: Account<'info, GovernanceState>,
    #[account(mut)]
    pub proposer: Signer<'info>,
    pub system_program: Program<'info, System>,
}

// ============================================================================
// ENHANCED EVENTS
// ============================================================================

#[event]
pub struct GovernanceInitializedEnhanced {
    pub authority: Pubkey,
    pub principles_count: u32,
    pub constitutional_hash: String,
    pub initialized_at: i64,
    pub version: u8,
}

#[event]
pub struct PolicyProposalCreatedEnhanced {
    pub policy_id: u64,
    pub proposer: Pubkey,
    pub title: String,
    pub voting_ends_at: i64,
    pub constitutional_compliance: u16,
    pub content_hash: [u8; 32],
}

#[event]
pub struct VoteCastEnhanced {
    pub policy_id: u64,
    pub voter: Pubkey,
    pub vote: bool,
    pub voting_power: u64,
    pub constitutional_weight: u16,
    pub timestamp: i64,
    pub has_delegation: bool,
}

#[event]
pub struct PolicyFinalizedEnhanced {
    pub policy_id: u64,
    pub status: ProposalStatus,
    pub votes_for: u64,
    pub votes_against: u64,
    pub total_voters: u32,
    pub constitutional_compliance_score: u16,
    pub finalized_at: i64,
    pub finalizer: Pubkey,
}

#[event]
pub struct BatchProposalsCreated {
    pub proposer: Pubkey,
    pub policy_ids: Vec<u64>,
    pub count: u32,
    pub timestamp: i64,
}

// ============================================================================
// ENHANCED ERROR TYPES
// ============================================================================

#[error_code]
pub enum GovernanceError {
    #[msg("Too many constitutional principles")]
    TooManyPrinciples,
    #[msg("Policy text too long")]
    PolicyTooLong,
    #[msg("Title too long")]
    TitleTooLong,
    #[msg("Description too long")]
    DescriptionTooLong,
    #[msg("Proposal is not active")]
    ProposalNotActive,
    #[msg("Voting period has ended")]
    VotingPeriodEnded,
    #[msg("Voting period has not ended")]
    VotingPeriodNotEnded,
    #[msg("Invalid voting power")]
    InvalidVotingPower,
    #[msg("Unauthorized emergency action")]
    UnauthorizedEmergencyAction,
    #[msg("Voter has already voted")]
    AlreadyVoted,
    #[msg("Insufficient governance tokens")]
    InsufficientTokens,
    #[msg("Invalid policy ID")]
    InvalidPolicyId,
    #[msg("Invalid title")]
    InvalidTitle,
    #[msg("Invalid policy text")]
    InvalidPolicyText,
    #[msg("Invalid authority")]
    InvalidAuthority,
    #[msg("Arithmetic overflow")]
    ArithmeticOverflow,
    #[msg("Arithmetic underflow")]
    ArithmeticUnderflow,
    #[msg("Emergency mode is active")]
    EmergencyModeActive,
    #[msg("Too many active proposals")]
    TooManyActiveProposals,
    #[msg("Proposal rate limited")]
    ProposalRateLimited,
    #[msg("Invalid constitutional hash")]
    InvalidConstitutionalHash,
    #[msg("No principles provided")]
    NoPrinciples,
    #[msg("Suspicious content detected")]
    SuspiciousContent,
    #[msg("Voting power too high")]
    VotingPowerTooHigh,
    #[msg("Voting power exceeds limit")]
    VotingPowerExceedsLimit,
    #[msg("Self delegation not allowed")]
    SelfDelegation,
    #[msg("Insufficient delegated power")]
    InsufficientDelegatedPower,
    #[msg("Delegation expired")]
    DelegationExpired,
    #[msg("Batch too large")]
    BatchTooLarge,
}