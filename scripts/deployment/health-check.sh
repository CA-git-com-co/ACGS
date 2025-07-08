#!/bin/bash
# ACGS-2 Comprehensive Health Check Script
# Constitutional Hash: cdd01ef066bc6cf2
# Performance Targets: P99 <5ms, >100 RPS, >85% cache hit

set -euo pipefail

# Configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DEPLOYMENT_MODE="${1:-docker}"
ENVIRONMENT="${2:-production}"
TIMEOUT="${3:-300}"  # 5 minutes default timeout
CHECK_INTERVAL="${4:-10}"  # 10 seconds between checks

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Health check results
HEALTH_RESULTS=()
FAILED_CHECKS=0
TOTAL_CHECKS=0

# Service definitions
declare -A SERVICES=(
    ["auth-service"]="8016"
    ["constitutional-ai-service"]="8001"
    ["integrity-service"]="8002"
    ["multi-agent-coordinator"]="8008"
    ["blackboard-service"]="8010"
)

declare -A INFRASTRUCTURE=(
    ["postgres"]="5439"
    ["redis"]="6389"
    ["prometheus"]="9090"
    ["grafana"]="3000"
)

# Health check functions
check_service_health() {
    local service_name="$1"
    local port="$2"
    local endpoint="${3:-/health}"

    log_info "Checking health of $service_name on port $port..."

    local url="http://localhost:$port$endpoint"
    local start_time=$(date +%s%N)

    if curl -f -s --max-time 10 "$url" > /dev/null 2>&1; then
        local end_time=$(date +%s%N)
        local response_time=$(( (end_time - start_time) / 1000000 ))  # Convert to milliseconds

        log_success "$service_name is healthy (${response_time}ms)"
        HEALTH_RESULTS+=("$service_name:HEALTHY:${response_time}ms")
        return 0
    else
        log_error "$service_name health check failed"
        HEALTH_RESULTS+=("$service_name:UNHEALTHY:timeout")
        FAILED_CHECKS=$((FAILED_CHECKS + 1))
        return 1
    fi
}

check_constitutional_compliance() {
    local service_name="$1"
    local port="$2"

    log_info "Checking constitutional compliance for $service_name..."

    local url="http://localhost:$port/constitutional-hash"

    if response=$(curl -f -s --max-time 5 "$url" 2>/dev/null); then
        if echo "$response" | grep -q "$CONSTITUTIONAL_HASH"; then
            log_success "$service_name constitutional compliance verified"
            return 0
        else
            log_warning "$service_name returned incorrect constitutional hash"
            return 1
        fi
    else
        log_warning "$service_name constitutional compliance endpoint not available"
        return 1
    fi
}

check_performance_metrics() {
    local service_name="$1"
    local port="$2"

    log_info "Checking performance metrics for $service_name..."

    local metrics_url="http://localhost:$port/metrics"

    if curl -f -s --max-time 5 "$metrics_url" > /dev/null 2>&1; then
        log_success "$service_name metrics endpoint available"
        return 0
    else
        log_warning "$service_name metrics endpoint not available"
        return 1
    fi
}

check_database_health() {
    log_info "Checking PostgreSQL database health..."

    if [[ "$DEPLOYMENT_MODE" == "docker" ]]; then
        if docker exec acgs_postgres_prod pg_isready -U acgs_production_user -d acgs_production > /dev/null 2>&1; then
            log_success "PostgreSQL is healthy"

            # Check constitutional compliance in database
            local compliance_check
            compliance_check=$(docker exec acgs_postgres_prod psql -U acgs_production_user -d acgs_production -t -c "SELECT COUNT(*) FROM constitutional_compliance WHERE hash = '$CONSTITUTIONAL_HASH';" 2>/dev/null | xargs)

            if [[ "$compliance_check" -gt 0 ]]; then
                log_success "Database constitutional compliance verified"
            else
                log_warning "Database constitutional compliance records not found"
            fi

            return 0
        else
            log_error "PostgreSQL health check failed"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            return 1
        fi
    else
        # Kubernetes health check
        if kubectl get pods -n acgs-production -l app=postgres -o jsonpath='{.items[0].status.phase}' | grep -q "Running"; then
            log_success "PostgreSQL pod is running"
            return 0
        else
            log_error "PostgreSQL pod is not running"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            return 1
        fi
    fi
}

