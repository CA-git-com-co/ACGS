#!/bin/bash

# ACGE Phase 2 Traffic Routing Controller
# Manages blue-green traffic shifting with constitutional compliance monitoring

set -euo pipefail

# Configuration
NAMESPACE_SHARED="acgs-shared"
NAMESPACE_BLUE="acgs-blue"
NAMESPACE_GREEN="acgs-green"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN}[✓] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[⚠] $1${NC}"
}

error() {
    echo -e "${RED}[✗] $1${NC}"
}

# Service list for migration
SERVICES=(
    "auth:8000"
    "ac:8001"
    "integrity:8002"
    "fv:8003"
    "gs:8004"
    "pgc:8005"
    "ec:8006"
)

# Get current traffic weights
get_traffic_weights() {
    local service_name=$1
    local service_port=$2
    
    kubectl get virtualservice acgs-blue-green-routing -n "$NAMESPACE_SHARED" -o yaml | \
        grep -A 20 "prefix: /api/v1/$service_name" | \
        grep -E "weight: [0-9]+" | \
        awk '{print $2}'
}

# Update traffic weights for a service
update_traffic_weights() {
    local service_name=$1
    local service_port=$2
    local blue_weight=$3
    local green_weight=$4
    
    log "Updating traffic weights for $service_name: Blue=$blue_weight%, Green=$green_weight%"
    
    # Create temporary patch file
    cat > /tmp/traffic-patch.yaml << EOF
spec:
  http:
    - match:
        - uri:
            prefix: /api/v1/$service_name
      route:
        - destination:
            host: acgs-$service_name-service-blue.$NAMESPACE_BLUE.svc.cluster.local
            port:
              number: $service_port
          weight: $blue_weight
        - destination:
            host: acgs-$service_name-service-green.$NAMESPACE_GREEN.svc.cluster.local
            port:
              number: $service_port
          weight: $green_weight
      headers:
        request:
          add:
            x-constitutional-hash: "$CONSTITUTIONAL_HASH"
            x-acge-phase: "phase-2"
EOF
    
    # Apply the patch
    kubectl patch virtualservice acgs-blue-green-routing -n "$NAMESPACE_SHARED" --patch-file /tmp/traffic-patch.yaml
    
    # Clean up
    rm -f /tmp/traffic-patch.yaml
    
    success "Traffic weights updated for $service_name"
}

# Monitor constitutional compliance
check_constitutional_compliance() {
    local service_name=$1
    local service_port=$2
    local environment=$3
    
    log "Checking constitutional compliance for $service_name in $environment environment..."
    
    # Get service endpoint
    local service_url
    if [[ "$environment" == "blue" ]]; then
        service_url="http://acgs-$service_name-service-blue.$NAMESPACE_BLUE.svc.cluster.local:$service_port"
    else
        service_url="http://acgs-$service_name-service-green.$NAMESPACE_GREEN.svc.cluster.local:$service_port"
    fi
    
    # Check health endpoint
    if kubectl run compliance-check-$service_name --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f -s "$service_url/health" >/dev/null 2>&1; then
        
        # Check constitutional compliance if available
        if kubectl run compliance-check-$service_name-constitutional --image=curlimages/curl --rm -i --restart=Never -- \
            curl -f -s "$service_url/health/constitutional" >/dev/null 2>&1; then
            success "Constitutional compliance verified for $service_name ($environment)"
            return 0
        else
            warning "Constitutional compliance endpoint not available for $service_name ($environment)"
            return 1
        fi
    else
        error "Health check failed for $service_name ($environment)"
        return 1
    fi
}

# Monitor performance metrics
check_performance_metrics() {
    local service_name=$1
    local environment=$2
    
    log "Checking performance metrics for $service_name in $environment environment..."
    
    # Query Prometheus for response time metrics
    local prometheus_url="http://acgs-prometheus.$NAMESPACE_SHARED.svc.cluster.local:9090"
    local query="histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{service=\"$service_name\",environment=\"$environment\"}[5m]))"
    
    # Check if response time is under 2 seconds
    local response_time
    response_time=$(kubectl run metrics-check-$service_name --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s "$prometheus_url/api/v1/query?query=$query" | \
        grep -o '"result":\[{"metric":{},"value":\[[0-9.]*,"[0-9.]*"\]}\]' | \
        grep -o '[0-9.]*"$' | sed 's/"$//' || echo "2.1")
    
    if (( $(echo "$response_time < 2.0" | bc -l) )); then
        success "Performance metrics acceptable for $service_name ($environment): ${response_time}s"
        return 0
    else
        error "Performance metrics unacceptable for $service_name ($environment): ${response_time}s"
        return 1
    fi
}

