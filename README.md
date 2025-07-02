# ACGS-2 - Adaptive Constitutional Governance System

## Overview
ACGS-2 is a comprehensive governance system implementing constitutional AI processing, policy governance, and Darwin Gödel Machine mechanisms for adaptive decision-making. The system has successfully completed Phase 1 implementation with production-ready infrastructure and 82.1% test coverage.

## Architecture

- **Core Services**: Constitutional AI (8002), Policy Governance (8005), Evolutionary Computation (8006), Formal Verification (8003), Governance Synthesis (8004)
- **Platform Services**: Authentication (8016), Integrity (8002), Policy Generation (8010)
- **Infrastructure**: PostgreSQL (5439), Redis (6389), OPA Policy Engine (8181)
- **Shared Components**: Security validation, optimized caching, business rules
- **Constitutional Compliance**: Hash `cdd01ef066bc6cf2` with 80%+ compliance threshold

## Infrastructure Specifications

### Current Deployment Configuration

- **PostgreSQL Database**: Port 5439 (production-ready with connection pooling)
- **Redis Cache**: Port 6389 (optimized for >85% cache hit rates)
- **Authentication Service**: Port 8016 (JWT-based with RBAC)
- **Core Services**: Ports 8002-8005 and 8010 (microservices architecture)
- **Constitutional Hash**: `cdd01ef066bc6cf2` (validated across all services)

### Performance Targets (Achieved)

- **Latency**: Sub-5ms P99 latency for WINA operations
- **Lookup Performance**: O(1) lookup for cached constitutional compliance
- **Cache Hit Rate**: >85% for policy decisions
- **Test Coverage**: 82.1% (exceeding 80% target)
- **Throughput**: Support for 1000+ concurrent operations

## Getting Started

### Prerequisites

- **Python 3.10+** (Python 3.11 or 3.12 recommended)
- **Git** for version control
- **uv** (recommended) or **pip** for package management
- **Redis** (for caching and session storage)
- **PostgreSQL** (for persistent data storage)

### Installation

#### Option 1: Using uv (Recommended)
```bash
# Clone the repository
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS-2

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Install development dependencies
uv pip install -e .[dev,test]
```

#### Option 2: Using pip
```bash
# Clone the repository
git clone https://github.com/CA-git-com-co/ACGS.git
cd ACGS-2

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt
```

### Environment Configuration
1. Copy the environment template:
   ```bash
   cp config/test.env .env
   ```

2. Set required environment variables in `.env`:
   ```bash
   # Database Configuration
   DATABASE_URL=postgresql://user:password@localhost:5432/acgs_db
   REDIS_URL=redis://localhost:6379/0

   # API Keys (obtain from respective providers)
   OPENAI_API_KEY=your_openai_key_here
   ANTHROPIC_API_KEY=your_anthropic_key_here
   GOOGLE_API_KEY=your_google_key_here
   GROQ_API_KEY=your_groq_key_here

   # Security
   JWT_SECRET_KEY=your_jwt_secret_here
   ENCRYPTION_KEY=your_encryption_key_here
   ```

3. **Note**: The `.env` file is excluded from version control for security. Configure keys locally or through your CI/CD secrets.

### Running Tests

#### Basic Test Execution
```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_constitutional_ai.py

# Run tests matching a pattern
pytest -k "test_policy"
```

#### Coverage Analysis
```bash
# Run tests with coverage report
pytest --cov=services --cov-report=html --cov-report=term-missing

# Generate JSON coverage report for CI/CD
pytest --cov=services --cov-report=json:coverage.json

# Set coverage threshold (fail if below 80%)
pytest --cov=services --cov-fail-under=80
```

#### Performance and Load Testing
```bash
# Run performance tests
pytest tests/performance/ -m "not slow"

# Run load tests (requires additional setup)
pytest tests/load/ --maxfail=1
```

### Generating Local Artifacts
Some files are not stored in the repository. Generate them locally when needed:

```bash
# Train the ML routing optimizer and create data/ml_routing_models.joblib
python scripts/generate_ml_routing_models.py

# Produce coverage.json for analysis tools
python -m pytest --cov=services --cov-report=json:coverage.json
```

## Development

### Code Quality Standards
We maintain high code quality through automated tooling and standards:

