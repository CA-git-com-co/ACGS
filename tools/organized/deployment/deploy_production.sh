#!/bin/bash
set -e

# ACGS-1 Production Deployment Script
# Phase 3 - Production Environment Setup and Deployment

echo "🚀 ACGS-1 Production Deployment Script"
echo "======================================="

# Configuration
DEPLOYMENT_VERSION=${DEPLOYMENT_VERSION:-"1.0.0"}
DEPLOYMENT_TIMESTAMP=$(date -u +"%Y%m%d_%H%M%S")
GIT_COMMIT_HASH=$(git rev-parse --short HEAD 2>/dev/null || echo "unknown")
BUILD_NUMBER=${BUILD_NUMBER:-"local"}

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
    
    # Check if Docker is installed and running
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is available
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    
    # Check if required environment files exist
    if [ ! -f "config/environments/production.env" ]; then
        log_error "Production environment file not found: config/environments/production.env"
        exit 1
    fi
    
    if [ ! -f "docker-compose.production.yml" ]; then
        log_error "Production Docker Compose file not found: docker-compose.production.yml"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Generate secrets if they don't exist
generate_secrets() {
    log_info "Generating production secrets..."
    
    SECRETS_FILE="config/production.secrets"
    
    if [ ! -f "$SECRETS_FILE" ]; then
        log_info "Creating new secrets file..."
        
        # Generate random secrets
        SECRET_KEY=$(openssl rand -hex 32)
        JWT_SECRET_KEY=$(openssl rand -hex 32)
        ENCRYPTION_KEY=$(openssl rand -hex 32)
        POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        REDIS_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
        GRAFANA_ADMIN_PASSWORD=$(openssl rand -base64 16 | tr -d "=+/" | cut -c1-12)
        
        # Create secrets file
        cat > "$SECRETS_FILE" << EOF
# ACGS-1 Production Secrets
# Generated on: $(date -u)
# WARNING: Keep this file secure and never commit to version control

SECRET_KEY=$SECRET_KEY
JWT_SECRET_KEY=$JWT_SECRET_KEY
ENCRYPTION_KEY=$ENCRYPTION_KEY
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
REDIS_PASSWORD=$REDIS_PASSWORD
GRAFANA_ADMIN_PASSWORD=$GRAFANA_ADMIN_PASSWORD

# Deployment Information
DEPLOYMENT_VERSION=$DEPLOYMENT_VERSION
DEPLOYMENT_TIMESTAMP=$DEPLOYMENT_TIMESTAMP
GIT_COMMIT_HASH=$GIT_COMMIT_HASH
BUILD_NUMBER=$BUILD_NUMBER
EOF
        
        chmod 600 "$SECRETS_FILE"
        log_success "Secrets generated and saved to $SECRETS_FILE"
    else
        log_info "Using existing secrets from $SECRETS_FILE"
    fi
    
    # Export secrets for Docker Compose
    set -a
    source "$SECRETS_FILE"
    set +a
}

# Create necessary directories
create_directories() {
    log_info "Creating necessary directories..."
    
    mkdir -p logs/nginx
    mkdir -p logs/services
    mkdir -p config/nginx/ssl
    mkdir -p config/postgres
    mkdir -p config/redis
    mkdir -p config/prometheus
    mkdir -p config/grafana/provisioning
    mkdir -p data/postgres
    mkdir -p data/redis
    mkdir -p data/prometheus
    mkdir -p data/grafana
    mkdir -p backups
    
    log_success "Directories created"
}

# Setup SSL certificates (self-signed for development)
setup_ssl() {
    log_info "Setting up SSL certificates..."
    
    SSL_DIR="config/nginx/ssl"
    
    if [ ! -f "$SSL_DIR/acgs.crt" ] || [ ! -f "$SSL_DIR/acgs.key" ]; then
        log_info "Generating self-signed SSL certificates..."
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout "$SSL_DIR/acgs.key" \
            -out "$SSL_DIR/acgs.crt" \
            -subj "/C=US/ST=CA/L=San Francisco/O=ACGS/OU=IT Department/CN=acgs.local"
        
        chmod 600 "$SSL_DIR/acgs.key"
        chmod 644 "$SSL_DIR/acgs.crt"
        
        log_success "SSL certificates generated"
    else
        log_info "Using existing SSL certificates"
    fi
}

