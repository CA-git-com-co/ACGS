// programs/appeals/src/lib.rs
// Quantumagi Appeals System - Democratic Appeal Process for Policy Violations
// Provides multi-tier appeal system with human oversight

// Suppress expected cfg warnings from Anchor macros due to CLI/crate version differences
#![allow(unexpected_cfgs)]

use anchor_lang::prelude::*;

declare_id!("278awDwWu5NZRyDCLufPXQk1p9Q16WAhn9cvsFwFtsfY");

#[program]
pub mod appeals {
    use super::*;

    /// Submit an appeal for a policy violation
    pub fn submit_appeal(
        ctx: Context<SubmitAppeal>,
        policy_id: u64,
        violation_details: String,
        evidence_hash: [u8; 32],
        appeal_type: AppealType,
    ) -> Result<()> {
        require!(
            violation_details.len() <= MAX_VIOLATION_DETAILS,
            AppealsError::ViolationDetailsTooLong
        );

        let appeal = &mut ctx.accounts.appeal;
        let clock = Clock::get()?;

        appeal.id = clock.unix_timestamp as u64;
        appeal.policy_id = policy_id;
        appeal.appellant = ctx.accounts.appellant.key();
        appeal.violation_details = violation_details;
        appeal.evidence_hash = evidence_hash;
        appeal.appeal_type = appeal_type;
        appeal.status = AppealStatus::Submitted;
        appeal.submitted_at = clock.unix_timestamp;
        appeal.reviewer = None;
        appeal.review_deadline = clock.unix_timestamp + REVIEW_DEADLINE_SECONDS;
        appeal.escalation_count = 0;

        msg!(
            "Appeal {} submitted for policy {} by {}",
            appeal.id,
            policy_id,
            ctx.accounts.appellant.key()
        );

        Ok(())
    }

    /// Review an appeal (first-tier automated/AI review)
    pub fn review_appeal(
        ctx: Context<ReviewAppeal>,
        reviewer_decision: ReviewDecision,
        review_evidence: String,
        confidence_score: u8,
    ) -> Result<()> {
        require!(
            confidence_score <= 100,
            AppealsError::InvalidConfidenceScore
        );
        require!(
            review_evidence.len() <= MAX_REVIEW_EVIDENCE,
            AppealsError::ReviewEvidenceTooLong
        );

        let appeal = &mut ctx.accounts.appeal;
        let clock = Clock::get()?;

        // Verify appeal is in correct status
        require!(
            appeal.status == AppealStatus::Submitted,
            AppealsError::InvalidAppealStatus
        );

        // Check review deadline
        require!(
            clock.unix_timestamp <= appeal.review_deadline,
            AppealsError::ReviewDeadlineExpired
        );

        appeal.reviewer = Some(ctx.accounts.reviewer.key());
        appeal.review_decision = Some(reviewer_decision.clone());
        appeal.review_evidence = review_evidence;
        appeal.confidence_score = confidence_score;
        appeal.reviewed_at = Some(clock.unix_timestamp);

        // Determine next status based on decision and confidence
        match reviewer_decision {
            ReviewDecision::Approve => {
                if confidence_score >= HIGH_CONFIDENCE_THRESHOLD {
                    appeal.status = AppealStatus::Approved;
                    msg!(
                        "Appeal {} approved with high confidence ({}%)",
                        appeal.id,
                        confidence_score
                    );
                } else {
                    appeal.status = AppealStatus::PendingHumanReview;
                    msg!(
                        "Appeal {} approved but requires human review (confidence: {}%)",
                        appeal.id,
                        confidence_score
                    );
                }
            }
            ReviewDecision::Reject => {
                if confidence_score >= HIGH_CONFIDENCE_THRESHOLD {
                    appeal.status = AppealStatus::Rejected;
                    msg!(
                        "Appeal {} rejected with high confidence ({}%)",
                        appeal.id,
                        confidence_score
                    );
                } else {
                    appeal.status = AppealStatus::PendingHumanReview;
                    msg!(
                        "Appeal {} rejected but requires human review (confidence: {}%)",
                        appeal.id,
                        confidence_score
                    );
                }
            }
            ReviewDecision::Escalate => {
                appeal.status = AppealStatus::PendingHumanReview;
                msg!("Appeal {} escalated to human review", appeal.id);
            }
        }

        Ok(())
    }

