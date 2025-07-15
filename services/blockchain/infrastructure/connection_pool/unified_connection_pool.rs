// Constitutional Hash: cdd01ef066bc6cf2
//! Unified Connection Pool Management for ACGS Services
//! 
//! This module provides standardized connection pool configuration and management
//! across all ACGS blockchain services with cost optimization and performance monitoring.

use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::time::{Duration, Instant};

/// Connection pool types supported by ACGS services
#[derive(Clone, Debug, Serialize, Deserialize, PartialEq, Eq, Hash)]
pub enum ConnectionPoolType {
    /// Redis connection pool
    Redis,
    /// PostgreSQL connection pool
    PostgreSQL,
    /// Solana RPC connection pool
    SolanaRPC,
    /// MongoDB connection pool
    MongoDB,
    /// HTTP/REST API connection pool
    HttpClient,
    /// WebSocket connection pool
    WebSocket,
    /// gRPC connection pool
    Grpc,
}

/// Connection pool configuration with standardized parameters
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ConnectionPoolConfig {
    /// Pool type identifier
    pub pool_type: ConnectionPoolType,
    /// Service name using this pool
    pub service_name: String,
    /// Constitutional hash for validation
    pub constitutional_hash: String,
    
    // Core pool parameters
    /// Minimum number of connections to maintain
    pub min_connections: u32,
    /// Maximum number of connections allowed
    pub max_connections: u32,
    /// Initial number of connections to create
    pub initial_connections: u32,
    
    // Timeout configurations
    /// Connection timeout in seconds
    pub connection_timeout_seconds: u32,
    /// Idle timeout before closing connection in seconds
    pub idle_timeout_seconds: u32,
    /// Maximum connection lifetime in seconds
    pub max_lifetime_seconds: u32,
    /// Health check interval in seconds
    pub health_check_interval_seconds: u32,
    
    // Performance tuning
    /// Enable connection keep-alive
    pub keep_alive_enabled: bool,
    /// TCP keep-alive interval in seconds
    pub tcp_keep_alive_seconds: u32,
    /// Connection retry attempts
    pub retry_attempts: u32,
    /// Retry delay in milliseconds
    pub retry_delay_ms: u32,
    
    // Cost optimization
    /// Enable dynamic sizing based on load
    pub dynamic_sizing_enabled: bool,
    /// Scale-down threshold (percentage of idle connections)
    pub scale_down_threshold_percent: u8,
    /// Scale-up threshold (percentage of active connections)
    pub scale_up_threshold_percent: u8,
    /// Cost optimization mode
    pub cost_optimization_mode: CostOptimizationMode,
    
    // Monitoring
    /// Enable detailed metrics collection
    pub metrics_enabled: bool,
    /// Metrics collection interval in seconds
    pub metrics_interval_seconds: u32,
    /// Alert thresholds
    pub alert_thresholds: AlertThresholds,
}

/// Cost optimization modes for connection pools
#[derive(Clone, Debug, Serialize, Deserialize)]
pub enum CostOptimizationMode {
    /// Conservative: Prioritize reliability over cost
    Conservative,
    /// Balanced: Balance cost and performance
    Balanced,
    /// Aggressive: Minimize cost, accept some performance trade-offs
    Aggressive,
    /// Custom: User-defined optimization parameters
    Custom {
        target_utilization_percent: u8,
        scale_factor: f32,
    },
}

/// Alert thresholds for connection pool monitoring
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct AlertThresholds {
    /// High connection usage threshold (percentage)
    pub high_usage_threshold_percent: u8,
    /// Connection failure rate threshold (per minute)
    pub failure_rate_threshold_per_minute: u32,
    /// Average response time threshold (milliseconds)
    pub response_time_threshold_ms: u32,
    /// Queue depth threshold
    pub queue_depth_threshold: u32,
}

impl Default for AlertThresholds {
    fn default() -> Self {
        Self {
            high_usage_threshold_percent: 80,
            failure_rate_threshold_per_minute: 10,
            response_time_threshold_ms: 5000,
            queue_depth_threshold: 100,
        }
    }
}

