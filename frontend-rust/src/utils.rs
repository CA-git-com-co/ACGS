/*!
 * ACGS-2 Utility Functions
 * Constitutional Hash: cdd01ef066bc6cf2
 */

use sha2::{Sha256, Digest};
use wasm_bindgen::JsValue;
use web_sys::{window, Storage};

// Constitutional compliance utilities
pub fn validate_constitutional_hash(hash: &str) -> bool {
    hash == crate::CONSTITUTIONAL_HASH
}

pub fn generate_hash(data: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data.as_bytes());
    hex::encode(hasher.finalize())
}

pub fn is_constitutionally_compliant(data: &serde_json::Value) -> bool {
    if let Some(hash) = data.get("constitutional_hash") {
        if let Some(hash_str) = hash.as_str() {
            return validate_constitutional_hash(hash_str);
        }
    }
    false
}

// Performance utilities (simplified)
pub fn measure_performance<F, R>(operation: F) -> (R, f64)
where
    F: FnOnce() -> R,
{
    // Simplified version without timing
    let result = operation();
    (result, 1.0) // Mock 1ms duration
}

pub fn check_performance_target(metric_name: &str, value: f64, target: f64) -> bool {
    let within_target = value <= target;
    if !within_target {
        log::warn!(
            "Performance target violation: {} = {:.2}, target = {:.2}",
            metric_name, value, target
        );
    }
    within_target
}

// Local storage utilities
pub fn get_local_storage() -> Result<Storage, JsValue> {
    window()
        .ok_or_else(|| JsValue::from_str("No window object"))?
        .local_storage()?
        .ok_or_else(|| JsValue::from_str("No localStorage"))
}

pub fn set_local_storage_item(key: &str, value: &str) -> Result<(), JsValue> {
    get_local_storage()?.set_item(key, value)
}

pub fn get_local_storage_item(key: &str) -> Result<Option<String>, JsValue> {
    get_local_storage()?.get_item(key)
}

pub fn remove_local_storage_item(key: &str) -> Result<(), JsValue> {
    get_local_storage()?.remove_item(key)
}

// Session storage utilities
pub fn get_session_storage() -> Result<Storage, JsValue> {
    window()
        .ok_or_else(|| JsValue::from_str("No window object"))?
        .session_storage()?
        .ok_or_else(|| JsValue::from_str("No sessionStorage"))
}

pub fn set_session_storage_item(key: &str, value: &str) -> Result<(), JsValue> {
    get_session_storage()?.set_item(key, value)
}

pub fn get_session_storage_item(key: &str) -> Result<Option<String>, JsValue> {
    get_session_storage()?.get_item(key)
}

// URL utilities
pub fn get_current_url() -> Option<String> {
    window()?.location().href().ok()
}

pub fn navigate_to(url: &str) -> Result<(), JsValue> {
    window()
        .ok_or_else(|| JsValue::from_str("No window object"))?
        .location()
        .set_href(url)
}

pub fn reload_page() -> Result<(), JsValue> {
    window()
        .ok_or_else(|| JsValue::from_str("No window object"))?
        .location()
        .reload()
}

// Date/time utilities
pub fn format_timestamp(timestamp: &str) -> String {
    match chrono::DateTime::parse_from_rfc3339(timestamp) {
        Ok(dt) => dt.format("%Y-%m-%d %H:%M:%S UTC").to_string(),
        Err(_) => timestamp.to_string(),
    }
}

pub fn format_relative_time(timestamp: &str) -> String {
    match chrono::DateTime::parse_from_rfc3339(timestamp) {
        Ok(dt) => {
            let now = chrono::Utc::now();
            let duration = now.signed_duration_since(dt.with_timezone(&chrono::Utc));
            
            if duration.num_seconds() < 60 {
                "just now".to_string()
            } else if duration.num_minutes() < 60 {
                format!("{}m ago", duration.num_minutes())
            } else if duration.num_hours() < 24 {
                format!("{}h ago", duration.num_hours())
            } else {
                format!("{}d ago", duration.num_days())
            }
        }
        Err(_) => timestamp.to_string(),
    }
}

