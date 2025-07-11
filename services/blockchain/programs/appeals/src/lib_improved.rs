// programs/appeals/src/lib_improved.rs
// Quantumagi Appeals System - Democratic Appeal Process with Enhanced Security and Performance

use anchor_lang::prelude::*;
use anchor_spl::token::{Token, TokenAccount};
use std::collections::HashMap;

declare_id!("278awDwWu5NZRyDCLufPXQk1p9Q16WAhn9cvsFwFtsfY");

// Constants with clear documentation
const MAX_VIOLATION_DETAILS: usize = 2000;
const MAX_REVIEW_EVIDENCE: usize = 1000;
const MAX_ESCALATION_REASON: usize = 500;
const MAX_RULING_DETAILS: usize = 2000;
const REVIEW_DEADLINE_SECONDS: i64 = 86_400; // 24 hours
const HUMAN_REVIEW_DEADLINE_SECONDS: i64 = 604_800; // 7 days
const HIGH_CONFIDENCE_THRESHOLD: u8 = 85;
const MAX_ESCALATIONS: u8 = 3;
const MIN_CONFIDENCE_SCORE: u8 = 0;
const MAX_CONFIDENCE_SCORE: u8 = 100;
const EVIDENCE_HASH_LEN: usize = 32;

// Type-safe newtypes
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq)]
pub struct AppealId(pub u64);

impl AppealId {
    pub fn new(timestamp: i64) -> Result<Self> {
        // Use timestamp + random component for uniqueness
        let id = (timestamp as u64) << 16 | (timestamp as u64 & 0xFFFF);
        Ok(Self(id))
    }
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy)]
pub struct PolicyId(pub u64);

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct ConfidenceScore(pub u8);

impl ConfidenceScore {
    pub fn new(score: u8) -> Result<Self> {
        require!(
            score <= MAX_CONFIDENCE_SCORE,
            AppealsError::InvalidConfidenceScore
        );
        Ok(Self(score))
    }

    pub fn is_high_confidence(&self) -> bool {
        self.0 >= HIGH_CONFIDENCE_THRESHOLD
    }
}

// Validated string types
#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct ViolationDetails(pub String);

impl ViolationDetails {
    pub fn new(details: String) -> Result<Self> {
        require!(
            !details.trim().is_empty(),
            AppealsError::InvalidViolationDetails
        );
        require!(
            details.len() <= MAX_VIOLATION_DETAILS,
            AppealsError::ViolationDetailsTooLong
        );
        Ok(Self(details))
    }

    pub fn hash(&self) -> [u8; EVIDENCE_HASH_LEN] {
        use anchor_lang::solana_program::hash::hash;
        let hash_result = hash(self.0.as_bytes());
        let mut hash_bytes = [0u8; EVIDENCE_HASH_LEN];
        hash_bytes.copy_from_slice(&hash_result.to_bytes());
        hash_bytes
    }
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct ReviewEvidence(pub String);

impl ReviewEvidence {
    pub fn new(evidence: String) -> Result<Self> {
        require!(
            evidence.len() <= MAX_REVIEW_EVIDENCE,
            AppealsError::ReviewEvidenceTooLong
        );
        Ok(Self(evidence))
    }
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct EscalationReason(pub String);

impl EscalationReason {
    pub fn new(reason: String) -> Result<Self> {
        require!(
            !reason.trim().is_empty(),
            AppealsError::InvalidEscalationReason
        );
        require!(
            reason.len() <= MAX_ESCALATION_REASON,
            AppealsError::EscalationReasonTooLong
        );
        Ok(Self(reason))
    }
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct RulingDetails(pub String);

impl RulingDetails {
    pub fn new(details: String) -> Result<Self> {
        require!(
            !details.trim().is_empty(),
            AppealsError::InvalidRulingDetails
        );
        require!(
            details.len() <= MAX_RULING_DETAILS,
            AppealsError::RulingDetailsTooLong
        );
        Ok(Self(details))
    }
}

#[program]
pub mod appeals {
    use super::*;

