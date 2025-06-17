#!/bin/bash
# ACGS-1 Automated Backup Script
# Constitution Hash: cdd01ef066bc6cf2

set -e

BACKUP_DIR="/var/backups/acgs"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="acgs_backup_${TIMESTAMP}"

echo "Starting ACGS-1 backup: ${BACKUP_NAME}"

# Create backup directory
mkdir -p "${BACKUP_DIR}/${BACKUP_NAME}"

# Backup PostgreSQL database
echo "Backing up PostgreSQL database..."
pg_dump -h localhost -U postgres acgs | gzip > "${BACKUP_DIR}/${BACKUP_NAME}/database.sql.gz"

# Backup Redis data
echo "Backing up Redis data..."
redis-cli --rdb "${BACKUP_DIR}/${BACKUP_NAME}/redis_dump.rdb"

# Backup configuration files
echo "Backing up configuration files..."
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}/config.tar.gz" config/ services/*/config/

# Backup blockchain state
echo "Backing up blockchain state..."
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}/blockchain.tar.gz" blockchain/

# Create backup manifest
cat > "${BACKUP_DIR}/${BACKUP_NAME}/manifest.json" << EOF
{
  "backup_timestamp": "${TIMESTAMP}",
  "constitution_hash": "cdd01ef066bc6cf2",
  "backup_type": "full",
  "components": [
    "postgresql_database",
    "redis_data",
    "configuration_files",
    "blockchain_state"
  ],
  "retention_days": 30
}
EOF

# Compress entire backup
echo "Compressing backup..."
tar -czf "${BACKUP_DIR}/${BACKUP_NAME}.tar.gz" -C "${BACKUP_DIR}" "${BACKUP_NAME}"
rm -rf "${BACKUP_DIR}/${BACKUP_NAME}"

# Cleanup old backups (keep 30 days)
find "${BACKUP_DIR}" -name "acgs_backup_*.tar.gz" -mtime +30 -delete

echo "Backup completed: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
