# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# Quantumagi Solana Devnet Deployment Script
# Complete deployment of constitutional governance system to Solana devnet

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SOLANA_CLUSTER="devnet"
ANCHOR_PROVIDER_URL="https://api.devnet.solana.com"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEPLOYMENT_LOG="$PROJECT_ROOT/deployment_$(date +%Y%m%d_%H%M%S).log"

echo -e "${BLUE}🚀 Quantumagi Solana Devnet Deployment${NC}"
echo "======================================"
echo "Project Root: $PROJECT_ROOT"
echo "Deployment Log: $DEPLOYMENT_LOG"
echo ""

# Logging function
log() {
    echo -e "$1" | tee -a "$DEPLOYMENT_LOG"
}

log_success() {
    log "${GREEN}[SUCCESS]${NC} $1"
}

log_info() {
    log "${BLUE}[INFO]${NC} $1"
}

log_warning() {
    log "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    log "${RED}[ERROR]${NC} $1"
}

# Error handling
handle_error() {
    log_error "Deployment failed at step: $1"
    log_error "Check the deployment log for details: $DEPLOYMENT_LOG"
    exit 1
}

# Pre-deployment checks
pre_deployment_checks() {
    log_info "Running pre-deployment checks..."
    
    # Check if we're in the right directory
    if [ ! -f "$PROJECT_ROOT/Anchor.toml" ]; then
        handle_error "Anchor.toml not found. Please run from quantumagi_core directory"
    fi
    
    # Check Anchor CLI
    if ! command -v anchor &> /dev/null; then
        handle_error "Anchor CLI not found. Please install Anchor CLI first"
    fi
    
    log_success "Anchor CLI found: $(anchor --version)"
    
    # Check Solana CLI
    if ! command -v solana &> /dev/null; then
        log_warning "Solana CLI not found. Attempting installation..."
        bash "$PROJECT_ROOT/scripts/install_solana_cli.sh" || handle_error "Solana CLI installation failed"
    fi
    
    log_success "Solana CLI found: $(solana --version)"
    
    # Check Node.js dependencies
    if [ ! -d "$PROJECT_ROOT/node_modules" ]; then
        log_info "Installing Node.js dependencies..."
        cd "$PROJECT_ROOT"
        npm install || handle_error "npm install failed"
    fi
    
    log_success "Pre-deployment checks completed"
}

# Configure Solana for devnet
configure_solana() {
    log_info "Configuring Solana for devnet deployment..."
    
    # Set cluster to devnet
    solana config set --url "$ANCHOR_PROVIDER_URL" || handle_error "Failed to set Solana cluster"
    
    # Check if keypair exists
    if [ ! -f ~/.config/solana/id.json ]; then
        log_info "Generating new keypair..."
        solana-keygen new --outfile ~/.config/solana/id.json --no-bip39-passphrase || handle_error "Keypair generation failed"
    fi
    
    # Get wallet address
    WALLET_ADDRESS=$(solana address)
    log_success "Wallet configured: $WALLET_ADDRESS"
    
    # Check balance
    BALANCE=$(solana balance --lamports | grep -o '[0-9]*' | head -1)
    log_info "Current balance: $BALANCE lamports"

    # Request airdrop if balance is low
    if [ "$BALANCE" -lt 1000000000 ]; then  # Less than 1 SOL
        log_info "Requesting devnet airdrop..."
        solana airdrop 2 || log_warning "Airdrop failed - you may need to request manually"
        sleep 5
        BALANCE=$(solana balance --lamports | grep -o '[0-9]*' | head -1)
        log_info "New balance: $BALANCE lamports"
    fi
    
    log_success "Solana configuration completed"
}

# Build the programs
build_programs() {
    log_info "Building Solana programs..."
    
    cd "$PROJECT_ROOT"
    
    # Clean previous builds
    anchor clean || log_warning "Clean failed (this is normal for first build)"
    
    # Build all programs
    anchor build || handle_error "Anchor build failed"
    
    log_success "Programs built successfully"
    
    # List built programs
    log_info "Built programs:"
    find target/deploy -name "*.so" -exec basename {} \; | tee -a "$DEPLOYMENT_LOG"
}

# Deploy programs to devnet
deploy_programs() {
    log_info "Deploying programs to Solana devnet..."
    
    cd "$PROJECT_ROOT"
    
    # Update Anchor.toml for devnet
    log_info "Updating Anchor.toml for devnet deployment..."
    
    # Backup original Anchor.toml
    cp Anchor.toml Anchor.toml.backup
    
    # Update cluster configuration
    sed -i 's/cluster = "Localnet"/cluster = "Devnet"/' Anchor.toml || handle_error "Failed to update Anchor.toml"
    
    # Deploy to devnet
    anchor deploy --provider.cluster devnet --provider.wallet ~/.config/solana/id.json || handle_error "Deployment failed"
    
    log_success "Programs deployed to devnet successfully"
    
    # Extract program IDs
    log_info "Extracting deployed program IDs..."
    
    # Get program IDs from deployment output
    QUANTUMAGI_PROGRAM_ID=$(anchor keys list | grep "quantumagi_core" | awk '{print $2}' || echo "")
    APPEALS_PROGRAM_ID=$(anchor keys list | grep "appeals" | awk '{print $2}' || echo "")
    LOGGING_PROGRAM_ID=$(anchor keys list | grep "logging" | awk '{print $2}' || echo "")
    
    log_success "Program IDs extracted:"
    log_info "  Quantumagi Core: $QUANTUMAGI_PROGRAM_ID"
    log_info "  Appeals: $APPEALS_PROGRAM_ID"
    log_info "  Logging: $LOGGING_PROGRAM_ID"
    
    # Save program IDs to file
    cat > "$PROJECT_ROOT/devnet_program_ids.json" << EOF
{
  "cluster": "devnet",
  "deployment_date": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "wallet_address": "$WALLET_ADDRESS",
  "programs": {
    "quantumagi_core": "$QUANTUMAGI_PROGRAM_ID",
    "appeals": "$APPEALS_PROGRAM_ID",
    "logging": "$LOGGING_PROGRAM_ID"
  }
}
EOF
    
    log_success "Program IDs saved to devnet_program_ids.json"
}