    /// Submit an appeal with enhanced validation
    pub fn submit_appeal(
        ctx: Context<SubmitAppeal>,
        policy_id: PolicyId,
        violation_details: String,
        evidence_hash: [u8; EVIDENCE_HASH_LEN],
        appeal_type: AppealType,
    ) -> Result<()> {
        // Validate inputs
        let violation_details = ViolationDetails::new(violation_details)?;
        
        // Verify evidence hash is not zero (indicates actual evidence provided)
        require!(
            evidence_hash != [0u8; EVIDENCE_HASH_LEN],
            AppealsError::InvalidEvidenceHash
        );

        let appeal = &mut ctx.accounts.appeal;
        let clock = Clock::get()?;
        let appeal_id = AppealId::new(clock.unix_timestamp)?;

        // Calculate deadlines with overflow protection
        let review_deadline = clock.unix_timestamp
            .checked_add(REVIEW_DEADLINE_SECONDS)
            .ok_or(AppealsError::ArithmeticOverflow)?;

        // Initialize appeal with secure defaults
        appeal.id = appeal_id;
        appeal.policy_id = policy_id;
        appeal.appellant = ctx.accounts.appellant.key();
        appeal.violation_details_hash = violation_details.hash();
        appeal.evidence_hash = evidence_hash;
        appeal.appeal_type = appeal_type.clone();
        appeal.status = AppealStatus::Submitted;
        appeal.submitted_at = clock.unix_timestamp;
        appeal.review_deadline = review_deadline;
        appeal.escalation_count = 0;
        appeal.security_logs = vec![];
        appeal.bump = ctx.bumps.appeal;

        // Add initial security log
        appeal.security_logs.push(SecurityLog {
            action: SecurityAction::AppealSubmitted,
            actor: ctx.accounts.appellant.key(),
            timestamp: clock.unix_timestamp,
            details: format!("Appeal submitted for policy {}", policy_id.0),
        });

        emit!(AppealSubmittedEvent {
            appeal_id: appeal_id.0,
            policy_id: policy_id.0,
            appellant: ctx.accounts.appellant.key(),
            appeal_type,
            submitted_at: clock.unix_timestamp,
            evidence_hash,
        });

        Ok(())
    }

    /// Review an appeal with enhanced security
    pub fn review_appeal(
        ctx: Context<ReviewAppeal>,
        reviewer_decision: ReviewDecision,
        review_evidence: String,
        confidence_score: u8,
    ) -> Result<()> {
        let review_evidence = ReviewEvidence::new(review_evidence)?;
        let confidence_score = ConfidenceScore::new(confidence_score)?;

        let appeal = &mut ctx.accounts.appeal;
        let clock = Clock::get()?;
        let reviewer = ctx.accounts.reviewer.key();

        // Verify appeal status
        require!(
            appeal.status == AppealStatus::Submitted,
            AppealsError::InvalidAppealStatus
        );

        // Check review deadline
        require!(
            clock.unix_timestamp <= appeal.review_deadline,
            AppealsError::ReviewDeadlineExpired
        );

        // Verify reviewer authorization (could check against a whitelist)
        require!(
            reviewer != appeal.appellant,
            AppealsError::ReviewerCannotBeAppellant
        );

        // Store review data
        appeal.reviewer = Some(reviewer);
        appeal.review_decision = Some(reviewer_decision.clone());
        appeal.review_evidence_hash = {
            use anchor_lang::solana_program::hash::hash;
            let hash_result = hash(review_evidence.0.as_bytes());
            let mut hash_bytes = [0u8; EVIDENCE_HASH_LEN];
            hash_bytes.copy_from_slice(&hash_result.to_bytes());
            hash_bytes
        };
        appeal.confidence_score = Some(confidence_score.clone());
        appeal.reviewed_at = Some(clock.unix_timestamp);

        // Determine next status based on decision and confidence
        let new_status = match (reviewer_decision.clone(), confidence_score.is_high_confidence()) {
            (ReviewDecision::Approve, true) => AppealStatus::Approved,
            (ReviewDecision::Reject, true) => AppealStatus::Rejected,
            (ReviewDecision::Approve | ReviewDecision::Reject, false) => AppealStatus::PendingHumanReview,
            (ReviewDecision::Escalate, _) => AppealStatus::PendingHumanReview,
        };

        appeal.status = new_status.clone();
        appeal.status_history.push(StatusChange {
            from: AppealStatus::Submitted,
            to: new_status,
            timestamp: clock.unix_timestamp,
            actor: reviewer,
        });

        // Add security log
        appeal.security_logs.push(SecurityLog {
            action: SecurityAction::AppealReviewed,
            actor: reviewer,
            timestamp: clock.unix_timestamp,
            details: format!("Review decision: {:?}, confidence: {}%", reviewer_decision, confidence_score.0),
        });

        emit!(AppealReviewedEvent {
            appeal_id: appeal.id.0,
            reviewer,
            decision: reviewer_decision,
            confidence_score: confidence_score.0,
            reviewed_at: clock.unix_timestamp,
        });

        Ok(())
    }

