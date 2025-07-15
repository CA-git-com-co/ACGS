# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash
# Master Deployment Script for ACGS-1 Subtask 13.6
# Integrate with Load Balancing Infrastructure - Complete Implementation
# Target: >99.9% availability, <500ms response times, >1000 concurrent users

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
LOG_FILE="/var/log/acgs/subtask-13-6-deployment.log"
DEPLOYMENT_REPORT="/var/log/acgs/subtask-13-6-report.json"

# Logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "ERROR: $1"
    update_deployment_status "failed" "$1"
    exit 1
}

# Initialize deployment tracking
init_deployment() {
    log "Initializing Subtask 13.6 deployment..."
    
    # Create log directory
    sudo mkdir -p /var/log/acgs
    sudo chown "$USER:$USER" /var/log/acgs
    
    # Initialize deployment report
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    cat > "$DEPLOYMENT_REPORT" << EOF
{
  "deployment": {
    "subtask": "13.6",
    "title": "Integrate with Load Balancing Infrastructure",
    "start_timestamp": "$timestamp",
    "status": "in_progress",
    "phase": "initialization"
  },
  "components": {
    "haproxy_configuration": {"status": "pending"},
    "prometheus_exporter": {"status": "pending"},
    "prometheus_integration": {"status": "pending"},
    "alert_rules": {"status": "pending"},
    "dashboard_enhancement": {"status": "pending"},
    "validation_testing": {"status": "pending"}
  },
  "performance_targets": {
    "response_time": "<500ms",
    "availability": ">99.9%",
    "concurrent_users": ">1000",
    "monitoring_overhead": "<1%"
  },
  "integration_points": {
    "existing_monitoring": "subtasks_13.3-13.5",
    "load_balancing": "task_12",
    "quantumagi_preservation": "required"
  }
}
EOF
    
    log "✓ Deployment tracking initialized"
}

# Update deployment status
update_deployment_status() {
    local status="$1"
    local message="${2:-}"
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    jq --arg status "$status" --arg timestamp "$timestamp" --arg message "$message" '
        .deployment.status = $status |
        .deployment.last_update = $timestamp |
        if $message != "" then .deployment.last_message = $message else . end
    ' "$DEPLOYMENT_REPORT" > /tmp/deployment_report.json && mv /tmp/deployment_report.json "$DEPLOYMENT_REPORT"
}

# Update component status
update_component_status() {
    local component="$1"
    local status="$2"
    local message="${3:-}"
    
    jq --arg component "$component" --arg status "$status" --arg message "$message" '
        .components[$component].status = $status |
        if $message != "" then .components[$component].message = $message else . end
    ' "$DEPLOYMENT_REPORT" > /tmp/deployment_report.json && mv /tmp/deployment_report.json "$DEPLOYMENT_REPORT"
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites for Subtask 13.6..."
    update_deployment_status "in_progress" "Checking prerequisites"
    
    # Check if HAProxy is running
    if ! systemctl is-active --quiet haproxy; then
        error_exit "HAProxy service is not running. Please start HAProxy first."
    fi
    
    # Check if Prometheus is running
    if ! systemctl is-active --quiet prometheus; then
        error_exit "Prometheus service is not running. Please start Prometheus first."
    fi
    
    # Check if Grafana is running
    if ! systemctl is-active --quiet grafana-server; then
        log "WARNING: Grafana service is not running. Dashboard integration may fail."
    fi
    
    # Check if previous monitoring infrastructure is in place
    if [ ! -f "$PROJECT_ROOT/infrastructure/monitoring/prometheus.yml" ]; then  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        error_exit "Prometheus configuration not found. Please complete Subtasks 13.3-13.5 first."
    fi
    
    # Check if load balancing infrastructure exists
    if [ ! -f "$PROJECT_ROOT/infrastructure/load-balancer/haproxy.cfg" ]; then
        error_exit "HAProxy configuration not found. Please complete Task 12 first."
    fi
    
    log "✓ Prerequisites check completed"
}

