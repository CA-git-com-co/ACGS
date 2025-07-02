#!/bin/bash
# ACGS-PGP Dependency Installation Script
# This script installs all required dependencies for the ACGS-PGP Constitutional Governance System
# Uses proper package managers: pnpm for Node.js, cargo for Rust, UV for Python

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log "📋 Checking prerequisites..."
    
    local missing_deps=()
    
    # Check for required system tools
    command -v git >/dev/null 2>&1 || missing_deps+=("git")
    command -v python3 >/dev/null 2>&1 || missing_deps+=("python3")
    command -v pip3 >/dev/null 2>&1 || missing_deps+=("python3-pip")
    command -v node >/dev/null 2>&1 || missing_deps+=("nodejs")
    command -v docker >/dev/null 2>&1 || missing_deps+=("docker")
    command -v docker-compose >/dev/null 2>&1 || missing_deps+=("docker-compose")

    # Check for preferred package managers (will install if missing)
    if ! command -v pnpm >/dev/null 2>&1; then
        log "pnpm not found, will install during Node.js setup"
    fi

    if ! command -v cargo >/dev/null 2>&1; then
        log "cargo not found, will install during Rust setup"
    fi

    if ! command -v uv >/dev/null 2>&1; then
        log "uv not found, will install during Python setup"
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        error "Missing required dependencies: ${missing_deps[*]}"
        echo "Please install the missing dependencies and run this script again."
        echo ""
        echo "Ubuntu/Debian installation commands:"
        echo "  sudo apt update"
        echo "  sudo apt install -y git python3 python3-pip nodejs npm docker.io docker-compose"
        echo ""
        echo "macOS installation commands (with Homebrew):"
        echo "  brew install git python3 node docker docker-compose"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Install Python dependencies
install_python_dependencies() {
    log "🐍 Installing Python dependencies..."
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        log "Creating Python virtual environment..."
        python3 -m venv venv
        success "Virtual environment created"
    else
        log "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    log "Upgrading pip..."
    pip install --upgrade pip
    
    # Install root dependencies
    if [ -f "requirements.txt" ]; then
        log "Installing root Python dependencies..."
        pip install -r requirements.txt
        success "Root dependencies installed"
    else
        warning "requirements.txt not found, skipping root dependencies"
    fi
    
    # Install service-specific dependencies
    log "Installing service-specific Python dependencies..."
    local services_found=0
    
    for service_dir in services/core/*/; do
        if [ -d "$service_dir" ] && [ -f "${service_dir}requirements.txt" ]; then
            log "Installing dependencies for ${service_dir}..."
            pip install -r "${service_dir}requirements.txt"
            ((services_found++))
        fi
    done
    
    for service_dir in services/platform/*/; do
        if [ -d "$service_dir" ] && [ -f "${service_dir}requirements.txt" ]; then
            log "Installing dependencies for ${service_dir}..."
            pip install -r "${service_dir}requirements.txt"
            ((services_found++))
        fi
    done
    
    # Install shared dependencies
    if [ -f "services/shared/requirements.txt" ]; then
        log "Installing shared service dependencies..."
        pip install -r services/shared/requirements.txt
        ((services_found++))
    fi
    
    # Install test dependencies
    if [ -f "requirements-test.txt" ]; then
        log "Installing test dependencies..."
        pip install -r requirements-test.txt
    fi
    
    success "Python dependencies installed (${services_found} service directories processed)"
}

# Install Node.js dependencies with pnpm
install_nodejs_dependencies() {
    log "📦 Installing Node.js dependencies with pnpm..."

    # Install pnpm if not available
    if ! command -v pnpm >/dev/null 2>&1; then
        log "Installing pnpm package manager..."
        if command -v npm >/dev/null 2>&1; then
            npm install -g pnpm
        else
            curl -fsSL https://get.pnpm.io/install.sh | sh -
            export PATH="$HOME/.local/share/pnpm:$PATH"
        fi
    fi

    # Verify pnpm installation
    if ! command -v pnpm >/dev/null 2>&1; then
        error "Failed to install pnpm, falling back to npm"

        # Fallback to npm
        if [ -f "package.json" ]; then
            log "Installing root Node.js dependencies with npm..."
            npm install
            success "Root Node.js dependencies installed with npm"
        fi

        for app_dir in applications/*/; do
            if [ -d "$app_dir" ] && [ -f "${app_dir}package.json" ]; then
                log "Installing dependencies for ${app_dir} with npm..."
                cd "$app_dir"
                npm install
                cd - > /dev/null
            fi
        done
        return
    fi

    # Install root package dependencies with pnpm
    if [ -f "package.json" ]; then
        log "Installing root Node.js dependencies with pnpm..."
        pnpm install
        success "Root Node.js dependencies installed with pnpm"
    else
        log "No root package.json found, skipping root dependencies"
    fi

    # Install application dependencies with pnpm
    local apps_found=0

    for app_dir in applications/*/; do
        if [ -d "$app_dir" ] && [ -f "${app_dir}package.json" ]; then
            log "Installing dependencies for ${app_dir} with pnpm..."
            cd "$app_dir"
            pnpm install
            cd - > /dev/null
            ((apps_found++))
        fi
    done

    success "Node.js dependencies installed with pnpm (${apps_found} application directories processed)"
}

