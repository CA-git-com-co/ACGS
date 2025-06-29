#!/bin/bash
# ACGS-1 Lite System Health Check Script
# Constitutional Hash: cdd01ef066bc6cf2

set -e

echo "🏥 ACGS-1 Lite System Health Check"
echo "Constitutional Hash: cdd01ef066bc6cf2"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Health check results
SERVICES_HEALTHY=0
SERVICES_TOTAL=0
ISSUES_FOUND=()

check_service_health() {
    local service_name="$1"
    local port="$2"
    local health_endpoint="$3"
    
    SERVICES_TOTAL=$((SERVICES_TOTAL + 1))
    
    echo -n "Checking $service_name (port $port): "
    
    if curl -sf "http://localhost:$port$health_endpoint" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ HEALTHY${NC}"
        SERVICES_HEALTHY=$((SERVICES_HEALTHY + 1))
        return 0
    else
        echo -e "${RED}❌ UNHEALTHY${NC}"
        ISSUES_FOUND+=("$service_name health check failed")
        return 1
    fi
}

check_docker_service() {
    local service_name="$1"
    
    echo -n "Checking Docker service $service_name: "
    
    if docker-compose ps "$service_name" 2>/dev/null | grep -q "Up"; then
        echo -e "${GREEN}✅ RUNNING${NC}"
        return 0
    else
        echo -e "${RED}❌ NOT RUNNING${NC}"
        ISSUES_FOUND+=("Docker service $service_name is not running")
        return 1
    fi
}

check_constitutional_hash() {
    echo "🔒 Verifying Constitutional Hash..."
    
    local expected_hash="cdd01ef066bc6cf2"
    local services=("8004:/v1/data/acgs/main/health" "8002:/health" "8003:/health" "8001:/health")
    
    for service in "${services[@]}"; do
        local port=$(echo "$service" | cut -d: -f1)
        local endpoint=$(echo "$service" | cut -d: -f2)
        
        echo -n "  Port $port: "
        
        local response=$(curl -s "http://localhost:$port$endpoint" 2>/dev/null || echo "{}")
        local hash=$(echo "$response" | jq -r '.constitutional_hash // empty' 2>/dev/null)
        
        if [ "$hash" = "$expected_hash" ]; then
            echo -e "${GREEN}✅ VERIFIED${NC}"
        elif [ -z "$hash" ]; then
            echo -e "${YELLOW}⚠️  NO HASH${NC}"
            ISSUES_FOUND+=("Service on port $port does not report constitutional hash")
        else
            echo -e "${RED}❌ MISMATCH${NC}"
            ISSUES_FOUND+=("Service on port $port reports incorrect constitutional hash: $hash")
        fi
    done
}

echo ""
echo "🐳 Docker Services Health Check"
echo "==============================="

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ docker-compose not found${NC}"
    ISSUES_FOUND+=("docker-compose is not installed or not in PATH")
else
    # Core services
    check_docker_service "policy-engine" || true
    check_docker_service "evolution-oversight" || true
    check_docker_service "audit-engine" || true
    check_docker_service "sandbox-controller" || true
    
    # Infrastructure services
    check_docker_service "postgres" || true
    check_docker_service "redis" || true
    check_docker_service "redpanda" || true
fi

echo ""
echo "🌐 Service Health Endpoints"
echo "============================"

# Check service health endpoints
check_service_health "Policy Engine" "8004" "/v1/data/acgs/main/health" || true
check_service_health "Evolution Oversight" "8002" "/health" || true
check_service_health "Audit Engine" "8003" "/health" || true
check_service_health "Sandbox Controller" "8001" "/health" || true

echo ""
check_constitutional_hash

echo ""
echo "📊 Performance Metrics Check"
echo "============================"

# Check policy engine performance
echo -n "Policy Engine Performance: "
if metrics=$(curl -s "http://localhost:8004/v1/metrics" 2>/dev/null); then
    p99_latency=$(echo "$metrics" | jq -r '.percentiles.p99 // 0')
    cache_hit_rate=$(echo "$metrics" | jq -r '.cache_hit_rate // 0')
    
    if (( $(echo "$p99_latency < 5.0" | bc -l) )) && (( $(echo "$cache_hit_rate > 0.8" | bc -l) )); then
        echo -e "${GREEN}✅ GOOD${NC} (P99: ${p99_latency}ms, Cache: $(echo "$cache_hit_rate * 100" | bc -l | cut -d. -f1)%)"
    else
        echo -e "${YELLOW}⚠️  DEGRADED${NC} (P99: ${p99_latency}ms, Cache: $(echo "$cache_hit_rate * 100" | bc -l | cut -d. -f1)%)"
        ISSUES_FOUND+=("Policy engine performance degraded")
    fi
