#!/bin/bash

# ACGS-1 Complete Service Startup Script
# Starts all 7 core services for Phase 3 completion

set -e

echo "🚀 ACGS-1 Complete Service Startup"
echo "=================================="
echo "Date: $(date)"
echo "Starting all 7 core services (ports 8000-8006)"
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

# Project root directory (current directory)
PROJECT_ROOT="/home/ubuntu/ACGS"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/pids"

# Create necessary directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Service configuration with correct paths
declare -A SERVICES=(
    ["auth_service"]="8000:services/platform/authentication/auth_service"
    ["ac_service"]="8001:services/core/constitutional-ai/ac_service"
    ["integrity_service"]="8002:services/platform/integrity/integrity_service"
    ["fv_service"]="8003:services/core/formal-verification/fv_service"
    ["gs_service"]="8004:services/core/governance-synthesis/gs_service"
    ["pgc_service"]="8005:services/core/policy-governance/pgc_service"
    ["ec_service"]="8006:services/core/evolutionary-computation"
)

# Function to check if service is running
check_service() {
    local service_name=$1
    local port=$2
    
    if curl -f -s --connect-timeout 5 --max-time 10 "http://localhost:$port/health" > /dev/null 2>&1; then
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
    pkill -f "$service_name" || true
    
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
    
    # Determine the correct main module path based on service structure
    local main_module=""
    local working_dir=""
    
    case $service_name in
        "auth_service")
            working_dir="$service_dir"
            if [ -f "$service_dir/app/main.py" ]; then
                main_module="app.main:app"
            else
                print_error "Auth service main.py not found"
                return 1
            fi
            ;;
        "ac_service")
            working_dir="$service_dir"
            if [ -f "$service_dir/app/main.py" ]; then
                main_module="app.main:app"
            else
                print_error "AC service main.py not found"
                return 1
            fi
            ;;
        "integrity_service")
            working_dir="$service_dir"
            if [ -f "$service_dir/app/main.py" ]; then
                main_module="app.main:app"
            else
                print_error "Integrity service main.py not found"
                return 1
            fi
            ;;
        "fv_service")
            working_dir="$service_dir"
            if [ -f "$service_dir/main.py" ]; then
                main_module="main:app"
            else
                print_error "FV service main.py not found"
                return 1
            fi
            ;;
        "gs_service")
            working_dir="$service_dir"
            if [ -f "$service_dir/app/main.py" ]; then
                main_module="app.main:app"
            else
                print_error "GS service main.py not found"
                return 1
            fi
            ;;
        "pgc_service")
            working_dir="$service_dir"
            if [ -f "$service_dir/app/main.py" ]; then
                main_module="app.main:app"
            else
                print_error "PGC service main.py not found"
                return 1
            fi
            ;;
        "ec_service")
            working_dir="$service_dir"
            if [ -f "$service_dir/app/main.py" ]; then
                main_module="app.main:app"
            else
                print_error "EC service main.py not found"
                return 1
            fi
            ;;
    esac
    
    # Stop any existing service
    stop_service "$service_name" "$port"
    
    # Set common environment variables
    export DATABASE_URL="sqlite+aiosqlite:///./acgs_test.db"
    export REDIS_URL="redis://localhost:6379/0"
    export LOG_LEVEL="INFO"
    export SERVICE_PORT="$port"
    export SECRET_KEY="acgs-development-secret-key-2024-phase3-completion-testing-$(date +%s)"
    export CSRF_SECRET_KEY="acgs-development-csrf-secret-key-2024-phase3-completion"
    export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/services:$PYTHONPATH"
    
    # Service-specific environment variables
    case $service_name in
        "auth_service")
            export AUTH_SERVICE_PORT="$port"
            ;;
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
        "pgc_service")
            export PGC_SERVICE_PORT="$port"
            ;;
        "ec_service")
            export EC_SERVICE_PORT="$port"
            ;;
    esac
    
    # Change to service directory
    cd "$working_dir"
    
    # Start the service in background
    print_status "Executing: uvicorn $main_module --host 0.0.0.0 --port $port"
    nohup python3 -m uvicorn "$main_module" --host 0.0.0.0 --port "$port" > "$log_file" 2>&1 &
    local service_pid=$!
    
    # Save PID
    echo "$service_pid" > "$pid_file"
    
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

    # Check if PostgreSQL is running (optional for testing)
    if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        print_warning "PostgreSQL not running - services will use fallback configuration"
    else
        print_success "PostgreSQL is running"
    fi

    # Check if Redis is running
    if ! redis-cli ping > /dev/null 2>&1; then
        print_warning "Redis not running - services will use fallback configuration"
    else
        print_success "Redis is running"
    fi

    return 0
}

# Main execution
main() {
    print_status "Step 1: Checking prerequisites"
    if ! check_prerequisites; then
        print_error "Prerequisites check failed"
        exit 1
    fi
    
    print_status "Step 2: Starting all ACGS services"
    
    # Service startup order (dependency-aware)
    local service_order=("auth_service" "ac_service" "integrity_service" "fv_service" "gs_service" "pgc_service" "ec_service")
    local started_services=0
    local total_services=${#service_order[@]}
    
    for service_name in "${service_order[@]}"; do
        if start_service "$service_name"; then
            started_services=$((started_services + 1))
        fi
        sleep 3  # Wait between service starts
    done
    
    print_status "Step 3: Final health check"
    sleep 10  # Wait for all services to stabilize
    
    echo ""
    print_success "🎉 Service Startup Completed!"
    echo "================================================"
    echo "✅ Total services started: $started_services/$total_services"
    echo ""
    
    # Final health check for all services
    print_status "Final health check for all services:"
    for service_name in "${service_order[@]}"; do
        local config=${SERVICES[$service_name]}
        local port=$(echo $config | cut -d: -f1)
        
        if check_service "$service_name" "$port"; then
            print_success "✅ $service_name (port $port): OPERATIONAL"
        else
            print_error "❌ $service_name (port $port): FAILED"
        fi
    done
    
    echo ""
    echo "📄 Logs directory: $LOG_DIR"
    echo "📄 PID files: $PID_DIR"
    echo ""
    echo "🔧 Service Management Commands:"
    echo "   Stop all services: pkill -f 'uvicorn.*:800[0-6]'"
    echo "   Check logs: tail -f $LOG_DIR/<service_name>.log"
    echo ""
    echo "🔍 Health Check Commands:"
    for service_name in "${service_order[@]}"; do
        local config=${SERVICES[$service_name]}
        local port=$(echo $config | cut -d: -f1)
        echo "   $service_name: curl -s http://localhost:$port/health"
    done
    
    if [ $started_services -eq $total_services ]; then
        print_success "🎯 ALL SERVICES OPERATIONAL - Phase 3 Complete!"
        return 0
    else
        print_warning "⚠️ Some services failed to start - Check logs for details"
        return 1
    fi
}

# Run main function
main "$@"
