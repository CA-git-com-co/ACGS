// Constitutional Hash: cdd01ef066bc6cf2
//! Connection Pool Management Module for ACGS Services
//! 
//! This module provides unified connection pool management with standardized
//! configurations, dynamic sizing, and cost optimization across all services.

pub mod unified_connection_pool;
pub mod dynamic_sizing;

pub use unified_connection_pool::*;
pub use dynamic_sizing::*;

/// Connection pool module configuration
#[derive(Clone, Debug)]
pub struct ConnectionPoolModuleConfig {
    pub constitutional_hash: String,
    pub global_optimization_enabled: bool,
    pub monitoring_enabled: bool,
    pub emergency_procedures_enabled: bool,
}

impl Default for ConnectionPoolModuleConfig {
    fn default() -> Self {
        Self {
            constitutional_hash: "cdd01ef066bc6cf2".to_string(),
            global_optimization_enabled: true,
            monitoring_enabled: true,
            emergency_procedures_enabled: true,
        }
    }
}