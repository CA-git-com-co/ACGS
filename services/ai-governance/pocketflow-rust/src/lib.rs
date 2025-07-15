//! PocketFlow-Rust: AI-driven governance framework for ACGS-2
//! 
//! This module provides a minimalist yet powerful framework for creating
//! AI agents that can interact with the QuantumAGI governance system on Solana.
//! 
//! Constitutional Hash: cdd01ef066bc6cf2

use std::any::Any;
use std::collections::HashMap;
use std::sync::{Arc, Mutex};
use std::time::Duration;

use anyhow::{anyhow, Result as AnyResult};
use async_trait::async_trait;
use log::{error, info};
use solana_client::nonblocking::rpc_client::RpcClient as NonblockingRpcClient;
use solana_sdk::{
    commitment_config::CommitmentConfig,
    pubkey::Pubkey,
    signature::Keypair,
};
use tokio::time::sleep;

pub mod governance;
pub mod llm;
pub mod nodes;

use crate::governance::QuantumAGIClient;
use crate::llm::LLMClient;

/// Constitutional hash for ACGS-2 compliance
pub const CONSTITUTIONAL_HASH: &str = "cdd01ef066bc6cf2";

/// Shared state for passing data between nodes
pub type Shared = HashMap<String, Box<dyn Any + Send + Sync>>;

/// Trait for synchronous runnable nodes
pub trait Runnable: Send + Sync {
    fn run(&self, shared: &mut Shared) -> String;
    fn get_successor(&self, action: &str) -> Option<Arc<dyn Runnable>>;
    fn set_params(&self, params: HashMap<String, Box<dyn Any + Send + Sync>>);
}

/// Trait for asynchronous runnable nodes
#[async_trait]
pub trait AsyncRunnable: Send + Sync {
    async fn run_async(&self, shared: &mut Shared) -> String;
    fn get_successor(&self, action: &str) -> Option<Arc<dyn AsyncRunnable>>;
    fn set_params(&self, params: HashMap<String, Box<dyn Any + Send + Sync>>);
}

/// Core flow executor for asynchronous workflows
pub struct AsyncFlow {
    start: Arc<dyn AsyncRunnable>,
}

impl AsyncFlow {
    pub fn new(start: Arc<dyn AsyncRunnable>) -> Self {
        Self { start }
    }

    pub async fn run_async(&self, shared: &mut Shared) -> AnyResult<()> {
        let mut current = Some(self.start.clone());
        let mut steps = 0;
        const MAX_STEPS: usize = 1000;

        // Ensure constitutional hash is in shared state
        shared.insert(
            "constitutional_hash".to_string(),
            Box::new(CONSTITUTIONAL_HASH.to_string()),
        );

        while let Some(node) = current {
            if steps >= MAX_STEPS {
                return Err(anyhow!("Maximum steps exceeded"));
            }
            
            let action = node.run_async(shared).await;
            info!("Node executed with action: {}", action);
            
            current = node.get_successor(&action);
            steps += 1;
        }

        Ok(())
    }
}

/// Asynchronous Solana query node for balance checks
#[derive(Clone)]
pub struct AsyncSolanaQueryNode {
    rpc_url: String,
    prep: Arc<dyn Fn(&mut Shared) -> Pubkey + Send + Sync>,
    post: Arc<dyn Fn(&mut Shared, &Pubkey, u64) -> Option<String> + Send + Sync>,
    max_retries: u32,
    wait: u32,
    successors: Arc<Mutex<HashMap<String, Arc<dyn AsyncRunnable>>>>,
}

impl AsyncSolanaQueryNode {
    pub fn new(
        rpc_url: String,
        prep: impl Fn(&mut Shared) -> Pubkey + Send + Sync + 'static,
        post: impl Fn(&mut Shared, &Pubkey, u64) -> Option<String> + Send + Sync + 'static,
        max_retries: u32,
        wait: u32,
    ) -> Arc<Self> {
        Arc::new(Self {
            rpc_url,
            prep: Arc::new(prep),
            post: Arc::new(post),
            max_retries,
            wait,
            successors: Arc::new(Mutex::new(HashMap::new())),
        })
    }

    pub fn add_successor(&self, action: String, node: Arc<dyn AsyncRunnable>) {
        self.successors.lock().unwrap().insert(action, node);
    }

