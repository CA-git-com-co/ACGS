# ACGS-1 Container-Based Development Environment

## Overview

This document provides comprehensive guidance for using the production-ready container-based development environment for ACGS-1 constitutional governance system. The containerized setup maintains full compatibility with the existing host-based architecture while enabling cloud-native deployment capabilities.

## Architecture

### Container Structure
- **Multi-stage Dockerfile** (`Dockerfile.acgs`) with optimized layers
- **7 Core Services** running in separate containers with proper dependency management
- **Infrastructure Services** (PostgreSQL, Redis, HAProxy) with production configurations
- **Development Tools** including Solana/Anchor environment and monitoring stack

### Service Ports
- **Auth Service**: 8000 (Authentication and Authorization)
- **AC Service**: 8001 (Constitutional AI)
- **Integrity Service**: 8002 (Data Integrity and Cryptographic Verification)
- **FV Service**: 8003 (Formal Verification)
- **GS Service**: 8004 (Governance Synthesis)
- **PGC Service**: 8005 (Policy Governance Compliance)
- **EC Service**: 8006 (Evolutionary Computation)

### Infrastructure Ports
- **PostgreSQL**: 5432
- **Redis**: 6379
- **HAProxy**: 80 (Load Balancer), 8080 (Stats)
- **Prometheus**: 9090
- **Grafana**: 3001

## Quick Start

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 8GB+ RAM available for containers
- 20GB+ disk space

### 1. Environment Setup
```bash
# Clone the repository
cd /home/dislove/ACGS-1

# Copy environment template
cp .env.example .env.docker

# Edit environment variables as needed
nano .env.docker
```

### 2. Build and Start Services
```bash
# Build all containers
docker-compose -f docker-compose.acgs.yml build

# Start infrastructure services first
docker-compose -f docker-compose.acgs.yml up -d postgres redis

# Wait for infrastructure to be ready (30 seconds)
sleep 30

# Start all ACGS services
docker-compose -f docker-compose.acgs.yml up -d
```

### 3. Verify Deployment
```bash
# Run comprehensive health check
./scripts/docker/health_check_all_services.sh

# Check service logs
docker-compose -f docker-compose.acgs.yml logs -f ac_service
```

## Development Workflow

### Service Management
```bash
# Start specific service
docker-compose -f docker-compose.acgs.yml up -d ac_service

# Stop specific service
docker-compose -f docker-compose.acgs.yml stop ac_service

# Restart service
docker-compose -f docker-compose.acgs.yml restart ac_service

# View service logs
docker-compose -f docker-compose.acgs.yml logs -f ac_service

# Execute commands in service container
docker-compose -f docker-compose.acgs.yml exec ac_service bash
```

### Anchor/Solana Development
```bash
# Access Solana development container
docker-compose -f docker-compose.acgs.yml exec solana_dev bash

# Run Anchor tests
./scripts/docker/anchor_test_container.sh

# Deploy to devnet
docker-compose -f docker-compose.acgs.yml exec solana_dev anchor deploy --provider.cluster devnet
```

### Performance Testing
```bash
# Run performance validation
./scripts/docker/performance_validation.sh

# Test Quantumagi deployment
./scripts/docker/quantumagi_deployment_test.sh

# Monitor resource usage
docker stats
```

## Configuration

### Environment Variables
Key environment variables for containerized deployment:

```bash
# Database Configuration
POSTGRES_USER=acgs_user
POSTGRES_PASSWORD=acgs_password
POSTGRES_DB=acgs_db

# Service Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO

# Constitutional Governance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
CONSTITUTIONAL_FIDELITY_THRESHOLD=0.85

# Performance Targets
PGC_LATENCY_TARGET=25
MAX_RESPONSE_TIME_MS=500

# Solana Configuration
SOLANA_NETWORK=devnet
ANCHOR_PROVIDER_URL=https://api.devnet.solana.com
```

### Resource Limits
Default resource allocations per service:

