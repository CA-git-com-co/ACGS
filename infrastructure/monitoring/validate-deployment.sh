# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash
# ACGS-1 Monitoring Infrastructure Deployment Validation Script
# Subtask 13.8: Comprehensive deployment validation and health checks
# 
# This script performs comprehensive validation of the monitoring infrastructure
# deployment to ensure all components are properly configured and operational.

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VALIDATION_LOG="/var/log/acgs/deployment-validation.log"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Service endpoints
PROMETHEUS_URL="http://localhost:9090"
GRAFANA_URL="http://localhost:3000"
ALERTMANAGER_URL="http://localhost:9093"
HAPROXY_EXPORTER_URL="http://localhost:9101"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Validation results
VALIDATION_RESULTS=()
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$VALIDATION_LOG"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] ✅ $1${NC}" | tee -a "$VALIDATION_LOG"
    VALIDATION_RESULTS+=("PASS: $1")
    ((PASSED_CHECKS++))
    ((TOTAL_CHECKS++))
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ❌ $1${NC}" | tee -a "$VALIDATION_LOG"
    VALIDATION_RESULTS+=("FAIL: $1")
    ((FAILED_CHECKS++))
    ((TOTAL_CHECKS++))
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] ⚠️ $1${NC}" | tee -a "$VALIDATION_LOG"
}

# Initialize validation
initialize_validation() {
    log "Starting ACGS-1 Monitoring Infrastructure Deployment Validation"
    log "Timestamp: $TIMESTAMP"
    log "=" * 80
    
    # Create log directory if it doesn't exist
    mkdir -p "$(dirname "$VALIDATION_LOG")"
    
    # Initialize validation log
    echo "ACGS-1 Monitoring Infrastructure Deployment Validation - $TIMESTAMP" > "$VALIDATION_LOG"
    echo "=======================================================================" >> "$VALIDATION_LOG"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
}

# Check Docker services
check_docker_services() {
    log "Checking Docker services status..."
    
    # Check if Docker is running
    if systemctl is-active --quiet docker; then
        success "Docker service is running"
    else
        error "Docker service is not running"
        return 1
    fi
    
    # Check Docker Compose services
    cd "$PROJECT_ROOT"
    
    if [[ -f "infrastructure/monitoring/docker-compose.monitoring.yml" ]]; then
        local services=$(docker-compose -f infrastructure/monitoring/docker-compose.monitoring.yml ps --services)
        
        for service in $services; do
            local status=$(docker-compose -f infrastructure/monitoring/docker-compose.monitoring.yml ps -q "$service" | xargs docker inspect --format='{{.State.Status}}' 2>/dev/null || echo "not_found")
            
            if [[ "$status" == "running" ]]; then
                success "Docker service '$service' is running"
            else
                error "Docker service '$service' is not running (status: $status)"
            fi
        done
    else
        error "Docker Compose file not found"
    fi
}

# Check service health endpoints
check_service_health() {
    log "Checking service health endpoints..."
    
    local services=(
        "Prometheus:$PROMETHEUS_URL/-/healthy"
        "Grafana:$GRAFANA_URL/api/health"
        "Alertmanager:$ALERTMANAGER_URL/-/healthy"
        "HAProxy Exporter:$HAPROXY_EXPORTER_URL/metrics"
    )
    
    for service_info in "${services[@]}"; do
        local service_name=$(echo "$service_info" | cut -d: -f1)
        local health_url=$(echo "$service_info" | cut -d: -f2-)
        
        if curl -s --max-time 10 "$health_url" > /dev/null 2>&1; then
            success "$service_name health endpoint is responding"
        else
            error "$service_name health endpoint is not responding"
        fi
    done
}

