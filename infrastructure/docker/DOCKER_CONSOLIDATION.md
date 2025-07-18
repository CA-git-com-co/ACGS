# Docker Compose Configuration Consolidation
**Constitutional Hash: cdd01ef066bc6cf2**


**Constitutional Hash**: `cdd01ef066bc6cf2`

## Overview

Consolidation of the 15+ scattered Docker Compose files into streamlined development and production configurations that align with the ACGS consolidated architecture.

## Consolidated Files

### Development Environment
**File**: `docker-compose.dev.yml`
- **Target**: Local development and testing
- **Features**: Hot reload, debugging tools, development tools
- **Services**: Core ACGS services + development tools (pgAdmin, Redis Commander, Swagger UI)
- **Network**: `acgs_dev` (172.20.0.0/16)

### Production Environment  
**File**: `docker-compose.prod.yml`
- **Target**: Production deployment
- **Features**: Security hardening, performance optimization, monitoring
- **Services**: Core ACGS services + production tooling (Nginx, Fluentd)
- **Network**: `acgs_prod` (172.21.0.0/16)

## Architecture Changes

### Before: Scattered Configuration
```
├── docker-compose.yml
├── docker-compose.acgs.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── docker-compose.staging.yml
├── config/docker/docker-compose.test.yml
├── docker-compose.monitoring.yml
├── docker-compose.security.yml
├── docker-compose.operational-excellence.yml
├── docker-compose.enterprise-stack.yml
├── docker-compose.kimi.yml
├── docker-compose.nano-vllm.yml
├── docker-compose.nvidia-router.yml
├── docker-compose.ocr.yml
├── docker-compose.nats.yml
└── ... (15+ files total)
```

### After: Streamlined Configuration
```
├── docker-compose.dev.yml     # Development environment
├── docker-compose.prod.yml    # Production environment
└── docker-compose.acgs.yml    # Legacy (maintained for compatibility)
```

## Service Consolidation Reflected

The new configurations reflect our consolidated service architecture:

### Consolidated Services (4 Core)
1. **API Gateway** (port 8080) - Integrated authentication
2. **Constitutional Core** (port 8001) - AI + formal verification  
3. **Governance Engine** (port 8004) - Policy synthesis + compliance
4. **Integrity Service** (port 8002) - Audit trail + cryptographic verification

### Infrastructure Services (3)
1. **PostgreSQL** (port 5439) - Database with RLS
2. **Redis** (port 6389) - Caching and sessions
3. **OPA** (port 8181) - Policy enforcement

## Development Usage

```bash
# Start development environment
docker-compose -f infrastructure/docker/docker-compose.dev.yml up -d

# Start with development tools
docker-compose -f infrastructure/docker/docker-compose.dev.yml --profile dev-tools up -d

# Access services
curl http://localhost:8080/health      # API Gateway
curl http://localhost:8001/health      # Constitutional Core
curl http://localhost:8004/health      # Governance Engine
curl http://localhost:8002/health      # Integrity Service

# Development tools
open http://localhost:5050             # pgAdmin
open http://localhost:8081             # Redis Commander  
open http://localhost:8082             # Swagger UI
```

## Production Usage

```bash
# Production deployment
export POSTGRES_PASSWORD="secure-production-password"
export REDIS_PASSWORD="secure-redis-password"
export ACGS_VERSION="v1.0.0"
export ALLOWED_ORIGINS="https://yourdomain.com"

docker-compose -f infrastructure/docker/docker-compose.prod.yml up -d

# Scale API Gateway for high availability
docker-compose -f infrastructure/docker/docker-compose.prod.yml up -d --scale api_gateway=3
```

## Key Features

### Development Configuration
- **Hot Reload**: Automatic code reloading for development
- **Volume Mounts**: Source code mounted for live editing
- **Debug Tools**: Enhanced logging and debugging capabilities
- **Development Tools**: pgAdmin, Redis Commander, Swagger UI
- **Profiles**: Optional tool activation via Docker Compose profiles

### Production Configuration  
- **Security Hardening**: 
  - `no-new-privileges:true`
  - Read-only containers with tmpfs for temporary files
  - Localhost-only binding for internal services
  - Security-optimized container configurations
- **Performance Optimization**:
  - Multi-worker uvicorn processes  
  - Resource limits and reservations
  - Optimized health checks and timeouts
  - Production-tuned database and cache settings
- **High Availability**:
  - Service replicas for API Gateway
  - Proper dependency ordering and health checks
  - Graceful restart policies
