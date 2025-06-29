# ACGS Docker-in-Docker Implementation Guide

## Overview

This guide covers the comprehensive Docker-in-Docker (DinD) implementation for the ACGS (Algorithmic Constitution Governance System). The DinD setup enables containerized testing, deployment, and management of all ACGS services in an isolated environment.

## Architecture

### DinD Components

1. **Docker Daemon Container** (`docker-dind`)
   - Privileged container running Docker daemon
   - TLS-secured communication
   - Isolated storage and networking

2. **ACGS Core Services**
   - Auth Service (Port 8000)
   - Algorithmic Constitution Service (Port 8001)
   - Integrity Verification Service (Port 8002)
   - Formal Verification Service (Port 8003)
   - Governance Simulation Service (Port 8004)
   - Policy Generation Consensus Service (Port 8005)
   - Evolutionary Computation Service (Port 8006)

3. **Infrastructure Services**
   - PostgreSQL Database
   - Redis Cache
   - NATS Message Broker

4. **Monitoring Stack**
   - Prometheus Metrics Collection
   - Grafana Dashboards

### Network Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Host System                              │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              Docker-in-Docker Network                 │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐   │  │
│  │  │   Docker    │  │    ACGS     │  │ Monitoring  │   │  │
│  │  │   Daemon    │  │  Services   │  │   Stack     │   │  │
│  │  │             │  │             │  │             │   │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘   │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Prerequisites

### System Requirements

- **Operating System**: Linux (Ubuntu 20.04+ recommended)
- **Memory**: 8GB RAM minimum, 16GB recommended
- **Storage**: 50GB available disk space
- **CPU**: 4 cores minimum, 8 cores recommended

### Software Dependencies

- Docker 24.0+
- Docker Compose 2.0+
- Python 3.11+
- Git

### Installation

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Add user to docker group
sudo usermod -aG docker $USER
```

## Quick Start

### 1. Setup DinD Environment

```bash
# Clone ACGS repository
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS

# Run DinD setup
./scripts/docker/setup-dind.sh setup
```

### 2. Deploy ACGS Services

```bash
# Deploy complete ACGS stack
python scripts/docker/deploy-acgs-dind.py

# Or use Docker Compose directly
cd infrastructure/docker/dind
docker-compose up -d
```

### 3. Verify Deployment

```bash
# Check service status
./scripts/docker/setup-dind.sh status

# Run integration tests
./scripts/docker/setup-dind.sh test
```

## Configuration

### Environment Variables

Key environment variables in `.env` file:

```bash
# Project Configuration
COMPOSE_PROJECT_NAME=acgs-dind
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2

# Database Configuration
POSTGRES_DB=acgs
POSTGRES_USER=acgs_user
POSTGRES_PASSWORD=acgs_secure_password

# Docker Configuration
DOCKER_TLS_VERIFY=1
DOCKER_CERT_PATH=/certs/client
DOCKER_HOST=tcp://docker-dind:2376
```

### Service Configuration

Each ACGS service can be configured through environment variables:

```yaml
# Example service configuration
acgs-auth-service:
  environment:
    - SERVICE_PORT=8000
    - CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
    - DATABASE_URL=postgresql://acgs_user:password@acgs-postgres:5432/acgs
    - REDIS_URL=redis://acgs-redis:6379
```

## Management Commands

### Service Management

```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d acgs-auth-service

# Stop all services
docker-compose down

# Stop with volume cleanup
docker-compose down -v

# Restart service
docker-compose restart acgs-auth-service

# Scale service
docker-compose up -d --scale acgs-auth-service=3
```

### Monitoring and Logs

```bash
# View logs for all services
docker-compose logs -f

# View logs for specific service
docker-compose logs -f acgs-auth-service

# View container status
docker-compose ps

# Execute command in container
docker-compose exec acgs-auth-service bash
```

### Health Checks

```bash
# Check service health
curl http://localhost:8000/health

# Check all service endpoints
for port in {8000..8006}; do
  echo "Checking port $port:"
  curl -s http://localhost:$port/health | jq .
