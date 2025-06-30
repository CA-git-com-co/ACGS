# ACGS-2 Production Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying ACGS-2 to production. Following this guide, a new team member should be able to deploy the entire system from scratch.

## Prerequisites

### System Requirements
- Ubuntu 20.04 LTS or later
- Docker 20.10+ and Docker Compose 2.0+
- Python 3.9+
- Node.js 16+
- Redis 6.2+
- PostgreSQL 13+
- Minimum 16GB RAM, 4 CPU cores
- 100GB available disk space

### Access Requirements
- SSH access to production servers
- Docker registry access
- Database admin credentials
- SSL certificates for HTTPS

## Step 1: Infrastructure Setup

### 1.1 Server Preparation
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Python dependencies
sudo apt install python3-pip python3-venv -y
```

### 1.2 Network Configuration
```bash
# Configure firewall
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw allow 8000:8010/tcp  # Service ports
sudo ufw enable
```

## Step 2: Application Deployment

### 2.1 Clone Repository
```bash
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS-2
```

### 2.2 Environment Configuration
```bash
# Copy environment template
cp .env.example .env.production

# Edit environment variables (see Configuration Reference)
nano .env.production
```

### 2.3 Security Setup
```bash
# Run security validation integration
python3 scripts/security/integrate_input_validation.py

# Verify security configuration
python3 scripts/security/external_security_audit.py
```

### 2.4 Database Setup
```bash
# Initialize database
docker-compose -f docker-compose.production.yml up -d postgres
python3 scripts/database/initialize_production_db.py

# Run migrations
python3 scripts/database/run_migrations.py
```

### 2.5 Cache Setup
```bash
# Deploy optimized cache configuration
python3 scripts/cache/optimize_cache_performance.py

# Start Redis with optimized configuration
docker-compose -f docker-compose.production.yml up -d redis
```

### 2.6 Service Deployment
```bash
# Build and deploy all services
docker-compose -f docker-compose.production.yml build
docker-compose -f docker-compose.production.yml up -d

# Verify service health
python3 scripts/monitoring/setup_basic_monitoring.py
```

## Step 3: Monitoring Setup

### 3.1 Deploy Monitoring Infrastructure
```bash
# Start monitoring services
./scripts/monitoring/start_monitoring.sh

# Verify monitoring endpoints
curl http://localhost:9090  # Prometheus
curl http://localhost:3000  # Grafana
```

### 3.2 Configure Alerts
```bash
# Test alert system
python3 scripts/monitoring/test_alerts.py
```

## Step 4: Verification

### 4.1 Health Checks
```bash
# Run comprehensive health check
python3 scripts/health/production_health_check.py
```

### 4.2 Security Validation
```bash
# Run security audit
python3 scripts/security/external_security_audit.py
```

### 4.3 Performance Testing
```bash
# Run performance tests
python3 -m pytest tests/performance/ -v
```

## Step 5: Go-Live Checklist

- [ ] All services healthy and responding
- [ ] Security audit passed (no critical/high vulnerabilities)
- [ ] Monitoring and alerting functional
- [ ] Backup procedures tested
- [ ] SSL certificates installed and valid
- [ ] DNS records configured
- [ ] Load balancer configured
- [ ] Incident response procedures documented

## Troubleshooting

See [Troubleshooting Guide](operations/troubleshooting_guide.md) for common issues and solutions.

## Support

For deployment support, contact the ACGS-2 team or refer to the operational runbook.
