# ACGS Deployment Quick Start Guide

**Version**: 2.0  
**Last Updated**: 2025-06-23  
**Tested On**: Ubuntu 22.04, macOS 13+, Windows 11

## 🎯 Overview

This guide provides step-by-step instructions for deploying ACGS-1 in development, staging, and production environments.

## 📋 Prerequisites

### System Requirements

- **OS**: Ubuntu 22.04+, macOS 13+, or Windows 11
- **RAM**: 16GB minimum, 32GB recommended
- **Storage**: 50GB free space
- **Network**: Stable internet connection

### Required Software

```bash
# Core Requirements
- Rust 1.81.0+ (blockchain development)
- Python 3.11+ (backend services)
- Node.js 18+ (frontend application)
- PostgreSQL 15+ (database)
- Redis 7+ (caching)
- Docker 24.0+ & Docker Compose (containerization)

# Package Managers
- UV (Python dependency management)
- npm/yarn/pnpm (Node.js packages)
- cargo (Rust packages)

# Blockchain Tools
- Solana CLI v1.18.22+
- Anchor Framework v0.29.0+
```

## 🚀 Quick Start (Development)

### 1. Environment Setup

```bash
# Clone repository
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS

# Install UV package manager
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc

# Setup Python environment
uv sync
```

### 2. Database Setup

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Run migrations
cd migrations
python -m alembic upgrade head
cd ..
```

### 3. Start Core Services

```bash
# Authentication Service (Port 8000)
cd services/platform/authentication/auth_service
uv sync && uv run uvicorn app.main:app --reload --port 8000 &

# Constitutional AI Service (Port 8001)
cd services/core/constitutional-ai/ac_service
uv sync && uv run uvicorn app.main:app --reload --port 8001 &

# Integrity Service (Port 8002)
cd services/platform/integrity/integrity_service
uv sync && uv run uvicorn app.main:app --reload --port 8002 &

# Formal Verification Service (Port 8003)
cd services/core/formal-verification/fv_service
uv sync && uv run uvicorn main:app --reload --port 8003 &

# Governance Synthesis Service (Port 8004)
cd services/core/governance-synthesis/gs_service
uv sync && uv run uvicorn app.main:app --reload --port 8004 &

# Policy Governance Service (Port 8005)
cd services/core/policy-governance/pgc_service
uv sync && uv run uvicorn app.main:app --reload --port 8005 &

# Evolutionary Computation Service (Port 8006)
cd services/core/evolutionary-computation
uv sync && uv run uvicorn app.main:app --reload --port 8006 &

# Darwin Gödel Machine Service (Port 8007)
cd services/core/dgm-service
uv sync && uv run python -m dgm_service.main &
```

### 4. Start Frontend Application

```bash
cd project
npm install
npm run dev
```

### 5. Deploy Blockchain (Optional)

```bash
cd blockchain
anchor build
anchor deploy --provider.cluster devnet
```

## 🐳 Docker Deployment

### Development Environment

```bash
# Start all services
docker-compose -f infrastructure/docker/docker-compose.yml up -d

# Check service health
curl http://localhost:8000/health  # Auth Service
curl http://localhost:8001/health  # Constitutional AI
curl http://localhost:8002/health  # Integrity
curl http://localhost:8003/health  # Formal Verification
curl http://localhost:8004/health  # Governance Synthesis
curl http://localhost:8005/health  # Policy Governance
curl http://localhost:8006/health  # Evolutionary Computation
```

### Production Environment

```bash
# Production deployment
docker-compose -f docker-compose.production.yml up -d

# Monitor logs
docker-compose logs -f
```

## 🔧 Configuration

### Environment Variables

Create `.env` file in project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://acgs:acgs@localhost:5432/acgs_db
REDIS_URL=redis://localhost:6379

# Service Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# API Keys (replace with actual keys)
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key

# Blockchain Configuration
SOLANA_CLUSTER=devnet
CONSTITUTION_HASH=cdd01ef066bc6cf2

# Security Configuration
JWT_SECRET=your_jwt_secret
ENCRYPTION_KEY=your_encryption_key
```

### Service Ports

| Service | Port | Health Check |
|---------|------|--------------|
| Authentication | 8000 | `/health` |
| Constitutional AI | 8001 | `/health` |
| Integrity | 8002 | `/health` |
| Formal Verification | 8003 | `/health` |
| Governance Synthesis | 8004 | `/health` |
| Policy Governance | 8005 | `/health` |
| Evolutionary Computation | 8006 | `/health` |
| Darwin Gödel Machine | 8007 | `/health` |

## ✅ Verification

### Health Checks

```bash
# Quick health check script
./scripts/comprehensive_health_check.py

# Individual service checks
curl -f http://localhost:8000/health || echo "Auth service down"
curl -f http://localhost:8001/health || echo "AC service down"
curl -f http://localhost:8002/health || echo "Integrity service down"
curl -f http://localhost:8003/health || echo "FV service down"
curl -f http://localhost:8004/health || echo "GS service down"
curl -f http://localhost:8005/health || echo "PGC service down"
curl -f http://localhost:8006/health || echo "EC service down"
curl -f http://localhost:8007/health || echo "DGM service down"
```

### Functional Tests

```bash
# Run integration tests
python -m pytest tests/integration/ -v

# Test blockchain deployment
cd blockchain && anchor test

# Test frontend
cd project && npm test
```

## 🚨 Troubleshooting

### Common Issues

**Service won't start**
```bash
# Check logs
docker-compose logs service-name

# Check port conflicts
netstat -tulpn | grep :8001
```

**Database connection failed**
```bash
# Verify PostgreSQL is running
docker-compose ps postgres

# Test connection
psql -h localhost -U acgs -d acgs_db
```

**Frontend build errors**
```bash
# Clear cache and reinstall
cd project
rm -rf node_modules package-lock.json
npm install
```

### Performance Issues

**High memory usage**
- Reduce service replicas in Docker Compose
- Increase Docker memory limits
- Monitor with `docker stats`

**Slow response times**
- Check database query performance
- Monitor Redis cache hit rates
- Review service logs for bottlenecks

## 📊 Monitoring

### Access Dashboards

- **Frontend**: http://localhost:3000
- **Grafana**: http://localhost:3001
- **Prometheus**: http://localhost:9090
- **API Documentation**: http://localhost:8001/docs

### Key Metrics

- Service response times: <500ms
- Database connections: <100 active
- Memory usage: <80% of allocated
- CPU usage: <70% average

## 🔄 Updates and Maintenance

### Regular Updates

```bash
# Pull latest changes
git pull origin main

# Update dependencies
uv sync
cd project && npm install

# Restart services
docker-compose restart
```

### Backup Procedures

```bash
# Database backup
./scripts/backup_database.sh

# Configuration backup
tar -czf config_backup.tar.gz config/ .env
```

## 📞 Support

- **Documentation**: [docs/](../README.md)
- **Issues**: [GitHub Issues](https://github.com/CA-git-com-co/ACGS/issues)
- **Health Checks**: `./scripts/comprehensive_health_check.py`
- **Emergency Procedures**: [docs/operations/EMERGENCY_PROCEDURES.md](operations/EMERGENCY_PROCEDURES.md)

---

**Next Steps**: After successful deployment, see [OPERATIONAL_RUNBOOK.md](OPERATIONAL_RUNBOOK.md) for ongoing maintenance procedures.