# Build Docker images
build_images() {
    log_info "Building Docker images..."
    
    # Use Docker Compose to build all services
    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.production.yml build --parallel
    else
        docker compose -f docker-compose.production.yml build --parallel
    fi
    
    log_success "Docker images built successfully"
}

# Deploy services
deploy_services() {
    log_info "Deploying ACGS-1 services..."
    
    # Stop any existing services
    log_info "Stopping existing services..."
    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.production.yml down --remove-orphans || true
    else
        docker compose -f docker-compose.production.yml down --remove-orphans || true
    fi
    
    # Start services
    log_info "Starting production services..."
    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.production.yml up -d
    else
        docker compose -f docker-compose.production.yml up -d
    fi
    
    log_success "Services deployed successfully"
}

# Wait for services to be healthy
wait_for_services() {
    log_info "Waiting for services to become healthy..."
    
    # Wait for database to be ready
    log_info "Waiting for PostgreSQL..."
    timeout 60 bash -c 'until docker exec acgs-postgres-prod pg_isready -U acgs_user -d acgs_production; do sleep 2; done'
    
    # Wait for Redis to be ready
    log_info "Waiting for Redis..."
    timeout 60 bash -c 'until docker exec acgs-redis-prod redis-cli ping; do sleep 2; done'
    
    # Wait for core services
    services=("auth-service:8000" "ac-service:8001" "integrity-service:8002" "fv-service:8003" "gs-service:8004" "pgc-service:8005" "ec-service:8006")
    
    for service in "${services[@]}"; do
        service_name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        log_info "Waiting for $service_name on port $port..."
        timeout 120 bash -c "until curl -f http://localhost:$port/health &>/dev/null; do sleep 5; done"
    done
    
    log_success "All services are healthy"
}

# Run validation tests
run_validation() {
    log_info "Running production validation tests..."
    
    # Run service validation
    if python3 scripts/validate_services.py; then
        log_success "Service validation passed"
    else
        log_error "Service validation failed"
        return 1
    fi
    
    # Run workflow validation
    if python3 scripts/validate_workflows.py; then
        log_success "Workflow validation passed"
    else
        log_error "Workflow validation failed"
        return 1
    fi
    
    log_success "All validation tests passed"
}

# Show deployment status
show_status() {
    log_info "Deployment Status:"
    echo "=================="
    
    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.production.yml ps
    else
        docker compose -f docker-compose.production.yml ps
    fi
    
    echo ""
    log_info "Service URLs:"
    echo "  Auth Service:        http://localhost:8000"
    echo "  Constitutional AI:   http://localhost:8001"
    echo "  Integrity Service:   http://localhost:8002"
    echo "  Formal Verification: http://localhost:8003"
    echo "  Governance Synthesis: http://localhost:8004"
    echo "  Policy Governance:   http://localhost:8005"
    echo "  Evolutionary Comp:   http://localhost:8006"
    echo "  Prometheus:          http://localhost:9090"
    echo "  Grafana:             http://localhost:3000"
    echo ""
    log_info "Deployment completed successfully!"
    log_info "Version: $DEPLOYMENT_VERSION"
    log_info "Timestamp: $DEPLOYMENT_TIMESTAMP"
    log_info "Git Commit: $GIT_COMMIT_HASH"
}

# Main deployment function
main() {
    log_info "Starting ACGS-1 production deployment..."
    
    check_prerequisites
    generate_secrets
    create_directories
    setup_ssl
    build_images
    deploy_services
    wait_for_services
    run_validation
    show_status
    
    log_success "🎉 ACGS-1 production deployment completed successfully!"
}

# Handle script arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "stop")
        log_info "Stopping ACGS-1 services..."
        if command -v docker-compose &> /dev/null; then
            docker-compose -f docker-compose.production.yml down
        else
            docker compose -f docker-compose.production.yml down
        fi
        log_success "Services stopped"
        ;;
    "status")
        show_status
        ;;
    "logs")
        if command -v docker-compose &> /dev/null; then
            docker-compose -f docker-compose.production.yml logs -f
        else
            docker compose -f docker-compose.production.yml logs -f
        fi
        ;;
    *)
        echo "Usage: $0 {deploy|stop|status|logs}"
        echo "  deploy - Deploy ACGS-1 to production"
        echo "  stop   - Stop all services"
        echo "  status - Show deployment status"
        echo "  logs   - Show service logs"
        exit 1
        ;;
esac
