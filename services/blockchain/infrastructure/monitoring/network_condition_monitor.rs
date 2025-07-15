// Constitutional Hash: cdd01ef066bc6cf2
//! Network Condition Monitor - Real-time network health assessment for adaptive batch sizing
//! 
//! This component provides continuous monitoring of Solana network conditions
//! to enable intelligent batch sizing and transaction optimization.

use anchor_lang::prelude::*;

// Declare program ID for network condition monitor module
declare_id!("11111111111111111111111111111114");

#[program]
pub mod acgs_network_monitor {
    use super::*;
    
    pub fn placeholder(_ctx: Context<InitializeNetworkMonitor>) -> Result<()> {
        Ok(())
    }
}

#[derive(Accounts)]
pub struct InitializeNetworkMonitor {}

use crate::observability::{NetworkConditionMetrics, NetworkTrend};

/// Real-time network condition monitoring system
#[account]
#[derive(InitSpace)]
pub struct NetworkConditionMonitor {
    /// Current network conditions
    pub current_conditions: NetworkConditionMetrics,
    
    /// Historical network data (last 10 samples)
    #[max_len(1000)]
    pub historical_data: Vec<NetworkConditionMetrics>,
    
    /// Monitoring configuration
    pub config: MonitoringConfig,
    
    /// Last monitoring cycle timestamp
    pub last_update: i64,
    
    /// Monitoring statistics
    pub stats: MonitoringStats,
    
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct MonitoringConfig {
    /// How often to update network conditions (seconds)
    pub update_interval: u32,
    
    /// Number of historical samples to keep
    pub history_size: u32,
    
    /// Solana RPC endpoint URL hash (for constitutional compliance)
    pub rpc_endpoint_hash: u64,
    
    /// Network monitoring enabled
    pub enabled: bool,
    
    /// Alert thresholds
    pub alert_thresholds: AlertThresholds,
    
    /// Adaptive parameters
    pub adaptive_config: AdaptiveConfig,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace, Default)]
pub struct AlertThresholds {
    /// Maximum acceptable latency (ms)
    pub max_latency_ms: u32,
    
    /// Minimum acceptable success rate (basis points)
    pub min_success_rate: u16,
    
    /// Maximum acceptable congestion score
    pub max_congestion_score: u8,
    
    /// Minimum network health score for operations
    pub min_health_score: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace, Default)]
pub struct AdaptiveConfig {
    /// Minimum batch size allowed
    pub min_batch_size: u8,
    
    /// Maximum batch size allowed
    pub max_batch_size: u8,
    
    /// Default batch size
    pub default_batch_size: u8,
    
    /// Minimum timeout (ms)
    pub min_timeout_ms: u32,
    
    /// Maximum timeout (ms)
    pub max_timeout_ms: u32,
    
    /// Default timeout (ms)
    pub default_timeout_ms: u32,
    
    /// Sensitivity factor for adjustments (0-100)
    pub sensitivity: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct MonitoringStats {
    /// Total monitoring cycles completed
    pub cycles_completed: u64,
    
    /// Number of network condition alerts triggered
    pub alerts_triggered: u32,
    
    /// Number of batch size adjustments made
    pub batch_adjustments: u32,
    
    /// Number of timeout adjustments made
    pub timeout_adjustments: u32,
    
    /// Average network health score (basis points)
    pub average_health_score: u16,
    
    /// Best network health score seen
    pub best_health_score: u8,
    
    /// Worst network health score seen
    pub worst_health_score: u8,
    
    /// Last alert timestamp
    pub last_alert: Option<i64>,
    
    /// Monitoring uptime (seconds)
    pub uptime_seconds: u64,
}

impl Default for MonitoringConfig {
    fn default() -> Self {
        Self {
            update_interval: 30,
            history_size: 10,
            rpc_endpoint_hash: 0,
            enabled: true,
            alert_thresholds: AlertThresholds {
                max_latency_ms: 5000,
                min_success_rate: 9000, // 90%
                max_congestion_score: 80,
                min_health_score: 50,
            },
            adaptive_config: AdaptiveConfig {
                min_batch_size: 1,
                max_batch_size: 15,
                default_batch_size: 5,
                min_timeout_ms: 1000,
                max_timeout_ms: 30000,
                default_timeout_ms: 3000,
                sensitivity: 70, // 70% sensitivity
            },
        }
    }
}

impl Default for MonitoringStats {
    fn default() -> Self {
        Self {
            cycles_completed: 0,
            alerts_triggered: 0,
            batch_adjustments: 0,
            timeout_adjustments: 0,
            average_health_score: 8000, // 80%
            best_health_score: 100,
            worst_health_score: 0,
            last_alert: None,
            uptime_seconds: 0,
        }
    }
}

impl NetworkConditionMonitor {
    /// Constitutional Hash: cdd01ef066bc6cf2
    /// Initialize the network condition monitor
    pub fn initialize(&mut self, config: MonitoringConfig) -> Result<()> {
        self.config = config;
        self.current_conditions = NetworkConditionMetrics::default();
        self.historical_data = Vec::with_capacity(self.config.history_size as usize);
        self.stats = MonitoringStats::default();
        self.last_update = Clock::get()?.unix_timestamp;
        
        Ok(())
    }
    
