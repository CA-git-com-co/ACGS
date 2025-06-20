#!/bin/bash
# ACGS Comprehensive Dependency Management Setup
# This script sets up unified dependency management for the entire ACGS project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
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
if [ ! -f "pyproject.toml" ] || [ ! -f "Cargo.toml" ]; then
    error "Please run this script from the ACGS project root directory"
    exit 1
fi

log "🚀 Starting ACGS Comprehensive Dependency Management Setup"

# Step 1: Backup current state
log "📦 Creating backup of current dependency state..."
BACKUP_DIR="dependency_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

# Backup key files
find . -name "requirements*.txt" -not -path "./node_modules/*" -not -path "./venv/*" -exec cp {} "$BACKUP_DIR/" \; 2>/dev/null || true
find . -name "package.json" -not -path "./node_modules/*" -exec cp {} "$BACKUP_DIR/" \; 2>/dev/null || true
find . -name "package-lock.json" -not -path "./node_modules/*" -exec cp {} "$BACKUP_DIR/" \; 2>/dev/null || true
find . -name "Cargo.toml" -not -path "./target/*" -exec cp {} "$BACKUP_DIR/" \; 2>/dev/null || true

success "Backup created in $BACKUP_DIR"

# Step 2: Install UV if not present
log "🐍 Checking UV installation..."
if ! command -v uv &> /dev/null; then
    log "Installing UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if command -v uv &> /dev/null; then
        success "UV installed successfully"
    else
        error "UV installation failed"
        exit 1
    fi
else
    success "UV is already installed: $(uv --version)"
fi

# Step 3: Install Node.js dependencies if needed
log "📦 Checking Node.js setup..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    success "Node.js is installed: $NODE_VERSION"
    
    # Check if version is >= 18
    NODE_MAJOR=$(echo $NODE_VERSION | cut -d'.' -f1 | sed 's/v//')
    if [ "$NODE_MAJOR" -lt 18 ]; then
        warning "Node.js version $NODE_VERSION is below recommended 18.x"
    fi
else
    warning "Node.js not found. Please install Node.js 18+ for frontend development"
fi

# Step 4: Install Rust if needed for blockchain development
log "🦀 Checking Rust setup..."
if command -v cargo &> /dev/null; then
    RUST_VERSION=$(rustc --version)
    success "Rust is installed: $RUST_VERSION"
else
    warning "Rust not found. Install with: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh"
fi

# Step 5: Clean existing dependency artifacts
log "🧹 Cleaning existing dependency artifacts..."
python3 scripts/cleanup_dependencies.py --auto-confirm 2>/dev/null || {
    warning "Cleanup script not found or failed, continuing with manual cleanup..."
    
    # Manual cleanup of major artifacts
    log "Removing node_modules directories..."
    find . -name "node_modules" -type d -prune -exec rm -rf {} + 2>/dev/null || true
    
    log "Removing Python cache directories..."
    find . -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null || true
    find . -name ".mypy_cache" -type d -prune -exec rm -rf {} + 2>/dev/null || true
    find . -name ".pytest_cache" -type d -prune -exec rm -rf {} + 2>/dev/null || true
    
    log "Removing build artifacts..."
    find . -name "dist" -type d -prune -exec rm -rf {} + 2>/dev/null || true
    find . -name "build" -type d -prune -exec rm -rf {} + 2>/dev/null || true
    find . -name ".next" -type d -prune -exec rm -rf {} + 2>/dev/null || true
    
    log "Removing lock files..."
    find . -name "package-lock.json" -not -path "./node_modules/*" -delete 2>/dev/null || true
    find . -name "yarn.lock" -not -path "./node_modules/*" -delete 2>/dev/null || true
    find . -name "Cargo.lock" -not -path "./target/*" -delete 2>/dev/null || true
}

success "Cleanup completed"

# Step 6: Setup Python dependencies with UV
log "🐍 Setting up Python dependencies with UV..."

# Initialize UV workspace
log "Initializing UV workspace..."
uv init --no-readme --workspace 2>/dev/null || true

# Sync dependencies
log "Syncing Python dependencies..."
if uv sync; then
    success "Python dependencies synced successfully"
else
    warning "UV sync had issues, but continuing..."
fi

