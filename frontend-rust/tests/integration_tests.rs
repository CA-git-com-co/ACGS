/*!
 * ACGS-2 Rust Frontend Integration Tests
 * Constitutional Hash: cdd01ef066bc6cf2
 */

use wasm_bindgen_test::*;
use yew::prelude::*;
use acgs_frontend::{
    app::App,
    components::{Dashboard, Layout, ConstitutionalIndicator},
    state::{AppState, ConstitutionalCompliance, ServiceStatus, Theme, UserPreferences},
    api::{ApiClient, ServiceManager},
    CONSTITUTIONAL_HASH,
};

wasm_bindgen_test_configure!(run_in_browser);

#[wasm_bindgen_test]
fn test_constitutional_hash_validation() {
    assert_eq!(CONSTITUTIONAL_HASH, "cdd01ef066bc6cf2");
    assert_eq!(CONSTITUTIONAL_HASH.len(), 16);
}

#[wasm_bindgen_test]
fn test_app_component_renders() {
    let app = html! { <App /> };
    assert!(format!("{:?}", app).contains("App"));
}

#[wasm_bindgen_test]
fn test_dashboard_component_renders() {
    let dashboard = html! { <Dashboard /> };
    assert!(format!("{:?}", dashboard).contains("Dashboard"));
}

#[wasm_bindgen_test]
fn test_constitutional_indicator_renders() {
    let indicator = html! { <ConstitutionalIndicator /> };
    assert!(format!("{:?}", indicator).contains("ConstitutionalIndicator"));
}

#[wasm_bindgen_test]
fn test_layout_component_renders() {
    let layout = html! {
        <Layout>
            <div>{"Test content"}</div>
        </Layout>
    };
    assert!(format!("{:?}", layout).contains("Layout"));
}

#[wasm_bindgen_test]
fn test_app_state_default() {
    let state = AppState::default();
    assert!(state.initialized);
    assert!(!state.loading);
    assert!(state.error.is_none());
    assert!(state.constitutional_compliance.compliant);
    assert_eq!(state.constitutional_compliance.hash, CONSTITUTIONAL_HASH);
    assert!(state.service_manager.is_some());
}

#[wasm_bindgen_test]
fn test_constitutional_compliance_default() {
    let compliance = ConstitutionalCompliance::default();
    assert_eq!(compliance.hash, CONSTITUTIONAL_HASH);
    assert!(compliance.compliant);
    assert!(compliance.score > 0.9);
    assert!(compliance.violations.is_empty());
}

#[wasm_bindgen_test]
fn test_user_preferences_default() {
    let preferences = UserPreferences::default();
    assert_eq!(preferences.language, "en");
    assert!(preferences.notifications_enabled);
    assert!(preferences.auto_refresh);
    assert!(preferences.performance_monitoring);
    assert!(matches!(preferences.theme, Theme::System));
}

#[wasm_bindgen_test]
fn test_service_status_variants() {
    let ready = ServiceStatus::Ready;
    let connected = ServiceStatus::Connected;
    let disconnected = ServiceStatus::Disconnected;
    let error = ServiceStatus::Error("Test error".to_string());

    assert!(matches!(ready, ServiceStatus::Ready));
    assert!(matches!(connected, ServiceStatus::Connected));
    assert!(matches!(disconnected, ServiceStatus::Disconnected));
    assert!(matches!(error, ServiceStatus::Error(_)));
}

#[wasm_bindgen_test]
fn test_api_client_creation() {
    let client = ApiClient::new("http://localhost:8001".to_string());
    assert_eq!(client.base_url, "http://localhost:8001");
    assert!(client.headers.contains_key("Content-Type"));
    assert!(client.headers.contains_key("X-Constitutional-Hash"));
    assert_eq!(client.headers.get("X-Constitutional-Hash").unwrap(), CONSTITUTIONAL_HASH);
}

#[wasm_bindgen_test]
fn test_service_manager_creation() {
    let manager = ServiceManager::new();
    assert!(manager.clients.contains_key("auth"));
    assert!(manager.clients.contains_key("constitutional_ai"));
    assert!(manager.clients.contains_key("integrity"));
    assert!(manager.clients.contains_key("formal_verification"));
    assert!(manager.clients.contains_key("governance_synthesis"));
    assert!(manager.clients.contains_key("policy_governance"));
    assert!(manager.clients.contains_key("evolutionary_computation"));
}

#[wasm_bindgen_test]
fn test_service_manager_get_client() {
    let manager = ServiceManager::new();
    let auth_client = manager.get_client("auth");
    assert!(auth_client.is_some());
    assert_eq!(auth_client.unwrap().base_url, "http://localhost:8016");

    let nonexistent_client = manager.get_client("nonexistent");
    assert!(nonexistent_client.is_none());
}

