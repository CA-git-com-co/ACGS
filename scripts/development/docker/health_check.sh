# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# ACGS-1 Container Health Check Script
# Validates service health for containerized deployment

set -e

# Default service port (can be overridden by environment)
SERVICE_PORT=${SERVICE_PORT:-8000}
SERVICE_NAME=${SERVICE_NAME:-"acgs_service"}

# Health check endpoint
HEALTH_ENDPOINT="http://localhost:${SERVICE_PORT}/health"

# Timeout settings
TIMEOUT=10
MAX_RETRIES=3

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1"
}

print_success() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] ${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] ${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] ${RED}[ERROR]${NC} $1"
}

# Function to check service health
check_health() {
    local attempt=$1
    
    print_status "Health check attempt $attempt/$MAX_RETRIES for $SERVICE_NAME on port $SERVICE_PORT"
    
    # Use curl to check health endpoint
    if curl -f -s --connect-timeout $TIMEOUT --max-time $TIMEOUT "$HEALTH_ENDPOINT" > /dev/null 2>&1; then
        print_success "$SERVICE_NAME health check passed"
        return 0
    else
        print_warning "$SERVICE_NAME health check failed (attempt $attempt/$MAX_RETRIES)"
        return 1
    fi
}

# Function to check if port is listening
check_port() {
    if netstat -tlnp 2>/dev/null | grep -q ":$SERVICE_PORT "; then
        print_status "Port $SERVICE_PORT is listening"
        return 0
    else
        print_error "Port $SERVICE_PORT is not listening"
        return 1
    fi
}

# Function to check process
check_process() {
    if pgrep -f "uvicorn.*:$SERVICE_PORT" > /dev/null 2>&1; then
        print_status "Service process is running"
        return 0
    else
        print_warning "Service process not found"
        return 1
    fi
}

# Main health check logic
main() {
    print_status "Starting health check for $SERVICE_NAME"
    
    # Check if port is listening
    if ! check_port; then
        print_error "Service port check failed"
        exit 1
    fi
    
    # Check if process is running
    check_process
    
    # Attempt health check with retries
    for attempt in $(seq 1 $MAX_RETRIES); do
        if check_health $attempt; then
            print_success "Health check completed successfully"
            exit 0
        fi
        
        if [ $attempt -lt $MAX_RETRIES ]; then
            print_status "Waiting 2 seconds before retry..."
            sleep 2
        fi
    done
    
    print_error "Health check failed after $MAX_RETRIES attempts"
    exit 1
}

# Execute main function
main "$@"
