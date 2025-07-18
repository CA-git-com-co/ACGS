#!/bin/bash

# ACGS-2 Shared Deployment Library
# This library consolidates common deployment functions used across all deployment scripts
# Constitutional Hash: cdd01ef066bc6cf2

# Color definitions
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly PURPLE='\033[0;35m'
readonly CYAN='\033[0;36m'
readonly WHITE='\033[1;37m'
readonly NC='\033[0m' # No Color

# Global constants
readonly CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
readonly PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
readonly LOG_FILE="${PROJECT_ROOT}/logs/deployment.log"
readonly PID_FILE="${PROJECT_ROOT}/logs/deployment.pid"

# Performance targets
readonly P99_LATENCY_TARGET="5ms"
readonly THROUGHPUT_TARGET="100 RPS"
readonly CACHE_HIT_RATE_TARGET="85%"

# Default service configurations
declare -A DEFAULT_SERVICES=(
    ["auth_service"]="8000"
    ["ac_service"]="8001"
    ["integrity_service"]="8002"
    ["fv_service"]="8003"
    ["gs_service"]="8004"
    ["pgc_service"]="8005"
    ["ec_service"]="8006"
)

# Default infrastructure ports
declare -A INFRASTRUCTURE_PORTS=(
    ["postgres"]="5432"
    ["redis"]="6379"
    ["prometheus"]="9090"
    ["grafana"]="3000"
    ["alertmanager"]="9093"
    ["haproxy"]="8404"
)

# Environment configurations
declare -A ENV_CONFIGS=(
    ["development"]="docker-compose.development.yml"
    ["staging"]="docker-compose.staging.yml"
    ["production"]="docker-compose.production-override.yml"
)

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "${LOG_FILE}"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "${LOG_FILE}"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "${LOG_FILE}"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "${LOG_FILE}"
}

log_debug() {
    if [[ "${DEBUG:-false}" == "true" ]]; then
        echo -e "${PURPLE}[DEBUG]${NC} $1" | tee -a "${LOG_FILE}"
    fi
}

log_step() {
    echo -e "${CYAN}[STEP]${NC} $1" | tee -a "${LOG_FILE}"
}

# Initialize logging
init_logging() {
    mkdir -p "$(dirname "${LOG_FILE}")"
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Deployment started" >> "${LOG_FILE}"
    echo "Constitutional Hash: ${CONSTITUTIONAL_HASH}" >> "${LOG_FILE}"
    echo "Project Root: ${PROJECT_ROOT}" >> "${LOG_FILE}"
    echo "---" >> "${LOG_FILE}"
}

# Cleanup function
cleanup() {
    log_info "Cleaning up deployment resources..."
    [[ -f "${PID_FILE}" ]] && rm -f "${PID_FILE}"
    log_info "Cleanup completed"
}

# Trap for cleanup
trap cleanup EXIT

# Validate constitutional hash
validate_constitutional_hash() {
    local found_hash
    found_hash=$(grep -r "constitutional_hash.*${CONSTITUTIONAL_HASH}" "${PROJECT_ROOT}" | head -1)
    
    if [[ -z "${found_hash}" ]]; then
        log_error "Constitutional hash validation failed: ${CONSTITUTIONAL_HASH}"
        return 1
    fi
    
    log_success "Constitutional hash validated: ${CONSTITUTIONAL_HASH}"
    return 0
}

# Check if Docker is available
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        return 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker daemon is not running"
        return 1
    fi
    
    log_success "Docker is available and running"
    return 0
}

# Check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        return 1
    fi
    
    log_success "Docker Compose is available"
    return 0
}

# Wait for service to be healthy
wait_for_service() {
    local service_name="$1"
    local port="$2"
    local max_attempts="${3:-30}"
    local wait_time="${4:-10}"
    local health_endpoint="${5:-/health}"
    
    log_step "Waiting for ${service_name} on port ${port} to be healthy..."
    
    for ((i=1; i<=max_attempts; i++)); do
        if curl -f -s "http://localhost:${port}${health_endpoint}" &> /dev/null; then
            log_success "${service_name} is healthy after ${i} attempts"
            return 0
        fi
        
        log_debug "Attempt ${i}/${max_attempts} - ${service_name} not ready yet"
        sleep "${wait_time}"
    done
    
    log_error "${service_name} failed to become healthy after ${max_attempts} attempts"
    return 1
}

