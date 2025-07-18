// Constitutional Hash: cdd01ef066bc6cf2
use futures::future;
use governance_rules::{SharedDecision as Decision, LlmError, LlmJudge, Rule, LocalWorkingMemory};
use itertools::Itertools;
use std::mem;
use thiserror::Error;

#[derive(Error, Debug)]
pub enum EngineError {
    #[error("An LLM judgment failed: {0}")]
    Llm(#[from] LlmError),
    #[error("The decision forest was empty")]
    EmptyForest,
}

pub type PolicyTree = Vec<Rule>;

#[derive(Debug, Clone)]
pub struct EngineConfig {
    pub confidence_threshold: f64,
}

#[derive(Debug)]
pub struct InferenceEngine {
    forest: Vec<PolicyTree>,
    config: EngineConfig,
    llm: Box<dyn LlmJudge>,
}

impl InferenceEngine {
    pub fn new(forest: Vec<PolicyTree>, config: EngineConfig, llm: Box<dyn LlmJudge>) -> Self {
        Self { forest, config, llm }
    }

    pub async fn govern(&self, memory: &LocalWorkingMemory) -> Result<(Decision, f64, Vec<Decision>), EngineError> {
        if self.forest.is_empty() {
            return Err(EngineError::EmptyForest);
        }

        let tree_eval_futures = self.forest.iter().map(|tree| self.evaluate_tree(tree, memory));
        let results: Vec<Result<Decision, LlmError>> = future::join_all(tree_eval_futures).await;
        let decisions: Vec<Decision> = results.into_iter().collect::<Result<_, _>>()?;

        let (winner_key, count) = decisions.iter()
            .map(|d| mem::discriminant(d))
            .counts()
            .into_iter()
            .max_by_key(|&(_, c)| c)
            .unwrap(); // Safe due to non-empty check

        let confidence = count as f64 / decisions.len() as f64;
        let final_decision = decisions.iter()
            .find(|d| mem::discriminant(*d) == winner_key)
            .cloned()
            .unwrap();

        if confidence < self.config.confidence_threshold {
            let explanations = decisions.iter().filter_map(|d| match d {
                Decision::Uncertain { explanation } => Some(explanation.as_str()),
                _ => None,
            }).collect::<Vec<_>>().join("; ");
            Ok((Decision::Uncertain { explanation: explanations }, confidence, decisions))
        } else {
            Ok((final_decision, confidence, decisions))
        }
    }

    async fn evaluate_tree(&self, tree: &PolicyTree, memory: &LocalWorkingMemory) -> Result<Decision, LlmError> {
        for rule in tree {
            match rule.evaluate(memory, self.llm.as_ref()).await? {
                Decision::Violate => return Ok(Decision::Violate),
                _ => continue,
            }
        }
        Ok(Decision::Comply)
    }
}
