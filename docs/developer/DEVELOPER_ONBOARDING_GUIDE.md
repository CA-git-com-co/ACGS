# ACGS-2 Developer Onboarding Guide

**Constitutional Hash**: `cdd01ef066bc6cf2`

## Welcome to ACGS-2 Development

This comprehensive guide will help you set up your development environment and understand the ACGS-2 (Advanced Constitutional Governance System) architecture for effective contribution.

## Prerequisites Checklist

Before starting, ensure you have the following installed:

- [ ] **Docker & Docker Compose** (v20.10+)
- [ ] **Python 3.11+**
- [ ] **UV package manager** (preferred) or pip
- [ ] **Git** (v2.30+)
- [ ] **Rust 1.70+** (for blockchain components)
- [ ] **Node.js 18+** and **Bun** (for CLI services)
- [ ] **Anchor CLI** (for Solana development)

### Optional but Recommended
- [ ] **kubectl** (for Kubernetes development)
- [ ] **PostgreSQL client** (psql)
- [ ] **Redis CLI** (redis-cli)
- [ ] **VS Code** with Python and Rust extensions

## Quick Start (5 Minutes)

### 1. Clone and Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd ACGS-2

# Install dependencies (choose one method)
uv sync  # Preferred - handles all dependencies with lockfile
# OR: pip install -e ".[dev,test]"  # Standard installation
```

### 2. Start Development Environment

```bash
# Start all services in background
make dev-detached

# Verify all services are running
make health
```

Expected output:
```
✓ Constitutional AI (8001): Healthy
✓ Integrity Service (8002): Healthy
✓ API Gateway (8080): Healthy
✓ Governance Synthesis (8004): Healthy
```

### 3. Run Your First Test

```bash
# Run the test suite
python scripts/testing/orchestrator.py

# Or run a quick smoke test
pytest tests/unit/ -v -k "test_health"
```

🎉 **Congratulations!** If all tests pass, your development environment is ready.

## Development Environment Details

### Service Architecture Overview

ACGS-2 runs 9 core microservices:

| Service | Port | Purpose | Language/Framework |
|---------|------|---------|-------------------|
| Constitutional Core | 8001 | AI reasoning & formal verification | Python/FastAPI |
| Integrity Service | 8002 | Audit trail & compliance logging | Python/FastAPI |
| Governance Engine | 8004 | Policy synthesis & enforcement | Python/FastAPI |
| Evolutionary Computation | 8006 | Constitutional evolution tracking | Python/FastAPI |
| Agent HITL | 8008 | Human-in-the-loop decisions | Python/FastAPI |
| Audit Aggregator | 8015 | Centralized audit collection | Python/FastAPI |
| Authentication | 8016 | Multi-tenant JWT auth | Python/FastAPI |
| OpenCode CLI | 8020 | CLI integration service | TypeScript/Bun |
| API Gateway | 8080 | Load balancing & routing | HAProxy |

### Infrastructure Services

| Service | Port | Purpose |
|---------|------|---------|
| PostgreSQL | 5439 | Multi-tenant database |
| Redis | 6389 | Caching & sessions |
| Prometheus | 9090 | Metrics collection |
| Grafana | 3001 | Monitoring dashboards |
| OPA | 8181/8282 | Policy evaluation |

## Detailed Setup Instructions

### Option 1: UV (Recommended)

```bash
# Install UV if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all dependencies with lockfile
uv sync

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Option 2: Traditional pip

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e ".[dev,test]"
```

### Option 3: Development with AI Models

```bash
# For full AI/ML development (includes GPU support)
pip install -e ".[ai,dev,test]"

# For complete installation (all optional dependencies)
pip install -e ".[all]"
```

## Service-by-Service Development Setup

### 1. Constitutional Core Service

**Location**: `services/core/constitutional-core/`

```bash
cd services/core/constitutional-core

# Install service-specific dependencies
pip install -r requirements.txt

# Run the service locally
python app/main_simple.py

# Test the service
curl http://localhost:8001/health
```

**Key files to understand**:
- `app/main_simple.py` - Service entry point
- `app/constitutional/` - Constitutional AI logic
- `app/formal_verification/` - Z3 SMT solver integration

### 2. Integrity Service

**Location**: `services/platform_services/integrity/`

```bash
cd services/platform_services/integrity

# Start local development
python integrity_service/app/main.py

# Test audit functionality
curl -X POST http://localhost:8002/api/v1/audit/create \
  -H "Content-Type: application/json" \
  -d '{"event_type": "test", "event_data": {"test": true}, "tenant_id": "dev"}'
