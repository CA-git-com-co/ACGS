#!/bin/bash

# ACGS-2 Consolidated Deployment Script
# This script consolidates all deployment functionality using the shared library
# Constitutional Hash: cdd01ef066bc6cf2

set -euo pipefail

# Script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Source the shared deployment library
# shellcheck source=scripts/shared/deployment_lib.sh
source "${SCRIPT_DIR}/shared/deployment_lib.sh"

# Default configuration
DEFAULT_ENVIRONMENT="development"
DEFAULT_ACTION="deploy"
DEFAULT_COMPONENTS="all"

# Configuration variables
ENVIRONMENT="${ENVIRONMENT:-${DEFAULT_ENVIRONMENT}}"
ACTION="${ACTION:-${DEFAULT_ACTION}}"
COMPONENTS="${COMPONENTS:-${DEFAULT_COMPONENTS}}"
SKIP_HEALTH_CHECK="${SKIP_HEALTH_CHECK:-false}"
SKIP_MONITORING="${SKIP_MONITORING:-false}"
FORCE_REBUILD="${FORCE_REBUILD:-false}"
DRY_RUN="${DRY_RUN:-false}"

# Usage function
show_usage() {
    cat << EOF
ACGS-2 Consolidated Deployment Script
Constitutional Hash: ${CONSTITUTIONAL_HASH}

Usage: $0 [OPTIONS]

Options:
    -e, --environment ENV       Target environment (development|staging|production)
    -a, --action ACTION         Action to perform (deploy|stop|restart|status|logs)
    -c, --components COMP       Components to deploy (all|infrastructure|services|monitoring)
    -s, --skip-health-check     Skip health check after deployment
    -m, --skip-monitoring       Skip monitoring stack deployment
    -f, --force-rebuild         Force rebuild of Docker images
    -d, --dry-run              Show what would be done without executing
    -h, --help                 Show this help message
    -v, --verbose              Enable verbose logging

Examples:
    $0                                          # Deploy all components to development
    $0 -e production -a deploy                  # Deploy to production
    $0 -e staging -c infrastructure             # Deploy only infrastructure to staging
    $0 -a stop -c services                      # Stop only services
    $0 -e production -a status                  # Check status of production deployment
    $0 -a logs -c services                      # Show logs for services

Environment Variables:
    ENVIRONMENT                 Target environment (default: development)
    ACTION                      Action to perform (default: deploy)
    COMPONENTS                  Components to deploy (default: all)
    SKIP_HEALTH_CHECK          Skip health check (default: false)
    SKIP_MONITORING            Skip monitoring (default: false)
    FORCE_REBUILD              Force rebuild (default: false)
    DRY_RUN                    Dry run mode (default: false)
    DEBUG                      Enable debug logging (default: false)

EOF
}

# Parse command line arguments
parse_arguments() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -a|--action)
                ACTION="$2"
                shift 2
                ;;
            -c|--components)
                COMPONENTS="$2"
                shift 2
                ;;
            -s|--skip-health-check)
                SKIP_HEALTH_CHECK="true"
                shift
                ;;
            -m|--skip-monitoring)
                SKIP_MONITORING="true"
                shift
                ;;
            -f|--force-rebuild)
                FORCE_REBUILD="true"
                shift
                ;;
            -d|--dry-run)
                DRY_RUN="true"
                shift
                ;;
            -v|--verbose)
                DEBUG="true"
                shift
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
}

# Validate arguments
validate_arguments() {
    # Validate environment
    case "${ENVIRONMENT}" in
        development|staging|production)
            log_info "Target environment: ${ENVIRONMENT}"
            ;;
        *)
            log_error "Invalid environment: ${ENVIRONMENT}"
            log_error "Valid environments: development, staging, production"
            exit 1
            ;;
    esac
    
    # Validate action
    case "${ACTION}" in
        deploy|stop|restart|status|logs)
            log_info "Action: ${ACTION}"
            ;;
        *)
            log_error "Invalid action: ${ACTION}"
            log_error "Valid actions: deploy, stop, restart, status, logs"
            exit 1
            ;;
    esac
    
    # Validate components
    case "${COMPONENTS}" in
        all|infrastructure|services|monitoring)
            log_info "Components: ${COMPONENTS}"
            ;;
        *)
            log_error "Invalid components: ${COMPONENTS}"
            log_error "Valid components: all, infrastructure, services, monitoring"
            exit 1
            ;;
    esac
}

# Execute dry run
execute_dry_run() {
    log_info "DRY RUN MODE - Actions that would be performed:"
    log_info "Environment: ${ENVIRONMENT}"
    log_info "Action: ${ACTION}"
    log_info "Components: ${COMPONENTS}"
    log_info "Skip Health Check: ${SKIP_HEALTH_CHECK}"
    log_info "Skip Monitoring: ${SKIP_MONITORING}"
    log_info "Force Rebuild: ${FORCE_REBUILD}"
    
    case "${ACTION}" in
        deploy)
            log_info "Would deploy ${COMPONENTS} to ${ENVIRONMENT} environment"
            ;;
        stop)
            log_info "Would stop ${COMPONENTS} in ${ENVIRONMENT} environment"
            ;;
        restart)
            log_info "Would restart ${COMPONENTS} in ${ENVIRONMENT} environment"
            ;;
        status)
            log_info "Would check status of ${COMPONENTS} in ${ENVIRONMENT} environment"
            ;;
        logs)
            log_info "Would show logs for ${COMPONENTS} in ${ENVIRONMENT} environment"
            ;;
    esac
    
    log_info "DRY RUN completed"
}

