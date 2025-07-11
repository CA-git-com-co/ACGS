use anchor_lang::prelude::*;
use anchor_spl::token::{Token, TokenAccount, Mint};
use std::collections::BTreeMap;

// Advanced governance features implementation

// Delegation system for liquid democracy
#[account]
#[derive(InitSpace)]
pub struct DelegationRegistry {
    pub delegations: BTreeMap<Pubkey, Delegation>,
    pub delegation_tree: BTreeMap<Pubkey, Vec<Pubkey>>, // delegate -> list of delegators
    pub max_delegation_depth: u8,
    pub total_delegations: u32,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct Delegation {
    pub delegator: Pubkey,
    pub delegate: Pubkey,
    pub delegation_power: u64,
    pub scope: DelegationScope,
    pub created_at: i64,
    pub expires_at: Option<i64>,
    pub revocable: bool,
    pub delegation_level: u8, // Prevent infinite delegation chains
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum DelegationScope {
    All,                    // Delegate all voting power
    PolicyCategory(String), // Delegate only for specific policy categories
    SpecificProposal(u64),  // Delegate only for specific proposal
    TimeRange { start: i64, end: i64 }, // Delegate for specific time range
}

// Multi-signature governance for critical operations
#[account]
#[derive(InitSpace)]
pub struct MultiSigGovernance {
    pub signers: Vec<Pubkey>,
    pub threshold: u8,
    pub pending_transactions: BTreeMap<u64, PendingTransaction>,
    pub executed_transactions: Vec<u64>,
    pub next_transaction_id: u64,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct PendingTransaction {
    pub id: u64,
    pub transaction_type: GovernanceTransaction,
    pub signatures: Vec<Pubkey>,
    pub required_signatures: u8,
    pub created_at: i64,
    pub expires_at: i64,
    pub executed: bool,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum GovernanceTransaction {
    UpdateAuthority { new_authority: Pubkey },
    UpdateThreshold { new_threshold: u8 },
    AddSigner { new_signer: Pubkey },
    RemoveSigner { signer: Pubkey },
    EmergencyStop,
    SystemUpgrade { new_program_id: Pubkey },
}

// Reputation system for governance participants
#[account]
#[derive(InitSpace)]
pub struct ReputationSystem {
    pub reputation_scores: BTreeMap<Pubkey, ReputationScore>,
    pub reputation_weights: ReputationWeights,
    pub decay_rate: u16, // Basis points per day (e.g., 10 = 0.1% decay per day)
    pub last_decay_update: i64,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ReputationScore {
    pub base_score: u64,
    pub activity_score: u64,
    pub accuracy_score: u64,
    pub last_updated: i64,
    pub participation_count: u32,
    pub successful_proposals: u32,
    pub failed_proposals: u32,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ReputationWeights {
    pub participation_weight: u16,  // Weight for participation
    pub accuracy_weight: u16,       // Weight for voting with majority
    pub proposal_weight: u16,       // Weight for successful proposals
    pub longevity_weight: u16,      // Weight for long-term participation
}

// Futarchy - prediction market governance
#[account]
#[derive(InitSpace)]
pub struct PredictionMarket {
    pub proposal_id: u64,
    pub market_type: MarketType,
    pub outcome_tokens: BTreeMap<String, OutcomeToken>,
    pub total_volume: u64,
    pub resolution_deadline: i64,
    pub oracle: Pubkey,
    pub resolved: bool,
    pub winning_outcome: Option<String>,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum MarketType {
    Binary { yes_outcome: String, no_outcome: String },
    Categorical { outcomes: Vec<String> },
    Scalar { min_value: i64, max_value: i64, precision: u8 },
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct OutcomeToken {
    pub name: String,
    pub price: u64,        // Price in base units
    pub total_supply: u64,
    pub volume_24h: u64,
    pub last_trade: i64,
}

// Time-locked governance for delayed execution
#[account]
#[derive(InitSpace)]
pub struct TimeLock {
    pub proposal_id: u64,
    pub execution_time: i64,
    pub grace_period: i64,
    pub executed: bool,
    pub cancelled: bool,
    pub proposal_hash: [u8; 32],
    pub bump: u8,
}

// Governance token economics
#[account]
#[derive(InitSpace)]
pub struct GovernanceTokenomics {
    pub token_mint: Pubkey,
    pub total_supply: u64,
    pub circulating_supply: u64,
    pub staked_supply: u64,
    pub inflation_rate: u16,      // Basis points per year
    pub staking_rewards_pool: u64,
    pub last_inflation_update: i64,
    pub voting_power_curve: VotingPowerCurve,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum VotingPowerCurve {
    Linear,                                    // 1:1 ratio
    SquareRoot,                               // sqrt(tokens)
    Logarithmic { base: u8 },                 // log_base(tokens)
    Quadratic { max_power: u64 },             // min(tokens^2, max_power)
    Tiered { tiers: Vec<VotingTier> },        // Different rates per tier
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct VotingTier {
    pub threshold: u64,
    pub multiplier: u16, // Basis points (e.g., 10000 = 1x)
}

// Conviction voting implementation
#[account]
#[derive(InitSpace)]
pub struct ConvictionVoting {
    pub proposal_id: u64,
    pub conviction_votes: BTreeMap<Pubkey, ConvictionVote>,
    pub total_conviction: u64,
    pub conviction_threshold: u64,
    pub half_life: u64, // Time for conviction to decay by half
    pub last_update: i64,
    pub funding_pool: u64,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ConvictionVote {
    pub voter: Pubkey,
    pub tokens_committed: u64,
    pub conviction_score: u64,
    pub commitment_start: i64,
    pub last_conviction_update: i64,
}

// Governance analytics and insights
#[account]
#[derive(InitSpace)]
pub struct GovernanceAnalytics {
    pub proposal_metrics: ProposalMetrics,
    pub voter_analytics: VoterAnalytics,
    pub network_health: NetworkHealth,
    pub participation_trends: ParticipationTrends,
    pub last_updated: i64,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ProposalMetrics {
    pub total_proposals: u32,
    pub passed_proposals: u32,
    pub failed_proposals: u32,
    pub average_voting_period: u64,
    pub average_participation_rate: u16, // Basis points
    pub proposal_success_rate: u16,      // Basis points
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct VoterAnalytics {
    pub total_voters: u32,
    pub active_voters_30d: u32,
    pub whale_concentration: u16,        // Top 10% voting power percentage
    pub average_vote_weight: u64,
    pub voter_retention_rate: u16,       // Basis points
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct NetworkHealth {
    pub decentralization_score: u16,     // 0-10000 basis points
    pub governance_attack_cost: u64,     // Cost to acquire 51% voting power
    pub liquidity_score: u16,            // Token liquidity health
    pub participation_diversity: u16,     // Geographic/entity diversity
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ParticipationTrends {
    pub daily_active_voters: [u32; 30],  // Last 30 days
    pub proposal_frequency: [u32; 12],   // Last 12 months
    pub voter_engagement_score: u16,     // Basis points
    pub seasonal_patterns: SeasonalPatterns,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct SeasonalPatterns {
    pub peak_activity_hour: u8,     // Hour of day (0-23)
    pub peak_activity_day: u8,      // Day of week (0-6)
    pub peak_activity_month: u8,    // Month (1-12)
    pub activity_variance: u16,     // Variance in activity levels
}

// Implementation of governance features
impl DelegationRegistry {
    pub fn delegate_voting_power(
        &mut self,
        delegator: Pubkey,
        delegate: Pubkey,
        power: u64,
        scope: DelegationScope,
        duration: Option<i64>,
    ) -> Result<()> {
        // Prevent delegation to self
        require!(delegator != delegate, GovernanceError::SelfDelegation);

        // Check delegation depth to prevent cycles
        let delegation_level = self.calculate_delegation_depth(&delegate)?;
        require!(
            delegation_level < self.max_delegation_depth,
            GovernanceError::DelegationDepthExceeded
        );

        let clock = Clock::get()?;
        let expires_at = duration.map(|d| clock.unix_timestamp + d);

        let delegation = Delegation {
            delegator,
            delegate,
            delegation_power: power,
            scope,
            created_at: clock.unix_timestamp,
            expires_at,
            revocable: true,
            delegation_level,
        };

        // Update delegation registry
        self.delegations.insert(delegator, delegation);
        self.delegation_tree.entry(delegate).or_insert_with(Vec::new).push(delegator);
        self.total_delegations += 1;

        Ok(())
    }

    pub fn revoke_delegation(&mut self, delegator: Pubkey) -> Result<()> {
        if let Some(delegation) = self.delegations.remove(&delegator) {
            require!(delegation.revocable, GovernanceError::DelegationNotRevocable);

            // Remove from delegation tree
            if let Some(delegators) = self.delegation_tree.get_mut(&delegation.delegate) {
                delegators.retain(|&d| d != delegator);
                if delegators.is_empty() {
                    self.delegation_tree.remove(&delegation.delegate);
                }
            }

            self.total_delegations = self.total_delegations.saturating_sub(1);
        }

        Ok(())
    }

    fn calculate_delegation_depth(&self, account: &Pubkey) -> Result<u8> {
        let mut depth = 0;
        let mut current = *account;
        let mut visited = std::collections::HashSet::new();

        while let Some(delegation) = self.delegations.get(&current) {
            if visited.contains(&current) {
                return Err(GovernanceError::DelegationCycle.into());
            }
            visited.insert(current);
            current = delegation.delegate;
            depth += 1;

            if depth > self.max_delegation_depth {
                return Err(GovernanceError::DelegationDepthExceeded.into());
            }
        }

        Ok(depth)
    }

    pub fn get_effective_voting_power(
        &self,
        voter: &Pubkey,
        proposal_id: u64,
        base_power: u64,
    ) -> u64 {
        let mut total_power = base_power;

        // Add delegated power
        if let Some(delegators) = self.delegation_tree.get(voter) {
            for delegator in delegators {
                if let Some(delegation) = self.delegations.get(delegator) {
                    if self.delegation_applies(delegation, proposal_id) {
                        total_power += delegation.delegation_power;
                    }
                }
            }
        }

        total_power
    }

    fn delegation_applies(&self, delegation: &Delegation, proposal_id: u64) -> bool {
        let clock = Clock::get().unwrap_or_default();

        // Check if delegation has expired
        if let Some(expires_at) = delegation.expires_at {
            if clock.unix_timestamp > expires_at {
                return false;
            }
        }

        // Check scope
        match &delegation.scope {
            DelegationScope::All => true,
            DelegationScope::SpecificProposal(id) => *id == proposal_id,
            DelegationScope::TimeRange { start, end } => {
                clock.unix_timestamp >= *start && clock.unix_timestamp <= *end
            }
            DelegationScope::PolicyCategory(_) => {
                // Would need to check proposal category
                true // Simplified for now
            }
        }
    }
}

impl ReputationSystem {
    pub fn update_reputation(
        &mut self,
        participant: Pubkey,
        action: ReputationAction,
    ) -> Result<()> {
        let score = self.reputation_scores.entry(participant).or_insert_with(|| {
            ReputationScore {
                base_score: 1000, // Starting reputation
                activity_score: 0,
                accuracy_score: 0,
                last_updated: Clock::get().unwrap_or_default().unix_timestamp,
                participation_count: 0,
                successful_proposals: 0,
                failed_proposals: 0,
            }
        });

        match action {
            ReputationAction::VoteParticipation => {
                score.activity_score += 10;
                score.participation_count += 1;
            }
            ReputationAction::ProposalSubmission => {
                score.activity_score += 50;
            }
            ReputationAction::ProposalSuccess => {
                score.base_score += 100;
                score.successful_proposals += 1;
            }
            ReputationAction::ProposalFailure => {
                score.base_score = score.base_score.saturating_sub(20);
                score.failed_proposals += 1;
            }
            ReputationAction::VoteWithMajority => {
                score.accuracy_score += 5;
            }
            ReputationAction::VoteAgainstMajority => {
                score.accuracy_score = score.accuracy_score.saturating_sub(2);
            }
        }

        score.last_updated = Clock::get()?.unix_timestamp;
        Ok(())
    }

    pub fn calculate_voting_multiplier(&self, participant: &Pubkey) -> u16 {
        if let Some(score) = self.reputation_scores.get(participant) {
            let total_score = score.base_score + score.activity_score + score.accuracy_score;
            
            // Convert to multiplier (basis points)
            // Higher reputation = higher voting weight
            let multiplier = 10000 + (total_score / 100); // Base 1x + bonus
            std::cmp::min(multiplier as u16, 20000) // Cap at 2x multiplier
        } else {
            10000 // 1x multiplier for new participants
        }
    }

    pub fn decay_reputation(&mut self) -> Result<()> {
        let current_time = Clock::get()?.unix_timestamp;
        let days_since_update = (current_time - self.last_decay_update) / 86400; // seconds per day

        if days_since_update > 0 {
            for score in self.reputation_scores.values_mut() {
                let decay_amount = (score.activity_score * self.decay_rate as u64) / 10000;
                score.activity_score = score.activity_score.saturating_sub(decay_amount * days_since_update as u64);
            }
            self.last_decay_update = current_time;
        }

        Ok(())
    }
}

#[derive(Clone)]
pub enum ReputationAction {
    VoteParticipation,
    ProposalSubmission,
    ProposalSuccess,
    ProposalFailure,
    VoteWithMajority,
    VoteAgainstMajority,
}

impl ConvictionVoting {
    pub fn add_conviction_vote(
        &mut self,
        voter: Pubkey,
        tokens: u64,
    ) -> Result<()> {
        let clock = Clock::get()?;
        
        if let Some(existing_vote) = self.conviction_votes.get_mut(&voter) {
            // Update existing vote
            existing_vote.tokens_committed += tokens;
            self.update_conviction_score(existing_vote, clock.unix_timestamp)?;
        } else {
            // New conviction vote
            let conviction_vote = ConvictionVote {
                voter,
                tokens_committed: tokens,
                conviction_score: 0, // Starts at 0, builds over time
                commitment_start: clock.unix_timestamp,
                last_conviction_update: clock.unix_timestamp,
            };
            self.conviction_votes.insert(voter, conviction_vote);
        }

        self.recalculate_total_conviction()?;
        Ok(())
    }

    fn update_conviction_score(&self, vote: &mut ConvictionVote, current_time: i64) -> Result<()> {
        let time_elapsed = current_time - vote.last_conviction_update;
        
        // Conviction grows over time using exponential function
        // conviction = tokens * (1 - e^(-t/half_life))
        let time_factor = (-time_elapsed as f64 / self.half_life as f64).exp();
        let conviction_multiplier = 1.0 - time_factor;
        
        vote.conviction_score = (vote.tokens_committed as f64 * conviction_multiplier) as u64;
        vote.last_conviction_update = current_time;
        
        Ok(())
    }

    fn recalculate_total_conviction(&mut self) -> Result<()> {
        self.total_conviction = self.conviction_votes.values()
            .map(|vote| vote.conviction_score)
            .sum();
        Ok(())
    }

    pub fn check_funding_threshold(&self) -> bool {
        self.total_conviction >= self.conviction_threshold
    }
}

// Error types for advanced governance features
#[error_code]
pub enum GovernanceError {
    #[msg("Cannot delegate voting power to yourself")]
    SelfDelegation,
    #[msg("Delegation depth exceeded maximum allowed")]
    DelegationDepthExceeded,
    #[msg("Delegation cycle detected")]
    DelegationCycle,
    #[msg("Delegation is not revocable")]
    DelegationNotRevocable,
    #[msg("Insufficient signatures for multi-sig transaction")]
    InsufficientSignatures,
    #[msg("Multi-sig transaction has expired")]
    TransactionExpired,
    #[msg("Invalid reputation action")]
    InvalidReputationAction,
    #[msg("Prediction market already resolved")]
    MarketAlreadyResolved,
    #[msg("Invalid market oracle")]
    InvalidOracle,
    #[msg("Time lock period has not elapsed")]
    TimeLockNotElapsed,
    #[msg("Conviction threshold not met")]
    ConvictionThresholdNotMet,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_delegation_system() {
        let mut registry = DelegationRegistry {
            delegations: BTreeMap::new(),
            delegation_tree: BTreeMap::new(),
            max_delegation_depth: 3,
            total_delegations: 0,
            bump: 0,
        };

        let delegator = Pubkey::new_unique();
        let delegate = Pubkey::new_unique();

        assert!(registry.delegate_voting_power(
            delegator,
            delegate,
            1000,
            DelegationScope::All,
            None
        ).is_ok());

        assert_eq!(registry.total_delegations, 1);
        assert!(registry.delegations.contains_key(&delegator));
    }

    #[test]
    fn test_reputation_system() {
        let mut reputation = ReputationSystem {
            reputation_scores: BTreeMap::new(),
            reputation_weights: ReputationWeights {
                participation_weight: 1000,
                accuracy_weight: 1000,
                proposal_weight: 1000,
                longevity_weight: 1000,
            },
            decay_rate: 10, // 0.1% per day
            last_decay_update: 0,
            bump: 0,
        };

        let participant = Pubkey::new_unique();
        
        assert!(reputation.update_reputation(
            participant,
            ReputationAction::VoteParticipation
        ).is_ok());

        let multiplier = reputation.calculate_voting_multiplier(&participant);
        assert!(multiplier > 10000); // Should be greater than base 1x
    }

    #[test]
    fn test_conviction_voting() {
        let mut conviction = ConvictionVoting {
            proposal_id: 1,
            conviction_votes: BTreeMap::new(),
            total_conviction: 0,
            conviction_threshold: 10000,
            half_life: 86400, // 1 day
            last_update: 0,
            funding_pool: 100000,
            bump: 0,
        };

        let voter = Pubkey::new_unique();
        
        assert!(conviction.add_conviction_vote(voter, 5000).is_ok());
        assert!(conviction.conviction_votes.contains_key(&voter));
    }
}