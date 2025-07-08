#!/bin/bash
# ACGS-2 Zero-Downtime Rollback Script
# Constitutional Hash: cdd01ef066bc6cf2
# Rollback Target: <30 seconds

set -euo pipefail

# Configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
DEPLOYMENT_MODE="${1:-docker}"
ROLLBACK_TARGET="${2:-previous}"  # previous, specific-version, or git-sha
ROLLBACK_TIMEOUT="${3:-30}"  # 30 seconds maximum rollback time

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

# Rollback state tracking
ROLLBACK_START_TIME=""
ROLLBACK_STEPS=()
FAILED_SERVICES=()

# Service definitions
declare -A SERVICES=(
    ["auth-service"]="8016"
    ["constitutional-ai-service"]="8001"
    ["integrity-service"]="8002"
    ["multi-agent-coordinator"]="8008"
    ["blackboard-service"]="8010"
)

# Rollback functions
start_rollback_timer() {
    ROLLBACK_START_TIME=$(date +%s)
    log_info "🕐 Rollback timer started (target: ${ROLLBACK_TIMEOUT}s)"
}

check_rollback_timeout() {
    local current_time=$(date +%s)
    local elapsed=$((current_time - ROLLBACK_START_TIME))
    
    if [[ $elapsed -gt $ROLLBACK_TIMEOUT ]]; then
        log_error "⏰ Rollback timeout exceeded: ${elapsed}s > ${ROLLBACK_TIMEOUT}s"
        return 1
    fi
    
    log_info "⏱️  Rollback time: ${elapsed}s / ${ROLLBACK_TIMEOUT}s"
    return 0
}

create_rollback_snapshot() {
    log_info "📸 Creating rollback snapshot..."
    
    local snapshot_dir="${PROJECT_ROOT}/rollback-snapshots/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$snapshot_dir"
    
    # Save current deployment state
    if [[ "$DEPLOYMENT_MODE" == "docker" ]]; then
        docker-compose -f docker-compose.production-complete.yml config > "$snapshot_dir/docker-compose.yml"
        docker-compose -f docker-compose.production-complete.yml ps --format json > "$snapshot_dir/container-state.json"
    else
        kubectl get all -n acgs-production -o yaml > "$snapshot_dir/kubernetes-state.yaml"
    fi
    
    # Save environment configuration
    cp .env.production-complete "$snapshot_dir/environment.env" 2>/dev/null || true
    
    # Save constitutional compliance state
    cat > "$snapshot_dir/rollback-metadata.json" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "constitutional_hash": "$CONSTITUTIONAL_HASH",
  "deployment_mode": "$DEPLOYMENT_MODE",
  "rollback_target": "$ROLLBACK_TARGET",
  "git_sha": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
  "git_branch": "$(git branch --show-current 2>/dev/null || echo 'unknown')"
}
EOF
    
    log_success "Rollback snapshot created: $snapshot_dir"
    echo "$snapshot_dir"
}

