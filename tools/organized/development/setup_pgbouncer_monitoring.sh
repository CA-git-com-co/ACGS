# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash
# ACGS-1 PgBouncer Monitoring Setup Script
# Phase 2 - Enterprise Scalability & Performance
# Sets up comprehensive monitoring for PgBouncer with Prometheus and Grafana

set -e

echo "🔧 Setting up PgBouncer monitoring for ACGS-1..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Configuration
PROJECT_ROOT="/home/dislove/ACGS-1"
PROMETHEUS_CONFIG_DIR="$PROJECT_ROOT/infrastructure/monitoring/prometheus"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
GRAFANA_CONFIG_DIR="$PROJECT_ROOT/infrastructure/monitoring/grafana"
EXPORTER_PORT="9187"
PGBOUNCER_HOST="localhost"
PGBOUNCER_PORT="6432"

# Create monitoring directories
print_status "Creating monitoring directories..."
mkdir -p "$PROMETHEUS_CONFIG_DIR/rules"
mkdir -p "$GRAFANA_CONFIG_DIR/dashboards"
mkdir -p "$GRAFANA_CONFIG_DIR/provisioning/dashboards"
mkdir -p "$GRAFANA_CONFIG_DIR/provisioning/datasources"
mkdir -p "logs"

print_success "Monitoring directories created"

# Update Prometheus configuration
print_status "Updating Prometheus configuration..."

cat > "$PROMETHEUS_CONFIG_DIR/prometheus.yml" << EOF
# ACGS-1 Prometheus Configuration
# Phase 2 - Enterprise Scalability & Performance

global:
  scrape_interval: 15s
  evaluation_interval: 15s
  external_labels:
    cluster: 'acgs-1'
    environment: 'production'

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  # Prometheus self-monitoring
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
    scrape_interval: 15s
    metrics_path: /metrics

  # Node Exporter
  - job_name: 'node'
    static_configs:
      - targets: ['localhost:9100']
    scrape_interval: 15s

  # PgBouncer Exporter
  - job_name: 'pgbouncer'
    static_configs:
      - targets: ['localhost:$EXPORTER_PORT']
    scrape_interval: 15s
    metrics_path: /metrics
    scrape_timeout: 10s

  # ACGS Core Services
  - job_name: 'acgs-auth'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'acgs-ac'
    static_configs:
      - targets: ['localhost:8001']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'acgs-integrity'
    static_configs:
      - targets: ['localhost:8002']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'acgs-fv'
    static_configs:
      - targets: ['localhost:8003']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'acgs-gs'
    static_configs:
      - targets: ['localhost:8004']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'acgs-pgc'
    static_configs:
      - targets: ['localhost:8005']
    metrics_path: /metrics
    scrape_interval: 30s

  - job_name: 'acgs-ec'
    static_configs:
      - targets: ['localhost:8006']
    metrics_path: /metrics
    scrape_interval: 30s

  # PostgreSQL Exporter
  - job_name: 'postgres'
    static_configs:
      - targets: ['localhost:9187']
    scrape_interval: 30s

  # Redis Exporter
  - job_name: 'redis'
    static_configs:
      - targets: ['localhost:9121']
    scrape_interval: 30s
EOF

print_success "Prometheus configuration updated"

# Copy alerting rules
print_status "Installing PgBouncer alerting rules..."
cp "$PROJECT_ROOT/infrastructure/monitoring/prometheus_rules/pgbouncer_alerts.yml" "$PROMETHEUS_CONFIG_DIR/rules/"  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
print_success "Alerting rules installed"

# Create Grafana datasource configuration
print_status "Creating Grafana datasource configuration..."

cat > "$GRAFANA_CONFIG_DIR/provisioning/datasources/prometheus.yml" << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://localhost:9090
    isDefault: true
    editable: true
    jsonData:
      timeInterval: "15s"
      queryTimeout: "60s"
      httpMethod: "POST"
EOF

print_success "Grafana datasource configuration created"

# Create Grafana dashboard provisioning
print_status "Creating Grafana dashboard provisioning..."

cat > "$GRAFANA_CONFIG_DIR/provisioning/dashboards/acgs.yml" << EOF
apiVersion: 1

