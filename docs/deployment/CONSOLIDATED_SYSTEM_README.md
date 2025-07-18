# ACGS-2 Consolidated System
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

The ACGS-2 Consolidated System represents a complete refactoring of the original ACGS-2 architecture, eliminating massive duplication and providing a unified, maintainable deployment platform.

## System Architecture

### Before Consolidation
- **60+ Docker Compose files** with 70% redundancy
- **7 identical authentication configuration files**
- **30+ Prometheus configurations** with substantial overlap
- **80+ placeholder-filled CLAUDE.md files**
- **20+ deployment scripts** with similar functionality

### After Consolidation
- **6 standardized Docker Compose files** with environment-specific overrides
- **1 centralized authentication configuration** with environment variants
- **1 unified monitoring stack** with comprehensive observability
- **1 automated documentation generator** for all directories
- **1 comprehensive deployment script** for all environments

## Quick Start

### 1. Deploy Development Environment
```bash
# Clone and navigate to project
cd ACGS-2

# Deploy full development stack
./scripts/deploy-acgs-consolidated.sh

# Access services
# - Services: http://localhost:8000-8006
# - Grafana: http://localhost:3000 (admin/admin)
# - Prometheus: http://localhost:9090
# - PgAdmin: http://localhost:5050
```

### 2. Deploy Production Environment
```bash
# Set production environment variables
export POSTGRES_PASSWORD="secure_production_password"
export REDIS_PASSWORD="secure_redis_password"
export JWT_SECRET_KEY="production_jwt_secret"

# Deploy production stack
./scripts/deploy-acgs-consolidated.sh -e production

# Access services
# - Services: http://localhost:8000-8006
# - Grafana: http://localhost:3000
# - Prometheus: http://localhost:9090
```

### 3. Generate Documentation
```bash
# Generate CLAUDE.md files for all directories
python3 scripts/tools/claude_md_generator.py --all --force

# Generate for specific directory
python3 scripts/tools/claude_md_generator.py docs/
```

## Architecture Components

### 1. Base Infrastructure (`docker-compose.base-infrastructure.yml`)
- **PostgreSQL**: Primary database with optimized configuration
- **Redis**: Caching and session management
- **NATS**: Message queuing and event streaming
- **OPA**: Policy enforcement and authorization
- **HAProxy**: Load balancing and SSL termination

### 2. ACGS Services (`docker-compose.acgs-services.yml`)
- **Authentication Service** (8000): User authentication and authorization
- **Constitutional AI Service** (8001): Constitutional compliance validation
- **Integrity Service** (8002): Data integrity and validation
- **Formal Verification Service** (8003): Formal verification processes
- **Governance Synthesis Service** (8004): Governance policy synthesis
- **Policy Governance Service** (8005): Policy management and enforcement
- **Evolutionary Computation Service** (8006): Optimization algorithms

### 3. Environment Overrides
- **Development** (`docker-compose.development.yml`): Dev tools, relaxed security
- **Staging** (`docker-compose.staging.yml`): Production-like testing environment
- **Production** (`docker-compose.production-override.yml`): Production optimizations

### 4. Monitoring Stack (`docker-compose.monitoring-consolidated.yml`)
- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Alertmanager**: Alert management and routing
- **Loki**: Log aggregation and analysis
- **Jaeger**: Distributed tracing
- **Exporters**: Node, PostgreSQL, Redis metrics

## Configuration Management

### 1. Shared Configuration (`config/shared/`)
- **`auth_config.yml`**: Centralized authentication settings
- **`environment.yml`**: Environment-specific configurations

### 2. Environment Variables (`config/environments/`)
- **`.env.template`**: Template for all environment variables
- **`.env.development`**: Development-specific variables
- **`.env.staging`**: Staging-specific variables
- **`.env.production`**: Production-specific variables

### 3. Service Discovery
All services use standardized naming and port allocation:
```yaml
services:
  auth_service: "http://auth_service:8000"
  ac_service: "http://ac_service:8001"
  integrity_service: "http://integrity_service:8002"
  # ... etc
```

## Deployment Options

### 1. Full Stack Deployment
```bash
# Deploy everything
./scripts/deploy-acgs-consolidated.sh -e production

# Deploy with monitoring
./scripts/deploy-acgs-consolidated.sh -e production --monitoring
```

### 2. Component-Specific Deployment
```bash
# Deploy only infrastructure
./scripts/deploy-acgs-consolidated.sh -c infrastructure

# Deploy only services
./scripts/deploy-acgs-consolidated.sh -c services

# Deploy only monitoring
./scripts/deploy-acgs-consolidated.sh -c monitoring
```

### 3. Service Management
```bash
# Stop all services
./scripts/deploy-acgs-consolidated.sh -a stop

# Restart services
./scripts/deploy-acgs-consolidated.sh -a restart

# Check status
./scripts/deploy-acgs-consolidated.sh -a status

# View logs
./scripts/deploy-acgs-consolidated.sh -a logs
```

## Migration from Legacy System

### Automated Migration
```bash
# Run migration script
./scripts/migrate-to-consolidated.sh

# This will:
# 1. Backup existing system
# 2. Stop old services
# 3. Migrate configurations
# 4. Validate new system
# 5. Generate migration report
```

