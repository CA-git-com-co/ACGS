//! Quantumagi Program ID Generator - Rust Implementation
//! Generate valid Solana program IDs for Quantumagi programs
//! Replaces blockchain/scripts/generate_program_ids.py with native Rust implementation

use anchor_client::solana_sdk::pubkey::Pubkey;
use anyhow::Result;
use clap::{Parser, Subcommand};
use colored::*;
use serde::{Deserialize, Serialize};
use sha2::{Sha256, Digest};
use std::{
    collections::HashMap,
    fs,
    path::{Path, PathBuf},
    str::FromStr,
};

#[derive(Parser)]
#[command(name = "generate_program_ids")]
#[command(about = "Generate valid Solana program IDs for Quantumagi programs")]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Generate program ID for a specific program
    Generate {
        /// Name of the program
        program_name: String,
        /// Optional seed for deterministic generation
        #[arg(short, long)]
        seed: Option<String>,
    },
    /// Generate all standard Quantumagi program IDs
    GenerateAll,
    /// List all generated program IDs
    List,
    /// Validate a program ID
    Validate {
        /// Program ID to validate
        program_id: String,
    },
    /// Export program IDs to various formats
    Export {
        /// Output format
        #[arg(short, long, default_value = "json")]
        format: ExportFormat,
        /// Output file path
        #[arg(short, long)]
        output: Option<String>,
    },
}

#[derive(Debug, Clone, clap::ValueEnum)]
enum ExportFormat {
    Json,
    Toml,
    Env,
    Rust,
    TypeScript,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct ProgramIdInfo {
    name: String,
    program_id: String,
    seed: String,
    description: String,
    generated_at: u64,
}

#[derive(Debug, Serialize, Deserialize)]
struct ProgramIdRegistry {
    programs: HashMap<String, ProgramIdInfo>,
    created_at: u64,
    last_updated: u64,
}

pub struct ProgramIdGenerator {
    registry_file: PathBuf,
}

impl ProgramIdGenerator {
    pub fn new() -> Result<Self> {
        let project_root = Path::new(env!("CARGO_MANIFEST_DIR")).parent()
            .ok_or_else(|| anyhow::anyhow!("Could not determine project root"))?;
        
        let registry_file = project_root.join("program_ids.json");

        Ok(Self {
            registry_file,
        })
    }

    pub fn generate_program_id(&self, program_name: &str, seed: Option<&str>) -> Result<ProgramIdInfo> {
        println!("{} Generating program ID for: {}", "🔧".blue(), program_name);

        // Create deterministic seed
        let default_seed = format!("quantumagi_{}", program_name);
        let seed_string = seed.unwrap_or(&default_seed);
        
        // Generate program ID using SHA-256 hash
        let mut hasher = Sha256::new();
        hasher.update(seed_string.as_bytes());
        let hash_bytes = hasher.finalize();

        // Convert to Pubkey (this is a simplified approach)
        // In practice, you might want to use a more sophisticated method
        let program_id = Pubkey::new_from_array(hash_bytes.into());

        let program_info = ProgramIdInfo {
            name: program_name.to_string(),
            program_id: program_id.to_string(),
            seed: seed_string.to_string(),
            description: format!("Quantumagi {} program", program_name),
            generated_at: std::time::SystemTime::now()
                .duration_since(std::time::UNIX_EPOCH)?
                .as_secs(),
        };

        println!("{} Generated program ID:", "✅".green());
        println!("   Name: {}", program_info.name);
        println!("   Program ID: {}", program_info.program_id);
        println!("   Seed: {}", program_info.seed);

        // Update registry
        let mut registry = self.load_registry()?;
        registry.programs.insert(program_name.to_string(), program_info.clone());
        registry.last_updated = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)?
            .as_secs();
        self.save_registry(&registry)?;

        Ok(program_info)
    }

    pub fn generate_all_standard_programs(&self) -> Result<Vec<ProgramIdInfo>> {
        println!("{} Generating all standard Quantumagi program IDs...", "🏭".blue());

        let standard_programs = vec![
            ("quantumagi_core", "Core governance and constitutional framework"),
            ("appeals", "Appeals and dispute resolution system"),
            ("logging", "Governance action logging and audit trail"),
            ("treasury", "Treasury management and financial operations"),
            ("voting", "Voting mechanism and ballot management"),
            ("policy_engine", "Policy creation and enforcement engine"),
        ];

        let mut generated_programs = Vec::new();

        for (program_name, description) in standard_programs {
            let mut program_info = self.generate_program_id(program_name, None)?;
            program_info.description = description.to_string();
            generated_programs.push(program_info);
        }

        println!("{} Generated {} standard program IDs", "✅".green(), generated_programs.len());

        Ok(generated_programs)
    }

    pub fn list_program_ids(&self) -> Result<()> {
        println!("{} Listing all generated program IDs:", "📋".blue());

        let registry = self.load_registry()?;

        if registry.programs.is_empty() {
            println!("   No program IDs found. Use 'generate-all' to create standard program IDs.");
            return Ok(());
        }

        for (name, info) in &registry.programs {
            println!("   {} {}", "•".cyan(), name);
            println!("     Program ID: {}", info.program_id);
            println!("     Description: {}", info.description);
            println!("     Generated: {}", chrono::DateTime::from_timestamp(info.generated_at as i64, 0)
                .map(|dt| dt.format("%Y-%m-%d %H:%M:%S UTC").to_string())
                .unwrap_or_else(|| "Unknown".to_string()));
            println!();
        }

        Ok(())
    }

