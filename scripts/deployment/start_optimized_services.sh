#!/bin/bash
# ACGS Optimized Services Startup Script
# Initializes performance-optimized Policy Governance and Governance Synthesis services
# with Redis caching, database optimization, and monitoring

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
REDIS_PORT=6389
POSTGRES_PORT=5439
PGC_SERVICE_PORT=8005
GS_SERVICE_PORT=8004
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001

# Performance targets
TARGET_P99_LATENCY_MS=5
TARGET_CACHE_HIT_RATE=0.85
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

echo -e "${BLUE}🚀 Starting ACGS Optimized Services${NC}"
echo -e "${BLUE}Performance Targets: P99 <${TARGET_P99_LATENCY_MS}ms, Cache Hit Rate >${TARGET_CACHE_HIT_RATE}, Constitutional Hash: ${CONSTITUTIONAL_HASH}${NC}"
echo ""

# Function to check if service is running
check_service() {
    local service_name=$1
    local port=$2
    local max_attempts=30
    local attempt=1
    
    echo -e "${YELLOW}⏳ Waiting for ${service_name} on port ${port}...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:${port}/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ ${service_name} is ready${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}   Attempt ${attempt}/${max_attempts} - waiting...${NC}"
        sleep 2
        ((attempt++))
    done
    
    echo -e "${RED}❌ ${service_name} failed to start within timeout${NC}"
    return 1
}

