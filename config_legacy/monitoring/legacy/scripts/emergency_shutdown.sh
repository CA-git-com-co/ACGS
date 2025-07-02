#!/bin/bash
# Emergency Shutdown Script for ACGS-PGP
# Provides <30min RTO capability

set -e

echo "ACGS-PGP Emergency Shutdown Initiated"
echo "Timestamp: $(date)"

# Stop all services gracefully
echo "Stopping ACGS services..."
docker-compose -f docker-compose.yml down --timeout 30

# Stop monitoring
echo "Stopping monitoring stack..."
docker-compose -f monitoring/docker-compose.monitoring.yml down

# Create emergency status file
echo "Emergency shutdown completed at $(date)" > emergency_status.txt

echo "Emergency shutdown completed"
echo "RTO: Services can be restored using ./scripts/emergency_restore.sh"
