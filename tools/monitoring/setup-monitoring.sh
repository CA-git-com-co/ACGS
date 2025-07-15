# Constitutional Hash: cdd01ef066bc6cf2
# ACGS-2 Constitutional Compliance Validation
#!/bin/bash

# ACGS-1 Monitoring Setup Script
# Comprehensive monitoring setup for ACGS-1 Constitutional Governance System

set -euo pipefail

# Configuration
MONITORING_NAMESPACE="acgs-monitoring"
PROMETHEUS_VERSION="v2.45.0"
GRAFANA_VERSION="10.0.0"
ALERTMANAGER_VERSION="v0.25.0"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    if ! command -v kubectl >/dev/null 2>&1; then
        log_error "kubectl is required but not installed"
        exit 1
    fi
    
    if ! command -v helm >/dev/null 2>&1; then
        log_error "helm is required but not installed"
        exit 1
    fi
    
    # Check if connected to cluster
    if ! kubectl cluster-info >/dev/null 2>&1; then
        log_error "Not connected to Kubernetes cluster"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

# Create monitoring namespace
create_namespace() {
    log_info "Creating monitoring namespace..."
    
    kubectl create namespace "$MONITORING_NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
    
    log_success "Monitoring namespace ready"
}

# Install Prometheus
install_prometheus() {
    log_info "Installing Prometheus..."
    
    # Add Prometheus Helm repository
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    # Create Prometheus values file
    cat > /tmp/prometheus-values.yml << EOF
server:
  global:
    scrape_interval: 15s
    evaluation_interval: 15s
  retention: "30d"
  persistentVolume:
    enabled: true
    size: 50Gi
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 2000m
      memory: 4Gi

alertmanager:
  enabled: true
  persistentVolume:
    enabled: true
    size: 10Gi

nodeExporter:
  enabled: true

pushgateway:
  enabled: true

serverFiles:
  prometheus.yml:
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
    
    rule_files:
      - "/etc/prometheus/rules/*.yml"
    
    scrape_configs:
      - job_name: 'prometheus'
        static_configs:
          - targets: ['localhost:9090']
      
      - job_name: 'acgs-services'
        kubernetes_sd_configs:
          - role: pod
            namespaces:
              names:
                - acgs-blue
                - acgs-green
        relabel_configs:
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
            action: keep
            regex: true
          - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
            action: replace
            target_label: __metrics_path__
            regex: (.+)
          - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
            action: replace
            regex: ([^:]+)(?::\d+)?;(\d+)
            replacement: \$1:\$2
            target_label: __address__
          - action: labelmap
            regex: __meta_kubernetes_pod_label_(.+)
          - source_labels: [__meta_kubernetes_namespace]
            action: replace
            target_label: kubernetes_namespace
          - source_labels: [__meta_kubernetes_pod_name]
            action: replace
            target_label: kubernetes_pod_name

  rules:
    acgs-rules.yml: |
      groups:
        - name: acgs.rules
          rules:
            - alert: ACGSServiceDown
              expr: up{job="acgs-services"} == 0
              for: 1m
              labels:
                severity: critical
              annotations:
                summary: "ACGS service {{ \$labels.instance }} is down"
                description: "ACGS service {{ \$labels.instance }} has been down for more than 1 minute."
            
            - alert: ACGSHighResponseTime
              expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="acgs-services"}[5m])) > 2
              for: 5m
              labels:
                severity: warning
              annotations:
                summary: "High response time for ACGS service {{ \$labels.instance }}"
                description: "95th percentile response time is {{ \$value }}s for {{ \$labels.instance }}"
            
            - alert: ACGSHighErrorRate
              expr: rate(http_requests_total{job="acgs-services",status=~"5.."}[5m]) / rate(http_requests_total{job="acgs-services"}[5m]) > 0.05
              for: 5m
              labels:
                severity: critical
              annotations:
                summary: "High error rate for ACGS service {{ \$labels.instance }}"
                description: "Error rate is {{ \$value | humanizePercentage }} for {{ \$labels.instance }}"
EOF
    
    # Install Prometheus
    helm upgrade --install prometheus prometheus-community/prometheus \
        --namespace "$MONITORING_NAMESPACE" \
        --values /tmp/prometheus-values.yml \
        --wait
    
    log_success "Prometheus installed successfully"
}

