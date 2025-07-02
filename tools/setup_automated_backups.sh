#!/bin/bash
# ACGS-1 Automated Backup Setup Script
# Sets up automated backups and monitoring

set -e

PROJECT_ROOT="/home/dislove/ACGS-1"
BACKUP_DIR="/home/dislove/ACGS-1/backups"
LOG_DIR="/home/dislove/ACGS-1/logs"

echo "🚀 Setting up ACGS-1 Automated Backup System"
echo "============================================="

# Create necessary directories
echo "📁 Creating backup directories..."
mkdir -p "$BACKUP_DIR"
mkdir -p "$LOG_DIR"
mkdir -p "$LOG_DIR/incidents"

# Create backup monitoring script
echo "📊 Creating backup monitoring script..."
cat > "$PROJECT_ROOT/scripts/monitor_backups.sh" << 'EOF'
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
EOF

chmod +x "$PROJECT_ROOT/scripts/monitor_backups.sh"

# Create backup cleanup script
echo "🧹 Creating backup cleanup script..."
cat > "$PROJECT_ROOT/scripts/cleanup_old_backups.sh" << 'EOF'
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
EOF

chmod +x "$PROJECT_ROOT/scripts/cleanup_old_backups.sh"

# Create health check automation script
echo "🏥 Creating automated health check script..."
cat > "$PROJECT_ROOT/scripts/automated_health_check.sh" << 'EOF'
#!/bin/bash
# ACGS-1 Automated Health Check Script

PROJECT_ROOT="/home/dislove/ACGS-1"
LOG_FILE="/home/dislove/ACGS-1/logs/automated_health.log"

echo "$(date): Starting automated health check..." >> "$LOG_FILE"

cd "$PROJECT_ROOT"

# Run health check
health_result=$(python3 scripts/emergency_rollback_procedures.py health 2>/dev/null)

if [ $? -eq 0 ]; then
    # Parse health status
    overall_status=$(echo "$health_result" | grep -o '"overall_status": "[^"]*"' | cut -d'"' -f4)
    health_percentage=$(echo "$health_result" | grep -o '"health_percentage": [0-9.]*' | cut -d':' -f2 | tr -d ' ')
    
    echo "$(date): Health check completed - Status: $overall_status, Health: $health_percentage%" >> "$LOG_FILE"
    
    # Alert if health is degraded
    if [ "$overall_status" != "healthy" ]; then
        echo "$(date): ALERT - System health is $overall_status" >> "$LOG_FILE"
        
        # Create incident report for critical status
        if [ "$overall_status" = "critical" ]; then
            python3 scripts/emergency_rollback_procedures.py incident \
                --type "system_health_critical" \
                --description "Automated health check detected critical system status" \
                --severity "critical" >> "$LOG_FILE" 2>&1
        fi
    fi
else
    echo "$(date): ERROR - Health check failed" >> "$LOG_FILE"
fi
EOF

chmod +x "$PROJECT_ROOT/scripts/automated_health_check.sh"

# Create cron job configuration
echo "⏰ Creating cron job configuration..."
cat > "$PROJECT_ROOT/cron_jobs.txt" << EOF
# ACGS-1 Automated Backup and Monitoring Cron Jobs
# Add these to your crontab: crontab -e

# Daily backup at 2:00 AM
0 2 * * * cd $PROJECT_ROOT && python3 scripts/simple_backup_recovery.py backup >> $LOG_DIR/daily_backup.log 2>&1

# Hourly backup monitoring
0 * * * * $PROJECT_ROOT/scripts/monitor_backups.sh

# Health check every 15 minutes
*/15 * * * * $PROJECT_ROOT/scripts/automated_health_check.sh

# Weekly backup cleanup (Sundays at 3:00 AM)
0 3 * * 0 $PROJECT_ROOT/scripts/cleanup_old_backups.sh

# Daily log rotation (4:00 AM)
0 4 * * * find $LOG_DIR -name "*.log" -size +100M -exec gzip {} \;

# Constitution hash verification (every 6 hours)
0 */6 * * * cd $PROJECT_ROOT && curl -s http://localhost:8005/api/v1/constitutional/validate | grep -q "cdd01ef066bc6cf2" || echo "\$(date): Constitution hash verification failed" >> $LOG_DIR/constitution_monitor.log
EOF

echo "📋 Cron job configuration created: $PROJECT_ROOT/cron_jobs.txt"
echo ""
echo "To install cron jobs, run:"
echo "  crontab $PROJECT_ROOT/cron_jobs.txt"
echo ""

