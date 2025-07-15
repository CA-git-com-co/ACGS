# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash
#
# ACGS Enterprise Monitoring Stack Startup Script
#
# This script starts the complete enterprise monitoring infrastructure including
# Prometheus, Grafana, Alertmanager, and deploys the enterprise dashboard.
#

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MONITORING_DIR="$PROJECT_ROOT/infrastructure/docker"
COMPOSE_FILE="$MONITORING_DIR/docker-compose-monitoring.yml"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    # Check if compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        log_error "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    local dirs=(
        "$PROJECT_ROOT/infrastructure/monitoring/config"
        "$PROJECT_ROOT/infrastructure/monitoring/rules"
        "$PROJECT_ROOT/infrastructure/monitoring/grafana/provisioning/datasources"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        "$PROJECT_ROOT/infrastructure/monitoring/grafana/provisioning/dashboards"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        "$PROJECT_ROOT/data/prometheus"
        "$PROJECT_ROOT/data/grafana"
        "$PROJECT_ROOT/data/alertmanager"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        log_info "Created directory: $dir"
    done
    
    log_success "Directories created successfully"
}

# Start monitoring stack
start_monitoring_stack() {
    log_info "Starting ACGS Enterprise Monitoring Stack..."
    
    cd "$MONITORING_DIR"
    
    # Stop any existing containers
    log_info "Stopping existing monitoring containers..."
    docker-compose -f docker-compose-monitoring.yml down 2>/dev/null || true
    
    # Start the monitoring stack
    log_info "Starting monitoring services..."
    if docker-compose -f docker-compose-monitoring.yml up -d; then
        log_success "Monitoring stack started successfully"
    else
        log_error "Failed to start monitoring stack"
        exit 1
    fi
}

# Wait for services to be ready
wait_for_services() {
    log_info "Waiting for services to be ready..."
    
    local services=(
        "prometheus:9090"
        "grafana:3001"
        "alertmanager:9093"
    )
    
    for service in "${services[@]}"; do
        local name="${service%:*}"
        local port="${service#*:}"
        
        log_info "Waiting for $name to be ready on port $port..."
        
        local max_attempts=30
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if curl -s "http://localhost:$port" > /dev/null 2>&1; then
                log_success "$name is ready"
                break
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                log_error "$name failed to start within timeout"
                return 1
            fi
            
            sleep 2
            ((attempt++))
        done
    done
    
    log_success "All services are ready"
}

# Deploy enterprise dashboard
deploy_dashboard() {
    log_info "Deploying enterprise monitoring dashboard..."
    
    local dashboard_script="$PROJECT_ROOT/scripts/monitoring/deploy_enterprise_dashboard.py"
    
    if [ -f "$dashboard_script" ]; then
        if python3 "$dashboard_script"; then
            log_success "Enterprise dashboard deployed successfully"
        else
            log_warning "Dashboard deployment failed, but monitoring stack is running"
        fi
    else
        log_warning "Dashboard deployment script not found: $dashboard_script"
    fi
}

# Display service URLs
display_service_urls() {
    log_info "Enterprise Monitoring Stack is now running!"
    echo ""
    echo "🔗 Service URLs:"
    echo "  📊 Prometheus:    http://localhost:9090"
    echo "  📈 Grafana:       http://localhost:3001 (admin/admin123)"
    echo "  🚨 Alertmanager:  http://localhost:9093"
    echo ""
    echo "📋 Key Metrics Monitored:"
    echo "  🎯 P99 Latency (Target: <5ms)"
    echo "  💾 Cache Hit Rate (Target: >85%)"
    echo "  🏛️ Constitutional Compliance"
    echo "  🚀 Throughput (Target: >100 RPS)"
    echo "  ⚡ Service Health & Availability"
    echo ""
    echo "📊 Enterprise Dashboard: http://localhost:3001/d/acgs-enterprise"
    echo ""
}

# Check service status
check_service_status() {
    log_info "Checking service status..."
    
    cd "$MONITORING_DIR"
    docker-compose -f docker-compose-monitoring.yml ps
}

# Main function
main() {
    echo "🚀 ACGS Enterprise Monitoring Stack Startup"
    echo "==========================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo ""
    
    check_prerequisites
    create_directories
    start_monitoring_stack
    
    if wait_for_services; then
        deploy_dashboard
        display_service_urls
        check_service_status
        
        log_success "Enterprise monitoring stack startup completed successfully!"
        echo ""
        log_info "To stop the monitoring stack, run:"
        log_info "  cd $MONITORING_DIR && docker-compose -f docker-compose-monitoring.yml down"
        
        return 0
    else
        log_error "Service startup failed"
        return 1
    fi
}

# Handle script arguments
case "${1:-start}" in
    "start")
        main
        ;;
    "stop")
        log_info "Stopping ACGS Enterprise Monitoring Stack..."
        cd "$MONITORING_DIR"
        docker-compose -f docker-compose-monitoring.yml down
        log_success "Monitoring stack stopped"
        ;;
    "restart")
        log_info "Restarting ACGS Enterprise Monitoring Stack..."
        cd "$MONITORING_DIR"
        docker-compose -f docker-compose-monitoring.yml down
        sleep 2
        main
        ;;
    "status")
        check_service_status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the enterprise monitoring stack (default)"
        echo "  stop    - Stop the monitoring stack"
        echo "  restart - Restart the monitoring stack"
        echo "  status  - Check service status"
        exit 1
        ;;
esac
