#!/bin/bash
set -e

ENVIRONMENT=${1:-staging}
MAX_ATTEMPTS=30
ATTEMPT=0

echo "🏥 Running health checks for $ENVIRONMENT environment..."

if [ "$ENVIRONMENT" = "staging" ]; then
    BASE_URL="http://$STAGING_HOST"
else
    BASE_URL="http://$PRODUCTION_HOST"
fi

# Health check endpoints
endpoints=(
    "$BASE_URL:8000/health"  # Auth Service
    "$BASE_URL:8001/health"  # Constitutional AI
    "$BASE_URL:8005/health"  # Policy Governance
    "$BASE_URL:8004/health"  # Governance Synthesis
)

# Check each endpoint
for endpoint in "${endpoints[@]}"; do
    echo "Checking $endpoint..."
    ATTEMPT=0

    while [ $ATTEMPT -lt $MAX_ATTEMPTS ]; do
        if curl -f -s "$endpoint" > /dev/null; then
            echo "✅ $endpoint is healthy"
            break
        else
            echo "⏳ Waiting for $endpoint... (attempt $((ATTEMPT+1))/$MAX_ATTEMPTS)"
            sleep 10
            ATTEMPT=$((ATTEMPT+1))
        fi
    done

    if [ $ATTEMPT -eq $MAX_ATTEMPTS ]; then
        echo "❌ Health check failed for $endpoint"
        exit 1
    fi
done

echo "✅ All health checks passed"
