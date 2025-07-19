/*!
 * ACGS-2 Service Integration Layer
 * Constitutional Hash: cdd01ef066bc6cf2
 * 
 * Provides integration with all ACGS-2 backend services including:
 * - Constitutional AI Service (Port 8001)
 * - Integrity Service (Port 8002) 
 * - Formal Verification Service (Port 8003)
 * - Governance Synthesis Service (Port 8004)
 * - Policy Governance Service (Port 8005)
 * - Evolutionary Computation Service (Port 8006)
 * - Auth Service (Port 8016)
 */

use std::collections::HashMap;
use serde::{Deserialize, Serialize};
use reqwasm::http::Request;
use wasm_bindgen_futures::JsFuture;
use web_sys::{WebSocket, MessageEvent, CloseEvent, ErrorEvent};
use gloo::net::websocket::{Message, WebSocketError};
use futures::{SinkExt, StreamExt};

use crate::{ACGSError, Result, CONSTITUTIONAL_HASH};

pub mod api_client;
pub mod constitutional_ai;
pub mod governance_synthesis;
pub mod policy_governance;
pub mod auth;
pub mod websocket;

// Service configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServiceConfig {
    pub auth_service: String,
    pub constitutional_ai: String,
    pub integrity_service: String,
    pub formal_verification: String,
    pub governance_synthesis: String,
    pub policy_governance: String,
    pub evolutionary_computation: String,
}

impl Default for ServiceConfig {
    fn default() -> Self {
        Self {
            auth_service: "http://localhost:8016".to_string(),
            constitutional_ai: "http://localhost:8001".to_string(),
            integrity_service: "http://localhost:8002".to_string(),
            formal_verification: "http://localhost:8003".to_string(),
            governance_synthesis: "http://localhost:8004".to_string(),
            policy_governance: "http://localhost:8005".to_string(),
            evolutionary_computation: "http://localhost:8006".to_string(),
        }
    }
}

// Service manager for coordinating all ACGS services
#[derive(Debug, Clone)]
pub struct ServiceManager {
    pub config: ServiceConfig,
    pub clients: HashMap<String, api_client::ApiClient>,
    pub websocket_connections: HashMap<String, websocket::WebSocketClient>,
}

impl ServiceManager {
    pub async fn initialize() -> Result<Self> {
        let config = ServiceConfig::default();
        let mut clients = HashMap::new();
        let mut websocket_connections = HashMap::new();

        // Initialize API clients for each service
        for (service_name, base_url) in [
            ("auth", &config.auth_service),
            ("constitutional_ai", &config.constitutional_ai),
            ("integrity", &config.integrity_service),
            ("formal_verification", &config.formal_verification),
            ("governance_synthesis", &config.governance_synthesis),
            ("policy_governance", &config.policy_governance),
            ("evolutionary_computation", &config.evolutionary_computation),
        ] {
            let client = api_client::ApiClient::new(base_url.clone());
            
            // Test connection
            match client.health_check().await {
                Ok(_) => {
                    log::info!("Connected to {} service at {}", service_name, base_url);
                    clients.insert(service_name.to_string(), client);
                }
                Err(e) => {
                    log::warn!("Failed to connect to {} service: {:?}", service_name, e);
                    // Still add the client for potential retry later
                    clients.insert(service_name.to_string(), client);
                }
            }
        }

        // Initialize WebSocket connections for real-time updates
        for (service_name, base_url) in [
            ("constitutional_ai", &config.constitutional_ai),
            ("governance_synthesis", &config.governance_synthesis),
            ("policy_governance", &config.policy_governance),
        ] {
            let ws_url = base_url.replace("http://", "ws://").replace("https://", "wss://") + "/ws";
            
            match websocket::WebSocketClient::new(&ws_url).await {
                Ok(ws_client) => {
                    log::info!("WebSocket connected to {} service", service_name);
                    websocket_connections.insert(service_name.to_string(), ws_client);
                }
                Err(e) => {
                    log::warn!("Failed to connect WebSocket to {} service: {:?}", service_name, e);
                }
            }
        }

        Ok(Self {
            config,
            clients,
            websocket_connections,
        })
    }

