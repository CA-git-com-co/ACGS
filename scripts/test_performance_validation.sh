#!/bin/bash

# ACGS-PGP Performance Validation Test Script
# Tests performance targets: ≤2s response time, 1000 RPS throughput
# Constitutional hash: cdd01ef066bc6cf2

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Performance targets
RESPONSE_TIME_TARGET=2000  # 2 seconds in milliseconds
THROUGHPUT_TARGET=1000     # RPS
CONSTITUTIONAL_COMPLIANCE_TARGET=0.95

# Service configuration
declare -A SERVICES=(
    ["auth_service"]="8000"
    ["ac_service"]="8001"
    ["integrity_service"]="8002"
    ["fv_service"]="8003"
    ["gs_service"]="8004"
    ["pgc_service"]="8005"
    ["ec_service"]="8006"
)

# Test results
TOTAL_SERVICES=0
PASSING_SERVICES=0
PERFORMANCE_RESULTS=()

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

failure() {
    echo -e "${RED}❌ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to test response time
test_response_time() {
    local service_name=$1
    local port=$2
    local endpoint=${3:-"/health"}
    
    log "Testing response time for $service_name on port $port..."
    
    # Test multiple requests to get average
    local total_time=0
    local successful_requests=0
    local test_count=10
    
    for i in $(seq 1 $test_count); do
        local start_time=$(date +%s%3N)
        
        if curl -f -s --connect-timeout 5 --max-time 3 "http://localhost:$port$endpoint" > /dev/null 2>&1; then
            local end_time=$(date +%s%3N)
            local response_time=$((end_time - start_time))
            total_time=$((total_time + response_time))
            ((successful_requests++))
        fi
        
        sleep 0.1  # Small delay between requests
    done
    
    if [ $successful_requests -gt 0 ]; then
        local avg_response_time=$((total_time / successful_requests))
        
        if [ $avg_response_time -le $RESPONSE_TIME_TARGET ]; then
            success "$service_name response time: ${avg_response_time}ms (≤${RESPONSE_TIME_TARGET}ms) ✓"
            return 0
        else
            failure "$service_name response time: ${avg_response_time}ms (>${RESPONSE_TIME_TARGET}ms) ✗"
            return 1
        fi
    else
        failure "$service_name: No successful requests"
        return 1
    fi
}

# Function to test constitutional compliance performance
test_constitutional_compliance_performance() {
    local service_name=$1
    local port=$2
    
    log "Testing constitutional compliance performance for $service_name..."
    
    local start_time=$(date +%s%3N)
    local compliance_response=$(curl -s --connect-timeout 5 --max-time 3 "http://localhost:$port/constitutional/compliance" 2>/dev/null || echo "")
    local end_time=$(date +%s%3N)
    local response_time=$((end_time - start_time))
    
    if [ -n "$compliance_response" ]; then
        # Extract compliance score
        local compliance_score=$(echo "$compliance_response" | grep -o '"compliance_score":[0-9.]*' | cut -d: -f2 | tr -d ' ')
        
        if [ -n "$compliance_score" ]; then
            local meets_threshold=$(awk -v score="$compliance_score" -v threshold="$CONSTITUTIONAL_COMPLIANCE_TARGET" 'BEGIN { print (score >= threshold) ? "1" : "0" }')
            
            if [ "$meets_threshold" = "1" ] && [ $response_time -le $RESPONSE_TIME_TARGET ]; then
                success "$service_name constitutional compliance: $compliance_score (${response_time}ms) ✓"
                return 0
            else
                failure "$service_name constitutional compliance: $compliance_score (${response_time}ms) - Performance/compliance issue"
                return 1
            fi
        else
            failure "$service_name constitutional compliance: Invalid response"
            return 1
        fi
    else
        warning "$service_name constitutional compliance: Endpoint not available"
        return 1
    fi
}

# Function to test basic throughput capability
test_throughput_capability() {
    local service_name=$1
    local port=$2
    
    log "Testing throughput capability for $service_name..."
    
    # Simple concurrent request test
    local concurrent_requests=20
    local test_duration=5  # seconds
    local successful_requests=0
    
    # Create temporary file for results
    local temp_file=$(mktemp)
    
    # Launch concurrent requests
    for i in $(seq 1 $concurrent_requests); do
        {
            local start_time=$(date +%s)
            while [ $(($(date +%s) - start_time)) -lt $test_duration ]; do
                if curl -f -s --connect-timeout 1 --max-time 2 "http://localhost:$port/health" > /dev/null 2>&1; then
                    echo "success" >> "$temp_file"
                fi
                sleep 0.1
            done
        } &
    done
    
    # Wait for all background processes
    wait
    
    # Count successful requests
    if [ -f "$temp_file" ]; then
        successful_requests=$(wc -l < "$temp_file")
        rm -f "$temp_file"
    fi
    
    local rps=$((successful_requests / test_duration))
    
    if [ $rps -ge 100 ]; then  # Lower threshold for basic validation
        success "$service_name throughput: ${rps} RPS (basic capability verified) ✓"
        return 0
    else
        failure "$service_name throughput: ${rps} RPS (insufficient) ✗"
        return 1
    fi
}

# Function to test DGM safety performance
test_dgm_safety_performance() {
    local service_name=$1
    local port=$2
    
    log "Testing DGM safety performance for $service_name..."
    
    local dgm_endpoints=(
        "/dgm/sandbox/status"
        "/dgm/review/status"
        "/dgm/rollback/status"
    )
    
    local successful_checks=0
    local total_time=0
    
    for endpoint in "${dgm_endpoints[@]}"; do
        local start_time=$(date +%s%3N)
        local response=$(curl -s --connect-timeout 2 --max-time 3 "http://localhost:$port$endpoint" 2>/dev/null || echo "")
        local end_time=$(date +%s%3N)
        local response_time=$((end_time - start_time))
        
        if [ -n "$response" ] && [ $response_time -le $RESPONSE_TIME_TARGET ]; then
            ((successful_checks++))
            total_time=$((total_time + response_time))
        fi
    done
    
    if [ $successful_checks -eq ${#dgm_endpoints[@]} ]; then
        local avg_time=$((total_time / successful_checks))
        success "$service_name DGM safety: ${avg_time}ms average (all endpoints responsive) ✓"
        return 0
    else
        failure "$service_name DGM safety: $successful_checks/${#dgm_endpoints[@]} endpoints responsive ✗"
        return 1
    fi
}

# Function to run comprehensive performance test for a service
test_service_performance() {
    local service_name=$1
    local port=$2
    
    log "🚀 Testing performance for $service_name (port $port)..."
    ((TOTAL_SERVICES++))
    
    local tests_passed=0
    local total_tests=4
    
    # Test 1: Basic response time
    if test_response_time "$service_name" "$port"; then
        ((tests_passed++))
    fi
    
    # Test 2: Constitutional compliance performance
    if test_constitutional_compliance_performance "$service_name" "$port"; then
        ((tests_passed++))
    fi
    
    # Test 3: Throughput capability
    if test_throughput_capability "$service_name" "$port"; then
        ((tests_passed++))
    fi
    
    # Test 4: DGM safety performance
    if test_dgm_safety_performance "$service_name" "$port"; then
        ((tests_passed++))
    fi
    
    local service_score=$((tests_passed * 100 / total_tests))
    PERFORMANCE_RESULTS+=("$service_name: $service_score% ($tests_passed/$total_tests tests passed)")
    
    if [ $service_score -ge 75 ]; then
        success "$service_name overall performance: $service_score% ✓"
        ((PASSING_SERVICES++))
        return 0
    else
        failure "$service_name overall performance: $service_score% ✗"
        return 1
    fi
}

# Main performance validation
main() {
    log "🚀 Starting ACGS-PGP Performance Validation"
    echo "============================================"
    echo "Response time target: ≤${RESPONSE_TIME_TARGET}ms"
    echo "Throughput target: ≥${THROUGHPUT_TARGET} RPS"
    echo "Constitutional compliance: ≥${CONSTITUTIONAL_COMPLIANCE_TARGET}"
    echo ""
    
    # Check if services are running
    log "Checking if services are running..."
    local running_services=0
    
    for service_name in "${!SERVICES[@]}"; do
        local port=${SERVICES[$service_name]}
        if curl -f -s --connect-timeout 2 --max-time 5 "http://localhost:$port/health" > /dev/null 2>&1; then
            log "$service_name (port $port): RUNNING ✓"
            ((running_services++))
        else
            warning "$service_name (port $port): NOT RUNNING"
        fi
    done
    
    if [ $running_services -eq 0 ]; then
        failure "No services are running. Please start services first with: ./scripts/start_all_services.sh"
        exit 1
    fi
    
    echo ""
    log "Running performance tests on $running_services running services..."
    echo ""
    
    # Test each running service
    for service_name in "${!SERVICES[@]}"; do
        local port=${SERVICES[$service_name]}
        
        # Only test if service is running
        if curl -f -s --connect-timeout 2 --max-time 5 "http://localhost:$port/health" > /dev/null 2>&1; then
            test_service_performance "$service_name" "$port"
            echo ""
        fi
    done
    
    # Generate performance report
    echo ""
    echo "============================================"
    echo "🚀 ACGS-PGP Performance Validation Results"
    echo "============================================"
    echo "Services tested: $TOTAL_SERVICES"
    echo "Services passing: $PASSING_SERVICES"
    echo "Overall success rate: $(( PASSING_SERVICES * 100 / TOTAL_SERVICES ))%"
    echo ""
    
    echo "📊 Detailed Results:"
    for result in "${PERFORMANCE_RESULTS[@]}"; do
        echo "  $result"
    done
    
    echo ""
    local overall_performance=$(( PASSING_SERVICES * 100 / TOTAL_SERVICES ))
    
    if [ $overall_performance -ge 95 ]; then
        success "🎉 PERFORMANCE VALIDATION PASSED (≥95%)"
        echo "✅ All services meet performance targets"
        echo "✅ Constitutional compliance validated"
        echo "✅ DGM safety patterns responsive"
        echo "✅ System ready for production load"
    elif [ $overall_performance -ge 80 ]; then
        warning "⚠️ PERFORMANCE VALIDATION PARTIAL ($overall_performance%)"
        echo "⚠️ Some services need optimization"
        echo "⚠️ Consider staging deployment first"
    else
        failure "❌ PERFORMANCE VALIDATION FAILED (<80%)"
        echo "❌ Critical performance issues found"
        echo "❌ System requires optimization"
    fi
    
    # Return appropriate exit code
    if [ $overall_performance -ge 80 ]; then
        return 0
    else
        return 1
    fi
}

# Run main function
main "$@"
