#!/bin/bash

# ACGS-PGP v8 Deployment Script
# Deploys the ACGS-PGP v8 service with comprehensive validation and monitoring

set -euo pipefail

# Configuration
SERVICE_NAME="acgs-pgp-v8"
SERVICE_PORT="8010"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
DOCKER_IMAGE="acgs-pgp-v8"
HEALTH_CHECK_TIMEOUT=60
DEPLOYMENT_TIMEOUT=300

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

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Validate prerequisites
validate_prerequisites() {
    log_info "Validating prerequisites..."
    
    # Check required commands
    local required_commands=("docker" "curl" "jq")
    for cmd in "${required_commands[@]}"; do
        if ! command_exists "$cmd"; then
            log_error "Required command '$cmd' not found"
            exit 1
        fi
    done
    
    # Check Docker daemon
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker daemon is not running"
        exit 1
    fi
    
    log_success "Prerequisites validated"
}

# Check dependencies
check_dependencies() {
    log_info "Checking ACGS-1 service dependencies..."
    
    local services=(
        "8000:Auth Service"
        "8004:GS Service"
        "8005:PGC Service"
    )
    
    local failed_services=()
    
    for service in "${services[@]}"; do
        local port="${service%%:*}"
        local name="${service##*:}"
        
        if curl -s -f "http://localhost:${port}/health" >/dev/null; then
            log_success "$name (port $port) is healthy"
        else
            log_warning "$name (port $port) is not responding"
            failed_services+=("$name")
        fi
    done
    
    if [ ${#failed_services[@]} -gt 0 ]; then
        log_warning "Some dependencies are not healthy: ${failed_services[*]}"
        log_warning "Deployment will continue but service may not function properly"
    fi
}

# Check database connectivity
check_database() {
    log_info "Checking database connectivity..."
    
    local db_url="${DATABASE_URL:-postgresql://acgs_user:acgs_password@localhost:5432/acgs_db}"
    
    if command_exists psql; then
        if psql "$db_url" -c "SELECT 1;" >/dev/null 2>&1; then
            log_success "Database connection successful"
        else
            log_error "Database connection failed"
            exit 1
        fi
    else
        log_warning "psql not available, skipping database check"
    fi
}

# Check Redis connectivity
check_redis() {
    log_info "Checking Redis connectivity..."
    
    if command_exists redis-cli; then
        if redis-cli ping >/dev/null 2>&1; then
            log_success "Redis connection successful"
        else
            log_error "Redis connection failed"
            exit 1
        fi
    else
        log_warning "redis-cli not available, skipping Redis check"
    fi
}

# Build Docker image
build_image() {
    log_info "Building Docker image..."
    
    local build_args=""
    if [ -n "${CONSTITUTIONAL_HASH:-}" ]; then
        build_args="--build-arg CONSTITUTIONAL_HASH=$CONSTITUTIONAL_HASH"
    fi
    
    if docker build $build_args -t "$DOCKER_IMAGE:latest" .; then
        log_success "Docker image built successfully"
    else
        log_error "Docker image build failed"
        exit 1
    fi
}

# Stop existing container
stop_existing_container() {
    log_info "Stopping existing container..."
    
    if docker ps -q -f name="$SERVICE_NAME" | grep -q .; then
        docker stop "$SERVICE_NAME" >/dev/null 2>&1 || true
        docker rm "$SERVICE_NAME" >/dev/null 2>&1 || true
        log_success "Existing container stopped and removed"
    else
        log_info "No existing container found"
    fi
}

# Deploy new container
deploy_container() {
    log_info "Deploying new container..."
    
    local env_vars=(
        "-e DATABASE_URL=${DATABASE_URL:-postgresql://acgs_user:acgs_password@localhost:5432/acgs_db}"
        "-e REDIS_URL=${REDIS_URL:-redis://localhost:6379/0}"
        "-e CONSTITUTIONAL_HASH=$CONSTITUTIONAL_HASH"
        "-e GS_SERVICE_URL=${GS_SERVICE_URL:-http://localhost:8004}"
        "-e PGC_SERVICE_URL=${PGC_SERVICE_URL:-http://localhost:8005}"
        "-e AUTH_SERVICE_URL=${AUTH_SERVICE_URL:-http://localhost:8000}"
        "-e JWT_SECRET_KEY=${JWT_SECRET_KEY:-acgs-pgp-v8-secret-key-2024}"
    )
    
    if docker run -d \
        --name "$SERVICE_NAME" \
        -p "$SERVICE_PORT:$SERVICE_PORT" \
        --restart unless-stopped \
        "${env_vars[@]}" \
        "$DOCKER_IMAGE:latest"; then
        log_success "Container deployed successfully"
    else
        log_error "Container deployment failed"
        exit 1
    fi
}

# Wait for service to be healthy
wait_for_health() {
    log_info "Waiting for service to become healthy..."
    
    local start_time=$(date +%s)
    local timeout=$HEALTH_CHECK_TIMEOUT
    
    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [ $elapsed -gt $timeout ]; then
            log_error "Health check timeout after ${timeout}s"
            return 1
        fi
        
        if curl -s -f "http://localhost:$SERVICE_PORT/health" >/dev/null 2>&1; then
            log_success "Service is healthy"
            return 0
        fi
        
        log_info "Waiting for service... (${elapsed}s/${timeout}s)"
        sleep 5
    done
}

# Validate deployment
validate_deployment() {
    log_info "Validating deployment..."
    
    # Health check
    local health_response
    if health_response=$(curl -s "http://localhost:$SERVICE_PORT/health"); then
        local status=$(echo "$health_response" | jq -r '.status // "unknown"')
        local constitutional_hash=$(echo "$health_response" | jq -r '.constitutional_hash // "unknown"')
        
        if [ "$status" = "healthy" ]; then
            log_success "Health check passed"
        else
            log_error "Health check failed: status=$status"
            return 1
        fi
        
        if [ "$constitutional_hash" = "$CONSTITUTIONAL_HASH" ]; then
            log_success "Constitutional hash validated"
        else
            log_error "Constitutional hash mismatch: expected=$CONSTITUTIONAL_HASH, actual=$constitutional_hash"
            return 1
        fi
    else
        log_error "Health check request failed"
        return 1
    fi
    
    # Metrics check
    if curl -s "http://localhost:$SERVICE_PORT/metrics" | grep -q "acgs_pgp_v8_system_uptime_seconds"; then
        log_success "Metrics endpoint validated"
    else
        log_error "Metrics endpoint validation failed"
        return 1
    fi
    
    # System status check
    if curl -s "http://localhost:$SERVICE_PORT/api/v1/status" >/dev/null 2>&1; then
        log_success "System status endpoint validated"
    else
        log_warning "System status endpoint not accessible (may require authentication)"
    fi
}

# Run monitoring integration test
run_monitoring_test() {
    log_info "Running monitoring integration test..."
    
    if [ -f "test_monitoring_integration.py" ]; then
        if python test_monitoring_integration.py; then
            log_success "Monitoring integration test passed"
        else
            log_warning "Monitoring integration test failed (non-critical)"
        fi
    else
        log_warning "Monitoring integration test not found"
    fi
}

# Display deployment summary
display_summary() {
    log_info "Deployment Summary:"
    echo "===================="
    echo "Service: $SERVICE_NAME"
    echo "Port: $SERVICE_PORT"
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "Docker Image: $DOCKER_IMAGE:latest"
    echo "Health Check: http://localhost:$SERVICE_PORT/health"
    echo "Metrics: http://localhost:$SERVICE_PORT/metrics"
    echo "API Documentation: docs/API_DOCUMENTATION.md"
    echo "Operational Runbook: docs/OPERATIONAL_RUNBOOK.md"
    echo "===================="
}

# Rollback function
rollback() {
    log_error "Deployment failed, initiating rollback..."
    
    # Stop failed container
    docker stop "$SERVICE_NAME" >/dev/null 2>&1 || true
    docker rm "$SERVICE_NAME" >/dev/null 2>&1 || true
    
    # Try to restore previous version if available
    if docker images | grep -q "$DOCKER_IMAGE:previous"; then
        log_info "Restoring previous version..."
        docker run -d \
            --name "$SERVICE_NAME" \
            -p "$SERVICE_PORT:$SERVICE_PORT" \
            --restart unless-stopped \
            "$DOCKER_IMAGE:previous"
        
        if wait_for_health; then
            log_success "Rollback successful"
        else
            log_error "Rollback failed"
        fi
    else
        log_warning "No previous version available for rollback"
    fi
}

# Main deployment function
main() {
    log_info "Starting ACGS-PGP v8 deployment..."
    
    # Trap errors for rollback
    trap rollback ERR
    
    # Deployment steps
    validate_prerequisites
    check_dependencies
    check_database
    check_redis
    
    # Tag current image as previous (if exists)
    if docker images | grep -q "$DOCKER_IMAGE:latest"; then
        docker tag "$DOCKER_IMAGE:latest" "$DOCKER_IMAGE:previous" >/dev/null 2>&1 || true
    fi
    
    build_image
    stop_existing_container
    deploy_container
    
    if wait_for_health; then
        validate_deployment
        run_monitoring_test
        display_summary
        log_success "ACGS-PGP v8 deployment completed successfully!"
    else
        log_error "Deployment validation failed"
        exit 1
    fi
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "rollback")
        rollback
        ;;
    "health")
        curl -s "http://localhost:$SERVICE_PORT/health" | jq .
        ;;
    "logs")
        docker logs -f "$SERVICE_NAME"
        ;;
    "stop")
        stop_existing_container
        ;;
    *)
        echo "Usage: $0 {deploy|rollback|health|logs|stop}"
        exit 1
        ;;
esac