# Deploy components
deploy_components() {
    log_step "Deploying ${COMPONENTS} to ${ENVIRONMENT} environment"
    
    # Set Docker Compose project name
    export COMPOSE_PROJECT_NAME="acgs-${ENVIRONMENT}"
    
    # Build images if force rebuild is enabled
    if [[ "${FORCE_REBUILD}" == "true" ]]; then
        log_step "Force rebuilding Docker images"
        cd "${PROJECT_ROOT}/infrastructure/docker" || exit 1
        docker-compose build --no-cache
    fi
    
    case "${COMPONENTS}" in
        infrastructure)
            start_infrastructure "${ENVIRONMENT}"
            ;;
        services)
            start_acgs_services "${ENVIRONMENT}"
            ;;
        monitoring)
            start_monitoring "${ENVIRONMENT}"
            ;;
        all)
            deploy_full_stack "${ENVIRONMENT}"
            return $?
            ;;
    esac
    
    # Health check
    if [[ "${SKIP_HEALTH_CHECK}" != "true" ]]; then
        log_step "Performing health checks"
        health_check_all
    fi
    
    log_success "Deployment completed successfully"
}

# Stop components
stop_components() {
    log_step "Stopping ${COMPONENTS} in ${ENVIRONMENT} environment"
    
    # Set Docker Compose project name
    export COMPOSE_PROJECT_NAME="acgs-${ENVIRONMENT}"
    
    stop_services "${COMPONENTS}"
    
    log_success "Components stopped successfully"
}

# Restart components
restart_components() {
    log_step "Restarting ${COMPONENTS} in ${ENVIRONMENT} environment"
    
    stop_components
    sleep 5
    deploy_components
    
    log_success "Components restarted successfully"
}

# Check status
check_status() {
    log_step "Checking status of ${COMPONENTS} in ${ENVIRONMENT} environment"
    
    # Set Docker Compose project name
    export COMPOSE_PROJECT_NAME="acgs-${ENVIRONMENT}"
    
    case "${COMPONENTS}" in
        infrastructure)
            docker-compose -f "${PROJECT_ROOT}/infrastructure/docker/docker-compose.base-infrastructure.yml" ps
            ;;
        services)
            docker-compose -f "${PROJECT_ROOT}/infrastructure/docker/docker-compose.acgs-services.yml" ps
            ;;
        monitoring)
            docker-compose -f "${PROJECT_ROOT}/infrastructure/monitoring/docker-compose.monitoring-consolidated.yml" ps
            ;;
        all)
            docker-compose -f "${PROJECT_ROOT}/infrastructure/docker/docker-compose.base-infrastructure.yml" ps
            docker-compose -f "${PROJECT_ROOT}/infrastructure/docker/docker-compose.acgs-services.yml" ps
            docker-compose -f "${PROJECT_ROOT}/infrastructure/monitoring/docker-compose.monitoring-consolidated.yml" ps
            ;;
    esac
    
    # Health check
    health_check_all
}

# Show logs
show_logs() {
    log_step "Showing logs for ${COMPONENTS} in ${ENVIRONMENT} environment"
    
    # Set Docker Compose project name
    export COMPOSE_PROJECT_NAME="acgs-${ENVIRONMENT}"
    
    case "${COMPONENTS}" in
        infrastructure)
            docker-compose -f "${PROJECT_ROOT}/infrastructure/docker/docker-compose.base-infrastructure.yml" logs -f
            ;;
        services)
            docker-compose -f "${PROJECT_ROOT}/infrastructure/docker/docker-compose.acgs-services.yml" logs -f
            ;;
        monitoring)
            docker-compose -f "${PROJECT_ROOT}/infrastructure/monitoring/docker-compose.monitoring-consolidated.yml" logs -f
            ;;
        all)
            docker-compose -f "${PROJECT_ROOT}/infrastructure/docker/docker-compose.base-infrastructure.yml" \
                          -f "${PROJECT_ROOT}/infrastructure/docker/docker-compose.acgs-services.yml" \
                          -f "${PROJECT_ROOT}/infrastructure/monitoring/docker-compose.monitoring-consolidated.yml" \
                          logs -f
            ;;
    esac
}

# Main function
main() {
    # Initialize logging
    init_logging
    
    log_info "ACGS-2 Consolidated Deployment Script"
    log_info "Constitutional Hash: ${CONSTITUTIONAL_HASH}"
    
    # Parse arguments
    parse_arguments "$@"
    
    # Validate arguments
    validate_arguments
    
    # Check if dry run
    if [[ "${DRY_RUN}" == "true" ]]; then
        execute_dry_run
        return 0
    fi
    
    # Pre-deployment checks
    if ! validate_constitutional_hash; then
        log_error "Constitutional hash validation failed"
        exit 1
    fi
    
    if ! check_docker || ! check_docker_compose; then
        log_error "Docker environment validation failed"
        exit 1
    fi
    
    # Execute action
    case "${ACTION}" in
        deploy)
            deploy_components
            ;;
        stop)
            stop_components
            ;;
        restart)
            restart_components
            ;;
        status)
            check_status
            ;;
        logs)
            show_logs
            ;;
        *)
            log_error "Unknown action: ${ACTION}"
            exit 1
            ;;
    esac
    
    log_success "Script completed successfully"
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi