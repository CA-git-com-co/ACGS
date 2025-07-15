#!/bin/bash
# ACGS Service Deployment Validation Script
# Constitutional hash: cdd01ef066bc6cf2

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Constitutional compliance
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

# Service configuration
declare -A SERVICES=(
    ["postgres"]="5439:acgs_postgres:required"
    ["redis"]="6389:acgs_redis:required"
    ["opa"]="8181:acgs_opa:required"
    ["api_gateway"]="8080:acgs_api_gateway:required"
    ["auth_service"]="8016:acgs_auth_service:optional"
    ["constitutional_core"]="8001:acgs_constitutional_core:required"
    ["integrity_service"]="8002:acgs_integrity_service:required"
    ["governance_engine"]="8004:acgs_governance_engine:required"
    ["ec_service"]="8006:acgs_ec_service:required"
    ["opencode_cli"]="8020:acgs_opencode_cli:optional"
)

# Health endpoints
declare -A HEALTH_ENDPOINTS=(
    ["opa"]="http://localhost:8181/health"
    ["api_gateway"]="http://localhost:8080/gateway/health"
    ["auth_service"]="http://localhost:8016/health"
    ["constitutional_core"]="http://localhost:8001/health"
    ["integrity_service"]="http://localhost:8002/health"
    ["governance_engine"]="http://localhost:8004/health"
    ["ec_service"]="http://localhost:8006/health"
)

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

log_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

log_error() {
    echo -e "${RED}✗ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Check if Docker is running
check_docker() {
    log "Checking Docker status..."
    if ! docker info >/dev/null 2>&1; then
        log_error "Docker is not running or not accessible"
        exit 1
    fi
    log_success "Docker is running"
}

# Check if port is accessible
check_port() {
    local port=$1
    if command -v nc >/dev/null 2>&1; then
        nc -z localhost "$port" 2>/dev/null
    elif command -v timeout >/dev/null 2>&1; then
        timeout 3 bash -c "cat < /dev/null > /dev/tcp/localhost/$port" 2>/dev/null
    else
        # Fallback using Python
        python3 -c "import socket; s=socket.socket(); s.settimeout(3); exit(0 if s.connect_ex(('localhost', $port))==0 else 1)" 2>/dev/null
    fi
}

# Check service health endpoint
check_health_endpoint() {
    local endpoint=$1
    local service_name=$2
    
    if command -v curl >/dev/null 2>&1; then
        local response
        local http_code
        
        # Get response with timeout
        response=$(curl -s -w "%{http_code}" --connect-timeout 5 --max-time 10 "$endpoint" 2>/dev/null || echo "000")
        http_code="${response: -3}"
        
        if [[ "$http_code" == "200" ]]; then
            # Check for constitutional hash in response
            if echo "$response" | grep -q "$CONSTITUTIONAL_HASH" 2>/dev/null; then
                return 0
            else
                # Try constitutional-specific endpoint
                local constitutional_endpoint="${endpoint%/health}/health/constitutional"
                local const_response
                const_response=$(curl -s --connect-timeout 3 --max-time 5 "$constitutional_endpoint" 2>/dev/null || echo "")
                if echo "$const_response" | grep -q "$CONSTITUTIONAL_HASH" 2>/dev/null; then
                    return 0
                fi
                return 2  # Healthy but not constitutionally compliant
            fi
        else
            return 1  # Not healthy
        fi
    elif command -v wget >/dev/null 2>&1; then
        if wget -q --spider --timeout=5 "$endpoint" 2>/dev/null; then
            return 0
        else
            return 1
        fi
    else
        log_warning "No curl or wget available for health check"
        return 0
    fi
}

# Check container status
check_container() {
    local container_name=$1
    local status
    status=$(docker inspect --format='{{.State.Status}}' "$container_name" 2>/dev/null || echo "not_found")
    
    case "$status" in
        "running")
            return 0
            ;;
        "not_found")
            return 1
            ;;
        *)
            return 2
            ;;
    esac
}

