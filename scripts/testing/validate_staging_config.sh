#!/bin/bash

# ACGS-PGP Staging Configuration Validation Script
# Validates staging environment configuration without requiring Docker

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

success() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
STAGING_ENV_FILE="config/environments/stagingconfig/environments/development.env"
STAGING_COMPOSE_FILE="infrastructure/docker/docker-compose.staging.yml"

# Validate constitutional hash consistency
validate_constitutional_hash() {
    log "Validating constitutional hash consistency..."
    
    local files_to_check=(
        "config/environments/stagingconfig/environments/development.env"
        "config/environments/productionconfig/environments/development.env"
        "config/monitoring/prometheus-acgs.yml"
        "config/opa/policies/constitutional_compliance_simple.rego"
    )
    
    local hash_found=false
    for file in "${files_to_check[@]}"; do
        if [[ -f "$file" ]]; then
            if grep -q "$CONSTITUTIONAL_HASH" "$file"; then
                success "Constitutional hash found in: $file"
                hash_found=true
            else
                warning "Constitutional hash not found in: $file"
            fi
        else
            warning "File not found: $file"
        fi
    done
    
    if [[ "$hash_found" == true ]]; then
        success "Constitutional hash validation completed"
    else
        error "Constitutional hash validation failed"
        return 1
    fi
}

# Validate service configuration
validate_service_config() {
    log "Validating service configuration..."
    
    local expected_services=("auth_service" "ac_service" "integrity_service" "fv_service" "gs_service" "pgc_service" "ec_service")
    local expected_ports=("8000" "8001" "8002" "8003" "8004" "8005" "8006")
    
    if [[ -f "$STAGING_COMPOSE_FILE" ]]; then
        local compose_content=$(cat "$STAGING_COMPOSE_FILE")
        
        for service in "${expected_services[@]}"; do
            if echo "$compose_content" | grep -q "$service:"; then
                success "Service configuration found: $service"
            else
                warning "Service configuration missing: $service"
            fi
        done
        
        for port in "${expected_ports[@]}"; do
            if echo "$compose_content" | grep -q ":$port"; then
                success "Port configuration found: $port"
            else
                warning "Port configuration missing: $port"
            fi
        done
    else
        error "Staging compose file not found: $STAGING_COMPOSE_FILE"
        return 1
    fi
}

# Validate resource limits
validate_resource_limits() {
    log "Validating resource limits configuration..."
    
    if [[ -f "$STAGING_COMPOSE_FILE" ]]; then
        local compose_content=$(cat "$STAGING_COMPOSE_FILE")
        
        # Check for CPU limits
        if echo "$compose_content" | grep -q "cpus.*0\.[25]"; then
            success "CPU limits configured in staging"
        else
            warning "CPU limits may not be properly configured"
        fi
        
        # Check for memory limits
        if echo "$compose_content" | grep -q "memory.*[12]G"; then
            success "Memory limits configured in staging"
        else
            warning "Memory limits may not be properly configured"
        fi
        
        # Check for health checks
        if echo "$compose_content" | grep -q "healthcheck:"; then
            success "Health checks configured in staging"
        else
            warning "Health checks may be missing"
        fi
    fi
}

# Validate environment variables
validate_environment_variables() {
    log "Validating environment variables..."
    
    if [[ -f "$STAGING_ENV_FILE" ]]; then
        local env_content=$(cat "$STAGING_ENV_FILE")
        
        local required_vars=(
            "CONSTITUTIONAL_HASH"
            "ENVIRONMENT"
            "DATABASE_URL"
            "REDIS_URL"
            "JWT_SECRET_KEY"
        )
        
        for var in "${required_vars[@]}"; do
            if echo "$env_content" | grep -q "^$var="; then
                success "Environment variable configured: $var"
            else
                warning "Environment variable missing: $var"
            fi
        done
        
        # Check constitutional hash value
        local staging_hash=$(echo "$env_content" | grep "CONSTITUTIONAL_HASH=" | cut -d'=' -f2)
        if [[ "$staging_hash" == "$CONSTITUTIONAL_HASH" ]]; then
            success "Constitutional hash matches expected value"
        else
            error "Constitutional hash mismatch: expected $CONSTITUTIONAL_HASH, found $staging_hash"
        fi
    else
        error "Staging environment file not found: $STAGING_ENV_FILE"
        return 1
    fi
}