    /// Update network conditions with new data
    pub fn update_network_conditions(&mut self, new_conditions: NetworkConditionMetrics) -> Result<()> {
        let current_time = Clock::get()?.unix_timestamp;
        
        // Store previous conditions for trend analysis
        let previous_conditions = self.current_conditions.clone();
        
        // Update current conditions
        self.current_conditions = new_conditions;
        
        // Perform comprehensive assessment
        self.current_conditions.assess_network_conditions(Some(&previous_conditions))?;
        
        // Add to historical data
        self.add_to_history(previous_conditions)?;
        
        // Update statistics
        self.update_statistics(current_time)?;
        
        // Check for alerts
        self.check_alert_conditions()?;
        
        self.last_update = current_time;
        self.stats.cycles_completed += 1;
        
        Ok(())
    }
    
    /// Add network conditions to historical data
    fn add_to_history(&mut self, conditions: NetworkConditionMetrics) -> Result<()> {
        // Add to history
        self.historical_data.push(conditions);
        
        // Maintain history size limit
        while self.historical_data.len() > self.config.history_size as usize {
            self.historical_data.remove(0);
        }
        
        Ok(())
    }
    
    /// Update monitoring statistics
    fn update_statistics(&mut self, current_time: i64) -> Result<()> {
        // Update average health score
        let current_health = self.current_conditions.network_health_score;
        let total_samples = self.stats.cycles_completed + 1;
        
        self.stats.average_health_score = 
            ((self.stats.average_health_score as u64 * self.stats.cycles_completed + current_health as u64 * 100) 
             / total_samples) as u16;
        
        // Update best/worst scores
        if current_health > self.stats.best_health_score {
            self.stats.best_health_score = current_health;
        }
        if current_health < self.stats.worst_health_score || self.stats.worst_health_score == 0 {
            self.stats.worst_health_score = current_health;
        }
        
        // Update uptime
        if self.stats.cycles_completed > 0 {
            self.stats.uptime_seconds = (current_time - (self.last_update - self.config.update_interval as i64)) as u64;
        }
        
        Ok(())
    }
    
    /// Check for alert conditions
    fn check_alert_conditions(&mut self) -> Result<bool> {
        let mut alert_triggered = false;
        let current_time = Clock::get()?.unix_timestamp;
        
        // Check latency threshold
        if self.current_conditions.p95_network_latency > self.config.alert_thresholds.max_latency_ms {
            alert_triggered = true;
        }
        
        // Check success rate threshold
        if self.current_conditions.transaction_success_rate < self.config.alert_thresholds.min_success_rate {
            alert_triggered = true;
        }
        
        // Check congestion threshold
        if self.current_conditions.congestion_score > self.config.alert_thresholds.max_congestion_score {
            alert_triggered = true;
        }
        
        // Check health score threshold
        if self.current_conditions.network_health_score < self.config.alert_thresholds.min_health_score {
            alert_triggered = true;
        }
        
        if alert_triggered {
            self.stats.alerts_triggered += 1;
            self.stats.last_alert = Some(current_time);
        }
        
        Ok(alert_triggered)
    }
    
    /// Get adaptive batch size recommendation
    pub fn get_adaptive_batch_size(&self) -> u8 {
        let optimal = self.current_conditions.optimal_batch_size;
        
        // Ensure within configured bounds
        optimal
            .max(self.config.adaptive_config.min_batch_size)
            .min(self.config.adaptive_config.max_batch_size)
    }
    
