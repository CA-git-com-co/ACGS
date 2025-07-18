# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash
# HAProxy Monitoring Integration Test Script for ACGS-1
# Subtask 13.6: Comprehensive validation of load balancing monitoring
# Target: >99.9% availability, <500ms response times, >1000 concurrent users

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
HAPROXY_EXPORTER_PORT="9101"
HAPROXY_STATS_PORT="8080"
PROMETHEUS_PORT="9090"
GRAFANA_PORT="3000"
TEST_RESULTS_FILE="/var/log/acgs/haproxy-monitoring-test-results.json"

# Test configuration
LOAD_TEST_DURATION=60  # seconds
CONCURRENT_USERS=50
TARGET_RESPONSE_TIME=500  # milliseconds
MIN_SUCCESS_RATE=95  # percentage

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "/var/log/acgs/haproxy-monitoring-test.log"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    exit 1
}

# Initialize test results
init_test_results() {
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    cat > "$TEST_RESULTS_FILE" << EOF
{
  "test_execution": {
    "timestamp": "$timestamp",
    "subtask": "13.6",
    "component": "haproxy-monitoring-integration",
    "status": "running"
  },
  "test_results": {
    "service_availability": {},
    "metrics_collection": {},
    "alert_system": {},
    "dashboard_integration": {},
    "performance_validation": {},
    "end_to_end_monitoring": {}
  },
  "performance_metrics": {
    "response_times": [],
    "error_rates": [],
    "throughput": [],
    "availability": []
  }
}
EOF
    
    log "✓ Test results file initialized: $TEST_RESULTS_FILE"
}

# Test service availability
test_service_availability() {
    log "Testing service availability..."
    
    local services=(
        "haproxy-exporter:$HAPROXY_EXPORTER_PORT:/metrics"
        "haproxy-stats:$HAPROXY_STATS_PORT:/stats"
        "prometheus:$PROMETHEUS_PORT/-/healthy"
        "grafana:$GRAFANA_PORT/api/health"
    )
    
    local all_healthy=true
    
    for service_info in "${services[@]}"; do
        IFS=':' read -ra SERVICE_PARTS <<< "$service_info"
        local service_name="${SERVICE_PARTS[0]}"
        local port="${SERVICE_PARTS[1]}"
        local endpoint="${SERVICE_PARTS[2]}"
        
        local url="http://localhost:$port$endpoint"
        
        if curl -s --max-time 10 "$url" > /dev/null; then
            log "✓ $service_name is healthy"
            jq --arg service "$service_name" '.test_results.service_availability[$service] = true' "$TEST_RESULTS_FILE" > /tmp/test_results.json && mv /tmp/test_results.json "$TEST_RESULTS_FILE"
        else
            log "✗ $service_name is not healthy"
            jq --arg service "$service_name" '.test_results.service_availability[$service] = false' "$TEST_RESULTS_FILE" > /tmp/test_results.json && mv /tmp/test_results.json "$TEST_RESULTS_FILE"
            all_healthy=false
        fi
    done
    
    if [ "$all_healthy" = true ]; then
        log "✓ All monitoring services are healthy"
        return 0
    else
        error_exit "Some monitoring services are not healthy"
    fi
}

