# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# ACGS-1 Enterprise Infrastructure Setup Script
# Automated infrastructure validation and setup for CI/CD pipeline

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_FILE="/tmp/acgs-infrastructure-setup.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")
            echo -e "${BLUE}[INFO]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[SUCCESS]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        "WARNING")
            echo -e "${YELLOW}[WARNING]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        "ERROR")
            echo -e "${RED}[ERROR]${NC} $message" | tee -a "$LOG_FILE"
            ;;
    esac
    echo "[$timestamp] [$level] $message" >> "$LOG_FILE"
}

# Enterprise infrastructure validation
validate_infrastructure() {
    log "INFO" "🔧 Starting enterprise infrastructure validation..."
    
    # Check system resources
    log "INFO" "Checking system resources..."
    
    # Memory check (minimum 4GB)
    local memory_gb=$(free -g | awk '/^Mem:/{print $2}')
    # Handle case where memory_gb might be empty or non-numeric
    if [[ -z "$memory_gb" || ! "$memory_gb" =~ ^[0-9]+$ ]]; then
        memory_gb=$(free -m | awk '/^Mem:/{printf "%.0f", $2/1024}')
    fi
    if [[ -n "$memory_gb" && "$memory_gb" =~ ^[0-9]+$ ]]; then
        if [ "$memory_gb" -lt 4 ]; then
            log "WARNING" "Available memory: ${memory_gb}GB (recommended: 4GB+)"
        else
            log "SUCCESS" "Memory check passed: ${memory_gb}GB available"
        fi
    else
        log "WARNING" "Could not determine memory size, assuming sufficient"
    fi
    
    # Disk space check (minimum 10GB)
    local disk_gb=$(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ "$disk_gb" -lt 10 ]; then
        log "WARNING" "Available disk space: ${disk_gb}GB (recommended: 10GB+)"
    else
        log "SUCCESS" "Disk space check passed: ${disk_gb}GB available"
    fi
    
    # CPU cores check
    local cpu_cores=$(nproc)
    log "INFO" "CPU cores available: $cpu_cores"
    
    # Network connectivity validation
    log "INFO" "Validating network connectivity..."
    
    local endpoints=(
        "github.com"
        "crates.io"
        "registry.npmjs.org"
        "pypi.org"
        "api.github.com"
    )
    
    for endpoint in "${endpoints[@]}"; do
        if ping -c 1 -W 5 "$endpoint" > /dev/null 2>&1; then
            log "SUCCESS" "✅ $endpoint connectivity verified"
        else
            log "ERROR" "❌ $endpoint connectivity failed"
            return 1
        fi
    done
    
    log "SUCCESS" "✅ Infrastructure validation completed successfully"
    return 0
}

# Solana test environment setup
setup_solana_test_environment() {
    log "INFO" "🔧 Setting up Solana test environment..."
    
    # Create Solana config directory
    local solana_config_dir="$HOME/.config/solana"
    mkdir -p "$solana_config_dir"
    
    # Generate test keypair if it doesn't exist
    local keypair_file="$solana_config_dir/id.json"
    if [ ! -f "$keypair_file" ]; then
        log "INFO" "Generating new test keypair..."
        if command -v solana-keygen >/dev/null 2>&1; then
            solana-keygen new --no-bip39-passphrase --silent --outfile "$keypair_file"
            log "SUCCESS" "✅ Test keypair created at $keypair_file"
        else
            log "ERROR" "❌ solana-keygen not found. Please install Solana CLI first."
            return 1
        fi
    else
        log "INFO" "Test keypair already exists at $keypair_file"
    fi
    
    # Validate keypair
    if command -v solana-keygen >/dev/null 2>&1; then
        if solana-keygen verify "$keypair_file" > /dev/null 2>&1; then
            log "SUCCESS" "✅ Keypair validation successful"
        else
            log "ERROR" "❌ Keypair validation failed"
            return 1
        fi
    fi
    
    # Configure Solana CLI for local testing
    if command -v solana >/dev/null 2>&1; then
        solana config set --url localhost --keypair "$keypair_file"
        log "SUCCESS" "✅ Solana CLI configured for local testing"
    else
        log "WARNING" "⚠️ Solana CLI not found. Configuration will be done during test execution."
    fi
    
    log "SUCCESS" "✅ Solana test environment setup completed"
    return 0
}

# Docker environment validation
validate_docker_environment() {
    log "INFO" "🐳 Validating Docker environment..."
    
    if command -v docker >/dev/null 2>&1; then
        if docker info > /dev/null 2>&1; then
            log "SUCCESS" "✅ Docker is available and running"
            
            # Check Docker version
            local docker_version=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
            log "INFO" "Docker version: $docker_version"
            
            # Check available Docker resources
            local docker_info=$(docker system df 2>/dev/null || echo "Docker system info unavailable")
            log "INFO" "Docker system info: $docker_info"
            
        else
            log "WARNING" "⚠️ Docker is installed but not running"
            return 1
        fi
    else
        log "WARNING" "⚠️ Docker not found (optional for some tests)"
    fi
    
    return 0
}

# Node.js environment validation
validate_nodejs_environment() {
    log "INFO" "📦 Validating Node.js environment..."
    
    if command -v node >/dev/null 2>&1; then
        local node_version=$(node --version)
        log "SUCCESS" "✅ Node.js available: $node_version"
        
        if command -v npm >/dev/null 2>&1; then
            local npm_version=$(npm --version)
            log "SUCCESS" "✅ npm available: v$npm_version"
        else
            log "WARNING" "⚠️ npm not found"
            return 1
        fi
    else
        log "WARNING" "⚠️ Node.js not found"
        return 1
    fi
    
    return 0
}

