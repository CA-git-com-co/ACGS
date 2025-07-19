/*!
 * ACGS-2 Constitutional AI Governance System - Rust Frontend
 * Constitutional Hash: cdd01ef066bc6cf2
 * 
 * A high-performance, memory-safe frontend for the ACGS-2 system built with Rust and WebAssembly.
 * Provides constitutional compliance validation, real-time service integration, and adaptive UI.
 */

use wasm_bindgen::prelude::*;

// Use `wee_alloc` as the global allocator for smaller bundle size
#[global_allocator]
static ALLOC: wee_alloc::WeeAlloc = wee_alloc::WeeAlloc::INIT;

// Core modules - organized for code splitting
pub mod app;
pub mod components;
pub mod types;
pub mod utils;
pub mod state;
pub mod api;
pub mod performance;
pub mod router;
pub mod cache_manager;

// Re-exports
pub use app::App;

// Constitutional compliance constants
pub const CONSTITUTIONAL_HASH: &str = "cdd01ef066bc6cf2";

// Performance targets
pub const PERFORMANCE_TARGETS: PerformanceTargets = PerformanceTargets {
    p99_latency_ms: 5,
    throughput_rps: 100,
    cache_hit_rate: 0.85,
};

#[derive(Debug, Clone, PartialEq)]
pub struct PerformanceTargets {
    pub p99_latency_ms: u32,
    pub throughput_rps: u32,
    pub cache_hit_rate: f64,
}

// WASM entry point
#[cfg(not(test))]
#[wasm_bindgen(start)]
pub fn main() {
    // Initialize logging only in debug mode for smaller release builds
    #[cfg(debug_assertions)]
    {
        console_log::init_with_level(log::Level::Info).expect("Failed to initialize logger");
        #[cfg(feature = "console_error_panic_hook")]
        console_error_panic_hook::set_once();
        log::info!("ACGS-2 Rust Frontend starting...");
        log::info!("Constitutional Hash: {}", CONSTITUTIONAL_HASH);
    }

    // Initialize performance monitoring only in debug mode
    #[cfg(debug_assertions)]
    let _timer = performance::PerformanceTimer::new("app-initialization");

    // Mount the Yew app
    yew::Renderer::<App>::new().render();
}

// Utility function to validate constitutional hash
pub fn validate_constitutional_hash(hash: &str) -> bool {
    hash == CONSTITUTIONAL_HASH
}

/// Initialize performance monitoring for P99 <5ms targets
pub fn init_performance_monitoring() {
    if let Some(window) = web_sys::window() {
        if let Some(performance) = window.performance() {
            // Mark the initialization time
            performance.mark("acgs-init-start").ok();

            // Log performance targets
            log::info!("Performance targets: P99 <{}ms, Throughput >{}RPS, Cache hit rate >{}%",
                PERFORMANCE_TARGETS.p99_latency_ms,
                PERFORMANCE_TARGETS.throughput_rps,
                (PERFORMANCE_TARGETS.cache_hit_rate * 100.0) as u32
            );
        }
    }
}

/// Measure and log performance metrics
pub fn measure_performance(operation: &str) -> f64 {
    if let Some(window) = web_sys::window() {
        if let Some(performance) = window.performance() {
            let start_time = performance.now();
            performance.mark(&format!("{}-start", operation)).ok();
            return start_time;
        }
    }
    0.0
}

/// End performance measurement and validate against targets
pub fn end_performance_measurement(operation: &str, start_time: f64) {
    if let Some(window) = web_sys::window() {
        if let Some(performance) = window.performance() {
            let end_time = performance.now();
            let duration = end_time - start_time;

            performance.mark(&format!("{}-end", operation)).ok();
            performance.measure_with_start_mark_and_end_mark(
                operation,
                &format!("{}-start", operation),
                &format!("{}-end", operation)
            ).ok();

            // Validate against P99 target
            if duration > PERFORMANCE_TARGETS.p99_latency_ms as f64 {
                log::warn!("Performance target exceeded for {}: {}ms > {}ms",
                    operation, duration, PERFORMANCE_TARGETS.p99_latency_ms);
            } else {
                log::debug!("Performance OK for {}: {}ms", operation, duration);
            }
        }
    }
}



// Constitutional compliance utilities
pub mod constitutional {
    use sha2::{Sha256, Digest};
    use serde::{Deserialize, Serialize};
    
