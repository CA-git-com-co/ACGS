#!/bin/bash
# Restart ACGS services with PgBouncer configuration

echo "🔄 Restarting ACGS services with PgBouncer configuration..."

# Export PgBouncer environment variables
export DATABASE_URL="postgresql://acgs_user:acgs_password@localhost:6432/acgs_db"
export DB_HOST="localhost"
export DB_PORT="6432"
export PGBOUNCER_ENABLED="true"

# Function to restart service if running
restart_service() {
    local port=$1
    local service_name=$2
    
    echo "Checking $service_name on port $port..."
    
    # Find process using the port
    local pid=$(lsof -ti:$port 2>/dev/null)
    
    if [ -n "$pid" ]; then
        echo "Stopping $service_name (PID: $pid)..."
        kill -TERM "$pid"
        sleep 5
        
        # Force kill if still running
        if kill -0 "$pid" 2>/dev/null; then
            echo "Force stopping $service_name..."
            kill -KILL "$pid"
        fi
        
        echo "$service_name stopped"
    else
        echo "$service_name is not running"
    fi
}

# Restart services
restart_service 8000 "auth_service"
restart_service 8001 "ac_service"
restart_service 8002 "integrity_service"
restart_service 8003 "fv_service"
restart_service 8004 "gs_service"
restart_service 8005 "pgc_service"
restart_service 8006 "ec_service"

echo "✅ Service restart script completed"
echo "Services will need to be manually restarted with new PgBouncer configuration"
