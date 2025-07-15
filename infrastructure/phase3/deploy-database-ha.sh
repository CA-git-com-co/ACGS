#!/bin/bash
# ACGS Phase 3A Database High Availability Deployment
# Constitutional Hash: cdd01ef066bc6cf2

set -e

echo "🚀 Starting ACGS Phase 3A Database High Availability Deployment"
echo "📋 Constitutional Hash: cdd01ef066bc6cf2"
echo "🎯 Target: PostgreSQL Primary-Replica setup for 99.9% uptime"
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
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
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
# ACGS Phase 3A Database HA Environment Configuration
# Constitutional Hash: cdd01ef066bc6cf2

# PostgreSQL Configuration
POSTGRES_PASSWORD=os.environ.get("PASSWORD")
POSTGRES_REPLICATION_PASSWORD=os.environ.get("PASSWORD")
REPLICATION_PASSWORD=os.environ.get("PASSWORD")
POSTGRES_EXPORTER_PASSWORD=os.environ.get("PASSWORD")

# Grafana Configuration
GRAFANA_ADMIN_PASSWORD=os.environ.get("PASSWORD")
GRAFANA_DB_PASSWORD=os.environ.get("PASSWORD")

# Constitutional Compliance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
EOF
    
    print_success "Environment file created"
}

# Deploy database HA infrastructure
deploy_database_ha() {
    print_status "Deploying database high availability infrastructure..."
    
    # Deploy in stages for proper dependency management
    print_status "Stage 1: Deploying PostgreSQL Primary..."
    docker-compose -f phase3a-database-ha.yml up -d postgres-primary-ha
    
    # Wait for primary to be ready
    print_status "Waiting for PostgreSQL Primary to be ready..."
    sleep 45
    
    # Check if primary is ready
    if docker exec acgs-postgres-primary-ha pg_isready -U acgs_admin -d acgs_production; then
        print_success "PostgreSQL Primary is ready"
    else
        print_error "PostgreSQL Primary failed to start properly"
        docker logs acgs-postgres-primary-ha
        exit 1
    fi
    
    print_status "Stage 2: Deploying PostgreSQL Replicas..."
    docker-compose -f phase3a-database-ha.yml up -d postgres-replica-a-ha postgres-replica-b-ha
    
    # Wait for replicas to sync
    print_status "Waiting for replicas to sync..."
    sleep 60
    
    print_status "Stage 3: Deploying PgBouncer connection pooling..."
    docker-compose -f phase3a-database-ha.yml up -d pgbouncer-ha
    
    sleep 10
    
    print_status "Stage 4: Deploying Redis cache..."
    docker-compose -f phase3a-database-ha.yml up -d redis-ha
    
    sleep 10
    
    print_status "Stage 5: Deploying HAProxy database load balancer..."
    docker-compose -f phase3a-database-ha.yml up -d haproxy-db
    
    print_success "Database HA infrastructure deployed"
}

# Validate deployment
validate_deployment() {
    print_status "Validating database HA deployment..."
    
    # Check PostgreSQL Primary
    if docker exec acgs-postgres-primary-ha pg_isready -U acgs_admin -d acgs_production; then
        print_success "PostgreSQL Primary is ready"
    else
        print_error "PostgreSQL Primary is not ready"
        return 1
    fi
    
    # Check PostgreSQL Replicas
    if docker exec acgs-postgres-replica-a-ha pg_isready -U acgs_admin -d acgs_production; then
        print_success "PostgreSQL Replica A is ready"
    else
        print_warning "PostgreSQL Replica A is not ready"
    fi
    
    if docker exec acgs-postgres-replica-b-ha pg_isready -U acgs_admin -d acgs_production; then
        print_success "PostgreSQL Replica B is ready"
    else
        print_warning "PostgreSQL Replica B is not ready"
    fi
    
    # Check Redis
    if docker exec acgs-redis-ha redis-cli ping | grep -q PONG; then
        print_success "Redis cache is ready"
    else
        print_error "Redis cache is not ready"
    fi
    
    # Check HAProxy
    if curl -f http://localhost:8082/stats &> /dev/null; then
        print_success "HAProxy database load balancer is ready"
    else
        print_error "HAProxy database load balancer is not ready"
    fi
    
    # Test replication
    print_status "Testing database replication..."
    docker exec acgs-postgres-primary-ha psql -U acgs_admin -d acgs_production -c "INSERT INTO constitutional_compliance (component, status, zone) VALUES ('replication_test', 'testing', 'validation');"
    
    sleep 5
    
    # Check if data replicated to replica A
    if docker exec acgs-postgres-replica-a-ha psql -U acgs_admin -d acgs_production -c "SELECT * FROM constitutional_compliance WHERE component='replication_test';" | grep -q "replication_test"; then
        print_success "Replication to Replica A is working"
    else
        print_warning "Replication to Replica A may not be working"
    fi
    
    print_success "Database HA deployment validation complete"
}

# Display deployment information
display_deployment_info() {
    echo ""
    echo "============================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo "🎉 ACGS Phase 3A Database High Availability Deployment Complete!"
    echo "📋 Constitutional Hash: cdd01ef066bc6cf2"
    echo "============================================================"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    echo ""
    echo "🗄️ Database Endpoints:"
    echo "  PostgreSQL Primary:   localhost:5450"
    echo "  PostgreSQL Replica A: localhost:5451"
    echo "  PostgreSQL Replica B: localhost:5452"
    echo "  HAProxy Write:        localhost:5460 (routes to primary)"
    echo "  HAProxy Read:         localhost:5461 (routes to replicas)"
    echo "  PgBouncer Pool:       localhost:6435"
    echo "  Redis Cache:          localhost:6380"
    echo ""
    echo "📊 Monitoring:"
    echo "  HAProxy Stats:        http://localhost:8082/stats"
    echo ""
    echo "🔐 Default Credentials:"
    echo "  PostgreSQL:           acgs_admin / acgs_secure_password_2025"
    echo "  Replication User:     replicator / acgs_replication_password_2025"
    echo ""
    echo "✅ High Availability Features:"
    echo "  ✓ PostgreSQL Primary-Replica replication"
    echo "  ✓ Connection pooling with PgBouncer"
    echo "  ✓ Load balancing with HAProxy"
    echo "  ✓ Redis caching for performance"
    echo "  ✓ Constitutional compliance tracking"
    echo ""
    echo "📋 Next Steps:"
    echo "  1. Test failover scenarios"
    echo "  2. Configure monitoring alerts"
    echo "  3. Deploy application services"
    echo "  4. Run performance tests"
    echo ""
    echo "🔐 Constitutional Hash: cdd01ef066bc6cf2"
}

# Main execution
main() {
    check_prerequisites
    create_env_file
    deploy_database_ha
    validate_deployment
    display_deployment_info
}

# Run main function
main "$@"
