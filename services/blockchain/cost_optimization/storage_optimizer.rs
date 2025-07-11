use anchor_lang::prelude::*;
use std::collections::{BTreeMap, HashMap};

// Ultra-efficient storage optimization for cost reduction

// Compressed data structures for minimal on-chain storage
#[account]
#[derive(InitSpace)]
pub struct CompressedGovernanceState {
    pub authority: Pubkey,                    // 32 bytes (required)
    pub principle_hashes: Vec<[u8; 8]>,      // 8-byte truncated hashes instead of 32
    pub total_policies: u16,                  // u16 instead of u32 (saves 2 bytes)
    pub active_proposals: u8,                 // u8 instead of u32 (max 255 active)
    pub flags: GovernanceFlags,               // Packed boolean flags
    pub initialization_timestamp: u32,        // u32 timestamp (relative to 2024)
    pub bump: u8,
}

// Bit-packed flags to save space
#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct GovernanceFlags {
    pub packed_flags: u8, // 8 boolean flags in 1 byte
}

impl GovernanceFlags {
    pub fn new() -> Self {
        Self { packed_flags: 0 }
    }

    pub fn set_emergency_mode(&mut self, enabled: bool) {
        if enabled {
            self.packed_flags |= 0b00000001;
        } else {
            self.packed_flags &= 0b11111110;
        }
    }

    pub fn emergency_mode(&self) -> bool {
        self.packed_flags & 0b00000001 != 0
    }

    pub fn set_paused(&mut self, paused: bool) {
        if paused {
            self.packed_flags |= 0b00000010;
        } else {
            self.packed_flags &= 0b11111101;
        }
    }

    pub fn is_paused(&self) -> bool {
        self.packed_flags & 0b00000010 != 0
    }
}

// Minimal proposal structure (stores only essentials on-chain)
#[account]
#[derive(InitSpace)]
pub struct CompressedProposal {
    pub policy_id: u32,                      // u32 instead of u64
    pub title_hash: [u8; 8],                 // 8-byte hash of title
    pub content_hash: [u8; 16],              // 16-byte hash of content
    pub proposer_id: [u8; 8],                // 8-byte hash of proposer
    pub timestamps: PackedTimestamps,         // Packed timestamps
    pub vote_data: PackedVoteData,           // Packed voting data
    pub status_flags: u8,                    // Packed status information
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct PackedTimestamps {
    pub created_offset: u16,     // Hours since base timestamp
    pub voting_duration: u8,     // Voting period in hours (max 255)
    pub finalized_offset: u16,   // Hours since base timestamp (0 if not finalized)
}

impl PackedTimestamps {
    const BASE_TIMESTAMP: i64 = 1704067200; // Jan 1, 2024

    pub fn new(created_at: i64, voting_period_hours: u8) -> Self {
        let created_offset = ((created_at - Self::BASE_TIMESTAMP) / 3600) as u16;
        Self {
            created_offset,
            voting_duration: voting_period_hours,
            finalized_offset: 0,
        }
    }

    pub fn get_created_timestamp(&self) -> i64 {
        Self::BASE_TIMESTAMP + (self.created_offset as i64 * 3600)
    }

    pub fn get_voting_end_timestamp(&self) -> i64 {
        self.get_created_timestamp() + (self.voting_duration as i64 * 3600)
    }

    pub fn set_finalized(&mut self, finalized_at: i64) {
        self.finalized_offset = ((finalized_at - Self::BASE_TIMESTAMP) / 3600) as u16;
    }

    pub fn get_finalized_timestamp(&self) -> Option<i64> {
        if self.finalized_offset == 0 {
            None
        } else {
            Some(Self::BASE_TIMESTAMP + (self.finalized_offset as i64 * 3600))
        }
    }
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct PackedVoteData {
    pub votes_for_scaled: u16,      // Scaled down by 1000
    pub votes_against_scaled: u16,  // Scaled down by 1000
    pub total_voters: u8,           // Max 255 voters
    pub quorum_flags: u8,          // Quorum status and other flags
}

impl PackedVoteData {
    const SCALE_FACTOR: u64 = 1000;

    pub fn new() -> Self {
        Self {
            votes_for_scaled: 0,
            votes_against_scaled: 0,
            total_voters: 0,
            quorum_flags: 0,
        }
    }