    /// Get adaptive timeout recommendation
    pub fn get_adaptive_timeout(&self) -> u32 {
        let optimal = self.current_conditions.recommended_timeout;
        
        // Ensure within configured bounds
        optimal
            .max(self.config.adaptive_config.min_timeout_ms)
            .min(self.config.adaptive_config.max_timeout_ms)
    }
    
    /// Check if current network conditions are suitable for batch processing
    pub fn is_suitable_for_batching(&self) -> bool {
        self.current_conditions.network_health_score >= self.config.alert_thresholds.min_health_score &&
        self.current_conditions.congestion_score <= self.config.alert_thresholds.max_congestion_score &&
        self.current_conditions.transaction_success_rate >= self.config.alert_thresholds.min_success_rate
    }
    
    /// Get network condition summary for external systems
    pub fn get_condition_summary(&self) -> NetworkConditionSummary {
        NetworkConditionSummary {
            health_score: self.current_conditions.network_health_score,
            congestion_level: self.current_conditions.congestion_score,
            recommended_batch_size: self.get_adaptive_batch_size(),
            recommended_timeout: self.get_adaptive_timeout(),
            suitable_for_batching: self.is_suitable_for_batching(),
            latency_trend: self.current_conditions.latency_trend.clone(),
            throughput_trend: self.current_conditions.throughput_trend.clone(),
            last_updated: self.last_update,
        }
    }
    
    /// Calculate network condition trends over historical data
    pub fn calculate_historical_trends(&self) -> Result<HistoricalTrends> {
        if self.historical_data.len() < 2 {
            return Ok(HistoricalTrends::default());
        }
        
        let recent = &self.current_conditions;
        let historical_avg = self.calculate_historical_average()?;
        
        Ok(HistoricalTrends {
            latency_improvement: if recent.average_network_latency < historical_avg.average_network_latency {
                ((historical_avg.average_network_latency - recent.average_network_latency) as f32 / historical_avg.average_network_latency as f32 * 100.0) as u16
            } else { 0 },
            throughput_improvement: if recent.network_throughput_tps > historical_avg.network_throughput_tps {
                ((recent.network_throughput_tps - historical_avg.network_throughput_tps) as f32 / historical_avg.network_throughput_tps as f32 * 100.0) as u16
            } else { 0 },
            health_trend: if recent.network_health_score > historical_avg.network_health_score {
                HealthTrend::Improving
            } else if recent.network_health_score < historical_avg.network_health_score {
                HealthTrend::Degrading
            } else {
                HealthTrend::Stable
            },
            stability_score: self.calculate_stability_score()?,
        })
    }
    
    /// Calculate average of historical network conditions
    fn calculate_historical_average(&self) -> Result<NetworkConditionMetrics> {
        let mut avg = NetworkConditionMetrics::default();
        let count = self.historical_data.len();
        
        if count == 0 {
            return Ok(avg);
        }
        
        let mut total_latency = 0u64;
        let mut total_throughput = 0u64;
        let mut total_health = 0u64;
        let mut total_congestion = 0u64;
        
        for condition in &self.historical_data {
            total_latency += condition.average_network_latency as u64;
            total_throughput += condition.network_throughput_tps as u64;
            total_health += condition.network_health_score as u64;
            total_congestion += condition.congestion_score as u64;
        }
        
        avg.average_network_latency = (total_latency / count as u64) as u32;
        avg.network_throughput_tps = (total_throughput / count as u64) as u32;
        avg.network_health_score = (total_health / count as u64) as u8;
        avg.congestion_score = (total_congestion / count as u64) as u8;
        
        Ok(avg)
    }
    
