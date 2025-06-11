// programs/quantumagi_core/src/lib.rs
// Quantumagi: On-Chain Constitutional Governance Framework for Solana
// Based on AlphaEvolve-ACGS framework adaptation

use anchor_lang::prelude::*;

// Program ID - Updated for devnet deployment
declare_id!("8eRUCnQsDxqK7vjp5XsYs7C3NGpdhzzaMW8QQGzfTUV4");

#[program]
pub mod quantumagi_core {
    use super::*;

    /// Initialize the constitutional governance system
    /// Sets up the foundational constitution with its hash and authority
    pub fn initialize(ctx: Context<Initialize>, constitution_hash: [u8; 32]) -> Result<()> {
        let constitution = &mut ctx.accounts.constitution;
        constitution.authority = ctx.accounts.authority.key();
        constitution.hash = constitution_hash;
        constitution.version = 1;
        constitution.created_at = Clock::get()?.unix_timestamp;
        constitution.is_active = true;

        msg!(
            "Constitution Initialized with hash: {:?}",
            constitution_hash
        );
        msg!("Authority: {}", constitution.authority);
        Ok(())
    }

    /// Propose a new policy (Called by the off-chain GS Engine)
    /// Creates a new policy in proposed state, not yet active
    pub fn propose_policy(
        ctx: Context<ProposePolicy>,
        policy_id: u64,
        rule: String,
        category: PolicyCategory,
        priority: PolicyPriority,
    ) -> Result<()> {
        require!(rule.len() <= MAX_RULE_LENGTH, QuantumagiError::RuleTooLong);

        let policy = &mut ctx.accounts.policy;
        policy.id = policy_id;
        policy.rule = rule.clone();
        policy.category = category;
        policy.priority = priority;
        policy.is_active = false;
        policy.proposed_at = Clock::get()?.unix_timestamp;
        policy.proposed_by = ctx.accounts.authority.key();
        policy.votes_for = 0;
        policy.votes_against = 0;

        msg!(
            "Policy {} Proposed: '{}' (Category: {:?}, Priority: {:?})",
            policy.id,
            policy.rule,
            policy.category,
            policy.priority
        );
        Ok(())
    }

    /// Enact a policy (Called by the constitutional authority/council)
    /// Activates a previously proposed policy
    pub fn enact_policy(ctx: Context<EnactPolicy>) -> Result<()> {
        let policy = &mut ctx.accounts.policy;
        let constitution = &ctx.accounts.constitution;

        // Verify authority
        require!(
            ctx.accounts.authority.key() == constitution.authority,
            QuantumagiError::Unauthorized
        );

        // Verify constitution is active
        require!(
            constitution.is_active,
            QuantumagiError::ConstitutionInactive
        );

        policy.is_active = true;
        policy.enacted_at = Some(Clock::get()?.unix_timestamp);
        policy.enacted_by = Some(ctx.accounts.authority.key());

        msg!("Policy {} has been ENACTED and is now ACTIVE.", policy.id);
        Ok(())
    }

    /// Vote on a proposed policy (Democratic governance mechanism)
    pub fn vote_on_policy(ctx: Context<VoteOnPolicy>, vote: PolicyVote) -> Result<()> {
        let policy = &mut ctx.accounts.policy;
        let voter_record = &mut ctx.accounts.voter_record;

        // Ensure policy is not yet active (still in voting phase)
        require!(!policy.is_active, QuantumagiError::PolicyAlreadyActive);

        // Prevent double voting
        require!(!voter_record.has_voted, QuantumagiError::AlreadyVoted);

        // Record the vote
        voter_record.has_voted = true;
        voter_record.vote = vote;
        voter_record.voted_at = Clock::get()?.unix_timestamp;

        // Update policy vote counts
        match vote {
            PolicyVote::For => policy.votes_for += 1,
            PolicyVote::Against => policy.votes_against += 1,
        }

        msg!("Vote recorded for Policy {}: {:?}", policy.id, vote);
        Ok(())
    }

    /// Check Compliance (The Prompt Governance Compiler - PGC)
    /// Core enforcement function that validates actions against active policies
    pub fn check_compliance(
        ctx: Context<CheckCompliance>,
        action_to_check: String,
        action_context: ActionContext,
    ) -> Result<()> {
        let policy = &ctx.accounts.policy;

        // Ensure the policy is active
        require!(policy.is_active, QuantumagiError::PolicyNotActive);

        // Core PGC logic - Enhanced compliance checking
        let compliance_result = evaluate_compliance(
            &policy.rule,
            &action_to_check,
            &action_context,
            &policy.category,
        )?;

        if compliance_result.is_compliant {
            msg!(
                "✅ Compliance check PASSED for action: '{}' (Confidence: {}%)",
                action_to_check,
                compliance_result.confidence
            );
            Ok(())
        } else {
            msg!(
                "❌ Compliance check FAILED for action: '{}' (Reason: {})",
                action_to_check,
                compliance_result.violation_reason
            );
            Err(error!(QuantumagiError::ComplianceFailed))
        }
    }

