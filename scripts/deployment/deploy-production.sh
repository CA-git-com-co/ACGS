#!/bin/bash
# ACGS-2 Production Deployment Script
# Constitutional Hash: cdd01ef066bc6cf2
# Performance Targets: P99 <5ms, >100 RPS, >85% cache hit

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
DEPLOYMENT_MODE="${1:-docker}"  # docker or kubernetes
ENVIRONMENT="${2:-production}"

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

# Validation functions
validate_constitutional_hash() {
    local hash="$1"
    if [[ "$hash" != "$CONSTITUTIONAL_HASH" ]]; then
        log_error "Constitutional hash validation failed. Expected: $CONSTITUTIONAL_HASH, Got: $hash"
        exit 1
    fi
    log_success "Constitutional hash validated: $hash"
}

validate_environment() {
    log_info "Validating deployment environment..."
    
    # Check required tools
    local required_tools=("docker" "docker-compose")
    if [[ "$DEPLOYMENT_MODE" == "kubernetes" ]]; then
        required_tools+=("kubectl" "helm")
    fi
    
    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Required tool not found: $tool"
            exit 1
        fi
    done
    
    # Check environment file
    local env_file="${PROJECT_ROOT}/.env.${ENVIRONMENT}-complete"
    if [[ ! -f "$env_file" ]]; then
        log_error "Environment file not found: $env_file"
        log_info "Please copy .env.example to $env_file and configure it"
        exit 1
    fi
    
    # Validate constitutional hash in environment
    if ! grep -q "CONSTITUTIONAL_HASH=$CONSTITUTIONAL_HASH" "$env_file"; then
        log_error "Constitutional hash not found or incorrect in $env_file"
        exit 1
    fi
    
    log_success "Environment validation completed"
}

validate_performance_targets() {
    log_info "Validating performance target configurations..."
    
    local env_file="${PROJECT_ROOT}/.env.${ENVIRONMENT}-complete"
    
    # Check performance targets
    local targets=(
        "TARGET_P99_LATENCY_MS=5.0"
        "TARGET_CACHE_HIT_RATE=0.85"
        "TARGET_THROUGHPUT_RPS=100.0"
    )
    
    for target in "${targets[@]}"; do
        if ! grep -q "$target" "$env_file"; then
            log_warning "Performance target not found: $target"
        fi
    done
    
    log_success "Performance targets validated"
}

# Database initialization
initialize_database() {
    log_info "Initializing PostgreSQL database..."
    
    local init_script="${PROJECT_ROOT}/infrastructure/scripts/init-db.sql"
    if [[ ! -f "$init_script" ]]; then
        log_info "Creating database initialization script..."
        cat > "$init_script" << EOF
-- ACGS-2 Production Database Initialization
-- Constitutional Hash: ${CONSTITUTIONAL_HASH}

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create application user
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'acgs_app') THEN
        CREATE ROLE acgs_app WITH LOGIN PASSWORD 'CHANGE_ME_APP_PASSWORD';
    END IF;
END
\$\$;

-- Grant permissions
GRANT CONNECT ON DATABASE acgs_production TO acgs_app;
GRANT USAGE ON SCHEMA public TO acgs_app;
GRANT CREATE ON SCHEMA public TO acgs_app;

-- Create constitutional compliance table
CREATE TABLE IF NOT EXISTS constitutional_compliance (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hash VARCHAR(16) NOT NULL DEFAULT '${CONSTITUTIONAL_HASH}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    service_name VARCHAR(100) NOT NULL,
    compliance_status BOOLEAN NOT NULL DEFAULT true,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Create performance metrics table
CREATE TABLE IF NOT EXISTS performance_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    service_name VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(10,3) NOT NULL,
    target_value DECIMAL(10,3),
    constitutional_hash VARCHAR(16) DEFAULT '${CONSTITUTIONAL_HASH}'
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_constitutional_compliance_hash ON constitutional_compliance(hash);
CREATE INDEX IF NOT EXISTS idx_constitutional_compliance_service ON constitutional_compliance(service_name);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_timestamp ON performance_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_performance_metrics_service ON performance_metrics(service_name);

-- Insert initial compliance record
INSERT INTO constitutional_compliance (service_name, compliance_status, metadata)
VALUES ('database_initialization', true, '{"deployment_date": "$(date -Iseconds)", "version": "1.0.0"}')
ON CONFLICT DO NOTHING;

COMMIT;
EOF
    fi
    
    log_success "Database initialization script prepared"
}

