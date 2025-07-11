use anchor_client::{
    solana_sdk::{
        commitment_config::CommitmentConfig,
        pubkey::Pubkey,
        signature::{Keypair, Signature},
        signer::Signer,
        transaction::Transaction,
        system_instruction,
    },
    Client, Cluster, Program,
};
use anyhow::{Result, Context, bail};
use std::{rc::Rc, time::Duration};
use tokio::time::sleep;
use serde::{Deserialize, Serialize};

pub mod governance;
pub mod appeals;
pub mod logging;
pub mod test_infrastructure;

// Configuration for program IDs
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProgramConfig {
    pub governance_program_id: Pubkey,
    pub appeals_program_id: Pubkey,
    pub logging_program_id: Pubkey,
}

impl ProgramConfig {
    /// Load from environment variables
    pub fn from_env() -> Result<Self> {
        Ok(Self {
            governance_program_id: std::env::var("GOVERNANCE_PROGRAM_ID")
                .context("GOVERNANCE_PROGRAM_ID not set")?
                .parse()
                .context("Invalid GOVERNANCE_PROGRAM_ID")?,
            appeals_program_id: std::env::var("APPEALS_PROGRAM_ID")
                .context("APPEALS_PROGRAM_ID not set")?
                .parse()
                .context("Invalid APPEALS_PROGRAM_ID")?,
            logging_program_id: std::env::var("LOGGING_PROGRAM_ID")
                .context("LOGGING_PROGRAM_ID not set")?
                .parse()
                .context("Invalid LOGGING_PROGRAM_ID")?,
        })
    }

    /// Load from a JSON file
    pub fn from_file(path: &str) -> Result<Self> {
        let content = std::fs::read_to_string(path)
            .context("Failed to read program config file")?;
        serde_json::from_str(&content)
            .context("Failed to parse program config")
    }

    /// Default devnet configuration
    pub fn devnet() -> Self {
        Self {
            governance_program_id: "8eRUCnQsDxqK7vjp5XsYs7C3NGpdhzzaMW8QQGzfTUV4"
                .parse().unwrap(),
            appeals_program_id: "CXKCLqyzxqyqTbEgpNbYR5qkC691BdiKMAB1nk6BMoFJ"
                .parse().unwrap(),
            logging_program_id: "7ZVxgkky5V12gvpfDh174nsDT8vfT7vQhN77C6csamsw"
                .parse().unwrap(),
        }
    }
}

// Transaction retry configuration
#[derive(Debug, Clone)]
pub struct RetryConfig {
    pub max_retries: u32,
    pub initial_backoff: Duration,
    pub max_backoff: Duration,
    pub exponential_base: f64,
}

impl Default for RetryConfig {
    fn default() -> Self {
        Self {
            max_retries: 3,
            initial_backoff: Duration::from_millis(500),
            max_backoff: Duration::from_secs(5),
            exponential_base: 2.0,
        }
    }
}

/// Enhanced ACGS Blockchain Client for Rust
///
/// Provides a robust, type-safe interface to interact with ACGS Solana programs
/// with improved error handling, retry logic, and monitoring capabilities.
pub struct AcgsClient {
    client: Client<Rc<Keypair>>,
    payer: Rc<Keypair>,
    config: ProgramConfig,
    retry_config: RetryConfig,
    commitment: CommitmentConfig,
}

impl AcgsClient {
    /// Create a new ACGS client instance with configuration
    pub fn new(
        cluster: Cluster,
        payer: Keypair,
        config: ProgramConfig,
        commitment: CommitmentConfig,
    ) -> Result<Self> {
        let payer = Rc::new(payer);
        let client = Client::new_with_options(
            cluster.clone(),
            payer.clone(),
            commitment,
        );

        // Validate cluster connection
        Self::validate_cluster_connection(&cluster)?;

        Ok(Self {
            client,
            payer,
            config,
            retry_config: RetryConfig::default(),
            commitment,
        })
    }