    /// Calculate network stability score based on variance in historical data
    fn calculate_stability_score(&self) -> Result<u8> {
        if self.historical_data.len() < 3 {
            return Ok(50); // Neutral score for insufficient data
        }
        
        // Calculate variance in health scores
        let health_scores: Vec<u8> = self.historical_data
            .iter()
            .map(|c| c.network_health_score)
            .collect();
        
        let avg_health = health_scores.iter().sum::<u8>() as f32 / health_scores.len() as f32;
        let variance = health_scores
            .iter()
            .map(|&x| (x as f32 - avg_health).powi(2))
            .sum::<f32>() / health_scores.len() as f32;
        
        // Convert variance to stability score (lower variance = higher stability)
        let stability = if variance < 25.0 {
            100 - (variance as u8)
        } else {
            75
        };
        
        Ok(stability.max(0).min(100))
    }
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct NetworkConditionSummary {
    pub health_score: u8,
    pub congestion_level: u8,
    pub recommended_batch_size: u8,
    pub recommended_timeout: u32,
    pub suitable_for_batching: bool,
    pub latency_trend: NetworkTrend,
    pub throughput_trend: NetworkTrend,
    pub last_updated: i64,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct HistoricalTrends {
    pub latency_improvement: u16,  // Percentage improvement
    pub throughput_improvement: u16, // Percentage improvement
    pub health_trend: HealthTrend,
    pub stability_score: u8,       // 0-100, higher = more stable
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub enum HealthTrend {
    Improving,
    Degrading,
    Stable,
}

impl Default for HistoricalTrends {
    fn default() -> Self {
        Self {
            latency_improvement: 0,
            throughput_improvement: 0,
            health_trend: HealthTrend::Stable,
            stability_score: 80,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_network_condition_monitor_initialization() {
        let mut monitor = NetworkConditionMonitor {
            current_conditions: NetworkConditionMetrics::default(),
            historical_data: Vec::new(),
            config: MonitoringConfig::default(),
            last_update: 0,
            stats: MonitoringStats::default(),
            bump: 0,
        };

        let config = MonitoringConfig::default();
        assert!(monitor.initialize(config).is_ok());
        assert_eq!(monitor.config.update_interval, 30);
        assert_eq!(monitor.config.history_size, 10);
        assert!(monitor.config.enabled);
    }

    #[test]
    fn test_adaptive_batch_sizing() {
        let mut monitor = NetworkConditionMonitor {
            current_conditions: NetworkConditionMetrics {
                optimal_batch_size: 8,
                ..Default::default()
            },
            historical_data: Vec::new(),
            config: MonitoringConfig {
                adaptive_config: AdaptiveConfig {
                    min_batch_size: 2,
                    max_batch_size: 10,
                    ..Default::default()
                },
                ..Default::default()
            },
            last_update: 0,
            stats: MonitoringStats::default(),
            bump: 0,
        };

        assert_eq!(monitor.get_adaptive_batch_size(), 8);

        // Test bounds enforcement
        monitor.current_conditions.optimal_batch_size = 15; // Above max
        assert_eq!(monitor.get_adaptive_batch_size(), 10);

        monitor.current_conditions.optimal_batch_size = 1; // Below min
        assert_eq!(monitor.get_adaptive_batch_size(), 2);
    }

    #[test]
    fn test_network_suitability_check() {
        let monitor = NetworkConditionMonitor {
            current_conditions: NetworkConditionMetrics {
                network_health_score: 80,
                congestion_score: 30,
                transaction_success_rate: 9500,
                ..Default::default()
            },
            historical_data: Vec::new(),
            config: MonitoringConfig {
                alert_thresholds: AlertThresholds {
                    min_health_score: 50,
                    max_congestion_score: 80,
                    min_success_rate: 9000,
                    ..Default::default()
                },
                ..Default::default()
            },
            last_update: 0,
            stats: MonitoringStats::default(),
            bump: 0,
        };

        assert!(monitor.is_suitable_for_batching());

        // Test with poor conditions
        let poor_monitor = NetworkConditionMonitor {
            current_conditions: NetworkConditionMetrics {
                network_health_score: 30, // Below threshold
                congestion_score: 90,     // Above threshold
                transaction_success_rate: 8500, // Below threshold
                ..Default::default()
            },
            config: monitor.config.clone(),
            ..monitor
        };

        assert!(!poor_monitor.is_suitable_for_batching());
    }

    #[test]
    fn test_historical_trends_calculation() {
        let mut monitor = NetworkConditionMonitor {
            current_conditions: NetworkConditionMetrics {
                average_network_latency: 400,
                network_throughput_tps: 1200,
                network_health_score: 85,
                ..Default::default()
            },
            historical_data: Vec::new(),
            config: MonitoringConfig::default(),
            last_update: 0,
            stats: MonitoringStats::default(),
            bump: 0,
        };

        // Add historical data showing improvement
        let historical_condition = NetworkConditionMetrics {
            average_network_latency: 600, // Was higher (worse)
            network_throughput_tps: 1000, // Was lower
            network_health_score: 75,     // Was lower
            ..Default::default()
        };
        
        monitor.historical_data.push(historical_condition);

        let trends = monitor.calculate_historical_trends().unwrap();
        assert!(trends.latency_improvement > 0);
        assert!(trends.throughput_improvement > 0);
        assert!(matches!(trends.health_trend, HealthTrend::Improving));
    }
}