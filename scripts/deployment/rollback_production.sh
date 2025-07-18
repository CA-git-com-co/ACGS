#!/bin/bash
# Production Rollback Script for 5-Tier Hybrid Inference Router
# Constitutional Hash: cdd01ef066bc6cf2

set -e

CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
BACKUP_DIR="${1:-$(ls -t backups/ | head -1)}"

if [[ -z "$BACKUP_DIR" ]]; then
    echo "❌ No backup directory specified or found"
    exit 1
fi

echo "🔄 Starting Production Rollback"
echo "🔒 Constitutional Hash: $CONSTITUTIONAL_HASH"
echo "📁 Using backup: $BACKUP_DIR"

# Stop current services
echo "🛑 Stopping current services..."
docker-compose -f config/docker/docker-compose.production.yml down

# Restore configuration files
echo "⚙️ Restoring configuration files..."
cp "backups/$BACKUP_DIR/config/docker/docker-compose.production.yml" .
cp "backups/$BACKUP_DIR/config/environments/developmentconfig/environments/production.env.backup" .
cp "backups/$BACKUP_DIR/config/nginx.production.conf" .

# Restore volumes
echo "💽 Restoring Docker volumes..."
docker run --rm -v acgs_prometheus_data:/data -v "$PWD/backups/$BACKUP_DIR":/backup alpine tar xzf /backup/prometheus_data.tar.gz -C /data
docker run --rm -v acgs_grafana_data:/data -v "$PWD/backups/$BACKUP_DIR":/backup alpine tar xzf /backup/grafana_data.tar.gz -C /data

# Start services
echo "🚀 Starting restored services..."
docker-compose -f config/docker/docker-compose.production.yml --env-file config/environments/developmentconfig/environments/production.env.backup up -d

# Wait for services
echo "⏳ Waiting for services to be ready..."
sleep 30

# Restore database
echo "📊 Restoring database..."
docker exec -i acgs-postgres-production psql -U acgs_user acgs_production < "backups/$BACKUP_DIR/database.sql"

# Restore Redis data
echo "🔄 Restoring Redis data..."
docker exec -i acgs-redis-production redis-cli --pipe < "backups/$BACKUP_DIR/redis.rdb"

# Health check
echo "🔍 Running health check..."
if curl -f -s https://localhost/health > /dev/null; then
    echo "✅ Rollback completed successfully"
else
    echo "❌ Rollback health check failed"
    exit 1
fi