    /// Escalate appeal to human committee
    pub fn escalate_to_human_committee(
        ctx: Context<EscalateAppeal>,
        escalation_reason: String,
        committee_type: CommitteeType,
    ) -> Result<()> {
        require!(
            escalation_reason.len() <= MAX_ESCALATION_REASON,
            AppealsError::EscalationReasonTooLong
        );

        let appeal = &mut ctx.accounts.appeal;
        let clock = Clock::get()?;

        // Verify appeal can be escalated
        require!(
            appeal.status == AppealStatus::PendingHumanReview
                || appeal.status == AppealStatus::Submitted,
            AppealsError::CannotEscalate
        );

        // Check escalation limits
        require!(
            appeal.escalation_count < MAX_ESCALATIONS,
            AppealsError::MaxEscalationsReached
        );

        appeal.status = AppealStatus::EscalatedToHuman;
        appeal.escalation_reason = Some(escalation_reason);
        appeal.committee_type = Some(committee_type.clone());
        appeal.escalated_at = Some(clock.unix_timestamp);
        appeal.escalation_count += 1;
        appeal.human_review_deadline = Some(clock.unix_timestamp + HUMAN_REVIEW_DEADLINE_SECONDS);

        msg!(
            "Appeal {} escalated to {:?} committee (escalation #{})",
            appeal.id,
            committee_type,
            appeal.escalation_count
        );

        Ok(())
    }

    /// Resolve appeal with final ruling
    pub fn resolve_with_ruling(
        ctx: Context<ResolveAppeal>,
        final_decision: FinalDecision,
        ruling_details: String,
        enforcement_action: EnforcementAction,
    ) -> Result<()> {
        require!(
            ruling_details.len() <= MAX_RULING_DETAILS,
            AppealsError::RulingDetailsTooLong
        );

        let appeal = &mut ctx.accounts.appeal;
        let clock = Clock::get()?;

        // Verify appeal is in correct status for resolution
        require!(
            appeal.status == AppealStatus::EscalatedToHuman
                || appeal.status == AppealStatus::PendingHumanReview,
            AppealsError::CannotResolve
        );

        appeal.final_decision = Some(final_decision.clone());
        appeal.ruling_details = ruling_details;
        appeal.enforcement_action = Some(enforcement_action.clone());
        appeal.resolved_at = Some(clock.unix_timestamp);
        appeal.resolver = Some(ctx.accounts.resolver.key());

        // Set final status
        match final_decision {
            FinalDecision::Uphold => {
                appeal.status = AppealStatus::Rejected;
                msg!(
                    "Appeal {} final ruling: UPHOLD original decision",
                    appeal.id
                );
            }
            FinalDecision::Overturn => {
                appeal.status = AppealStatus::Approved;
                msg!(
                    "Appeal {} final ruling: OVERTURN original decision",
                    appeal.id
                );
            }
            FinalDecision::Modify => {
                appeal.status = AppealStatus::ModifiedApproval;
                msg!("Appeal {} final ruling: MODIFY with conditions", appeal.id);
            }
        }

        // Log enforcement action
        match enforcement_action {
            EnforcementAction::None => {}
            EnforcementAction::PolicyUpdate => {
                msg!("Enforcement: Policy {} requires update", appeal.policy_id);
            }
            EnforcementAction::SystemAlert => {
                msg!(
                    "Enforcement: System alert issued for policy {}",
                    appeal.policy_id
                );
            }
            EnforcementAction::TemporaryExemption => {
                msg!("Enforcement: Temporary exemption granted for appellant");
            }
        }

        Ok(())
    }

