#!/bin/bash
# ACGS-1 Backup Cleanup Script

BACKUP_DIR="/home/dislove/ACGS-1/backups"
LOG_FILE="/home/dislove/ACGS-1/logs/backup_cleanup.log"

echo "$(date): Starting backup cleanup..." >> "$LOG_FILE"

# Keep last 7 daily backups
find "$BACKUP_DIR" -name "acgs_simple_backup_*" -type d -mtime +7 -exec rm -rf {} \; 2>/dev/null || true

# Log cleanup results
remaining_backups=$(find "$BACKUP_DIR" -name "acgs_simple_backup_*" -type d | wc -l)
echo "$(date): Cleanup completed. $remaining_backups backups remaining" >> "$LOG_FILE"