# Deploy HAProxy configuration updates
deploy_haproxy_config() {
    log "Deploying HAProxy configuration updates..."
    update_component_status "haproxy_configuration" "in_progress"
    
    # Backup current configuration
    sudo cp /etc/haproxy/haproxy.cfg "/etc/haproxy/haproxy.cfg.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Deploy updated configuration
    sudo cp "$PROJECT_ROOT/infrastructure/load-balancer/haproxy.cfg" /etc/haproxy/haproxy.cfg
    
    # Validate configuration
    if sudo haproxy -c -f /etc/haproxy/haproxy.cfg; then
        log "✓ HAProxy configuration is valid"
        
        # Reload HAProxy
        sudo systemctl reload haproxy
        
        # Wait for reload to complete
        sleep 5
        
        # Verify HAProxy is still running
        if systemctl is-active --quiet haproxy; then
            log "✓ HAProxy reloaded successfully"
            update_component_status "haproxy_configuration" "completed"
        else
            error_exit "HAProxy failed to reload with new configuration"
        fi
    else
        error_exit "HAProxy configuration validation failed"
    fi
}

# Deploy HAProxy Prometheus Exporter
deploy_prometheus_exporter() {
    log "Deploying HAProxy Prometheus Exporter..."
    update_component_status "prometheus_exporter" "in_progress"
    
    # Make deployment script executable
    chmod +x "$SCRIPT_DIR/deploy-haproxy-exporter.sh"
    
    # Execute deployment
    if "$SCRIPT_DIR/deploy-haproxy-exporter.sh"; then
        log "✓ HAProxy Prometheus Exporter deployed successfully"
        update_component_status "prometheus_exporter" "completed"
    else
        error_exit "HAProxy Prometheus Exporter deployment failed"
    fi
}

# Update Prometheus configuration
update_prometheus_config() {
    log "Updating Prometheus configuration..."
    update_component_status "prometheus_integration" "in_progress"
    
    # Backup current Prometheus configuration
    sudo cp /etc/prometheus/prometheus.yml "/etc/prometheus/prometheus.yml.backup.$(date +%Y%m%d_%H%M%S)"
    
    # Deploy updated configuration
    sudo cp "$PROJECT_ROOT/infrastructure/monitoring/prometheus.yml" /etc/prometheus/prometheus.yml  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    
    # Validate Prometheus configuration
    if prometheus --config.file=/etc/prometheus/prometheus.yml --dry-run 2>/dev/null; then
        log "✓ Prometheus configuration is valid"
        
        # Reload Prometheus
        sudo systemctl reload prometheus
        
        # Wait for reload to complete
        sleep 10
        
        # Verify Prometheus is still running
        if systemctl is-active --quiet prometheus; then
            log "✓ Prometheus reloaded successfully"
            update_component_status "prometheus_integration" "completed"
        else
            error_exit "Prometheus failed to reload with new configuration"
        fi
    else
        error_exit "Prometheus configuration validation failed"
    fi
}

# Deploy alert rules
deploy_alert_rules() {
    log "Deploying enhanced alert rules..."
    update_component_status "alert_rules" "in_progress"
    
    # Deploy updated alert rules
    sudo cp "$PROJECT_ROOT/infrastructure/monitoring/rules/infrastructure_alerts.yml" /etc/prometheus/rules/  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    
    # Reload Prometheus to pick up new rules
    sudo systemctl reload prometheus
    
    # Wait for reload
    sleep 5
    
    # Verify alert rules are loaded
    if curl -s "http://localhost:9090/api/v1/rules" | jq -r '.data.groups[].rules[].alert' | grep -q "HAProxyDown"; then
        log "✓ HAProxy alert rules loaded successfully"
        update_component_status "alert_rules" "completed"
    else
        log "WARNING: HAProxy alert rules may not be loaded correctly"
        update_component_status "alert_rules" "completed_with_warnings"
    fi
}

