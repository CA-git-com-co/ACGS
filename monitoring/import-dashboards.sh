#!/bin/bash
# ACGS Dashboard Import Script
# Constitutional Hash: cdd01ef066bc6cf2

set -e

GRAFANA_URL="http://localhost:3001"
GRAFANA_USER="admin"
GRAFANA_PASSWORD=os.environ.get("PASSWORD")
DASHBOARD_DIR="./monitoring/dashboards"

echo "Importing ACGS Dashboards to Grafana..."
echo "Constitutional Hash: cdd01ef066bc6cf2"

# Function to import a dashboard
import_dashboard() {
    local dashboard_file=$1
    local dashboard_name=$(basename "$dashboard_file" .json)
    
    echo "Importing dashboard: $dashboard_name"
    
    curl -X POST \
        -H "Content-Type: application/json" \
        -u "$GRAFANA_USER:$GRAFANA_PASSWORD" \
        -d @"$dashboard_file" \
        "$GRAFANA_URL/api/dashboards/db" \
        --silent --show-error
    
    echo "✓ Dashboard $dashboard_name imported successfully"
}

# Create Prometheus data source first
echo "Creating Prometheus data source..."
curl -X POST \
    -H "Content-Type: application/json" \
    -u "$GRAFANA_USER:$GRAFANA_PASSWORD" \
    -d '{
        "name": "Prometheus",
        "type": "prometheus",
        "url": "http://localhost:9091",
        "access": "proxy",
        "isDefault": true,
        "jsonData": {
            "httpMethod": "POST",
            "manageAlerts": true,
            "alertmanagerUid": ""
        }
    }' \
    "$GRAFANA_URL/api/datasources" \
    --silent --show-error || echo "Data source may already exist"

echo "✓ Prometheus data source configured"

# Import all dashboard files
for dashboard_file in "$DASHBOARD_DIR"/*.json; do
    if [ -f "$dashboard_file" ]; then
        import_dashboard "$dashboard_file"
    fi
done

echo ""
echo "All ACGS dashboards imported successfully!"
echo "Access Grafana at: $GRAFANA_URL"
echo "Username: $GRAFANA_USER"
echo "Password: os.environ.get("PASSWORD")
echo "Constitutional Hash: cdd01ef066bc6cf2"