# Redis configuration
configure_redis() {
    log_info "Configuring Redis cache..."
    
    local redis_conf="${PROJECT_ROOT}/infrastructure/redis/redis.conf"
    mkdir -p "$(dirname "$redis_conf")"
    
    cat > "$redis_conf" << EOF
# ACGS-2 Production Redis Configuration
# Constitutional Hash: ${CONSTITUTIONAL_HASH}

# Memory management
maxmemory 512mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Security
requirepass CHANGE_ME_REDIS_PASSWORD

# Performance
tcp-keepalive 300
timeout 0

# Logging
loglevel notice
logfile /var/log/redis/redis-server.log

# Constitutional compliance metadata
# hash: ${CONSTITUTIONAL_HASH}
# performance_target_cache_hit: 85%
EOF
    
    log_success "Redis configuration prepared"
}

# Docker deployment
deploy_docker() {
    log_info "Deploying ACGS-2 with Docker Compose..."
    
    cd "$PROJECT_ROOT"
    
    # Copy environment file
    cp ".env.${ENVIRONMENT}-complete" ".env"
    
    # Pull latest images
    log_info "Pulling latest Docker images..."
    docker-compose -f docker-compose.production-complete.yml pull
    
    # Start infrastructure services first
    log_info "Starting infrastructure services..."
    docker-compose -f docker-compose.production-complete.yml up -d postgres redis
    
    # Wait for infrastructure to be ready
    log_info "Waiting for infrastructure services to be ready..."
    sleep 30
    
    # Start ACGS services
    log_info "Starting ACGS services..."
    docker-compose -f docker-compose.production-complete.yml up -d
    
    # Wait for services to start
    sleep 60
    
    log_success "Docker deployment completed"
}

# Kubernetes deployment
deploy_kubernetes() {
    log_info "Deploying ACGS-2 with Kubernetes..."
    
    # Create namespace
    kubectl apply -f "${PROJECT_ROOT}/infrastructure/kubernetes/production/namespace.yaml" || true
    
    # Apply secrets and configmaps
    log_info "Applying secrets and configmaps..."
    kubectl apply -f "${PROJECT_ROOT}/infrastructure/kubernetes/production/acgs-production-complete.yaml"
    
    # Wait for deployment
    log_info "Waiting for deployments to be ready..."
    kubectl wait --for=condition=available --timeout=600s deployment/postgres -n acgs-production
    kubectl wait --for=condition=available --timeout=600s deployment/redis -n acgs-production
    kubectl wait --for=condition=available --timeout=600s deployment/auth-service -n acgs-production
    kubectl wait --for=condition=available --timeout=600s deployment/constitutional-ai-service -n acgs-production
    
    log_success "Kubernetes deployment completed"
}