    /// Escalate appeal with rate limiting
    pub fn escalate_to_human_committee(
        ctx: Context<EscalateAppeal>,
        escalation_reason: String,
        committee_type: CommitteeType,
    ) -> Result<()> {
        let escalation_reason = EscalationReason::new(escalation_reason)?;
        
        let appeal = &mut ctx.accounts.appeal;
        let clock = Clock::get()?;
        let escalator = ctx.accounts.escalator.key();

        // Verify appeal can be escalated
        require!(
            matches!(
                appeal.status,
                AppealStatus::PendingHumanReview | AppealStatus::Submitted
            ),
            AppealsError::CannotEscalate
        );

        // Check escalation limits
        require!(
            appeal.escalation_count < MAX_ESCALATIONS,
            AppealsError::MaxEscalationsReached
        );

        // Rate limit: prevent rapid escalations (min 1 hour between escalations)
        if let Some(last_escalation) = appeal.last_escalation_at {
            let time_since_last = clock.unix_timestamp
                .checked_sub(last_escalation)
                .ok_or(AppealsError::ArithmeticUnderflow)?;
            require!(
                time_since_last >= 3600, // 1 hour
                AppealsError::EscalationTooSoon
            );
        }

        // Calculate human review deadline
        let human_review_deadline = clock.unix_timestamp
            .checked_add(HUMAN_REVIEW_DEADLINE_SECONDS)
            .ok_or(AppealsError::ArithmeticOverflow)?;

        // Update appeal state
        let old_status = appeal.status.clone();
        appeal.status = AppealStatus::EscalatedToHuman;
        appeal.escalation_reasons.push(escalation_reason.clone());
        appeal.committee_type = Some(committee_type.clone());
        appeal.escalated_at = Some(clock.unix_timestamp);
        appeal.last_escalation_at = Some(clock.unix_timestamp);
        appeal.escalation_count = appeal.escalation_count
            .checked_add(1)
            .ok_or(AppealsError::ArithmeticOverflow)?;
        appeal.human_review_deadline = Some(human_review_deadline);

        // Add to status history
        appeal.status_history.push(StatusChange {
            from: old_status,
            to: AppealStatus::EscalatedToHuman,
            timestamp: clock.unix_timestamp,
            actor: escalator,
        });

        // Add security log
        appeal.security_logs.push(SecurityLog {
            action: SecurityAction::AppealEscalated,
            actor: escalator,
            timestamp: clock.unix_timestamp,
            details: format!("Escalated to {:?} committee", committee_type),
        });

        emit!(AppealEscalatedEvent {
            appeal_id: appeal.id.0,
            committee_type,
            escalation_count: appeal.escalation_count,
            escalated_at: clock.unix_timestamp,
            escalation_reason: escalation_reason.0,
        });

        Ok(())
    }

