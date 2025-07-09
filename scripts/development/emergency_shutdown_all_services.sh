#!/bin/bash
# Emergency shutdown script for ACGS-PGP services
# Properly terminates all services on their designated ports

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Emergency shutdown function
emergency_shutdown() {
    log_info "🚨 INITIATING EMERGENCY SHUTDOWN PROCEDURE"
    
    local shutdown_start_time=$(date +%s)
    local services_stopped=0
    
    # Step 1: Send graceful shutdown signals to all services
    log_info "Step 1: Sending graceful shutdown signals..."
    for service_name in "${!SERVICES[@]}"; do
        local port=${SERVICES[$service_name]}
        log_info "Stopping $service_name on port $port..."
        
        # Find and kill processes listening on the port
        local pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$pids" ]; then
            for pid in $pids; do
                kill -TERM $pid 2>/dev/null || true
            done
            log_success "$service_name shutdown signal sent"
        else
            log_info "$service_name not found running on port $port"
        fi
    done
    
    # Step 2: Wait for graceful shutdown (max 10 seconds)
    log_info "Step 2: Waiting for graceful shutdown..."
    sleep 5
    
    # Step 3: Force kill any remaining processes
    log_info "Step 3: Force stopping any remaining services..."
    for service_name in "${!SERVICES[@]}"; do
        local port=${SERVICES[$service_name]}
        local pids=$(lsof -ti:$port 2>/dev/null || true)
        if [ -n "$pids" ]; then
            for pid in $pids; do
                kill -9 $pid 2>/dev/null || true
            done
            log_info "$service_name force stopped"
        fi
    done
    
    # Step 4: Verify all services are stopped
    log_info "Step 4: Verifying all services are stopped..."
    sleep 2
    for service_name in "${!SERVICES[@]}"; do
        local port=${SERVICES[$service_name]}
        if ! curl -s -f "http://localhost:$port/health" >/dev/null 2>&1; then
            ((services_stopped++))
            log_success "$service_name confirmed stopped"
        else
            log_error "$service_name still responding after shutdown"
        fi
    done
    
    local shutdown_end_time=$(date +%s)
    local shutdown_duration=$((shutdown_end_time - shutdown_start_time))
    
    log_info "Emergency shutdown completed in ${shutdown_duration} seconds"
    log_info "Services stopped: $services_stopped/${#SERVICES[@]}"
    
    if [ $services_stopped -eq ${#SERVICES[@]} ]; then
        log_success "✅ All services successfully stopped"
        return 0
    else
        log_error "❌ Some services failed to stop"
        return 1
    fi
}

# Main execution
emergency_shutdown