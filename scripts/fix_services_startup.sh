#!/bin/bash
# ACGS-2 Service Startup Fix Script
# Constitutional Hash: cdd01ef066bc6cf2

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 ACGS-2 Service Startup Fix Script${NC}"
echo -e "${BLUE}Constitutional Hash: cdd01ef066bc6cf2${NC}"
echo ""

# Project root
PROJECT_ROOT="/home/dislove/ACGS-2"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/pids"

# Create directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Function to print status
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to kill existing services
kill_existing_services() {
    print_status "Killing existing services..."
    
    # Kill services by port
    for port in 8001 8002 8003 8004 8005 8006 8007 8008 8009 8010 8014 8016; do
        if lsof -ti:$port >/dev/null 2>&1; then
            print_status "Killing service on port $port"
            lsof -ti:$port | xargs kill -9 2>/dev/null || true
        fi
    done
    
    # Kill by process name
    pkill -f "uvicorn.*800" 2>/dev/null || true
    pkill -f "python.*800" 2>/dev/null || true
    
    sleep 2
    print_status "Existing services killed"
}

# Function to start a service
start_service() {
    local service_name=$1
    local service_path=$2
    local port=$3
    local main_module=$4
    
    print_status "Starting $service_name on port $port..."
    
    local log_file="$LOG_DIR/${service_name}.log"
    local pid_file="$PID_DIR/${service_name}.pid"
    
    # Set environment variables
    export PYTHONPATH="$PROJECT_ROOT"
    export CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
    export ENVIRONMENT="development"
    
    # Change to service directory
    cd "$PROJECT_ROOT/$service_path"
    
    # Start service
    nohup python3 -m uvicorn "$main_module" \
        --host 0.0.0.0 \
        --port "$port" \
        --reload \
        --log-level info \
        > "$log_file" 2>&1 &
    
    local service_pid=$!
    echo "$service_pid" > "$pid_file"
    
    print_status "$service_name started with PID $service_pid"
    
    # Wait a moment and check if service is running
    sleep 3
    if kill -0 "$service_pid" 2>/dev/null; then
        print_status "$service_name is running successfully"
    else
        print_error "$service_name failed to start"
        return 1
    fi
}

# Function to test service health
test_service_health() {
    local service_name=$1
    local port=$2
    
    print_status "Testing $service_name health..."
    
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "http://localhost:$port/health" >/dev/null 2>&1; then
            print_status "$service_name health check passed"
            return 0
        fi
        
        print_warning "Attempt $attempt/$max_attempts failed for $service_name"
        sleep 2
        ((attempt++))
    done
    
    print_error "$service_name health check failed after $max_attempts attempts"
    return 1
}

# Main execution
main() {
    print_status "Starting ACGS-2 service fixes..."
    
    # Kill existing services
    kill_existing_services
    
    # Start core services
    print_status "Starting core services..."
    
    # Constitutional AI Service
    if start_service "constitutional_ai" "services/core/constitutional-ai/ac_service" "8001" "app.main_simple:app"; then
        test_service_health "Constitutional AI" "8001"
    fi
    
    # Authentication Service
    if start_service "auth_service" "services/platform_services/authentication/auth_service" "8016" "app.main:app"; then
        test_service_health "Authentication" "8016"
    fi
    
    # Agent HITL Service (already running, just test)
    test_service_health "Agent HITL" "8008" || print_warning "Agent HITL service may need restart"
    
    # API Gateway (already running, just test)
    test_service_health "API Gateway" "8010" || print_warning "API Gateway service may need restart"
    
    print_status "Service startup fixes completed!"
    print_status "Check logs in $LOG_DIR for detailed information"
    
    # Show service status
    echo ""
    print_status "Current service status:"
    for port in 8001 8008 8010 8016; do
        if curl -s -f "http://localhost:$port/health" >/dev/null 2>&1; then
            echo -e "  ✅ Port $port: ${GREEN}Healthy${NC}"
        else
            echo -e "  ❌ Port $port: ${RED}Not responding${NC}"
        fi
    done
}

# Run main function
main "$@"
