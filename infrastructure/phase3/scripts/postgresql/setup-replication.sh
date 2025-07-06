#!/bin/bash
# ACGS Phase 3A PostgreSQL Primary Replication Setup
# Constitutional Hash: cdd01ef066bc6cf2

set -e

echo "🚀 Setting up PostgreSQL Primary for replication..."
echo "📋 Constitutional Hash: cdd01ef066bc6cf2"

# Wait for PostgreSQL to be ready
until pg_isready -U postgres; do
  echo "⏳ Waiting for PostgreSQL to be ready..."
  sleep 2
done

# Create replication user
echo "👤 Creating replication user..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Create replication user
    CREATE USER replicator WITH REPLICATION ENCRYPTED PASSWORD '$POSTGRES_REPLICATION_PASSWORD';
    
    -- Create Grafana database and user
    CREATE DATABASE grafana;
    CREATE USER grafana WITH ENCRYPTED PASSWORD '$GRAFANA_DB_PASSWORD';
    GRANT ALL PRIVILEGES ON DATABASE grafana TO grafana;
    
    -- Create monitoring user
    CREATE USER postgres_exporter WITH ENCRYPTED PASSWORD '$POSTGRES_EXPORTER_PASSWORD';
    GRANT CONNECT ON DATABASE $POSTGRES_DB TO postgres_exporter;
    GRANT pg_monitor TO postgres_exporter;
    
    -- Create replication slots for replicas
    SELECT pg_create_physical_replication_slot('replica_a_slot');
    SELECT pg_create_physical_replication_slot('replica_b_slot');
    
    -- Constitutional compliance table
    CREATE TABLE IF NOT EXISTS constitutional_compliance (
        id SERIAL PRIMARY KEY,
        hash VARCHAR(16) NOT NULL DEFAULT 'cdd01ef066bc6cf2',
        component VARCHAR(255) NOT NULL,
        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        status VARCHAR(50) NOT NULL DEFAULT 'compliant'
    );
    
    -- Insert initial compliance record
    INSERT INTO constitutional_compliance (component, status) 
    VALUES ('postgresql_primary', 'compliant');
    
    -- Create indexes for performance
    CREATE INDEX IF NOT EXISTS idx_constitutional_hash ON constitutional_compliance(hash);
    CREATE INDEX IF NOT EXISTS idx_constitutional_timestamp ON constitutional_compliance(timestamp);
EOSQL

# Create archive directory
echo "📁 Creating archive directory..."
mkdir -p /var/lib/postgresql/archive
chown postgres:postgres /var/lib/postgresql/archive
chmod 700 /var/lib/postgresql/archive

# Set up SSL certificates (self-signed for development)
echo "🔐 Setting up SSL certificates..."
mkdir -p /etc/ssl/certs /etc/ssl/private
openssl req -new -x509 -days 365 -nodes -text \
    -out /etc/ssl/certs/server.crt \
    -keyout /etc/ssl/private/server.key \
    -subj "/CN=acgs-postgres-primary"
cp /etc/ssl/certs/server.crt /etc/ssl/certs/ca.crt
chown postgres:postgres /etc/ssl/certs/server.crt /etc/ssl/private/server.key /etc/ssl/certs/ca.crt
chmod 600 /etc/ssl/private/server.key
chmod 644 /etc/ssl/certs/server.crt /etc/ssl/certs/ca.crt

echo "✅ PostgreSQL Primary replication setup complete!"
echo "🔐 Constitutional Hash: cdd01ef066bc6cf2"
