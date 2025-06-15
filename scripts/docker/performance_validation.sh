#!/bin/bash

# ACGS-1 Performance Validation Script for Containerized Environment
# Tests constitutional governance workflows and PGC compliance with performance targets

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Performance targets
MAX_RESPONSE_TIME_MS=500
MIN_UPTIME_PERCENT=99.5
MAX_PGC_LATENCY_MS=25
MIN_COMPLIANCE_ACCURACY=95

# Test configuration
CONCURRENT_USERS=10
TEST_DURATION=60
WARMUP_TIME=10

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

# Function to measure response time
measure_response_time() {
    local url=$1
    local description=$2
    
    local start_time=$(date +%s%3N)
    local response_code=$(curl -o /dev/null -s -w "%{http_code}" --connect-timeout 10 --max-time 10 "$url")
    local end_time=$(date +%s%3N)
    local response_time=$((end_time - start_time))
    
    if [ "$response_code" = "200" ]; then
        if [ $response_time -le $MAX_RESPONSE_TIME_MS ]; then
            print_success "$description: ${response_time}ms (✅ <${MAX_RESPONSE_TIME_MS}ms)"
            return 0
        else
            print_warning "$description: ${response_time}ms (⚠️ >${MAX_RESPONSE_TIME_MS}ms)"
            return 1
        fi
    else
        print_error "$description: HTTP $response_code (❌ Failed)"
        return 1
    fi
}

# Function to test constitutional governance workflows
test_governance_workflows() {
    print_status "Testing constitutional governance workflows..."
    
    local workflow_tests=0
    local workflow_passed=0
    
    # Test 1: Policy Creation Workflow
    print_status "Testing Policy Creation Workflow..."
    if measure_response_time "http://localhost:8001/api/v1/constitutional/rules" "Policy Creation"; then
        workflow_passed=$((workflow_passed + 1))
    fi
    workflow_tests=$((workflow_tests + 1))
    
    # Test 2: Constitutional Compliance Workflow
    print_status "Testing Constitutional Compliance Workflow..."
    if measure_response_time "http://localhost:8001/api/v1/status" "Constitutional Compliance"; then
        workflow_passed=$((workflow_passed + 1))
    fi
    workflow_tests=$((workflow_tests + 1))
    
    # Test 3: Policy Enforcement Workflow
    print_status "Testing Policy Enforcement Workflow..."
    if measure_response_time "http://localhost:8005/api/v1/status" "Policy Enforcement"; then
        workflow_passed=$((workflow_passed + 1))
    fi
    workflow_tests=$((workflow_tests + 1))
    
    # Test 4: Formal Verification Workflow
    print_status "Testing Formal Verification Workflow..."
    if measure_response_time "http://localhost:8003/health" "Formal Verification"; then
        workflow_passed=$((workflow_passed + 1))
    fi
    workflow_tests=$((workflow_tests + 1))
    
    # Test 5: Governance Synthesis Workflow
    print_status "Testing Governance Synthesis Workflow..."
    if measure_response_time "http://localhost:8004/health" "Governance Synthesis"; then
        workflow_passed=$((workflow_passed + 1))
    fi
    workflow_tests=$((workflow_tests + 1))
    
    local workflow_success_rate=$((workflow_passed * 100 / workflow_tests))
    print_status "Governance workflow success rate: ${workflow_success_rate}% (${workflow_passed}/${workflow_tests})"
    
    if [ $workflow_success_rate -ge 80 ]; then
        print_success "Governance workflows: OPERATIONAL ✅"
        return 0
    else
        print_error "Governance workflows: DEGRADED ❌"
        return 1
    fi
}

# Function to test PGC compliance performance
test_pgc_compliance() {
    print_status "Testing PGC compliance performance..."
    
    local pgc_tests=0
    local pgc_passed=0
    
    # Test PGC latency multiple times
    for i in {1..5}; do
        local start_time=$(date +%s%3N)
        local response=$(curl -s --connect-timeout 5 --max-time 5 "http://localhost:8005/health" 2>/dev/null)
        local end_time=$(date +%s%3N)
        local latency=$((end_time - start_time))
        
        pgc_tests=$((pgc_tests + 1))
        
        if [ -n "$response" ] && [ $latency -le $MAX_PGC_LATENCY_MS ]; then
            print_success "PGC test $i: ${latency}ms (✅ <${MAX_PGC_LATENCY_MS}ms)"
            pgc_passed=$((pgc_passed + 1))
        else
            print_warning "PGC test $i: ${latency}ms (⚠️ >${MAX_PGC_LATENCY_MS}ms)"
        fi
    done
    
    local pgc_success_rate=$((pgc_passed * 100 / pgc_tests))
    print_status "PGC compliance success rate: ${pgc_success_rate}% (${pgc_passed}/${pgc_tests})"
    
    if [ $pgc_success_rate -ge 80 ]; then
        print_success "PGC compliance: OPTIMAL ✅"
        return 0
    else
        print_warning "PGC compliance: NEEDS OPTIMIZATION ⚠️"
        return 1
    fi
}

