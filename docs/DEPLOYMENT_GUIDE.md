# ACGS-2 Deployment Guide

This guide covers deployment strategies for ACGS-2 across different environments.

## Prerequisites

### System Requirements
- **CPU**: 8+ cores (16+ recommended for production)
- **Memory**: 16GB+ RAM (32GB+ recommended for production)
- **Storage**: 100GB+ SSD storage
- **Network**: High-speed internet connection

### Software Dependencies
- **Docker**: 20.10+ with Docker Compose
- **Python**: 3.10+ (if running without containers)
- **PostgreSQL**: 13+ (or managed database service)
- **Redis**: 6.0+ (or managed cache service)
- **Nginx**: 1.20+ (for reverse proxy)

## Environment Setup

### Development Environment

#### Local Development
```bash
# Clone repository
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS-2

# Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-test.txt

# Configure environment
cp config/test.env .env
# Edit .env with your configuration

# Start dependencies
docker-compose -f docker-compose.dev.yml up -d postgres redis

# Run services
python scripts/start_development_services.py
```

#### Docker Development
```bash
# Build and start all services
docker-compose -f docker-compose.dev.yml up --build

# Start specific services
docker-compose -f docker-compose.dev.yml up constitutional_ai policy_governance

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

### Staging Environment

#### Docker Compose Staging
```bash
# Create staging environment file
cp config/staging.env .env.staging

# Deploy staging stack
docker-compose -f docker-compose.staging.yml up -d

# Run health checks
python scripts/validate_service_startup.py --env staging

# Run integration tests
python scripts/test_runner.py --type integration --env staging
```

### Production Environment

#### Container Orchestration (Kubernetes)

**Prerequisites:**
- Kubernetes cluster (1.20+)
- kubectl configured
- Helm 3.0+

```bash
# Add ACGS Helm repository
helm repo add acgs https://charts.acgs.ai
helm repo update

# Create namespace
kubectl create namespace acgs-production

# Install ACGS
helm install acgs-prod acgs/acgs \
  --namespace acgs-production \
  --values production-values.yaml

# Verify deployment
kubectl get pods -n acgs-production
kubectl get services -n acgs-production
```

**Production Values (production-values.yaml):**
```yaml
global:
  environment: production
  imageTag: "v2.0.0"
  
database:
  host: "postgres.acgs.internal"
  port: 5432
  name: "acgs_production"
  
redis:
  host: "redis.acgs.internal"
  port: 6379
  
services:
  constitutional_ai:
    replicas: 3
    resources:
      requests:
        cpu: "500m"
        memory: "1Gi"
      limits:
        cpu: "2000m"
        memory: "4Gi"
        
  policy_governance:
    replicas: 3
    resources:
      requests:
        cpu: "500m"
        memory: "1Gi"
      limits:
        cpu: "2000m"
        memory: "4Gi"

ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: api.acgs.ai
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: acgs-tls
      hosts:
        - api.acgs.ai
```

#### Cloud Deployment (AWS)

**Using AWS ECS:**
```bash
# Build and push images
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com

# Build images
docker build -t acgs/constitutional-ai:latest services/core/constitutional_ai/
docker tag acgs/constitutional-ai:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/acgs/constitutional-ai:latest
docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/acgs/constitutional-ai:latest

# Deploy using CloudFormation or Terraform
terraform init
terraform plan -var-file="production.tfvars"
terraform apply
```

**Using AWS Lambda (Serverless):**
```bash
# Install Serverless Framework
npm install -g serverless

# Deploy serverless functions
cd deployment/serverless
serverless deploy --stage production
```

## Configuration Management

### Environment Variables

**Core Configuration:**
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/acgs_db
REDIS_URL=redis://localhost:6379/0

# API Keys
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GOOGLE_API_KEY=your_google_key

# Security
JWT_SECRET_KEY=your_jwt_secret
ENCRYPTION_KEY=your_encryption_key

# Performance
CACHE_TTL=3600
MAX_WORKERS=4
REQUEST_TIMEOUT=30

# Monitoring
PROMETHEUS_ENABLED=true
JAEGER_ENDPOINT=http://jaeger:14268/api/traces
```

### Secrets Management

**Using Kubernetes Secrets:**
```bash
# Create secrets
kubectl create secret generic acgs-secrets \
  --from-literal=database-password=secure_password \
  --from-literal=jwt-secret=jwt_secret_key \
  --namespace acgs-production

# Use in deployment
apiVersion: apps/v1
kind: Deployment
spec:
  template:
    spec:
      containers:
      - name: constitutional-ai
        env:
        - name: DATABASE_PASSWORD
          valueFrom:
            secretKeyRef:
              name: acgs-secrets
              key: database-password
```

