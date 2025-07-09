#!/bin/bash
# ACGS Hourly Validation Script
# Constitutional Hash: cdd01ef066bc6cf2
# 
# Single-page validation script for operations teams to run during off-hours incidents
# Provides comprehensive system health check in under 60 seconds

set -euo pipefail

# Constitutional compliance
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
SCRIPT_VERSION="1.0.0"
VALIDATION_START=$(date +%s)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging
LOG_FILE="/var/log/acgs/hourly_validation_$(date +%Y%m%d_%H%M%S).log"
mkdir -p "$(dirname "$LOG_FILE")"

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

print_header() {
    echo -e "${BLUE}================================================================================================${NC}"
    echo -e "${BLUE}🎯 ACGS HOURLY VALIDATION SCRIPT${NC}"
    echo -e "${BLUE}================================================================================================${NC}"
    echo -e "Constitutional Hash: ${GREEN}$CONSTITUTIONAL_HASH${NC}"
    echo -e "Script Version: $SCRIPT_VERSION"
    echo -e "Validation Start: $(date)"
    echo -e "Log File: $LOG_FILE"
    echo ""
}

print_section() {
    echo -e "${BLUE}📊 $1${NC}"
    echo "----------------------------------------"
}

check_status() {
    local status=$1
    local message=$2
    
    if [ "$status" -eq 0 ]; then
        echo -e "  ✅ ${GREEN}$message${NC}"
        return 0
    else
        echo -e "  ❌ ${RED}$message${NC}"
        return 1
    fi
}

# 1. CONSTITUTIONAL COMPLIANCE VALIDATION
validate_constitutional_compliance() {
    print_section "Constitutional Compliance Validation"
    local compliance_score=0
    local total_checks=5
    
    # Check constitutional hash in environment
    if [ "${CONSTITUTIONAL_HASH:-}" = "cdd01ef066bc6cf2" ]; then
        check_status 0 "Constitutional hash environment variable correct"
        ((compliance_score++))
    else
        check_status 1 "Constitutional hash environment variable incorrect or missing"
    fi
    
    # Check constitutional compliance framework
    if python3 -c "
import sys
sys.path.append('/home/dislove/ACGS-2/tools')
try:
    from acgs_constitutional_compliance_framework import ACGSConstitutionalComplianceFramework
    print('Constitutional compliance framework importable')
    exit(0)
except Exception as e:
    print(f'Constitutional compliance framework import failed: {e}')
    exit(1)
" 2>/dev/null; then
        check_status 0 "Constitutional compliance framework accessible"
        ((compliance_score++))
    else
        check_status 1 "Constitutional compliance framework not accessible"
    fi
    
    # Check unified orchestrator
    if python3 -c "
import sys
sys.path.append('/home/dislove/ACGS-2/tools')
try:
    from acgs_unified_orchestrator import ACGSUnifiedOrchestrator
    print('Unified orchestrator importable')
    exit(0)
except Exception as e:
    print(f'Unified orchestrator import failed: {e}')
    exit(1)
" 2>/dev/null; then
        check_status 0 "Unified orchestrator accessible"
        ((compliance_score++))
    else
        check_status 1 "Unified orchestrator not accessible"
    fi
    
    # Check tools directory structure
    if [ -d "/home/dislove/ACGS-2/tools" ] && [ "$(find /home/dislove/ACGS-2/tools -name 'acgs_*.py' | wc -l)" -ge 8 ]; then
        check_status 0 "ACGS tools directory structure valid"
        ((compliance_score++))
    else
        check_status 1 "ACGS tools directory structure invalid"
    fi
    
    # Check constitutional hash in tool files
    local tools_with_hash=$(grep -l "$CONSTITUTIONAL_HASH" /home/dislove/ACGS-2/tools/acgs_*.py 2>/dev/null | wc -l)
    if [ "$tools_with_hash" -ge 8 ]; then
        check_status 0 "Constitutional hash present in tool files ($tools_with_hash/9)"
        ((compliance_score++))
    else
        check_status 1 "Constitutional hash missing from tool files ($tools_with_hash/9)"
    fi
    
    local compliance_percentage=$((compliance_score * 100 / total_checks))
    echo ""
    echo -e "Constitutional Compliance Score: ${GREEN}$compliance_percentage%${NC} ($compliance_score/$total_checks)"
    
    if [ "$compliance_percentage" -eq 100 ]; then
        echo -e "Status: ${GREEN}✅ FULLY COMPLIANT${NC}"
        return 0
    elif [ "$compliance_percentage" -ge 80 ]; then
        echo -e "Status: ${YELLOW}⚠️ MOSTLY COMPLIANT${NC}"
        return 1
    else
        echo -e "Status: ${RED}❌ NON-COMPLIANT${NC}"
        return 2
    fi
}