providers:
  - name: 'ACGS Dashboards'
    orgId: 1
    folder: 'ACGS-1'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF

print_success "Grafana dashboard provisioning created"

# Copy dashboard
print_status "Installing PgBouncer dashboard..."
cp "$PROJECT_ROOT/infrastructure/monitoring/grafana_dashboards/pgbouncer_dashboard.json" "$GRAFANA_CONFIG_DIR/dashboards/"
print_success "PgBouncer dashboard installed"

# Create systemd service for PgBouncer exporter
print_status "Creating systemd service for PgBouncer exporter..."

sudo tee /etc/systemd/system/pgbouncer-exporter.service > /dev/null << EOF
[Unit]
Description=PgBouncer Prometheus Exporter
After=network.target
Wants=network.target

[Service]
Type=simple
User=acgs
Group=acgs
WorkingDirectory=$PROJECT_ROOT
ExecStart=/usr/bin/python3 $PROJECT_ROOT/infrastructure/monitoring/pgbouncer_exporter.py \\  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
    --pgbouncer-host $PGBOUNCER_HOST \\
    --pgbouncer-port $PGBOUNCER_PORT \\
    --exporter-port $EXPORTER_PORT \\
    --scrape-interval 15
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=pgbouncer-exporter

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=$PROJECT_ROOT/logs

[Install]
WantedBy=multi-user.target
EOF

print_success "Systemd service created"

# Install Python dependencies for exporter
print_status "Installing Python dependencies for PgBouncer exporter..."
pip3 install --user asyncpg prometheus_client || print_warning "Failed to install some dependencies"

# Reload systemd and enable service
print_status "Enabling PgBouncer exporter service..."
sudo systemctl daemon-reload
sudo systemctl enable pgbouncer-exporter.service

# Start the exporter
print_status "Starting PgBouncer exporter..."
sudo systemctl start pgbouncer-exporter.service

# Wait a moment and check status
sleep 3
if sudo systemctl is-active --quiet pgbouncer-exporter.service; then
    print_success "PgBouncer exporter is running"
else
    print_warning "PgBouncer exporter may not be running properly"
    sudo systemctl status pgbouncer-exporter.service --no-pager -l
fi

# Test exporter endpoint
print_status "Testing PgBouncer exporter endpoint..."
if curl -s "http://localhost:$EXPORTER_PORT/metrics" > /dev/null; then
    print_success "PgBouncer exporter endpoint is responding"
else
    print_warning "PgBouncer exporter endpoint is not responding"
fi

# Restart Prometheus to pick up new configuration
print_status "Restarting Prometheus to load new configuration..."
if sudo systemctl is-active --quiet prometheus; then
    sudo systemctl restart prometheus
    sleep 5
    if sudo systemctl is-active --quiet prometheus; then
        print_success "Prometheus restarted successfully"
    else
        print_error "Failed to restart Prometheus"
        sudo systemctl status prometheus --no-pager -l
    fi
else
    print_warning "Prometheus is not running - please start it manually"
fi

# Restart Grafana to pick up new dashboards
print_status "Restarting Grafana to load new dashboards..."
if sudo systemctl is-active --quiet grafana-server; then
    sudo systemctl restart grafana-server
    sleep 5
    if sudo systemctl is-active --quiet grafana-server; then
        print_success "Grafana restarted successfully"
    else
        print_error "Failed to restart Grafana"
        sudo systemctl status grafana-server --no-pager -l
    fi
else
    print_warning "Grafana is not running - please start it manually"
fi

# Create performance tuning script
print_status "Creating performance tuning script..."

cat > "scripts/tune_pgbouncer_performance.py" << 'EOF'
#!/usr/bin/env python3
"""
ACGS-1 PgBouncer Performance Tuning Script
Analyzes metrics and provides optimization recommendations
"""

import asyncio
import asyncpg
import json
import time
from typing import Dict, List, Any

