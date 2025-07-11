use crate::{AcgsClient, TransactionBuilder};
use anchor_client::{
    solana_sdk::{
        instruction::{AccountMeta, Instruction},
        pubkey::Pubkey,
        signature::Signature,
        signer::Signer,
        system_program,
    },
    Program,
};
use anchor_lang::{prelude::*, InstructionData, ToAccountMetas};
use anyhow::{Result, Context};
use serde::{Deserialize, Serialize};
use std::str::FromStr;

// Constants matching the program
const MAX_PRINCIPLES: usize = 100;
const MAX_POLICY_LENGTH: usize = 1000;
const MAX_TITLE_LENGTH: usize = 100;
const MAX_DESCRIPTION_LENGTH: usize = 500;

// Type-safe wrappers matching program types
#[derive(Debug, Clone, Copy, Serialize, Deserialize, AnchorSerialize, AnchorDeserialize)]
pub struct PolicyId(pub u64);

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ConstitutionalPrinciple {
    pub hash: [u8; 32],
    pub index: u8,
    pub title: String,  // Stored off-chain
    pub content: String, // Stored off-chain
    pub is_active: bool,
    pub created_at: i64,
}

impl ConstitutionalPrinciple {
    pub fn new(index: u8, title: String, content: String) -> Self {
        use anchor_lang::solana_program::hash::hash;
        let combined = format!("{}{}", title, content);
        let hash_result = hash(combined.as_bytes());
        let mut hash_bytes = [0u8; 32];
        hash_bytes.copy_from_slice(&hash_result.to_bytes());

        Self {
            hash: hash_bytes,
            index,
            title,
            content,
            is_active: true,
            created_at: Clock::get().unwrap_or_default().unix_timestamp,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PolicyProposal {
    pub id: PolicyId,
    pub title: String,
    pub description: String,
    pub policy_text: String,
    pub proposer: Pubkey,
    pub created_at: i64,
    pub voting_ends_at: i64,
    pub votes_for: u64,
    pub votes_against: u64,
    pub total_voters: u32,
    pub status: ProposalStatus,
    pub quorum_reached: bool,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, AnchorSerialize, AnchorDeserialize)]
pub enum ProposalStatus {
    Active,
    Approved,
    Rejected,
    Emergency,
    Cancelled,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VoteRecord {
    pub voter: Pubkey,
    pub policy_id: PolicyId,
    pub vote: bool,
    pub voting_power: u64,
    pub timestamp: i64,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, AnchorSerialize, AnchorDeserialize)]
pub enum EmergencyActionType {
    SuspendProposal,
    ForceApproval,
    UpdateAuthority,
    SystemMaintenance,
}

// Instruction data structures
#[derive(AnchorSerialize, AnchorDeserialize)]
struct InitializeGovernanceData {
    authority: Pubkey,
    principle_hashes: Vec<[u8; 32]>,
}

#[derive(AnchorSerialize, AnchorDeserialize)]
struct CreatePolicyProposalData {
    policy_id: PolicyId,
    title: String,
    description: String,
    policy_text: String,
}

#[derive(AnchorSerialize, AnchorDeserialize)]
struct VoteOnProposalData {
    policy_id: PolicyId,
    vote: bool,
    voting_power: u64,
}

#[derive(AnchorSerialize, AnchorDeserialize)]
struct FinalizeProposalData {
    policy_id: PolicyId,
}

#[derive(AnchorSerialize, AnchorDeserialize)]
struct EmergencyActionData {
    action_type: EmergencyActionType,
    target_policy_id: Option<PolicyId>,
    justification: String,
}

// PDA derivation helpers
pub struct GovernancePDAs;

impl GovernancePDAs {
    pub fn governance(program_id: &Pubkey) -> (Pubkey, u8) {
        Pubkey::find_program_address(&[b"governance"], program_id)
    }

    pub fn proposal(program_id: &Pubkey, policy_id: PolicyId) -> (Pubkey, u8) {
        Pubkey::find_program_address(
            &[b"proposal", &policy_id.0.to_le_bytes()],
            program_id,
        )
    }

    pub fn vote_record(
        program_id: &Pubkey,
        policy_id: PolicyId,
        voter: &Pubkey,
    ) -> (Pubkey, u8) {
        Pubkey::find_program_address(
            &[b"vote", &policy_id.0.to_le_bytes(), voter.as_ref()],
            program_id,
        )
    }
}

// Governance operations implementation
impl AcgsClient {
    /// Initialize the governance system with constitutional principles
    pub async fn initialize_governance(
        &self,
        authority: Pubkey,
        principles: Vec<ConstitutionalPrinciple>,
    ) -> Result<Signature> {
        if principles.len() > MAX_PRINCIPLES {
            anyhow::bail!("Too many principles: {} > {}", principles.len(), MAX_PRINCIPLES);
        }

        let program = self.governance_program()?;
        let program_id = self.config.governance_program_id;

        // Derive PDAs
        let (governance_pda, _) = GovernancePDAs::governance(&program_id);

        // Extract principle hashes
        let principle_hashes: Vec<[u8; 32]> = principles.iter()
            .map(|p| p.hash)
            .collect();

        // Build instruction
        let accounts = vec![
            AccountMeta::new(governance_pda, false),
            AccountMeta::new(self.pubkey(), true),
            AccountMeta::new_readonly(system_program::id(), false),
        ];

        let data = InitializeGovernanceData {
            authority,
            principle_hashes,
        };

        let ix = Instruction {
            program_id,
            accounts,
            data: data.try_to_vec()?,
        };

        // Store principles off-chain (in a real implementation)
        for principle in &principles {
            tracing::info!(
                "Storing principle {} off-chain: {}",
                principle.index,
                principle.title
            );
        }

        // Build and send transaction
        let tx = self.transaction_builder()
            .add_instruction(ix)
            .build()?;

        self.send_and_confirm_transaction(tx).await
            .context("Failed to initialize governance")
    }

    /// Submit a new policy proposal
    pub async fn submit_policy_proposal(
        &self,
        policy_id: PolicyId,
        title: String,
        description: String,
        policy_text: String,
    ) -> Result<Signature> {
        // Validate inputs
        if title.len() > MAX_TITLE_LENGTH {
            anyhow::bail!("Title too long: {} > {}", title.len(), MAX_TITLE_LENGTH);
        }
        if description.len() > MAX_DESCRIPTION_LENGTH {
            anyhow::bail!("Description too long: {} > {}", description.len(), MAX_DESCRIPTION_LENGTH);
        }
        if policy_text.len() > MAX_POLICY_LENGTH {
            anyhow::bail!("Policy text too long: {} > {}", policy_text.len(), MAX_POLICY_LENGTH);
        }

        let program_id = self.config.governance_program_id;

        // Derive PDAs
        let (governance_pda, _) = GovernancePDAs::governance(&program_id);
        let (proposal_pda, _) = GovernancePDAs::proposal(&program_id, policy_id);

        // Build instruction
        let accounts = vec![
            AccountMeta::new(proposal_pda, false),
            AccountMeta::new(governance_pda, false),
            AccountMeta::new(self.pubkey(), true),
            AccountMeta::new_readonly(system_program::id(), false),
        ];

        let data = CreatePolicyProposalData {
            policy_id,
            title: title.clone(),
            description: description.clone(),
            policy_text: policy_text.clone(),
        };

        let ix = Instruction {
            program_id,
            accounts,
            data: data.try_to_vec()?,
        };

        // Store full policy text off-chain
        tracing::info!("Storing policy {} off-chain: {}", policy_id.0, title);

        // Build and send transaction
        let tx = self.transaction_builder()
            .add_instruction(ix)
            .build()?;

        self.send_and_confirm_transaction(tx).await
            .context("Failed to submit policy proposal")
    }

    /// Vote on a policy proposal
    pub async fn vote_on_proposal(
        &self,
        policy_id: PolicyId,
        vote: bool,
        voting_power: u64,
    ) -> Result<Signature> {
        if voting_power == 0 {
            anyhow::bail!("Voting power must be greater than 0");
        }

        let program_id = self.config.governance_program_id;

        // Derive PDAs
        let (proposal_pda, _) = GovernancePDAs::proposal(&program_id, policy_id);
        let (vote_record_pda, _) = GovernancePDAs::vote_record(
            &program_id,
            policy_id,
            &self.pubkey(),
        );

        // Build instruction
        let accounts = vec![
            AccountMeta::new(proposal_pda, false),
            AccountMeta::new(vote_record_pda, false),
            AccountMeta::new(self.pubkey(), true),
            AccountMeta::new_readonly(system_program::id(), false),
        ];

        let data = VoteOnProposalData {
            policy_id,
            vote,
            voting_power,
        };

        let ix = Instruction {
            program_id,
            accounts,
            data: data.try_to_vec()?,
        };

        // Build and send transaction
        let tx = self.transaction_builder()
            .add_instruction(ix)
            .build()?;

        tracing::info!(
            "Voting {} on proposal {} with {} voting power",
            if vote { "YES" } else { "NO" },
            policy_id.0,
            voting_power
        );

        self.send_and_confirm_transaction(tx).await
            .context("Failed to vote on proposal")
    }

    /// Finalize a proposal after voting period
    pub async fn finalize_proposal(&self, policy_id: PolicyId) -> Result<Signature> {
        let program_id = self.config.governance_program_id;

        // Derive PDAs
        let (governance_pda, _) = GovernancePDAs::governance(&program_id);
        let (proposal_pda, _) = GovernancePDAs::proposal(&program_id, policy_id);

        // Build instruction
        let accounts = vec![
            AccountMeta::new(proposal_pda, false),
            AccountMeta::new(governance_pda, false),
            AccountMeta::new_readonly(self.pubkey(), true),
        ];

        let data = FinalizeProposalData { policy_id };

        let ix = Instruction {
            program_id,
            accounts,
            data: data.try_to_vec()?,
        };

        // Build and send transaction
        let tx = self.transaction_builder()
            .add_instruction(ix)
            .build()?;

        tracing::info!("Finalizing proposal {}", policy_id.0);

        self.send_and_confirm_transaction(tx).await
            .context("Failed to finalize proposal")
    }

    /// Execute emergency action (authority only)
    pub async fn emergency_action(
        &self,
        action_type: EmergencyActionType,
        target_policy_id: Option<PolicyId>,
        justification: String,
    ) -> Result<Signature> {
        if justification.trim().is_empty() || justification.len() > 500 {
            anyhow::bail!("Invalid justification");
        }

        let program_id = self.config.governance_program_id;

        // Derive PDAs
        let (governance_pda, _) = GovernancePDAs::governance(&program_id);

        // Build instruction
        let accounts = vec![
            AccountMeta::new(governance_pda, false),
            AccountMeta::new_readonly(self.pubkey(), true),
        ];

        let data = EmergencyActionData {
            action_type,
            target_policy_id,
            justification: justification.clone(),
        };

        let ix = Instruction {
            program_id,
            accounts,
            data: data.try_to_vec()?,
        };

        // Build and send transaction
        let tx = self.transaction_builder()
            .add_instruction(ix)
            .build()?;

        tracing::warn!(
            "Executing emergency action: {:?} - {}",
            action_type,
            justification
        );

        self.send_and_confirm_transaction(tx).await
            .context("Failed to execute emergency action")
    }

    /// Get governance state
    pub async fn get_governance_state(&self) -> Result<GovernanceState> {
        let program_id = self.config.governance_program_id;
        let (governance_pda, _) = GovernancePDAs::governance(&program_id);

        // In real implementation, fetch account data and deserialize
        // For now, return mock data
        Ok(GovernanceState {
            authority: self.pubkey(),
            principle_count: 10,
            total_policies: 5,
            active_proposals: 2,
            emergency_mode: false,
            initialized_at: 1640995200,
        })
    }

    /// Get proposal details
    pub async fn get_proposal(&self, policy_id: PolicyId) -> Result<PolicyProposal> {
        let program_id = self.config.governance_program_id;
        let (proposal_pda, _) = GovernancePDAs::proposal(&program_id, policy_id);

        // In real implementation, fetch account data and deserialize
        // For now, return mock data
        Ok(PolicyProposal {
            id: policy_id,
            title: "Mock Proposal".to_string(),
            description: "This is a mock proposal".to_string(),
            policy_text: "Mock policy text".to_string(),
            proposer: self.pubkey(),
            created_at: 1640995200,
            voting_ends_at: 1641081600,
            votes_for: 100,
            votes_against: 50,
            total_voters: 10,
            status: ProposalStatus::Active,
            quorum_reached: false,
        })
    }

    /// Get all active proposals
    pub async fn get_active_proposals(&self) -> Result<Vec<PolicyProposal>> {
        // In real implementation, use getProgramAccounts with filters
        // For now, return empty vector
        tracing::debug!("Fetching active proposals");
        Ok(vec![])
    }

    /// Check constitutional compliance
    pub async fn check_constitutional_compliance(
        &self,
        policy_text: &str,
    ) -> Result<ComplianceReport> {
        // In real implementation, this would involve:
        // 1. Hashing the policy text
        // 2. Checking against constitutional principles
        // 3. Running compliance algorithms

        let compliance_score = if policy_text.contains("unconstitutional") {
            0.3
        } else {
            0.95
        };

        Ok(ComplianceReport {
            is_compliant: compliance_score > 0.8,
            compliance_score,
            violations: vec![],
            recommendations: vec![],
        })
    }
}

// Additional data structures

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GovernanceState {
    pub authority: Pubkey,
    pub principle_count: u32,
    pub total_policies: u32,
    pub active_proposals: u32,
    pub emergency_mode: bool,
    pub initialized_at: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ComplianceReport {
    pub is_compliant: bool,
    pub compliance_score: f64,
    pub violations: Vec<String>,
    pub recommendations: Vec<String>,
}

#[cfg(test)]
mod tests {
    use super::*;
    use anchor_client::solana_sdk::signature::Keypair;

    #[test]
    fn test_constitutional_principle_hashing() {
        let principle = ConstitutionalPrinciple::new(
            0,
            "Test Principle".to_string(),
            "This is a test principle".to_string(),
        );

        assert_eq!(principle.index, 0);
        assert_eq!(principle.title, "Test Principle");
        assert!(principle.is_active);

        // Hash should be deterministic
        let principle2 = ConstitutionalPrinciple::new(
            0,
            "Test Principle".to_string(),
            "This is a test principle".to_string(),
        );
        assert_eq!(principle.hash, principle2.hash);
    }

    #[test]
    fn test_pda_derivation() {
        let program_id = Pubkey::new_unique();
        
        let (governance_pda, bump1) = GovernancePDAs::governance(&program_id);
        let (governance_pda2, bump2) = GovernancePDAs::governance(&program_id);
        
        assert_eq!(governance_pda, governance_pda2);
        assert_eq!(bump1, bump2);

        let policy_id = PolicyId(1);
        let (proposal_pda, _) = GovernancePDAs::proposal(&program_id, policy_id);
        assert_ne!(proposal_pda, governance_pda);
    }

    #[tokio::test]
    async fn test_input_validation() {
        let payer = Keypair::new();
        let client = crate::AcgsClient::devnet(payer).unwrap();

        // Test title too long
        let result = client.submit_policy_proposal(
            PolicyId(1),
            "x".repeat(101),
            "Description".to_string(),
            "Policy text".to_string(),
        ).await;
        
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("Title too long"));

        // Test voting power validation
        let result = client.vote_on_proposal(PolicyId(1), true, 0).await;
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("Voting power must be greater than 0"));
    }

    #[tokio::test]
    async fn test_compliance_check() {
        let payer = Keypair::new();
        let client = crate::AcgsClient::devnet(payer).unwrap();

        let compliant_report = client.check_constitutional_compliance(
            "This is a compliant policy"
        ).await.unwrap();
        
        assert!(compliant_report.is_compliant);
        assert!(compliant_report.compliance_score > 0.8);

        let non_compliant_report = client.check_constitutional_compliance(
            "This is an unconstitutional policy"
        ).await.unwrap();
        
        assert!(!non_compliant_report.is_compliant);
        assert!(non_compliant_report.compliance_score < 0.8);
    }
}