# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash
# Simple service startup script for ACGS-1

set -e

echo "🚀 Starting ACGS-1 Services"
echo "=========================="

# Set up environment
export PYTHONPATH="/home/ubuntu/ACGS/services/shared:/home/ubuntu/ACGS/services/core/policy-governance/pgc_service:$PYTHONPATH"
export DATABASE_URL=os.environ.get("DATABASE_URL")
export REDIS_URL="redis://localhost:6379/0"

# Activate virtual environment
source /home/ubuntu/ACGS/.venv/bin/activate

# Function to start a service
start_service() {
    local service_name=$1
    local port=$2
    local service_path=$3
    
    echo "Starting $service_name on port $port..."
    
    cd "/home/dislove/ACGS-1/$service_path"
    
    # Kill any existing process on the port
    pkill -f "port $port" || true
    
    # Start the service in background
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port $port > "/home/dislove/ACGS-1/logs/${service_name}.log" 2>&1 &
    
    # Save PID
    echo $! > "/home/dislove/ACGS-1/pids/${service_name}.pid"
    
    echo "✅ $service_name started with PID $!"
    
    # Wait a moment for startup
    sleep 3
}

# Create directories
mkdir -p /home/dislove/ACGS-1/logs
mkdir -p /home/dislove/ACGS-1/pids

# Start Integrity Service
start_service "integrity_service" 8002 "services/platform/integrity/integrity_service"

# Start PGC Service  
start_service "pgc_service" 8005 "services/core/policy-governance/pgc_service"

echo ""
echo "🔍 Checking service health..."
sleep 10

# Health check
for port in 8002 8005; do
    if curl -f -s "http://localhost:$port/health" > /dev/null; then
        echo "✅ Service on port $port is healthy"
    else
        echo "❌ Service on port $port is not responding"
    fi
done

echo ""
echo "✅ Service startup completed"
