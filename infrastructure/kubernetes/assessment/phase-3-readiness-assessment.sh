#!/bin/bash

# ACGE Phase 3 Readiness Assessment
# Generate production readiness certification for Phase 3 edge deployment

set -euo pipefail

# Configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
NAMESPACE_GREEN="acgs-green"
NAMESPACE_SHARED="acgs-shared"
ASSESSMENT_VERSION="3.0.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

info() {
    echo -e "${CYAN}[ℹ] $1${NC}"
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

# Assessment criteria
declare -A assessment_scores
assessment_scores["system_health"]=0
assessment_scores["performance"]=0
assessment_scores["constitutional_compliance"]=0
assessment_scores["security"]=0
assessment_scores["operational_readiness"]=0
assessment_scores["documentation"]=0

# Assess system health
assess_system_health() {
    log "🏥 Assessing system health..."
    
    local healthy_services=0
    local total_services=${#SERVICES[@]}
    
    for service_info in "${SERVICES[@]}"; do
        local service_name=$(echo "$service_info" | cut -d: -f1)
        local service_port=$(echo "$service_info" | cut -d: -f2)
        
        # Check service health
        if kubectl run health-assess-$service_name --image=curlimages/curl --rm -i --restart=Never -- \
            curl -f -s "http://acgs-$service_name-service-green.$NAMESPACE_GREEN.svc.cluster.local:$service_port/health" >/dev/null 2>&1; then
            success "$service_name: Healthy"
            ((healthy_services++))
        else
            error "$service_name: Unhealthy"
        fi
    done
    
    # Check ACGE model service
    if kubectl run health-assess-acge --image=curlimages/curl --rm -i --restart=Never -- \
        curl -f -s "http://acge-model-service.$NAMESPACE_SHARED.svc.cluster.local:8080/health" >/dev/null 2>&1; then
        success "ACGE Model Service: Healthy"
        ((healthy_services++))
        ((total_services++))
    else
        error "ACGE Model Service: Unhealthy"
        ((total_services++))
    fi
    
    # Calculate health score
    local health_percentage=$((healthy_services * 100 / total_services))
    assessment_scores["system_health"]=$health_percentage
    
    if [[ $health_percentage -ge 95 ]]; then
        success "System Health: $health_percentage% (EXCELLENT)"
    elif [[ $health_percentage -ge 90 ]]; then
        success "System Health: $health_percentage% (GOOD)"
    else
        warning "System Health: $health_percentage% (NEEDS IMPROVEMENT)"
    fi
}

# Assess performance metrics
assess_performance() {
    log "⚡ Assessing performance metrics..."
    
    local performance_score=0
    local total_checks=0
    
    # Check response times
    for service_info in "${SERVICES[@]}"; do
        local service_name=$(echo "$service_info" | cut -d: -f1)
        local service_port=$(echo "$service_info" | cut -d: -f2)
        
        local response_time
        response_time=$(kubectl run perf-assess-$service_name --image=curlimages/curl --rm -i --restart=Never -- \
            curl -w "%{time_total}" -s -o /dev/null --max-time 10 \
            "http://acgs-$service_name-service-green.$NAMESPACE_GREEN.svc.cluster.local:$service_port/health" 2>/dev/null || echo "10.0")
        
        ((total_checks++))
        if (( $(echo "$response_time <= 2.0" | bc -l) )); then
            success "$service_name: Response time ${response_time}s (≤2s target)"
            ((performance_score++))
        else
            warning "$service_name: Response time ${response_time}s (>2s target)"
        fi
    done
    
    # Calculate performance score
    local performance_percentage=$((performance_score * 100 / total_checks))
    assessment_scores["performance"]=$performance_percentage
    
    if [[ $performance_percentage -ge 95 ]]; then
        success "Performance: $performance_percentage% (EXCELLENT)"
    elif [[ $performance_percentage -ge 90 ]]; then
        success "Performance: $performance_percentage% (GOOD)"
    else
        warning "Performance: $performance_percentage% (NEEDS IMPROVEMENT)"
    fi
}

# Assess constitutional compliance
assess_constitutional_compliance() {
    log "🏛️ Assessing constitutional compliance..."
    
    local compliant_services=0
    local total_services=${#SERVICES[@]}
    local hash_consistent_services=0
    
    for service_info in "${SERVICES[@]}"; do
        local service_name=$(echo "$service_info" | cut -d: -f1)
        local service_port=$(echo "$service_info" | cut -d: -f2)
        
        # Check constitutional compliance
        local compliance_status
        compliance_status=$(kubectl run compliance-assess-$service_name --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s --max-time 10 "http://acgs-$service_name-service-green.$NAMESPACE_GREEN.svc.cluster.local:$service_port/health/constitutional" | \
            grep -o '"constitutional_compliance":"[^"]*' | cut -d: -f2 | tr -d '"' 2>/dev/null || echo "unknown")
        
        if [[ "$compliance_status" == "active" ]]; then
            success "$service_name: Constitutional compliance active"
            ((compliant_services++))
        else
            warning "$service_name: Constitutional compliance not active ($compliance_status)"
        fi
        
        # Check constitutional hash
        local service_hash
        service_hash=$(kubectl run hash-assess-$service_name --image=curlimages/curl --rm -i --restart=Never -- \
            curl -s --max-time 10 "http://acgs-$service_name-service-green.$NAMESPACE_GREEN.svc.cluster.local:$service_port/health" | \
            grep -o '"constitutional_hash":"[^"]*' | cut -d: -f2 | tr -d '"' 2>/dev/null || echo "")
        
        if [[ "$service_hash" == "$CONSTITUTIONAL_HASH" ]]; then
            success "$service_name: Constitutional hash consistent"
            ((hash_consistent_services++))
        else
            error "$service_name: Constitutional hash mismatch ($service_hash)"
        fi
    done
    
    # Calculate compliance score (both compliance and hash consistency)
    local compliance_percentage=$(((compliant_services + hash_consistent_services) * 100 / (total_services * 2)))
    assessment_scores["constitutional_compliance"]=$compliance_percentage
    
    if [[ $compliance_percentage -ge 95 ]]; then
        success "Constitutional Compliance: $compliance_percentage% (EXCELLENT)"
    elif [[ $compliance_percentage -ge 90 ]]; then
        success "Constitutional Compliance: $compliance_percentage% (GOOD)"
    else
        warning "Constitutional Compliance: $compliance_percentage% (NEEDS IMPROVEMENT)"
    fi
}

# Assess security posture
assess_security() {
    log "🔒 Assessing security posture..."
    
    local security_score=0
    local total_checks=0
    
    # Check pod security contexts
    for service_info in "${SERVICES[@]}"; do
        local service_name=$(echo "$service_info" | cut -d: -f1)
        
        # Check if pods are running as non-root
        local non_root_check
        non_root_check=$(kubectl get pods -n "$NAMESPACE_GREEN" -l app=acgs-$service_name-service -o jsonpath='{.items[*].spec.securityContext.runAsNonRoot}' 2>/dev/null || echo "")
        
        ((total_checks++))
        if [[ "$non_root_check" == "true" ]]; then
            success "$service_name: Running as non-root user"
            ((security_score++))
        else
            warning "$service_name: Security context check failed"
        fi
        
        # Check if read-only root filesystem is enabled
        local readonly_check
        readonly_check=$(kubectl get pods -n "$NAMESPACE_GREEN" -l app=acgs-$service_name-service -o jsonpath='{.items[*].spec.containers[*].securityContext.readOnlyRootFilesystem}' 2>/dev/null || echo "")
        
        ((total_checks++))
        if [[ "$readonly_check" == "true" ]]; then
            success "$service_name: Read-only root filesystem enabled"
            ((security_score++))
        else
            warning "$service_name: Read-only root filesystem not enabled"
        fi
    done
    
    # Check network policies exist
    local network_policies
    network_policies=$(kubectl get networkpolicies -n "$NAMESPACE_GREEN" --no-headers 2>/dev/null | wc -l || echo "0")
    
    ((total_checks++))
    if [[ $network_policies -gt 0 ]]; then
        success "Network policies: $network_policies policies configured"
        ((security_score++))
    else
        warning "Network policies: No network policies found"
    fi
    
    # Calculate security score
    local security_percentage=$((security_score * 100 / total_checks))
    assessment_scores["security"]=$security_percentage
    
    if [[ $security_percentage -ge 90 ]]; then
        success "Security: $security_percentage% (EXCELLENT)"
    elif [[ $security_percentage -ge 80 ]]; then
        success "Security: $security_percentage% (GOOD)"
    else
        warning "Security: $security_percentage% (NEEDS IMPROVEMENT)"
    fi
}

# Assess operational readiness
assess_operational_readiness() {
    log "🔧 Assessing operational readiness..."
    
    local operational_score=0
    local total_checks=0
    
    # Check monitoring stack
    ((total_checks++))
    if kubectl get deployment prometheus-server -n monitoring >/dev/null 2>&1; then
        success "Monitoring: Prometheus deployed"
        ((operational_score++))
    else
        warning "Monitoring: Prometheus not found"
    fi
    
    ((total_checks++))
    if kubectl get deployment grafana -n monitoring >/dev/null 2>&1; then
        success "Monitoring: Grafana deployed"
        ((operational_score++))
    else
        warning "Monitoring: Grafana not found"
    fi
    
    # Check logging stack
    ((total_checks++))
    if kubectl get deployment elasticsearch -n logging >/dev/null 2>&1; then
        success "Logging: Elasticsearch deployed"
        ((operational_score++))
    else
        warning "Logging: Elasticsearch not found"
    fi
    
    # Check backup procedures
    ((total_checks++))
    if [[ -f "infrastructure/kubernetes/blue-green/backup-system.sh" ]]; then
        success "Backup: Backup procedures documented"
        ((operational_score++))
    else
        warning "Backup: Backup procedures not found"
    fi
    
    # Check rollback procedures
    ((total_checks++))
    if [[ -f "infrastructure/kubernetes/blue-green/automated-rollback.sh" ]]; then
        success "Rollback: Automated rollback system available"
        ((operational_score++))
    else
        warning "Rollback: Automated rollback system not found"
    fi
    
    # Calculate operational score
    local operational_percentage=$((operational_score * 100 / total_checks))
    assessment_scores["operational_readiness"]=$operational_percentage
    
    if [[ $operational_percentage -ge 90 ]]; then
        success "Operational Readiness: $operational_percentage% (EXCELLENT)"
    elif [[ $operational_percentage -ge 80 ]]; then
        success "Operational Readiness: $operational_percentage% (GOOD)"
    else
        warning "Operational Readiness: $operational_percentage% (NEEDS IMPROVEMENT)"
    fi
}

# Assess documentation
assess_documentation() {
    log "📚 Assessing documentation..."
    
    local doc_score=0
    local total_docs=0
    
    # Check for key documentation files
    local required_docs=(
        "README.md"
        "infrastructure/kubernetes/README.md"
        "services/README.md"
        "docs/ACGE-Phase-2-Migration.md"
        "docs/Constitutional-Compliance.md"
        "docs/Operational-Procedures.md"
    )
    
    for doc in "${required_docs[@]}"; do
        ((total_docs++))
        if [[ -f "$doc" ]]; then
            success "Documentation: $doc exists"
            ((doc_score++))
        else
            warning "Documentation: $doc missing"
        fi
    done
    
    # Calculate documentation score
    local doc_percentage=$((doc_score * 100 / total_docs))
    assessment_scores["documentation"]=$doc_percentage
    
    if [[ $doc_percentage -ge 90 ]]; then
        success "Documentation: $doc_percentage% (EXCELLENT)"
    elif [[ $doc_percentage -ge 80 ]]; then
        success "Documentation: $doc_percentage% (GOOD)"
    else
        warning "Documentation: $doc_percentage% (NEEDS IMPROVEMENT)"
    fi
}

# Generate readiness certification
generate_readiness_certification() {
    local timestamp=$(date -u +%Y-%m-%dT%H:%M:%SZ)
    local cert_file="/tmp/phase-3-readiness-certification-$(date +%Y%m%d-%H%M%S).json"
    
    log "📋 Generating Phase 3 Readiness Certification..."
    
    # Calculate overall score
    local total_score=0
    local category_count=0
    
    for category in "${!assessment_scores[@]}"; do
        total_score=$((total_score + assessment_scores["$category"]))
        ((category_count++))
    done
    
    local overall_score=$((total_score / category_count))
    
    # Determine readiness level
    local readiness_level
    local certification_status
    
    if [[ $overall_score -ge 95 ]]; then
        readiness_level="EXCELLENT"
        certification_status="CERTIFIED"
    elif [[ $overall_score -ge 90 ]]; then
        readiness_level="GOOD"
        certification_status="CERTIFIED"
    elif [[ $overall_score -ge 80 ]]; then
        readiness_level="ACCEPTABLE"
        certification_status="CONDITIONAL"
    else
        readiness_level="NEEDS_IMPROVEMENT"
        certification_status="NOT_CERTIFIED"
    fi
    
    cat > "$cert_file" << EOF
{
  "certification": {
    "title": "ACGE Phase 3 Edge Deployment Readiness Certification",
    "version": "$ASSESSMENT_VERSION",
    "timestamp": "$timestamp",
    "constitutional_hash": "$CONSTITUTIONAL_HASH",
    "overall_score": $overall_score,
    "readiness_level": "$readiness_level",
    "certification_status": "$certification_status"
  },
  "assessment_categories": {
    "system_health": {
      "score": ${assessment_scores["system_health"]},
      "weight": 20,
      "description": "Overall system health and service availability"
    },
    "performance": {
      "score": ${assessment_scores["performance"]},
      "weight": 20,
      "description": "Response times and throughput performance"
    },
    "constitutional_compliance": {
      "score": ${assessment_scores["constitutional_compliance"]},
      "weight": 25,
      "description": "Constitutional compliance and hash consistency"
    },
    "security": {
      "score": ${assessment_scores["security"]},
      "weight": 15,
      "description": "Security posture and best practices"
    },
    "operational_readiness": {
      "score": ${assessment_scores["operational_readiness"]},
      "weight": 15,
      "description": "Monitoring, logging, and operational procedures"
    },
    "documentation": {
      "score": ${assessment_scores["documentation"]},
      "weight": 5,
      "description": "Documentation completeness and quality"
    }
  },
  "services_assessed": [
$(for service_info in "${SERVICES[@]}"; do
    service_name=$(echo "$service_info" | cut -d: -f1)
    service_port=$(echo "$service_info" | cut -d: -f2)
    echo "    {\"name\": \"$service_name\", \"port\": $service_port},"
done | sed '$ s/,$//')
  ],
  "phase_3_recommendations": {
    "edge_deployment_ready": $(if [[ "$certification_status" == "CERTIFIED" ]]; then echo "true"; else echo "false"; fi),
    "recommended_actions": [
$(if [[ $overall_score -lt 95 ]]; then
    echo "      \"Monitor performance metrics continuously\","
    echo "      \"Validate constitutional compliance regularly\","
    echo "      \"Implement additional security hardening\","
    echo "      \"Complete documentation updates\""
else
    echo "      \"Proceed with Phase 3 edge deployment\","
    echo "      \"Maintain current monitoring and compliance levels\","
    echo "      \"Continue regular health assessments\""
fi)
    ],
    "next_assessment_due": "$(date -d '+30 days' -u +%Y-%m-%dT%H:%M:%SZ)"
  }
}
EOF
    
    success "📋 Phase 3 Readiness Certification generated: $cert_file"
    
    # Display certification summary
    echo ""
    echo "=========================================="
    echo "🏆 ACGE Phase 3 Readiness Certification"
    echo "=========================================="
    echo "Overall Score: $overall_score%"
    echo "Readiness Level: $readiness_level"
    echo "Certification Status: $certification_status"
    echo ""
    echo "Category Scores:"
    echo "  System Health: ${assessment_scores["system_health"]}%"
    echo "  Performance: ${assessment_scores["performance"]}%"
    echo "  Constitutional Compliance: ${assessment_scores["constitutional_compliance"]}%"
    echo "  Security: ${assessment_scores["security"]}%"
    echo "  Operational Readiness: ${assessment_scores["operational_readiness"]}%"
    echo "  Documentation: ${assessment_scores["documentation"]}%"
    echo ""
    
    if [[ "$certification_status" == "CERTIFIED" ]]; then
        success "🎉 SYSTEM CERTIFIED FOR PHASE 3 EDGE DEPLOYMENT!"
    elif [[ "$certification_status" == "CONDITIONAL" ]]; then
        warning "⚠️ CONDITIONAL CERTIFICATION - Address recommendations before deployment"
    else
        error "❌ NOT CERTIFIED - Significant improvements required"
    fi
}

# Main assessment execution
main() {
    log "🚀 Starting ACGE Phase 3 Readiness Assessment"
    log "📊 Assessment Version: $ASSESSMENT_VERSION"
    log "🏛️ Constitutional Hash: $CONSTITUTIONAL_HASH"
    
    # Run all assessments
    assess_system_health
    assess_performance
    assess_constitutional_compliance
    assess_security
    assess_operational_readiness
    assess_documentation
    
    # Generate certification
    generate_readiness_certification
    
    success "✅ Phase 3 Readiness Assessment completed"
}

# Script entry point
case "${1:-assess}" in
    "assess")
        main
        ;;
    "health")
        assess_system_health
        ;;
    "performance")
        assess_performance
        ;;
    "compliance")
        assess_constitutional_compliance
        ;;
    "security")
        assess_security
        ;;
    *)
        echo "Usage: $0 {assess|health|performance|compliance|security}"
        echo ""
        echo "Commands:"
        echo "  assess      - Run complete Phase 3 readiness assessment"
        echo "  health      - Assess system health only"
        echo "  performance - Assess performance only"
        echo "  compliance  - Assess constitutional compliance only"
        echo "  security    - Assess security posture only"
        exit 1
        ;;
esac