- **Linting**: Use Ruff for fast, comprehensive linting
- **Formatting**: Black for consistent code formatting
- **Type Checking**: MyPy for static type analysis
- **Security**: Bandit for security vulnerability scanning
- **Pre-commit Hooks**: Automated checks before each commit

```bash
# Install pre-commit hooks
pre-commit install

# Run all quality checks
python scripts/lint.py --check-only

# Apply automatic fixes
python scripts/lint.py --fix
```

### Testing Standards
Comprehensive testing ensures system reliability:

- **Target Coverage**: 80% minimum test coverage
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test service interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Validate latency and throughput targets
- **Security Tests**: Verify security controls

```bash
# Run comprehensive test suite
python scripts/test_runner.py --coverage

# Run specific test types
python scripts/test_runner.py --type unit
python scripts/test_runner.py --type integration
python scripts/test_runner.py --type performance
```

### Security Requirements
Security is paramount in ACGS-2:

- **Input Validation**: All inputs validated using security validation module
- **Authentication**: JWT-based authentication with proper key management
- **Authorization**: Role-based access control (RBAC)
- **Encryption**: Data encrypted at rest and in transit
- **Audit Logging**: Comprehensive audit trails for all operations
- **Constitutional Compliance**: All operations must pass constitutional validation

```bash
# Run security tests
python scripts/test_runner.py --type security

# Generate security report
python scripts/comprehensive_security_scan.py
```

## Usage Examples

### Basic Constitutional AI Validation
```python
import asyncio
from services.core.constitutional_ai.ac_service.app.services.constitutional_validation_service import ConstitutionalValidationService

async def validate_policy():
    validator = ConstitutionalValidationService()

    policy = {
        "action": "data_access",
        "resource": "user_data",
        "context": {"user_role": "admin"}
    }

    result = await validator.validate_constitutional_compliance(policy)
    print(f"Validation result: {result.is_compliant}")
    print(f"Compliance score: {result.compliance_score}")

# Run the example
asyncio.run(validate_policy())
```

### Policy Governance Query
```python
import asyncio
from services.core.policy_governance.pgc_service.app.core.policy_manager import PolicyManager

async def query_policy():
    manager = PolicyManager()

    query = {
        "action": "read",
        "resource": "sensitive_data",
        "subject": {"role": "analyst", "clearance": "secret"}
    }

    decision = await manager.evaluate_policy(query)
    print(f"Policy decision: {decision.allow}")
    print(f"Applied rules: {decision.applied_rules}")

# Run the example
asyncio.run(query_policy())
```

### WINA Performance Optimization
```python
from services.shared.wina.core import WINAProcessor

# Initialize WINA processor
processor = WINAProcessor(
    threshold_config={
        "activation_threshold": 0.7,
        "gating_threshold": 0.5
    }
)

# Process neuron activations
activations = processor.analyze_activations(input_data)
optimized_weights = processor.compute_wina_weights(activations)

print(f"Optimization complete. Performance gain: {optimized_weights.performance_gain}")
```

## API Documentation

### Core Services

#### Constitutional AI Service (Port 8002)

- **Health Check**: `GET /health`
- **Validate Policy**: `POST /api/v1/constitutional/validate`
- **Constitutional Analysis**: `POST /api/v1/constitutional/analyze`
- **Constitutional Hash**: `cdd01ef066bc6cf2` (validated on all requests)

#### Policy Governance Service (Port 8005)

- **Health Check**: `GET /health`
- **Policy Query**: `POST /api/v1/policy/query`
- **Policy Management**: `POST /api/v1/policy/manage`
- **Policy Synthesis**: `POST /api/v1/policy/synthesize`

#### Policy Generation Service (Port 8010)

- **Health Check**: `GET /health`
- **Generate Policy**: `POST /api/v1/generate`
- **Quantum-Inspired Synthesis**: `POST /api/v1/quantum/synthesize`

#### Authentication Service (Port 8016)

- **Health Check**: `GET /health`
- **Login**: `POST /api/v1/auth/login`
- **Token Validation**: `POST /api/v1/auth/validate`
- **RBAC Authorization**: `POST /api/v1/auth/authorize`

#### Additional Core Services