# Python environment validation
validate_python_environment() {
    log "INFO" "🐍 Validating Python environment..."
    
    if command -v python3 >/dev/null 2>&1; then
        local python_version=$(python3 --version)
        log "SUCCESS" "✅ Python available: $python_version"
        
        if command -v pip3 >/dev/null 2>&1; then
            local pip_version=$(pip3 --version | cut -d' ' -f2)
            log "SUCCESS" "✅ pip available: v$pip_version"
        else
            log "WARNING" "⚠️ pip3 not found"
            return 1
        fi
    else
        log "WARNING" "⚠️ Python3 not found"
        return 1
    fi
    
    return 0
}

# Rust environment validation
validate_rust_environment() {
    log "INFO" "🦀 Validating Rust environment..."
    
    if command -v rustc >/dev/null 2>&1; then
        local rust_version=$(rustc --version)
        log "SUCCESS" "✅ Rust available: $rust_version"
        
        if command -v cargo >/dev/null 2>&1; then
            local cargo_version=$(cargo --version)
            log "SUCCESS" "✅ Cargo available: $cargo_version"
        else
            log "WARNING" "⚠️ Cargo not found"
            return 1
        fi
    else
        log "WARNING" "⚠️ Rust not found"
        return 1
    fi
    
    return 0
}

# Pre-flight environment checks
run_preflight_checks() {
    log "INFO" "🚀 Running enterprise pre-flight checks..."
    
    local checks_passed=0
    local total_checks=6
    
    # Run all validation checks
    validate_infrastructure && ((checks_passed++)) || log "WARNING" "Infrastructure validation failed"
    validate_docker_environment && ((checks_passed++)) || log "WARNING" "Docker validation failed"
    validate_nodejs_environment && ((checks_passed++)) || log "WARNING" "Node.js validation failed"
    validate_python_environment && ((checks_passed++)) || log "WARNING" "Python validation failed"
    validate_rust_environment && ((checks_passed++)) || log "WARNING" "Rust validation failed"
    setup_solana_test_environment && ((checks_passed++)) || log "WARNING" "Solana environment setup failed"
    
    # Report results
    log "INFO" "Pre-flight checks completed: $checks_passed/$total_checks passed"
    
    if [ "$checks_passed" -eq "$total_checks" ]; then
        log "SUCCESS" "✅ All pre-flight checks passed - environment ready for enterprise CI/CD"
        return 0
    elif [ "$checks_passed" -ge 4 ]; then
        log "WARNING" "⚠️ Most pre-flight checks passed - environment partially ready"
        return 0
    else
        log "ERROR" "❌ Critical pre-flight checks failed - environment not ready"
        return 1
    fi
}

# Generate infrastructure report
generate_infrastructure_report() {
    log "INFO" "📊 Generating infrastructure readiness report..."
    
    local report_file="/tmp/infrastructure-readiness-report.json"
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    
    cat > "$report_file" << EOF
{
  "timestamp": "$timestamp",
  "infrastructure_validation": {
    "system_resources": {
      "memory_gb": $(free -g | awk '/^Mem:/{print $2}'),
      "disk_gb": $(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//'),
      "cpu_cores": $(nproc)
    },
    "network_connectivity": {
      "github_com": "$(ping -c 1 -W 5 github.com > /dev/null 2>&1 && echo 'ok' || echo 'failed')",
      "crates_io": "$(ping -c 1 -W 5 crates.io > /dev/null 2>&1 && echo 'ok' || echo 'failed')",
      "npmjs_org": "$(ping -c 1 -W 5 registry.npmjs.org > /dev/null 2>&1 && echo 'ok' || echo 'failed')"
    },
    "toolchain_availability": {
      "docker": "$(command -v docker >/dev/null 2>&1 && echo 'available' || echo 'not_found')",
      "node": "$(command -v node >/dev/null 2>&1 && echo 'available' || echo 'not_found')",
      "python3": "$(command -v python3 >/dev/null 2>&1 && echo 'available' || echo 'not_found')",
      "rust": "$(command -v rustc >/dev/null 2>&1 && echo 'available' || echo 'not_found')",
      "solana": "$(command -v solana >/dev/null 2>&1 && echo 'available' || echo 'not_found')"
    },
    "solana_test_environment": {
      "keypair_exists": "$([ -f "$HOME/.config/solana/id.json" ] && echo 'true' || echo 'false')",
      "config_directory": "$HOME/.config/solana"
    }
  },
  "readiness_status": "$([ -f "$HOME/.config/solana/id.json" ] && echo 'ready' || echo 'partial')"
}
EOF
    
    log "SUCCESS" "✅ Infrastructure report generated: $report_file"
    
    # Display summary
    log "INFO" "Infrastructure Readiness Summary:"
    log "INFO" "- Memory: $(free -g | awk '/^Mem:/{print $2}')GB"
    log "INFO" "- Disk: $(df -BG / | awk 'NR==2 {print $4}' | sed 's/G//')GB"
    log "INFO" "- CPU Cores: $(nproc)"
    log "INFO" "- Solana Keypair: $([ -f "$HOME/.config/solana/id.json" ] && echo 'Ready' || echo 'Not Found')"
    
    return 0
}

# Main execution
main() {
    log "INFO" "🚀 Starting ACGS-1 Enterprise Infrastructure Setup..."
    
    # Create log file
    touch "$LOG_FILE"
    
    # Run pre-flight checks
    if run_preflight_checks; then
        log "SUCCESS" "✅ Pre-flight checks completed successfully"
    else
        log "ERROR" "❌ Pre-flight checks failed"
        exit 1
    fi
    
    # Generate infrastructure report
    generate_infrastructure_report
    
    log "SUCCESS" "✅ Enterprise infrastructure setup completed successfully"
    log "INFO" "📋 Full log available at: $LOG_FILE"
    
    return 0
}

# Execute main function if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