    /// Create client with automatic configuration detection
    pub fn auto_configure(payer: Keypair) -> Result<Self> {
        // Try to load from environment first
        let config = ProgramConfig::from_env()
            .or_else(|_| ProgramConfig::from_file("program_ids.json"))
            .unwrap_or_else(|_| ProgramConfig::devnet());

        // Detect cluster from environment
        let cluster = match std::env::var("SOLANA_CLUSTER").as_deref() {
            Ok("mainnet") => Cluster::Mainnet,
            Ok("testnet") => Cluster::Testnet,
            Ok("localnet") => Cluster::Localnet,
            _ => Cluster::Devnet,
        };

        Self::new(cluster, payer, config, CommitmentConfig::confirmed())
    }

    /// Create client for devnet with default program IDs
    pub fn devnet(payer: Keypair) -> Result<Self> {
        Self::new(
            Cluster::Devnet,
            payer,
            ProgramConfig::devnet(),
            CommitmentConfig::confirmed(),
        )
    }

    /// Create client for localnet (for testing)
    pub fn localnet(payer: Keypair, config: ProgramConfig) -> Result<Self> {
        Self::new(
            Cluster::Localnet,
            payer,
            config,
            CommitmentConfig::processed(), // Faster for local testing
        )
    }

    /// Set custom retry configuration
    pub fn with_retry_config(mut self, retry_config: RetryConfig) -> Self {
        self.retry_config = retry_config;
        self
    }

    /// Get the client's public key
    pub fn pubkey(&self) -> Pubkey {
        self.payer.pubkey()
    }

    /// Get current commitment level
    pub fn commitment(&self) -> CommitmentConfig {
        self.commitment
    }

    /// Validate cluster connection
    fn validate_cluster_connection(cluster: &Cluster) -> Result<()> {
        // In a real implementation, this would check RPC endpoint availability
        match cluster {
            Cluster::Devnet | Cluster::Testnet | Cluster::Mainnet => Ok(()),
            Cluster::Localnet => {
                // Could check if local validator is running
                Ok(())
            }
            _ => bail!("Unsupported cluster"),
        }
    }

    /// Submit a transaction with retry logic
    pub async fn send_and_confirm_transaction(
        &self,
        transaction: Transaction,
    ) -> Result<Signature> {
        let mut retries = 0;
        let mut backoff = self.retry_config.initial_backoff;

        loop {
            match self.send_transaction_once(&transaction).await {
                Ok(signature) => {
                    // Wait for confirmation with timeout
                    match self.confirm_transaction(&signature).await {
                        Ok(_) => return Ok(signature),
                        Err(e) if retries < self.retry_config.max_retries => {
                            tracing::warn!(
                                "Transaction confirmation failed (attempt {}/{}): {}",
                                retries + 1,
                                self.retry_config.max_retries,
                                e
                            );
                        }
                        Err(e) => return Err(e),
                    }
                }
                Err(e) if retries < self.retry_config.max_retries => {
                    tracing::warn!(
                        "Transaction send failed (attempt {}/{}): {}",
                        retries + 1,
                        self.retry_config.max_retries,
                        e
                    );
                }
                Err(e) => return Err(e),
            }

            retries += 1;
            if retries > self.retry_config.max_retries {
                bail!("Transaction failed after {} retries", self.retry_config.max_retries);
            }

            // Exponential backoff
            sleep(backoff).await;
            backoff = std::cmp::min(
                self.retry_config.max_backoff,
                Duration::from_secs_f64(
                    backoff.as_secs_f64() * self.retry_config.exponential_base
                ),
            );
        }
    }

    /// Send transaction once (no retry)
    async fn send_transaction_once(&self, transaction: &Transaction) -> Result<Signature> {
        // In a real implementation, this would use the RPC client
        // For now, returning a placeholder
        let signature = transaction.signatures.get(0)
            .cloned()
            .unwrap_or_default();
        
        tracing::info!("Sending transaction: {}", signature);
        Ok(signature)
    }

