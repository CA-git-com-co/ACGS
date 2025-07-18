# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash
# ACGS-1 Development Environment Startup Script
# This script starts all development services for the ACGS-1 Constitutional Governance System

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
}

# Project configuration
PROJECT_ROOT="/home/ubuntu/ACGS"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/pids"

# Create necessary directories
create_directories() {
    log "📁 Creating necessary directories..."
    mkdir -p "$LOG_DIR" "$PID_DIR"
    success "Directories created"
}

# Check if virtual environment is activated
check_virtual_env() {
    log "🐍 Checking Python virtual environment..."
    
    if [ ! -d "venv" ]; then
        error "Virtual environment not found. Please run ./scripts/setup/install_dependencies.sh first"
        exit 1
    fi
    
    if [ -z "$VIRTUAL_ENV" ]; then
        log "Activating virtual environment..."
        source venv/bin/activate
        success "Virtual environment activated"
    else
        log "Virtual environment already active: $VIRTUAL_ENV"
    fi
}

# Setup environment variables
setup_environment() {
    log "🔧 Setting up environment variables..."
    
    # Load environment variables if config/environments/development.env file exists
    if [ -f "config/env/config/environments/development.env" ]; then
        export $(cat config/env/config/environments/development.env | grep -v '^#' | xargs)
        success "Environment variables loaded from config/env/config/environments/development.env"
    elif [ -f "config/environments/development.env" ]; then
        export $(cat config/environments/development.env | grep -v '^#' | xargs)
        success "Environment variables loaded from config/environments/development.env"
    else
        warning "No config/environments/development.env file found, using default environment"
    fi
    
    # Set default values if not provided
    export ENVIRONMENT=${ENVIRONMENT:-development}
    export DEBUG=${DEBUG:-true}
    export LOG_LEVEL=${LOG_LEVEL:-INFO}
}

# Start infrastructure services (Docker)
start_infrastructure() {
    log "🐳 Starting infrastructure services..."
    
    if command -v docker >/dev/null 2>&1 && command -v docker-compose >/dev/null 2>&1; then
        # Check if Docker is running
        if ! docker info >/dev/null 2>&1; then
            error "Docker is not running. Please start Docker and try again."
            exit 1
        fi
        
        # Start infrastructure services
        if [ -f "infrastructure/docker/docker-compose.yml" ]; then
            log "Starting services with docker-compose.yml..."
            cd infrastructure/docker
            docker-compose up -d postgres redis
            cd - > /dev/null
            success "Infrastructure services started"
        elif [ -f "infrastructure/docker/docker-compose.dev.yml" ]; then
            log "Starting services with docker-compose.dev.yml..."
            cd infrastructure/docker
            docker-compose -f config/docker/docker-compose.dev.yml up -d
            cd - > /dev/null
            success "Development infrastructure services started"
        else
            warning "No docker-compose file found, skipping infrastructure startup"
        fi
        
        # Wait for services to be ready
        log "Waiting for infrastructure services to be ready..."
        sleep 10
        
        # Check PostgreSQL
        if docker ps | grep -q postgres; then
            log "PostgreSQL container is running"
        fi
        
        # Check Redis
        if docker ps | grep -q redis; then
            log "Redis container is running"
        fi
        
    else
        warning "Docker or docker-compose not found, skipping infrastructure startup"
    fi
}

# Start backend services
start_backend_services() {
    log "🚀 Starting backend services..."
    
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
    
    local started_services=0
    
    for service_name in "${!SERVICES[@]}"; do
        IFS=':' read -r port service_path <<< "${SERVICES[$service_name]}"
        
        if [ -d "$service_path" ]; then
            log "Starting $service_name on port $port..."
            
            # Check if service has a main.py or app.py
            if [ -f "$service_path/app/main.py" ]; then
                cd "$service_path"
                nohup python -m uvicorn app.main:app --host 0.0.0.0 --port "$port" --reload > "$LOG_DIR/${service_name}.log" 2>&1 &
                echo $! > "$PID_DIR/${service_name}.pid"
                cd - > /dev/null
                ((started_services++))
                log "$service_name started (PID: $(cat $PID_DIR/${service_name}.pid))"
            elif [ -f "$service_path/main.py" ]; then
                cd "$service_path"
                nohup python main.py --port "$port" > "$LOG_DIR/${service_name}.log" 2>&1 &
                echo $! > "$PID_DIR/${service_name}.pid"
                cd - > /dev/null
                ((started_services++))
                log "$service_name started (PID: $(cat $PID_DIR/${service_name}.pid))"
            else
                warning "$service_name: No main.py or app/main.py found in $service_path"
            fi
        else
            warning "$service_name: Directory $service_path not found"
        fi
    done
    
    success "Backend services startup complete ($started_services services started)"
}

