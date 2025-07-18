<!-- Constitutional Hash: cdd01ef066bc6cf2 -->

# ACGS Team Documentation - New Repository Structure

## 🎯 Executive Summary

The ACGS codebase has been successfully reorganized from a monolithic structure into 7 focused repositories. This document provides comprehensive guidance for development teams on working with the new structure.

## 📋 Quick Migration Guide

### For Developers

**Old Way:**
```bash
git clone https://github.com/ACGS/ACGS-monolith.git
cd ACGS-monolith
# Work on everything in one place
```

**New Way:**
```bash
# Clone the workspace
git clone https://github.com/ACGS/acgs-workspace.git
cd acgs-workspace

# Or clone individual repositories
git clone https://github.com/ACGS/acgs-core.git
git clone https://github.com/ACGS/acgs-platform.git
# ... etc
```

## 🏗️ New Repository Structure

| Repository | Purpose | Size | Team Ownership | Key Technologies |
|------------|---------|------|----------------|------------------|
| **[acgs-core](https://github.com/ACGS/acgs-core)** | Constitutional AI services | 19MB | AI/ML Team | Python, FastAPI, PyTorch |
| **[acgs-platform](https://github.com/ACGS/acgs-platform)** | Platform & shared services | 5.3MB | Platform Team | Python, Redis, PostgreSQL |
| **[acgs-blockchain](https://github.com/ACGS/acgs-blockchain)** | Blockchain integration | 2.2MB | Blockchain Team | Rust, Solana, Anchor |
| **[acgs-models](https://github.com/ACGS/acgs-models)** | AI model services | 2.1MB | ML Engineering | Python, WINA, Model Routing |
| **[acgs-applications](https://github.com/ACGS/acgs-applications)** | Frontend & CLI tools | 2.3MB | Frontend Team | React, TypeScript, Python CLI |
| **[acgs-infrastructure](https://github.com/ACGS/acgs-infrastructure)** | Infrastructure as Code | 5.9MB | DevOps Team | Docker, K8s, Terraform |
| **[acgs-tools](https://github.com/ACGS/acgs-tools)** | Development tools | 20MB | All Teams | Python, Shell scripts |

## 🔄 Development Workflows

### Working on a Single Component

```bash
# For core AI development
git clone https://github.com/ACGS/acgs-core.git
cd acgs-core
uv sync
# Make changes, test, commit
git push
```

### Cross-Repository Development

```bash
# Clone workspace for integrated development
git clone https://github.com/ACGS/acgs-workspace.git
cd acgs-workspace

# All repositories are included as subdirectories
cd acgs-core      # Work on core services
cd ../acgs-platform  # Work on platform services

# Run integration tests across repositories
python scripts/run_integration_tests.py
```

### Setting Up Development Environment

#### Option 1: Individual Repository
```bash
git clone https://github.com/ACGS/acgs-[repository].git
cd acgs-[repository]

# Python repositories
uv sync --all-extras
uv run pytest

# Node.js repositories  
pnpm install
pnpm test

# Rust repositories
cargo build
cargo test
```

#### Option 2: Full Workspace
```bash
git clone https://github.com/ACGS/acgs-workspace.git
cd acgs-workspace
python scripts/setup_workspace.py
```

## 🏢 Team Responsibilities

### AI/ML Team → acgs-core
**Repositories**: `acgs-core`, `acgs-models`

**Key Components**:
- Constitutional AI service
- Formal verification service  
- Governance synthesis
- Policy governance
- Evolutionary computation
- Multi-agent coordination
- Worker agents (ethics, legal, operational)

**Development Setup**:
```bash
git clone https://github.com/ACGS/acgs-core.git
cd acgs-core
uv sync --all-extras
uv run pytest tests/
```

### Platform Team → acgs-platform
**Repositories**: `acgs-platform`

**Key Components**:
- Authentication service (JWT, MFA, OAuth)
- Integrity verification service
- Shared utilities (blackboard, service mesh, database, Redis)

**Development Setup**:
```bash
git clone https://github.com/ACGS/acgs-platform.git
cd acgs-platform
uv sync --all-extras
uv run pytest tests/
```

### Blockchain Team → acgs-blockchain
**Repositories**: `acgs-blockchain`

**Key Components**:
- Anchor programs (quantumagi-core, appeals, logging)
- Client libraries (Python, Rust)
- Solana integration

**Development Setup**:
```bash
git clone https://github.com/ACGS/acgs-blockchain.git
cd acgs-blockchain
cargo build
cargo test
pnpm install  # For TypeScript tests
pnpm test
```

### Frontend Team → acgs-applications
**Repositories**: `acgs-applications`

**Key Components**:
- MCP Inspector web application (React)
- Gemini CLI interface
- OpenCode adapter
- Example applications

**Development Setup**:
```bash
git clone https://github.com/ACGS/acgs-applications.git
cd acgs-applications
pnpm install
pnpm dev      # Start development server
pnpm test
```

### DevOps Team → acgs-infrastructure
**Repositories**: `acgs-infrastructure`

**Key Components**:
- Docker configurations (30+ compose files)
- Kubernetes manifests
- Terraform definitions
- Monitoring (Prometheus, Grafana)
- Security policies

**Development Setup**:
```bash
git clone https://github.com/ACGS/acgs-infrastructure.git
cd acgs-infrastructure
terraform init
terraform plan
kubectl apply --dry-run=client -f kubernetes/
```

## 🔧 Common Development Tasks

### Adding a New Feature

#### Single Repository Feature
```bash
# 1. Clone the relevant repository
git clone https://github.com/ACGS/acgs-[repository].git
cd acgs-[repository]

# 2. Create feature branch
git checkout -b feature/new-feature

# 3. Develop and test
# ... make changes ...
uv run pytest  # or appropriate test command

# 4. Create pull request
git push -u origin feature/new-feature
# Open PR on GitHub
```

#### Cross-Repository Feature
```bash
# 1. Clone workspace
git clone https://github.com/ACGS/acgs-workspace.git
cd acgs-workspace

# 2. Create feature branches in affected repositories
cd acgs-core
git checkout -b feature/new-feature-core

cd ../acgs-platform  
git checkout -b feature/new-feature-platform

# 3. Develop and test integration
python scripts/run_integration_tests.py

# 4. Create coordinated pull requests
# Push each repository and reference related PRs
```

### Running Tests

#### Repository-Specific Tests
```bash
# Python repositories
uv run pytest tests/ -v --cov

# Node.js repositories
pnpm test --coverage

# Rust repositories
cargo test --verbose

# Infrastructure
terraform plan
kubectl apply --dry-run=client -f .
```

#### Integration Tests
```bash
cd acgs-workspace
python scripts/run_integration_tests.py
```

### Debugging Issues

#### Service Dependencies
```bash
# Check which services depend on each other
cat acgs-workspace.json | jq '.repositories[].dependencies'

# Start dependent services first
cd acgs-platform && uv run python -m services.platform_services.authentication &
cd acgs-core && uv run python -m services.core.constitutional_ai &
```

#### Cross-Repository Issues
```bash
# Use workspace for debugging interactions
cd acgs-workspace
python scripts/comprehensive_validation.py
```

## 📊 CI/CD Pipeline Overview

Each repository has its own CI/CD pipeline with:

### Automated Testing
- **Code Quality**: Linting, formatting, type checking
- **Security**: Vulnerability scanning with Trivy
- **Coverage**: Test coverage reporting
- **Integration**: Cross-service compatibility tests

### Deployment Stages
1. **Pull Request**: Run tests, security scans
2. **Staging**: Deploy to staging environment (develop branch)
3. **Production**: Deploy to production (main branch)

### Pipeline Commands
```bash
# Trigger CI/CD manually
gh workflow run ci-cd.yml

# Check pipeline status
gh run list --repo ACGS/acgs-core

# View pipeline logs
gh run view [run-id] --log
```

## 🔍 Monitoring & Observability

### Repository-Specific Monitoring

Each repository includes monitoring configurations:

```bash
# View health endpoints
curl https://api.acgs.ai/acgs-core/health
curl https://api.acgs.ai/acgs-platform/health

# Check metrics
curl https://metrics.acgs.ai/prometheus/api/v1/query?query=up{service="acgs-core"}
```

### Cross-Repository Tracing

```bash
# Distributed tracing across services
# View trace in Jaeger UI: https://tracing.acgs.ai
# Correlation ID: trace requests across repositories
```

## 🚨 Emergency Procedures

### Rollback Procedures

#### Single Repository Rollback
```bash
git revert [commit-hash]
git push
# Trigger automated deployment
```

#### Cross-Repository Rollback
```bash
cd acgs-workspace
python scripts/emergency_rollback.py --version [stable-version]
```

### Incident Response
1. **Identify Affected Repository**: Check monitoring dashboards
2. **Isolate Issue**: Use repository-specific logs and metrics
3. **Apply Fix**: Deploy to affected repository only
4. **Verify**: Run integration tests to ensure system stability

## 📚 Documentation Links

### Repository Documentation
- [acgs-core README](https://github.com/ACGS/acgs-core/blob/main/README.md)
- [acgs-platform README](https://github.com/ACGS/acgs-platform/blob/main/README.md)
- [acgs-blockchain README](https://github.com/ACGS/acgs-blockchain/blob/main/README.md)
- [acgs-models README](https://github.com/ACGS/acgs-models/blob/main/README.md)
- [acgs-applications README](https://github.com/ACGS/acgs-applications/blob/main/README.md)
- [acgs-infrastructure README](https://github.com/ACGS/acgs-infrastructure/blob/main/README.md)
- [acgs-tools README](https://github.com/ACGS/acgs-tools/blob/main/README.md)

### API Documentation
- [Core Services API](https://docs.acgs.ai/core/)
- [Platform Services API](https://docs.acgs.ai/platform/)
- [Blockchain API](https://docs.acgs.ai/blockchain/)

### Operational Guides
- [Deployment Guide](../../infrastructure/kubernetes/DEPLOYMENT_GUIDE.md.backup)
- [Monitoring Setup](../../infrastructure/load-balancer/MONITORING_INTEGRATION.md)
- [Security Guidelines](../../infrastructure/monitoring/SECURITY_GUIDE.md)

## 🔄 Migration Timeline

### Phase 1: Immediate (Completed)
- ✅ Repository reorganization
- ✅ CI/CD pipeline setup
- ✅ Documentation updates

### Phase 2: This Week
- 🔄 Team onboarding and training
- 🔄 GitHub repository setup and permissions
- 🔄 Production deployment testing

### Phase 3: Next 2 Weeks  
- 📋 Full production migration
- 📋 Monitoring dashboard setup
- 📋 Performance optimization

## ❓ FAQ

### Q: Can I still work on multiple services simultaneously?
**A**: Yes! Use the workspace approach or clone multiple repositories. The integration testing ensures compatibility.

### Q: How do I handle dependencies between repositories?
**A**: Dependencies are managed through the workspace configuration. Use local development links during development and proper versioning for production.

### Q: What if I need to make changes across multiple repositories?
**A**: Create coordinated feature branches, reference related PRs in commit messages, and use integration testing to validate changes.

### Q: How do deployment dependencies work?
**A**: The CI/CD pipelines respect dependency order. Platform services deploy before core services that depend on them.

### Q: Where do I report issues that span multiple repositories?
**A**: Use the [acgs-workspace](https://github.com/ACGS/acgs-workspace) repository for cross-cutting issues and integration problems.

## 📞 Support & Contact

- **General Questions**: #acgs-dev Slack channel
- **Repository Issues**: Create issues in specific repository
- **Integration Issues**: [acgs-workspace issues](https://github.com/ACGS/acgs-workspace/issues)
- **Emergency**: Page on-call DevOps team



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

---

*This documentation is maintained by the ACGS DevOps team. Last updated: 2025-01-02*