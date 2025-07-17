# Contributing to ACGS-2

Welcome to the ACGS-2 (Adaptive Constitutional Governance System) project! This guide will help you get started with contributing to our advanced constitutional AI governance platform.

## 🏗️ Project Structure

ACGS-2 follows a microservices architecture with constitutional AI at its core:

```text
ACGS-2/
├── services/                   # 🏗️ Core Services & Platform
│   ├── core/                   # Constitutional AI, Policy Governance
│   ├── platform_services/     # Authentication, Integrity
│   └── shared/                 # Common utilities and middleware
├── blockchain/                 # 🔗 Solana/Anchor Programs (legacy)
├── config/                     # 🔧 Configuration files
├── scripts/                    # 🛠️ Automation and deployment scripts
├── tests/                      # 🧪 Comprehensive test suites
├── docs/                       # 📚 Documentation
└── tools/                      # 🛠️ Development and analysis tools
```

## 🚀 Quick Start

### Prerequisites

- **Python** 3.10+ (3.11 or 3.12 recommended for all backend services)
- **uv** (recommended) or **pip** for Python dependency management
- **Git** for version control
- **Redis** 6.0+ (for caching and session storage)
- **PostgreSQL** 13+ (for persistent data storage)
- **Node.js** 18+ (optional, for frontend development)
- **Docker** (optional, for containerized development)
- **PostgreSQL** 15+ (for database services)
- **Redis** 7+ (for caching and session management)
- **Docker** 24.0+ & **Docker Compose** (for containerization)

### Development Environment Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/CA-git-com-co/ACGS.git
   cd ACGS-2
   ```

2. **Set up Python environment** (recommended approach):

   ```bash
   # Using uv package manager (recommended)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source ~/.bashrc

   # Create virtual environment and install dependencies
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -e .
   uv pip install -e .[dev,test]
   ```

3. **Alternative: Traditional Python setup**:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-test.txt
   ```

4. **Set up pre-commit hooks**:

   ```bash
   pre-commit install
   ```

5. **Configure environment variables**:

   ```bash
   cp config/testconfig/environments/development.env config/environments/development.env
   # Edit config/environments/development.env with your API keys and database URLs
   ```

5. **Build Anchor programs**:
   ```bash
   cd blockchain
   anchor build
   cd ..
   ```

## 📦 Dependency Management

ACGS-2 uses a standardized approach to dependency management with **pyproject.toml** as the primary source of truth.

### Adding Dependencies

1. **Core dependencies** (required for runtime):
   ```bash
   # Add to pyproject.toml [project.dependencies]
   uv add package-name>=version
   ```

2. **Development dependencies**:
   ```bash
   # Add to pyproject.toml [project.optional-dependencies.dev]
   uv add --dev package-name>=version
   ```

3. **Test dependencies**:
   ```bash
   # Add to pyproject.toml [project.optional-dependencies.test]
   uv add --group test package-name>=version
   ```

### Dependency Guidelines

- **Always pin minimum versions** with `>=` for compatibility
- **Use version ranges sparingly** and only for security-critical packages
- **Update requirements.txt** to match pyproject.toml for deployment compatibility
- **Test all dependency changes** with the full test suite
- **Document breaking changes** in commit messages

### Updating Dependencies

```bash
# Update all dependencies
uv sync --upgrade

# Update specific package
uv add package-name>=new-version

# Check for outdated packages
uv pip list --outdated
```

## 🎯 Development Workflows

### Blockchain Development

**Location**: `blockchain/programs/`

1. **Program Development**:

   ```bash
   cd blockchain
   anchor build                    # Build all programs
   anchor test                     # Run tests
   anchor deploy --provider.cluster devnet  # Deploy to devnet
   ```

2. **Adding New Programs**:
   - Create program in `blockchain/programs/your-program/`
   - Update `blockchain/Anchor.toml`
   - Add tests in `blockchain/tests/`

### Backend Service Development

**Location**: `services/core/` or `services/platform/`

1. **Core Services** (Constitutional AI, Governance Synthesis, etc.):

   ```bash
   cd services/core/your-service/service_directory
   # Using UV (recommended)
   uv sync && uv run uvicorn app.main:app --reload --port 800X

   # Alternative: Traditional
   python -m uvicorn app.main:app --reload --port 800X
   ```

2. **Platform Services** (Authentication, Integrity, etc.):

   ```bash
   cd services/platform/your-service
   # Using UV (recommended)
   uv sync && uv run uvicorn app.main:app --reload --port 800X

   # Alternative: Traditional
   python -m uvicorn app.main:app --reload --port 800X
   ```