# Initialize the constitution on-chain
initialize_constitution() {
    log_info "Initializing constitution on Solana devnet..."
    
    cd "$PROJECT_ROOT"
    
    # Run the initialization script
    if [ -f "scripts/initialize_constitution.py" ]; then
        python3 scripts/initialize_constitution.py --cluster devnet || handle_error "Constitution initialization failed"
    else
        log_warning "Constitution initialization script not found, skipping..."
    fi
    
    log_success "Constitution initialized on devnet"
}

# Run end-to-end tests on devnet
run_devnet_tests() {
    log_info "Running end-to-end tests on devnet..."

    cd "$PROJECT_ROOT"

    # Update test configuration for devnet
    export ANCHOR_PROVIDER_URL="$ANCHOR_PROVIDER_URL"
    export ANCHOR_WALLET="$HOME/.config/solana/id.json"

    # Run comprehensive devnet validation
    if [ -f "scripts/validate_devnet_deployment.py" ]; then
        log_info "Running devnet validation script..."
        python3 scripts/validate_devnet_deployment.py --cluster devnet || handle_error "Devnet validation failed"
    fi

    # Run Anchor tests against devnet
    log_info "Running Anchor tests against devnet..."
    anchor test --skip-local-validator --provider.cluster devnet || handle_error "Devnet tests failed"

    log_success "Devnet tests completed successfully"
}

# Generate deployment report
generate_deployment_report() {
    log_info "Generating deployment report..."
    
    REPORT_FILE="$PROJECT_ROOT/devnet_deployment_report_$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$REPORT_FILE" << EOF
{
  "deployment_summary": {
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "cluster": "$SOLANA_CLUSTER",
    "status": "successful",
    "wallet_address": "$WALLET_ADDRESS",
    "deployment_log": "$DEPLOYMENT_LOG"
  },
  "programs": {
    "quantumagi_core": {
      "program_id": "$QUANTUMAGI_PROGRAM_ID",
      "status": "deployed",
      "features": ["constitution_management", "policy_governance", "compliance_checking"]
    },
    "appeals": {
      "program_id": "$APPEALS_PROGRAM_ID", 
      "status": "deployed",
      "features": ["appeal_submission", "review_process", "resolution_tracking"]
    },
    "logging": {
      "program_id": "$LOGGING_PROGRAM_ID",
      "status": "deployed", 
      "features": ["governance_events", "audit_trail", "compliance_logs"]
    }
  },
  "next_steps": [
    "Test governance workflows using client libraries",
    "Integrate with frontend applications",
    "Monitor program performance and costs",
    "Prepare for mainnet deployment"
  ],
  "resources": {
    "solana_explorer": "https://explorer.solana.com/?cluster=devnet",
    "program_explorer": "https://explorer.solana.com/address/$QUANTUMAGI_PROGRAM_ID?cluster=devnet",
    "documentation": "./docs/",
    "client_examples": "./client/"
  }
}
EOF
    
    log_success "Deployment report generated: $REPORT_FILE"
}

# Main deployment function
main() {
    log_info "Starting Quantumagi devnet deployment..."
    
    # Execute deployment steps
    pre_deployment_checks
    configure_solana
    build_programs
    deploy_programs
    initialize_constitution
    run_devnet_tests
    generate_deployment_report
    
    log_success "🎉 Quantumagi successfully deployed to Solana devnet!"
    log_info ""
    log_info "Deployment Summary:"
    log_info "  Cluster: $SOLANA_CLUSTER"
    log_info "  Wallet: $WALLET_ADDRESS"
    log_info "  Quantumagi Core: $QUANTUMAGI_PROGRAM_ID"
    log_info "  Appeals Program: $APPEALS_PROGRAM_ID"
    log_info "  Logging Program: $LOGGING_PROGRAM_ID"
    log_info ""
    log_info "Next Steps:"
    log_info "  1. View programs on Solana Explorer: https://explorer.solana.com/?cluster=devnet"
    log_info "  2. Test governance workflows: python3 client/solana_client.py"
    log_info "  3. Review deployment report: $(basename "$REPORT_FILE")"
    log_info ""
    log_info "Full deployment log: $DEPLOYMENT_LOG"
}

# Execute main function
main "$@"
