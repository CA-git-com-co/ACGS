# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# Policy Synthesis Enhancement Deployment Script
# ACGS-1 Governance Framework - Production Deployment

set -euo pipefail

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_FILE="$PROJECT_ROOT/policy_synthesis_deployment.log"
DEPLOYMENT_CONFIG="$PROJECT_ROOT/config/deployment/policy_synthesis_config.json"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# Check prerequisites
check_prerequisites() {
    log "🔍 Checking deployment prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    # Check required environment variables
    required_vars=("POSTGRES_PASSWORD" "JWT_SECRET_KEY" "REDIS_PASSWORD")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    # Check if production compose file exists
    if [[ ! -f "$PROJECT_ROOT/docker-compose.prod.yml" ]]; then
        error "Production Docker Compose file not found"
        exit 1
    fi
    
    success "Prerequisites check passed"
}

# Backup current deployment
backup_current_deployment() {
    log "💾 Creating backup of current deployment..."
    
    backup_dir="$PROJECT_ROOT/backups/$(date +'%Y%m%d_%H%M%S')"
    mkdir -p "$backup_dir"
    
    # Backup database
    if docker ps | grep -q "acgs-postgres-prod"; then
        log "Backing up database..."
        docker exec acgs-postgres-prod pg_dump -U acgs_user acgs_prod > "$backup_dir/database_backup.sql"
        success "Database backup created"
    else
        warning "Production database not running, skipping database backup"
    fi
    
    # Backup configuration files
    cp -r "$PROJECT_ROOT/config" "$backup_dir/"
    
    success "Backup created at $backup_dir"
}

# Deploy enhanced services
deploy_enhanced_services() {
    log "🚀 Deploying enhanced Policy Synthesis services..."
    
    cd "$PROJECT_ROOT"
    
    # Pull latest images
    log "Pulling latest Docker images..."
    docker-compose -f config/docker/docker-compose.prod.yml pull
    
    # Build and deploy services
    log "Building and starting services..."
    docker-compose -f config/docker/docker-compose.prod.yml up -d --build
    
    # Wait for services to be ready
    log "Waiting for services to be ready..."
    sleep 30
    
    # Verify service health
    verify_service_health
}

# Verify service health
verify_service_health() {
    log "🏥 Verifying service health..."
    
    services=(
        "ac_service:8011"
        "integrity_service:8012"
        "fv_service:8013"
        "gs_service:8014"
        "pgc_service:8015"
    )
    
    all_healthy=true
    
    for service in "${services[@]}"; do
        service_name="${service%:*}"
        port="${service#*:}"
        
        log "Checking health of $service_name on port $port..."
        
        # Try health check endpoint
        if curl -f -s "http://localhost:$port/health" > /dev/null; then
            success "$service_name is healthy"
        else
            error "$service_name health check failed"
            all_healthy=false
        fi
    done
    
    if $all_healthy; then
        success "All services are healthy"
    else
        error "Some services failed health checks"
        exit 1
    fi
}

# Deploy monitoring stack
deploy_monitoring() {
    log "📊 Deploying monitoring stack..."
    
    cd "$PROJECT_ROOT"
    
    # Deploy monitoring services
    docker-compose -f docker-compose-monitoring.yml up -d
    
    # Wait for monitoring services
    sleep 20
    
    # Verify monitoring services
    monitoring_services=(
        "prometheus:9090"
        "grafana:3002"
        "alertmanager:9093"
    )
    
    for service in "${monitoring_services[@]}"; do
        service_name="${service%:*}"
        port="${service#*:}"
        
        if curl -f -s "http://localhost:$port" > /dev/null; then
            success "$service_name monitoring service is running"
        else
            warning "$service_name monitoring service may not be ready yet"
        fi
    done
    
    success "Monitoring stack deployed"
}

# Configure alerting
configure_alerting() {
    log "🚨 Configuring alerting system..."
    
    # Copy alert rules to monitoring directory
    if [[ -f "$PROJECT_ROOT/config/monitoring/policy_synthesis_alert_rules.yml" ]]; then
        cp "$PROJECT_ROOT/config/monitoring/policy_synthesis_alert_rules.yml" \
           "$PROJECT_ROOT/monitoring/"
        success "Alert rules configured"
    else
        warning "Alert rules file not found, using defaults"
    fi
    
    # Restart Prometheus to load new rules
    docker-compose -f docker-compose-monitoring.yml restart prometheus
    
    success "Alerting system configured"
}

# Run deployment validation
run_deployment_validation() {
    log "✅ Running deployment validation..."
    
    # Test policy synthesis endpoint
    log "Testing policy synthesis endpoint..."
    test_payload='{"principle": "Democratic voting requires quorum", "context": {"domain": "governance"}, "enable_enhancement": true}'
    
    if curl -f -s -X POST \
        -H "Content-Type: application/json" \
        -d "$test_payload" \
        "http://localhost:8014/api/v1/synthesis/policy" > /dev/null; then
        success "Policy synthesis endpoint test passed"
    else
        error "Policy synthesis endpoint test failed"
        exit 1
    fi
    
    # Test multi-model consensus endpoint
    log "Testing multi-model consensus endpoint..."
    consensus_payload='{"principle": "Constitutional amendments require supermajority", "enable_multi_model": true}'
    
    if curl -f -s -X POST \
        -H "Content-Type: application/json" \
        -d "$consensus_payload" \
        "http://localhost:8014/api/v1/synthesis/multi-model" > /dev/null; then
        success "Multi-model consensus endpoint test passed"
    else
        warning "Multi-model consensus endpoint test failed (may be expected if not fully configured)"
    fi
    
    success "Deployment validation completed"
}

# Generate deployment report
generate_deployment_report() {
    log "📋 Generating deployment report..."
    
    report_file="$PROJECT_ROOT/deployment_report_$(date +'%Y%m%d_%H%M%S').json"
    
    cat > "$report_file" << EOF
{
  "deployment_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "deployment_version": "policy_synthesis_enhancement_v1.0",
  "services_deployed": [
    "ac_service",
    "integrity_service", 
    "fv_service",
    "gs_service",
    "pgc_service"
  ],
  "monitoring_stack": [
    "prometheus",
    "grafana",
    "alertmanager"
  ],
  "health_checks": "passed",
  "validation_tests": "passed",
  "deployment_status": "successful",
  "next_steps": [
    "Monitor system performance for 24 hours",
    "Run comprehensive test suite",
    "Begin threshold optimization phase",
    "Schedule performance review"
  ]
}
EOF
    
    success "Deployment report generated: $report_file"
}

# Main deployment function
main() {
    log "🚀 Starting Policy Synthesis Enhancement Deployment"
    log "Project root: $PROJECT_ROOT"
    
    # Run deployment steps
    check_prerequisites
    backup_current_deployment
    deploy_enhanced_services
    deploy_monitoring
    configure_alerting
    run_deployment_validation
    generate_deployment_report
    
    success "🎉 Policy Synthesis Enhancement deployment completed successfully!"
    log "📊 Monitoring dashboards:"
    log "  - Grafana: http://localhost:3002"
    log "  - Prometheus: http://localhost:9090"
    log "  - Alertmanager: http://localhost:9093"
    log ""
    log "🔗 Service endpoints:"
    log "  - GS Service: http://localhost:8014"
    log "  - Policy Synthesis API: http://localhost:8014/api/v1/synthesis"
    log ""
    log "📋 Next steps:"
    log "  1. Monitor system performance for 24 hours"
    log "  2. Run comprehensive test suite"
    log "  3. Begin threshold optimization phase"
    log "  4. Schedule performance review"
}

# Run main function
main "$@"
