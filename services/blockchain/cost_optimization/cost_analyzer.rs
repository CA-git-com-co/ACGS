use anchor_lang::prelude::*;
use std::collections::BTreeMap;

// Cost analysis and optimization framework for Solana programs

// Cost tracking and analysis system
#[account]
#[derive(InitSpace)]
pub struct CostTracker {
    pub operation_costs: BTreeMap<String, OperationCost>,
    pub daily_costs: BTreeMap<i64, DailyCostSummary>, // Unix timestamp (day) -> costs
    pub monthly_budgets: BTreeMap<u32, MonthlyBudget>, // Month -> budget
    pub cost_optimization_settings: CostOptimizationSettings,
    pub alerts: Vec<CostAlert>,
    pub total_cost_saved: u64,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct OperationCost {
    pub operation_name: String,
    pub average_compute_units: u32,
    pub average_storage_bytes: u32,
    pub average_rent_cost: u64,      // lamports
    pub frequency_per_day: u32,
    pub total_executions: u64,
    pub cost_per_execution: u64,     // lamports
    pub optimization_potential: u16, // basis points (0-10000)
    pub last_updated: i64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct DailyCostSummary {
    pub date: i64, // Unix timestamp
    pub compute_costs: u64,
    pub storage_costs: u64,
    pub rent_costs: u64,
    pub transaction_fees: u64,
    pub total_costs: u64,
    pub operations_count: u32,
    pub cost_per_operation: u64,
    pub optimization_savings: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct MonthlyBudget {
    pub month: u32, // YYYYMM format
    pub allocated_budget: u64,
    pub spent_amount: u64,
    pub remaining_budget: u64,
    pub projected_spend: u64,
    pub budget_utilization: u16, // basis points
    pub cost_categories: BTreeMap<String, CategoryBudget>,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct CategoryBudget {
    pub category_name: String,
    pub allocated: u64,
    pub spent: u64,
    pub utilization: u16, // basis points
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct CostOptimizationSettings {
    pub auto_optimization_enabled: bool,
    pub max_cost_per_operation: u64,
    pub storage_compression_enabled: bool,
    pub batch_processing_threshold: u32,
    pub cache_ttl_seconds: u64,
    pub cost_alert_threshold: u16, // basis points over budget
    pub optimization_strategies: Vec<OptimizationStrategy>,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum OptimizationStrategy {
    StorageCompression,
    BatchProcessing,
    LazyLoading,
    DataDeduplication,
    ComputeUnitOptimization,
    RentOptimization,
    CachingStrategy,
    OffChainStorage,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct CostAlert {
    pub alert_id: u64,
    pub alert_type: CostAlertType,
    pub severity: AlertSeverity,
    pub threshold_exceeded: u64,
    pub current_value: u64,
    pub message: String,
    pub triggered_at: i64,
    pub acknowledged: bool,
    pub resolved: bool,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum CostAlertType {
    BudgetExceeded,
    HighComputeUsage,
    StorageCostSpike,
    UnexpectedRentIncrease,
    InefficiencyDetected,
    ProjectedOverspend,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum AlertSeverity {
    Info,
    Warning,
    Critical,
    Emergency,
}

// Storage optimization structures
#[account]
#[derive(InitSpace)]
pub struct StorageOptimizer {
    pub compression_rules: Vec<CompressionRule>,
    pub storage_analytics: StorageAnalytics,
    pub cleanup_policies: Vec<CleanupPolicy>,
    pub data_archival_settings: DataArchivalSettings,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct CompressionRule {
    pub field_pattern: String,
    pub compression_type: CompressionType,
    pub compression_ratio: u16, // basis points saved
    pub enabled: bool,
    pub min_size_threshold: u32,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum CompressionType {
    HashStorage,        // Store hash, keep data off-chain
    DeltaCompression,   // Store only changes
    PackedBits,         // Bit packing for small values
    DictionaryCompression, // Common values dictionary
    None,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct StorageAnalytics {
    pub total_storage_used: u64,
    pub compressed_storage: u64,
    pub uncompressed_storage: u64,
    pub compression_savings: u64,
    pub average_compression_ratio: u16,
    pub storage_growth_rate: i16, // basis points per day
    pub rent_cost_per_byte: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct CleanupPolicy {
    pub policy_name: String,
    pub account_pattern: String,
    pub retention_period: u64, // seconds
    pub cleanup_action: CleanupAction,
    pub enabled: bool,
    pub last_cleanup: i64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum CleanupAction {
    Archive,      // Move to off-chain storage
    Compress,     // Apply compression
    Delete,       // Permanent deletion
    Migrate,      // Move to cheaper storage
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct DataArchivalSettings {
    pub auto_archival_enabled: bool,
    pub archival_threshold_days: u32,
    pub archival_storage_url: String,
    pub retrieval_cost_per_mb: u64,
    pub archival_compression_enabled: bool,
}

// Compute unit optimization
#[account]
#[derive(InitSpace)]
pub struct ComputeOptimizer {
    pub instruction_costs: BTreeMap<String, InstructionCost>,
    pub optimization_patterns: Vec<OptimizationPattern>,
    pub compute_budgets: BTreeMap<String, ComputeBudget>,
    pub performance_profiles: Vec<PerformanceProfile>,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct InstructionCost {
    pub instruction_name: String,
    pub base_compute_units: u32,
    pub variable_compute_units: u32, // Per additional item/byte
    pub optimization_level: OptimizationLevel,
    pub cost_reduction_potential: u16, // basis points
    pub execution_frequency: u32,
    pub total_compute_units_used: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum OptimizationLevel {
    None,
    Basic,
    Advanced,
    Maximum,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct OptimizationPattern {
    pub pattern_name: String,
    pub description: String,
    pub applicable_instructions: Vec<String>,
    pub compute_unit_savings: u32,
    pub implementation_complexity: ComplexityLevel,
    pub estimated_implementation_time: u32, // hours
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum ComplexityLevel {
    Low,
    Medium,
    High,
    VeryHigh,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ComputeBudget {
    pub operation_name: String,
    pub allocated_compute_units: u32,
    pub used_compute_units: u32,
    pub efficiency_ratio: u16, // basis points
    pub auto_scaling_enabled: bool,
    pub scaling_thresholds: ScalingThresholds,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ScalingThresholds {
    pub scale_up_threshold: u16,   // basis points of budget used
    pub scale_down_threshold: u16,
    pub max_scale_factor: u16,     // Maximum scaling multiplier
    pub cooldown_period: u64,      // Seconds between scaling actions
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct PerformanceProfile {
    pub profile_name: String,
    pub target_operations: Vec<String>,
    pub compute_limit: u32,
    pub storage_limit: u32,
    pub latency_target: u32,      // milliseconds
    pub cost_target: u64,         // lamports per operation
    pub optimization_priorities: Vec<OptimizationPriority>,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum OptimizationPriority {
    Cost,
    Performance,
    Storage,
    Reliability,
    Scalability,
}

// Cost-effective caching system
#[account]
#[derive(InitSpace)]
pub struct CostEffectiveCache {
    pub cache_policies: Vec<CachePolicy>,
    pub cache_statistics: CacheStatistics,
    pub cost_savings_analytics: CostSavingsAnalytics,
    pub cache_tiers: Vec<CacheTier>,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct CachePolicy {
    pub policy_name: String,
    pub cache_key_pattern: String,
    pub ttl_seconds: u64,
    pub cache_tier: CacheTierType,
    pub eviction_strategy: EvictionStrategy,
    pub cost_per_cache_hit: u64,
    pub cost_per_cache_miss: u64,
    pub enabled: bool,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum CacheTierType {
    Memory,       // Fastest, most expensive
    SSD,          // Fast, moderate cost
    HDD,          // Slower, cheapest
    OffChain,     // External storage
    Hybrid,       // Multiple tiers
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum EvictionStrategy {
    LRU,          // Least Recently Used
    LFU,          // Least Frequently Used
    FIFO,         // First In, First Out
    TTL,          // Time To Live
    CostBased,    // Evict based on cost/benefit
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct CacheStatistics {
    pub total_cache_hits: u64,
    pub total_cache_misses: u64,
    pub hit_ratio: u16,           // basis points
    pub average_response_time_cached: u32,   // microseconds
    pub average_response_time_uncached: u32,
    pub total_cost_saved: u64,
    pub cache_maintenance_cost: u64,
    pub net_cost_savings: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct CostSavingsAnalytics {
    pub daily_savings: Vec<DailySavings>,
    pub savings_by_operation: BTreeMap<String, u64>,
    pub roi_percentage: u16,      // Return on investment
    pub payback_period_days: u32,
    pub projected_annual_savings: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct DailySavings {
    pub date: i64,
    pub compute_savings: u64,
    pub storage_savings: u64,
    pub transaction_fee_savings: u64,
    pub total_savings: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct CacheTier {
    pub tier_name: String,
    pub tier_type: CacheTierType,
    pub capacity_bytes: u64,
    pub used_bytes: u64,
    pub cost_per_byte_per_day: u64,
    pub access_latency: u32,      // microseconds
    pub throughput_mbps: u32,
    pub reliability_score: u16,   // basis points
}

// Resource allocation optimizer
#[account]
#[derive(InitSpace)]
pub struct ResourceAllocator {
    pub allocation_strategies: Vec<AllocationStrategy>,
    pub resource_pools: BTreeMap<String, ResourcePool>,
    pub allocation_history: Vec<AllocationEvent>,
    pub cost_efficiency_metrics: CostEfficiencyMetrics,
    pub auto_scaling_config: AutoScalingConfig,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct AllocationStrategy {
    pub strategy_name: String,
    pub resource_type: ResourceType,
    pub allocation_algorithm: AllocationAlgorithm,
    pub cost_weight: u16,         // basis points
    pub performance_weight: u16,
    pub utilization_target: u16,  // basis points
    pub enabled: bool,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum ResourceType {
    ComputeUnits,
    Storage,
    Network,
    Memory,
    Cache,
    Rent,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum AllocationAlgorithm {
    GreedyCost,       // Minimize cost
    GreedyPerformance, // Maximize performance
    Balanced,         // Balance cost and performance
    PredictiveCost,   // ML-based cost prediction
    DynamicAdjustment, // Real-time adjustment
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ResourcePool {
    pub pool_name: String,
    pub resource_type: ResourceType,
    pub total_capacity: u64,
    pub allocated_capacity: u64,
    pub reserved_capacity: u64,
    pub utilization_percentage: u16,
    pub cost_per_unit: u64,
    pub performance_score: u16,
    pub allocation_queue: Vec<AllocationRequest>,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct AllocationRequest {
    pub request_id: u64,
    pub requester: Pubkey,
    pub resource_type: ResourceType,
    pub requested_amount: u64,
    pub priority: AllocationPriority,
    pub max_cost: u64,
    pub requested_at: i64,
    pub deadline: Option<i64>,
    pub status: AllocationStatus,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum AllocationPriority {
    Low,
    Normal,
    High,
    Critical,
    Emergency,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum AllocationStatus {
    Pending,
    Approved,
    Allocated,
    Rejected,
    Expired,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct AllocationEvent {
    pub event_id: u64,
    pub resource_type: ResourceType,
    pub amount_allocated: u64,
    pub cost: u64,
    pub efficiency_score: u16,
    pub timestamp: i64,
    pub allocation_reason: String,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct CostEfficiencyMetrics {
    pub cost_per_transaction: u64,
    pub cost_per_user: u64,
    pub cost_per_compute_unit: u64,
    pub cost_per_storage_byte: u64,
    pub efficiency_trend: i16,    // basis points change per day
    pub benchmark_comparison: BenchmarkComparison,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct BenchmarkComparison {
    pub our_cost_per_transaction: u64,
    pub industry_average_cost: u64,
    pub cost_advantage_percentage: i16, // Can be negative
    pub ranking_percentile: u16,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct AutoScalingConfig {
    pub enabled: bool,
    pub scale_up_threshold: u16,   // Resource utilization percentage
    pub scale_down_threshold: u16,
    pub scale_up_factor: u16,      // basis points
    pub scale_down_factor: u16,
    pub cooldown_period: u64,      // seconds
    pub max_scale_factor: u16,
    pub cost_limit_per_scale: u64,
}

// Implementation of cost optimization functionality
impl CostTracker {
    pub fn record_operation_cost(
        &mut self,
        operation_name: String,
        compute_units: u32,
        storage_bytes: u32,
        rent_cost: u64,
    ) -> Result<()> {
        let cost_per_execution = self.calculate_operation_cost(compute_units, storage_bytes, rent_cost)?;
        
        let operation_cost = self.operation_costs.entry(operation_name.clone()).or_insert(
            OperationCost {
                operation_name: operation_name.clone(),
                average_compute_units: 0,
                average_storage_bytes: 0,
                average_rent_cost: 0,
                frequency_per_day: 0,
                total_executions: 0,
                cost_per_execution: 0,
                optimization_potential: 0,
                last_updated: Clock::get()?.unix_timestamp,
            }
        );

        // Update running averages
        let total_executions = operation_cost.total_executions + 1;
        operation_cost.average_compute_units = 
            ((operation_cost.average_compute_units as u64 * operation_cost.total_executions) + compute_units as u64) as u32 / total_executions as u32;
        operation_cost.average_storage_bytes = 
            ((operation_cost.average_storage_bytes as u64 * operation_cost.total_executions) + storage_bytes as u64) as u32 / total_executions as u32;
        operation_cost.average_rent_cost = 
            (operation_cost.average_rent_cost * operation_cost.total_executions + rent_cost) / total_executions;
        operation_cost.cost_per_execution = 
            (operation_cost.cost_per_execution * operation_cost.total_executions + cost_per_execution) / total_executions;
        
        operation_cost.total_executions = total_executions;
        operation_cost.last_updated = Clock::get()?.unix_timestamp;

        // Calculate optimization potential
        operation_cost.optimization_potential = self.calculate_optimization_potential(operation_cost)?;

        self.update_daily_costs(cost_per_execution)?;
        Ok(())
    }

    fn calculate_operation_cost(&self, compute_units: u32, storage_bytes: u32, rent_cost: u64) -> Result<u64> {
        // Solana cost calculation (simplified)
        let compute_cost = (compute_units as u64 * 1000) / 1_000_000; // ~1000 lamports per 1M CU
        let storage_cost = storage_bytes as u64 * 10; // ~10 lamports per byte
        let total_cost = compute_cost + storage_cost + rent_cost;
        Ok(total_cost)
    }

    fn calculate_optimization_potential(&self, operation: &OperationCost) -> Result<u16> {
        let mut potential = 0u16;

        // High compute usage = high optimization potential
        if operation.average_compute_units > 100_000 {
            potential += 2000; // 20%
        } else if operation.average_compute_units > 50_000 {
            potential += 1000; // 10%
        }

        // Large storage = compression potential
        if operation.average_storage_bytes > 1000 {
            potential += 1500; // 15%
        }

        // High frequency = batch processing potential
        if operation.frequency_per_day > 1000 {
            potential += 1000; // 10%
        }

        Ok(std::cmp::min(potential, 5000)) // Cap at 50%
    }

    fn update_daily_costs(&mut self, operation_cost: u64) -> Result<()> {
        let current_day = Clock::get()?.unix_timestamp / 86400 * 86400; // Start of day
        
        let daily_summary = self.daily_costs.entry(current_day).or_insert(
            DailyCostSummary {
                date: current_day,
                compute_costs: 0,
                storage_costs: 0,
                rent_costs: 0,
                transaction_fees: 0,
                total_costs: 0,
                operations_count: 0,
                cost_per_operation: 0,
                optimization_savings: 0,
            }
        );

        daily_summary.total_costs += operation_cost;
        daily_summary.operations_count += 1;
        daily_summary.cost_per_operation = daily_summary.total_costs / daily_summary.operations_count as u64;

        Ok(())
    }

    pub fn check_budget_alerts(&mut self) -> Result<Vec<CostAlert>> {
        let mut alerts = Vec::new();
        let current_month = self.get_current_month();

        if let Some(budget) = self.monthly_budgets.get(&current_month) {
            let utilization = (budget.spent_amount * 10000) / budget.allocated_budget;
            
            if utilization > self.cost_optimization_settings.cost_alert_threshold {
                alerts.push(CostAlert {
                    alert_id: self.alerts.len() as u64,
                    alert_type: CostAlertType::BudgetExceeded,
                    severity: if utilization > 9000 { AlertSeverity::Critical } else { AlertSeverity::Warning },
                    threshold_exceeded: utilization,
                    current_value: budget.spent_amount,
                    message: format!("Monthly budget {}% utilized", utilization / 100),
                    triggered_at: Clock::get()?.unix_timestamp,
                    acknowledged: false,
                    resolved: false,
                });
            }
        }

        self.alerts.extend(alerts.clone());
        Ok(alerts)
    }

    fn get_current_month(&self) -> u32 {
        // Simplified month calculation
        202412 // December 2024
    }

    pub fn get_cost_optimization_recommendations(&self) -> Vec<OptimizationRecommendation> {
        let mut recommendations = Vec::new();

        for (operation_name, cost) in &self.operation_costs {
            if cost.optimization_potential > 1000 { // > 10% savings potential
                let recommendation = OptimizationRecommendation {
                    operation: operation_name.clone(),
                    potential_savings: cost.optimization_potential,
                    estimated_monthly_savings: (cost.cost_per_execution * cost.frequency_per_day as u64 * 30 * cost.optimization_potential as u64) / 10000,
                    recommended_strategies: self.get_strategies_for_operation(cost),
                    implementation_effort: self.estimate_implementation_effort(cost),
                    priority: if cost.optimization_potential > 2000 { 
                        RecommendationPriority::High 
                    } else { 
                        RecommendationPriority::Medium 
                    },
                };
                recommendations.push(recommendation);
            }
        }

        recommendations.sort_by(|a, b| b.estimated_monthly_savings.cmp(&a.estimated_monthly_savings));
        recommendations
    }

    fn get_strategies_for_operation(&self, cost: &OperationCost) -> Vec<OptimizationStrategy> {
        let mut strategies = Vec::new();

        if cost.average_compute_units > 50_000 {
            strategies.push(OptimizationStrategy::ComputeUnitOptimization);
        }
        if cost.average_storage_bytes > 500 {
            strategies.push(OptimizationStrategy::StorageCompression);
        }
        if cost.frequency_per_day > 100 {
            strategies.push(OptimizationStrategy::BatchProcessing);
            strategies.push(OptimizationStrategy::CachingStrategy);
        }

        strategies
    }

    fn estimate_implementation_effort(&self, cost: &OperationCost) -> ImplementationEffort {
        if cost.optimization_potential > 3000 {
            ImplementationEffort::High // High savings usually require more work
        } else if cost.optimization_potential > 1500 {
            ImplementationEffort::Medium
        } else {
            ImplementationEffort::Low
        }
    }
}

// Supporting structures for recommendations
#[derive(Clone)]
pub struct OptimizationRecommendation {
    pub operation: String,
    pub potential_savings: u16, // basis points
    pub estimated_monthly_savings: u64, // lamports
    pub recommended_strategies: Vec<OptimizationStrategy>,
    pub implementation_effort: ImplementationEffort,
    pub priority: RecommendationPriority,
}

#[derive(Clone)]
pub enum ImplementationEffort {
    Low,    // < 1 day
    Medium, // 1-5 days
    High,   // > 5 days
}

#[derive(Clone)]
pub enum RecommendationPriority {
    Low,
    Medium,
    High,
    Critical,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_cost_tracking() {
        let mut tracker = CostTracker {
            operation_costs: BTreeMap::new(),
            daily_costs: BTreeMap::new(),
            monthly_budgets: BTreeMap::new(),
            cost_optimization_settings: CostOptimizationSettings {
                auto_optimization_enabled: true,
                max_cost_per_operation: 10000,
                storage_compression_enabled: true,
                batch_processing_threshold: 10,
                cache_ttl_seconds: 3600,
                cost_alert_threshold: 8000, // 80%
                optimization_strategies: vec![],
            },
            alerts: vec![],
            total_cost_saved: 0,
            bump: 0,
        };

        // Record a high-cost operation
        assert!(tracker.record_operation_cost(
            "create_proposal".to_string(),
            150_000, // High compute units
            2000,    // Large storage
            100_000  // High rent cost
        ).is_ok());

        let recommendations = tracker.get_cost_optimization_recommendations();
        assert!(!recommendations.is_empty());
        assert!(recommendations[0].potential_savings > 1000); // Should have optimization potential
    }

    #[test]
    fn test_budget_alerts() {
        let mut tracker = CostTracker {
            operation_costs: BTreeMap::new(),
            daily_costs: BTreeMap::new(),
            monthly_budgets: {
                let mut budgets = BTreeMap::new();
                budgets.insert(202412, MonthlyBudget {
                    month: 202412,
                    allocated_budget: 100_000_000, // 0.1 SOL
                    spent_amount: 85_000_000,       // 85% spent
                    remaining_budget: 15_000_000,
                    projected_spend: 100_000_000,
                    budget_utilization: 8500, // 85%
                    cost_categories: BTreeMap::new(),
                });
                budgets
            },
            cost_optimization_settings: CostOptimizationSettings {
                auto_optimization_enabled: true,
                max_cost_per_operation: 10000,
                storage_compression_enabled: true,
                batch_processing_threshold: 10,
                cache_ttl_seconds: 3600,
                cost_alert_threshold: 8000, // 80%
                optimization_strategies: vec![],
            },
            alerts: vec![],
            total_cost_saved: 0,
            bump: 0,
        };

        let alerts = tracker.check_budget_alerts().unwrap();
        assert!(!alerts.is_empty());
        assert_eq!(alerts[0].alert_type, CostAlertType::BudgetExceeded);
    }

    #[test]
    fn test_cost_calculation() {
        let tracker = CostTracker {
            operation_costs: BTreeMap::new(),
            daily_costs: BTreeMap::new(),
            monthly_budgets: BTreeMap::new(),
            cost_optimization_settings: CostOptimizationSettings {
                auto_optimization_enabled: true,
                max_cost_per_operation: 10000,
                storage_compression_enabled: true,
                batch_processing_threshold: 10,
                cache_ttl_seconds: 3600,
                cost_alert_threshold: 8000,
                optimization_strategies: vec![],
            },
            alerts: vec![],
            total_cost_saved: 0,
            bump: 0,
        };

        let cost = tracker.calculate_operation_cost(100_000, 1000, 50_000).unwrap();
        assert!(cost > 0);
        assert!(cost < 1_000_000); // Reasonable cost
    }
}