# Deploy dashboard enhancements
deploy_dashboard_enhancements() {
    log "Deploying Grafana dashboard enhancements..."
    update_component_status "dashboard_enhancement" "in_progress"
    
    # Check if Grafana is accessible
    if curl -s "http://localhost:3000/api/health" > /dev/null; then
        log "✓ Grafana is accessible"
        
        # Deploy updated dashboard (manual step for now)
        log "📋 Dashboard configuration updated in: $PROJECT_ROOT/infrastructure/monitoring/grafana/dashboards/infrastructure/load-balancing-dashboard.json"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        log "📋 Please import the updated dashboard manually or restart Grafana to auto-load"
        
        update_component_status "dashboard_enhancement" "completed"
    else
        log "WARNING: Grafana is not accessible. Dashboard deployment skipped."
        update_component_status "dashboard_enhancement" "skipped"
    fi
}

# Run validation tests
run_validation_tests() {
    log "Running validation tests..."
    update_component_status "validation_testing" "in_progress"
    
    # Make test script executable
    chmod +x "$SCRIPT_DIR/test-monitoring-integration.sh"
    
    # Run comprehensive tests
    if "$SCRIPT_DIR/test-monitoring-integration.sh"; then
        log "✓ All validation tests passed"
        update_component_status "validation_testing" "completed"
        return 0
    else
        log "⚠ Some validation tests failed"
        update_component_status "validation_testing" "completed_with_failures"
        return 1
    fi
}

# Generate final deployment report
generate_final_report() {
    log "Generating final deployment report..."
    
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local overall_status="completed"
    
    # Check component statuses
    local failed_components
    failed_components=$(jq -r '.components | to_entries[] | select(.value.status == "failed") | .key' "$DEPLOYMENT_REPORT")
    
    if [ -n "$failed_components" ]; then
        overall_status="failed"
    fi
    
    # Update final status
    jq --arg status "$overall_status" --arg timestamp "$timestamp" '
        .deployment.status = $status |
        .deployment.completion_timestamp = $timestamp |
        .deployment.phase = "completed"
    ' "$DEPLOYMENT_REPORT" > /tmp/deployment_report.json && mv /tmp/deployment_report.json "$DEPLOYMENT_REPORT"
    
    # Add performance validation results
    if [ -f "/var/log/acgs/haproxy-monitoring-test-results.json" ]; then
        jq '.validation_results = input' "$DEPLOYMENT_REPORT" /var/log/acgs/haproxy-monitoring-test-results.json > /tmp/deployment_report.json && mv /tmp/deployment_report.json "$DEPLOYMENT_REPORT"
    fi
    
    log "📊 Final deployment report: $DEPLOYMENT_REPORT"
}

# Main deployment function
main() {
    log "🚀 Starting ACGS-1 Subtask 13.6: Integrate with Load Balancing Infrastructure"
    
    # Initialize deployment
    init_deployment
    
    # Execute deployment phases
    check_prerequisites
    deploy_haproxy_config
    deploy_prometheus_exporter
    update_prometheus_config
    deploy_alert_rules
    deploy_dashboard_enhancements
    
    # Run validation
    local validation_success=true
    run_validation_tests || validation_success=false
    
    # Generate final report
    generate_final_report
    
    # Final status
    if [ "$validation_success" = true ]; then
        update_deployment_status "completed" "All components deployed and validated successfully"
        log "✅ Subtask 13.6 deployment completed successfully"
        log "📊 HAProxy monitoring integration is now operational"
        log "🔗 Metrics endpoint: http://localhost:9101/metrics"
        log "📈 Dashboard: Load Balancing & Circuit Breaker Dashboard"
        log "🚨 Alerts: HAProxy-specific alerts are active"
        log "📋 Documentation: $PROJECT_ROOT/infrastructure/load-balancer/MONITORING_INTEGRATION.md"
        exit 0
    else
        update_deployment_status "completed_with_issues" "Deployment completed but validation tests failed"
        log "⚠ Subtask 13.6 deployment completed with issues"
        log "📊 Please review test results and address any failures"
        exit 1
    fi
}

# Handle script termination
cleanup() {
    log "Deployment interrupted"
    update_deployment_status "interrupted" "Deployment was interrupted"
    exit 1
}

trap cleanup SIGINT SIGTERM

# Execute main function
main "$@"
