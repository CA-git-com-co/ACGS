# ACGS-1 Lite Production Deployment Guide

**Constitutional Hash:** `cdd01ef066bc6cf2`  
**Version:** 1.0.0  
**Target Audience:** DevOps Engineers, Site Reliability Engineers

## 🎯 Overview

This guide provides step-by-step instructions for deploying ACGS-1 Lite in production environments. It covers everything from infrastructure setup to monitoring configuration and operational procedures.

## 📋 Prerequisites

### Infrastructure Requirements

#### Minimum Hardware Requirements
```
Production Environment:
- CPU: 8 cores (16 recommended)
- RAM: 16GB (32GB recommended)
- Storage: 100GB SSD (500GB recommended)
- Network: 1Gbps
- Architecture: x86_64 or ARM64

Development Environment:
- CPU: 4 cores
- RAM: 8GB
- Storage: 50GB SSD
- Network: 100Mbps
```

#### Software Requirements
```bash
# Container Runtime
Docker Engine: 20.10+
Docker Compose: 2.0+

# Operating System (Recommended)
Ubuntu 22.04 LTS
CentOS Stream 9
Red Hat Enterprise Linux 9

# Network Requirements
- Outbound HTTPS (443) for container images
- Inbound access to service ports (8001-8004)
- Internal service communication
- Database access (PostgreSQL, Redis)
```

## 🏗️ Infrastructure Setup

### 1. Operating System Configuration

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y curl wget git unzip jq

# Configure system limits
sudo tee -a /etc/security/limits.conf << EOF
* soft nofile 65536
* hard nofile 65536
* soft nproc 4096
* hard nproc 4096
EOF

# Configure sysctl for performance
sudo tee -a /etc/sysctl.d/99-acgs.conf << EOF
# Network performance
net.core.rmem_default = 262144
net.core.rmem_max = 16777216
net.core.wmem_default = 262144
net.core.wmem_max = 16777216

# File handle limits
fs.file-max = 2097152

# Container networking
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward = 1
EOF

sudo sysctl --system
```

### 2. Docker Installation

```bash
# Add Docker repository
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Configure Docker daemon
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "storage-driver": "overlay2",
  "live-restore": true,
  "userland-proxy": false,
  "experimental": false
}
EOF

# Start and enable Docker
sudo systemctl enable docker
sudo systemctl start docker

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker
```

### 3. Network Configuration

```bash
# Create dedicated network for ACGS
docker network create acgs-network \
  --driver bridge \
  --subnet=172.20.0.0/16 \
  --ip-range=172.20.1.0/24

# Configure firewall (UFW)
sudo ufw allow ssh
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8001:8004/tcp  # ACGS services
sudo ufw allow 9090/tcp  # Prometheus
sudo ufw allow 3000/tcp  # Grafana
sudo ufw --force enable
```

## 📦 Application Deployment

### 1. Clone and Prepare Repository

```bash
# Clone repository
git clone <repository-url> /opt/acgs
cd /opt/acgs/services

# Set correct permissions
sudo chown -R $USER:$USER /opt/acgs
chmod +x */deploy.sh
chmod +x */build.sh
chmod +x */test.sh

# Create data directories
sudo mkdir -p /var/lib/acgs/{postgres,redis,prometheus,grafana,audit-data}
sudo chown -R $USER:$USER /var/lib/acgs
```

### 2. Configuration Management

```bash
# Create production configuration
mkdir -p /opt/acgs/config/production

# Environment configuration
cat > /opt/acgs/config/production/.env << EOF
# ACGS-1 Lite Production Configuration
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false

# Service URLs (internal)
POLICY_ENGINE_URL=http://policy-engine:8004
EVOLUTION_OVERSIGHT_URL=http://evolution-oversight:8002
AUDIT_ENGINE_URL=http://audit-engine:8003
SANDBOX_CONTROLLER_URL=http://sandbox-controller:8001

# Database Configuration
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=acgs_audit
POSTGRES_USER=acgs
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-$(openssl rand -base64 32)}

# Redis Configuration
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=${REDIS_PASSWORD:-$(openssl rand -base64 32)}

# S3 Configuration (MinIO)
S3_ENDPOINT=http://minio:9000
S3_BUCKET=acgs-audit-data
S3_ACCESS_KEY=${S3_ACCESS_KEY:-acgs-admin}
S3_SECRET_KEY=${S3_SECRET_KEY:-$(openssl rand -base64 32)}