pub fn get_current_timestamp() -> String {
    chrono::Utc::now().to_rfc3339()
}

// String utilities
pub fn truncate_string(s: &str, max_length: usize) -> String {
    if s.len() <= max_length {
        s.to_string()
    } else {
        format!("{}...", &s[..max_length.saturating_sub(3)])
    }
}

pub fn capitalize_first_letter(s: &str) -> String {
    let mut chars = s.chars();
    match chars.next() {
        None => String::new(),
        Some(first) => first.to_uppercase().collect::<String>() + chars.as_str(),
    }
}

pub fn snake_case_to_title_case(s: &str) -> String {
    s.split('_')
        .map(capitalize_first_letter)
        .collect::<Vec<_>>()
        .join(" ")
}

// Validation utilities
pub fn is_valid_email(email: &str) -> bool {
    email.contains('@') && email.contains('.')
}

pub fn is_valid_url(url: &str) -> bool {
    url.starts_with("http://") || url.starts_with("https://")
}

pub fn is_valid_uuid(uuid: &str) -> bool {
    // Simplified UUID validation
    uuid.len() == 36 && uuid.chars().filter(|&c| c == '-').count() == 4
}

// Error handling utilities
pub fn log_error(error: &str, context: Option<&str>) {
    if let Some(ctx) = context {
        log::error!("[{}] {}", ctx, error);
    } else {
        log::error!("{}", error);
    }
}

pub fn log_warning(warning: &str, context: Option<&str>) {
    if let Some(ctx) = context {
        log::warn!("[{}] {}", ctx, warning);
    } else {
        log::warn!("{}", warning);
    }
}

pub fn log_info(info: &str, context: Option<&str>) {
    if let Some(ctx) = context {
        log::info!("[{}] {}", ctx, info);
    } else {
        log::info!("{}", info);
    }
}

// Constitutional compliance logging
pub fn log_constitutional_event(event: &str, compliant: bool) {
    let status = if compliant { "COMPLIANT" } else { "VIOLATION" };
    log::info!("[CONSTITUTIONAL:{}] {}", status, event);
}

// Performance logging
pub fn log_performance_metric(metric_name: &str, value: f64, target: Option<f64>) {
    if let Some(target_val) = target {
        let status = if value <= target_val { "GOOD" } else { "POOR" };
        log::info!("[PERFORMANCE:{}] {} = {:.2} (target: {:.2})", status, metric_name, value, target_val);
    } else {
        log::info!("[PERFORMANCE] {} = {:.2}", metric_name, value);
    }
}

// Debounce utility
pub struct Debouncer {
    timeout_id: Option<i32>,
}

impl Debouncer {
    pub fn new() -> Self {
        Self { timeout_id: None }
    }
    
    pub fn debounce<F>(&mut self, delay_ms: i32, callback: F)
    where
        F: FnOnce() + 'static,
    {
        // Clear existing timeout
        if let Some(id) = self.timeout_id {
            window().unwrap().clear_timeout_with_handle(id);
        }
        
        // Set new timeout
        let timeout_id = window()
            .unwrap()
            .set_timeout_with_callback_and_timeout_and_arguments_0(
                &wasm_bindgen::closure::Closure::once_into_js(callback).into(),
                delay_ms,
            )
            .unwrap();
            
        self.timeout_id = Some(timeout_id);
    }
}

impl Default for Debouncer {
    fn default() -> Self {
        Self::new()
    }
}

// Theme utilities
pub fn get_system_theme() -> crate::types::Theme {
    // Simplified version without media query
    crate::types::Theme::Light
}

pub fn apply_theme(theme: &crate::types::Theme) {
    if let Some(document) = window().and_then(|w| w.document()) {
        if let Some(html) = document.document_element() {
            let theme_attr = match theme {
                crate::types::Theme::Light => "light",
                crate::types::Theme::Dark => "dark",
                crate::types::Theme::Constitutional => "constitutional",
                crate::types::Theme::System => "light", // Default to light
            };

            let _ = html.set_attribute("data-theme", theme_attr);
        }
    }
}
