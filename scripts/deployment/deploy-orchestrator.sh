#!/bin/bash
# ACGS-2 Production Deployment Orchestrator
# Constitutional Hash: cdd01ef066bc6cf2
# Zero-downtime deployment with <30 second rollback capability

set -euo pipefail

# Configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

# Command line arguments
COMMAND="${1:-help}"
DEPLOYMENT_MODE="${2:-docker}"
ENVIRONMENT="${3:-production}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_header() { echo -e "${PURPLE}[ACGS-2]${NC} $1"; }

# Help function
show_help() {
    cat << EOF
ACGS-2 Production Deployment Orchestrator
Constitutional Hash: $CONSTITUTIONAL_HASH

Usage: $0 <command> [deployment_mode] [environment]

Commands:
  deploy      - Deploy ACGS-2 to production
  health      - Perform comprehensive health checks
  rollback    - Rollback to previous deployment
  status      - Show deployment status
  validate    - Validate constitutional compliance
  monitor     - Start monitoring stack
  backup      - Create deployment backup
  restore     - Restore from backup
  help        - Show this help message

Deployment Modes:
  docker      - Deploy using Docker Compose (default)
  kubernetes  - Deploy using Kubernetes

Environments:
  staging     - Deploy to staging environment
  production  - Deploy to production environment (default)

Examples:
  $0 deploy docker production
  $0 health
  $0 rollback docker
  $0 validate
  $0 monitor

Performance Targets:
  - P99 Latency: <5ms
  - Throughput: >100 RPS
  - Cache Hit Rate: >85%
  - Constitutional Compliance: 100%
  - Rollback Time: <30 seconds

EOF
}

# Validation functions
validate_prerequisites() {
    log_info "🔍 Validating prerequisites..."

    # Check required tools
    local required_tools=("docker" "docker-compose" "curl" "jq")
    if [[ "$DEPLOYMENT_MODE" == "kubernetes" ]]; then
        required_tools+=("kubectl" "helm")
    fi

    for tool in "${required_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            log_error "Required tool not found: $tool"
            return 1
        fi
    done

    # Check constitutional hash
    if [[ -z "$CONSTITUTIONAL_HASH" || "$CONSTITUTIONAL_HASH" != "cdd01ef066bc6cf2" ]]; then
        log_error "Invalid constitutional hash: $CONSTITUTIONAL_HASH"
        return 1
    fi

    # Check environment file
    local env_file="${PROJECT_ROOT}/.env.${ENVIRONMENT}-complete"
    if [[ ! -f "$env_file" ]]; then
        log_error "Environment file not found: $env_file"
        return 1
    fi

    log_success "Prerequisites validation passed"
    return 0
}

# Deployment functions
deploy_acgs() {
    log_header "🚀 Starting ACGS-2 Production Deployment"
    log_info "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log_info "Deployment Mode: $DEPLOYMENT_MODE"
    log_info "Environment: $ENVIRONMENT"

    # Validate prerequisites
    if ! validate_prerequisites; then
        log_error "Prerequisites validation failed"
        return 1
    fi

    # Run deployment script
    log_info "Executing deployment script..."
    if [[ -x "${SCRIPT_DIR}/deploy-production.sh" ]]; then
        "${SCRIPT_DIR}/deploy-production.sh" "$DEPLOYMENT_MODE" "$ENVIRONMENT"
    else
        log_error "Deployment script not found or not executable"
        return 1
    fi

    # Perform health checks
    log_info "Performing post-deployment health checks..."
    if [[ -x "${SCRIPT_DIR}/health-check.sh" ]]; then
        "${SCRIPT_DIR}/health-check.sh" "$DEPLOYMENT_MODE" "$ENVIRONMENT"
    else
        log_warning "Health check script not found"
    fi

    log_success "🎉 ACGS-2 deployment completed successfully!"
}

# Health check function
check_health() {
    log_header "🏥 Performing ACGS-2 Health Checks"

    if [[ -x "${SCRIPT_DIR}/health-check.sh" ]]; then
        "${SCRIPT_DIR}/health-check.sh" "$DEPLOYMENT_MODE" "$ENVIRONMENT"
    else
        log_error "Health check script not found"
        return 1
    fi
}

# Rollback function
perform_rollback() {
    log_header "🔄 Performing ACGS-2 Rollback"
    log_warning "This will rollback the current deployment"

    # Confirmation for production
    if [[ "$ENVIRONMENT" == "production" ]]; then
        read -p "Are you sure you want to rollback production? (yes/no): " -r
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            log_info "Rollback cancelled"
            return 0
        fi
    fi

    if [[ -x "${SCRIPT_DIR}/rollback.sh" ]]; then
        "${SCRIPT_DIR}/rollback.sh" "$DEPLOYMENT_MODE" "previous"
    else
        log_error "Rollback script not found"
        return 1
    fi
}

# Status function
show_status() {
    log_header "📊 ACGS-2 Deployment Status"
    log_info "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log_info "Deployment Mode: $DEPLOYMENT_MODE"
    log_info "Environment: $ENVIRONMENT"

    # Service status
    log_info "Checking service status..."

    local services=("8016" "8001" "8002" "8008" "8010")
    local healthy_services=0

    for port in "${services[@]}"; do
        if curl -f -s --max-time 3 "http://localhost:$port/health" > /dev/null 2>&1; then
            log_success "Port $port: Healthy"
            healthy_services=$((healthy_services + 1))
        else
            log_error "Port $port: Unhealthy"
        fi
    done

    log_info "Service Health: $healthy_services/${#services[@]} services healthy"

    # Infrastructure status
    log_info "Checking infrastructure status..."

    if [[ "$DEPLOYMENT_MODE" == "docker" ]]; then
        # Docker status
        if docker ps --filter "name=acgs_" --format "table {{.Names}}\t{{.Status}}" | grep -q "Up"; then
            log_success "Docker containers are running"
        else
            log_error "Docker containers are not running"
        fi
    else
        # Kubernetes status
        if kubectl get pods -n acgs-production --no-headers | grep -q "Running"; then
            log_success "Kubernetes pods are running"
        else
            log_error "Kubernetes pods are not running"
        fi
    fi

    # Performance metrics
    log_info "Performance Targets:"
    log_info "  - P99 Latency: <5ms"
    log_info "  - Throughput: >100 RPS"
    log_info "  - Cache Hit Rate: >85%"
    log_info "  - Constitutional Compliance: 100%"
}

