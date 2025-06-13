# ACGS-1 Load Balancing and High Availability Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the ACGS-1 Load Balancing and High Availability infrastructure. The system is designed to support >1000 concurrent users with >99.9% availability and <500ms response times.

## Architecture Overview

### Core Components

1. **HAProxy Load Balancer** - Intelligent load balancing with health checks
2. **Service Discovery System** - Dynamic service registration and discovery
3. **Failover Circuit Breakers** - Automatic failover and recovery
4. **Session Affinity Manager** - Governance workflow continuity
5. **Performance Monitor** - Real-time monitoring and alerting
6. **Infrastructure Integration** - Redis caching and PostgreSQL optimization

### Performance Targets

- **Response Time**: <500ms for 95% of requests
- **Availability**: >99.9% uptime
- **Concurrent Users**: >1000 simultaneous users
- **Error Rate**: <1% of total requests

## Prerequisites

### System Requirements

- **Operating System**: Ubuntu 20.04 LTS or CentOS 8+
- **CPU**: Minimum 8 cores (16 cores recommended)
- **Memory**: Minimum 16GB RAM (32GB recommended)
- **Storage**: Minimum 100GB SSD
- **Network**: Gigabit Ethernet

### Software Dependencies

```bash
# Docker and Docker Compose
sudo apt update
sudo apt install -y docker.io docker-compose

# Python 3.9+
sudo apt install -y python3.9 python3.9-pip python3.9-venv

# Redis (if not using Docker)
sudo apt install -y redis-server

# PostgreSQL (if not using Docker)
sudo apt install -y postgresql postgresql-contrib

# HAProxy
sudo apt install -y haproxy

# Monitoring tools
sudo apt install -y htop iotop netstat-nat
```

## Deployment Steps

### Step 1: Environment Setup

1. **Clone Repository**
```bash
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS
```

2. **Create Environment Configuration**
```bash
cp .env.example .env.production
```

3. **Configure Environment Variables**
```bash
# Edit .env.production
ENVIRONMENT=production
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=postgresql://user:password@localhost:5432/acgs_lb
HAPROXY_STATS_USER=admin
HAPROXY_STATS_PASSWORD=secure_password_here
```

### Step 2: Infrastructure Deployment

#### Option A: Docker Deployment (Recommended)

1. **Build and Deploy Services**
```bash
# Build load balancer image
cd infrastructure/load-balancer
docker build -t acgs-haproxy:latest .

# Deploy with Docker Compose
cd ../../infrastructure/docker
docker-compose -f infrastructure/docker/docker-compose.yml up -d
```

2. **Verify Deployment**
```bash
# Check service status
docker-compose ps

# Check HAProxy stats
curl http://localhost:8080/stats
```

#### Option B: Host-Based Deployment

1. **Install Python Dependencies**
```bash
python3.9 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure HAProxy**
```bash
sudo cp infrastructure/load-balancer/haproxy.cfg /etc/haproxy/
sudo systemctl restart haproxy
sudo systemctl enable haproxy
```

3. **Start ACGS Services**
```bash
# Start each service on designated ports
python -m services.core.auth.main --port 8000 &
python -m services.core.ac.main --port 8001 &
python -m services.core.integrity.main --port 8002 &
python -m services.core.fv.main --port 8003 &
python -m services.core.gs.main --port 8004 &
python -m services.core.pgc.main --port 8005 &
python -m services.core.ec.main --port 8006 &
```

### Step 3: Database Setup

1. **Initialize PostgreSQL Schema**
```bash
# Connect to PostgreSQL
psql -U postgres -h localhost

# Create database and user
CREATE DATABASE acgs_lb;
CREATE USER acgs_lb_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE acgs_lb TO acgs_lb_user;
```

2. **Run Schema Migrations**
```bash
python -c "
from services.shared.service_mesh.infrastructure_integration import initialize_load_balancing_schema, DatabaseConnectionManager, ConnectionPoolConfig
import asyncio

async def init_schema():
    config = ConnectionPoolConfig()
    db_manager = DatabaseConnectionManager(config)
    await db_manager.create_pool('metrics', 'postgresql://acgs_lb_user:secure_password@localhost:5432/acgs_lb')
    await initialize_load_balancing_schema(db_manager)

asyncio.run(init_schema())
"
```

### Step 4: Redis Configuration

1. **Configure Redis for Load Balancing**
```bash
# Edit Redis configuration
sudo nano /etc/redis/redis.conf

# Add/modify these settings:
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

2. **Restart Redis**
```bash
sudo systemctl restart redis-server
sudo systemctl enable redis-server
```

### Step 5: Service Discovery Configuration

1. **Configure Service Registry**
```python
# services/shared/service_mesh/registry.py
SERVICE_REGISTRY = {
    ServiceType.AUTH: ServiceConfig(
        name="auth",
        port=8000,
        health_endpoint="/health",
        instances=["auth-1:8000", "auth-2:8000"]
    ),
    # ... other services
}
```

