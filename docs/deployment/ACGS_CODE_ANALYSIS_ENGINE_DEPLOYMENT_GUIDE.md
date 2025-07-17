# ACGS Code Analysis Engine - Production Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the ACGS Code Analysis Engine in production environments. The deployment is designed to integrate seamlessly with existing ACGS infrastructure while maintaining high availability, performance, and constitutional compliance.

**Service Specifications:**
- **Service Name**: ACGS Code Analysis Engine
- **Port**: 8007
- <!-- Constitutional Hash: cdd01ef066bc6cf2 -->
- **Performance Targets**: P99 < 10ms, >100 RPS, >85% cache hit rate

## Prerequisites

### Infrastructure Requirements

#### Hardware Requirements
- **CPU**: Minimum 4 cores, Recommended 8+ cores
- **Memory**: Minimum 8GB RAM, Recommended 16GB+ RAM
- **Storage**: Minimum 50GB SSD, Recommended 100GB+ SSD
- **Network**: 1Gbps network interface

#### Software Requirements
- **Operating System**: Ubuntu 20.04+ LTS or RHEL 8+
- **Python**: 3.11 or 3.12
- **Docker**: 20.10+ (for containerized deployment)
- **Kubernetes**: 1.25+ (for orchestrated deployment)

#### ACGS Infrastructure Dependencies
- **PostgreSQL**: Port 5439 with pgvector extension
- **Redis**: Port 6389 with appropriate access permissions
- **Auth Service**: Port 8016 for authentication
- **Context Service**: Port 8012 for integration
- **Service Registry**: Available for service discovery

### Network Configuration

```bash
# Required firewall rules
sudo ufw allow 8007/tcp  # Code Analysis Engine API
sudo ufw allow 9091/tcp  # Prometheus metrics (optional)

# Outbound connections required
# - PostgreSQL: 5439
# - Redis: 6389
# - Auth Service: 8016
# - Context Service: 8012
```

## Installation Methods

### Method 1: Docker Deployment (Recommended)

#### Step 1: Prepare Environment

```bash
# Create deployment directory
sudo mkdir -p /opt/acgs/code-analysis
cd /opt/acgs/code-analysis

# Create configuration directory
sudo mkdir -p config logs data

# Set permissions
sudo chown -R $USER:$USER /opt/acgs/code-analysis
```

#### Step 2: Create Environment Configuration

```bash
# Create production environment file
cat > config/config/environments/development.env << 'EOF'
# Service Configuration
ENVIRONMENT=production
ACGS_CODE_ANALYSIS_HOST=0.0.0.0
ACGS_CODE_ANALYSIS_PORT=8007
ACGS_CODE_ANALYSIS_WORKERS=4

# Database Configuration (ACGS PostgreSQL)
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5439
POSTGRESQL_DATABASE=acgs
POSTGRESQL_USER=acgs_code_analysis_user
POSTGRESQL_PASSWORD=${ACGS_DB_PASSWORD}
POSTGRESQL_POOL_SIZE=20
POSTGRESQL_MAX_OVERFLOW=10

# Redis Configuration (ACGS Redis)
REDIS_HOST=localhost
REDIS_PORT=6389
REDIS_DB=3
REDIS_PASSWORD=${ACGS_REDIS_PASSWORD}
REDIS_POOL_SIZE=20

# Service Integration
AUTH_SERVICE_URL=http://localhost:8016
CONTEXT_SERVICE_URL=http://localhost:8012
SERVICE_REGISTRY_URL=http://localhost:8001/registry

# Constitutional Compliance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
AUDIT_ENABLED=true
COMPLIANCE_STRICT_MODE=true

# Performance Configuration
CACHE_TTL_DEFAULT=1800
EMBEDDING_BATCH_SIZE=32
MAX_CONCURRENT_REQUESTS=100
REQUEST_TIMEOUT_SECONDS=30

# Monitoring
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=9091
LOG_LEVEL=INFO
STRUCTURED_LOGGING=true

# Code Analysis Configuration
WATCH_PATHS=/home/dislove/ACGS-2
EMBEDDING_MODEL=microsoft/codebert-base

# Security
ALLOWED_ORIGINS=https://acgs.ai,https://dashboard.acgs.ai
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=1000
EOF
```

