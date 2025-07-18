#!/bin/bash
# ACGS-2 Unified Deployment Script
# Constitutional Hash: cdd01ef066bc6cf2

set -euo pipefail

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ACGS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

# Default values
ENVIRONMENT="${1:-development}"
ACTION="${2:-up}"
SERVICES="${3:-all}"

# Color codes for output
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
validate_environment() {
    local env="$1"
    case "$env" in
        development|staging|production)
            return 0
            ;;
        *)
            log_error "Invalid environment: $env"
            log_info "Valid environments: development, staging, production"
            exit 1
            ;;
    esac
}

validate_action() {
    local action="$1"
    case "$action" in
        up|down|restart|logs|status|build|pull)
            return 0
            ;;
        *)
            log_error "Invalid action: $action"
            log_info "Valid actions: up, down, restart, logs, status, build, pull"
            exit 1
            ;;
    esac
}

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
    
    # Check environment file
    local env_file="${ACGS_ROOT}/config/environments/${ENVIRONMENT}.env"
    if [[ ! -f "$env_file" ]]; then
        log_error "Environment file not found: $env_file"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

load_environment() {
    local env_file="${ACGS_ROOT}/config/environments/${ENVIRONMENT}.env"
    log_info "Loading environment from: $env_file"
    
    # Export environment variables
    set -a
    source "$env_file"
    set +a
    
    # Set ACGS_ROOT if not already set
    export ACGS_ROOT="${ACGS_ROOT}"
    
    log_success "Environment loaded successfully"
}

get_compose_files() {
    local env="$1"
    local base_file="${ACGS_ROOT}/config/docker/docker-compose.base.yml"
    local env_file="${ACGS_ROOT}/config/docker/docker-compose.${env}.yml"
    
    if [[ ! -f "$base_file" ]]; then
        log_error "Base compose file not found: $base_file"
        exit 1
    fi
    
    if [[ ! -f "$env_file" ]]; then
        log_error "Environment compose file not found: $env_file"
        exit 1
    fi
    
    echo "-f $base_file -f $env_file"
}

validate_constitutional_compliance() {
    log_info "Validating constitutional compliance..."
    
    # Check if constitutional hash is present in environment
    if [[ "${CONSTITUTIONAL_HASH:-}" != "$CONSTITUTIONAL_HASH" ]]; then
        log_error "Constitutional hash mismatch or missing"
        log_error "Expected: $CONSTITUTIONAL_HASH"
        log_error "Found: ${CONSTITUTIONAL_HASH:-<not set>}"
        exit 1
    fi
    
    log_success "Constitutional compliance validated"
}

deploy_services() {
    local env="$1"
    local action="$2"
    local services="$3"
    
    local compose_files
    compose_files=$(get_compose_files "$env")
    
    log_info "Deploying ACGS-2 services..."
    log_info "Environment: $env"
    log_info "Action: $action"
    log_info "Services: $services"
    
    cd "$ACGS_ROOT"
    
    case "$action" in
        up)
            if [[ "$services" == "all" ]]; then
                docker-compose $compose_files up -d
            else
                docker-compose $compose_files up -d $services
            fi
            ;;
        down)
            docker-compose $compose_files down
            ;;
        restart)
            if [[ "$services" == "all" ]]; then
                docker-compose $compose_files restart
            else
                docker-compose $compose_files restart $services
            fi
            ;;
        logs)
            if [[ "$services" == "all" ]]; then
                docker-compose $compose_files logs -f
            else
                docker-compose $compose_files logs -f $services
            fi
            ;;
        status)
            docker-compose $compose_files ps
            ;;
        build)
            if [[ "$services" == "all" ]]; then
                docker-compose $compose_files build
            else
                docker-compose $compose_files build $services
            fi
            ;;
        pull)
            if [[ "$services" == "all" ]]; then
                docker-compose $compose_files pull
            else
                docker-compose $compose_files pull $services
            fi
            ;;
    esac
}

health_check() {
    log_info "Performing health checks..."
    
    local compose_files
    compose_files=$(get_compose_files "$ENVIRONMENT")
    
    cd "$ACGS_ROOT"
    
    # Get list of running services
    local services
    services=$(docker-compose $compose_files ps --services --filter "status=running")
    
    local failed_services=()
    
    for service in $services; do
        log_info "Checking health of service: $service"
        
        # Get container name
        local container_name
        container_name=$(docker-compose $compose_files ps -q "$service")
        
        if [[ -n "$container_name" ]]; then
            # Check if container is healthy
            local health_status
            health_status=$(docker inspect --format='{{.State.Health.Status}}' "$container_name" 2>/dev/null || echo "no-healthcheck")
            
            case "$health_status" in
                healthy)
                    log_success "Service $service is healthy"
                    ;;
                unhealthy)
                    log_error "Service $service is unhealthy"
                    failed_services+=("$service")
                    ;;
                starting)
                    log_warning "Service $service is still starting"
                    ;;
                no-healthcheck)
                    log_warning "Service $service has no health check configured"
                    ;;
                *)
                    log_warning "Service $service has unknown health status: $health_status"
                    ;;
            esac
        else
            log_error "Service $service is not running"
            failed_services+=("$service")
        fi
    done
    
    if [[ ${#failed_services[@]} -eq 0 ]]; then
        log_success "All services are healthy"
        return 0
    else
        log_error "Failed services: ${failed_services[*]}"
        return 1
    fi
}

show_usage() {
    cat << EOF
ACGS-2 Unified Deployment Script
Constitutional Hash: $CONSTITUTIONAL_HASH

Usage: $0 [ENVIRONMENT] [ACTION] [SERVICES]

ENVIRONMENT:
    development  - Development environment (default)
    staging      - Staging environment
    production   - Production environment

ACTION:
    up          - Start services (default)
    down        - Stop services
    restart     - Restart services
    logs        - Show service logs
    status      - Show service status
    build       - Build service images
    pull        - Pull service images

SERVICES:
    all         - All services (default)
    <service>   - Specific service name

Examples:
    $0                                    # Start development environment
    $0 production up                      # Start production environment
    $0 staging restart constitutional_ai  # Restart constitutional_ai in staging
    $0 development logs                   # Show logs for development environment

Constitutional Compliance:
    All deployments maintain constitutional hash validation: $CONSTITUTIONAL_HASH
    Performance targets: P99 <5ms, >100 RPS, >85% cache hit rates
EOF
}

main() {
    # Show usage if help requested
    if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
        show_usage
        exit 0
    fi
    
    log_info "🚀 ACGS-2 Unified Deployment Script"
    log_info "📋 Constitutional Hash: $CONSTITUTIONAL_HASH"
    
    # Validate inputs
    validate_environment "$ENVIRONMENT"
    validate_action "$ACTION"
    
    # Check prerequisites
    check_prerequisites
    
    # Load environment
    load_environment
    
    # Validate constitutional compliance
    validate_constitutional_compliance
    
    # Deploy services
    deploy_services "$ENVIRONMENT" "$ACTION" "$SERVICES"
    
    # Perform health check for up action
    if [[ "$ACTION" == "up" ]]; then
        sleep 10  # Wait for services to start
        if health_check; then
            log_success "✅ ACGS-2 deployment completed successfully"
        else
            log_error "❌ Some services failed health checks"
            exit 1
        fi
    else
        log_success "✅ ACGS-2 $ACTION completed successfully"
    fi
}

# Run main function
main "$@"
