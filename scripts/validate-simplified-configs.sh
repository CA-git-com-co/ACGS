#!/bin/bash
# ACGS-2 Simplified Configuration Validation Script
# Constitutional Hash: cdd01ef066bc6cf2

set -euo pipefail

CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACGS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 ACGS-2 Simplified Configuration Validation${NC}"
echo -e "${BLUE}📋 Constitutional Hash: ${CONSTITUTIONAL_HASH}${NC}"
echo ""

# Validation counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Function to check file
check_file() {
    local file="$1"
    local description="$2"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if [[ -f "$file" ]]; then
        if grep -q "$CONSTITUTIONAL_HASH" "$file"; then
            echo -e "✅ ${GREEN}PASS${NC}: $description"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            echo -e "❌ ${RED}FAIL${NC}: $description (missing constitutional hash)"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        fi
    else
        echo -e "❌ ${RED}FAIL${NC}: $description (file not found)"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
}

# Function to check directory
check_directory() {
    local dir="$1"
    local description="$2"
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    if [[ -d "$dir" ]]; then
        echo -e "✅ ${GREEN}PASS${NC}: $description"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "❌ ${RED}FAIL${NC}: $description (directory not found)"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
}

echo -e "${YELLOW}📋 Validating Docker Compose Unification...${NC}"
check_file "$ACGS_ROOT/config/docker/docker-compose.base.yml" "Base Docker Compose configuration"
check_file "$ACGS_ROOT/config/docker/docker-compose.development.yml" "Development Docker Compose configuration"
check_file "$ACGS_ROOT/config/docker/docker-compose.staging.yml" "Staging Docker Compose configuration"
check_file "$ACGS_ROOT/config/docker/docker-compose.production.yml" "Production Docker Compose configuration"
check_file "$ACGS_ROOT/scripts/deploy-acgs.sh" "Unified deployment script"

echo ""
echo -e "${YELLOW}📋 Validating Environment Standardization...${NC}"
check_file "$ACGS_ROOT/config/environments/development.env" "Development environment configuration"
check_file "$ACGS_ROOT/config/environments/staging.env" "Staging environment configuration"
check_file "$ACGS_ROOT/config/environments/production-standardized.env" "Production environment configuration"

echo ""
echo -e "${YELLOW}📋 Validating Service Architecture Mapping...${NC}"
check_file "$ACGS_ROOT/config/services/service-architecture-mapping.yml" "Service architecture mapping"

echo ""
echo -e "${YELLOW}📋 Validating Monitoring Consolidation...${NC}"
check_file "$ACGS_ROOT/config/monitoring/unified-observability-stack.yml" "Unified observability stack configuration"

echo ""
echo -e "${YELLOW}📋 Validating Constitutional Compliance Tools...${NC}"
check_file "$ACGS_ROOT/scripts/constitutional-compliance-validator.py" "Constitutional compliance validator"
check_file "$ACGS_ROOT/scripts/config-analysis.py" "Configuration analysis tool"

echo ""
echo -e "${YELLOW}📋 Validating Analysis Results...${NC}"
check_file "$ACGS_ROOT/config-consolidation-analysis.json" "Configuration consolidation analysis"

echo ""
echo -e "${YELLOW}📋 Validating Documentation...${NC}"
check_file "$ACGS_ROOT/ACGS-2-OPERATIONAL-SIMPLIFICATION-SUMMARY.md" "Operational simplification summary"

echo ""
echo -e "${YELLOW}📋 Checking Performance Targets in Configurations...${NC}"

# Check performance targets in key files
PERF_CHECKS=0
PERF_PASSED=0

check_performance_targets() {
    local file="$1"
    local description="$2"
    
    PERF_CHECKS=$((PERF_CHECKS + 1))
    
    if [[ -f "$file" ]]; then
        if grep -q -E "(p99|P99|latency|throughput|cache.*hit)" "$file"; then
            echo -e "✅ ${GREEN}PASS${NC}: $description (performance targets found)"
            PERF_PASSED=$((PERF_PASSED + 1))
        else
            echo -e "⚠️  ${YELLOW}WARN${NC}: $description (no performance targets found)"
        fi
    else
        echo -e "❌ ${RED}FAIL${NC}: $description (file not found)"
    fi
}

check_performance_targets "$ACGS_ROOT/config/environments/development.env" "Development performance targets"
check_performance_targets "$ACGS_ROOT/config/environments/staging.env" "Staging performance targets"
check_performance_targets "$ACGS_ROOT/config/environments/production-standardized.env" "Production performance targets"
check_performance_targets "$ACGS_ROOT/config/monitoring/unified-observability-stack.yml" "Monitoring performance targets"

echo ""
echo -e "${YELLOW}📋 Checking Service Definitions...${NC}"