# Validate single service
validate_service() {
    local service_name=$1
    local service_info=$2
    
    IFS=':' read -r port container_name required <<< "$service_info"
    
    echo ""
    log "Validating service: $service_name"
    echo "  Container: $container_name"
    echo "  Port: $port"
    echo "  Required: $required"
    
    local container_status=0
    local port_status=0
    local health_status=0
    local constitutional_status=0
    local overall_status=0
    
    # Check container
    if check_container "$container_name"; then
        log_success "  Container is running"
        container_status=1
    else
        log_error "  Container is not running"
        container_status=0
        overall_status=1
    fi
    
    # Check port accessibility
    if check_port "$port"; then
        log_success "  Port $port is accessible"
        port_status=1
    else
        log_error "  Port $port is not accessible"
        port_status=0
        if [[ "$required" == "required" ]]; then
            overall_status=1
        fi
    fi
    
    # Check health endpoint if available
    if [[ -n "${HEALTH_ENDPOINTS[$service_name]:-}" ]]; then
        local endpoint="${HEALTH_ENDPOINTS[$service_name]}"
        local health_result
        
        check_health_endpoint "$endpoint" "$service_name"
        health_result=$?
        
        case $health_result in
            0)
                log_success "  Health endpoint is responding and constitutionally compliant"
                health_status=1
                constitutional_status=1
                ;;
            1)
                log_error "  Health endpoint is not responding"
                health_status=0
                constitutional_status=0
                if [[ "$required" == "required" ]]; then
                    overall_status=1
                fi
                ;;
            2)
                log_warning "  Health endpoint is responding but not constitutionally compliant"
                health_status=1
                constitutional_status=0
                ;;
        esac
    else
        log "  No health endpoint defined"
        health_status=1
        constitutional_status=1
    fi
    
    # Store results in global arrays for summary
    SERVICE_CONTAINER_STATUS["$service_name"]=$container_status
    SERVICE_PORT_STATUS["$service_name"]=$port_status
    SERVICE_HEALTH_STATUS["$service_name"]=$health_status
    SERVICE_CONSTITUTIONAL_STATUS["$service_name"]=$constitutional_status
    SERVICE_OVERALL_STATUS["$service_name"]=$overall_status
    SERVICE_REQUIRED["$service_name"]=$required
}

