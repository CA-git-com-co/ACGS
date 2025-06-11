#!/bin/bash

# ACGS-1 FV and GS Service Restoration Validation Script
# Validates that the enhanced start_missing_services.sh script successfully restores services

set -e

echo "🔍 ACGS-1 FV and GS Service Restoration Validation"
echo "=================================================="
echo "Date: $(date)"
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Test service health with detailed response
test_service_health() {
    local service_name=$1
    local port=$2
    local endpoint=${3:-"/health"}
    
    print_status "Testing $service_name on port $port..."
    
    if curl -f -s --connect-timeout 5 --max-time 10 "http://localhost:$port$endpoint" > /dev/null 2>&1; then
        print_success "$service_name is responding on port $port"
        
        # Get detailed health information
        local health_response=$(curl -s "http://localhost:$port$endpoint" 2>/dev/null || echo '{"error": "no_response"}')
        echo "   Response: $health_response" | head -c 200
        echo ""
        return 0
    else
        print_error "$service_name is not responding on port $port"
        return 1
    fi
}

# Test constitutional compliance workflows
test_constitutional_workflows() {
    print_status "Testing constitutional compliance workflows..."
    
    # Test FV enterprise status
    print_status "Testing FV enterprise verification capabilities..."
    if curl -f -s "http://localhost:8003/api/v1/enterprise/status" > /dev/null 2>&1; then
        print_success "FV enterprise verification endpoints are accessible"
    else
        print_warning "FV enterprise verification endpoints may not be fully operational"
    fi
    
    # Test GS synthesis capabilities
    print_status "Testing GS synthesis capabilities..."
    if curl -f -s "http://localhost:8004/api/v1/status" > /dev/null 2>&1; then
        print_success "GS synthesis endpoints are accessible"
    else
        print_warning "GS synthesis endpoints may not be fully operational"
    fi
}

# Check service logs for errors
check_service_logs() {
    local log_dir="/home/dislove/ACGS-1/logs"
    
    print_status "Checking service logs for errors..."
    
    # Check FV service log
    if [ -f "$log_dir/fv_service.log" ]; then
        local fv_errors=$(grep -i "error\|exception\|failed" "$log_dir/fv_service.log" | tail -5 || echo "")
        if [ -n "$fv_errors" ]; then
            print_warning "Recent FV service errors found:"
            echo "$fv_errors"
        else
            print_success "No recent errors in FV service log"
        fi
    else
        print_warning "FV service log not found at $log_dir/fv_service.log"
    fi
    
    # Check GS service log
    if [ -f "$log_dir/gs_service.log" ]; then
        local gs_errors=$(grep -i "error\|exception\|failed" "$log_dir/gs_service.log" | tail -5 || echo "")
        if [ -n "$gs_errors" ]; then
            print_warning "Recent GS service errors found:"
            echo "$gs_errors"
        else
            print_success "No recent errors in GS service log"
        fi
    else
        print_warning "GS service log not found at $log_dir/gs_service.log"
    fi
}

# Check PID files
check_pid_files() {
    local pid_dir="/home/dislove/ACGS-1/pids"
    
    print_status "Checking PID files..."
    
    # Check FV service PID
    if [ -f "$pid_dir/fv_service.pid" ]; then
        local fv_pid=$(cat "$pid_dir/fv_service.pid")
        if kill -0 "$fv_pid" 2>/dev/null; then
            print_success "FV service is running with PID: $fv_pid"
        else
            print_warning "FV service PID file exists but process is not running"
        fi
    else
        print_warning "FV service PID file not found"
    fi
    
    # Check GS service PID
    if [ -f "$pid_dir/gs_service.pid" ]; then
        local gs_pid=$(cat "$pid_dir/gs_service.pid")
        if kill -0 "$gs_pid" 2>/dev/null; then
            print_success "GS service is running with PID: $gs_pid"
        else
            print_warning "GS service PID file exists but process is not running"
        fi
    else
        print_warning "GS service PID file not found"
    fi
}

# Main validation function
main() {
    print_status "Step 1: Basic Service Health Checks"
    local fv_healthy=false
    local gs_healthy=false
    
    if test_service_health "FV Service" "8003"; then
        fv_healthy=true
    fi
    
    if test_service_health "GS Service" "8004"; then
        gs_healthy=true
    fi
    
    echo ""
    print_status "Step 2: Constitutional Compliance Workflow Testing"
    test_constitutional_workflows
    
    echo ""
    print_status "Step 3: Service Log Analysis"
    check_service_logs
    
    echo ""
    print_status "Step 4: PID File Validation"
    check_pid_files
    
    echo ""
    print_status "Step 5: Validation Summary"
    echo "=========================="
    
    if [ "$fv_healthy" = true ] && [ "$gs_healthy" = true ]; then
        print_success "🎯 VALIDATION PASSED: Both FV and GS services are operational"
        print_success "🏛️ Constitutional governance workflows are ready for use"
        echo ""
        echo "✅ Next Steps:"
        echo "   - Services are ready for constitutional compliance validation"
        echo "   - Policy synthesis workflows can be tested"
        echo "   - Formal verification capabilities are available"
        return 0
    elif [ "$fv_healthy" = true ] || [ "$gs_healthy" = true ]; then
        print_warning "⚠️ PARTIAL VALIDATION: Some services are operational"
        echo ""
        echo "🔧 Recommended Actions:"
        echo "   - Check logs for failed service"
        echo "   - Retry service restoration"
        echo "   - Verify service dependencies"
        return 1
    else
        print_error "❌ VALIDATION FAILED: Critical services are not operational"
        echo ""
        echo "🚨 Required Actions:"
        echo "   - Run enhanced start_missing_services.sh script"
        echo "   - Check system dependencies (PostgreSQL, Redis)"
        echo "   - Review service logs for detailed error information"
        return 1
    fi
}

# Execute main function
main "$@"
