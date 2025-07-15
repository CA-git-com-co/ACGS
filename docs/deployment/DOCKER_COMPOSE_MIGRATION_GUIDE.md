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