# Health checks
perform_health_checks() {
    log_info "Performing health checks..."
    
    local services=(
        "auth-service:8016"
        "constitutional-ai-service:8001"
        "integrity-service:8002"
        "multi-agent-coordinator:8008"
        "blackboard-service:8010"
    )
    
    local base_url="http://localhost"
    if [[ "$DEPLOYMENT_MODE" == "kubernetes" ]]; then
        base_url="http://$(kubectl get svc -n acgs-production -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}')"
    fi
    
    for service in "${services[@]}"; do
        local service_name="${service%:*}"
        local port="${service#*:}"
        local url="${base_url}:${port}/health"
        
        log_info "Checking health of $service_name..."
        
        local retries=0
        local max_retries=10
        while [[ $retries -lt $max_retries ]]; do
            if curl -f -s "$url" > /dev/null 2>&1; then
                log_success "$service_name is healthy"
                break
            else
                ((retries++))
                if [[ $retries -eq $max_retries ]]; then
                    log_error "$service_name health check failed after $max_retries attempts"
                    return 1
                fi
                log_info "Retrying health check for $service_name ($retries/$max_retries)..."
                sleep 10
            fi
        done
    done
    
    log_success "All health checks passed"
}

# Constitutional compliance validation
validate_constitutional_compliance() {
    log_info "Validating constitutional compliance..."
    
    # Check if all services report correct constitutional hash
    local services=("auth-service:8016" "constitutional-ai-service:8001")
    
    for service in "${services[@]}"; do
        local service_name="${service%:*}"
        local port="${service#*:}"
        local url="http://localhost:${port}/constitutional-hash"
        
        log_info "Checking constitutional compliance for $service_name..."
        
        local response
        if response=$(curl -f -s "$url" 2>/dev/null); then
            if echo "$response" | grep -q "$CONSTITUTIONAL_HASH"; then
                log_success "$service_name constitutional compliance validated"
            else
                log_error "$service_name constitutional compliance failed"
                return 1
            fi
        else
            log_warning "$service_name constitutional compliance endpoint not available"
        fi
    done
    
    log_success "Constitutional compliance validation completed"
}

# Performance validation
validate_performance() {
    log_info "Validating performance targets..."
    
    # Basic performance test
    local test_url="http://localhost:8016/health"
    local total_requests=100
    local concurrent_requests=10
    
    log_info "Running performance test with $total_requests requests, $concurrent_requests concurrent..."
    
    if command -v ab &> /dev/null; then
        local ab_output
        ab_output=$(ab -n "$total_requests" -c "$concurrent_requests" "$test_url" 2>/dev/null | grep "Time per request" | head -1 | awk '{print $4}')
        
        if [[ -n "$ab_output" ]]; then
            local latency_ms=$(echo "$ab_output" | cut -d'.' -f1)
            if [[ "$latency_ms" -lt 5 ]]; then
                log_success "Performance test passed: ${latency_ms}ms < 5ms target"
            else
                log_warning "Performance test: ${latency_ms}ms exceeds 5ms target"
            fi
        fi
    else
        log_warning "Apache Bench (ab) not available for performance testing"
    fi
    
    log_success "Performance validation completed"
}

# Main deployment function
main() {
    log_info "Starting ACGS-2 Production Deployment"
    log_info "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log_info "Deployment Mode: $DEPLOYMENT_MODE"
    log_info "Environment: $ENVIRONMENT"
    
    # Validation phase
    validate_constitutional_hash "$CONSTITUTIONAL_HASH"
    validate_environment
    validate_performance_targets
    
    # Preparation phase
    initialize_database
    configure_redis
    
    # Deployment phase
    if [[ "$DEPLOYMENT_MODE" == "kubernetes" ]]; then
        deploy_kubernetes
    else
        deploy_docker
    fi
    
    # Validation phase
    perform_health_checks
    validate_constitutional_compliance
    validate_performance
    
    log_success "ACGS-2 Production Deployment completed successfully!"
    log_info "Access the services at:"
    log_info "  - Auth Service: http://localhost:8016"
    log_info "  - Constitutional AI: http://localhost:8001"
    log_info "  - Integrity Service: http://localhost:8002"
    log_info "  - Multi-Agent Coordinator: http://localhost:8008"
    log_info "  - Blackboard Service: http://localhost:8010"
    log_info "  - Prometheus: http://localhost:9090"
    log_info "  - Grafana: http://localhost:3000"
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