3. **Service Communication**:
   - Use `services/shared/` for common utilities
   - Follow port conventions: Auth (8000), AC (8001), Integrity (8002), FV (8003), GS (8004), PGC (8005), EC (8006), DGM (8007)
   - Implement health checks at `/health` endpoint
   - Use UV package manager for dependency management

### Frontend Development

**Location**: `applications/`

1. **Governance Dashboard**:

   ```bash
   cd project
   npm run dev                     # Development server
   npm run build                   # Production build
   ```

2. **Component Development**:
   - Follow React best practices
   - Use TypeScript for type safety
   - Integrate with Anchor client libraries

### Integration Development

**Location**: `integrations/`

1. **Quantumagi Bridge**: Blockchain-backend integration
2. **AlphaEvolve Engine**: AI governance integration

### DGM Development

**Location**: `services/core/dgm-service/`

1. **Darwin Gödel Machine Service** (Port 8007):

   ```bash
   cd services/core/dgm-service
   # Using UV (recommended)
   uv sync && uv run python -m dgm_service.main

   # Alternative: Traditional
   python -m dgm_service.main
   ```

2. **Event-Driven Architecture**:
   - NATS message broker integration for real-time events
   - Service mesh communication (Istio/Linkerd)
   - LSU interface for self-evolving systems
   - Conservative bandit algorithms for safe exploration
   - Archive-backed evolution loops with performance tracking

## 🧪 Testing Guidelines

### Test Organization

- **Unit Tests**: `tests/unit/`
- **Integration Tests**: `tests/integration/`
- **End-to-End Tests**: `tests/e2e/`
- **Performance Tests**: `tests/performance/`

### Running Tests

```bash
# Anchor program tests
cd blockchain && anchor test

# Python service tests (using UV recommended)
uv run pytest tests/unit/
uv run pytest tests/integration/

# Alternative: Traditional Python testing
python -m pytest tests/unit/
python -m pytest tests/integration/

# Frontend tests
cd project && npm test

# Full test suite
./run_tests.sh
```

### Test Requirements (Phase 1 Achieved)

- **Overall Coverage**: 82.1% achieved (Target: >80%) ✅
- **Core Services**: Comprehensive unit and integration tests ✅
- **Constitutional Compliance**: 100% validation with hash `cdd01ef066bc6cf2` ✅
- **Performance Tests**: Sub-5ms P99 latency validation ✅
- **Security Tests**: Complete security validation suite ✅
- **End-to-End**: Complete governance workflow validation ✅

### Current Test Infrastructure

```bash
# Run comprehensive test suite (82.1% coverage achieved)
python scripts/test_runner.py --coverage

# Run constitutional compliance tests
python tests/policies/test_constitutional_policies.py

# Run performance validation (sub-5ms P99 latency)
python performance/validation/latency_validation_suite.py

# Run security tests
python -m pytest tests/security/ -v
```

## 📋 Code Review Guidelines

### Service Boundaries

1. **Blockchain Components**: Focus on Solana/Anchor best practices
2. **Core Services**: Ensure constitutional governance compliance
3. **Platform Services**: Maintain security and scalability standards
4. **Frontend**: Prioritize user experience and accessibility

### Review Checklist

- [ ] Code follows project structure conventions
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] Security considerations addressed
- [ ] Performance impact assessed
- [ ] Constitutional compliance maintained

## 🔧 Development Tools

### Available Scripts

- `./run_tests.sh` - Run comprehensive test suite
- `./scripts/health_check.sh` - Check service health
- `./blockchain/quantumagi-deployment/deploy_quantumagi_devnet.sh` - Deploy to Solana devnet

### IDE Configuration

- **VS Code**: Recommended extensions for Rust, Python, TypeScript
- **Rust Analyzer**: For Anchor program development
- **Python Language Server**: For backend service development

## 🚀 Deployment Process

### Development Deployment

1. **Local Development**:

   ```bash
   docker-compose -f infrastructure/docker/docker-compose.yml up -d
   ```

2. **Solana Devnet**:
   ```bash
   cd blockchain/quantumagi-deployment
   ./deploy_quantumagi_devnet.sh
   ```

### Production Deployment

- Follow deployment guides in `docs/deployment/`
- Use CI/CD pipelines in `.github/workflows/`
- Ensure all tests pass before deployment

## 🎯 Performance Targets (Phase 1 Achieved)

### Current Performance Metrics ✅

