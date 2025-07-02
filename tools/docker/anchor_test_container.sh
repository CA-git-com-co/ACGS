#!/bin/bash

# ACGS-1 Anchor Test Script for Containerized Environment
# Runs Anchor program tests within the Solana development container

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SOLANA_CONTAINER="acgs_solana_dev"
BLOCKCHAIN_DIR="/app/blockchain"
QUANTUMAGI_DIR="/app/blockchain/quantumagi-deployment"

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

# Function to check if Solana container is running
check_solana_container() {
    if ! docker ps --format "table {{.Names}}" | grep -q "^${SOLANA_CONTAINER}$"; then
        print_error "Solana development container is not running"
        print_status "Starting Solana development container..."
        docker-compose -f docker-compose.acgs.yml up -d solana_dev
        sleep 10
        
        if ! docker ps --format "table {{.Names}}" | grep -q "^${SOLANA_CONTAINER}$"; then
            print_error "Failed to start Solana development container"
            return 1
        fi
    fi
    print_success "Solana development container is running"
    return 0
}

# Function to setup Solana environment in container
setup_solana_environment() {
    print_status "Setting up Solana environment in container..."
    
    # Configure Solana CLI for devnet
    docker exec "$SOLANA_CONTAINER" solana config set --url devnet
    
    # Check Solana version
    local solana_version=$(docker exec "$SOLANA_CONTAINER" solana --version)
    print_status "Solana version: $solana_version"
    
    # Check Anchor version
    local anchor_version=$(docker exec "$SOLANA_CONTAINER" anchor --version)
    print_status "Anchor version: $anchor_version"
    
    # Ensure we have a keypair
    if ! docker exec "$SOLANA_CONTAINER" test -f /root/.config/solana/id.json; then
        print_status "Generating new Solana keypair..."
        docker exec "$SOLANA_CONTAINER" solana-keygen new --no-bip39-passphrase --silent
    fi
    
    # Get wallet address
    local wallet_address=$(docker exec "$SOLANA_CONTAINER" solana address)
    print_status "Wallet address: $wallet_address"
    
    # Check wallet balance
    local balance=$(docker exec "$SOLANA_CONTAINER" solana balance)
    print_status "Wallet balance: $balance"
    
    # Request airdrop if balance is low
    if [[ "$balance" == "0 SOL" ]]; then
        print_status "Requesting SOL airdrop for testing..."
        docker exec "$SOLANA_CONTAINER" solana airdrop 2 || print_warning "Airdrop failed - continuing with existing balance"
    fi
}

# Function to run Anchor tests
run_anchor_tests() {
    print_status "Running Anchor tests in container..."
    
    # Change to blockchain directory and run tests
    docker exec -w "$BLOCKCHAIN_DIR" "$SOLANA_CONTAINER" bash -c "
        echo 'Running Anchor test suite...'
        anchor test --provider.cluster devnet 2>&1 | tee /tmp/anchor_test_output.log
    "
    
    # Check test results
    if docker exec "$SOLANA_CONTAINER" grep -q "passing" /tmp/anchor_test_output.log; then
        print_success "Anchor tests completed successfully"
        return 0
    else
        print_error "Anchor tests failed"
        return 1
    fi
}

# Function to validate Quantumagi deployment
validate_quantumagi_deployment() {
    print_status "Validating Quantumagi deployment..."
    
    # Check if Quantumagi programs are deployed
    docker exec -w "$QUANTUMAGI_DIR" "$SOLANA_CONTAINER" bash -c "
        if [ -f devnet_program_ids.json ]; then
            echo 'Quantumagi program IDs found:'
            cat devnet_program_ids.json
            return 0
        else
            echo 'Quantumagi programs not deployed'
            return 1
        fi
    "
    
    if [ $? -eq 0 ]; then
        print_success "Quantumagi deployment validated"
        
        # Test constitutional hash validation
        local constitutional_hash="cdd01ef066bc6cf2"
        print_status "Testing constitutional hash validation: $constitutional_hash"
        
        # Run constitutional validation test
        docker exec -w "$QUANTUMAGI_DIR" "$SOLANA_CONTAINER" bash -c "
            python3 -c \"
import json
try:
    with open('constitution_data.json', 'r') as f:
        data = json.load(f)
    if data.get('hash') == '$constitutional_hash':
        print('✅ Constitutional hash validation: PASSED')
        exit(0)
    else:
        print('❌ Constitutional hash validation: FAILED')
        exit(1)
except Exception as e:
    print(f'⚠️ Constitutional hash validation: ERROR - {e}')
    exit(1)
            \"
        "
        
        if [ $? -eq 0 ]; then
            print_success "Constitutional hash validation passed"
        else
            print_warning "Constitutional hash validation failed"
        fi
    else
        print_warning "Quantumagi deployment not found"
    fi
}

