# ACGS-2 Consolidation Usage Guide
<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

## Overview

This guide explains how to use the consolidated ACGS-2 infrastructure after the duplication elimination consolidation. The new system provides a unified, environment-agnostic approach to deployment, configuration, and documentation.

## New Architecture

### 1. Docker Compose Structure

The new Docker Compose architecture uses a layered approach:

```
infrastructure/docker/
├── docker-compose.base-infrastructure.yml    # Base infrastructure services
├── docker-compose.acgs-services.yml          # ACGS core services
├── docker-compose.development.yml            # Development overrides
├── docker-compose.staging.yml                # Staging overrides (to be created)
└── docker-compose.production-override.yml    # Production overrides
```

### 2. Configuration Management

Centralized configuration files:

```
config/shared/
├── auth_config.yml        # Unified authentication configuration
└── environment.yml        # Environment-specific settings
```

### 3. Monitoring Stack

Consolidated monitoring:

```
infrastructure/monitoring/
├── docker-compose.monitoring-consolidated.yml
└── config/
    └── prometheus-consolidated.yml
```

### 4. Deployment Scripts

Unified deployment system:

```
scripts/
├── shared/
│   └── deployment_lib.sh              # Shared deployment functions
├── deploy-acgs-consolidated.sh        # Main deployment script
└── tools/
    └── claude_md_generator.py         # Documentation generator
```

## Usage Instructions

### Quick Start

1. **Deploy Development Environment**
   ```bash
   ./scripts/deploy-acgs-consolidated.sh
   ```

2. **Deploy Production Environment**
   ```bash
   ./scripts/deploy-acgs-consolidated.sh -e production
   ```

3. **Deploy Only Infrastructure**
   ```bash
   ./scripts/deploy-acgs-consolidated.sh -c infrastructure
   ```

### Detailed Usage

#### 1. Environment Deployment

**Development (with dev tools)**:
```bash
# Use the consolidated deployment script
./scripts/deploy-acgs-consolidated.sh -e development

# Or use Docker Compose directly
cd infrastructure/docker
docker-compose -f docker-compose.base-infrastructure.yml -f docker-compose.development.yml up -d
```

**Production (with monitoring)**:
```bash
# Full production deployment
./scripts/deploy-acgs-consolidated.sh -e production

# Or use Docker Compose directly
cd infrastructure/docker
docker-compose -f docker-compose.base-infrastructure.yml -f docker-compose.acgs-services.yml -f docker-compose.production-override.yml up -d
```

#### 2. Service Management

**Start specific components**:
```bash
# Start only infrastructure
./scripts/deploy-acgs-consolidated.sh -c infrastructure

# Start only services
./scripts/deploy-acgs-consolidated.sh -c services

# Start only monitoring
./scripts/deploy-acgs-consolidated.sh -c monitoring
```

**Stop services**:
```bash
# Stop all services
./scripts/deploy-acgs-consolidated.sh -a stop

# Stop specific components
./scripts/deploy-acgs-consolidated.sh -a stop -c services
```

**Check status**:
```bash
# Check all services
./scripts/deploy-acgs-consolidated.sh -a status

# Check specific components
./scripts/deploy-acgs-consolidated.sh -a status -c infrastructure
```

**View logs**:
```bash
# View all logs
./scripts/deploy-acgs-consolidated.sh -a logs

# View specific component logs
./scripts/deploy-acgs-consolidated.sh -a logs -c services
```

#### 3. Configuration Management

**Authentication Configuration**:
```bash
# Edit shared auth config
vim config/shared/auth_config.yml

# Apply changes by restarting services
./scripts/deploy-acgs-consolidated.sh -a restart -c services
```

**Environment Configuration**:
```bash
# Edit environment settings
vim config/shared/environment.yml

# Apply with environment variable
ENVIRONMENT=production ./scripts/deploy-acgs-consolidated.sh -a restart
```

#### 4. Monitoring

**Access Monitoring Services**:
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)
- **Alertmanager**: http://localhost:9093

**Start monitoring stack**:
```bash
cd infrastructure/monitoring
docker-compose -f docker-compose.monitoring-consolidated.yml up -d
```

#### 5. Documentation Generation

**Generate CLAUDE.md files**:
```bash
# Generate for single directory
python3 scripts/tools/claude_md_generator.py docs/

# Generate for all directories
python3 scripts/tools/claude_md_generator.py --all

# Force overwrite existing files
python3 scripts/tools/claude_md_generator.py --all --force
```

