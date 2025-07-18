# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash

# ACGS Nano-vLLM Staging Validation Script
# Comprehensive validation of Nano-vLLM deployment against success criteria

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BASE_URL="http://localhost:8100"
PROMETHEUS_URL="http://localhost:9191"
GRAFANA_URL="http://localhost:3100"
LOG_FILE="$PROJECT_ROOT/logs/staging/validation-$(date +%Y%m%d-%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Success criteria
TARGET_RESPONSE_TIME=2.0
MIN_COMPLIANCE_SCORE=0.75
MIN_SUCCESS_RATE=0.95
TARGET_CONCURRENT_REQUESTS=20
TEST_DURATION_MINUTES=30

# Validation results
VALIDATION_RESULTS=()

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
    VALIDATION_RESULTS+=("PASS: $1")
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
    VALIDATION_RESULTS+=("WARN: $1")
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
    VALIDATION_RESULTS+=("FAIL: $1")
}

# Function to check service availability
check_service_availability() {
    log "Checking service availability..."
    
    # Check main service
    if curl -f "$BASE_URL/health" > /dev/null 2>&1; then
        success "Nano-vLLM service is available"
    else
        error "Nano-vLLM service is not available"
        return 1
    fi
    
    # Check Prometheus
    if curl -f "$PROMETHEUS_URL/api/v1/status/config" > /dev/null 2>&1; then
        success "Prometheus monitoring is available"
    else
        error "Prometheus monitoring is not available"
    fi
    
    # Check Grafana
    if curl -f "$GRAFANA_URL/api/health" > /dev/null 2>&1; then
        success "Grafana dashboard is available"
    else
        error "Grafana dashboard is not available"
    fi
}

# Function to test constitutional reasoning endpoints
test_constitutional_endpoints() {
    log "Testing constitutional reasoning endpoints..."
    
    # Test constitutional reasoning endpoint
    local response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/v1/constitutional-reasoning" \
        -H "Content-Type: application/json" \
        -d '{
            "content": "Should we implement a policy that restricts user access?",
            "domain": "governance",
            "reasoning_depth": "standard"
        }')
    
    local http_code="${response: -3}"
    local body="${response%???}"
    
    if [ "$http_code" = "200" ]; then
        success "Constitutional reasoning endpoint is accessible"
        
        # Check compliance score
        local compliance_score=$(echo "$body" | jq -r '.constitutional_compliance // 0')
        if (( $(echo "$compliance_score >= $MIN_COMPLIANCE_SCORE" | bc -l) )); then
            success "Constitutional compliance score meets threshold ($compliance_score >= $MIN_COMPLIANCE_SCORE)"
        else
            error "Constitutional compliance score below threshold ($compliance_score < $MIN_COMPLIANCE_SCORE)"
        fi
    else
        error "Constitutional reasoning endpoint failed (HTTP $http_code)"
    fi
    
    # Test chat completions endpoint
    local chat_response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d '{
            "model": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
            "messages": [{"role": "user", "content": "Hello, test message"}],
            "max_tokens": 50
        }')
    
    local chat_http_code="${chat_response: -3}"
    
    if [ "$chat_http_code" = "200" ]; then
        success "Chat completions endpoint is accessible"
    else
        error "Chat completions endpoint failed (HTTP $chat_http_code)"
    fi
}

# Function to test fallback mechanisms
test_fallback_mechanisms() {
    log "Testing fallback mechanisms..."
    
    # Check if fallback is configured
    local fallback_config=$(docker-compose -f "$PROJECT_ROOT/infrastructure/docker/docker-compose.nano-vllm-staging.yml" config | grep -c "FALLBACK_TO_VLLM=true" || echo "0")
    
    if [ "$fallback_config" -gt 0 ]; then
        success "Fallback to vLLM is configured"
    else
        warning "Fallback to vLLM is not configured"
    fi
    
    # Test graceful degradation
    local health_response=$(curl -s "$BASE_URL/health")
    local fallback_available=$(echo "$health_response" | jq -r '.fallback_available // false')
    
    if [ "$fallback_available" = "true" ]; then
        success "Fallback mechanism is available"
    else
        warning "Fallback mechanism status unknown"
    fi
}