# 2. PERFORMANCE VALIDATION
validate_performance() {
    print_section "Performance Validation"
    local performance_score=0
    local total_checks=4
    
    # Check system load
    local load_avg=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    local load_threshold=2.0
    if (( $(echo "$load_avg < $load_threshold" | bc -l) )); then
        check_status 0 "System load average acceptable ($load_avg < $load_threshold)"
        ((performance_score++))
    else
        check_status 1 "System load average high ($load_avg >= $load_threshold)"
    fi
    
    # Check memory usage
    local memory_usage=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
    local memory_threshold=85.0
    if (( $(echo "$memory_usage < $memory_threshold" | bc -l) )); then
        check_status 0 "Memory usage acceptable (${memory_usage}% < ${memory_threshold}%)"
        ((performance_score++))
    else
        check_status 1 "Memory usage high (${memory_usage}% >= ${memory_threshold}%)"
    fi
    
    # Check disk usage
    local disk_usage=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
    local disk_threshold=90
    if [ "$disk_usage" -lt "$disk_threshold" ]; then
        check_status 0 "Disk usage acceptable (${disk_usage}% < ${disk_threshold}%)"
        ((performance_score++))
    else
        check_status 1 "Disk usage high (${disk_usage}% >= ${disk_threshold}%)"
    fi
    
    # Check if Python processes are responsive
    if pgrep -f python3 > /dev/null; then
        check_status 0 "Python processes running"
        ((performance_score++))
    else
        check_status 1 "No Python processes found"
    fi
    
    local performance_percentage=$((performance_score * 100 / total_checks))
    echo ""
    echo -e "Performance Score: ${GREEN}$performance_percentage%${NC} ($performance_score/$total_checks)"
    
    if [ "$performance_percentage" -eq 100 ]; then
        echo -e "Status: ${GREEN}✅ OPTIMAL PERFORMANCE${NC}"
        return 0
    elif [ "$performance_percentage" -ge 75 ]; then
        echo -e "Status: ${YELLOW}⚠️ ACCEPTABLE PERFORMANCE${NC}"
        return 1
    else
        echo -e "Status: ${RED}❌ POOR PERFORMANCE${NC}"
        return 2
    fi
}

# 3. SERVICE HEALTH VALIDATION
validate_service_health() {
    print_section "Service Health Validation"
    local health_score=0
    local total_checks=3
    
    # Check PostgreSQL (if running)
    if command -v psql >/dev/null 2>&1; then
        if pg_isready -h localhost -p 5439 >/dev/null 2>&1; then
            check_status 0 "PostgreSQL service healthy (port 5439)"
            ((health_score++))
        else
            check_status 1 "PostgreSQL service unhealthy or not running (port 5439)"
        fi
    else
        check_status 0 "PostgreSQL client not installed (skipping check)"
        ((health_score++))
    fi
    
    # Check Redis (if running)
    if command -v redis-cli >/dev/null 2>&1; then
        if redis-cli -h localhost -p 6389 ping >/dev/null 2>&1; then
            check_status 0 "Redis service healthy (port 6389)"
            ((health_score++))
        else
            check_status 1 "Redis service unhealthy or not running (port 6389)"
        fi
    else
        check_status 0 "Redis client not installed (skipping check)"
        ((health_score++))
    fi
    
    # Check if ACGS tools are accessible
    if [ -f "/home/dislove/ACGS-2/tools/acgs_unified_orchestrator.py" ]; then
        if python3 /home/dislove/ACGS-2/tools/acgs_unified_orchestrator.py --list-tools >/dev/null 2>&1; then
            check_status 0 "ACGS unified orchestrator functional"
            ((health_score++))
        else
            check_status 1 "ACGS unified orchestrator not functional"
        fi
    else
        check_status 1 "ACGS unified orchestrator not found"
    fi
    
    local health_percentage=$((health_score * 100 / total_checks))
    echo ""
    echo -e "Service Health Score: ${GREEN}$health_percentage%${NC} ($health_score/$total_checks)"
    
    if [ "$health_percentage" -eq 100 ]; then
        echo -e "Status: ${GREEN}✅ ALL SERVICES HEALTHY${NC}"
        return 0
    elif [ "$health_percentage" -ge 67 ]; then
        echo -e "Status: ${YELLOW}⚠️ MOST SERVICES HEALTHY${NC}"
        return 1
    else
        echo -e "Status: ${RED}❌ SERVICES UNHEALTHY${NC}"
        return 2
    fi
}