# Check service health
check_service_health() {
    local service_name="$1"
    local port="$2"
    local endpoint="${3:-/health}"
    
    log_debug "Checking health of ${service_name} on port ${port}"
    
    if ! curl -f -s "http://localhost:${port}${endpoint}" &> /dev/null; then
        log_error "${service_name} health check failed"
        return 1
    fi
    
    log_success "${service_name} is healthy"
    return 0
}

# Validate service configuration
validate_service_config() {
    local service_name="$1"
    local config_file="$2"
    
    if [[ ! -f "${config_file}" ]]; then
        log_error "Configuration file not found: ${config_file}"
        return 1
    fi
    
    # Check for constitutional hash in config
    if ! grep -q "${CONSTITUTIONAL_HASH}" "${config_file}"; then
        log_warning "Constitutional hash not found in ${config_file}"
    fi
    
    log_success "Configuration validated for ${service_name}"
    return 0
}

# Start infrastructure services
start_infrastructure() {
    local environment="${1:-development}"
    
    log_step "Starting infrastructure services for ${environment} environment"
    
    local compose_files="-f docker-compose.base-infrastructure.yml"
    
    if [[ -n "${ENV_CONFIGS[$environment]}" ]]; then
        compose_files="${compose_files} -f ${ENV_CONFIGS[$environment]}"
    fi
    
    log_debug "Using compose files: ${compose_files}"
    
    cd "${PROJECT_ROOT}/infrastructure/docker" || {
        log_error "Failed to change to infrastructure directory"
        return 1
    }
    
    if docker-compose ${compose_files} up -d; then
        log_success "Infrastructure services started successfully"
        return 0
    else
        log_error "Failed to start infrastructure services"
        return 1
    fi
}

# Start ACGS services
start_acgs_services() {
    local environment="${1:-development}"
    
    log_step "Starting ACGS services for ${environment} environment"
    
    local compose_files="-f docker-compose.base-infrastructure.yml -f docker-compose.acgs-services.yml"
    
    if [[ -n "${ENV_CONFIGS[$environment]}" ]]; then
        compose_files="${compose_files} -f ${ENV_CONFIGS[$environment]}"
    fi
    
    log_debug "Using compose files: ${compose_files}"
    
    cd "${PROJECT_ROOT}/infrastructure/docker" || {
        log_error "Failed to change to infrastructure directory"
        return 1
    }
    
    if docker-compose ${compose_files} up -d; then
        log_success "ACGS services started successfully"
        return 0
    else
        log_error "Failed to start ACGS services"
        return 1
    fi
}

# Start monitoring stack
start_monitoring() {
    local environment="${1:-development}"
    
    log_step "Starting monitoring stack for ${environment} environment"
    
    cd "${PROJECT_ROOT}/infrastructure/monitoring" || {
        log_error "Failed to change to monitoring directory"
        return 1
    }
    
    if docker-compose -f config/docker/docker-compose.monitoring-consolidated.yml up -d; then
        log_success "Monitoring stack started successfully"
        return 0
    else
        log_error "Failed to start monitoring stack"
        return 1
    fi
}

# Stop services
stop_services() {
    local service_type="${1:-all}"
    
    log_step "Stopping ${service_type} services"
    
    case "${service_type}" in
        "infrastructure")
            cd "${PROJECT_ROOT}/infrastructure/docker" || return 1
            docker-compose -f config/docker/docker-compose.base-infrastructure.yml down
            ;;
        "services")
            cd "${PROJECT_ROOT}/infrastructure/docker" || return 1
            docker-compose -f config/docker/docker-compose.acgs-services.yml down
            ;;
        "monitoring")
            cd "${PROJECT_ROOT}/infrastructure/monitoring" || return 1
            docker-compose -f config/docker/docker-compose.monitoring-consolidated.yml down
            ;;
        "all")
            stop_services "monitoring"
            stop_services "services"
            stop_services "infrastructure"
            ;;
        *)
            log_error "Unknown service type: ${service_type}"
            return 1
            ;;
    esac
    
    log_success "${service_type} services stopped"
    return 0
}