# Performance Configuration
PERFORMANCE_TARGET_P99_MS=1.0
CACHE_TTL_SECONDS=300
MAX_CONCURRENT_REQUESTS=1000
BATCH_SIZE=10
BATCH_WINDOW_MS=5

# Security Configuration
JWT_SECRET_KEY=${JWT_SECRET_KEY:-$(openssl rand -base64 64)}
ADMIN_API_KEY=${ADMIN_API_KEY:-$(openssl rand -base64 32)}
ENCRYPTION_KEY=${ENCRYPTION_KEY:-$(openssl rand -base64 32)}

# Monitoring Configuration
PROMETHEUS_RETENTION=30d
GRAFANA_ADMIN_PASSWORD=${GRAFANA_ADMIN_PASSWORD:-$(openssl rand -base64 16)}

# TLS Configuration
TLS_CERT_PATH=/etc/ssl/certs/acgs.crt
TLS_KEY_PATH=/etc/ssl/private/acgs.key
EOF

# Make environment file secure
chmod 600 /opt/acgs/config/production/.env
```

### 3. TLS Certificate Setup

```bash
# Option 1: Self-signed certificates (development/testing)
sudo mkdir -p /etc/ssl/private
sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/ssl/private/acgs.key \
  -out /etc/ssl/certs/acgs.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=acgs.local"

# Option 2: Let's Encrypt (production)
sudo snap install --classic certbot
sudo certbot certonly --standalone -d your-domain.com
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /etc/ssl/certs/acgs.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /etc/ssl/private/acgs.key

# Set permissions
sudo chmod 644 /etc/ssl/certs/acgs.crt
sudo chmod 600 /etc/ssl/private/acgs.key
```

### 4. Production Docker Compose

```bash
# Create production docker-compose.yml
cat > /opt/acgs/services/docker-compose.prod.yml << 'EOF'
version: '3.8'