# Install Grafana
install_grafana() {
    log_info "Installing Grafana..."
    
    # Add Grafana Helm repository
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo update
    
    # Create Grafana values file
    cat > /tmp/grafana-values.yml << EOF
adminPassword: os.environ.get("PASSWORD")  # Change this in production

persistence:
  enabled: true
  size: 10Gi

resources:
  requests:
    cpu: 250m
    memory: 512Mi
  limits:
    cpu: 500m
    memory: 1Gi

datasources:
  datasources.yaml:
    apiVersion: 1
    datasources:
      - name: Prometheus
        type: prometheus
        url: http://prometheus-server:80
        access: proxy
        isDefault: true

dashboardProviders:
  dashboardproviders.yaml:
    apiVersion: 1
    providers:
      - name: 'acgs-dashboards'
        orgId: 1
        folder: 'ACGS'
        type: file
        disableDeletion: false
        editable: true
        options:
          path: /var/lib/grafana/dashboards/acgs

dashboards:
  acgs-dashboards:
    acgs-overview:
      gnetId: 1860
      revision: 27
      datasource: Prometheus
    
    acgs-services:
      json: |
        {
          "dashboard": {
            "id": null,
            "title": "ACGS Services Overview",
            "tags": ["acgs", "constitutional-governance"],
            "timezone": "browser",
            "panels": [
              {
                "id": 1,
                "title": "Service Availability",
                "type": "stat",
                "targets": [
                  {
                    "expr": "up{job=\"acgs-services\"}",
                    "legendFormat": "{{ instance }}"
                  }
                ],
                "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
              },
              {
                "id": 2,
                "title": "Response Time (95th percentile)",
                "type": "graph",
                "targets": [
                  {
                    "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job=\"acgs-services\"}[5m]))",
                    "legendFormat": "{{ instance }}"
                  }
                ],
                "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
              }
            ],
            "time": {"from": "now-1h", "to": "now"},
            "refresh": "30s"
          }
        }

service:
  type: LoadBalancer
  port: 80

ingress:
  enabled: true
  annotations:
    kubernetes.io/ingress.class: nginx
  hosts:
    - host: grafana.acgs-pgp.local
      paths:
        - path: /
          pathType: Prefix
EOF
    
    # Install Grafana
    helm upgrade --install grafana grafana/grafana \
        --namespace "$MONITORING_NAMESPACE" \
        --values /tmp/grafana-values.yml \
        --wait
    
    log_success "Grafana installed successfully"
}

# Install Jaeger for distributed tracing
install_jaeger() {
    log_info "Installing Jaeger for distributed tracing..."
    
    # Add Jaeger Helm repository
    helm repo add jaegertracing https://jaegertracing.github.io/helm-charts
    helm repo update
    
    # Create Jaeger values file
    cat > /tmp/jaeger-values.yml << EOF
provisionDataStore:
  cassandra: false
  elasticsearch: true

elasticsearch:
  replicas: 1
  minimumMasterNodes: 1
  resources:
    requests:
      cpu: 500m
      memory: 1Gi
    limits:
      cpu: 1000m
      memory: 2Gi

agent:
  enabled: true

collector:
  enabled: true
  resources:
    requests:
      cpu: 250m
      memory: 512Mi
    limits:
      cpu: 500m
      memory: 1Gi

query:
  enabled: true
  resources:
    requests:
      cpu: 250m
      memory: 512Mi
    limits:
      cpu: 500m
      memory: 1Gi
  
  ingress:
    enabled: true
    annotations:
      kubernetes.io/ingress.class: nginx
    hosts:
      - host: jaeger.acgs-pgp.local
        paths:
          - path: /
            pathType: Prefix
EOF
    
    # Install Jaeger
    helm upgrade --install jaeger jaegertracing/jaeger \
        --namespace "$MONITORING_NAMESPACE" \
        --values /tmp/jaeger-values.yml \
        --wait
    
    log_success "Jaeger installed successfully"
}

# Setup service monitors
setup_service_monitors() {
    log_info "Setting up service monitors..."
    
    # Create ServiceMonitor for ACGS services
    cat > /tmp/acgs-service-monitor.yml << EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: acgs-services
  namespace: $MONITORING_NAMESPACE
  labels:
    app: acgs
spec:
  selector:
    matchLabels:
      app: acgs
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
  namespaceSelector:
    matchNames:
    - acgs-blue
    - acgs-green
EOF
    
    kubectl apply -f /tmp/acgs-service-monitor.yml
    
    log_success "Service monitors configured"
}

# Create monitoring dashboard
create_monitoring_dashboard() {
    log_info "Creating monitoring dashboard..."
    
    # Get Grafana admin password
    GRAFANA_PASSWORD=os.environ.get("PASSWORD")$MONITORING_NAMESPACE" grafana -o jsonpath="{.data.admin-password}" | base64 --decode)
    
    log_info "Grafana admin password: os.environ.get("PASSWORD")
    log_info "Access Grafana at: http://grafana.acgs-pgp.local"
    log_info "Access Jaeger at: http://jaeger.acgs-pgp.local"
    
    # Port forward for local access
    log_info "Setting up port forwarding for local access..."
    log_info "Run these commands for local access:"
    echo "kubectl port-forward --namespace $MONITORING_NAMESPACE svc/grafana 3000:80"
    echo "kubectl port-forward --namespace $MONITORING_NAMESPACE svc/jaeger-query 16686:80"
    echo "kubectl port-forward --namespace $MONITORING_NAMESPACE svc/prometheus-server 9090:80"
    
    log_success "Monitoring dashboard ready"
}

# Main execution
main() {
    log_info "Setting up ACGS-1 monitoring infrastructure..."
    
    check_prerequisites
    create_namespace
    install_prometheus
    install_grafana
    install_jaeger
    setup_service_monitors
    create_monitoring_dashboard
    
    log_success "ACGS-1 monitoring setup completed successfully!"
    log_info "Next steps:"
    log_info "1. Configure service metrics endpoints"
    log_info "2. Set up alerting rules"
    log_info "3. Create custom dashboards"
    log_info "4. Test monitoring and alerting"
}

# Run main function
main "$@"
