#!/bin/bash
set -e

# ACGS-2 Automated Backup Script
# Performs comprehensive backup of database, application data, and configuration

BACKUP_DIR="/opt/acgs-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

echo "🔄 Starting ACGS-2 backup process..."

# Create backup directory
mkdir -p "$BACKUP_DIR/database" "$BACKUP_DIR/application" "$BACKUP_DIR/config"

# Database backup
echo "💾 Backing up PostgreSQL database..."
pg_dump -h localhost -U acgs_user -d acgs_production | gzip > "$BACKUP_DIR/database/acgs_db_$TIMESTAMP.sql.gz"

# Application data backup
echo "📁 Backing up application data..."
tar -czf "$BACKUP_DIR/application/acgs_app_data_$TIMESTAMP.tar.gz" /opt/acgs-2/data/

# Configuration backup
echo "⚙️ Backing up configuration..."
tar -czf "$BACKUP_DIR/config/acgs_config_$TIMESTAMP.tar.gz" /opt/acgs-2/config/

# Cleanup old backups
echo "🧹 Cleaning up old backups..."
find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete

# Verify backup integrity
echo "✅ Verifying backup integrity..."
for backup_file in "$BACKUP_DIR"/*/*.gz; do
    if ! gzip -t "$backup_file" 2>/dev/null; then
        echo "❌ Backup verification failed: $backup_file"
        exit 1
    fi
done

# Upload to remote storage (if configured)
if [ -n "$REMOTE_BACKUP_ENDPOINT" ]; then
    echo "☁️ Uploading to remote storage..."
    aws s3 sync "$BACKUP_DIR" "$REMOTE_BACKUP_ENDPOINT/acgs-backups/"
fi

echo "✅ Backup process completed successfully"