#### Step 3: Create Docker Compose Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  acgs-code-analysis:
    image: acgs/code-analysis-engine:latest
    container_name: acgs-code-analysis-engine
    restart: unless-stopped
    ports:
      - "8007:8007"
      - "9091:9091"  # Prometheus metrics
    environment:
      - ENV_FILE=/app/config/config/environments/development.env
    env_file:
      - ./config/config/environments/development.env
    volumes:
      - ./config:/app/config:ro
      - ./logs:/app/logs
      - ./data:/app/data
      - /home/dislove/ACGS-2:/workspace:ro  # Mount ACGS codebase
    networks:
      - acgs-network
    depends_on:
      - postgresql
      - redis
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8007/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
        reservations:
          memory: 1G
          cpus: '1.0'

  # PostgreSQL (if not using existing ACGS instance)
  postgresql:
    image: pgvector/pgvector:pg15
    container_name: acgs-postgresql
    restart: unless-stopped
    ports:
      - "5439:5432"
    environment:
      POSTGRES_DB: acgs
      POSTGRES_USER: acgs_code_analysis_user
      POSTGRES_PASSWORD: ${ACGS_DB_PASSWORD}
    volumes:
      - postgresql_data:/var/lib/postgresql/data
      - ./database/migrations:/docker-entrypoint-initdb.d:ro
    networks:
      - acgs-network

  # Redis (if not using existing ACGS instance)
  redis:
    image: redis:7-alpine
    container_name: acgs-redis
    restart: unless-stopped
    ports:
      - "6389:6379"
    command: redis-server --requirepass ${ACGS_REDIS_PASSWORD} --maxmemory 1gb --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
    networks:
      - acgs-network

networks:
  acgs-network:
    driver: bridge

volumes:
  postgresql_data:
  redis_data:
```

#### Step 4: Deploy with Docker Compose

```bash
# Set required environment variables
export ACGS_DB_PASSWORD="your_secure_db_password"
export ACGS_REDIS_PASSWORD="your_secure_redis_password"

# Pull latest images
docker-compose pull

# Start services
docker-compose up -d

# Verify deployment
docker-compose ps
docker-compose logs acgs-code-analysis

# Check health
curl http://localhost:8007/health
```

### Method 2: Kubernetes Deployment

#### Step 1: Create Namespace and Secrets

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: acgs-code-analysis
  labels:
    app.kubernetes.io/name: acgs-code-analysis
    app.kubernetes.io/part-of: acgs
---
# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: acgs-code-analysis-secrets
  namespace: acgs-code-analysis
type: Opaque
stringData:
  postgresql-password: "your_secure_db_password"
  redis-password: "your_secure_redis_password"
  jwt-secret: "your_jwt_secret"
```

#### Step 2: Create ConfigMap

```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: acgs-code-analysis-config
  namespace: acgs-code-analysis
data:
  config/environments/development.env: |
    ENVIRONMENT=production
    ACGS_CODE_ANALYSIS_HOST=0.0.0.0
    ACGS_CODE_ANALYSIS_PORT=8007
    ACGS_CODE_ANALYSIS_WORKERS=4

    POSTGRESQL_HOST=acgs-postgresql
    POSTGRESQL_PORT=5439
    POSTGRESQL_DATABASE=acgs
    POSTGRESQL_USER=acgs_code_analysis_user

    REDIS_HOST=acgs-redis
    REDIS_PORT=6389
    REDIS_DB=3

    AUTH_SERVICE_URL=http://acgs-auth-service:8016
    CONTEXT_SERVICE_URL=http://acgs-context-service:8012

    CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
    AUDIT_ENABLED=true
    COMPLIANCE_STRICT_MODE=true

    PROMETHEUS_ENABLED=true
    LOG_LEVEL=INFO
    STRUCTURED_LOGGING=true

    WATCH_PATHS=/workspace
    EMBEDDING_MODEL=microsoft/codebert-base
```

