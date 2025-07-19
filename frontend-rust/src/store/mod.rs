/*!
 * ACGS-2 State Management
 * Constitutional Hash: cdd01ef066bc6cf2
 */

use std::collections::HashMap;
use serde::{Deserialize, Serialize};
use yewdux::prelude::*;

use crate::constitutional::ConstitutionalCompliance;
use crate::services::ServiceManager;

// Main application store
#[derive(Debug, Clone, PartialEq, Store, Serialize, Deserialize)]
pub struct AppStore {
    pub initialized: bool,
    pub loading: bool,
    pub error: Option<String>,
    pub services: Option<ServiceManager>,
    pub constitutional_violations: u32,
    pub performance_metrics: HashMap<String, f64>,
    pub user: Option<User>,
    pub theme: Theme,
    pub layout_config: LayoutConfig,
}

impl Default for AppStore {
    fn default() -> Self {
        Self {
            initialized: false,
            loading: false,
            error: None,
            services: None,
            constitutional_violations: 0,
            performance_metrics: HashMap::new(),
            user: None,
            theme: Theme::System,
            layout_config: LayoutConfig::default(),
        }
    }
}

// Constitutional compliance store
#[derive(Debug, Clone, PartialEq, Store, Serialize, Deserialize)]
pub struct ConstitutionalStore {
    pub compliance: ConstitutionalCompliance,
    pub validation_history: Vec<ConstitutionalValidation>,
    pub auto_validation_enabled: bool,
    pub last_validation: Option<String>,
}

impl Default for ConstitutionalStore {
    fn default() -> Self {
        Self {
            compliance: ConstitutionalCompliance::default(),
            validation_history: Vec::new(),
            auto_validation_enabled: true,
            last_validation: None,
        }
    }
}

