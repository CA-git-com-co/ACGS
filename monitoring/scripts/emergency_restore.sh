#!/bin/bash
# Emergency Restore Script for ACGS-PGP
# Restores services after emergency shutdown

set -e

echo "ACGS-PGP Emergency Restore Initiated"
echo "Timestamp: $(date)"

# Start monitoring first
echo "Starting monitoring stack..."
cd monitoring
docker-compose -f docker-compose.monitoring.yml up -d
cd ..

# Start ACGS services
echo "Starting ACGS services..."
docker-compose -f docker-compose.yml up -d

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Validate service health
echo "Validating service health..."
python scripts/production_deployment_validation.py

echo "Emergency restore completed"