# Generate summary report
generate_summary() {
    echo ""
    echo "================================================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "                    ACGS SERVICE DEPLOYMENT VALIDATION REPORT"
    echo "                    Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "                    Generated: $(date -Iseconds)"
    echo "================================================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo ""
    
    local total_services=${#SERVICES[@]}
    local running_services=0
    local healthy_services=0
    local compliant_services=0
    local required_services=0
    local required_running=0
    local failed_required=()
    local non_compliant=()
    
    echo "SUMMARY:"
    
    for service_name in "${!SERVICES[@]}"; do
        if [[ "${SERVICE_CONTAINER_STATUS[$service_name]}" == "1" ]]; then
            ((running_services++))
        fi
        
        if [[ "${SERVICE_HEALTH_STATUS[$service_name]}" == "1" ]]; then
            ((healthy_services++))
        fi
        
        if [[ "${SERVICE_CONSTITUTIONAL_STATUS[$service_name]}" == "1" ]]; then
            ((compliant_services++))
        fi
        
        if [[ "${SERVICE_REQUIRED[$service_name]}" == "required" ]]; then
            ((required_services++))
            if [[ "${SERVICE_CONTAINER_STATUS[$service_name]}" == "1" ]]; then
                ((required_running++))
            else
                failed_required+=("$service_name")
            fi
        fi
        
        if [[ "${SERVICE_CONSTITUTIONAL_STATUS[$service_name]}" == "0" && -n "${HEALTH_ENDPOINTS[$service_name]:-}" ]]; then
            non_compliant+=("$service_name")
        fi
    done
    
    echo "  Total Services: $total_services"
    echo "  Running: $running_services/$total_services"
    echo "  Healthy: $healthy_services/$total_services"
    echo "  Constitutional Compliant: $compliant_services/$total_services"
    echo "  Required Services Running: $required_running/$required_services"
    echo ""
    
    echo "DETAILED RESULTS:"
    echo ""
    
    for service_name in "${!SERVICES[@]}"; do
        IFS=':' read -r port container_name required <<< "${SERVICES[$service_name]}"
        echo "Service: ${service_name^^} (${required^^})"
        echo "  Container: $container_name"
        echo "  Port: $port"
        
        if [[ "${SERVICE_CONTAINER_STATUS[$service_name]}" == "1" ]]; then
            echo -e "  Running: ${GREEN}✓${NC}"
        else
            echo -e "  Running: ${RED}✗${NC}"
        fi
        
        if [[ "${SERVICE_PORT_STATUS[$service_name]}" == "1" ]]; then
            echo -e "  Port Accessible: ${GREEN}✓${NC}"
        else
            echo -e "  Port Accessible: ${RED}✗${NC}"
        fi
        
        if [[ "${SERVICE_HEALTH_STATUS[$service_name]}" == "1" ]]; then
            echo -e "  Healthy: ${GREEN}✓${NC}"
        else
            echo -e "  Healthy: ${RED}✗${NC}"
        fi
        
        if [[ "${SERVICE_CONSTITUTIONAL_STATUS[$service_name]}" == "1" ]]; then
            echo -e "  Constitutional Compliant: ${GREEN}✓${NC}"
        else
            echo -e "  Constitutional Compliant: ${RED}✗${NC}"
        fi
        
        echo ""
    done
    
    echo "RECOMMENDATIONS:"
    
    if [[ ${#failed_required[@]} -gt 0 ]]; then
        log_error "Critical: Start required services: ${failed_required[*]}"
    fi
    
    if [[ ${#non_compliant[@]} -gt 0 ]]; then
        log_warning "Compliance: Non-compliant services: ${non_compliant[*]}"
    fi
    
    if [[ ${#failed_required[@]} -eq 0 && ${#non_compliant[@]} -eq 0 ]]; then
        log_success "All services are properly deployed and compliant!"
    fi
    
    echo ""
    echo "================================================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    
    # Return exit code
    if [[ ${#failed_required[@]} -gt 0 ]]; then
        return 1
    else
        return 0
    fi
}

# Start missing services
start_missing_services() {
    local failed_required=()
    
    for service_name in "${!SERVICES[@]}"; do
        IFS=':' read -r port container_name required <<< "${SERVICES[$service_name]}"
        if [[ "$required" == "required" && "${SERVICE_CONTAINER_STATUS[$service_name]}" != "1" ]]; then
            failed_required+=("$service_name")
        fi
    done
    
    if [[ ${#failed_required[@]} -eq 0 ]]; then
        log_success "All required services are already running"
        return 0
    fi
    
    log "Starting missing required services: ${failed_required[*]}"
    
    if docker-compose -f infrastructure/docker/docker-compose.acgs.yml up -d "${failed_required[@]}" 2>/dev/null; then
        log_success "Services started successfully"
        return 0
    else
        log_error "Failed to start some services"
        return 1
    fi
}

# Main function
main() {
    echo "================================================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "                    ACGS Service Deployment Validation"
    echo "                    Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "================================================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    
    # Global arrays to store results
    declare -A SERVICE_CONTAINER_STATUS
    declare -A SERVICE_PORT_STATUS
    declare -A SERVICE_HEALTH_STATUS
    declare -A SERVICE_CONSTITUTIONAL_STATUS
    declare -A SERVICE_OVERALL_STATUS
    declare -A SERVICE_REQUIRED
    
    # Check Docker
    check_docker
    
    # Validate each service
    for service_name in "${!SERVICES[@]}"; do
        validate_service "$service_name" "${SERVICES[$service_name]}"
    done
    
    # Generate summary and get exit code
    if generate_summary; then
        echo ""
        log_success "Validation PASSED: All required services are running"
        exit 0
    else
        echo ""
        log_error "Validation FAILED: Some required services are not running"
        
        # Ask user if they want to start missing services
        echo ""
        read -p "Would you like to start missing services? (y/N): " -n 1 -r
        echo ""
        
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            start_missing_services
            echo ""
            log "Services started. Run validation again to verify."
        fi
        
        exit 1
    fi
}

# Run main function with error handling
if ! main "$@"; then
    log_error "Validation script failed"
    exit 1
fi