2. **Start Service Discovery**
```bash
python -c "
from services.shared.service_mesh.discovery import get_service_discovery
import asyncio

async def start_discovery():
    discovery = await get_service_discovery()
    await discovery.start()
    # Keep running
    while True:
        await asyncio.sleep(60)

asyncio.run(start_discovery())
" &
```

## Configuration

### HAProxy Configuration

Key configuration parameters in `infrastructure/load-balancer/haproxy.cfg`:

```haproxy
# Performance tuning
maxconn 4096
nbthread 4

# Health check configuration
option httpchk GET /health
http-check expect status 200
timeout check 3s

# Load balancing algorithm
balance roundrobin
hash-type consistent

# Session affinity
stick-table type ip size 100k expire 30s
```

### Service Discovery Configuration

```python
# Load balancing strategy
DEFAULT_STRATEGY = LoadBalancingStrategy.LEAST_RESPONSE_TIME

# Health check interval
HEALTH_CHECK_INTERVAL = 30.0  # seconds

# Session affinity TTL
SESSION_TTL = 3600  # 1 hour
```

### Performance Monitor Configuration

```python
# Monitoring interval
MONITORING_INTERVAL = 30.0  # seconds

# Performance thresholds
THRESHOLDS = {
    "response_time_ms": 500,
    "availability_percent": 99.9,
    "error_rate_percent": 1.0,
    "concurrent_users": 1000
}
```

## Monitoring and Alerting

### HAProxy Statistics

Access HAProxy statistics dashboard:
- URL: `http://your-server:8080/stats`
- Username: `admin`
- Password: `[configured password]`

### Performance Monitoring

1. **Real-time Metrics**
```bash
# Check service health
curl http://localhost:8080/health

# Get performance summary
python -c "
from services.shared.service_mesh.performance_monitor import get_performance_monitor
import asyncio

async def get_stats():
    monitor = await get_performance_monitor()
    summary = monitor.get_current_performance_summary()
    print(summary)

asyncio.run(get_stats())
"
```

2. **Alert Configuration**
```python
# Configure alert callbacks
def email_alert_handler(alert):
    # Send email notification
    pass

def slack_alert_handler(alert):
    # Send Slack notification
    pass

# Register alert handlers
monitor.register_alert_callback(email_alert_handler)
monitor.register_alert_callback(slack_alert_handler)
```

### Log Monitoring

1. **HAProxy Logs**
```bash
# View HAProxy logs
sudo tail -f /var/log/haproxy/haproxy.log

# Monitor error rates
grep "5[0-9][0-9]" /var/log/haproxy/haproxy.log | wc -l
```

2. **Service Discovery Logs**
```bash
# View service discovery logs
tail -f logs/service_discovery.log

# Monitor health check failures
grep "health check failed" logs/service_discovery.log
```

## Scaling and Optimization

### Horizontal Scaling

1. **Add Service Instances**
```python
# Register new instance
instance = ServiceInstance(
    service_type=ServiceType.GS,
    instance_id="gs-3",
    base_url="http://gs-3:8004",
    port=8004,
    health_url="http://gs-3:8004/health"
)
discovery.register_instance(instance)
```

2. **Load Balancer Scaling**
```bash
# Deploy additional HAProxy instances
docker run -d --name haproxy-2 \
  -p 8081:80 -p 8082:8080 \
  -v $(pwd)/haproxy.cfg:/usr/local/etc/haproxy/haproxy.cfg \
  acgs-haproxy:latest
```

### Performance Optimization

1. **Database Connection Pooling**
```python
# Optimize connection pool settings
config = ConnectionPoolConfig(
    min_connections=10,
    max_connections=50,
    max_inactive_connection_lifetime=300.0
)
```

2. **Redis Optimization**
```bash
# Increase Redis memory
redis-cli CONFIG SET maxmemory 4gb

# Optimize persistence
redis-cli CONFIG SET save "900 1 300 10 60 10000"
```

3. **HAProxy Tuning**
```haproxy
# Increase connection limits
maxconn 8192
nbthread 8

# Optimize timeouts
timeout connect 2s
timeout client 30s
timeout server 30s
```

## Security Considerations

### SSL/TLS Configuration

1. **Generate SSL Certificates**
```bash
# Generate self-signed certificate for testing
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout acgs.key -out acgs.crt

# Combine for HAProxy
cat acgs.crt acgs.key > acgs.pem
```

2. **Configure HTTPS in HAProxy**
```haproxy
frontend acgs_frontend
    bind *:443 ssl crt /etc/ssl/certs/acgs.pem
    redirect scheme https if !{ ssl_fc }
```

### Access Control

