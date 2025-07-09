#!/bin/bash
# Environment Variable Override for ACGS-1 Services
# Source this file to set correct service URLs

export AC_SERVICE_URL="http://localhost:8001"
export INTEGRITY_SERVICE_URL="http://localhost:8002"
export FV_SERVICE_URL="http://localhost:8003"
export GS_SERVICE_URL="http://localhost:8004"
export PGC_SERVICE_URL="http://localhost:8005"
export EC_SERVICE_URL="http://localhost:8006"
export AUTH_SERVICE_URL="http://localhost:8000"

export SERVICE_DISCOVERY_ENABLED="true"
export HEALTH_CHECK_TIMEOUT="5.0"
export REQUEST_TIMEOUT="30.0"

echo "✅ ACGS-1 service environment variables set for localhost deployment"
