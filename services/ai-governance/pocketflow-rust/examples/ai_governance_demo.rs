//! AI Governance Demo for ACGS-2 Integration
//! 
//! This example demonstrates how PocketFlow-Rust enables AI agents to autonomously
//! interact with the QuantumAGI governance system on Solana.
//! 
//! Constitutional Hash: cdd01ef066bc6cf2

use std::collections::HashMap;
use std::env;
use std::str::FromStr;

use anyhow::Result as AnyResult;
use log::info;
use pocketflow_rust::{
    AsyncFlow, AsyncSolanaQueryNode, LLMNode, QuantumAGINode, Shared, CONSTITUTIONAL_HASH,
    nodes::{AlertNode, ConstitutionalValidatorNode, IntegrityAuditNode, AuditEvent},
};
use solana_sdk::{pubkey::Pubkey, signature::Keypair};

#[tokio::main]
async fn main() -> AnyResult<()> {
    env_logger::init();
    info!("Starting AI Governance Demo");

    // Initialize shared state
    let mut shared: Shared = HashMap::new();
    shared.insert("wallet_pubkey".to_string(), Box::new(Pubkey::new_unique()));
    shared.insert("constitutional_hash".to_string(), Box::new(CONSTITUTIONAL_HASH.to_string()));
    shared.insert("balance_threshold".to_string(), Box::new(10_000_000u64)); // 0.01 SOL

    // Configuration
    let rpc_url = "https://api.devnet.solana.com".to_string();
    let quantum_program_id = Pubkey::from_str("45shrZAMBbFGfLrev4FSDBchP847Q7oUR4jVqcxqnRD3")?;
    let api_key = env::var("OPENAI_API_KEY").unwrap_or_else(|_| "demo_key".to_string());

    // Create the AI governance workflow
    let workflow = build_ai_governance_workflow(rpc_url, quantum_program_id, api_key)?;

    // Execute the workflow
    workflow.run_async(&mut shared).await?;

    info!("AI Governance Demo completed successfully");
    Ok(())
}

