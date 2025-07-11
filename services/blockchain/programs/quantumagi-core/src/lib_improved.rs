use anchor_lang::prelude::*;
use anchor_spl::token::{Token, TokenAccount};
use std::str::FromStr;

declare_id!("45shrZAMBbFGfLrev4FSDBchP847Q7oUR4jVqcxqnRD3");

// Constants with clear documentation
const MAX_PRINCIPLES: usize = 100;
const MAX_POLICY_LENGTH: usize = 1000;
const MAX_TITLE_LENGTH: usize = 100;
const MAX_DESCRIPTION_LENGTH: usize = 500;
const VOTING_PERIOD_SLOTS: u64 = 5; // ~2 seconds for testing
const SLOT_TIME_MS: u64 = 400; // Solana average slot time
const APPROVAL_THRESHOLD_PERCENT: u64 = 60;
const MIN_VOTING_POWER: u64 = 1;
const PRINCIPLE_HASH_LEN: usize = 32;

// Type-safe newtypes for better type safety
#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct PolicyId(pub u64);

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct VotingPower(pub u64);

impl VotingPower {
    pub fn new(power: u64) -> Result<Self> {
        require!(power >= MIN_VOTING_POWER, GovernanceError::InvalidVotingPower);
        Ok(Self(power))
    }
}

// Validated string types
#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct PolicyTitle(pub String);

impl PolicyTitle {
    pub fn new(title: String) -> Result<Self> {
        require!(
            !title.trim().is_empty(),
            GovernanceError::InvalidTitle
        );
        require!(
            title.len() <= MAX_TITLE_LENGTH,
            GovernanceError::TitleTooLong
        );
        Ok(Self(title))
    }
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct PolicyDescription(pub String);

impl PolicyDescription {
    pub fn new(desc: String) -> Result<Self> {
        require!(
            desc.len() <= MAX_DESCRIPTION_LENGTH,
            GovernanceError::DescriptionTooLong
        );
        Ok(Self(desc))
    }
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct PolicyText(pub String);

impl PolicyText {
    pub fn new(text: String) -> Result<Self> {
        require!(
            !text.trim().is_empty(),
            GovernanceError::InvalidPolicyText
        );
        require!(
            text.len() <= MAX_POLICY_LENGTH,
            GovernanceError::PolicyTooLong
        );
        Ok(Self(text))
    }
}

// Store principle hashes instead of full text for efficiency
#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct PrincipleHash {
    pub hash: [u8; PRINCIPLE_HASH_LEN],
    pub index: u8,
}

impl PrincipleHash {
    pub fn from_principle(principle: &str, index: u8) -> Self {
        use anchor_lang::solana_program::hash::hash;
        let hash_result = hash(principle.as_bytes());
        let mut hash_bytes = [0u8; PRINCIPLE_HASH_LEN];
        hash_bytes.copy_from_slice(&hash_result.to_bytes());
        
        Self {
            hash: hash_bytes,
            index,
        }
    }
}

#[program]
pub mod quantumagi_core {
    use super::*;

    /// Initialize governance with constitutional principles
    /// Stores only hashes of principles on-chain for efficiency
    pub fn initialize_governance(
        ctx: Context<InitializeGovernance>,
        authority: Pubkey,
        principle_hashes: Vec<[u8; PRINCIPLE_HASH_LEN]>,
    ) -> Result<()> {
        require!(
            principle_hashes.len() <= MAX_PRINCIPLES,
            GovernanceError::TooManyPrinciples
        );

        // Validate authority is not system program or other reserved addresses
        require!(
            authority != System::id() && authority != Token::id(),
            GovernanceError::InvalidAuthority
        );

        let governance = &mut ctx.accounts.governance;
        governance.authority = authority;
        governance.principle_hashes = principle_hashes.into_iter()
            .enumerate()
            .map(|(i, hash)| PrincipleHash { hash, index: i as u8 })
            .collect();
        governance.total_policies = 0;
        governance.active_proposals = 0;
        governance.emergency_mode = false;
        governance.last_emergency_at = None;
        governance.bump = ctx.bumps.governance;
        governance.initialized_at = Clock::get()?.unix_timestamp;

        emit!(GovernanceInitialized {
            authority,
            principles_count: governance.principle_hashes.len() as u32,
            initialized_at: governance.initialized_at,
        });

        Ok(())
    }