    async fn query_balance(&self, pubkey: &Pubkey) -> AnyResult<u64> {
        let client = NonblockingRpcClient::new_with_commitment(
            self.rpc_url.clone(),
            CommitmentConfig::confirmed(),
        );
        client.get_balance(pubkey).await.map_err(|e| anyhow!(e))
    }
}

#[async_trait]
impl AsyncRunnable for AsyncSolanaQueryNode {
    async fn run_async(&self, shared: &mut Shared) -> String {
        info!("Solana query started");
        let pubkey = (self.prep)(shared);
        let mut balance: u64 = 0;
        let mut last_exc: Option<anyhow::Error> = None;

        for attempt in 0..self.max_retries {
            match self.query_balance(&pubkey).await {
                Ok(b) => {
                    balance = b;
                    last_exc = None;
                    info!("Successfully queried balance: {} lamports", b);
                    break;
                }
                Err(e) => {
                    error!("Query attempt {} failed: {}", attempt + 1, e);
                    last_exc = Some(e);
                    sleep(Duration::from_secs(self.wait as u64)).await;
                }
            }
        }

        if let Some(e) = last_exc {
            error!("All query attempts failed: {}", e);
            balance = 0;
        }

        let action = (self.post)(shared, &pubkey, balance).unwrap_or("default".to_string());
        action
    }

    fn get_successor(&self, action: &str) -> Option<Arc<dyn AsyncRunnable>> {
        self.successors.lock().unwrap().get(action).cloned()
    }

    fn set_params(&self, _params: HashMap<String, Box<dyn Any + Send + Sync>>) {}
}

/// LLM node for AI-driven decision making
#[derive(Clone)]
pub struct LLMNode {
    prep: Arc<dyn Fn(&mut Shared) -> String + Send + Sync>,
    post: Arc<dyn Fn(&mut Shared, &String) -> Option<String> + Send + Sync>,
    successors: Arc<Mutex<HashMap<String, Arc<dyn AsyncRunnable>>>>,
    llm_client: LLMClient,
}

impl LLMNode {
    pub fn new(
        prep: impl Fn(&mut Shared) -> String + Send + Sync + 'static,
        post: impl Fn(&mut Shared, &String) -> Option<String> + Send + Sync + 'static,
        api_key: String,
    ) -> Arc<Self> {
        Arc::new(Self {
            prep: Arc::new(prep),
            post: Arc::new(post),
            successors: Arc::new(Mutex::new(HashMap::new())),
            llm_client: LLMClient::new(api_key),
        })
    }

    pub fn add_successor(&self, action: String, node: Arc<dyn AsyncRunnable>) {
        self.successors.lock().unwrap().insert(action, node);
    }
}

#[async_trait]
impl AsyncRunnable for LLMNode {
    async fn run_async(&self, shared: &mut Shared) -> String {
        info!("LLM analysis started");
        let prompt = (self.prep)(shared);
        
        // Ensure constitutional compliance in prompt
        let constitutional_prompt = format!(
            "Constitutional Hash: {}. {}",
            CONSTITUTIONAL_HASH, prompt
        );

        let response = match self.llm_client.call(&constitutional_prompt).await {
            Ok(resp) => resp,
            Err(e) => {
                error!("LLM call failed: {}", e);
                "error".to_string()
            }
        };

        let action = (self.post)(shared, &response).unwrap_or("default".to_string());
        info!("LLM decision: {}", action);
        action
    }

    fn get_successor(&self, action: &str) -> Option<Arc<dyn AsyncRunnable>> {
        self.successors.lock().unwrap().get(action).cloned()
    }

    fn set_params(&self, _params: HashMap<String, Box<dyn Any + Send + Sync>>) {}
}

/// QuantumAGI governance interaction node
#[derive(Clone)]
pub struct QuantumAGINode {
    #[allow(dead_code)]
    rpc_url: String,
    payer: Arc<Keypair>,
    #[allow(dead_code)]
    program_id: Pubkey,
    prep: Arc<dyn Fn(&mut Shared) -> String + Send + Sync>,
    post: Arc<dyn Fn(&mut Shared, &String) -> Option<String> + Send + Sync>,
    successors: Arc<Mutex<HashMap<String, Arc<dyn AsyncRunnable>>>>,
    quantum_client: QuantumAGIClient,
    llm_client: LLMClient,
}

