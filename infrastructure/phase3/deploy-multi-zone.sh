#!/bin/bash
# ACGS Phase 3A Multi-Zone Infrastructure Deployment Script
# Constitutional Hash: cdd01ef066bc6cf2

set -e

echo "🚀 Starting ACGS Phase 3A Multi-Zone Infrastructure Deployment"
echo "📋 Constitutional Hash: cdd01ef066bc6cf2"
echo "🎯 Target: 99.9% uptime with multi-zone high availability"
echo "============================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2

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

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if running as root or with docker permissions
    if ! docker ps &> /dev/null; then
        print_error "Cannot access Docker. Please run with sudo or add user to docker group"
        exit 1
    fi
    
    print_success "Prerequisites check passed"
}

# Create environment file
create_env_file() {
    print_status "Creating environment configuration..."
    
    cat > config/environments/development.env <<EOF
# ACGS Phase 3A Environment Configuration
# Constitutional Hash: cdd01ef066bc6cf2

# PostgreSQL Configuration
POSTGRES_PASSWORD=os.environ.get("PASSWORD")
POSTGRES_REPLICATION_PASSWORD=os.environ.get("PASSWORD")
REPLICATION_PASSWORD=os.environ.get("PASSWORD")
POSTGRES_EXPORTER_PASSWORD=os.environ.get("PASSWORD")

# Grafana Configuration
GRAFANA_ADMIN_PASSWORD=os.environ.get("PASSWORD")
GRAFANA_DB_PASSWORD=os.environ.get("PASSWORD")

# Redis Configuration
REDIS_PASSWORD=os.environ.get("PASSWORD")

# SSL Configuration
SSL_CERT_PATH=./config/ssl
SSL_KEY_PATH=./config/ssl

# Constitutional Compliance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
EOF
    
    print_success "Environment file created"
}