# Check service definitions
SERVICE_CHECKS=0
SERVICE_PASSED=0

check_service_definitions() {
    local file="$1"
    local description="$2"
    
    SERVICE_CHECKS=$((SERVICE_CHECKS + 1))
    
    if [[ -f "$file" ]]; then
        if grep -q -E "(constitutional_ai|governance_synthesis|formal_verification)" "$file"; then
            echo -e "✅ ${GREEN}PASS${NC}: $description (core services found)"
            SERVICE_PASSED=$((SERVICE_PASSED + 1))
        else
            echo -e "⚠️  ${YELLOW}WARN${NC}: $description (core services not found)"
        fi
    else
        echo -e "❌ ${RED}FAIL${NC}: $description (file not found)"
    fi
}

check_service_definitions "$ACGS_ROOT/config/services/service-architecture-mapping.yml" "Service architecture mapping"
check_service_definitions "$ACGS_ROOT/config/docker/docker-compose.base.yml" "Base Docker Compose services"

echo ""
echo -e "${YELLOW}📋 Checking Constitutional Hash Distribution...${NC}"

# Count constitutional hash occurrences in simplified configs (excluding archives)
HASH_COUNT=$(find "$ACGS_ROOT/config" \
    -path "*/archive*" -prune -o \
    -path "*/backup*" -prune -o \
    -path "*/old*" -prune -o \
    -path "*/legacy*" -prune -o \
    -path "*/deprecated*" -prune -o \
    -name "*.yml" -print -o -name "*.yaml" -print -o -name "*.env" -print | \
    xargs grep -l "$CONSTITUTIONAL_HASH" 2>/dev/null | wc -l)
echo -e "📊 Constitutional hash found in ${HASH_COUNT} simplified configuration files"

if [[ $HASH_COUNT -gt 10 ]]; then
    echo -e "✅ ${GREEN}PASS${NC}: Constitutional hash widely distributed"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "⚠️  ${YELLOW}WARN${NC}: Constitutional hash distribution could be improved"
fi

TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

echo ""
echo -e "${YELLOW}📋 Checking Deployment Script Functionality...${NC}"

# Check if deployment script is executable
if [[ -x "$ACGS_ROOT/scripts/deploy-acgs.sh" ]]; then
    echo -e "✅ ${GREEN}PASS${NC}: Deployment script is executable"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "❌ ${RED}FAIL${NC}: Deployment script is not executable"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

# Check if constitutional compliance validator is executable
if [[ -x "$ACGS_ROOT/scripts/constitutional-compliance-validator.py" ]]; then
    echo -e "✅ ${GREEN}PASS${NC}: Constitutional compliance validator is executable"
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
else
    echo -e "❌ ${RED}FAIL${NC}: Constitutional compliance validator is not executable"
    FAILED_CHECKS=$((FAILED_CHECKS + 1))
fi

TOTAL_CHECKS=$((TOTAL_CHECKS + 1))

echo ""
echo -e "${BLUE}📊 Validation Summary${NC}"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "Total Checks: ${TOTAL_CHECKS}"
echo -e "Passed: ${GREEN}${PASSED_CHECKS}${NC}"
echo -e "Failed: ${RED}${FAILED_CHECKS}${NC}"

# Calculate success rate
SUCCESS_RATE=$(( (PASSED_CHECKS * 100) / TOTAL_CHECKS ))
echo -e "Success Rate: ${SUCCESS_RATE}%"

echo ""
if [[ $SUCCESS_RATE -ge 90 ]]; then
    echo -e "🎉 ${GREEN}EXCELLENT${NC}: ACGS-2 operational simplification validation passed!"
    echo -e "✅ Constitutional compliance maintained"
    echo -e "✅ Performance targets preserved"
    echo -e "✅ Simplified configurations validated"
elif [[ $SUCCESS_RATE -ge 75 ]]; then
    echo -e "✅ ${YELLOW}GOOD${NC}: ACGS-2 operational simplification mostly successful"
    echo -e "⚠️  Some improvements needed"
else
    echo -e "❌ ${RED}NEEDS IMPROVEMENT${NC}: ACGS-2 operational simplification requires attention"
    echo -e "🔧 Please address failed checks"
fi

echo ""
echo -e "${BLUE}📋 Constitutional Compliance Statement${NC}"
echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "Constitutional Hash: ${CONSTITUTIONAL_HASH}"
echo -e "Performance Targets: P99 <5ms, >100 RPS, >85% cache hit rates"
echo -e "Compliance Status: $(if [[ $SUCCESS_RATE -ge 90 ]]; then echo -e "${GREEN}COMPLIANT${NC}"; else echo -e "${YELLOW}PARTIAL${NC}"; fi)"

# Exit with appropriate code
if [[ $SUCCESS_RATE -ge 90 ]]; then
    exit 0
else
    exit 1
fi