fn build_ai_governance_workflow(
    rpc_url: String,
    quantum_program_id: Pubkey,
    api_key: String,
) -> AnyResult<AsyncFlow> {
    // 1. Solana Balance Query Node
    let solana_node = AsyncSolanaQueryNode::new(
        rpc_url.clone(),
        |shared| {
            *shared.get("wallet_pubkey")
                .unwrap()
                .downcast_ref::<Pubkey>()
                .unwrap()
        },
        |shared, _pubkey, balance| {
            shared.insert("current_balance".to_string(), Box::new(balance));
            let threshold = *shared.get("balance_threshold")
                .unwrap()
                .downcast_ref::<u64>()
                .unwrap();
            
            if balance < threshold {
                Some("low_balance".to_string())
            } else {
                Some("sufficient_balance".to_string())
            }
        },
        3, // max retries
        2, // wait seconds
    );

    // 2. LLM Analysis Node
    let llm_node = LLMNode::new(
        |shared| {
            let balance = *shared.get("current_balance")
                .unwrap()
                .downcast_ref::<u64>()
                .unwrap();
            let threshold = *shared.get("balance_threshold")
                .unwrap()
                .downcast_ref::<u64>()
                .unwrap();
            
            format!(
                "Analyze the current balance {} lamports against threshold {} lamports. \
                If balance is low, recommend a governance action to optimize costs. \
                Respond with: 'propose_optimization' if action needed, 'monitor' if not.",
                balance, threshold
            )
        },
        |shared, response| {
            shared.insert("llm_analysis".to_string(), Box::new(response.clone()));
            if response.contains("propose_optimization") {
                Some("propose".to_string())
            } else {
                Some("monitor".to_string())
            }
        },
        api_key.clone(),
    );

    // 3. Constitutional Validator Node
    let validator_node = ConstitutionalValidatorNode::new(
        "http://localhost:8001".to_string(), // Constitutional AI Service
        |shared| {
            shared.get("llm_analysis")
                .unwrap()
                .downcast_ref::<String>()
                .unwrap()
                .clone()
        },
        |shared, is_compliant| {
            shared.insert("is_constitutionally_compliant".to_string(), Box::new(is_compliant));
            if is_compliant {
                Some("compliant".to_string())
            } else {
                Some("non_compliant".to_string())
            }
        },
    );

    // 4. QuantumAGI Governance Node
    let quantum_node = QuantumAGINode::new(
        rpc_url.clone(),
        Keypair::new(),
        quantum_program_id,
        |shared| {
            let balance = *shared.get("current_balance")
                .unwrap()
                .downcast_ref::<u64>()
                .unwrap();
            
            format!(
                "Create a policy proposal to optimize transaction costs when balance is low. \
                Current balance: {} lamports. \
                Proposal should suggest fee optimization strategies that comply with constitutional hash {}.",
                balance, CONSTITUTIONAL_HASH
            )
        },
        |shared, proposal| {
            shared.insert("governance_proposal".to_string(), Box::new(proposal.clone()));
            Some("proposed".to_string())
        },
        api_key.clone(),
    );

    // 5. Integrity Audit Node
    let audit_node = IntegrityAuditNode::new(
        "http://localhost:8002".to_string(), // Integrity Service
        |shared| {
            AuditEvent {
                event_type: "ai_governance_action".to_string(),
                actor: "pocketflow_ai_agent".to_string(),
                action: "policy_proposal_creation".to_string(),
                resource: shared.get("governance_proposal")
                    .map(|p| p.downcast_ref::<String>().unwrap().clone())
                    .unwrap_or_else(|| "unknown".to_string()),
                constitutional_hash: CONSTITUTIONAL_HASH.to_string(),
                metadata: {
                    let mut meta = HashMap::new();
                    meta.insert("balance".to_string(), 
                        shared.get("current_balance")
                            .unwrap()
                            .downcast_ref::<u64>()
                            .unwrap()
                            .to_string());
                    meta
                },
            }
        },
    );

    // 6. Alert Node
    let alert_node = AlertNode::new(
        |shared| {
            let balance = *shared.get("current_balance")
                .unwrap()
                .downcast_ref::<u64>()
                .unwrap();
            
            format!(
                "🤖 AI Governance Action Completed\n\
                Balance: {} lamports\n\
                Action: Policy proposal submitted\n\
                Constitutional Hash: {}\n\
                Compliance: Verified",
                balance, CONSTITUTIONAL_HASH
            )
        },
        "https://hooks.slack.com/services/YOUR/WEBHOOK/URL".to_string(),
    );

    // 7. Monitoring Node (for sufficient balance)
    let monitor_node = AlertNode::new(
        |shared| {
            let balance = *shared.get("current_balance")
                .unwrap()
                .downcast_ref::<u64>()
                .unwrap();
            
            format!(
                "📊 Balance Monitoring Update\n\
                Balance: {} lamports\n\
                Status: Sufficient\n\
                Constitutional Hash: {}",
                balance, CONSTITUTIONAL_HASH
            )
        },
        "https://hooks.slack.com/services/YOUR/WEBHOOK/URL".to_string(),
    );

    // Build the workflow graph
    // solana_node -> llm_node -> validator_node -> quantum_node -> audit_node -> alert_node
    //             \-> monitor_node (if balance sufficient)
    
    solana_node.add_successor("low_balance".to_string(), llm_node.clone());
    solana_node.add_successor("sufficient_balance".to_string(), monitor_node.clone());
    
    llm_node.add_successor("propose".to_string(), validator_node.clone());
    llm_node.add_successor("monitor".to_string(), monitor_node.clone());
    
    validator_node.add_successor("compliant".to_string(), quantum_node.clone());
    validator_node.add_successor("non_compliant".to_string(), alert_node.clone());
    
    quantum_node.add_successor("proposed".to_string(), audit_node.clone());
    quantum_node.add_successor("failed".to_string(), alert_node.clone());
    
    audit_node.add_successor("logged".to_string(), alert_node.clone());
    audit_node.add_successor("failed".to_string(), alert_node.clone());

    Ok(AsyncFlow::new(solana_node))
}

/// Example of a custom node for specific business logic
#[cfg(feature = "custom-nodes")]
mod custom_nodes {
    use super::*;
    use async_trait::async_trait;
    use pocketflow_rust::AsyncRunnable;

    pub struct CostOptimizationNode {
        // Custom implementation for cost optimization strategies
    }

    #[async_trait]
    impl AsyncRunnable for CostOptimizationNode {
        async fn run_async(&self, shared: &mut Shared) -> String {
            // Implement cost optimization logic
            "optimized".to_string()
        }

        fn get_successor(&self, _action: &str) -> Option<std::rc::Rc<dyn AsyncRunnable>> {
            None
        }

        fn set_params(&self, _params: HashMap<String, Box<dyn std::any::Any>>) {}
    }
}