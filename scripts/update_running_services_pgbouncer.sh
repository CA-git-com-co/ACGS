#!/bin/bash
# ACGS-1 Running Services PgBouncer Configuration Update
# Phase 2 - Enterprise Scalability & Performance
# Updates running services to use PgBouncer connection pooling

set -e

echo "🔧 Updating running ACGS services to use PgBouncer..."

# Colors for output
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

# PgBouncer configuration
PGBOUNCER_HOST="localhost"
PGBOUNCER_PORT="6432"
DB_USER="acgs_user"
DB_PASSWORD="acgs_password"
DB_NAME="acgs_db"

# New database URL through PgBouncer
NEW_DATABASE_URL="postgresql://${DB_USER}:${DB_PASSWORD}@${PGBOUNCER_HOST}:${PGBOUNCER_PORT}/${DB_NAME}"
NEW_ASYNC_DATABASE_URL="postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@${PGBOUNCER_HOST}:${PGBOUNCER_PORT}/${DB_NAME}"

print_status "New database URL: $NEW_DATABASE_URL"

# Function to check if service is running
check_service() {
    local port=$1
    local service_name=$2
    
    if curl -s "http://localhost:${port}/health" > /dev/null 2>&1; then
        print_success "${service_name} (port ${port}) is running"
        return 0
    else
        print_warning "${service_name} (port ${port}) is not responding"
        return 1
    fi
}

# Function to update service environment file
update_service_env() {
    local service_path=$1
    local service_name=$2
    
    if [ -d "$service_path" ]; then
        print_status "Updating $service_name environment configuration..."
        
        # Update .env file if it exists
        if [ -f "$service_path/.env" ]; then
            # Backup original
            cp "$service_path/.env" "$service_path/.env.backup.$(date +%Y%m%d_%H%M%S)"
            
            # Update DATABASE_URL
            sed -i "s|DATABASE_URL=.*|DATABASE_URL=$NEW_DATABASE_URL|g" "$service_path/.env"
            print_success "Updated $service_name .env file"
        fi
        
        # Update .env.example if it exists
        if [ -f "$service_path/.env.example" ]; then
            sed -i "s|DATABASE_URL=.*|DATABASE_URL=$NEW_DATABASE_URL|g" "$service_path/.env.example"
            print_success "Updated $service_name .env.example file"
        fi
        
        return 0
    else
        print_warning "Service directory not found: $service_path"
        return 1
    fi
}

# Function to create service-specific environment override
create_env_override() {
    local service_name=$1
    local port=$2
    
    # Create environment override file
    cat > "/tmp/${service_name}_pgbouncer.env" << EOF
# PgBouncer Configuration Override for $service_name
# Generated on $(date)

# Database connection through PgBouncer
DATABASE_URL=$NEW_DATABASE_URL
DB_HOST=$PGBOUNCER_HOST
DB_PORT=$PGBOUNCER_PORT
DB_USER=$DB_USER
DB_PASSWORD=$DB_PASSWORD
DB_NAME=$DB_NAME

# Connection pool settings optimized for $service_name
DATABASE_POOL_SIZE=30
DATABASE_MAX_OVERFLOW=20
DATABASE_POOL_TIMEOUT=20
DATABASE_POOL_RECYCLE=1800
DATABASE_POOL_PRE_PING=true

# Service-specific settings
SERVICE_PORT=$port
PGBOUNCER_ENABLED=true
CONNECTION_POOLING_ENABLED=true

# Performance optimization
ASYNC_DATABASE_URL=$NEW_ASYNC_DATABASE_URL
EOF

    print_success "Created environment override for $service_name: /tmp/${service_name}_pgbouncer.env"
}

# Check running services and update configurations
print_status "Checking running services..."