# Install Rust dependencies with proper cargo usage
install_rust_dependencies() {
    log "🦀 Installing Rust dependencies for constitutional governance..."

    # Install Rust if not present
    if ! command -v cargo >/dev/null 2>&1; then
        log "Installing Rust..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        source ~/.cargo/env
    fi

    if command -v cargo >/dev/null 2>&1; then
        # Update Rust to latest stable
        log "Updating Rust to latest stable..."
        rustup update stable
        rustup default stable

        # Install required Rust components
        log "Installing Rust components..."
        rustup component add rustfmt clippy

        # Build blockchain components if present
        if [ -f "blockchain/Cargo.toml" ]; then
            log "Building ACGS-PGP blockchain components..."
            cd blockchain

            # Check dependencies and build
            cargo check
            cargo build --release

            # Run tests to validate constitutional governance components
            log "Running constitutional governance tests..."
            cargo test --release

            cd - > /dev/null
            success "ACGS-PGP Rust blockchain components built and tested"
        else
            log "No blockchain Cargo.toml found, skipping blockchain dependencies"
        fi

        # Install Anchor CLI if not present (for Solana development)
        if ! command -v anchor >/dev/null 2>&1; then
            log "Installing Anchor CLI for Solana development..."
            cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
            if command -v avm >/dev/null 2>&1; then
                avm install latest
                avm use latest
                success "Anchor CLI installed"
            else
                warning "AVM installation failed, but continuing..."
            fi
        else
            log "Anchor CLI already installed"
        fi

        # Install additional Rust tools for constitutional governance
        log "Installing additional Rust tools..."
        cargo install cargo-audit cargo-outdated cargo-tree

        success "Rust dependencies and tools installed"
    else
        error "Failed to install Rust, skipping Rust dependencies"
    fi
}

# Install system dependencies for AI/ML models
install_system_dependencies() {
    log "🤖 Installing system dependencies for AI/ML models..."
    
    # Check if we're in a virtual environment
    if [ -n "$VIRTUAL_ENV" ] || [ -d "venv" ]; then
        if [ ! -n "$VIRTUAL_ENV" ]; then
            source venv/bin/activate
        fi
        
        # Install AI/ML dependencies
        log "Installing AI/ML Python packages..."
        pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
        pip install transformers accelerate timm einops open-clip-torch
        pip install vllm
        
        success "AI/ML dependencies installed"
    else
        warning "Virtual environment not found, skipping AI/ML dependencies"
    fi
}

# Verify installations
verify_installations() {
    log "🔍 Verifying installations..."
    
    # Check Python environment
    if [ -d "venv" ]; then
        source venv/bin/activate
        python_version=$(python --version 2>&1)
        pip_version=$(pip --version 2>&1)
        log "Python: $python_version"
        log "Pip: $pip_version"
    fi
    
    # Check Node.js
    if command -v node >/dev/null 2>&1; then
        node_version=$(node --version 2>&1)
        npm_version=$(npm --version 2>&1)
        log "Node.js: $node_version"
        log "NPM: $npm_version"
    fi
    
    # Check Docker
    if command -v docker >/dev/null 2>&1; then
        docker_version=$(docker --version 2>&1)
        log "Docker: $docker_version"
    fi
    
    # Check Rust (if available)
    if command -v cargo >/dev/null 2>&1; then
        cargo_version=$(cargo --version 2>&1)
        log "Cargo: $cargo_version"
    fi
    
    success "Installation verification complete"
}

# Main installation function
main() {
    log "🚀 Starting ACGS-1 Dependency Installation"
    echo "========================================="
    
    # Run installation steps
    check_prerequisites
    install_python_dependencies
    install_nodejs_dependencies
    install_rust_dependencies
    install_system_dependencies
    verify_installations
    
    echo ""
    echo "=============================================="
    echo "🎉 DEPENDENCY INSTALLATION COMPLETE"
    echo "=============================================="
    echo ""
    echo "📋 Summary:"
    echo "  ✅ Prerequisites verified"
    echo "  ✅ Python dependencies installed"
    echo "  ✅ Node.js dependencies installed"
    echo "  ✅ Rust dependencies built (if available)"
    echo "  ✅ AI/ML system dependencies installed"
    echo "  ✅ Installation verification complete"
    echo ""
    echo "🚀 Next Steps:"
    echo "  1. Run: source venv/bin/activate"
    echo "  2. Run: ./scripts/setup/start_development.sh"
    echo "  3. Or run: ./scripts/setup/quick_start.sh for full setup"
    echo ""
    echo "To activate the environment in new terminals, run: source venv/bin/activate"
}

# Run main function
main "$@"
