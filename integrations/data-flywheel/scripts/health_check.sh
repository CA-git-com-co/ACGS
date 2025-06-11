#!/bin/bash

# ACGS-1 Data Flywheel Health Check Script
# Comprehensive health check for the integrated system

set -e

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

# Health check function
check_service() {
    local service_name=$1
    local url=$2
    local timeout=${3:-5}
    
    if curl -f -s --connect-timeout $timeout --max-time $timeout "$url" > /dev/null 2>&1; then
        print_success "$service_name is healthy"
        return 0
    else
        print_error "$service_name is not responding"
        return 1
    fi
}

# Detailed health check function
check_service_detailed() {
    local service_name=$1
    local url=$2
    local timeout=${3:-5}
    
    print_status "Checking $service_name..."
    
    local response=$(curl -f -s --connect-timeout $timeout --max-time $timeout "$url" 2>/dev/null || echo "ERROR")
    
    if [ "$response" != "ERROR" ]; then
        print_success "$service_name is healthy"
        echo "   Response: $(echo "$response" | head -c 100)..."
        return 0
    else
        print_error "$service_name is not responding"
        return 1
    fi
}

echo "🏥 ACGS-1 Data Flywheel Health Check"
echo "===================================="
echo "Timestamp: $(date)"
echo ""

# Check ACGS-1 Core Services
print_status "Checking ACGS-1 Core Services..."
acgs_healthy=0
acgs_total=7

acgs_services=(
    "Auth Service:http://localhost:8000/health"
    "AC Service:http://localhost:8001/health"
    "Integrity Service:http://localhost:8002/health"
    "FV Service:http://localhost:8003/health"
    "GS Service:http://localhost:8004/health"
    "PGC Service:http://localhost:8005/health"
    "EC Service:http://localhost:8006/health"
)

for service_info in "${acgs_services[@]}"; do
    IFS=':' read -r name url <<< "$service_info"
    if check_service "$name" "$url"; then
        acgs_healthy=$((acgs_healthy + 1))
    fi
done

echo ""
print_status "ACGS-1 Services Health: $acgs_healthy/$acgs_total healthy"

# Check Data Flywheel Services
print_status "Checking Data Flywheel Services..."
flywheel_healthy=0
flywheel_total=4

flywheel_services=(
    "Data Flywheel API:http://localhost:8010/health"
    "Constitutional Health:http://localhost:8010/constitutional/health"
    "Governance Workloads:http://localhost:8010/constitutional/workloads"
    "Prometheus Metrics:http://localhost:9090/-/healthy"
)

for service_info in "${flywheel_services[@]}"; do
    IFS=':' read -r name url <<< "$service_info"
    if check_service "$name" "$url"; then
        flywheel_healthy=$((flywheel_healthy + 1))
    fi
done

echo ""
print_status "Data Flywheel Services Health: $flywheel_healthy/$flywheel_total healthy"

# Check Infrastructure Services
print_status "Checking Infrastructure Services..."
infra_healthy=0
infra_total=3

infra_services=(
    "Elasticsearch:http://localhost:9200/_cluster/health"
    "MongoDB:http://localhost:27017"
    "Redis:http://localhost:6379"
)

# Special handling for MongoDB and Redis
if curl -f -s --connect-timeout 5 "http://localhost:9200/_cluster/health" > /dev/null 2>&1; then
    print_success "Elasticsearch is healthy"
    infra_healthy=$((infra_healthy + 1))
else
    print_error "Elasticsearch is not responding"
fi

# MongoDB check (different approach)
if echo 'db.runCommand("ping").ok' | mongosh localhost:27017/test --quiet > /dev/null 2>&1; then
    print_success "MongoDB is healthy"
    infra_healthy=$((infra_healthy + 1))
else
    print_error "MongoDB is not responding"
fi