#### Step 3: Create Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: acgs-code-analysis-engine
  namespace: acgs-code-analysis
  labels:
    app.kubernetes.io/name: acgs-code-analysis-engine
    app.kubernetes.io/version: "1.0.0"
    app.kubernetes.io/component: api
    app.kubernetes.io/part-of: acgs
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app.kubernetes.io/name: acgs-code-analysis-engine
  template:
    metadata:
      labels:
        app.kubernetes.io/name: acgs-code-analysis-engine
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "9091"
        prometheus.io/path: "/metrics"
    spec:
      serviceAccountName: acgs-code-analysis
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      containers:
      - name: code-analysis-engine
        image: acgs/code-analysis-engine:1.0.0
        imagePullPolicy: IfNotPresent
        ports:
        - name: http
          containerPort: 8007
          protocol: TCP
        - name: metrics
          containerPort: 9091
          protocol: TCP
        env:
        - name: POSTGRESQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: acgs-code-analysis-secrets
              key: postgresql-password
        - name: REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: acgs-code-analysis-secrets
              key: redis-password
        envFrom:
        - configMapRef:
            name: acgs-code-analysis-config
        volumeMounts:
        - name: workspace
          mountPath: /workspace
          readOnly: true
        - name: config
          mountPath: /app/config
          readOnly: true
        - name: logs
          mountPath: /app/logs
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        startupProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 30
      volumes:
      - name: workspace
        hostPath:
          path: /home/dislove/ACGS-2
          type: Directory
      - name: config
        configMap:
          name: acgs-code-analysis-config
      - name: logs
        emptyDir: {}
      nodeSelector:
        kubernetes.io/os: linux
      tolerations:
      - key: "acgs.ai/code-analysis"
        operator: "Equal"
        value: "true"
        effect: "NoSchedule"
```

#### Step 4: Create Service and Ingress

```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: acgs-code-analysis-service
  namespace: acgs-code-analysis
  labels:
    app.kubernetes.io/name: acgs-code-analysis-engine
spec:
  type: ClusterIP
  ports:
  - name: http
    port: 8007
    targetPort: http
    protocol: TCP
  - name: metrics
    port: 9091
    targetPort: metrics
    protocol: TCP
  selector:
    app.kubernetes.io/name: acgs-code-analysis-engine

## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: acgs-code-analysis-ingress
  namespace: acgs-code-analysis
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "1000"
    nginx.ingress.kubernetes.io/rate-limit-window: "1m"
spec:
  tls:
  - hosts:
    - api.acgs.ai
    secretName: acgs-tls-secret
  rules:
  - host: api.acgs.ai
    http:
      paths:
      - path: /code-analysis
        pathType: Prefix
        backend:
          service:
            name: acgs-code-analysis-service
            port:
              number: 8007
```

#### Step 5: Deploy to Kubernetes

```bash
# Apply configurations
kubectl apply -f namespace.yaml
kubectl apply -f secrets.yaml
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# Verify deployment
kubectl get pods -n acgs-code-analysis
kubectl get services -n acgs-code-analysis
kubectl logs -n acgs-code-analysis deployment/acgs-code-analysis-engine

# Check health
kubectl port-forward -n acgs-code-analysis service/acgs-code-analysis-service 8007:8007
curl http://localhost:8007/health
```

## Database Setup

### PostgreSQL Configuration

```sql
-- Connect to PostgreSQL as superuser
psql -h localhost -p 5439 -U postgres

-- Create database and user
CREATE DATABASE acgs;
CREATE USER acgs_code_analysis_user WITH PASSWORD 'your_secure_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE acgs TO acgs_code_analysis_user;

-- Connect to acgs database
\c acgs

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "vector";

-- Grant schema permissions
GRANT USAGE ON SCHEMA public TO acgs_code_analysis_user;
GRANT CREATE ON SCHEMA public TO acgs_code_analysis_user;
```

### Database Migration

```bash
# Run database migrations
cd /opt/acgs/code-analysis

# Using Docker
docker-compose exec acgs-code-analysis python -m alembic upgrade head

# Using Kubernetes
kubectl exec -n acgs-code-analysis deployment/acgs-code-analysis-engine -- python -m alembic upgrade head

# Verify schema
psql -h localhost -p 5439 -U acgs_code_analysis_user -d acgs -c "\dt code_analysis.*"
```

## Monitoring and Observability

### Prometheus Metrics

```yaml
# prometheus-config.yaml
global:
  scrape_interval: 15s