impl Default for ConnectionPoolConfig {
    fn default() -> Self {
        Self {
            pool_type: ConnectionPoolType::Redis,
            service_name: "default".to_string(),
            constitutional_hash: "cdd01ef066bc6cf2".to_string(),
            min_connections: 5,
            max_connections: 50,
            initial_connections: 10,
            connection_timeout_seconds: 30,
            idle_timeout_seconds: 300,
            max_lifetime_seconds: 3600,
            health_check_interval_seconds: 60,
            keep_alive_enabled: true,
            tcp_keep_alive_seconds: 60,
            retry_attempts: 3,
            retry_delay_ms: 1000,
            dynamic_sizing_enabled: true,
            scale_down_threshold_percent: 20,
            scale_up_threshold_percent: 80,
            cost_optimization_mode: CostOptimizationMode::Balanced,
            metrics_enabled: true,
            metrics_interval_seconds: 30,
            alert_thresholds: AlertThresholds::default(),
        }
    }
}

/// Connection pool metrics for monitoring and optimization
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ConnectionPoolMetrics {
    /// Pool identifier
    pub pool_id: String,
    /// Current active connections
    pub active_connections: u32,
    /// Current idle connections
    pub idle_connections: u32,
    /// Total connections in pool
    pub total_connections: u32,
    /// Connections created since start
    pub connections_created: u64,
    /// Connections closed since start
    pub connections_closed: u64,
    /// Connection creation failures
    pub connection_failures: u32,
    /// Current queue depth (pending requests)
    pub queue_depth: u32,
    /// Average response time (milliseconds)
    pub average_response_time_ms: f64,
    /// P95 response time (milliseconds)
    pub p95_response_time_ms: u32,
    /// Pool utilization percentage
    pub utilization_percent: f64,
    /// Cost efficiency score (0-100)
    pub cost_efficiency_score: f64,
    /// Last metrics update timestamp
    pub last_updated: i64,
    /// Constitutional hash validation
    pub constitutional_hash: String,
}

impl Default for ConnectionPoolMetrics {
    fn default() -> Self {
        Self {
            pool_id: String::new(),
            active_connections: 0,
            idle_connections: 0,
            total_connections: 0,
            connections_created: 0,
            connections_closed: 0,
            connection_failures: 0,
            queue_depth: 0,
            average_response_time_ms: 0.0,
            p95_response_time_ms: 0,
            utilization_percent: 0.0,
            cost_efficiency_score: 100.0,
            last_updated: 0,
            constitutional_hash: "cdd01ef066bc6cf2".to_string(),
        }
    }
}

/// Unified connection pool manager
pub struct UnifiedConnectionPoolManager {
    pools: HashMap<String, ConnectionPoolInstance>,
    global_config: GlobalPoolConfig,
    metrics_collector: MetricsCollector,
}

/// Global configuration for all connection pools
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct GlobalPoolConfig {
    /// Constitutional hash for validation
    pub constitutional_hash: String,
    /// Global cost optimization enabled
    pub cost_optimization_enabled: bool,
    /// Global monitoring enabled
    pub monitoring_enabled: bool,
    /// Default configuration template
    pub default_config_template: ConnectionPoolConfig,
    /// Service-specific configuration overrides
    pub service_overrides: HashMap<String, ConnectionPoolConfig>,
    /// Emergency scale-down threshold (global)
    pub emergency_scale_down_threshold: f64,
    /// Maximum total connections across all pools
    pub global_max_connections: u32,
}

impl Default for GlobalPoolConfig {
    fn default() -> Self {
        Self {
            constitutional_hash: "cdd01ef066bc6cf2".to_string(),
            cost_optimization_enabled: true,
            monitoring_enabled: true,
            default_config_template: ConnectionPoolConfig::default(),
            service_overrides: HashMap::new(),
            emergency_scale_down_threshold: 0.95,
            global_max_connections: 1000,
        }
    }
}

/// Individual connection pool instance
struct ConnectionPoolInstance {
    config: ConnectionPoolConfig,
    metrics: ConnectionPoolMetrics,
    last_scale_action: Instant,
    scale_cooldown: Duration,
}

/// Metrics collector for all pools
struct MetricsCollector {
    collection_interval: Duration,
    last_collection: Instant,
    historical_metrics: HashMap<String, Vec<ConnectionPoolMetrics>>,
}

impl UnifiedConnectionPoolManager {
    /// Constitutional Hash: cdd01ef066bc6cf2
    /// Create new unified connection pool manager
    pub fn new(global_config: GlobalPoolConfig) -> Self {
        Self {
            pools: HashMap::new(),
            global_config,
            metrics_collector: MetricsCollector {
                collection_interval: Duration::from_secs(30),
                last_collection: Instant::now(),
                historical_metrics: HashMap::new(),
            },
        }
    }

