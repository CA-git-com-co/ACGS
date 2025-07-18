# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# ACGS-1 Enterprise Performance Monitoring Script
# Real-time performance tracking and enterprise compliance reporting

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PERFORMANCE_LOG="/tmp/acgs-performance-monitor.log"
METRICS_FILE="/tmp/pipeline-performance-metrics.json"

# Enterprise targets
ENTERPRISE_BUILD_TARGET_MINUTES=${ENTERPRISE_BUILD_TARGET_MINUTES:-5}
ENTERPRISE_AVAILABILITY_TARGET=${ENTERPRISE_AVAILABILITY_TARGET:-99.5}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Global variables
START_TIME=""
PIPELINE_ID=""
CURRENT_STAGE=""
STAGE_START_TIME=""

# Logging function
log_performance() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")
            echo -e "${BLUE}[PERF-INFO]${NC} $message" | tee -a "$PERFORMANCE_LOG"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[PERF-SUCCESS]${NC} $message" | tee -a "$PERFORMANCE_LOG"
            ;;
        "WARNING")
            echo -e "${YELLOW}[PERF-WARNING]${NC} $message" | tee -a "$PERFORMANCE_LOG"
            ;;
        "ERROR")
            echo -e "${RED}[PERF-ERROR]${NC} $message" | tee -a "$PERFORMANCE_LOG"
            ;;
        "METRIC")
            echo -e "${PURPLE}[PERF-METRIC]${NC} $message" | tee -a "$PERFORMANCE_LOG"
            ;;
    esac
    echo "[$timestamp] [$level] $message" >> "$PERFORMANCE_LOG"
}

# Initialize performance monitoring
initialize_monitoring() {
    START_TIME=$(date +%s)
    PIPELINE_ID="${GITHUB_RUN_ID:-local}-$(date +%s)"
    
    log_performance "INFO" "🚀 Enterprise Performance Monitoring Initialized"
    log_performance "INFO" "Pipeline ID: $PIPELINE_ID"
    log_performance "INFO" "Start Time: $(date -d @$START_TIME)"
    log_performance "INFO" "Enterprise Target: <$ENTERPRISE_BUILD_TARGET_MINUTES minutes"
    log_performance "INFO" "Availability Target: >$ENTERPRISE_AVAILABILITY_TARGET%"
    
    # Create initial metrics structure
    cat > "$METRICS_FILE" << EOF
{
  "pipeline_id": "$PIPELINE_ID",
  "start_time": $START_TIME,
  "start_time_iso": "$(date -u -d @$START_TIME +%Y-%m-%dT%H:%M:%SZ)",
  "enterprise_targets": {
    "build_duration_minutes": $ENTERPRISE_BUILD_TARGET_MINUTES,
    "availability_percentage": $ENTERPRISE_AVAILABILITY_TARGET
  },
  "stages": {},
  "overall_metrics": {},
  "compliance_status": "in_progress"
}
EOF
    
    log_performance "SUCCESS" "✅ Performance monitoring initialized"
}

# Start stage monitoring
start_stage() {
    local stage_name="$1"
    CURRENT_STAGE="$stage_name"
    STAGE_START_TIME=$(date +%s)
    
    log_performance "INFO" "📊 Starting stage: $stage_name"
    log_performance "METRIC" "Stage '$stage_name' started at $(date -d @$STAGE_START_TIME)"
    
    # Update metrics file
    local temp_file=$(mktemp)
    jq --arg stage "$stage_name" --arg start_time "$STAGE_START_TIME" \
       '.stages[$stage] = {
          "start_time": ($start_time | tonumber),
          "start_time_iso": (($start_time | tonumber) | strftime("%Y-%m-%dT%H:%M:%SZ")),
          "status": "running"
        }' "$METRICS_FILE" > "$temp_file" && mv "$temp_file" "$METRICS_FILE"
}

# End stage monitoring
end_stage() {
    local stage_name="${1:-$CURRENT_STAGE}"
    local status="${2:-success}"
    local end_time=$(date +%s)
    local duration=$((end_time - STAGE_START_TIME))
    
    log_performance "INFO" "📊 Ending stage: $stage_name"
    log_performance "METRIC" "Stage '$stage_name' completed in ${duration}s with status: $status"
    
    # Update metrics file
    local temp_file=$(mktemp)
    jq --arg stage "$stage_name" --arg end_time "$end_time" --arg duration "$duration" --arg status "$status" \
       '.stages[$stage] += {
          "end_time": ($end_time | tonumber),
          "end_time_iso": (($end_time | tonumber) | strftime("%Y-%m-%dT%H:%M:%SZ")),
          "duration_seconds": ($duration | tonumber),
          "duration_minutes": (($duration | tonumber) / 60),
          "status": $status
        }' "$METRICS_FILE" > "$temp_file" && mv "$temp_file" "$METRICS_FILE"
    
    # Check if stage exceeded targets
    local duration_minutes=$(echo "scale=2; $duration / 60" | bc)
    if (( $(echo "$duration_minutes > 2" | bc -l) )); then
        log_performance "WARNING" "⚠️ Stage '$stage_name' took ${duration_minutes} minutes (>2 min threshold)"
    else
        log_performance "SUCCESS" "✅ Stage '$stage_name' completed within performance targets"
    fi
}

