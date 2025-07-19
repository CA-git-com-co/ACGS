/*!
 * ACGS-2 Custom Hooks
 * Constitutional Hash: cdd01ef066bc6cf2
 */

use std::collections::HashMap;
use yew::prelude::*;
use yewdux::prelude::*;

use crate::types::{ConstitutionalCompliance, ServiceInfo, PerformanceMetrics};
use crate::store::{AppStore, ConstitutionalStore};

// Constitutional compliance hook
#[hook]
pub fn use_constitutional_compliance() -> ConstitutionalCompliance {
    let (constitutional_store, _) = use_store::<ConstitutionalStore>();
    constitutional_store.compliance.clone()
}

// Service health hook
#[hook]
pub fn use_service_health() -> HashMap<String, bool> {
    let (app_store, _) = use_store::<AppStore>();
    
    // Mock service health data for now
    let mut health = HashMap::new();
    health.insert("constitutional_ai".to_string(), true);
    health.insert("integrity_service".to_string(), true);
    health.insert("formal_verification".to_string(), true);
    health.insert("governance_synthesis".to_string(), true);
    health.insert("policy_governance".to_string(), true);
    health.insert("evolutionary_computation".to_string(), true);
    health.insert("auth_service".to_string(), true);
    
    health
}

// Performance metrics hook
#[hook]
pub fn use_performance_metrics() -> PerformanceMetrics {
    let (app_store, _) = use_store::<AppStore>();
    
    // Mock performance data for now
    PerformanceMetrics {
        latency_p99: 2.3,
        throughput_rps: 156.0,
        cache_hit_rate: 0.92,
        error_rate: 0.001,
        timestamp: chrono::Utc::now().to_rfc3339(),
    }
}

// Local storage hook
#[hook]
pub fn use_local_storage<T>(key: &str, default_value: T) -> (T, Callback<T>)
where
    T: Clone + serde::Serialize + for<'de> serde::Deserialize<'de> + 'static,
{
    let key = key.to_string();
    
    // Initialize state from localStorage or default
    let initial_value = {
        match crate::utils::get_local_storage_item(&key) {
            Ok(Some(stored_value)) => {
                match serde_json::from_str::<T>(&stored_value) {
                    Ok(parsed) => parsed,
                    Err(_) => default_value.clone(),
                }
            }
            _ => default_value.clone(),
        }
    };
    
    let state = use_state(|| initial_value);
    
    let setter = {
        let state = state.clone();
        let key = key.clone();
        Callback::from(move |new_value: T| {
            // Update state
            state.set(new_value.clone());
            
            // Update localStorage
            if let Ok(serialized) = serde_json::to_string(&new_value) {
                let _ = crate::utils::set_local_storage_item(&key, &serialized);
            }
        })
    };
    
    ((*state).clone(), setter)
}

// Debounced value hook
#[hook]
pub fn use_debounced_value<T>(value: T, delay_ms: u32) -> T
where
    T: Clone + PartialEq + 'static,
{
    let debounced_value = use_state(|| value.clone());
    
    use_effect_with((value.clone(), delay_ms), {
        let debounced_value = debounced_value.clone();
        move |(new_value, delay)| {
            let timeout = gloo::timers::callback::Timeout::new(*delay, {
                let debounced_value = debounced_value.clone();
                let new_value = new_value.clone();
                move || {
                    debounced_value.set(new_value);
                }
            });
            
            // Return cleanup function
            move || drop(timeout)
        }
    });
    
    (*debounced_value).clone()
}