# Start frontend applications
start_frontend_applications() {
    log "🌐 Starting frontend applications..."
    
    local started_apps=0
    
    # Start governance dashboard
    if [ -d "applications/governance-dashboard" ] && [ -f "applications/governance-dashboard/package.json" ]; then
        log "Starting governance dashboard..."
        cd applications/governance-dashboard
        nohup npm start > "$LOG_DIR/governance-dashboard.log" 2>&1 &
        echo $! > "$PID_DIR/governance-dashboard.pid"
        cd - > /dev/null
        ((started_apps++))
        log "Governance dashboard started (PID: $(cat $PID_DIR/governance-dashboard.pid))"
    else
        warning "Governance dashboard not found or missing package.json"
    fi
    
    # Start constitutional council interface
    if [ -d "applications/constitutional-council" ] && [ -f "applications/constitutional-council/package.json" ]; then
        log "Starting constitutional council interface..."
        cd applications/constitutional-council
        nohup npm start > "$LOG_DIR/constitutional-council.log" 2>&1 &
        echo $! > "$PID_DIR/constitutional-council.pid"
        cd - > /dev/null
        ((started_apps++))
        log "Constitutional council interface started (PID: $(cat $PID_DIR/constitutional-council.pid))"
    else
        log "Constitutional council interface not found, skipping"
    fi
    
    success "Frontend applications startup complete ($started_apps applications started)"
}

# Run health checks
run_health_checks() {
    log "🔍 Running health checks..."
    
    # Wait a moment for services to fully start
    sleep 5
    
    # Check infrastructure services
    log "Checking infrastructure services..."
    
    # Check PostgreSQL
    if command -v pg_isready >/dev/null 2>&1; then
        if pg_isready -h localhost -p 5432 >/dev/null 2>&1; then
            success "PostgreSQL is ready"
        else
            warning "PostgreSQL is not ready"
        fi
    fi
    
    # Check Redis
    if command -v redis-cli >/dev/null 2>&1; then
        if redis-cli ping 2>/dev/null | grep -q "PONG"; then
            success "Redis is ready"
        else
            warning "Redis is not ready"
        fi
    fi
    
    # Check backend services
    log "Checking backend services..."
    local healthy_services=0
    
    for port in 8000 8001 8002 8003 8004 8005 8006; do
        if curl -s -f "http://localhost:$port/health" >/dev/null 2>&1; then
            success "Service on port $port is healthy"
            ((healthy_services++))
        elif curl -s -f "http://localhost:$port/" >/dev/null 2>&1; then
            log "Service on port $port is responding (no health endpoint)"
            ((healthy_services++))
        else
            warning "Service on port $port is not responding"
        fi
    done
    
    success "Health checks complete ($healthy_services backend services healthy)"
}

# Display service status
display_status() {
    echo ""
    echo "=============================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "🎉 DEVELOPMENT ENVIRONMENT STARTED"
    echo "=============================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo ""
    echo "📋 Service Status:"
    
    # Infrastructure services
    echo "  🐳 Infrastructure:"
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(postgres|redis)" >/dev/null 2>&1; then
        docker ps --format "    ✅ {{.Names}}: {{.Status}}" | grep -E "(postgres|redis)"
    else
        echo "    ⚠️  No infrastructure containers running"
    fi
    
    # Backend services
    echo "  🚀 Backend Services:"
    for pid_file in "$PID_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            service_name=$(basename "$pid_file" .pid)
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                echo "    ✅ $service_name (PID: $pid)"
            else
                echo "    ❌ $service_name (PID: $pid - not running)"
            fi
        fi
    done
    
    echo ""
    echo "🌐 Access URLs:"
    echo "  • Governance Dashboard: http://localhost:3000"
    echo "  • Constitutional AI Service: http://localhost:8001"
    echo "  • Authentication Service: http://localhost:8000"
    echo "  • Integrity Service: http://localhost:8002"
    echo "  • Formal Verification Service: http://localhost:8003"
    echo "  • Governance Synthesis Service: http://localhost:8004"
    echo "  • Policy Governance Service: http://localhost:8005"
    echo "  • Evolutionary Computation Service: http://localhost:8006"
    echo ""
    echo "📁 Logs Directory: $LOG_DIR"
    echo "📁 PID Directory: $PID_DIR"
    echo ""
    echo "🛑 To stop all services, run: ./scripts/stop_all_services.sh"
    echo "🔍 To check service health, run: ./scripts/health_check_all_services.sh"
}

# Main startup function
main() {
    log "🚀 Starting ACGS-1 Development Environment"
    echo "=========================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    
    # Run startup steps
    create_directories
    check_virtual_env
    setup_environment
    start_infrastructure
    start_backend_services
    start_frontend_applications
    run_health_checks
    display_status
}

# Handle script termination
cleanup() {
    log "🛑 Received termination signal, cleaning up..."
    # Note: Individual service cleanup is handled by stop_all_services.sh
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Run main function
main "$@"