# Check metrics collection
check_metrics_collection() {
    log "Checking metrics collection..."
    
    # Check if Prometheus is collecting metrics
    local up_targets=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=up" | jq -r '.data.result | length' 2>/dev/null || echo "0")
    
    if [[ "$up_targets" -gt 0 ]]; then
        success "Prometheus is collecting metrics from $up_targets targets"
    else
        error "Prometheus is not collecting metrics from any targets"
    fi
    
    # Check ACGS service metrics
    local acgs_services=("auth" "ac" "integrity" "fv" "gs" "pgc" "ec")
    
    for service in "${acgs_services[@]}"; do
        local service_up=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=up{job=\"acgs-$service-service\"}" | jq -r '.data.result[0].value[1]' 2>/dev/null || echo "0")
        
        if [[ "$service_up" == "1" ]]; then
            success "ACGS $service service metrics are being collected"
        else
            warn "ACGS $service service metrics are not available (service may not be running)"
        fi
    done
    
    # Check custom ACGS metrics
    local custom_metrics=(
        "acgs_constitutional_compliance_score"
        "acgs_policy_synthesis_operations_total"
        "acgs_governance_decision_duration_seconds"
    )
    
    for metric in "${custom_metrics[@]}"; do
        local metric_exists=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=$metric" | jq -r '.data.result | length' 2>/dev/null || echo "0")
        
        if [[ "$metric_exists" -gt 0 ]]; then
            success "Custom metric '$metric' is available"
        else
            warn "Custom metric '$metric' is not available (may be generated by ACGS services)"
        fi
    done
}

# Check alert rules
check_alert_rules() {
    log "Checking alert rules configuration..."
    
    # Get alert rules from Prometheus
    local rules_response=$(curl -s "$PROMETHEUS_URL/api/v1/rules" 2>/dev/null || echo '{"data":{"groups":[]}}')
    local total_rules=$(echo "$rules_response" | jq -r '.data.groups[].rules[] | select(.type=="alerting") | .name' 2>/dev/null | wc -l)
    
    if [[ "$total_rules" -gt 0 ]]; then
        success "Found $total_rules alert rules configured"
    else
        error "No alert rules found in Prometheus"
    fi
    
    # Check for critical alert rules
    local critical_alerts=(
        "ServiceDown"
        "HighResponseTime"
        "LowConstitutionalCompliance"
        "PolicySynthesisFailureRate"
    )
    
    for alert in "${critical_alerts[@]}"; do
        local alert_exists=$(echo "$rules_response" | jq -r ".data.groups[].rules[] | select(.name==\"$alert\") | .name" 2>/dev/null)
        
        if [[ "$alert_exists" == "$alert" ]]; then
            success "Critical alert rule '$alert' is configured"
        else
            error "Critical alert rule '$alert' is missing"
        fi
    done
    
    # Check alert rule syntax
    if command -v promtool &> /dev/null; then
        if find /etc/prometheus/rules -name "*.yml" -exec promtool check rules {} \; > /dev/null 2>&1; then
            success "Alert rule syntax validation passed"
        else
            error "Alert rule syntax validation failed"
        fi
    else
        warn "promtool not available for alert rule syntax validation"
    fi
}

# Check Grafana dashboards
check_grafana_dashboards() {
    log "Checking Grafana dashboards..."
    
    # Check if Grafana API is accessible
    local grafana_health=$(curl -s "$GRAFANA_URL/api/health" | jq -r '.database' 2>/dev/null || echo "unknown")
    
    if [[ "$grafana_health" == "ok" ]]; then
        success "Grafana database connection is healthy"
    else
        error "Grafana database connection is not healthy"
    fi
    
    # Check for ACGS dashboards (requires authentication, so we'll check files)
    local dashboard_files=(
        "acgs-services-overview"
        "acgs-governance-workflows"
        "acgs-infrastructure"
        "acgs-performance"
        "acgs-security"
    )
    
    for dashboard in "${dashboard_files[@]}"; do
        if [[ -f "/etc/grafana/dashboards/$dashboard.json" ]] || [[ -f "$SCRIPT_DIR/grafana/dashboards/$dashboard.json" ]]; then
            success "Dashboard '$dashboard' configuration file exists"
        else
            warn "Dashboard '$dashboard' configuration file not found"
        fi
    done
}

