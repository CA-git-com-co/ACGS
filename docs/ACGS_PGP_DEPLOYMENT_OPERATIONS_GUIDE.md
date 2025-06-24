# ACGS-PGP Production Deployment and Operations Guide

## Executive Summary

This comprehensive guide provides step-by-step instructions for deploying and operating the ACGS-PGP (Autonomous Constitutional Governance System - Policy Generation Platform) in production environments with DGM safety patterns and constitutional AI constraints.

**System Version**: 3.0.0  
**Architecture**: 7-service microservices with constitutional compliance  
**Constitutional Hash**: `cdd01ef066bc6cf2`  
**Emergency RTO**: <30 minutes with automated rollback

## Prerequisites

### System Requirements

#### Production Environment
- **Operating System**: Ubuntu 22.04+ LTS or RHEL 9+
- **Memory**: 32GB RAM (64GB for high-load environments)
- **CPU**: 16 cores with AVX2 support (Intel Xeon or AMD EPYC)
- **Storage**: 500GB NVMe SSD with 1TB backup storage
- **Network**: Redundant 10Gbps connections
- **GPU**: Optional NVIDIA A100/H100 for AI acceleration

#### Minimum Development Environment
- **Memory**: 16GB RAM
- **CPU**: 8 cores (x86_64)
- **Storage**: 100GB SSD
- **Network**: Stable internet connection (1Gbps recommended)

### Software Dependencies

#### Core Infrastructure
```bash
# Container Runtime
Docker 24.0+ with BuildKit support
Docker Compose 2.20+

# Programming Languages
Python 3.11+ with pip and venv
Node.js 18+ with npm/pnpm
Rust 1.75+ (for blockchain components)

# Databases
PostgreSQL 14+ with extensions (uuid-ossp, pgcrypto)
Redis 7+ with persistence and clustering support

# Load Balancing & Proxy
Nginx 1.24+ or HAProxy 2.8+
Certbot for SSL certificate management

# Monitoring & Observability
Prometheus 2.45+
Grafana 10.0+
```

#### AI Model Dependencies
```bash
# AI Model APIs (Required)
Google Gemini API access
DeepSeek API access  
NVIDIA API access
OpenAI API access (fallback)

# Cryptographic Tools
OpenSSL 3.0+ for cryptographic operations
GnuPG 2.2+ for PGP operations

# Policy Engine
Open Policy Agent (OPA) 0.58+
```

## Deployment Architecture

### Service Overview

| Service | Port | Purpose | CPU Limit | Memory Limit | Health Check |
|---------|------|---------|-----------|--------------|--------------|
| **auth-service** | 8000 | Authentication & Authorization | 500m | 1Gi | `/health` |
| **ac-service** | 8001 | Constitutional AI & Compliance | 500m | 1Gi | `/health` |
| **integrity-service** | 8002 | Cryptographic Integrity & PGP | 500m | 1Gi | `/health` |
| **fv-service** | 8003 | Formal Verification & Validation | 500m | 1Gi | `/health` |
| **gs-service** | 8004 | Governance Synthesis & AI Models | 500m | 1Gi | `/health` |
| **pgc-service** | 8005 | Policy Governance & Enforcement | 500m | 1Gi | `/health` |
| **ec-service** | 8006 | Evolutionary Computation & WINA | 500m | 1Gi | `/health` |

### Infrastructure Components

| Component | Port | Purpose | Configuration |
|-----------|------|---------|---------------|
| **PostgreSQL** | 5432 | Primary database | Multi-schema, connection pooling |
| **Redis** | 6379 | Cache & sessions | Persistence, 6GB memory limit |
| **OPA** | 8181 | Policy enforcement | Required for PGC service |
| **Prometheus** | 9090 | Metrics collection | 15-day retention, 2GB storage |
| **Grafana** | 3000 | Monitoring dashboards | Pre-configured ACGS dashboards |
| **Nginx** | 80/443 | Load balancer & SSL termination | Rate limiting, SSL/TLS |

## Step-by-Step Deployment

### 1. Environment Preparation

```bash
# Clone repository
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS

# Verify repository integrity
git verify-commit HEAD

# Create deployment directory
sudo mkdir -p /opt/acgs-pgp
sudo chown $USER:$USER /opt/acgs-pgp
cp -r . /opt/acgs-pgp/
cd /opt/acgs-pgp
```