    /// Register a new connection pool with standardized configuration
    pub fn register_pool(&mut self, pool_id: String, pool_type: ConnectionPoolType, service_name: String) -> Result<(), String> {
        // Get configuration for this service
        let mut config = self.global_config.service_overrides
            .get(&service_name)
            .cloned()
            .unwrap_or_else(|| {
                let mut template = self.global_config.default_config_template.clone();
                template.service_name = service_name.clone();
                template.pool_type = pool_type.clone();
                template
            });

        // Apply pool-type specific optimizations
        self.apply_pool_type_optimizations(&mut config, &pool_type);

        // Apply cost optimization
        if self.global_config.cost_optimization_enabled {
            self.apply_cost_optimizations(&mut config);
        }

        // Create pool instance
        let instance = ConnectionPoolInstance {
            config: config.clone(),
            metrics: ConnectionPoolMetrics {
                pool_id: pool_id.clone(),
                constitutional_hash: config.constitutional_hash.clone(),
                ..Default::default()
            },
            last_scale_action: Instant::now(),
            scale_cooldown: Duration::from_secs(60), // 1 minute cooldown
        };

        self.pools.insert(pool_id, instance);
        Ok(())
    }

    /// Apply pool-type specific configuration optimizations
    fn apply_pool_type_optimizations(&self, config: &mut ConnectionPoolConfig, pool_type: &ConnectionPoolType) {
        match pool_type {
            ConnectionPoolType::Redis => {
                // Redis optimizations
                config.min_connections = 5;
                config.max_connections = 25;
                config.connection_timeout_seconds = 5;
                config.idle_timeout_seconds = 300;
                config.tcp_keep_alive_seconds = 60;
            },
            ConnectionPoolType::PostgreSQL => {
                // PostgreSQL optimizations
                config.min_connections = 10;
                config.max_connections = 100;
                config.connection_timeout_seconds = 30;
                config.idle_timeout_seconds = 600;
                config.max_lifetime_seconds = 3600;
            },
            ConnectionPoolType::SolanaRPC => {
                // Solana RPC optimizations
                config.min_connections = 3;
                config.max_connections = 15;
                config.connection_timeout_seconds = 15;
                config.retry_attempts = 5;
                config.retry_delay_ms = 2000;
            },
            ConnectionPoolType::HttpClient => {
                // HTTP client optimizations
                config.min_connections = 20;
                config.max_connections = 200;
                config.connection_timeout_seconds = 10;
                config.keep_alive_enabled = true;
                config.tcp_keep_alive_seconds = 30;
            },
            ConnectionPoolType::MongoDB => {
                // MongoDB optimizations
                config.min_connections = 5;
                config.max_connections = 50;
                config.connection_timeout_seconds = 20;
                config.idle_timeout_seconds = 300;
            },
            ConnectionPoolType::WebSocket => {
                // WebSocket optimizations
                config.min_connections = 2;
                config.max_connections = 10;
                config.connection_timeout_seconds = 30;
                config.health_check_interval_seconds = 30;
            },
            ConnectionPoolType::Grpc => {
                // gRPC optimizations
                config.min_connections = 5;
                config.max_connections = 50;
                config.connection_timeout_seconds = 10;
                config.keep_alive_enabled = true;
                config.tcp_keep_alive_seconds = 30;
            },
        }
    }

    /// Apply cost optimization strategies
    fn apply_cost_optimizations(&self, config: &mut ConnectionPoolConfig) {
        match config.cost_optimization_mode {
            CostOptimizationMode::Conservative => {
                // Maintain higher connection counts for reliability
                config.min_connections = (config.min_connections as f32 * 1.2) as u32;
                config.scale_down_threshold_percent = 30;
                config.scale_up_threshold_percent = 70;
            },
            CostOptimizationMode::Balanced => {
                // Standard optimization
                config.dynamic_sizing_enabled = true;
                config.scale_down_threshold_percent = 20;
                config.scale_up_threshold_percent = 80;
            },
            CostOptimizationMode::Aggressive => {
                // Minimize connections for cost savings
                config.min_connections = ((config.min_connections as f32 * 0.7) as u32).max(1);
                config.max_connections = (config.max_connections as f32 * 0.8) as u32;
                config.scale_down_threshold_percent = 10;
                config.scale_up_threshold_percent = 90;
                config.idle_timeout_seconds = 180; // Shorter idle timeout
            },
            CostOptimizationMode::Custom { target_utilization_percent, scale_factor } => {
                // Custom optimization
                config.scale_up_threshold_percent = target_utilization_percent;
                config.scale_down_threshold_percent = (target_utilization_percent as f32 * 0.3) as u8;
                config.max_connections = (config.max_connections as f32 * scale_factor) as u32;
            },
        }
    }

