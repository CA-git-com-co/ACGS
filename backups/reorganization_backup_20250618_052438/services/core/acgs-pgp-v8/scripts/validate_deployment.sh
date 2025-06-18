#!/bin/bash

# ACGS-PGP v8 Deployment Validation Script
# Comprehensive validation of deployment readiness and operational status

set -euo pipefail

# Configuration
SERVICE_NAME="acgs-pgp-v8"
SERVICE_PORT="8010"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
VALIDATION_TIMEOUT=300

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Validation results tracking
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNING_CHECKS=0

# Track validation result
track_result() {
    local result=$1
    local message=$2
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    case $result in
        "PASS")
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            log_success "$message"
            ;;
        "FAIL")
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            log_error "$message"
            ;;
        "WARN")
            WARNING_CHECKS=$((WARNING_CHECKS + 1))
            log_warning "$message"
            ;;
    esac
}

# Check if service is running
check_service_running() {
    log_info "Checking if ACGS-PGP v8 service is running..."
    
    if curl -s -f "http://localhost:$SERVICE_PORT/health" >/dev/null 2>&1; then
        track_result "PASS" "Service is responding on port $SERVICE_PORT"
    else
        track_result "FAIL" "Service is not responding on port $SERVICE_PORT"
        return 1
    fi
}

# Validate health endpoint
validate_health_endpoint() {
    log_info "Validating health endpoint..."
    
    local health_response
    if health_response=$(curl -s "http://localhost:$SERVICE_PORT/health" 2>/dev/null); then
        # Check if response is valid JSON
        if echo "$health_response" | jq . >/dev/null 2>&1; then
            local status=$(echo "$health_response" | jq -r '.status // "unknown"')
            local service=$(echo "$health_response" | jq -r '.service // "unknown"')
            local constitutional_hash=$(echo "$health_response" | jq -r '.constitutional_hash // "unknown"')
            
            if [ "$status" = "healthy" ]; then
                track_result "PASS" "Health status is healthy"
            else
                track_result "FAIL" "Health status is $status (expected: healthy)"
            fi
            
            if [ "$service" = "acgs-pgp-v8" ]; then
                track_result "PASS" "Service name is correct"
            else
                track_result "FAIL" "Service name is $service (expected: acgs-pgp-v8)"
            fi
            
            if [ "$constitutional_hash" = "$CONSTITUTIONAL_HASH" ]; then
                track_result "PASS" "Constitutional hash is correct"
            else
                track_result "FAIL" "Constitutional hash is $constitutional_hash (expected: $CONSTITUTIONAL_HASH)"
            fi
        else
            track_result "FAIL" "Health endpoint returned invalid JSON"
        fi
    else
        track_result "FAIL" "Health endpoint is not accessible"
    fi
}