# Function to test GPU support
test_gpu_support() {
    log "Testing GPU support..."
    
    # Check if GPU is detected
    local gpu_info=$(curl -s "$BASE_URL/metrics" 2>/dev/null | grep -c "gpu" || echo "0")
    
    if [ "$gpu_info" -gt 0 ]; then
        success "GPU metrics are available"
    else
        warning "GPU metrics not found - running in CPU mode"
    fi
    
    # Check NVIDIA runtime
    if docker info 2>/dev/null | grep -q nvidia; then
        success "NVIDIA Docker runtime is available"
    else
        warning "NVIDIA Docker runtime not detected"
    fi
}

# Function to run performance validation
run_performance_validation() {
    log "Running performance validation..."
    
    # Run quick performance test
    local start_time=$(date +%s.%N)
    local response=$(curl -s -X POST "$BASE_URL/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d '{
            "model": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
            "messages": [{"role": "user", "content": "Quick performance test"}],
            "max_tokens": 20
        }')
    local end_time=$(date +%s.%N)
    
    local response_time=$(echo "$end_time - $start_time" | bc)
    
    if (( $(echo "$response_time <= $TARGET_RESPONSE_TIME" | bc -l) )); then
        success "Response time meets target ($response_time <= $TARGET_RESPONSE_TIME seconds)"
    else
        warning "Response time exceeds target ($response_time > $TARGET_RESPONSE_TIME seconds)"
    fi
}

# Function to test concurrent request handling
test_concurrent_requests() {
    log "Testing concurrent request handling..."
    
    # Start background requests
    local pids=()
    local success_count=0
    local total_requests=$TARGET_CONCURRENT_REQUESTS
    
    for i in $(seq 1 $total_requests); do
        (
            local response=$(curl -s -w "%{http_code}" -X POST "$BASE_URL/v1/chat/completions" \
                -H "Content-Type: application/json" \
                -d '{
                    "model": "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
                    "messages": [{"role": "user", "content": "Concurrent test '$i'"}],
                    "max_tokens": 10
                }')
            
            local http_code="${response: -3}"
            if [ "$http_code" = "200" ]; then
                echo "SUCCESS"
            else
                echo "FAILED"
            fi
        ) &
        pids+=($!)
    done
    
    # Wait for all requests and count successes
    for pid in "${pids[@]}"; do
        if wait $pid; then
            local result=$(jobs -p | wc -l)
            if [ "$result" = "SUCCESS" ]; then
                ((success_count++))
            fi
        fi
    done
    
    local success_rate=$(echo "scale=2; $success_count / $total_requests" | bc)
    
    if (( $(echo "$success_rate >= $MIN_SUCCESS_RATE" | bc -l) )); then
        success "Concurrent request handling meets target ($success_rate >= $MIN_SUCCESS_RATE)"
    else
        error "Concurrent request handling below target ($success_rate < $MIN_SUCCESS_RATE)"
    fi
}

# Function to check monitoring metrics
check_monitoring_metrics() {
    log "Checking monitoring metrics..."
    
    # Check if metrics are being collected
    local metrics_response=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=up" 2>/dev/null)
    local metrics_count=$(echo "$metrics_response" | jq -r '.data.result | length' 2>/dev/null || echo "0")
    
    if [ "$metrics_count" -gt 0 ]; then
        success "Prometheus metrics are being collected ($metrics_count targets)"
    else
        error "No Prometheus metrics found"
    fi
    
    # Check for constitutional compliance metrics
    local compliance_metrics=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=constitutional_compliance_score" 2>/dev/null)
    local compliance_available=$(echo "$compliance_metrics" | jq -r '.data.result | length' 2>/dev/null || echo "0")
    
    if [ "$compliance_available" -gt 0 ]; then
        success "Constitutional compliance metrics are available"
    else
        warning "Constitutional compliance metrics not found"
    fi
    
    # Check alert rules
    local alert_rules=$(curl -s "$PROMETHEUS_URL/api/v1/rules" 2>/dev/null)
    local rules_count=$(echo "$alert_rules" | jq -r '.data.groups | length' 2>/dev/null || echo "0")
    
    if [ "$rules_count" -gt 0 ]; then
        success "Alert rules are configured ($rules_count rule groups)"
    else
        warning "No alert rules found"
    fi
}

