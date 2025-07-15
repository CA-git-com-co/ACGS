use async_trait::async_trait;
use reqwest::Client;
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::env;
use std::fmt::Debug;
use std::time::Duration;
use thiserror::Error;
pub use moka::future::Cache as MokaCache;
use sha2::{Sha256, Digest};
use std::sync::Arc;
// Redis support available but not used directly in this crate

// Import shared ACGS types
use acgs_types::{Decision, WorkingMemory};

// --- Error & Decision Types ---
#[derive(Error, Debug)]
pub enum LlmError {
    #[error("API request failed: {0}")]
    RequestFailed(#[from] reqwest::Error),
    #[error("Failed to parse API response: {0}")]
    ResponseParsingFailed(String),
    #[error("API key is not set in environment")]
    ApiKeyMissing,
}

// Re-export shared types for public use by other crates
pub use acgs_types::Decision as SharedDecision;
pub use acgs_types::WorkingMemory as SharedWorkingMemory;

// Local governance query structure for this crate's specific needs
#[derive(Debug, Clone, Serialize, Deserialize)]
#[cfg_attr(feature = "utoipa", derive(utoipa::ToSchema))]
pub struct LocalGovernanceQuery {
    /// Role of the actor making the request
    pub actor_role: ActorRole,
    /// Sensitivity level of the data being accessed
    pub data_sensitivity: DataSensitivity,
}

// Compatibility wrapper for WorkingMemory with query field
#[derive(Debug, Clone, Serialize, Deserialize)]
#[cfg_attr(feature = "utoipa", derive(utoipa::ToSchema))]
pub struct LocalWorkingMemory {
    /// The governance query to evaluate
    pub query: LocalGovernanceQuery,
    /// Underlying shared working memory
    pub shared_memory: WorkingMemory,
}

impl LocalWorkingMemory {
    pub fn new(query: LocalGovernanceQuery) -> Self {
        let mut shared_memory = WorkingMemory::new();
        shared_memory.add_fact("actor_role", format!("{:?}", query.actor_role));
        shared_memory.add_fact("data_sensitivity", format!("{:?}", query.data_sensitivity));

        Self {
            query,
            shared_memory,
        }
    }