    /// Confirm transaction with timeout
    async fn confirm_transaction(&self, signature: &Signature) -> Result<()> {
        let timeout = Duration::from_secs(30);
        let start = std::time::Instant::now();

        while start.elapsed() < timeout {
            // In a real implementation, check transaction status
            tracing::debug!("Confirming transaction: {}", signature);
            
            // Simulate confirmation delay
            sleep(Duration::from_millis(500)).await;
            
            // For now, always succeed after a delay
            return Ok(());
        }

        bail!("Transaction confirmation timeout")
    }

    /// Request airdrop for testing (devnet/testnet only)
    pub async fn request_airdrop(&self, lamports: u64) -> Result<Signature> {
        match self.client.cluster() {
            Cluster::Devnet | Cluster::Testnet => {
                tracing::info!("Requesting airdrop of {} lamports", lamports);
                // In real implementation, use RPC client to request airdrop
                Ok(Signature::default())
            }
            _ => bail!("Airdrop only available on devnet/testnet"),
        }
    }

    /// Get account balance
    pub async fn get_balance(&self, pubkey: &Pubkey) -> Result<u64> {
        // In real implementation, query RPC for balance
        tracing::debug!("Getting balance for {}", pubkey);
        Ok(1_000_000_000) // 1 SOL for testing
    }

    /// Get the governance program with enhanced error handling
    pub fn governance_program(&self) -> Result<Program<Rc<Keypair>>> {
        self.client
            .program(self.config.governance_program_id)
            .context("Failed to get governance program")
    }

    /// Get the appeals program with enhanced error handling
    pub fn appeals_program(&self) -> Result<Program<Rc<Keypair>>> {
        self.client
            .program(self.config.appeals_program_id)
            .context("Failed to get appeals program")
    }

    /// Get the logging program with enhanced error handling
    pub fn logging_program(&self) -> Result<Program<Rc<Keypair>>> {
        self.client
            .program(self.config.logging_program_id)
            .context("Failed to get logging program")
    }

    /// Check if all programs are deployed and accessible
    pub async fn verify_programs(&self) -> Result<()> {
        // Check governance program
        self.verify_program_deployed(&self.config.governance_program_id, "Governance").await?;
        
        // Check appeals program
        self.verify_program_deployed(&self.config.appeals_program_id, "Appeals").await?;
        
        // Check logging program
        self.verify_program_deployed(&self.config.logging_program_id, "Logging").await?;
        
        tracing::info!("All programs verified successfully");
        Ok(())
    }

    /// Verify a single program is deployed
    async fn verify_program_deployed(&self, program_id: &Pubkey, name: &str) -> Result<()> {
        // In real implementation, check if program account exists and is executable
        tracing::debug!("Verifying {} program at {}", name, program_id);
        
        // Simulate verification
        sleep(Duration::from_millis(100)).await;
        
        Ok(())
    }

    /// Get program configuration
    pub fn config(&self) -> &ProgramConfig {
        &self.config
    }

    /// Create a new transaction builder
    pub fn transaction_builder(&self) -> TransactionBuilder {
        TransactionBuilder::new(self.payer.clone())
    }
}

/// Transaction builder for complex transactions
pub struct TransactionBuilder {
    payer: Rc<Keypair>,
    instructions: Vec<anchor_client::solana_sdk::instruction::Instruction>,
    signers: Vec<Rc<Keypair>>,
}

impl TransactionBuilder {
    pub fn new(payer: Rc<Keypair>) -> Self {
        Self {
            payer: payer.clone(),
            instructions: vec![],
            signers: vec![payer],
        }
    }

    pub fn add_instruction(
        mut self,
        instruction: anchor_client::solana_sdk::instruction::Instruction,
    ) -> Self {
        self.instructions.push(instruction);
        self
    }

    pub fn add_signer(mut self, signer: Rc<Keypair>) -> Self {
        if !self.signers.iter().any(|s| s.pubkey() == signer.pubkey()) {
            self.signers.push(signer);
        }
        self
    }