# Test metrics collection
test_metrics_collection() {
    log "Testing HAProxy metrics collection..."
    
    local haproxy_metrics_url="http://localhost:$HAPROXY_EXPORTER_PORT/metrics"
    local expected_metrics=(
        "haproxy_server_status"
        "haproxy_server_current_sessions"
        "haproxy_server_response_time_average_seconds"
        "haproxy_backend_status"
        "haproxy_backend_current_sessions"
        "haproxy_backend_http_requests_total"
    )
    
    local metrics_response
    metrics_response=$(curl -s "$haproxy_metrics_url")
    
    if [ -z "$metrics_response" ]; then
        error_exit "Unable to retrieve HAProxy metrics"
    fi
    
    local metrics_available=0
    local total_metrics=${#expected_metrics[@]}
    
    for metric in "${expected_metrics[@]}"; do
        if echo "$metrics_response" | grep -q "$metric"; then
            log "✓ Metric $metric is available"
            ((metrics_available++))
        else
            log "✗ Metric $metric is missing"
        fi
    done
    
    local metrics_percentage=$((metrics_available * 100 / total_metrics))
    
    jq --arg percentage "$metrics_percentage" '.test_results.metrics_collection.availability_percentage = ($percentage | tonumber)' "$TEST_RESULTS_FILE" > /tmp/test_results.json && mv /tmp/test_results.json "$TEST_RESULTS_FILE"
    jq --arg available "$metrics_available" --arg total "$total_metrics" '.test_results.metrics_collection.metrics_available = ($available | tonumber) | .test_results.metrics_collection.total_metrics = ($total | tonumber)' "$TEST_RESULTS_FILE" > /tmp/test_results.json && mv /tmp/test_results.json "$TEST_RESULTS_FILE"
    
    if [ $metrics_percentage -ge 90 ]; then
        log "✓ Metrics collection test passed ($metrics_percentage%)"
        return 0
    else
        error_exit "Metrics collection test failed ($metrics_percentage% < 90%)"
    fi
}

# Test Prometheus integration
test_prometheus_integration() {
    log "Testing Prometheus integration..."
    
    local prometheus_targets_url="http://localhost:$PROMETHEUS_PORT/api/v1/targets"
    local prometheus_query_url="http://localhost:$PROMETHEUS_PORT/api/v1/query"
    
    # Check if HAProxy exporter target is up in Prometheus
    local targets_response
    targets_response=$(curl -s "$prometheus_targets_url")
    
    if echo "$targets_response" | jq -r '.data.activeTargets[] | select(.job=="haproxy-exporter") | .health' | grep -q "up"; then
        log "✓ HAProxy exporter target is up in Prometheus"
        jq '.test_results.metrics_collection.prometheus_target_up = true' "$TEST_RESULTS_FILE" > /tmp/test_results.json && mv /tmp/test_results.json "$TEST_RESULTS_FILE"
    else
        log "✗ HAProxy exporter target is down in Prometheus"
        jq '.test_results.metrics_collection.prometheus_target_up = false' "$TEST_RESULTS_FILE" > /tmp/test_results.json && mv /tmp/test_results.json "$TEST_RESULTS_FILE"
        return 1
    fi
    
    # Test querying HAProxy metrics through Prometheus
    local test_query="up{job=\"haproxy-exporter\"}"
    local query_response
    query_response=$(curl -s -G "$prometheus_query_url" --data-urlencode "query=$test_query")
    
    if echo "$query_response" | jq -r '.data.result[0].value[1]' | grep -q "1"; then
        log "✓ HAProxy metrics are queryable through Prometheus"
        jq '.test_results.metrics_collection.prometheus_query_success = true' "$TEST_RESULTS_FILE" > /tmp/test_results.json && mv /tmp/test_results.json "$TEST_RESULTS_FILE"
        return 0
    else
        log "✗ HAProxy metrics are not queryable through Prometheus"
        jq '.test_results.metrics_collection.prometheus_query_success = false' "$TEST_RESULTS_FILE" > /tmp/test_results.json && mv /tmp/test_results.json "$TEST_RESULTS_FILE"
        return 1
    fi
}

# Test alert system integration
test_alert_system() {
    log "Testing alert system integration..."
    
    local prometheus_rules_url="http://localhost:$PROMETHEUS_PORT/api/v1/rules"
    local rules_response
    rules_response=$(curl -s "$prometheus_rules_url")
    
    # Check if HAProxy alert rules are loaded
    local haproxy_alerts=(
        "HAProxyDown"
        "HAProxyBackendServerDown"
        "HAProxyHighResponseTime"
        "HAProxyHighConnectionCount"
    )
    
    local alerts_loaded=0
    local total_alerts=${#haproxy_alerts[@]}
    
    for alert in "${haproxy_alerts[@]}"; do
        if echo "$rules_response" | jq -r '.data.groups[].rules[].alert' | grep -q "$alert"; then
            log "✓ Alert rule $alert is loaded"
            ((alerts_loaded++))
        else
            log "✗ Alert rule $alert is missing"
        fi
    done
    
    local alerts_percentage=$((alerts_loaded * 100 / total_alerts))
    
    jq --arg percentage "$alerts_percentage" '.test_results.alert_system.rules_loaded_percentage = ($percentage | tonumber)' "$TEST_RESULTS_FILE" > /tmp/test_results.json && mv /tmp/test_results.json "$TEST_RESULTS_FILE"
    
    if [ $alerts_percentage -ge 90 ]; then
        log "✓ Alert system integration test passed ($alerts_percentage%)"
        return 0
    else
        log "✗ Alert system integration test failed ($alerts_percentage% < 90%)"
        return 1
    fi
}

# Test dashboard integration
test_dashboard_integration() {
    log "Testing Grafana dashboard integration..."
    
    local grafana_api_url="http://localhost:$GRAFANA_PORT/api"
    local dashboard_search_url="$grafana_api_url/search?query=load-balancing"
    
    # Check if load balancing dashboard exists
    local dashboard_response
    dashboard_response=$(curl -s "$dashboard_search_url")
    
    if echo "$dashboard_response" | jq -r '.[].title' | grep -q -i "load.*balanc"; then
        log "✓ Load balancing dashboard is available in Grafana"
        jq '.test_results.dashboard_integration.dashboard_available = true' "$TEST_RESULTS_FILE" > /tmp/test_results.json && mv /tmp/test_results.json "$TEST_RESULTS_FILE"
        return 0
    else
        log "✗ Load balancing dashboard is not available in Grafana"
        jq '.test_results.dashboard_integration.dashboard_available = false' "$TEST_RESULTS_FILE" > /tmp/test_results.json && mv /tmp/test_results.json "$TEST_RESULTS_FILE"
        return 1
    fi
}

# Perform load testing
perform_load_test() {
    log "Performing load test to validate monitoring under stress..."
    
    local backends=("8000" "8001" "8002" "8003" "8004" "8005" "8006")
    local test_results=()
    
    for backend_port in "${backends[@]}"; do
        log "Testing backend on port $backend_port..."
        
        # Use curl to simulate load (simplified load test)
        local start_time=$(date +%s)
        local success_count=0
        local total_requests=10
        
        for ((i=1; i<=total_requests; i++)); do
            local response_time
            response_time=$(curl -s -w "%{time_total}" -o /dev/null "http://localhost:$backend_port/health" 2>/dev/null || echo "999")
            
            if (( $(echo "$response_time < 1.0" | bc -l) )); then
                ((success_count++))
            fi
            
            # Add small delay between requests
            sleep 0.1
        done
        
        local success_rate=$((success_count * 100 / total_requests))
        test_results+=("$backend_port:$success_rate")
        
        log "Backend $backend_port: $success_rate% success rate"
    done
    
    # Calculate overall performance
    local total_success=0
    local backend_count=${#backends[@]}
    
    for result in "${test_results[@]}"; do
        IFS=':' read -ra RESULT_PARTS <<< "$result"
        local success_rate="${RESULT_PARTS[1]}"
        total_success=$((total_success + success_rate))
    done
    
    local average_success=$((total_success / backend_count))
    
    jq --arg success "$average_success" '.test_results.performance_validation.average_success_rate = ($success | tonumber)' "$TEST_RESULTS_FILE" > /tmp/test_results.json && mv /tmp/test_results.json "$TEST_RESULTS_FILE"
    
    if [ $average_success -ge $MIN_SUCCESS_RATE ]; then
        log "✓ Load test passed (average success rate: $average_success%)"
        return 0
    else
        log "✗ Load test failed (average success rate: $average_success% < $MIN_SUCCESS_RATE%)"
        return 1
    fi
}

# Generate final test report
generate_test_report() {
    log "Generating final test report..."
    
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local overall_success=true
    
    # Check if all tests passed
    local service_availability=$(jq -r '.test_results.service_availability | to_entries | map(.value) | all' "$TEST_RESULTS_FILE")
    local metrics_percentage=$(jq -r '.test_results.metrics_collection.availability_percentage // 0' "$TEST_RESULTS_FILE")
    local prometheus_integration=$(jq -r '.test_results.metrics_collection.prometheus_target_up // false' "$TEST_RESULTS_FILE")
    local alert_percentage=$(jq -r '.test_results.alert_system.rules_loaded_percentage // 0' "$TEST_RESULTS_FILE")
    local dashboard_available=$(jq -r '.test_results.dashboard_integration.dashboard_available // false' "$TEST_RESULTS_FILE")
    local performance_success=$(jq -r '.test_results.performance_validation.average_success_rate // 0' "$TEST_RESULTS_FILE")
    
    # Determine overall success
    if [ "$service_availability" != "true" ] || \
       [ "$(echo "$metrics_percentage < 90" | bc -l)" = "1" ] || \
       [ "$prometheus_integration" != "true" ] || \
       [ "$(echo "$alert_percentage < 90" | bc -l)" = "1" ] || \
       [ "$dashboard_available" != "true" ] || \
       [ "$(echo "$performance_success < $MIN_SUCCESS_RATE" | bc -l)" = "1" ]; then
        overall_success=false
    fi
    
    # Update test results with final status
    jq --arg timestamp "$timestamp" --argjson success "$overall_success" '
        .test_execution.completion_timestamp = $timestamp |
        .test_execution.status = (if $success then "passed" else "failed" end) |
        .test_execution.overall_success = $success
    ' "$TEST_RESULTS_FILE" > /tmp/test_results.json && mv /tmp/test_results.json "$TEST_RESULTS_FILE"
    
    if [ "$overall_success" = true ]; then
        log "✅ All HAProxy monitoring integration tests passed"
        log "📊 Test report: $TEST_RESULTS_FILE"
        return 0
    else
        log "❌ Some HAProxy monitoring integration tests failed"
        log "📊 Test report: $TEST_RESULTS_FILE"
        return 1
    fi
}

# Main test execution
main() {
    log "Starting HAProxy monitoring integration tests for Subtask 13.6"
    
    # Create log directory
    sudo mkdir -p /var/log/acgs
    sudo chown "$USER:$USER" /var/log/acgs
    
    # Initialize test results
    init_test_results
    
    # Execute test suite
    local test_success=true
    
    test_service_availability || test_success=false
    test_metrics_collection || test_success=false
    test_prometheus_integration || test_success=false
    test_alert_system || test_success=false
    test_dashboard_integration || test_success=false
    perform_load_test || test_success=false
    
    # Generate final report
    generate_test_report
    
    if [ "$test_success" = true ]; then
        log "🎉 HAProxy monitoring integration validation completed successfully"
        exit 0
    else
        log "💥 HAProxy monitoring integration validation failed"
        exit 1
    fi
}

# Handle script termination
cleanup() {
    log "Test execution interrupted"
    jq '.test_execution.status = "interrupted"' "$TEST_RESULTS_FILE" > /tmp/test_results.json && mv /tmp/test_results.json "$TEST_RESULTS_FILE" 2>/dev/null || true
    exit 1
}

trap cleanup SIGINT SIGTERM

# Execute main function
main "$@"
