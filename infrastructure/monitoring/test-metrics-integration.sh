# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash
# ACGS-1 Phase A3: Enhanced Prometheus Metrics Integration Testing
# Comprehensive validation of custom metrics across all 7 ACGS services

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_FILE="/var/log/acgs/metrics-integration-test.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

info() {
    log "INFO" "${BLUE}$*${NC}"
}

warn() {
    log "WARN" "${YELLOW}$*${NC}"
}

error() {
    log "ERROR" "${RED}$*${NC}"
}

success() {
    log "SUCCESS" "${GREEN}$*${NC}"
}

# Test metrics endpoint availability
test_metrics_endpoint() {
    local service_name=$1
    local port=$2
    
    info "Testing metrics endpoint for $service_name on port $port..."
    
    local url="http://localhost:$port/metrics"
    local response_code
    local response_time
    
    # Test endpoint availability
    if response_code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "$url"); then
        if [ "$response_code" = "200" ]; then
            success "✅ $service_name metrics endpoint is accessible"
            
            # Test response time
            response_time=$(curl -s -o /dev/null -w "%{time_total}" --max-time 10 "$url")
            if (( $(echo "$response_time < 2.0" | bc -l) )); then
                success "✅ $service_name metrics response time: ${response_time}s (target: <2s)"
            else
                warn "⚠️ $service_name metrics response time: ${response_time}s (exceeds 2s target)"
            fi
            
            return 0
        else
            error "❌ $service_name metrics endpoint returned HTTP $response_code"
            return 1
        fi
    else
        error "❌ $service_name metrics endpoint is not accessible"
        return 1
    fi
}

# Test specific metrics presence
test_metrics_content() {
    local service_name=$1
    local port=$2
    
    info "Testing metrics content for $service_name..."
    
    local url="http://localhost:$port/metrics"
    local metrics_content
    
    if metrics_content=$(curl -s --max-time 10 "$url"); then
        # Test for basic ACGS metrics
        local required_metrics=(
            "acgs_requests_total"
            "acgs_request_duration_seconds"
            "acgs_active_connections"
            "acgs_errors_total"
        )
        
        local missing_metrics=()
        for metric in "${required_metrics[@]}"; do
            if ! echo "$metrics_content" | grep -q "$metric"; then
                missing_metrics+=("$metric")
            fi
        done
        
        if [ ${#missing_metrics[@]} -eq 0 ]; then
            success "✅ $service_name has all required basic metrics"
        else
            warn "⚠️ $service_name missing metrics: ${missing_metrics[*]}"
        fi
        
        # Test for service-specific metrics
        case $service_name in
            "auth_service")
                test_auth_specific_metrics "$metrics_content"
                ;;
            "ac_service")
                test_ac_specific_metrics "$metrics_content"
                ;;
            "fv_service")
                test_fv_specific_metrics "$metrics_content"
                ;;
            "gs_service")
                test_gs_specific_metrics "$metrics_content"
                ;;
            "pgc_service")
                test_pgc_specific_metrics "$metrics_content"
                ;;
            "ec_service")
                test_ec_specific_metrics "$metrics_content"
                ;;
            "integrity_service")
                test_integrity_specific_metrics "$metrics_content"
                ;;
        esac
        
        return 0
    else
        error "❌ Failed to retrieve metrics content from $service_name"
        return 1
    fi
}

# Service-specific metric tests
test_auth_specific_metrics() {
    local content=$1
    local auth_metrics=(
        "acgs_auth_session_duration_seconds"
        "acgs_mfa_operations_total"
        "acgs_api_key_operations_total"
    )
    
    for metric in "${auth_metrics[@]}"; do
        if echo "$content" | grep -q "$metric"; then
            success "✅ Auth service metric found: $metric"
        else
            warn "⚠️ Auth service metric missing: $metric"
        fi
    done
}

test_ac_specific_metrics() {
    local content=$1
    local ac_metrics=(
        "acgs_constitutional_ai_processing_seconds"
        "acgs_compliance_validation_latency_seconds"
        "acgs_constitutional_compliance_checks_total"
    )
    
    for metric in "${ac_metrics[@]}"; do
        if echo "$content" | grep -q "$metric"; then
            success "✅ AC service metric found: $metric"
        else
            warn "⚠️ AC service metric missing: $metric"
        fi
    done
}

test_fv_specific_metrics() {
    local content=$1
    local fv_metrics=(
        "acgs_z3_solver_operations_total"
        "acgs_formal_verification_duration_seconds"
    )
    
    for metric in "${fv_metrics[@]}"; do
        if echo "$content" | grep -q "$metric"; then
            success "✅ FV service metric found: $metric"
        else
            warn "⚠️ FV service metric missing: $metric"
        fi
    done
}

test_gs_specific_metrics() {
    local content=$1
    local gs_metrics=(
        "acgs_llm_token_usage_total"
        "acgs_policy_synthesis_operations_total"
        "acgs_multi_model_consensus_operations_total"
    )
    
    for metric in "${gs_metrics[@]}"; do
        if echo "$content" | grep -q "$metric"; then
            success "✅ GS service metric found: $metric"
        else
            warn "⚠️ GS service metric missing: $metric"
        fi
    done
}

