#!/bin/bash

# ACGS-PGP Staging Environment Setup Script
# Establishes staging environment with production parity for testing

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Configuration
STAGING_ENV_FILE="config/environments/staging.env"
STAGING_COMPOSE_FILE="infrastructure/docker/docker-compose.staging.yml"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites for staging environment setup..."
    
    # Check if required files exist
    if [[ ! -f "$STAGING_ENV_FILE" ]]; then
        error "Staging environment file not found: $STAGING_ENV_FILE"
        exit 1
    fi
    
    if [[ ! -f "$STAGING_COMPOSE_FILE" ]]; then
        error "Staging Docker Compose file not found: $STAGING_COMPOSE_FILE"
        exit 1
    fi
    
    # Check if required environment variables are set
    if [[ -z "${POSTGRES_PASSWORD:-}" ]]; then
        warning "POSTGRES_PASSWORD not set, using default"
        export POSTGRES_PASSWORD="acgs_staging_password_2024"
    fi
    
    if [[ -z "${JWT_SECRET_KEY:-}" ]]; then
        warning "JWT_SECRET_KEY not set, generating one"
        export JWT_SECRET_KEY="acgs_staging_jwt_secret_$(date +%s)"
    fi
    
    success "Prerequisites check completed"
}

# Validate environment parity
validate_environment_parity() {
    log "Validating staging environment parity with production..."
    
    # Check constitutional hash consistency
    local staging_hash=$(grep "CONSTITUTIONAL_HASH" "$STAGING_ENV_FILE" | cut -d'=' -f2 | tr -d '"')
    if [[ "$staging_hash" != "$CONSTITUTIONAL_HASH" ]]; then
        error "Constitutional hash mismatch in staging environment"
        exit 1
    fi
    
    # Validate resource limits are production-like
    local staging_compose_content=$(cat "$STAGING_COMPOSE_FILE")
    if ! echo "$staging_compose_content" | grep -q "cpus.*200m\|cpus.*0.2"; then
        warning "Staging resource limits may not match production standards"
    fi
    
    # Check service ports configuration
    local expected_ports=("8000" "8001" "8002" "8003" "8004" "8005" "8006" "8181")
    for port in "${expected_ports[@]}"; do
        if ! echo "$staging_compose_content" | grep -q ":$port"; then
            warning "Port $port configuration may be missing in staging"
        fi
    done
    
    success "Environment parity validation completed"
}

# Setup staging network
setup_staging_network() {
    log "Setting up staging network infrastructure..."
    
    # Create staging network if it doesn't exist
    if ! docker network ls | grep -q "acgs-staging"; then
        docker network create acgs-staging --driver bridge --subnet 172.31.0.0/16
        success "Created staging network"
    else
        log "Staging network already exists"
    fi
}

# Setup staging volumes
setup_staging_volumes() {
    log "Setting up staging persistent volumes..."
    
    local volumes=("postgres_staging_data" "redis_staging_data" "opa_staging_policies")
    
    for volume in "${volumes[@]}"; do
        if ! docker volume ls | grep -q "$volume"; then
            docker volume create "$volume"
            success "Created volume: $volume"
        else
            log "Volume already exists: $volume"
        fi
    done
}

# Validate staging configuration
validate_staging_config() {
    log "Validating staging configuration files..."
    
    # Check if OPA is accessible
    if curl -f http://localhost:8181/health >/dev/null 2>&1; then
        success "OPA is accessible on port 8181"
    else
        warning "OPA not accessible - will be started with staging environment"
    fi
    
    # Check if Prometheus is accessible
    if curl -f http://localhost:9090/api/v1/status/config >/dev/null 2>&1; then
        success "Prometheus is accessible on port 9090"
    else
        warning "Prometheus not accessible - monitoring may need setup"
    fi
    
    # Check if Grafana is accessible
    if curl -f http://localhost:3000/api/health >/dev/null 2>&1; then
        success "Grafana is accessible on port 3000"
    else
        warning "Grafana not accessible - monitoring may need setup"
    fi
}

# Create staging environment summary
create_staging_summary() {
    log "Creating staging environment summary..."
    
    local summary_file="staging_environment_summary.md"
    
    cat > "$summary_file" << EOF
# ACGS-PGP Staging Environment Summary

## Environment Configuration
- **Constitutional Hash**: $CONSTITUTIONAL_HASH
- **Environment**: staging
- **Database**: PostgreSQL (port 5435)
- **Cache**: Redis (port 6382)
- **Policy Engine**: OPA (port 8181)

## Service Endpoints (Staging)
- **Auth Service**: http://localhost:8010 (mapped from 8000)
- **AC Service**: http://localhost:8011 (mapped from 8001)
- **Integrity Service**: http://localhost:8012 (mapped from 8002)
- **FV Service**: http://localhost:8013 (mapped from 8003)
- **GS Service**: http://localhost:8014 (mapped from 8004)
- **PGC Service**: http://localhost:8015 (mapped from 8005)
- **EC Service**: http://localhost:8016 (mapped from 8006)

## Monitoring Stack
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/acgs_admin_2024)

## Resource Limits (Production Parity)
- **CPU Request**: 200m
- **CPU Limit**: 500m (1000m for PGC)
- **Memory Request**: 512Mi
- **Memory Limit**: 1Gi (2Gi for high-performance services)

## Validation Commands
\`\`\`bash
# Check service health
curl http://localhost:8010/health  # Auth Service
curl http://localhost:8011/health  # AC Service
curl http://localhost:8015/health  # PGC Service

# Check OPA policy engine
curl http://localhost:8181/health

# Check constitutional compliance
curl -X POST http://localhost:8181/v1/data/acgs/constitutional/allow \\
  -H "Content-Type: application/json" \\
  -d '{"input": {"constitutional_hash": "$CONSTITUTIONAL_HASH", "compliance_score": 0.85}}'

# Check monitoring
curl http://localhost:9090/api/v1/status/config
curl http://localhost:3000/api/health
\`\`\`

## Next Steps
1. Deploy services using: \`docker-compose -f $STAGING_COMPOSE_FILE up -d\`
2. Run health checks and validation tests
3. Execute load testing for performance validation
4. Validate constitutional compliance monitoring
5. Test emergency response procedures (<30min RTO)

Generated: $(date)
EOF

    success "Staging environment summary created: $summary_file"
}

# Main function
main() {
    log "Starting ACGS-PGP Staging Environment Setup"
    log "============================================"
    
    check_prerequisites
    validate_environment_parity
    setup_staging_network
    setup_staging_volumes
    validate_staging_config
    create_staging_summary
    
    success "Staging environment setup completed successfully!"
    log "Environment is ready for testing and validation"
    log "Use 'docker-compose -f $STAGING_COMPOSE_FILE up -d' to start services"
}

# Execute main function
main "$@"