### 2. System Dependencies Installation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install core dependencies
sudo apt install -y \
  docker.io docker-compose-plugin \
  postgresql-client redis-tools \
  nginx certbot python3-certbot-nginx \
  curl wget jq htop iotop \
  python3.11 python3.11-venv python3-pip

# Setup Docker permissions
sudo usermod -aG docker $USER
newgrp docker

# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

### 3. Configuration Setup

```bash
# Copy environment template
cp .env.example .env

# Configure environment variables
nano .env
```

#### Required Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://acgs_user:secure_password@localhost:5432/acgs_main
REDIS_URL=redis://localhost:6379/0

# AI Model API Keys
GEMINI_API_KEY=your-gemini-api-key-here
DEEPSEEK_API_KEY=your-deepseek-api-key-here
NVIDIA_API_KEY=your-nvidia-api-key-here
OPENAI_API_KEY=your-openai-fallback-key-here

# Cryptographic Configuration
SECRET_KEY=your-256-bit-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Constitutional Governance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
CONSTITUTIONAL_COMPLIANCE_THRESHOLD=0.8

# Service Configuration
ENVIRONMENT=production
LOG_LEVEL=INFO
DEBUG=false

# Security Configuration
ENABLE_RATE_LIMITING=true
ENABLE_AUDIT_LOGGING=true
ENABLE_SECURITY_HEADERS=true
```

### 4. Database Initialization

```bash
# Start PostgreSQL and Redis
sudo systemctl enable postgresql redis-server
sudo systemctl start postgresql redis-server

# Create databases and users
sudo -u postgres psql << EOF
CREATE USER acgs_user WITH PASSWORD 'secure_password';
CREATE DATABASE acgs_main OWNER acgs_user;
CREATE DATABASE acgs_auth OWNER acgs_user;
CREATE DATABASE acgs_constitutional OWNER acgs_user;
CREATE DATABASE acgs_integrity OWNER acgs_user;
GRANT ALL PRIVILEGES ON DATABASE acgs_main TO acgs_user;
GRANT ALL PRIVILEGES ON DATABASE acgs_auth TO acgs_user;
GRANT ALL PRIVILEGES ON DATABASE acgs_constitutional TO acgs_user;
GRANT ALL PRIVILEGES ON DATABASE acgs_integrity TO acgs_user;
EOF

# Run database migrations
./scripts/setup/setup_databases.sh
```

### 5. SSL Certificate Setup

```bash
# Configure Nginx
sudo cp config/nginx/acgs-pgp.conf /etc/nginx/sites-available/
sudo ln -s /etc/nginx/sites-available/acgs-pgp.conf /etc/nginx/sites-enabled/
sudo nginx -t

# Obtain SSL certificates
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# Setup automatic renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 6. Service Deployment

```bash
# Install Python dependencies
uv sync --frozen

# Build and start services
./scripts/deploy.sh --environment production --validate

# Verify deployment
./scripts/comprehensive_system_validation.py

# Check service health
./scripts/health_check.sh --detailed
```

### 7. Monitoring Setup

```bash
# Start monitoring stack
docker-compose -f monitoring/docker-compose.yml up -d

# Import Grafana dashboards
./scripts/setup/import_grafana_dashboards.sh

# Configure alerting
./scripts/setup/setup_alerting.sh
```

## Operational Procedures

### Health Monitoring

#### Automated Health Checks
```bash
# Comprehensive health check
./scripts/health_check.sh

# Constitutional compliance verification
curl -s http://localhost:8001/api/v1/compliance/status | jq '.data.constitutional_hash'
# Expected: "cdd01ef066bc6cf2"

# Service-specific health checks
for port in 8000 8001 8002 8003 8004 8005 8006; do
  echo "Port $port: $(curl -s http://localhost:$port/health | jq -r '.status // "ERROR"')"
done
```

#### Performance Monitoring
```bash
# Check response times
./scripts/performance_testing.py --quick

# Monitor resource usage
./scripts/monitor_resources.sh

# Check constitutional compliance metrics
curl -s http://localhost:8001/api/v1/fidelity/metrics | jq '.compliance_score'
```

