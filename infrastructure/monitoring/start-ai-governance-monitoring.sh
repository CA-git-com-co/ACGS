# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash

# ACGS AI Governance Monitoring Stack Startup Script
# Starts enhanced monitoring infrastructure for Constitutional AI and Multi-Armed Bandits

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.ai-governance.yml"
PROJECT_NAME="acgs-ai-governance"
HEALTH_CHECK_TIMEOUT=300  # 5 minutes
HEALTH_CHECK_INTERVAL=10  # 10 seconds

echo -e "${BLUE}🚀 Starting ACGS AI Governance Monitoring Stack...${NC}"

# Check if Docker and Docker Compose are available
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed or not in PATH${NC}"
    exit 1
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
mkdir -p ./config
mkdir -p ./dashboards/ai-governance
mkdir -p ./dashboards/constitutional-ai
mkdir -p ./dashboards/bandit-algorithms
mkdir -p ./policies
mkdir -p ./evidently-projects

# Check if configuration files exist
echo -e "${YELLOW}🔍 Checking configuration files...${NC}"
required_files=(
    "config/prometheus-ai-governance.yml"
    "config/ai-governance-alert-rules.yml"
    "config/opa-ai-governance-config.yaml"
    "policies/constitutional-ai-governance.rego"
)

for file in "${required_files[@]}"; do
    if [[ ! -f "$file" ]]; then
        echo -e "${RED}❌ Required file not found: $file${NC}"
        exit 1
    fi
done

echo -e "${GREEN}✅ All required configuration files found${NC}"

# Stop any existing containers
echo -e "${YELLOW}🛑 Stopping any existing AI governance monitoring containers...${NC}"
docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" down --remove-orphans 2>/dev/null || true

# Pull latest images
echo -e "${YELLOW}📥 Pulling latest Docker images...${NC}"
docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" pull

# Start the monitoring stack
echo -e "${YELLOW}🚀 Starting AI governance monitoring services...${NC}"
docker-compose -f "$COMPOSE_FILE" -p "$PROJECT_NAME" up -d

# Function to check service health
check_service_health() {
    local service_name=$1
    local health_url=$2
    local max_attempts=$((HEALTH_CHECK_TIMEOUT / HEALTH_CHECK_INTERVAL))
    local attempt=1

    echo -e "${YELLOW}🔍 Checking health of $service_name...${NC}"
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -s -f "$health_url" > /dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is healthy${NC}"
            return 0
        fi
        
        echo -e "${YELLOW}⏳ Waiting for $service_name (attempt $attempt/$max_attempts)...${NC}"
        sleep $HEALTH_CHECK_INTERVAL
        ((attempt++))
    done
    
    echo -e "${RED}❌ $service_name failed to become healthy within $HEALTH_CHECK_TIMEOUT seconds${NC}"
    return 1
}

# Wait for services to start and perform health checks
echo -e "${BLUE}🏥 Performing health checks...${NC}"

# Check Prometheus
check_service_health "Prometheus" "http://localhost:9091/-/healthy"

# Check Grafana
check_service_health "Grafana" "http://localhost:3001/api/health"

# Check Evidently AI
check_service_health "Evidently AI" "http://localhost:8080/health"

# Check OPA
check_service_health "OPA Policy Engine" "http://localhost:8181/health"

# Check AlertManager
check_service_health "AlertManager" "http://localhost:9094/-/healthy"

# Display service URLs
echo -e "${GREEN}🎉 ACGS AI Governance Monitoring Stack is running!${NC}"
echo ""
echo -e "${BLUE}📊 Service URLs:${NC}"
echo -e "  • Prometheus:     ${GREEN}http://localhost:9091${NC}"
echo -e "  • Grafana:        ${GREEN}http://localhost:3001${NC} (admin/acgs_ai_governance_admin)"
echo -e "  • Evidently AI:   ${GREEN}http://localhost:8080${NC}"
echo -e "  • OPA Engine:     ${GREEN}http://localhost:8181${NC}"
echo -e "  • AlertManager:   ${GREEN}http://localhost:9094${NC}"
echo -e "  • Jaeger Tracing: ${GREEN}http://localhost:16686${NC}"
echo ""

# Display monitoring targets
echo -e "${BLUE}🎯 Monitoring Targets:${NC}"
echo -e "  • Constitutional AI Compliance"
echo -e "  • Multi-Armed Bandit Performance"
echo -e "  • Policy Governance Metrics"
echo -e "  • AI Model Drift Detection"
echo -e "  • System Performance"
echo ""

# Display key metrics to watch
echo -e "${BLUE}📈 Key Metrics to Monitor:${NC}"
echo -e "  • constitutional_compliance_score"
echo -e "  • conservative_linucb_safety_violations_total"
echo -e "  • mab_exploration_rate"
echo -e "  • policy_violations_total"
echo -e "  • llm_reliability_score"
echo ""

# Check if services are accessible
echo -e "${YELLOW}🔍 Verifying service accessibility...${NC}"

services=(
    "Prometheus:http://localhost:9091"
    "Grafana:http://localhost:3001"
    "Evidently:http://localhost:8080"
    "OPA:http://localhost:8181"
    "AlertManager:http://localhost:9094"
)

for service in "${services[@]}"; do
    name="${service%%:*}"
    url="${service##*:}"
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "  ✅ $name is accessible"
    else
        echo -e "  ❌ $name is not accessible at $url"
    fi
done

echo ""
echo -e "${GREEN}🚀 AI Governance Monitoring Stack startup complete!${NC}"
echo -e "${YELLOW}💡 Next steps:${NC}"
echo -e "  1. Import Grafana dashboards for AI governance"
echo -e "  2. Configure alert notification channels"
echo -e "  3. Set up Evidently AI projects for model monitoring"
echo -e "  4. Review OPA policies and update as needed"
echo ""
echo -e "${BLUE}📚 Documentation: https://docs.acgs.ai/monitoring/ai-governance${NC}"

# Optional: Open Grafana in browser (uncomment if desired)
# if command -v xdg-open &> /dev/null; then
#     echo -e "${YELLOW}🌐 Opening Grafana in browser...${NC}"
#     xdg-open http://localhost:3001
# elif command -v open &> /dev/null; then
#     echo -e "${YELLOW}🌐 Opening Grafana in browser...${NC}"
#     open http://localhost:3001
# fi
