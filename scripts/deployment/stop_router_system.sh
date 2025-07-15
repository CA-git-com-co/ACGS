#!/bin/bash
# ACGS-2 Router System Stop Script
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

echo -e "${BLUE}🛑 Stopping ACGS-2 Router System${NC}"
echo -e "${BLUE}Constitutional Hash: ${CONSTITUTIONAL_HASH}${NC}"
echo "=" * 50

# Stop services by PID files
stop_services() {
    echo -e "${YELLOW}🛑 Stopping ACGS services...${NC}"
    
    # Service PID files
    PID_FILES=(
        "/tmp/router.pid:Router"
        "/tmp/ac_service.pid:Constitutional AI"
        "/tmp/gs_service.pid:Governance Synthesis"
        "/tmp/pgc_service.pid:Policy Governance"
    )
    
    for entry in "${PID_FILES[@]}"; do
        IFS=':' read -r pid_file service_name <<< "$entry"
        
        if [ -f "$pid_file" ]; then
            PID=$(cat "$pid_file")
            if kill -0 "$PID" 2>/dev/null; then
                echo -e "${YELLOW}🛑 Stopping $service_name (PID: $PID)...${NC}"
                kill "$PID"
                
                # Wait for graceful shutdown
                for i in {1..10}; do
                    if ! kill -0 "$PID" 2>/dev/null; then
                        echo -e "${GREEN}✅ $service_name stopped gracefully${NC}"
                        break
                    fi
                    sleep 1
                done
                
                # Force kill if still running
                if kill -0 "$PID" 2>/dev/null; then
                    echo -e "${YELLOW}⚠️  Force killing $service_name...${NC}"
                    kill -9 "$PID"
                    echo -e "${GREEN}✅ $service_name force stopped${NC}"
                fi
            else
                echo -e "${YELLOW}⚠️  $service_name process not running${NC}"
            fi
            rm -f "$pid_file"
        else
            echo -e "${YELLOW}⚠️  No PID file found for $service_name${NC}"
        fi
    done
}

# Stop services by port (fallback)
stop_by_port() {
    echo -e "${YELLOW}🔍 Checking for services by port...${NC}"
    
    # Ports to check
    PORTS=(8000 8001 8004 8005)
    
    for port in "${PORTS[@]}"; do
        PID=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$PID" ]; then
            echo -e "${YELLOW}🛑 Stopping service on port $port (PID: $PID)...${NC}"
            kill "$PID" 2>/dev/null || true
            sleep 1
            
            # Check if still running
            if kill -0 "$PID" 2>/dev/null; then
                echo -e "${YELLOW}⚠️  Force killing service on port $port...${NC}"
                kill -9 "$PID" 2>/dev/null || true
            fi
            echo -e "${GREEN}✅ Service on port $port stopped${NC}"
        fi
    done
}

# Clean up temporary files
cleanup_files() {
    echo -e "${YELLOW}🧹 Cleaning up temporary files...${NC}"
    
    # Remove PID files
    rm -f /tmp/router.pid
    rm -f /tmp/ac_service.pid
    rm -f /tmp/gs_service.pid
    rm -f /tmp/pgc_service.pid
    
    # Remove any router-specific temp files
    rm -f /tmp/router_*.log
    rm -f /tmp/acgs_router_*.tmp
    
    echo -e "${GREEN}✅ Temporary files cleaned up${NC}"
}

# Verify all services are stopped
verify_stopped() {
    echo -e "${YELLOW}🔍 Verifying services are stopped...${NC}"
    
    # Check router endpoint
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${RED}❌ Router still responding on port 8000${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Router stopped${NC}"
    fi
    
    # Check other service ports
    PORTS=(8001 8004 8005)
    for port in "${PORTS[@]}"; do
        if lsof -ti:$port > /dev/null 2>&1; then
            echo -e "${RED}❌ Service still running on port $port${NC}"
            return 1
        else
            echo -e "${GREEN}✅ Port $port is free${NC}"
        fi
    done
    
    return 0
}

# Display final status
show_final_status() {
    echo -e "${BLUE}📊 Final System Status${NC}"
    echo "=" * 30
    
    if verify_stopped; then
        echo -e "${GREEN}✅ All ACGS-2 Router System services stopped${NC}"
        echo -e "${BLUE}🔧 System is ready for restart${NC}"
    else
        echo -e "${YELLOW}⚠️  Some services may still be running${NC}"
        echo -e "${BLUE}💡 Try running this script again or check manually${NC}"
    fi
    
    echo -e "${BLUE}📝 Next steps:${NC}"
    echo -e "  Start system: ./scripts/deployment/start_router_system.sh"
    echo -e "  Check processes: ps aux | grep -E '(router|acgs)'"
    echo -e "  Check ports: netstat -tlnp | grep -E '(8000|8001|8004|8005)'"
}

# Main execution
main() {
    stop_services
    stop_by_port
    cleanup_files
    
    # Wait a moment for everything to settle
    sleep 2
    
    show_final_status
    
    echo -e "${GREEN}🎉 ACGS-2 Router System shutdown complete!${NC}"
}

# Run main function
main "$@"
