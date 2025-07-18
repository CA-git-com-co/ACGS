# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash
# ACGS-1 Monitoring Infrastructure Deployment Script
# Deploy Prometheus, Grafana, and Alertmanager with enterprise configuration

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MONITORING_DIR="$SCRIPT_DIR"
LOG_FILE="/var/log/acgs/monitoring-deployment.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo -e "${timestamp} [${level}] ${message}" | tee -a "$LOG_FILE"
}

info() {
    log "INFO" "${BLUE}$*${NC}"
}

warn() {
    log "WARN" "${YELLOW}$*${NC}"
}

error() {
    log "ERROR" "${RED}$*${NC}"
}

success() {
    log "SUCCESS" "${GREEN}$*${NC}"
}

# Check prerequisites
check_prerequisites() {
    info "Checking prerequisites..."
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    # Create log directory
    sudo mkdir -p "$(dirname "$LOG_FILE")"
    sudo touch "$LOG_FILE"
    sudo chmod 666 "$LOG_FILE"
    
    success "Prerequisites check completed"
}

# Create necessary directories
create_directories() {
    info "Creating monitoring directories..."
    
    local dirs=(
        "$MONITORING_DIR/grafana/dashboards/system-overview"
        "$MONITORING_DIR/grafana/dashboards/services"
        "$MONITORING_DIR/grafana/dashboards/governance-workflows"
        "$MONITORING_DIR/grafana/dashboards/infrastructure"
        "$MONITORING_DIR/grafana/dashboards/performance"
        "$MONITORING_DIR/grafana/dashboards/security"
        "$MONITORING_DIR/grafana/dashboards/blockchain"
        "$MONITORING_DIR/grafana/dashboards/alerting"
        "$MONITORING_DIR/grafana/dashboards/development"
        "$MONITORING_DIR/grafana/dashboards/executive"
        "$MONITORING_DIR/grafana/alerting"
        "$MONITORING_DIR/prometheus/rules"
        "$MONITORING_DIR/postgres_exporter"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        info "Created directory: $dir"
    done
    
    success "Directory structure created"
}

# Validate configuration files
validate_configs() {
    info "Validating configuration files..."
    
    # Check Prometheus configuration
    if [ -f "$MONITORING_DIR/prometheus.yml" ]; then
        if docker run --rm -v "$MONITORING_DIR/prometheus.yml:/etc/prometheus/prometheus.yml" \
           prom/prometheus:v2.40.7 promtool check config /etc/prometheus/prometheus.yml; then
            success "Prometheus configuration is valid"
        else
            error "Prometheus configuration is invalid"
            exit 1
        fi
    else
        error "Prometheus configuration file not found"
        exit 1
    fi
    
    # Check Alertmanager configuration
    if [ -f "$MONITORING_DIR/alertmanager.yml" ]; then
        if docker run --rm -v "$MONITORING_DIR/alertmanager.yml:/etc/alertmanager/alertmanager.yml" \
           prom/alertmanager:v0.25.0 amtool check-config /etc/alertmanager/alertmanager.yml; then
            success "Alertmanager configuration is valid"
        else
            error "Alertmanager configuration is invalid"
            exit 1
        fi
    else
        error "Alertmanager configuration file not found"
        exit 1
    fi
    
    # Check Docker Compose file
    if [ -f "$MONITORING_DIR/docker-compose.monitoring.yml" ]; then
        if docker-compose -f "$MONITORING_DIR/docker-compose.monitoring.yml" config > /dev/null; then
            success "Docker Compose configuration is valid"
        else
            error "Docker Compose configuration is invalid"
            exit 1
        fi
    else
        error "Docker Compose file not found"
        exit 1
    fi
}

# Deploy monitoring stack
deploy_monitoring() {
    info "Deploying ACGS-1 monitoring stack..."
    
    cd "$MONITORING_DIR"
    
    # Pull latest images
    info "Pulling Docker images..."
    docker-compose -f config/docker/docker-compose.monitoring.yml pull
    
    # Start monitoring services
    info "Starting monitoring services..."
    docker-compose -f config/docker/docker-compose.monitoring.yml up -d
    
    # Wait for services to be ready
    info "Waiting for services to be ready..."
    
    local services=(
        "prometheus:9090"
        "grafana:3000"
        "alertmanager:9093"
    )
    
    for service in "${services[@]}"; do
        local name=$(echo "$service" | cut -d: -f1)
        local port=$(echo "$service" | cut -d: -f2)
        
        info "Waiting for $name to be ready on port $port..."
        
        local max_attempts=30
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if curl -s "http://localhost:$port" > /dev/null 2>&1; then
                success "$name is ready"
                break
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                error "$name failed to start within timeout"
                exit 1
            fi
            
            sleep 10
            ((attempt++))
        done
    done
    
    success "Monitoring stack deployed successfully"
}

# Configure Grafana
configure_grafana() {
    info "Configuring Grafana..."
    
    # Wait for Grafana to be fully ready
    sleep 30
    
    # Check if Grafana is accessible
    local grafana_url="http://localhost:3000"
    local admin_user="admin"
    local admin_pass="acgs_admin_2024"
    
    if curl -s -u "$admin_user:$admin_pass" "$grafana_url/api/health" | grep -q "ok"; then
        success "Grafana is accessible"
    else
        error "Grafana is not accessible"
        exit 1
    fi
    
    # Import dashboards (if any additional ones need to be imported via API)
    info "Grafana configuration completed"
}

# Verify deployment
verify_deployment() {
    info "Verifying monitoring deployment..."
    
    # Check service status
    local services=("acgs_prometheus" "acgs_grafana" "acgs_alertmanager")
    
    for service in "${services[@]}"; do
        if docker ps --filter "name=$service" --filter "status=running" | grep -q "$service"; then
            success "$service is running"
        else
            error "$service is not running"
            exit 1
        fi
    done
    
    # Check metrics collection
    info "Checking metrics collection..."
    if curl -s "http://localhost:9090/api/v1/query?query=up" | grep -q "success"; then
        success "Prometheus is collecting metrics"
    else
        warn "Prometheus metrics collection may have issues"
    fi
    
    # Check Grafana dashboards
    info "Checking Grafana dashboards..."
    if curl -s -u "admin:acgs_admin_2024" "http://localhost:3000/api/search" | grep -q "acgs"; then
        success "Grafana dashboards are available"
    else
        warn "Grafana dashboards may not be loaded yet"
    fi
    
    success "Deployment verification completed"
}

# Display access information
display_access_info() {
    info "Monitoring stack access information:"
    echo ""
    echo "🔍 Prometheus: http://localhost:9090"
    echo "📊 Grafana: http://localhost:3000 (admin/acgs_admin_2024)"
    echo "🚨 Alertmanager: http://localhost:9093"
    echo ""
    echo "📈 Key Dashboards:"
    echo "  - ACGS System Overview: http://localhost:3000/d/acgs-system-overview"
    echo "  - Service Monitoring: http://localhost:3000/dashboards/folder/acgs-services"
    echo "  - Governance Workflows: http://localhost:3000/dashboards/folder/governance-workflows"
    echo ""
    echo "🎯 Performance Targets:"
    echo "  - System Availability: >99.9%"
    echo "  - Response Time P95: <500ms"
    echo "  - Concurrent Users: >1000 capacity"
    echo "  - Constitutional Compliance: >99%"
    echo ""
}

# Main execution
main() {
    info "Starting ACGS-1 monitoring infrastructure deployment..."
    
    check_prerequisites
    create_directories
    validate_configs
    deploy_monitoring
    configure_grafana
    verify_deployment
    display_access_info
    
    success "ACGS-1 monitoring infrastructure deployment completed successfully!"
    info "Monitor the logs with: tail -f $LOG_FILE"
}

# Handle script interruption
trap 'error "Deployment interrupted"; exit 1' INT TERM

# Execute main function
main "$@"