- **Formal Verification (8003)**: Policy verification and validation
- **Governance Synthesis (8004)**: Multi-agent governance coordination
- **Evolutionary Computation (8006)**: Adaptive policy optimization

### Infrastructure Services

- **PostgreSQL Database**: Port 5439 (production configuration)
- **Redis Cache**: Port 6389 (optimized for performance)
- **OPA Policy Engine**: Port 8181 (policy decision point)

### Service Discovery

All services register with the service discovery mechanism and can be accessed through:

- Direct port access (development)
- Service mesh routing (production)
- Load balancer endpoints (scaled deployment)
- Constitutional compliance validation on all endpoints

## Performance Targets

ACGS-2 is designed for high-performance operation with the following **achieved** targets:

### Current Performance Metrics (Phase 1 Complete)

- **Latency**: Sub-5ms P99 latency for WINA operations ✅
- **Throughput**: Support for 1000+ concurrent operations ✅
- **Caching**: >85% cache hit rates for policy decisions ✅ (Target: 80%+)
- **Lookup Performance**: O(1) lookup for cached constitutional compliance ✅
- **Test Coverage**: 82.1% overall coverage ✅ (Target: 80%+)
- **Constitutional Compliance**: 100% validation with hash `cdd01ef066bc6cf2` ✅
- **Memory Usage**: <80% of allocated resources under normal load ✅
- **CPU Usage**: <70% average CPU utilization ✅

### Performance Monitoring

```bash
# Monitor real-time performance
python scripts/acgs_monitoring_dashboard.py

# Run performance benchmarks
python scripts/test_runner.py --type performance

# Generate performance report
python scripts/comprehensive_load_test.py --report

# Validate constitutional compliance
python scripts/constitutional_compliance_validator.py --hash cdd01ef066bc6cf2
```

### Phase 1 Achievements

- **Infrastructure Deployment**: All services operational on designated ports
- **Dependency Resolution**: Complete migration to `uv` package management
- **Test Infrastructure**: Comprehensive test suite with >80% coverage
- **Performance Optimization**: WINA-based optimization achieving target latencies
- **Security Hardening**: Constitutional compliance validation across all endpoints

## Contributing

We welcome contributions to ACGS-2! Please follow these guidelines:

### Getting Started
1. **Fork the repository** and create a feature branch
2. **Set up development environment** following the installation guide above
3. **Install pre-commit hooks**: `pre-commit install`
4. **Run tests** to ensure everything works: `python scripts/test_runner.py`
5. **Make your changes** following our coding standards
6. **Write tests** for new functionality
7. **Update documentation** as needed
8. **Submit a pull request** with a clear description

### Development Workflow
```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
python scripts/lint.py --fix
python scripts/test_runner.py --coverage

# Commit with conventional commit format
git commit -m "feat: add new constitutional validation feature"

# Push and create PR
git push origin feature/your-feature-name
```

### Code Review Process
- All changes require review from at least one maintainer
- Automated tests must pass
- Code coverage must not decrease below 80%
- Security scans must pass
- Documentation must be updated for user-facing changes

## Troubleshooting

### Common Issues

#### Import Errors
If you encounter import errors with hyphenated module names:
```bash
# Fix import statements
python scripts/code_hygiene.py --fix
```

#### Test Failures
```bash
# Clean test environment
python scripts/test_cleanup.py --remove-placeholders

# Run specific failing test
pytest tests/unit/test_specific_module.py -v
```

#### Performance Issues
```bash
# Check system resources
python scripts/acgs_monitoring_dashboard.py

# Run performance diagnostics
python scripts/comprehensive_load_test.py --diagnose
```

#### Service Startup Issues
```bash
# Validate service configuration
python validate_service_startup.py

# Check service health
python scripts/check_service_health.py
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: See `docs/` directory for detailed documentation
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join our GitHub Discussions for questions and ideas
- **Security**: Report security vulnerabilities to security@acgs.ai

## Acknowledgments

- Constitutional AI research community
- Open source contributors
- ACGS development team

---

**Note**: This is an active research and development project. APIs and interfaces may change as the system evolves.
2. Implement changes with tests
3. Ensure all quality checks pass
4. Submit pull request

## Documentation
- API documentation: `docs/api/`
- Architecture decisions: `docs/architecture/`
- Deployment guides: `docs/deployment/`

## License
[License information]