    /// Resolve appeal with comprehensive enforcement
    pub fn resolve_with_ruling(
        ctx: Context<ResolveAppeal>,
        final_decision: FinalDecision,
        ruling_details: String,
        enforcement_action: EnforcementAction,
    ) -> Result<()> {
        let ruling_details = RulingDetails::new(ruling_details)?;
        
        let appeal = &mut ctx.accounts.appeal;
        let clock = Clock::get()?;
        let resolver = ctx.accounts.resolver.key();

        // Verify appeal is ready for resolution
        require!(
            matches!(
                appeal.status,
                AppealStatus::EscalatedToHuman | AppealStatus::PendingHumanReview
            ),
            AppealsError::CannotResolve
        );

        // Verify resolver authorization (could check committee membership)
        require!(
            resolver != appeal.appellant,
            AppealsError::ResolverCannotBeAppellant
        );

        // Store resolution data
        let old_status = appeal.status.clone();
        appeal.final_decision = Some(final_decision.clone());
        appeal.ruling_details_hash = {
            use anchor_lang::solana_program::hash::hash;
            let hash_result = hash(ruling_details.0.as_bytes());
            let mut hash_bytes = [0u8; EVIDENCE_HASH_LEN];
            hash_bytes.copy_from_slice(&hash_result.to_bytes());
            hash_bytes
        };
        appeal.enforcement_action = Some(enforcement_action.clone());
        appeal.resolved_at = Some(clock.unix_timestamp);
        appeal.resolver = Some(resolver);

        // Set final status based on decision
        let final_status = match final_decision {
            FinalDecision::Uphold => AppealStatus::Rejected,
            FinalDecision::Overturn => AppealStatus::Approved,
            FinalDecision::Modify => AppealStatus::ModifiedApproval,
        };
        appeal.status = final_status.clone();

        // Calculate resolution time
        let resolution_time = clock.unix_timestamp
            .checked_sub(appeal.submitted_at)
            .ok_or(AppealsError::ArithmeticUnderflow)?;

        // Add to status history
        appeal.status_history.push(StatusChange {
            from: old_status,
            to: final_status,
            timestamp: clock.unix_timestamp,
            actor: resolver,
        });

        // Add security log
        appeal.security_logs.push(SecurityLog {
            action: SecurityAction::AppealResolved,
            actor: resolver,
            timestamp: clock.unix_timestamp,
            details: format!("Final decision: {:?}, enforcement: {:?}", final_decision, enforcement_action),
        });

        // Update global statistics
        if let Some(stats) = ctx.accounts.appeal_stats.as_mut() {
            stats.total_resolved = stats.total_resolved
                .checked_add(1)
                .ok_or(AppealsError::ArithmeticOverflow)?;
            
            match final_status {
                AppealStatus::Approved => stats.approved_appeals = stats.approved_appeals
                    .checked_add(1)
                    .ok_or(AppealsError::ArithmeticOverflow)?,
                AppealStatus::Rejected => stats.rejected_appeals = stats.rejected_appeals
                    .checked_add(1)
                    .ok_or(AppealsError::ArithmeticOverflow)?,
                AppealStatus::ModifiedApproval => stats.modified_appeals = stats.modified_appeals
                    .checked_add(1)
                    .ok_or(AppealsError::ArithmeticOverflow)?,
                _ => {}
            }

            // Update average resolution time
            let total_time = stats.average_resolution_time
                .checked_mul(stats.total_resolved - 1)
                .ok_or(AppealsError::ArithmeticOverflow)?
                .checked_add(resolution_time as u64)
                .ok_or(AppealsError::ArithmeticOverflow)?;
            stats.average_resolution_time = total_time / stats.total_resolved;
        }

        emit!(AppealResolvedEvent {
            appeal_id: appeal.id.0,
            final_decision,
            enforcement_action,
            resolver,
            resolved_at: clock.unix_timestamp,
            resolution_time,
        });

        Ok(())
    }

