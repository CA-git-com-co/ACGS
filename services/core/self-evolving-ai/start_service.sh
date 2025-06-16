#!/bin/bash

# ACGS-1 Self-Evolving AI Architecture Foundation Service Startup Script
# This script starts the self-evolving AI service with proper configuration

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Service configuration
SERVICE_NAME="acgs-self-evolving-ai"
SERVICE_PORT=8007
SERVICE_HOST="0.0.0.0"
LOG_DIR="logs"
PID_DIR="pids"
CONFIG_FILE=".env"

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

# Function to check if service is running
is_service_running() {
    if [ -f "${PID_DIR}/${SERVICE_NAME}.pid" ]; then
        local pid=$(cat "${PID_DIR}/${SERVICE_NAME}.pid")
        if ps -p $pid > /dev/null 2>&1; then
            return 0
        else
            rm -f "${PID_DIR}/${SERVICE_NAME}.pid"
            return 1
        fi
    fi
    return 1
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p $LOG_DIR
    mkdir -p $PID_DIR
    mkdir -p data
    mkdir -p config
    print_success "Directories created"
}

# Function to check dependencies
check_dependencies() {
    print_status "Checking dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    
    # Check pip
    if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
        print_error "pip is not installed"
        exit 1
    fi
    
    # Check if virtual environment exists
    if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
        print_warning "Virtual environment not found. Creating one..."
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        print_success "Virtual environment created and dependencies installed"
    fi
    
    print_success "Dependencies check completed"
}

# Function to setup configuration
setup_configuration() {
    print_status "Setting up configuration..."
    
    if [ ! -f "$CONFIG_FILE" ]; then
        print_status "Creating default configuration file..."
        cat > $CONFIG_FILE << EOF
# ACGS-1 Self-Evolving AI Architecture Foundation Configuration

# Service Configuration
SERVICE_NAME=acgs-self-evolving-ai
VERSION=1.0.0
HOST=0.0.0.0
PORT=8007
DEBUG=false
ENVIRONMENT=development

# Security Configuration
SECRET_KEY=acgs-self-evolving-ai-secret-key-2024
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Database Configuration
DATABASE_URL=postgresql://acgs_user:acgs_password@localhost:5432/acgs_self_evolving_ai

# Redis Configuration
REDIS_URL=redis://localhost:6379/0

# Celery Configuration
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# OPA Configuration
OPA_SERVER_URL=http://localhost:8181
OPA_BUNDLE_NAME=self_evolving_ai

# Sandboxing Configuration
SANDBOX_ENABLED=true
SANDBOX_TYPE=gvisor
RESOURCE_LIMITS_ENABLED=true

# OpenTelemetry Configuration
OPENTELEMETRY_ENABLED=true
OTLP_ENDPOINT=http://localhost:4317
TRACING_ENABLED=true
METRICS_ENABLED=true

# ACGS-1 Core Services Integration
AUTH_SERVICE_URL=http://localhost:8000
AC_SERVICE_URL=http://localhost:8001
INTEGRITY_SERVICE_URL=http://localhost:8002
FV_SERVICE_URL=http://localhost:8003
GS_SERVICE_URL=http://localhost:8004
PGC_SERVICE_URL=http://localhost:8005
EC_SERVICE_URL=http://localhost:8006

# Quantumagi Solana Integration
QUANTUMAGI_ENABLED=true
SOLANA_CLUSTER=devnet
SOLANA_RPC_URL=https://api.devnet.solana.com
CONSTITUTION_HASH=cdd01ef066bc6cf2

# Evolution Engine Configuration
EVOLUTION_ENABLED=true
MANUAL_APPROVAL_REQUIRED=true
MAX_CONCURRENT_EVOLUTIONS=5
EVOLUTION_TIMEOUT_MINUTES=10

# Performance Configuration
MAX_CONCURRENT_REQUESTS=1000
REQUEST_TIMEOUT_SECONDS=30
RESPONSE_TIME_TARGET_MS=500
AVAILABILITY_TARGET_PERCENT=99.9

# Logging Configuration
LOG_LEVEL=INFO
LOG_FILE=logs/self_evolving_ai.log
EOF
        print_success "Default configuration file created"
    else
        print_success "Configuration file already exists"
    fi
}

