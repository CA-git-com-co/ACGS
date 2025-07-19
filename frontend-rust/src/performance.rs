/*!
 * ACGS-2 Performance Optimization Module
 * Constitutional Hash: cdd01ef066bc6cf2
 * 
 * Implements performance monitoring, code splitting, and optimization
 * to meet P99 <5ms latency targets.
 */

// Removed unused import: Performance
use yew::prelude::*;
use std::collections::HashMap;
use std::sync::{Mutex, LazyLock};

/// Performance metrics collector
pub struct PerformanceMetrics {
    measurements: HashMap<String, Vec<f64>>,
}

impl PerformanceMetrics {
    pub fn new() -> Self {
        Self {
            measurements: HashMap::new(),
        }
    }

    pub fn record(&mut self, operation: &str, duration: f64) {
        self.measurements
            .entry(operation.to_string())
            .or_insert_with(Vec::new)
            .push(duration);
    }

    pub fn get_p99(&self, operation: &str) -> Option<f64> {
        if let Some(measurements) = self.measurements.get(operation) {
            if measurements.is_empty() {
                return None;
            }
            
            let mut sorted = measurements.clone();
            sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());
            
            let index = ((sorted.len() as f64) * 0.99).ceil() as usize - 1;
            Some(sorted[index.min(sorted.len() - 1)])
        } else {
            None
        }
    }

    pub fn get_average(&self, operation: &str) -> Option<f64> {
        if let Some(measurements) = self.measurements.get(operation) {
            if measurements.is_empty() {
                return None;
            }
            Some(measurements.iter().sum::<f64>() / measurements.len() as f64)
        } else {
            None
        }
    }
}

/// Global performance metrics instance
static METRICS: LazyLock<Mutex<PerformanceMetrics>> = LazyLock::new(|| {
    Mutex::new(PerformanceMetrics::new())
});

/// Performance timer for measuring operations
pub struct PerformanceTimer {
    operation: String,
    start_time: f64,
}

impl PerformanceTimer {
    pub fn new(operation: &str) -> Self {
        let start_time = if let Some(window) = web_sys::window() {
            if let Some(performance) = window.performance() {
                performance.mark(&format!("{}-start", operation)).ok();
                performance.now()
            } else {
                0.0
            }
        } else {
            0.0
        };

        Self {
            operation: operation.to_string(),
            start_time,
        }
    }
}

impl Drop for PerformanceTimer {
    fn drop(&mut self) {
        if let Some(window) = web_sys::window() {
            if let Some(performance) = window.performance() {
                let end_time = performance.now();
                let duration = end_time - self.start_time;
                
                performance.mark(&format!("{}-end", &self.operation)).ok();
                performance.measure_with_start_mark_and_end_mark(
                    &self.operation,
                    &format!("{}-start", &self.operation),
                    &format!("{}-end", &self.operation)
                ).ok();

                // Record in global metrics
                if let Ok(mut metrics) = METRICS.lock() {
                    metrics.record(&self.operation, duration);
                }

                // Validate against P99 target (5ms)
                if duration > 5.0 {
                    log::warn!("Performance target exceeded for {}: {}ms > 5ms", 
                        &self.operation, duration);
                } else {
                    log::debug!("Performance OK for {}: {}ms", &self.operation, duration);
                }
            }
        }
    }
}

/// Macro for easy performance measurement
#[macro_export]
macro_rules! measure_performance {
    ($operation:expr, $code:block) => {{
        let _timer = $crate::performance::PerformanceTimer::new($operation);
        $code
    }};
}

/// Lazy loading component wrapper
#[derive(Properties, PartialEq)]
pub struct LazyProps {
    pub children: Children,
    pub loading_component: Option<Html>,
}

#[function_component(Lazy)]
pub fn lazy(props: &LazyProps) -> Html {
    let loaded = use_state(|| false);
    
    use_effect_with((), {
        let loaded = loaded.clone();
        move |_| {
            // Simulate async loading with a small delay
            wasm_bindgen_futures::spawn_local(async move {
                // Use requestIdleCallback if available for better performance
                if let Some(_window) = web_sys::window() {
                    // Small delay to allow for lazy loading
                    gloo_timers::future::TimeoutFuture::new(1).await;
                }
                loaded.set(true);
            });
        }
    });

    if *loaded {
        html! { <>{ for props.children.iter() }</> }
    } else {
        props.loading_component.clone().unwrap_or_else(|| {
            html! {
                <div class="loading-spinner">
                    <div class="spinner"></div>
                    <span>{"Loading..."}</span>
                </div>
            }
        })
    }
}

/// Cache implementation for API responses
pub struct ResponseCache {
    cache: HashMap<String, (String, f64)>, // (response, timestamp)
    ttl: f64, // Time to live in milliseconds
}

impl ResponseCache {
    pub fn new(ttl_seconds: f64) -> Self {
        Self {
            cache: HashMap::new(),
            ttl: ttl_seconds * 1000.0, // Convert to milliseconds
        }
    }

    pub fn get(&mut self, key: &str) -> Option<String> {
        if let Some((response, timestamp)) = self.cache.get(key) {
            let now = if let Some(window) = web_sys::window() {
                if let Some(performance) = window.performance() {
                    performance.now()
                } else {
                    0.0
                }
            } else {
                0.0
            };

            if now - timestamp < self.ttl {
                Some(response.clone())
            } else {
                self.cache.remove(key);
                None
            }
        } else {
            None
        }
    }

    pub fn set(&mut self, key: String, response: String) {
        let timestamp = if let Some(window) = web_sys::window() {
            if let Some(performance) = window.performance() {
                performance.now()
            } else {
                0.0
            }
        } else {
            0.0
        };

        self.cache.insert(key, (response, timestamp));
    }

    pub fn clear_expired(&mut self) {
        let now = if let Some(window) = web_sys::window() {
            if let Some(performance) = window.performance() {
                performance.now()
            } else {
                0.0
            }
        } else {
            0.0
        };

        self.cache.retain(|_, (_, timestamp)| now - *timestamp < self.ttl);
    }
}

/// Get performance report
pub fn get_performance_report() -> String {
    if let Ok(metrics) = METRICS.lock() {
        let mut report = String::from("ACGS-2 Performance Report\n");
        report.push_str("Constitutional Hash: cdd01ef066bc6cf2\n\n");
        
        for (operation, _) in &metrics.measurements {
            if let Some(p99) = metrics.get_p99(operation) {
                if let Some(avg) = metrics.get_average(operation) {
                    let status = if p99 <= 5.0 { "✅ PASS" } else { "❌ FAIL" };
                    report.push_str(&format!(
                        "{}: P99={:.2}ms, Avg={:.2}ms {}\n",
                        operation, p99, avg, status
                    ));
                }
            }
        }
        
        report
    } else {
        "Failed to access performance metrics".to_string()
    }
}
