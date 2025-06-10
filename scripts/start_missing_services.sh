#!/bin/bash

# ACGS-1 Missing Services Startup Script
# Priority: CRITICAL
# Starts all missing core services for host-based deployment

set -e

echo "🚀 ACGS-1 Missing Services Startup"
echo "=================================="
echo "Date: $(date)"
echo "Priority: CRITICAL"
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

# Project root directory
PROJECT_ROOT="/home/dislove/ACGS-1"
VENV_PATH="$PROJECT_ROOT/venv"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/pids"

# Create necessary directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Service configuration
declare -A SERVICES=(
    ["ac_service"]="8001:services/core/constitutional-ai/ac_service"
    ["integrity_service"]="8002:services/platform/integrity/integrity_service"
    ["fv_service"]="8003:services/core/formal-verification/fv_service"
    ["gs_service"]="8004:services/core/governance-synthesis/gs_service"
)

# Function to check if service is running
check_service() {
    local service_name=$1
    local port=$2
    
    if curl -f -s "http://localhost:$port/health" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to stop existing service
stop_service() {
    local service_name=$1
    local port=$2
    local pid_file="$PID_DIR/${service_name}.pid"
    
    print_status "Stopping existing $service_name processes..."
    
    # Kill by PID file if exists
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid"
            print_success "Stopped $service_name (PID: $pid)"
        fi
        rm -f "$pid_file"
    fi
    
    # Kill any uvicorn processes on the port
    pkill -f "uvicorn.*:$port" || true
    
    # Wait for process to stop
    sleep 2
}

# Function to start a service
start_service() {
    local service_name=$1
    local config=${SERVICES[$service_name]}
    local port=$(echo $config | cut -d: -f1)
    local service_path=$(echo $config | cut -d: -f2)
    local service_dir="$PROJECT_ROOT/$service_path"
    local log_file="$LOG_DIR/${service_name}.log"
    local pid_file="$PID_DIR/${service_name}.pid"
    
    print_status "Starting $service_name on port $port..."
    
    # Check if service directory exists
    if [ ! -d "$service_dir" ]; then
        print_error "Service directory not found: $service_dir"
        return 1
    fi
    
    # Check for main.py or app/main.py
    local main_module=""
    if [ -f "$service_dir/main.py" ]; then
        main_module="main:app"
    elif [ -f "$service_dir/app/main.py" ]; then
        main_module="app.main:app"
    else
        print_error "No main.py found in $service_dir"
        return 1
    fi
    
    # Stop any existing service
    stop_service "$service_name" "$port"
    
    # Set environment variables
    export DATABASE_URL="postgresql://acgs_user:acgs_password@localhost:5432/acgs_db"
    export REDIS_URL="redis://localhost:6379/0"
    export LOG_LEVEL="INFO"
    export SERVICE_PORT="$port"
    
    # Service-specific environment variables
    case $service_name in
        "ac_service")
            export AC_SERVICE_PORT="$port"
            ;;
        "integrity_service")
            export INTEGRITY_SERVICE_PORT="$port"
            ;;
        "fv_service")
            export FV_SERVICE_PORT="$port"
            ;;
        "gs_service")
            export GS_SERVICE_PORT="$port"
            export AC_SERVICE_URL="http://localhost:8001"
            export INTEGRITY_SERVICE_URL="http://localhost:8002"
            export FV_SERVICE_URL="http://localhost:8003"
            export PGC_SERVICE_URL="http://localhost:8005"
            export EC_SERVICE_URL="http://localhost:8006"
            export AUTH_SERVICE_URL="http://localhost:8000"
            ;;
    esac
    
    # Change to service directory
    cd "$service_dir"
    
    # Activate virtual environment
    source "$VENV_PATH/bin/activate"
    
    # Start the service in background
    print_status "Executing: uvicorn $main_module --host 0.0.0.0 --port $port"
    nohup uvicorn "$main_module" --host 0.0.0.0 --port "$port" > "$log_file" 2>&1 &
    local service_pid=$!
    
    # Save PID
    echo "$service_pid" > "$pid_file"
    
    # Deactivate virtual environment
    deactivate
    
    # Wait and check if service started
    sleep 5
    if kill -0 "$service_pid" 2>/dev/null; then
        print_success "$service_name started successfully (PID: $service_pid)"
        
        # Test health endpoint
        local attempts=0
        while [ $attempts -lt 6 ]; do
            if check_service "$service_name" "$port"; then
                print_success "$service_name health check passed"
                return 0
            fi
            print_status "Waiting for $service_name to be ready... (attempt $((attempts+1))/6)"
            sleep 5
            attempts=$((attempts+1))
        done
        
        print_warning "$service_name started but health check failed"
        return 1
    else
        print_error "$service_name failed to start. Check log: $log_file"
        return 1
    fi
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if virtual environment exists
    if [ ! -d "$VENV_PATH" ]; then
        print_error "Virtual environment not found at $VENV_PATH"
        return 1
    fi
    
    # Check if PostgreSQL is running
    if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        print_warning "PostgreSQL not running. Attempting to start..."
        sudo systemctl start postgresql || true
        sleep 3
        if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
            print_error "Failed to start PostgreSQL"
            return 1
        fi
    fi
    print_success "PostgreSQL is running"
    
    # Check if Redis is running
    if ! redis-cli ping > /dev/null 2>&1; then
        print_warning "Redis not running. Attempting to start..."
        sudo systemctl start redis-server || true
        sleep 3
        if ! redis-cli ping > /dev/null 2>&1; then
            print_error "Failed to start Redis"
            return 1
        fi
    fi
    print_success "Redis is running"
    
    return 0
}

# Main execution
main() {
    print_status "Step 1: Checking prerequisites"
    if ! check_prerequisites; then
        print_error "Prerequisites check failed"
        exit 1
    fi
    
    print_status "Step 2: Starting missing services"
    local started_services=0
    local total_services=${#SERVICES[@]}
    
    # Start services in dependency order
    local service_order=("ac_service" "integrity_service" "fv_service" "gs_service")
    
    for service_name in "${service_order[@]}"; do
        if [[ -n "${SERVICES[$service_name]}" ]]; then
            if start_service "$service_name"; then
                started_services=$((started_services + 1))
            fi
            sleep 3  # Wait between service starts
        fi
    done
    
    print_status "Step 3: Final health check"
    sleep 10  # Wait for all services to stabilize
    
    # Run comprehensive health check
    if [ -f "$PROJECT_ROOT/scripts/comprehensive_health_check.py" ]; then
        print_status "Running comprehensive health check..."
        cd "$PROJECT_ROOT"
        python scripts/comprehensive_health_check.py
    fi
    
    print_status "Step 4: Summary"
    echo ""
    print_success "🎉 Service startup completed!"
    echo "=============================="
    echo "✅ Started services: $started_services/$total_services"
    echo "📄 Logs directory: $LOG_DIR"
    echo "📄 PID files: $PID_DIR"
    echo ""
    echo "🔧 To stop services:"
    echo "   pkill -f 'uvicorn.*:800[1-4]'"
    echo ""
    echo "🔧 To check individual service logs:"
    for service_name in "${service_order[@]}"; do
        echo "   tail -f $LOG_DIR/${service_name}.log"
    done
    
    if [ $started_services -eq $total_services ]; then
        print_success "All services started successfully!"
        return 0
    else
        print_warning "Some services failed to start. Check logs for details."
        return 1
    fi
}

# Run main function
main "$@"