### Manual Migration Steps
1. **Backup existing system**
2. **Stop all running services**
3. **Update environment variables**
4. **Deploy new system**
5. **Validate and test**

## Performance Targets

The consolidated system maintains strict performance requirements:

| Metric | Target | Constitutional Requirement |
|--------|--------|----------------------------|
| P99 Latency | <5ms | ✅ Required |
| Throughput | >100 RPS | ✅ Required |
| Cache Hit Rate | >85% | ✅ Required |
| Constitutional Compliance | 100% | ✅ Required |

## Monitoring and Observability

### 1. Metrics Collection
- **Prometheus**: Service metrics, performance indicators
- **Node Exporter**: System metrics
- **PostgreSQL Exporter**: Database metrics
- **Redis Exporter**: Cache metrics

### 2. Visualization
- **Grafana Dashboards**: Real-time monitoring
- **Custom Dashboards**: Service-specific metrics
- **Alert Panels**: Critical issue visualization

### 3. Logging
- **Loki**: Centralized log aggregation
- **Promtail**: Log collection from containers
- **Structured Logging**: JSON-formatted logs

### 4. Tracing
- **Jaeger**: Distributed request tracing
- **OpenTelemetry**: Instrumentation framework

## Security Features

### 1. Authentication & Authorization
- **JWT-based authentication**: Secure token management
- **Role-based access control**: Granular permissions
- **Service-to-service authentication**: Secure inter-service communication

### 2. Network Security
- **Container network isolation**: Secure service communication
- **SSL/TLS termination**: Encrypted external communication
- **Rate limiting**: DDoS protection

### 3. Data Protection
- **Encrypted passwords**: Secure credential storage
- **Database encryption**: Data at rest protection
- **Audit logging**: Comprehensive activity tracking

## Development Workflow

### 1. Local Development
```bash
# Start development environment
./scripts/deploy-acgs-consolidated.sh -e development

# Make changes to services
# Services auto-reload in development mode

# Run tests
./scripts/deploy-acgs-consolidated.sh -a test
```

### 2. Testing
```bash
# Run all tests
./scripts/deploy-acgs-consolidated.sh -a test

# Run specific test suite
./scripts/deploy-acgs-consolidated.sh -a test -c services
```

### 3. Documentation
```bash
# Generate documentation
python3 scripts/tools/claude_md_generator.py --all

# Update specific documentation
python3 scripts/tools/claude_md_generator.py docs/
```

## Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -tulpn | grep :8000
   
   # Use alternative ports
   AUTH_SERVICE_PORT=8010 ./scripts/deploy-acgs-consolidated.sh
   ```

2. **Service Health Check Failures**
   ```bash
   # Check service logs
   ./scripts/deploy-acgs-consolidated.sh -a logs -c services
   
   # Test individual service
   curl http://localhost:8000/health
   ```

3. **Database Connection Issues**
   ```bash
   # Check database status
   docker-compose -f infrastructure/docker/docker-compose.base-infrastructure.yml ps postgres
   
   # Check database logs
   docker-compose -f infrastructure/docker/docker-compose.base-infrastructure.yml logs postgres
   ```

### Debug Mode
```bash
# Enable debug logging
DEBUG=true ./scripts/deploy-acgs-consolidated.sh -v

# Dry run mode
./scripts/deploy-acgs-consolidated.sh --dry-run
```

## Constitutional Compliance

All components maintain constitutional hash `cdd01ef066bc6cf2` validation:

- **Configuration Validation**: All configs include constitutional hash
- **Performance Monitoring**: Continuous validation of performance targets
- **Audit Trails**: Complete logging of all operations
- **Compliance Reporting**: Automated compliance status reporting

## Benefits of Consolidation

### 1. Reduced Complexity
- **90% reduction** in duplicate configurations
- **Single source of truth** for all settings
- **Standardized patterns** across all environments

### 2. Improved Maintainability
- **Centralized configuration management**
- **Shared libraries and utilities**
- **Automated documentation generation**

### 3. Enhanced Reliability
- **Consistent deployment patterns**
- **Comprehensive monitoring**
- **Automated health checks**

### 4. Better Developer Experience
- **Single deployment command**
- **Standardized development environment**
- **Comprehensive documentation**

## Contributing

### Adding New Services
1. **Add service definition** to `docker-compose.acgs-services.yml`
2. **Update shared configuration** in `config/shared/`
3. **Add service to deployment script**
4. **Update monitoring configuration**
5. **Generate documentation**

### Modifying Configurations
1. **Update shared configuration files**
2. **Test in development environment**
3. **Validate constitutional compliance**
4. **Update documentation**
5. **Deploy to staging for testing**

## Support

For issues, questions, or contributions:

1. **Check troubleshooting guide**: `docs/deployment/CONSOLIDATION_USAGE_GUIDE.md`
2. **Review migration report**: `MIGRATION_REPORT.md`
3. **Examine service logs**: `./scripts/deploy-acgs-consolidated.sh -a logs`
4. **Validate constitutional compliance**: Check for hash `cdd01ef066bc6cf2`

---

**Constitutional Hash**: `cdd01ef066bc6cf2`
**Last Updated**: 2025-07-18
**System Status**: ✅ PRODUCTION READY