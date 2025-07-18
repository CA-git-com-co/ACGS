# Docker Compose Migration Guide
# Constitutional Hash: cdd01ef066bc6cf2

## Migration from Old Structure to New Consolidated Structure

### Old Structure (48+ files scattered across directories)
```
docker-compose.yml
docker-compose.*.yml (multiple variations)
infrastructure/docker/docker-compose.*.yml
infrastructure/monitoring/docker-compose.*.yml
infrastructure/load-balancer/docker-compose.*.yml
```

### New Consolidated Structure
```
# Core files
docker-compose.base.yml              # Infrastructure (PostgreSQL, Redis, OPA, NATS)
docker-compose.services.yml          # Core ACGS services
docker-compose.monitoring.yml        # Unified monitoring stack

# Environment overrides
docker-compose.development.override.yml   # Development with hot reload
docker-compose.production.override.yml    # Production optimizations
docker-compose.testing.override.yml       # Testing configurations

# Specialized stacks
compose-stacks/docker-compose.mcp.yml     # Model Context Protocol services
compose-stacks/docker-compose.*.yml       # Other specialized services
```

### Usage Patterns

#### Development Environment
```bash
# Start infrastructure + services + development overrides
docker-compose -f docker-compose.base.yml \
              -f docker-compose.services.yml \
              -f docker-compose.development.override.yml up

# Add monitoring
docker-compose -f docker-compose.base.yml \
              -f docker-compose.services.yml \
              -f docker-compose.development.override.yml \
              -f docker-compose.monitoring.yml up
```

#### Production Environment
```bash
# Start with production optimizations
docker-compose -f docker-compose.base.yml \
              -f docker-compose.services.yml \
              -f docker-compose.production.override.yml up

# With monitoring and load balancer
docker-compose -f docker-compose.base.yml \
              -f docker-compose.services.yml \
              -f docker-compose.production.override.yml \
              -f docker-compose.monitoring.yml up
```

#### Testing Environment
```bash
# Automated testing setup
docker-compose -f docker-compose.base.yml \
              -f docker-compose.services.yml \
              -f docker-compose.testing.override.yml up
```

#### With Specialized Services
```bash
# Add MCP services for multi-agent coordination
docker-compose -f docker-compose.base.yml -f docker-compose.services.yml up -d
docker-compose -f compose-stacks/docker-compose.mcp.yml up -d
```

### Migration Benefits

1. **Reduced Complexity**: From 48+ files to 6 core files + specialized stacks
2. **Clear Separation**: Infrastructure, services, monitoring, and environments
3. **Easier Maintenance**: Single source of truth for each component type
4. **Better Documentation**: Clear usage patterns and purpose
5. **Constitutional Compliance**: Maintained across all configurations

### Environment Variables

Create `config/environments/development.env` files for different environments:

```bash
# config/environments/development.env.development
POSTGRES_PASSWORD=acgs_dev_password
REDIS_PASSWORD=acgs_dev_redis
ENVIRONMENT=development

# config/environments/developmentconfig/environments/production.env.backup  
POSTGRES_PASSWORD=${SECURE_POSTGRES_PASSWORD}
REDIS_PASSWORD=${SECURE_REDIS_PASSWORD}
ENVIRONMENT=production
```

### Rollback Strategy

If issues arise, restore from backups:
```bash
# Backups are stored in docker-compose-backups/migration_YYYYMMDD/
cp -r docker-compose-backups/migration_*/infrastructure ./
```

## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

## Deployment Configuration

### Environment Variables
```bash
export CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
export PERFORMANCE_TARGET_P99=5ms
export PERFORMANCE_TARGET_RPS=100
export CACHE_HIT_RATE_TARGET=85
```

### Docker Deployment
```yaml
version: '3.8'
services:
  app:
    environment:
      - CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8002/health/constitutional"]
      interval: 30s
      timeout: 10s
      retries: 3
```

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: acgs-service
spec:
  template:
    spec:
      containers:
      - name: app
        env:
        - name: CONSTITUTIONAL_HASH
          value: "cdd01ef066bc6cf2"
        livenessProbe:
          httpGet:
            path: /health/constitutional
            port: 8001
```

## Performance Requirements

### Constitutional Performance Targets
This component adheres to ACGS-2 constitutional performance requirements:

- **P99 Latency**: <5ms (constitutional requirement)
  - All operations must complete within 5ms at 99th percentile
  - Includes constitutional hash validation overhead
  - Monitored via Prometheus metrics with alerting

- **Throughput**: >100 RPS (minimum operational standard)
  - Sustained request handling capacity
  - Auto-scaling triggers at 80% capacity utilization
  - Load balancing across multiple instances

- **Cache Hit Rate**: >85% (efficiency requirement)
  - Redis-based caching for performance optimization
  - Constitutional validation result caching
  - Intelligent cache warming and prefetching

### Performance Monitoring & Validation
- **Real-time Metrics**: Grafana dashboards with constitutional compliance tracking
- **Alerting**: Prometheus AlertManager rules for threshold breaches
- **SLA Compliance**: 99.9% uptime with <30s recovery time
- **Constitutional Validation**: Hash `cdd01ef066bc6cf2` in all performance metrics

### Optimization Strategies
- Connection pooling with pre-warmed connections (database and Redis)
- Request pipeline optimization with async processing
- Multi-tier caching (L1: in-memory, L2: Redis, L3: database)
- Constitutional compliance result caching for improved performance