# Gradual traffic shifting
gradual_traffic_shift() {
    local service_name=$1
    local service_port=$2
    
    log "Starting gradual traffic shift for $service_name..."
    
    # Traffic shifting stages: 100/0 -> 90/10 -> 50/50 -> 10/90 -> 0/100
    local stages=("90 10" "50 50" "10 90" "0 100")
    
    for stage in "${stages[@]}"; do
        local blue_weight=$(echo "$stage" | awk '{print $1}')
        local green_weight=$(echo "$stage" | awk '{print $2}')
        
        log "Shifting traffic to Blue=$blue_weight%, Green=$green_weight%"
        
        # Update traffic weights
        update_traffic_weights "$service_name" "$service_port" "$blue_weight" "$green_weight"
        
        # Wait for traffic to stabilize
        sleep 30
        
        # Check constitutional compliance and performance
        if ! check_constitutional_compliance "$service_name" "$service_port" "green"; then
            error "Constitutional compliance check failed for $service_name. Rolling back..."
            update_traffic_weights "$service_name" "$service_port" "100" "0"
            return 1
        fi
        
        if ! check_performance_metrics "$service_name" "green"; then
            error "Performance check failed for $service_name. Rolling back..."
            update_traffic_weights "$service_name" "$service_port" "100" "0"
            return 1
        fi
        
        success "Stage completed: Blue=$blue_weight%, Green=$green_weight%"
        
        # Wait before next stage
        if [[ "$green_weight" != "100" ]]; then
            log "Waiting 2 minutes before next stage..."
            sleep 120
        fi
    done
    
    success "Traffic shift completed for $service_name"
}

# Rollback traffic to blue environment
rollback_traffic() {
    local service_name=$1
    local service_port=$2
    
    warning "Rolling back traffic for $service_name to blue environment..."
    update_traffic_weights "$service_name" "$service_port" "100" "0"
    success "Rollback completed for $service_name"
}

# Migrate single service
migrate_service() {
    local service_info=$1
    local service_name=$(echo "$service_info" | cut -d: -f1)
    local service_port=$(echo "$service_info" | cut -d: -f2)
    
    log "Starting migration for $service_name service (port $service_port)..."
    
    # Verify green environment is ready
    if ! check_constitutional_compliance "$service_name" "$service_port" "green"; then
        error "Green environment not ready for $service_name. Aborting migration."
        return 1
    fi
    
    # Perform gradual traffic shift
    if gradual_traffic_shift "$service_name" "$service_port"; then
        success "Migration completed successfully for $service_name"
        return 0
    else
        error "Migration failed for $service_name"
        return 1
    fi
}

# Migrate all services
migrate_all_services() {
    log "Starting migration of all services in order..."
    
    for service_info in "${SERVICES[@]}"; do
        local service_name=$(echo "$service_info" | cut -d: -f1)
        
        log "Migrating $service_name service..."
        
        if migrate_service "$service_info"; then
            success "✅ $service_name migration completed"
        else
            error "❌ $service_name migration failed"
            log "Stopping migration process due to failure"
            return 1
        fi
        
        # Wait between service migrations
        log "Waiting 5 minutes before next service migration..."
        sleep 300
    done
    
    success "🎉 All services migrated successfully!"
}

# Show current traffic distribution
show_traffic_status() {
    log "Current traffic distribution:"
    echo ""
    
    for service_info in "${SERVICES[@]}"; do
        local service_name=$(echo "$service_info" | cut -d: -f1)
        local service_port=$(echo "$service_info" | cut -d: -f2)
        
        local weights
        weights=$(get_traffic_weights "$service_name" "$service_port")
        local blue_weight=$(echo "$weights" | head -1)
        local green_weight=$(echo "$weights" | tail -1)
        
        echo "  $service_name: Blue=$blue_weight%, Green=$green_weight%"
    done
    
    echo ""
}

# Main function
main() {
    case "${1:-}" in
        "migrate")
            if [[ -n "${2:-}" ]]; then
                # Migrate specific service
                local service_name="$2"
                local service_port="$3"
                migrate_service "$service_name:$service_port"
            else
                # Migrate all services
                migrate_all_services
            fi
            ;;
        "rollback")
            local service_name="$2"
            local service_port="$3"
            rollback_traffic "$service_name" "$service_port"
            ;;
        "status")
            show_traffic_status
            ;;
        "shift")
            local service_name="$2"
            local service_port="$3"
            local blue_weight="$4"
            local green_weight="$5"
            update_traffic_weights "$service_name" "$service_port" "$blue_weight" "$green_weight"
            ;;
        *)
            echo "Usage: $0 {migrate|rollback|status|shift} [service] [port] [blue_weight] [green_weight]"
            echo ""
            echo "Commands:"
            echo "  migrate                    - Migrate all services"
            echo "  migrate <service> <port>   - Migrate specific service"
            echo "  rollback <service> <port>  - Rollback specific service"
            echo "  status                     - Show current traffic distribution"
            echo "  shift <service> <port> <blue%> <green%> - Set specific traffic weights"
            echo ""
            echo "Services: auth, ac, integrity, fv, gs, pgc, ec"
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"