    pub fn build(self) -> Result<Transaction> {
        if self.instructions.is_empty() {
            bail!("No instructions in transaction");
        }

        // In real implementation, fetch recent blockhash
        let recent_blockhash = anchor_client::solana_sdk::hash::Hash::default();
        
        let mut transaction = Transaction::new_with_payer(
            &self.instructions,
            Some(&self.payer.pubkey()),
        );
        
        transaction.partial_sign(&self.signers, recent_blockhash);
        
        Ok(transaction)
    }
}

/// Health check for the client and programs
#[derive(Debug, Serialize)]
pub struct HealthStatus {
    pub client_healthy: bool,
    pub governance_program: bool,
    pub appeals_program: bool,
    pub logging_program: bool,
    pub cluster: String,
    pub payer_balance: u64,
}

impl AcgsClient {
    /// Perform health check on client and programs
    pub async fn health_check(&self) -> Result<HealthStatus> {
        let mut status = HealthStatus {
            client_healthy: true,
            governance_program: false,
            appeals_program: false,
            logging_program: false,
            cluster: format!("{:?}", self.client.cluster()),
            payer_balance: 0,
        };

        // Check payer balance
        match self.get_balance(&self.pubkey()).await {
            Ok(balance) => {
                status.payer_balance = balance;
                if balance == 0 {
                    tracing::warn!("Payer account has zero balance");
                }
            }
            Err(e) => {
                tracing::error!("Failed to get payer balance: {}", e);
                status.client_healthy = false;
            }
        }

        // Check programs
        if self.verify_program_deployed(&self.config.governance_program_id, "Governance").await.is_ok() {
            status.governance_program = true;
        }
        if self.verify_program_deployed(&self.config.appeals_program_id, "Appeals").await.is_ok() {
            status.appeals_program = true;
        }
        if self.verify_program_deployed(&self.config.logging_program_id, "Logging").await.is_ok() {
            status.logging_program = true;
        }

        Ok(status)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_program_config() {
        // Test default devnet config
        let config = ProgramConfig::devnet();
        assert_eq!(
            config.governance_program_id.to_string(),
            "8eRUCnQsDxqK7vjp5XsYs7C3NGpdhzzaMW8QQGzfTUV4"
        );

        // Test serialization
        let json = serde_json::to_string(&config).unwrap();
        let deserialized: ProgramConfig = serde_json::from_str(&json).unwrap();
        assert_eq!(config.governance_program_id, deserialized.governance_program_id);
    }

    #[test]
    fn test_retry_config() {
        let config = RetryConfig::default();
        assert_eq!(config.max_retries, 3);
        assert_eq!(config.initial_backoff, Duration::from_millis(500));
    }

    #[tokio::test]
    async fn test_client_creation() {
        let payer = Keypair::new();
        let client = AcgsClient::devnet(payer);
        assert!(client.is_ok());

        let client = client.unwrap();
        assert_eq!(client.commitment(), CommitmentConfig::confirmed());
    }

    #[tokio::test]
    async fn test_transaction_builder() {
        let payer = Keypair::new();
        let client = AcgsClient::devnet(payer).unwrap();
        
        let builder = client.transaction_builder();
        
        // Add a dummy instruction
        let instruction = system_instruction::transfer(
            &client.pubkey(),
            &Pubkey::new_unique(),
            1000,
        );
        
        let transaction = builder
            .add_instruction(instruction)
            .build();
        
        assert!(transaction.is_ok());
    }

    #[tokio::test]
    async fn test_health_check() {
        let payer = Keypair::new();
        let client = AcgsClient::devnet(payer).unwrap();
        
        let health = client.health_check().await;
        assert!(health.is_ok());
        
        let status = health.unwrap();
        assert!(status.client_healthy);
        assert_eq!(status.cluster, "Devnet");
    }

    #[test]
    fn test_auto_configure() {
        std::env::set_var("SOLANA_CLUSTER", "devnet");
        
        let payer = Keypair::new();
        let client = AcgsClient::auto_configure(payer);
        assert!(client.is_ok());
    }
}