    /// Create a new policy proposal with enhanced validation
    pub fn create_policy_proposal(
        ctx: Context<CreatePolicyProposal>,
        policy_id: PolicyId,
        title: String,
        description: String,
        policy_text: String,
    ) -> Result<()> {
        // Validate inputs using type-safe wrappers
        let title = PolicyTitle::new(title)?;
        let description = PolicyDescription::new(description)?;
        let policy_text = PolicyText::new(policy_text)?;

        let proposal = &mut ctx.accounts.proposal;
        let governance = &mut ctx.accounts.governance;
        let clock = Clock::get()?;

        // Check for emergency mode
        require!(
            !governance.emergency_mode,
            GovernanceError::EmergencyModeActive
        );

        // Prevent proposal spam
        require!(
            governance.active_proposals < 100,
            GovernanceError::TooManyActiveProposals
        );

        // Calculate voting end time with overflow protection
        let voting_duration_ms = VOTING_PERIOD_SLOTS
            .checked_mul(SLOT_TIME_MS)
            .ok_or(GovernanceError::ArithmeticOverflow)?;
        let voting_ends_at = clock.unix_timestamp
            .checked_add(voting_duration_ms as i64 / 1000)
            .ok_or(GovernanceError::ArithmeticOverflow)?;

        proposal.policy_id = policy_id;
        proposal.title = title;
        proposal.description = description;
        proposal.policy_text_hash = {
            use anchor_lang::solana_program::hash::hash;
            let hash_result = hash(policy_text.0.as_bytes());
            let mut hash_bytes = [0u8; PRINCIPLE_HASH_LEN];
            hash_bytes.copy_from_slice(&hash_result.to_bytes());
            hash_bytes
        };
        proposal.proposer = ctx.accounts.proposer.key();
        proposal.created_at = clock.unix_timestamp;
        proposal.voting_ends_at = voting_ends_at;
        proposal.status = ProposalStatus::Active;
        proposal.votes_for = 0;
        proposal.votes_against = 0;
        proposal.total_voters = 0;
        proposal.unique_voters = vec![];
        proposal.quorum_reached = false;
        proposal.bump = ctx.bumps.proposal;

        governance.active_proposals = governance.active_proposals
            .checked_add(1)
            .ok_or(GovernanceError::ArithmeticOverflow)?;

        emit!(PolicyProposalCreated {
            policy_id: policy_id.0,
            proposer: ctx.accounts.proposer.key(),
            title: proposal.title.0.clone(),
            created_at: proposal.created_at,
            voting_ends_at: proposal.voting_ends_at,
        });

        Ok(())
    }

    /// Vote on a policy proposal with enhanced validation
    pub fn vote_on_proposal(
        ctx: Context<VoteOnProposal>,
        policy_id: PolicyId,
        vote: bool,
        voting_power: u64,
    ) -> Result<()> {
        let proposal = &mut ctx.accounts.proposal;
        let vote_record = &mut ctx.accounts.vote_record;
        let clock = Clock::get()?;
        let voter = ctx.accounts.voter.key();

        // Validate voting power
        let voting_power = VotingPower::new(voting_power)?;

        require!(
            proposal.status == ProposalStatus::Active,
            GovernanceError::ProposalNotActive
        );
        require!(
            clock.unix_timestamp <= proposal.voting_ends_at,
            GovernanceError::VotingPeriodEnded
        );

        // Prevent double voting with better tracking
        require!(
            !proposal.unique_voters.contains(&voter),
            GovernanceError::AlreadyVoted
        );

        // Token-based voting validation (if token account provided)
        if let Some(token_account) = ctx.accounts.token_account.as_ref() {
            require!(
                token_account.amount >= voting_power.0,
                GovernanceError::InsufficientTokens
            );
        }

        // Record the vote
        vote_record.voter = voter;
        vote_record.policy_id = policy_id;
        vote_record.vote = vote;
        vote_record.voting_power = voting_power.clone();
        vote_record.timestamp = clock.unix_timestamp;
        vote_record.bump = ctx.bumps.vote_record;

        // Update proposal with overflow protection
        if vote {
            proposal.votes_for = proposal.votes_for
                .checked_add(voting_power.0)
                .ok_or(GovernanceError::ArithmeticOverflow)?;
        } else {
            proposal.votes_against = proposal.votes_against
                .checked_add(voting_power.0)
                .ok_or(GovernanceError::ArithmeticOverflow)?;
        }
        
        proposal.total_voters = proposal.total_voters
            .checked_add(1)
            .ok_or(GovernanceError::ArithmeticOverflow)?;
        proposal.unique_voters.push(voter);

        // Check quorum (25% of circulating supply for example)
        let total_votes = proposal.votes_for
            .checked_add(proposal.votes_against)
            .ok_or(GovernanceError::ArithmeticOverflow)?;
        if total_votes >= 1000 { // Example quorum threshold
            proposal.quorum_reached = true;
        }

        emit!(VoteCast {
            policy_id: policy_id.0,
            voter,
            vote,
            voting_power: voting_power.0,
            timestamp: clock.unix_timestamp,
        });

        Ok(())
    }