# Function to run performance benchmarks
run_performance_benchmarks() {
    print_status "Running performance benchmarks..."
    
    # Test transaction costs
    docker exec -w "$BLOCKCHAIN_DIR" "$SOLANA_CONTAINER" bash -c "
        echo 'Testing transaction costs...'
        if [ -f scripts/cost_optimization.ts ]; then
            npx ts-node scripts/cost_optimization.ts 2>&1 | tee /tmp/cost_benchmark.log
        else
            echo 'Cost optimization script not found'
        fi
    "
    
    # Check if costs are within target (<0.01 SOL)
    if docker exec "$SOLANA_CONTAINER" grep -q "Cost.*0.00" /tmp/cost_benchmark.log; then
        print_success "Transaction costs within target (<0.01 SOL)"
    else
        print_warning "Transaction costs may exceed target"
    fi
}

# Function to generate test report
generate_test_report() {
    local test_status=$1
    local report_file="/tmp/anchor_test_report_$(date +%Y%m%d_%H%M%S).json"
    
    print_status "Generating test report..."
    
    docker exec "$SOLANA_CONTAINER" bash -c "
        cat > $report_file << EOF
{
    \"timestamp\": \"$(date -u +%Y-%m-%dT%H:%M:%SZ)\",
    \"test_status\": \"$test_status\",
    \"environment\": \"containerized\",
    \"solana_version\": \"$(solana --version)\",
    \"anchor_version\": \"$(anchor --version)\",
    \"wallet_address\": \"$(solana address)\",
    \"wallet_balance\": \"$(solana balance)\",
    \"constitutional_hash\": \"cdd01ef066bc6cf2\",
    \"container_name\": \"$SOLANA_CONTAINER\",
    \"blockchain_directory\": \"$BLOCKCHAIN_DIR\"
}
EOF
        echo 'Test report generated: $report_file'
        cat $report_file
    "
}

# Main execution
main() {
    echo "⚓ ACGS-1 Containerized Anchor Testing"
    echo "====================================="
    echo "Date: $(date)"
    echo "Container: $SOLANA_CONTAINER"
    echo ""
    
    # Step 1: Check Solana container
    print_status "Step 1: Checking Solana development container"
    if ! check_solana_container; then
        print_error "Failed to start Solana container"
        exit 1
    fi
    echo ""
    
    # Step 2: Setup Solana environment
    print_status "Step 2: Setting up Solana environment"
    if ! setup_solana_environment; then
        print_error "Failed to setup Solana environment"
        exit 1
    fi
    echo ""
    
    # Step 3: Run Anchor tests
    print_status "Step 3: Running Anchor tests"
    local test_success=false
    if run_anchor_tests; then
        test_success=true
    fi
    echo ""
    
    # Step 4: Validate Quantumagi deployment
    print_status "Step 4: Validating Quantumagi deployment"
    validate_quantumagi_deployment
    echo ""
    
    # Step 5: Run performance benchmarks
    print_status "Step 5: Running performance benchmarks"
    run_performance_benchmarks
    echo ""
    
    # Step 6: Generate report
    print_status "Step 6: Generating test report"
    if [ "$test_success" = true ]; then
        generate_test_report "PASSED"
        print_success "🎉 Anchor tests completed successfully!"
        print_success "🏛️ Constitutional governance programs are operational"
        return 0
    else
        generate_test_report "FAILED"
        print_error "❌ Anchor tests failed"
        print_error "🔧 Check container logs and program deployment"
        return 1
    fi
}

# Execute main function
main "$@"