    /// Update constitution hash (for constitutional amendments)
    pub fn update_constitution(ctx: Context<UpdateConstitution>, new_hash: [u8; 32]) -> Result<()> {
        let constitution = &mut ctx.accounts.constitution;

        require!(
            ctx.accounts.authority.key() == constitution.authority,
            QuantumagiError::Unauthorized
        );

        constitution.hash = new_hash;
        constitution.version += 1;
        constitution.updated_at = Some(Clock::get()?.unix_timestamp);

        msg!(
            "Constitution updated to version {} with new hash: {:?}",
            constitution.version,
            new_hash
        );
        Ok(())
    }

    /// Deactivate a policy (Emergency governance function)
    pub fn deactivate_policy(ctx: Context<DeactivatePolicy>) -> Result<()> {
        let policy = &mut ctx.accounts.policy;
        let constitution = &ctx.accounts.constitution;

        require!(
            ctx.accounts.authority.key() == constitution.authority,
            QuantumagiError::Unauthorized
        );

        policy.is_active = false;
        policy.deactivated_at = Some(Clock::get()?.unix_timestamp);

        msg!("Policy {} has been DEACTIVATED.", policy.id);
        Ok(())
    }
}

// Constants
const MAX_RULE_LENGTH: usize = 1000;

// Enhanced compliance evaluation function
fn evaluate_compliance(
    rule: &str,
    action: &str,
    context: &ActionContext,
    category: &PolicyCategory,
) -> Result<ComplianceResult> {
    // This is a simplified implementation
    // In a real system, this would involve complex policy evaluation logic

    match category {
        PolicyCategory::PromptConstitution => {
            // PC-001: No Extrajudicial State Mutation
            if action.contains("unauthorized") || action.contains("bypass") {
                return Ok(ComplianceResult {
                    is_compliant: false,
                    confidence: 95,
                    violation_reason: "Potential unauthorized state mutation detected".to_string(),
                });
            }
        }
        PolicyCategory::Safety => {
            // Safety-critical rule evaluation
            if action.contains("unsafe") || action.contains("exploit") {
                return Ok(ComplianceResult {
                    is_compliant: false,
                    confidence: 98,
                    violation_reason: "Safety violation detected".to_string(),
                });
            }
        }
        PolicyCategory::Governance => {
            // Governance rule evaluation
            if context.requires_governance && !context.has_governance_approval {
                return Ok(ComplianceResult {
                    is_compliant: false,
                    confidence: 90,
                    violation_reason: "Governance approval required".to_string(),
                });
            }
        }
        PolicyCategory::Financial => {
            // Financial rule evaluation
            if context.involves_funds && context.amount > context.authorized_limit {
                return Ok(ComplianceResult {
                    is_compliant: false,
                    confidence: 99,
                    violation_reason: "Amount exceeds authorized limit".to_string(),
                });
            }
        }
    }

    // Simple string matching for basic compliance (enhanced logic would go here)
    let is_compliant = rule == action || rule.contains("ALLOW") && action.contains(&rule[6..]);

    Ok(ComplianceResult {
        is_compliant,
        confidence: if is_compliant { 85 } else { 80 },
        violation_reason: if is_compliant {
            "Action complies with policy".to_string()
        } else {
            "Action does not match policy rule".to_string()
        },
    })
}

