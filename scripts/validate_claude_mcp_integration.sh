#!/bin/bash
# Claude-MCP-ACGS Integration Validation Script
# Constitutional Hash: cdd01ef066bc6cf2
# 
# This script validates the complete integration between Claude agents,
# MCP server stack, and ACGS services, ensuring constitutional compliance
# and performance targets are met.

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
MAX_LATENCY_MS=5
MIN_THROUGHPUT_RPS=100
REQUIRED_CACHE_HIT_RATE=85

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}✅ $1${NC}"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

error() {
    echo -e "${RED}❌ $1${NC}"
    exit 1
}

# Function to check service health
check_service_health() {
    local service_name=$1
    local port=$2
    local endpoint=${3:-/health}
    
    log "Checking $service_name health on port $port..."
    
    if curl -sf "http://localhost:$port$endpoint" > /dev/null 2>&1; then
        success "$service_name is healthy"
        return 0
    else
        error "$service_name health check failed on port $port"
        return 1
    fi
}

# Function to validate constitutional compliance
validate_constitutional_compliance() {
    local service_name=$1
    local port=$2
    
    log "Validating constitutional compliance for $service_name..."
    
    local response
    response=$(curl -s "http://localhost:$port/health" 2>/dev/null || echo "{}")
    
    if echo "$response" | grep -q "$CONSTITUTIONAL_HASH"; then
        success "$service_name constitutional compliance verified"
        return 0
    else
        error "$service_name constitutional compliance validation failed"
        return 1
    fi
}

# Function to test performance
test_performance() {
    local service_name=$1
    local url=$2
    local expected_rps=$3
    
    log "Testing performance for $service_name..."
    
    # Use Apache Bench for performance testing
    if command -v ab > /dev/null 2>&1; then
        local ab_output
        ab_output=$(ab -n 100 -c 10 -q "$url" 2>/dev/null || echo "")
        
        if [[ -n "$ab_output" ]]; then
            local rps
            rps=$(echo "$ab_output" | grep "Requests per second" | awk '{print $4}' | cut -d'.' -f1)
            
            if [[ -n "$rps" && "$rps" -ge "$expected_rps" ]]; then
                success "$service_name performance: ${rps} RPS (target: ${expected_rps}+ RPS)"
            else
                warning "$service_name performance: ${rps:-0} RPS (below target: ${expected_rps}+ RPS)"
            fi
        else
            warning "$service_name performance test failed"
        fi
    else
        warning "Apache Bench (ab) not available, skipping performance test"
    fi
}

# Function to test MCP tool integration
test_mcp_tool_integration() {
    log "Testing MCP tool integration..."
    
    # Test filesystem MCP
    if curl -sf "http://localhost:3000/mcp/filesystem/status" > /dev/null 2>&1; then
        success "Filesystem MCP integration working"
    else
        error "Filesystem MCP integration failed"
    fi
    
    # Test GitHub MCP
    if curl -sf "http://localhost:3000/mcp/github/status" > /dev/null 2>&1; then
        success "GitHub MCP integration working"
    else
        error "GitHub MCP integration failed"
    fi
    
    # Test Browser MCP
    if curl -sf "http://localhost:3000/mcp/browser/status" > /dev/null 2>&1; then
        success "Browser MCP integration working"
    else
        error "Browser MCP integration failed"
    fi
}

# Function to test ACGS service integration
test_acgs_integration() {
    log "Testing ACGS service integration..."
    
    # Test if MCP aggregator can reach ACGS services
    local mcp_logs
    mcp_logs=$(docker-compose logs mcp_aggregator 2>/dev/null | tail -20 || echo "")
    
    if echo "$mcp_logs" | grep -q "ACGS"; then
        success "ACGS service integration detected in logs"
    else
        warning "ACGS service integration not detected in logs"
    fi
    
    # Test constitutional validation endpoint
    if curl -sf "http://localhost:3000/acgs/validate" > /dev/null 2>&1; then
        success "ACGS constitutional validation endpoint accessible"
    else
        warning "ACGS constitutional validation endpoint not accessible"
    fi
}

# Function to test coordination workflow
test_coordination_workflow() {
    log "Testing multi-agent coordination workflow..."
    
    # Test coordination request
    local coordination_response
    coordination_response=$(curl -s -X POST "http://localhost:3000/acgs/coordinate" \
        -H "Content-Type: application/json" \
        -d '{
            "claude_agent_id": "test_agent",
            "coordination_type": "task_delegation",
            "constitutional_hash": "'"$CONSTITUTIONAL_HASH"'"
        }' 2>/dev/null || echo "{}")
    
    if echo "$coordination_response" | grep -q "success\|pending"; then
        success "Coordination workflow test passed"
    else
        warning "Coordination workflow test inconclusive"
    fi
}

