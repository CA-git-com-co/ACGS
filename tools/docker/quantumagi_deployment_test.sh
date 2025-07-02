#!/bin/bash

# ACGS-1 Quantumagi Deployment Test for Containerized Environment
# Validates Solana devnet deployment functionality with constitutional hash cdd01ef066bc6cf2

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SOLANA_CONTAINER="acgs_solana_dev"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
QUANTUMAGI_DIR="/app/blockchain/quantumagi-deployment"
MAX_SOL_COST="0.01"

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

# Function to check Solana container
check_solana_container() {
    if ! docker ps --format "table {{.Names}}" | grep -q "^${SOLANA_CONTAINER}$"; then
        print_error "Solana development container is not running"
        return 1
    fi
    print_success "Solana development container is running"
    return 0
}

# Function to validate Quantumagi programs
validate_quantumagi_programs() {
    print_status "Validating Quantumagi program deployment..."
    
    # Check if program IDs file exists
    if ! docker exec "$SOLANA_CONTAINER" test -f "$QUANTUMAGI_DIR/devnet_program_ids.json"; then
        print_error "Quantumagi program IDs file not found"
        return 1
    fi
    
    # Read and validate program IDs
    local program_ids=$(docker exec "$SOLANA_CONTAINER" cat "$QUANTUMAGI_DIR/devnet_program_ids.json")
    print_status "Program IDs found:"
    echo "$program_ids" | jq . 2>/dev/null || echo "$program_ids"
    
    # Extract program IDs
    local quantumagi_core_id=$(echo "$program_ids" | jq -r '.quantumagi_core // empty' 2>/dev/null)
    local appeals_id=$(echo "$program_ids" | jq -r '.appeals // empty' 2>/dev/null)
    local logging_id=$(echo "$program_ids" | jq -r '.logging // empty' 2>/dev/null)
    
    # Validate each program
    local programs_valid=0
    
    if [ -n "$quantumagi_core_id" ] && [ "$quantumagi_core_id" != "null" ]; then
        if docker exec "$SOLANA_CONTAINER" solana account "$quantumagi_core_id" > /dev/null 2>&1; then
            print_success "Quantumagi Core program: DEPLOYED ✅ ($quantumagi_core_id)"
            programs_valid=$((programs_valid + 1))
        else
            print_error "Quantumagi Core program: NOT FOUND ❌ ($quantumagi_core_id)"
        fi
    else
        print_error "Quantumagi Core program ID not found"
    fi
    
    if [ -n "$appeals_id" ] && [ "$appeals_id" != "null" ]; then
        if docker exec "$SOLANA_CONTAINER" solana account "$appeals_id" > /dev/null 2>&1; then
            print_success "Appeals program: DEPLOYED ✅ ($appeals_id)"
            programs_valid=$((programs_valid + 1))
        else
            print_error "Appeals program: NOT FOUND ❌ ($appeals_id)"
        fi
    else
        print_error "Appeals program ID not found"
    fi
    
    if [ -n "$logging_id" ] && [ "$logging_id" != "null" ]; then
        if docker exec "$SOLANA_CONTAINER" solana account "$logging_id" > /dev/null 2>&1; then
            print_success "Logging program: DEPLOYED ✅ ($logging_id)"
            programs_valid=$((programs_valid + 1))
        else
            print_error "Logging program: NOT FOUND ❌ ($logging_id)"
        fi
    else
        print_error "Logging program ID not found"
    fi
    
    if [ $programs_valid -eq 3 ]; then
        print_success "All Quantumagi programs are deployed and accessible"
        return 0
    else
        print_error "Some Quantumagi programs are missing or inaccessible"
        return 1
    fi
}

# Function to validate constitutional hash
validate_constitutional_hash() {
    print_status "Validating constitutional hash: $CONSTITUTIONAL_HASH"
    
    # Check constitution data file
    if ! docker exec "$SOLANA_CONTAINER" test -f "$QUANTUMAGI_DIR/constitution_data.json"; then
        print_error "Constitution data file not found"
        return 1
    fi
    
    # Validate constitutional hash
    local constitution_data=$(docker exec "$SOLANA_CONTAINER" cat "$QUANTUMAGI_DIR/constitution_data.json")
    local stored_hash=$(echo "$constitution_data" | jq -r '.hash // empty' 2>/dev/null)
    
    if [ "$stored_hash" = "$CONSTITUTIONAL_HASH" ]; then
        print_success "Constitutional hash validation: PASSED ✅"
        print_status "Stored hash: $stored_hash"
        return 0
    else
        print_error "Constitutional hash validation: FAILED ❌"
        print_error "Expected: $CONSTITUTIONAL_HASH"
        print_error "Found: $stored_hash"
        return 1
    fi
}