async def analyze_pgbouncer_performance():
    """Analyze PgBouncer performance and provide recommendations."""
    
    try:
        # Connect to PgBouncer admin interface
        conn = await asyncpg.connect(
            host="localhost",
            port=6432,
            database="pgbouncer",
            user="acgs_user",
            password=os.environ.get("PASSWORD"),
            timeout=10
        )
        
        # Collect performance data
        stats = await conn.fetch("SHOW STATS")
        pools = await conn.fetch("SHOW POOLS")
        config = await conn.fetch("SHOW CONFIG")
        
        await conn.close()
        
        # Analyze and generate recommendations
        recommendations = []
        
        # Analyze pool usage
        for pool in pools:
            usage_percent = (pool['pool_used'] / pool['pool_size']) * 100 if pool['pool_size'] > 0 else 0
            
            if usage_percent > 80:
                recommendations.append({
                    "type": "pool_size",
                    "severity": "high",
                    "database": pool['database'],
                    "current_usage": f"{usage_percent:.1f}%",
                    "recommendation": f"Increase pool size for {pool['database']} from {pool['pool_size']} to {int(pool['pool_size'] * 1.5)}"
                })
        
        # Analyze request performance
        for stat in stats:
            if stat['database'] == 'pgbouncer':
                continue
                
            if stat['total_requests'] > 0:
                avg_req_time = stat['total_query_time'] / stat['total_requests'] / 1000  # Convert to ms
                avg_wait_time = stat['total_wait_time'] / stat['total_requests'] / 1000
                
                if avg_req_time > 500:
                    recommendations.append({
                        "type": "performance",
                        "severity": "medium",
                        "database": stat['database'],
                        "avg_request_time": f"{avg_req_time:.2f}ms",
                        "recommendation": "High request time detected - consider optimizing queries or increasing connection pool"
                    })
                
                if avg_wait_time > 100:
                    recommendations.append({
                        "type": "performance",
                        "severity": "medium",
                        "database": stat['database'],
                        "avg_wait_time": f"{avg_wait_time:.2f}ms",
                        "recommendation": "High wait time detected - consider increasing pool size or max_client_conn"
                    })
        
        # Generate report
        report = {
            "timestamp": time.time(),
            "analysis_summary": {
                "total_recommendations": len(recommendations),
                "high_severity": len([r for r in recommendations if r["severity"] == "high"]),
                "medium_severity": len([r for r in recommendations if r["severity"] == "medium"]),
            },
            "recommendations": recommendations,
            "current_stats": [dict(stat) for stat in stats],
            "current_pools": [dict(pool) for pool in pools],
        }
        
        # Save report
        with open("logs/pgbouncer_performance_analysis.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print("🔍 PgBouncer Performance Analysis Complete")
        print("=" * 50)
        print(f"Total Recommendations: {len(recommendations)}")
        print(f"High Severity: {len([r for r in recommendations if r['severity'] == 'high'])}")
        print(f"Medium Severity: {len([r for r in recommendations if r['severity'] == 'medium'])}")
        
        if recommendations:
            print("\n📋 Top Recommendations:")
            for i, rec in enumerate(recommendations[:5], 1):
                print(f"{i}. [{rec['severity'].upper()}] {rec['recommendation']}")
        else:
            print("\n✅ No performance issues detected!")
        
        print(f"\n📄 Full report saved to: logs/pgbouncer_performance_analysis.json")
        
    except Exception as e:
        print(f"❌ Error analyzing PgBouncer performance: {e}")

if __name__ == "__main__":
    asyncio.run(analyze_pgbouncer_performance())
EOF

chmod +x "scripts/tune_pgbouncer_performance.py"
print_success "Performance tuning script created"

print_success "PgBouncer monitoring setup completed!"
print_status "Monitoring Summary:"
echo "- PgBouncer Exporter: http://localhost:$EXPORTER_PORT/metrics"
echo "- Prometheus: http://localhost:9090"
echo "- Grafana: http://localhost:3000"
echo "- PgBouncer Dashboard: Available in Grafana under 'ACGS-1' folder"
echo "- Alerting Rules: Configured for >99.9% availability and <500ms response times"
echo "- Performance Analysis: Run ./scripts/tune_pgbouncer_performance.py"

print_status "Next steps:"
echo "1. Access Grafana dashboard to monitor PgBouncer performance"
echo "2. Configure alert notifications (email, Slack, etc.)"
echo "3. Run performance analysis script regularly"
echo "4. Monitor alerts and optimize based on recommendations"
echo "5. Set up automated performance tuning based on metrics"