    #[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
    pub struct ConstitutionalCompliance {
        pub hash: String,
        pub compliant: bool,
        pub score: f64,
        pub violations: Vec<String>,
        pub last_validated: String,
        pub metadata: serde_json::Value,
    }
    
    impl Default for ConstitutionalCompliance {
        fn default() -> Self {
            Self {
                hash: crate::CONSTITUTIONAL_HASH.to_string(),
                compliant: true,
                score: 1.0,
                violations: Vec::new(),
                last_validated: chrono::Utc::now().to_rfc3339(),
                metadata: serde_json::Value::Object(serde_json::Map::new()),
            }
        }
    }
    
    pub fn validate_hash(data: &str) -> String {
        let mut hasher = Sha256::new();
        hasher.update(data.as_bytes());
        hex::encode(hasher.finalize())
    }
    
    pub fn is_constitutionally_compliant(compliance: &ConstitutionalCompliance) -> bool {
        compliance.hash == crate::CONSTITUTIONAL_HASH && 
        compliance.compliant && 
        compliance.score >= 0.95
    }
}

// Simple error type
#[derive(Debug)]
pub enum ACGSError {
    ConstitutionalViolation(String),
    ServiceError(String),
    PerformanceViolation { metric: String, value: f64, target: f64 },
    AuthError(String),
    NetworkError(String),
}

impl std::fmt::Display for ACGSError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            ACGSError::ConstitutionalViolation(msg) => write!(f, "Constitutional compliance violation: {}", msg),
            ACGSError::ServiceError(msg) => write!(f, "Service communication error: {}", msg),
            ACGSError::PerformanceViolation { metric, value, target } => {
                write!(f, "Performance target violation: {} = {}, target = {}", metric, value, target)
            }
            ACGSError::AuthError(msg) => write!(f, "Authentication error: {}", msg),
            ACGSError::NetworkError(msg) => write!(f, "Network error: {}", msg),
        }
    }
}

impl std::error::Error for ACGSError {}

pub type Result<T> = std::result::Result<T, ACGSError>;

#[cfg(test)]
mod tests {
    use super::*;
    use wasm_bindgen_test::*;

    wasm_bindgen_test_configure!(run_in_browser);

    #[wasm_bindgen_test]
    fn test_constitutional_hash() {
        assert_eq!(CONSTITUTIONAL_HASH, "cdd01ef066bc6cf2");
        assert_eq!(CONSTITUTIONAL_HASH.len(), 16);
    }

    #[wasm_bindgen_test]
    fn test_performance_targets() {
        assert_eq!(PERFORMANCE_TARGETS.p99_latency_ms, 5);
        assert_eq!(PERFORMANCE_TARGETS.throughput_rps, 100);
        assert_eq!(PERFORMANCE_TARGETS.cache_hit_rate, 0.85);
    }

    #[wasm_bindgen_test]
    fn test_error_display() {
        let constitutional_error = ACGSError::ConstitutionalViolation("test".to_string());
        assert!(format!("{}", constitutional_error).contains("Constitutional compliance violation"));

        let performance_error = ACGSError::PerformanceViolation {
            metric: "latency".to_string(),
            value: 10.0,
            target: 5.0,
        };
        assert!(format!("{}", performance_error).contains("Performance target violation"));
    }

    #[test]
    fn test_constitutional_hash_format() {
        // Test that the hash is in the expected format (16 hex characters)
        assert!(CONSTITUTIONAL_HASH.chars().all(|c| c.is_ascii_hexdigit()));
        assert_eq!(CONSTITUTIONAL_HASH.len(), 16);
    }

    #[test]
    fn test_performance_targets_validity() {
        // Test that performance targets are reasonable
        assert!(PERFORMANCE_TARGETS.p99_latency_ms > 0);
        assert!(PERFORMANCE_TARGETS.p99_latency_ms < 1000); // Less than 1 second
        assert!(PERFORMANCE_TARGETS.throughput_rps > 0);
        assert!(PERFORMANCE_TARGETS.throughput_rps < 10000); // Reasonable upper bound
        assert!(PERFORMANCE_TARGETS.cache_hit_rate > 0.0);
        assert!(PERFORMANCE_TARGETS.cache_hit_rate <= 1.0);
    }
}