services:
  # Core ACGS Services
  policy-engine:
    build: ./core/opa-policies
    image: acgs/policy-engine:1.0.0
    container_name: acgs-policy-engine
    restart: unless-stopped
    ports:
      - "8004:8004"
    environment:
      - CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
      - REDIS_URL=redis://redis:6379
      - PROMETHEUS_METRICS=true
    volumes:
      - /var/lib/acgs/policy-cache:/app/cache
    networks:
      - acgs-network
    depends_on:
      - redis
    deploy:
      resources:
        limits:
          memory: 500M
          cpus: '1.0'
        reservations:
          memory: 300M
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8004/v1/data/acgs/main/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  evolution-oversight:
    build: ./core/evolutionary-computation
    image: acgs/evolution-oversight:1.0.0
    container_name: acgs-evolution-oversight
    restart: unless-stopped
    ports:
      - "8002:8002"
    environment:
      - CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
      - POSTGRES_URL=postgresql://acgs:${POSTGRES_PASSWORD}@postgres:5432/acgs_audit
    networks:
      - acgs-network
    depends_on:
      - postgres
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '2.0'
        reservations:
          memory: 512M
          cpus: '1.0'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  audit-engine:
    build: ./core/audit-engine
    image: acgs/audit-engine:1.0.0
    container_name: acgs-audit-engine
    restart: unless-stopped
    ports:
      - "8003:8003"
    environment:
      - CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
      - POSTGRES_URL=postgresql://acgs:${POSTGRES_PASSWORD}@postgres:5432/acgs_audit
      - REDPANDA_BROKERS=redpanda:9092
      - S3_ENDPOINT=http://minio:9000
      - S3_BUCKET=acgs-audit-data
    volumes:
      - /var/lib/acgs/audit-data:/app/data
    networks:
      - acgs-network
    depends_on:
      - postgres
      - redpanda
      - minio
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '2.0'
        reservations:
          memory: 512M
          cpus: '1.0'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8003/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  sandbox-controller:
    build: ./core/sandbox-controller/hardened
    image: acgs/sandbox-controller:1.0.0
    container_name: acgs-sandbox-controller
    restart: unless-stopped
    privileged: true
    ports:
      - "8001:8001"
    environment:
      - CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
      - DEFAULT_RUNTIME=gvisor
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - /var/lib/acgs/sandbox-data:/app/data
    networks:
      - acgs-network
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '4.0'
        reservations:
          memory: 1G
          cpus: '2.0'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8001/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Infrastructure Services
  postgres:
    image: postgres:15
    container_name: acgs-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: acgs_audit
      POSTGRES_USER: acgs
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_INITDB_ARGS: "--auth-host=scram-sha-256"
    volumes:
      - /var/lib/acgs/postgres:/var/lib/postgresql/data
      - ./config/postgres/postgresql.conf:/etc/postgresql/postgresql.conf
    networks:
      - acgs-network
    ports:
      - "5432:5432"
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
        reservations:
          memory: 1G
          cpus: '1.0'
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U acgs -d acgs_audit"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: acgs-redis
    restart: unless-stopped
    command: >
      redis-server
      --requirepass ${REDIS_PASSWORD}
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
      --save 900 1
      --save 300 10
      --save 60 10000
    volumes:
      - /var/lib/acgs/redis:/data
    networks:
      - acgs-network
    ports:
      - "6379:6379"
    deploy:
      resources:
        limits:
          memory: 768M
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "redis-cli", "--raw", "incr", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  redpanda:
    image: vectorized/redpanda:v23.2.8
    container_name: acgs-redpanda
    restart: unless-stopped
    command:
      - redpanda
      - start
      - --smp
      - "1"
      - --reserve-memory
      - "0M"
      - --overprovisioned
      - --node-id
      - "0"
      - --kafka-addr
      - "PLAINTEXT://0.0.0.0:29092,OUTSIDE://0.0.0.0:9092"
      - --advertise-kafka-addr
      - "PLAINTEXT://redpanda:29092,OUTSIDE://localhost:9092"
    volumes:
      - /var/lib/acgs/redpanda:/var/lib/redpanda/data
    networks:
      - acgs-network
    ports:
      - "9092:9092"
      - "29092:29092"
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'

  minio:
    image: minio/minio:latest
    container_name: acgs-minio
    restart: unless-stopped
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: ${S3_ACCESS_KEY}
      MINIO_ROOT_PASSWORD: ${S3_SECRET_KEY}
    volumes:
      - /var/lib/acgs/minio:/data
    networks:
      - acgs-network
    ports:
      - "9000:9000"
      - "9001:9001"
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '1.0'
        reservations:
          memory: 256M
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Monitoring Services
  prometheus:
    image: prom/prometheus:v2.47.0
    container_name: acgs-prometheus
    restart: unless-stopped
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    volumes:
      - /var/lib/acgs/prometheus:/prometheus
      - ./config/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
    networks:
      - acgs-network
    ports:
      - "9090:9090"
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'

  grafana:
    image: grafana/grafana:10.1.0
    container_name: acgs-grafana
    restart: unless-stopped
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_ADMIN_PASSWORD}
      GF_USERS_ALLOW_SIGN_UP: false
      GF_USERS_DEFAULT_THEME: dark
      GF_ANALYTICS_REPORTING_ENABLED: false
      GF_ANALYTICS_CHECK_FOR_UPDATES: false
    volumes:
      - /var/lib/acgs/grafana:/var/lib/grafana
      - ./config/grafana/provisioning:/etc/grafana/provisioning
    networks:
      - acgs-network
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'

  # Load Balancer
  nginx:
    image: nginx:1.25-alpine
    container_name: acgs-nginx
    restart: unless-stopped
    volumes:
      - ./config/nginx/nginx.conf:/etc/nginx/nginx.conf
      - /etc/ssl/certs/acgs.crt:/etc/ssl/certs/acgs.crt
      - /etc/ssl/private/acgs.key:/etc/ssl/private/acgs.key
    networks:
      - acgs-network
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - policy-engine
      - evolution-oversight
      - audit-engine
      - sandbox-controller
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.5'
        reservations:
          memory: 128M
          cpus: '0.25'

networks:
  acgs-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16

volumes:
  postgres-data:
  redis-data:
  redpanda-data:
  minio-data:
  prometheus-data:
  grafana-data:
EOF
```

### 5. Configuration Files

```bash
# Create configuration directories
mkdir -p /opt/acgs/services/config/{nginx,prometheus,grafana/provisioning/{dashboards,datasources}}

