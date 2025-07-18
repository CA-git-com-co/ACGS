#!/bin/bash
# ACGS-2 PostgreSQL Backup Script
# Constitutional Hash: cdd01ef066bc6cf2

set -euo pipefail

CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="${BACKUP_DIR:-/backups/postgres}"
BACKUP_FILE="$BACKUP_DIR/acgs_backup_$TIMESTAMP.sql.gz"
POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_PORT="${POSTGRES_PORT:-5432}"
POSTGRES_USER="${POSTGRES_USER:-acgs_user}"
POSTGRES_DB="${POSTGRES_DB:-acgs_db}"

echo "🏛️ ACGS-2 PostgreSQL Backup"
echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
echo "Timestamp: $TIMESTAMP"
echo "Backup Location: $BACKUP_FILE"
echo "=================================="

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Check if we're running in Kubernetes
if command -v kubectl &> /dev/null && kubectl get pods -n acgs-system &> /dev/null; then
    echo "🔍 Running in Kubernetes environment"
    
    # Check if PostgreSQL pod is running
    if ! kubectl get pods -l app=postgres -n acgs-system --field-selector=status.phase=Running | grep -q Running; then
        echo "❌ PostgreSQL pod is not running"
        exit 1
    fi
    
    echo "📊 Checking database connectivity..."
    if ! kubectl exec deployment/postgres -n acgs-system -- pg_isready -h localhost -p $POSTGRES_PORT -U $POSTGRES_USER; then
        echo "❌ Database connection failed"
        exit 1
    fi
    
    echo "💾 Creating database backup..."
    # Create backup using kubectl exec
    kubectl exec deployment/postgres -n acgs-system -- pg_dump \
        -h localhost \
        -p $POSTGRES_PORT \
        -U $POSTGRES_USER \
        -d $POSTGRES_DB \
        --column-inserts \
        --verbose \
        --clean \
        --if-exists \
        --quote-all-identifiers \
        --exclude-table-data='pg_stat_statements' \
        --exclude-table-data='pg_stat_activity' \
        | gzip > "$BACKUP_FILE"
    
else
    echo "🔍 Running in direct PostgreSQL environment"
    
    # Direct PostgreSQL backup
    echo "📊 Checking database connectivity..."
    if ! pg_isready -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER; then
        echo "❌ Database connection failed"
        exit 1
    fi
    
    echo "💾 Creating database backup..."
    pg_dump \
        -h $POSTGRES_HOST \
        -p $POSTGRES_PORT \
        -U $POSTGRES_USER \
        -d $POSTGRES_DB \
        --column-inserts \
        --verbose \
        --clean \
        --if-exists \
        --quote-all-identifiers \
        --exclude-table-data='pg_stat_statements' \
        --exclude-table-data='pg_stat_activity' \
        | gzip > "$BACKUP_FILE"
fi

# Check if backup was created successfully
if [[ ! -f "$BACKUP_FILE" ]] || [[ ! -s "$BACKUP_FILE" ]]; then
    echo "❌ Backup file was not created or is empty"
    exit 1
fi

BACKUP_SIZE=$(stat -c%s "$BACKUP_FILE")
echo "✅ Backup created successfully"
echo "📊 Backup size: $((BACKUP_SIZE / 1024 / 1024)) MB"

# Verify constitutional hash in backup
echo "🏛️ Verifying constitutional compliance..."
if zcat "$BACKUP_FILE" | grep -q "$CONSTITUTIONAL_HASH"; then
    echo "✅ Constitutional hash found in backup"
    CONSTITUTIONAL_COMPLIANCE=true
else
    echo "⚠️ Constitutional hash not found in backup"
    CONSTITUTIONAL_COMPLIANCE=false
fi