// Async data fetching hook
#[hook]
pub fn use_async_data<T, F, Fut>(fetch_fn: F) -> (Option<T>, bool, Option<String>)
where
    T: Clone + 'static,
    F: Fn() -> Fut + 'static,
    Fut: std::future::Future<Output = Result<T, String>> + 'static,
{
    let data = use_state(|| None);
    let loading = use_state(|| false);
    let error = use_state(|| None);
    
    use_effect_with((), {
        let data = data.clone();
        let loading = loading.clone();
        let error = error.clone();
        
        move |_| {
            loading.set(true);
            error.set(None);
            
            wasm_bindgen_futures::spawn_local(async move {
                match fetch_fn().await {
                    Ok(result) => {
                        data.set(Some(result));
                        error.set(None);
                    }
                    Err(err) => {
                        error.set(Some(err));
                        data.set(None);
                    }
                }
                loading.set(false);
            });
        }
    });
    
    ((*data).clone(), *loading, (*error).clone())
}

// Interval hook
#[hook]
pub fn use_interval<F>(callback: F, delay_ms: Option<u32>)
where
    F: Fn() + 'static,
{
    use_effect_with(delay_ms, move |delay| {
        if let Some(delay_ms) = delay {
            let interval = gloo::timers::callback::Interval::new(*delay_ms, callback);
            
            // Return cleanup function
            move || drop(interval)
        } else {
            // No cleanup needed if no delay
            move || {}
        }
    });
}

// Window size hook
#[hook]
pub fn use_window_size() -> (u32, u32) {
    let size = use_state(|| {
        if let Some(window) = web_sys::window() {
            (
                window.inner_width().unwrap().as_f64().unwrap() as u32,
                window.inner_height().unwrap().as_f64().unwrap() as u32,
            )
        } else {
            (1920, 1080) // Default size
        }
    });
    
    use_effect_with((), {
        let size = size.clone();
        move |_| {
            let resize_callback = {
                let size = size.clone();
                Closure::wrap(Box::new(move || {
                    if let Some(window) = web_sys::window() {
                        let new_size = (
                            window.inner_width().unwrap().as_f64().unwrap() as u32,
                            window.inner_height().unwrap().as_f64().unwrap() as u32,
                        );
                        size.set(new_size);
                    }
                }) as Box<dyn Fn()>)
            };
            
            if let Some(window) = web_sys::window() {
                let _ = window.add_event_listener_with_callback(
                    "resize",
                    resize_callback.as_ref().unchecked_ref(),
                );
            }
            
            // Return cleanup function
            move || {
                if let Some(window) = web_sys::window() {
                    let _ = window.remove_event_listener_with_callback(
                        "resize",
                        resize_callback.as_ref().unchecked_ref(),
                    );
                }
                drop(resize_callback);
            }
        }
    });
    
    *size
}

// Theme hook
#[hook]
pub fn use_theme() -> (crate::types::Theme, Callback<crate::types::Theme>) {
    let (theme, set_theme) = use_local_storage("acgs_theme", crate::types::Theme::System);
    
    // Apply theme when it changes
    use_effect_with(theme.clone(), |theme| {
        crate::utils::apply_theme(theme);
    });
    
    (theme, set_theme)
}

// Constitutional validation hook
#[hook]
pub fn use_constitutional_validation() -> Callback<serde_json::Value, bool> {
    Callback::from(|data: serde_json::Value| {
        crate::utils::is_constitutionally_compliant(&data)
    })
}

// Performance monitoring hook
#[hook]
pub fn use_performance_monitor() -> Callback<(String, f64, Option<f64>)> {
    Callback::from(|(metric_name, value, target): (String, f64, Option<f64>)| {
        crate::utils::log_performance_metric(&metric_name, value, target);
        
        if let Some(target_val) = target {
            crate::utils::check_performance_target(&metric_name, value, target_val);
        }
    })
}

// Error boundary hook
#[hook]
pub fn use_error_boundary() -> (Option<String>, Callback<String>, Callback<()>) {
    let error = use_state(|| None);
    
    let set_error = {
        let error = error.clone();
        Callback::from(move |err: String| {
            crate::utils::log_error(&err, Some("ErrorBoundary"));
            error.set(Some(err));
        })
    };
    
    let clear_error = {
        let error = error.clone();
        Callback::from(move |_| {
            error.set(None);
        })
    };
    
    ((*error).clone(), set_error, clear_error)
}

use wasm_bindgen::closure::Closure;
