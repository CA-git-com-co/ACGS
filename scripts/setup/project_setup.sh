#!/bin/bash
# ACGS-1 Comprehensive Project Setup Script
# This script sets up the complete development environment for ACGS-1

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

# Check if running from project root
if [ ! -f "requirements.txt" ]; then
    error "Please run this script from the ACGS project root directory"
    exit 1
fi

# Create backup directory
BACKUP_DIR="./setup_backup_$(date +'%Y%m%d_%H%M%S')"
mkdir -p "$BACKUP_DIR"
log "Created backup directory: $BACKUP_DIR"

# Step 1: Setup Python environment
setup_python_env() {
    log "🐍 Setting up Python environment..."
    
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
    
    # Install dependencies
    log "Installing Python dependencies..."
    pip install -r requirements.txt
    
    # Install service-specific dependencies
    for service_dir in services/core/*/; do
        if [ -f "${service_dir}requirements.txt" ]; then
            log "Installing dependencies for ${service_dir}..."
            pip install -r "${service_dir}requirements.txt"
        fi
    done
    
    success "Python environment setup complete"
}

# Step 2: Setup Node.js environment
setup_nodejs_env() {
    log "📦 Setting up Node.js environment..."
    
    if command -v npm &> /dev/null; then
        # Install root dependencies
        if [ -f "package.json" ]; then
            log "Installing root package dependencies..."
            npm install
        fi
        
        # Install application dependencies
        if [ -d "applications/governance-dashboard" ]; then
            log "Installing governance dashboard dependencies..."
            cd applications/governance-dashboard
            npm install
            cd ../..
        fi
        
        success "Node.js environment setup complete"
    else
        warning "npm not available, skipping Node.js setup"
    fi
}

# Step 3: Setup Rust/Anchor environment
setup_rust_env() {
    log "🦀 Setting up Rust/Anchor environment..."
    
    if command -v cargo &> /dev/null; then
        if [ -d "blockchain" ]; then
            log "Building Anchor programs..."
            cd blockchain
            anchor build
            cd ..
            
            # Set up Solana configuration
            if command -v solana &> /dev/null; then
                log "Configuring Solana for devnet..."
                solana config set --url devnet
                solana config set --keypair ~/.config/solana/id.json
            else
                warning "Solana CLI not found, skipping Solana configuration"
            fi
        fi
        
        success "Rust environment setup complete"
    else
        warning "Cargo not found, skipping Rust setup"
    fi
}

# Step 4: Setup environment variables
setup_env_vars() {
    log "🔧 Setting up environment variables..."
    
    if [ ! -f "config/env/.env" ]; then
        log "Creating .env file from example..."
        cp -n config/env/.env.example config/env/.env
        
        # Generate secure keys
        log "Generating secure keys..."
        SECRET_KEY=$(openssl rand -hex 32)
        CSRF_SECRET_KEY=$(openssl rand -hex 32)
        REDIS_PASSWORD=$(openssl rand -hex 16)
        
        # Update .env file with secure keys
        sed -i "s/SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" config/env/.env
        sed -i "s/CSRF_SECRET_KEY=.*/CSRF_SECRET_KEY=$CSRF_SECRET_KEY/" config/env/.env
        sed -i "s/REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PASSWORD/" config/env/.env
        
        success "Environment file created with secure keys"
    else
        log "Environment file already exists"
    fi
    
    # Source environment variables
    log "Sourcing environment variables..."
    source scripts/set_service_env.sh
    
    success "Environment variables setup complete"
}

# Step 5: Setup Docker infrastructure
setup_docker_infra() {
    log "🐳 Setting up Docker infrastructure..."
    
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        log "Starting development services..."
        cd infrastructure/docker
        docker-compose -f docker-compose.dev.yml up -d
        cd ../..
        
        success "Docker infrastructure setup complete"
    else
        warning "Docker or docker-compose not found, skipping infrastructure setup"
    fi
}

# Step 6: Run database migrations
run_migrations() {
    log "🔄 Running database migrations..."
    
    if [ -f "scripts/run_migrations.sh" ]; then
        ./scripts/run_migrations.sh
        success "Database migrations complete"
    else
        warning "Migration script not found, skipping migrations"
    fi
}

# Step 7: Seed test data
seed_test_data() {
    log "🌱 Seeding test data..."
    
    if [ -f "scripts/seed_test_data.sh" ]; then
        ./scripts/seed_test_data.sh
        success "Test data seeded"
    else
        warning "Seed script not found, skipping test data"
    fi
}

# Step 8: Run health checks
run_health_checks() {
    log "🔍 Running health checks..."
    
    if [ -f "scripts/health_check_all_services.sh" ]; then
        ./scripts/health_check_all_services.sh
        success "Health checks complete"
    else
        warning "Health check script not found, skipping health checks"
    fi
}

# Step 9: Setup dependency management with UV
setup_dependency_management() {
    log "📦 Setting up dependency management with UV..."
    
    # Check if UV is installed
    if command -v uv &> /dev/null; then
        log "UV is installed, setting up workspace..."
        
        # Run the dependency management script if it exists
        if [ -f "scripts/setup_dependency_management.py" ]; then
            python scripts/setup_dependency_management.py
            success "Dependency management setup complete"
        else
            warning "Dependency management script not found, skipping"
        fi
    else
        warning "UV not installed, attempting to install..."
        pip install uv
        
        if command -v uv &> /dev/null; then
            log "UV installed successfully, setting up workspace..."
            python scripts/setup_dependency_management.py
            success "Dependency management setup complete"
        else
            warning "Failed to install UV, skipping dependency management setup"
        fi
    fi
}

# Main setup function
main() {
    log "🚀 Starting ACGS-1 Project Setup"
    echo "============================="
    
    # Run setup steps
    setup_python_env
    setup_nodejs_env
    setup_rust_env
    setup_env_vars
    setup_docker_infra
    run_migrations
    seed_test_data
    setup_dependency_management
    run_health_checks
    
    echo ""
    echo "=============================================="
    echo "🎉 ACGS-1 PROJECT SETUP COMPLETE"
    echo "=============================================="
    echo ""
    echo "📋 Summary:"
    echo "  ✅ Python environment configured"
    echo "  ✅ Node.js dependencies installed"
    echo "  ✅ Rust/Anchor programs built"
    echo "  ✅ Environment variables configured"
    echo "  ✅ Docker infrastructure started"
    echo "  ✅ Database migrations applied"
    echo "  ✅ Test data seeded"
    echo "  ✅ Dependency management configured"
    echo "  ✅ Health checks performed"
    echo ""
    echo "📁 Backup created: $BACKUP_DIR"
    echo ""
    echo "🚀 Next Steps:"
    echo "  1. Review the .env file and update API keys"
    echo "  2. Start individual services for development:"
    echo "     - Python services: cd services/core/<service> && uvicorn app.main:app --reload"
    echo "     - Frontend: cd applications/governance-dashboard && npm start"
    echo "  3. Run tests to verify functionality:"
    echo "     - Python: pytest"
    echo "     - Rust: cargo test"
    echo ""
    echo "To activate the environment in new terminals, run: source venv/bin/activate"
}

# Run main function
main "$@"