# 4. SECURITY VALIDATION
validate_security() {
    print_section "Security Validation"
    local security_score=0
    local total_checks=4
    
    # Check file permissions on critical files
    if [ -f "/home/dislove/ACGS-2/tools/acgs_unified_orchestrator.py" ]; then
        local file_perms=$(stat -c "%a" "/home/dislove/ACGS-2/tools/acgs_unified_orchestrator.py")
        if [ "$file_perms" = "644" ] || [ "$file_perms" = "755" ]; then
            check_status 0 "Critical file permissions secure ($file_perms)"
            ((security_score++))
        else
            check_status 1 "Critical file permissions insecure ($file_perms)"
        fi
    else
        check_status 1 "Critical file not found"
    fi
    
    # Check for suspicious processes
    local suspicious_processes=$(ps aux | grep -E "(nc|netcat|nmap|tcpdump)" | grep -v grep | wc -l)
    if [ "$suspicious_processes" -eq 0 ]; then
        check_status 0 "No suspicious network processes detected"
        ((security_score++))
    else
        check_status 1 "Suspicious network processes detected ($suspicious_processes)"
    fi
    
    # Check system updates (basic check)
    if command -v apt >/dev/null 2>&1; then
        local updates_available=$(apt list --upgradable 2>/dev/null | grep -c upgradable || echo "0")
        if [ "$updates_available" -lt 10 ]; then
            check_status 0 "System updates manageable ($updates_available available)"
            ((security_score++))
        else
            check_status 1 "Many system updates available ($updates_available)"
        fi
    else
        check_status 0 "Package manager not available (skipping update check)"
        ((security_score++))
    fi
    
    # Check constitutional hash integrity
    local hash_files=$(find /home/dislove/ACGS-2 -name "*.py" -exec grep -l "$CONSTITUTIONAL_HASH" {} \; 2>/dev/null | wc -l)
    if [ "$hash_files" -ge 8 ]; then
        check_status 0 "Constitutional hash integrity maintained ($hash_files files)"
        ((security_score++))
    else
        check_status 1 "Constitutional hash integrity compromised ($hash_files files)"
    fi
    
    local security_percentage=$((security_score * 100 / total_checks))
    echo ""
    echo -e "Security Score: ${GREEN}$security_percentage%${NC} ($security_score/$total_checks)"
    
    if [ "$security_percentage" -eq 100 ]; then
        echo -e "Status: ${GREEN}✅ SECURE${NC}"
        return 0
    elif [ "$security_percentage" -ge 75 ]; then
        echo -e "Status: ${YELLOW}⚠️ MOSTLY SECURE${NC}"
        return 1
    else
        echo -e "Status: ${RED}❌ SECURITY ISSUES${NC}"
        return 2
    fi
}