# Function to run load test
run_load_test() {
    log "Running comprehensive load test..."
    
    if [ -f "$PROJECT_ROOT/tests/load/constitutional-ai-load-test.py" ]; then
        log "Starting $TEST_DURATION_MINUTES minute load test with $TARGET_CONCURRENT_REQUESTS concurrent users..."
        
        cd "$PROJECT_ROOT"
        python3 tests/load/constitutional-ai-load-test.py \
            --url "$BASE_URL" \
            --users "$TARGET_CONCURRENT_REQUESTS" \
            --duration "$TEST_DURATION_MINUTES" \
            --output "logs/staging/load-test-results-$(date +%Y%m%d-%H%M%S).json" \
            2>&1 | tee -a "$LOG_FILE"
        
        if [ $? -eq 0 ]; then
            success "Load test completed successfully"
        else
            error "Load test failed"
        fi
    else
        warning "Load test script not found, skipping comprehensive load test"
    fi
}

# Function to generate validation report
generate_validation_report() {
    log "Generating validation report..."
    
    local report_file="$PROJECT_ROOT/logs/staging/validation-report-$(date +%Y%m%d-%H%M%S).txt"
    
    {
        echo "ACGS Nano-vLLM Staging Validation Report"
        echo "========================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        echo "Validation Date: $(date)"
        echo "Environment: Staging"
        echo ""
        
        echo "Success Criteria:"
        echo "- Response Time Target: ≤ $TARGET_RESPONSE_TIME seconds"
        echo "- Compliance Score Target: ≥ $MIN_COMPLIANCE_SCORE"
        echo "- Success Rate Target: ≥ $MIN_SUCCESS_RATE"
        echo "- Concurrent Requests Target: $TARGET_CONCURRENT_REQUESTS"
        echo "- Test Duration: $TEST_DURATION_MINUTES minutes"
        echo ""
        
        echo "Validation Results:"
        echo "==================="
        for result in "${VALIDATION_RESULTS[@]}"; do
            echo "$result"
        done
        echo ""
        
        echo "Service Status:"
        echo "==============="
        curl -s "$BASE_URL/health" | jq '.' 2>/dev/null || echo "Health check failed"
        echo ""
        
        echo "System Metrics:"
        echo "==============="
        curl -s "$BASE_URL/metrics" 2>/dev/null | head -20 || echo "Metrics not available"
        
    } > "$report_file"
    
    success "Validation report generated: $report_file"
}

# Main validation function
main() {
    log "Starting ACGS Nano-vLLM staging validation..."
    
    # Create logs directory
    mkdir -p "$PROJECT_ROOT/logs/staging"
    
    # Run validation tests
    check_service_availability
    test_constitutional_endpoints
    test_fallback_mechanisms
    test_gpu_support
    run_performance_validation
    test_concurrent_requests
    check_monitoring_metrics
    
    # Run comprehensive load test if requested
    if [ "${1:-}" = "--load-test" ]; then
        run_load_test
    else
        log "Skipping comprehensive load test (use --load-test to include)"
    fi
    
    generate_validation_report
    
    # Summary
    local pass_count=$(printf '%s\n' "${VALIDATION_RESULTS[@]}" | grep -c "PASS:" || echo "0")
    local warn_count=$(printf '%s\n' "${VALIDATION_RESULTS[@]}" | grep -c "WARN:" || echo "0")
    local fail_count=$(printf '%s\n' "${VALIDATION_RESULTS[@]}" | grep -c "FAIL:" || echo "0")
    local total_count=${#VALIDATION_RESULTS[@]}
    
    echo ""
    echo "========================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "VALIDATION SUMMARY"
    echo "========================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "Total Tests: $total_count"
    echo "Passed: $pass_count"
    echo "Warnings: $warn_count"
    echo "Failed: $fail_count"
    echo ""
    
    if [ "$fail_count" -eq 0 ]; then
        success "All critical validations passed!"
        if [ "$warn_count" -gt 0 ]; then
            warning "$warn_count warnings found - review recommended"
        fi
        exit 0
    else
        error "$fail_count critical validations failed"
        exit 1
    fi
}

# Run main function
main "$@"
