# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash
# ACGS-1 Read Replica Setup Script
# Phase 2 - Enterprise Scalability & Performance
# Sets up PostgreSQL read replicas with PgBouncer routing

set -e

echo "🔧 Setting up PostgreSQL Read Replicas for ACGS-1..."

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

# Configuration
PRIMARY_HOST="localhost"
PRIMARY_PORT="5432"
REPLICA1_PORT="5433"
REPLICA2_PORT="5434"
DB_NAME="acgs_db"
DB_USER="acgs_user"
DB_PASSWORD=os.environ.get("PASSWORD")
REPLICATION_USER="replicator"
REPLICATION_PASSWORD=os.environ.get("PASSWORD")

# Create replication user on primary
print_status "Setting up replication user on primary database..."

# Check if primary database is accessible
if PGPASSWORD=os.environ.get("PASSWORD") psql -h "$PRIMARY_HOST" -p "$PRIMARY_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
    print_success "Primary database is accessible"
    
    # Create replication user if it doesn't exist
    PGPASSWORD=os.environ.get("PASSWORD") psql -h "$PRIMARY_HOST" -p "$PRIMARY_PORT" -U "$DB_USER" -d "$DB_NAME" << EOF
DO \$\$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '$REPLICATION_USER') THEN
        CREATE USER $REPLICATION_USER WITH REPLICATION PASSWORD '$REPLICATION_PASSWORD';
        GRANT CONNECT ON DATABASE $DB_NAME TO $REPLICATION_USER;
    END IF;
END
\$\$;
EOF
    
    print_success "Replication user configured"
else
    print_warning "Primary database not accessible - creating configuration files only"
fi

# Create PgBouncer configuration for read replicas
print_status "Creating PgBouncer configuration for read replicas..."

cat > "infrastructure/database/pgbouncer_replicas.ini" << EOF
# PgBouncer Configuration for Read Replicas
# ACGS-1 Phase 2 - Enterprise Scalability & Performance

[databases]
# Primary database (read/write)
acgs_db_primary = host=$PRIMARY_HOST port=$PRIMARY_PORT dbname=$DB_NAME user=$DB_USER password=os.environ.get("PASSWORD")

# Read replica 1
acgs_db_replica1 = host=$PRIMARY_HOST port=$REPLICA1_PORT dbname=$DB_NAME user=$DB_USER password=os.environ.get("PASSWORD")

# Read replica 2  
acgs_db_replica2 = host=$PRIMARY_HOST port=$REPLICA2_PORT dbname=$DB_NAME user=$DB_USER password=os.environ.get("PASSWORD")

# Load balanced read pool
acgs_db_read = host=$PRIMARY_HOST port=$REPLICA1_PORT dbname=$DB_NAME user=$DB_USER password=os.environ.get("PASSWORD")

[pgbouncer]
# Connection settings for read replicas
listen_addr = 0.0.0.0
listen_port = 6433
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

# Pool configuration optimized for read workloads
pool_mode = transaction
max_client_conn = 500
default_pool_size = 20
min_pool_size = 5
reserve_pool_size = 5
reserve_pool_timeout = 3
max_db_connections = 50
max_user_connections = 50

# Read-optimized timeouts
server_round_robin = 1
server_connect_timeout = 10
server_login_retry = 10
query_timeout = 0
query_wait_timeout = 60
client_idle_timeout = 0
server_idle_timeout = 300
server_lifetime = 1800

# Logging
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1
log_stats = 1
stats_period = 60

# Administrative settings
admin_users = $DB_USER
stats_users = $DB_USER

pidfile = /var/run/pgbouncer/pgbouncer_replicas.pid
logfile = /var/log/pgbouncer/pgbouncer_replicas.log
EOF

print_success "PgBouncer replica configuration created"

# Create Docker Compose configuration for read replicas
print_status "Creating Docker Compose configuration for read replicas..."

cat > "infrastructure/database/docker-compose.replicas.yml" << EOF
# PostgreSQL Read Replicas Configuration
# ACGS-1 Phase 2 - Enterprise Scalability & Performance