    pub fn add_vote(&mut self, vote_for: bool, voting_power: u64) -> Result<()> {
        let scaled_power = (voting_power / Self::SCALE_FACTOR) as u16;
        
        if vote_for {
            self.votes_for_scaled = self.votes_for_scaled
                .checked_add(scaled_power)
                .ok_or(StorageError::VoteOverflow)?;
        } else {
            self.votes_against_scaled = self.votes_against_scaled
                .checked_add(scaled_power)
                .ok_or(StorageError::VoteOverflow)?;
        }

        self.total_voters = self.total_voters
            .checked_add(1)
            .ok_or(StorageError::VoterOverflow)?;

        Ok(())
    }

    pub fn get_votes_for(&self) -> u64 {
        self.votes_for_scaled as u64 * Self::SCALE_FACTOR
    }

    pub fn get_votes_against(&self) -> u64 {
        self.votes_against_scaled as u64 * Self::SCALE_FACTOR
    }

    pub fn set_quorum_reached(&mut self, reached: bool) {
        if reached {
            self.quorum_flags |= 0b00000001;
        } else {
            self.quorum_flags &= 0b11111110;
        }
    }

    pub fn quorum_reached(&self) -> bool {
        self.quorum_flags & 0b00000001 != 0
    }
}

// Off-chain storage registry for large data
#[account]
#[derive(InitSpace)]
pub struct OffChainRegistry {
    pub storage_providers: BTreeMap<u8, StorageProvider>, // Max 255 providers
    pub content_index: BTreeMap<[u8; 16], ContentMetadata>, // Content hash -> metadata
    pub cost_statistics: OffChainCostStats,
    pub cleanup_schedule: Vec<CleanupTask>,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct StorageProvider {
    pub provider_id: u8,
    pub name: String,
    #[max_len(100)]
    pub endpoint_url: String,
    pub cost_per_mb_per_month: u32,      // Cost in lamports
    pub reliability_score: u8,           // 0-100
    pub max_file_size_mb: u16,
    pub supported_formats: Vec<u8>,      // Format IDs
    pub is_active: bool,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ContentMetadata {
    pub content_hash: [u8; 16],
    pub storage_provider_id: u8,
    pub file_size_bytes: u32,
    pub content_type: ContentType,
    pub upload_timestamp: u32,           // Relative to base timestamp
    pub access_count: u16,
    pub last_accessed: u32,              // Relative to base timestamp
    pub compression_ratio: u8,           // Percentage (0-100)
    pub retrieval_cost: u16,             // Cost in lamports
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum ContentType {
    ProposalText,
    Evidence,
    Documentation,
    Image,
    Video,
    Archive,
    Other,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct OffChainCostStats {
    pub total_storage_cost_monthly: u32,
    pub total_retrieval_cost: u32,
    pub storage_efficiency_ratio: u8,    // Percentage
    pub bandwidth_saved: u32,            // Bytes saved by compression
    pub cost_saved_vs_onchain: u32,     // Lamports saved
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct CleanupTask {
    pub task_id: u16,
    pub content_hash: [u8; 16],
    pub cleanup_type: CleanupType,
    pub scheduled_time: u32,             // Relative timestamp
    pub estimated_savings: u16,          // Lamports
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum CleanupType {
    Delete,
    Archive,
    Compress,
    Migrate,
}

// Data compression utilities
pub struct DataCompressor;

impl DataCompressor {
    // Simple run-length encoding for repetitive data
    pub fn compress_votes(votes: &[bool]) -> Vec<u8> {
        let mut compressed = Vec::new();
        if votes.is_empty() {
            return compressed;
        }

        let mut current_value = votes[0];
        let mut count = 1u8;

        for &vote in votes.iter().skip(1) {
            if vote == current_value && count < 255 {
                count += 1;
            } else {
                compressed.push(if current_value { 0x80 | count } else { count });
                current_value = vote;
                count = 1;
            }
        }
        
        // Push the last run
        compressed.push(if current_value { 0x80 | count } else { count });
        compressed
    }

    pub fn decompress_votes(compressed: &[u8]) -> Vec<bool> {
        let mut votes = Vec::new();
        
        for &byte in compressed {
            let value = (byte & 0x80) != 0; // Extract boolean from high bit
            let count = byte & 0x7F;        // Extract count from low 7 bits
            
            for _ in 0..count {
                votes.push(value);
            }
        }
        
        votes
    }

    // Dictionary compression for common strings
    pub fn create_string_dictionary(strings: &[String]) -> (Vec<u8>, HashMap<String, u8>) {
        let mut dictionary = HashMap::new();
        let mut compressed = Vec::new();
        let mut dict_id = 0u8;

        for string in strings {
            if let Some(&id) = dictionary.get(string) {
                compressed.push(id);
            } else if dict_id < 255 {
                dictionary.insert(string.clone(), dict_id);
                compressed.push(dict_id);
                dict_id += 1;
            } else {
                // Dictionary full, use raw encoding
                compressed.push(255); // Escape code
                compressed.extend(string.as_bytes());
                compressed.push(0);   // Null terminator
            }
        }

        (compressed, dictionary)
    }

    // Hash-based deduplication
    pub fn deduplicate_content(contents: &[Vec<u8>]) -> (Vec<[u8; 16]>, HashMap<[u8; 16], Vec<u8>>) {
        let mut unique_content = HashMap::new();
        let mut hash_list = Vec::new();

        for content in contents {
            let hash = Self::hash_content(content);
            hash_list.push(hash);
            
            if !unique_content.contains_key(&hash) {
                unique_content.insert(hash, content.clone());
            }
        }

        (hash_list, unique_content)
    }

    fn hash_content(content: &[u8]) -> [u8; 16] {
        use anchor_lang::solana_program::hash::hash;
        let full_hash = hash(content);
        let mut short_hash = [0u8; 16];
        short_hash.copy_from_slice(&full_hash.to_bytes()[..16]);
        short_hash
    }
}

// Cost-optimized vote record
#[account]
#[derive(InitSpace)]
pub struct CompressedVoteRecord {
    pub voter_hash: [u8; 8],             // 8-byte hash of voter
    pub proposal_id: u16,                // u16 instead of u64
    pub vote_data: u8,                   // Packed: vote (1 bit) + power tier (3 bits) + flags (4 bits)
    pub timestamp_offset: u16,           // Hours since base timestamp
    pub bump: u8,
}

impl CompressedVoteRecord {
    pub fn new(voter: &Pubkey, proposal_id: u16, vote: bool, voting_power: u64, timestamp: i64) -> Self {
        let voter_hash = Self::hash_voter(voter);
        let power_tier = Self::voting_power_to_tier(voting_power);
        let vote_data = Self::pack_vote_data(vote, power_tier, 0);
        let timestamp_offset = ((timestamp - PackedTimestamps::BASE_TIMESTAMP) / 3600) as u16;

        Self {
            voter_hash,
            proposal_id,
            vote_data,
            timestamp_offset,
            bump: 0,
        }
    }

    fn hash_voter(voter: &Pubkey) -> [u8; 8] {
        use anchor_lang::solana_program::hash::hash;
        let full_hash = hash(voter.as_ref());
        let mut short_hash = [0u8; 8];
        short_hash.copy_from_slice(&full_hash.to_bytes()[..8]);
        short_hash
    }

    fn voting_power_to_tier(power: u64) -> u8 {
        match power {
            0..=999 => 0,
            1000..=9999 => 1,
            10000..=99999 => 2,
            100000..=999999 => 3,
            1000000..=9999999 => 4,
            10000000..=99999999 => 5,
            100000000..=999999999 => 6,
            _ => 7,
        }
    }

    fn tier_to_voting_power(tier: u8) -> u64 {
        match tier {
            0 => 500,
            1 => 5000,
            2 => 50000,
            3 => 500000,
            4 => 5000000,
            5 => 50000000,
            6 => 500000000,
            _ => 1000000000,
        }
    }

    fn pack_vote_data(vote: bool, power_tier: u8, flags: u8) -> u8 {
        let vote_bit = if vote { 0x80 } else { 0x00 };
        let power_bits = (power_tier & 0x07) << 4;
        let flag_bits = flags & 0x0F;
        vote_bit | power_bits | flag_bits
    }

    pub fn get_vote(&self) -> bool {
        (self.vote_data & 0x80) != 0
    }

    pub fn get_voting_power_estimate(&self) -> u64 {
        let tier = (self.vote_data >> 4) & 0x07;
        Self::tier_to_voting_power(tier)
    }

    pub fn get_timestamp(&self) -> i64 {
        PackedTimestamps::BASE_TIMESTAMP + (self.timestamp_offset as i64 * 3600)
    }
}

// Storage analytics for cost optimization
#[account]
#[derive(InitSpace)]
pub struct StorageAnalytics {
    pub total_accounts: u32,
    pub storage_usage_by_type: BTreeMap<u8, StorageTypeUsage>, // Type ID -> usage
    pub compression_statistics: CompressionStatistics,
    pub cost_breakdown: CostBreakdown,
    pub optimization_opportunities: Vec<OptimizationOpportunity>,
    pub last_analysis: u32,                                    // Relative timestamp
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct StorageTypeUsage {
    pub account_type: u8,           // Type identifier
    pub account_count: u32,
    pub total_bytes: u32,
    pub average_bytes_per_account: u16,
    pub rent_cost_per_account: u32,
    pub total_rent_cost: u32,
    pub compression_ratio: u8,      // Percentage
    pub optimization_potential: u8, // Percentage
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct CompressionStatistics {
    pub original_size_bytes: u32,
    pub compressed_size_bytes: u32,
    pub compression_ratio: u8,      // Percentage
    pub space_saved_bytes: u32,
    pub cost_saved_lamports: u32,
    pub compression_techniques_used: Vec<u8>, // Technique IDs
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct CostBreakdown {
    pub account_creation_cost: u32,
    pub rent_cost_monthly: u32,
    pub transaction_fees: u32,
    pub off_chain_storage_cost: u32,
    pub bandwidth_cost: u32,
    pub total_cost_monthly: u32,
    pub cost_per_user: u32,
    pub cost_per_transaction: u16,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct OptimizationOpportunity {
    pub opportunity_id: u8,
    pub opportunity_type: OptimizationType,
    pub potential_savings_lamports: u32,
    pub potential_savings_percentage: u8,
    pub implementation_effort: u8,       // 1-10 scale
    pub estimated_implementation_days: u8,
    pub description: String,
    #[max_len(50)]
    pub technical_details: String,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum OptimizationType {
    DataCompression,
    OffChainMigration,
    AccountConsolidation,
    DataDeduplication,
    ArchiveOldData,
    OptimizeDataStructures,
    ImplementCaching,
    BatchOperations,
}

// Implementation of storage optimization
impl CompressedGovernanceState {
    pub fn from_regular_state(
        authority: Pubkey,
        principles: &[String],
        total_policies: u32,
        active_proposals: u32,
        emergency_mode: bool,
        initialized_at: i64,
    ) -> Result<Self> {
        // Convert principles to 8-byte hashes
        let principle_hashes: Vec<[u8; 8]> = principles.iter()
            .map(|p| {
                use anchor_lang::solana_program::hash::hash;
                let full_hash = hash(p.as_bytes());
                let mut short_hash = [0u8; 8];
                short_hash.copy_from_slice(&full_hash.to_bytes()[..8]);
                short_hash
            })
            .collect();

        // Convert to smaller types with bounds checking
        let total_policies = std::cmp::min(total_policies, u16::MAX as u32) as u16;
        let active_proposals = std::cmp::min(active_proposals, u8::MAX as u32) as u8;
        
        let mut flags = GovernanceFlags::new();
        flags.set_emergency_mode(emergency_mode);

        let initialization_timestamp = ((initialized_at - PackedTimestamps::BASE_TIMESTAMP) / 3600) as u32;

        Ok(Self {
            authority,
            principle_hashes,
            total_policies,
            active_proposals,
            flags,
            initialization_timestamp,
            bump: 0,
        })
    }

    pub fn get_storage_savings() -> StorageSavings {
        let original_size = 32 + (32 * 100) + 4 + 4 + 1 + 8 + 1; // Original structure
        let compressed_size = 32 + (8 * 100) + 2 + 1 + 1 + 4 + 1; // Compressed structure
        
        StorageSavings {
            original_bytes: original_size,
            compressed_bytes: compressed_size,
            bytes_saved: original_size - compressed_size,
            compression_ratio: ((compressed_size * 100) / original_size) as u8,
            estimated_cost_savings_lamports: ((original_size - compressed_size) * 10) as u32, // ~10 lamports per byte
        }
    }
}

pub struct StorageSavings {
    pub original_bytes: usize,
    pub compressed_bytes: usize,
    pub bytes_saved: usize,
    pub compression_ratio: u8,
    pub estimated_cost_savings_lamports: u32,
}

// Error types for storage optimization
#[error_code]
pub enum StorageError {
    #[msg("Vote count overflow in compressed format")]
    VoteOverflow,
    #[msg("Voter count overflow (max 255)")]
    VoterOverflow,
    #[msg("Content too large for compression")]
    ContentTooLarge,
    #[msg("Invalid compression format")]
    InvalidCompressionFormat,
    #[msg("Decompression failed")]
    DecompressionFailed,
    #[msg("Storage provider not found")]
    StorageProviderNotFound,
    #[msg("Off-chain storage failed")]
    OffChainStorageFailed,
    #[msg("Content not found in off-chain storage")]
    ContentNotFound,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_data_compression() {
        let votes = vec![true, true, true, false, false, true];
        let compressed = DataCompressor::compress_votes(&votes);
        let decompressed = DataCompressor::decompress_votes(&compressed);
        
        assert_eq!(votes, decompressed);
        assert!(compressed.len() < votes.len()); // Should be smaller
    }

    #[test]
    fn test_packed_timestamps() {
        let created_at = 1704067200 + 86400; // 1 day after base
        let timestamps = PackedTimestamps::new(created_at, 24); // 24 hour voting period
        
        assert_eq!(timestamps.get_created_timestamp(), created_at);
        assert_eq!(timestamps.get_voting_end_timestamp(), created_at + 86400);
        
        timestamps.set_finalized(created_at + 172800); // 2 days later
        assert!(timestamps.get_finalized_timestamp().is_some());
    }

    #[test]
    fn test_vote_data_packing() {
        let mut vote_data = PackedVoteData::new();
        
        assert!(vote_data.add_vote(true, 50000).is_ok());  // 50 scaled
        assert!(vote_data.add_vote(false, 30000).is_ok()); // 30 scaled
        
        assert_eq!(vote_data.get_votes_for(), 50000);
        assert_eq!(vote_data.get_votes_against(), 30000);
        assert_eq!(vote_data.total_voters, 2);
    }

    #[test]
    fn test_compressed_vote_record() {
        let voter = Pubkey::new_unique();
        let record = CompressedVoteRecord::new(&voter, 123, true, 50000, 1704067200 + 3600);
        
        assert!(record.get_vote());
        assert_eq!(record.get_voting_power_estimate(), 50000);
        assert_eq!(record.proposal_id, 123);
    }

    #[test]
    fn test_storage_savings() {
        let savings = CompressedGovernanceState::get_storage_savings();
        
        assert!(savings.bytes_saved > 0);
        assert!(savings.compression_ratio < 100);
        assert!(savings.estimated_cost_savings_lamports > 0);
    }

    #[test]
    fn test_governance_flags() {
        let mut flags = GovernanceFlags::new();
        
        assert!(!flags.emergency_mode());
        flags.set_emergency_mode(true);
        assert!(flags.emergency_mode());
        
        assert!(!flags.is_paused());
        flags.set_paused(true);
        assert!(flags.is_paused());
        
        // Both flags should be set
        assert_eq!(flags.packed_flags, 0b00000011);
    }

    #[test]
    fn test_string_dictionary_compression() {
        let strings = vec![
            "governance".to_string(),
            "proposal".to_string(),
            "governance".to_string(), // Duplicate
            "vote".to_string(),
            "proposal".to_string(),   // Duplicate
        ];
        
        let (compressed, dictionary) = DataCompressor::create_string_dictionary(&strings);
        
        assert_eq!(compressed.len(), 5);
        assert_eq!(dictionary.len(), 3); // Only unique strings
        assert!(dictionary.contains_key("governance"));
        assert!(dictionary.contains_key("proposal"));
        assert!(dictionary.contains_key("vote"));
    }
}