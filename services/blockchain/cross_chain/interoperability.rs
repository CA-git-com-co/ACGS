use anchor_lang::prelude::*;
use std::collections::BTreeMap;

// Cross-chain interoperability for ACGS governance system

// Cross-chain bridge for multi-network governance
#[account]
#[derive(InitSpace)]
pub struct CrossChainBridge {
    pub supported_chains: BTreeMap<ChainId, ChainInfo>,
    pub bridge_operators: Vec<Pubkey>,
    pub multi_sig_threshold: u8,
    pub pending_transfers: BTreeMap<String, PendingTransfer>,
    pub completed_transfers: Vec<TransferRecord>,
    pub bridge_stats: BridgeStatistics,
    pub security_config: BridgeSecurityConfig,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, InitSpace)]
pub struct ChainId(pub u32);

impl ChainId {
    pub const ETHEREUM: ChainId = ChainId(1);
    pub const POLYGON: ChainId = ChainId(137);
    pub const ARBITRUM: ChainId = ChainId(42161);
    pub const OPTIMISM: ChainId = ChainId(10);
    pub const AVALANCHE: ChainId = ChainId(43114);
    pub const BINANCE: ChainId = ChainId(56);
    pub const SOLANA: ChainId = ChainId(999999); // Custom ID for Solana
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ChainInfo {
    pub chain_id: ChainId,
    pub name: String,
    pub native_token: String,
    pub governance_contract: String, // Contract address on target chain
    pub bridge_contract: String,
    pub is_active: bool,
    pub min_confirmation_blocks: u32,
    pub gas_limits: GasLimits,
    pub supported_tokens: Vec<TokenInfo>,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct GasLimits {
    pub vote_transaction: u64,
    pub proposal_transaction: u64,
    pub delegation_transaction: u64,
    pub emergency_transaction: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct TokenInfo {
    pub symbol: String,
    pub decimals: u8,
    pub contract_address: String,
    pub is_governance_token: bool,
    pub exchange_rate: u64, // Rate relative to base token
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct PendingTransfer {
    pub transfer_id: String,
    pub from_chain: ChainId,
    pub to_chain: ChainId,
    pub transfer_type: TransferType,
    pub amount: u64,
    pub recipient: String, // Address on target chain
    pub sender: Pubkey,
    pub initiated_at: i64,
    pub confirmations: Vec<TransferConfirmation>,
    pub required_confirmations: u8,
    pub expires_at: i64,
    pub status: TransferStatus,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum TransferType {
    VotingPower { proposal_id: u64 },
    GovernanceTokens,
    DelegationRights { delegate: String },
    ProposalData { proposal_hash: [u8; 32] },
    ReputationScore { reputation: u64 },
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct TransferConfirmation {
    pub operator: Pubkey,
    pub timestamp: i64,
    pub signature: [u8; 64],
    pub transaction_hash: String, // Hash on source chain
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum TransferStatus {
    Pending,
    Confirmed,
    Executed,
    Failed,
    Expired,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct TransferRecord {
    pub transfer_id: String,
    pub from_chain: ChainId,
    pub to_chain: ChainId,
    pub transfer_type: TransferType,
    pub amount: u64,
    pub completed_at: i64,
    pub gas_used: u64,
    pub fees_paid: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct BridgeStatistics {
    pub total_transfers: u64,
    pub total_volume: u64,
    pub failed_transfers: u32,
    pub average_confirmation_time: u64,
    pub total_fees_collected: u64,
    pub active_operators: u8,
    pub uptime_percentage: u16, // basis points
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct BridgeSecurityConfig {
    pub max_daily_volume: u64,
    pub max_single_transfer: u64,
    pub operator_bond_required: u64,
    pub slash_percentage: u16, // basis points
    pub emergency_pause_enabled: bool,
    pub rate_limit_per_user: u32, // transfers per hour
    pub suspicious_activity_threshold: u16,
}

// Universal governance message format for cross-chain communication
#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct UniversalGovernanceMessage {
    pub version: u8,
    pub message_type: MessageType,
    pub source_chain: ChainId,
    pub target_chain: ChainId,
    pub nonce: u64,
    pub timestamp: i64,
    pub payload: MessagePayload,
    pub signature: [u8; 64],
    pub hash: [u8; 32],
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum MessageType {
    Vote,
    Proposal,
    Delegation,
    Emergency,
    Configuration,
    Reputation,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum MessagePayload {
    Vote {
        proposal_id: u64,
        voter: String,
        vote: bool,
        voting_power: u64,
        proof: VoteProof,
    },
    Proposal {
        proposal_id: u64,
        title: String,
        description_hash: [u8; 32],
        voting_period: u64,
        quorum_threshold: u64,
    },
    Delegation {
        delegator: String,
        delegate: String,
        amount: u64,
        duration: u64,
        scope: DelegationScope,
    },
    Emergency {
        action_type: EmergencyActionType,
        justification_hash: [u8; 32],
        required_confirmations: u8,
    },
    Configuration {
        parameter: String,
        old_value: String,
        new_value: String,
        effective_time: i64,
    },
    Reputation {
        user: String,
        old_score: u64,
        new_score: u64,
        reason: ReputationChangeReason,
    },
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct VoteProof {
    pub merkle_proof: Vec<[u8; 32]>,
    pub token_balance_proof: TokenBalanceProof,
    pub delegation_proof: Option<DelegationProof>,
    pub reputation_proof: ReputationProof,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct TokenBalanceProof {
    pub balance: u64,
    pub block_number: u64,
    pub merkle_root: [u8; 32],
    pub account_proof: Vec<[u8; 32]>,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct DelegationProof {
    pub delegated_amount: u64,
    pub delegation_expiry: i64,
    pub delegation_signature: [u8; 64],
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ReputationProof {
    pub reputation_score: u64,
    pub last_updated: i64,
    pub reputation_merkle_proof: Vec<[u8; 32]>,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum DelegationScope {
    Universal,
    ChainSpecific(ChainId),
    ProposalSpecific(u64),
    CategorySpecific(String),
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum EmergencyActionType {
    PauseBridge,
    HaltGovernance,
    UpdateSecurityParams,
    SlashOperator,
    EmergencyUpgrade,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum ReputationChangeReason {
    VoteParticipation,
    ProposalSuccess,
    ProposalFailure,
    MaliciousActivity,
    CommunityContribution,
}

// Cross-chain state synchronization
#[account]
#[derive(InitSpace)]
pub struct CrossChainState {
    pub chain_states: BTreeMap<ChainId, ChainState>,
    pub global_state_hash: [u8; 32],
    pub last_sync_time: i64,
    pub sync_interval: u64,
    pub state_conflicts: Vec<StateConflict>,
    pub consensus_mechanism: ConsensusMechanism,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ChainState {
    pub chain_id: ChainId,
    pub block_height: u64,
    pub state_root: [u8; 32],
    pub governance_state_hash: [u8; 32],
    pub last_updated: i64,
    pub validator_set: Vec<ValidatorInfo>,
    pub pending_updates: Vec<StateUpdate>,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ValidatorInfo {
    pub address: String,
    pub stake: u64,
    pub is_active: bool,
    pub last_activity: i64,
    pub slash_count: u32,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct StateUpdate {
    pub update_id: u64,
    pub update_type: StateUpdateType,
    pub data_hash: [u8; 32],
    pub timestamp: i64,
    pub confirmations: u32,
    pub required_confirmations: u32,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum StateUpdateType {
    ProposalCreated,
    ProposalFinalized,
    VoteCast,
    DelegationChanged,
    EmergencyAction,
    ConfigurationUpdate,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct StateConflict {
    pub conflict_id: u64,
    pub chain_a: ChainId,
    pub chain_b: ChainId,
    pub conflict_type: ConflictType,
    pub detected_at: i64,
    pub resolution_status: ConflictResolution,
    pub resolution_data: String,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum ConflictType {
    ProposalIdCollision,
    VotingPowerMismatch,
    DelegationConflict,
    StateRootMismatch,
    TimestampSkew,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum ConflictResolution {
    Pending,
    ResolvedByConsensus,
    ResolvedByOracle,
    ManualIntervention,
    Ignored,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum ConsensusMechanism {
    ProofOfStake,
    ProofOfAuthority,
    ByzantineFaultTolerant,
    Tendermint,
    HotStuff,
}

// Light client implementation for efficient cross-chain verification
#[account]
#[derive(InitSpace)]
pub struct LightClient {
    pub target_chain: ChainId,
    pub trusted_header: BlockHeader,
    pub validator_set: ValidatorSet,
    pub trust_period: u64,
    pub trusting_period: u64,
    pub max_clock_drift: u64,
    pub verification_cache: VerificationCache,
    pub client_state: ClientState,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct BlockHeader {
    pub height: u64,
    pub time: i64,
    pub chain_id: ChainId,
    pub app_hash: [u8; 32],
    pub validators_hash: [u8; 32],
    pub next_validators_hash: [u8; 32],
    pub consensus_hash: [u8; 32],
    pub last_commit_hash: [u8; 32],
    pub data_hash: [u8; 32],
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ValidatorSet {
    pub validators: Vec<Validator>,
    pub proposer: Validator,
    pub total_voting_power: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct Validator {
    pub address: [u8; 20],
    pub pub_key: [u8; 32],
    pub voting_power: u64,
    pub proposer_priority: i64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct VerificationCache {
    pub verified_headers: BTreeMap<u64, [u8; 32]>, // height -> hash
    pub cache_size: u32,
    pub hit_rate: u16,
    pub last_cleanup: i64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum ClientState {
    Active,
    Frozen,
    Expired,
    Updating,
}

// Cross-chain governance aggregator
#[account]
#[derive(InitSpace)]
pub struct GovernanceAggregator {
    pub chain_configs: BTreeMap<ChainId, ChainGovernanceConfig>,
    pub global_proposals: BTreeMap<u64, GlobalProposal>,
    pub cross_chain_votes: BTreeMap<u64, CrossChainVoteData>,
    pub delegation_registry: CrossChainDelegationRegistry,
    pub reputation_system: CrossChainReputationSystem,
    pub aggregation_rules: AggregationRules,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ChainGovernanceConfig {
    pub chain_id: ChainId,
    pub governance_weight: u16, // basis points of total weight
    pub quorum_requirement: u16, // basis points
    pub voting_period: u64,
    pub execution_delay: u64,
    pub emergency_threshold: u16,
    pub is_active: bool,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct GlobalProposal {
    pub proposal_id: u64,
    pub title: String,
    pub description_hash: [u8; 32],
    pub proposer_chain: ChainId,
    pub proposer_address: String,
    pub target_chains: Vec<ChainId>,
    pub proposal_type: GlobalProposalType,
    pub created_at: i64,
    pub voting_starts_at: i64,
    pub voting_ends_at: i64,
    pub execution_time: Option<i64>,
    pub status: GlobalProposalStatus,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum GlobalProposalType {
    ConfigurationChange,
    CrossChainTokenTransfer,
    BridgeUpgrade,
    EmergencyAction,
    ReputationSystemUpdate,
    GovernanceParameterChange,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum GlobalProposalStatus {
    Draft,
    Active,
    Succeeded,
    Defeated,
    Queued,
    Executed,
    Cancelled,
    Expired,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct CrossChainVoteData {
    pub proposal_id: u64,
    pub chain_votes: BTreeMap<ChainId, ChainVoteData>,
    pub total_voting_power: u64,
    pub votes_for: u64,
    pub votes_against: u64,
    pub abstains: u64,
    pub quorum_reached: bool,
    pub weighted_result: VoteResult,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ChainVoteData {
    pub chain_id: ChainId,
    pub votes_for: u64,
    pub votes_against: u64,
    pub abstains: u64,
    pub total_voting_power: u64,
    pub participation_rate: u16, // basis points
    pub last_updated: i64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum VoteResult {
    Pending,
    Approved,
    Rejected,
    QuorumNotMet,
    Tied,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct CrossChainDelegationRegistry {
    pub delegations: BTreeMap<String, CrossChainDelegation>, // delegator_chain_address -> delegation
    pub delegation_trees: BTreeMap<ChainId, BTreeMap<String, Vec<String>>>, // chain -> delegate -> delegators
    pub max_delegation_depth: u8,
    pub total_delegated_power: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct CrossChainDelegation {
    pub delegator_chain: ChainId,
    pub delegator_address: String,
    pub delegate_chain: ChainId,
    pub delegate_address: String,
    pub delegated_power: u64,
    pub scope: CrossChainDelegationScope,
    pub created_at: i64,
    pub expires_at: Option<i64>,
    pub is_revocable: bool,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum CrossChainDelegationScope {
    Global,
    ChainSpecific(Vec<ChainId>),
    ProposalTypeSpecific(GlobalProposalType),
    TimeWindow { start: i64, end: i64 },
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct CrossChainReputationSystem {
    pub user_reputations: BTreeMap<String, CrossChainReputation>, // chain_address -> reputation
    pub reputation_weights: BTreeMap<ChainId, u16>, // chain weight in reputation calculation
    pub global_reputation_metrics: GlobalReputationMetrics,
    pub reputation_sync_interval: u64,
    pub last_sync: i64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct CrossChainReputation {
    pub user_id: String, // chain_id:address format
    pub chain_reputations: BTreeMap<ChainId, u64>,
    pub global_reputation: u64,
    pub participation_history: ParticipationHistory,
    pub reputation_multiplier: u16, // basis points
    pub last_updated: i64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ParticipationHistory {
    pub total_votes: u32,
    pub cross_chain_votes: u32,
    pub proposals_created: u32,
    pub successful_proposals: u32,
    pub delegation_activity: u32,
    pub governance_contribution_score: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct GlobalReputationMetrics {
    pub total_participants: u32,
    pub active_cross_chain_participants: u32,
    pub average_reputation_score: u64,
    pub reputation_distribution: ReputationDistribution,
    pub top_contributors: Vec<String>,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ReputationDistribution {
    pub low_reputation: u32,    // 0-25th percentile
    pub medium_reputation: u32, // 25-75th percentile
    pub high_reputation: u32,   // 75-95th percentile
    pub elite_reputation: u32,  // 95th+ percentile
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct AggregationRules {
    pub vote_weighting_method: VoteWeightingMethod,
    pub quorum_calculation: QuorumCalculation,
    pub conflict_resolution: ConflictResolutionMethod,
    pub finality_requirements: FinalityRequirements,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum VoteWeightingMethod {
    Equal,                    // Each chain has equal weight
    ProportionalToTVL,       // Weight by total value locked
    ProportionalToParticipation, // Weight by participation rate
    CustomWeights,           // Manual weight assignment
    Hybrid,                  // Combination of methods
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum QuorumCalculation {
    GlobalQuorum(u16),       // Percentage of all chains
    ChainBasedQuorum(u16),   // Percentage per chain
    WeightedQuorum(u16),     // Weighted by chain importance
    AdaptiveQuorum,          // Dynamic based on participation
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum ConflictResolutionMethod {
    MajorityRule,
    SuperMajority(u16),      // Percentage required
    WeightedVoting,
    OracleArbitration,
    CommunityMediation,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct FinalityRequirements {
    pub min_chain_confirmations: BTreeMap<ChainId, u32>,
    pub min_time_delay: u64,
    pub required_validator_signatures: u32,
    pub slashing_conditions: Vec<SlashingCondition>,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct SlashingCondition {
    pub condition_type: SlashingType,
    pub penalty_percentage: u16, // basis points
    pub evidence_requirement: EvidenceRequirement,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum SlashingType {
    DoubleVoting,
    InvalidProof,
    Censorship,
    Unavailability,
    MaliciousActivity,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum EvidenceRequirement {
    CryptographicProof,
    MultipleWitnesses(u32),
    OnChainEvidence,
    CommunityReport,
}

// Implementation of cross-chain functionality
impl CrossChainBridge {
    pub fn initiate_transfer(
        &mut self,
        from_chain: ChainId,
        to_chain: ChainId,
        transfer_type: TransferType,
        amount: u64,
        recipient: String,
        sender: Pubkey,
    ) -> Result<String> {
        // Validate chains are supported
        require!(
            self.supported_chains.contains_key(&from_chain) &&
            self.supported_chains.contains_key(&to_chain),
            CrossChainError::UnsupportedChain
        );

        // Check bridge limits
        require!(
            amount <= self.security_config.max_single_transfer,
            CrossChainError::TransferAmountExceeded
        );

        let transfer_id = self.generate_transfer_id()?;
        let clock = Clock::get()?;

        let pending_transfer = PendingTransfer {
            transfer_id: transfer_id.clone(),
            from_chain,
            to_chain,
            transfer_type,
            amount,
            recipient,
            sender,
            initiated_at: clock.unix_timestamp,
            confirmations: vec![],
            required_confirmations: self.multi_sig_threshold,
            expires_at: clock.unix_timestamp + 3600, // 1 hour expiry
            status: TransferStatus::Pending,
        };

        self.pending_transfers.insert(transfer_id.clone(), pending_transfer);
        self.bridge_stats.total_transfers += 1;

        Ok(transfer_id)
    }

    pub fn confirm_transfer(
        &mut self,
        transfer_id: String,
        operator: Pubkey,
        signature: [u8; 64],
        transaction_hash: String,
    ) -> Result<()> {
        let transfer = self.pending_transfers.get_mut(&transfer_id)
            .ok_or(CrossChainError::TransferNotFound)?;

        // Verify operator is authorized
        require!(
            self.bridge_operators.contains(&operator),
            CrossChainError::UnauthorizedOperator
        );

        // Check if already confirmed by this operator
        require!(
            !transfer.confirmations.iter().any(|c| c.operator == operator),
            CrossChainError::AlreadyConfirmed
        );

        let confirmation = TransferConfirmation {
            operator,
            timestamp: Clock::get()?.unix_timestamp,
            signature,
            transaction_hash,
        };

        transfer.confirmations.push(confirmation);

        // Check if we have enough confirmations
        if transfer.confirmations.len() >= transfer.required_confirmations as usize {
            transfer.status = TransferStatus::Confirmed;
            self.execute_transfer(&transfer_id)?;
        }

        Ok(())
    }

    fn execute_transfer(&mut self, transfer_id: &str) -> Result<()> {
        let mut transfer = self.pending_transfers.remove(transfer_id)
            .ok_or(CrossChainError::TransferNotFound)?;

        transfer.status = TransferStatus::Executed;

        let record = TransferRecord {
            transfer_id: transfer.transfer_id.clone(),
            from_chain: transfer.from_chain,
            to_chain: transfer.to_chain,
            transfer_type: transfer.transfer_type,
            amount: transfer.amount,
            completed_at: Clock::get()?.unix_timestamp,
            gas_used: 21000, // Estimated
            fees_paid: 1000, // Estimated
        };

        self.completed_transfers.push(record);
        self.bridge_stats.total_volume += transfer.amount;

        Ok(())
    }

    fn generate_transfer_id(&self) -> Result<String> {
        let clock = Clock::get()?;
        Ok(format!("tx_{}", clock.unix_timestamp))
    }
}

impl GovernanceAggregator {
    pub fn create_global_proposal(
        &mut self,
        title: String,
        description_hash: [u8; 32],
        proposer_chain: ChainId,
        proposer_address: String,
        target_chains: Vec<ChainId>,
        proposal_type: GlobalProposalType,
        voting_period: u64,
    ) -> Result<u64> {
        let proposal_id = self.global_proposals.len() as u64 + 1;
        let clock = Clock::get()?;

        let proposal = GlobalProposal {
            proposal_id,
            title,
            description_hash,
            proposer_chain,
            proposer_address,
            target_chains: target_chains.clone(),
            proposal_type,
            created_at: clock.unix_timestamp,
            voting_starts_at: clock.unix_timestamp + 3600, // 1 hour delay
            voting_ends_at: clock.unix_timestamp + 3600 + voting_period,
            execution_time: None,
            status: GlobalProposalStatus::Active,
        };

        self.global_proposals.insert(proposal_id, proposal);

        // Initialize cross-chain vote data
        let mut chain_votes = BTreeMap::new();
        for chain_id in target_chains {
            chain_votes.insert(chain_id, ChainVoteData {
                chain_id,
                votes_for: 0,
                votes_against: 0,
                abstains: 0,
                total_voting_power: 0,
                participation_rate: 0,
                last_updated: clock.unix_timestamp,
            });
        }

        let vote_data = CrossChainVoteData {
            proposal_id,
            chain_votes,
            total_voting_power: 0,
            votes_for: 0,
            votes_against: 0,
            abstains: 0,
            quorum_reached: false,
            weighted_result: VoteResult::Pending,
        };

        self.cross_chain_votes.insert(proposal_id, vote_data);

        Ok(proposal_id)
    }

    pub fn aggregate_votes(&mut self, proposal_id: u64) -> Result<VoteResult> {
        let vote_data = self.cross_chain_votes.get_mut(&proposal_id)
            .ok_or(CrossChainError::ProposalNotFound)?;

        let mut total_weight = 0u64;
        let mut weighted_votes_for = 0u64;
        let mut weighted_votes_against = 0u64;

        for (chain_id, chain_vote) in &vote_data.chain_votes {
            if let Some(config) = self.chain_configs.get(chain_id) {
                let weight = config.governance_weight as u64;
                total_weight += weight;

                let chain_total = chain_vote.votes_for + chain_vote.votes_against + chain_vote.abstains;
                if chain_total > 0 {
                    let for_percentage = (chain_vote.votes_for * 10000) / chain_total;
                    let against_percentage = (chain_vote.votes_against * 10000) / chain_total;

                    weighted_votes_for += (weight * for_percentage) / 10000;
                    weighted_votes_against += (weight * against_percentage) / 10000;
                }
            }
        }

        // Calculate result based on aggregation rules
        let result = if weighted_votes_for > weighted_votes_against {
            VoteResult::Approved
        } else if weighted_votes_against > weighted_votes_for {
            VoteResult::Rejected
        } else {
            VoteResult::Tied
        };

        vote_data.weighted_result = result.clone();
        Ok(result)
    }
}

// Error types for cross-chain functionality
#[error_code]
pub enum CrossChainError {
    #[msg("Chain not supported by bridge")]
    UnsupportedChain,
    #[msg("Transfer amount exceeds maximum allowed")]
    TransferAmountExceeded,
    #[msg("Transfer not found")]
    TransferNotFound,
    #[msg("Operator not authorized")]
    UnauthorizedOperator,
    #[msg("Transfer already confirmed by this operator")]
    AlreadyConfirmed,
    #[msg("Proposal not found")]
    ProposalNotFound,
    #[msg("Invalid chain configuration")]
    InvalidChainConfig,
    #[msg("Cross-chain message verification failed")]
    MessageVerificationFailed,
    #[msg("Light client verification failed")]
    LightClientVerificationFailed,
    #[msg("State synchronization conflict")]
    StateSyncConflict,
    #[msg("Delegation scope not supported")]
    UnsupportedDelegationScope,
    #[msg("Reputation sync failed")]
    ReputationSyncFailed,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cross_chain_transfer() {
        let mut bridge = CrossChainBridge {
            supported_chains: {
                let mut chains = BTreeMap::new();
                chains.insert(ChainId::ETHEREUM, ChainInfo {
                    chain_id: ChainId::ETHEREUM,
                    name: "Ethereum".to_string(),
                    native_token: "ETH".to_string(),
                    governance_contract: "0x123...".to_string(),
                    bridge_contract: "0x456...".to_string(),
                    is_active: true,
                    min_confirmation_blocks: 12,
                    gas_limits: GasLimits {
                        vote_transaction: 100000,
                        proposal_transaction: 200000,
                        delegation_transaction: 150000,
                        emergency_transaction: 300000,
                    },
                    supported_tokens: vec![],
                });
                chains.insert(ChainId::SOLANA, ChainInfo {
                    chain_id: ChainId::SOLANA,
                    name: "Solana".to_string(),
                    native_token: "SOL".to_string(),
                    governance_contract: "11111111111111111111111111111112".to_string(),
                    bridge_contract: "11111111111111111111111111111113".to_string(),
                    is_active: true,
                    min_confirmation_blocks: 32,
                    gas_limits: GasLimits {
                        vote_transaction: 5000,
                        proposal_transaction: 10000,
                        delegation_transaction: 7500,
                        emergency_transaction: 15000,
                    },
                    supported_tokens: vec![],
                });
                chains
            },
            bridge_operators: vec![Pubkey::new_unique()],
            multi_sig_threshold: 1,
            pending_transfers: BTreeMap::new(),
            completed_transfers: vec![],
            bridge_stats: BridgeStatistics {
                total_transfers: 0,
                total_volume: 0,
                failed_transfers: 0,
                average_confirmation_time: 0,
                total_fees_collected: 0,
                active_operators: 1,
                uptime_percentage: 10000,
            },
            security_config: BridgeSecurityConfig {
                max_daily_volume: 1000000,
                max_single_transfer: 100000,
                operator_bond_required: 10000,
                slash_percentage: 1000,
                emergency_pause_enabled: true,
                rate_limit_per_user: 10,
                suspicious_activity_threshold: 500,
            },
            bump: 0,
        };

        let transfer_id = bridge.initiate_transfer(
            ChainId::ETHEREUM,
            ChainId::SOLANA,
            TransferType::GovernanceTokens,
            1000,
            "11111111111111111111111111111114".to_string(),
            Pubkey::new_unique(),
        ).unwrap();

        assert!(!transfer_id.is_empty());
        assert_eq!(bridge.pending_transfers.len(), 1);
        assert_eq!(bridge.bridge_stats.total_transfers, 1);
    }

    #[test]
    fn test_governance_aggregator() {
        let mut aggregator = GovernanceAggregator {
            chain_configs: {
                let mut configs = BTreeMap::new();
                configs.insert(ChainId::ETHEREUM, ChainGovernanceConfig {
                    chain_id: ChainId::ETHEREUM,
                    governance_weight: 5000, // 50%
                    quorum_requirement: 3000, // 30%
                    voting_period: 86400, // 1 day
                    execution_delay: 3600, // 1 hour
                    emergency_threshold: 8000, // 80%
                    is_active: true,
                });
                configs.insert(ChainId::SOLANA, ChainGovernanceConfig {
                    chain_id: ChainId::SOLANA,
                    governance_weight: 5000, // 50%
                    quorum_requirement: 3000, // 30%
                    voting_period: 86400,
                    execution_delay: 3600,
                    emergency_threshold: 8000,
                    is_active: true,
                });
                configs
            },
            global_proposals: BTreeMap::new(),
            cross_chain_votes: BTreeMap::new(),
            delegation_registry: CrossChainDelegationRegistry {
                delegations: BTreeMap::new(),
                delegation_trees: BTreeMap::new(),
                max_delegation_depth: 3,
                total_delegated_power: 0,
            },
            reputation_system: CrossChainReputationSystem {
                user_reputations: BTreeMap::new(),
                reputation_weights: BTreeMap::new(),
                global_reputation_metrics: GlobalReputationMetrics {
                    total_participants: 0,
                    active_cross_chain_participants: 0,
                    average_reputation_score: 0,
                    reputation_distribution: ReputationDistribution {
                        low_reputation: 0,
                        medium_reputation: 0,
                        high_reputation: 0,
                        elite_reputation: 0,
                    },
                    top_contributors: vec![],
                },
                reputation_sync_interval: 3600,
                last_sync: 0,
            },
            aggregation_rules: AggregationRules {
                vote_weighting_method: VoteWeightingMethod::Equal,
                quorum_calculation: QuorumCalculation::GlobalQuorum(3000),
                conflict_resolution: ConflictResolutionMethod::MajorityRule,
                finality_requirements: FinalityRequirements {
                    min_chain_confirmations: BTreeMap::new(),
                    min_time_delay: 3600,
                    required_validator_signatures: 3,
                    slashing_conditions: vec![],
                },
            },
            bump: 0,
        };

        let proposal_id = aggregator.create_global_proposal(
            "Test Proposal".to_string(),
            [0u8; 32],
            ChainId::ETHEREUM,
            "0x123...".to_string(),
            vec![ChainId::ETHEREUM, ChainId::SOLANA],
            GlobalProposalType::ConfigurationChange,
            86400,
        ).unwrap();

        assert_eq!(proposal_id, 1);
        assert_eq!(aggregator.global_proposals.len(), 1);
        assert_eq!(aggregator.cross_chain_votes.len(), 1);
    }
}