# Check data persistence
check_data_persistence() {
    log "Checking data persistence..."
    
    # Check Prometheus data directory
    local prometheus_data_dir="/var/lib/docker/volumes/prometheus_data/_data"
    if [[ -d "$prometheus_data_dir" ]] && [[ -n "$(ls -A "$prometheus_data_dir" 2>/dev/null)" ]]; then
        success "Prometheus data directory exists and contains data"
    else
        error "Prometheus data directory is missing or empty"
    fi
    
    # Check Grafana data directory
    local grafana_data_dir="/var/lib/docker/volumes/grafana_data/_data"
    if [[ -d "$grafana_data_dir" ]] && [[ -n "$(ls -A "$grafana_data_dir" 2>/dev/null)" ]]; then
        success "Grafana data directory exists and contains data"
    else
        error "Grafana data directory is missing or empty"
    fi
    
    # Check disk space
    local available_space=$(df /var/lib/docker/volumes | awk 'NR==2{print $4}')
    local available_gb=$((available_space / 1024 / 1024))
    
    if [[ "$available_gb" -gt 10 ]]; then
        success "Sufficient disk space available: ${available_gb}GB"
    else
        warn "Low disk space available: ${available_gb}GB"
    fi
}

# Check network connectivity
check_network_connectivity() {
    log "Checking network connectivity..."
    
    # Check internal service connectivity
    local services=("9090" "3000" "9093" "9101")
    
    for port in "${services[@]}"; do
        if nc -z localhost "$port" 2>/dev/null; then
            success "Port $port is accessible"
        else
            error "Port $port is not accessible"
        fi
    done
    
    # Check ACGS service connectivity
    local acgs_ports=(8000 8001 8002 8003 8004 8005 8006)
    
    for port in "${acgs_ports[@]}"; do
        if nc -z localhost "$port" 2>/dev/null; then
            success "ACGS service port $port is accessible"
        else
            warn "ACGS service port $port is not accessible (service may not be running)"
        fi
    done
}

# Check security configuration
check_security_configuration() {
    log "Checking security configuration..."
    
    # Check if environment file exists and is secure
    if [[ -f "/etc/acgs/monitoringconfig/environments/development.env" ]]; then
        local file_perms=$(stat -c "%a" /etc/acgs/monitoringconfig/environments/development.env)
        if [[ "$file_perms" == "600" ]]; then
            success "Monitoring environment file has secure permissions"
        else
            error "Monitoring environment file has insecure permissions: $file_perms"
        fi
    else
        error "Monitoring environment file not found"
    fi
    
    # Check SSL certificates
    if [[ -f "/etc/acgs/certs/monitoring.crt" ]] && [[ -f "/etc/acgs/certs/monitoring.key" ]]; then
        success "SSL certificates are present"
        
        # Check certificate expiration
        local cert_expiry=$(openssl x509 -enddate -noout -in /etc/acgs/certs/monitoring.crt | cut -d= -f2)
        local expiry_timestamp=$(date -d "$cert_expiry" +%s)
        local current_timestamp=$(date +%s)
        local days_until_expiry=$(( (expiry_timestamp - current_timestamp) / 86400 ))
        
        if [[ "$days_until_expiry" -gt 30 ]]; then
            success "SSL certificate is valid for $days_until_expiry days"
        else
            warn "SSL certificate expires in $days_until_expiry days"
        fi
    else
        warn "SSL certificates not found (using default configuration)"
    fi
    
    # Check firewall status
    if command -v ufw &> /dev/null; then
        if ufw status | grep -q "Status: active"; then
            success "UFW firewall is active"
        else
            warn "UFW firewall is not active"
        fi
    else
        warn "UFW firewall not installed"
    fi
}

# Check performance metrics
check_performance_metrics() {
    log "Checking performance metrics..."
    
    # Check response times
    local prometheus_response_time=$(curl -w "%{time_total}" -s -o /dev/null "$PROMETHEUS_URL/-/healthy" 2>/dev/null || echo "999")
    local grafana_response_time=$(curl -w "%{time_total}" -s -o /dev/null "$GRAFANA_URL/api/health" 2>/dev/null || echo "999")
    
    if (( $(echo "$prometheus_response_time < 1.0" | bc -l) )); then
        success "Prometheus response time is acceptable: ${prometheus_response_time}s"
    else
        warn "Prometheus response time is high: ${prometheus_response_time}s"
    fi
    
    if (( $(echo "$grafana_response_time < 2.0" | bc -l) )); then
        success "Grafana response time is acceptable: ${grafana_response_time}s"
    else
        warn "Grafana response time is high: ${grafana_response_time}s"
    fi
    
    # Check system resources
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    
    if (( $(echo "$cpu_usage < 80" | bc -l) )); then
        success "CPU usage is acceptable: ${cpu_usage}%"
    else
        warn "CPU usage is high: ${cpu_usage}%"
    fi
    
    if (( $(echo "$memory_usage < 85" | bc -l) )); then
        success "Memory usage is acceptable: ${memory_usage}%"
    else
        warn "Memory usage is high: ${memory_usage}%"
    fi
}

