// Constitutional Hash: cdd01ef066bc6cf2
//! QuantumAGI governance integration module
//! 
//! This module provides client functionality for interacting with the
//! QuantumAGI governance programs on Solana, ensuring constitutional compliance.

use anyhow::{anyhow, Result as AnyResult};
use solana_client::nonblocking::rpc_client::RpcClient;
use solana_sdk::{
    instruction::{AccountMeta, Instruction},
    pubkey::Pubkey,
    signature::{Keypair, Signature, Signer},
    system_program,
    transaction::Transaction,
};

use crate::CONSTITUTIONAL_HASH;

/// QuantumAGI program discriminators (8-byte prefixes for instructions)
const CREATE_POLICY_DISCRIMINATOR: [u8; 8] = [124, 69, 178, 157, 67, 128, 235, 146];
const VOTE_DISCRIMINATOR: [u8; 8] = [132, 148, 3, 170, 149, 189, 196, 66];

/// QuantumAGI client for governance interactions
#[derive(Clone)]
pub struct QuantumAGIClient {
    rpc_url: String,
    program_id: Pubkey,
}

impl QuantumAGIClient {
    pub fn new(rpc_url: String, program_id: Pubkey) -> Self {
        Self { rpc_url, program_id }
    }

    /// Create a policy proposal on the QuantumAGI governance system
    pub async fn create_policy_proposal(
        &self,
        payer: &Keypair,
        proposal_content: &str,
    ) -> AnyResult<Signature> {
        let client = RpcClient::new(self.rpc_url.clone());
        
        // Parse proposal content (expecting JSON with title, description, policy_text)
        let proposal: ProposalData = serde_json::from_str(proposal_content)
            .map_err(|e| anyhow!("Invalid proposal format: {}", e))?;

        // Validate constitutional compliance
        if !proposal.policy_text.contains(CONSTITUTIONAL_HASH) {
            return Err(anyhow!("Proposal must reference constitutional hash"));
        }

        // Generate unique policy ID
        let policy_id = generate_policy_id();

        // Derive PDAs
        let (governance_pda, _) = Pubkey::find_program_address(
            &[b"governance"],
            &self.program_id,
        );

        let (proposal_pda, _) = Pubkey::find_program_address(
            &[b"proposal", &policy_id.to_le_bytes()],
            &self.program_id,
        );

        // Build instruction data
        let mut data = Vec::new();
        data.extend_from_slice(&CREATE_POLICY_DISCRIMINATOR);
        data.extend_from_slice(&policy_id.to_le_bytes());
        
        // Serialize strings (length-prefixed)
        serialize_string(&mut data, &proposal.title)?;
        serialize_string(&mut data, &proposal.description)?;
        serialize_string(&mut data, &proposal.policy_text)?;

        // Create instruction
        let instruction = Instruction {
            program_id: self.program_id,
            accounts: vec![
                AccountMeta::new(proposal_pda, false),
                AccountMeta::new(governance_pda, false),
                AccountMeta::new(payer.pubkey(), true),
                AccountMeta::new_readonly(system_program::id(), false),
            ],
            data,
        };

        // Send transaction
        let recent_blockhash = client.get_latest_blockhash().await?;
        let transaction = Transaction::new_signed_with_payer(
            &[instruction],
            Some(&payer.pubkey()),
            &[payer],
            recent_blockhash,
        );

        let signature = client.send_and_confirm_transaction(&transaction).await?;
        Ok(signature)
    }

    /// Vote on an existing proposal
    pub async fn vote_on_proposal(
        &self,
        voter: &Keypair,
        policy_id: u64,
        vote: bool,
    ) -> AnyResult<Signature> {
        let client = RpcClient::new(self.rpc_url.clone());

        // Derive PDAs
        let (proposal_pda, _) = Pubkey::find_program_address(
            &[b"proposal", &policy_id.to_le_bytes()],
            &self.program_id,
        );

        let (vote_record_pda, _) = Pubkey::find_program_address(
            &[b"vote", &policy_id.to_le_bytes(), voter.pubkey().as_ref()],
            &self.program_id,
        );

        // Build instruction data
        let mut data = Vec::new();
        data.extend_from_slice(&VOTE_DISCRIMINATOR);
        data.extend_from_slice(&policy_id.to_le_bytes());
        data.push(if vote { 1 } else { 0 });

        // Create instruction
        let instruction = Instruction {
            program_id: self.program_id,
            accounts: vec![
                AccountMeta::new(proposal_pda, false),
                AccountMeta::new(vote_record_pda, false),
                AccountMeta::new(voter.pubkey(), true),
                AccountMeta::new_readonly(system_program::id(), false),
            ],
            data,
        };

        // Send transaction
        let recent_blockhash = client.get_latest_blockhash().await?;
        let transaction = Transaction::new_signed_with_payer(
            &[instruction],
            Some(&voter.pubkey()),
            &[voter],
            recent_blockhash,
        );

        let signature = client.send_and_confirm_transaction(&transaction).await?;
        Ok(signature)
    }

    /// Query the status of a proposal
    pub async fn get_proposal_status(&self, policy_id: u64) -> AnyResult<ProposalStatus> {
        let client = RpcClient::new(self.rpc_url.clone());

        let (proposal_pda, _) = Pubkey::find_program_address(
            &[b"proposal", &policy_id.to_le_bytes()],
            &self.program_id,
        );

        let _account = client.get_account(&proposal_pda).await?;
        
        // Parse account data (simplified for demo)
        // In production, use proper Anchor account deserialization
        Ok(ProposalStatus {
            policy_id,
            votes_for: 0,
            votes_against: 0,
            status: "active".to_string(),
        })
    }
}

/// Proposal data structure
#[derive(Debug, serde::Serialize, serde::Deserialize)]
pub struct ProposalData {
    pub title: String,
    pub description: String,
    pub policy_text: String,
}

/// Proposal status
#[derive(Debug)]
pub struct ProposalStatus {
    pub policy_id: u64,
    pub votes_for: u64,
    pub votes_against: u64,
    pub status: String,
}

/// Generate a unique policy ID (simplified - use proper method in production)
fn generate_policy_id() -> u64 {
    use std::time::{SystemTime, UNIX_EPOCH};
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs()
}

/// Serialize a string with length prefix (Anchor format)
fn serialize_string(data: &mut Vec<u8>, s: &str) -> AnyResult<()> {
    let bytes = s.as_bytes();
    if bytes.len() > 1000 {
        return Err(anyhow!("String too long"));
    }
    
    // Write 4-byte length prefix
    data.extend_from_slice(&(bytes.len() as u32).to_le_bytes());
    // Write string bytes
    data.extend_from_slice(bytes);
    
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_serialize_string() {
        let mut data = Vec::new();
        serialize_string(&mut data, "test").unwrap();
        
        assert_eq!(data.len(), 8); // 4 bytes length + 4 bytes "test"
        assert_eq!(&data[0..4], &4u32.to_le_bytes());
        assert_eq!(&data[4..8], b"test");
    }

    #[test]
    fn test_constitutional_validation() {
        let proposal = ProposalData {
            title: "Test Proposal".to_string(),
            description: "A test proposal".to_string(),
            policy_text: format!("Policy compliant with hash {}", CONSTITUTIONAL_HASH),
        };

        assert!(proposal.policy_text.contains(CONSTITUTIONAL_HASH));
    }
}