# Validation function
validate_compliance() {
    log_header "⚖️  Validating Constitutional Compliance"

    local compliance_score=0
    local total_checks=0

    # Check constitutional hash in files
    local files=(
        ".env.${ENVIRONMENT}-complete"
        "docker-compose.production-complete.yml"
        "infrastructure/kubernetes/production/acgs-production-complete.yaml"
    )

    for file in "${files[@]}"; do
        total_checks=$((total_checks + 1))
        if [[ -f "$file" ]] && grep -q "$CONSTITUTIONAL_HASH" "$file"; then
            log_success "$file: Constitutional hash validated"
            compliance_score=$((compliance_score + 1))
        else
            log_error "$file: Constitutional hash missing or incorrect"
        fi
    done

    # Check service compliance
    local services=("8016" "8001" "8002" "8008" "8010")
    for port in "${services[@]}"; do
        total_checks=$((total_checks + 1))
        if curl -f -s --max-time 3 "http://localhost:$port/constitutional-hash" 2>/dev/null | grep -q "$CONSTITUTIONAL_HASH"; then
            log_success "Port $port: Constitutional compliance verified"
            compliance_score=$((compliance_score + 1))
        else
            log_warning "Port $port: Constitutional compliance check failed"
        fi
    done

    local compliance_percentage=$((compliance_score * 100 / total_checks))
    log_info "Constitutional Compliance Score: $compliance_score/$total_checks ($compliance_percentage%)"

    if [[ $compliance_percentage -eq 100 ]]; then
        log_success "🎉 Constitutional compliance: PERFECT"
    elif [[ $compliance_percentage -ge 80 ]]; then
        log_success "✅ Constitutional compliance: PASSED"
    else
        log_error "❌ Constitutional compliance: FAILED"
        return 1
    fi
}

# Monitoring function
start_monitoring() {
    log_header "📊 Starting ACGS-2 Monitoring Stack"

    if [[ "$DEPLOYMENT_MODE" == "docker" ]]; then
        # Start monitoring with Docker Compose
        log_info "Starting Prometheus and Grafana..."
        docker-compose -f docker-compose.production-complete.yml up -d prometheus grafana

        # Wait for services
        sleep 30

        # Check monitoring health
        if curl -f -s "http://localhost:9090/-/healthy" > /dev/null; then
            log_success "Prometheus is healthy: http://localhost:9090"
        else
            log_error "Prometheus health check failed"
        fi

        if curl -f -s "http://localhost:3000/api/health" > /dev/null; then
            log_success "Grafana is healthy: http://localhost:3000"
        else
            log_error "Grafana health check failed"
        fi
    else
        # Start monitoring with Kubernetes
        log_info "Deploying monitoring stack to Kubernetes..."
        kubectl apply -f infrastructure/kubernetes/monitoring/ -n acgs-production

        log_info "Waiting for monitoring pods to be ready..."
        kubectl wait --for=condition=ready pod -l app=prometheus -n acgs-production --timeout=120s
        kubectl wait --for=condition=ready pod -l app=grafana -n acgs-production --timeout=120s
    fi

    log_success "Monitoring stack is running"
    log_info "Access URLs:"
    log_info "  - Prometheus: http://localhost:9090"
    log_info "  - Grafana: http://localhost:3000"
}

# Backup function
create_backup() {
    log_header "💾 Creating ACGS-2 Deployment Backup"

    local backup_dir="${PROJECT_ROOT}/backups/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup_dir"

    # Backup configuration files
    cp .env.${ENVIRONMENT}-complete "$backup_dir/" 2>/dev/null || true
    cp docker-compose.production-complete.yml "$backup_dir/" 2>/dev/null || true

    # Backup deployment state
    if [[ "$DEPLOYMENT_MODE" == "docker" ]]; then
        docker-compose -f docker-compose.production-complete.yml config > "$backup_dir/docker-compose-resolved.yml"
        docker-compose -f docker-compose.production-complete.yml ps --format json > "$backup_dir/container-state.json"
    else
        kubectl get all -n acgs-production -o yaml > "$backup_dir/kubernetes-state.yaml"
    fi

    # Create backup metadata
    cat > "$backup_dir/backup-metadata.json" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "constitutional_hash": "$CONSTITUTIONAL_HASH",
  "deployment_mode": "$DEPLOYMENT_MODE",
  "environment": "$ENVIRONMENT",
  "git_sha": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "git_branch": "$(git branch --show-current 2>/dev/null || echo 'unknown')"
}
EOF

    log_success "Backup created: $backup_dir"
}

# Main function
main() {
    case "$COMMAND" in
        "deploy")
            deploy_acgs
            ;;
        "health")
            check_health
            ;;
        "rollback")
            perform_rollback
            ;;
        "status")
            show_status
            ;;
        "validate")
            validate_compliance
            ;;
        "monitor")
            start_monitoring
            ;;
        "backup")
            create_backup
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Make scripts executable
chmod +x "${SCRIPT_DIR}"/*.sh 2>/dev/null || true

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
