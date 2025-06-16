// transaction_optimizer.rs
// Solana Transaction Optimization Module for Quantumagi
// Target: Reduce governance costs to <0.01 SOL per action through batching

use anchor_lang::prelude::*;
use std::collections::HashMap;

/// Transaction batching configuration
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct BatchConfig {
    /// Maximum number of instructions per batch (Solana limit: ~10)
    pub max_batch_size: u8,
    /// Timeout for batch accumulation in seconds
    pub batch_timeout_seconds: u64,
    /// Cost optimization target in lamports
    pub cost_target_lamports: u64,
    /// Enable/disable batching
    pub enabled: bool,
}

impl Default for BatchConfig {
    fn default() -> Self {
        Self {
            max_batch_size: 10,
            batch_timeout_seconds: 5,
            cost_target_lamports: 10_000_000, // 0.01 SOL
            enabled: true,
        }
    }
}

/// Governance operation types that can be batched
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq)]
pub enum GovernanceOperation {
    PolicyProposal {
        policy_id: u64,
        rule_hash: [u8; 32],
    },
    PolicyVote {
        policy_id: u64,
        vote: bool,
    },
    PolicyEnactment {
        policy_id: u64,
    },
    ComplianceCheck {
        policy_id: u64,
        action_hash: [u8; 32],
    },
    ConstitutionalUpdate {
        version: u32,
        hash: [u8; 32],
    },
}

/// Batch operation metadata for cost estimation
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct BatchOperation {
    pub operation: GovernanceOperation,
    pub estimated_compute_units: u32,
    pub estimated_account_writes: u8,
    pub priority_score: u8, // 1-10, higher = more urgent
}

/// Transaction batch for governance operations
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct GovernanceBatch {
    pub batch_id: [u8; 16],
    pub operations: Vec<BatchOperation>,
    pub total_compute_units: u32,
    pub total_account_writes: u8,
    pub estimated_cost_lamports: u64,
    pub created_at: i64,
    pub expires_at: i64,
}

impl GovernanceBatch {
    /// Create new governance batch
    pub fn new(batch_id: [u8; 16], config: &BatchConfig) -> Self {
        let current_time = Clock::get().unwrap().unix_timestamp;

        Self {
            batch_id,
            operations: Vec::new(),
            total_compute_units: 0,
            total_account_writes: 0,
            estimated_cost_lamports: 0,
            created_at: current_time,
            expires_at: current_time + config.batch_timeout_seconds as i64,
        }
    }

    /// Add operation to batch if it fits within limits
    pub fn try_add_operation(
        &mut self,
        operation: BatchOperation,
        config: &BatchConfig,
    ) -> Result<bool> {
        // Check batch size limit
        if self.operations.len() >= config.max_batch_size as usize {
            return Ok(false);
        }

        // Check compute unit limit (Solana limit: ~1.4M CU per transaction)
        let new_compute_total = self.total_compute_units + operation.estimated_compute_units;
        if new_compute_total > 1_200_000 {
            // Conservative limit
            return Ok(false);
        }

        // Check account write limit (affects transaction size)
        let new_writes_total = self.total_account_writes + operation.estimated_account_writes;
        if new_writes_total > 64 {
            // Conservative limit for transaction size
            return Ok(false);
        }

        // Add operation to batch
        self.total_compute_units = new_compute_total;
        self.total_account_writes = new_writes_total;
        self.estimated_cost_lamports = self.calculate_estimated_cost();
        self.operations.push(operation);

        Ok(true)
    }

    /// Calculate estimated transaction cost in lamports
    fn calculate_estimated_cost(&self) -> u64 {
        // Base transaction fee (5000 lamports)
        let base_fee = 5_000u64;

        // Compute unit fee (prioritization fee)
        let compute_fee = (self.total_compute_units as u64 * 1) / 1000; // ~1 lamport per 1000 CU

        // Account rent exemption estimates
        let rent_fee = self.total_account_writes as u64 * 2_000; // ~2000 lamports per account

        // Signature fees (1 signature per operation for simplicity)
        let signature_fee = self.operations.len() as u64 * 5_000;

        base_fee + compute_fee + rent_fee + signature_fee
    }

    /// Check if batch is ready for execution
    pub fn is_ready_for_execution(&self, config: &BatchConfig) -> bool {
        if !config.enabled {
            return false;
        }

        let current_time = Clock::get().unwrap().unix_timestamp;

        // Execute if batch is full or timeout reached
        self.operations.len() >= config.max_batch_size as usize
            || current_time >= self.expires_at
            || self.estimated_cost_lamports <= config.cost_target_lamports
    }

    /// Get cost optimization percentage compared to individual transactions
    pub fn get_cost_optimization(&self) -> f64 {
        if self.operations.is_empty() {
            return 0.0;
        }

        // Estimate cost if operations were executed individually
        let individual_cost: u64 = self
            .operations
            .iter()
            .map(|op| {
                // Base cost per individual transaction
                5_000 + // Base fee
                (op.estimated_compute_units as u64 * 1) / 1000 + // Compute fee
                op.estimated_account_writes as u64 * 2_000 + // Rent fee
                5_000 // Signature fee
            })
            .sum();

        if individual_cost == 0 {
            return 0.0;
        }

        let savings = individual_cost.saturating_sub(self.estimated_cost_lamports);
        (savings as f64 / individual_cost as f64) * 100.0
    }
}