- **Auth Service**: 512MB RAM, 0.5 CPU
- **AC Service**: 1GB RAM, 0.75 CPU
- **Integrity Service**: 512MB RAM, 0.5 CPU
- **FV Service**: 1GB RAM, 0.75 CPU
- **GS Service**: 1.5GB RAM, 1.0 CPU
- **PGC Service**: 1GB RAM, 0.75 CPU
- **EC Service**: 1GB RAM, 0.75 CPU

## Monitoring and Observability

### Health Checks
All services include comprehensive health checks:
- **HTTP Health Endpoints**: `/health` for each service
- **Container Health Checks**: Built into Docker Compose
- **Dependency Checks**: Services wait for dependencies to be healthy

### Metrics and Monitoring
- **Prometheus**: Metrics collection at `http://localhost:9090`
- **Grafana**: Dashboards at `http://localhost:3001` (admin/admin123)
- **HAProxy Stats**: Load balancer stats at `http://localhost:8080/stats`

### Log Aggregation
- **Centralized Logging**: All service logs in `/app/logs` volume
- **Fluent Bit**: Log aggregation and forwarding
- **Structured Logging**: JSON format with correlation IDs

## Performance Targets

### Response Time Requirements
- **General Services**: <500ms for 95% of operations
- **PGC Service**: <25ms for compliance checks
- **Constitutional Validation**: <100ms for compliance checks

### Availability Targets
- **Service Availability**: >99.5% uptime
- **Constitutional Governance**: >95% compliance accuracy
- **Blockchain Costs**: <0.01 SOL per governance action

### Scalability Targets
- **Concurrent Users**: Support >1000 simultaneous governance actions
- **Throughput**: Handle governance workflows at scale
- **Resource Efficiency**: Optimized container resource usage

## Troubleshooting

### Common Issues

#### Container Startup Failures
```bash
# Check container logs
docker-compose -f docker-compose.acgs.yml logs service_name

# Check resource usage
docker stats

# Restart problematic service
docker-compose -f docker-compose.acgs.yml restart service_name
```

#### Service Communication Issues
```bash
# Test service connectivity
docker-compose -f docker-compose.acgs.yml exec ac_service curl http://auth_service:8000/health

# Check network configuration
docker network ls
docker network inspect acgs_acgs_network
```

#### Performance Issues
```bash
# Run performance validation
./scripts/docker/performance_validation.sh

# Check resource limits
docker-compose -f docker-compose.acgs.yml config

# Monitor real-time metrics
docker stats --no-stream
```

### Debug Mode
Enable debug mode for detailed logging:
```bash
# Set debug environment
export LOG_LEVEL=DEBUG
export ENVIRONMENT=debug

# Restart services with debug logging
docker-compose -f docker-compose.acgs.yml restart
```

## Migration from Host-Based Deployment

### Data Migration
```bash
# Export data from host-based deployment
pg_dump acgs_db > acgs_backup.sql

# Import to containerized database
docker-compose -f docker-compose.acgs.yml exec postgres psql -U acgs_user -d acgs_db < acgs_backup.sql
```

### Configuration Migration
1. Copy environment variables from host `.env` to `.env.docker`
2. Update service URLs to use container names
3. Verify Solana keypair locations in volumes

### Validation
```bash
# Run comprehensive validation
./scripts/docker/health_check_all_services.sh
./scripts/docker/quantumagi_deployment_test.sh
./scripts/docker/performance_validation.sh
```

## Production Deployment

### Security Considerations
- Use production-grade secrets management
- Configure proper network policies
- Enable container security scanning
- Implement proper backup strategies

### Scaling Considerations
- Use Kubernetes for orchestration
- Implement horizontal pod autoscaling
- Configure persistent volume claims
- Set up proper ingress controllers

### Monitoring in Production
- Configure alerting rules
- Set up log retention policies
- Implement distributed tracing
- Monitor constitutional compliance metrics

## Support and Maintenance

### Regular Maintenance
- Update container images regularly
- Monitor resource usage trends
- Review and rotate secrets
- Backup persistent data

### Performance Optimization
- Tune resource limits based on usage
- Optimize database queries
- Configure caching strategies
- Monitor and optimize network latency

For additional support, refer to the ACGS-1 documentation or contact the development team.