// User information
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct User {
    pub id: String,
    pub username: String,
    pub email: String,
    pub roles: Vec<String>,
    pub permissions: Vec<String>,
    pub preferences: UserPreferences,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct UserPreferences {
    pub theme: Theme,
    pub language: String,
    pub notifications_enabled: bool,
    pub auto_save: bool,
    pub performance_monitoring: bool,
}

impl Default for UserPreferences {
    fn default() -> Self {
        Self {
            theme: Theme::System,
            language: "en".to_string(),
            notifications_enabled: true,
            auto_save: true,
            performance_monitoring: true,
        }
    }
}

// Theme configuration
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum Theme {
    Light,
    Dark,
    System,
    Constitutional, // Special ACGS theme
}

// Layout configuration
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct LayoutConfig {
    pub sidebar_collapsed: bool,
    pub sidebar_width: u32,
    pub header_height: u32,
    pub density: Density,
    pub navigation_style: NavigationStyle,
}

impl Default for LayoutConfig {
    fn default() -> Self {
        Self {
            sidebar_collapsed: false,
            sidebar_width: 256,
            header_height: 64,
            density: Density::Comfortable,
            navigation_style: NavigationStyle::Sidebar,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum Density {
    Compact,
    Comfortable,
    Spacious,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum NavigationStyle {
    Sidebar,
    Topbar,
    Minimal,
}

// Constitutional validation record
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ConstitutionalValidation {
    pub timestamp: String,
    pub action: String,
    pub result: bool,
    pub score: f64,
    pub violations: Vec<String>,
    pub context: serde_json::Value,
}

// Dashboard store for dashboard-specific state
#[derive(Debug, Clone, PartialEq, Store, Serialize, Deserialize)]
pub struct DashboardStore {
    pub active_tab: String,
    pub widgets: Vec<DashboardWidget>,
    pub layout: DashboardLayout,
    pub auto_refresh: bool,
    pub refresh_interval: u32, // seconds
}

impl Default for DashboardStore {
    fn default() -> Self {
        Self {
            active_tab: "overview".to_string(),
            widgets: vec![
                DashboardWidget {
                    id: "constitutional-status".to_string(),
                    title: "Constitutional Status".to_string(),
                    widget_type: WidgetType::ConstitutionalStatus,
                    position: WidgetPosition { x: 0, y: 0, width: 6, height: 4 },
                    visible: true,
                },
                DashboardWidget {
                    id: "service-health".to_string(),
                    title: "Service Health".to_string(),
                    widget_type: WidgetType::ServiceHealth,
                    position: WidgetPosition { x: 6, y: 0, width: 6, height: 4 },
                    visible: true,
                },
                DashboardWidget {
                    id: "performance-metrics".to_string(),
                    title: "Performance Metrics".to_string(),
                    widget_type: WidgetType::PerformanceMetrics,
                    position: WidgetPosition { x: 0, y: 4, width: 12, height: 6 },
                    visible: true,
                },
            ],
            layout: DashboardLayout::Grid,
            auto_refresh: true,
            refresh_interval: 30,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DashboardWidget {
    pub id: String,
    pub title: String,
    pub widget_type: WidgetType,
    pub position: WidgetPosition,
    pub visible: bool,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum WidgetType {
    ConstitutionalStatus,
    ServiceHealth,
    PerformanceMetrics,
    GovernanceInsights,
    PolicyCompliance,
    AuditLog,
    UserActivity,
    SystemAlerts,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct WidgetPosition {
    pub x: u32,
    pub y: u32,
    pub width: u32,
    pub height: u32,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum DashboardLayout {
    Grid,
    Masonry,
    List,
}

// Notification store
#[derive(Debug, Clone, PartialEq, Store, Serialize, Deserialize)]
pub struct NotificationStore {
    pub notifications: Vec<Notification>,
    pub max_notifications: usize,
    pub auto_dismiss_timeout: u32, // milliseconds
}

impl Default for NotificationStore {
    fn default() -> Self {
        Self {
            notifications: Vec::new(),
            max_notifications: 10,
            auto_dismiss_timeout: 5000,
        }
    }
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct Notification {
    pub id: String,
    pub title: String,
    pub message: String,
    pub notification_type: NotificationType,
    pub timestamp: String,
    pub read: bool,
    pub actions: Vec<NotificationAction>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum NotificationType {
    Info,
    Success,
    Warning,
    Error,
    Constitutional,
    Security,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct NotificationAction {
    pub label: String,
    pub action_type: ActionType,
    pub target: Option<String>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum ActionType {
    Dismiss,
    Navigate,
    Execute,
    Acknowledge,
}

// Store actions/reducers
impl AppStore {
    pub fn set_loading(&mut self, loading: bool) {
        self.loading = loading;
    }

    pub fn set_error(&mut self, error: Option<String>) {
        self.error = error;
    }

    pub fn set_user(&mut self, user: Option<User>) {
        self.user = user;
    }

    pub fn update_performance_metric(&mut self, name: String, value: f64) {
        self.performance_metrics.insert(name, value);
    }

    pub fn increment_constitutional_violations(&mut self) {
        self.constitutional_violations += 1;
    }
}

impl ConstitutionalStore {
    pub fn update_compliance(&mut self, compliance: ConstitutionalCompliance) {
        // Add to history
        let validation = ConstitutionalValidation {
            timestamp: chrono::Utc::now().to_rfc3339(),
            action: "compliance_update".to_string(),
            result: compliance.compliant,
            score: compliance.score,
            violations: compliance.violations.clone(),
            context: serde_json::Value::Object(serde_json::Map::new()),
        };
        
        self.validation_history.push(validation);
        
        // Keep only last 100 validations
        if self.validation_history.len() > 100 {
            self.validation_history.remove(0);
        }
        
        self.compliance = compliance;
        self.last_validation = Some(chrono::Utc::now().to_rfc3339());
    }
}

impl NotificationStore {
    pub fn add_notification(&mut self, notification: Notification) {
        self.notifications.push(notification);
        
        // Remove oldest if exceeding max
        if self.notifications.len() > self.max_notifications {
            self.notifications.remove(0);
        }
    }

    pub fn remove_notification(&mut self, id: &str) {
        self.notifications.retain(|n| n.id != id);
    }

    pub fn mark_read(&mut self, id: &str) {
        if let Some(notification) = self.notifications.iter_mut().find(|n| n.id == id) {
            notification.read = true;
        }
    }
}
