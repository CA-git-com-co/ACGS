#!/bin/bash
# ACGS-2 Basic Monitoring Startup Script

echo "🚀 Starting ACGS-2 Basic Monitoring Infrastructure..."

# Start Prometheus
echo "📊 Starting Prometheus..."
prometheus --config.file=config/monitoring/prometheus.yml --storage.tsdb.path=data/prometheus &
PROMETHEUS_PID=$!

# Start Alertmanager
echo "🚨 Starting Alertmanager..."
alertmanager --config.file=config/monitoring/alertmanager.yml --storage.path=data/alertmanager &
ALERTMANAGER_PID=$!

# Start Grafana
echo "📈 Starting Grafana..."
grafana-server --config=config/monitoring/grafana.ini &
GRAFANA_PID=$!

echo "✅ Monitoring infrastructure started successfully!"
echo "📊 Prometheus: http://localhost:9090"
echo "🚨 Alertmanager: http://localhost:9093"
echo "📈 Grafana: http://localhost:3000"

# Save PIDs for cleanup
echo $PROMETHEUS_PID > data/prometheus.pid
echo $ALERTMANAGER_PID > data/alertmanager.pid
echo $GRAFANA_PID > data/grafana.pid

echo "🔍 Monitoring ACGS-2 services..."
echo "Press Ctrl+C to stop monitoring"

# Wait for interrupt
trap 'echo "🛑 Stopping monitoring..."; kill $PROMETHEUS_PID $ALERTMANAGER_PID $GRAFANA_PID; exit' INT
wait