    /// Update pool metrics and trigger scaling if needed
    pub fn update_pool_metrics(&mut self, pool_id: &str, active_connections: u32, queue_depth: u32, response_time_ms: f64) -> Result<(), String> {
        let pool_id_owned = pool_id.to_string();

        // Update metrics in a separate scope to end the mutable borrow
        let (metrics_clone, config_clone) = {
            let instance = self.pools.get_mut(pool_id)
                .ok_or_else(|| format!("Pool {} not found", pool_id))?;

            // Update metrics
            instance.metrics.active_connections = active_connections;
            instance.metrics.queue_depth = queue_depth;
            instance.metrics.average_response_time_ms = response_time_ms;
            instance.metrics.total_connections = active_connections + instance.metrics.idle_connections;
            instance.metrics.utilization_percent = if instance.metrics.total_connections > 0 {
                (active_connections as f64 / instance.metrics.total_connections as f64) * 100.0
            } else {
                0.0
            };
            instance.metrics.last_updated = std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)
                .map(|d| d.as_secs() as i64)
                .unwrap_or_else(|_| 0); // Fallback to 0 if system time is before UNIX_EPOCH

            // Clone data for cost efficiency calculation
            (instance.metrics.clone(), instance.config.clone())
        }; // Mutable borrow ends here

        let cost_efficiency_score = self.calculate_cost_efficiency(&metrics_clone, &config_clone);

        // Re-acquire the mutable borrow to update the score
        if let Some(instance) = self.pools.get_mut(&pool_id_owned) {
            instance.metrics.cost_efficiency_score = cost_efficiency_score;
        }

        // Check if scaling is needed
        if let Some(instance) = self.pools.get(&pool_id_owned) {
            if instance.config.dynamic_sizing_enabled {
                self.check_and_apply_scaling(&pool_id_owned)?;
            }
        }