    /// Get appeal statistics for governance reporting
    pub fn get_appeal_stats(ctx: Context<GetAppealStats>) -> Result<()> {
        // This would typically return statistics but Anchor doesn't support return values
        // Instead, we emit an event with the statistics

        let stats = &ctx.accounts.appeal_stats;

        emit!(AppealStatsEvent {
            total_appeals: stats.total_appeals,
            approved_appeals: stats.approved_appeals,
            rejected_appeals: stats.rejected_appeals,
            pending_appeals: stats.pending_appeals,
            average_resolution_time: stats.average_resolution_time,
            human_escalation_rate: stats.human_escalation_rate,
        });

        Ok(())
    }
}

// Constants
const MAX_VIOLATION_DETAILS: usize = 2000;
const MAX_REVIEW_EVIDENCE: usize = 1000;
const MAX_ESCALATION_REASON: usize = 500;
const MAX_RULING_DETAILS: usize = 2000;
const REVIEW_DEADLINE_SECONDS: i64 = 24 * 60 * 60; // 24 hours
const HUMAN_REVIEW_DEADLINE_SECONDS: i64 = 7 * 24 * 60 * 60; // 7 days
const HIGH_CONFIDENCE_THRESHOLD: u8 = 85;
const MAX_ESCALATIONS: u8 = 3;

// Account Structures

/// Appeal Account: Represents a single appeal case
#[account]
pub struct Appeal {
    /// Unique appeal identifier
    pub id: u64,
    /// Policy ID being appealed
    pub policy_id: u64,
    /// Public key of the appellant
    pub appellant: Pubkey,
    /// Detailed description of the violation
    pub violation_details: String,
    /// Hash of supporting evidence (stored off-chain)
    pub evidence_hash: [u8; 32],
    /// Type of appeal
    pub appeal_type: AppealType,
    /// Current status of the appeal
    pub status: AppealStatus,
    /// When the appeal was submitted
    pub submitted_at: i64,
    /// Deadline for initial review
    pub review_deadline: i64,
    /// Who reviewed the appeal (if any)
    pub reviewer: Option<Pubkey>,
    /// Review decision (if any)
    pub review_decision: Option<ReviewDecision>,
    /// Evidence provided by reviewer
    pub review_evidence: String,
    /// Confidence score of the review (0-100)
    pub confidence_score: u8,
    /// When the appeal was reviewed
    pub reviewed_at: Option<i64>,
    /// Reason for escalation (if escalated)
    pub escalation_reason: Option<String>,
    /// Type of committee handling escalation
    pub committee_type: Option<CommitteeType>,
    /// When escalated to human review
    pub escalated_at: Option<i64>,
    /// Number of times escalated
    pub escalation_count: u8,
    /// Deadline for human review
    pub human_review_deadline: Option<i64>,
    /// Final decision (if resolved)
    pub final_decision: Option<FinalDecision>,
    /// Detailed ruling explanation
    pub ruling_details: String,
    /// Enforcement action to be taken
    pub enforcement_action: Option<EnforcementAction>,
    /// When the appeal was resolved
    pub resolved_at: Option<i64>,
    /// Who resolved the appeal
    pub resolver: Option<Pubkey>,
}

/// Appeal Statistics Account
#[account]
pub struct AppealStats {
    pub total_appeals: u64,
    pub approved_appeals: u64,
    pub rejected_appeals: u64,
    pub pending_appeals: u64,
    pub average_resolution_time: u64, // in seconds
    pub human_escalation_rate: u8,    // percentage
}