scrape_configs:
- job_name: 'acgs-code-analysis'
  static_configs:
  - targets: ['localhost:9091']
  metrics_path: '/metrics'
  scrape_interval: 15s
  scrape_timeout: 10s
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "title": "ACGS Code Analysis Engine",
    "panels": [
      {
        "title": "Request Rate",
        "targets": [
          {
            "expr": "rate(acgs_code_analysis_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time P99",
        "targets": [
          {
            "expr": "histogram_quantile(0.99, rate(acgs_code_analysis_request_duration_seconds_bucket[5m]))",
            "legendFormat": "P99 Latency"
          }
        ]
      },
      {
        "title": "Cache Hit Rate",
        "targets": [
          {
            "expr": "acgs_code_analysis_cache_hit_rate",
            "legendFormat": "Cache Hit Rate"
          }
        ]
      }
    ]
  }
}
```

### Log Aggregation

```yaml
# fluentd-config.yaml
<source>
  @type tail
  path /opt/acgs/code-analysis/logs/*.log
  pos_file /var/log/fluentd/acgs-code-analysis.log.pos
  tag acgs.code-analysis
  format json
  time_key timestamp
  time_format %Y-%m-%dT%H:%M:%S.%LZ
</source>

<match acgs.code-analysis>
  @type elasticsearch
  host elasticsearch.acgs.ai
  port 9200
  index_name acgs-code-analysis
  type_name _doc
</match>
```

## Operational Runbooks

### SOP-001: High Latency Response

**Symptoms**: P99 latency > 10ms, slow API responses

**Diagnosis Steps**:
1. Check Prometheus metrics for latency trends
2. Verify cache hit rate (should be >85%)
3. Check database connection pool status
4. Monitor CPU and memory usage
5. Review application logs for errors

**Resolution Steps**:
```bash
# Check service health
curl http://localhost:8007/health

# Check cache status
redis-cli -h localhost -p 6389 -a $REDIS_PASSWORD info stats

# Check database connections
psql -h localhost -p 5439 -U acgs_code_analysis_user -d acgs -c "
SELECT count(*) as active_connections, state
FROM pg_stat_activity
WHERE datname = 'acgs'
GROUP BY state;"

# Clear cache if corrupted
redis-cli -h localhost -p 6389 -a $REDIS_PASSWORD flushdb

# Restart service if necessary
docker-compose restart acgs-code-analysis
# OR
kubectl rollout restart deployment/acgs-code-analysis-engine -n acgs-code-analysis
```

### SOP-002: Service Unavailable

**Symptoms**: HTTP 503 errors, health check failures

**Diagnosis Steps**:
1. Check service status and logs
2. Verify database connectivity
3. Check Redis connectivity
4. Verify Auth Service integration
5. Check resource utilization

**Resolution Steps**:
```bash
# Check service status
docker-compose ps
# OR
kubectl get pods -n acgs-code-analysis

# Check logs
docker-compose logs acgs-code-analysis --tail=100
# OR
kubectl logs -n acgs-code-analysis deployment/acgs-code-analysis-engine --tail=100

# Test database connectivity
psql -h localhost -p 5439 -U acgs_code_analysis_user -d acgs -c "SELECT 1;"

# Test Redis connectivity
redis-cli -h localhost -p 6389 -a $REDIS_PASSWORD ping

# Restart services
docker-compose down && docker-compose up -d
# OR
kubectl rollout restart deployment/acgs-code-analysis-engine -n acgs-code-analysis
```

### SOP-003: High Memory Usage

**Symptoms**: Memory usage > 2GB, OOM kills

**Diagnosis Steps**:
1. Check memory metrics in Prometheus
2. Review application logs for memory leaks
3. Check embedding model memory usage
4. Monitor garbage collection patterns

**Resolution Steps**:
```bash
# Check memory usage
docker stats acgs-code-analysis-engine
# OR
kubectl top pods -n acgs-code-analysis

# Force garbage collection (if using Python debug endpoint)
curl -X POST http://localhost:8007/debug/gc

# Restart service to clear memory
docker-compose restart acgs-code-analysis
# OR
kubectl rollout restart deployment/acgs-code-analysis-engine -n acgs-code-analysis

# Scale up resources if needed (Kubernetes)
kubectl patch deployment acgs-code-analysis-engine -n acgs-code-analysis -p '
{
  "spec": {
    "template": {
      "spec": {
        "containers": [
          {
            "name": "code-analysis-engine",
            "resources": {
              "limits": {
                "memory": "4Gi"
              }
            }
          }
        ]
      }
    }
  }
}'
```

### SOP-004: Index Not Updating

**Symptoms**: New code changes not reflected in search results

**Diagnosis Steps**:
1. Check file watcher status in logs
2. Verify file system permissions
3. Check indexing job status
4. Review analysis job errors

**Resolution Steps**:
```bash
# Check file watcher logs
docker-compose logs acgs-code-analysis | grep "file_watcher"

# Trigger manual re-index
curl -X POST http://localhost:8007/api/v1/analysis/trigger \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "analysis_type": "full_scan",
    "force_reanalysis": true
  }'

# Check analysis job status
curl http://localhost:8007/api/v1/analysis/jobs \
  -H "Authorization: Bearer $AUTH_TOKEN"

# Restart file watcher
docker-compose restart acgs-code-analysis
```

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: Authentication Failures

**Error**: `401 Unauthorized` responses

**Solution**:
```bash
# Verify Auth Service connectivity
curl http://localhost:8016/health

# Check JWT token validity
curl -X POST http://localhost:8016/api/v1/auth/validate \
  -H "Authorization: Bearer $TOKEN"

# Update Auth Service URL if needed
docker-compose exec acgs-code-analysis env | grep AUTH_SERVICE_URL
```

#### Issue: Database Connection Errors

**Error**: `Connection refused` or `Too many connections`

**Solution**:
```bash
# Check PostgreSQL status
systemctl status postgresql
# OR
docker-compose ps postgresql

# Check connection limits
psql -h localhost -p 5439 -U postgres -c "SHOW max_connections;"

# Check active connections
psql -h localhost -p 5439 -U postgres -c "
SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

# Restart PostgreSQL if needed
systemctl restart postgresql
# OR
docker-compose restart postgresql
```

#### Issue: Cache Performance Problems

**Error**: Low cache hit rate, slow responses

**Solution**:
```bash
# Check Redis memory usage
redis-cli -h localhost -p 6389 -a $REDIS_PASSWORD info memory

# Check cache statistics
redis-cli -h localhost -p 6389 -a $REDIS_PASSWORD info stats

# Optimize cache configuration
redis-cli -h localhost -p 6389 -a $REDIS_PASSWORD config set maxmemory-policy allkeys-lru

# Clear and rebuild cache
redis-cli -h localhost -p 6389 -a $REDIS_PASSWORD flushdb
```

### Performance Optimization

#### Database Optimization

```sql
-- Analyze table statistics
ANALYZE code_analysis.code_symbols;
ANALYZE code_analysis.code_dependencies;
ANALYZE code_analysis.code_embeddings;

-- Check index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'code_analysis'
ORDER BY idx_scan DESC;

-- Optimize slow queries
EXPLAIN ANALYZE SELECT * FROM code_analysis.code_symbols
WHERE symbol_name ILIKE '%auth%' LIMIT 10;
```

#### Cache Optimization

```bash
# Monitor cache hit ratio
redis-cli -h localhost -p 6389 -a $REDIS_PASSWORD info stats | grep hit_rate

# Optimize memory usage
redis-cli -h localhost -p 6389 -a $REDIS_PASSWORD config set maxmemory 2gb
redis-cli -h localhost -p 6389 -a $REDIS_PASSWORD config set maxmemory-policy allkeys-lru

# Monitor key expiration
redis-cli -h localhost -p 6389 -a $REDIS_PASSWORD info keyspace
```

## Security Considerations

### SSL/TLS Configuration

```nginx
# nginx.conf for SSL termination
server {
    listen 443 ssl http2;
    server_name api.acgs.ai;

    ssl_certificate /etc/ssl/certs/acgs.ai.crt;
    ssl_certificate_key /etc/ssl/private/acgs.ai.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;

    location /code-analysis/ {
        proxy_pass http://localhost:8007/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Rate limiting
        limit_req zone=api burst=100 nodelay;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
    }
}
```

### Network Security

```bash
# Configure firewall rules
sudo ufw enable
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow specific services
sudo ufw allow from 10.0.0.0/8 to any port 8007  # Internal network only
sudo ufw allow from 10.0.0.0/8 to any port 5439  # PostgreSQL
sudo ufw allow from 10.0.0.0/8 to any port 6389  # Redis

# Monitor connections
sudo netstat -tulpn | grep :8007
sudo ss -tulpn | grep :8007
```

## Backup and Recovery

### Database Backup

```bash
# Create backup script
cat > /opt/acgs/scripts/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/acgs/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="acgs_code_analysis_${DATE}.sql"

mkdir -p $BACKUP_DIR

pg_dump -h localhost -p 5439 -U acgs_code_analysis_user -d acgs \
  --schema=code_analysis \
  --no-password \
  --verbose \
  --file="$BACKUP_DIR/$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_DIR/$BACKUP_FILE"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "acgs_code_analysis_*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/${BACKUP_FILE}.gz"
EOF

chmod +x /opt/acgs/scripts/backup-db.sh

# Schedule daily backups
echo "0 2 * * * /opt/acgs/scripts/backup-db.sh" | crontab -
```

### Service Recovery

```bash
# Create recovery script
cat > /opt/acgs/scripts/recover-service.sh << 'EOF'
#!/bin/bash
echo "Starting ACGS Code Analysis Engine recovery..."

# Stop service
docker-compose down

# Restore database if needed
# gunzip -c /opt/acgs/backups/latest_backup.sql.gz | psql -h localhost -p 5439 -U acgs_code_analysis_user -d acgs

# Clear cache
redis-cli -h localhost -p 6389 -a $REDIS_PASSWORD flushdb

# Start service
docker-compose up -d

# Wait for service to be ready
sleep 30

# Verify health
curl -f http://localhost:8007/health || exit 1

echo "Recovery completed successfully"
EOF

chmod +x /opt/acgs/scripts/recover-service.sh
```

## Maintenance Procedures

### Regular Maintenance Tasks

```bash
# Weekly maintenance script
cat > /opt/acgs/scripts/weekly-maintenance.sh << 'EOF'
#!/bin/bash
echo "Starting weekly maintenance..."

# Update database statistics
psql -h localhost -p 5439 -U acgs_code_analysis_user -d acgs -c "
ANALYZE code_analysis.code_symbols;
ANALYZE code_analysis.code_dependencies;
ANALYZE code_analysis.code_embeddings;"

# Clean old logs
find /opt/acgs/code-analysis/logs -name "*.log" -mtime +30 -delete

# Restart service for memory cleanup
docker-compose restart acgs-code-analysis

echo "Weekly maintenance completed"
EOF

chmod +x /opt/acgs/scripts/weekly-maintenance.sh

# Schedule weekly maintenance
echo "0 3 * * 0 /opt/acgs/scripts/weekly-maintenance.sh" | crontab -
```

### Update Procedures

```bash
# Update service to new version
cat > /opt/acgs/scripts/update-service.sh << 'EOF'
#!/bin/bash
NEW_VERSION=$1

if [ -z "$NEW_VERSION" ]; then
    echo "Usage: $0 <version>"
    exit 1
fi

echo "Updating to version $NEW_VERSION..."

# Backup current configuration
cp docker-compose.yml docker-compose.yml.backup

# Update image version
sed -i "s/acgs\/code-analysis-engine:.*/acgs\/code-analysis-engine:$NEW_VERSION/" docker-compose.yml