# Generate validation report
generate_validation_report() {
    log "Generating validation report..."
    
    local report_file="/var/log/acgs/deployment-validation-report-$TIMESTAMP.json"
    
    cat > "$report_file" << EOF
{
  "validation_metadata": {
    "timestamp": "$TIMESTAMP",
    "validation_type": "deployment_validation",
    "total_checks": $TOTAL_CHECKS,
    "passed_checks": $PASSED_CHECKS,
    "failed_checks": $FAILED_CHECKS,
    "success_rate": $(echo "scale=2; $PASSED_CHECKS * 100 / $TOTAL_CHECKS" | bc -l)
  },
  "validation_results": [
EOF
    
    # Add validation results
    local first_result=true
    for result in "${VALIDATION_RESULTS[@]}"; do
        if [[ "$first_result" == "false" ]]; then
            echo "," >> "$report_file"
        fi
        
        local status=$(echo "$result" | cut -d: -f1)
        local description=$(echo "$result" | cut -d: -f2-)
        
        echo "    {\"status\": \"$status\", \"description\": \"$description\"}" >> "$report_file"
        first_result=false
    done
    
    cat >> "$report_file" << EOF
  ],
  "recommendations": [
    "Review failed checks and address any critical issues",
    "Monitor system performance and resource utilization",
    "Ensure all ACGS services are properly configured",
    "Verify backup and disaster recovery procedures",
    "Schedule regular maintenance and updates"
  ]
}
EOF
    
    success "Validation report generated: $report_file"
}

# Display validation summary
display_validation_summary() {
    echo ""
    echo "======================================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "🔍 ACGS-1 Monitoring Infrastructure Validation Summary"
    echo "======================================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo ""
    echo "📊 Validation Results:"
    echo "  Total Checks: $TOTAL_CHECKS"
    echo "  Passed: $PASSED_CHECKS"
    echo "  Failed: $FAILED_CHECKS"
    echo "  Success Rate: $(echo "scale=1; $PASSED_CHECKS * 100 / $TOTAL_CHECKS" | bc -l)%"
    echo ""
    
    if [[ "$FAILED_CHECKS" -eq 0 ]]; then
        echo "✅ All validation checks passed!"
        echo "🎉 Monitoring infrastructure is ready for production deployment"
    elif [[ "$FAILED_CHECKS" -lt 3 ]]; then
        echo "⚠️  Some validation checks failed, but deployment may proceed with caution"
        echo "🔧 Review failed checks and address issues as needed"
    else
        echo "❌ Multiple validation checks failed"
        echo "🛠️  Address critical issues before proceeding with production deployment"
    fi
    
    echo ""
    echo "📋 Next Steps:"
    echo "  1. Review validation report for detailed results"
    echo "  2. Address any failed validation checks"
    echo "  3. Run performance validation if needed"
    echo "  4. Proceed with production deployment"
    echo ""
    echo "======================================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
}

# Main validation function
main() {
    initialize_validation
    
    # Run validation checks
    check_docker_services
    check_service_health
    check_metrics_collection
    check_alert_rules
    check_grafana_dashboards
    check_data_persistence
    check_network_connectivity
    check_security_configuration
    check_performance_metrics
    
    # Generate report and summary
    generate_validation_report
    display_validation_summary
    
    # Return appropriate exit code
    if [[ "$FAILED_CHECKS" -eq 0 ]]; then
        exit 0
    elif [[ "$FAILED_CHECKS" -lt 3 ]]; then
        exit 1  # Warning level
    else
        exit 2  # Error level
    fi
}

# Execute main function
main "$@"