## Environment Variables

### Core Variables

```bash
# Environment selection
ENVIRONMENT=development|staging|production

# Database configuration
POSTGRES_USER=acgs_user
POSTGRES_PASSWORD=secure_password
POSTGRES_DB=acgs

# Redis configuration
REDIS_PASSWORD=secure_password

# Authentication
JWT_SECRET_KEY=your-secret-key
AUTH_SECRET_KEY=your-auth-secret

# Monitoring
GF_ADMIN_USER=admin
GF_ADMIN_PASSWORD=admin
```

### Development Variables

```bash
# Development-specific
DEBUG=true
LOG_LEVEL=DEBUG
SKIP_HEALTH_CHECK=false
```

### Production Variables

```bash
# Production-specific
WORKERS=4
DATABASE_POOL_SIZE=20
PROMETHEUS_RETENTION=30d
```

## Service Endpoints

### Core Services

| Service | Port | Health Check | Description |
|---------|------|-------------|-------------|
| auth_service | 8000 | /health | Authentication service |
| ac_service | 8001 | /health | Constitutional AI service |
| integrity_service | 8002 | /health | Integrity service |
| fv_service | 8003 | /health | Formal verification service |
| gs_service | 8004 | /health | Governance synthesis service |
| pgc_service | 8005 | /health | Policy governance service |
| ec_service | 8006 | /health | Evolutionary computation service |

### Infrastructure Services

| Service | Port | Description |
|---------|------|-------------|
| postgres | 5432 | PostgreSQL database |
| redis | 6379 | Redis cache |
| prometheus | 9090 | Metrics collection |
| grafana | 3000 | Visualization dashboard |
| alertmanager | 9093 | Alert management |

### Development Tools

| Service | Port | Description |
|---------|------|-------------|
| pgadmin | 5050 | PostgreSQL admin |
| redis-commander | 8081 | Redis admin |

## Migration from Old System

### 1. Stop Old Services

```bash
# Stop all existing services
docker-compose down
docker system prune -f
```

### 2. Update Environment Files

```bash
# Copy existing environment variables to new format
cp .env config/shared/.env

# Update references to use new service names
sed -i 's/old_service_name/new_service_name/g' config/shared/.env
```

### 3. Migrate Data

```bash
# Backup existing data
docker volume ls | grep postgres
docker volume ls | grep redis

# Data will be preserved in named volumes
```

### 4. Deploy New System

```bash
# Deploy with new consolidated approach
./scripts/deploy-acgs-consolidated.sh -e production
```

## Troubleshooting

### Common Issues

1. **Port conflicts**:
   ```bash
   # Check port usage
   netstat -tulpn | grep :8000
   
   # Stop conflicting services
   docker ps | grep :8000
   ```

2. **Health check failures**:
   ```bash
   # Check service logs
   ./scripts/deploy-acgs-consolidated.sh -a logs -c services
   
   # Check individual service health
   curl http://localhost:8000/health
   ```

3. **Configuration issues**:
   ```bash
   # Validate configuration
   ./scripts/deploy-acgs-consolidated.sh -d  # Dry run
   
   # Check constitutional hash
   grep -r "cdd01ef066bc6cf2" config/
   ```

### Health Check Commands

```bash
# Check all services
./scripts/deploy-acgs-consolidated.sh -a status

# Check specific service
curl -f http://localhost:8000/health

# Check infrastructure
docker-compose -f infrastructure/docker/docker-compose.base-infrastructure.yml ps
```

## Performance Targets

The consolidated system maintains the same performance targets:

- **P99 Latency**: <5ms (constitutional requirement)
- **Throughput**: >100 RPS (minimum operational standard)
- **Cache Hit Rate**: >85% (efficiency requirement)
- **Constitutional Compliance**: 100% (hash: cdd01ef066bc6cf2)

## Benefits of Consolidation

1. **Reduced Complexity**: 60+ compose files → ~6 files
2. **Improved Consistency**: Standardized configurations across environments
3. **Better Maintainability**: Shared libraries and templates
4. **Enhanced Monitoring**: Unified observability stack
5. **Simplified Deployment**: Single deployment script for all environments

## Constitutional Compliance

All consolidated components maintain constitutional hash `cdd01ef066bc6cf2` validation and ensure compliance with ACGS-2 requirements.

---

**Last Updated**: 2025-07-18 - Initial consolidation implementation