1. **IP Whitelisting**
```haproxy
# Restrict admin access
acl admin_networks src 10.0.0.0/8 192.168.0.0/16
http-request deny if { path_beg /admin } !admin_networks
```

2. **Rate Limiting**
```haproxy
# Rate limiting configuration
stick-table type ip size 100k expire 30s store http_req_rate(10s)
http-request track-sc0 src
http-request reject if { sc_http_req_rate(0) gt 20 }
```

## Troubleshooting

### Common Issues

1. **Service Discovery Failures**
```bash
# Check service registration
python -c "
from services.shared.service_mesh.discovery import get_service_discovery
import asyncio

async def check_services():
    discovery = await get_service_discovery()
    for service_type in ServiceType:
        instances = discovery.get_healthy_instances(service_type)
        print(f'{service_type.value}: {len(instances)} healthy instances')

asyncio.run(check_services())
"
```

2. **Load Balancing Issues**
```bash
# Check HAProxy backend status
echo "show stat" | socat stdio /var/run/haproxy/admin.sock

# Test load distribution
for i in {1..10}; do
  curl -s http://localhost/api/v1/auth/health | grep instance_id
done
```

3. **Performance Issues**
```bash
# Monitor system resources
htop
iotop
netstat -tuln

# Check database connections
psql -U acgs_lb_user -d acgs_lb -c "SELECT count(*) FROM pg_stat_activity;"
```

### Recovery Procedures

1. **Service Recovery**
```bash
# Restart failed service
docker-compose restart gs_service

# Or for host-based deployment
pkill -f "services.core.gs.main"
python -m services.core.gs.main --port 8004 &
```

2. **Load Balancer Recovery**
```bash
# Restart HAProxy
sudo systemctl restart haproxy

# Or for Docker
docker-compose restart haproxy_load_balancer
```

## Maintenance

### Regular Maintenance Tasks

1. **Database Maintenance**
```sql
-- Clean old metrics (run weekly)
DELETE FROM load_balancing_metrics 
WHERE timestamp < EXTRACT(EPOCH FROM NOW() - INTERVAL '30 days');

-- Vacuum and analyze
VACUUM ANALYZE load_balancing_metrics;
```

2. **Log Rotation**
```bash
# Configure logrotate for HAProxy
sudo nano /etc/logrotate.d/haproxy

# Add configuration:
/var/log/haproxy/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    postrotate
        systemctl reload haproxy
    endscript
}
```

3. **Performance Review**
```bash
# Weekly performance report
python scripts/generate_performance_report.py --days 7

# Monthly capacity planning
python scripts/capacity_planning_analysis.py --month $(date +%m)
```

### Backup and Recovery

1. **Configuration Backup**
```bash
# Backup configurations
tar -czf acgs-lb-config-$(date +%Y%m%d).tar.gz \
  infrastructure/load-balancer/haproxy.cfg \
  .env.production \
  services/shared/service_mesh/registry.py
```

2. **Database Backup**
```bash
# Backup metrics database
pg_dump -U acgs_lb_user acgs_lb > acgs_lb_backup_$(date +%Y%m%d).sql
```

## Support and Contact

For deployment support and issues:
- **Documentation**: [ACGS-1 Wiki](https://github.com/CA-git-com-co/ACGS/wiki)
- **Issues**: [GitHub Issues](https://github.com/CA-git-com-co/ACGS/issues)
- **Email**: support@acgs.ai

---

## Monitoring Dashboards

### Grafana Dashboard Setup

1. **Install Grafana**
```bash
# Add Grafana repository
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install grafana

# Start Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

2. **Configure Data Sources**
```json
{
  "name": "ACGS-PostgreSQL",
  "type": "postgres",
  "url": "localhost:5432",
  "database": "acgs_lb",
  "user": "acgs_lb_user",
  "password": "secure_password"
}
```

3. **Import Dashboard Configuration**
```bash
# Copy dashboard configuration
cp infrastructure/monitoring/grafana/dashboards/acgs-load-balancing.json \
   /var/lib/grafana/dashboards/
```

### Prometheus Integration

1. **Configure Prometheus**
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'haproxy'
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/stats/prometheus'

  - job_name: 'acgs-services'
    static_configs:
      - targets:
        - 'localhost:8000'  # Auth
        - 'localhost:8001'  # AC
        - 'localhost:8004'  # GS
        - 'localhost:8005'  # PGC
```

2. **Key Metrics to Monitor**
- Response time percentiles (P50, P95, P99)
- Request rate and error rate
- Active connections and queue depth
- Service health status
- Resource utilization (CPU, Memory)

### Alert Rules

```yaml
# alert-rules.yml
groups:
  - name: acgs-load-balancing
    rules:
      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"

      - alert: LowAvailability
        expr: (up / count(up)) * 100 < 99.9
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Service availability below target"
```

---

**Last Updated**: December 2024
**Version**: 1.0.0
**Compatibility**: ACGS-1 Phase A3
