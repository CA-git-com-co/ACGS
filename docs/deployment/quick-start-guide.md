# ACGS-1 Load Balancing Quick Start Guide

## 🚀 Quick Deployment (5 Minutes)

This guide gets you up and running with ACGS-1 Load Balancing in under 5 minutes.

### Prerequisites

- Docker and Docker Compose installed
- 8GB+ RAM available
- Ports 80, 443, 8000-8006, 8080 available

### Step 1: Clone and Setup

```bash
# Clone repository
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS

# Copy environment configuration
cp .env.example .env.local

# Set basic configuration
export ENVIRONMENT=development
export REDIS_URL=redis://redis:6379/0
export DATABASE_URL=postgresql://postgres:postgres@postgres:5432/acgs_lb
```

### Step 2: Deploy with Docker Compose

```bash
# Start all services
docker-compose -f infrastructure/docker/infrastructure/docker/docker-compose.yml up -d

# Wait for services to start (30-60 seconds)
sleep 60

# Verify deployment
docker-compose ps
```

### Step 3: Verify Load Balancing

```bash
# Check HAProxy stats
curl http://localhost:8080/stats

# Test load balancing
for i in {1..5}; do
  curl -s http://localhost/api/v1/auth/health | grep instance_id
done

# Check service discovery
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8004/health
curl http://localhost:8005/health
```

### Step 4: Access Monitoring

- **HAProxy Stats**: http://localhost:8080/stats (admin/admin)
- **Grafana Dashboard**: http://localhost:3001 (admin/admin123)
- **Service Health**: http://localhost/health

## 🔧 Configuration

### Environment Variables

```bash
# Core settings
ENVIRONMENT=development
LOG_LEVEL=INFO

# Load balancing
LB_STRATEGY=least_response_time
HEALTH_CHECK_INTERVAL=30
SESSION_TTL=3600

# Performance targets
TARGET_RESPONSE_TIME_MS=500
TARGET_AVAILABILITY_PERCENT=99.9
TARGET_CONCURRENT_USERS=1000
```

### Service Ports

| Service | Port | Description |
|---------|------|-------------|
| HAProxy | 80/443 | Load balancer |
| HAProxy Stats | 8080 | Statistics dashboard |
| Auth Service | 8000 | Authentication |
| AC Service | 8001 | Constitutional AI |
| Integrity Service | 8002 | Data integrity |
| FV Service | 8003 | Formal verification |
| GS Service | 8004 | Governance synthesis |
| PGC Service | 8005 | Policy governance |
| EC Service | 8006 | Evolutionary computation |

## 📊 Monitoring

### Key Metrics

```bash
# Response time monitoring
curl http://localhost:8080/stats | grep "time"

# Service health status
curl http://localhost/api/v1/health/summary

# Load distribution
curl http://localhost:8080/stats | grep "weight"

# Error rates
curl http://localhost:8080/stats | grep "errors"
```

### Performance Validation

```bash
# Run performance tests
cd tests/service_mesh
python run_load_balancing_tests.py

# Check test results
cat load_balancing_test_report.json
```

## 🧪 Testing Load Balancing

### Basic Load Test

```bash
# Install testing tools
pip install httpx asyncio

# Run concurrent requests
python -c "
import asyncio
import httpx
import time

async def test_load():
    async with httpx.AsyncClient() as client:
        tasks = []
        for i in range(100):
            task = client.get('http://localhost/api/v1/auth/health')
            tasks.append(task)
        
        start = time.time()
        responses = await asyncio.gather(*tasks)
        end = time.time()
        
        success_count = sum(1 for r in responses if r.status_code == 200)
        print(f'Completed {len(responses)} requests in {end-start:.2f}s')
        print(f'Success rate: {success_count/len(responses)*100:.1f}%')

asyncio.run(test_load())
"
```

### Session Affinity Test