# Record system metrics
record_system_metrics() {
    local stage_name="${1:-current}"
    
    log_performance "INFO" "📈 Recording system metrics for stage: $stage_name"
    
    # Collect system metrics
    local memory_usage=$(free | awk '/^Mem:/ {printf "%.1f", $3/$2 * 100.0}')
    local disk_usage=$(df / | awk 'NR==2 {printf "%.1f", $5}' | sed 's/%//')
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//')
    local load_average=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    
    # Update metrics file with system metrics
    local temp_file=$(mktemp)
    jq --arg stage "$stage_name" --arg memory "$memory_usage" --arg disk "$disk_usage" \
       --arg cpu "$cpu_usage" --arg load "$load_average" \
       '.stages[$stage] += {
          "system_metrics": {
            "memory_usage_percent": ($memory | tonumber),
            "disk_usage_percent": ($disk | tonumber),
            "cpu_usage_percent": ($cpu | tonumber),
            "load_average": ($load | tonumber)
          }
        }' "$METRICS_FILE" > "$temp_file" && mv "$temp_file" "$METRICS_FILE"
    
    log_performance "METRIC" "System metrics - Memory: ${memory_usage}%, Disk: ${disk_usage}%, CPU: ${cpu_usage}%, Load: ${load_average}"
}

# Calculate overall pipeline metrics
calculate_overall_metrics() {
    local end_time=$(date +%s)
    local total_duration=$((end_time - START_TIME))
    local total_duration_minutes=$(echo "scale=2; $total_duration / 60" | bc)
    
    log_performance "INFO" "📊 Calculating overall pipeline metrics"
    log_performance "METRIC" "Total pipeline duration: ${total_duration}s (${total_duration_minutes} minutes)"
    
    # Determine compliance status
    local compliance_status="compliant"
    local availability_status="compliant"
    
    # Check duration compliance
    if (( $(echo "$total_duration_minutes > $ENTERPRISE_BUILD_TARGET_MINUTES" | bc -l) )); then
        compliance_status="non_compliant"
        log_performance "ERROR" "❌ Pipeline duration ${total_duration_minutes}m exceeds target ${ENTERPRISE_BUILD_TARGET_MINUTES}m"
    else
        log_performance "SUCCESS" "✅ Pipeline duration within enterprise target"
    fi
    
    # Calculate success rate (simplified - based on stage statuses)
    local total_stages=$(jq '.stages | length' "$METRICS_FILE")
    local successful_stages=$(jq '[.stages[] | select(.status == "success")] | length' "$METRICS_FILE")
    local success_rate=0
    
    if [ "$total_stages" -gt 0 ]; then
        success_rate=$(echo "scale=2; $successful_stages * 100 / $total_stages" | bc)
    fi
    
    # Check availability compliance
    if (( $(echo "$success_rate < $ENTERPRISE_AVAILABILITY_TARGET" | bc -l) )); then
        availability_status="non_compliant"
        log_performance "ERROR" "❌ Success rate ${success_rate}% below target ${ENTERPRISE_AVAILABILITY_TARGET}%"
    else
        log_performance "SUCCESS" "✅ Success rate meets enterprise availability target"
    fi
    
    # Update metrics file with overall metrics
    local temp_file=$(mktemp)
    jq --arg end_time "$end_time" --arg total_duration "$total_duration" \
       --arg total_duration_minutes "$total_duration_minutes" --arg success_rate "$success_rate" \
       --arg compliance_status "$compliance_status" --arg availability_status "$availability_status" \
       '.overall_metrics = {
          "end_time": ($end_time | tonumber),
          "end_time_iso": (($end_time | tonumber) | strftime("%Y-%m-%dT%H:%M:%SZ")),
          "total_duration_seconds": ($total_duration | tonumber),
          "total_duration_minutes": ($total_duration_minutes | tonumber),
          "success_rate_percentage": ($success_rate | tonumber),
          "enterprise_compliance": {
            "duration_compliant": ($compliance_status == "compliant"),
            "availability_compliant": ($availability_status == "compliant"),
            "overall_status": (if ($compliance_status == "compliant" and $availability_status == "compliant") then "compliant" else "non_compliant" end)
          }
        } | .compliance_status = .overall_metrics.enterprise_compliance.overall_status' \
       "$METRICS_FILE" > "$temp_file" && mv "$temp_file" "$METRICS_FILE"
    
    log_performance "METRIC" "Overall compliance status: $(jq -r '.compliance_status' "$METRICS_FILE")"
}