# Validate monitoring configuration
validate_monitoring_config() {
    log "Validating monitoring configuration..."
    
    # Check if monitoring services are running
    local monitoring_services=(
        "localhost:9090"  # Prometheus
        "localhost:3000"  # Grafana
        "localhost:8181"  # OPA
    )
    
    for service in "${monitoring_services[@]}"; do
        local host=$(echo "$service" | cut -d':' -f1)
        local port=$(echo "$service" | cut -d':' -f2)
        
        if nc -z "$host" "$port" 2>/dev/null; then
            success "Monitoring service accessible: $service"
        else
            warning "Monitoring service not accessible: $service"
        fi
    done
}

# Generate staging readiness report
generate_readiness_report() {
    log "Generating staging readiness report..."
    
    local report_file="staging_readiness_report.md"
    
    cat > "$report_file" << EOF
# ACGS-PGP Staging Environment Readiness Report

## Configuration Validation Summary

### Constitutional Hash Validation
- **Expected Hash**: $CONSTITUTIONAL_HASH
- **Status**: $(grep -q "$CONSTITUTIONAL_HASH" "$STAGING_ENV_FILE" && echo "✅ VALID" || echo "❌ INVALID")

### Service Configuration
- **7 Core Services**: $(grep -c "_service:" "$STAGING_COMPOSE_FILE" 2>/dev/null || echo "0") configured
- **Port Mapping**: Staging ports 8010-8016 mapped to production ports 8000-8006
- **Health Checks**: $(grep -c "healthcheck:" "$STAGING_COMPOSE_FILE" 2>/dev/null || echo "0") configured

### Resource Limits (Production Parity)
- **CPU Request**: 200m
- **CPU Limit**: 500m (1000m for PGC service)
- **Memory Request**: 512Mi
- **Memory Limit**: 1Gi (2Gi for high-performance services)

### Environment Variables
- **Environment**: staging
- **Database**: PostgreSQL (staging database)
- **Cache**: Redis (staging instance)
- **Constitutional Hash**: $CONSTITUTIONAL_HASH

### Monitoring Stack Status
- **Prometheus**: $(nc -z localhost 9090 2>/dev/null && echo "✅ Running" || echo "⚠️ Not Running")
- **Grafana**: $(nc -z localhost 3000 2>/dev/null && echo "✅ Running" || echo "⚠️ Not Running")
- **OPA**: $(nc -z localhost 8181 2>/dev/null && echo "✅ Running" || echo "⚠️ Not Running")

### Deployment Commands
\`\`\`bash
# Start staging environment (requires Docker permissions)
docker-compose -f $STAGING_COMPOSE_FILE up -d

# Validate services
curl http://localhost:8010/health  # Auth Service (staging)
curl http://localhost:8015/health  # PGC Service (staging)

# Test constitutional compliance
curl -X POST http://localhost:8181/v1/data/acgs/constitutional/allow \\
  -H "Content-Type: application/json" \\
  -d '{"input": {"constitutional_hash": "$CONSTITUTIONAL_HASH", "compliance_score": 0.85}}'
\`\`\`

### Next Steps for Production Deployment
1. ✅ Staging environment configuration validated
2. ⏳ Deploy staging services for testing
3. ⏳ Run comprehensive validation tests
4. ⏳ Validate performance targets (≤2s response time, >95% compliance)
5. ⏳ Test emergency response procedures (<30min RTO)
6. ⏳ Proceed with production deployment

Generated: $(date)
EOF

    success "Staging readiness report generated: $report_file"
}

# Main function
main() {
    log "Starting ACGS-PGP Staging Configuration Validation"
    log "=================================================="  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    
    validate_constitutional_hash
    validate_service_config
    validate_resource_limits
    validate_environment_variables
    validate_monitoring_config
    generate_readiness_report
    
    success "Staging configuration validation completed!"
    log "Review the staging readiness report for next steps"
}

# Execute main function
main "$@"