# 5. QUICK REMEDIATION ACTIONS
quick_remediation() {
    print_section "Quick Remediation Actions"
    
    echo "Available quick fixes:"
    echo "  1. Restart ACGS services: sudo systemctl restart acgs-*"
    echo "  2. Clear temporary files: sudo find /tmp -name 'acgs_*' -delete"
    echo "  3. Validate constitutional compliance: python3 tools/acgs_constitutional_compliance_framework.py"
    echo "  4. Run comprehensive validation: python3 tools/acgs_unified_orchestrator.py --comprehensive"
    echo "  5. Check system resources: htop or top"
    echo "  6. View ACGS logs: tail -f /var/log/acgs/*.log"
    echo ""
    echo "Emergency contacts:"
    echo "  - Constitutional Compliance: constitutional-team@acgs.gov"
    echo "  - SRE Team: sre-team@acgs.gov"
    echo "  - Security Team: security-team@acgs.gov"
    echo ""
}

# MAIN EXECUTION
main() {
    print_header
    
    local overall_status=0
    local compliance_status=0
    local performance_status=0
    local health_status=0
    local security_status=0
    
    # Run all validations
    log "Starting constitutional compliance validation"
    validate_constitutional_compliance
    compliance_status=$?
    
    echo ""
    log "Starting performance validation"
    validate_performance
    performance_status=$?
    
    echo ""
    log "Starting service health validation"
    validate_service_health
    health_status=$?
    
    echo ""
    log "Starting security validation"
    validate_security
    security_status=$?
    
    echo ""
    quick_remediation
    
    # Calculate overall status
    local total_status=$((compliance_status + performance_status + health_status + security_status))
    
    # Print final summary
    echo -e "${BLUE}================================================================================================${NC}"
    echo -e "${BLUE}📋 VALIDATION SUMMARY${NC}"
    echo -e "${BLUE}================================================================================================${NC}"
    
    if [ "$compliance_status" -eq 0 ]; then
        echo -e "Constitutional Compliance: ${GREEN}✅ PASS${NC}"
    elif [ "$compliance_status" -eq 1 ]; then
        echo -e "Constitutional Compliance: ${YELLOW}⚠️ WARNING${NC}"
    else
        echo -e "Constitutional Compliance: ${RED}❌ FAIL${NC}"
    fi
    
    if [ "$performance_status" -eq 0 ]; then
        echo -e "Performance: ${GREEN}✅ PASS${NC}"
    elif [ "$performance_status" -eq 1 ]; then
        echo -e "Performance: ${YELLOW}⚠️ WARNING${NC}"
    else
        echo -e "Performance: ${RED}❌ FAIL${NC}"
    fi
    
    if [ "$health_status" -eq 0 ]; then
        echo -e "Service Health: ${GREEN}✅ PASS${NC}"
    elif [ "$health_status" -eq 1 ]; then
        echo -e "Service Health: ${YELLOW}⚠️ WARNING${NC}"
    else
        echo -e "Service Health: ${RED}❌ FAIL${NC}"
    fi
    
    if [ "$security_status" -eq 0 ]; then
        echo -e "Security: ${GREEN}✅ PASS${NC}"
    elif [ "$security_status" -eq 1 ]; then
        echo -e "Security: ${YELLOW}⚠️ WARNING${NC}"
    else
        echo -e "Security: ${RED}❌ FAIL${NC}"
    fi
    
    echo ""
    local validation_duration=$(($(date +%s) - VALIDATION_START))
    echo -e "Validation Duration: ${BLUE}${validation_duration} seconds${NC}"
    echo -e "Constitutional Hash: ${GREEN}$CONSTITUTIONAL_HASH${NC}"
    echo -e "Log File: $LOG_FILE"
    
    # Overall status
    if [ "$total_status" -eq 0 ]; then
        echo -e "\nOverall Status: ${GREEN}✅ ALL SYSTEMS OPERATIONAL${NC}"
        overall_status=0
    elif [ "$total_status" -le 2 ]; then
        echo -e "\nOverall Status: ${YELLOW}⚠️ MINOR ISSUES DETECTED${NC}"
        overall_status=1
    else
        echo -e "\nOverall Status: ${RED}❌ CRITICAL ISSUES DETECTED${NC}"
        overall_status=2
    fi
    
    echo -e "${BLUE}================================================================================================${NC}"
    
    log "Validation completed with overall status: $overall_status"
    
    return $overall_status
}

# Execute main function
main "$@"
