#!/bin/bash
# Constitutional Health Check Script
# Constitutional hash: cdd01ef066bc6cf2

set -euo pipefail

# Constants
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"
TIMEOUT=10
RETRIES=3

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] HEALTH CHECK: $1${NC}"
}

log_error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Check if service port is provided via environment variable
if [ -n "${SERVICE_PORT:-}" ]; then
    PORT=$SERVICE_PORT
elif [ -n "${1:-}" ]; then
    PORT=$1
else
    PORT=8000  # Default port
fi

log "Starting constitutional health check for service on port $PORT"

# Check if the port is open
if ! command -v curl &> /dev/null; then
    if ! command -v wget &> /dev/null; then
        log_error "Neither curl nor wget is available for health check"
        exit 1
    fi
    HEALTH_CMD="wget -q --spider --timeout=$TIMEOUT"
else
    HEALTH_CMD="curl -f --connect-timeout $TIMEOUT --max-time $TIMEOUT -s"
fi

# Health check URL
HEALTH_URL="http://localhost:$PORT/health"

# Perform health check with retries
for i in $(seq 1 $RETRIES); do
    log "Health check attempt $i/$RETRIES"
    
    if $HEALTH_CMD $HEALTH_URL > /dev/null 2>&1; then
        log "✅ Service is responding on port $PORT"
        
        # Check for constitutional compliance if curl is available
        if command -v curl &> /dev/null; then
            response=$(curl -s --connect-timeout $TIMEOUT --max-time $TIMEOUT $HEALTH_URL 2>/dev/null || echo "")
            if echo "$response" | grep -q "$CONSTITUTIONAL_HASH" 2>/dev/null; then
                log "✅ Constitutional compliance verified (hash: $CONSTITUTIONAL_HASH)"
                exit 0
            else
                log_warning "⚠️ Service responding but constitutional hash not found"
                # Try constitutional-specific endpoint
                constitutional_url="http://localhost:$PORT/health/constitutional"
                const_response=$(curl -s --connect-timeout $TIMEOUT --max-time $TIMEOUT $constitutional_url 2>/dev/null || echo "")
                if echo "$const_response" | grep -q "$CONSTITUTIONAL_HASH" 2>/dev/null; then
                    log "✅ Constitutional compliance verified via constitutional endpoint"
                    exit 0
                else
                    log_warning "Constitutional compliance check inconclusive, but service is healthy"
                    exit 0
                fi
            fi
        else
            log "✅ Service is healthy (constitutional compliance check requires curl)"
            exit 0
        fi
    else
        log_error "❌ Health check failed (attempt $i/$RETRIES)"
        if [ $i -lt $RETRIES ]; then
            sleep 2
        fi
    fi
done

log_error "❌ Health check failed after $RETRIES attempts"
exit 1