# Nginx configuration
cat > /opt/acgs/services/config/nginx/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream policy_engine {
        server policy-engine:8004 weight=3 max_fails=3 fail_timeout=30s;
    }
    
    upstream evolution_oversight {
        server evolution-oversight:8002 weight=2 max_fails=3 fail_timeout=30s;
    }
    
    upstream audit_engine {
        server audit-engine:8003 weight=2 max_fails=3 fail_timeout=30s;
    }
    
    upstream sandbox_controller {
        server sandbox-controller:8001 weight=1 max_fails=3 fail_timeout=30s;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=100r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=10r/s;

    # Redirect HTTP to HTTPS
    server {
        listen 80;
        server_name _;
        return 301 https://$host$request_uri;
    }

    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name _;

        ssl_certificate /etc/ssl/certs/acgs.crt;
        ssl_certificate_key /etc/ssl/private/acgs.key;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES128-GCM-SHA256:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=63072000" always;

        # Policy Engine
        location /v1/data/acgs/main/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://policy_engine;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_valid 200 60s;
        }

        # Evolution Oversight
        location /evolution/ {
            limit_req zone=auth burst=10 nodelay;
            proxy_pass http://evolution_oversight/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Audit Engine
        location /audit/ {
            limit_req zone=auth burst=10 nodelay;
            proxy_pass http://audit_engine/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Sandbox Controller
        location /sandbox/ {
            limit_req zone=auth burst=5 nodelay;
            proxy_pass http://sandbox_controller/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 300s;
            proxy_connect_timeout 60s;
        }

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }
}
EOF

# Prometheus configuration
cat > /opt/acgs/services/config/prometheus/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "acgs_alerts.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets: []

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'acgs-policy-engine'
    static_configs:
      - targets: ['policy-engine:8004']
    metrics_path: '/v1/metrics'
    scrape_interval: 5s

  - job_name: 'acgs-services'
    static_configs:
      - targets:
        - 'evolution-oversight:8002'
        - 'audit-engine:8003'
        - 'sandbox-controller:8001'
    metrics_path: '/metrics'
    scrape_interval: 15s

  - job_name: 'infrastructure'
    static_configs:
      - targets:
        - 'postgres:5432'
        - 'redis:6379'
        - 'redpanda:9092'
EOF
```

## 🚀 Deployment Process

### 1. Pre-deployment Validation

```bash
# Load environment variables
source /opt/acgs/config/production/.env

# Validate configuration
echo "Validating configuration..."
echo "Constitutional Hash: $CONSTITUTIONAL_HASH"
echo "Environment: $ENVIRONMENT"

# Test connectivity
ping -c 3 8.8.8.8  # Internet connectivity
docker info        # Docker daemon
docker-compose version  # Docker Compose

# Build images
cd /opt/acgs/services
docker-compose -f docker-compose.prod.yml build
```

### 2. Database Initialization

```bash
# Start database services first
docker-compose -f docker-compose.prod.yml up -d postgres redis

# Wait for databases to be ready
echo "Waiting for databases to be ready..."
timeout 60 bash -c 'until docker exec acgs-postgres pg_isready -U acgs; do sleep 2; done'
timeout 60 bash -c 'until docker exec acgs-redis redis-cli ping; do sleep 2; done'

# Run database migrations (if needed)
# docker exec acgs-postgres psql -U acgs -d acgs_audit -f /migrations/init.sql
```

### 3. Service Deployment

```bash
# Deploy all services
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
echo "Waiting for services to be healthy..."
sleep 30

# Verify service health
services=("policy-engine" "evolution-oversight" "audit-engine" "sandbox-controller")
for service in "${services[@]}"; do
    if docker-compose -f docker-compose.prod.yml ps $service | grep -q "Up (healthy)"; then
        echo "✅ $service is healthy"
    else
        echo "❌ $service is not healthy"
        docker-compose -f docker-compose.prod.yml logs $service
    fi
done
```

### 4. Post-deployment Verification

```bash
# Create verification script
cat > /opt/acgs/scripts/verify-deployment.sh << 'EOF'
#!/bin/bash

echo "🔍 ACGS-1 Lite Deployment Verification"
echo "===================================="

# Test service endpoints
echo "Testing service endpoints..."

# Policy Engine
echo -n "Policy Engine: "
if curl -s -f http://localhost:8004/v1/data/acgs/main/health > /dev/null; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

# Evolution Oversight
echo -n "Evolution Oversight: "
if curl -s -f http://localhost:8002/health > /dev/null; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

