use anchor_lang::prelude::*;
use std::collections::BTreeMap;

// Compute Unit (CU) optimization for maximum cost efficiency

// Compute unit tracking and optimization
#[account]
#[derive(InitSpace)]
pub struct ComputeUnitOptimizer {
    pub instruction_profiles: BTreeMap<String, InstructionProfile>,
    pub optimization_strategies: Vec<ComputeOptimizationStrategy>,
    pub compute_budgets: BTreeMap<String, ComputeBudget>,
    pub performance_benchmarks: Vec<PerformanceBenchmark>,
    pub cost_efficiency_metrics: ComputeCostMetrics,
    pub auto_optimization_config: AutoOptimizationConfig,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct InstructionProfile {
    pub instruction_name: String,
    pub base_compute_units: u32,
    pub variable_compute_units: u32,     // Per additional data unit
    pub execution_count: u64,
    pub total_compute_units_consumed: u64,
    pub average_execution_time: u32,     // microseconds
    pub optimization_opportunities: Vec<OptimizationOpportunity>,
    pub cost_per_execution: u32,         // lamports
    pub efficiency_score: u16,           // basis points (0-10000)
    pub last_profiled: i64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct OptimizationOpportunity {
    pub optimization_type: OptimizationType,
    pub potential_cu_savings: u32,
    pub confidence_level: u8,            // 0-100
    pub implementation_complexity: ComplexityLevel,
    pub estimated_savings_percentage: u8, // 0-100
    pub description: String,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum OptimizationType {
    AlgorithmOptimization,      // Better algorithms
    DataStructureOptimization,  // More efficient data structures
    MemoryOptimization,         // Reduce memory allocations
    LoopOptimization,          // Optimize loops and iterations
    ConditionalOptimization,   // Optimize branching logic
    BatchProcessing,           // Process multiple items together
    LazyEvaluation,           // Defer computation until needed
    Caching,                  // Cache frequently computed values
    InstructionReordering,    // Reorder for better CPU pipeline
    ParallelProcessing,       // Use parallel execution where possible
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum ComplexityLevel {
    Trivial,    // < 1 hour
    Simple,     // 1-4 hours
    Moderate,   // 1-2 days
    Complex,    // 3-7 days
    VeryComplex, // > 1 week
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ComputeOptimizationStrategy {
    pub strategy_name: String,
    pub target_instructions: Vec<String>,
    pub optimization_techniques: Vec<OptimizationType>,
    pub expected_cu_reduction: u32,
    pub expected_cu_reduction_percentage: u8,
    pub implementation_status: ImplementationStatus,
    pub priority_score: u16,             // Higher = more important
    pub estimated_roi: u16,              // Return on investment percentage
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum ImplementationStatus {
    NotStarted,
    InProgress,
    Testing,
    Deployed,
    Monitoring,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ComputeBudget {
    pub operation_name: String,
    pub base_budget: u32,
    pub current_usage: u32,
    pub peak_usage: u32,
    pub average_usage: u32,
    pub utilization_percentage: u16,     // basis points
    pub budget_efficiency: u16,          // basis points
    pub auto_scaling_enabled: bool,
    pub scaling_thresholds: ScalingThresholds,
    pub cost_per_cu: u32,               // lamports per compute unit
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ScalingThresholds {
    pub scale_up_threshold: u16,         // basis points
    pub scale_down_threshold: u16,       // basis points
    pub max_budget_multiplier: u16,      // basis points (e.g., 20000 = 2x)
    pub min_budget_multiplier: u16,      // basis points (e.g., 5000 = 0.5x)
    pub scaling_cooldown_seconds: u32,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct PerformanceBenchmark {
    pub benchmark_name: String,
    pub instruction_name: String,
    pub input_size: u32,
    pub compute_units_used: u32,
    pub execution_time_us: u32,
    pub memory_used_bytes: u32,
    pub benchmark_timestamp: i64,
    pub baseline_comparison: BenchmarkComparison,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct BenchmarkComparison {
    pub baseline_cu: u32,
    pub current_cu: u32,
    pub improvement_percentage: i16,     // Can be negative if worse
    pub regression_detected: bool,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct ComputeCostMetrics {
    pub total_cu_consumed_daily: u64,
    pub total_cost_daily: u64,           // lamports
    pub average_cu_per_transaction: u32,
    pub cost_per_transaction: u32,       // lamports
    pub efficiency_trend: i16,           // basis points change per day
    pub top_consuming_instructions: Vec<TopConsumer>,
    pub optimization_savings: OptimizationSavings,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct TopConsumer {
    pub instruction_name: String,
    pub cu_consumed_daily: u64,
    pub cost_daily: u64,                // lamports
    pub percentage_of_total: u16,       // basis points
    pub optimization_potential: u16,    // basis points
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct OptimizationSavings {
    pub total_cu_saved: u64,
    pub total_cost_saved: u64,          // lamports
    pub daily_cu_savings: u32,
    pub daily_cost_savings: u32,        // lamports
    pub roi_percentage: u16,            // Return on optimization investment
    pub payback_period_days: u16,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct AutoOptimizationConfig {
    pub enabled: bool,
    pub optimization_frequency: u32,    // seconds between optimization runs
    pub min_savings_threshold: u32,     // minimum CU savings to implement
    pub max_risk_level: RiskLevel,
    pub auto_deploy_enabled: bool,
    pub rollback_enabled: bool,
    pub monitoring_period: u32,         // seconds to monitor after deployment
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum RiskLevel {
    Low,        // Safe optimizations only
    Medium,     // Moderate risk optimizations
    High,       // All optimizations (manual approval)
}

// Specific optimization implementations
pub struct ComputeOptimizations;

impl ComputeOptimizations {
    // Optimize governance proposal creation
    pub fn optimize_create_proposal(
        ctx: Context<CreateProposal>,
        proposal_data: OptimizedProposalData,
    ) -> Result<u32> {
        let start_cu = Self::get_remaining_compute_units();

        // Optimized implementation with minimal allocations
        let proposal = &mut ctx.accounts.proposal;
        
        // Use stack allocation for small data
        let mut title_buffer = [0u8; 32];
        let title_bytes = proposal_data.title_hash;
        title_buffer[..title_bytes.len()].copy_from_slice(&title_bytes);
        
        // Batch all writes to minimize syscalls
        proposal.policy_id = proposal_data.policy_id;
        proposal.title_hash = title_bytes;
        proposal.content_hash = proposal_data.content_hash;
        proposal.proposer_hash = proposal_data.proposer_hash;
        proposal.created_at = Clock::get()?.unix_timestamp;
        proposal.voting_ends_at = proposal.created_at + proposal_data.voting_period as i64;
        proposal.status = ProposalStatus::Active as u8;
        
        // Initialize vote counters efficiently
        proposal.votes_for = 0;
        proposal.votes_against = 0;
        proposal.total_voters = 0;
        
        let end_cu = Self::get_remaining_compute_units();
        Ok(start_cu - end_cu)
    }

    // Optimized voting with minimal compute usage
    pub fn optimize_vote_on_proposal(
        ctx: Context<VoteOnProposal>,
        vote_data: OptimizedVoteData,
    ) -> Result<u32> {
        let start_cu = Self::get_remaining_compute_units();

        let proposal = &mut ctx.accounts.proposal;
        let vote_record = &mut ctx.accounts.vote_record;

        // Validate with early returns to save compute
        if proposal.status != ProposalStatus::Active as u8 {
            return Err(GovernanceError::ProposalNotActive.into());
        }

        let current_time = Clock::get()?.unix_timestamp;
        if current_time > proposal.voting_ends_at {
            return Err(GovernanceError::VotingPeriodEnded.into());
        }

        // Use bit manipulation for flags
        let vote_flags = if vote_data.vote { 0x80 } else { 0x00 } | 
                        (vote_data.power_tier & 0x07) << 4;

        // Minimal vote record creation
        vote_record.voter_hash = vote_data.voter_hash;
        vote_record.proposal_id = vote_data.proposal_id;
        vote_record.vote_flags = vote_flags;
        vote_record.timestamp = (current_time / 3600) as u16; // Store as hours

        // Update proposal counters efficiently
        let voting_power = Self::tier_to_power(vote_data.power_tier);
        if vote_data.vote {
            proposal.votes_for += voting_power;
        } else {
            proposal.votes_against += voting_power;
        }
        proposal.total_voters += 1;

        let end_cu = Self::get_remaining_compute_units();
        Ok(start_cu - end_cu)
    }

    // Batch processing for multiple operations
    pub fn batch_process_votes(
        ctx: Context<BatchProcessVotes>,
        vote_batch: Vec<OptimizedVoteData>,
    ) -> Result<u32> {
        let start_cu = Self::get_remaining_compute_units();

        // Pre-allocate vectors to avoid reallocations
        let mut for_votes = 0u64;
        let mut against_votes = 0u64;
        let vote_count = vote_batch.len();

        // Process all votes in a single loop
        for vote_data in vote_batch {
            let voting_power = Self::tier_to_power(vote_data.power_tier);
            if vote_data.vote {
                for_votes += voting_power;
            } else {
                against_votes += voting_power;
            }
        }

        // Single update to proposal
        let proposal = &mut ctx.accounts.proposal;
        proposal.votes_for += for_votes;
        proposal.votes_against += against_votes;
        proposal.total_voters += vote_count as u32;

        let end_cu = Self::get_remaining_compute_units();
        Ok(start_cu - end_cu)
    }

    // Memory-efficient data structure operations
    pub fn optimize_data_structures() -> DataStructureOptimizations {
        DataStructureOptimizations {
            use_packed_structs: true,
            minimize_allocations: true,
            use_stack_allocation: true,
            cache_frequently_accessed: true,
            lazy_load_large_data: true,
        }
    }

    // Loop optimization techniques
    pub fn optimize_loops<T>(data: &[T], processor: impl Fn(&T) -> u32) -> u32 {
        let mut total = 0u32;
        
        // Unroll loop for better performance (process 4 items at once)
        let chunks = data.chunks_exact(4);
        let remainder = chunks.remainder();
        
        for chunk in chunks {
            total += processor(&chunk[0]);
            total += processor(&chunk[1]);
            total += processor(&chunk[2]);
            total += processor(&chunk[3]);
        }
        
        // Process remaining items
        for item in remainder {
            total += processor(item);
        }
        
        total
    }

    // Branch prediction optimization
    pub fn optimize_conditionals(condition: bool, high_probability_branch: impl Fn(), low_probability_branch: impl Fn()) {
        if likely(condition) {
            high_probability_branch();
        } else {
            low_probability_branch();
        }
    }

    // Cache-friendly memory access patterns
    pub fn optimize_memory_access<T>(data: &mut [T], operation: impl Fn(&mut T)) {
        // Process data in cache-line-friendly chunks
        const CACHE_LINE_SIZE: usize = 64;
        let items_per_line = CACHE_LINE_SIZE / std::mem::size_of::<T>();
        
        for chunk in data.chunks_mut(items_per_line) {
            for item in chunk {
                operation(item);
            }
        }
    }

    // Helper functions
    fn get_remaining_compute_units() -> u32 {
        // This would use Solana's compute budget syscall
        // Placeholder implementation
        200000 // Default compute budget
    }

    fn tier_to_power(tier: u8) -> u64 {
        match tier {
            0 => 1000,
            1 => 10000,
            2 => 100000,
            3 => 1000000,
            _ => 10000000,
        }
    }
}

// Optimized data structures
#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct OptimizedProposalData {
    pub policy_id: u32,
    pub title_hash: [u8; 8],
    pub content_hash: [u8; 16],
    pub proposer_hash: [u8; 8],
    pub voting_period: u32, // seconds
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct OptimizedVoteData {
    pub voter_hash: [u8; 8],
    pub proposal_id: u16,
    pub vote: bool,
    pub power_tier: u8,
}

pub struct DataStructureOptimizations {
    pub use_packed_structs: bool,
    pub minimize_allocations: bool,
    pub use_stack_allocation: bool,
    pub cache_frequently_accessed: bool,
    pub lazy_load_large_data: bool,
}

// Placeholder for likely/unlikely hints (would use compiler intrinsics)
fn likely(condition: bool) -> bool { condition }
fn _unlikely(condition: bool) -> bool { condition }

// Compute unit profiler
pub struct ComputeUnitProfiler {
    instruction_costs: BTreeMap<String, u32>,
}

impl ComputeUnitProfiler {
    pub fn new() -> Self {
        Self {
            instruction_costs: BTreeMap::new(),
        }
    }

    pub fn profile_instruction<F, R>(&mut self, name: &str, operation: F) -> (R, u32)
    where
        F: FnOnce() -> R,
    {
        let start_cu = ComputeOptimizations::get_remaining_compute_units();
        let result = operation();
        let end_cu = ComputeOptimizations::get_remaining_compute_units();
        let cu_used = start_cu - end_cu;

        self.instruction_costs.insert(name.to_string(), cu_used);
        (result, cu_used)
    }

    pub fn get_instruction_cost(&self, name: &str) -> Option<u32> {
        self.instruction_costs.get(name).copied()
    }

    pub fn get_total_cost(&self) -> u32 {
        self.instruction_costs.values().sum()
    }

    pub fn get_cost_breakdown(&self) -> Vec<(String, u32, f32)> {
        let total = self.get_total_cost();
        self.instruction_costs
            .iter()
            .map(|(name, cost)| {
                let percentage = if total > 0 { (*cost as f32 / total as f32) * 100.0 } else { 0.0 };
                (name.clone(), *cost, percentage)
            })
            .collect()
    }
}

// Account contexts for optimized operations
#[derive(Accounts)]
pub struct CreateProposal<'info> {
    #[account(init, payer = proposer, space = 8 + 64)] // Minimal space
    pub proposal: Account<'info, OptimizedProposal>,
    #[account(mut)]
    pub proposer: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct VoteOnProposal<'info> {
    #[account(mut)]
    pub proposal: Account<'info, OptimizedProposal>,
    #[account(init, payer = voter, space = 8 + 32)] // Minimal vote record
    pub vote_record: Account<'info, OptimizedVoteRecord>,
    #[account(mut)]
    pub voter: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct BatchProcessVotes<'info> {
    #[account(mut)]
    pub proposal: Account<'info, OptimizedProposal>,
    #[account(mut)]
    pub processor: Signer<'info>,
}

// Minimal account structures for compute efficiency
#[account]
pub struct OptimizedProposal {
    pub policy_id: u32,
    pub title_hash: [u8; 8],
    pub content_hash: [u8; 16],
    pub proposer_hash: [u8; 8],
    pub created_at: i64,
    pub voting_ends_at: i64,
    pub status: u8,
    pub votes_for: u64,
    pub votes_against: u64,
    pub total_voters: u32,
}

#[account]
pub struct OptimizedVoteRecord {
    pub voter_hash: [u8; 8],
    pub proposal_id: u16,
    pub vote_flags: u8,     // vote (1 bit) + power tier (3 bits) + flags (4 bits)
    pub timestamp: u16,     // hours since epoch
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq)]
pub enum ProposalStatus {
    Active = 0,
    Approved = 1,
    Rejected = 2,
    Expired = 3,
}

// Implementation
impl ComputeUnitOptimizer {
    pub fn record_instruction_execution(
        &mut self,
        instruction_name: String,
        compute_units_used: u32,
        execution_time_us: u32,
    ) -> Result<()> {
        let profile = self.instruction_profiles.entry(instruction_name.clone()).or_insert(
            InstructionProfile {
                instruction_name: instruction_name.clone(),
                base_compute_units: compute_units_used,
                variable_compute_units: 0,
                execution_count: 0,
                total_compute_units_consumed: 0,
                average_execution_time: 0,
                optimization_opportunities: vec![],
                cost_per_execution: 0,
                efficiency_score: 5000, // 50% default
                last_profiled: Clock::get()?.unix_timestamp,
            }
        );

        // Update running averages
        profile.execution_count += 1;
        profile.total_compute_units_consumed += compute_units_used as u64;
        
        let total_time = profile.average_execution_time as u64 * (profile.execution_count - 1) + execution_time_us as u64;
        profile.average_execution_time = (total_time / profile.execution_count) as u32;

        // Calculate efficiency score
        profile.efficiency_score = self.calculate_efficiency_score(profile)?;

        // Identify optimization opportunities
        self.identify_optimization_opportunities(profile)?;

        Ok(())
    }

    fn calculate_efficiency_score(&self, profile: &InstructionProfile) -> Result<u16> {
        // Base efficiency calculation
        let cu_per_ms = if profile.average_execution_time > 0 {
            (profile.base_compute_units * 1000) / profile.average_execution_time
        } else {
            profile.base_compute_units
        };

        // Benchmark against typical instruction efficiency
        let typical_cu_per_ms = 50000; // Baseline
        let efficiency = if cu_per_ms > 0 {
            std::cmp::min((typical_cu_per_ms * 10000) / cu_per_ms, 10000)
        } else {
            0
        };

        Ok(efficiency as u16)
    }

    fn identify_optimization_opportunities(&mut self, profile: &mut InstructionProfile) -> Result<()> {
        profile.optimization_opportunities.clear();

        // High compute usage opportunity
        if profile.base_compute_units > 100000 {
            profile.optimization_opportunities.push(OptimizationOpportunity {
                optimization_type: OptimizationType::AlgorithmOptimization,
                potential_cu_savings: profile.base_compute_units / 4, // 25% potential savings
                confidence_level: 80,
                implementation_complexity: ComplexityLevel::Moderate,
                estimated_savings_percentage: 25,
                description: "High compute usage detected - algorithm optimization recommended".to_string(),
            });
        }

        // Low efficiency opportunity
        if profile.efficiency_score < 3000 { // < 30%
            profile.optimization_opportunities.push(OptimizationOpportunity {
                optimization_type: OptimizationType::DataStructureOptimization,
                potential_cu_savings: profile.base_compute_units / 3, // 33% potential savings
                confidence_level: 70,
                implementation_complexity: ComplexityLevel::Complex,
                estimated_savings_percentage: 33,
                description: "Low efficiency detected - data structure optimization needed".to_string(),
            });
        }

        // Frequent execution opportunity
        if profile.execution_count > 1000 {
            profile.optimization_opportunities.push(OptimizationOpportunity {
                optimization_type: OptimizationType::Caching,
                potential_cu_savings: profile.base_compute_units / 5, // 20% potential savings
                confidence_level: 90,
                implementation_complexity: ComplexityLevel::Simple,
                estimated_savings_percentage: 20,
                description: "Frequent execution detected - caching recommended".to_string(),
            });
        }

        Ok(())
    }

    pub fn generate_optimization_report(&self) -> ComputeOptimizationReport {
        let mut total_potential_savings = 0u64;
        let mut total_current_cost = 0u64;

        for profile in self.instruction_profiles.values() {
            total_current_cost += profile.total_compute_units_consumed;
            for opportunity in &profile.optimization_opportunities {
                total_potential_savings += (opportunity.potential_cu_savings as u64 * profile.execution_count);
            }
        }

        let potential_savings_percentage = if total_current_cost > 0 {
            ((total_potential_savings * 100) / total_current_cost) as u16
        } else {
            0
        };

        ComputeOptimizationReport {
            total_instructions_profiled: self.instruction_profiles.len() as u32,
            total_compute_units_consumed: total_current_cost,
            total_potential_savings,
            potential_savings_percentage,
            top_optimization_targets: self.get_top_optimization_targets(5),
            estimated_cost_savings_lamports: total_potential_savings / 1000, // Rough conversion
        }
    }

    fn get_top_optimization_targets(&self, count: usize) -> Vec<OptimizationTarget> {
        let mut targets: Vec<_> = self.instruction_profiles
            .iter()
            .map(|(name, profile)| {
                let total_potential_savings: u32 = profile.optimization_opportunities
                    .iter()
                    .map(|opp| opp.potential_cu_savings)
                    .sum();
                
                OptimizationTarget {
                    instruction_name: name.clone(),
                    current_cu_cost: profile.base_compute_units,
                    potential_cu_savings: total_potential_savings,
                    execution_frequency: profile.execution_count,
                    priority_score: (total_potential_savings as u64 * profile.execution_count) as u32,
                }
            })
            .collect();

        targets.sort_by(|a, b| b.priority_score.cmp(&a.priority_score));
        targets.into_iter().take(count).collect()
    }
}

pub struct ComputeOptimizationReport {
    pub total_instructions_profiled: u32,
    pub total_compute_units_consumed: u64,
    pub total_potential_savings: u64,
    pub potential_savings_percentage: u16,
    pub top_optimization_targets: Vec<OptimizationTarget>,
    pub estimated_cost_savings_lamports: u64,
}

pub struct OptimizationTarget {
    pub instruction_name: String,
    pub current_cu_cost: u32,
    pub potential_cu_savings: u32,
    pub execution_frequency: u64,
    pub priority_score: u32,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_compute_unit_profiler() {
        let mut profiler = ComputeUnitProfiler::new();
        
        let (result, cu_used) = profiler.profile_instruction("test_op", || {
            // Simulate some work
            42
        });
        
        assert_eq!(result, 42);
        assert!(cu_used > 0);
        assert_eq!(profiler.get_instruction_cost("test_op"), Some(cu_used));
    }

    #[test]
    fn test_optimization_opportunity_identification() {
        let mut optimizer = ComputeUnitOptimizer {
            instruction_profiles: BTreeMap::new(),
            optimization_strategies: vec![],
            compute_budgets: BTreeMap::new(),
            performance_benchmarks: vec![],
            cost_efficiency_metrics: ComputeCostMetrics {
                total_cu_consumed_daily: 0,
                total_cost_daily: 0,
                average_cu_per_transaction: 0,
                cost_per_transaction: 0,
                efficiency_trend: 0,
                top_consuming_instructions: vec![],
                optimization_savings: OptimizationSavings {
                    total_cu_saved: 0,
                    total_cost_saved: 0,
                    daily_cu_savings: 0,
                    daily_cost_savings: 0,
                    roi_percentage: 0,
                    payback_period_days: 0,
                },
            },
            auto_optimization_config: AutoOptimizationConfig {
                enabled: true,
                optimization_frequency: 3600,
                min_savings_threshold: 1000,
                max_risk_level: RiskLevel::Medium,
                auto_deploy_enabled: false,
                rollback_enabled: true,
                monitoring_period: 86400,
            },
            bump: 0,
        };

        // Record a high-cost instruction
        optimizer.record_instruction_execution(
            "expensive_operation".to_string(),
            150000, // High CU usage
            5000,   // 5ms execution time
        ).unwrap();

        let profile = optimizer.instruction_profiles.get("expensive_operation").unwrap();
        assert!(!profile.optimization_opportunities.is_empty());
    }

    #[test]
    fn test_loop_optimization() {
        let data = vec![1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
        let result = ComputeOptimizations::optimize_loops(&data, |x| *x as u32);
        assert_eq!(result, 55); // Sum of 1-10
    }

    #[test]
    fn test_optimization_report_generation() {
        let optimizer = ComputeUnitOptimizer {
            instruction_profiles: {
                let mut profiles = BTreeMap::new();
                profiles.insert("test_op".to_string(), InstructionProfile {
                    instruction_name: "test_op".to_string(),
                    base_compute_units: 50000,
                    variable_compute_units: 0,
                    execution_count: 100,
                    total_compute_units_consumed: 5000000,
                    average_execution_time: 1000,
                    optimization_opportunities: vec![
                        OptimizationOpportunity {
                            optimization_type: OptimizationType::AlgorithmOptimization,
                            potential_cu_savings: 12500,
                            confidence_level: 80,
                            implementation_complexity: ComplexityLevel::Moderate,
                            estimated_savings_percentage: 25,
                            description: "Test optimization".to_string(),
                        }
                    ],
                    cost_per_execution: 50,
                    efficiency_score: 4000,
                    last_profiled: 1640995200,
                });
                profiles
            },
            optimization_strategies: vec![],
            compute_budgets: BTreeMap::new(),
            performance_benchmarks: vec![],
            cost_efficiency_metrics: ComputeCostMetrics {
                total_cu_consumed_daily: 0,
                total_cost_daily: 0,
                average_cu_per_transaction: 0,
                cost_per_transaction: 0,
                efficiency_trend: 0,
                top_consuming_instructions: vec![],
                optimization_savings: OptimizationSavings {
                    total_cu_saved: 0,
                    total_cost_saved: 0,
                    daily_cu_savings: 0,
                    daily_cost_savings: 0,
                    roi_percentage: 0,
                    payback_period_days: 0,
                },
            },
            auto_optimization_config: AutoOptimizationConfig {
                enabled: true,
                optimization_frequency: 3600,
                min_savings_threshold: 1000,
                max_risk_level: RiskLevel::Medium,
                auto_deploy_enabled: false,
                rollback_enabled: true,
                monitoring_period: 86400,
            },
            bump: 0,
        };

        let report = optimizer.generate_optimization_report();
        assert_eq!(report.total_instructions_profiled, 1);
        assert!(report.total_potential_savings > 0);
        assert!(!report.top_optimization_targets.is_empty());
    }
}