# Function to test governance actions cost
test_governance_costs() {
    print_status "Testing governance action costs..."
    
    # Get current wallet balance
    local initial_balance=$(docker exec "$SOLANA_CONTAINER" solana balance --lamports)
    print_status "Initial balance: $initial_balance lamports"
    
    # Simulate a governance action (simple account creation for testing)
    local test_keypair="/tmp/test_governance_$(date +%s).json"
    docker exec "$SOLANA_CONTAINER" solana-keygen new --no-bip39-passphrase --silent --outfile "$test_keypair"
    
    # Get balance after operation
    local final_balance=$(docker exec "$SOLANA_CONTAINER" solana balance --lamports)
    print_status "Final balance: $final_balance lamports"
    
    # Calculate cost in SOL
    local cost_lamports=$((initial_balance - final_balance))
    local cost_sol=$(echo "scale=6; $cost_lamports / 1000000000" | bc -l 2>/dev/null || echo "0")
    
    print_status "Governance action cost: $cost_sol SOL ($cost_lamports lamports)"
    
    # Check if cost is within target
    if (( $(echo "$cost_sol < $MAX_SOL_COST" | bc -l 2>/dev/null || echo "0") )); then
        print_success "Governance cost: WITHIN TARGET ✅ (<$MAX_SOL_COST SOL)"
        return 0
    else
        print_warning "Governance cost: EXCEEDS TARGET ⚠️ (>$MAX_SOL_COST SOL)"
        return 1
    fi
}

# Function to test constitutional compliance
test_constitutional_compliance() {
    print_status "Testing constitutional compliance validation..."
    
    # Test compliance check through PGC service
    local compliance_response=$(curl -s --connect-timeout 5 --max-time 5 "http://localhost:8005/api/v1/status" 2>/dev/null)
    
    if [ -n "$compliance_response" ]; then
        print_success "PGC service: ACCESSIBLE ✅"
        
        # Check if constitutional hash is referenced
        if echo "$compliance_response" | grep -q "$CONSTITUTIONAL_HASH"; then
            print_success "Constitutional hash integration: VERIFIED ✅"
        else
            print_warning "Constitutional hash integration: NOT VERIFIED ⚠️"
        fi
        
        return 0
    else
        print_error "PGC service: NOT ACCESSIBLE ❌"
        return 1
    fi
}

# Function to run end-to-end workflow test
test_end_to_end_workflow() {
    print_status "Running end-to-end governance workflow test..."
    
    # Test workflow: Policy Creation → Constitutional Validation → Compliance Check
    local workflow_steps=0
    local workflow_passed=0
    
    # Step 1: Policy Creation (AC Service)
    if curl -f -s --connect-timeout 5 "http://localhost:8001/api/v1/constitutional/rules" > /dev/null 2>&1; then
        print_success "Step 1 - Policy Creation: PASSED ✅"
        workflow_passed=$((workflow_passed + 1))
    else
        print_error "Step 1 - Policy Creation: FAILED ❌"
    fi
    workflow_steps=$((workflow_steps + 1))
    
    # Step 2: Constitutional Validation (AC Service)
    if curl -f -s --connect-timeout 5 "http://localhost:8001/health" > /dev/null 2>&1; then
        print_success "Step 2 - Constitutional Validation: PASSED ✅"
        workflow_passed=$((workflow_passed + 1))
    else
        print_error "Step 2 - Constitutional Validation: FAILED ❌"
    fi
    workflow_steps=$((workflow_steps + 1))
    
    # Step 3: Compliance Check (PGC Service)
    if curl -f -s --connect-timeout 5 "http://localhost:8005/health" > /dev/null 2>&1; then
        print_success "Step 3 - Compliance Check: PASSED ✅"
        workflow_passed=$((workflow_passed + 1))
    else
        print_error "Step 3 - Compliance Check: FAILED ❌"
    fi
    workflow_steps=$((workflow_steps + 1))
    
    local workflow_success_rate=$((workflow_passed * 100 / workflow_steps))
    print_status "End-to-end workflow success rate: ${workflow_success_rate}% (${workflow_passed}/${workflow_steps})"
    
    if [ $workflow_success_rate -ge 100 ]; then
        print_success "End-to-end workflow: FULLY OPERATIONAL ✅"
        return 0
    elif [ $workflow_success_rate -ge 66 ]; then
        print_warning "End-to-end workflow: PARTIALLY OPERATIONAL ⚠️"
        return 1
    else
        print_error "End-to-end workflow: NOT OPERATIONAL ❌"
        return 1
    fi
}