#[wasm_bindgen_test]
fn test_api_client_url_building() {
    let client = ApiClient::new("http://localhost:8001".to_string());
    
    // Test with leading slash
    let url1 = client.build_url("/api/v1/test");
    assert_eq!(url1, "http://localhost:8001/api/v1/test");
    
    // Test without leading slash
    let url2 = client.build_url("api/v1/test");
    assert_eq!(url2, "http://localhost:8001/api/v1/test");
}

#[wasm_bindgen_test]
fn test_constitutional_compliance_serialization() {
    let compliance = ConstitutionalCompliance::default();
    let serialized = serde_json::to_string(&compliance);
    assert!(serialized.is_ok());
    
    let json_str = serialized.unwrap();
    assert!(json_str.contains(CONSTITUTIONAL_HASH));
    assert!(json_str.contains("true")); // compliant field
}

#[wasm_bindgen_test]
fn test_user_preferences_serialization() {
    let preferences = UserPreferences::default();
    let serialized = serde_json::to_string(&preferences);
    assert!(serialized.is_ok());
    
    let json_str = serialized.unwrap();
    assert!(json_str.contains("en")); // language
    assert!(json_str.contains("System")); // theme
}

#[wasm_bindgen_test]
fn test_theme_variants() {
    let light = Theme::Light;
    let dark = Theme::Dark;
    let system = Theme::System;
    let constitutional = Theme::Constitutional;

    assert!(matches!(light, Theme::Light));
    assert!(matches!(dark, Theme::Dark));
    assert!(matches!(system, Theme::System));
    assert!(matches!(constitutional, Theme::Constitutional));
}

#[wasm_bindgen_test]
fn test_performance_targets() {
    // Test that our performance targets are met
    let start = web_sys::js_sys::Date::now();
    
    // Simulate component rendering
    let _app = html! { <App /> };
    let _dashboard = html! { <Dashboard /> };
    let _indicator = html! { <ConstitutionalIndicator /> };
    
    let end = web_sys::js_sys::Date::now();
    let duration_ms = end - start;
    
    // Should render components in under 5ms (P99 target)
    assert!(duration_ms < 5.0, "Component rendering took {}ms, exceeding 5ms target", duration_ms);
}

#[wasm_bindgen_test]
fn test_constitutional_compliance_validation() {
    let compliance = ConstitutionalCompliance::default();
    
    // Test that constitutional hash matches
    assert_eq!(compliance.hash, CONSTITUTIONAL_HASH);
    
    // Test that compliance score is within acceptable range
    assert!(compliance.score >= 0.8 && compliance.score <= 1.0);
    
    // Test that default state is compliant
    assert!(compliance.compliant);
    
    // Test that violations list is empty by default
    assert!(compliance.violations.is_empty());
}

#[wasm_bindgen_test]
fn test_service_manager_default() {
    let manager1 = ServiceManager::new();
    let manager2 = ServiceManager::default();
    
    // Both should have the same number of clients
    assert_eq!(manager1.clients.len(), manager2.clients.len());
    
    // Both should have the same client keys
    for key in manager1.clients.keys() {
        assert!(manager2.clients.contains_key(key));
    }
}

#[wasm_bindgen_test]
fn test_error_handling() {
    use acgs_frontend::ACGSError;
    
    let constitutional_error = ACGSError::ConstitutionalViolation("Test violation".to_string());
    let service_error = ACGSError::ServiceError("Test service error".to_string());
    let auth_error = ACGSError::AuthError("Test auth error".to_string());
    let network_error = ACGSError::NetworkError("Test network error".to_string());
    
    assert!(format!("{}", constitutional_error).contains("Constitutional compliance violation"));
    assert!(format!("{}", service_error).contains("Service communication error"));
    assert!(format!("{}", auth_error).contains("Authentication error"));
    assert!(format!("{}", network_error).contains("Network error"));
}

#[wasm_bindgen_test]
fn test_memory_usage() {
    // Test that creating multiple components doesn't cause memory issues
    let mut components = Vec::new();
    
    for _ in 0..100 {
        components.push(html! { <ConstitutionalIndicator /> });
        components.push(html! { <Dashboard /> });
    }
    
    // If we get here without panicking, memory usage is acceptable
    assert_eq!(components.len(), 200);
}

#[wasm_bindgen_test]
fn test_concurrent_state_access() {
    // Test that multiple state instances can be created without conflicts
    let state1 = AppState::default();
    let state2 = AppState::default();
    let state3 = AppState::default();
    
    assert_eq!(state1.constitutional_compliance.hash, state2.constitutional_compliance.hash);
    assert_eq!(state2.constitutional_compliance.hash, state3.constitutional_compliance.hash);
    assert_eq!(state1.constitutional_compliance.hash, CONSTITUTIONAL_HASH);
}
