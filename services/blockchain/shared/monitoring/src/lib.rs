// Constitutional Hash: cdd01ef066bc6cf2
//! ACGS-2 Shared Monitoring and Observability Components
//! 
//! This library provides unified monitoring, metrics, and observability
//! components for both expert service and blockchain components.

use acgs_constitutional::{ConstitutionalCompliance, ConstitutionalError, ConstitutionalMetadata, CONSTITUTIONAL_HASH};
use acgs_types::Decision;
use prometheus::{Gauge, Histogram, IntCounter, IntGauge, Registry};
use serde::{Deserialize, Serialize};
use std::time::{Duration, Instant};
use thiserror::Error;

/// Monitoring errors
#[derive(Error, Debug)]
pub enum MonitoringError {
    #[error("Metrics registration failed: {0}")]
    MetricsRegistration(String),
    
    #[error("Constitutional compliance error: {0}")]
    Constitutional(#[from] ConstitutionalError),
    
    #[error("Monitoring configuration error: {0}")]
    Configuration(String),
}

/// Performance metrics for ACGS-2 components
#[derive(Debug, Clone)]
pub struct AcgsMetrics {
    // Governance decision metrics
    pub governance_decisions_total: IntCounter,
    pub governance_decision_latency: Histogram,
    pub governance_confidence_score: Gauge,
    
    // Constitutional compliance metrics
    pub constitutional_validations_total: IntCounter,
    pub constitutional_violations_total: IntCounter,
    
    // Blockchain metrics
    pub blockchain_transactions_total: IntCounter,
    pub blockchain_transaction_latency: Histogram,
    pub blockchain_errors_total: IntCounter,
    
    // LLM provider metrics
    pub llm_requests_total: IntCounter,
    pub llm_request_latency: Histogram,
    pub llm_errors_total: IntCounter,
    
    // Cache metrics
    pub cache_hits_total: IntCounter,
    pub cache_misses_total: IntCounter,
    pub cache_size: IntGauge,
    
    // System health metrics
    pub system_uptime: Gauge,
    pub active_connections: IntGauge,
    pub memory_usage: Gauge,
}

impl AcgsMetrics {
    /// Create new ACGS metrics with default registry
    pub fn new() -> Result<Self, MonitoringError> {
        Self::with_registry(&prometheus::default_registry())
    }
    