# Create SSL certificates
create_ssl_certificates() {
    print_status "Creating SSL certificates..."
    
    mkdir -p config/ssl
    
    # Create CA certificate
    openssl req -new -x509 -days 365 -nodes -text \
        -out config/ssl/ca.crt \
        -keyout config/ssl/ca.key \
        -subj "/CN=ACGS-CA/O=ACGS/C=US"
    
    # Create server certificate
    openssl req -new -nodes -text \
        -out config/ssl/server.csr \
        -keyout config/ssl/server.key \
        -subj "/CN=acgs.local/O=ACGS/C=US"
    
    openssl x509 -req -in config/ssl/server.csr \
        -text -days 365 \
        -CA config/ssl/ca.crt \
        -CAkey config/ssl/ca.key \
        -CAcreateserial \
        -out config/ssl/server.crt
    
    # Create combined certificate for HAProxy
    cat config/ssl/server.crt config/ssl/server.key > config/ssl/acgs.pem
    
    # Set permissions
    chmod 600 config/ssl/*.key config/ssl/*.pem
    chmod 644 config/ssl/*.crt
    
    print_success "SSL certificates created"
}

# Make scripts executable
make_scripts_executable() {
    print_status "Making scripts executable..."
    
    chmod +x scripts/postgresql/*.sh
    
    print_success "Scripts made executable"
}

# Deploy infrastructure
deploy_infrastructure() {
    print_status "Deploying multi-zone infrastructure..."
    
    # Networks will be created automatically by Docker Compose
    print_status "Preparing multi-zone infrastructure deployment..."
    
    # Deploy in stages for proper dependency management
    print_status "Stage 1: Deploying PostgreSQL Primary..."
    docker-compose -f multi-zone-deployment.yml up -d postgres-primary
    
    # Wait for primary to be ready
    print_status "Waiting for PostgreSQL Primary to be ready..."
    sleep 30
    
    print_status "Stage 2: Deploying PostgreSQL Replicas..."
    docker-compose -f multi-zone-deployment.yml up -d postgres-replica-a postgres-replica-b
    
    # Wait for replicas to sync
    print_status "Waiting for replicas to sync..."
    sleep 20
    
    print_status "Stage 3: Deploying Redis Cluster..."
    docker-compose -f multi-zone-deployment.yml up -d redis-cluster-1 redis-cluster-2 redis-cluster-3
    
    # Wait for Redis nodes to start
    sleep 10
    
    # Initialize Redis cluster
    print_status "Initializing Redis cluster..."
    docker exec redis-cluster-1 redis-cli --cluster create \
        redis-cluster-1:7001 redis-cluster-2:7002 redis-cluster-3:7003 \
        --cluster-replicas 0 --cluster-yes || true
    
    print_status "Stage 4: Deploying ACGS Services..."
    docker-compose -f multi-zone-deployment.yml up -d acgs-auth-zone-a acgs-auth-zone-b acgs-auth-zone-c
    
    print_status "Stage 5: Deploying Monitoring..."
    docker-compose -f multi-zone-deployment.yml up -d prometheus-ha grafana-ha
    
    print_status "Stage 6: Deploying Load Balancer..."
    docker-compose -f multi-zone-deployment.yml up -d acgs-load-balancer
    
    print_success "Multi-zone infrastructure deployed"
}

# Validate deployment
validate_deployment() {
    print_status "Validating deployment..."
    
    # Check PostgreSQL Primary
    if docker exec postgres-primary pg_isready -U acgs_admin -d acgs_production; then
        print_success "PostgreSQL Primary is ready"
    else
        print_error "PostgreSQL Primary is not ready"
        return 1
    fi
    
    # Check PostgreSQL Replicas
    if docker exec postgres-replica-a pg_isready -U acgs_admin -d acgs_production; then
        print_success "PostgreSQL Replica A is ready"
    else
        print_warning "PostgreSQL Replica A is not ready"
    fi
    
    if docker exec postgres-replica-b pg_isready -U acgs_admin -d acgs_production; then
        print_success "PostgreSQL Replica B is ready"
    else
        print_warning "PostgreSQL Replica B is not ready"
    fi
    
    # Check Redis Cluster
    if docker exec redis-cluster-1 redis-cli -p 7001 ping | grep -q PONG; then
        print_success "Redis Cluster Node 1 is ready"
    else
        print_error "Redis Cluster Node 1 is not ready"
    fi
    
    # Check Load Balancer
    if curl -f http://localhost:8080/stats &> /dev/null; then
        print_success "HAProxy Load Balancer is ready"
    else
        print_error "HAProxy Load Balancer is not ready"
    fi
    
    print_success "Deployment validation complete"
}

# Display deployment information
display_deployment_info() {
    echo ""
    echo "============================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "🎉 ACGS Phase 3A Multi-Zone Infrastructure Deployment Complete!"
    echo "📋 Constitutional Hash: cdd01ef066bc6cf2"
    echo "============================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo ""
    echo "🌐 Service Endpoints:"
    echo "  Load Balancer:     http://localhost:80 (HTTP)"
    echo "                     https://localhost:443 (HTTPS)"
    echo "  HAProxy Stats:     http://localhost:8080/stats"
    echo "  PostgreSQL Primary: localhost:5432"
    echo "  PostgreSQL Replica A: localhost:5433"
    echo "  PostgreSQL Replica B: localhost:5434"
    echo "  Redis Cluster:     localhost:7001, 7002, 7003"
    echo "  Prometheus:        http://localhost:9090"
    echo "  Grafana:           http://localhost:3000"
    echo ""
    echo "🔐 Default Credentials:"
    echo "  Grafana:           admin / acgs_grafana_admin_2025"
    echo "  PostgreSQL:        acgs_admin / acgs_secure_password_2025"
    echo ""
    echo "📊 Next Steps:"
    echo "  1. Verify all services are healthy"
    echo "  2. Run performance tests"
    echo "  3. Configure monitoring alerts"
    echo "  4. Test failover scenarios"
    echo ""
    echo "🔐 Constitutional Hash: cdd01ef066bc6cf2"
}

# Main execution
main() {
    check_prerequisites
    create_env_file
    create_ssl_certificates
    make_scripts_executable
    deploy_infrastructure
    validate_deployment
    display_deployment_info
}

# Run main function
main "$@"