# Redis check
if redis-cli ping > /dev/null 2>&1; then
    print_success "Redis is healthy"
    infra_healthy=$((infra_healthy + 1))
else
    print_error "Redis is not responding"
fi

echo ""
print_status "Infrastructure Services Health: $infra_healthy/$infra_total healthy"

# Detailed Constitutional Governance Check
print_status "Detailed Constitutional Governance Check..."

if curl -f -s "http://localhost:8010/constitutional/health" > /dev/null 2>&1; then
    constitutional_response=$(curl -s "http://localhost:8010/constitutional/health" 2>/dev/null)
    
    print_success "Constitutional governance integration is operational"
    echo "   Overall Status: $(echo "$constitutional_response" | jq -r '.overall_status' 2>/dev/null || echo "unknown")"
    echo "   Validation Available: $(echo "$constitutional_response" | jq -r '.constitutional_validation_available' 2>/dev/null || echo "unknown")"
    echo "   Workflows Operational: $(echo "$constitutional_response" | jq -r '.governance_workflows_operational' 2>/dev/null || echo "unknown")"
else
    print_error "Constitutional governance integration is not operational"
fi

# Docker Services Check
print_status "Checking Docker Services..."

if command -v docker-compose > /dev/null 2>&1; then
    cd "$(dirname "$0")/.."
    
    if [ -f "deploy/docker-compose.acgs.yaml" ]; then
        docker_services=$(docker-compose -f deploy/docker-compose.acgs.yaml ps --services 2>/dev/null || echo "")
        
        if [ -n "$docker_services" ]; then
            running_services=0
            total_services=0
            
            for service in $docker_services; do
                total_services=$((total_services + 1))
                if docker-compose -f deploy/docker-compose.acgs.yaml ps "$service" | grep -q "Up\|healthy"; then
                    print_success "Docker service $service is running"
                    running_services=$((running_services + 1))
                else
                    print_warning "Docker service $service is not running"
                fi
            done
            
            print_status "Docker Services: $running_services/$total_services running"
        else
            print_warning "No Docker services found or Docker Compose not configured"
        fi
    else
        print_warning "Docker Compose configuration not found"
    fi
else
    print_warning "Docker Compose not available"
fi

# Performance Check
print_status "Performance Check..."

# Check response times
api_response_time=$(curl -o /dev/null -s -w '%{time_total}' "http://localhost:8010/health" 2>/dev/null || echo "0")
constitutional_response_time=$(curl -o /dev/null -s -w '%{time_total}' "http://localhost:8010/constitutional/health" 2>/dev/null || echo "0")

echo "   API Response Time: ${api_response_time}s"
echo "   Constitutional Check Time: ${constitutional_response_time}s"

# Check if response times are within acceptable limits
if (( $(echo "$api_response_time < 2.0" | bc -l 2>/dev/null || echo "0") )); then
    print_success "API response time is acceptable"
else
    print_warning "API response time is slow (>${api_response_time}s)"
fi

# Summary
echo ""
print_status "Health Check Summary"
echo "===================="

total_healthy=$((acgs_healthy + flywheel_healthy + infra_healthy))
total_services=$((acgs_total + flywheel_total + infra_total))

echo "   Total Services: $total_healthy/$total_services healthy"
echo "   ACGS-1 Core: $acgs_healthy/$acgs_total"
echo "   Data Flywheel: $flywheel_healthy/$flywheel_total"
echo "   Infrastructure: $infra_healthy/$infra_total"

# Overall status determination
if [ $total_healthy -eq $total_services ]; then
    print_success "🎯 All systems operational - Ready for constitutional governance optimization!"
    exit 0
elif [ $acgs_healthy -ge 5 ] && [ $flywheel_healthy -ge 2 ] && [ $infra_healthy -ge 2 ]; then
    print_warning "⚠️ System partially operational - Some services need attention"
    exit 1
else
    print_error "❌ System not operational - Multiple critical services are down"
    exit 2
fi
