/*!
 * HTTP API Client for ACGS-2 Services
 * Constitutional Hash: cdd01ef066bc6cf2
 */

use std::collections::HashMap;
use serde::{Deserialize, Serialize};
use reqwasm::http::{Request, Response};
use wasm_bindgen::JsValue;
use web_sys::Headers;

use crate::{ACGSError, Result, CONSTITUTIONAL_HASH};

#[derive(Debug, Clone)]
pub struct ApiClient {
    pub base_url: String,
    pub headers: HashMap<String, String>,
    pub timeout_ms: u32,
}

impl ApiClient {
    pub fn new(base_url: String) -> Self {
        let mut headers = HashMap::new();
        headers.insert("Content-Type".to_string(), "application/json".to_string());
        headers.insert("X-Constitutional-Hash".to_string(), CONSTITUTIONAL_HASH.to_string());
        headers.insert("X-Client-Type".to_string(), "rust-wasm".to_string());
        headers.insert("X-Client-Version".to_string(), env!("CARGO_PKG_VERSION").to_string());

        Self {
            base_url,
            headers,
            timeout_ms: 10000, // 10 seconds
        }
    }

    pub fn set_auth_token(&mut self, token: &str) {
        self.headers.insert("Authorization".to_string(), format!("Bearer {}", token));
    }

    pub fn set_header(&mut self, key: String, value: String) {
        self.headers.insert(key, value);
    }

    fn build_url(&self, endpoint: &str) -> String {
        if endpoint.starts_with('/') {
            format!("{}{}", self.base_url, endpoint)
        } else {
            format!("{}/{}", self.base_url, endpoint)
        }
    }

    async fn make_request(&self, method: &str, url: &str, body: Option<String>) -> Result<Response> {
        let mut request = Request::new(&url);
        
        // Set method
        request = match method {
            "GET" => request.method(reqwasm::http::Method::GET),
            "POST" => request.method(reqwasm::http::Method::POST),
            "PUT" => request.method(reqwasm::http::Method::PUT),
            "DELETE" => request.method(reqwasm::http::Method::DELETE),
            "PATCH" => request.method(reqwasm::http::Method::PATCH),
            _ => return Err(ACGSError::NetworkError(format!("Unsupported method: {}", method))),
        };

        // Set headers
        for (key, value) in &self.headers {
            request = request.header(key, value);
        }

        // Set body if provided
        if let Some(body_data) = body {
            request = request.body(body_data);
        }

        // Make the request
        let response = request.send().await
            .map_err(|e| ACGSError::NetworkError(format!("Request failed: {:?}", e)))?;

        // Check for HTTP errors
        if !response.ok() {
            let status = response.status();
            let error_text = response.text().await
                .unwrap_or_else(|_| format!("HTTP {} error", status));
            return Err(ACGSError::NetworkError(format!("HTTP {}: {}", status, error_text)));
        }

        Ok(response)
    }

    pub async fn get<T>(&self, endpoint: &str) -> Result<T>
    where
        T: for<'de> Deserialize<'de>,
    {
        let url = self.build_url(endpoint);
        let response = self.make_request("GET", &url, None).await?;
        
        let text = response.text().await
            .map_err(|e| ACGSError::NetworkError(format!("Failed to read response: {:?}", e)))?;
        
        serde_json::from_str(&text)
            .map_err(|e| ACGSError::NetworkError(format!("Failed to parse JSON: {:?}", e)))
    }

    pub async fn post<T>(&self, endpoint: &str, data: serde_json::Value) -> Result<T>
    where
        T: for<'de> Deserialize<'de>,
    {
        let url = self.build_url(endpoint);
        let body = serde_json::to_string(&data)
            .map_err(|e| ACGSError::NetworkError(format!("Failed to serialize data: {:?}", e)))?;
        
        let response = self.make_request("POST", &url, Some(body)).await?;
        
        let text = response.text().await
            .map_err(|e| ACGSError::NetworkError(format!("Failed to read response: {:?}", e)))?;
        
        serde_json::from_str(&text)
            .map_err(|e| ACGSError::NetworkError(format!("Failed to parse JSON: {:?}", e)))
    }

    pub async fn put<T>(&self, endpoint: &str, data: serde_json::Value) -> Result<T>
    where
        T: for<'de> Deserialize<'de>,
    {
        let url = self.build_url(endpoint);
        let body = serde_json::to_string(&data)
            .map_err(|e| ACGSError::NetworkError(format!("Failed to serialize data: {:?}", e)))?;
        
        let response = self.make_request("PUT", &url, Some(body)).await?;
        
        let text = response.text().await
            .map_err(|e| ACGSError::NetworkError(format!("Failed to read response: {:?}", e)))?;
        
        serde_json::from_str(&text)
            .map_err(|e| ACGSError::NetworkError(format!("Failed to parse JSON: {:?}", e)))
    }

    pub async fn delete(&self, endpoint: &str) -> Result<()> {
        let url = self.build_url(endpoint);
        self.make_request("DELETE", &url, None).await?;
        Ok(())
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

    // Performance monitoring
    pub async fn measure_request_performance<T, F, Fut>(&self, operation: F) -> Result<(T, f64)>
    where
        F: FnOnce() -> Fut,
        Fut: std::future::Future<Output = Result<T>>,
    {
        let start = instant::Instant::now();
        let result = operation().await?;
        let duration_ms = start.elapsed().as_millis() as f64;
        
        // Log performance if it exceeds targets
        if duration_ms > crate::PERFORMANCE_TARGETS.p99_latency_ms as f64 {
            log::warn!("Request exceeded P99 latency target: {}ms > {}ms", 
                      duration_ms, crate::PERFORMANCE_TARGETS.p99_latency_ms);
        }
        
        Ok((result, duration_ms))
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HealthStatus {
    pub status: String,
    pub constitutional_hash: String,
    pub timestamp: String,
    pub service: String,
}

// Request/Response wrapper for constitutional compliance
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConstitutionalRequest<T> {
    pub data: T,
    pub constitutional_hash: String,
    pub timestamp: String,
    pub request_id: String,
}

impl<T> ConstitutionalRequest<T> {
    pub fn new(data: T) -> Self {
        Self {
            data,
            constitutional_hash: CONSTITUTIONAL_HASH.to_string(),
            timestamp: chrono::Utc::now().to_rfc3339(),
            request_id: uuid::Uuid::new_v4().to_string(),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConstitutionalResponse<T> {
    pub data: T,
    pub constitutional_hash: String,
    pub timestamp: String,
    pub request_id: String,
    pub service: String,
}

impl<T> ConstitutionalResponse<T> {
    pub fn is_valid(&self) -> bool {
        self.constitutional_hash == CONSTITUTIONAL_HASH
    }
}