    pub fn validate_program_id(&self, program_id: &str) -> Result<()> {
        println!("{} Validating program ID: {}", "🔍".blue(), program_id);

        match Pubkey::from_str(program_id) {
            Ok(pubkey) => {
                println!("{} Program ID is valid:", "✅".green());
                println!("   Program ID: {}", pubkey);
                println!("   Base58 format: Valid");
                println!("   Length: 32 bytes");
                
                // Check if it's in our registry
                let registry = self.load_registry()?;
                if let Some((name, info)) = registry.programs.iter()
                    .find(|(_, info)| info.program_id == program_id) {
                    println!("   Registry: Found as '{}'", name);
                    println!("   Description: {}", info.description);
                } else {
                    println!("   Registry: Not found in local registry");
                }
            }
            Err(e) => {
                println!("{} Program ID is invalid:", "❌".red());
                println!("   Error: {}", e);
                println!("   Expected: 32-byte base58 encoded string");
            }
        }

        Ok(())
    }

    pub fn export_program_ids(&self, format: ExportFormat, output_path: Option<&str>) -> Result<()> {
        println!("{} Exporting program IDs in {:?} format...", "📤".blue(), format);

        let registry = self.load_registry()?;

        if registry.programs.is_empty() {
            println!("   No program IDs to export. Generate some first.");
            return Ok(());
        }

        let content = match format {
            ExportFormat::Json => {
                serde_json::to_string_pretty(&registry.programs)?
            }
            ExportFormat::Toml => {
                toml::to_string_pretty(&registry.programs)?
            }
            ExportFormat::Env => {
                let mut env_content = String::new();
                env_content.push_str("# Quantumagi Program IDs\n");
                for (name, info) in &registry.programs {
                    env_content.push_str(&format!(
                        "{}={}\n",
                        name.to_uppercase().replace('-', "_") + "_PROGRAM_ID",
                        info.program_id
                    ));
                }
                env_content
            }
            ExportFormat::Rust => {
                let mut rust_content = String::new();
                rust_content.push_str("// Quantumagi Program IDs\n");
                rust_content.push_str("use anchor_client::solana_sdk::pubkey::Pubkey;\n\n");
                for (name, info) in &registry.programs {
                    rust_content.push_str(&format!(
                        "pub const {}_PROGRAM_ID: Pubkey = solana_program::pubkey!(\"{}\");\n",
                        name.to_uppercase().replace('-', "_"),
                        info.program_id
                    ));
                }
                rust_content
            }
            ExportFormat::TypeScript => {
                let mut ts_content = String::new();
                ts_content.push_str("// Quantumagi Program IDs\n");
                ts_content.push_str("import { PublicKey } from '@solana/web3.js';\n\n");
                for (name, info) in &registry.programs {
                    ts_content.push_str(&format!(
                        "export const {}_PROGRAM_ID = new PublicKey('{}');\n",
                        name.to_uppercase().replace('-', "_"),
                        info.program_id
                    ));
                }
                ts_content
            }
        };

        let output_file = if let Some(path) = output_path {
            PathBuf::from(path)
        } else {
            let extension = match format {
                ExportFormat::Json => "json",
                ExportFormat::Toml => "toml",
                ExportFormat::Env => "env",
                ExportFormat::Rust => "rs",
                ExportFormat::TypeScript => "ts",
            };
            self.registry_file.parent().unwrap().join(format!("program_ids.{}", extension))
        };

        fs::write(&output_file, content)?;

        println!("{} Program IDs exported to: {}", "✅".green(), output_file.display());

        Ok(())
    }

    fn load_registry(&self) -> Result<ProgramIdRegistry> {
        if self.registry_file.exists() {
            let content = fs::read_to_string(&self.registry_file)?;
            Ok(serde_json::from_str(&content)?)
        } else {
            Ok(ProgramIdRegistry {
                programs: HashMap::new(),
                created_at: std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)?
                    .as_secs(),
                last_updated: std::time::SystemTime::now()
                    .duration_since(std::time::UNIX_EPOCH)?
                    .as_secs(),
            })
        }
    }

    fn save_registry(&self, registry: &ProgramIdRegistry) -> Result<()> {
        let content = serde_json::to_string_pretty(registry)?;
        fs::write(&self.registry_file, content)?;
        Ok(())
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    let cli = Cli::parse();
    let generator = ProgramIdGenerator::new()?;

    match cli.command {
        Commands::Generate { program_name, seed } => {
            generator.generate_program_id(&program_name, seed.as_deref())?;
        }
        Commands::GenerateAll => {
            generator.generate_all_standard_programs()?;
        }
        Commands::List => {
            generator.list_program_ids()?;
        }
        Commands::Validate { program_id } => {
            generator.validate_program_id(&program_id)?;
        }
        Commands::Export { format, output } => {
            generator.export_program_ids(format, output.as_deref())?;
        }
    }

    Ok(())
}
