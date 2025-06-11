#!/bin/bash

# ACGS-1 Data Flywheel Integration Setup Script
# This script sets up the NVIDIA Data Flywheel with ACGS-1 constitutional governance integration

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
ACGS_ROOT="/home/dislove/ACGS-1"

print_status "🚀 ACGS-1 Data Flywheel Integration Setup"
echo "=========================================="
echo "Project Directory: $PROJECT_DIR"
echo "ACGS-1 Root: $ACGS_ROOT"
echo ""

# Check prerequisites
print_status "Step 1: Checking prerequisites..."

# Check if we're in the right directory
if [ ! -f "$PROJECT_DIR/config/acgs_config.yaml" ]; then
    print_error "ACGS configuration not found. Please run this script from the data-flywheel integration directory."
    exit 1
fi

# Check Docker
if ! command -v docker > /dev/null 2>&1; then
    print_error "Docker is required but not installed. Please install Docker first."
    exit 1
fi
print_success "Docker is available"

# Check Docker Compose
if ! command -v docker-compose > /dev/null 2>&1; then
    print_error "Docker Compose is required but not installed. Please install Docker Compose first."
    exit 1
fi
print_success "Docker Compose is available"

# Check ACGS-1 services
print_status "Checking ACGS-1 services..."
acgs_services_healthy=true

for port in 8000 8001 8002 8003 8004 8005 8006; do
    if curl -f -s --connect-timeout 2 "http://localhost:$port/health" > /dev/null 2>&1; then
        print_success "ACGS-1 service on port $port is healthy"
    else
        print_warning "ACGS-1 service on port $port is not responding"
        acgs_services_healthy=false
    fi
done

if [ "$acgs_services_healthy" = false ]; then
    print_warning "Some ACGS-1 services are not healthy. The integration will still work but with limited functionality."
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Setup cancelled by user"
        exit 1
    fi
fi

# Step 2: Environment configuration
print_status "Step 2: Setting up environment configuration..."

# Create .env file if it doesn't exist
if [ ! -f "$PROJECT_DIR/.env" ]; then
    print_status "Creating .env file..."
    cat > "$PROJECT_DIR/.env" << EOF
# ACGS-1 Data Flywheel Integration Environment Configuration

# NGC API Key (required for NeMo Microservices)
NGC_API_KEY=your_ngc_api_key_here

# ACGS-1 Integration Settings
ACGS_BASE_URL=http://localhost
CONSTITUTIONAL_COMPLIANCE_THRESHOLD=0.95
GOVERNANCE_WORKFLOW_VALIDATION=true
POLICY_SYNTHESIS_OPTIMIZATION=true
FORMAL_VERIFICATION_ENHANCEMENT=true

# Database Configuration
ELASTICSEARCH_URL=http://localhost:9200
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=acgs_flywheel
REDIS_URL=redis://localhost:6379/1

# Service Configuration
FLYWHEEL_API_PORT=8010
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001

# Logging Configuration
LOG_LEVEL=INFO
CONSTITUTIONAL_LOG_LEVEL=DEBUG

# Docker Configuration
TAG=latest
COMPOSE_PROJECT_NAME=acgs_flywheel
EOF
    print_success "Created .env file"
    print_warning "Please edit .env file and add your NGC_API_KEY"
else
    print_success ".env file already exists"
fi

# Step 3: Create necessary directories
print_status "Step 3: Creating necessary directories..."

directories=(
    "logs"
    "logs/constitutional"
    "data"
    "data/governance"
    "data/models"
    "data/traffic"
)

for dir in "${directories[@]}"; do
    mkdir -p "$PROJECT_DIR/$dir"
    print_success "Created directory: $dir"
done

# Step 4: Install Python dependencies
print_status "Step 4: Installing Python dependencies..."

cd "$PROJECT_DIR"

# Check if uv is available
if command -v uv > /dev/null 2>&1; then
    print_status "Installing dependencies with uv..."
    uv sync
    print_success "Dependencies installed with uv"
