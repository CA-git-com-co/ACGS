/*!
 * ACGS-2 Type Definitions
 * Constitutional Hash: cdd01ef066bc6cf2
 */

use serde::{Deserialize, Serialize};
use std::collections::HashMap;

// Service types
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ServiceInfo {
    pub name: String,
    pub url: String,
    pub port: u16,
    pub healthy: bool,
    pub version: String,
    pub constitutional_hash: String,
}

// API Response wrapper
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ApiResponse<T> {
    pub data: T,
    pub success: bool,
    pub message: Option<String>,
    pub constitutional_hash: String,
    pub timestamp: String,
}

// Performance metrics
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PerformanceMetrics {
    pub latency_p99: f64,
    pub throughput_rps: f64,
    pub cache_hit_rate: f64,
    pub error_rate: f64,
    pub timestamp: String,
}

// Constitutional compliance types
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

// User types
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct User {
    pub id: String,
    pub username: String,
    pub email: String,
    pub roles: Vec<String>,
    pub permissions: Vec<String>,
    pub created_at: String,
    pub last_login: Option<String>,
}

// Authentication types
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct AuthToken {
    pub token: String,
    pub expires_at: String,
    pub user_id: String,
    pub permissions: Vec<String>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct LoginRequest {
    pub username: String,
    pub password: String,
    pub remember_me: bool,
}

// Dashboard types
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct DashboardWidget {
    pub id: String,
    pub title: String,
    pub widget_type: WidgetType,
    pub position: WidgetPosition,
    pub config: serde_json::Value,
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

// Notification types
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

// WebSocket message types
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct WebSocketMessage {
    pub message_type: String,
    pub data: serde_json::Value,
    pub timestamp: String,
    pub constitutional_hash: String,
}

// Error types
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ErrorInfo {
    pub code: String,
    pub message: String,
    pub details: Option<serde_json::Value>,
    pub timestamp: String,
    pub constitutional_compliant: bool,
}

// Configuration types
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct AppConfig {
    pub api_base_url: String,
    pub websocket_url: String,
    pub constitutional_hash: String,
    pub performance_targets: PerformanceTargets,
    pub features: HashMap<String, bool>,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct PerformanceTargets {
    pub p99_latency_ms: u32,
    pub throughput_rps: u32,
    pub cache_hit_rate: f64,
}

impl Default for PerformanceTargets {
    fn default() -> Self {
        Self {
            p99_latency_ms: 5,
            throughput_rps: 100,
            cache_hit_rate: 0.85,
        }
    }
}

// Theme types
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum Theme {
    Light,
    Dark,
    System,
    Constitutional,
}

impl Default for Theme {
    fn default() -> Self {
        Self::System
    }
}

// Layout types
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct LayoutConfig {
    pub sidebar_collapsed: bool,
    pub sidebar_width: u32,
    pub header_height: u32,
    pub density: Density,
    pub navigation_style: NavigationStyle,
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

// Validation result types
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub struct ValidationResult {
    pub valid: bool,
    pub errors: Vec<String>,
    pub warnings: Vec<String>,
    pub constitutional_compliant: bool,
    pub score: f64,
}

impl Default for ValidationResult {
    fn default() -> Self {
        Self {
            valid: true,
            errors: Vec::new(),
            warnings: Vec::new(),
            constitutional_compliant: true,
            score: 1.0,
        }
    }
}
