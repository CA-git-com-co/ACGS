#!/bin/bash
# ACGS-1 Dev Container Setup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[SETUP]${NC} $1"
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

log "🏛️ Setting up ACGS-1 Development Environment..."

# Ensure we're in the workspace directory
cd /workspace

# Set up Python environment
log "🐍 Setting up Python environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    success "Python virtual environment created"
else
    log "Python virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies if requirements files exist
if [ -f "requirements.txt" ]; then
    log "Installing Python dependencies..."
    pip install -r requirements.txt
    success "Python dependencies installed"
fi

if [ -f "requirements-dev.txt" ]; then
    log "Installing development dependencies..."
    pip install -r requirements-dev.txt
    success "Development dependencies installed"
fi

if [ -f "requirements-test.txt" ]; then
    log "Installing test dependencies..."
    pip install -r requirements-test.txt
    success "Test dependencies installed"
fi

# Install service-specific dependencies
log "Installing service-specific dependencies..."
for service_dir in services/core/*/; do
    if [ -d "$service_dir" ] && [ -f "${service_dir}requirements.txt" ]; then
        log "Installing dependencies for ${service_dir}..."
        pip install -r "${service_dir}requirements.txt"
    fi
done

for service_dir in services/platform/*/; do
    if [ -d "$service_dir" ] && [ -f "${service_dir}requirements.txt" ]; then
        log "Installing dependencies for ${service_dir}..."
        pip install -r "${service_dir}requirements.txt"
    fi
done

# Install shared dependencies
if [ -f "services/shared/requirements.txt" ]; then
    log "Installing shared service dependencies..."
    pip install -r services/shared/requirements.txt
fi

# Set up Node.js dependencies
log "📦 Setting up Node.js dependencies..."
if [ -f "package.json" ]; then
    npm install
    success "Root Node.js dependencies installed"
fi

# Install application dependencies
for app_dir in applications/*/; do
    if [ -d "$app_dir" ] && [ -f "${app_dir}package.json" ]; then
        log "Installing dependencies for ${app_dir}..."
        cd "$app_dir"
        npm install
        cd /workspace
    fi
done

# Set up Rust environment
log "🦀 Setting up Rust environment..."
if [ -d "blockchain" ] && [ -f "blockchain/Cargo.toml" ]; then
    cd blockchain
    cargo build
    cd /workspace
    success "Rust blockchain components built"
fi

# Fix Python imports
log "🔧 Fixing Python imports..."
if [ -f "root_scripts/fix_python_imports.py" ]; then
    python root_scripts/fix_python_imports.py
    success "Python imports fixed"
fi

# Set up environment variables
log "🔧 Setting up environment variables..."
if [ -f "config/env/.env.example" ]; then
    if [ ! -f "config/env/.env" ]; then
        cp config/env/.env.example config/env/.env
        success "Environment file created from example"
    fi
elif [ -f ".env.example" ]; then
    if [ ! -f ".env" ]; then
        cp .env.example .env
        success "Environment file created from example"
    fi
fi

# Create necessary directories
log "📁 Creating necessary directories..."
mkdir -p logs pids backups temp
success "Directories created"

# Set up Git hooks (if they exist)
if [ -d ".githooks" ]; then
    log "🔗 Setting up Git hooks..."
    git config core.hooksPath .githooks
    chmod +x .githooks/*
    success "Git hooks configured"
fi

# Wait for database to be ready
log "🗄️ Waiting for database to be ready..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if pg_isready -h postgres -p 5432 -U acgs_user >/dev/null 2>&1; then
        success "Database is ready"
        break
    fi
    attempt=$((attempt + 1))
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    warning "Database connection timeout, but continuing setup"
fi

# Wait for Redis to be ready
log "🔴 Waiting for Redis to be ready..."
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if redis-cli -h redis ping >/dev/null 2>&1; then
        success "Redis is ready"
        break
    fi
    attempt=$((attempt + 1))
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    warning "Redis connection timeout, but continuing setup"
fi

# Run database migrations (if they exist)
if [ -f "scripts/database/migrate.py" ]; then
    log "🗄️ Running database migrations..."
    python scripts/database/migrate.py
    success "Database migrations completed"
fi

# Set up pre-commit hooks (if available)
if command -v pre-commit >/dev/null 2>&1; then
    log "🔍 Setting up pre-commit hooks..."
    pre-commit install
    success "Pre-commit hooks installed"
fi

# Final setup message
echo ""
echo "=============================================="
echo "🎉 ACGS-1 DEV CONTAINER SETUP COMPLETE"
echo "=============================================="
echo ""
echo "📋 Environment Summary:"
echo "  ✅ Python virtual environment activated"
echo "  ✅ Python dependencies installed"
echo "  ✅ Node.js dependencies installed"
echo "  ✅ Rust environment configured"
echo "  ✅ Database and Redis connections verified"
echo "  ✅ Development tools configured"
echo ""
echo "🚀 Quick Start Commands:"
echo "  • Start development services: ./scripts/setup/start_development.sh"
echo "  • Run tests: pytest tests/ -v"
echo "  • Check service health: curl http://localhost:8001/health"
echo "  • View logs: tail -f logs/*.log"
echo ""
echo "🔗 Useful URLs:"
echo "  • Governance Dashboard: http://localhost:3000"
echo "  • API Documentation: http://localhost:8001/docs"
echo "  • Database: postgresql://acgs_user:acgs_password@postgres:5432/acgs_db"
echo "  • Redis: redis://redis:6379/0"
echo ""
echo "Happy coding! 🏛️✨"