# Function to check external dependencies
check_external_dependencies() {
    print_status "Checking external dependencies..."
    
    # Check Redis
    if ! nc -z localhost 6379 2>/dev/null; then
        print_warning "Redis is not running on localhost:6379"
        print_status "Please start Redis or update REDIS_URL in $CONFIG_FILE"
    else
        print_success "Redis connection available"
    fi
    
    # Check PostgreSQL
    if ! nc -z localhost 5432 2>/dev/null; then
        print_warning "PostgreSQL is not running on localhost:5432"
        print_status "Please start PostgreSQL or update DATABASE_URL in $CONFIG_FILE"
    else
        print_success "PostgreSQL connection available"
    fi
    
    # Check OPA
    if ! nc -z localhost 8181 2>/dev/null; then
        print_warning "OPA is not running on localhost:8181"
        print_status "Please start OPA or update OPA_SERVER_URL in $CONFIG_FILE"
    else
        print_success "OPA connection available"
    fi
}

# Function to start the service
start_service() {
    print_status "Starting $SERVICE_NAME..."
    
    if is_service_running; then
        print_warning "Service is already running"
        return 0
    fi
    
    # Activate virtual environment if it exists
    if [ -d "venv" ]; then
        source venv/bin/activate
    elif [ -d ".venv" ]; then
        source .venv/bin/activate
    fi
    
    # Start the service
    nohup python -m app.main > "${LOG_DIR}/${SERVICE_NAME}.log" 2>&1 &
    local pid=$!
    
    # Save PID
    echo $pid > "${PID_DIR}/${SERVICE_NAME}.pid"
    
    # Wait a moment and check if service started successfully
    sleep 3
    
    if is_service_running; then
        print_success "Service started successfully (PID: $pid)"
        print_status "Service is running on http://${SERVICE_HOST}:${SERVICE_PORT}"
        print_status "Health check: http://${SERVICE_HOST}:${SERVICE_PORT}/health"
        print_status "API documentation: http://${SERVICE_HOST}:${SERVICE_PORT}/docs"
        print_status "Log file: ${LOG_DIR}/${SERVICE_NAME}.log"
    else
        print_error "Service failed to start"
        print_status "Check log file: ${LOG_DIR}/${SERVICE_NAME}.log"
        exit 1
    fi
}

# Function to stop the service
stop_service() {
    print_status "Stopping $SERVICE_NAME..."
    
    if ! is_service_running; then
        print_warning "Service is not running"
        return 0
    fi
    
    local pid=$(cat "${PID_DIR}/${SERVICE_NAME}.pid")
    kill $pid
    
    # Wait for graceful shutdown
    local count=0
    while is_service_running && [ $count -lt 30 ]; do
        sleep 1
        count=$((count + 1))
    done
    
    if is_service_running; then
        print_warning "Service did not stop gracefully, forcing shutdown..."
        kill -9 $pid
        rm -f "${PID_DIR}/${SERVICE_NAME}.pid"
    fi
    
    print_success "Service stopped"
}

# Function to restart the service
restart_service() {
    stop_service
    sleep 2
    start_service
}

# Function to show service status
show_status() {
    if is_service_running; then
        local pid=$(cat "${PID_DIR}/${SERVICE_NAME}.pid")
        print_success "Service is running (PID: $pid)"
        print_status "Service URL: http://${SERVICE_HOST}:${SERVICE_PORT}"
        
        # Try to get health status
        if command -v curl &> /dev/null; then
            print_status "Health check:"
            curl -s "http://${SERVICE_HOST}:${SERVICE_PORT}/health" | python -m json.tool 2>/dev/null || echo "Health check failed"
        fi
    else
        print_warning "Service is not running"
    fi
}

# Function to show logs
show_logs() {
    if [ -f "${LOG_DIR}/${SERVICE_NAME}.log" ]; then
        tail -f "${LOG_DIR}/${SERVICE_NAME}.log"
    else
        print_error "Log file not found: ${LOG_DIR}/${SERVICE_NAME}.log"
    fi
}

# Main script logic
case "${1:-start}" in
    start)
        create_directories
        check_dependencies
        setup_configuration
        check_external_dependencies
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    setup)
        create_directories
        check_dependencies
        setup_configuration
        print_success "Setup completed"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs|setup}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the service"
        echo "  stop    - Stop the service"
        echo "  restart - Restart the service"
        echo "  status  - Show service status"
        echo "  logs    - Show service logs (tail -f)"
        echo "  setup   - Setup directories and configuration"
        exit 1
        ;;
esac
