# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash

# ACGS Auth Service Startup Script
# Sets proper environment and starts the auth service

set -e

PROJECT_ROOT="/home/ubuntu/ACGS"
SERVICE_DIR="$PROJECT_ROOT/services/platform/authentication/auth_service"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
LOG_FILE="$PROJECT_ROOT/logs/auth_service.log"

echo "Starting ACGS Auth Service..."
echo "Project Root: $PROJECT_ROOT"
echo "Service Dir: $SERVICE_DIR"
echo "Log File: $LOG_FILE"

# Ensure log directory exists
mkdir -p "$PROJECT_ROOT/logs"

# Kill any existing auth service processes
pkill -f "uvicorn.*:8000" || true
sleep 2

# Change to service directory
cd "$SERVICE_DIR"

# Set environment variables
export PYTHONPATH="$PROJECT_ROOT"
export SECRET_KEY="acgs-development-secret-key-2024-constitutional-ai-governance"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
export CSRF_SECRET_KEY="acgs-development-csrf-secret-key-2024-phase1-infrastructure-stabilization"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
export ACCESS_TOKEN_EXPIRE_MINUTES=30
export REFRESH_TOKEN_EXPIRE_DAYS=7
export BACKEND_CORS_ORIGINS="http://localhost:3000,http://localhost:8080"

# Start the service
echo "Starting auth service with PYTHONPATH=$PYTHONPATH"
"$PROJECT_ROOT/.venv/bin/python" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 > "$LOG_FILE" 2>&1 &

AUTH_PID=$!
echo "Auth service started with PID: $AUTH_PID"

# Wait a moment and check if it's running
sleep 3
if kill -0 $AUTH_PID 2>/dev/null; then
    echo "Auth service is running"
    # Test health endpoint
    sleep 2
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Auth service health check passed"
        exit 0
    else
        echo "❌ Auth service health check failed"
        echo "Check logs: tail -f $LOG_FILE"
        exit 1
    fi
else
    echo "❌ Auth service failed to start"
    echo "Check logs: tail -f $LOG_FILE"
    exit 1
fi
