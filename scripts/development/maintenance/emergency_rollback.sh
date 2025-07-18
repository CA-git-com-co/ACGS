# Constitutional Hash: cdd01ef066bc6cf2
#!/bin/bash
# ACGS-1 Emergency Rollback Script
# Generated: 2025-06-24T00:09:12.960104
# Backup: /home/ubuntu/ACGS/backups/20250624_000909

set -e

echo "Starting emergency rollback..."

# Stop all services
echo "Stopping services..."
pkill -f "python.*service" || true
sleep 5

# Restore from backup
echo "Restoring from backup: /home/ubuntu/ACGS/backups/20250624_000909"
if [ -d "/home/ubuntu/ACGS/backups/20250624_000909" ]; then
    cp -r /home/ubuntu/ACGS/backups/20250624_000909/* /home/ubuntu/ACGS/
    echo "Rollback completed successfully"
else
    echo "ERROR: Backup directory not found!"
    exit 1
fi

# Restart services
echo "Restarting services..."
cd /home/ubuntu/ACGS
./scripts/start_all_services.sh

echo "Rollback completed. Please verify system functionality."