# Audit Engine
echo -n "Audit Engine: "
if curl -s -f http://localhost:8003/health > /dev/null; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

# Sandbox Controller
echo -n "Sandbox Controller: "
if curl -s -f http://localhost:8001/health > /dev/null; then
    echo "✅ OK"
else
    echo "❌ FAILED"
fi

# Test policy evaluation
echo ""
echo "Testing policy evaluation..."
response=$(curl -s -X POST http://localhost:8004/v1/data/acgs/main/decision \
  -H "Content-Type: application/json" \
  -d '{
    "type": "constitutional_evaluation",
    "constitutional_hash": "cdd01ef066bc6cf2",
    "action": "data.read_public",
    "context": {
      "environment": {"sandbox_enabled": true, "audit_enabled": true},
      "agent": {"trust_level": 0.9},
      "responsible_party": "deployment_test",
      "explanation": "Deployment verification test"
    }
  }')

if echo "$response" | jq -e '.allow == true' > /dev/null; then
    echo "✅ Policy evaluation working"
else
    echo "❌ Policy evaluation failed"
    echo "$response"
fi

echo ""
echo "Deployment verification complete!"
EOF

chmod +x /opt/acgs/scripts/verify-deployment.sh
/opt/acgs/scripts/verify-deployment.sh
```

## 📊 Monitoring Setup

### 1. Configure Alerting

```bash
# Create alert rules
cat > /opt/acgs/services/config/prometheus/acgs_alerts.yml << 'EOF'
groups:
  - name: acgs-lite-alerts
    rules:
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "ACGS service is down"
          description: "{{ $labels.instance }} has been down for more than 1 minute."

      - alert: HighLatency
        expr: acgs_latency_p99 > 0.005  # 5ms
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High latency detected"
          description: "P99 latency is {{ $value }}s, above 5ms threshold."

      - alert: LowCacheHitRate
        expr: acgs_cache_hit_rate < 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low cache hit rate"
          description: "Cache hit rate is {{ $value | humanizePercentage }}, below 90% threshold."

      - alert: ConstitutionalViolation
        expr: increase(acgs_safety_violations_total[5m]) > 10
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Multiple constitutional violations"
          description: "{{ $value }} constitutional violations in the last 5 minutes."

      - alert: DatabaseConnectionFailure
        expr: postgres_up == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection failure"
          description: "PostgreSQL database is not accessible."

      - alert: HighMemoryUsage
        expr: (container_memory_usage_bytes / container_spec_memory_limit_bytes) > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Container {{ $labels.name }} memory usage is {{ $value | humanizePercentage }}."
EOF
```

### 2. Grafana Dashboard Setup

```bash
# Create Grafana datasource
cat > /opt/acgs/services/config/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

# Create dashboard provisioning
cat > /opt/acgs/services/config/grafana/provisioning/dashboards/acgs.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'acgs'
    orgId: 1
    folder: 'ACGS'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
EOF
```

## 🔧 Operational Procedures

### 1. Backup Procedures

```bash
# Create backup script
cat > /opt/acgs/scripts/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/var/backups/acgs"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

mkdir -p $BACKUP_DIR

echo "Starting ACGS backup at $(date)"

# Database backup
echo "Backing up PostgreSQL..."
docker exec acgs-postgres pg_dump -U acgs acgs_audit | gzip > $BACKUP_DIR/postgres_$DATE.sql.gz

# Redis backup
echo "Backing up Redis..."
docker exec acgs-redis redis-cli BGSAVE
sleep 5
docker cp acgs-redis:/data/dump.rdb $BACKUP_DIR/redis_$DATE.rdb

# Configuration backup
echo "Backing up configuration..."
tar -czf $BACKUP_DIR/config_$DATE.tar.gz -C /opt/acgs config/

# Audit data backup (if using local storage)
echo "Backing up audit data..."
tar -czf $BACKUP_DIR/audit_data_$DATE.tar.gz -C /var/lib/acgs audit-data/

# Clean old backups
echo "Cleaning old backups..."
find $BACKUP_DIR -name "*.gz" -mtime +$RETENTION_DAYS -delete
find $BACKUP_DIR -name "*.rdb" -mtime +$RETENTION_DAYS -delete

echo "Backup completed at $(date)"
EOF