- **Response Times**: Sub-5ms P99 latency for WINA operations (Target: <2s for 95% of requests)
- **Test Coverage**: 82.1% overall coverage (Target: >80%)
- **Cache Hit Rate**: >85% for policy decisions
- **Lookup Performance**: O(1) lookup for cached constitutional compliance
- **Constitutional Compliance**: 100% validation with hash `cdd01ef066bc6cf2`
- **Concurrent Users**: >1000 simultaneous governance actions
- **Availability**: >99.5% uptime target

### Infrastructure Specifications

- **PostgreSQL Database**: Port 5439 (production-ready configuration)
- **Redis Cache**: Port 6389 (optimized for >85% cache hit rates)
- **Authentication Service**: Port 8016 (JWT-based with RBAC)
- **Core Services**: Ports 8002-8005 and 8010
- <!-- Constitutional Hash: cdd01ef066bc6cf2 --> (validated across all services)

## 🤝 Community Guidelines

### Communication

- **GitHub Issues**: Bug reports and feature requests
- **Pull Requests**: Code contributions with detailed descriptions
- **Discussions**: Architecture and design conversations

### Code of Conduct

- Respectful and inclusive communication
- Focus on constitutional governance principles
- Collaborative problem-solving approach
- Commitment to transparency and accountability

## 📚 Additional Resources

- **Architecture Overview**: `docs/architecture/REORGANIZED_ARCHITECTURE.md`
- **API Documentation**: `docs/api/`
- **Deployment Guides**: `docs/deployment/`
- **Developer Guides**: `docs/development/`

## 📚 Additional Resources

- **Architecture Overview**: `docs/architecture/REORGANIZED_ARCHITECTURE.md`
- **API Documentation**: `docs/api/`
- **Deployment Guides**: `docs/deployment/`
- **Developer Guides**: `docs/development/`

## Related Information

For a broader understanding of the ACGS platform and its components, refer to:

- [ACGS Service Architecture Overview](../../docs/ACGS_SERVICE_OVERVIEW.md)
- [ACGS Documentation Implementation and Maintenance Plan - Completion Report](../../docs/ACGS_DOCUMENTATION_IMPLEMENTATION_COMPLETION_REPORT.md)
- [ACGE Strategic Implementation Plan - 24 Month Roadmap](../../docs/ACGE_STRATEGIC_IMPLEMENTATION_PLAN_24_MONTH.md)
- [ACGE Testing and Validation Framework](../../docs/ACGE_TESTING_VALIDATION_FRAMEWORK.md)
- [ACGE Cost Analysis and ROI Projections](../../docs/ACGE_COST_ANALYSIS_ROI_PROJECTIONS.md)
- [ACGS Comprehensive Task Completion - Final Report](../architecture/ACGS_COMPREHENSIVE_TASK_COMPLETION_FINAL_REPORT.md)
- [ACGS-Claudia Integration Architecture Plan](../architecture/ACGS_CLAUDIA_INTEGRATION_ARCHITECTURE.md)
- [ACGS Implementation Guide](../deployment/ACGS_IMPLEMENTATION_GUIDE.md)
- [ACGS-PGP Operational Deployment Guide](../deployment/ACGS_PGP_OPERATIONAL_DEPLOYMENT_GUIDE.md)
- [ACGS-PGP Troubleshooting Guide](../deployment/ACGS_PGP_TROUBLESHOOTING_GUIDE.md)
- [ACGS-PGP Setup Guide](../deployment/ACGS_PGP_SETUP_GUIDE.md)
- [Service Status Dashboard](../operations/SERVICE_STATUS.md)
- [ACGS Configuration Guide](../configuration/README.md)
- [ACGS-2 Technical Specifications - 2025 Edition](../TECHNICAL_SPECIFICATIONS_2025.md)

## 🆘 Getting Help

1. **Documentation**: Check relevant docs in `docs/` directory
2. **Issues**: Search existing GitHub issues
3. **Discussions**: Start a GitHub discussion for questions
4. **Code Review**: Request review from maintainers

Thank you for contributing to ACGS-1! Together, we're building the future of constitutional governance on the blockchain.

## Implementation Status

- ✅ **Constitutional Hash Validation**: Active enforcement of `cdd01ef066bc6cf2`
- 🔄 **Performance Monitoring**: Continuous validation of targets
- ✅ **Documentation Standards**: Compliant with ACGS-2 requirements
- 🔄 **Cross-Reference Validation**: Ongoing link integrity maintenance

**Overall Status**: 🔄 IN PROGRESS - Systematic enhancement implementation