```

**Key features**:
- Cryptographic audit trails
- Multi-tenant audit isolation
- Hash chain integrity

### 3. Governance Engine

**Location**: `services/core/governance-engine/`

```bash
cd services/core/governance-engine

# Start the service
python app/main.py

# Test policy evaluation
curl -X POST http://localhost:8004/api/v1/policy/evaluate \
  -H "Content-Type: application/json" \
  -d '{"policy_type": "constitutional", "input": {"test": true}, "tenant_id": "dev"}'
```

**Key features**:
- OPA policy integration
- Policy synthesis
- Constitutional compliance checking

### 4. Blockchain Development (Optional)

**Location**: `services/blockchain/`

```bash
cd services/blockchain

# Install Anchor CLI if not installed
npm install -g @coral-xyz/anchor-cli

# Build blockchain programs
make build

# Run tests
make test

# Deploy to devnet
make deploy
```

**Key components**:
- Solana Anchor programs
- Rust client libraries
- Constitutional compliance for blockchain operations

## Common Development Workflows

### 1. Adding a New API Endpoint

```bash
# 1. Choose the appropriate service (e.g., constitutional-core)
cd services/core/constitutional-core

# 2. Add endpoint in app/api/routes.py
# 3. Add Pydantic schemas in app/schemas.py
# 4. Add business logic in app/constitutional/
# 5. Add tests in tests/

# 6. Test your changes
pytest tests/test_your_feature.py -v

# 7. Run integration tests
python scripts/testing/orchestrator.py --service constitutional-core
```

### 2. Database Schema Changes

```bash
# 1. Navigate to shared services
cd services/shared

# 2. Modify models in models/
# 3. Generate migration
alembic revision --autogenerate -m "Add new feature table"

# 4. Review the generated migration
alembic history --verbose

# 5. Apply migration
alembic upgrade head

# 6. Test with sample data
python -c "
from database.connection import get_db_session
# Test your changes here
"
```

### 3. Running Specific Test Categories

```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests
pytest tests/integration/ -v

# Performance tests
pytest tests/performance/ -v

# Constitutional compliance tests
pytest -m constitutional -v

# Test with coverage
pytest --cov=services --cov-report=html

# Test a specific service
python scripts/testing/orchestrator.py --service constitutional-core --test-type unit
```

### 4. Code Quality Workflow

```bash
# Format code automatically
ruff check --fix && ruff format
black services/ scripts/ tests/
isort services/ scripts/ tests/

# Type checking
mypy services/ scripts/ --strict

# Security scanning
bandit -r services/ scripts/

# Run all quality checks
python scripts/validation/validate_constitutional_compliance.py
```

## Development Environment Configuration

### Environment Variables

Create `.env.acgs` in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://acgs:acgs@localhost:5439/acgs
REDIS_URL=redis://localhost:6389/0

# Constitutional Compliance
CONSTITUTIONAL_HASH=cdd01ef066bc6cf2

# Service Configuration
ENVIRONMENT=development
LOG_LEVEL=DEBUG

# Multi-Tenant Configuration
DEFAULT_TENANT_ID=dev-tenant

# API Keys (for AI services)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GROQ_API_KEY=your_groq_key

# Monitoring
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
```

### Docker Compose Configurations

The project uses multiple Docker Compose files for different environments:

```bash
# Development with hot reload
make dev

# Development in background
make dev-detached

# Production environment
make prod-detached

# Development with monitoring
make dev-full

# MCP services only
make mcp
```

## Debugging and Troubleshooting

### Common Issues and Solutions

#### 1. Services Won't Start

```bash
# Check if ports are already in use
netstat -tulpn | grep :8001

# Check Docker containers
docker ps -a

# View service logs
make logs

# Restart specific service
docker-compose restart constitutional-core
```

#### 2. Database Connection Issues

```bash
# Check PostgreSQL is running
docker-compose ps postgresql

# Test database connection
psql -h localhost -p 5439 -U acgs -d acgs

# Check migrations
cd services/shared && alembic current
```

#### 3. Import Errors

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Reinstall dependencies
uv sync --force
```

#### 4. Constitutional Hash Validation Fails

```bash
# Verify constitutional hash is set
python -c "
from services.shared.configuration.settings import get_settings
print(f'Hash: {get_settings().constitutional_hash}')
"

# Run compliance validation
python scripts/validation/validate_constitutional_compliance.py
```

### Debugging Tools

#### 1. Service Health Monitoring

```bash
# Check all service health
make health

# Detailed health check
curl http://localhost:8001/health/detailed

# View metrics
curl http://localhost:8001/metrics
```

#### 2. Log Analysis

```bash
# View real-time logs
make logs

# Filter logs by service
docker-compose logs constitutional-core

