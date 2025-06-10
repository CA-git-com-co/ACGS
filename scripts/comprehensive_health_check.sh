#!/bin/bash
# ACGS-1 Comprehensive Health Check Script
# Validates all services and blockchain components

set -e

echo "🏥 ACGS-1 System Health Check"
echo "============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Health check results
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0

# Function to check service health
check_service() {
    local service_name=$1
    local port=$2
    local endpoint=${3:-"/health"}
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "Checking $service_name (port $port)... "
    
    if curl -s -f "http://localhost:$port$endpoint" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ HEALTHY${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}❌ UNHEALTHY${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
}

# Function to check response time
check_response_time() {
    local service_name=$1
    local port=$2
    local endpoint=${3:-"/health"}
    local max_time=${4:-2}
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "Checking $service_name response time... "
    
    response_time=$(curl -s -w "%{time_total}" -o /dev/null "http://localhost:$port$endpoint" 2>/dev/null || echo "999")
    
    if (( $(echo "$response_time < $max_time" | bc -l) )); then
        echo -e "${GREEN}✅ ${response_time}s (< ${max_time}s)${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}❌ ${response_time}s (> ${max_time}s)${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
}

# Function to check Solana connection
check_solana() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    echo -n "Checking Solana devnet connection... "
    
    if solana cluster-version --url devnet > /dev/null 2>&1; then
        echo -e "${GREEN}✅ CONNECTED${NC}"
        PASSED_CHECKS=$((PASSED_CHECKS + 1))
    else
        echo -e "${RED}❌ DISCONNECTED${NC}"
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
    fi
}

# Function to check Quantumagi programs
check_quantumagi_programs() {
    local programs=(
        "8eRUCnQsDxqK7vjp5XsYs7C3NGpdhzzaMW8QQGzfTUV4:Quantumagi Core"
        "CXKCLqyzxqyqTbEgpNbYR5qkC691BdiKMAB1nk6BMoFJ:Appeals Program"
    )
    
    for program_info in "${programs[@]}"; do
        IFS=':' read -r program_id program_name <<< "$program_info"
        
        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
        
        echo -n "Checking $program_name... "
        
        if solana account "$program_id" --url devnet > /dev/null 2>&1; then
            echo -e "${GREEN}✅ DEPLOYED${NC}"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
        else
            echo -e "${RED}❌ NOT FOUND${NC}"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
        fi
    done
}

echo "🔍 Checking Core Services..."
echo "----------------------------"

# Check all ACGS-1 services
check_service "Authentication" 8000
check_service "Constitutional AI" 8001
check_service "Governance Synthesis" 8002
check_service "Policy Governance" 8003
check_service "Formal Verification" 8004
check_service "Integrity" 8005
check_service "Evolutionary Computation" 8006

echo ""
echo "⏱️  Checking Response Times..."
echo "------------------------------"

# Check response times (target <2s)
check_response_time "Authentication" 8000 "/health" 2
check_response_time "Constitutional AI" 8001 "/health" 2
check_response_time "Governance Synthesis" 8002 "/health" 2
check_response_time "Policy Governance" 8003 "/health" 2
check_response_time "Formal Verification" 8004 "/health" 2
check_response_time "Integrity" 8005 "/health" 2

echo ""
echo "🔗 Checking Blockchain Components..."
echo "------------------------------------"

# Check Solana connection
check_solana

# Check Quantumagi programs
check_quantumagi_programs

echo ""
echo "📊 Health Check Summary"
echo "======================"
echo "Total Checks: $TOTAL_CHECKS"
echo -e "Passed: ${GREEN}$PASSED_CHECKS${NC}"
echo -e "Failed: ${RED}$FAILED_CHECKS${NC}"

# Calculate success rate
success_rate=$(echo "scale=1; $PASSED_CHECKS * 100 / $TOTAL_CHECKS" | bc)
echo "Success Rate: $success_rate%"

# Determine overall health
if [ "$FAILED_CHECKS" -eq 0 ]; then
    echo -e "\n${GREEN}🎉 System Status: HEALTHY${NC}"
    exit 0
elif [ "$success_rate" -ge 90 ]; then
    echo -e "\n${YELLOW}⚠️  System Status: DEGRADED${NC}"
    exit 1
else
    echo -e "\n${RED}🚨 System Status: CRITICAL${NC}"
    exit 2
fi
