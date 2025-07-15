//! Specialized nodes for PocketFlow-Rust
//! 
//! This module provides additional node types for building
//! complex AI governance workflows.

use std::collections::HashMap;
use std::sync::{Arc, Mutex};

use anyhow::{anyhow, Result as AnyResult};
use async_trait::async_trait;
use log::{error, info, warn};
use reqwest::Client;
use serde_json::Value;

use crate::{AsyncRunnable, Shared, CONSTITUTIONAL_HASH};

/// Alert node for sending notifications
#[derive(Clone)]
pub struct AlertNode {
    prep: Arc<dyn Fn(&mut Shared) -> String + Send + Sync>,
    webhook_url: String,
    successors: Arc<Mutex<HashMap<String, Arc<dyn AsyncRunnable>>>>,
}

impl AlertNode {
    pub fn new(
        prep: impl Fn(&mut Shared) -> String + Send + Sync + 'static,
        webhook_url: String,
    ) -> Arc<Self> {
        Arc::new(Self {
            prep: Arc::new(prep),
            webhook_url,
            successors: Arc::new(Mutex::new(HashMap::new())),
        })
    }

    pub fn add_successor(&self, action: String, node: Arc<dyn AsyncRunnable>) {
        self.successors.lock().unwrap().insert(action, node);
    }

    async fn send_alert(&self, message: &str) -> AnyResult<()> {
        let client = Client::new();
        let payload = serde_json::json!({
            "text": message,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "service": "PocketFlow-Rust",
        });

        let response = client
            .post(&self.webhook_url)
            .json(&payload)
            .send()
            .await?;

        if !response.status().is_success() {
            return Err(anyhow!("Alert webhook failed: {}", response.status()));
        }

        Ok(())
    }
}

#[async_trait]
impl AsyncRunnable for AlertNode {
    async fn run_async(&self, shared: &mut Shared) -> String {
        let message = (self.prep)(shared);
        info!("Sending alert: {}", message);

        match self.send_alert(&message).await {
            Ok(_) => {
                info!("Alert sent successfully");
                "sent".to_string()
            }
            Err(e) => {
                error!("Failed to send alert: {}", e);
                "failed".to_string()
            }
        }
    }

    fn get_successor(&self, action: &str) -> Option<Arc<dyn AsyncRunnable>> {
        self.successors.lock().unwrap().get(action).cloned()
    }

    fn set_params(&self, _params: HashMap<String, Box<dyn std::any::Any + Send + Sync>>) {}
}

/// Constitutional validator node
#[derive(Clone)]
pub struct ConstitutionalValidatorNode {
    constitutional_service_url: String,
    prep: Arc<dyn Fn(&mut Shared) -> String + Send + Sync>,
    post: Arc<dyn Fn(&mut Shared, bool) -> Option<String> + Send + Sync>,
    successors: Arc<Mutex<HashMap<String, Arc<dyn AsyncRunnable>>>>,
}

impl ConstitutionalValidatorNode {
    pub fn new(
        constitutional_service_url: String,
        prep: impl Fn(&mut Shared) -> String + Send + Sync + 'static,
        post: impl Fn(&mut Shared, bool) -> Option<String> + Send + Sync + 'static,
    ) -> Arc<Self> {
        Arc::new(Self {
            constitutional_service_url,
            prep: Arc::new(prep),
            post: Arc::new(post),
            successors: Arc::new(Mutex::new(HashMap::new())),
        })
    }

    pub fn add_successor(&self, action: String, node: Arc<dyn AsyncRunnable>) {
        self.successors.lock().unwrap().insert(action, node);
    }

    async fn validate_content(&self, content: &str) -> AnyResult<bool> {
        let client = Client::new();
        let validation_request = serde_json::json!({
            "content": content,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        });

        let response = client
            .post(&format!("{}/validate", self.constitutional_service_url))
            .json(&validation_request)
            .send()
            .await?;

        if response.status().is_success() {
            let result: Value = response.json().await?;
            Ok(result["compliant"].as_bool().unwrap_or(false))
        } else {
            Err(anyhow!("Constitutional validation service error"))
        }
    }
}