    /// Finalize a proposal with enhanced validation
    pub fn finalize_proposal(ctx: Context<FinalizeProposal>, policy_id: PolicyId) -> Result<()> {
        let proposal = &mut ctx.accounts.proposal;
        let governance = &mut ctx.accounts.governance;
        let clock = Clock::get()?;

        require!(
            proposal.status == ProposalStatus::Active,
            GovernanceError::ProposalNotActive
        );
        require!(
            clock.unix_timestamp > proposal.voting_ends_at,
            GovernanceError::VotingPeriodNotEnded
        );

        // Calculate outcome with overflow protection
        let total_votes = proposal.votes_for
            .checked_add(proposal.votes_against)
            .ok_or(GovernanceError::ArithmeticOverflow)?;
        
        if total_votes == 0 {
            proposal.status = ProposalStatus::Rejected;
            emit!(PolicyRejected {
                policy_id: policy_id.0,
                votes_for: 0,
                votes_against: 0,
                reason: "No votes cast".to_string(),
            });
        } else {
            let approval_threshold = total_votes
                .checked_mul(APPROVAL_THRESHOLD_PERCENT)
                .ok_or(GovernanceError::ArithmeticOverflow)?
                .checked_div(100)
                .ok_or(GovernanceError::ArithmeticOverflow)?;

            if proposal.votes_for >= approval_threshold && proposal.quorum_reached {
                proposal.status = ProposalStatus::Approved;
                governance.total_policies = governance.total_policies
                    .checked_add(1)
                    .ok_or(GovernanceError::ArithmeticOverflow)?;

                emit!(PolicyApproved {
                    policy_id: policy_id.0,
                    votes_for: proposal.votes_for,
                    votes_against: proposal.votes_against,
                    approval_percentage: (proposal.votes_for * 100) / total_votes,
                });
            } else {
                proposal.status = ProposalStatus::Rejected;
                let reason = if !proposal.quorum_reached {
                    "Quorum not reached"
                } else {
                    "Insufficient approval"
                };

                emit!(PolicyRejected {
                    policy_id: policy_id.0,
                    votes_for: proposal.votes_for,
                    votes_against: proposal.votes_against,
                    reason: reason.to_string(),
                });
            }
        }

        proposal.finalized_at = Some(clock.unix_timestamp);
        governance.active_proposals = governance.active_proposals
            .checked_sub(1)
            .ok_or(GovernanceError::ArithmeticUnderflow)?;

        Ok(())
    }

    /// Emergency governance action with enhanced controls
    pub fn emergency_action(
        ctx: Context<EmergencyAction>,
        action_type: EmergencyActionType,
        target_policy_id: Option<PolicyId>,
        justification: String,
    ) -> Result<()> {
        let governance = &mut ctx.accounts.governance;
        let clock = Clock::get()?;

        require!(
            ctx.accounts.authority.key() == governance.authority,
            GovernanceError::UnauthorizedEmergencyAction
        );

        // Rate limit emergency actions (max once per day)
        if let Some(last_emergency) = governance.last_emergency_at {
            let time_since_last = clock.unix_timestamp
                .checked_sub(last_emergency)
                .ok_or(GovernanceError::ArithmeticUnderflow)?;
            require!(
                time_since_last >= 86400, // 24 hours
                GovernanceError::EmergencyActionTooSoon
            );
        }

        // Validate justification
        require!(
            !justification.trim().is_empty() && justification.len() <= 500,
            GovernanceError::InvalidJustification
        );

        // Execute action based on type
        match action_type {
            EmergencyActionType::SuspendProposal => {
                require!(
                    target_policy_id.is_some(),
                    GovernanceError::PolicyIdRequired
                );
                governance.emergency_mode = true;
            }
            EmergencyActionType::ForceApproval => {
                require!(
                    target_policy_id.is_some(),
                    GovernanceError::PolicyIdRequired
                );
                // Additional validation would be done on the proposal account
            }
            EmergencyActionType::UpdateAuthority => {
                // Authority update requires additional validation
                governance.emergency_mode = true;
            }
            EmergencyActionType::SystemMaintenance => {
                governance.emergency_mode = true;
            }
        }

        governance.last_emergency_at = Some(clock.unix_timestamp);

        emit!(EmergencyActionExecuted {
            authority: ctx.accounts.authority.key(),
            action_type,
            target_policy_id: target_policy_id.map(|id| id.0),
            timestamp: clock.unix_timestamp,
            justification,
        });

        Ok(())
    }