// Enums

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq)]
pub enum AppealType {
    PolicyViolation,         // Appeal against policy violation ruling
    ProcessError,            // Appeal due to process/system error
    NewEvidence,             // Appeal with new evidence
    ConstitutionalChallenge, // Challenge policy constitutionality
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq)]
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

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq)]
pub enum ReviewDecision {
    Approve,  // Approve the appeal
    Reject,   // Reject the appeal
    Escalate, // Escalate to human review
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq)]
pub enum CommitteeType {
    Technical,      // Technical review committee
    Governance,     // Governance committee
    Ethics,         // Ethics review committee
    Constitutional, // Constitutional review committee
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq)]
pub enum FinalDecision {
    Uphold,   // Uphold original decision
    Overturn, // Overturn original decision
    Modify,   // Modify with conditions
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq)]
pub enum EnforcementAction {
    None,               // No action required
    PolicyUpdate,       // Policy needs updating
    SystemAlert,        // Issue system alert
    TemporaryExemption, // Grant temporary exemption
}

// Instruction Contexts

/// Context for submitting an appeal
#[derive(Accounts)]
#[instruction(policy_id: u64, violation_details: String)]
pub struct SubmitAppeal<'info> {
    #[account(
        init,
        payer = appellant,
        space = 8 + 8 + 8 + 32 + 4 + violation_details.len() + 32 + 1 + 1 + 8 + 8 + 33 + 33 + 4 + 1 + 9 + 4 + 33 + 9 + 1 + 9 + 33 + 4 + 33 + 9 + 33,
        seeds = [b"appeal", policy_id.to_le_bytes().as_ref(), appellant.key().as_ref()],
        bump
    )]
    pub appeal: Account<'info, Appeal>,
    #[account(mut)]
    pub appellant: Signer<'info>,
    pub system_program: Program<'info, System>,
}

/// Context for reviewing an appeal
#[derive(Accounts)]
pub struct ReviewAppeal<'info> {
    #[account(mut)]
    pub appeal: Account<'info, Appeal>,
    pub reviewer: Signer<'info>,
}

/// Context for escalating an appeal
#[derive(Accounts)]
pub struct EscalateAppeal<'info> {
    #[account(mut)]
    pub appeal: Account<'info, Appeal>,
    pub escalator: Signer<'info>,
}

/// Context for resolving an appeal
#[derive(Accounts)]
pub struct ResolveAppeal<'info> {
    #[account(mut)]
    pub appeal: Account<'info, Appeal>,
    pub resolver: Signer<'info>,
}

/// Context for getting appeal statistics
#[derive(Accounts)]
pub struct GetAppealStats<'info> {
    pub appeal_stats: Account<'info, AppealStats>,
}

// Events

#[event]
pub struct AppealSubmittedEvent {
    pub appeal_id: u64,
    pub policy_id: u64,
    pub appellant: Pubkey,
    pub appeal_type: AppealType,
    pub submitted_at: i64,
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
}

#[event]
pub struct AppealResolvedEvent {
    pub appeal_id: u64,
    pub final_decision: FinalDecision,
    pub enforcement_action: EnforcementAction,
    pub resolver: Pubkey,
    pub resolved_at: i64,
}

#[event]
pub struct AppealStatsEvent {
    pub total_appeals: u64,
    pub approved_appeals: u64,
    pub rejected_appeals: u64,
    pub pending_appeals: u64,
    pub average_resolution_time: u64,
    pub human_escalation_rate: u8,
}

// Custom Error Codes
#[error_code]
pub enum AppealsError {
    #[msg("Violation details are too long.")]
    ViolationDetailsTooLong,
    #[msg("Review evidence is too long.")]
    ReviewEvidenceTooLong,
    #[msg("Escalation reason is too long.")]
    EscalationReasonTooLong,
    #[msg("Ruling details are too long.")]
    RulingDetailsTooLong,
    #[msg("Invalid confidence score. Must be 0-100.")]
    InvalidConfidenceScore,
    #[msg("Appeal is not in the correct status for this operation.")]
    InvalidAppealStatus,
    #[msg("Review deadline has expired.")]
    ReviewDeadlineExpired,
    #[msg("Appeal cannot be escalated in its current status.")]
    CannotEscalate,
    #[msg("Maximum number of escalations reached.")]
    MaxEscalationsReached,
    #[msg("Appeal cannot be resolved in its current status.")]
    CannotResolve,
}