version: '3.8'

services:
  # PostgreSQL Read Replica 1
  postgres_replica1:
    image: postgres:15-alpine
    container_name: acgs_postgres_replica1
    environment:
      POSTGRES_USER: $DB_USER
      POSTGRES_PASSWORD: os.environ.get("PASSWORD")
      POSTGRES_DB: $DB_NAME
      PGUSER: $DB_USER
    ports:
      - "$REPLICA1_PORT:5432"
    volumes:
      - postgres_replica1_data:/var/lib/postgresql/data
      - ./replica_setup.sh:/docker-entrypoint-initdb.d/replica_setup.sh
    command: |
      postgres
      -c wal_level=replica
      -c max_wal_senders=3
      -c max_replication_slots=3
      -c hot_standby=on
      -c hot_standby_feedback=on
    networks:
      - acgs_network
    depends_on:
      - postgres_primary
    restart: unless-stopped

  # PostgreSQL Read Replica 2
  postgres_replica2:
    image: postgres:15-alpine
    container_name: acgs_postgres_replica2
    environment:
      POSTGRES_USER: $DB_USER
      POSTGRES_PASSWORD: os.environ.get("PASSWORD")
      POSTGRES_DB: $DB_NAME
      PGUSER: $DB_USER
    ports:
      - "$REPLICA2_PORT:5432"
    volumes:
      - postgres_replica2_data:/var/lib/postgresql/data
      - ./replica_setup.sh:/docker-entrypoint-initdb.d/replica_setup.sh
    command: |
      postgres
      -c wal_level=replica
      -c max_wal_senders=3
      -c max_replication_slots=3
      -c hot_standby=on
      -c hot_standby_feedback=on
    networks:
      - acgs_network
    depends_on:
      - postgres_primary
    restart: unless-stopped

  # PgBouncer for Read Replicas
  pgbouncer_replicas:
    image: pgbouncer/pgbouncer:latest
    container_name: acgs_pgbouncer_replicas
    environment:
      DATABASES_HOST: postgres_replica1
      DATABASES_PORT: 5432
      DATABASES_USER: $DB_USER
      DATABASES_PASSWORD: os.environ.get("PASSWORD")
      DATABASES_DBNAME: $DB_NAME
      POOL_MODE: transaction
      MAX_CLIENT_CONN: 500
      DEFAULT_POOL_SIZE: 20
    ports:
      - "6433:5432"
    volumes:
      - ./pgbouncer_replicas.ini:/etc/pgbouncer/pgbouncer.ini
      - ./userlist.txt:/etc/pgbouncer/userlist.txt
    networks:
      - acgs_network
    depends_on:
      - postgres_replica1
      - postgres_replica2
    restart: unless-stopped

volumes:
  postgres_replica1_data:
    driver: local
  postgres_replica2_data:
    driver: local

networks:
  acgs_network:
    external: true
EOF

print_success "Docker Compose replica configuration created"

# Create replica setup script
print_status "Creating replica setup script..."

cat > "infrastructure/database/replica_setup.sh" << 'EOF'
#!/bin/bash
# PostgreSQL Replica Setup Script

set -e

echo "Setting up PostgreSQL replica..."

# Wait for primary to be ready
until pg_isready -h postgres_primary -p 5432 -U acgs_user; do
  echo "Waiting for primary database..."
  sleep 2
done

# Create replication slot on primary (if not exists)
PGPASSWORD=os.environ.get("PASSWORD") psql -h postgres_primary -p 5432 -U acgs_user -d acgs_db -c "
SELECT pg_create_physical_replication_slot('replica_slot_$(hostname)', true);
" || echo "Replication slot may already exist"

# Configure recovery
cat > /var/lib/postgresql/data/postgresql.auto.conf << EOL
# Replica configuration
hot_standby = on
hot_standby_feedback = on
primary_conninfo = 'host=postgres_primary port=5432 user=replicator password=os.environ.get("PASSWORD")
primary_slot_name = 'replica_slot_$(hostname)'
EOL

