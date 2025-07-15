#!/bin/bash
# Production Backup Script for 5-Tier Hybrid Inference Router
# Constitutional Hash: cdd01ef066bc6cf2

set -e

CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
BACKUP_DIR="./backups/$(date +%Y%m%d_%H%M%S)"

echo "💾 Starting Production Backup"
echo "🔒 Constitutional Hash: $CONSTITUTIONAL_HASH"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup database
echo "📊 Backing up database..."
docker exec acgs-postgres-production pg_dump -U acgs_user acgs_production > "$BACKUP_DIR/database.sql"

# Backup Redis data
echo "🔄 Backing up Redis data..."
docker exec acgs-redis-production redis-cli --rdb - > "$BACKUP_DIR/redis.rdb"

# Backup configuration files
echo "⚙️ Backing up configuration files..."
cp config/docker/config/docker/config/docker/docker-compose.production.yml "$BACKUP_DIR/"
cp config/environments/developmentconfig/environments/productionconfig/environments/developmentconfig/environments/development.env.backup "$BACKUP_DIR/"
cp nginx.production.conf "$BACKUP_DIR/"

# Backup volumes
echo "💽 Backing up Docker volumes..."
docker run --rm -v acgs_prometheus_data:/data -v "$PWD/$BACKUP_DIR":/backup alpine tar czf /backup/prometheus_data.tar.gz -C /data .
docker run --rm -v acgs_grafana_data:/data -v "$PWD/$BACKUP_DIR":/backup alpine tar czf /backup/grafana_data.tar.gz -C /data .

# Create backup manifest
cat > "$BACKUP_DIR/manifest.json" << EOF
{
  "constitutional_hash": "$CONSTITUTIONAL_HASH",
  "backup_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "environment": "production",
  "files": [
    "database.sql",
    "redis.rdb",
    "config/docker/config/docker/config/docker/docker-compose.production.yml",
    "config/environments/developmentconfig/environments/productionconfig/environments/developmentconfig/environments/development.env.backup",
    "nginx.production.conf",
    "prometheus_data.tar.gz",
    "grafana_data.tar.gz"
  ]
}
EOF

echo "✅ Backup completed: $BACKUP_DIR"
