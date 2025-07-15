#!/bin/bash

# ACGS Production Readiness - Simple Service Startup
# Starts core ACGS services on correct ports for Phase 1 validation

set -e

echo "🚀 ACGS Production Readiness - Service Startup"
echo "=============================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
echo "Date: $(date)"
echo "Starting ACGS core services on production ports"
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
PROJECT_ROOT="/home/dislove/ACGS-2"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/pids"

# Create necessary directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# ACGS Service configuration with production ports
declare -A SERVICES=(
    ["auth_service"]="8016:services/platform/authentication/auth_service"
    ["ac_service"]="8002:services/core/constitutional-ai/ac_service"
    ["pgc_service"]="8003:services/core/policy-governance/pgc_service"
    ["gs_service"]="8004:services/core/governance-synthesis/gs_service"
    ["fv_service"]="8005:services/core/formal-verification/fv_service"
    ["ec_service"]="8010:services/core/evolutionary-computation"
)

# Function to check if service is running
check_service() {
    local service_name=$1
    local port=$2

    if curl -f -s --connect-timeout 3 --max-time 5 "http://localhost:$port/health" > /dev/null 2>&1; then
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
    
    # Determine the correct main module path
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
        "pgc_service")
            working_dir="$service_dir"
            if [ -f "$service_dir/app/main.py" ]; then
                main_module="app.main:app"
            else
                print_error "PGC service main.py not found"
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
        "fv_service")
            working_dir="$service_dir"
            if [ -f "$service_dir/main.py" ]; then
                main_module="main:app"
            elif [ -f "$service_dir/app/main.py" ]; then
                main_module="app.main:app"
            else
                print_error "FV service main.py not found"
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
    
    # Set environment variables
    export DATABASE_URL=os.environ.get("DATABASE_URL")
    export REDIS_URL="redis://localhost:6379/0"
    export LOG_LEVEL="INFO"
    export SERVICE_PORT="$port"
    export SECRET_KEY="acgs-production-secret-key-phase1-$(date +%s)"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    export CSRF_SECRET_KEY="acgs-production-csrf-secret-key-phase1"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    export PYTHONPATH="$PROJECT_ROOT:$PROJECT_ROOT/services:$PYTHONPATH"

    # Constitutional compliance configuration
    export CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
    export CONSTITUTIONAL_COMPLIANCE_THRESHOLD="0.95"
    export GOVERNANCE_VALIDATION_ENABLED="true"
    
    # Change to service directory
    cd "$working_dir"
    
    # Start the service in background
    print_status "Executing: python3 -m uvicorn $main_module --host 0.0.0.0 --port $port"
    nohup env PYTHONPATH="$PROJECT_ROOT" python3 -m uvicorn "$main_module" --host 0.0.0.0 --port "$port" > "$log_file" 2>&1 &
    local service_pid=$!
    
    # Save PID
    echo "$service_pid" > "$pid_file"
    
    # Wait and check if service started
    sleep 3
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
            sleep 3
            attempts=$((attempts+1))
        done
        
        print_warning "$service_name started but health check failed"
        return 1
    else
        print_error "$service_name failed to start. Check log: $log_file"
        return 1
    fi
}

# Main execution
main() {
    print_status "Starting ACGS core services for Phase 1 validation"
    
    # Service startup order
    local service_order=("auth_service" "ac_service" "pgc_service" "gs_service" "fv_service" "ec_service")
    local started_services=0
    local total_services=${#service_order[@]}
    
    for service_name in "${service_order[@]}"; do
        if start_service "$service_name"; then
            started_services=$((started_services + 1))
        fi
        sleep 2  # Wait between service starts
    done
    
    echo ""
    print_success "🎉 ACGS Service Startup Completed!"
    echo "================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "✅ Total services started: $started_services/$total_services"
    echo ""

    # Basic health check for all services
    print_status "Performing health checks:"
    local healthy_services=0
    for service_name in "${service_order[@]}"; do
        local config=${SERVICES[$service_name]}
        local port=$(echo $config | cut -d: -f1)

        if check_service "$service_name" "$port"; then
            print_success "✅ $service_name (port $port): OPERATIONAL"
            healthy_services=$((healthy_services + 1))
        else
            print_error "❌ $service_name (port $port): FAILED"
        fi
    done

    echo ""
    echo "📊 ACGS Infrastructure Status"
    echo "================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "✅ Services Started: $started_services/$total_services"
    echo "✅ Health Checks: $healthy_services/$total_services"
    echo ""
    echo "📄 Logs directory: $LOG_DIR"
    echo "📄 PID files: $PID_DIR"
    echo ""
    echo "🔧 Service Management Commands:"
    echo "   Stop all services: pkill -f 'uvicorn.*:80[0-9][0-9]'"
    echo "   Check logs: tail -f $LOG_DIR/<service_name>.log"
    echo ""

    if [ $started_services -eq $total_services ] && [ $healthy_services -eq $total_services ]; then
        print_success "🎯 ACGS INFRASTRUCTURE READY FOR PHASE 1 VALIDATION!"
        return 0
    else
        print_error "❌ ACGS INFRASTRUCTURE STARTUP INCOMPLETE - Check logs for details"
        return 1
    fi
}

# Run main function
main "$@"