check_redis_health() {
    log_info "Checking Redis cache health..."

    if [[ "$DEPLOYMENT_MODE" == "docker" ]]; then
        if docker exec acgs_redis_prod redis-cli ping > /dev/null 2>&1; then
            log_success "Redis is healthy"

            # Check cache performance
            local cache_info
            cache_info=$(docker exec acgs_redis_prod redis-cli info stats 2>/dev/null | grep keyspace_hits || echo "keyspace_hits:0")
            log_info "Redis cache stats: $cache_info"

            return 0
        else
            log_error "Redis health check failed"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            return 1
        fi
    else
        # Kubernetes health check
        if kubectl get pods -n acgs-production -l app=redis -o jsonpath='{.items[0].status.phase}' | grep -q "Running"; then
            log_success "Redis pod is running"
            return 0
        else
            log_error "Redis pod is not running"
            FAILED_CHECKS=$((FAILED_CHECKS + 1))
            return 1
        fi
    fi
}

check_monitoring_stack() {
    log_info "Checking monitoring stack health..."

    # Prometheus
    if curl -f -s --max-time 10 "http://localhost:9090/-/healthy" > /dev/null 2>&1; then
        log_success "Prometheus is healthy"
    else
        log_warning "Prometheus health check failed"
    fi

    # Grafana
    if curl -f -s --max-time 10 "http://localhost:3000/api/health" > /dev/null 2>&1; then
        log_success "Grafana is healthy"
    else
        log_warning "Grafana health check failed"
    fi
}

check_load_balancer() {
    log_info "Checking load balancer health..."

    if curl -f -s --max-time 10 "http://localhost/health" > /dev/null 2>&1; then
        log_success "Load balancer is healthy"
    else
        log_warning "Load balancer health check failed"
    fi
}

