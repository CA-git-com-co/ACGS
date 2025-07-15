#!/bin/bash
# ACGS Phase 3A PostgreSQL Replica Setup
# Constitutional Hash: cdd01ef066bc6cf2

set -e

echo "🚀 Setting up PostgreSQL Replica..."
echo "📋 Constitutional Hash: cdd01ef066bc6cf2"

# Wait for primary to be ready
echo "⏳ Waiting for primary PostgreSQL to be ready..."
until pg_isready -h "$POSTGRES_PRIMARY_HOST" -p 5432 -U postgres; do
  echo "⏳ Waiting for primary PostgreSQL at $POSTGRES_PRIMARY_HOST..."
  sleep 5
done

# Stop PostgreSQL if running
echo "🛑 Stopping PostgreSQL for replica setup..."
pg_ctl stop -D "$PGDATA" -m fast || true

# Remove existing data directory
echo "🗑️ Cleaning existing data directory..."
rm -rf "$PGDATA"/*

# Create base backup from primary
echo "📥 Creating base backup from primary..."
PGPASSWORD=os.environ.get("PASSWORD") pg_basebackup \
    -h "$POSTGRES_PRIMARY_HOST" \
    -D "$PGDATA" \
    -U replicator \
    -v \
    -P \
    -W \
    -R

# Set up SSL certificates (copy from primary or create)
echo "🔐 Setting up SSL certificates..."
mkdir -p /etc/ssl/certs /etc/ssl/private
openssl req -new -x509 -days 365 -nodes -text \
    -out /etc/ssl/certs/server.crt \
    -keyout /etc/ssl/private/server.key \
    -subj "/CN=acgs-postgres-replica"
cp /etc/ssl/certs/server.crt /etc/ssl/certs/ca.crt
chown postgres:postgres /etc/ssl/certs/server.crt /etc/ssl/private/server.key /etc/ssl/certs/ca.crt
chmod 600 /etc/ssl/private/server.key
chmod 644 /etc/ssl/certs/server.crt /etc/ssl/certs/ca.crt

# Create recovery configuration
echo "⚙️ Creating recovery configuration..."
cat > "$PGDATA/postgresql.auto.conf" <<EOF
# ACGS Replica Configuration
# Constitutional Hash: cdd01ef066bc6cf2

# Primary connection
primary_conninfo = 'host=$POSTGRES_PRIMARY_HOST port=5432 user=replicator password=os.environ.get("PASSWORD")

# Recovery settings
recovery_target_timeline = 'latest'
standby_mode = 'on'
EOF

# Create standby signal file
echo "📡 Creating standby signal..."
touch "$PGDATA/standby.signal"

# Set proper permissions
echo "🔒 Setting permissions..."
chown -R postgres:postgres "$PGDATA"
chmod 700 "$PGDATA"

# Create archive directory
echo "📁 Creating archive directory..."
mkdir -p /var/lib/postgresql/archive
chown postgres:postgres /var/lib/postgresql/archive
chmod 700 /var/lib/postgresql/archive

echo "✅ PostgreSQL Replica setup complete!"
echo "🔐 Constitutional Hash: cdd01ef066bc6cf2"
echo "🚀 Starting replica in standby mode..."