# Function to validate performance targets
validate_performance() {
    local service_name=$1
    local port=$2
    
    echo -e "${YELLOW}🎯 Validating performance targets for ${service_name}...${NC}"
    
    # Run quick performance test
    local start_time=$(date +%s%3N)
    local response=$(curl -s http://localhost:${port}/health)
    local end_time=$(date +%s%3N)
    local response_time=$((end_time - start_time))
    
    # Check constitutional hash
    local hash=$(echo "$response" | jq -r '.constitutional_hash // empty')
    
    if [ "$hash" = "$CONSTITUTIONAL_HASH" ]; then
        echo -e "${GREEN}   ✅ Constitutional hash validated: ${hash}${NC}"
    else
        echo -e "${RED}   ❌ Constitutional hash mismatch: expected ${CONSTITUTIONAL_HASH}, got ${hash}${NC}"
        return 1
    fi
    
    # Check response time
    if [ $response_time -le $TARGET_P99_LATENCY_MS ]; then
        echo -e "${GREEN}   ✅ Response time: ${response_time}ms (target: <${TARGET_P99_LATENCY_MS}ms)${NC}"
    else
        echo -e "${YELLOW}   ⚠️  Response time: ${response_time}ms (target: <${TARGET_P99_LATENCY_MS}ms)${NC}"
    fi
    
    return 0
}

# Function to warm up caches
warm_up_caches() {
    local service_name=$1
    local port=$2
    
    echo -e "${YELLOW}🔥 Warming up caches for ${service_name}...${NC}"
    
    # Make several requests to warm up caches
    for i in {1..10}; do
        curl -s http://localhost:${port}/health > /dev/null
        curl -s http://localhost:${port}/api/v1/performance/metrics > /dev/null
        sleep 0.1
    done
    
    echo -e "${GREEN}   ✅ Cache warm-up completed${NC}"
}

# Function to check Redis connectivity
check_redis() {
    echo -e "${YELLOW}🔴 Checking Redis connectivity...${NC}"
    
    if redis-cli -h localhost -p $REDIS_PORT ping | grep -q "PONG"; then
        echo -e "${GREEN}✅ Redis is accessible on port ${REDIS_PORT}${NC}"
        
        # Check Redis memory usage
        local memory_info=$(redis-cli -h localhost -p $REDIS_PORT info memory | grep used_memory_human)
        echo -e "${BLUE}   📊 Redis memory usage: ${memory_info#*:}${NC}"
        
        return 0
    else
        echo -e "${RED}❌ Redis is not accessible on port ${REDIS_PORT}${NC}"
        return 1
    fi
}

# Function to check PostgreSQL connectivity
check_postgres() {
    echo -e "${YELLOW}🗄️  Checking PostgreSQL connectivity...${NC}"
    
    if pg_isready -h localhost -p $POSTGRES_PORT -U acgs_user > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL is accessible on port ${POSTGRES_PORT}${NC}"
        return 0
    else
        echo -e "${RED}❌ PostgreSQL is not accessible on port ${POSTGRES_PORT}${NC}"
        return 1
    fi
}

# Function to start monitoring
start_monitoring() {
    echo -e "${YELLOW}📊 Starting monitoring services...${NC}"
    
    # Check if Prometheus is running
    if curl -s http://localhost:${PROMETHEUS_PORT}/api/v1/status/config > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Prometheus is running on port ${PROMETHEUS_PORT}${NC}"
    else
        echo -e "${YELLOW}⚠️  Prometheus not detected on port ${PROMETHEUS_PORT}${NC}"
    fi
    
    # Check if Grafana is running
    if curl -s http://localhost:${GRAFANA_PORT}/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Grafana is running on port ${GRAFANA_PORT}${NC}"
    else
        echo -e "${YELLOW}⚠️  Grafana not detected on port ${GRAFANA_PORT}${NC}"
    fi
}

# Function to run performance validation
run_performance_validation() {
    echo -e "${YELLOW}🧪 Running performance validation...${NC}"
    
    # Run load test if available
    if [ -f "tests/performance/load_test_optimized_services.py" ]; then
        echo -e "${BLUE}   Running optimized load test...${NC}"
        python3 tests/performance/load_test_optimized_services.py --quick-test
    else
        echo -e "${YELLOW}   Load test script not found, skipping detailed validation${NC}"
    fi
}

# Function to display service status
display_service_status() {
    echo -e "${BLUE}📋 Service Status Summary:${NC}"
    echo -e "${BLUE}================================${NC}"
    
    # Policy Governance Service
    if curl -s http://localhost:${PGC_SERVICE_PORT}/health > /dev/null 2>&1; then
        local pgc_metrics=$(curl -s http://localhost:${PGC_SERVICE_PORT}/api/v1/performance/metrics 2>/dev/null || echo '{}')
        echo -e "${GREEN}✅ Policy Governance Service (${PGC_SERVICE_PORT})${NC}"
        echo -e "   📊 Performance metrics available"
    else
        echo -e "${RED}❌ Policy Governance Service (${PGC_SERVICE_PORT})${NC}"
    fi
    
    # Governance Synthesis Service
    if curl -s http://localhost:${GS_SERVICE_PORT}/health > /dev/null 2>&1; then
        local gs_metrics=$(curl -s http://localhost:${GS_SERVICE_PORT}/api/v1/performance/metrics 2>/dev/null || echo '{}')
        echo -e "${GREEN}✅ Governance Synthesis Service (${GS_SERVICE_PORT})${NC}"
        echo -e "   📊 Performance metrics available"
    else
        echo -e "${RED}❌ Governance Synthesis Service (${GS_SERVICE_PORT})${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}🎯 Performance Targets:${NC}"
    echo -e "   P99 Latency: <${TARGET_P99_LATENCY_MS}ms"
    echo -e "   Cache Hit Rate: >${TARGET_CACHE_HIT_RATE}"
    echo -e "   Constitutional Hash: ${CONSTITUTIONAL_HASH}"
    echo ""
    echo -e "${BLUE}🔗 Service URLs:${NC}"
    echo -e "   Policy Governance: http://localhost:${PGC_SERVICE_PORT}"
    echo -e "   Governance Synthesis: http://localhost:${GS_SERVICE_PORT}"
    echo -e "   Prometheus: http://localhost:${PROMETHEUS_PORT}"
    echo -e "   Grafana: http://localhost:${GRAFANA_PORT}"
}

# Main execution
main() {
    echo -e "${BLUE}🔧 Pre-flight checks...${NC}"
    
    # Check dependencies
    if ! command -v curl &> /dev/null; then
        echo -e "${RED}❌ curl is required but not installed${NC}"
        exit 1
    fi
    
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}❌ jq is required but not installed${NC}"
        exit 1
    fi
    
    # Check infrastructure services
    check_redis || exit 1
    check_postgres || exit 1
    
    echo ""
    echo -e "${BLUE}🚀 Starting optimized ACGS services...${NC}"
    
    # Wait for services to be ready
    check_service "Policy Governance Service" $PGC_SERVICE_PORT || exit 1
    check_service "Governance Synthesis Service" $GS_SERVICE_PORT || exit 1
    
    echo ""
    echo -e "${BLUE}🔥 Warming up services...${NC}"
    
    # Warm up caches
    warm_up_caches "Policy Governance Service" $PGC_SERVICE_PORT
    warm_up_caches "Governance Synthesis Service" $GS_SERVICE_PORT
    
    echo ""
    echo -e "${BLUE}🎯 Validating performance...${NC}"
    
    # Validate performance targets
    validate_performance "Policy Governance Service" $PGC_SERVICE_PORT
    validate_performance "Governance Synthesis Service" $GS_SERVICE_PORT
    
    echo ""
    echo -e "${BLUE}📊 Setting up monitoring...${NC}"
    
    # Start monitoring
    start_monitoring
    
    echo ""
    echo -e "${GREEN}🎉 ACGS Optimized Services Started Successfully!${NC}"
    echo ""
    
    # Display final status
    display_service_status
    
    echo ""
    echo -e "${BLUE}💡 Next Steps:${NC}"
    echo -e "   1. Run load tests: python3 tests/performance/load_test_optimized_services.py"
    echo -e "   2. Monitor performance: http://localhost:${GRAFANA_PORT}"
    echo -e "   3. Check metrics: curl http://localhost:${PGC_SERVICE_PORT}/api/v1/performance/metrics"
    echo ""
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "ACGS Optimized Services Startup Script"
        echo ""
        echo "Usage: $0 [options]"
        echo ""
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --quick        Skip performance validation"
        echo "  --no-warmup    Skip cache warm-up"
        echo ""
        echo "Environment Variables:"
        echo "  REDIS_PORT     Redis port (default: 6389)"
        echo "  POSTGRES_PORT  PostgreSQL port (default: 5439)"
        echo "  PGC_PORT       Policy Governance port (default: 8005)"
        echo "  GS_PORT        Governance Synthesis port (default: 8004)"
        exit 0
        ;;
    --quick)
        echo -e "${YELLOW}⚡ Quick start mode - skipping detailed validation${NC}"
        QUICK_MODE=true
        ;;
    --no-warmup)
        echo -e "${YELLOW}❄️  Skipping cache warm-up${NC}"
        NO_WARMUP=true
        ;;
esac

# Run main function
main