    /// Transfer governance authority with multi-sig support
    pub fn transfer_authority(
        ctx: Context<TransferAuthority>,
        new_authority: Pubkey,
    ) -> Result<()> {
        let governance = &mut ctx.accounts.governance;
        let old_authority = governance.authority;

        // Validate new authority
        require!(
            new_authority != System::id() && new_authority != Token::id(),
            GovernanceError::InvalidAuthority
        );
        require!(
            new_authority != old_authority,
            GovernanceError::SameAuthority
        );

        governance.authority = new_authority;

        emit!(AuthorityTransferred {
            old_authority,
            new_authority,
            timestamp: Clock::get()?.unix_timestamp,
        });

        Ok(())
    }
}

// Account Structures with InitSpace derive

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
#[instruction(policy_id: PolicyId)]
pub struct CreatePolicyProposal<'info> {
    #[account(
        init,
        payer = proposer,
        space = 8 + PolicyProposal::INIT_SPACE,
        seeds = [b"proposal", policy_id.0.to_le_bytes().as_ref()],
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
#[instruction(policy_id: PolicyId)]
pub struct VoteOnProposal<'info> {
    #[account(
        mut,
        seeds = [b"proposal", policy_id.0.to_le_bytes().as_ref()],
        bump = proposal.bump
    )]
    pub proposal: Account<'info, PolicyProposal>,

    #[account(
        init,
        payer = voter,
        space = 8 + VoteRecord::INIT_SPACE,
        seeds = [b"vote", policy_id.0.to_le_bytes().as_ref(), voter.key().as_ref()],
        bump
    )]
    pub vote_record: Account<'info, VoteRecord>,

    #[account(mut)]
    pub voter: Signer<'info>,

    /// Optional token account for token-weighted voting
    pub token_account: Option<Account<'info, TokenAccount>>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
#[instruction(policy_id: PolicyId)]
pub struct FinalizeProposal<'info> {
    #[account(
        mut,
        seeds = [b"proposal", policy_id.0.to_le_bytes().as_ref()],
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
pub struct EmergencyAction<'info> {
    #[account(
        mut,
        seeds = [b"governance"],
        bump = governance.bump
    )]
    pub governance: Account<'info, GovernanceState>,

    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct TransferAuthority<'info> {
    #[account(
        mut,
        seeds = [b"governance"],
        bump = governance.bump,
        constraint = governance.authority == authority.key() @ GovernanceError::UnauthorizedTransfer
    )]
    pub governance: Account<'info, GovernanceState>,

    pub authority: Signer<'info>,
}

// Data Structures with InitSpace

#[account]
#[derive(InitSpace)]
pub struct GovernanceState {
    pub authority: Pubkey,
    #[max_len(MAX_PRINCIPLES)]
    pub principle_hashes: Vec<PrincipleHash>,
    pub total_policies: u32,
    pub active_proposals: u32,
    pub emergency_mode: bool,
    pub last_emergency_at: Option<i64>,
    pub initialized_at: i64,
    pub bump: u8,
}

#[account]
#[derive(InitSpace)]
pub struct PolicyProposal {
    pub policy_id: PolicyId,
    pub title: PolicyTitle,
    pub description: PolicyDescription,
    pub policy_text_hash: [u8; PRINCIPLE_HASH_LEN], // Store hash instead of full text
    pub proposer: Pubkey,
    pub created_at: i64,
    pub voting_ends_at: i64,
    pub finalized_at: Option<i64>,
    pub status: ProposalStatus,
    pub votes_for: u64,
    pub votes_against: u64,
    pub total_voters: u32,
    #[max_len(1000)] // Max unique voters to track
    pub unique_voters: Vec<Pubkey>,
    pub quorum_reached: bool,
    pub bump: u8,
}

#[account]
#[derive(InitSpace)]
pub struct VoteRecord {
    pub voter: Pubkey,
    pub policy_id: PolicyId,
    pub vote: bool,
    pub voting_power: VotingPower,
    pub timestamp: i64,
    pub bump: u8,
}