else
    echo -e "${RED}❌ UNAVAILABLE${NC}"
    ISSUES_FOUND+=("Policy engine metrics unavailable")
fi

echo ""
echo "💾 Infrastructure Health Check"
echo "=============================="

# Check PostgreSQL
echo -n "PostgreSQL Database: "
if docker exec -it postgres psql -U acgs -d acgs_audit -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ CONNECTED${NC}"
else
    echo -e "${RED}❌ CONNECTION FAILED${NC}"
    ISSUES_FOUND+=("PostgreSQL database connection failed")
fi

# Check Redis
echo -n "Redis Cache: "
if docker exec -it redis redis-cli ping 2>/dev/null | grep -q "PONG"; then
    echo -e "${GREEN}✅ CONNECTED${NC}"
else
    echo -e "${RED}❌ CONNECTION FAILED${NC}"
    ISSUES_FOUND+=("Redis cache connection failed")
fi

# Check Redpanda/Kafka
echo -n "Redpanda/Kafka: "
if docker exec -it redpanda rpk cluster info > /dev/null 2>&1; then
    echo -e "${GREEN}✅ RUNNING${NC}"
else
    echo -e "${RED}❌ NOT AVAILABLE${NC}"
    ISSUES_FOUND+=("Redpanda/Kafka not available")
fi

echo ""
echo "🔧 System Resources Check"
echo "========================="

# Check disk space
echo -n "Disk Space: "
disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$disk_usage" -lt 80 ]; then
    echo -e "${GREEN}✅ OK${NC} (${disk_usage}% used)"
elif [ "$disk_usage" -lt 90 ]; then
    echo -e "${YELLOW}⚠️  WARNING${NC} (${disk_usage}% used)"
    ISSUES_FOUND+=("Disk usage is high: ${disk_usage}%")
else
    echo -e "${RED}❌ CRITICAL${NC} (${disk_usage}% used)"
    ISSUES_FOUND+=("Disk usage is critical: ${disk_usage}%")
fi

# Check memory usage
echo -n "Memory Usage: "
memory_usage=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ "$memory_usage" -lt 80 ]; then
    echo -e "${GREEN}✅ OK${NC} (${memory_usage}% used)"
elif [ "$memory_usage" -lt 90 ]; then
    echo -e "${YELLOW}⚠️  WARNING${NC} (${memory_usage}% used)"
    ISSUES_FOUND+=("Memory usage is high: ${memory_usage}%")
else
    echo -e "${RED}❌ CRITICAL${NC} (${memory_usage}% used)"
    ISSUES_FOUND+=("Memory usage is critical: ${memory_usage}%")
fi

# Check CPU load
echo -n "CPU Load: "
cpu_load=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
cpu_cores=$(nproc)
if (( $(echo "$cpu_load < $cpu_cores" | bc -l) )); then
    echo -e "${GREEN}✅ OK${NC} (${cpu_load}/${cpu_cores} cores)"
else
    echo -e "${YELLOW}⚠️  HIGH${NC} (${cpu_load}/${cpu_cores} cores)"
    ISSUES_FOUND+=("CPU load is high: ${cpu_load}/${cpu_cores}")
fi

echo ""
echo "📋 Health Check Summary"
echo "======================"

echo "Services Healthy: $SERVICES_HEALTHY/$SERVICES_TOTAL"
echo "Constitutional Hash: cdd01ef066bc6cf2"

if [ ${#ISSUES_FOUND[@]} -eq 0 ]; then
    echo ""
    echo -e "${GREEN}🎉 All health checks passed!${NC}"
    echo -e "${GREEN}✅ ACGS-1 Lite system is healthy and ready${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ Issues found (${#ISSUES_FOUND[@]})${NC}"
    echo ""
    for issue in "${ISSUES_FOUND[@]}"; do
        echo -e "${RED}  • $issue${NC}"
    done
    echo ""
    echo -e "${YELLOW}🔧 Please address the issues above before proceeding${NC}"
    exit 1
fi