    /// Create new ACGS metrics with custom registry
    pub fn with_registry(registry: &Registry) -> Result<Self, MonitoringError> {
        let governance_decisions_total = IntCounter::new(
            "acgs_governance_decisions_total",
            "Total number of governance decisions made"
        ).map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        
        let governance_decision_latency = Histogram::with_opts(
            prometheus::HistogramOpts::new(
                "acgs_governance_decision_latency_seconds",
                "Latency of governance decisions in seconds"
            ).buckets(vec![0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 5.0])
        ).map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        
        let governance_confidence_score = Gauge::new(
            "acgs_governance_confidence_score",
            "Current governance decision confidence score"
        ).map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        
        let constitutional_validations_total = IntCounter::new(
            "acgs_constitutional_validations_total",
            "Total number of constitutional validations performed"
        ).map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        
        let constitutional_violations_total = IntCounter::new(
            "acgs_constitutional_violations_total",
            "Total number of constitutional violations detected"
        ).map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        
        let blockchain_transactions_total = IntCounter::new(
            "acgs_blockchain_transactions_total",
            "Total number of blockchain transactions"
        ).map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        
        let blockchain_transaction_latency = Histogram::with_opts(
            prometheus::HistogramOpts::new(
                "acgs_blockchain_transaction_latency_seconds",
                "Latency of blockchain transactions in seconds"
            ).buckets(vec![0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0])
        ).map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        
        let blockchain_errors_total = IntCounter::new(
            "acgs_blockchain_errors_total",
            "Total number of blockchain errors"
        ).map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        
        let llm_requests_total = IntCounter::new(
            "acgs_llm_requests_total",
            "Total number of LLM requests"
        ).map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        
        let llm_request_latency = Histogram::with_opts(
            prometheus::HistogramOpts::new(
                "acgs_llm_request_latency_seconds",
                "Latency of LLM requests in seconds"
            ).buckets(vec![0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0])
        ).map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        
        let llm_errors_total = IntCounter::new(
            "acgs_llm_errors_total",
            "Total number of LLM errors"
        ).map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        
        let cache_hits_total = IntCounter::new(
            "acgs_cache_hits_total",
            "Total number of cache hits"
        ).map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        
        let cache_misses_total = IntCounter::new(
            "acgs_cache_misses_total",
            "Total number of cache misses"
        ).map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        
        let cache_size = IntGauge::new(
            "acgs_cache_size",
            "Current cache size"
        ).map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        
        let system_uptime = Gauge::new(
            "acgs_system_uptime_seconds",
            "System uptime in seconds"
        ).map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        
        let active_connections = IntGauge::new(
            "acgs_active_connections",
            "Number of active connections"
        ).map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        
        let memory_usage = Gauge::new(
            "acgs_memory_usage_bytes",
            "Memory usage in bytes"
        ).map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        
        // Register all metrics
        registry.register(Box::new(governance_decisions_total.clone()))
            .map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        registry.register(Box::new(governance_decision_latency.clone()))
            .map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        registry.register(Box::new(governance_confidence_score.clone()))
            .map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        registry.register(Box::new(constitutional_validations_total.clone()))
            .map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        registry.register(Box::new(constitutional_violations_total.clone()))
            .map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        registry.register(Box::new(blockchain_transactions_total.clone()))
            .map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        registry.register(Box::new(blockchain_transaction_latency.clone()))
            .map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        registry.register(Box::new(blockchain_errors_total.clone()))
            .map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        registry.register(Box::new(llm_requests_total.clone()))
            .map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        registry.register(Box::new(llm_request_latency.clone()))
            .map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        registry.register(Box::new(llm_errors_total.clone()))
            .map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        registry.register(Box::new(cache_hits_total.clone()))
            .map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        registry.register(Box::new(cache_misses_total.clone()))
            .map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        registry.register(Box::new(cache_size.clone()))
            .map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        registry.register(Box::new(system_uptime.clone()))
            .map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        registry.register(Box::new(active_connections.clone()))
            .map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        registry.register(Box::new(memory_usage.clone()))
            .map_err(|e| MonitoringError::MetricsRegistration(e.to_string()))?;
        
        Ok(Self {
            governance_decisions_total,
            governance_decision_latency,
            governance_confidence_score,
            constitutional_validations_total,
            constitutional_violations_total,
            blockchain_transactions_total,
            blockchain_transaction_latency,
            blockchain_errors_total,
            llm_requests_total,
            llm_request_latency,
            llm_errors_total,
            cache_hits_total,
            cache_misses_total,
            cache_size,
            system_uptime,
            active_connections,
            memory_usage,
        })
    }
    
    /// Record a governance decision
    pub fn record_governance_decision(&self, decision: &Decision, confidence: f64, latency: Duration) {
        self.governance_decisions_total.inc();
        self.governance_decision_latency.observe(latency.as_secs_f64());
        self.governance_confidence_score.set(confidence);
        
        tracing::info!(
            "📊 Governance decision recorded: decision={}, confidence={:.2}, latency={:.3}s",
            decision,
            confidence,
            latency.as_secs_f64()
        );
    }
    
    /// Record constitutional validation
    pub fn record_constitutional_validation(&self, is_valid: bool) {
        if is_valid {
            self.constitutional_validations_total.inc();
        } else {
            self.constitutional_violations_total.inc();
        }
    }
    
    /// Record blockchain transaction
    pub fn record_blockchain_transaction(&self, success: bool, latency: Duration) {
        self.blockchain_transactions_total.inc();
        self.blockchain_transaction_latency.observe(latency.as_secs_f64());
        
        if !success {
            self.blockchain_errors_total.inc();
        }
    }
    
    /// Record LLM request
    pub fn record_llm_request(&self, success: bool, latency: Duration) {
        self.llm_requests_total.inc();
        self.llm_request_latency.observe(latency.as_secs_f64());
        
        if !success {
            self.llm_errors_total.inc();
        }
    }
    
    /// Record cache operation
    pub fn record_cache_operation(&self, hit: bool, current_size: i64) {
        if hit {
            self.cache_hits_total.inc();
        } else {
            self.cache_misses_total.inc();
        }
        self.cache_size.set(current_size);
    }
    
