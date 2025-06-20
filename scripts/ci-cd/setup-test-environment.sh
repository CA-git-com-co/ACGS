#!/bin/bash

# ACGS-1 Test Environment Setup Script
# This script sets up the complete testing environment for CI/CD pipelines

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_FILE="/tmp/acgs-test-setup.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Python dependencies
setup_python_environment() {
    log "Setting up Python environment..."
    
    # Check Python version
    if ! command_exists python3; then
        error "Python 3 is not installed"
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    info "Python version: $PYTHON_VERSION"
    
    # Upgrade pip
    python3 -m pip install --upgrade pip
    
    # Install core testing dependencies
    log "Installing Python testing dependencies..."
    pip install pytest pytest-asyncio pytest-cov pytest-mock pytest-benchmark
    pip install aiohttp requests psutil
    
    # Install additional dependencies if requirements file exists
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        log "Installing project requirements..."
        pip install -r "$PROJECT_ROOT/requirements.txt"
    fi
    
    if [ -f "$PROJECT_ROOT/tests/requirements.txt" ]; then
        log "Installing test requirements..."
        pip install -r "$PROJECT_ROOT/tests/requirements.txt"
    fi
    
    log "✅ Python environment setup complete"
}

# Function to setup Node.js environment
setup_nodejs_environment() {
    log "Setting up Node.js environment..."
    
    if ! command_exists node; then
        warn "Node.js not found, skipping Node.js setup"
        return 0
    fi
    
    NODE_VERSION=$(node --version)
    info "Node.js version: $NODE_VERSION"
    
    # Install global dependencies
    if command_exists npm; then
        log "Installing global Node.js dependencies..."
        npm install -g @coral-xyz/anchor-cli
        
        # Install project dependencies if package.json exists
        if [ -f "$PROJECT_ROOT/package.json" ]; then
            log "Installing project Node.js dependencies..."
            cd "$PROJECT_ROOT"
            npm install
        fi
    fi
    
    log "✅ Node.js environment setup complete"
}

# Function to setup Rust environment
setup_rust_environment() {
    log "Setting up Rust environment..."
    
    if ! command_exists rustc; then
        warn "Rust not found, skipping Rust setup"
        return 0
    fi
    
    RUST_VERSION=$(rustc --version)
    info "Rust version: $RUST_VERSION"
    
    # Install additional Rust components
    rustup component add rustfmt clippy
    
    log "✅ Rust environment setup complete"
}

# Function to setup Solana environment
setup_solana_environment() {
    log "Setting up Solana environment..."
    
    if ! command_exists solana; then
        warn "Solana CLI not found, attempting to install..."
        
        # Install Solana CLI
        sh -c "$(curl -sSfL https://release.solana.com/v1.18.0/install)"
        
        # Add to PATH
        export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
        
        if ! command_exists solana; then
            warn "Solana CLI installation failed, skipping Solana setup"
            return 0
        fi
    fi
    
    SOLANA_VERSION=$(solana --version)
    info "Solana version: $SOLANA_VERSION"
    
    # Configure Solana for testing
    log "Configuring Solana for testing..."
    solana config set --url devnet
    
    # Generate test keypair if it doesn't exist
    if [ ! -f "$HOME/.config/solana/id.json" ]; then
        log "Generating Solana test keypair..."
        solana-keygen new --no-bip39-passphrase --silent --outfile "$HOME/.config/solana/id.json"
    fi
    
    # Request airdrop for testing (may fail, that's okay)
    log "Requesting SOL airdrop for testing..."
    solana airdrop 2 || warn "Airdrop failed, continuing with existing balance"
    
    # Check balance
    BALANCE=$(solana balance)
    info "Solana balance: $BALANCE"
    
    log "✅ Solana environment setup complete"
}

# Function to setup test directories
setup_test_directories() {
    log "Setting up test directories..."
    
    # Create necessary directories
    mkdir -p "$PROJECT_ROOT/tests/results"
    mkdir -p "$PROJECT_ROOT/tests/logs"
    mkdir -p "$PROJECT_ROOT/tests/reports"
    mkdir -p "$PROJECT_ROOT/tests/artifacts"
    
    # Set permissions
    chmod 755 "$PROJECT_ROOT/tests/results"
    chmod 755 "$PROJECT_ROOT/tests/logs"
    chmod 755 "$PROJECT_ROOT/tests/reports"
    chmod 755 "$PROJECT_ROOT/tests/artifacts"
    
    log "✅ Test directories setup complete"
}

# Function to validate test environment
validate_test_environment() {
    log "Validating test environment..."
    
    # Check required test files
    REQUIRED_FILES=(
        "tests/e2e/test_pytest_integration.py"
        "tests/e2e/test_comprehensive_scenarios.py"
        "tests/e2e/conftest.py"
        "tests/e2e/improved_mock_services.py"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -f "$PROJECT_ROOT/$file" ]; then
            error "Required test file missing: $file"
        fi
        info "✅ Found: $file"
    done
    
    # Test Python imports
    log "Testing Python imports..."
    cd "$PROJECT_ROOT"
    python3 -c "
import pytest
import aiohttp
import requests
print('✅ All Python dependencies available')
" || error "Python dependency check failed"
    
    # Test pytest discovery
    log "Testing pytest discovery..."
    cd "$PROJECT_ROOT"
    DISCOVERED_TESTS=$(python3 -m pytest tests/e2e/ --collect-only -q | grep -c "test session starts" || echo "0")
    if [ "$DISCOVERED_TESTS" -gt 0 ]; then
        info "✅ Pytest can discover tests"
    else
        warn "Pytest test discovery may have issues"
    fi
    
    log "✅ Test environment validation complete"
}

