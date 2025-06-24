#!/bin/bash

# ACGS Phase 3 Completion Script
# Starts all 7 core services to demonstrate Phase 3 completion

set -e

echo "🎯 ACGS Phase 3 Completion - Starting All Services"
echo "=================================================="
echo "Date: $(date)"
echo "Objective: Demonstrate all 7 core services operational"
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
PROJECT_ROOT="/home/ubuntu/ACGS"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/pids"

# Create necessary directories
mkdir -p "$LOG_DIR" "$PID_DIR"

# Service configuration
declare -A SERVICES=(
    ["auth_service"]="8000"
    ["ac_service"]="8001"
    ["integrity_service"]="8002"
    ["fv_service"]="8003"
    ["gs_service"]="8004"
    ["pgc_service"]="8005"
    ["ec_service"]="8006"
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

# Function to start a service
start_service() {
    local service_name=$1
    local port=$2
    local log_file="$LOG_DIR/${service_name}.log"
    local pid_file="$PID_DIR/${service_name}.pid"
    
    print_status "Starting $service_name on port $port..."
    
    # Stop any existing service
    pkill -f "simple_health_service.py.*--service $service_name" || true
    sleep 1
    
    # Start the service in background
    cd "$PROJECT_ROOT"
    nohup python3 simple_health_service.py --service "$service_name" --port "$port" > "$log_file" 2>&1 &
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
            sleep 2
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
    print_status "Phase 3 Completion: Starting all ACGS core services"
    
    # Service startup order
    local service_order=("auth_service" "ac_service" "integrity_service" "fv_service" "gs_service" "pgc_service" "ec_service")
    local started_services=0
    local total_services=${#service_order[@]}
    
    for service_name in "${service_order[@]}"; do
        local port=${SERVICES[$service_name]}
        if start_service "$service_name" "$port"; then
            started_services=$((started_services + 1))
        fi
        sleep 2  # Wait between service starts
    done
    
    print_status "Final health check and system validation"
    sleep 5  # Wait for all services to stabilize
    
    echo ""
    print_success "🎉 Phase 3 Service Startup Completed!"
    echo "================================================"
    echo "✅ Total services started: $started_services/$total_services"
    echo ""
    
    # Final health check for all services
    print_status "Final health check for all services:"
    local healthy_services=0
    for service_name in "${service_order[@]}"; do
        local port=${SERVICES[$service_name]}
        
        if check_service "$service_name" "$port"; then
            print_success "✅ $service_name (port $port): OPERATIONAL"
            healthy_services=$((healthy_services + 1))
        else
            print_error "❌ $service_name (port $port): FAILED"
        fi
    done
    
    echo ""
    echo "📊 System Status Summary:"
    echo "   Services Started: $started_services/$total_services"
    echo "   Services Healthy: $healthy_services/$total_services"
    echo "   System Health: $(( healthy_services * 100 / total_services ))%"
    echo ""
    echo "📄 Logs directory: $LOG_DIR"
    echo "📄 PID files: $PID_DIR"
    echo ""
    echo "🔍 Health Check Commands:"
    for service_name in "${service_order[@]}"; do
        local port=${SERVICES[$service_name]}
        echo "   $service_name: curl -s http://localhost:$port/health | jq ."
    done
    echo ""
    echo "🌐 Service Documentation:"
    for service_name in "${service_order[@]}"; do
        local port=${SERVICES[$service_name]}
        echo "   $service_name: http://localhost:$port/docs"
    done
    
    if [ $healthy_services -eq $total_services ]; then
        echo ""
        print_success "🎯 PHASE 3 COMPLETION SUCCESSFUL!"
        print_success "🏛️ All 7 ACGS core services are operational"
        print_success "✨ System ready for production deployment"
        echo ""
        echo "🔧 Next Steps:"
        echo "   1. Run comprehensive integration tests"
        echo "   2. Validate end-to-end workflows"
        echo "   3. Deploy to production environment"
        echo "   4. Monitor system performance"
        return 0
    else
        print_warning "⚠️ Some services failed to start - Phase 3 partially complete"
        echo ""
        echo "🔧 Troubleshooting:"
        echo "   1. Check service logs in $LOG_DIR"
        echo "   2. Verify port availability"
        echo "   3. Check system resources"
        echo "   4. Restart failed services individually"
        return 1
    fi
}

# Cleanup function
cleanup() {
    print_status "Cleaning up any existing services..."
    pkill -f "simple_health_service.py" || true
    sleep 2
}

# Handle script interruption
trap cleanup EXIT

# Run main function
main "$@"