### Emergency Procedures

#### Emergency Shutdown (<30min RTO)
```bash
# Immediate emergency shutdown
./scripts/emergency_rollback.py --immediate --reason "security_incident"

# Graceful emergency shutdown
./scripts/emergency_rollback.py --graceful --reason "maintenance"

# Verify shutdown
./scripts/verify_shutdown.sh
```

#### Disaster Recovery
```bash
# Create full system backup
./scripts/backup_system.py --full --encrypt

# Restore from backup
./scripts/restore_system.py --backup-id <backup_timestamp> --verify

# Validate restoration
./scripts/comprehensive_system_validation.py --post-restore
```

### Maintenance Procedures

#### Regular Maintenance
```bash
# Daily health check (automated via cron)
0 6 * * * /opt/acgs-pgp/scripts/daily_health_check.sh

# Weekly backup verification
0 2 * * 0 /opt/acgs-pgp/scripts/verify_backups.sh

# Monthly security scan
0 3 1 * * /opt/acgs-pgp/scripts/security_scan.sh
```

#### Service Updates
```bash
# Rolling update with zero downtime
./scripts/rolling_update.sh --version 3.1.0 --validate

# Canary deployment
./scripts/canary_deploy.sh --percentage 10 --monitor

# Rollback if needed
./scripts/rollback.sh --to-version 3.0.0 --immediate
```

## Security Operations

### Security Monitoring
```bash
# Security audit
./scripts/security_audit.py --comprehensive

# Check for vulnerabilities
./scripts/vulnerability_scan.sh --update-db

# Monitor constitutional violations
curl -s http://localhost:8001/api/v1/compliance/violations | jq '.data.recent_violations'
```

### Incident Response
```bash
# Security incident response
./scripts/incident_response.py --type security --severity high

# Constitutional violation response
./scripts/constitutional_incident.py --violation-id <id> --remediate

# Generate incident report
./scripts/generate_incident_report.py --incident-id <id>
```

## Troubleshooting

### Common Issues

#### PGC Service Degraded
```bash
# Check OPA status
curl http://localhost:8181/health

# Restart OPA if needed
sudo systemctl restart opa

# Verify PGC service
curl http://localhost:8005/health
```

#### Constitutional Hash Mismatch
```bash
# Verify constitutional hash
./scripts/verify_constitutional_hash.py

# Reset if corrupted
./scripts/reset_constitutional_state.py --hash cdd01ef066bc6cf2
```

#### AI Model API Failures
```bash
# Test AI model connectivity
./scripts/test_ai_models.py --all

# Check API quotas and limits
./scripts/check_api_quotas.py

# Enable fallback models
./scripts/enable_fallback_models.py
```

## Performance Optimization

### Database Optimization
```bash
# Optimize database performance
./scripts/optimize_database.py --analyze --vacuum

# Monitor query performance
./scripts/monitor_db_queries.py --slow-queries

# Setup connection pooling
./scripts/setup_pgbouncer.sh
```

### Caching Optimization
```bash
# Monitor cache hit rates
redis-cli info stats | grep hit_rate

# Optimize cache configuration
./scripts/optimize_redis.py --memory-policy allkeys-lru

# Clear cache if needed
./scripts/clear_cache.py --selective
```

## Support and Documentation

### Documentation Resources
- **API Documentation**: `/docs/api/` - Complete API specifications
- **Architecture Guide**: `/docs/architecture/` - System design documentation
- **Security Guide**: `/docs/security/` - Security procedures and policies
- **Troubleshooting**: `/docs/troubleshooting/` - Common issues and solutions

### Support Contacts
- **Emergency**: Use emergency procedures above
- **Technical Issues**: Check service logs in `/logs/`
- **Configuration**: Review `/config/` directory
- **Monitoring**: Access Grafana at `https://your-domain.com:3000`

### Logging and Diagnostics
```bash
# View service logs
tail -f /logs/auth_service.log
tail -f /logs/ac_service.log
tail -f /logs/integrity_service.log

# Aggregate logs
./scripts/aggregate_logs.py --since "1 hour ago"

# Generate diagnostic report
./scripts/generate_diagnostics.py --comprehensive
```
