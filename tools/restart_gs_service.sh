#!/bin/bash
# GS Service Restart Script
# This script restarts the GS Service with updated configuration

echo "🔄 Restarting GS Service with updated configuration..."

# Change to GS Service directory
cd /home/dislove/ACGS-1/services/core/governance-synthesis/gs_service

# Load environment variables
export $(cat config/environments/development.env | xargs)

# Kill existing GS Service process (if running as current user)
pkill -f "uvicorn.*8004" 2>/dev/null || true

# Wait for process to stop
sleep 3

# Start GS Service with new configuration
echo "🚀 Starting GS Service..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload > gs_service.log 2>&1 &

# Wait for service to start
sleep 5

# Test service health
echo "🏥 Testing service health..."
curl -s http://localhost:8004/health | jq .

echo "✅ GS Service restart complete"
