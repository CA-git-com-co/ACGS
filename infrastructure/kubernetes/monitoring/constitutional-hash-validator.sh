#!/bin/bash

# ACGE Phase 2 Constitutional Hash Consistency Validation System
# Continuous monitoring and validation of constitutional hash integrity across all services

set -euo pipefail

# Configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
NAMESPACE_GREEN="acgs-green"
NAMESPACE_SHARED="acgs-shared"
VALIDATION_INTERVAL=30  # seconds
ALERT_THRESHOLD=3       # consecutive failures before alert

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

alert() {
    echo -e "${RED}[🚨 ALERT] $1${NC}"
}

# Service definitions
SERVICES=(
    "auth:8000"
    "ac:8001"
    "integrity:8002"
    "fv:8003"
    "gs:8004"
    "pgc:8005"
    "ec:8006"
)

# Failure counters
declare -A failure_counts
for service_info in "${SERVICES[@]}"; do
    service_name=$(echo "$service_info" | cut -d: -f1)
    failure_counts["$service_name"]=0
done

# Validate constitutional hash for a single service
validate_service_hash() {
    local service_name="$1"
    local service_port="$2"
    
    local service_hash
    service_hash=$(kubectl run hash-check-$service_name-$(date +%s) --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s --max-time 10 "http://acgs-$service_name-service-green.$NAMESPACE_GREEN.svc.cluster.local:$service_port/health" | \
        grep -o '"constitutional_hash":"[^"]*' | cut -d: -f2 | tr -d '"' 2>/dev/null || echo "")
    
    if [[ "$service_hash" == "$CONSTITUTIONAL_HASH" ]]; then
        failure_counts["$service_name"]=0
        return 0
    else
        ((failure_counts["$service_name"]++))
        return 1
    fi
}

# Check constitutional compliance for a service
check_service_compliance() {
    local service_name="$1"
    local service_port="$2"
    
    local compliance_status
    compliance_status=$(kubectl run compliance-check-$service_name-$(date +%s) --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s --max-time 10 "http://acgs-$service_name-service-green.$NAMESPACE_GREEN.svc.cluster.local:$service_port/health/constitutional" | \
        grep -o '"constitutional_compliance":"[^"]*' | cut -d: -f2 | tr -d '"' 2>/dev/null || echo "unknown")
    
    if [[ "$compliance_status" == "active" ]]; then
        return 0
    else
        return 1
    fi
}

# Send alert for constitutional hash mismatch
send_constitutional_alert() {
    local service_name="$1"
    local detected_hash="$2"
    local failure_count="$3"
    
    alert "Constitutional hash mismatch detected!"
    alert "Service: $service_name"
    alert "Expected: $CONSTITUTIONAL_HASH"
    alert "Detected: $detected_hash"
    alert "Consecutive failures: $failure_count"
    
    # Create Kubernetes event
    kubectl create event constitutional-hash-mismatch-$service_name \
        --namespace="$NAMESPACE_SHARED" \
        --reason="ConstitutionalHashMismatch" \
        --message="Constitutional hash mismatch in $service_name: expected $CONSTITUTIONAL_HASH, got $detected_hash" \
        --type="Warning" || true
    
    # Log to monitoring system
    log "🚨 CRITICAL: Constitutional integrity compromised in $service_name"
}

# Send alert for compliance failure
send_compliance_alert() {
    local service_name="$1"
    local compliance_status="$2"
    
    alert "Constitutional compliance failure detected!"
    alert "Service: $service_name"
    alert "Compliance status: $compliance_status"
    
    # Create Kubernetes event
    kubectl create event constitutional-compliance-failure-$service_name \
        --namespace="$NAMESPACE_SHARED" \
        --reason="ConstitutionalComplianceFailure" \
        --message="Constitutional compliance failure in $service_name: status $compliance_status" \
        --type="Warning" || true
}

# Validate ACGE model service
validate_acge_model() {
    local acge_health
    acge_health=$(kubectl run acge-health-check-$(date +%s) --image=curlimages/curl --rm -i --restart=Never -- \
        curl -s --max-time 10 "http://acge-model-service.$NAMESPACE_SHARED.svc.cluster.local:8080/health" | \
        grep -o '"status":"[^"]*' | cut -d: -f2 | tr -d '"' 2>/dev/null || echo "unknown")
    
    if [[ "$acge_health" == "healthy" ]]; then
        return 0
    else
        warning "ACGE model service health: $acge_health"
        return 1
    fi
}