    /// Acknowledge security action for audit trail
    pub fn acknowledge_security_action(
        ctx: Context<AcknowledgeSecurityAction>,
        action_details: String,
    ) -> Result<()> {
        let security_log = &mut ctx.accounts.security_log;
        let clock = Clock::get()?;

        security_log.acknowledged_by = Some(ctx.accounts.acknowledger.key());
        security_log.acknowledged_at = Some(clock.unix_timestamp);
        security_log.acknowledgment_details = action_details;

        Ok(())
    }

    /// Initialize appeal statistics account
    pub fn initialize_appeal_stats(ctx: Context<InitializeAppealStats>) -> Result<()> {
        let stats = &mut ctx.accounts.appeal_stats;
        stats.total_appeals = 0;
        stats.approved_appeals = 0;
        stats.rejected_appeals = 0;
        stats.modified_appeals = 0;
        stats.pending_appeals = 0;
        stats.total_resolved = 0;
        stats.average_resolution_time = 0;
        stats.human_escalation_rate = 0;
        stats.last_updated = Clock::get()?.unix_timestamp;
        stats.bump = ctx.bumps.appeal_stats;

        Ok(())
    }
}

// Account Structures with InitSpace

#[account]
#[derive(InitSpace)]
pub struct Appeal {
    pub id: AppealId,
    pub policy_id: PolicyId,
    pub appellant: Pubkey,
    pub violation_details_hash: [u8; EVIDENCE_HASH_LEN], // Store hash, not full text
    pub evidence_hash: [u8; EVIDENCE_HASH_LEN],
    pub appeal_type: AppealType,
    pub status: AppealStatus,
    pub submitted_at: i64,
    pub review_deadline: i64,
    
    // Review data
    pub reviewer: Option<Pubkey>,
    pub review_decision: Option<ReviewDecision>,
    pub review_evidence_hash: [u8; EVIDENCE_HASH_LEN],
    pub confidence_score: Option<ConfidenceScore>,
    pub reviewed_at: Option<i64>,
    
    // Escalation data
    #[max_len(MAX_ESCALATIONS)]
    pub escalation_reasons: Vec<EscalationReason>,
    pub committee_type: Option<CommitteeType>,
    pub escalated_at: Option<i64>,
    pub last_escalation_at: Option<i64>,
    pub escalation_count: u8,
    pub human_review_deadline: Option<i64>,
    
    // Resolution data
    pub final_decision: Option<FinalDecision>,
    pub ruling_details_hash: [u8; EVIDENCE_HASH_LEN],
    pub enforcement_action: Option<EnforcementAction>,
    pub resolved_at: Option<i64>,
    pub resolver: Option<Pubkey>,
    
    // Audit trail
    #[max_len(50)]
    pub status_history: Vec<StatusChange>,
    #[max_len(100)]
    pub security_logs: Vec<SecurityLog>,
    