else
    print_warning "uv not found, falling back to pip..."
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Dependencies installed with pip"
    else
        print_warning "No requirements.txt found, skipping Python dependency installation"
    fi
fi

# Step 5: Build Docker images
print_status "Step 5: Building Docker images..."

docker-compose -f deploy/docker-compose.acgs.yaml build
print_success "Docker images built successfully"

# Step 6: Initialize databases
print_status "Step 6: Initializing databases..."

# Start database services
docker-compose -f deploy/docker-compose.acgs.yaml up -d elasticsearch mongodb redis
print_status "Database services started, waiting for initialization..."

# Wait for services to be ready
sleep 30

# Check if services are healthy
for service in elasticsearch mongodb redis; do
    if docker-compose -f deploy/docker-compose.acgs.yaml ps $service | grep -q "healthy\|Up"; then
        print_success "$service is ready"
    else
        print_warning "$service may not be fully ready"
    fi
done

# Step 7: Create Elasticsearch indices
print_status "Step 7: Creating Elasticsearch indices..."

# Create governance traffic index
curl -X PUT "localhost:9200/acgs_governance_traffic" -H 'Content-Type: application/json' -d'
{
  "mappings": {
    "properties": {
      "timestamp": {"type": "date"},
      "workload_id": {"type": "keyword"},
      "client_id": {"type": "keyword"},
      "service_name": {"type": "keyword"},
      "request": {"type": "object"},
      "response": {"type": "object"},
      "constitutional_context": {"type": "object"},
      "performance_metrics": {"type": "object"}
    }
  }
}' > /dev/null 2>&1

if [ $? -eq 0 ]; then
    print_success "Elasticsearch indices created"
else
    print_warning "Failed to create Elasticsearch indices (may already exist)"
fi

# Step 8: Validate installation
print_status "Step 8: Validating installation..."

# Start all services
docker-compose -f deploy/docker-compose.acgs.yaml up -d
print_status "All services started, waiting for readiness..."

sleep 60

# Check service health
if curl -f -s "http://localhost:8010/health" > /dev/null 2>&1; then
    print_success "ACGS-1 Data Flywheel API is healthy"
else
    print_error "ACGS-1 Data Flywheel API is not responding"
fi

if curl -f -s "http://localhost:8010/constitutional/health" > /dev/null 2>&1; then
    print_success "Constitutional governance integration is operational"
else
    print_warning "Constitutional governance integration may not be fully operational"
fi

# Final summary
echo ""
print_success "🎉 ACGS-1 Data Flywheel Integration Setup Complete!"
echo "=================================================="
echo ""
echo "✅ Services Status:"
echo "   - Data Flywheel API: http://localhost:8010"
echo "   - Constitutional Health: http://localhost:8010/constitutional/health"
echo "   - Prometheus Metrics: http://localhost:9090"
echo "   - Grafana Dashboards: http://localhost:3001 (admin/acgs_admin)"
echo ""
echo "🔧 Management Commands:"
echo "   - Start services: docker-compose -f deploy/docker-compose.acgs.yaml up -d"
echo "   - Stop services: docker-compose -f deploy/docker-compose.acgs.yaml down"
echo "   - View logs: docker-compose -f deploy/docker-compose.acgs.yaml logs -f"
echo "   - Health check: curl http://localhost:8010/health"
echo ""
echo "📚 Next Steps:"
echo "   1. Edit .env file and add your NGC_API_KEY"
echo "   2. Test constitutional governance integration"
echo "   3. Create your first governance optimization job"
echo "   4. Monitor constitutional compliance metrics"
echo ""
echo "🏛️ Constitutional Governance Features:"
echo "   - Policy synthesis optimization"
echo "   - Formal verification enhancement"
echo "   - Constitutional compliance validation"
echo "   - Governance workflow integration"
echo ""

if [ "$acgs_services_healthy" = true ]; then
    print_success "🎯 All ACGS-1 services are healthy and ready for integration!"
else
    print_warning "⚠️ Some ACGS-1 services need attention. Check service health before proceeding."
fi

print_status "Setup completed successfully!"