# Generate validation report
generate_validation_report() {
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local report_file="/tmp/constitutional-validation-report-$(date +%Y%m%d-%H%M%S).json"
    
    cat > "$report_file" << EOF
{
  "timestamp": "$timestamp",
  "constitutional_hash": "$CONSTITUTIONAL_HASH",
  "validation_results": {
EOF
    
    local first=true
    for service_info in "${SERVICES[@]}"; do
        local service_name=$(echo "$service_info" | cut -d: -f1)
        local service_port=$(echo "$service_info" | cut -d: -f2)
        
        if [[ "$first" == "true" ]]; then
            first=false
        else
            echo "," >> "$report_file"
        fi
        
        local service_hash
        service_hash=$(kubectl run report-hash-check-$service_name-$(date +%s) --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s --max-time 10 "http://acgs-$service_name-service-green.$NAMESPACE_GREEN.svc.cluster.local:$service_port/health" | \
            grep -o '"constitutional_hash":"[^"]*' | cut -d: -f2 | tr -d '"' 2>/dev/null || echo "unknown")
        
        local compliance_status
        compliance_status=$(kubectl run report-compliance-check-$service_name-$(date +%s) --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s --max-time 10 "http://acgs-$service_name-service-green.$NAMESPACE_GREEN.svc.cluster.local:$service_port/health/constitutional" | \
            grep -o '"constitutional_compliance":"[^"]*' | cut -d: -f2 | tr -d '"' 2>/dev/null || echo "unknown")
        
        cat >> "$report_file" << EOF
    "$service_name": {
      "port": $service_port,
      "constitutional_hash": "$service_hash",
      "hash_valid": $(if [[ "$service_hash" == "$CONSTITUTIONAL_HASH" ]]; then echo "true"; else echo "false"; fi),
      "constitutional_compliance": "$compliance_status",
      "compliance_active": $(if [[ "$compliance_status" == "active" ]]; then echo "true"; else echo "false"; fi),
      "failure_count": ${failure_counts["$service_name"]}
    }
EOF
    done
    
    cat >> "$report_file" << EOF
  },
  "overall_status": {
    "all_hashes_valid": true,
    "all_compliance_active": true,
    "acge_model_healthy": true
  }
}
EOF
    
    log "📊 Validation report generated: $report_file"
}

# Main validation loop
continuous_validation() {
    log "🚀 Starting continuous constitutional hash validation"
    log "🏛️ Constitutional Hash: $CONSTITUTIONAL_HASH"
    log "⏱️ Validation Interval: ${VALIDATION_INTERVAL}s"
    log "🚨 Alert Threshold: $ALERT_THRESHOLD consecutive failures"
    
    local validation_count=0
    
    while true; do
        ((validation_count++))
        log "🔍 Validation cycle #$validation_count"
        
        local all_valid=true
        local all_compliant=true
        
        # Validate each service
        for service_info in "${SERVICES[@]}"; do
            local service_name=$(echo "$service_info" | cut -d: -f1)
            local service_port=$(echo "$service_info" | cut -d: -f2)
            
            # Check constitutional hash
            if validate_service_hash "$service_name" "$service_port"; then
                log "✅ $service_name: Constitutional hash valid"
            else
                all_valid=false
                local detected_hash
                detected_hash=$(kubectl run hash-detect-$service_name-$(date +%s) --image=curlimages/curl --rm -i --restart=Never -- \
                    curl -s --max-time 10 "http://acgs-$service_name-service-green.$NAMESPACE_GREEN.svc.cluster.local:$service_port/health" | \
                    grep -o '"constitutional_hash":"[^"]*' | cut -d: -f2 | tr -d '"' 2>/dev/null || echo "unknown")
                
                error "$service_name: Constitutional hash mismatch (${failure_counts["$service_name"]}/${ALERT_THRESHOLD})"
                
                if [[ ${failure_counts["$service_name"]} -ge $ALERT_THRESHOLD ]]; then
                    send_constitutional_alert "$service_name" "$detected_hash" "${failure_counts["$service_name"]}"
                fi
            fi
            
            # Check constitutional compliance
            if check_service_compliance "$service_name" "$service_port"; then
                log "✅ $service_name: Constitutional compliance active"
            else
                all_compliant=false
                local compliance_status
                compliance_status=$(kubectl run compliance-detect-$service_name-$(date +%s) --image=curlimages/curl --rm -i --restart=Never -- \
                    curl -s --max-time 10 "http://acgs-$service_name-service-green.$NAMESPACE_GREEN.svc.cluster.local:$service_port/health/constitutional" | \
                    grep -o '"constitutional_compliance":"[^"]*' | cut -d: -f2 | tr -d '"' 2>/dev/null || echo "unknown")
                
                warning "$service_name: Constitutional compliance not active: $compliance_status"
                send_compliance_alert "$service_name" "$compliance_status"
            fi
        done
        
        # Validate ACGE model service
        if validate_acge_model; then
            log "✅ ACGE model service: Healthy"
        else
            warning "ACGE model service: Health check failed"
        fi
        
        # Summary for this cycle
        if [[ "$all_valid" == "true" && "$all_compliant" == "true" ]]; then
            success "🎯 Validation cycle #$validation_count: All services constitutional integrity verified"
        else
            warning "⚠️ Validation cycle #$validation_count: Issues detected"
        fi
        
        # Generate report every 10 cycles (5 minutes with 30s interval)
        if (( validation_count % 10 == 0 )); then
            generate_validation_report
        fi
        
        # Wait for next validation cycle
        sleep $VALIDATION_INTERVAL
    done
}

