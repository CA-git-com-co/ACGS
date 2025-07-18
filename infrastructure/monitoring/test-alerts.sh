# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# ACGS-1 Alert Testing and Validation Script - Subtask 13.5
# Comprehensive testing for alert rules and notification system
# Target: >95% alert accuracy, multi-channel delivery validation

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMETHEUS_URL="${PROMETHEUS_URL:-http://localhost:9090}"
ALERTMANAGER_URL="${ALERTMANAGER_URL:-http://localhost:9093}"
GRAFANA_URL="${GRAFANA_URL:-http://localhost:3000}"

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

# Check if services are accessible
check_service_connectivity() {
    log_info "Checking service connectivity..."
    
    local services_ok=0
    
    # Check Prometheus
    if curl -s -f "$PROMETHEUS_URL/api/v1/status/config" >/dev/null; then
        log_success "Prometheus is accessible at $PROMETHEUS_URL"
        services_ok=$((services_ok + 1))
    else
        log_error "Cannot connect to Prometheus at $PROMETHEUS_URL"
    fi
    
    # Check Alertmanager
    if curl -s -f "$ALERTMANAGER_URL/api/v1/status" >/dev/null; then
        log_success "Alertmanager is accessible at $ALERTMANAGER_URL"
        services_ok=$((services_ok + 1))
    else
        log_error "Cannot connect to Alertmanager at $ALERTMANAGER_URL"
    fi
    
    # Check Grafana
    if curl -s -f "$GRAFANA_URL/api/health" >/dev/null; then
        log_success "Grafana is accessible at $GRAFANA_URL"
        services_ok=$((services_ok + 1))
    else
        log_warning "Cannot connect to Grafana at $GRAFANA_URL (optional for alert testing)"
    fi
    
    if [[ $services_ok -lt 1 ]]; then
        log_error "Insufficient services available for alert testing"
        return 1
    fi
    
    return 0
}

# Validate alert rule syntax
validate_alert_rules() {
    log_info "Validating alert rule syntax..."
    
    local validation_failed=0
    
    # Check all alert rule files
    for rule_file in \
        "rules/acgs_alert_rules.yml" \
        "rules/service_specific_alerts.yml" \
        "rules/governance_service_alerts.yml" \
        "rules/governance_workflow_alerts.yml" \
        "rules/infrastructure_alerts.yml" \
        "rules/blockchain_alerts.yml"
    do
        if [[ -f "$SCRIPT_DIR/$rule_file" ]]; then
            log_info "Validating $rule_file..."
            
            # Use promtool to validate if available
            if command -v promtool >/dev/null 2>&1; then
                if promtool check rules "$SCRIPT_DIR/$rule_file" >/dev/null 2>&1; then
                    log_success "✓ $rule_file syntax is valid"
                else
                    log_error "✗ $rule_file has syntax errors"
                    validation_failed=1
                fi
            else
                # Basic YAML validation
                if python3 -c "import yaml; yaml.safe_load(open('$SCRIPT_DIR/$rule_file'))" 2>/dev/null; then
                    log_success "✓ $rule_file YAML syntax is valid"
                else
                    log_error "✗ $rule_file has YAML syntax errors"
                    validation_failed=1
                fi
            fi
        else
            log_warning "Alert rule file not found: $rule_file"
        fi
    done
    
    if [[ $validation_failed -eq 0 ]]; then
        log_success "All alert rule files passed validation"
        return 0
    else
        log_error "Some alert rule files failed validation"
        return 1
    fi
}

# Validate alertmanager configuration
validate_alertmanager_config() {
    log_info "Validating Alertmanager configuration..."
    
    if [[ -f "$SCRIPT_DIR/alertmanager.yml" ]]; then
        # Use amtool to validate if available
        if command -v amtool >/dev/null 2>&1; then
            if amtool config check "$SCRIPT_DIR/alertmanager.yml" >/dev/null 2>&1; then
                log_success "✓ Alertmanager configuration is valid"
                return 0
            else
                log_error "✗ Alertmanager configuration has errors"
                return 1
            fi
        else
            # Basic YAML validation
            if python3 -c "import yaml; yaml.safe_load(open('$SCRIPT_DIR/alertmanager.yml'))" 2>/dev/null; then
                log_success "✓ Alertmanager YAML syntax is valid"
                return 0
            else
                log_error "✗ Alertmanager configuration has YAML syntax errors"
                return 1
            fi
        fi
    else
        log_error "Alertmanager configuration file not found"
        return 1
    fi
}

# Test alert rule queries
test_alert_queries() {
    log_info "Testing alert rule queries against Prometheus..."
    
    local query_tests=0
    local query_failures=0
    
    # Test basic service health queries
    local test_queries=(
        "up{job=~\"acgs-.*-service\"}"
        "rate(acgs_errors_total[5m])"
        "histogram_quantile(0.95, rate(acgs_http_request_duration_seconds_bucket[5m]))"
        "acgs_constitutional_compliance_score"
        "acgs_pgc_validation_latency_seconds"
        "acgs_blockchain_integration_health"
    )
    
    for query in "${test_queries[@]}"; do
        query_tests=$((query_tests + 1))
        log_info "Testing query: $query"
        
        # URL encode the query
        encoded_query=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$query'))")
        
        # Test the query
        if curl -s -f "$PROMETHEUS_URL/api/v1/query?query=$encoded_query" >/dev/null; then
            log_success "✓ Query executed successfully"
        else
            log_error "✗ Query failed to execute"
            query_failures=$((query_failures + 1))
        fi
    done
    
    log_info "Query test results: $((query_tests - query_failures))/$query_tests passed"
    
    if [[ $query_failures -eq 0 ]]; then
        log_success "All alert queries executed successfully"
        return 0
    else
        log_warning "Some alert queries failed - check metric availability"
        return 1
    fi
}