// Data Structures and Enums
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq)]
pub enum PolicyCategory {
    PromptConstitution, // PC-001 type rules
    Safety,             // Safety-critical policies
    Governance,         // DAO governance rules
    Financial,          // Treasury and financial policies
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq)]
pub enum PolicyPriority {
    Critical, // Must be enforced immediately
    High,     // Important but not critical
    Medium,   // Standard priority
    Low,      // Advisory level
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, Debug, PartialEq)]
pub enum PolicyVote {
    For,
    Against,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct ActionContext {
    pub requires_governance: bool,
    pub has_governance_approval: bool,
    pub involves_funds: bool,
    pub amount: u64,
    pub authorized_limit: u64,
    pub caller: Pubkey,
}

#[derive(Debug)]
pub struct ComplianceResult {
    pub is_compliant: bool,
    pub confidence: u8,
    pub violation_reason: String,
}

// Account Structures

/// Constitution Account: Stores the foundational governance document
#[account]
pub struct Constitution {
    /// The authority that can make constitutional changes
    pub authority: Pubkey,
    /// SHA-256 hash of the constitutional document (stored off-chain)
    pub hash: [u8; 32],
    /// Version number for constitutional amendments
    pub version: u32,
    /// Whether this constitution is currently active
    pub is_active: bool,
    /// Timestamp when constitution was created
    pub created_at: i64,
    /// Timestamp when constitution was last updated
    pub updated_at: Option<i64>,
}

/// Policy Account: Represents a single, enforceable governance rule
#[account]
pub struct Policy {
    /// Unique identifier for the policy
    pub id: u64,
    /// The actual rule content/logic
    pub rule: String,
    /// Category of the policy (Safety, Governance, etc.)
    pub category: PolicyCategory,
    /// Priority level of the policy
    pub priority: PolicyPriority,
    /// Whether the policy is active and being enforced
    pub is_active: bool,
    /// When the policy was proposed
    pub proposed_at: i64,
    /// Who proposed the policy
    pub proposed_by: Pubkey,
    /// When the policy was enacted (if enacted)
    pub enacted_at: Option<i64>,
    /// Who enacted the policy (if enacted)
    pub enacted_by: Option<Pubkey>,
    /// When the policy was deactivated (if deactivated)
    pub deactivated_at: Option<i64>,
    /// Vote counts for democratic governance
    pub votes_for: u32,
    pub votes_against: u32,
}

/// Voter Record: Tracks individual votes on policies
#[account]
pub struct VoterRecord {
    /// The voter's public key
    pub voter: Pubkey,
    /// The policy being voted on
    pub policy_id: u64,
    /// Whether this voter has already voted
    pub has_voted: bool,
    /// The vote cast (if any)
    pub vote: PolicyVote,
    /// When the vote was cast
    pub voted_at: i64,
}

// Instruction Contexts

/// Context for initializing the constitution
#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + 32 + 32 + 4 + 1 + 8 + 9, // discriminator + pubkey + hash + version + bool + timestamp + option
        seeds = [b"constitution"],
        bump
    )]
    pub constitution: Account<'info, Constitution>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

/// Context for proposing a new policy
#[derive(Accounts)]
#[instruction(policy_id: u64, rule: String)]
pub struct ProposePolicy<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + 8 + 4 + rule.len() + 1 + 1 + 1 + 8 + 32 + 9 + 33 + 9 + 4 + 4, // Base + dynamic rule length
        seeds = [b"policy", policy_id.to_le_bytes().as_ref()],
        bump
    )]
    pub policy: Account<'info, Policy>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

/// Context for enacting a policy
#[derive(Accounts)]
pub struct EnactPolicy<'info> {
    #[account(mut)]
    pub policy: Account<'info, Policy>,
    pub constitution: Account<'info, Constitution>,
    pub authority: Signer<'info>,
}

/// Context for voting on a policy
#[derive(Accounts)]
#[instruction(vote: PolicyVote)]
pub struct VoteOnPolicy<'info> {
    #[account(mut)]
    pub policy: Account<'info, Policy>,
    #[account(
        init,
        payer = voter,
        space = 8 + 32 + 8 + 1 + 1 + 8, // discriminator + pubkey + policy_id + bool + vote + timestamp
        seeds = [b"vote", policy.id.to_le_bytes().as_ref(), voter.key().as_ref()],
        bump
    )]
    pub voter_record: Account<'info, VoterRecord>,
    #[account(mut)]
    pub voter: Signer<'info>,
    pub system_program: Program<'info, System>,
}

/// Context for compliance checking (PGC)
#[derive(Accounts)]
pub struct CheckCompliance<'info> {
    /// The policy account being checked against
    pub policy: Account<'info, Policy>,
}

/// Context for updating constitution
#[derive(Accounts)]
pub struct UpdateConstitution<'info> {
    #[account(mut)]
    pub constitution: Account<'info, Constitution>,
    pub authority: Signer<'info>,
}

/// Context for deactivating a policy
#[derive(Accounts)]
pub struct DeactivatePolicy<'info> {
    #[account(mut)]
    pub policy: Account<'info, Policy>,
    pub constitution: Account<'info, Constitution>,
    pub authority: Signer<'info>,
}

// Custom Error Codes
#[error_code]
pub enum QuantumagiError {
    #[msg("You are not authorized to perform this action.")]
    Unauthorized,
    #[msg("The proposed action violates an active policy.")]
    ComplianceFailed,
    #[msg("The policy being checked is not currently active.")]
    PolicyNotActive,
    #[msg("The constitution is not currently active.")]
    ConstitutionInactive,
    #[msg("The policy is already active and cannot be voted on.")]
    PolicyAlreadyActive,
    #[msg("You have already voted on this policy.")]
    AlreadyVoted,
    #[msg("The rule text is too long.")]
    RuleTooLong,
}