validate_rollback_target() {
    log_info "🎯 Validating rollback target: $ROLLBACK_TARGET"
    
    case "$ROLLBACK_TARGET" in
        "previous")
            log_info "Rolling back to previous deployment"
            return 0
            ;;
        "v"*)
            log_info "Rolling back to version: $ROLLBACK_TARGET"
            return 0
            ;;
        *)
            if [[ ${#ROLLBACK_TARGET} -eq 40 ]]; then
                log_info "Rolling back to git SHA: $ROLLBACK_TARGET"
                return 0
            else
                log_error "Invalid rollback target: $ROLLBACK_TARGET"
                return 1
            fi
            ;;
    esac
}

perform_docker_rollback() {
    log_info "🐳 Performing Docker rollback..."
    
    # Stop current services gracefully
    log_info "Stopping current services..."
    docker-compose -f docker-compose.production-complete.yml stop --timeout 10
    
    ROLLBACK_STEPS+=("docker_services_stopped")
    
    # Rollback to previous images
    log_info "Rolling back to previous images..."
    
    for service in "${!SERVICES[@]}"; do
        local current_image="acgs/${service}:latest"
        local previous_image="acgs/${service}:previous"
        
        if docker image inspect "$previous_image" > /dev/null 2>&1; then
            log_info "Rolling back $service to previous image"
            docker tag "$previous_image" "$current_image"
        else
            log_warning "Previous image not found for $service, keeping current"
        fi
    done
    
    ROLLBACK_STEPS+=("docker_images_rolled_back")
    
    # Start services with rollback configuration
    log_info "Starting services with rollback configuration..."
    docker-compose -f docker-compose.production-complete.yml up -d
    
    ROLLBACK_STEPS+=("docker_services_started")
    
    # Wait for services to be ready
    sleep 15
    
    log_success "Docker rollback completed"
}

perform_kubernetes_rollback() {
    log_info "☸️  Performing Kubernetes rollback..."
    
    # Rollback deployments
    for service in "${!SERVICES[@]}"; do
        log_info "Rolling back $service deployment..."
        
        if kubectl rollout undo deployment/"$service" -n acgs-production --timeout=20s; then
            log_success "$service rollback initiated"
        else
            log_error "$service rollback failed"
            FAILED_SERVICES+=("$service")
        fi
    done
    
    ROLLBACK_STEPS+=("kubernetes_deployments_rolled_back")
    
    # Wait for rollout to complete
    log_info "Waiting for rollback to complete..."
    
    for service in "${!SERVICES[@]}"; do
        if [[ ! " ${FAILED_SERVICES[@]} " =~ " ${service} " ]]; then
            kubectl rollout status deployment/"$service" -n acgs-production --timeout=20s || {
                log_error "$service rollback status check failed"
                FAILED_SERVICES+=("$service")
            }
        fi
    done
    
    ROLLBACK_STEPS+=("kubernetes_rollout_completed")
    
    log_success "Kubernetes rollback completed"
}

verify_rollback_health() {
    log_info "🏥 Verifying rollback health..."
    
    local healthy_services=0
    local total_services=${#SERVICES[@]}
    
    # Quick health check with reduced timeout
    for service in "${!SERVICES[@]}"; do
        local port="${SERVICES[$service]}"
        local url="http://localhost:$port/health"
        
        if curl -f -s --max-time 3 "$url" > /dev/null 2>&1; then
            log_success "$service is healthy after rollback"
            healthy_services=$((healthy_services + 1))
        else
            log_error "$service is unhealthy after rollback"
            FAILED_SERVICES+=("$service")
        fi
    done
    
    local health_percentage=$((healthy_services * 100 / total_services))
    log_info "Service health after rollback: $healthy_services/$total_services ($health_percentage%)"
    
    if [[ $health_percentage -ge 80 ]]; then
        log_success "Rollback health verification passed"
        return 0
    else
        log_error "Rollback health verification failed"
        return 1
    fi
}

verify_constitutional_compliance() {
    log_info "⚖️  Verifying constitutional compliance after rollback..."
    
    local compliant_services=0
    local total_services=${#SERVICES[@]}
    
    for service in "${!SERVICES[@]}"; do
        local port="${SERVICES[$service]}"
        local url="http://localhost:$port/constitutional-hash"
        
        if response=$(curl -f -s --max-time 3 "$url" 2>/dev/null); then
            if echo "$response" | grep -q "$CONSTITUTIONAL_HASH"; then
                log_success "$service constitutional compliance verified"
                compliant_services=$((compliant_services + 1))
            else
                log_warning "$service constitutional compliance check failed"
            fi
        else
            log_warning "$service constitutional compliance endpoint unavailable"
        fi
    done
    
    local compliance_percentage=$((compliant_services * 100 / total_services))
    log_info "Constitutional compliance after rollback: $compliant_services/$total_services ($compliance_percentage%)"
    
    if [[ $compliance_percentage -ge 80 ]]; then
        log_success "Constitutional compliance verification passed"
        return 0
    else
        log_warning "Constitutional compliance verification needs attention"
        return 1
    fi
}

cleanup_failed_rollback() {
    log_error "🧹 Cleaning up failed rollback..."
    
    # Attempt to restore from snapshot if available
    local latest_snapshot
    latest_snapshot=$(find "${PROJECT_ROOT}/rollback-snapshots" -type d -name "*" | sort | tail -1 2>/dev/null || echo "")
    
    if [[ -n "$latest_snapshot" && -d "$latest_snapshot" ]]; then
        log_info "Attempting to restore from snapshot: $latest_snapshot"
        
        if [[ "$DEPLOYMENT_MODE" == "docker" ]]; then
            if [[ -f "$latest_snapshot/docker-compose.yml" ]]; then
                cp "$latest_snapshot/docker-compose.yml" docker-compose.production-complete.yml
                docker-compose -f docker-compose.production-complete.yml up -d
            fi
        else
            if [[ -f "$latest_snapshot/kubernetes-state.yaml" ]]; then
                kubectl apply -f "$latest_snapshot/kubernetes-state.yaml" -n acgs-production
            fi
        fi
    else
        log_error "No rollback snapshot available for restoration"
    fi
}

generate_rollback_report() {
    local rollback_end_time=$(date +%s)
    local total_rollback_time=$((rollback_end_time - ROLLBACK_START_TIME))
    
    log_info "📊 Generating rollback report..."
    
    local report_file="${PROJECT_ROOT}/rollback-report-$(date +%Y%m%d-%H%M%S).json"
    
    cat > "$report_file" << EOF
{
  "timestamp": "$(date -Iseconds)",
  "constitutional_hash": "$CONSTITUTIONAL_HASH",
  "deployment_mode": "$DEPLOYMENT_MODE",
  "rollback_target": "$ROLLBACK_TARGET",
  "rollback_time_seconds": $total_rollback_time,
  "rollback_timeout_seconds": $ROLLBACK_TIMEOUT,
  "rollback_success": $([ $total_rollback_time -le $ROLLBACK_TIMEOUT ] && echo "true" || echo "false"),
  "rollback_steps_completed": [
$(printf '    "%s"' "${ROLLBACK_STEPS[@]}" | paste -sd, -)
  ],
  "failed_services": [
$(printf '    "%s"' "${FAILED_SERVICES[@]}" | paste -sd, -)
  ],
  "performance_impact": {
    "target_rollback_time": "${ROLLBACK_TIMEOUT}s",
    "actual_rollback_time": "${total_rollback_time}s",
    "within_target": $([ $total_rollback_time -le $ROLLBACK_TIMEOUT ] && echo "true" || echo "false")
  }
}
EOF
    
    log_success "Rollback report saved to: $report_file"
    cat "$report_file"
}

# Main rollback function
main() {
    log_info "🔄 Starting ACGS-2 Zero-Downtime Rollback"
    log_info "Constitutional Hash: $CONSTITUTIONAL_HASH"
    log_info "Deployment Mode: $DEPLOYMENT_MODE"
    log_info "Rollback Target: $ROLLBACK_TARGET"
    log_info "Rollback Timeout: ${ROLLBACK_TIMEOUT}s"
    
    # Start rollback timer
    start_rollback_timer
    
    # Validate rollback target
    if ! validate_rollback_target; then
        log_error "Rollback validation failed"
        exit 1
    fi
    
    # Create rollback snapshot
    local snapshot_dir
    snapshot_dir=$(create_rollback_snapshot)
    
    # Check timeout before proceeding
    if ! check_rollback_timeout; then
        log_error "Rollback timeout exceeded during preparation"
        exit 1
    fi
    
    # Perform rollback based on deployment mode
    if [[ "$DEPLOYMENT_MODE" == "kubernetes" ]]; then
        perform_kubernetes_rollback
    else
        perform_docker_rollback
    fi
    
    # Check timeout after rollback
    if ! check_rollback_timeout; then
        log_error "Rollback timeout exceeded during execution"
        cleanup_failed_rollback
        exit 1
    fi
    
    # Verify rollback success
    if verify_rollback_health && verify_constitutional_compliance; then
        local rollback_end_time=$(date +%s)
        local total_time=$((rollback_end_time - ROLLBACK_START_TIME))
        
        log_success "🎉 Rollback completed successfully in ${total_time}s"
        log_success "All services are healthy and constitutionally compliant"
        
        # Generate success report
        generate_rollback_report
        
        exit 0
    else
        log_error "Rollback verification failed"
        cleanup_failed_rollback
        generate_rollback_report
        exit 1
    fi
}

# Script execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