/// Transaction optimizer for governance operations
pub struct TransactionOptimizer {
    config: BatchConfig,
    pending_batches: HashMap<[u8; 16], GovernanceBatch>,
    operation_estimates: HashMap<GovernanceOperation, (u32, u8)>, // (compute_units, account_writes)
}

impl TransactionOptimizer {
    /// Create new transaction optimizer
    pub fn new(config: BatchConfig) -> Self {
        let mut operation_estimates = HashMap::new();

        // Initialize operation cost estimates based on Quantumagi program analysis
        operation_estimates.insert(
            GovernanceOperation::PolicyProposal {
                policy_id: 0,
                rule_hash: [0; 32],
            },
            (50_000, 2), // Policy creation: moderate compute, 2 account writes
        );
        operation_estimates.insert(
            GovernanceOperation::PolicyVote {
                policy_id: 0,
                vote: true,
            },
            (25_000, 2), // Voting: low compute, 2 account writes
        );
        operation_estimates.insert(
            GovernanceOperation::PolicyEnactment { policy_id: 0 },
            (30_000, 1), // Enactment: low-moderate compute, 1 account write
        );
        operation_estimates.insert(
            GovernanceOperation::ComplianceCheck {
                policy_id: 0,
                action_hash: [0; 32],
            },
            (40_000, 0), // Compliance: moderate compute, read-only
        );
        operation_estimates.insert(
            GovernanceOperation::ConstitutionalUpdate {
                version: 0,
                hash: [0; 32],
            },
            (60_000, 1), // Constitutional update: high compute, 1 account write
        );

        Self {
            config,
            pending_batches: HashMap::new(),
            operation_estimates,
        }
    }

    /// Add operation to optimizer for batching
    pub fn add_operation(
        &mut self,
        operation: GovernanceOperation,
        priority: u8,
    ) -> Result<[u8; 16]> {
        // Get operation estimates
        let (compute_units, account_writes) = self
            .operation_estimates
            .get(&operation)
            .copied()
            .unwrap_or((30_000, 1)); // Default estimates

        let batch_operation = BatchOperation {
            operation: operation.clone(),
            estimated_compute_units: compute_units,
            estimated_account_writes: account_writes,
            priority_score: priority,
        };

        // Try to add to existing batch or create new one
        let batch_id = self.find_or_create_batch(&batch_operation)?;

        Ok(batch_id)
    }

    /// Find suitable batch or create new one
    fn find_or_create_batch(&mut self, operation: &BatchOperation) -> Result<[u8; 16]> {
        // Try to add to existing batch
        for (batch_id, batch) in self.pending_batches.iter_mut() {
            if batch.try_add_operation(operation.clone(), &self.config)? {
                return Ok(*batch_id);
            }
        }

        // Create new batch
        let batch_id = self.generate_batch_id();
        let mut new_batch = GovernanceBatch::new(batch_id, &self.config);
        new_batch.try_add_operation(operation.clone(), &self.config)?;

        self.pending_batches.insert(batch_id, new_batch);
        Ok(batch_id)
    }

    /// Generate unique batch ID
    fn generate_batch_id(&self) -> [u8; 16] {
        let clock = Clock::get().unwrap();
        let mut id = [0u8; 16];

        // Use timestamp and slot for uniqueness
        let timestamp_bytes = clock.unix_timestamp.to_le_bytes();
        let slot_bytes = clock.slot.to_le_bytes();

        id[0..8].copy_from_slice(&timestamp_bytes);
        id[8..16].copy_from_slice(&slot_bytes);

        id
    }

    /// Get ready batches for execution
    pub fn get_ready_batches(&mut self) -> Vec<GovernanceBatch> {
        let mut ready_batches = Vec::new();
        let mut batch_ids_to_remove = Vec::new();

        for (batch_id, batch) in &self.pending_batches {
            if batch.is_ready_for_execution(&self.config) {
                ready_batches.push(batch.clone());
                batch_ids_to_remove.push(*batch_id);
            }
        }

        // Remove ready batches from pending
        for batch_id in batch_ids_to_remove {
            self.pending_batches.remove(&batch_id);
        }

        ready_batches
    }

    /// Get optimization statistics
    pub fn get_optimization_stats(&self) -> OptimizationStats {
        let total_operations: usize = self
            .pending_batches
            .values()
            .map(|batch| batch.operations.len())
            .sum();

        let total_estimated_savings: f64 = self
            .pending_batches
            .values()
            .map(|batch| batch.get_cost_optimization())
            .sum();

        let avg_batch_size = if self.pending_batches.is_empty() {
            0.0
        } else {
            total_operations as f64 / self.pending_batches.len() as f64
        };

        OptimizationStats {
            pending_batches: self.pending_batches.len(),
            total_pending_operations: total_operations,
            average_batch_size: avg_batch_size,
            estimated_cost_savings_percent: if self.pending_batches.is_empty() {
                0.0
            } else {
                total_estimated_savings / self.pending_batches.len() as f64
            },
            target_cost_lamports: self.config.cost_target_lamports,
            batching_enabled: self.config.enabled,
        }
    }
}

/// Optimization statistics
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct OptimizationStats {
    pub pending_batches: usize,
    pub total_pending_operations: usize,
    pub average_batch_size: f64,
    pub estimated_cost_savings_percent: f64,
    pub target_cost_lamports: u64,
    pub batching_enabled: bool,
}