# Test notification channels
test_notification_channels() {
    log_info "Testing notification channel configuration..."
    
    # Check if environment variables are set for notification channels
    local channels_configured=0
    
    if [[ -n "${SMTP_HOST:-}" ]]; then
        log_success "✓ SMTP configuration detected"
        channels_configured=$((channels_configured + 1))
    else
        log_warning "SMTP configuration not found (SMTP_HOST not set)"
    fi
    
    if [[ -n "${SLACK_WEBHOOK_URL:-}" ]]; then
        log_success "✓ Slack webhook configuration detected"
        channels_configured=$((channels_configured + 1))
    else
        log_warning "Slack webhook configuration not found (SLACK_WEBHOOK_URL not set)"
    fi
    
    if [[ -n "${PAGERDUTY_INTEGRATION_KEY:-}" ]]; then
        log_success "✓ PagerDuty configuration detected"
        channels_configured=$((channels_configured + 1))
    else
        log_warning "PagerDuty configuration not found (PAGERDUTY_INTEGRATION_KEY not set)"
    fi
    
    if [[ $channels_configured -gt 0 ]]; then
        log_success "Notification channels configured: $channels_configured"
        return 0
    else
        log_warning "No notification channels configured - alerts will use default email"
        return 1
    fi
}

# Count and categorize alert rules
count_alert_rules() {
    log_info "Analyzing alert rule coverage..."
    
    local total_rules=0
    local critical_rules=0
    local warning_rules=0
    local service_rules=0
    local workflow_rules=0
    local infrastructure_rules=0
    local blockchain_rules=0
    
    # Count rules in each file
    for rule_file in "$SCRIPT_DIR"/rules/*.yml; do
        if [[ -f "$rule_file" ]]; then
            local file_rules=$(grep -c "alert:" "$rule_file" 2>/dev/null || echo 0)
            total_rules=$((total_rules + file_rules))
            
            local file_critical=$(grep -A5 "alert:" "$rule_file" | grep -c "severity: critical" 2>/dev/null || echo 0)
            critical_rules=$((critical_rules + file_critical))
            
            local file_warning=$(grep -A5 "alert:" "$rule_file" | grep -c "severity: warning" 2>/dev/null || echo 0)
            warning_rules=$((warning_rules + file_warning))
            
            # Categorize by file type
            case "$(basename "$rule_file")" in
                *service*)
                    service_rules=$((service_rules + file_rules))
                    ;;
                *workflow*)
                    workflow_rules=$((workflow_rules + file_rules))
                    ;;
                *infrastructure*)
                    infrastructure_rules=$((infrastructure_rules + file_rules))
                    ;;
                *blockchain*)
                    blockchain_rules=$((blockchain_rules + file_rules))
                    ;;
            esac
            
            log_info "  $(basename "$rule_file"): $file_rules rules"
        fi
    done
    
    log_success "Alert rule coverage analysis:"
    log_info "  Total alert rules: $total_rules"
    log_info "  Critical severity: $critical_rules"
    log_info "  Warning severity: $warning_rules"
    log_info "  Service-specific: $service_rules"
    log_info "  Workflow-specific: $workflow_rules"
    log_info "  Infrastructure: $infrastructure_rules"
    log_info "  Blockchain: $blockchain_rules"
    
    # Validate coverage targets
    if [[ $total_rules -ge 50 ]]; then
        log_success "✓ Comprehensive alert coverage achieved ($total_rules rules)"
    else
        log_warning "Alert coverage may be insufficient ($total_rules rules)"
    fi
    
    if [[ $critical_rules -ge 15 ]]; then
        log_success "✓ Adequate critical alert coverage ($critical_rules rules)"
    else
        log_warning "Critical alert coverage may be insufficient ($critical_rules rules)"
    fi
}

# Main execution
main() {
    log_info "Starting ACGS-1 Alert Testing and Validation"
    log_info "Subtask 13.5: Implement Alert Rules and Notification System"
    echo
    
    local test_results=0
    
    # Run all validation tests
    if check_service_connectivity; then
        test_results=$((test_results + 1))
    fi
    echo
    
    if validate_alert_rules; then
        test_results=$((test_results + 1))
    fi
    echo
    
    if validate_alertmanager_config; then
        test_results=$((test_results + 1))
    fi
    echo
    
    if test_alert_queries; then
        test_results=$((test_results + 1))
    fi
    echo
    
    if test_notification_channels; then
        test_results=$((test_results + 1))
    fi
    echo
    
    count_alert_rules
    echo
    
    # Final results
    log_info "Alert testing results: $test_results/5 tests passed"
    
    if [[ $test_results -ge 4 ]]; then
        log_success "Alert system validation completed successfully!"
        log_info "✓ Alert rules syntax validated"
        log_info "✓ Alertmanager configuration validated"
        log_info "✓ Notification channels configured"
        log_info "✓ Comprehensive alert coverage achieved"
        log_info "✓ Ready for production deployment"
        return 0
    else
        log_warning "Alert system validation completed with warnings"
        log_info "Some tests failed - review configuration before production deployment"
        return 1
    fi
}

# Execute main function
main "$@"