impl QuantumAGINode {
    pub fn new(
        rpc_url: String,
        payer: Keypair,
        program_id: Pubkey,
        prep: impl Fn(&mut Shared) -> String + Send + Sync + 'static,
        post: impl Fn(&mut Shared, &String) -> Option<String> + Send + Sync + 'static,
        api_key: String,
    ) -> Arc<Self> {
        let quantum_client = QuantumAGIClient::new(rpc_url.clone(), program_id);
        Arc::new(Self {
            rpc_url,
            payer: Arc::new(payer),
            program_id,
            prep: Arc::new(prep),
            post: Arc::new(post),
            successors: Arc::new(Mutex::new(HashMap::new())),
            quantum_client,
            llm_client: LLMClient::new(api_key),
        })
    }

    pub fn add_successor(&self, action: String, node: Arc<dyn AsyncRunnable>) {
        self.successors.lock().unwrap().insert(action, node);
    }
}

#[async_trait]
impl AsyncRunnable for QuantumAGINode {
    async fn run_async(&self, shared: &mut Shared) -> String {
        info!("QuantumAGI governance interaction started");
        let prompt = (self.prep)(shared);

        // Generate policy proposal using LLM
        let proposal_prompt = format!(
            "Generate a QuantumAGI policy proposal that is compliant with constitutional hash {}. Context: {}",
            CONSTITUTIONAL_HASH, prompt
        );

        let proposal_content = match self.llm_client.call(&proposal_prompt).await {
            Ok(content) => content,
            Err(e) => {
                error!("Failed to generate proposal: {}", e);
                return "error".to_string();
            }
        };

        // Create governance proposal instruction
        match self.quantum_client.create_policy_proposal(
            &*self.payer,
            &proposal_content,
        ).await {
            Ok(signature) => {
                info!("Policy proposed successfully: {}", signature);
                shared.insert("proposal_signature".to_string(), Box::new(signature));
            }
            Err(e) => {
                error!("Proposal submission failed: {}", e);
                return "failed".to_string();
            }
        }

        let action = (self.post)(shared, &proposal_content).unwrap_or("proposed".to_string());
        action
    }

    fn get_successor(&self, action: &str) -> Option<Arc<dyn AsyncRunnable>> {
        self.successors.lock().unwrap().get(action).cloned()
    }

    fn set_params(&self, _params: HashMap<String, Box<dyn Any + Send + Sync>>) {}
}

#[cfg(feature = "python")]
pub mod python_bridge {
    use super::*;
    use pyo3::prelude::*;

    #[pyclass]
    pub struct PyAsyncFlow {
        inner: AsyncFlow,
    }

    #[pymethods]
    impl PyAsyncFlow {
        #[new]
        fn new(start_node: PyObject) -> PyResult<Self> {
            // Implementation would convert Python node to Rust node
            unimplemented!("Python bridge implementation pending")
        }

        fn run_async(&self, py: Python, shared: &PyDict) -> PyResult<()> {
            let mut rust_shared: Shared = HashMap::new();
            
            // Convert PyDict to Rust HashMap
            for (key, value) in shared.iter() {
                let key_str = key.extract::<String>()?;
                // For now, just handle strings
                if let Ok(val_str) = value.extract::<String>() {
                    rust_shared.insert(key_str, Box::new(val_str));
                }
            }

            // Run the flow
            py.allow_threads(|| {
                tokio::runtime::Runtime::new()
                    .unwrap()
                    .block_on(self.inner.run_async(&mut rust_shared))
                    .unwrap();
            });

            // Update PyDict with results
            for (k, v) in rust_shared {
                if let Some(s) = v.downcast_ref::<String>() {
                    shared.set_item(k, s)?;
                }
            }

            Ok(())
        }
    }

    #[pymodule]
    fn pocketflow_rust(_py: Python, m: &PyModule) -> PyResult<()> {
        m.add_class::<PyAsyncFlow>()?;
        m.add("CONSTITUTIONAL_HASH", CONSTITUTIONAL_HASH)?;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_async_flow() {
        let mut shared = Shared::new();
        shared.insert("test_key".to_string(), Box::new("test_value".to_string()));

        // Test basic flow execution
        // Implementation pending
    }
}