#[async_trait]
impl AsyncRunnable for ConstitutionalValidatorNode {
    async fn run_async(&self, shared: &mut Shared) -> String {
        let content = (self.prep)(shared);
        info!("Validating content for constitutional compliance");

        let is_compliant = match self.validate_content(&content).await {
            Ok(compliant) => compliant,
            Err(e) => {
                error!("Validation error: {}", e);
                false
            }
        };

        info!("Constitutional compliance: {}", is_compliant);
        shared.insert("constitutional_compliant".to_string(), Box::new(is_compliant));

        let action = (self.post)(shared, is_compliant).unwrap_or("validated".to_string());
        action
    }

    fn get_successor(&self, action: &str) -> Option<Arc<dyn AsyncRunnable>> {
        self.successors.lock().unwrap().get(action).cloned()
    }

    fn set_params(&self, _params: HashMap<String, Box<dyn std::any::Any + Send + Sync>>) {}
}

/// Integrity audit node for logging to ACGS-2 Integrity Service
#[derive(Clone)]
pub struct IntegrityAuditNode {
    integrity_service_url: String,
    prep: Arc<dyn Fn(&mut Shared) -> AuditEvent + Send + Sync>,
    successors: Arc<Mutex<HashMap<String, Arc<dyn AsyncRunnable>>>>,
}

#[derive(Debug, serde::Serialize)]
pub struct AuditEvent {
    pub event_type: String,
    pub actor: String,
    pub action: String,
    pub resource: String,
    pub constitutional_hash: String,
    pub metadata: HashMap<String, String>,
}

impl IntegrityAuditNode {
    pub fn new(
        integrity_service_url: String,
        prep: impl Fn(&mut Shared) -> AuditEvent + Send + Sync + 'static,
    ) -> Arc<Self> {
        Arc::new(Self {
            integrity_service_url,
            prep: Arc::new(prep),
            successors: Arc::new(Mutex::new(HashMap::new())),
        })
    }

    pub fn add_successor(&self, action: String, node: Arc<dyn AsyncRunnable>) {
        self.successors.lock().unwrap().insert(action, node);
    }

    async fn log_audit_event(&self, event: &AuditEvent) -> AnyResult<()> {
        let client = Client::new();
        
        let response = client
            .post(&format!("{}/audit", self.integrity_service_url))
            .json(event)
            .send()
            .await?;

        if !response.status().is_success() {
            return Err(anyhow!("Integrity audit logging failed"));
        }

        Ok(())
    }
}

#[async_trait]
impl AsyncRunnable for IntegrityAuditNode {
    async fn run_async(&self, shared: &mut Shared) -> String {
        let mut event = (self.prep)(shared);
        event.constitutional_hash = CONSTITUTIONAL_HASH.to_string();

        info!("Logging audit event: {:?}", event);

        match self.log_audit_event(&event).await {
            Ok(_) => {
                info!("Audit event logged successfully");
                "logged".to_string()
            }
            Err(e) => {
                error!("Failed to log audit event: {}", e);
                "failed".to_string()
            }
        }
    }

    fn get_successor(&self, action: &str) -> Option<Arc<dyn AsyncRunnable>> {
        self.successors.lock().unwrap().get(action).cloned()
    }

    fn set_params(&self, _params: HashMap<String, Box<dyn std::any::Any + Send + Sync>>) {}
}

/// Conditional branch node for complex decision trees
#[derive(Clone)]
pub struct ConditionalNode {
    condition: Arc<dyn Fn(&mut Shared) -> bool + Send + Sync>,
    true_successor: Arc<Mutex<Option<Arc<dyn AsyncRunnable>>>>,
    false_successor: Arc<Mutex<Option<Arc<dyn AsyncRunnable>>>>,
}

impl ConditionalNode {
    pub fn new(
        condition: impl Fn(&mut Shared) -> bool + Send + Sync + 'static,
    ) -> Arc<Self> {
        Arc::new(Self {
            condition: Arc::new(condition),
            true_successor: Arc::new(Mutex::new(None)),
            false_successor: Arc::new(Mutex::new(None)),
        })
    }