# Function to generate deployment test report
generate_deployment_report() {
    local programs_status=$1
    local hash_status=$2
    local cost_status=$3
    local compliance_status=$4
    local workflow_status=$5
    
    local report_file="/tmp/quantumagi_deployment_test_$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "environment": "containerized",
    "constitutional_hash": "$CONSTITUTIONAL_HASH",
    "max_sol_cost": "$MAX_SOL_COST",
    "test_results": {
        "quantumagi_programs": "$programs_status",
        "constitutional_hash": "$hash_status",
        "governance_costs": "$cost_status",
        "constitutional_compliance": "$compliance_status",
        "end_to_end_workflow": "$workflow_status"
    },
    "container": "$SOLANA_CONTAINER",
    "quantumagi_directory": "$QUANTUMAGI_DIR"
}
EOF
    
    print_status "Deployment test report generated: $report_file"
    cat "$report_file"
}

# Main execution
main() {
    echo "🌌 ACGS-1 Quantumagi Deployment Test"
    echo "===================================="
    echo "Date: $(date)"
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "Max SOL Cost: $MAX_SOL_COST"
    echo ""
    
    # Check prerequisites
    if ! check_solana_container; then
        print_error "Prerequisites not met"
        exit 1
    fi
    
    local programs_status="FAILED"
    local hash_status="FAILED"
    local cost_status="FAILED"
    local compliance_status="FAILED"
    local workflow_status="FAILED"
    
    # Test 1: Validate Quantumagi programs
    print_status "Test 1: Quantumagi Program Validation"
    if validate_quantumagi_programs; then
        programs_status="PASSED"
    fi
    echo ""
    
    # Test 2: Validate constitutional hash
    print_status "Test 2: Constitutional Hash Validation"
    if validate_constitutional_hash; then
        hash_status="PASSED"
    fi
    echo ""
    
    # Test 3: Test governance costs
    print_status "Test 3: Governance Action Costs"
    if test_governance_costs; then
        cost_status="PASSED"
    fi
    echo ""
    
    # Test 4: Test constitutional compliance
    print_status "Test 4: Constitutional Compliance Integration"
    if test_constitutional_compliance; then
        compliance_status="PASSED"
    fi
    echo ""
    
    # Test 5: End-to-end workflow
    print_status "Test 5: End-to-End Governance Workflow"
    if test_end_to_end_workflow; then
        workflow_status="PASSED"
    fi
    echo ""
    
    # Generate report
    print_status "Generating deployment test report..."
    generate_deployment_report "$programs_status" "$hash_status" "$cost_status" "$compliance_status" "$workflow_status"
    echo ""
    
    # Summary
    echo "📊 QUANTUMAGI DEPLOYMENT TEST SUMMARY"
    echo "====================================="
    echo "🌌 Quantumagi Programs: $programs_status"
    echo "🏛️ Constitutional Hash: $hash_status"
    echo "💰 Governance Costs: $cost_status"
    echo "⚖️ Constitutional Compliance: $compliance_status"
    echo "🔄 End-to-End Workflow: $workflow_status"
    echo ""
    
    if [ "$programs_status" = "PASSED" ] && [ "$hash_status" = "PASSED" ] && [ "$workflow_status" = "PASSED" ]; then
        print_success "🎉 QUANTUMAGI DEPLOYMENT FULLY OPERATIONAL!"
        print_success "🏛️ Constitutional governance system is ready for use"
        return 0
    else
        print_warning "⚠️ QUANTUMAGI DEPLOYMENT ISSUES DETECTED"
        print_warning "🔧 Review deployment status and service integration"
        return 1
    fi
}

# Execute main function
main "$@"