        Ok(())
    }

    /// Calculate cost efficiency score for a pool
    fn calculate_cost_efficiency(&self, metrics: &ConnectionPoolMetrics, config: &ConnectionPoolConfig) -> f64 {
        let utilization = metrics.utilization_percent / 100.0;
        let target_utilization = match config.cost_optimization_mode {
            CostOptimizationMode::Conservative => 0.5,
            CostOptimizationMode::Balanced => 0.7,
            CostOptimizationMode::Aggressive => 0.85,
            CostOptimizationMode::Custom { target_utilization_percent, .. } => target_utilization_percent as f64 / 100.0,
        };

        // Score based on how close to target utilization
        let utilization_score = 100.0 - ((utilization - target_utilization).abs() * 100.0);
        
        // Penalty for high response times
        let response_penalty = if metrics.average_response_time_ms > config.alert_thresholds.response_time_threshold_ms as f64 {
            20.0
        } else {
            0.0
        };

        // Penalty for connection failures
        let failure_penalty = (metrics.connection_failures as f64 * 2.0).min(30.0);

        (utilization_score - response_penalty - failure_penalty).max(0.0).min(100.0)
    }

    /// Check if scaling is needed and apply it
    fn check_and_apply_scaling(&mut self, pool_id: &str) -> Result<(), String> {
        let instance = self.pools.get_mut(pool_id)
            .ok_or_else(|| format!("Pool {} not found", pool_id))?;

        // Check cooldown period
        if instance.last_scale_action.elapsed() < instance.scale_cooldown {
            return Ok(()); // Still in cooldown
        }

        let utilization = instance.metrics.utilization_percent;
        let config = &instance.config;
        let current_total = instance.metrics.total_connections;
        
        let scaling_action = if utilization > config.scale_up_threshold_percent as f64 {
            // Scale up
            let new_size = (current_total as f32 * 1.5) as u32;
            Some(new_size.min(config.max_connections))
        } else if utilization < config.scale_down_threshold_percent as f64 {
            // Scale down
            let new_size = (current_total as f32 * 0.8) as u32;
            Some(new_size.max(config.min_connections))
        } else {
            None
        };

        if let Some(new_size) = scaling_action {
            if new_size != current_total {
                self.apply_scaling(pool_id, new_size)?;
                let instance = self.pools.get_mut(pool_id)
                    .ok_or_else(|| format!("Pool {} not found for scaling update", pool_id))?;
                instance.last_scale_action = Instant::now();
            }
        }

        Ok(())
    }

    /// Apply scaling to a connection pool
    fn apply_scaling(&mut self, pool_id: &str, new_size: u32) -> Result<(), String> {
        // In a real implementation, this would:
        // 1. Gradually adjust connection count
        // 2. Monitor for errors during scaling
        // 3. Rollback if scaling causes issues
        
        println!("Scaling pool {} to {} connections - Constitutional Hash: cdd01ef066bc6cf2", 
                 pool_id, new_size);
        
        if let Some(instance) = self.pools.get_mut(pool_id) {
            instance.metrics.total_connections = new_size;
            // Simulate connection distribution
            instance.metrics.idle_connections = new_size - instance.metrics.active_connections;
        }
        
        Ok(())
    }

    /// Get standardized configuration for a service
    pub fn get_standardized_config(&self, service_name: &str, pool_type: ConnectionPoolType) -> ConnectionPoolConfig {
        let mut config = self.global_config.service_overrides
            .get(service_name)
            .cloned()
            .unwrap_or_else(|| {
                let mut template = self.global_config.default_config_template.clone();
                template.service_name = service_name.to_string();
                template.pool_type = pool_type.clone();
                template
            });

        // Apply pool-type optimizations
        self.apply_pool_type_optimizations(&mut config, &pool_type);

        // Apply cost optimizations if enabled
        if self.global_config.cost_optimization_enabled {
            self.apply_cost_optimizations(&mut config);
        }

        config
    }

    /// Get comprehensive pool metrics report
    pub fn get_pools_report(&self) -> ConnectionPoolsReport {
        let pool_metrics: Vec<_> = self.pools.iter()
            .map(|(id, instance)| (id.clone(), instance.metrics.clone()))
            .collect();

        let total_connections: u32 = pool_metrics.iter()
            .map(|(_, metrics)| metrics.total_connections)
            .sum();

        let average_utilization: f64 = if !pool_metrics.is_empty() {
            pool_metrics.iter()
                .map(|(_, metrics)| metrics.utilization_percent)
                .sum::<f64>() / pool_metrics.len() as f64
        } else {
            0.0
        };

        let average_cost_efficiency: f64 = if !pool_metrics.is_empty() {
            pool_metrics.iter()
                .map(|(_, metrics)| metrics.cost_efficiency_score)
                .sum::<f64>() / pool_metrics.len() as f64
        } else {
            100.0
        };

        ConnectionPoolsReport {
            constitutional_hash: self.global_config.constitutional_hash.clone(),
            total_pools: self.pools.len() as u32,
            total_connections,
            average_utilization,
            average_cost_efficiency,
            pool_metrics,
            cost_optimization_enabled: self.global_config.cost_optimization_enabled,
            monitoring_enabled: self.global_config.monitoring_enabled,
            recommendations: self.generate_optimization_recommendations(),
        }
    }

    /// Generate optimization recommendations
    fn generate_optimization_recommendations(&self) -> Vec<String> {
        let mut recommendations = Vec::new();

        for (pool_id, instance) in &self.pools {
            let metrics = &instance.metrics;
            
            if metrics.cost_efficiency_score < 60.0 {
                recommendations.push(format!("Pool {}: Consider optimizing configuration for better cost efficiency", pool_id));
            }
            
            if metrics.utilization_percent < 20.0 {
                recommendations.push(format!("Pool {}: Low utilization - consider reducing pool size", pool_id));
            }
            
            if metrics.utilization_percent > 90.0 {
                recommendations.push(format!("Pool {}: High utilization - consider increasing pool size", pool_id));
            }
            
            if metrics.average_response_time_ms > instance.config.alert_thresholds.response_time_threshold_ms as f64 {
                recommendations.push(format!("Pool {}: High response times - investigate performance issues", pool_id));
            }
        }

        if recommendations.is_empty() {
            recommendations.push("All connection pools are operating optimally".to_string());
        }

        recommendations
    }

    /// Collect and store historical metrics
    pub fn collect_metrics(&mut self) {
        if self.metrics_collector.last_collection.elapsed() < self.metrics_collector.collection_interval {
            return;
        }

        for (pool_id, instance) in &self.pools {
            self.metrics_collector.historical_metrics
                .entry(pool_id.clone())
                .or_insert_with(Vec::new)
                .push(instance.metrics.clone());

            // Keep only last 100 entries per pool
            if let Some(history) = self.metrics_collector.historical_metrics.get_mut(pool_id) {
                if history.len() > 100 {
                    history.remove(0);
                }
            }
        }

        self.metrics_collector.last_collection = Instant::now();
    }

    /// Emergency scale-down all pools (e.g., during cost emergencies)
    pub fn emergency_scale_down(&mut self, scale_factor: f64) -> Result<(), String> {
        let pool_ids: Vec<String> = self.pools.keys().cloned().collect();

        for pool_id in pool_ids {
            let (current_size, min_connections) = {
                let instance = self.pools.get(&pool_id)
                    .ok_or_else(|| format!("Pool {} not found", pool_id))?;
                (instance.metrics.total_connections, instance.config.min_connections)
            };

            let new_size = ((current_size as f64 * scale_factor) as u32)
                .max(min_connections);

            if new_size < current_size {
                self.apply_scaling(&pool_id, new_size)?;
                println!("Emergency scaled down pool {} from {} to {} connections",
                         pool_id, current_size, new_size);
            }
        }
        Ok(())
    }
}