# Validate metrics endpoint
validate_metrics_endpoint() {
    log_info "Validating metrics endpoint..."
    
    local metrics_response
    if metrics_response=$(curl -s "http://localhost:$SERVICE_PORT/metrics" 2>/dev/null); then
        # Check for key metrics
        local required_metrics=(
            "acgs_pgp_v8_system_uptime_seconds"
            "acgs_pgp_v8_policy_generation_requests_total"
            "acgs_pgp_v8_component_health"
            "acgs_pgp_v8_constitutional_validations_total"
        )
        
        local missing_metrics=()
        for metric in "${required_metrics[@]}"; do
            if echo "$metrics_response" | grep -q "$metric"; then
                track_result "PASS" "Metric $metric is present"
            else
                missing_metrics+=("$metric")
                track_result "FAIL" "Metric $metric is missing"
            fi
        done
        
        if [ ${#missing_metrics[@]} -eq 0 ]; then
            track_result "PASS" "All required metrics are present"
        fi
    else
        track_result "FAIL" "Metrics endpoint is not accessible"
    fi
}

# Validate system status endpoint
validate_system_status() {
    log_info "Validating system status endpoint..."
    
    # Note: This endpoint requires authentication, so we expect 401 if no token provided
    local status_code
    if status_code=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$SERVICE_PORT/api/v1/status" 2>/dev/null); then
        if [ "$status_code" = "401" ]; then
            track_result "PASS" "System status endpoint requires authentication (expected)"
        elif [ "$status_code" = "200" ]; then
            track_result "PASS" "System status endpoint is accessible"
        else
            track_result "WARN" "System status endpoint returned status code $status_code"
        fi
    else
        track_result "FAIL" "System status endpoint is not accessible"
    fi
}

# Check component health
check_component_health() {
    log_info "Checking component health..."
    
    local health_response
    if health_response=$(curl -s "http://localhost:$SERVICE_PORT/health" 2>/dev/null); then
        if echo "$health_response" | jq . >/dev/null 2>&1; then
            local components=$(echo "$health_response" | jq -r '.components // {}')
            
            # Check each component
            local component_names=("generation_engine" "stabilizer_environment" "diagnostic_engine" "cache_manager")
            
            for component in "${component_names[@]}"; do
                local component_status=$(echo "$components" | jq -r ".$component.status // \"unknown\"")
                
                if [ "$component_status" = "healthy" ]; then
                    track_result "PASS" "Component $component is healthy"
                elif [ "$component_status" = "not_initialized" ]; then
                    track_result "WARN" "Component $component is not initialized"
                else
                    track_result "FAIL" "Component $component status is $component_status"
                fi
            done
        fi
    fi
}

# Check dependencies
check_dependencies() {
    log_info "Checking ACGS-1 service dependencies..."
    
    local services=(
        "8000:Auth Service"
        "8004:GS Service"
        "8005:PGC Service"
    )
    
    for service in "${services[@]}"; do
        local port="${service%%:*}"
        local name="${service##*:}"
        
        if curl -s -f "http://localhost:${port}/health" >/dev/null 2>&1; then
            track_result "PASS" "$name (port $port) is healthy"
        else
            track_result "WARN" "$name (port $port) is not responding"
        fi
    done
}

# Check database connectivity
check_database() {
    log_info "Checking database connectivity..."
    
    if command -v psql >/dev/null 2>&1; then
        local db_url="${DATABASE_URL:-postgresql://acgs_user:acgs_password@localhost:5432/acgs_db}"
        
        if psql "$db_url" -c "SELECT 1;" >/dev/null 2>&1; then
            track_result "PASS" "Database connection successful"
        else
            track_result "FAIL" "Database connection failed"
        fi
    else
        track_result "WARN" "psql not available, skipping database check"
    fi
}

# Check Redis connectivity
check_redis() {
    log_info "Checking Redis connectivity..."
    
    if command -v redis-cli >/dev/null 2>&1; then
        if redis-cli ping >/dev/null 2>&1; then
            track_result "PASS" "Redis connection successful"
        else
            track_result "FAIL" "Redis connection failed"
        fi
    else
        track_result "WARN" "redis-cli not available, skipping Redis check"
    fi
}

# Check Docker container (if running in Docker)
check_docker_container() {
    log_info "Checking Docker container status..."
    
    if command -v docker >/dev/null 2>&1; then
        if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$SERVICE_NAME"; then
            local container_status=$(docker ps --format "{{.Status}}" --filter "name=$SERVICE_NAME")
            track_result "PASS" "Docker container is running: $container_status"
        else
            track_result "WARN" "Docker container not found (may be running natively)"
        fi
    else
        track_result "WARN" "Docker not available, skipping container check"
    fi
}

# Performance validation
validate_performance() {
    log_info "Validating performance..."
    
    # Test response time
    local start_time=$(date +%s%N)
    if curl -s "http://localhost:$SERVICE_PORT/health" >/dev/null 2>&1; then
        local end_time=$(date +%s%N)
        local response_time_ms=$(( (end_time - start_time) / 1000000 ))
        
        if [ $response_time_ms -lt 500 ]; then
            track_result "PASS" "Response time is ${response_time_ms}ms (target: <500ms)"
        else
            track_result "WARN" "Response time is ${response_time_ms}ms (target: <500ms)"
        fi
    else
        track_result "FAIL" "Performance test failed - service not responding"
    fi
}

# Security validation
validate_security() {
    log_info "Validating security configuration..."
    
    # Check security headers
    local headers
    if headers=$(curl -s -I "http://localhost:$SERVICE_PORT/health" 2>/dev/null); then
        local security_headers=(
            "X-Content-Type-Options"
            "X-Frame-Options"
            "X-Constitutional-Hash"
            "X-ACGS-Service"
        )
        
        for header in "${security_headers[@]}"; do
            if echo "$headers" | grep -qi "$header"; then
                track_result "PASS" "Security header $header is present"
            else
                track_result "WARN" "Security header $header is missing"
            fi
        done
    else
        track_result "FAIL" "Could not retrieve security headers"
    fi
}

# Generate validation report
generate_report() {
    log_info "Generating validation report..."
    
    echo ""
    echo "========================================"
    echo "ACGS-PGP v8 Deployment Validation Report"
    echo "========================================"
    echo "Service: $SERVICE_NAME"
    echo "Port: $SERVICE_PORT"
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "Timestamp: $(date -u +"%Y-%m-%d %H:%M:%S UTC")"
    echo ""
    echo "Validation Results:"
    echo "  Total Checks: $TOTAL_CHECKS"
    echo "  Passed: $PASSED_CHECKS"
    echo "  Failed: $FAILED_CHECKS"
    echo "  Warnings: $WARNING_CHECKS"
    echo ""
    
    local success_rate=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
    echo "Success Rate: $success_rate%"
    echo ""
    
    if [ $FAILED_CHECKS -eq 0 ]; then
        if [ $WARNING_CHECKS -eq 0 ]; then
            log_success "🎉 Deployment validation PASSED - Service is ready for production!"
            echo "Status: READY FOR PRODUCTION"
        else
            log_warning "⚠️  Deployment validation PASSED with warnings - Service is functional but has minor issues"
            echo "Status: FUNCTIONAL WITH WARNINGS"
        fi
        return 0
    else
        log_error "❌ Deployment validation FAILED - Service has critical issues"
        echo "Status: DEPLOYMENT FAILED"
        return 1
    fi
}

# Main validation function
main() {
    log_info "Starting ACGS-PGP v8 deployment validation..."
    echo ""
    
    # Core service validation
    check_service_running || exit 1
    validate_health_endpoint
    validate_metrics_endpoint
    validate_system_status
    check_component_health
    
    # Infrastructure validation
    check_dependencies
    check_database
    check_redis
    check_docker_container
    
    # Quality validation
    validate_performance
    validate_security
    
    # Generate final report
    echo ""
    generate_report
}

# Run validation
main "$@"
