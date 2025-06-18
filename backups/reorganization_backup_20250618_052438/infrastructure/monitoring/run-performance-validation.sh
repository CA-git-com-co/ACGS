#!/bin/bash
# ACGS-1 Monitoring Infrastructure Performance Validation Master Script
# Subtask 13.7: Comprehensive performance validation and testing orchestration
# 
# This script orchestrates all performance validation tests for the monitoring infrastructure
# including load testing, alert system validation, and dashboard performance testing.

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="/var/log/acgs"
RESULTS_DIR="$LOG_DIR/performance-validation-results"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Performance test configuration
CONCURRENT_USERS=${CONCURRENT_USERS:-1000}
TEST_DURATION=${TEST_DURATION:-600}  # 10 minutes
PROMETHEUS_URL=${PROMETHEUS_URL:-"http://localhost:9090"}
GRAFANA_URL=${GRAFANA_URL:-"http://localhost:3000"}
ALERTMANAGER_URL=${ALERTMANAGER_URL:-"http://localhost:9093"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_DIR/performance-validation.log"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$LOG_DIR/performance-validation.log"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$LOG_DIR/performance-validation.log"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️ $1${NC}" | tee -a "$LOG_DIR/performance-validation.log"
}

# Initialize environment
initialize_environment() {
    log "Initializing ACGS-1 monitoring performance validation environment..."
    
    # Create necessary directories
    sudo mkdir -p "$LOG_DIR" "$RESULTS_DIR"
    sudo chown -R "$USER:$USER" "$LOG_DIR"
    
    # Set permissions for test scripts
    chmod +x "$SCRIPT_DIR"/*.py
    
    # Check Python dependencies
    if ! python3 -c "import aiohttp, asyncio, psutil" 2>/dev/null; then
        error "Missing required Python dependencies. Installing..."
        pip3 install aiohttp psutil
    fi
    
    success "Environment initialized"
}

# Check monitoring services health
check_monitoring_services() {
    log "Checking monitoring services health..."
    
    local services=(
        "Prometheus:$PROMETHEUS_URL/-/healthy"
        "Grafana:$GRAFANA_URL/api/health"
        "Alertmanager:$ALERTMANAGER_URL/-/healthy"
    )
    
    local all_healthy=true
    
    for service_info in "${services[@]}"; do
        local service_name=$(echo "$service_info" | cut -d: -f1)
        local health_url=$(echo "$service_info" | cut -d: -f2-)
        
        if curl -s --max-time 10 "$health_url" > /dev/null 2>&1; then
            success "$service_name is healthy"
        else
            error "$service_name is not responding"
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = true ]; then
        success "All monitoring services are healthy"
        return 0
    else
        error "Some monitoring services are not healthy"
        return 1
    fi
}

# Run comprehensive load testing
run_load_testing() {
    log "Starting comprehensive monitoring infrastructure load testing..."
    
    local test_script="$SCRIPT_DIR/load-test-monitoring.py"
    local results_file="$RESULTS_DIR/load-test-results-$TIMESTAMP.json"
    
    if [ ! -f "$test_script" ]; then
        error "Load testing script not found: $test_script"
        return 1
    fi
    
    log "Running load test with $CONCURRENT_USERS concurrent users for ${TEST_DURATION}s..."
    
    if python3 "$test_script" \
        --users "$CONCURRENT_USERS" \
        --duration "$TEST_DURATION" \
        --prometheus-url "$PROMETHEUS_URL" \
        --grafana-url "$GRAFANA_URL" \
        2>&1 | tee "$LOG_DIR/load-test-$TIMESTAMP.log"; then
        
        success "Load testing completed successfully"
        
        # Copy results to timestamped file
        if [ -f "$LOG_DIR/monitoring-load-test-results.json" ]; then
            cp "$LOG_DIR/monitoring-load-test-results.json" "$results_file"
            success "Load test results saved to: $results_file"
        fi
        
        return 0
    else
        error "Load testing failed"
        return 1
    fi
}

# Run alert system testing
run_alert_system_testing() {
    log "Starting alert system performance testing..."
    
    local test_script="$SCRIPT_DIR/test-alert-system.py"
    local results_file="$RESULTS_DIR/alert-system-results-$TIMESTAMP.json"
    
    if [ ! -f "$test_script" ]; then
        error "Alert system testing script not found: $test_script"
        return 1
    fi
    
    log "Running alert system tests..."
    
    if python3 "$test_script" \
        --duration 300 \
        --prometheus-url "$PROMETHEUS_URL" \
        --alertmanager-url "$ALERTMANAGER_URL" \
        2>&1 | tee "$LOG_DIR/alert-system-test-$TIMESTAMP.log"; then
        
        success "Alert system testing completed successfully"
        
        # Copy results to timestamped file
        if [ -f "$LOG_DIR/alert-system-test-report.json" ]; then
            cp "$LOG_DIR/alert-system-test-report.json" "$results_file"
            success "Alert system test results saved to: $results_file"
        fi
        
        return 0
    else
        error "Alert system testing failed"
        return 1
    fi
}

# Run dashboard performance testing
run_dashboard_testing() {
    log "Starting dashboard performance testing..."
    
    local test_script="$SCRIPT_DIR/test-dashboard-performance.py"
    local results_file="$RESULTS_DIR/dashboard-performance-results-$TIMESTAMP.json"
    
    if [ ! -f "$test_script" ]; then
        error "Dashboard performance testing script not found: $test_script"
        return 1
    fi
    
    log "Running dashboard performance tests..."
    
    if python3 "$test_script" \
        --users 100 \
        --duration 300 \
        --grafana-url "$GRAFANA_URL" \
        --prometheus-url "$PROMETHEUS_URL" \
        2>&1 | tee "$LOG_DIR/dashboard-performance-test-$TIMESTAMP.log"; then
        
        success "Dashboard performance testing completed successfully"
        
        # Copy results to timestamped file
        if [ -f "$LOG_DIR/dashboard-performance-test-report.json" ]; then
            cp "$LOG_DIR/dashboard-performance-test-report.json" "$results_file"
            success "Dashboard performance test results saved to: $results_file"
        fi
        
        return 0
    else
        error "Dashboard performance testing failed"
        return 1
    fi
}

# Run comprehensive performance validation
run_comprehensive_validation() {
    log "Starting comprehensive monitoring infrastructure performance validation..."
    
    local test_script="$SCRIPT_DIR/performance-validation.py"
    local results_file="$RESULTS_DIR/comprehensive-validation-results-$TIMESTAMP.json"
    
    if [ ! -f "$test_script" ]; then
        error "Comprehensive validation script not found: $test_script"
        return 1
    fi
    
    log "Running comprehensive performance validation..."
    
    if python3 "$test_script" \
        --users "$CONCURRENT_USERS" \
        --duration "$TEST_DURATION" \
        --prometheus-url "$PROMETHEUS_URL" \
        --grafana-url "$GRAFANA_URL" \
        --alertmanager-url "$ALERTMANAGER_URL" \
        2>&1 | tee "$LOG_DIR/comprehensive-validation-$TIMESTAMP.log"; then
        
        success "Comprehensive performance validation completed successfully"
        
        # Copy results to timestamped file
        if [ -f "$LOG_DIR/monitoring-performance-validation-report.json" ]; then
            cp "$LOG_DIR/monitoring-performance-validation-report.json" "$results_file"
            success "Comprehensive validation results saved to: $results_file"
        fi
        
        return 0
    else
        error "Comprehensive performance validation failed"
        return 1
    fi
}

# Generate consolidated performance report
generate_consolidated_report() {
    log "Generating consolidated performance validation report..."
    
    local consolidated_report="$RESULTS_DIR/consolidated-performance-report-$TIMESTAMP.json"
    
    # Create consolidated report structure
    cat > "$consolidated_report" << EOF
{
  "test_metadata": {
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "test_suite": "ACGS-1 Monitoring Infrastructure Performance Validation",
    "subtask": "13.7",
    "concurrent_users": $CONCURRENT_USERS,
    "test_duration_seconds": $TEST_DURATION,
    "test_environment": {
      "prometheus_url": "$PROMETHEUS_URL",
      "grafana_url": "$GRAFANA_URL",
      "alertmanager_url": "$ALERTMANAGER_URL"
    }
  },
  "test_results": {
EOF
    
    # Add individual test results
    local first_result=true
    
    for result_file in "$RESULTS_DIR"/*-results-$TIMESTAMP.json; do
        if [ -f "$result_file" ]; then
            local test_name=$(basename "$result_file" | sed "s/-results-$TIMESTAMP.json//")
            
            if [ "$first_result" = false ]; then
                echo "," >> "$consolidated_report"
            fi
            
            echo "    \"$test_name\": " >> "$consolidated_report"
            cat "$result_file" >> "$consolidated_report"
            
            first_result=false
        fi
    done
    
    # Close JSON structure
    cat >> "$consolidated_report" << EOF
  },
  "summary": {
    "total_test_suites": $(find "$RESULTS_DIR" -name "*-results-$TIMESTAMP.json" | wc -l),
    "test_completion_time": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  }
}
EOF
    
    success "Consolidated performance report generated: $consolidated_report"
}

# Display performance summary
display_performance_summary() {
    log "Performance Validation Summary"
    echo "=" * 80
    
    log "📊 Test Configuration:"
    log "  Concurrent Users: $CONCURRENT_USERS"
    log "  Test Duration: ${TEST_DURATION}s"
    log "  Timestamp: $TIMESTAMP"
    
    log "📁 Results Location: $RESULTS_DIR"
    
    # List all result files
    log "📄 Generated Reports:"
    for result_file in "$RESULTS_DIR"/*-$TIMESTAMP.*; do
        if [ -f "$result_file" ]; then
            local file_size=$(du -h "$result_file" | cut -f1)
            log "  $(basename "$result_file") ($file_size)"
        fi
    done
    
    echo "=" * 80
}

# Main execution function
main() {
    log "🚀 Starting ACGS-1 Monitoring Infrastructure Performance Validation"
    log "Subtask 13.7: Performance Validation and Testing"
    log "=" * 80
    
    local overall_success=true
    
    # Step 1: Initialize environment
    if ! initialize_environment; then
        error "Environment initialization failed"
        exit 1
    fi
    
    # Step 2: Check monitoring services health
    if ! check_monitoring_services; then
        error "Monitoring services health check failed"
        exit 1
    fi
    
    # Step 3: Run load testing
    if ! run_load_testing; then
        warn "Load testing failed"
        overall_success=false
    fi
    
    # Step 4: Run alert system testing
    if ! run_alert_system_testing; then
        warn "Alert system testing failed"
        overall_success=false
    fi
    
    # Step 5: Run dashboard performance testing
    if ! run_dashboard_testing; then
        warn "Dashboard performance testing failed"
        overall_success=false
    fi
    
    # Step 6: Run comprehensive validation
    if ! run_comprehensive_validation; then
        warn "Comprehensive validation failed"
        overall_success=false
    fi
    
    # Step 7: Generate consolidated report
    generate_consolidated_report
    
    # Step 8: Display summary
    display_performance_summary
    
    # Final result
    if [ "$overall_success" = true ]; then
        success "🎉 ACGS-1 Monitoring Infrastructure Performance Validation COMPLETED SUCCESSFULLY!"
        success "All performance targets achieved and monitoring system validated for production deployment"
        exit 0
    else
        error "❌ ACGS-1 Monitoring Infrastructure Performance Validation COMPLETED WITH ISSUES"
        error "Some performance tests failed. Review logs and results for details."
        exit 1
    fi
}

# Handle script interruption
trap 'error "Performance validation interrupted"; exit 1' INT TERM

# Execute main function
main "$@"