chmod +x /opt/acgs/scripts/backup.sh

# Schedule backups with cron
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/acgs/scripts/backup.sh >> /var/log/acgs-backup.log 2>&1") | crontab -
```

### 2. Log Management

```bash
# Configure log rotation
sudo tee /etc/logrotate.d/acgs << 'EOF'
/var/log/acgs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 acgs acgs
    postrotate
        docker-compose -f /opt/acgs/services/docker-compose.prod.yml restart nginx
    endscript
}
EOF

# Create log collection script
cat > /opt/acgs/scripts/collect-logs.sh << 'EOF'
#!/bin/bash

LOG_DIR="/var/log/acgs"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $LOG_DIR

echo "Collecting ACGS logs at $(date)"

# Collect service logs
services=("policy-engine" "evolution-oversight" "audit-engine" "sandbox-controller" "postgres" "redis")

for service in "${services[@]}"; do
    echo "Collecting logs for $service..."
    docker-compose -f /opt/acgs/services/docker-compose.prod.yml logs --tail=1000 $service > $LOG_DIR/${service}_${DATE}.log
done

# Collect system logs
journalctl -u docker.service --since "1 hour ago" > $LOG_DIR/docker_${DATE}.log

echo "Log collection completed at $(date)"
EOF

chmod +x /opt/acgs/scripts/collect-logs.sh
```

### 3. Update Procedures

```bash
# Create update script
cat > /opt/acgs/scripts/update.sh << 'EOF'
#!/bin/bash

set -e

echo "🔄 ACGS-1 Lite Update Procedure"
echo "==============================="

# Backup before update
echo "Creating backup..."
/opt/acgs/scripts/backup.sh

# Pull latest changes
echo "Pulling latest code..."
cd /opt/acgs
git fetch
git pull origin main

# Build new images
echo "Building new images..."
cd /opt/acgs/services
docker-compose -f docker-compose.prod.yml build

# Update services with rolling deployment
services=("nginx" "policy-engine" "evolution-oversight" "audit-engine" "sandbox-controller")

for service in "${services[@]}"; do
    echo "Updating $service..."
    docker-compose -f docker-compose.prod.yml up -d --no-deps $service
    
    # Wait for health check
    sleep 30
    
    if docker-compose -f docker-compose.prod.yml ps $service | grep -q "Up (healthy)"; then
        echo "✅ $service updated successfully"
    else
        echo "❌ $service update failed, rolling back..."
        docker-compose -f docker-compose.prod.yml restart $service
        exit 1
    fi
done

# Verify deployment
echo "Verifying deployment..."
/opt/acgs/scripts/verify-deployment.sh

echo "✅ Update completed successfully"
EOF

chmod +x /opt/acgs/scripts/update.sh
```

## 🚨 Troubleshooting

### Common Issues and Solutions

#### High Memory Usage
```bash
# Check memory usage
docker stats --no-stream

# Optimize JVM settings (if applicable)
# Adjust container memory limits
docker-compose -f docker-compose.prod.yml up -d --scale policy-engine=2
```

#### Database Connection Issues
```bash
# Check PostgreSQL logs
docker-compose -f docker-compose.prod.yml logs postgres

# Test connection
docker exec acgs-postgres psql -U acgs -d acgs_audit -c "SELECT version();"

# Reset connections
docker-compose -f docker-compose.prod.yml restart postgres
```

#### Performance Degradation
```bash
# Check metrics
curl http://localhost:8004/v1/metrics

# Warm cache
curl http://localhost:8004/v1/cache/warm

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale policy-engine=3
```

## 📋 Maintenance Checklist

### Daily Checks
- [ ] Service health status
- [ ] Resource utilization (CPU, memory, disk)
- [ ] Error rates and latencies
- [ ] Backup completion
- [ ] Security alerts

### Weekly Checks
- [ ] Performance trends analysis
- [ ] Log review for anomalies
- [ ] Security patch updates
- [ ] Capacity planning review
- [ ] Backup restore testing

### Monthly Checks
- [ ] Full disaster recovery test
- [ ] Security vulnerability scan
- [ ] Performance optimization review
- [ ] Documentation updates
- [ ] Certificate renewal (if needed)

---

**Constitutional Hash:** `cdd01ef066bc6cf2`  
**Deployment Guide Version:** 1.0.0  
**Last Updated:** 2024-12-28