**Using AWS Secrets Manager:**
```python
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-west-2')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

# Usage in application
database_password = get_secret('acgs/database/password')
```

## Database Setup

### PostgreSQL Setup
```sql
-- Create database and user
CREATE DATABASE acgs_production;
CREATE USER acgs_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE acgs_production TO acgs_user;

-- Create extensions
\c acgs_production;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

### Database Migrations
```bash
# Run migrations
python -m alembic upgrade head

# Create new migration
python -m alembic revision --autogenerate -m "Add new table"

# Rollback migration
python -m alembic downgrade -1
```

## Monitoring and Observability

### Prometheus Metrics
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'acgs-services'
    static_configs:
      - targets: ['constitutional-ai:8002', 'policy-governance:8010']
    metrics_path: '/metrics'
```

### Grafana Dashboards
```bash
# Import ACGS dashboards
curl -X POST \
  http://grafana:3000/api/dashboards/db \
  -H 'Content-Type: application/json' \
  -d @monitoring/grafana/acgs-dashboard.json
```

### Log Aggregation
```yaml
# fluentd configuration
<source>
  @type tail
  path /var/log/acgs/*.log
  pos_file /var/log/fluentd/acgs.log.pos
  tag acgs.*
  format json
</source>

<match acgs.**>
  @type elasticsearch
  host elasticsearch
  port 9200
  index_name acgs-logs
</match>
```

## Security Considerations

### Network Security
- Use TLS 1.3 for all external communications
- Implement network segmentation
- Configure firewalls and security groups
- Use VPN for administrative access

### Application Security
- Enable authentication for all endpoints
- Implement rate limiting
- Use input validation and sanitization
- Regular security scanning with tools like Bandit

### Data Security
- Encrypt data at rest and in transit
- Implement proper key management
- Regular backup and recovery testing
- Audit logging for all operations

## Performance Optimization

### Caching Strategy
```python
# Redis caching configuration
CACHE_CONFIG = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        }
    }
}
```

### Database Optimization
```sql
-- Create indexes for performance
CREATE INDEX CONCURRENTLY idx_policy_rules_action ON policy_rules(action);
CREATE INDEX CONCURRENTLY idx_constitutional_validations_hash ON constitutional_validations(constitutional_hash);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM policy_rules WHERE action = 'read';
```

### Load Balancing
```nginx
# nginx.conf
upstream acgs_backend {
    least_conn;
    server constitutional-ai-1:8002 weight=3;
    server constitutional-ai-2:8002 weight=3;
    server constitutional-ai-3:8002 weight=2;
}

server {
    listen 80;
    server_name api.acgs.ai;
    
    location / {
        proxy_pass http://acgs_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Backup and Recovery

### Database Backup
```bash
# Automated backup script
#!/bin/bash
BACKUP_DIR="/backups/postgresql"
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump -h postgres -U acgs_user acgs_production > $BACKUP_DIR/acgs_backup_$DATE.sql
gzip $BACKUP_DIR/acgs_backup_$DATE.sql

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

### Disaster Recovery
```bash
# Recovery procedure
# 1. Restore database
gunzip -c /backups/postgresql/acgs_backup_20240101_120000.sql.gz | psql -h postgres -U acgs_user acgs_production

# 2. Restart services
kubectl rollout restart deployment/constitutional-ai -n acgs-production
kubectl rollout restart deployment/policy-governance -n acgs-production

# 3. Verify system health
python scripts/validate_service_startup.py --env production
```

## Troubleshooting

### Common Issues

**Service Won't Start:**
```bash
# Check logs
kubectl logs -f deployment/constitutional-ai -n acgs-production

# Check configuration
kubectl describe configmap acgs-config -n acgs-production

# Verify secrets
kubectl get secrets -n acgs-production
```

**Database Connection Issues:**
```bash
# Test database connectivity
psql -h postgres -U acgs_user -d acgs_production -c "SELECT 1;"

# Check connection pool
python scripts/database_performance_analysis.py
```

**Performance Issues:**
```bash
# Monitor resource usage
kubectl top pods -n acgs-production

# Check cache hit rates
python scripts/cache_monitor.py

# Analyze slow queries
python scripts/database_query_optimization.py
```

For additional support, consult the troubleshooting section in the main README or contact the ACGS support team.