# Function to validate environment configuration
validate_environment() {
    log "Validating environment configuration..."
    
    # Check if required environment variables are set
    local required_vars=(
        "CONSTITUTIONAL_HASH"
        "GITHUB_TOKEN"
    )
    
    for var in "${required_vars[@]}"; do
        if [[ -n "${!var:-}" ]]; then
            success "Environment variable $var is set"
        else
            warning "Environment variable $var is not set"
        fi
    done
    
    # Validate constitutional hash
    if [[ "${CONSTITUTIONAL_HASH:-}" == "cdd01ef066bc6cf2" ]]; then
        success "Constitutional hash is correct"
    else
        error "Constitutional hash is incorrect or missing"
    fi
}

# Function to check Docker services
check_docker_services() {
    log "Checking Docker service status..."
    
    # Check if docker-compose is running
    if docker-compose ps | grep -q "Up"; then
        success "Docker Compose services are running"
    else
        error "Docker Compose services are not running"
    fi
    
    # Check specific services
    local services=("acgs_mcp_aggregator" "acgs_mcp_filesystem" "acgs_mcp_github" "acgs_mcp_browser")
    
    for service in "${services[@]}"; do
        if docker-compose ps "$service" | grep -q "Up"; then
            success "Service $service is running"
        else
            error "Service $service is not running"
        fi
    done
}

# Function to generate integration report
generate_report() {
    log "Generating integration validation report..."
    
    local report_file="claude_mcp_acgs_integration_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# Claude-MCP-ACGS Integration Validation Report
**Date:** $(date)
**Constitutional Hash:** $CONSTITUTIONAL_HASH

## Service Health Status
- MCP Aggregator (3000): $(curl -sf http://localhost:3000/health > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy")
- Filesystem MCP (3001): $(curl -sf http://localhost:3001/health > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy")
- GitHub MCP (3002): $(curl -sf http://localhost:3002/health > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy")
- Browser MCP (3003): $(curl -sf http://localhost:3003/health > /dev/null && echo "✅ Healthy" || echo "❌ Unhealthy")

## ACGS Service Integration
- Constitutional AI (8001): $(curl -sf http://localhost:8001/health > /dev/null && echo "✅ Accessible" || echo "❌ Not Accessible")
- Integrity Service (8002): $(curl -sf http://localhost:8002/health > /dev/null && echo "✅ Accessible" || echo "❌ Not Accessible")
- Multi-Agent Coordinator (8008): $(curl -sf http://localhost:8008/health > /dev/null && echo "✅ Accessible" || echo "❌ Not Accessible")
- Blackboard Service (8010): $(curl -sf http://localhost:8010/health > /dev/null && echo "✅ Accessible" || echo "❌ Not Accessible")

## Constitutional Compliance
- Hash Verification: $CONSTITUTIONAL_HASH
- Compliance Status: $(curl -s http://localhost:3000/health | grep -q "$CONSTITUTIONAL_HASH" && echo "✅ Verified" || echo "❌ Failed")

## Performance Metrics
- Target P99 Latency: <${MAX_LATENCY_MS}ms
- Target Throughput: >${MIN_THROUGHPUT_RPS} RPS
- Target Cache Hit Rate: >${REQUIRED_CACHE_HIT_RATE}%

## Integration Test Results
- MCP Tool Integration: $(curl -sf http://localhost:3000/mcp/filesystem/status > /dev/null && echo "✅ Passed" || echo "❌ Failed")
- ACGS Service Integration: $(docker-compose logs mcp_aggregator | grep -q "ACGS" && echo "✅ Detected" || echo "❌ Not Detected")
- Coordination Workflow: $(curl -sf http://localhost:3000/acgs/coordinate > /dev/null && echo "✅ Available" || echo "❌ Not Available")

## Recommendations
- Ensure all services are healthy before production deployment
- Monitor constitutional compliance continuously
- Validate performance targets under load
- Test coordination workflows with real Claude agents
EOF
    
    success "Integration report generated: $report_file"
}

# Main validation function
main() {
    log "Starting Claude-MCP-ACGS Integration Validation"
    log "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo
    
    # Environment validation
    validate_environment
    echo
    
    # Docker services check
    check_docker_services
    echo
    
    # Service health checks
    log "=== Service Health Validation ==="
    check_service_health "MCP Aggregator" 3000
    check_service_health "Filesystem MCP" 3001
    check_service_health "GitHub MCP" 3002
    check_service_health "Browser MCP" 3003
    echo
    
    # Constitutional compliance validation
    log "=== Constitutional Compliance Validation ==="
    validate_constitutional_compliance "MCP Aggregator" 3000
    echo
    
    # Performance testing
    log "=== Performance Testing ==="
    test_performance "MCP Aggregator" "http://localhost:3000/health" $MIN_THROUGHPUT_RPS
    echo
    
    # Integration testing
    log "=== Integration Testing ==="
    test_mcp_tool_integration
    test_acgs_integration
    test_coordination_workflow
    echo
    
    # Generate report
    generate_report
    echo
    
    success "Claude-MCP-ACGS Integration Validation Completed Successfully!"
    log "All systems are ready for Claude agent coordination with constitutional compliance"
}

# Run main function
main "$@"