# Create standby signal
touch /var/lib/postgresql/data/standby.signal

echo "Replica setup completed"
EOF

chmod +x "infrastructure/database/replica_setup.sh"
print_success "Replica setup script created"

# Create health check script for replicas
print_status "Creating health check script for replicas..."

cat > "scripts/check_replica_health.py" << 'EOF'
#!/usr/bin/env python3
"""
ACGS-1 Read Replica Health Check Script
Monitors health and lag of PostgreSQL read replicas
"""

import asyncio
import asyncpg
import time
import json
from typing import Dict, List

async def check_replica_health():
    """Check health of all read replicas."""
    
    replicas = [
        {"name": "primary", "host": "localhost", "port": 5432},
        {"name": "replica1", "host": "localhost", "port": 5433},
        {"name": "replica2", "host": "localhost", "port": 5434},
    ]
    
    results = []
    
    for replica in replicas:
        try:
            conn = await asyncpg.connect(
                host=replica["host"],
                port=replica["port"],
                database="acgs_db",
                user="acgs_user",
                password=os.environ.get("PASSWORD"),
                timeout=5
            )
            
            # Check basic connectivity
            start_time = time.time()
            result = await conn.fetchval("SELECT 1")
            response_time = time.time() - start_time
            
            # Check replication lag (for replicas)
            lag_info = None
            if replica["name"] != "primary":
                try:
                    lag_query = """
                    SELECT 
                        CASE 
                            WHEN pg_is_in_recovery() THEN 
                                EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))
                            ELSE 0 
                        END as lag_seconds
                    """
                    lag_info = await conn.fetchval(lag_query)
                except:
                    lag_info = None
            
            await conn.close()
            
            results.append({
                "name": replica["name"],
                "host": replica["host"],
                "port": replica["port"],
                "status": "healthy",
                "response_time": response_time,
                "lag_seconds": lag_info,
                "timestamp": time.time()
            })
            
        except Exception as e:
            results.append({
                "name": replica["name"],
                "host": replica["host"],
                "port": replica["port"],
                "status": "unhealthy",
                "error": str(e),
                "timestamp": time.time()
            })
    
    return results

async def main():
    """Main health check function."""
    print("🔍 Checking read replica health...")
    
    results = await check_replica_health()
    
    print("\n📊 Replica Health Status:")
    print("=" * 50)
    
    for result in results:
        status_icon = "✅" if result["status"] == "healthy" else "❌"
        print(f"{status_icon} {result['name']:10} ({result['host']}:{result['port']})")
        
        if result["status"] == "healthy":
            print(f"   Response Time: {result['response_time']:.3f}s")
            if result.get("lag_seconds") is not None:
                print(f"   Replication Lag: {result['lag_seconds']:.2f}s")
        else:
            print(f"   Error: {result.get('error', 'Unknown error')}")
        print()
    
    # Export results to JSON
    with open("logs/replica_health.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("📄 Health check results saved to logs/replica_health.json")

if __name__ == "__main__":
    asyncio.run(main())
EOF

chmod +x "scripts/check_replica_health.py"
print_success "Health check script created"

print_success "Read replica setup completed!"
print_status "Configuration Summary:"
echo "- Primary Database: $PRIMARY_HOST:$PRIMARY_PORT"
echo "- Read Replica 1: $PRIMARY_HOST:$REPLICA1_PORT"
echo "- Read Replica 2: $PRIMARY_HOST:$REPLICA2_PORT"
echo "- PgBouncer Replicas: localhost:6433"
echo "- Configuration files created in infrastructure/database/"
echo "- Health check script: scripts/check_replica_health.py"

print_status "Next steps:"
echo "1. Start read replicas: docker-compose -f infrastructure/database/docker-compose.replicas.yml up -d"
echo "2. Configure PgBouncer for replica routing"
echo "3. Update application connection strings for read operations"
echo "4. Monitor replica health and lag"
echo "5. Implement read/write splitting in application code"
