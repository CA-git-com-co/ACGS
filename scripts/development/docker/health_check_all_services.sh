# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# ACGS-1 Comprehensive Health Check for Containerized Services
# Validates all 7 services with <500ms response time requirements

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Performance targets
MAX_RESPONSE_TIME_MS=500
HEALTH_CHECK_TIMEOUT=10

# Service configuration
declare -A SERVICES=(
    ["auth_service"]="8000"
    ["ac_service"]="8001"
    ["integrity_service"]="8002"
    ["fv_service"]="8003"
    ["gs_service"]="8004"
    ["pgc_service"]="8005"
    ["ec_service"]="8006"
)

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

# Function to check service health with response time measurement
check_service_health() {
    local service_name=$1
    local port=$2
    local container_name="acgs_${service_name}"
    
    print_status "Checking $service_name (container: $container_name, port: $port)..."
    
    # Check if container is running
    if ! docker ps --format "table {{.Names}}" | grep -q "^${container_name}$"; then
        print_error "$service_name container is not running"
        return 1
    fi
    
    # Measure response time
    local start_time=$(date +%s%3N)
    local health_response
    
    if health_response=$(curl -f -s --connect-timeout $HEALTH_CHECK_TIMEOUT --max-time $HEALTH_CHECK_TIMEOUT "http://localhost:$port/health" 2>/dev/null); then
        local end_time=$(date +%s%3N)
        local response_time=$((end_time - start_time))
        
        if [ $response_time -le $MAX_RESPONSE_TIME_MS ]; then
            print_success "$service_name: HEALTHY (${response_time}ms) ✅"
            return 0
        else
            print_warning "$service_name: SLOW RESPONSE (${response_time}ms > ${MAX_RESPONSE_TIME_MS}ms) ⚠️"
            return 1
        fi
    else
        print_error "$service_name: UNHEALTHY (no response) ❌"
        return 1
    fi
}

# Function to check container resource usage
check_container_resources() {
    local service_name=$1
    local container_name="acgs_${service_name}"
    
    if docker ps --format "table {{.Names}}" | grep -q "^${container_name}$"; then
        local stats=$(docker stats --no-stream --format "table {{.CPUPerc}}\t{{.MemUsage}}" "$container_name" 2>/dev/null | tail -n 1)
        if [ -n "$stats" ]; then
            print_status "$service_name resources: $stats"
        fi
    fi
}

# Function to check infrastructure services
check_infrastructure() {
    print_status "Checking infrastructure services..."
    
    # PostgreSQL
    if docker ps --format "table {{.Names}}" | grep -q "^acgs_postgres$"; then
        if docker exec acgs_postgres pg_isready -U acgs_user -d acgs_db > /dev/null 2>&1; then
            print_success "PostgreSQL: HEALTHY ✅"
        else
            print_error "PostgreSQL: UNHEALTHY ❌"
            return 1
        fi
    else
        print_error "PostgreSQL container not running ❌"
        return 1
    fi
    
    # Redis
    if docker ps --format "table {{.Names}}" | grep -q "^acgs_redis$"; then
        if docker exec acgs_redis redis-cli ping > /dev/null 2>&1; then
            print_success "Redis: HEALTHY ✅"
        else
            print_error "Redis: UNHEALTHY ❌"
            return 1
        fi
    else
        print_error "Redis container not running ❌"
        return 1
    fi
    
    # HAProxy
    if docker ps --format "table {{.Names}}" | grep -q "^acgs_haproxy$"; then
        if curl -f -s --connect-timeout 5 "http://localhost:8080/stats" > /dev/null 2>&1; then
            print_success "HAProxy: HEALTHY ✅"
        else
            print_warning "HAProxy: Stats interface not accessible ⚠️"
        fi
    else
        print_warning "HAProxy container not running ⚠️"
    fi
}

# Function to test constitutional governance workflows
test_governance_workflows() {
    print_status "Testing constitutional governance workflows..."
    
    # Test AC service constitutional validation
    if curl -f -s --connect-timeout 5 "http://localhost:8001/api/v1/constitutional/rules" > /dev/null 2>&1; then
        print_success "Constitutional rules endpoint: ACCESSIBLE ✅"
    else
        print_warning "Constitutional rules endpoint: NOT ACCESSIBLE ⚠️"
    fi
    
    # Test PGC service compliance checking
    if curl -f -s --connect-timeout 5 "http://localhost:8005/api/v1/status" > /dev/null 2>&1; then
        print_success "PGC compliance endpoint: ACCESSIBLE ✅"
    else
        print_warning "PGC compliance endpoint: NOT ACCESSIBLE ⚠️"
    fi
}

# Main execution
main() {
    echo "🏛️ ACGS-1 Containerized Health Check"
    echo "===================================="
    echo "Date: $(date)"
    echo "Performance Target: <${MAX_RESPONSE_TIME_MS}ms response time"
    echo ""
    
    local healthy_services=0
    local total_services=${#SERVICES[@]}
    
    # Check infrastructure first
    print_status "Step 1: Infrastructure Health Check"
    if check_infrastructure; then
        print_success "Infrastructure services are healthy"
    else
        print_error "Infrastructure issues detected"
    fi
    echo ""
    
    # Check all ACGS services
    print_status "Step 2: ACGS Services Health Check"
    for service_name in "${!SERVICES[@]}"; do
        local port=${SERVICES[$service_name]}
        if check_service_health "$service_name" "$port"; then
            healthy_services=$((healthy_services + 1))
        fi
        check_container_resources "$service_name"
        echo ""
    done
    
    # Test governance workflows
    print_status "Step 3: Constitutional Governance Workflow Test"
    test_governance_workflows
    echo ""
    
    # Summary
    echo "📊 HEALTH CHECK SUMMARY"
    echo "======================"
    echo "✅ Healthy services: $healthy_services/$total_services"
    echo "🎯 Performance target: <${MAX_RESPONSE_TIME_MS}ms"
    echo "🏛️ Constitutional governance: $([ $healthy_services -ge 5 ] && echo "OPERATIONAL" || echo "DEGRADED")"
    echo ""
    
    if [ $healthy_services -eq $total_services ]; then
        print_success "🎉 ALL SERVICES HEALTHY - ACGS-1 is fully operational!"
        echo "🔗 Access services:"
        echo "   - Auth Service: http://localhost:8000"
        echo "   - Constitutional AI: http://localhost:8001"
        echo "   - Integrity Service: http://localhost:8002"
        echo "   - Formal Verification: http://localhost:8003"
        echo "   - Governance Synthesis: http://localhost:8004"
        echo "   - Policy Compliance: http://localhost:8005"
        echo "   - Evolutionary Computation: http://localhost:8006"
        echo "   - HAProxy Stats: http://localhost:8080/stats"
        echo "   - Prometheus: http://localhost:9090"
        echo "   - Grafana: http://localhost:3001"
        return 0
    elif [ $healthy_services -ge 5 ]; then
        print_warning "⚠️ PARTIAL OPERATION - Some services need attention"
        return 1
    else
        print_error "❌ SYSTEM DEGRADED - Multiple service failures detected"
        return 1
    fi
}

# Execute main function
main "$@"