# Search for errors
docker-compose logs | grep ERROR
```

#### 3. Performance Monitoring

```bash
# Check performance metrics
curl http://localhost:9090/api/v1/query?query=http_requests_total

# View Grafana dashboards
open http://localhost:3001  # admin/admin
```

## IDE Setup and Configuration

### VS Code Configuration

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "black",
    "editor.formatOnSave": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "files.associations": {
        "*.rego": "open-policy-agent"
    }
}
```

### Recommended VS Code Extensions

```json
{
    "recommendations": [
        "ms-python.python",
        "ms-python.black-formatter",
        "charliermarsh.ruff",
        "ms-python.mypy-type-checker",
        "tsandall.opa",
        "rust-lang.rust-analyzer",
        "ms-vscode.docker",
        "ms-kubernetes-tools.vscode-kubernetes-tools"
    ]
}
```

## Testing Your Development Environment

### 1. End-to-End Workflow Test

```python
# test_development_setup.py
import asyncio
import httpx

async def test_full_workflow():
    """Test complete ACGS workflow"""

    # Test constitutional validation
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8001/api/v1/constitutional/validate",
            json={
                "decision": {
                    "description": "Test development setup",
                    "context": {"domain": "test", "impact_level": "low"}
                },
                "tenant_id": "dev-tenant"
            }
        )

        assert response.status_code == 200
        result = response.json()
        assert result["constitutional_hash"] == "cdd01ef066bc6cf2"
        print("✓ Constitutional validation working")

        # Test audit logging
        audit_response = await client.post(
            "http://localhost:8002/api/v1/audit/create",
            json={
                "event_type": "development_test",
                "event_data": result,
                "tenant_id": "dev-tenant"
            }
        )

        assert audit_response.status_code == 200
        print("✓ Audit logging working")

        print("🎉 Development environment fully functional!")

if __name__ == "__main__":
    asyncio.run(test_full_workflow())
```

Run the test:
```bash
python test_development_setup.py
```

### 2. Performance Baseline Test

```bash
# Run performance tests to establish baseline
pytest tests/performance/ --benchmark-only -v

# Check if performance targets are met
python scripts/validation/validate_performance_targets.py
```

## Next Steps

### 1. Explore the Codebase

**Recommended exploration order**:

1. **Start with CLAUDE.md** - Overview of the entire system
2. **Services structure** - Understand the microservices architecture
3. **Shared utilities** - Learn common patterns and utilities
4. **API documentation** - Study the API design patterns
5. **Testing framework** - Understand the testing strategy

### 2. Make Your First Contribution

1. **Pick a small issue** - Look for "good first issue" labels
2. **Create a feature branch** - `git checkout -b feature/your-feature`
3. **Follow the coding standards** - Use ruff, black, and mypy
4. **Add tests** - Maintain >90% coverage
5. **Update documentation** - Keep docs in sync with code
6. **Submit a pull request** - Include constitutional hash in commits

### 3. Learn the Architecture Patterns

- **Constitutional Compliance**: How every operation validates against constitutional principles
- **Multi-Tenant Isolation**: Database and service-level tenant separation
- **Audit Trail**: Cryptographic logging of all operations
- **Policy Synthesis**: Dynamic policy generation and evaluation
- **Performance Monitoring**: Sub-5ms latency targets and monitoring

### 4. Advanced Development Topics

- **Formal Verification**: Z3 SMT solver integration for mathematical proofs
- **Blockchain Integration**: Solana Anchor program development
- **Multi-Agent Coordination**: Agent orchestration and consensus algorithms
- **Policy Language**: OPA Rego policy development
- **Performance Optimization**: Caching strategies and optimization patterns

## Getting Help

### 1. Documentation Resources

- **API Guide**: `docs/api/ACGS_API_COMPREHENSIVE_GUIDE.md`
- **Architecture Docs**: `docs/architecture/`
- **Deployment Guides**: `docs/deployment/`
- **Troubleshooting**: Search existing documentation

### 2. Development Support

- **Health Checks**: `make health` for quick status
- **Log Analysis**: `make logs` for real-time debugging
- **Test Suite**: `python scripts/testing/orchestrator.py` for comprehensive testing
- **Validation**: `python scripts/validation/validate_constitutional_compliance.py`

### 3. Community and Contribution

- Follow constitutional compliance requirements
- Maintain performance standards (P99 <5ms, >100 RPS)
- Include constitutional hash `cdd01ef066bc6cf2` in all contributions
- Write comprehensive tests and documentation

---

**Constitutional Hash**: `cdd01ef066bc6cf2`
**Last Updated**: 2025-01-08
**Guide Version**: 2.0.0

**Welcome to the ACGS-2 development community! 🚀**
