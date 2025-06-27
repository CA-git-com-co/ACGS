//! Quantumagi Key Management Tool - Rust Implementation
//! Secure key generation, backup, and authority management for Solana programs
//! Replaces blockchain/scripts/key_management.sh with native Rust implementation

use anchor_client::solana_sdk::signature::{Keypair, Signer};
use anyhow::{Result, Context};
use clap::{Parser, Subcommand};
use colored::*;
use serde::{Deserialize, Serialize};
use std::{
    collections::HashMap,
    fs,
    path::{Path, PathBuf},
    time::{SystemTime, UNIX_EPOCH},
};

#[derive(Parser)]
#[command(name = "key_management")]
#[command(about = "Quantumagi key management and validation tool")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Initialize key directories
    Init,
    /// Generate program upgrade authority keys
    GenerateProgram,
    /// Generate governance authority keys
    GenerateGovernance,
    /// Generate multi-signature setup
    GenerateMultisig,
    /// Display key information
    Info,
    /// Transfer program authority
    TransferAuthority {
        /// Program ID to transfer authority for
        program_id: String,
        /// Path to new authority keypair
        new_authority: String,
        /// Path to current authority keypair
        current_authority: String,
    },
    /// Revoke program authority (make immutable)
    RevokeAuthority {
        /// Program ID to revoke authority for
        program_id: String,
        /// Path to current authority keypair
        current_authority: String,
    },
    /// Audit key security
    Audit,
    /// Generate specific keypair
    Generate {
        /// Name of the keypair
        name: String,
        /// Purpose/description of the keypair
        #[arg(short, long)]
        purpose: Option<String>,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct KeyInfo {
    name: String,
    purpose: String,
    public_key: String,
    file_path: String,
    created_at: u64,
    last_used: Option<u64>,
}

#[derive(Debug, Serialize, Deserialize)]
struct KeyRegistry {
    keys: HashMap<String, KeyInfo>,
    created_at: u64,
    last_updated: u64,
}

pub struct KeyManager {
    keys_dir: PathBuf,
    backup_dir: PathBuf,
    registry_file: PathBuf,
}

impl KeyManager {
    pub fn new() -> Result<Self> {
        let project_root = Path::new(env!("CARGO_MANIFEST_DIR")).parent()
            .context("Could not determine project root")?;
        
        let keys_dir = project_root.join("keys");
        let backup_dir = keys_dir.join("backups");
        let registry_file = keys_dir.join("key_registry.json");

        Ok(Self {
            keys_dir,
            backup_dir,
            registry_file,
        })
    }

    pub fn init_directories(&self) -> Result<()> {
        println!("{} Initializing key directories...", "🔧".blue());

        // Create directories with secure permissions
        fs::create_dir_all(&self.keys_dir)?;
        fs::create_dir_all(&self.backup_dir)?;

        // Set secure permissions (Unix only)
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let permissions = fs::Permissions::from_mode(0o700);
            fs::set_permissions(&self.keys_dir, permissions.clone())?;
            fs::set_permissions(&self.backup_dir, permissions)?;
        }

        // Initialize registry if it doesn't exist
        if !self.registry_file.exists() {
            let registry = KeyRegistry {
                keys: HashMap::new(),
                created_at: SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs(),
                last_updated: SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs(),
            };
            self.save_registry(&registry)?;
        }

        println!("{} Key directories initialized:", "✅".green());
        println!("   Keys directory: {}", self.keys_dir.display());
        println!("   Backup directory: {}", self.backup_dir.display());
        println!("   Registry file: {}", self.registry_file.display());

        Ok(())
    }

    pub fn generate_keypair(&self, name: &str, purpose: Option<&str>) -> Result<KeyInfo> {
        let purpose = purpose.unwrap_or("General purpose keypair");
        let key_path = self.keys_dir.join(format!("{}-keypair.json", name));

        // Check if key already exists
        if key_path.exists() {
            println!("{} Key {} already exists at {}", "⚠️".yellow(), name, key_path.display());
            print!("Overwrite? (y/N): ");
            use std::io::{self, Write};
            io::stdout().flush()?;
            
            let mut input = String::new();
            io::stdin().read_line(&mut input)?;
            
            if !input.trim().to_lowercase().starts_with('y') {
                println!("Key generation cancelled");
                return Err(anyhow::anyhow!("Key generation cancelled by user"));
            }

            // Backup existing key
            self.backup_key(name)?;
        }

        println!("{} Generating new keypair: {}", "🔑".blue(), name);

        // Generate new keypair
        let keypair = Keypair::new();
        let public_key = keypair.pubkey();

        // Save keypair to file
        let keypair_bytes = keypair.to_bytes();
        let keypair_json = serde_json::to_string(&keypair_bytes.to_vec())?;
        fs::write(&key_path, keypair_json)?;

        // Set secure permissions
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let permissions = fs::Permissions::from_mode(0o600);
            fs::set_permissions(&key_path, permissions)?;
        }

        let key_info = KeyInfo {
            name: name.to_string(),
            purpose: purpose.to_string(),
            public_key: public_key.to_string(),
            file_path: key_path.to_string_lossy().to_string(),
            created_at: SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs(),
            last_used: None,
        };

        // Update registry
        let mut registry = self.load_registry()?;
        registry.keys.insert(name.to_string(), key_info.clone());
        registry.last_updated = SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs();
        self.save_registry(&registry)?;

        println!("{} Keypair generated successfully:", "✅".green());
        println!("   Name: {}", name);
        println!("   Purpose: {}", purpose);
        println!("   Public Key: {}", public_key);
        println!("   Private Key: {}", key_path.display());

        // Log key generation
        self.log_key_operation(&format!("Generated keypair {} ({}) - {}", name, purpose, public_key))?;

        Ok(key_info)
    }

    pub fn backup_key(&self, name: &str) -> Result<()> {
        let key_path = self.keys_dir.join(format!("{}-keypair.json", name));
        
        if key_path.exists() {
            let timestamp = SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs();
            let backup_path = self.backup_dir.join(format!("{}-keypair-{}.json", name, timestamp));
            
            fs::copy(&key_path, &backup_path)?;
            
            #[cfg(unix)]
            {
                use std::os::unix::fs::PermissionsExt;
                let permissions = fs::Permissions::from_mode(0o600);
                fs::set_permissions(&backup_path, permissions)?;
            }
            
            println!("{} Key backed up to {}", "✅".green(), backup_path.display());
        }
        
        Ok(())
    }

    pub fn generate_program_authorities(&self) -> Result<()> {
        println!("{} Generating program upgrade authority keys...", "🏛️".blue());
        
        self.generate_keypair("quantumagi-upgrade-authority", Some("Quantumagi Core program upgrade authority"))?;
        self.generate_keypair("appeals-upgrade-authority", Some("Appeals program upgrade authority"))?;
        self.generate_keypair("logging-upgrade-authority", Some("Logging program upgrade authority"))?;
        
        println!("{} All program upgrade authority keys generated", "✅".green());
        Ok(())
    }

    pub fn generate_governance_authorities(&self) -> Result<()> {
        println!("{} Generating governance authority keys...", "🏛️".blue());
        
        self.generate_keypair("governance-authority", Some("Main governance authority for constitutional changes"))?;
        self.generate_keypair("emergency-authority", Some("Emergency governance authority for critical situations"))?;
        self.generate_keypair("treasury-authority", Some("Treasury management authority"))?;
        
        println!("{} All governance authority keys generated", "✅".green());
        Ok(())
    }

    pub fn generate_multisig_setup(&self) -> Result<()> {
        println!("{} Generating multi-signature setup...", "🔐".blue());
        
        // Generate individual signer keys
        for i in 1..=3 {
            self.generate_keypair(
                &format!("multisig-signer-{}", i),
                Some(&format!("Multi-signature signer {} for constitutional changes", i))
            )?;
        }
        
        println!("{} Multi-signature setup requires manual configuration:", "📋".yellow());
        println!("   Use the generated signer keys to create a multi-signature account");
        println!("   Recommended threshold: 2 of 3 signers for constitutional changes");
        
        Ok(())
    }

    fn load_registry(&self) -> Result<KeyRegistry> {
        if self.registry_file.exists() {
            let content = fs::read_to_string(&self.registry_file)?;
            Ok(serde_json::from_str(&content)?)
        } else {
            Ok(KeyRegistry {
                keys: HashMap::new(),
                created_at: SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs(),
                last_updated: SystemTime::now().duration_since(UNIX_EPOCH)?.as_secs(),
            })
        }
    }

    fn save_registry(&self, registry: &KeyRegistry) -> Result<()> {
        let content = serde_json::to_string_pretty(registry)?;
        fs::write(&self.registry_file, content)?;
        Ok(())
    }

    fn log_key_operation(&self, message: &str) -> Result<()> {
        let log_file = self.keys_dir.join("key_operations.log");
        let timestamp = chrono::Utc::now().format("%Y-%m-%d %H:%M:%S UTC");
        let log_entry = format!("{}: {}\n", timestamp, message);
        
        use std::fs::OpenOptions;
        use std::io::Write;
        
        let mut file = OpenOptions::new()
            .create(true)
            .append(true)
            .open(log_file)?;
        file.write_all(log_entry.as_bytes())?;
        
        Ok(())
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();
    let key_manager = KeyManager::new()?;

    match cli.command {
        Commands::Init => {
            key_manager.init_directories()?;
        }
        Commands::GenerateProgram => {
            key_manager.generate_program_authorities()?;
        }
        Commands::GenerateGovernance => {
            key_manager.generate_governance_authorities()?;
        }
        Commands::GenerateMultisig => {
            key_manager.generate_multisig_setup()?;
        }
        Commands::Generate { name, purpose } => {
            key_manager.generate_keypair(&name, purpose.as_deref())?;
        }
        Commands::Info => {
            // Implementation for displaying key info will be added
            println!("{} Key information display not yet implemented", "⚠️".yellow());
        }
        Commands::TransferAuthority { program_id: _, new_authority: _, current_authority: _ } => {
            // Implementation for authority transfer will be added
            println!("{} Authority transfer not yet implemented", "⚠️".yellow());
        }
        Commands::RevokeAuthority { program_id: _, current_authority: _ } => {
            // Implementation for authority revocation will be added
            println!("{} Authority revocation not yet implemented", "⚠️".yellow());
        }
        Commands::Audit => {
            // Implementation for security audit will be added
            println!("{} Security audit not yet implemented", "⚠️".yellow());
        }
    }

    Ok(())
}