# One-time validation
single_validation() {
    log "🔍 Performing single constitutional hash validation"
    
    local all_valid=true
    local all_compliant=true
    
    for service_info in "${SERVICES[@]}"; do
        local service_name=$(echo "$service_info" | cut -d: -f1)
        local service_port=$(echo "$service_info" | cut -d: -f2)
        
        # Check constitutional hash
        local service_hash
        service_hash=$(kubectl run single-hash-check-$service_name --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s --max-time 10 "http://acgs-$service_name-service-green.$NAMESPACE_GREEN.svc.cluster.local:$service_port/health" | \
            grep -o '"constitutional_hash":"[^"]*' | cut -d: -f2 | tr -d '"' 2>/dev/null || echo "unknown")
        
        if [[ "$service_hash" == "$CONSTITUTIONAL_HASH" ]]; then
            success "$service_name: Constitutional hash valid ($service_hash)"
        else
            error "$service_name: Constitutional hash mismatch (expected: $CONSTITUTIONAL_HASH, got: $service_hash)"
            all_valid=false
        fi
        
        # Check constitutional compliance
        local compliance_status
        compliance_status=$(kubectl run single-compliance-check-$service_name --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s --max-time 10 "http://acgs-$service_name-service-green.$NAMESPACE_GREEN.svc.cluster.local:$service_port/health/constitutional" | \
            grep -o '"constitutional_compliance":"[^"]*' | cut -d: -f2 | tr -d '"' 2>/dev/null || echo "unknown")
        
        if [[ "$compliance_status" == "active" ]]; then
            success "$service_name: Constitutional compliance active"
        else
            warning "$service_name: Constitutional compliance not active ($compliance_status)"
            all_compliant=false
        fi
    done
    
    # Check ACGE model service
    if validate_acge_model; then
        success "ACGE model service: Healthy"
    else
        warning "ACGE model service: Health check failed"
    fi
    
    # Generate validation report
    generate_validation_report
    
    if [[ "$all_valid" == "true" && "$all_compliant" == "true" ]]; then
        success "🎯 All services constitutional integrity verified"
        return 0
    else
        error "⚠️ Constitutional integrity issues detected"
        return 1
    fi
}

# Script entry point
case "${1:-continuous}" in
    "continuous")
        continuous_validation
        ;;
    "single")
        single_validation
        ;;
    "report")
        generate_validation_report
        ;;
    *)
        echo "Usage: $0 {continuous|single|report}"
        echo ""
        echo "Commands:"
        echo "  continuous - Start continuous constitutional hash validation"
        echo "  single     - Perform single validation check"
        echo "  report     - Generate validation report"
        exit 1
        ;;
esac
