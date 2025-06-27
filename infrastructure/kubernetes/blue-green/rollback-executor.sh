#!/bin/bash

# ACGE Phase 2 Automated Rollback Executor
# Executes automated rollback based on constitutional compliance and performance triggers

set -euo pipefail

# Configuration
NAMESPACE_SHARED="acgs-shared"
NAMESPACE_BLUE="acgs-blue"
NAMESPACE_GREEN="acgs-green"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
PROMETHEUS_URL="http://prometheus:9090"

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

# Service configurations
declare -A SERVICES=(
    ["auth"]="8000"
    ["ac"]="8001"
    ["integrity"]="8002"
    ["fv"]="8003"
    ["gs"]="8004"
    ["pgc"]="8005"
    ["ec"]="8006"
)

declare -A CRITICAL_SERVICES=(
    ["auth"]="true"
    ["ac"]="true"
    ["integrity"]="true"
    ["pgc"]="true"
    ["fv"]="false"
    ["gs"]="false"
    ["ec"]="false"
)

# Check current metrics
check_constitutional_compliance() {
    local service_name=$1
    local environment=${2:-"green"}
    
    log "Checking constitutional compliance for $service_name in $environment environment..."
    
    local query="constitutional_compliance_score{service=\"$service_name\",environment=\"$environment\"}"
    local response
    response=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=$query" || echo '{"data":{"result":[]}}')
    
    local compliance_score
    compliance_score=$(echo "$response" | jq -r '.data.result[0].value[1] // "0.0"')
    
    echo "$compliance_score"
}

check_response_time() {
    local service_name=$1
    local environment=${2:-"green"}
    
    log "Checking response time for $service_name in $environment environment..."
    
    local query="histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{service=\"$service_name\",environment=\"$environment\"}[5m]))"
    local response
    response=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=$query" || echo '{"data":{"result":[]}}')
    
    local response_time
    response_time=$(echo "$response" | jq -r '.data.result[0].value[1] // "0.0"')
    
    echo "$response_time"
}

check_error_rate() {
    local service_name=$1
    local environment=${2:-"green"}
    
    log "Checking error rate for $service_name in $environment environment..."
    
    local query="rate(http_requests_total{status=~\"5..\",service=\"$service_name\",environment=\"$environment\"}[5m]) / rate(http_requests_total{service=\"$service_name\",environment=\"$environment\"}[5m])"
    local response
    response=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=$query" || echo '{"data":{"result":[]}}')
    
    local error_rate
    error_rate=$(echo "$response" | jq -r '.data.result[0].value[1] // "0.0"')
    
    echo "$error_rate"
}

check_constitutional_hash() {
    local service_name=$1
    local environment=${2:-"green"}
    
    log "Checking constitutional hash for $service_name in $environment environment..."
    
    local query="constitutional_hash_valid{service=\"$service_name\",environment=\"$environment\"}"
    local response
    response=$(curl -s "$PROMETHEUS_URL/api/v1/query?query=$query" || echo '{"data":{"result":[]}}')
    
    local hash_valid
    hash_valid=$(echo "$response" | jq -r '.data.result[0].value[1] // "0"')
    
    echo "$hash_valid"
}

# Rollback execution functions
rollback_service_traffic() {
    local service_name=$1
    local service_port=$2
    
    log "Rolling back traffic for $service_name to blue environment..."
    
    # Create VirtualService patch to route 100% traffic to blue
    cat > /tmp/rollback-patch.yaml << EOF
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
          weight: 100
        - destination:
            host: acgs-$service_name-service-green.$NAMESPACE_GREEN.svc.cluster.local
            port:
              number: $service_port
          weight: 0
      headers:
        request:
          add:
            x-constitutional-hash: "$CONSTITUTIONAL_HASH"
            x-rollback-reason: "automated-rollback"
            x-rollback-timestamp: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
EOF
    
    # Apply the patch
    if kubectl patch virtualservice acgs-blue-green-routing -n "$NAMESPACE_SHARED" --patch-file /tmp/rollback-patch.yaml; then
        success "Traffic rollback completed for $service_name"
        
        # Record rollback event
        kubectl create event rollback-executed \
            --namespace="$NAMESPACE_SHARED" \
            --reason="AutomatedRollback" \
            --message="Automated rollback executed for $service_name due to compliance/performance issues" \
            --type="Warning" || true
        
        return 0
    else
        error "Failed to rollback traffic for $service_name"
        return 1
    fi
    
    # Clean up
    rm -f /tmp/rollback-patch.yaml
}

# Validate rollback success
validate_rollback() {
    local service_name=$1
    local service_port=$2
    
    log "Validating rollback for $service_name..."
    
    # Wait for traffic to stabilize
    sleep 30
    
    # Check blue environment health
    local blue_health
    blue_health=$(kubectl run rollback-validation-$service_name --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f -s "http://acgs-$service_name-service-blue.$NAMESPACE_BLUE.svc.cluster.local:$service_port/health" >/dev/null 2>&1 && echo "healthy" || echo "unhealthy")
    
    if [[ "$blue_health" == "healthy" ]]; then
        success "Blue environment health validated for $service_name"
        
        # Check constitutional compliance in blue environment
        local blue_compliance
        blue_compliance=$(check_constitutional_compliance "$service_name" "blue")
        
        if (( $(echo "$blue_compliance >= 0.95" | bc -l) )); then
            success "Constitutional compliance restored for $service_name: $blue_compliance"
            return 0
        else
            warning "Constitutional compliance still low in blue environment: $blue_compliance"
            return 1
        fi
    else
        error "Blue environment health check failed for $service_name"
        return 1
    fi
}