/// Comprehensive connection pools report
#[derive(Clone, Debug, Serialize, Deserialize)]
pub struct ConnectionPoolsReport {
    pub constitutional_hash: String,
    pub total_pools: u32,
    pub total_connections: u32,
    pub average_utilization: f64,
    pub average_cost_efficiency: f64,
    pub pool_metrics: Vec<(String, ConnectionPoolMetrics)>,
    pub cost_optimization_enabled: bool,
    pub monitoring_enabled: bool,
    pub recommendations: Vec<String>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_default_configuration() {
        let config = ConnectionPoolConfig::default();
        assert_eq!(config.constitutional_hash, "cdd01ef066bc6cf2");
        assert!(config.dynamic_sizing_enabled);
        assert!(config.metrics_enabled);
    }

    #[test]
    fn test_pool_type_optimizations() {
        let global_config = GlobalPoolConfig::default();
        let manager = UnifiedConnectionPoolManager::new(global_config);
        
        let redis_config = manager.get_standardized_config("test-service", ConnectionPoolType::Redis);
        assert_eq!(redis_config.max_connections, 25);
        
        let postgres_config = manager.get_standardized_config("test-service", ConnectionPoolType::PostgreSQL);
        assert_eq!(postgres_config.max_connections, 100);
    }

    #[test]
    fn test_cost_optimization_modes() {
        let mut config = ConnectionPoolConfig::default();
        config.min_connections = 10;
        config.max_connections = 100;
        
        let manager = UnifiedConnectionPoolManager::new(GlobalPoolConfig::default());
        
        // Test aggressive optimization
        config.cost_optimization_mode = CostOptimizationMode::Aggressive;
        let mut test_config = config.clone();
        manager.apply_cost_optimizations(&mut test_config);
        assert!(test_config.min_connections < config.min_connections);
        assert!(test_config.max_connections < config.max_connections);
    }

    #[test]
    fn test_metrics_calculation() {
        let global_config = GlobalPoolConfig::default();
        let manager = UnifiedConnectionPoolManager::new(global_config);
        
        let config = ConnectionPoolConfig::default();
        let mut metrics = ConnectionPoolMetrics::default();
        metrics.active_connections = 30;
        metrics.total_connections = 50;
        metrics.utilization_percent = 60.0;
        metrics.average_response_time_ms = 100.0;
        
        let efficiency = manager.calculate_cost_efficiency(&metrics, &config);
        assert!(efficiency > 0.0);
        assert!(efficiency <= 100.0);
    }

    #[test]
    fn test_pool_registration() {
        let global_config = GlobalPoolConfig::default();
        let mut manager = UnifiedConnectionPoolManager::new(global_config);
        
        let result = manager.register_pool(
            "test-redis".to_string(),
            ConnectionPoolType::Redis,
            "test-service".to_string()
        );
        
        assert!(result.is_ok());
        assert!(manager.pools.contains_key("test-redis"));
    }

    #[test]
    fn test_scaling_logic() {
        let global_config = GlobalPoolConfig::default();
        let mut manager = UnifiedConnectionPoolManager::new(global_config);
        
        manager.register_pool(
            "test-pool".to_string(),
            ConnectionPoolType::Redis,
            "test-service".to_string()
        ).unwrap();
        
        // Simulate high utilization
        manager.update_pool_metrics("test-pool", 20, 5, 100.0).unwrap();
        
        let pool = manager.pools.get("test-pool").unwrap();
        assert!(pool.metrics.utilization_percent > 0.0);
    }
}