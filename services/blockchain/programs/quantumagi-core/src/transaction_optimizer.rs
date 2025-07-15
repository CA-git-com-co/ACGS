// transaction_optimizer.rs
// Solana Transaction Optimization Module for Quantumagi
// Target: Reduce governance costs to <0.01 SOL per action through adaptive batching
// Constitutional Hash: cdd01ef066bc6cf2

use anchor_lang::prelude::*;
use std::collections::HashMap;

/// Transaction batching configuration with adaptive capabilities
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
    /// Adaptive batching configuration
    pub adaptive_config: AdaptiveBatchConfig,
}

/// Adaptive batch sizing configuration based on network conditions
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct AdaptiveBatchConfig {
    /// Enable adaptive batch sizing based on network conditions
    pub adaptive_enabled: bool,
    /// Minimum batch size allowed (safety bound)
    pub min_batch_size: u8,
    /// Network condition check interval (seconds)
    pub network_check_interval: u32,
    /// Congestion threshold for reducing batch size (0-100)
    pub congestion_threshold: u8,
    /// Latency threshold for reducing batch size (milliseconds)
    pub latency_threshold: u32,
    /// Success rate threshold for reducing batch size (basis points)
    pub success_rate_threshold: u16,
    /// Sensitivity factor for adjustments (0-100)
    pub adjustment_sensitivity: u8,
    /// Last network condition update timestamp
    pub last_network_update: i64,
    /// Current network-adjusted batch size
    pub current_optimal_size: u8,
    /// Current network-adjusted timeout
    pub current_optimal_timeout: u32,
}

impl Default for AdaptiveBatchConfig {
    fn default() -> Self {
        Self {
            adaptive_enabled: true,
            min_batch_size: 1,
            network_check_interval: 30, // Check every 30 seconds
            congestion_threshold: 70,   // Reduce batch size if congestion > 70%
            latency_threshold: 5000,    // Reduce batch size if latency > 5s
            success_rate_threshold: 9000, // Reduce batch size if success rate < 90%
            adjustment_sensitivity: 70,  // 70% sensitivity to network changes
            last_network_update: 0,
            current_optimal_size: 5,     // Start with moderate size
            current_optimal_timeout: 3000, // 3 seconds default
        }
    }
}

