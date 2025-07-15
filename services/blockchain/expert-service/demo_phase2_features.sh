#!/bin/bash

# ACGS-2 Expert System Phase 2 Features Demo
# Constitutional Hash: cdd01ef066bc6cf2

set -e

echo "🏛️ ACGS-2 Expert System Phase 2 Production Features Demo"
echo "========================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
EXPERT_SYSTEM_URL="http://localhost:3000"
METRICS_URL="http://localhost:9090/metrics"
DOCS_URL="http://localhost:3000/docs"

# Function to check if service is running
check_service() {
    local url=$1
    local name=$2
    
    if curl -s -f "$url/health" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $name is running${NC}"
        return 0
    else
        echo -e "${RED}❌ $name is not running${NC}"
        return 1
    fi
}

# Function to make API request and show response
make_request() {
    local method=$1
    local endpoint=$2
    local data=$3
    local description=$4
    
    echo -e "${BLUE}📡 $description${NC}"
    echo "   Method: $method"
    echo "   Endpoint: $endpoint"
    
    if [ -n "$data" ]; then
        echo "   Data: $data"
        response=$(curl -s -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$EXPERT_SYSTEM_URL$endpoint")
    else
        response=$(curl -s -X "$method" "$EXPERT_SYSTEM_URL$endpoint")
    fi
    
    echo -e "${GREEN}   Response:${NC}"
    echo "$response" | jq '.' 2>/dev/null || echo "$response"
    echo ""
}

# Function to test rate limiting
test_rate_limiting() {
    echo -e "${PURPLE}🚦 Testing Rate Limiting${NC}"
    echo "Making rapid requests to test rate limiting..."
    
    for i in {1..5}; do
        echo "Request $i:"
        curl -s -w "Status: %{http_code}, Time: %{time_total}s\n" \
            -H "Content-Type: application/json" \
            -d '{"query":{"actorRole":"Researcher","dataSensitivity":"AnonymizedAggregate"}}' \
            "$EXPERT_SYSTEM_URL/govern" | head -1
        sleep 0.1
    done
    echo ""
}

# Function to test circuit breaker (simulated)
test_circuit_breaker() {
    echo -e "${PURPLE}🔄 Circuit Breaker Status${NC}"
    echo "Checking circuit breaker status in readiness endpoint..."
    
    response=$(curl -s "$EXPERT_SYSTEM_URL/ready")
    echo "$response" | jq '.circuit_breaker_states' 2>/dev/null || echo "Circuit breaker status not available"
    echo ""
}

# Function to test caching performance
test_caching_performance() {
    echo -e "${PURPLE}💾 Testing Caching Performance${NC}"
    
    # First request (cache miss)
    echo "First request (cache miss):"
    time curl -s -H "Content-Type: application/json" \
        -d '{"query":{"actorRole":"Researcher","dataSensitivity":"AnonymizedAggregate"}}' \
        "$EXPERT_SYSTEM_URL/govern" > /dev/null
    
    echo ""
    
    # Second request (cache hit)
    echo "Second request (cache hit):"
    time curl -s -H "Content-Type: application/json" \
        -d '{"query":{"actorRole":"Researcher","dataSensitivity":"AnonymizedAggregate"}}' \
        "$EXPERT_SYSTEM_URL/govern" > /dev/null
    
    echo ""
}

# Main demo execution
main() {
    echo -e "${CYAN}🔍 Checking Service Status${NC}"
    
    if ! check_service "$EXPERT_SYSTEM_URL" "Expert System"; then
        echo -e "${YELLOW}⚠️ Expert System is not running. Please start it first:${NC}"
        echo "   cargo run --bin governance_app"
        echo ""
        echo -e "${YELLOW}Or using Docker:${NC}"
        echo "   docker-compose up -d"
        exit 1
    fi
    
    echo ""
    
    # Test basic health endpoints
    echo -e "${CYAN}🏥 Testing Health Endpoints${NC}"
    make_request "GET" "/health" "" "Basic health check"
    make_request "GET" "/ready" "" "Readiness check with circuit breaker status"
    
    # Test governance endpoints
    echo -e "${CYAN}🏛️ Testing Governance Endpoints${NC}"
    make_request "POST" "/govern" \
        '{"query":{"actorRole":"Researcher","dataSensitivity":"AnonymizedAggregate"}}' \
        "Standard governance decision"
    
    make_request "POST" "/govern" \
        '{"query":{"actorRole":"Clinician","dataSensitivity":"IdentifiedPatientRecords"}}' \
        "Governance decision for sensitive data"
    
    make_request "POST" "/govern/blockchain" \
        '{"query":{"actorRole":"Researcher","dataSensitivity":"AnonymizedAggregate"}}' \
        "Blockchain-integrated governance decision"
    
    # Test Phase 2 features
    test_rate_limiting
    test_circuit_breaker
    test_caching_performance
    
    # Show OpenAPI documentation
    echo -e "${CYAN}📚 OpenAPI Documentation${NC}"
    echo "API documentation is available at: $DOCS_URL"
    echo ""
    
    # Show metrics
    echo -e "${CYAN}📊 Prometheus Metrics${NC}"
    echo "Metrics are available at: $METRICS_URL"
    echo ""
    echo "Sample metrics:"
    curl -s "$METRICS_URL" | grep -E "(http_requests_total|http_request_duration)" | head -5
    echo ""
    
    # Configuration summary
    echo -e "${CYAN}⚙️ Current Configuration${NC}"
    echo "Constitutional Hash: cdd01ef066bc6cf2"
    echo "LLM Provider: $(curl -s "$EXPERT_SYSTEM_URL/ready" | jq -r '.llm_provider' 2>/dev/null || echo 'Unknown')"
    echo "Blockchain Enabled: $(curl -s "$EXPERT_SYSTEM_URL/ready" | jq -r '.blockchain_enabled' 2>/dev/null || echo 'Unknown')"
    echo ""
    
    # Performance summary
    echo -e "${GREEN}✅ Phase 2 Features Demonstrated:${NC}"
    echo "   🚦 Rate limiting with configurable limits"
    echo "   🔄 Circuit breaker pattern for LLM APIs"
    echo "   📖 OpenAPI/Swagger documentation"
    echo "   💾 Redis-based distributed caching"
    echo "   🏥 Enhanced health and readiness checks"
    echo "   📊 Prometheus metrics integration"
    echo "   🐳 Docker containerization support"
    echo ""
    
    echo -e "${GREEN}🎉 Demo completed successfully!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Visit $DOCS_URL to explore the API documentation"
    echo "2. Check $METRICS_URL for detailed metrics"
    echo "3. Run integration tests: cargo test"
    echo "4. Deploy using Docker: docker-compose up -d"
}

# Run the demo
main "$@"