# Service definitions with their actual paths
declare -A SERVICES=(
    ["auth_service"]="services/platform/authentication/auth_service:8000"
    ["ac_service"]="services/core/constitutional-ai/ac_service:8001"
    ["integrity_service"]="services/platform/integrity/integrity_service:8002"
    ["fv_service"]="services/core/formal-verification/fv_service:8003"
    ["gs_service"]="services/core/governance-synthesis/gs_service:8004"
    ["pgc_service"]="services/core/policy-governance/pgc_service:8005"
    ["ec_service"]="services/core/evolutionary-computation:8006"
)

# Update configurations for each service
for service_info in "${SERVICES[@]}"; do
    IFS=':' read -r service_path service_port <<< "$service_info"
    service_name=$(basename "$service_path")
    
    print_status "Processing $service_name..."
    
    # Check if service is running
    if check_service "$service_port" "$service_name"; then
        # Update service configuration
        update_service_env "$service_path" "$service_name"
        
        # Create environment override
        create_env_override "$service_name" "$service_port"
        
        print_success "$service_name configuration updated"
    else
        print_warning "Skipping $service_name (not running)"
    fi
    
    echo ""
done

# Test PgBouncer connection
print_status "Testing PgBouncer connection..."
if PGPASSWORD="$DB_PASSWORD" psql -h "$PGBOUNCER_HOST" -p "$PGBOUNCER_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
    print_success "PgBouncer connection test successful"
else
    print_error "PgBouncer connection test failed"
    print_status "Please check PgBouncer configuration and ensure it's running"
fi

# Create restart script for services
print_status "Creating service restart script..."
cat > "scripts/restart_services_with_pgbouncer.sh" << 'EOF'
#!/bin/bash
# Restart ACGS services with PgBouncer configuration

echo "🔄 Restarting ACGS services with PgBouncer configuration..."

# Export PgBouncer environment variables
export DATABASE_URL="postgresql://acgs_user:acgs_password@localhost:6432/acgs_db"
export DB_HOST="localhost"
export DB_PORT="6432"
export PGBOUNCER_ENABLED="true"

# Function to restart service if running
restart_service() {
    local port=$1
    local service_name=$2
    
    echo "Checking $service_name on port $port..."
    
    # Find process using the port
    local pid=$(lsof -ti:$port 2>/dev/null)
    
    if [ -n "$pid" ]; then
        echo "Stopping $service_name (PID: $pid)..."
        kill -TERM "$pid"
        sleep 5
        
        # Force kill if still running
        if kill -0 "$pid" 2>/dev/null; then
            echo "Force stopping $service_name..."
            kill -KILL "$pid"
        fi
        
        echo "$service_name stopped"
    else
        echo "$service_name is not running"
    fi
}

# Restart services
restart_service 8000 "auth_service"
restart_service 8001 "ac_service"
restart_service 8002 "integrity_service"
restart_service 8003 "fv_service"
restart_service 8004 "gs_service"
restart_service 8005 "pgc_service"
restart_service 8006 "ec_service"

echo "✅ Service restart script completed"
echo "Services will need to be manually restarted with new PgBouncer configuration"
EOF

chmod +x "scripts/restart_services_with_pgbouncer.sh"
print_success "Created restart script: scripts/restart_services_with_pgbouncer.sh"

print_success "PgBouncer configuration update completed!"
print_status "Next steps:"
echo "1. Review the environment override files in /tmp/"
echo "2. Restart services using: ./scripts/restart_services_with_pgbouncer.sh"
echo "3. Verify services are using PgBouncer by checking connection counts"
echo "4. Monitor performance and connection pooling metrics"
echo "5. Implement retry mechanisms and circuit breakers"

# Display summary
print_status "Configuration Summary:"
echo "- PgBouncer Host: $PGBOUNCER_HOST"
echo "- PgBouncer Port: $PGBOUNCER_PORT"
echo "- Database URL: $NEW_DATABASE_URL"
echo "- Environment overrides created in /tmp/"
echo "- Backup files created with timestamp suffix"
