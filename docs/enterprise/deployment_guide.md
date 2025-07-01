# ACGS Enterprise Deployment Guide

**Version:** 3.0.0  
**Date:** July 1, 2025  
**Constitutional Hash:** cdd01ef066bc6cf2  

## Overview

This guide provides comprehensive instructions for deploying the Autonomous Coding Governance System (ACGS) in enterprise environments. ACGS is a production-ready constitutional AI governance platform designed for enterprise-scale autonomous software development.

## Prerequisites

### System Requirements

**Minimum Requirements:**
- **CPU:** 8 cores (Intel Xeon or AMD EPYC)
- **Memory:** 32 GB RAM
- **Storage:** 500 GB SSD
- **Network:** 1 Gbps connection
- **OS:** Ubuntu 20.04 LTS or CentOS 8+

**Recommended for Production:**
- **CPU:** 16+ cores (Intel Xeon or AMD EPYC)
- **Memory:** 64+ GB RAM
- **Storage:** 1+ TB NVMe SSD
- **Network:** 10 Gbps connection
- **OS:** Ubuntu 22.04 LTS

### Software Dependencies

```bash
# Core dependencies
Python 3.9+
PostgreSQL 13+
Redis 6.2+
NGINX 1.20+

# Python packages (installed via requirements.txt)
fastapi>=0.104.0
uvicorn>=0.24.0
asyncpg>=0.29.0
redis>=5.0.0
cryptography>=41.0.0
```

## Installation Guide

### 1. System Preparation

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3.9 python3.9-venv python3.9-dev \
    postgresql-13 postgresql-contrib redis-server nginx \
    build-essential libssl-dev libffi-dev

# Create ACGS user
sudo useradd -m -s /bin/bash acgs
sudo usermod -aG sudo acgs
```

### 2. Database Setup

```bash
# Configure PostgreSQL
sudo -u postgres createuser acgs
sudo -u postgres createdb acgs_production
sudo -u postgres psql -c "ALTER USER acgs PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE acgs_production TO acgs;"

# Configure Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Secure Redis configuration
echo "requirepass secure_redis_password" | sudo tee -a /etc/redis/redis.conf
sudo systemctl restart redis-server
```

### 3. ACGS Application Deployment

```bash
# Switch to ACGS user
sudo su - acgs

# Clone repository
git clone https://github.com/your-org/ACGS.git
cd ACGS

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp config/production.env.example config/production.env
# Edit production.env with your configuration
```

### 4. Configuration

#### Environment Configuration (`config/production.env`)

```bash
# Database Configuration
DATABASE_URL=postgresql://acgs:secure_password@localhost:5432/acgs_production
REDIS_URL=redis://:secure_redis_password@localhost:6379/0

# Security Configuration
SECRET_KEY=your-256-bit-secret-key
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
JWT_SECRET_KEY=your-jwt-secret-key

# Service Configuration
AUTH_SERVICE_PORT=8016
AC_SERVICE_PORT=8002
PGC_SERVICE_PORT=8003
GS_SERVICE_PORT=8004
FV_SERVICE_PORT=8005
EC_SERVICE_PORT=8010

# Performance Configuration
MAX_WORKERS=4
CACHE_TTL=3600
RATE_LIMIT_PER_MINUTE=120

# Monitoring Configuration
LOG_LEVEL=INFO
METRICS_ENABLED=true
HEALTH_CHECK_INTERVAL=30
```

### 5. Service Deployment

```bash
# Initialize database schema
python scripts/init_database.py

# Start core services
./scripts/start_acgs_services.sh

# Verify services are running
./scripts/health_check.sh
```

## High Availability Configuration

### Load Balancer Setup (NGINX)

```nginx
# /etc/nginx/sites-available/acgs
upstream acgs_auth {
    server 127.0.0.1:8016;
    server 127.0.0.1:8017;
    server 127.0.0.1:8018;
}

upstream acgs_api {
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
    server 127.0.0.1:8004;
    server 127.0.0.1:8005;
    server 127.0.0.1:8010;
}

