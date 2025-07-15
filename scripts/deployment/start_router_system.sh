#!/bin/bash
# ACGS-2 Router System Startup Script
# Constitutional Hash: cdd01ef066bc6cf2

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Constitutional compliance
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

echo -e "${BLUE}🚀 Starting ACGS-2 Router System${NC}"
echo -e "${BLUE}Constitutional Hash: ${CONSTITUTIONAL_HASH}${NC}"
echo "=" * 50

# Check environment variables
check_env_vars() {
    echo -e "${YELLOW}🔍 Checking environment variables...${NC}"
    
    if [ -z "$GROQ_API_KEY" ]; then
        echo -e "${RED}❌ GROQ_API_KEY not set${NC}"
        exit 1
    fi
    
    if [ -z "$REDIS_URL" ]; then
        echo -e "${YELLOW}⚠️  REDIS_URL not set, using default${NC}"
        export REDIS_URL="redis://localhost:6379/0"
    fi
    
    # Set router configuration
    export ROUTER_ENABLED=true
    export ROUTER_PRIMARY_PROVIDER=true
    export KIMI_K2_ENABLED=true
    export USE_ROUTER=true
    export CONSTITUTIONAL_HASH=$CONSTITUTIONAL_HASH
    
    echo -e "${GREEN}✅ Environment variables configured${NC}"
}

# Start Redis if not running
start_redis() {
    echo -e "${YELLOW}🔍 Checking Redis...${NC}"
    
    if ! redis-cli ping > /dev/null 2>&1; then
        echo -e "${YELLOW}🚀 Starting Redis...${NC}"
        redis-server --daemonize yes --port 6379
        sleep 2
        
        if redis-cli ping > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Redis started successfully${NC}"
        else
            echo -e "${RED}❌ Failed to start Redis${NC}"
            exit 1
        fi
    else
        echo -e "${GREEN}✅ Redis already running${NC}"
    fi
}

# Start the Hybrid Inference Router
start_router() {
    echo -e "${YELLOW}🚀 Starting Hybrid Inference Router...${NC}"
    
    cd services/shared/routing
    
    # Install dependencies if needed
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
    else
        source venv/bin/activate
    fi
    
    # Start the router service
    echo -e "${YELLOW}🌐 Starting router on port 8000...${NC}"
    python main.py &
    ROUTER_PID=$!
    
    # Wait for router to start
    sleep 5
    
    # Check if router is running
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "${GREEN}✅ Router started successfully (PID: $ROUTER_PID)${NC}"
        echo $ROUTER_PID > /tmp/router.pid
    else
        echo -e "${RED}❌ Failed to start router${NC}"
        exit 1
    fi
    
    cd - > /dev/null
}

# Test router integration
test_router() {
    echo -e "${YELLOW}🧪 Testing router integration...${NC}"
    
    # Test health endpoint
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        echo -e "${GREEN}✅ Router health check passed${NC}"
    else
        echo -e "${RED}❌ Router health check failed${NC}"
        return 1
    fi
    
    # Test model listing
    if curl -s http://localhost:8000/models | grep -q "moonshotai/kimi-k2-instruct"; then
        echo -e "${GREEN}✅ Kimi K2 model available in router${NC}"
    else
        echo -e "${YELLOW}⚠️  Kimi K2 model not found in router response${NC}"
    fi
    
    # Run integration tests
    echo -e "${YELLOW}🧪 Running integration tests...${NC}"
    cd scripts/testing
    python test_router_integration.py
    cd - > /dev/null
}

# Start core ACGS services with router configuration
start_services() {
    echo -e "${YELLOW}🚀 Starting ACGS core services...${NC}"
    
    # Set environment for all services to use router
    export AI_PROVIDER="router"
    export AI_ENDPOINT="http://localhost:8000"
    export USE_ROUTER=true
    
    # Start services in background
    echo -e "${YELLOW}📡 Starting Constitutional AI Service...${NC}"
    cd services/core/constitutional-ai/ac_service
    python main.py &
    AC_PID=$!
    echo $AC_PID > /tmp/ac_service.pid
    cd - > /dev/null
    
    echo -e "${YELLOW}📡 Starting Governance Synthesis Service...${NC}"
    cd services/core/governance-synthesis/gs_service
    python main.py &
    GS_PID=$!
    echo $GS_PID > /tmp/gs_service.pid
    cd - > /dev/null
    
    echo -e "${YELLOW}📡 Starting Policy Governance Service...${NC}"
    cd services/core/policy-governance/pgc_service
    python main.py &
    PGC_PID=$!
    echo $PGC_PID > /tmp/pgc_service.pid
    cd - > /dev/null
    
    # Wait for services to start
    sleep 10
    
    echo -e "${GREEN}✅ Core services started${NC}"
    echo -e "${BLUE}Service PIDs:${NC}"
    echo -e "  Router: $ROUTER_PID"
    echo -e "  Constitutional AI: $AC_PID"
    echo -e "  Governance Synthesis: $GS_PID"
    echo -e "  Policy Governance: $PGC_PID"
}

# Display system status
show_status() {
    echo -e "${BLUE}📊 ACGS-2 Router System Status${NC}"
    echo "=" * 40
    
    echo -e "${BLUE}🌐 Router Service:${NC}"
    if curl -s http://localhost:8000/health > /dev/null; then
        echo -e "  Status: ${GREEN}✅ Running${NC}"
        echo -e "  Endpoint: http://localhost:8000"
        echo -e "  Health: http://localhost:8000/health"
        echo -e "  Models: http://localhost:8000/models"
    else
        echo -e "  Status: ${RED}❌ Not Running${NC}"
    fi
    
    echo -e "${BLUE}🔧 Configuration:${NC}"
    echo -e "  Router Enabled: ${ROUTER_ENABLED:-false}"
    echo -e "  Primary Provider: ${ROUTER_PRIMARY_PROVIDER:-false}"
    echo -e "  Kimi K2 Enabled: ${KIMI_K2_ENABLED:-false}"
    echo -e "  Constitutional Hash: ${CONSTITUTIONAL_HASH}"
    
    echo -e "${BLUE}📝 Usage:${NC}"
    echo -e "  Test router: curl http://localhost:8000/health"
    echo -e "  List models: curl http://localhost:8000/models"
    echo -e "  Route query: curl -X POST http://localhost:8000/route -d '{\"query\":\"test\"}'"
    echo -e "  Stop system: ./scripts/deployment/stop_router_system.sh"
}

# Cleanup function
cleanup() {
    echo -e "${YELLOW}🧹 Cleaning up...${NC}"
    
    # Kill services if PIDs exist
    for pid_file in /tmp/router.pid /tmp/ac_service.pid /tmp/gs_service.pid /tmp/pgc_service.pid; do
        if [ -f "$pid_file" ]; then
            PID=$(cat "$pid_file")
            if kill -0 "$PID" 2>/dev/null; then
                kill "$PID"
                echo -e "${GREEN}✅ Stopped process $PID${NC}"
            fi
            rm -f "$pid_file"
        fi
    done
}

# Trap cleanup on exit
trap cleanup EXIT

# Main execution
main() {
    check_env_vars
    start_redis
    start_router
    test_router
    start_services
    show_status
    
    echo -e "${GREEN}🎉 ACGS-2 Router System started successfully!${NC}"
    echo -e "${BLUE}Press Ctrl+C to stop all services${NC}"
    
    # Keep script running
    wait
}

# Run main function
main "$@"