    pub fn get_client(&self, service_name: &str) -> Option<&api_client::ApiClient> {
        self.clients.get(service_name)
    }

    pub fn get_websocket(&self, service_name: &str) -> Option<&websocket::WebSocketClient> {
        self.websocket_connections.get(service_name)
    }

    // Constitutional AI service methods
    pub async fn validate_constitutional_compliance(&self, data: serde_json::Value) -> Result<crate::constitutional::ConstitutionalCompliance> {
        let client = self.get_client("constitutional_ai")
            .ok_or_else(|| ACGSError::ServiceError("Constitutional AI service not available".to_string()))?;

        let request_data = serde_json::json!({
            "data": data,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": chrono::Utc::now().to_rfc3339()
        });

        client.post("/api/v1/validate", request_data).await
    }

    // Governance Synthesis service methods
    pub async fn synthesize_governance_policy(&self, principles: Vec<String>) -> Result<serde_json::Value> {
        let client = self.get_client("governance_synthesis")
            .ok_or_else(|| ACGSError::ServiceError("Governance Synthesis service not available".to_string()))?;

        let request_data = serde_json::json!({
            "principles": principles,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": chrono::Utc::now().to_rfc3339()
        });

        client.post("/api/v1/synthesize", request_data).await
    }

    // Policy Governance service methods
    pub async fn evaluate_policy(&self, policy: serde_json::Value) -> Result<serde_json::Value> {
        let client = self.get_client("policy_governance")
            .ok_or_else(|| ACGSError::ServiceError("Policy Governance service not available".to_string()))?;

        let request_data = serde_json::json!({
            "policy": policy,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": chrono::Utc::now().to_rfc3339()
        });

        client.post("/api/v1/policies/evaluate", request_data).await
    }

    // Authentication service methods
    pub async fn authenticate(&self, credentials: serde_json::Value) -> Result<String> {
        let client = self.get_client("auth")
            .ok_or_else(|| ACGSError::ServiceError("Auth service not available".to_string()))?;

        let response: serde_json::Value = client.post("/api/v1/auth/login", credentials).await?;
        
        response.get("token")
            .and_then(|t| t.as_str())
            .map(|s| s.to_string())
            .ok_or_else(|| ACGSError::AuthError("No token in response".to_string()))
    }

    // Service health monitoring
    pub async fn check_all_services_health(&self) -> HashMap<String, bool> {
        let mut health_status = HashMap::new();
        
        for (service_name, client) in &self.clients {
            let is_healthy = client.health_check().await.is_ok();
            health_status.insert(service_name.clone(), is_healthy);
        }
        
        health_status
    }

    // Performance metrics collection
    pub async fn collect_performance_metrics(&self) -> Result<HashMap<String, serde_json::Value>> {
        let mut metrics = HashMap::new();
        
        for (service_name, client) in &self.clients {
            match client.get("/api/v1/metrics").await {
                Ok(service_metrics) => {
                    metrics.insert(service_name.clone(), service_metrics);
                }
                Err(e) => {
                    log::warn!("Failed to collect metrics from {}: {:?}", service_name, e);
                }
            }
        }
        
        Ok(metrics)
    }
}

// Service response wrapper
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServiceResponse<T> {
    pub data: T,
    pub constitutional_hash: String,
    pub timestamp: String,
    pub service: String,
    pub status: String,
}

impl<T> ServiceResponse<T> {
    pub fn is_constitutionally_valid(&self) -> bool {
        self.constitutional_hash == CONSTITUTIONAL_HASH
    }
}

// Service event for real-time updates
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ServiceEvent {
    pub event_type: String,
    pub service: String,
    pub data: serde_json::Value,
    pub constitutional_hash: String,
    pub timestamp: String,
}

impl ServiceEvent {
    pub fn is_constitutionally_valid(&self) -> bool {
        self.constitutional_hash == CONSTITUTIONAL_HASH
    }
}
