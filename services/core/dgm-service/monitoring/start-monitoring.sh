#!/bin/bash

# DGM Service Monitoring Stack Startup Script
# Starts Prometheus, Alertmanager, Grafana, and related monitoring services

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.monitoring.yml"
ENV_FILE="$SCRIPT_DIR/.env"

# Functions
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

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

create_env_file() {
    if [[ ! -f "$ENV_FILE" ]]; then
        log_info "Creating environment file..."
        cat > "$ENV_FILE" << EOF
# DGM Service Monitoring Environment Variables

# Database Configuration
POSTGRES_DB=dgm_db
POSTGRES_USER=dgm_user
POSTGRES_PASSWORD=dgm_secure_password_$(openssl rand -hex 8)

# Redis Configuration
REDIS_PASSWORD=redis_secure_password_$(openssl rand -hex 8)

# Grafana Configuration
GRAFANA_ADMIN_PASSWORD=admin_secure_password_$(openssl rand -hex 8)

# Alerting Configuration
SMTP_PASSWORD=your_smtp_password_here
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
PAGERDUTY_ROUTING_KEY=your_pagerduty_routing_key_here

# Monitoring Configuration
PROMETHEUS_RETENTION_TIME=30d
PROMETHEUS_RETENTION_SIZE=10GB
ALERTMANAGER_RETENTION=120h
EOF
        log_success "Environment file created at $ENV_FILE"
        log_warning "Please update the environment variables in $ENV_FILE before starting the services"
    else
        log_info "Environment file already exists"
    fi
}

create_directories() {
    log_info "Creating necessary directories..."
    
    local dirs=(
        "$SCRIPT_DIR/grafana/provisioning/datasources"
        "$SCRIPT_DIR/grafana/provisioning/dashboards"
        "$SCRIPT_DIR/grafana/dashboards"
        "$SCRIPT_DIR/templates"
        "$SCRIPT_DIR/data/prometheus"
        "$SCRIPT_DIR/data/grafana"
        "$SCRIPT_DIR/data/alertmanager"
        "$SCRIPT_DIR/data/loki"
    )
    
    for dir in "${dirs[@]}"; do
        mkdir -p "$dir"
        log_info "Created directory: $dir"
    done
    
    log_success "Directories created successfully"
}

validate_config_files() {
    log_info "Validating configuration files..."
    
    local required_files=(
        "$SCRIPT_DIR/prometheus-dgm.yml"
        "$SCRIPT_DIR/alert_rules.yml"
        "$SCRIPT_DIR/alertmanager.yml"
        "$SCRIPT_DIR/blackbox.yml"
    )
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "Required configuration file not found: $file"
            exit 1
        fi
        log_info "Found configuration file: $(basename "$file")"
    done
    
    # Validate Prometheus config
    if command -v promtool &> /dev/null; then
        log_info "Validating Prometheus configuration..."
        if promtool check config "$SCRIPT_DIR/prometheus-dgm.yml"; then
            log_success "Prometheus configuration is valid"
        else
            log_error "Prometheus configuration validation failed"
            exit 1
        fi
        
        log_info "Validating alert rules..."
        if promtool check rules "$SCRIPT_DIR/alert_rules.yml"; then
            log_success "Alert rules are valid"
        else
            log_error "Alert rules validation failed"
            exit 1
        fi
    else
        log_warning "promtool not found, skipping Prometheus config validation"
    fi
    
    log_success "Configuration validation completed"
}

create_networks() {
    log_info "Creating Docker networks..."
    
    # Create ACGS network if it doesn't exist
    if ! docker network ls | grep -q "acgs-network"; then
        docker network create acgs-network
        log_success "Created acgs-network"
    else
        log_info "acgs-network already exists"
    fi
    
    # Create DGM monitoring network if it doesn't exist
    if ! docker network ls | grep -q "dgm-monitoring"; then
        docker network create dgm-monitoring
        log_success "Created dgm-monitoring network"
    else
        log_info "dgm-monitoring network already exists"
    fi
}

start_services() {
    log_info "Starting DGM monitoring services..."
    
    # Pull latest images
    log_info "Pulling latest Docker images..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" pull
    
    # Start services
    log_info "Starting services in background..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    
    log_success "DGM monitoring services started successfully"
}

wait_for_services() {
    log_info "Waiting for services to become healthy..."
    
    local services=(
        "dgm-prometheus:9091"
        "dgm-alertmanager:9093"
        "dgm-grafana:3000"
    )
    
    for service in "${services[@]}"; do
        local name="${service%:*}"
        local port="${service#*:}"
        
        log_info "Waiting for $name to be ready..."
        local retries=30
        while [[ $retries -gt 0 ]]; do
            if curl -s "http://localhost:$port" > /dev/null 2>&1; then
                log_success "$name is ready"
                break
            fi
            ((retries--))
            sleep 2
        done
        
        if [[ $retries -eq 0 ]]; then
            log_warning "$name may not be ready yet"
        fi
    done
}

show_service_info() {
    log_info "DGM Monitoring Services Information:"
    echo
    echo -e "${GREEN}Prometheus:${NC}     http://localhost:9091"
    echo -e "${GREEN}Alertmanager:${NC}   http://localhost:9093"
    echo -e "${GREEN}Grafana:${NC}       http://localhost:3000"
    echo
    echo -e "${YELLOW}Default Grafana credentials:${NC}"
    echo -e "  Username: admin"
    echo -e "  Password: Check .env file for GRAFANA_ADMIN_PASSWORD"
    echo
    echo -e "${BLUE}To stop services:${NC}"
    echo -e "  docker-compose -f $COMPOSE_FILE down"
    echo
    echo -e "${BLUE}To view logs:${NC}"
    echo -e "  docker-compose -f $COMPOSE_FILE logs -f [service_name]"
    echo
}

# Main execution
main() {
    log_info "Starting DGM Service Monitoring Stack..."
    
    check_prerequisites
    create_env_file
    create_directories
    validate_config_files
    create_networks
    start_services
    wait_for_services
    show_service_info
    
    log_success "DGM monitoring stack is now running!"
}

# Handle script arguments
case "${1:-start}" in
    start)
        main
        ;;
    stop)
        log_info "Stopping DGM monitoring services..."
        docker-compose -f "$COMPOSE_FILE" down
        log_success "Services stopped"
        ;;
    restart)
        log_info "Restarting DGM monitoring services..."
        docker-compose -f "$COMPOSE_FILE" down
        sleep 5
        main
        ;;
    status)
        log_info "DGM monitoring services status:"
        docker-compose -f "$COMPOSE_FILE" ps
        ;;
    logs)
        docker-compose -f "$COMPOSE_FILE" logs -f "${2:-}"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs [service_name]}"
        exit 1
        ;;
esac
