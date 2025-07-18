// Constitutional Hash: cdd01ef066bc6cf2
//! LLM client module for AI-driven decision making
//! 
//! This module provides integration with various LLM providers
//! while ensuring constitutional compliance in all interactions.

use anyhow::{anyhow, Result as AnyResult};
use reqwest::Client;
use serde::{Deserialize, Serialize};
use std::env;

use crate::CONSTITUTIONAL_HASH;

/// Message format for LLM APIs
#[derive(Debug, Serialize, Deserialize)]
pub struct Message {
    pub role: String,
    pub content: String,
}

/// LLM response format
#[derive(Debug, Deserialize)]
struct LLMResponse {
    choices: Vec<Choice>,
}

#[derive(Debug, Deserialize)]
struct Choice {
    message: Message,
}

/// LLM client for interacting with AI models
#[derive(Clone)]
pub struct LLMClient {
    api_key: String,
    client: Client,
    model: String,
}

impl LLMClient {
    pub fn new(api_key: String) -> Self {
        Self {
            api_key,
            client: Client::new(),
            model: "gpt-4o".to_string(), // Default to GPT-4o
        }
    }

    /// Create a new client from environment variables
    pub fn from_env() -> AnyResult<Self> {
        let api_key = env::var("OPENAI_API_KEY")
            .map_err(|_| anyhow!("OPENAI_API_KEY not set"))?;
        Ok(Self::new(api_key))
    }

    /// Set the model to use
    pub fn with_model(mut self, model: String) -> Self {
        self.model = model;
        self
    }

    /// Call the LLM with a prompt
    pub async fn call(&self, prompt: &str) -> AnyResult<String> {
        // System message enforcing constitutional compliance
        let system_message = Message {
            role: "system".to_string(),
            content: format!(
                "You are an AI assistant operating within the ACGS-2 constitutional framework. \
                All responses must comply with constitutional hash: {}. \
                You are helping with AI governance on Solana blockchain.",
                CONSTITUTIONAL_HASH
            ),
        };

        let user_message = Message {
            role: "user".to_string(),
            content: prompt.to_string(),
        };

        let messages = vec![system_message, user_message];

        let response = self
            .client
            .post("https://api.openai.com/v1/chat/completions")
            .header("Authorization", format!("Bearer {}", self.api_key))
            .json(&serde_json::json!({
                "model": self.model,
                "messages": messages,
                "temperature": 0.7,
                "max_tokens": 1000,
            }))
            .send()
            .await?;

        if !response.status().is_success() {
            let error_text = response.text().await?;
            return Err(anyhow!("LLM API error: {}", error_text));
        }

        let llm_response: LLMResponse = response.json().await?;
        
        llm_response
            .choices
            .first()
            .map(|c| c.message.content.clone())
            .ok_or_else(|| anyhow!("No response from LLM"))
    }

    /// Generate a structured policy proposal
    pub async fn generate_policy_proposal(
        &self,
        context: &str,
        requirements: &str,
    ) -> AnyResult<String> {
        let prompt = format!(
            "Generate a JSON policy proposal for the QuantumAGI governance system.\n\
            Context: {}\n\
            Requirements: {}\n\
            The proposal must include:\n\
            - title: A concise title (max 100 chars)\n\
            - description: A clear description (max 500 chars)\n\
            - policy_text: The full policy text (max 1000 chars) that must reference constitutional hash {}\n\
            \n\
            Respond only with valid JSON.",
            context, requirements, CONSTITUTIONAL_HASH
        );

        self.call(&prompt).await
    }

    /// Analyze on-chain data and make a decision
    pub async fn analyze_and_decide(
        &self,
        data: &str,
        decision_criteria: &str,
    ) -> AnyResult<String> {
        let prompt = format!(
            "Analyze the following on-chain data and make a decision based on the criteria.\n\
            Data: {}\n\
            Decision Criteria: {}\n\
            Constitutional Hash: {}\n\
            \n\
            Provide a decision as one of: approve, reject, escalate, or defer.\n\
            Include reasoning that references the constitutional principles.",
            data, decision_criteria, CONSTITUTIONAL_HASH
        );

        let response = self.call(&prompt).await?;
        
        // Extract decision from response
        let decision = if response.contains("approve") {
            "approve"
        } else if response.contains("reject") {
            "reject"
        } else if response.contains("escalate") {
            "escalate"
        } else {
            "defer"
        };

        Ok(decision.to_string())
    }
}

/// Integration with ACGS-2 Constitutional AI Service
pub struct ConstitutionalLLMClient {
    llm_client: LLMClient,
    constitutional_service_url: String,
}

impl ConstitutionalLLMClient {
    pub fn new(api_key: String, constitutional_service_url: String) -> Self {
        Self {
            llm_client: LLMClient::new(api_key),
            constitutional_service_url,
        }
    }

    /// Validate a response against constitutional principles
    pub async fn validate_response(&self, response: &str) -> AnyResult<bool> {
        let client = Client::new();
        
        let validation_request = serde_json::json!({
            "content": response,
            "constitutional_hash": CONSTITUTIONAL_HASH,
        });

        let resp = client
            .post(&format!("{}/validate", self.constitutional_service_url))
            .json(&validation_request)
            .send()
            .await?;

        if resp.status().is_success() {
            let result: serde_json::Value = resp.json().await?;
            Ok(result["compliant"].as_bool().unwrap_or(false))
        } else {
            Err(anyhow!("Constitutional validation failed"))
        }
    }

    /// Generate a constitutionally compliant response
    pub async fn generate_compliant_response(&self, prompt: &str) -> AnyResult<String> {
        let mut attempts = 0;
        const MAX_ATTEMPTS: u32 = 3;

        while attempts < MAX_ATTEMPTS {
            let response = self.llm_client.call(prompt).await?;
            
            if self.validate_response(&response).await? {
                return Ok(response);
            }

            attempts += 1;
            log::warn!("Response failed constitutional validation, retrying...");
        }

        Err(anyhow!("Failed to generate constitutionally compliant response"))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_message_serialization() {
        let message = Message {
            role: "user".to_string(),
            content: "Test message".to_string(),
        };

        let json = serde_json::to_string(&message).unwrap();
        assert!(json.contains("user"));
        assert!(json.contains("Test message"));
    }

    #[tokio::test]
    async fn test_llm_client_creation() {
        let client = LLMClient::new("test_key".to_string());
        assert_eq!(client.model, "gpt-4o");

        let client_with_model = client.with_model("gpt-3.5-turbo".to_string());
        assert_eq!(client_with_model.model, "gpt-3.5-turbo");
    }
}