perform_readiness_checks() {
    log_info "Performing readiness checks..."

    local ready_services=0
    local total_services=${#SERVICES[@]}

    for service in "${!SERVICES[@]}"; do
        local port="${SERVICES[$service]}"

        if check_service_health "$service" "$port" "/ready"; then
            ready_services=$((ready_services + 1))
        fi
    done

    local readiness_percentage=$((ready_services * 100 / total_services))
    log_info "Service readiness: $ready_services/$total_services ($readiness_percentage%)"

    if [[ $readiness_percentage -ge 80 ]]; then
        log_success "Readiness check passed"
        return 0
    else
        log_error "Readiness check failed"
        return 1
    fi
}

perform_liveness_checks() {
    log_info "Performing liveness checks..."

    local live_services=0
    local total_services=${#SERVICES[@]}

    for service in "${!SERVICES[@]}"; do
        local port="${SERVICES[$service]}"

        if check_service_health "$service" "$port" "/health"; then
            live_services=$((live_services + 1))
        fi

        TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    done

    local liveness_percentage=$((live_services * 100 / total_services))
    log_info "Service liveness: $live_services/$total_services ($liveness_percentage%)"

    if [[ $liveness_percentage -eq 100 ]]; then
        log_success "Liveness check passed"
        return 0
    else
        log_error "Liveness check failed"
        return 1
    fi
}

perform_constitutional_compliance_checks() {
    log_info "Performing constitutional compliance checks..."

    local compliant_services=0
    local total_services=${#SERVICES[@]}

    for service in "${!SERVICES[@]}"; do
        local port="${SERVICES[$service]}"

        if check_constitutional_compliance "$service" "$port"; then
            compliant_services=$((compliant_services + 1))
        fi
    done

    local compliance_percentage=$((compliant_services * 100 / total_services))
    log_info "Constitutional compliance: $compliant_services/$total_services ($compliance_percentage%)"

    if [[ $compliance_percentage -ge 80 ]]; then
        log_success "Constitutional compliance check passed"
        return 0
    else
        log_error "Constitutional compliance check failed"
        return 1
    fi
}

perform_performance_checks() {
    log_info "Performing performance checks..."

    # Simple performance test
    local test_url="http://localhost:8016/health"
    local start_time=$(date +%s%N)

    if curl -f -s --max-time 5 "$test_url" > /dev/null; then
        local end_time=$(date +%s%N)
        local response_time=$(( (end_time - start_time) / 1000000 ))  # Convert to milliseconds

        if [[ $response_time -lt 5 ]]; then
            log_success "Performance check passed: ${response_time}ms < 5ms target"
            return 0
        else
            log_warning "Performance check: ${response_time}ms exceeds 5ms target"
            return 1
        fi
    else
        log_error "Performance check failed: request timeout"
        return 1
    fi
}

wait_for_services() {
    log_info "Waiting for services to be ready (timeout: ${TIMEOUT}s)..."

    local elapsed=0
    local all_healthy=false

    while [[ $elapsed -lt $TIMEOUT ]]; do
        log_info "Health check attempt $((elapsed / CHECK_INTERVAL + 1))..."

        local healthy_count=0
        local total_count=${#SERVICES[@]}

        for service in "${!SERVICES[@]}"; do
            local port="${SERVICES[$service]}"

            if curl -f -s --max-time 5 "http://localhost:$port/health" > /dev/null 2>&1; then
                healthy_count=$((healthy_count + 1))
            fi
        done

        log_info "Healthy services: $healthy_count/$total_count"

        if [[ $healthy_count -eq $total_count ]]; then
            all_healthy=true
            break
        fi

        sleep $CHECK_INTERVAL
        elapsed=$((elapsed + CHECK_INTERVAL))
    done

    if [[ "$all_healthy" == "true" ]]; then
        log_success "All services are healthy after ${elapsed}s"
        return 0
    else
        log_error "Services failed to become healthy within ${TIMEOUT}s"
        return 1
    fi
}

generate_health_report() {
    log_info "Generating health check report..."

    local report_file="${PROJECT_ROOT}/health-check-report-$(date +%Y%m%d-%H%M%S).json"

    cat > "$report_file" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "constitutional_hash": "$CONSTITUTIONAL_HASH",
  "deployment_mode": "$DEPLOYMENT_MODE",
  "environment": "$ENVIRONMENT",
  "total_checks": $TOTAL_CHECKS,
  "failed_checks": $FAILED_CHECKS,
  "success_rate": $(( (TOTAL_CHECKS - FAILED_CHECKS) * 100 / TOTAL_CHECKS ))%,
  "health_results": [
$(printf '    "%s"' "${HEALTH_RESULTS[@]}" | paste -sd, -)
  ],
  "performance_targets": {
    "p99_latency_ms": 5,
    "throughput_rps": 100,
    "cache_hit_rate": 85
  }
}
EOF

    log_success "Health check report saved to: $report_file"
    cat "$report_file"
}

# Main health check function
main() {
    log_info "Starting ACGS-2 Health Check"
    log_info "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log_info "Deployment Mode: $DEPLOYMENT_MODE"
    log_info "Environment: $ENVIRONMENT"
    log_info "Timeout: ${TIMEOUT}s"

    # Wait for services to be ready
    if ! wait_for_services; then
        log_error "Services failed to become ready"
        exit 1
    fi

    # Perform comprehensive health checks
    log_info "Performing comprehensive health checks..."

    # Infrastructure checks
    check_database_health
    check_redis_health
    check_monitoring_stack
    check_load_balancer

    # Service checks
    perform_readiness_checks
    perform_liveness_checks
    perform_constitutional_compliance_checks
    perform_performance_checks

    # Generate report
    generate_health_report

    # Final assessment
    if [[ $FAILED_CHECKS -eq 0 ]]; then
        log_success "All health checks passed! 🎉"
        log_success "ACGS-2 deployment is healthy and constitutionally compliant"
        exit 0
    else
        log_error "Health checks failed: $FAILED_CHECKS failures detected"
        log_error "ACGS-2 deployment requires attention"
        exit 1
    fi
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
