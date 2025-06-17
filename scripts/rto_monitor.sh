#!/bin/bash
# ACGS-1 RTO Monitoring Script
# Automated RTO validation and alerting for continuous monitoring

set -e

PROJECT_ROOT="/home/dislove/ACGS-1"
LOG_DIR="$PROJECT_ROOT/logs/rto_monitoring"
ALERT_THRESHOLD=3  # Number of consecutive failures before alert

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create log directory
mkdir -p "$LOG_DIR"

# Function to log with timestamp
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_DIR/rto_monitor.log"
}

# Function to send alert (placeholder for actual alerting system)
send_alert() {
    local severity="$1"
    local message="$2"
    
    log "ALERT [$severity]: $message"
    
    # In production, this would integrate with:
    # - Email notifications
    # - Slack/Teams webhooks
    # - PagerDuty/OpsGenie
    # - SMS alerts
    
    echo -e "${RED}🚨 ALERT [$severity]: $message${NC}"
}

# Function to check RTO compliance
check_rto_compliance() {
    local test_type="$1"
    
    log "Running RTO validation test: $test_type"
    
    # Run RTO validation
    cd "$PROJECT_ROOT"
    python3 scripts/rto_validation_test.py --test-type "$test_type" > "$LOG_DIR/latest_test.json" 2>&1
    
    # Check if test was successful
    if [ $? -eq 0 ]; then
        # Parse results
        local compliance=$(cat "$LOG_DIR/latest_test.json" | grep -o '"rto_compliance": [^,]*' | cut -d' ' -f2)
        local overall_status=$(cat "$LOG_DIR/latest_test.json" | grep -o '"overall_status": "[^"]*"' | cut -d'"' -f4)
        
        if [ "$compliance" = "true" ]; then
            log "✅ RTO compliance check PASSED for $test_type"
            echo -e "${GREEN}✅ RTO compliance: PASSED${NC}"
            return 0
        else
            log "❌ RTO compliance check FAILED for $test_type"
            echo -e "${RED}❌ RTO compliance: FAILED${NC}"
            return 1
        fi
    else
        log "❌ RTO validation test failed to execute"
        echo -e "${RED}❌ RTO test execution: FAILED${NC}"
        return 1
    fi
}

# Function to check service health
check_service_health() {
    local services=("8000" "8001" "8002" "8003" "8004" "8005" "8006")
    local service_names=("auth" "ac" "integrity" "fv" "gs" "pgc" "ec")
    local failed_services=()
    
    log "Checking service health..."
    
    for i in "${!services[@]}"; do
        local port="${services[$i]}"
        local name="${service_names[$i]}"
        
        # Check if service is responding
        if curl -s -f "http://localhost:$port/health" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $name service (port $port): OK${NC}"
        else
            echo -e "${RED}❌ $name service (port $port): FAILED${NC}"
            failed_services+=("$name")
        fi
    done
    
    if [ ${#failed_services[@]} -eq 0 ]; then
        log "✅ All services are healthy"
        return 0
    else
        log "❌ Failed services: ${failed_services[*]}"
        return 1
    fi
}

# Function to generate daily RTO report
generate_daily_report() {
    local report_file="$LOG_DIR/daily_rto_report_$(date +%Y%m%d).txt"
    
    log "Generating daily RTO report: $report_file"
    
    {
        echo "ACGS-1 Daily RTO Compliance Report"
        echo "=================================="
        echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Constitution Hash: cdd01ef066bc6cf2"
        echo ""
        
        # Run comprehensive RTO test
        cd "$PROJECT_ROOT"
        python3 scripts/rto_validation_test.py --test-type full --report 2>/dev/null || echo "RTO test failed"
        
        echo ""
        echo "Service Health Summary:"
        echo "----------------------"
        check_service_health
        
        echo ""
        echo "Recent RTO Test Results:"
        echo "----------------------"
        if [ -f "$LOG_DIR/latest_test.json" ]; then
            cat "$LOG_DIR/latest_test.json" | grep -E '"overall_status"|"rto_compliance"|"total_test_time"' || echo "No recent test data"
        else
            echo "No recent test data available"
        fi
        
    } > "$report_file"
    
    echo -e "${BLUE}📄 Daily report generated: $report_file${NC}"
}

# Function to check failure count and alert
check_failure_count() {
    local failure_file="$LOG_DIR/failure_count.txt"
    local current_failures=0
    
    # Read current failure count
    if [ -f "$failure_file" ]; then
        current_failures=$(cat "$failure_file")
    fi
    
    # Check latest test result
    if check_rto_compliance "health"; then
        # Reset failure count on success
        echo "0" > "$failure_file"
    else
        # Increment failure count
        current_failures=$((current_failures + 1))
        echo "$current_failures" > "$failure_file"
        
        # Send alert if threshold exceeded
        if [ "$current_failures" -ge "$ALERT_THRESHOLD" ]; then
            send_alert "HIGH" "RTO compliance failed $current_failures consecutive times"
        elif [ "$current_failures" -eq 1 ]; then
            send_alert "MEDIUM" "RTO compliance failure detected"
        fi
    fi
    
    log "Current failure count: $current_failures"
}

# Main execution
main() {
    local action="${1:-monitor}"
    
    case "$action" in
        "monitor")
            log "🔍 Starting RTO monitoring check"
            check_failure_count
            ;;
        "health")
            log "🏥 Running service health check"
            check_service_health
            ;;
        "test")
            local test_type="${2:-health}"
            log "🧪 Running RTO test: $test_type"
            check_rto_compliance "$test_type"
            ;;
        "report")
            log "📊 Generating daily RTO report"
            generate_daily_report
            ;;
        "alert-test")
            log "🚨 Testing alert system"
            send_alert "TEST" "This is a test alert from RTO monitoring system"
            ;;
        *)
            echo "Usage: $0 {monitor|health|test|report|alert-test}"
            echo ""
            echo "Commands:"
            echo "  monitor     - Run continuous RTO monitoring (default)"
            echo "  health      - Check service health status"
            echo "  test [type] - Run RTO validation test (health|services|constitutional|backup|emergency|full)"
            echo "  report      - Generate daily RTO compliance report"
            echo "  alert-test  - Test alert notification system"
            echo ""
            echo "Examples:"
            echo "  $0 monitor"
            echo "  $0 test constitutional"
            echo "  $0 report"
            exit 1
            ;;
    esac
}

# Execute main function with all arguments
main "$@"