done
```

## Security

### TLS Configuration

DinD uses TLS for secure communication:

- **CA Certificate**: `/certs/ca/cert.pem`
- **Server Certificate**: `/certs/server/cert.pem`
- **Client Certificate**: `/certs/client/cert.pem`

### Container Security

- Services run as non-root users
- Resource limits enforced
- Network isolation
- Read-only filesystems where possible

### Constitutional Compliance

All services validate constitutional hash: `cdd01ef066bc6cf2`

## Monitoring

### Prometheus Metrics

Access Prometheus at: http://localhost:9090

Key metrics:
- `acgs_constitutional_compliance_score`
- `http_request_duration_seconds`
- `evolution_requests_total`
- `container_cpu_usage_seconds_total`

### Grafana Dashboards

Access Grafana at: http://localhost:3001
- Username: `admin`
- Password: `acgs_grafana_admin`

Pre-configured dashboards:
- ACGS Docker-in-Docker Monitoring
- Service Health Overview
- Constitutional Compliance Tracking

## Testing

### Integration Tests

```bash
# Run comprehensive DinD tests
python tests/dind/test_dind_integration.py

# Run specific test suite
pytest tests/dind/ -v

# Run with coverage
pytest tests/dind/ --cov=services --cov-report=html
```

### Performance Testing

```bash
# Load testing with locust
pip install locust
locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

## Troubleshooting

### Common Issues

#### 1. Docker Daemon Not Starting

```bash
# Check Docker daemon logs
docker-compose logs docker-dind

# Restart Docker daemon
docker-compose restart docker-dind
```

#### 2. Service Health Check Failures

```bash
# Check service logs
docker-compose logs acgs-auth-service

# Check container resources
docker stats

# Verify network connectivity
docker-compose exec acgs-auth-service ping acgs-postgres
```

#### 3. TLS Certificate Issues

```bash
# Regenerate certificates
./scripts/docker/setup-dind.sh cleanup
./scripts/docker/setup-dind.sh setup
```

#### 4. Database Connection Issues

```bash
# Check PostgreSQL status
docker-compose exec acgs-postgres pg_isready -U acgs_user

# Reset database
docker-compose down -v
docker-compose up -d acgs-postgres
```

### Performance Optimization

#### Resource Allocation

```yaml
# Optimize service resources
services:
  acgs-auth-service:
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
```

#### Database Tuning

```bash
# PostgreSQL optimization
echo "shared_preload_libraries = 'pg_stat_statements'" >> postgresql.conf
echo "max_connections = 200" >> postgresql.conf
echo "shared_buffers = 256MB" >> postgresql.conf
```

## Backup and Recovery

### Database Backup

```bash
# Create database backup
docker-compose exec acgs-postgres pg_dump -U acgs_user acgs > backup.sql

# Restore database
docker-compose exec -T acgs-postgres psql -U acgs_user acgs < backup.sql
```

### Volume Backup

```bash
# Backup volumes
docker run --rm -v acgs-dind_postgres-data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz -C /data .

# Restore volumes
docker run --rm -v acgs-dind_postgres-data:/data -v $(pwd):/backup alpine tar xzf /backup/postgres-backup.tar.gz -C /data
```

## Development

### Adding New Services

1. Create service directory structure
2. Add Dockerfile
3. Update docker-compose.yml
4. Add health checks
5. Update monitoring configuration

### Custom Images

```dockerfile
# Example custom service image
FROM acgs/base:latest

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${SERVICE_PORT}/health || exit 1

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0"]
```

## Production Deployment

### Scaling Considerations

- Use Docker Swarm or Kubernetes for production
- Implement load balancing
- Configure persistent storage
- Set up monitoring and alerting
- Implement backup strategies

### Security Hardening

- Use secrets management
- Enable audit logging
- Implement network policies
- Regular security updates
- Vulnerability scanning

## Support

### Documentation

- [ACGS Architecture Guide](./architecture.md)
- [API Documentation](./api_documentation.md)
- [Security Guide](./security_architecture.md)

### Community

- GitHub Issues: https://github.com/CA-git-com-co/ACGS/issues
- Discussions: https://github.com/CA-git-com-co/ACGS/discussions

### Constitutional Compliance

All DinD implementations must maintain constitutional hash validation: `cdd01ef066bc6cf2`

For questions or support, please refer to the project documentation or create an issue in the GitHub repository.