    pub fn into_shared(self) -> WorkingMemory {
        self.shared_memory
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[cfg_attr(feature = "utoipa", derive(utoipa::ToSchema))]
pub enum ActorRole {
    /// Research personnel
    Researcher,
    /// Clinical staff
    Clinician,
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[cfg_attr(feature = "utoipa", derive(utoipa::ToSchema))]
pub enum DataSensitivity {
    /// Anonymized aggregate data
    AnonymizedAggregate,
    /// Identified patient records
    IdentifiedPatientRecords,
}

// --- LlmJudge Trait and Implementations ---
#[async_trait]
pub trait LlmJudge: Send + Sync + Debug {
    async fn make_judgment(
        &self,
        principle_name: &str,
        memory: &LocalWorkingMemory,
    ) -> Result<Decision, LlmError>;
}

// Mock Judge for testing and cost-free benchmarking
#[derive(Debug)]
pub struct MockLlmJudge;
#[async_trait]
impl LlmJudge for MockLlmJudge {
    async fn make_judgment(&self, principle_name: &str, memory: &LocalWorkingMemory) -> Result<Decision, LlmError> {
        // Simulate network latency
        tokio::time::sleep(Duration::from_millis(50)).await;
        let decision = match principle_name {
            "hipaa-privacy" if memory.query.data_sensitivity == DataSensitivity::IdentifiedPatientRecords => Decision::Violate,
            _ => Decision::Comply,
        };
        Ok(decision)
    }
}

// Real Judge using OpenAI API
#[derive(Debug)]
pub struct OpenAiLlmJudge {
    client: Client,
    api_key: String,
    model: String,
    cache: Arc<MokaCache<String, Decision>>,
}

impl OpenAiLlmJudge {
    pub fn new(model: &str) -> Result<Self, LlmError> {
        let api_key = env::var("OPENAI_API_KEY").map_err(|_| LlmError::ApiKeyMissing)?;

        // Create cache with 1000 entries, 1 hour TTL
        let cache = Arc::new(MokaCache::builder()
            .max_capacity(1000)
            .time_to_live(Duration::from_secs(3600))
            .build());

        Ok(Self {
            client: Client::builder().timeout(Duration::from_secs(30)).build().unwrap(),
            api_key,
            model: model.to_string(),
            cache,
        })
    }

    /// Generate cache key for a query
    fn cache_key(principle_name: &str, memory: &LocalWorkingMemory) -> String {
        let mut hasher = Sha256::new();
        hasher.update(principle_name.as_bytes());
        hasher.update(format!("{:?}", memory.query).as_bytes());
        format!("{:x}", hasher.finalize())
    }
}

#[derive(Deserialize)]
struct OpenAiResponse {
    choices: Vec<OpenAiChoice>,
}
#[derive(Deserialize)]
struct OpenAiChoice {
    message: OpenAiMessage,
}
#[derive(Deserialize)]
struct OpenAiMessage {
    content: String,
}

#[async_trait]
impl LlmJudge for OpenAiLlmJudge {
    async fn make_judgment(&self, principle_name: &str, memory: &LocalWorkingMemory) -> Result<Decision, LlmError> {
        // Check cache first
        let cache_key = Self::cache_key(principle_name, memory);
        if let Some(cached_decision) = self.cache.get(&cache_key).await {
            tracing::debug!("🎯 Cache hit for principle: {}", principle_name);
            return Ok(cached_decision);
        }

        tracing::debug!("🔍 Cache miss, making LLM call for principle: {}", principle_name);
        let prompt = format!(
            "You are an AI governance judge evaluating constitutional compliance.

Principle: {}
Query: {:?}

Analyze if this query complies with the given principle. Consider:
- Data sensitivity and access patterns
- Actor roles and permissions
- Constitutional requirements (hash: cdd01ef066bc6cf2)

Respond with EXACTLY one word: 'Comply', 'Violate', or 'Uncertain'",
            principle_name, memory.query
        );

        let response = self.client.post("https://api.openai.com/v1/chat/completions")
            .bearer_auth(&self.api_key)
            .json(&json!({
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
                "n": 1,
            }))
            .send()
            .await?;

        if !response.status().is_success() {
            let err_text = response.text().await.unwrap_or_else(|_| "Unknown error".into());
            return Err(LlmError::ResponseParsingFailed(format!("API returned non-200 status: {}", err_text)));
        }

        let response_body: OpenAiResponse = response.json().await.map_err(|e| LlmError::ResponseParsingFailed(e.to_string()))?;
        let text = response_body.choices.get(0).map(|c| c.message.content.trim()).unwrap_or("");

        let decision = Self::parse_decision_response(text, principle_name)?;

        // Cache the result
        self.cache.insert(cache_key, decision.clone()).await;
        tracing::debug!("💾 Cached decision for principle: {}", principle_name);

        Ok(decision)
    }

}

impl OpenAiLlmJudge {
    /// Enhanced response parsing that handles various LLM response formats
    fn parse_decision_response(response_text: &str, principle_name: &str) -> Result<Decision, LlmError> {
        let text = response_text.trim().to_lowercase();

        // Handle exact matches first
        if text == "comply" {
            return Ok(Decision::Comply);
        }
        if text == "violate" {
            return Ok(Decision::Violate);
        }
        if text == "uncertain" {
            return Ok(Decision::Uncertain {
                explanation: format!("LLM judged '{}' as uncertain", principle_name)
            });
        }

        // Handle responses with extra text (e.g., "Comply." or "The answer is: Comply")
        if text.contains("comply") {
            return Ok(Decision::Comply);
        }
        if text.contains("violate") {
            return Ok(Decision::Violate);
        }
        if text.contains("uncertain") {
            return Ok(Decision::Uncertain {
                explanation: format!("LLM indicated uncertainty for '{}'", principle_name)
            });
        }

        // Fallback: treat unclear responses as uncertain
        Ok(Decision::Uncertain {
            explanation: format!("Unclear LLM response for '{}': '{}'", principle_name, response_text)
        })
    }
}

// New: Real Judge using Groq API (Compatible with OpenAI format)
#[derive(Debug)]
pub struct GroqLlmJudge {
    client: Client,
    api_key: String,
    model: String,
    cache: Arc<MokaCache<String, Decision>>,
}

impl GroqLlmJudge {
    pub fn new(model: &str) -> Result<Self, LlmError> {
        let api_key = env::var("GROQ_API_KEY").map_err(|_| LlmError::ApiKeyMissing)?;

        // Create cache with 1000 entries, 1 hour TTL
        let cache = Arc::new(MokaCache::builder()
            .max_capacity(1000)
            .time_to_live(Duration::from_secs(3600))
            .build());

        Ok(Self {
            client: Client::builder().timeout(Duration::from_secs(30)).build().unwrap(),
            api_key,
            model: model.to_string(),
            cache,
        })
    }
}

#[async_trait]
impl LlmJudge for GroqLlmJudge {
    async fn make_judgment(&self, principle_name: &str, memory: &LocalWorkingMemory) -> Result<Decision, LlmError> {
        // Check cache first
        let cache_key = OpenAiLlmJudge::cache_key(principle_name, memory);
        if let Some(cached_decision) = self.cache.get(&cache_key).await {
            tracing::debug!("🚀 Groq cache hit for principle: {}", principle_name);
            return Ok(cached_decision);
        }

        tracing::debug!("⚡ Groq cache miss, making ultra-fast LLM call for principle: {}", principle_name);
        let prompt = format!(
            "You are an AI governance judge evaluating constitutional compliance.

Principle: {}
Query: {:?}

Analyze if this query complies with the given principle. Consider:
- Data sensitivity and access patterns
- Actor roles and permissions
- Constitutional requirements (hash: cdd01ef066bc6cf2)

Respond with EXACTLY one word: 'Comply', 'Violate', or 'Uncertain'",
            principle_name, memory.query
        );

        let response = self.client.post("https://api.groq.com/openai/v1/chat/completions")
            .bearer_auth(&self.api_key)
            .json(&json!({
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.0,
                "n": 1,
            }))
            .send()
            .await?;

        if !response.status().is_success() {
            let err_text = response.text().await.unwrap_or_else(|_| "Unknown error".into());
            return Err(LlmError::ResponseParsingFailed(format!("API returned non-200 status: {}", err_text)));
        }

        let response_body: OpenAiResponse = response.json().await.map_err(|e| LlmError::ResponseParsingFailed(e.to_string()))?;
        let text = response_body.choices.get(0).map(|c| c.message.content.trim()).unwrap_or("");

        let decision = OpenAiLlmJudge::parse_decision_response(text, principle_name)?;

        // Cache the result
        self.cache.insert(cache_key, decision.clone()).await;
        tracing::debug!("🚀 Cached Groq decision for principle: {}", principle_name);

        Ok(decision)
    }
}

// --- Rule Enum for Static Dispatch ---
#[derive(Debug, Clone)]
pub enum Rule {
    Hipaa(HIPAAPrivacyRule),
    Fairness(FairnessRule),
    Integrity(IntegrityRule),
}

impl Rule {
    pub fn name(&self) -> &str {
        match self {
            Rule::Hipaa(r) => r.name(),
            Rule::Fairness(r) => r.name(),
            Rule::Integrity(r) => r.name(),
        }
    }

    pub async fn evaluate(&self, memory: &LocalWorkingMemory, llm: &dyn LlmJudge) -> Result<Decision, LlmError> {
        match self {
            Rule::Hipaa(r) => r.evaluate(memory, llm).await,
            Rule::Fairness(r) => r.evaluate(memory, llm).await,
            Rule::Integrity(r) => r.evaluate(memory, llm).await,
        }
    }
}

// --- Concrete Rule Structs ---
#[derive(Debug, Clone)]
pub struct HIPAAPrivacyRule;
impl HIPAAPrivacyRule {
    fn name(&self) -> &str { "hipaa-privacy" }
    async fn evaluate(&self, memory: &LocalWorkingMemory, llm: &dyn LlmJudge) -> Result<Decision, LlmError> {
        llm.make_judgment(self.name(), memory).await
    }
}

#[derive(Debug, Clone)]
pub struct FairnessRule;
impl FairnessRule {
    fn name(&self) -> &str { "fairness" }
    async fn evaluate(&self, memory: &LocalWorkingMemory, llm: &dyn LlmJudge) -> Result<Decision, LlmError> {
        llm.make_judgment(self.name(), memory).await
    }
}

#[derive(Debug, Clone)]
pub struct IntegrityRule;
impl IntegrityRule {
    fn name(&self) -> &str { "integrity" }
    async fn evaluate(&self, memory: &LocalWorkingMemory, llm: &dyn LlmJudge) -> Result<Decision, LlmError> {
        llm.make_judgment(self.name(), memory).await
    }
}