server {
    listen 80;
    server_name acgs.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name acgs.yourdomain.com;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/private.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    location /auth/ {
        proxy_pass http://acgs_auth/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/ {
        proxy_pass http://acgs_api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
```

### Database Clustering

```bash
# PostgreSQL Streaming Replication Setup
# Primary server configuration (postgresql.conf)
wal_level = replica
max_wal_senders = 3
max_replication_slots = 3
synchronous_commit = on
synchronous_standby_names = 'standby1'

# Replica server setup
pg_basebackup -h primary_server -D /var/lib/postgresql/13/main -U replication -v -P -W
```

### Redis Sentinel Configuration

```bash
# Redis Sentinel configuration
port 26379
sentinel monitor acgs-master 127.0.0.1 6379 2
sentinel auth-pass acgs-master secure_redis_password
sentinel down-after-milliseconds acgs-master 30000
sentinel parallel-syncs acgs-master 1
sentinel failover-timeout acgs-master 180000
```

## Security Configuration

### SSL/TLS Setup

```bash
# Generate SSL certificates (using Let's Encrypt)
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d acgs.yourdomain.com

# Or use your own certificates
sudo mkdir -p /etc/ssl/acgs
sudo cp your-cert.pem /etc/ssl/acgs/cert.pem
sudo cp your-private-key.pem /etc/ssl/acgs/private.key
sudo chmod 600 /etc/ssl/acgs/private.key
```

### Firewall Configuration

```bash
# Configure UFW firewall
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow from trusted_ip to any port 5432  # PostgreSQL
sudo ufw allow from trusted_ip to any port 6379  # Redis
```

### Key Management

```bash
# Generate application keys
python scripts/generate_keys.py

# Store keys securely
sudo mkdir -p /etc/acgs/keys
sudo cp keys/* /etc/acgs/keys/
sudo chmod 600 /etc/acgs/keys/*
sudo chown acgs:acgs /etc/acgs/keys/*
```

## Monitoring and Logging

### Log Configuration

```bash
# Configure log rotation
sudo tee /etc/logrotate.d/acgs << EOF
/var/log/acgs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 acgs acgs
    postrotate
        systemctl reload acgs-*
    endscript
}
EOF
```

### Health Monitoring

```bash
# Create health check script
cat > /home/acgs/scripts/health_monitor.sh << 'EOF'
#!/bin/bash
SERVICES=("auth_service:8016" "ac_service:8002" "pgc_service:8003")
ALERT_EMAIL="admin@yourdomain.com"

for service in "${SERVICES[@]}"; do
    name=${service%:*}
    port=${service#*:}
    
    if ! curl -f http://localhost:$port/health > /dev/null 2>&1; then
        echo "ALERT: $name is down" | mail -s "ACGS Service Alert" $ALERT_EMAIL
    fi
done
EOF

chmod +x /home/acgs/scripts/health_monitor.sh

# Add to crontab
echo "*/5 * * * * /home/acgs/scripts/health_monitor.sh" | crontab -
```

## Performance Tuning

### Database Optimization

```sql
-- PostgreSQL performance tuning
ALTER SYSTEM SET shared_buffers = '8GB';
ALTER SYSTEM SET effective_cache_size = '24GB';
ALTER SYSTEM SET maintenance_work_mem = '2GB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
ALTER SYSTEM SET default_statistics_target = 100;
SELECT pg_reload_conf();
```

### Application Tuning

```bash
# Increase file descriptor limits
echo "acgs soft nofile 65536" | sudo tee -a /etc/security/limits.conf
echo "acgs hard nofile 65536" | sudo tee -a /etc/security/limits.conf

# Optimize kernel parameters
sudo tee -a /etc/sysctl.conf << EOF
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 120
EOF

sudo sysctl -p
```

## Backup and Recovery

### Database Backup

```bash
# Create backup script
cat > /home/acgs/scripts/backup_database.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/acgs"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/acgs_backup_$DATE.sql"

mkdir -p $BACKUP_DIR
pg_dump -h localhost -U acgs acgs_production > $BACKUP_FILE
gzip $BACKUP_FILE

# Keep only last 30 days of backups
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
EOF

chmod +x /home/acgs/scripts/backup_database.sh

# Schedule daily backups
echo "0 2 * * * /home/acgs/scripts/backup_database.sh" | crontab -
```

### Configuration Backup

```bash
# Backup configuration files
tar -czf /var/backups/acgs/config_$(date +%Y%m%d).tar.gz \
    /home/acgs/ACGS/config/ \
    /etc/nginx/sites-available/acgs \
    /etc/postgresql/13/main/postgresql.conf
```

## Troubleshooting

### Common Issues

**Service Won't Start:**
```bash
# Check logs
tail -f /var/log/acgs/service.log

# Check port conflicts
sudo netstat -tlnp | grep :8016

# Verify configuration
python scripts/validate_config.py
```

**High Latency:**
```bash
# Check database connections
SELECT count(*) FROM pg_stat_activity;

# Monitor system resources
htop
iotop

# Check Redis performance
redis-cli info stats
```

**Constitutional Compliance Failures:**
```bash
# Verify constitutional hash
grep "cdd01ef066bc6cf2" /var/log/acgs/*.log

# Check policy validation
python scripts/validate_policies.py
```

### Performance Diagnostics

```bash
# Application performance
python scripts/performance_test.py

# Database performance
SELECT query, mean_time, calls FROM pg_stat_statements ORDER BY mean_time DESC LIMIT 10;

# System performance
vmstat 1 10
iostat -x 1 10
```

## Maintenance

### Regular Maintenance Tasks

**Daily:**
- Monitor service health
- Check log files for errors
- Verify backup completion

**Weekly:**
- Update security patches
- Review performance metrics
- Clean up old log files

**Monthly:**
- Update ACGS to latest version
- Review and rotate SSL certificates
- Conduct security audit

### Update Procedure

```bash
# Backup current installation
tar -czf acgs_backup_$(date +%Y%m%d).tar.gz /home/acgs/ACGS/

# Pull latest updates
cd /home/acgs/ACGS
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run database migrations
python scripts/migrate_database.py

# Restart services
./scripts/restart_acgs_services.sh

# Verify deployment
./scripts/health_check.sh
```

## Support and Resources

### Documentation
- **API Documentation:** https://docs.acgs.ai/api
- **Configuration Reference:** https://docs.acgs.ai/config
- **Troubleshooting Guide:** https://docs.acgs.ai/troubleshooting

### Support Channels
- **Enterprise Support:** support@acgs.ai
- **Community Forum:** https://community.acgs.ai
- **GitHub Issues:** https://github.com/your-org/ACGS/issues

### Training Resources
- **Administrator Training:** https://training.acgs.ai/admin
- **User Training:** https://training.acgs.ai/users
- **Best Practices:** https://docs.acgs.ai/best-practices

---

**Document Version:** 3.0.0  
**Last Updated:** July 1, 2025  
**Constitutional Hash:** cdd01ef066bc6cf2  
**Support:** enterprise-support@acgs.ai