test_pgc_specific_metrics() {
    local content=$1
    local pgc_metrics=(
        "acgs_pgc_validation_latency_seconds"
        "acgs_policy_enforcement_actions_total"
    )
    
    for metric in "${pgc_metrics[@]}"; do
        if echo "$content" | grep -q "$metric"; then
            success "✅ PGC service metric found: $metric"
        else
            warn "⚠️ PGC service metric missing: $metric"
        fi
    done
}

test_ec_specific_metrics() {
    local content=$1
    local ec_metrics=(
        "acgs_wina_optimization_score"
        "acgs_evolutionary_computation_iterations_total"
    )
    
    for metric in "${ec_metrics[@]}"; do
        if echo "$content" | grep -q "$metric"; then
            success "✅ EC service metric found: $metric"
        else
            warn "⚠️ EC service metric missing: $metric"
        fi
    done
}

test_integrity_specific_metrics() {
    local content=$1
    local integrity_metrics=(
        "acgs_cryptographic_operations_total"
        "acgs_audit_trail_operations_total"
    )
    
    for metric in "${integrity_metrics[@]}"; do
        if echo "$content" | grep -q "$metric"; then
            success "✅ Integrity service metric found: $metric"
        else
            warn "⚠️ Integrity service metric missing: $metric"
        fi
    done
}

# Test governance workflow metrics
test_governance_workflow_metrics() {
    info "Testing governance workflow metrics across services..."
    
    local workflow_metrics=(
        "acgs_governance_workflow_operations_total"
        "acgs_governance_workflow_duration_seconds"
        "acgs_constitutional_compliance_score"
    )
    
    local services_with_workflows=("ac_service" "gs_service" "pgc_service")
    
    for service in "${services_with_workflows[@]}"; do
        local port=${SERVICES[$service]}
        local url="http://localhost:$port/metrics"
        
        if metrics_content=$(curl -s --max-time 10 "$url" 2>/dev/null); then
            for metric in "${workflow_metrics[@]}"; do
                if echo "$metrics_content" | grep -q "$metric"; then
                    success "✅ $service has governance workflow metric: $metric"
                else
                    warn "⚠️ $service missing governance workflow metric: $metric"
                fi
            done
        else
            warn "⚠️ Could not retrieve metrics from $service for workflow testing"
        fi
    done
}

# Test performance impact
test_performance_impact() {
    info "Testing metrics collection performance impact..."
    
    for service_name in "${!SERVICES[@]}"; do
        local port=${SERVICES[$service_name]}
        local url="http://localhost:$port/health"
        
        # Test multiple requests to measure impact
        local total_time=0
        local request_count=5
        
        for i in $(seq 1 $request_count); do
            if response_time=$(curl -s -o /dev/null -w "%{time_total}" --max-time 5 "$url" 2>/dev/null); then
                total_time=$(echo "$total_time + $response_time" | bc -l)
            else
                warn "⚠️ Failed to measure response time for $service_name request $i"
            fi
        done
        
        if [ $request_count -gt 0 ]; then
            local avg_time=$(echo "scale=3; $total_time / $request_count" | bc -l)
            if (( $(echo "$avg_time < 0.5" | bc -l) )); then
                success "✅ $service_name average response time: ${avg_time}s (target: <500ms)"
            else
                warn "⚠️ $service_name average response time: ${avg_time}s (exceeds 500ms target)"
            fi
        fi
    done
}

# Main test execution
main() {
    info "Starting ACGS-1 Phase A3 Enhanced Prometheus Metrics Integration Testing..."
    
    # Create log directory
    sudo mkdir -p "$(dirname "$LOG_FILE")"
    sudo touch "$LOG_FILE"
    sudo chmod 666 "$LOG_FILE"
    
    local total_tests=0
    local passed_tests=0
    local failed_tests=0
    
    # Test each service
    for service_name in "${!SERVICES[@]}"; do
        local port=${SERVICES[$service_name]}
        
        info "Testing $service_name (port $port)..."
        
        # Test metrics endpoint
        if test_metrics_endpoint "$service_name" "$port"; then
            ((passed_tests++))
        else
            ((failed_tests++))
        fi
        ((total_tests++))
        
        # Test metrics content
        if test_metrics_content "$service_name" "$port"; then
            ((passed_tests++))
        else
            ((failed_tests++))
        fi
        ((total_tests++))
    done
    
    # Test governance workflow metrics
    test_governance_workflow_metrics
    ((total_tests++))
    
    # Test performance impact
    test_performance_impact
    ((total_tests++))
    
    # Summary
    info "Test Summary:"
    info "Total Tests: $total_tests"
    info "Passed: $passed_tests"
    info "Failed: $failed_tests"
    
    local success_rate=$(echo "scale=2; $passed_tests * 100 / $total_tests" | bc -l)
    info "Success Rate: ${success_rate}%"
    
    if [ "$failed_tests" -eq 0 ]; then
        success "🎉 All metrics integration tests passed!"
        return 0
    else
        warn "⚠️ Some tests failed. Check the logs for details."
        return 1
    fi
}

# Execute main function
main "$@"