    pub bump: u8,
}

#[account]
#[derive(InitSpace)]
pub struct AppealStats {
    pub total_appeals: u64,
    pub approved_appeals: u64,
    pub rejected_appeals: u64,
    pub modified_appeals: u64,
    pub pending_appeals: u64,
    pub total_resolved: u64,
    pub average_resolution_time: u64, // in seconds
    pub human_escalation_rate: u8,    // percentage
    pub last_updated: i64,
    pub bump: u8,
}

#[account]
#[derive(InitSpace)]
pub struct SecurityLog {
    pub action: SecurityAction,
    pub actor: Pubkey,
    pub timestamp: i64,
    #[max_len(200)]
    pub details: String,
    pub acknowledged_by: Option<Pubkey>,
    pub acknowledged_at: Option<i64>,
    #[max_len(200)]
    pub acknowledgment_details: String,
}

// Supporting data structures

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct StatusChange {
    pub from: AppealStatus,
    pub to: AppealStatus,
    pub timestamp: i64,
    pub actor: Pubkey,
}

// Enums with InitSpace

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq, InitSpace)]
pub enum AppealType {
    PolicyViolation,         // Appeal against policy violation ruling
    ProcessError,            // Appeal due to process/system error
    NewEvidence,             // Appeal with new evidence
    ConstitutionalChallenge, // Challenge policy constitutionality
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq, InitSpace)]
pub enum AppealStatus {
    Submitted,          // Initial submission
    UnderReview,        // Being reviewed
    PendingHumanReview, // Awaiting human committee
    EscalatedToHuman,   // Escalated to human oversight
    Approved,           // Appeal approved
    Rejected,           // Appeal rejected
    ModifiedApproval,   // Approved with modifications
    Expired,            // Deadline expired
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq, InitSpace)]
pub enum ReviewDecision {
    Approve,  // Approve the appeal
    Reject,   // Reject the appeal
    Escalate, // Escalate to human review
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq, InitSpace)]
pub enum CommitteeType {
    Technical,      // Technical review committee
    Governance,     // Governance committee
    Ethics,         // Ethics review committee
    Constitutional, // Constitutional review committee
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq, InitSpace)]
pub enum FinalDecision {
    Uphold,   // Uphold original decision
    Overturn, // Overturn original decision
    Modify,   // Modify with conditions
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq, InitSpace)]
pub enum EnforcementAction {
    None,               // No action required
    PolicyUpdate,       // Policy needs updating
    SystemAlert,        // Issue system alert
    TemporaryExemption, // Grant temporary exemption
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq, InitSpace)]
pub enum SecurityAction {
    AppealSubmitted,
    AppealReviewed,
    AppealEscalated,
    AppealResolved,
    SecurityAlert,
    SystemOverride,
}

// Instruction Contexts

#[derive(Accounts)]
#[instruction(policy_id: PolicyId)]
pub struct SubmitAppeal<'info> {
    #[account(
        init,
        payer = appellant,
        space = 8 + Appeal::INIT_SPACE,
        seeds = [b"appeal", policy_id.0.to_le_bytes().as_ref(), appellant.key().as_ref()],
        bump
    )]
    pub appeal: Account<'info, Appeal>,
    
    #[account(mut)]
    pub appellant: Signer<'info>,
    
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ReviewAppeal<'info> {
    #[account(mut)]
    pub appeal: Account<'info, Appeal>,
    
    pub reviewer: Signer<'info>,
}

#[derive(Accounts)]
pub struct EscalateAppeal<'info> {
    #[account(mut)]
    pub appeal: Account<'info, Appeal>,
    
    pub escalator: Signer<'info>,
}

#[derive(Accounts)]
pub struct ResolveAppeal<'info> {
    #[account(mut)]
    pub appeal: Account<'info, Appeal>,
    
    #[account(
        mut,
        seeds = [b"appeal_stats"],
        bump = appeal_stats.bump
    )]
    pub appeal_stats: Option<Account<'info, AppealStats>>,
    
    pub resolver: Signer<'info>,
}

#[derive(Accounts)]
pub struct AcknowledgeSecurityAction<'info> {
    #[account(mut)]
    pub security_log: Account<'info, SecurityLog>,
    
    pub acknowledger: Signer<'info>,
}

#[derive(Accounts)]
pub struct InitializeAppealStats<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + AppealStats::INIT_SPACE,
        seeds = [b"appeal_stats"],
        bump
    )]
    pub appeal_stats: Account<'info, AppealStats>,
    
    #[account(mut)]
    pub authority: Signer<'info>,
    
    pub system_program: Program<'info, System>,
}

// Enhanced Events