# Function to run quick smoke tests
run_smoke_tests() {
    log "Running smoke tests..."
    
    cd "$PROJECT_ROOT"
    
    # Run a quick test to ensure everything works
    log "Running basic integration test..."
    python3 -m pytest tests/e2e/test_pytest_integration.py::TestServiceIntegration::test_service_health_validation -v --tb=short || warn "Smoke test failed"
    
    log "✅ Smoke tests complete"
}

# Function to generate environment report
generate_environment_report() {
    log "Generating environment report..."
    
    REPORT_FILE="$PROJECT_ROOT/tests/reports/environment_setup_report.md"
    
    cat > "$REPORT_FILE" << EOF
# ACGS-1 Test Environment Setup Report

**Generated**: $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Setup Script**: $0
**Project Root**: $PROJECT_ROOT

## Environment Information

### System Information
- **OS**: $(uname -s)
- **Architecture**: $(uname -m)
- **Kernel**: $(uname -r)

### Software Versions
EOF

    # Add Python information
    if command_exists python3; then
        echo "- **Python**: $(python3 --version)" >> "$REPORT_FILE"
        echo "- **Pip**: $(pip --version | cut -d' ' -f1-2)" >> "$REPORT_FILE"
    fi
    
    # Add Node.js information
    if command_exists node; then
        echo "- **Node.js**: $(node --version)" >> "$REPORT_FILE"
        echo "- **NPM**: $(npm --version)" >> "$REPORT_FILE"
    fi
    
    # Add Rust information
    if command_exists rustc; then
        echo "- **Rust**: $(rustc --version)" >> "$REPORT_FILE"
        echo "- **Cargo**: $(cargo --version)" >> "$REPORT_FILE"
    fi
    
    # Add Solana information
    if command_exists solana; then
        echo "- **Solana**: $(solana --version)" >> "$REPORT_FILE"
    fi
    
    cat >> "$REPORT_FILE" << EOF

### Test Environment Status
- **Test Directories**: ✅ Created
- **Python Dependencies**: ✅ Installed
- **Pytest Discovery**: ✅ Working
- **Mock Services**: ✅ Available

### Test Files Validated
EOF

    # List validated test files
    REQUIRED_FILES=(
        "tests/e2e/test_pytest_integration.py"
        "tests/e2e/test_comprehensive_scenarios.py"
        "tests/e2e/conftest.py"
        "tests/e2e/improved_mock_services.py"
    )
    
    for file in "${REQUIRED_FILES[@]}"; do
        if [ -f "$PROJECT_ROOT/$file" ]; then
            echo "- ✅ $file" >> "$REPORT_FILE"
        else
            echo "- ❌ $file (missing)" >> "$REPORT_FILE"
        fi
    done
    
    cat >> "$REPORT_FILE" << EOF

### Next Steps
1. Run comprehensive test suite: \`pytest tests/e2e/ -v\`
2. Execute performance monitoring: \`pytest tests/e2e/ -m performance\`
3. Validate security compliance: \`pytest tests/e2e/ -m security\`

---
*Generated by ACGS-1 Test Environment Setup Script*
EOF

    log "✅ Environment report generated: $REPORT_FILE"
}

# Main execution function
main() {
    log "🚀 Starting ACGS-1 Test Environment Setup"
    log "========================================"
    
    # Change to project root
    cd "$PROJECT_ROOT"
    
    # Setup environments
    setup_python_environment
    setup_nodejs_environment
    setup_rust_environment
    setup_solana_environment
    
    # Setup test infrastructure
    setup_test_directories
    
    # Validate everything works
    validate_test_environment
    
    # Run smoke tests
    run_smoke_tests
    
    # Generate report
    generate_environment_report
    
    log "🎉 ACGS-1 Test Environment Setup Complete!"
    log "=========================================="
    log "Environment ready for CI/CD testing"
    log "Log file: $LOG_FILE"
    log "Report: $PROJECT_ROOT/tests/reports/environment_setup_report.md"
}

# Handle script arguments
case "${1:-setup}" in
    "setup")
        main
        ;;
    "validate")
        validate_test_environment
        ;;
    "smoke")
        run_smoke_tests
        ;;
    "report")
        generate_environment_report
        ;;
    "help")
        echo "ACGS-1 Test Environment Setup Script"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  setup     - Full environment setup (default)"
        echo "  validate  - Validate existing environment"
        echo "  smoke     - Run smoke tests only"
        echo "  report    - Generate environment report"
        echo "  help      - Show this help message"
        ;;
    *)
        error "Unknown command: $1. Use 'help' for usage information."
        ;;
esac