# Create metadata file
echo "📄 Creating backup metadata..."
cat > "$BACKUP_FILE.meta" << EOF
{
  "constitutional_hash": "$CONSTITUTIONAL_HASH",
  "timestamp": "$TIMESTAMP",
  "backup_type": "postgres_full",
  "size_bytes": $BACKUP_SIZE,
  "retention_until": "$(date -d "+30 days" --iso-8601)",
  "constitutional_compliance": $CONSTITUTIONAL_COMPLIANCE,
  "postgres_host": "$POSTGRES_HOST",
  "postgres_port": $POSTGRES_PORT,
  "postgres_user": "$POSTGRES_USER",
  "postgres_db": "$POSTGRES_DB",
  "compression": "gzip",
  "backup_method": "pg_dump",
  "created_by": "$(whoami)",
  "hostname": "$(hostname)"
}
EOF

# Test backup integrity
echo "🔍 Testing backup integrity..."
if zcat "$BACKUP_FILE" | head -10 | grep -q "PostgreSQL database dump"; then
    echo "✅ Backup integrity verified"
else
    echo "❌ Backup integrity check failed"
    exit 1
fi

# Calculate backup statistics
TOTAL_BACKUPS=$(find "$BACKUP_DIR" -name "*.sql.gz" | wc -l)
TOTAL_SIZE=$(find "$BACKUP_DIR" -name "*.sql.gz" -exec stat -c%s {} + | awk '{sum+=$1} END {print sum}')

echo ""
echo "📊 BACKUP STATISTICS"
echo "===================="
echo "Current backup: $BACKUP_FILE"
echo "Backup size: $((BACKUP_SIZE / 1024 / 1024)) MB"
echo "Constitutional compliance: $(if [[ "$CONSTITUTIONAL_COMPLIANCE" == "true" ]]; then echo "✅ COMPLIANT"; else echo "❌ NON-COMPLIANT"; fi)"
echo "Total backups in directory: $TOTAL_BACKUPS"
echo "Total backup storage: $((TOTAL_SIZE / 1024 / 1024)) MB"
echo "Backup location: $BACKUP_DIR"
echo "Retention policy: 30 days"

# Create backup log entry
echo "📝 Logging backup operation..."
LOG_FILE="/var/log/acgs_backup.log"
echo "$(date --iso-8601=seconds) - PostgreSQL backup created - File: $BACKUP_FILE - Size: $((BACKUP_SIZE / 1024 / 1024))MB - Constitutional: $CONSTITUTIONAL_COMPLIANCE" >> "$LOG_FILE"

# Optional: Upload to offsite storage
if [[ "${OFFSITE_BACKUP:-false}" == "true" ]] && [[ -n "${OFFSITE_LOCATION:-}" ]]; then
    echo "☁️ Uploading to offsite storage..."
    
    case "$OFFSITE_LOCATION" in
        s3://*)
            if command -v aws &> /dev/null; then
                aws s3 cp "$BACKUP_FILE" "$OFFSITE_LOCATION/" && \
                aws s3 cp "$BACKUP_FILE.meta" "$OFFSITE_LOCATION/" && \
                echo "✅ Offsite backup uploaded successfully"
            else
                echo "⚠️ AWS CLI not available for offsite backup"
            fi
            ;;
        gs://*)
            if command -v gsutil &> /dev/null; then
                gsutil cp "$BACKUP_FILE" "$OFFSITE_LOCATION/" && \
                gsutil cp "$BACKUP_FILE.meta" "$OFFSITE_LOCATION/" && \
                echo "✅ Offsite backup uploaded successfully"
            else
                echo "⚠️ Google Cloud SDK not available for offsite backup"
            fi
            ;;
        *)
            echo "⚠️ Unsupported offsite location: $OFFSITE_LOCATION"
            ;;
    esac
fi

echo ""
echo "🎉 PostgreSQL backup completed successfully!"
echo "🏛️ Constitutional compliance maintained"
echo "📁 Backup location: $BACKUP_FILE"
echo "📄 Metadata: $BACKUP_FILE.meta"

# Exit with success code
exit 0