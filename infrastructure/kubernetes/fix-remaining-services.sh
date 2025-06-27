#!/bin/bash

# Fix remaining ACGS-PGP services with correct ports, resources, and security
set -e

# Service configurations: name:port:current_port
declare -A SERVICES=(
    ["governance-synthesis-service"]="8004:8040"
    ["policy-governance-service"]="8005:8050"
    ["evolutionary-computation-service"]="8006:8060"
    ["model-orchestrator-service"]="8007:8070"
)

SERVICES_DIR="infrastructure/kubernetes/services"
CONSTITUTIONAL_HASH="cdd01ef066bc6cf2"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Generate corrected service YAML
generate_service_yaml() {
    local service_name=$1
    local port=$2
    local redis_db=$3
    
    cat > "$SERVICES_DIR/$service_name.yaml" << EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $service_name
  namespace: acgs-system
  labels:
    app: $service_name
    app.kubernetes.io/name: $service_name
    app.kubernetes.io/part-of: acgs-system
    app.kubernetes.io/version: "1.0.0"
spec:
  replicas: 3
  selector:
    matchLabels:
      app: $service_name
  template:
    metadata:
      labels:
        app: $service_name
        app.kubernetes.io/name: $service_name
        app.kubernetes.io/part-of: acgs-system
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
      containers:
      - name: $service_name
        image: acgs/$service_name:latest
        ports:
        - containerPort: $port
          name: http
        env:
        - name: SERVICE_PORT
          value: "$port"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: acgs-secrets
              key: database-url
        - name: REDIS_URL
          value: "redis://dragonflydb:6379/$redis_db"
        - name: AUTH_SERVICE_URL
          value: "http://auth-service:8000"
        - name: AC_SERVICE_URL
          value: "http://constitutional-ai-service:8001"
        - name: INTEGRITY_SERVICE_URL
          value: "http://integrity-service:8002"
        - name: FV_SERVICE_URL
          value: "http://formal-verification-service:8003"
        - name: CONSTITUTIONAL_HASH
          value: "$CONSTITUTIONAL_HASH"
        - name: COMPLIANCE_THRESHOLD
          value: "0.95"
        resources:
          requests:
            cpu: 200m
            memory: 512Mi
          limits:
            cpu: 500m
            memory: 1Gi
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
        readinessProbe:
          httpGet:
            path: /health
            port: $port
          initialDelaySeconds: 10
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: $port
          initialDelaySeconds: 30
          periodSeconds: 10
        volumeMounts:
        - name: tmp
          mountPath: /tmp
        - name: var-run
          mountPath: /var/run
      volumes:
      - name: tmp
        emptyDir: {}
      - name: var-run
        emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: $service_name
  namespace: acgs-system
  labels:
    app: $service_name
    app.kubernetes.io/name: $service_name
    app.kubernetes.io/part-of: acgs-system
spec:
  selector:
    app: $service_name
  ports:
  - name: http
    protocol: TCP
    port: $port
    targetPort: $port
  type: ClusterIP
EOF
}

# Main execution
main() {
    log_info "Fixing remaining ACGS-PGP services..."
    
    # Backup existing files
    log_info "Creating backups..."
    mkdir -p "$SERVICES_DIR/backup"
    for service in "${!SERVICES[@]}"; do
        if [[ -f "$SERVICES_DIR/$service.yaml" ]]; then
            cp "$SERVICES_DIR/$service.yaml" "$SERVICES_DIR/backup/$service.yaml.bak"
        fi
    done
    
    # Generate corrected configurations
    local redis_db=4
    for service in "${!SERVICES[@]}"; do
        local port_info="${SERVICES[$service]}"
        local correct_port=$(echo $port_info | cut -d: -f1)
        
        log_info "Fixing $service (port $correct_port)..."
        generate_service_yaml "$service" "$correct_port" "$redis_db"
        ((redis_db++))
    done
    
    log_info "All services fixed successfully!"
    log_info "Backups stored in: $SERVICES_DIR/backup/"
    
    # Validate the changes
    log_info "Validating configurations..."
    for service in "${!SERVICES[@]}"; do
        local port_info="${SERVICES[$service]}"
        local correct_port=$(echo $port_info | cut -d: -f1)
        
        if grep -q "containerPort: $correct_port" "$SERVICES_DIR/$service.yaml"; then
            log_info "✓ $service port validated ($correct_port)"
        else
            log_warn "⚠ $service port validation failed"
        fi
        
        if grep -q "cpu: 200m" "$SERVICES_DIR/$service.yaml" && \
           grep -q "memory: 512Mi" "$SERVICES_DIR/$service.yaml"; then
            log_info "✓ $service resource limits validated"
        else
            log_warn "⚠ $service resource limits validation failed"
        fi
        
        if grep -q "$CONSTITUTIONAL_HASH" "$SERVICES_DIR/$service.yaml"; then
            log_info "✓ $service constitutional hash validated"
        else
            log_warn "⚠ $service constitutional hash validation failed"
        fi
    done
    
    log_info "Service configuration fixes completed!"
}

main "$@"