# Pull new image
docker-compose pull

# Rolling update
docker-compose up -d --no-deps acgs-code-analysis

# Verify health
sleep 30
curl -f http://localhost:8007/health || {
    echo "Health check failed, rolling back..."
    cp docker-compose.yml.backup docker-compose.yml
    docker-compose up -d --no-deps acgs-code-analysis
    exit 1
}

echo "Update completed successfully"
EOF

chmod +x /opt/acgs/scripts/update-service.sh
```

## Related Information

For a broader understanding of the ACGS platform and its components, refer to:

- [ACGS Service Architecture Overview](../../docs/ACGS_SERVICE_OVERVIEW.md)
- [ACGS Documentation Implementation and Maintenance Plan - Completion Report](../../docs/ACGS_DOCUMENTATION_IMPLEMENTATION_COMPLETION_REPORT.md)
- [ACGE Strategic Implementation Plan - 24 Month Roadmap](../../docs/ACGE_STRATEGIC_IMPLEMENTATION_PLAN_24_MONTH.md)
- [ACGE Testing and Validation Framework](../../docs/ACGE_TESTING_VALIDATION_FRAMEWORK.md)
- [ACGE Cost Analysis and ROI Projections](../../docs/ACGE_COST_ANALYSIS_ROI_PROJECTIONS.md)
- [ACGS Comprehensive Task Completion - Final Report](../architecture/ACGS_COMPREHENSIVE_TASK_COMPLETION_FINAL_REPORT.md)
- [ACGS-Claudia Integration Architecture Plan](../architecture/ACGS_CLAUDIA_INTEGRATION_ARCHITECTURE.md)
- [ACGS Implementation Guide](../deployment/ACGS_IMPLEMENTATION_GUIDE.md)
- [ACGS-PGP Operational Deployment Guide](../deployment/ACGS_PGP_OPERATIONAL_DEPLOYMENT_GUIDE.md)
- [ACGS-PGP Troubleshooting Guide](../deployment/ACGS_PGP_TROUBLESHOOTING_GUIDE.md)
- [ACGS-PGP Setup Guide](../deployment/ACGS_PGP_SETUP_GUIDE.md)
- [Service Status Dashboard](../operations/SERVICE_STATUS.md)
- [ACGS Configuration Guide](../configuration/README.md)
- [ACGS-2 Technical Specifications - 2025 Edition](../TECHNICAL_SPECIFICATIONS_2025.md)
- [ACGS GitOps Task Completion Report](../architecture/ACGS_GITOPS_TASK_COMPLETION_REPORT.md)
- [ACGS GitOps Comprehensive Validation Report](../architecture/ACGS_GITOPS_COMPREHENSIVE_VALIDATION_REPORT.md)
- [ACGS-PGP Setup Scripts Architecture Analysis Report](../architecture/ACGS_PGP_SETUP_SCRIPTS_ANALYSIS_REPORT.md)
- [ACGS Documentation Quality Metrics and Continuous Improvement](../DOCUMENTATION_QUALITY_METRICS.md)
- [Quarterly Documentation Audit Procedures](../QUARTERLY_DOCUMENTATION_AUDIT_PROCEDURES.md)
- [ACGE Security Assessment and Compliance Validation](../security/ACGE_SECURITY_ASSESSMENT_COMPLIANCE.md)
- [ACGE Phase 3: Edge Infrastructure & Deployment](../architecture/ACGE_PHASE3_EDGE_INFRASTRUCTURE.md)
- [ACGE Phase 4: Cross-Domain Modules & Production Validation](../architecture/ACGE_PHASE4_CROSS_DOMAIN_PRODUCTION.md)
- [ACGS Next Phase Development Roadmap](../architecture/NEXT_PHASE_DEVELOPMENT_ROADMAP.md)
- [ACGS Remaining Tasks Completion Summary](../REMAINING_TASKS_COMPLETION_SUMMARY.md)
- [GitHub Actions Systematic Fixes - Final Report](../workflow_systematic_fixes_final_report.md)
- [GitHub Actions Workflow Systematic Fixes Summary](../workflow_fixes_summary.md)
- [Security Input Validation Integration - Completion Report](../security_validation_completion_report.md)
- [Phase 2: Enhanced Production Readiness - COMPLETION REPORT](../phase2_completion_report.md)
- [Phase 1: Critical Path to Basic Production Readiness - COMPLETION REPORT](../phase1_completion_report.md)
- [Free Model Usage Guide for ACGS OpenRouter Integration](../free_model_usage.md)
- [Migration Guide: Gemini CLI to OpenCode Adapter](../deployment/MIGRATION_GUIDE_OPENCODE.md)
- [Branch Protection Guide](BRANCH_PROTECTION_GUIDE.md)
- [Workflow Transition & Deprecation Guide](WORKFLOW_TRANSITION_GUIDE.md)