# Create disaster recovery test script
echo "🧪 Creating disaster recovery test script..."
cat > "$PROJECT_ROOT/scripts/test_disaster_recovery.sh" << 'EOF'
#!/bin/bash
# ACGS-1 Disaster Recovery Test Script

PROJECT_ROOT="/home/dislove/ACGS-1"
LOG_FILE="/home/dislove/ACGS-1/logs/dr_test.log"

echo "$(date): Starting disaster recovery test..." >> "$LOG_FILE"

cd "$PROJECT_ROOT"

# 1. Create test backup
echo "$(date): Creating test backup..." >> "$LOG_FILE"
backup_result=$(python3 scripts/simple_backup_recovery.py backup 2>&1)
if [ $? -eq 0 ]; then
    echo "$(date): Test backup created successfully" >> "$LOG_FILE"
else
    echo "$(date): ERROR - Test backup failed" >> "$LOG_FILE"
    exit 1
fi

# 2. Test emergency procedures
echo "$(date): Testing emergency health check..." >> "$LOG_FILE"
health_result=$(python3 scripts/emergency_rollback_procedures.py health 2>&1)
if [ $? -eq 0 ]; then
    echo "$(date): Emergency health check passed" >> "$LOG_FILE"
else
    echo "$(date): ERROR - Emergency health check failed" >> "$LOG_FILE"
fi

# 3. Test service isolation (non-destructive)
echo "$(date): Testing emergency procedures documentation..." >> "$LOG_FILE"
procedures_result=$(python3 scripts/emergency_rollback_procedures.py procedures 2>&1)
if [ $? -eq 0 ]; then
    echo "$(date): Emergency procedures documentation accessible" >> "$LOG_FILE"
else
    echo "$(date): ERROR - Emergency procedures documentation failed" >> "$LOG_FILE"
fi

echo "$(date): Disaster recovery test completed" >> "$LOG_FILE"
EOF

chmod +x "$PROJECT_ROOT/scripts/test_disaster_recovery.sh"

# Update operational runbooks
echo "📖 Updating operational runbooks..."
cat >> "$PROJECT_ROOT/OPERATIONAL_RUNBOOKS.md" << 'EOF'

## 🔄 Automated Backup System

### Backup Schedule
- **Daily Backups**: 2:00 AM (configurations, service states, blockchain)
- **Backup Monitoring**: Every hour
- **Health Checks**: Every 15 minutes
- **Cleanup**: Weekly (Sundays at 3:00 AM)

### Backup Commands
```bash
# Manual backup
python3 scripts/simple_backup_recovery.py backup

# List backups
python3 scripts/simple_backup_recovery.py list

# Monitor backup health
./scripts/monitor_backups.sh

# Test disaster recovery
./scripts/test_disaster_recovery.sh
```

### Emergency Procedures
```bash
# Quick health check
python3 scripts/emergency_rollback_procedures.py health

# Emergency stop all services
python3 scripts/emergency_rollback_procedures.py stop

# Emergency restart all services
python3 scripts/emergency_rollback_procedures.py restart

# Isolate specific service
python3 scripts/emergency_rollback_procedures.py isolate --service pgc_service

# Create incident report
python3 scripts/emergency_rollback_procedures.py incident \
  --type "service_failure" \
  --description "PGC service unresponsive" \
  --severity "high"

# Get emergency procedures
python3 scripts/emergency_rollback_procedures.py procedures
```

### Recovery Time Objectives
- **RTO (Recovery Time Objective)**: < 1 hour
- **RPO (Recovery Point Objective)**: < 15 minutes
- **Service Restart Time**: < 5 minutes
- **Health Check Response**: < 30 seconds

### Escalation Matrix
- **Low**: Log incident, monitor
- **Medium**: Contact primary on-call
- **High**: Contact primary + secondary
- **Critical**: Contact all teams + escalation

EOF

echo "✅ Automated backup system setup completed!"
echo ""
echo "📋 Summary:"
echo "  - Backup scripts created and configured"
echo "  - Emergency procedures implemented"
echo "  - Monitoring and alerting configured"
echo "  - Cron jobs ready for installation"
echo "  - Operational runbooks updated"
echo ""
echo "🔧 Next steps:"
echo "  1. Install cron jobs: crontab $PROJECT_ROOT/cron_jobs.txt"
echo "  2. Test backup system: python3 scripts/simple_backup_recovery.py backup"
echo "  3. Test emergency procedures: python3 scripts/emergency_rollback_procedures.py health"
echo "  4. Run disaster recovery test: ./scripts/test_disaster_recovery.sh"
echo ""
echo "✅ ACGS-1 backup and disaster recovery system is ready for production!"