```bash
# Test session affinity
SESSION_ID="test-session-123"

for i in {1..10}; do
  curl -s -H "X-Session-ID: $SESSION_ID" \
    http://localhost/api/v1/auth/health | \
    grep instance_id
done
```

### Failover Test

```bash
# Stop one service instance
docker-compose stop auth_service

# Test continued availability
curl http://localhost/api/v1/auth/health

# Restart service
docker-compose start auth_service
```

## 🔍 Troubleshooting

### Common Issues

1. **Services not starting**
```bash
# Check logs
docker-compose logs auth_service
docker-compose logs haproxy_load_balancer

# Check ports
netstat -tuln | grep -E "800[0-6]|80|443"
```

2. **Load balancing not working**
```bash
# Check HAProxy configuration
docker exec acgs_haproxy_lb cat /usr/local/etc/haproxy/haproxy.cfg

# Check backend status
echo "show stat" | docker exec -i acgs_haproxy_lb socat stdio /var/run/haproxy/admin.sock
```

3. **High response times**
```bash
# Check resource usage
docker stats

# Check service health
for port in 8000 8001 8004 8005; do
  curl -w "Response time: %{time_total}s\n" http://localhost:$port/health
done
```

### Health Checks

```bash
# Comprehensive health check
./scripts/health_check.sh

# Or manual checks
curl http://localhost/health
curl http://localhost:8080/stats
docker-compose ps
```

## 📈 Performance Optimization

### Quick Optimizations

1. **Increase connection limits**
```bash
# Edit HAProxy config
docker exec acgs_haproxy_lb sed -i 's/maxconn 4096/maxconn 8192/' /usr/local/etc/haproxy/haproxy.cfg
docker-compose restart haproxy_load_balancer
```

2. **Optimize Redis**
```bash
# Increase Redis memory
docker exec acgs_redis redis-cli CONFIG SET maxmemory 2gb
```

3. **Scale services**
```bash
# Scale up services
docker-compose -f infrastructure/docker/docker-compose.yml up -d --scale gs_service=3 --scale auth_service=2
```

## 🛡️ Security

### Basic Security Setup

```bash
# Generate SSL certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/acgs.key -out ssl/acgs.crt \
  -subj "/C=US/ST=CA/L=SF/O=ACGS/CN=localhost"

# Combine for HAProxy
cat ssl/acgs.crt ssl/acgs.key > ssl/acgs.pem

# Update HAProxy to use HTTPS
# (Edit infrastructure/load-balancer/haproxy.cfg)
```

### Access Control

```bash
# Change default passwords
export HAPROXY_STATS_PASSWORD="your-secure-password"
export GRAFANA_ADMIN_PASSWORD="your-secure-password"

# Restart services
docker-compose -f infrastructure/docker/docker-compose.yml down && docker-compose -f infrastructure/docker/docker-compose.yml up -d
```

## 📚 Next Steps

### Production Deployment
- Review [Production Deployment Guide](load-balancing-deployment.md)
- Complete [Production Readiness Checklist](production-readiness-checklist.md)
- Set up monitoring and alerting
- Configure SSL certificates
- Implement backup procedures

### Advanced Configuration
- Configure custom load balancing strategies
- Set up multi-region deployment
- Implement advanced monitoring
- Configure governance workflows
- Set up disaster recovery

### Integration
- Integrate with existing systems
- Configure LDAP/SSO authentication
- Set up external monitoring
- Configure log aggregation
- Implement CI/CD pipeline

## 🆘 Support

- **Documentation**: [Full Deployment Guide](load-balancing-deployment.md)
- **Issues**: [GitHub Issues](https://github.com/CA-git-com-co/ACGS/issues)
- **Community**: [ACGS Discord](https://discord.gg/acgs)
- **Email**: support@acgs.ai

---

**Quick Start Version**: 1.0.0  
**Last Updated**: December 2024  
**Estimated Setup Time**: 5 minutes