# Health check all services
health_check_all() {
    local failed_services=()
    
    log_step "Performing health checks on all services"
    
    # Check infrastructure services
    for service in postgres redis; do
        local port="${INFRASTRUCTURE_PORTS[$service]}"
        if [[ -n "${port}" ]]; then
            if ! check_service_health "${service}" "${port}" "/"; then
                failed_services+=("${service}")
            fi
        fi
    done
    
    # Check ACGS services
    for service in "${!DEFAULT_SERVICES[@]}"; do
        local port="${DEFAULT_SERVICES[$service]}"
        if ! check_service_health "${service}" "${port}" "/health"; then
            failed_services+=("${service}")
        fi
    done
    
    if [[ ${#failed_services[@]} -eq 0 ]]; then
        log_success "All services are healthy"
        return 0
    else
        log_error "Failed health checks for: ${failed_services[*]}"
        return 1
    fi
}

# Validate performance targets
validate_performance_targets() {
    log_step "Validating performance targets"
    
    # This would typically involve more sophisticated monitoring
    log_info "P99 Latency Target: ${P99_LATENCY_TARGET}"
    log_info "Throughput Target: ${THROUGHPUT_TARGET}"
    log_info "Cache Hit Rate Target: ${CACHE_HIT_RATE_TARGET}"
    
    # Placeholder for actual performance validation
    log_warning "Performance validation not yet implemented"
    return 0
}

# Deploy full stack
deploy_full_stack() {
    local environment="${1:-development}"
    
    log_step "Deploying full ACGS-2 stack for ${environment} environment"
    
    # Initialize
    init_logging
    
    # Validate environment
    if ! validate_constitutional_hash; then
        return 1
    fi
    
    if ! check_docker || ! check_docker_compose; then
        return 1
    fi
    
    # Deploy infrastructure
    if ! start_infrastructure "${environment}"; then
        return 1
    fi
    
    # Wait for infrastructure to be ready
    log_step "Waiting for infrastructure services to be ready..."
    wait_for_service "postgres" "${INFRASTRUCTURE_PORTS[postgres]}" 30 10 "/"
    wait_for_service "redis" "${INFRASTRUCTURE_PORTS[redis]}" 30 10 "/"
    
    # Deploy ACGS services
    if ! start_acgs_services "${environment}"; then
        return 1
    fi
    
    # Wait for services to be ready
    log_step "Waiting for ACGS services to be ready..."
    for service in "${!DEFAULT_SERVICES[@]}"; do
        wait_for_service "${service}" "${DEFAULT_SERVICES[$service]}" 30 10 "/health"
    done
    
    # Deploy monitoring
    if ! start_monitoring "${environment}"; then
        return 1
    fi
    
    # Final health check
    if ! health_check_all; then
        log_error "Deployment completed with health check failures"
        return 1
    fi
    
    # Validate performance
    validate_performance_targets
    
    log_success "Full ACGS-2 stack deployed successfully for ${environment} environment"
    log_info "Services available at:"
    for service in "${!DEFAULT_SERVICES[@]}"; do
        log_info "  - ${service}: http://localhost:${DEFAULT_SERVICES[$service]}"
    done
    log_info "  - Prometheus: http://localhost:${INFRASTRUCTURE_PORTS[prometheus]}"
    log_info "  - Grafana: http://localhost:${INFRASTRUCTURE_PORTS[grafana]}"
    
    return 0
}

# Print usage information
usage() {
    cat << EOF
ACGS-2 Deployment Library
Constitutional Hash: ${CONSTITUTIONAL_HASH}

Available functions:
  init_logging                    - Initialize logging
  validate_constitutional_hash    - Validate constitutional hash
  check_docker                   - Check Docker availability
  check_docker_compose           - Check Docker Compose availability
  wait_for_service               - Wait for service to be healthy
  check_service_health           - Check service health
  validate_service_config        - Validate service configuration
  start_infrastructure           - Start infrastructure services
  start_acgs_services           - Start ACGS services
  start_monitoring              - Start monitoring stack
  stop_services                 - Stop services
  health_check_all              - Health check all services
  validate_performance_targets   - Validate performance targets
  deploy_full_stack             - Deploy full stack

Environment variables:
  DEBUG                         - Enable debug logging (default: false)
  ENVIRONMENT                   - Deployment environment (default: development)

Examples:
  source deployment_lib.sh
  deploy_full_stack production
  health_check_all
  stop_services all
EOF
}

# Export functions for use in other scripts
export -f log_info log_success log_error log_warning log_debug log_step
export -f init_logging cleanup validate_constitutional_hash
export -f check_docker check_docker_compose
export -f wait_for_service check_service_health validate_service_config
export -f start_infrastructure start_acgs_services start_monitoring stop_services
export -f health_check_all validate_performance_targets deploy_full_stack
export -f usage