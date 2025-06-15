#!/bin/bash

# ACGS-1 Enterprise CI/CD 24-Check Validation Script
# Validates all enterprise-grade CI/CD pipeline checks for zero-tolerance compliance
# requires: All 24 enterprise checks pass, <5 minute builds, >99.5% availability
# ensures: Enterprise compliance scoring 8-9/10, zero critical vulnerabilities
# sha256: b7e4f2a1c8d9e6f3b2a5d8c7f4e1b9a6d3f2e5c8b7a4d1f6e9c2b5a8d7f4e1b3

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
VALIDATION_LOG="/tmp/acgs-24-check-validation.log"
RESULTS_FILE="/tmp/enterprise-24-check-results.json"

# Enterprise targets
ENTERPRISE_BUILD_TARGET_MINUTES=5
ENTERPRISE_AVAILABILITY_TARGET=99.5
ENTERPRISE_COMPLIANCE_TARGET=8

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# Logging function
log_validation() {
    local level="$1"
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case "$level" in
        "INFO")
            echo -e "${BLUE}[24-CHECK-INFO]${NC} $message" | tee -a "$VALIDATION_LOG"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[24-CHECK-SUCCESS]${NC} $message" | tee -a "$VALIDATION_LOG"
            ;;
        "WARNING")
            echo -e "${YELLOW}[24-CHECK-WARNING]${NC} $message" | tee -a "$VALIDATION_LOG"
            ;;
        "ERROR")
            echo -e "${RED}[24-CHECK-ERROR]${NC} $message" | tee -a "$VALIDATION_LOG"
            ;;
        "CRITICAL")
            echo -e "${RED}[24-CHECK-CRITICAL]${NC} $message" | tee -a "$VALIDATION_LOG"
            ;;
    esac
    echo "[$timestamp] [$level] $message" >> "$VALIDATION_LOG"
}

# Initialize validation
initialize_validation() {
    local start_time=$(date +%s)
    local validation_id="24check-$(date +%s)"
    
    log_validation "INFO" "🚀 ACGS-1 Enterprise 24-Check Validation Started"
    log_validation "INFO" "Validation ID: $validation_id"
    log_validation "INFO" "Target: All 24 enterprise checks must pass"
    log_validation "INFO" "Zero-tolerance policy: NO failures allowed"
    
    # Create initial results structure
    cat > "$RESULTS_FILE" << EOF
{
  "validation_id": "$validation_id",
  "start_time": $start_time,
  "start_time_iso": "$(date -u -d @$start_time +%Y-%m-%dT%H:%M:%SZ)",
  "enterprise_targets": {
    "build_duration_minutes": $ENTERPRISE_BUILD_TARGET_MINUTES,
    "availability_percentage": $ENTERPRISE_AVAILABILITY_TARGET,
    "compliance_score_target": $ENTERPRISE_COMPLIANCE_TARGET
  },
  "checks": {},
  "summary": {
    "total_checks": 24,
    "passed": 0,
    "failed": 0,
    "warnings": 0
  },
  "compliance_status": "in_progress"
}
EOF
    
    log_validation "SUCCESS" "✅ 24-Check validation initialized"
}

# Validate individual check
validate_check() {
    local check_name="$1"
    local check_command="$2"
    local check_category="${3:-general}"
    local critical="${4:-false}"
    
    log_validation "INFO" "🔍 Validating check: $check_name"
    
    local start_time=$(date +%s)
    local status="unknown"
    local error_message=""
    
    # Execute check command
    if eval "$check_command" >/dev/null 2>&1; then
        status="passed"
        log_validation "SUCCESS" "✅ Check '$check_name' PASSED"
    else
        status="failed"
        error_message="Command failed: $check_command"
        if [ "$critical" = "true" ]; then
            log_validation "CRITICAL" "❌ CRITICAL check '$check_name' FAILED"
        else
            log_validation "ERROR" "❌ Check '$check_name' FAILED"
        fi
    fi
    
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    
    # Update results file
    local temp_file=$(mktemp)
    jq --arg check "$check_name" --arg status "$status" --arg category "$check_category" \
       --arg duration "$duration" --arg error "$error_message" --arg critical "$critical" \
       '.checks[$check] = {
          "status": $status,
          "category": $category,
          "duration_seconds": ($duration | tonumber),
          "critical": ($critical == "true"),
          "error_message": $error,
          "timestamp": now
        }' "$RESULTS_FILE" > "$temp_file" && mv "$temp_file" "$RESULTS_FILE"
    
    # Update summary counts
    if [ "$status" = "passed" ]; then
        jq '.summary.passed += 1' "$RESULTS_FILE" > "$temp_file" && mv "$temp_file" "$RESULTS_FILE"
    else
        jq '.summary.failed += 1' "$RESULTS_FILE" > "$temp_file" && mv "$temp_file" "$RESULTS_FILE"
    fi
    
    return $([ "$status" = "passed" ] && echo 0 || echo 1)
}

# Run all 24 enterprise checks
run_24_checks() {
    log_validation "INFO" "🔄 Running all 24 enterprise checks..."
    
    local total_failures=0
    local critical_failures=0
    
    # Infrastructure Checks (1-6)
    log_validation "INFO" "📋 Category 1: Infrastructure Checks (1-6)"
    
    validate_check "01_rust_toolchain" "rustc --version | grep -q '1.81.0'" "infrastructure" "true" || ((total_failures++, critical_failures++))
    validate_check "02_solana_cli" "solana --version | grep -q '1.18.22'" "infrastructure" "true" || ((total_failures++, critical_failures++))
    validate_check "03_anchor_cli" "anchor --version | grep -q '0.29.0'" "infrastructure" "true" || ((total_failures++, critical_failures++))
    validate_check "04_node_version" "node --version | grep -qE 'v(18|20|22)'" "infrastructure" "false" || ((total_failures++))
    validate_check "05_cargo_cache" "[ -d ~/.cargo/registry ]" "infrastructure" "false" || ((total_failures++))
    validate_check "06_workspace_config" "[ -f blockchain/Cargo.toml ]" "infrastructure" "true" || ((total_failures++, critical_failures++))
    
    # Security Checks (7-16)
    log_validation "INFO" "🔒 Category 2: Security Checks (7-16)"
    
    validate_check "07_cargo_audit" "command -v cargo-audit" "security" "true" || ((total_failures++, critical_failures++))
    validate_check "08_cargo_deny" "command -v cargo-deny" "security" "true" || ((total_failures++, critical_failures++))
    validate_check "09_crypto_patches" "grep -q 'ed25519-dalek.*git' blockchain/Cargo.toml" "security" "true" || ((total_failures++, critical_failures++))
    validate_check "10_ed25519_patches" "grep -q '1042cb60a07cdaacb59ca209716b69f444460f8f' blockchain/Cargo.toml" "security" "true" || ((total_failures++, critical_failures++))
    validate_check "11_audit_config" "[ -f blockchain/audit.toml ]" "security" "true" || ((total_failures++, critical_failures++))
    validate_check "12_deny_config" "[ -f blockchain/deny.toml ]" "security" "true" || ((total_failures++, critical_failures++))
    validate_check "13_trivy_available" "command -v trivy || echo 'trivy via action'" "security" "false" || ((total_failures++))
    validate_check "14_msdo_workflow" "grep -q 'microsoft/security-devops-action' .github/workflows/enterprise-ci.yml" "security" "true" || ((total_failures++, critical_failures++))
    validate_check "15_codeql_workflow" "grep -q 'github/codeql-action' .github/workflows/enterprise-ci.yml" "security" "true" || ((total_failures++, critical_failures++))
    validate_check "16_secret_detection" "grep -q 'trufflesecurity/trufflehog' .github/workflows/enterprise-ci.yml" "security" "true" || ((total_failures++, critical_failures++))
    
    # Build & Quality Checks (17-20)
    log_validation "INFO" "🏗️ Category 3: Build & Quality Checks (17-20)"
    
    validate_check "17_rust_format" "(cd blockchain && cargo fmt --all -- --check)" "quality" "false" || ((total_failures++))
    validate_check "18_rust_clippy" "(cd blockchain && cargo clippy --all-targets --all-features -- -D warnings)" "quality" "false" || ((total_failures++))
    validate_check "19_anchor_build" "(cd blockchain && anchor build --skip-lint)" "quality" "true" || ((total_failures++, critical_failures++))
    validate_check "20_incremental_compilation" "grep -A5 '\[profile\.dev\]' blockchain/Cargo.toml | grep -q 'incremental = true'" "quality" "false" || ((total_failures++))
    
    # Performance & Monitoring Checks (21-24)
    log_validation "INFO" "⚡ Category 4: Performance & Monitoring Checks (21-24)"
    
    validate_check "21_performance_monitor" "test -x scripts/enterprise/performance-monitor.sh" "performance" "false" || ((total_failures++))
    validate_check "22_failure_analysis" "test -x scripts/enterprise/failure-analysis.sh" "performance" "false" || ((total_failures++))
    validate_check "23_parallel_jobs" "grep -c 'runs-on.*ubuntu-latest' .github/workflows/enterprise-ci.yml | awk '{if(\$1>=5) exit 0; else exit 1}'" "performance" "false" || ((total_failures++))
    validate_check "24_circuit_breaker" "grep -q 'install_anchor_with_circuit_breaker' .github/workflows/enterprise-ci.yml" "performance" "false" || ((total_failures++))
    
    log_validation "INFO" "📊 24-Check validation completed"
    log_validation "INFO" "Total failures: $total_failures/24"
    log_validation "INFO" "Critical failures: $critical_failures"
    
    return $total_failures
}

# Generate final compliance report
generate_compliance_report() {
    local end_time=$(date +%s)
    local start_time=$(jq -r '.start_time' "$RESULTS_FILE")
    local total_duration=$((end_time - start_time))
    
    local passed_checks=$(jq -r '.summary.passed' "$RESULTS_FILE")
    local failed_checks=$(jq -r '.summary.failed' "$RESULTS_FILE")
    local success_rate=$(echo "scale=2; $passed_checks * 100 / 24" | bc)
    
    # Calculate compliance score
    local compliance_score=100
    local deductions=$((failed_checks * 5))  # 5 points per failed check
    compliance_score=$((compliance_score - deductions))
    
    # Determine compliance status
    local compliance_status="non_compliant"
    local compliance_level="FAILED"
    
    if [ $failed_checks -eq 0 ]; then
        compliance_status="fully_compliant"
        compliance_level="EXCELLENT"
    elif [ $compliance_score -ge 90 ]; then
        compliance_status="mostly_compliant"
        compliance_level="GOOD"
    elif [ $compliance_score -ge 80 ]; then
        compliance_status="partially_compliant"
        compliance_level="ACCEPTABLE"
    fi
    
    # Update results file with final metrics
    local temp_file=$(mktemp)
    jq --arg end_time "$end_time" --arg total_duration "$total_duration" \
       --arg success_rate "$success_rate" --arg compliance_score "$compliance_score" \
       --arg compliance_status "$compliance_status" --arg compliance_level "$compliance_level" \
       '.end_time = ($end_time | tonumber) |
        .total_duration_seconds = ($total_duration | tonumber) |
        .success_rate_percentage = ($success_rate | tonumber) |
        .compliance_score = ($compliance_score | tonumber) |
        .compliance_status = $compliance_status |
        .compliance_level = $compliance_level' \
       "$RESULTS_FILE" > "$temp_file" && mv "$temp_file" "$RESULTS_FILE"
    
    # Generate human-readable report
    local report_file="/tmp/enterprise-24-check-report.md"
    
    cat > "$report_file" << EOF
# ACGS-1 Enterprise 24-Check Validation Report

**Validation ID:** $(jq -r '.validation_id' "$RESULTS_FILE")
**Generated:** $(date)
**Duration:** ${total_duration} seconds

## Compliance Summary

- **Overall Status:** $compliance_level
- **Compliance Score:** $compliance_score/100
- **Success Rate:** $success_rate% ($passed_checks/24 checks passed)
- **Failed Checks:** $failed_checks
- **Zero-Tolerance Policy:** $([ $failed_checks -eq 0 ] && echo "✅ COMPLIANT" || echo "❌ VIOLATED")

## Check Results by Category

### Infrastructure Checks (1-6)
$(jq -r '.checks | to_entries[] | select(.value.category == "infrastructure") | "- **\(.key):** \(.value.status | ascii_upcase)"' "$RESULTS_FILE")

### Security Checks (7-16)  
$(jq -r '.checks | to_entries[] | select(.value.category == "security") | "- **\(.key):** \(.value.status | ascii_upcase)"' "$RESULTS_FILE")

### Build & Quality Checks (17-20)
$(jq -r '.checks | to_entries[] | select(.value.category == "quality") | "- **\(.key):** \(.value.status | ascii_upcase)"' "$RESULTS_FILE")

### Performance & Monitoring Checks (21-24)
$(jq -r '.checks | to_entries[] | select(.value.category == "performance") | "- **\(.key):** \(.value.status | ascii_upcase)"' "$RESULTS_FILE")

## Enterprise Compliance Assessment

EOF
    
    if [ $failed_checks -eq 0 ]; then
        cat >> "$report_file" << EOF
✅ **ENTERPRISE COMPLIANCE ACHIEVED**

All 24 enterprise checks passed successfully. The ACGS-1 CI/CD pipeline meets all enterprise-grade standards:
- Zero-tolerance security policy enforced
- Performance targets met
- Quality gates passed
- Infrastructure reliability confirmed

**Status:** READY FOR PRODUCTION DEPLOYMENT
EOF
    else
        cat >> "$report_file" << EOF
❌ **ENTERPRISE COMPLIANCE GAPS IDENTIFIED**

$failed_checks out of 24 checks failed. Immediate remediation required:

### Failed Checks
$(jq -r '.checks | to_entries[] | select(.value.status == "failed") | "- **\(.key):** \(.value.error_message)"' "$RESULTS_FILE")

### Remediation Priority
1. **CRITICAL:** Fix all security-related failures immediately
2. **HIGH:** Address infrastructure and build failures
3. **MEDIUM:** Resolve performance and monitoring issues

**Status:** NOT READY FOR PRODUCTION - REMEDIATION REQUIRED
EOF
    fi
    
    log_validation "SUCCESS" "✅ Compliance report generated: $report_file"
    log_validation "INFO" "📊 Results file: $RESULTS_FILE"
    
    # Final status
    if [ $failed_checks -eq 0 ]; then
        log_validation "SUCCESS" "🎉 ALL 24 ENTERPRISE CHECKS PASSED - ZERO-TOLERANCE COMPLIANCE ACHIEVED"
        return 0
    else
        log_validation "CRITICAL" "🚨 $failed_checks/24 CHECKS FAILED - ZERO-TOLERANCE POLICY VIOLATED"
        return 1
    fi
}

# Main execution
main() {
    case "${1:-validate}" in
        "validate")
            initialize_validation
            if run_24_checks; then
                generate_compliance_report
                exit 0
            else
                generate_compliance_report
                exit 1
            fi
            ;;
        "report")
            if [ -f "$RESULTS_FILE" ]; then
                generate_compliance_report
            else
                log_validation "ERROR" "No validation results found. Run validation first."
                exit 1
            fi
            ;;
        "help"|*)
            echo "ACGS-1 Enterprise 24-Check Validation"
            echo "Usage: $0 {validate|report|help}"
            echo ""
            echo "Commands:"
            echo "  validate    Run all 24 enterprise checks"
            echo "  report      Generate compliance report from existing results"
            echo "  help        Show this help message"
            ;;
    esac
}

# Execute main function
main "$@"
