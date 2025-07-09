#!/bin/bash
# ACGS-1 Backup Monitoring Script

PROJECT_ROOT="/home/dislove/ACGS-1"
BACKUP_DIR="/home/dislove/ACGS-1/backups"
LOG_FILE="/home/dislove/ACGS-1/logs/backup_monitor.log"

echo "$(date): Starting backup monitoring..." >> "$LOG_FILE"

# Check if backup directory exists and has recent backups
if [ ! -d "$BACKUP_DIR" ]; then
    echo "$(date): ERROR - Backup directory not found" >> "$LOG_FILE"
    exit 1
fi

# Check for backups in last 24 hours
recent_backups=$(find "$BACKUP_DIR" -name "acgs_simple_backup_*" -mtime -1 | wc -l)

if [ "$recent_backups" -eq 0 ]; then
    echo "$(date): WARNING - No recent backups found" >> "$LOG_FILE"
    # Create emergency backup
    cd "$PROJECT_ROOT"
    python3 scripts/simple_backup_recovery.py backup >> "$LOG_FILE" 2>&1
else
    echo "$(date): OK - Found $recent_backups recent backup(s)" >> "$LOG_FILE"
fi

# Check backup sizes and integrity
for backup_dir in "$BACKUP_DIR"/acgs_simple_backup_*; do
    if [ -d "$backup_dir" ]; then
        manifest_file="$backup_dir/backup_manifest.json"
        if [ -f "$manifest_file" ]; then
            status=$(grep -o '"status": "[^"]*"' "$manifest_file" | cut -d'"' -f4)
            if [ "$status" = "completed" ]; then
                echo "$(date): OK - Backup $(basename "$backup_dir") is valid" >> "$LOG_FILE"
            else
                echo "$(date): ERROR - Backup $(basename "$backup_dir") is invalid" >> "$LOG_FILE"
            fi
        fi
    fi
done

echo "$(date): Backup monitoring completed" >> "$LOG_FILE"