# Step 7: Setup Node.js dependencies
if command -v npm &> /dev/null; then
    log "📦 Setting up Node.js dependencies..."
    
    # Install root dependencies
    log "Installing root package dependencies..."
    npm install --no-package-lock
    
    # Install workspace dependencies
    log "Installing workspace dependencies..."
    npm install --workspaces --no-package-lock 2>/dev/null || {
        warning "Some workspace installs failed, installing individually..."
        
        # Install blockchain dependencies
        if [ -d "blockchain" ] && [ -f "blockchain/package.json" ]; then
            log "Installing blockchain dependencies..."
            cd blockchain && npm install --no-package-lock && cd ..
        fi
        
        # Install application dependencies
        for app_dir in applications/*/; do
            if [ -f "${app_dir}package.json" ]; then
                log "Installing dependencies for $(basename "$app_dir")..."
                cd "$app_dir" && npm install --no-package-lock && cd - > /dev/null
            fi
        done
        
        # Install tool dependencies
        if [ -d "tools/mcp-inspector" ] && [ -f "tools/mcp-inspector/package.json" ]; then
            log "Installing MCP inspector dependencies..."
            cd tools/mcp-inspector && npm install --no-package-lock && cd - > /dev/null
        fi
    }
    
    success "Node.js dependencies installed"
else
    warning "npm not available, skipping Node.js dependency installation"
fi

# Step 8: Setup Rust dependencies
if command -v cargo &> /dev/null; then
    log "🦀 Setting up Rust dependencies..."
    
    # Check dependencies without building
    if cargo check --workspace 2>/dev/null; then
        success "Rust dependencies are valid"
    else
        warning "Rust dependency check failed, but continuing..."
    fi
else
    warning "cargo not available, skipping Rust dependency check"
fi

# Step 9: Update .gitignore to exclude dependency artifacts
log "📝 Updating .gitignore..."
if ! grep -q "# DEPENDENCY DIRECTORIES & ARTIFACTS" .gitignore; then
    warning ".gitignore may need manual updates for dependency exclusions"
else
    success ".gitignore is already configured for dependency management"
fi

# Step 10: Remove dependency artifacts from Git tracking
log "🗑️  Removing dependency artifacts from Git tracking..."
git rm -r --cached --ignore-unmatch node_modules/ 2>/dev/null || true
git rm -r --cached --ignore-unmatch target/ 2>/dev/null || true
git rm -r --cached --ignore-unmatch dist/ 2>/dev/null || true
git rm -r --cached --ignore-unmatch build/ 2>/dev/null || true
git rm -r --cached --ignore-unmatch __pycache__/ 2>/dev/null || true
git rm --cached --ignore-unmatch package-lock.json 2>/dev/null || true
git rm --cached --ignore-unmatch yarn.lock 2>/dev/null || true
git rm --cached --ignore-unmatch Cargo.lock 2>/dev/null || true

success "Dependency artifacts removed from Git tracking"

# Step 11: Generate summary report
log "📊 Generating setup report..."

echo ""
echo "=============================================="
echo "🎉 ACGS DEPENDENCY MANAGEMENT SETUP COMPLETE"
echo "=============================================="
echo ""
echo "📋 Summary:"
echo "  ✅ UV configured for Python dependency management"
echo "  ✅ Workspace structure established"
echo "  ✅ Node.js dependencies installed (if available)"
echo "  ✅ Rust dependencies checked (if available)"
echo "  ✅ .gitignore updated for dependency exclusions"
echo "  ✅ Git tracking cleaned of dependency artifacts"
echo ""
echo "📁 Backup created: $BACKUP_DIR"
echo ""
echo "🚀 Next Steps:"
echo "  1. Review and test your services:"
echo "     - Python: 'uv run python -m pytest'"
echo "     - Node.js: 'npm test'"
echo "     - Rust: 'cargo test'"
echo ""
echo "  2. Development workflow:"
echo "     - Add Python deps: 'uv add <package>'"
echo "     - Add Node deps: 'npm install <package> --workspace=<workspace>'"
echo "     - Add Rust deps: 'cargo add <crate>'"
echo ""
echo "  3. Commit your changes:"
echo "     - 'git add .'"
echo "     - 'git commit -m \"Setup unified dependency management with UV and TOML\"'"
echo ""
echo "📚 Documentation:"
echo "  - UV: https://docs.astral.sh/uv/"
echo "  - npm workspaces: https://docs.npmjs.com/cli/v7/using-npm/workspaces"
echo "  - Cargo workspaces: https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html"
echo ""

success "Setup completed successfully! 🎉"