impl Default for BatchConfig {
    fn default() -> Self {
        Self {
            max_batch_size: 10,
            batch_timeout_seconds: 5,
            cost_target_lamports: 10_000_000, // 0.01 SOL
            enabled: true,
            adaptive_config: AdaptiveBatchConfig::default(),
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

    /// Add operation to batch if it fits within limits (with adaptive sizing support)
    pub fn try_add_operation(
        &mut self,
        operation: BatchOperation,
        config: &BatchConfig,
    ) -> Result<bool> {
        // Use adaptive batch size if enabled, otherwise use max batch size
        let effective_batch_size = if config.adaptive_config.adaptive_enabled {
            config.adaptive_config.current_optimal_size
        } else {
            config.max_batch_size
        };
        
        // Check batch size limit
        if self.operations.len() >= effective_batch_size as usize {
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

    /// Check if batch is ready for execution (with adaptive sizing support)
    pub fn is_ready_for_execution(&self, config: &BatchConfig) -> bool {
        if !config.enabled {
            return false;
        }

        let current_time = Clock::get().unwrap().unix_timestamp;
        
        // Use adaptive batch size if enabled
        let effective_batch_size = if config.adaptive_config.adaptive_enabled {
            config.adaptive_config.current_optimal_size
        } else {
            config.max_batch_size
        };
        
        // Calculate adaptive timeout expiry
        let adaptive_timeout_ms = if config.adaptive_config.adaptive_enabled {
            config.adaptive_config.current_optimal_timeout
        } else {
            config.batch_timeout_seconds as u32 * 1000
        };
        
        let adaptive_expires_at = self.created_at + (adaptive_timeout_ms as i64) / 1000;

        // Execute if batch is full, timeout reached, or cost target met
        self.operations.len() >= effective_batch_size as usize
            || current_time >= adaptive_expires_at
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

/// Transaction optimizer for governance operations with adaptive batch sizing
pub struct TransactionOptimizer {
    config: BatchConfig,
    pending_batches: HashMap<[u8; 16], GovernanceBatch>,
    operation_estimates: HashMap<GovernanceOperation, (u32, u8)>, // (compute_units, account_writes)
    current_network_condition: NetworkCondition,
    adaptive_stats: AdaptiveStats,
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
            current_network_condition: NetworkCondition::default(),
            adaptive_stats: AdaptiveStats::default(),
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

    /// Constitutional Hash: cdd01ef066bc6cf2
    /// Update network conditions and adjust batch sizing parameters
    pub fn update_network_conditions(&mut self, network_condition: NetworkCondition) -> Result<()> {
        if !self.config.adaptive_config.adaptive_enabled {
            return Ok(());
        }

        let current_time = Clock::get()?.unix_timestamp;
        
        // Check if enough time has passed for update
        if current_time - self.config.adaptive_config.last_network_update < 
           self.config.adaptive_config.network_check_interval as i64 {
            return Ok(());
        }

        let previous_condition = self.current_network_condition.clone();
        self.current_network_condition = network_condition;
        
        // Calculate new optimal batch size and timeout
        let (new_batch_size, new_timeout) = self.calculate_adaptive_parameters()?;
        
        // Apply adjustments if significant change
        let size_changed = new_batch_size != self.config.adaptive_config.current_optimal_size;
        let timeout_changed = (new_timeout as i32 - self.config.adaptive_config.current_optimal_timeout as i32).abs() > 500;
        
        if size_changed {
            self.config.adaptive_config.current_optimal_size = new_batch_size;
            self.adaptive_stats.size_adjustments += 1;
            self.adaptive_stats.last_adjustment = current_time;
        }
        
        if timeout_changed {
            self.config.adaptive_config.current_optimal_timeout = new_timeout;
            self.adaptive_stats.timeout_adjustments += 1;
            self.adaptive_stats.last_adjustment = current_time;
        }
        
        // Update statistics
        self.update_adaptive_statistics(new_batch_size, new_timeout)?;
        
        self.config.adaptive_config.last_network_update = current_time;
        self.adaptive_stats.network_updates += 1;
        
        Ok(())
    }
    
    /// Calculate optimal batch parameters based on current network conditions
    fn calculate_adaptive_parameters(&self) -> Result<(u8, u32)> {
        let condition = &self.current_network_condition;
        let adaptive_config = &self.config.adaptive_config;
        
        // Start with base configuration
        let mut optimal_size = self.config.max_batch_size;
        let mut optimal_timeout = self.config.batch_timeout_seconds as u32 * 1000; // Convert to ms
        
        // Adjust for network congestion
        if condition.congestion_score > adaptive_config.congestion_threshold {
            let congestion_factor = (condition.congestion_score as f32 / 100.0).min(1.0);
            let size_reduction = ((optimal_size as f32) * congestion_factor * 0.5) as u8;
            optimal_size = optimal_size.saturating_sub(size_reduction);
            
            // Increase timeout for high congestion
            optimal_timeout += (congestion_factor * 2000.0) as u32;
        }
        
        // Adjust for network latency
        if condition.average_latency > adaptive_config.latency_threshold {
            let latency_factor = (condition.average_latency as f32 / adaptive_config.latency_threshold as f32).min(2.0);
            optimal_size = optimal_size.saturating_sub((latency_factor - 1.0) as u8);
            optimal_timeout += (latency_factor * 1000.0) as u32;
        }
        
        // Adjust for transaction success rate
        if condition.success_rate < adaptive_config.success_rate_threshold {
            let failure_rate = (10000 - condition.success_rate) as f32 / 10000.0;
            optimal_size = optimal_size.saturating_sub((failure_rate * 3.0) as u8);
            optimal_timeout += (failure_rate * 3000.0) as u32;
        }
        
        // Apply sensitivity factor
        let sensitivity = adaptive_config.adjustment_sensitivity as f32 / 100.0;
        let current_size = adaptive_config.current_optimal_size;
        let current_timeout = adaptive_config.current_optimal_timeout;
        
        // Smooth adjustments based on sensitivity
        optimal_size = (current_size as f32 * (1.0 - sensitivity) + optimal_size as f32 * sensitivity) as u8;
        optimal_timeout = (current_timeout as f32 * (1.0 - sensitivity) + optimal_timeout as f32 * sensitivity) as u32;
        
        // Enforce bounds
        optimal_size = optimal_size
            .max(adaptive_config.min_batch_size)
            .min(self.config.max_batch_size);
        optimal_timeout = optimal_timeout.max(1000).min(30000); // 1s to 30s range
        
        Ok((optimal_size, optimal_timeout))
    }
    
    /// Update adaptive statistics with new parameters
    fn update_adaptive_statistics(&mut self, new_size: u8, new_timeout: u32) -> Result<()> {
        let updates = self.adaptive_stats.network_updates as f32;
        
        // Update rolling averages
        if updates > 0.0 {
            self.adaptive_stats.avg_optimal_size = 
                (self.adaptive_stats.avg_optimal_size * updates + new_size as f32) / (updates + 1.0);
            self.adaptive_stats.avg_optimal_timeout = 
                (self.adaptive_stats.avg_optimal_timeout * updates + new_timeout as f32) / (updates + 1.0);
        } else {
            self.adaptive_stats.avg_optimal_size = new_size as f32;
            self.adaptive_stats.avg_optimal_timeout = new_timeout as f32;
        }
        
        // Calculate performance improvement estimate
        let base_timeout = self.config.batch_timeout_seconds as f32 * 1000.0;
        let timeout_improvement = if new_timeout < base_timeout as u32 {
            (base_timeout - new_timeout as f32) / base_timeout * 100.0
        } else {
            0.0
        };
        
        let size_utilization = new_size as f32 / self.config.max_batch_size as f32 * 100.0;
        self.adaptive_stats.performance_improvement = (timeout_improvement + size_utilization) / 2.0;
        
        Ok(())
    }
    
    /// Get current adaptive batch size (network-optimized)
    pub fn get_adaptive_batch_size(&self) -> u8 {
        if self.config.adaptive_config.adaptive_enabled {
            self.config.adaptive_config.current_optimal_size
        } else {
            self.config.max_batch_size
        }
    }
    
    /// Get current adaptive timeout (network-optimized)
    pub fn get_adaptive_timeout_ms(&self) -> u32 {
        if self.config.adaptive_config.adaptive_enabled {
            self.config.adaptive_config.current_optimal_timeout
        } else {
            self.config.batch_timeout_seconds as u32 * 1000
        }
    }
    
    /// Check if network conditions are suitable for batching
    pub fn is_network_suitable_for_batching(&self) -> bool {
        let condition = &self.current_network_condition;
        let adaptive_config = &self.config.adaptive_config;
        
        condition.health_score > 50 &&
        condition.congestion_score < 80 &&
        condition.success_rate >= adaptive_config.success_rate_threshold &&
        condition.average_latency < adaptive_config.latency_threshold * 2
    }
    
    /// Get adaptive optimization statistics
    pub fn get_adaptive_stats(&self) -> AdaptiveStats {
        self.adaptive_stats.clone()
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

/// Network condition data for adaptive batch sizing
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct NetworkCondition {
    /// Network congestion score (0-100, higher = more congested)
    pub congestion_score: u8,
    /// Average network latency in milliseconds
    pub average_latency: u32,
    /// Transaction success rate (basis points, 0-10000)
    pub success_rate: u16,
    /// Current network throughput (TPS)
    pub throughput: u32,
    /// Network health score (0-100, higher = healthier)
    pub health_score: u8,
    /// Timestamp of last update
    pub last_updated: i64,
}

impl Default for NetworkCondition {
    fn default() -> Self {
        Self {
            congestion_score: 25,
            average_latency: 1000,
            success_rate: 9900,
            throughput: 1000,
            health_score: 80,
            last_updated: 0,
        }
    }
}

/// Adaptive batch sizing statistics
#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct AdaptiveStats {
    /// Number of batch size adjustments made
    pub size_adjustments: u32,
    /// Number of timeout adjustments made
    pub timeout_adjustments: u32,
    /// Total network condition updates processed
    pub network_updates: u32,
    /// Average optimal batch size over time
    pub avg_optimal_size: f32,
    /// Average optimal timeout over time (milliseconds)
    pub avg_optimal_timeout: f32,
    /// Performance improvement from adaptive sizing (percentage)
    pub performance_improvement: f32,
    /// Last adjustment timestamp
    pub last_adjustment: i64,
}

impl Default for AdaptiveStats {
    fn default() -> Self {
        Self {
            size_adjustments: 0,
            timeout_adjustments: 0,
            network_updates: 0,
            avg_optimal_size: 5.0,
            avg_optimal_timeout: 3000.0,
            performance_improvement: 0.0,
            last_adjustment: 0,
        }
    }
}