# Send notifications
send_notification() {
    local service_name=$1
    local trigger_type=$2
    local trigger_value=$3
    local rollback_status=$4
    
    log "Sending rollback notification for $service_name..."
    
    local message="🚨 ACGE Automated Rollback Executed
Service: $service_name
Trigger: $trigger_type
Value: $trigger_value
Status: $rollback_status
Constitutional Hash: $CONSTITUTIONAL_HASH
Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Environment: Production"
    
    # Send to notification service
    curl -X POST "http://rollback-notifier:8082/notify" \
        -H "Content-Type: application/json" \
        -d "{
            \"service\": \"$service_name\",
            \"trigger\": \"$trigger_type\",
            \"value\": \"$trigger_value\",
            \"status\": \"$rollback_status\",
            \"message\": \"$message\",
            \"severity\": \"critical\"
        }" || warning "Failed to send notification"
}

# Main rollback execution
execute_rollback() {
    local service_name=$1
    local trigger_type=$2
    local trigger_value=$3
    
    log "🚨 Executing automated rollback for $service_name"
    log "Trigger: $trigger_type = $trigger_value"
    
    local service_port="${SERVICES[$service_name]}"
    local is_critical="${CRITICAL_SERVICES[$service_name]}"
    
    # Record rollback start
    log "Starting rollback execution at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
    
    # Execute traffic rollback
    if rollback_service_traffic "$service_name" "$service_port"; then
        log "Traffic rollback completed, validating..."
        
        # Validate rollback success
        if validate_rollback "$service_name" "$service_port"; then
            success "✅ Rollback validation successful for $service_name"
            send_notification "$service_name" "$trigger_type" "$trigger_value" "SUCCESS"
            
            # If critical service, check if other services need rollback
            if [[ "$is_critical" == "true" ]]; then
                warning "Critical service $service_name rolled back. Consider rolling back dependent services."
            fi
            
            return 0
        else
            error "❌ Rollback validation failed for $service_name"
            send_notification "$service_name" "$trigger_type" "$trigger_value" "VALIDATION_FAILED"
            return 1
        fi
    else
        error "❌ Traffic rollback failed for $service_name"
        send_notification "$service_name" "$trigger_type" "$trigger_value" "ROLLBACK_FAILED"
        return 1
    fi
}

# Check if rollback is needed
check_rollback_triggers() {
    local service_name=$1
    
    log "Checking rollback triggers for $service_name..."
    
    # Check constitutional compliance
    local compliance_score
    compliance_score=$(check_constitutional_compliance "$service_name")
    if (( $(echo "$compliance_score < 0.95" | bc -l) )); then
        warning "Constitutional compliance trigger: $compliance_score < 0.95"
        execute_rollback "$service_name" "constitutional_compliance" "$compliance_score"
        return $?
    fi
    
    # Check response time
    local response_time
    response_time=$(check_response_time "$service_name")
    if (( $(echo "$response_time > 2.0" | bc -l) )); then
        warning "Response time trigger: ${response_time}s > 2.0s"
        execute_rollback "$service_name" "response_time" "$response_time"
        return $?
    fi
    
    # Check error rate
    local error_rate
    error_rate=$(check_error_rate "$service_name")
    if (( $(echo "$error_rate > 0.01" | bc -l) )); then
        warning "Error rate trigger: $error_rate > 0.01"
        execute_rollback "$service_name" "error_rate" "$error_rate"
        return $?
    fi
    
    # Check constitutional hash
    local hash_valid
    hash_valid=$(check_constitutional_hash "$service_name")
    if [[ "$hash_valid" != "1" ]]; then
        error "Constitutional hash mismatch trigger"
        execute_rollback "$service_name" "constitutional_hash_mismatch" "$hash_valid"
        return $?
    fi
    
    success "All triggers within acceptable ranges for $service_name"
    return 0
}

# Main function
main() {
    case "${1:-}" in
        "check")
            local service_name="${2:-}"
            if [[ -n "$service_name" ]]; then
                check_rollback_triggers "$service_name"
            else
                log "Checking all services for rollback triggers..."
                for service in "${!SERVICES[@]}"; do
                    check_rollback_triggers "$service"
                done
            fi
            ;;
        "rollback")
            local service_name="$2"
            local trigger_type="$3"
            local trigger_value="$4"
            execute_rollback "$service_name" "$trigger_type" "$trigger_value"
            ;;
        "validate")
            local service_name="$2"
            local service_port="${SERVICES[$service_name]}"
            validate_rollback "$service_name" "$service_port"
            ;;
        *)
            echo "Usage: $0 {check|rollback|validate} [service] [trigger_type] [trigger_value]"
            echo ""
            echo "Commands:"
            echo "  check [service]                           - Check rollback triggers"
            echo "  rollback <service> <trigger> <value>      - Execute rollback"
            echo "  validate <service>                        - Validate rollback"
            echo ""
            echo "Services: ${!SERVICES[*]}"
            exit 1
            ;;
    esac
}

# Execute main function
main "$@"
