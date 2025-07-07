#!/bin/bash
# ACGS Automated Metrics Collection Script
# Constitutional Hash: cdd01ef066bc6cf2

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
METRICS_DIR="$SCRIPT_DIR/../../monitoring/metrics"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

# Create metrics directory
mkdir -p "$METRICS_DIR"

echo "=== ACGS Automated Metrics Collection ==="
echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
echo "Timestamp: $TIMESTAMP"
echo ""

# Function to collect Prometheus metrics
collect_prometheus_metrics() {
    echo "Collecting Prometheus metrics..."
    
    local metrics_file="$METRICS_DIR/prometheus_metrics_$TIMESTAMP.json"
    
    # Collect key performance metrics
    cat > "$metrics_file" << EOF
{
  "constitutional_hash": "$CONSTITUTIONAL_HASH",
  "timestamp": "$(date -Iseconds)",
  "collection_type": "prometheus_metrics",
  "metrics": {
EOF

    # Query Prometheus for key metrics
    echo "    \"prometheus_health\": $(curl -s http://localhost:9091/api/v1/query?query=up | jq '.data.result | length')," >> "$metrics_file"
    echo "    \"active_alerts\": $(curl -s http://localhost:9091/api/v1/alerts | jq '.data.alerts | length')," >> "$metrics_file"
    echo "    \"rule_groups\": $(curl -s http://localhost:9091/api/v1/rules | jq '.data.groups | length')," >> "$metrics_file"
    
    # Get target health status
    local targets_up=$(curl -s http://localhost:9091/api/v1/targets | jq '.data.activeTargets | map(select(.health == "up")) | length')
    local targets_total=$(curl -s http://localhost:9091/api/v1/targets | jq '.data.activeTargets | length')
    
    echo "    \"targets_up\": $targets_up," >> "$metrics_file"
    echo "    \"targets_total\": $targets_total," >> "$metrics_file"
    echo "    \"target_health_percentage\": $(( (targets_up * 100) / targets_total ))" >> "$metrics_file"
    
    cat >> "$metrics_file" << EOF
  }
}
EOF

    echo "✓ Prometheus metrics saved to: $metrics_file"
}

# Function to collect Grafana metrics
collect_grafana_metrics() {
    echo "Collecting Grafana metrics..."
    
    local metrics_file="$METRICS_DIR/grafana_metrics_$TIMESTAMP.json"
    
    # Collect Grafana dashboard and datasource info
    cat > "$metrics_file" << EOF
{
  "constitutional_hash": "$CONSTITUTIONAL_HASH",
  "timestamp": "$(date -Iseconds)",
  "collection_type": "grafana_metrics",
  "metrics": {
EOF

    # Get dashboard count
    local dashboard_count=$(curl -s -u admin:acgs_admin_2025 http://localhost:3001/api/search?type=dash-db | jq '. | length')
    local datasource_count=$(curl -s -u admin:acgs_admin_2025 http://localhost:3001/api/datasources | jq '. | length')
    
    echo "    \"dashboards_count\": $dashboard_count," >> "$metrics_file"
    echo "    \"datasources_count\": $datasource_count," >> "$metrics_file"
    
    # Get health status
    local health_status=$(curl -s http://localhost:3001/api/health | jq -r '.database')
    echo "    \"health_status\": \"$health_status\"" >> "$metrics_file"
    
    cat >> "$metrics_file" << EOF
  }
}
EOF

    echo "✓ Grafana metrics saved to: $metrics_file"
}

# Function to collect infrastructure metrics
collect_infrastructure_metrics() {
    echo "Collecting infrastructure metrics..."
    
    local metrics_file="$METRICS_DIR/infrastructure_metrics_$TIMESTAMP.json"
    
    cat > "$metrics_file" << EOF
{
  "constitutional_hash": "$CONSTITUTIONAL_HASH",
  "timestamp": "$(date -Iseconds)",
  "collection_type": "infrastructure_metrics",
  "services": {
EOF

    # Check PostgreSQL
    if docker exec acgs_postgres_production pg_isready -U acgs_user -d acgs > /dev/null 2>&1; then
        echo "    \"postgresql\": {" >> "$metrics_file"
        echo "      \"status\": \"healthy\"," >> "$metrics_file"
        echo "      \"port\": 5440," >> "$metrics_file"
        echo "      \"container\": \"acgs_postgres_production\"" >> "$metrics_file"
        echo "    }," >> "$metrics_file"
    else
        echo "    \"postgresql\": {" >> "$metrics_file"
        echo "      \"status\": \"unhealthy\"," >> "$metrics_file"
        echo "      \"port\": 5440," >> "$metrics_file"
        echo "      \"container\": \"acgs_postgres_production\"" >> "$metrics_file"
        echo "    }," >> "$metrics_file"
    fi

    # Check Redis
    if docker exec acgs_redis_production redis-cli -a redis_production_password_2025 ping > /dev/null 2>&1; then
        echo "    \"redis\": {" >> "$metrics_file"
        echo "      \"status\": \"healthy\"," >> "$metrics_file"
        echo "      \"port\": 6390," >> "$metrics_file"
        echo "      \"container\": \"acgs_redis_production\"" >> "$metrics_file"
        echo "    }," >> "$metrics_file"
    else
        echo "    \"redis\": {" >> "$metrics_file"
        echo "      \"status\": \"unhealthy\"," >> "$metrics_file"
        echo "      \"port\": 6390," >> "$metrics_file"
        echo "      \"container\": \"acgs_redis_production\"" >> "$metrics_file"
        echo "    }," >> "$metrics_file"
    fi

    # Check Prometheus
    if curl -s http://localhost:9091/api/v1/status/config > /dev/null; then
        echo "    \"prometheus\": {" >> "$metrics_file"
        echo "      \"status\": \"healthy\"," >> "$metrics_file"
        echo "      \"port\": 9091," >> "$metrics_file"
        echo "      \"container\": \"acgs_prometheus_production\"" >> "$metrics_file"
        echo "    }," >> "$metrics_file"
    else
        echo "    \"prometheus\": {" >> "$metrics_file"
        echo "      \"status\": \"unhealthy\"," >> "$metrics_file"
        echo "      \"port\": 9091," >> "$metrics_file"
        echo "      \"container\": \"acgs_prometheus_production\"" >> "$metrics_file"
        echo "    }," >> "$metrics_file"
    fi

    # Check Grafana
    if curl -s http://localhost:3001/api/health > /dev/null; then
        echo "    \"grafana\": {" >> "$metrics_file"
        echo "      \"status\": \"healthy\"," >> "$metrics_file"
        echo "      \"port\": 3001," >> "$metrics_file"
        echo "      \"container\": \"acgs_grafana_production\"" >> "$metrics_file"
        echo "    }" >> "$metrics_file"
    else
        echo "    \"grafana\": {" >> "$metrics_file"
        echo "      \"status\": \"unhealthy\"," >> "$metrics_file"
        echo "      \"port\": 3001," >> "$metrics_file"
        echo "      \"container\": \"acgs_grafana_production\"" >> "$metrics_file"
        echo "    }" >> "$metrics_file"
    fi

    cat >> "$metrics_file" << EOF
  }
}
EOF

    echo "✓ Infrastructure metrics saved to: $metrics_file"
}

# Function to generate summary report
generate_summary_report() {
    echo "Generating summary report..."
    
    local summary_file="$METRICS_DIR/metrics_summary_$TIMESTAMP.json"
    
    cat > "$summary_file" << EOF
{
  "constitutional_hash": "$CONSTITUTIONAL_HASH",
  "timestamp": "$(date -Iseconds)",
  "collection_summary": {
    "prometheus_metrics": "prometheus_metrics_$TIMESTAMP.json",
    "grafana_metrics": "grafana_metrics_$TIMESTAMP.json",
    "infrastructure_metrics": "infrastructure_metrics_$TIMESTAMP.json"
  },
  "collection_status": "completed",
  "next_collection": "$(date -d '+1 hour' -Iseconds)"
}
EOF

    echo "✓ Summary report saved to: $summary_file"
}

# Main execution
main() {
    collect_prometheus_metrics
    collect_grafana_metrics
    collect_infrastructure_metrics
    generate_summary_report
    
    echo ""
    echo "=== Metrics Collection Complete ==="
    echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
    echo "All metrics saved to: $METRICS_DIR"
    echo "Next collection scheduled for: $(date -d '+1 hour')"
}

# Execute main function
main "$@"