# Generate enterprise performance report
generate_performance_report() {
    log_performance "INFO" "📋 Generating enterprise performance report"
    
    # Calculate final metrics
    calculate_overall_metrics
    
    # Create human-readable report
    local report_file="/tmp/enterprise-performance-report.md"
    
    cat > "$report_file" << EOF
# ACGS-1 Enterprise Performance Report

**Pipeline ID:** $(jq -r '.pipeline_id' "$METRICS_FILE")
**Generated:** $(date)
**Duration:** $(jq -r '.overall_metrics.total_duration_minutes' "$METRICS_FILE") minutes

## Enterprise Compliance Status

- **Overall Status:** $(jq -r '.compliance_status' "$METRICS_FILE" | tr '[:lower:]' '[:upper:]')
- **Duration Target:** <$ENTERPRISE_BUILD_TARGET_MINUTES minutes
- **Actual Duration:** $(jq -r '.overall_metrics.total_duration_minutes' "$METRICS_FILE") minutes
- **Duration Compliant:** $(jq -r '.overall_metrics.enterprise_compliance.duration_compliant' "$METRICS_FILE")
- **Availability Target:** >$ENTERPRISE_AVAILABILITY_TARGET%
- **Actual Success Rate:** $(jq -r '.overall_metrics.success_rate_percentage' "$METRICS_FILE")%
- **Availability Compliant:** $(jq -r '.overall_metrics.enterprise_compliance.availability_compliant' "$METRICS_FILE")

## Stage Performance Breakdown

EOF
    
    # Add stage details
    jq -r '.stages | to_entries[] | "- **\(.key):** \(.value.duration_minutes // 0) minutes (\(.value.status // "unknown"))"' "$METRICS_FILE" >> "$report_file"
    
    cat >> "$report_file" << EOF

## Performance Recommendations

EOF
    
    # Add recommendations based on compliance status
    if [ "$(jq -r '.compliance_status' "$METRICS_FILE")" = "non_compliant" ]; then
        cat >> "$report_file" << EOF
⚠️ **CRITICAL:** Pipeline does not meet enterprise standards.

### Immediate Actions Required:
1. **Performance Optimization:** Implement parallel job execution
2. **Caching Enhancement:** Improve dependency caching strategies
3. **Infrastructure Scaling:** Consider upgrading runner resources
4. **Process Optimization:** Review and optimize slow stages

EOF
    else
        cat >> "$report_file" << EOF
✅ **SUCCESS:** Pipeline meets all enterprise standards.

### Continuous Improvement Opportunities:
1. Monitor performance trends over time
2. Implement additional caching optimizations
3. Consider further parallelization opportunities

EOF
    fi
    
    log_performance "SUCCESS" "✅ Performance report generated: $report_file"
    log_performance "INFO" "📊 Metrics file available: $METRICS_FILE"
}

# Monitor stage with timeout
monitor_stage_with_timeout() {
    local stage_name="$1"
    local timeout_minutes="${2:-10}"
    local command="$3"
    
    start_stage "$stage_name"
    
    log_performance "INFO" "⏱️ Monitoring stage '$stage_name' with ${timeout_minutes}m timeout"
    
    # Execute command with timeout
    if timeout "${timeout_minutes}m" bash -c "$command"; then
        end_stage "$stage_name" "success"
        record_system_metrics "$stage_name"
        return 0
    else
        local exit_code=$?
        if [ $exit_code -eq 124 ]; then
            log_performance "ERROR" "❌ Stage '$stage_name' timed out after ${timeout_minutes} minutes"
            end_stage "$stage_name" "timeout"
        else
            log_performance "ERROR" "❌ Stage '$stage_name' failed with exit code $exit_code"
            end_stage "$stage_name" "failed"
        fi
        record_system_metrics "$stage_name"
        return $exit_code
    fi
}

# Main monitoring functions
case "${1:-help}" in
    "init")
        initialize_monitoring
        ;;
    "start-stage")
        start_stage "$2"
        ;;
    "end-stage")
        end_stage "$2" "${3:-success}"
        ;;
    "record-metrics")
        record_system_metrics "${2:-current}"
        ;;
    "monitor-stage")
        monitor_stage_with_timeout "$2" "${3:-10}" "$4"
        ;;
    "generate-report")
        generate_performance_report
        ;;
    "help"|*)
        echo "ACGS-1 Enterprise Performance Monitor"
        echo "Usage: $0 {init|start-stage|end-stage|record-metrics|monitor-stage|generate-report}"
        echo ""
        echo "Commands:"
        echo "  init                           Initialize performance monitoring"
        echo "  start-stage <name>             Start monitoring a stage"
        echo "  end-stage <name> [status]      End monitoring a stage"
        echo "  record-metrics [stage]         Record system metrics"
        echo "  monitor-stage <name> <timeout> <command>  Monitor stage with timeout"
        echo "  generate-report                Generate final performance report"
        ;;
esac