    /// Get cache hit rate
    pub fn cache_hit_rate(&self) -> f64 {
        let hits = self.cache_hits_total.get() as f64;
        let misses = self.cache_misses_total.get() as f64;
        let total = hits + misses;
        
        if total == 0.0 {
            0.0
        } else {
            hits / total
        }
    }
}

/// Performance timer for measuring operation latency
pub struct PerformanceTimer {
    start: Instant,
    operation: String,
    constitutional_metadata: ConstitutionalMetadata,
}

impl PerformanceTimer {
    /// Start a new performance timer
    pub fn start(operation: impl Into<String>) -> Self {
        Self {
            start: Instant::now(),
            operation: operation.into(),
            constitutional_metadata: ConstitutionalMetadata::new("performance-timer"),
        }
    }
    
    /// Stop the timer and return elapsed duration
    pub fn stop(self) -> Duration {
        let elapsed = self.start.elapsed();
        tracing::debug!(
            "⏱️ Operation '{}' completed in {:.3}s",
            self.operation,
            elapsed.as_secs_f64()
        );
        elapsed
    }
    
    /// Stop the timer and record to metrics
    pub fn stop_and_record<F>(self, record_fn: F) -> Duration 
    where
        F: FnOnce(Duration),
    {
        let elapsed = self.stop();
        record_fn(elapsed);
        elapsed
    }
}

impl ConstitutionalCompliance for PerformanceTimer {
    fn validate_constitutional_compliance(&self) -> Result<(), ConstitutionalError> {
        self.constitutional_metadata.validate_constitutional_compliance()
    }
    
    fn constitutional_hash(&self) -> &str {
        self.constitutional_metadata.constitutional_hash()
    }
}

/// Health check status
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HealthStatus {
    pub status: String,
    pub timestamp: i64,
    pub constitutional_hash: String,
    pub version: String,
    pub uptime_seconds: u64,
    pub components: Vec<ComponentHealth>,
}

/// Individual component health
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ComponentHealth {
    pub name: String,
    pub status: String,
    pub last_check: i64,
    pub details: Option<String>,
}

impl HealthStatus {
    /// Create a new health status
    pub fn new(version: impl Into<String>, uptime_seconds: u64) -> Self {
        Self {
            status: "healthy".to_string(),
            timestamp: chrono::Utc::now().timestamp(),
            constitutional_hash: CONSTITUTIONAL_HASH.to_string(),
            version: version.into(),
            uptime_seconds,
            components: Vec::new(),
        }
    }
    
    /// Add component health
    pub fn add_component(mut self, name: impl Into<String>, status: impl Into<String>) -> Self {
        self.components.push(ComponentHealth {
            name: name.into(),
            status: status.into(),
            last_check: chrono::Utc::now().timestamp(),
            details: None,
        });
        self
    }
    
    /// Add component health with details
    pub fn add_component_with_details(
        mut self,
        name: impl Into<String>,
        status: impl Into<String>,
        details: impl Into<String>,
    ) -> Self {
        self.components.push(ComponentHealth {
            name: name.into(),
            status: status.into(),
            last_check: chrono::Utc::now().timestamp(),
            details: Some(details.into()),
        });
        self
    }
    
    /// Check if all components are healthy
    pub fn is_healthy(&self) -> bool {
        self.components.iter().all(|c| c.status == "healthy")
    }
}

impl ConstitutionalCompliance for HealthStatus {
    fn validate_constitutional_compliance(&self) -> Result<(), ConstitutionalError> {
        if self.constitutional_hash != CONSTITUTIONAL_HASH {
            return Err(ConstitutionalError::HashMismatch {
                expected: CONSTITUTIONAL_HASH.to_string(),
                actual: self.constitutional_hash.clone(),
            });
        }
        Ok(())
    }
    
    fn constitutional_hash(&self) -> &str {
        &self.constitutional_hash
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;
    use std::time::Duration;

    #[test]
    fn test_acgs_metrics_creation() {
        let metrics = AcgsMetrics::new().unwrap();
        assert_eq!(metrics.governance_decisions_total.get(), 0);
    }

    #[test]
    fn test_performance_timer() {
        let timer = PerformanceTimer::start("test_operation");
        thread::sleep(Duration::from_millis(10));
        let elapsed = timer.stop();
        assert!(elapsed >= Duration::from_millis(10));
    }

    #[test]
    fn test_health_status() {
        let health = HealthStatus::new("1.0.0", 3600)
            .add_component("database", "healthy")
            .add_component_with_details("cache", "healthy", "Redis connected");
        
        assert!(health.is_healthy());
        assert!(health.is_constitutionally_compliant());
    }
}
