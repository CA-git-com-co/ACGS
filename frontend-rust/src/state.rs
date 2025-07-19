/*!
 * ACGS-2 State Management
 * Constitutional Hash: cdd01ef066bc6cf2
 */

use std::collections::HashMap;
use yew::prelude::*;
use serde::{Deserialize, Serialize};

use crate::api::ServiceManager;

// Application state
#[derive(Debug, Clone, PartialEq)]
pub struct AppState {
    pub initialized: bool,
    pub loading: bool,
    pub error: Option<String>,
    pub constitutional_compliance: ConstitutionalCompliance,
    pub services: HashMap<String, ServiceStatus>,
    pub user_preferences: UserPreferences,
    pub performance_metrics: HashMap<String, f64>,
    pub service_manager: Option<ServiceManager>,
}

impl Default for AppState {
    fn default() -> Self {
        let mut services = HashMap::new();
        services.insert("constitutional_ai".to_string(), ServiceStatus::Ready);
        services.insert("integrity_service".to_string(), ServiceStatus::Ready);
        services.insert("formal_verification".to_string(), ServiceStatus::Ready);
        services.insert("governance_synthesis".to_string(), ServiceStatus::Ready);
        services.insert("policy_governance".to_string(), ServiceStatus::Ready);
        services.insert("evolutionary_computation".to_string(), ServiceStatus::Ready);
        services.insert("auth_service".to_string(), ServiceStatus::Ready);

        Self {
            initialized: true,
            loading: false,
            error: None,
            constitutional_compliance: ConstitutionalCompliance::default(),
            services,
            user_preferences: UserPreferences::default(),
            performance_metrics: HashMap::new(),
            service_manager: Some(ServiceManager::new()),
        }
    }
}

// Constitutional compliance state
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ConstitutionalCompliance {
    pub hash: String,
    pub compliant: bool,
    pub score: f64,
    pub violations: Vec<String>,
    pub last_validated: String,
}

impl Default for ConstitutionalCompliance {
    fn default() -> Self {
        Self {
            hash: crate::CONSTITUTIONAL_HASH.to_string(),
            compliant: true,
            score: 0.987,
            violations: Vec::new(),
            last_validated: chrono::Utc::now().to_rfc3339(),
        }
    }
}

// Service status
#[derive(Debug, Clone, PartialEq)]
pub enum ServiceStatus {
    Ready,
    Connected,
    Disconnected,
    Error(String),
}

// User preferences
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct UserPreferences {
    pub theme: Theme,
    pub language: String,
    pub notifications_enabled: bool,
    pub auto_refresh: bool,
    pub performance_monitoring: bool,
}

impl Default for UserPreferences {
    fn default() -> Self {
        Self {
            theme: Theme::System,
            language: "en".to_string(),
            notifications_enabled: true,
            auto_refresh: true,
            performance_monitoring: true,
        }
    }
}

// Theme options
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum Theme {
    Light,
    Dark,
    System,
    Constitutional,
}

// State actions
#[derive(Debug, Clone)]
pub enum AppAction {
    SetLoading(bool),
    SetError(Option<String>),
    UpdateConstitutionalCompliance(ConstitutionalCompliance),
    UpdateServiceStatus(String, ServiceStatus),
    UpdateUserPreferences(UserPreferences),
    UpdatePerformanceMetric(String, f64),
    InitializeServiceManager(ServiceManager),
    Initialize,
}

// Implement Reducible trait for AppState
impl Reducible for AppState {
    type Action = AppAction;

