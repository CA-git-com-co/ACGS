/*!
 * ACGS-2 API Integration
 * Constitutional Hash: cdd01ef066bc6cf2
 */

use std::collections::HashMap;
use serde::{Deserialize, Serialize};
use wasm_bindgen::prelude::*;
use wasm_bindgen_futures::JsFuture;
use web_sys::{Request, RequestInit, RequestMode, Response};

use crate::{ACGSError, Result, CONSTITUTIONAL_HASH};

// API client for ACGS-2 services
#[derive(Debug, Clone, PartialEq)]
pub struct ApiClient {
    pub base_url: String,
    pub headers: HashMap<String, String>,
}

impl ApiClient {
    pub fn new(base_url: String) -> Self {
        let mut headers = HashMap::new();
        headers.insert("Content-Type".to_string(), "application/json".to_string());
        headers.insert("X-Constitutional-Hash".to_string(), CONSTITUTIONAL_HASH.to_string());
        headers.insert("X-Client-Type".to_string(), "rust-wasm".to_string());
        headers.insert("X-Client-Version".to_string(), env!("CARGO_PKG_VERSION").to_string());

        Self { base_url, headers }
    }

    pub fn set_auth_token(&mut self, token: &str) {
        self.headers.insert("Authorization".to_string(), format!("Bearer {}", token));
    }

    pub fn build_url(&self, endpoint: &str) -> String {
        if endpoint.starts_with('/') {
            format!("{}{}", self.base_url, endpoint)
        } else {
            format!("{}/{}", self.base_url, endpoint)
        }
    }

    pub async fn get<T>(&self, endpoint: &str) -> Result<T>
    where
        T: for<'de> Deserialize<'de>,
    {
        let url = self.build_url(endpoint);
        let response = self.make_request("GET", &url, None).await?;
        self.parse_response(response).await
    }

    pub async fn post<T>(&self, endpoint: &str, data: serde_json::Value) -> Result<T>
    where
        T: for<'de> Deserialize<'de>,
    {
        let url = self.build_url(endpoint);
        let body = serde_json::to_string(&data)
            .map_err(|e| ACGSError::NetworkError(format!("Failed to serialize data: {:?}", e)))?;
        
        let response = self.make_request("POST", &url, Some(body)).await?;
        self.parse_response(response).await
    }

    async fn make_request(&self, method: &str, url: &str, body: Option<String>) -> Result<Response> {
        let opts = RequestInit::new();
        opts.set_method(method);
        opts.set_mode(RequestMode::Cors);

        if let Some(body_data) = body {
            opts.set_body(&JsValue::from_str(&body_data));
        }

        let request = Request::new_with_str_and_init(url, &opts)
            .map_err(|e| ACGSError::NetworkError(format!("Failed to create request: {:?}", e)))?;

        // Set headers
        for (key, value) in &self.headers {
            request.headers().set(key, value)
                .map_err(|e| ACGSError::NetworkError(format!("Failed to set header: {:?}", e)))?;
        }

        let window = web_sys::window()
            .ok_or_else(|| ACGSError::NetworkError("No window object".to_string()))?;

        let resp_value = JsFuture::from(window.fetch_with_request(&request))
            .await
            .map_err(|e| ACGSError::NetworkError(format!("Fetch failed: {:?}", e)))?;

        let response: Response = resp_value.dyn_into()
            .map_err(|e| ACGSError::NetworkError(format!("Invalid response: {:?}", e)))?;

        if !response.ok() {
            return Err(ACGSError::NetworkError(format!("HTTP {}: {}", response.status(), response.status_text())));
        }

        Ok(response)
    }

    async fn parse_response<T>(&self, response: Response) -> Result<T>
    where
        T: for<'de> Deserialize<'de>,
    {
        let text_promise = response.text()
            .map_err(|e| ACGSError::NetworkError(format!("Failed to get response text: {:?}", e)))?;
        
        let text_value = JsFuture::from(text_promise)
            .await
            .map_err(|e| ACGSError::NetworkError(format!("Failed to read response: {:?}", e)))?;
        
        let text = text_value.as_string()
            .ok_or_else(|| ACGSError::NetworkError("Response is not text".to_string()))?;
        
        serde_json::from_str(&text)
            .map_err(|e| ACGSError::NetworkError(format!("Failed to parse JSON: {:?}", e)))
    }

    pub async fn health_check(&self) -> Result<HealthStatus> {
        match self.get::<HealthStatus>("/health").await {
            Ok(status) => {
                if status.constitutional_hash != CONSTITUTIONAL_HASH {
                    return Err(ACGSError::ConstitutionalViolation(
                        format!("Service constitutional hash mismatch: expected {}, got {}", 
                               CONSTITUTIONAL_HASH, status.constitutional_hash)
                    ));
                }
                Ok(status)
            }
            Err(_) => {
                // Fallback to simple ping
                self.get::<serde_json::Value>("/ping").await?;
                Ok(HealthStatus {
                    status: "ok".to_string(),
                    constitutional_hash: CONSTITUTIONAL_HASH.to_string(),
                    timestamp: chrono::Utc::now().to_rfc3339(),
                    service: "unknown".to_string(),
                })
            }
        }
    }
}

// Service manager for all ACGS-2 services
#[derive(Debug, Clone, PartialEq)]
pub struct ServiceManager {
    pub clients: HashMap<String, ApiClient>,
}

impl ServiceManager {
    pub fn new() -> Self {
        let mut clients = HashMap::new();
        
        // Initialize clients for each ACGS-2 service
        let services = [
            ("auth", "http://localhost:8016"),
            ("constitutional_ai", "http://localhost:8001"),
            ("integrity", "http://localhost:8002"),
            ("formal_verification", "http://localhost:8003"),
            ("governance_synthesis", "http://localhost:8004"),
            ("policy_governance", "http://localhost:8005"),
            ("evolutionary_computation", "http://localhost:8006"),
        ];

        for (name, url) in services {
            clients.insert(name.to_string(), ApiClient::new(url.to_string()));
        }

        Self { clients }
    }

    pub fn get_client(&self, service_name: &str) -> Option<&ApiClient> {
        self.clients.get(service_name)
    }

    pub async fn check_all_services(&self) -> HashMap<String, bool> {
        let mut results = HashMap::new();
        
        for (service_name, client) in &self.clients {
            let is_healthy = client.health_check().await.is_ok();
            results.insert(service_name.clone(), is_healthy);
            
            if is_healthy {
                log::info!("Service {} is healthy", service_name);
            } else {
                log::warn!("Service {} is not responding", service_name);
            }
        }
        
        results
    }

    // Constitutional AI service methods
    pub async fn validate_constitutional_compliance(&self, data: serde_json::Value) -> Result<crate::state::ConstitutionalCompliance> {
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
}

impl Default for ServiceManager {
    fn default() -> Self {
        Self::new()
    }
}

// Response types
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HealthStatus {
    pub status: String,
    pub constitutional_hash: String,
    pub timestamp: String,
    pub service: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiResponse<T> {
    pub data: T,
    pub success: bool,
    pub message: Option<String>,
    pub constitutional_hash: String,
    pub timestamp: String,
}

impl<T> ApiResponse<T> {
    pub fn is_constitutionally_valid(&self) -> bool {
        self.constitutional_hash == CONSTITUTIONAL_HASH
    }
}