- **Monitoring & Logging**:
  - Nginx reverse proxy with SSL termination
  - Fluentd log aggregation
  - Centralized log storage

## Environmental Variables

### Development
```bash
# Optional - uses reasonable defaults
POSTGRES_USER=acgs_user
POSTGRES_PASSWORD=acgs_password  
POSTGRES_DB=acgs_db
```

### Production
```bash
# Required
POSTGRES_USER=acgs_prod_user
POSTGRES_PASSWORD=<secure-password>
REDIS_PASSWORD=<secure-redis-password>
ACGS_VERSION=v1.0.0
ALLOWED_ORIGINS=https://yourdomain.com

# Optional
POSTGRES_DB=acgs_prod
```

## Network Architecture

### Development Network (`acgs_dev`)
- **Subnet**: 172.20.0.0/16
- **Access**: All ports exposed for development
- **Security**: Basic container isolation

### Production Network (`acgs_prod`)  
- **Subnet**: 172.21.0.0/16
- **Access**: Only API Gateway (8080) and Nginx (80/443) exposed
- **Security**: Enhanced with `enable_icc: false` and IP masquerading

## Volume Management

### Development
- **Source Mounting**: Code mounted for live editing
- **Data Persistence**: Named volumes for database and cache
- **Log Access**: Local log access for debugging

### Production
- **Data Isolation**: Separate volumes for each service
- **Log Aggregation**: Centralized via Fluentd
- **Backup Ready**: Named volumes suitable for backup strategies

## Migration Path

### From Legacy Configurations
1. **Identify Current Environment**: Dev/staging/prod
2. **Extract Environment Variables**: From current compose files
3. **Update Scripts**: Point to new consolidated files
4. **Test Migration**: In non-production environment first
5. **Deploy**: Replace old configurations with new ones

### Service Migration
Services automatically work with new configurations due to:
- **Consistent Naming**: Service names preserved where possible
- **Environment Variables**: Maintained compatibility
- **Port Mapping**: Core ports unchanged
- **Volume Structure**: Compatible with existing data

## Performance Improvements

### Resource Optimization
- **Reduced Overhead**: Fewer containers and networks
- **Memory Efficiency**: Optimized resource allocation
- **CPU Utilization**: Better CPU distribution across services

### Network Efficiency  
- **Simplified Routing**: Fewer network hops
- **Reduced Latency**: Direct service communication
- **Better Caching**: Optimized Redis configurations

## Security Enhancements

### Development Security
- **Container Isolation**: Basic network isolation
- **Development Secrets**: Non-production credentials
- **Debug Access**: Accessible but contained

### Production Security
- **Hardened Containers**: Security-first configuration
- **Network Isolation**: Strict network policies
- **Secret Management**: External secret injection
- **Minimal Attack Surface**: Only necessary ports exposed

## Constitutional Compliance

All configurations maintain constitutional compliance with hash `cdd01ef066bc6cf2`:

- ✅ All services include constitutional hash validation
- ✅ Service consolidation preserves constitutional capabilities  
- ✅ Environmental isolation maintains compliance boundaries
- ✅ Audit logging preserved across all configurations

## Troubleshooting

### Common Issues
1. **Port Conflicts**: Check for existing services on ports 5439, 6389, 8080-8004
2. **Permission Issues**: Ensure Docker has access to volume mount paths
3. **Memory Issues**: Adjust resource limits for your environment
4. **Network Issues**: Verify subnet doesn't conflict with existing networks

### Debug Commands
```bash
# Check service status
docker-compose -f infrastructure/docker/docker-compose.dev.yml ps

# View service logs
docker-compose -f infrastructure/docker/docker-compose.dev.yml logs -f api_gateway

# Check service health
docker-compose -f infrastructure/docker/docker-compose.dev.yml exec api_gateway curl http://localhost:8080/health

# Network inspection
docker network ls
docker network inspect acgs_dev
```

## Future Enhancements

1. **Kubernetes Migration**: These configurations provide foundation for K8s manifests
2. **Multi-Environment**: Add staging configuration if needed
3. **Service Mesh**: Integration with Istio or similar for advanced networking
4. **Observability**: Enhanced monitoring and tracing integration

This consolidation significantly simplifies the ACGS deployment process while maintaining all core functionality and improving security, performance, and maintainability.

## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation

## Performance Targets

This component maintains the following performance requirements:

- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

These targets are validated continuously and must be maintained across all operations.