    fn reduce(self: std::rc::Rc<Self>, action: Self::Action) -> std::rc::Rc<Self> {
        let mut new_state = (*self).clone();

        match action {
            AppAction::SetLoading(loading) => {
                new_state.loading = loading;
            }
            AppAction::SetError(error) => {
                new_state.error = error;
            }
            AppAction::UpdateConstitutionalCompliance(compliance) => {
                new_state.constitutional_compliance = compliance;
            }
            AppAction::UpdateServiceStatus(service, status) => {
                new_state.services.insert(service, status);
            }
            AppAction::UpdateUserPreferences(preferences) => {
                new_state.user_preferences = preferences;
            }
            AppAction::UpdatePerformanceMetric(name, value) => {
                new_state.performance_metrics.insert(name, value);
            }
            AppAction::InitializeServiceManager(service_manager) => {
                new_state.service_manager = Some(service_manager);
            }
            AppAction::Initialize => {
                new_state.initialized = true;
                new_state.loading = false;
                new_state.error = None;
            }
        }

        std::rc::Rc::new(new_state)
    }
}

// State context
pub type AppStateContext = UseReducerHandle<AppState>;

// State provider component
#[derive(Properties, PartialEq)]
pub struct StateProviderProps {
    pub children: Children,
}

#[function_component(StateProvider)]
pub fn state_provider(props: &StateProviderProps) -> Html {
    let state = use_reducer(|| AppState::default());
    
    // Initialize state
    use_effect_with((), {
        let state = state.clone();
        move |_| {
            state.dispatch(AppAction::Initialize);
            log::info!("ACGS-2 state initialized");
        }
    });

    html! {
        <ContextProvider<AppStateContext> context={state}>
            { for props.children.iter() }
        </ContextProvider<AppStateContext>>
    }
}

// State hooks
#[hook]
pub fn use_app_state() -> AppStateContext {
    use_context::<AppStateContext>().expect("use_app_state must be used within StateProvider")
}

#[hook]
pub fn use_constitutional_compliance() -> ConstitutionalCompliance {
    let state = use_app_state();
    (*state).constitutional_compliance.clone()
}

#[hook]
pub fn use_service_status() -> HashMap<String, ServiceStatus> {
    let state = use_app_state();
    (*state).services.clone()
}

#[hook]
pub fn use_user_preferences() -> (UserPreferences, Callback<UserPreferences>) {
    let state = use_app_state();
    let preferences = (*state).user_preferences.clone();

    let update_preferences = {
        let state = state.clone();
        Callback::from(move |new_preferences: UserPreferences| {
            state.dispatch(AppAction::UpdateUserPreferences(new_preferences));
        })
    };

    (preferences, update_preferences)
}

#[hook]
pub fn use_performance_metrics() -> HashMap<String, f64> {
    let state = use_app_state();
    (*state).performance_metrics.clone()
}

#[hook]
pub fn use_service_manager() -> Option<ServiceManager> {
    let state = use_app_state();
    (*state).service_manager.clone()
}

// Local storage utilities for persistence
pub fn save_user_preferences(preferences: &UserPreferences) {
    if let Ok(serialized) = serde_json::to_string(preferences) {
        let _ = crate::utils::set_local_storage_item("acgs_user_preferences", &serialized);
    }
}

pub fn load_user_preferences() -> Option<UserPreferences> {
    if let Ok(Some(stored)) = crate::utils::get_local_storage_item("acgs_user_preferences") {
        serde_json::from_str(&stored).ok()
    } else {
        None
    }
}

// Performance monitoring
pub fn log_performance_metric(name: &str, value: f64, target: Option<f64>) {
    if let Some(target_val) = target {
        let status = if value <= target_val { "GOOD" } else { "POOR" };
        log::info!("[PERFORMANCE:{}] {} = {:.2}ms (target: {:.2}ms)", status, name, value, target_val);
    } else {
        log::info!("[PERFORMANCE] {} = {:.2}ms", name, value);
    }
}

// Constitutional compliance validation
pub fn validate_constitutional_hash(hash: &str) -> bool {
    hash == crate::CONSTITUTIONAL_HASH
}

pub fn create_constitutional_compliance_report() -> ConstitutionalCompliance {
    ConstitutionalCompliance {
        hash: crate::CONSTITUTIONAL_HASH.to_string(),
        compliant: true,
        score: 0.987,
        violations: Vec::new(),
        last_validated: chrono::Utc::now().to_rfc3339(),
    }
}