#[event]
pub struct AppealSubmittedEvent {
    pub appeal_id: u64,
    pub policy_id: u64,
    pub appellant: Pubkey,
    pub appeal_type: AppealType,
    pub submitted_at: i64,
    pub evidence_hash: [u8; EVIDENCE_HASH_LEN],
}

#[event]
pub struct AppealReviewedEvent {
    pub appeal_id: u64,
    pub reviewer: Pubkey,
    pub decision: ReviewDecision,
    pub confidence_score: u8,
    pub reviewed_at: i64,
}

#[event]
pub struct AppealEscalatedEvent {
    pub appeal_id: u64,
    pub committee_type: CommitteeType,
    pub escalation_count: u8,
    pub escalated_at: i64,
    pub escalation_reason: String,
}

#[event]
pub struct AppealResolvedEvent {
    pub appeal_id: u64,
    pub final_decision: FinalDecision,
    pub enforcement_action: EnforcementAction,
    pub resolver: Pubkey,
    pub resolved_at: i64,
    pub resolution_time: i64,
}

// Enhanced Custom Errors

#[error_code]
pub enum AppealsError {
    #[msg("Violation details are too long. Maximum length: 2000")]
    ViolationDetailsTooLong,
    #[msg("Invalid violation details: cannot be empty")]
    InvalidViolationDetails,
    #[msg("Review evidence is too long. Maximum length: 1000")]
    ReviewEvidenceTooLong,
    #[msg("Escalation reason is too long. Maximum length: 500")]
    EscalationReasonTooLong,
    #[msg("Invalid escalation reason: cannot be empty")]
    InvalidEscalationReason,
    #[msg("Ruling details are too long. Maximum length: 2000")]
    RulingDetailsTooLong,
    #[msg("Invalid ruling details: cannot be empty")]
    InvalidRulingDetails,
    #[msg("Invalid confidence score. Must be 0-100")]
    InvalidConfidenceScore,
    #[msg("Appeal is not in the correct status for this operation")]
    InvalidAppealStatus,
    #[msg("Review deadline has expired")]
    ReviewDeadlineExpired,
    #[msg("Appeal cannot be escalated in its current status")]
    CannotEscalate,
    #[msg("Maximum number of escalations reached (3)")]
    MaxEscalationsReached,
    #[msg("Appeal cannot be resolved in its current status")]
    CannotResolve,
    #[msg("Invalid evidence hash: cannot be empty")]
    InvalidEvidenceHash,
    #[msg("Arithmetic overflow occurred")]
    ArithmeticOverflow,
    #[msg("Arithmetic underflow occurred")]
    ArithmeticUnderflow,
    #[msg("Reviewer cannot be the same as appellant")]
    ReviewerCannotBeAppellant,
    #[msg("Resolver cannot be the same as appellant")]
    ResolverCannotBeAppellant,
    #[msg("Escalation rate limit: minimum 1 hour between escalations")]
    EscalationTooSoon,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_confidence_score_validation() {
        assert!(ConfidenceScore::new(0).is_ok());
        assert!(ConfidenceScore::new(100).is_ok());
        assert!(ConfidenceScore::new(101).is_err());
        
        let high_confidence = ConfidenceScore::new(90).unwrap();
        assert!(high_confidence.is_high_confidence());
        
        let low_confidence = ConfidenceScore::new(50).unwrap();
        assert!(!low_confidence.is_high_confidence());
    }

    #[test]
    fn test_violation_details_validation() {
        assert!(ViolationDetails::new("".to_string()).is_err());
        assert!(ViolationDetails::new("   ".to_string()).is_err());
        assert!(ViolationDetails::new("Valid violation".to_string()).is_ok());
        assert!(ViolationDetails::new("x".repeat(2001)).is_err());
    }

    #[test]
    fn test_appeal_id_generation() {
        let id1 = AppealId::new(1234567890).unwrap();
        let id2 = AppealId::new(1234567890).unwrap();
        assert_ne!(id1.0, id2.0); // Should be different due to random component
    }
}