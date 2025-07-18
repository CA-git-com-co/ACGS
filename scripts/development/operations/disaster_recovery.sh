# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash
set -e

# ACGS-2 Disaster Recovery Script
# Restores system from backup in case of disaster

BACKUP_DIR="/opt/acgs-backups"
RESTORE_TIMESTAMP=${1:-latest}

echo "🚨 Starting ACGS-2 disaster recovery process..."

if [ "$RESTORE_TIMESTAMP" = "latest" ]; then
    # Find latest backup
    DB_BACKUP=$(ls -t "$BACKUP_DIR/database/"*.sql.gz | head -1)
    APP_BACKUP=$(ls -t "$BACKUP_DIR/application/"*.tar.gz | head -1)
    CONFIG_BACKUP=$(ls -t "$BACKUP_DIR/config/"*.tar.gz | head -1)
else
    # Use specific timestamp
    DB_BACKUP="$BACKUP_DIR/database/acgs_db_$RESTORE_TIMESTAMP.sql.gz"
    APP_BACKUP="$BACKUP_DIR/application/acgs_app_data_$RESTORE_TIMESTAMP.tar.gz"
    CONFIG_BACKUP="$BACKUP_DIR/config/acgs_config_$RESTORE_TIMESTAMP.tar.gz"
fi

# Verify backup files exist
for backup_file in "$DB_BACKUP" "$APP_BACKUP" "$CONFIG_BACKUP"; do
    if [ ! -f "$backup_file" ]; then
        echo "❌ Backup file not found: $backup_file"
        exit 1
    fi
done

# Stop services
echo "🛑 Stopping ACGS-2 services..."
docker-compose -f config/docker/docker-compose.production.yml down

# Restore database
echo "🗄️ Restoring database..."
dropdb -h localhost -U acgs_user acgs_production --if-exists
createdb -h localhost -U acgs_user acgs_production
gunzip -c "$DB_BACKUP" | psql -h localhost -U acgs_user -d acgs_production

# Restore application data
echo "📁 Restoring application data..."
rm -rf /opt/acgs-2/data/
tar -xzf "$APP_BACKUP" -C /

# Restore configuration
echo "⚙️ Restoring configuration..."
tar -xzf "$CONFIG_BACKUP" -C /

# Start services
echo "🚀 Starting ACGS-2 services..."
docker-compose -f config/docker/docker-compose.production.yml up -d

# Verify system health
echo "🏥 Verifying system health..."
sleep 30
./scripts/health/production_health_check.py

echo "✅ Disaster recovery completed successfully"