    pub fn set_true_successor(&self, successor: Arc<dyn AsyncRunnable>) {
        *self.true_successor.lock().unwrap() = Some(successor);
    }

    pub fn set_false_successor(&self, successor: Arc<dyn AsyncRunnable>) {
        *self.false_successor.lock().unwrap() = Some(successor);
    }
}

#[async_trait]
impl AsyncRunnable for ConditionalNode {
    async fn run_async(&self, shared: &mut Shared) -> String {
        let result = (self.condition)(shared);
        
        info!("Conditional evaluation: {}", result);
        
        if result {
            "true".to_string()
        } else {
            "false".to_string()
        }
    }

    fn get_successor(&self, action: &str) -> Option<Arc<dyn AsyncRunnable>> {
        match action {
            "true" => self.true_successor.lock().unwrap().clone(),
            "false" => self.false_successor.lock().unwrap().clone(),
            _ => None,
        }
    }

    fn set_params(&self, _params: HashMap<String, Box<dyn std::any::Any + Send + Sync>>) {}
}

/// Batch processing node for handling multiple items
#[derive(Clone)]
pub struct BatchProcessingNode {
    items_extractor: Arc<dyn Fn(&mut Shared) -> Vec<String> + Send + Sync>,
    processor: Arc<dyn Fn(&mut Shared, &str) -> AnyResult<()> + Send + Sync>,
    successors: Arc<Mutex<HashMap<String, Arc<dyn AsyncRunnable>>>>,
}

impl BatchProcessingNode {
    pub fn new(
        items_extractor: impl Fn(&mut Shared) -> Vec<String> + Send + Sync + 'static,
        processor: impl Fn(&mut Shared, &str) -> AnyResult<()> + Send + Sync + 'static,
    ) -> Arc<Self> {
        Arc::new(Self {
            items_extractor: Arc::new(items_extractor),
            processor: Arc::new(processor),
            successors: Arc::new(Mutex::new(HashMap::new())),
        })
    }

    pub fn add_successor(&self, action: String, node: Arc<dyn AsyncRunnable>) {
        self.successors.lock().unwrap().insert(action, node);
    }
}

#[async_trait]
impl AsyncRunnable for BatchProcessingNode {
    async fn run_async(&self, shared: &mut Shared) -> String {
        let items = (self.items_extractor)(shared);
        info!("Processing batch of {} items", items.len());

        let mut success_count = 0;
        let mut error_count = 0;

        for item in &items {
            match (self.processor)(shared, item) {
                Ok(_) => success_count += 1,
                Err(e) => {
                    warn!("Error processing item {}: {}", item, e);
                    error_count += 1;
                }
            }
        }

        info!("Batch processing complete: {} success, {} errors", success_count, error_count);
        
        if error_count == 0 {
            "success".to_string()
        } else if success_count == 0 {
            "failed".to_string()
        } else {
            "partial".to_string()
        }
    }

    fn get_successor(&self, action: &str) -> Option<Arc<dyn AsyncRunnable>> {
        self.successors.lock().unwrap().get(action).cloned()
    }

    fn set_params(&self, _params: HashMap<String, Box<dyn std::any::Any + Send + Sync>>) {}
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_audit_event_creation() {
        let event = AuditEvent {
            event_type: "policy_proposal".to_string(),
            actor: "ai_agent_1".to_string(),
            action: "create".to_string(),
            resource: "proposal_123".to_string(),
            constitutional_hash: CONSTITUTIONAL_HASH.to_string(),
            metadata: HashMap::new(),
        };

        let json = serde_json::to_string(&event).unwrap();
        assert!(json.contains(CONSTITUTIONAL_HASH));
    }

    #[tokio::test]
    async fn test_conditional_node() {
        let node = ConditionalNode::new(|shared| {
            shared.get("test_value")
                .and_then(|v| v.downcast_ref::<bool>())
                .map(|&b| b)
                .unwrap_or(false)
        });

        let mut shared = Shared::new();
        shared.insert("test_value".to_string(), Box::new(true));

        let result = node.as_ref().run_async(&mut shared).await;
        assert_eq!(result, "true");
    }
}