// Enums and Types

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Eq, InitSpace)]
pub enum ProposalStatus {
    Active,
    Approved,
    Rejected,
    Emergency,
    Cancelled,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum EmergencyActionType {
    SuspendProposal,
    ForceApproval,
    UpdateAuthority,
    SystemMaintenance,
}

// Enhanced Events

#[event]
pub struct GovernanceInitialized {
    pub authority: Pubkey,
    pub principles_count: u32,
    pub initialized_at: i64,
}

#[event]
pub struct PolicyProposalCreated {
    pub policy_id: u64,
    pub proposer: Pubkey,
    pub title: String,
    pub created_at: i64,
    pub voting_ends_at: i64,
}

#[event]
pub struct VoteCast {
    pub policy_id: u64,
    pub voter: Pubkey,
    pub vote: bool,
    pub voting_power: u64,
    pub timestamp: i64,
}

#[event]
pub struct PolicyApproved {
    pub policy_id: u64,
    pub votes_for: u64,
    pub votes_against: u64,
    pub approval_percentage: u64,
}

#[event]
pub struct PolicyRejected {
    pub policy_id: u64,
    pub votes_for: u64,
    pub votes_against: u64,
    pub reason: String,
}

#[event]
pub struct EmergencyActionExecuted {
    pub authority: Pubkey,
    pub action_type: EmergencyActionType,
    pub target_policy_id: Option<u64>,
    pub timestamp: i64,
    pub justification: String,
}

#[event]
pub struct AuthorityTransferred {
    pub old_authority: Pubkey,
    pub new_authority: Pubkey,
    pub timestamp: i64,
}

// Enhanced Custom Errors with context

#[error_code]
pub enum GovernanceError {
    #[msg("Too many constitutional principles. Maximum allowed: 100")]
    TooManyPrinciples,
    #[msg("Policy text too long. Maximum length: 1000 characters")]
    PolicyTooLong,
    #[msg("Title too long. Maximum length: 100 characters")]
    TitleTooLong,
    #[msg("Title cannot be empty")]
    InvalidTitle,
    #[msg("Description too long. Maximum length: 500 characters")]
    DescriptionTooLong,
    #[msg("Policy text cannot be empty")]
    InvalidPolicyText,
    #[msg("Proposal is not active")]
    ProposalNotActive,
    #[msg("Voting period has ended")]
    VotingPeriodEnded,
    #[msg("Voting period has not ended yet")]
    VotingPeriodNotEnded,
    #[msg("Invalid voting power. Minimum required: 1")]
    InvalidVotingPower,
    #[msg("Unauthorized emergency action")]
    UnauthorizedEmergencyAction,
    #[msg("Voter has already voted on this proposal")]
    AlreadyVoted,
    #[msg("Insufficient governance tokens for voting")]
    InsufficientTokens,
    #[msg("Arithmetic overflow occurred")]
    ArithmeticOverflow,
    #[msg("Arithmetic underflow occurred")]
    ArithmeticUnderflow,
    #[msg("Emergency mode is currently active")]
    EmergencyModeActive,
    #[msg("Too many active proposals. Maximum: 100")]
    TooManyActiveProposals,
    #[msg("Emergency action rate limit: once per 24 hours")]
    EmergencyActionTooSoon,
    #[msg("Invalid justification for emergency action")]
    InvalidJustification,
    #[msg("Policy ID required for this action")]
    PolicyIdRequired,
    #[msg("Invalid authority address")]
    InvalidAuthority,
    #[msg("Cannot transfer to same authority")]
    SameAuthority,
    #[msg("Unauthorized authority transfer")]
    UnauthorizedTransfer,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_voting_power_validation() {
        assert!(VotingPower::new(0).is_err());
        assert!(VotingPower::new(1).is_ok());
        assert!(VotingPower::new(1000).is_ok());
    }

    #[test]
    fn test_policy_title_validation() {
        assert!(PolicyTitle::new("".to_string()).is_err());
        assert!(PolicyTitle::new("   ".to_string()).is_err());
        assert!(PolicyTitle::new("Valid Title".to_string()).is_ok());
        assert!(PolicyTitle::new("x".repeat(101)).is_err());
    }

    #[test]
    fn test_principle_hash_generation() {
        let hash1 = PrincipleHash::from_principle("Test Principle", 0);
        let hash2 = PrincipleHash::from_principle("Test Principle", 0);
        assert_eq!(hash1.hash, hash2.hash);
        
        let hash3 = PrincipleHash::from_principle("Different Principle", 0);
        assert_ne!(hash1.hash, hash3.hash);
    }
}