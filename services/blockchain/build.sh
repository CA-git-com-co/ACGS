#!/bin/bash
# Unified Build Script for ACGS Blockchain Service
# Constitutional Hash: cdd01ef066bc6cf2

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Parse command line arguments
COMMAND=${1:-"all"}
CLUSTER=${2:-"devnet"}
SKIP_TESTS=${3:-false}

print_status "Starting ACGS Blockchain build process..."
print_status "Command: $COMMAND"
print_status "Cluster: $CLUSTER"

case $COMMAND in
    "clean")
        print_status "Cleaning build artifacts..."
        anchor clean
        cd scripts && cargo clean
        print_success "Clean completed"
        ;;
    
    "rust-tools")
        print_status "Building Rust deployment tools..."
        cd scripts && cargo build --release
        print_success "Rust tools built successfully"
        ;;
    
    "programs")
        print_status "Building Anchor programs..."
        if [ "$CLUSTER" = "mainnet" ]; then
            anchor build --release
        else
            anchor build
        fi
        print_success "Anchor programs built successfully"
        ;;
    
    "test")
        print_status "Running test suite..."
        
        # Rust tests
        print_status "Running Rust integration tests..."
        cd scripts && cargo test --release
        cd ..
        
        # Anchor tests
        print_status "Running Anchor tests..."
        anchor test
        
        print_success "All tests passed"
        ;;
    
    "deploy")
        print_status "Deploying to $CLUSTER..."
        
        # Build first
        bash build.sh programs $CLUSTER true
        
        # Deploy using Rust tools
        cd scripts && cargo run --bin deploy_quantumagi -- deploy --cluster $CLUSTER
        
        print_success "Deployment to $CLUSTER completed"
        ;;
    
    "init")
        print_status "Initializing constitution on $CLUSTER..."
        cd scripts && cargo run --bin initialize_constitution -- --cluster $CLUSTER
        print_success "Constitution initialized"
        ;;
    
    "validate")
        print_status "Validating deployment on $CLUSTER..."
        cd scripts && cargo run --bin validate_deployment -- --cluster $CLUSTER
        print_success "Deployment validation completed"
        ;;
    
    "dev")
        print_status "Development build (fast iteration)..."
        
        # Clean first
        bash build.sh clean
        
        # Build tools and programs
        bash build.sh rust-tools
        bash build.sh programs $CLUSTER
        
        # Run tests unless skipped
        if [ "$SKIP_TESTS" != "true" ]; then
            bash build.sh test
        fi
        
        print_success "Development build completed"
        ;;
    
    "ci")
        print_status "CI/CD build pipeline..."
        
        # Lint check
        npm run lint
        
        # Full build
        bash build.sh all $CLUSTER
        
        # Validate
        bash build.sh validate $CLUSTER
        
        print_success "CI/CD pipeline completed"
        ;;
    
    "all"|*)
        print_status "Full build process..."
        
        # Clean
        bash build.sh clean
        
        # Build Rust tools
        bash build.sh rust-tools
        
        # Build programs
        bash build.sh programs $CLUSTER
        
        # Run tests unless skipped
        if [ "$SKIP_TESTS" != "true" ]; then
            bash build.sh test
        fi
        
        print_success "Full build completed successfully"
        ;;
esac

print_status "Build process finished."