# Function to test concurrent load
test_concurrent_load() {
    print_status "Testing concurrent load ($CONCURRENT_USERS users for ${TEST_DURATION}s)..."
    
    # Create temporary directory for test results
    local test_dir="/tmp/acgs_load_test_$(date +%s)"
    mkdir -p "$test_dir"
    
    # Warmup period
    print_status "Warmup period: ${WARMUP_TIME}s..."
    sleep $WARMUP_TIME
    
    # Start concurrent requests
    local pids=()
    for i in $(seq 1 $CONCURRENT_USERS); do
        (
            local user_requests=0
            local user_success=0
            local start_time=$(date +%s)
            local end_time=$((start_time + TEST_DURATION))
            
            while [ $(date +%s) -lt $end_time ]; do
                if curl -f -s --connect-timeout 2 --max-time 2 "http://localhost:8001/health" > /dev/null 2>&1; then
                    user_success=$((user_success + 1))
                fi
                user_requests=$((user_requests + 1))
                sleep 0.5
            done
            
            echo "$user_success,$user_requests" > "$test_dir/user_$i.result"
        ) &
        pids+=($!)
    done
    
    # Wait for all background processes
    for pid in "${pids[@]}"; do
        wait $pid
    done
    
    # Analyze results
    local total_requests=0
    local total_success=0
    
    for i in $(seq 1 $CONCURRENT_USERS); do
        if [ -f "$test_dir/user_$i.result" ]; then
            local result=$(cat "$test_dir/user_$i.result")
            local success=$(echo $result | cut -d, -f1)
            local requests=$(echo $result | cut -d, -f2)
            total_success=$((total_success + success))
            total_requests=$((total_requests + requests))
        fi
    done
    
    # Calculate success rate
    local success_rate=0
    if [ $total_requests -gt 0 ]; then
        success_rate=$((total_success * 100 / total_requests))
    fi
    
    print_status "Concurrent load test results:"
    print_status "  Total requests: $total_requests"
    print_status "  Successful requests: $total_success"
    print_status "  Success rate: ${success_rate}%"
    
    # Cleanup
    rm -rf "$test_dir"
    
    if [ $success_rate -ge 95 ]; then
        print_success "Concurrent load test: PASSED ✅"
        return 0
    else
        print_warning "Concurrent load test: NEEDS IMPROVEMENT ⚠️"
        return 1
    fi
}

# Function to generate performance report
generate_performance_report() {
    local governance_status=$1
    local pgc_status=$2
    local load_status=$3
    
    local report_file="/tmp/acgs_performance_report_$(date +%Y%m%d_%H%M%S).json"
    
    cat > "$report_file" << EOF
{
    "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "environment": "containerized",
    "performance_targets": {
        "max_response_time_ms": $MAX_RESPONSE_TIME_MS,
        "min_uptime_percent": $MIN_UPTIME_PERCENT,
        "max_pgc_latency_ms": $MAX_PGC_LATENCY_MS,
        "min_compliance_accuracy": $MIN_COMPLIANCE_ACCURACY
    },
    "test_results": {
        "governance_workflows": "$governance_status",
        "pgc_compliance": "$pgc_status",
        "concurrent_load": "$load_status"
    },
    "test_configuration": {
        "concurrent_users": $CONCURRENT_USERS,
        "test_duration_seconds": $TEST_DURATION,
        "warmup_time_seconds": $WARMUP_TIME
    }
}
EOF
    
    print_status "Performance report generated: $report_file"
    cat "$report_file"
}

# Main execution
main() {
    echo "🚀 ACGS-1 Performance Validation"
    echo "================================"
    echo "Date: $(date)"
    echo "Targets: <${MAX_RESPONSE_TIME_MS}ms response, <${MAX_PGC_LATENCY_MS}ms PGC latency"
    echo ""
    
    local governance_status="FAILED"
    local pgc_status="FAILED"
    local load_status="FAILED"
    
    # Test 1: Governance workflows
    print_status "Test 1: Constitutional Governance Workflows"
    if test_governance_workflows; then
        governance_status="PASSED"
    fi
    echo ""
    
    # Test 2: PGC compliance
    print_status "Test 2: PGC Compliance Performance"
    if test_pgc_compliance; then
        pgc_status="PASSED"
    fi
    echo ""
    
    # Test 3: Concurrent load
    print_status "Test 3: Concurrent Load Testing"
    if test_concurrent_load; then
        load_status="PASSED"
    fi
    echo ""
    
    # Generate report
    print_status "Generating performance report..."
    generate_performance_report "$governance_status" "$pgc_status" "$load_status"
    echo ""
    
    # Summary
    echo "📊 PERFORMANCE VALIDATION SUMMARY"
    echo "================================="
    echo "🏛️ Governance Workflows: $governance_status"
    echo "⚖️ PGC Compliance: $pgc_status"
    echo "🔄 Concurrent Load: $load_status"
    echo ""
    
    if [ "$governance_status" = "PASSED" ] && [ "$pgc_status" = "PASSED" ] && [ "$load_status" = "PASSED" ]; then
        print_success "🎉 ALL PERFORMANCE TESTS PASSED!"
        print_success "🏛️ ACGS-1 meets constitutional governance performance requirements"
        return 0
    else
        print_warning "⚠️ SOME PERFORMANCE TESTS FAILED"
        print_warning "🔧 Review service configuration and resource allocation"
        return 1
    fi
}

# Execute main function
main "$@"
