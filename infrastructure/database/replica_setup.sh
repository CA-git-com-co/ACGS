# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
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
