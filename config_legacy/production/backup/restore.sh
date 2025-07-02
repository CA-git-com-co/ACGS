#!/bin/bash
# ACGS-1 Automated Restore Script
# Constitution Hash: cdd01ef066bc6cf2

set -e

if [ $# -ne 1 ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

BACKUP_FILE="$1"
RESTORE_DIR="/tmp/acgs_restore_$(date +%s)"

echo "Starting ACGS-1 restore from: ${BACKUP_FILE}"

# Extract backup
mkdir -p "${RESTORE_DIR}"
tar -xzf "${BACKUP_FILE}" -C "${RESTORE_DIR}"

BACKUP_NAME=$(basename "${BACKUP_FILE}" .tar.gz)
BACKUP_PATH="${RESTORE_DIR}/${BACKUP_NAME}"

# Verify backup manifest
if [ ! -f "${BACKUP_PATH}/manifest.json" ]; then
    echo "Error: Invalid backup file - missing manifest"
    exit 1
fi

# Stop services
echo "Stopping ACGS services..."
systemctl stop acgs-auth acgs-ac acgs-integrity acgs-fv acgs-gs acgs-pgc acgs-ec

# Restore PostgreSQL database
echo "Restoring PostgreSQL database..."
dropdb --if-exists acgs
createdb acgs
gunzip -c "${BACKUP_PATH}/database.sql.gz" | psql acgs

# Restore Redis data
echo "Restoring Redis data..."
systemctl stop redis
cp "${BACKUP_PATH}/redis_dump.rdb" /var/lib/redis/dump.rdb
chown redis:redis /var/lib/redis/dump.rdb
systemctl start redis

# Restore configuration files
echo "Restoring configuration files..."
tar -xzf "${BACKUP_PATH}/config.tar.gz" -C /

# Restore blockchain state
echo "Restoring blockchain state..."
tar -xzf "${BACKUP_PATH}/blockchain.tar.gz" -C /

# Start services
echo "Starting ACGS services..."
systemctl start acgs-auth acgs-ac acgs-integrity acgs-fv acgs-gs acgs-pgc acgs-ec

# Verify restoration
echo "Verifying restoration..."
sleep 10
curl -f http://localhost:8000/health || { echo "Restore verification failed"; exit 1; }

# Cleanup
rm -rf "${RESTORE_DIR}"

echo "Restore completed successfully"
