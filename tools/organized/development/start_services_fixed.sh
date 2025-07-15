# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash
# ACGS-1 Service Startup Script - Fixed Version
# This script starts all 7 core services with proper path handling

set -e

PROJECT_ROOT="/home/ubuntu/ACGS"
VENV_PATH="$PROJECT_ROOT/.venv"
LOG_DIR="$PROJECT_ROOT/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== ACGS-1 Service Startup - Fixed Version ===${NC}"
echo "Project Root: $PROJECT_ROOT"
echo "Virtual Environment: $VENV_PATH"
echo "Log Directory: $LOG_DIR"

# Create logs directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to stop service on a port
stop_service_on_port() {
    local port=$1
    local service_name=$2
    
    if check_port $port; then
        echo -e "${YELLOW}Stopping existing service on port $port ($service_name)...${NC}"
        lsof -ti:$port | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
}

# Function to start a service
start_service() {
    local service_name=$1
    local service_path=$2
    local port=$3
    local main_file=$4
    
    echo -e "${BLUE}Starting $service_name on port $port...${NC}"
    
    # Stop any existing service on this port
    stop_service_on_port $port $service_name
    
    # Check if service directory exists
    if [ ! -d "$service_path" ]; then
        echo -e "${RED}Error: Service directory not found: $service_path${NC}"
        return 1
    fi
    
    # Check if main file exists
    if [ ! -f "$service_path/$main_file" ]; then
        echo -e "${RED}Error: Main file not found: $service_path/$main_file${NC}"
        return 1
    fi
    
    # Start the service
    cd "$service_path"
    
    # Activate virtual environment if it exists
    if [ -f "$VENV_PATH/bin/activate" ]; then
        source "$VENV_PATH/bin/activate"
    fi
    
    # Set PYTHONPATH to include shared services
    export PYTHONPATH="$PROJECT_ROOT/services/shared:$PROJECT_ROOT:$PYTHONPATH"
    
    # Start service in background
    nohup python3 "$main_file" > "$LOG_DIR/${service_name}.log" 2>&1 &
    local pid=$!
    
    # Wait a moment and check if service started
    sleep 3
    
    if kill -0 $pid 2>/dev/null; then
        if check_port $port; then
            echo -e "${GREEN}✅ $service_name started successfully (PID: $pid, Port: $port)${NC}"
            return 0
        else
            echo -e "${YELLOW}⚠️ $service_name process running but port $port not responding${NC}"
            return 1
        fi
    else
        echo -e "${RED}❌ $service_name failed to start${NC}"
        echo "Last 10 lines of log:"
        tail -10 "$LOG_DIR/${service_name}.log" 2>/dev/null || echo "No log available"
        return 1
    fi
}

# Function to check service health
check_service_health() {
    local service_name=$1
    local port=$2
    
    echo -e "${BLUE}Checking health of $service_name on port $port...${NC}"
    
    # Try to curl the health endpoint
    if curl -s -f "http://localhost:$port/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $service_name health check passed${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ $service_name health check failed${NC}"
        return 1
    fi
}

echo -e "${BLUE}=== Stopping all existing services ===${NC}"

# Stop all services first
for port in 8000 8001 8002 8003 8004 8005 8006; do
    stop_service_on_port $port "service-on-$port"
done

echo -e "${BLUE}=== Starting core services ===${NC}"

# Service definitions: name, path, port, main_file
declare -a services=(
    "auth_service|$PROJECT_ROOT/services/platform/authentication/auth_service|8000|simple_main.py"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    "ac_service|$PROJECT_ROOT/services/core/constitutional-ai/ac_service/app|8001|main.py"
    "integrity_service|$PROJECT_ROOT/services/platform/integrity/integrity_service/app|8002|main.py"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    "fv_service|$PROJECT_ROOT/services/core/formal-verification/fv_service|8003|main.py"
    "gs_service|$PROJECT_ROOT/services/core/governance-synthesis/gs_service/app|8004|main.py"
    "pgc_service|$PROJECT_ROOT/services/core/policy-governance/pgc_service/app|8005|main.py"
    "ec_service|$PROJECT_ROOT/services/core/evolutionary-computation/app|8006|main.py"
)

# Start each service
started_services=0
total_services=${#services[@]}

for service_def in "${services[@]}"; do
    IFS='|' read -r service_name service_path port main_file <<< "$service_def"
    
    if start_service "$service_name" "$service_path" "$port" "$main_file"; then
        ((started_services++))
    fi
    
    echo # Add blank line for readability
done

echo -e "${BLUE}=== Service Startup Summary ===${NC}"
echo "Services started: $started_services/$total_services"

if [ $started_services -eq $total_services ]; then
    echo -e "${GREEN}🎉 All services started successfully!${NC}"
else
    echo -e "${YELLOW}⚠️ Some services failed to start. Check logs for details.${NC}"
fi

echo -e "${BLUE}=== Running health checks ===${NC}"

# Wait a bit for services to fully initialize
sleep 5

# Check health of all services
healthy_services=0
for service_def in "${services[@]}"; do
    IFS='|' read -r service_name service_path port main_file <<< "$service_def"
    
    if check_service_health "$service_name" "$port"; then
        ((healthy_services++))
    fi
done

echo -e "${BLUE}=== Health Check Summary ===${NC}"
echo "Healthy services: $healthy_services/$total_services"

if [ $healthy_services -eq $total_services ]; then
    echo -e "${GREEN}🎉 All services are healthy!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️ Some services are not responding to health checks.${NC}"
    exit 1
fi
