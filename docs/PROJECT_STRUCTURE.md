# ACGS-2 Project Structure

This document provides a comprehensive overview of the ACGS-2 project structure and organization.

## Root Directory Structure

```
ACGS-2/
├── services/                   # Core application services
├── scripts/                    # Automation and utility scripts
├── tests/                      # Comprehensive test suites
├── docs/                       # Documentation
├── config/                     # Configuration files
├── tools/                      # Development and analysis tools
├── infrastructure/             # Infrastructure and deployment
├── blockchain/                 # Blockchain components (legacy)
├── migrations/                 # Database migrations
├── requirements.txt            # Python dependencies
├── requirements-test.txt       # Test dependencies
├── pyproject.toml             # Project configuration
├── README.md                  # Project overview
└── CONTRIBUTING.md            # Contribution guidelines
```

## Services Directory

The `services/` directory contains the core ACGS-2 microservices:

### Core Services (`services/core/`)

#### Constitutional AI (`services/core/constitutional_ai/`)
- **Purpose**: Constitutional compliance validation and analysis
- **Port**: 8002
- **Key Components**:
  - Constitutional validation service
  - Human-in-the-loop integration
  - Democratic governance mechanisms
  - Conflict resolution systems

#### Policy Governance (`services/core/policy_governance/`)
- **Purpose**: Policy management and enforcement
- **Port**: 8010
- **Key Components**:
  - Policy synthesis engine
  - Real-time compliance engine
  - WINA enforcement optimizer
  - Quantum policy enforcement

#### Governance Synthesis (`services/core/governance_synthesis/`)
- **Purpose**: Advanced governance workflow orchestration
- **Port**: 8005
- **Key Components**:
  - Multi-model consensus
  - QEC error correction
  - Performance optimization
  - Stakeholder engagement

#### Formal Verification (`services/core/formal_verification/`)
- **Purpose**: Mathematical verification of policies
- **Port**: 8004
- **Key Components**:
  - Z3 solver integration
  - Formal property verification
  - Mathematical proof generation

#### Evolutionary Computation (`services/core/evolutionary_computation/`)
- **Purpose**: Adaptive system evolution
- **Port**: 8003
- **Key Components**:
  - Genetic algorithms
  - Evolution oversight
  - Adaptive mechanisms

### Platform Services (`services/platform_services/`)

#### Authentication (`services/platform_services/authentication/`)
- **Purpose**: User authentication and authorization
- **Port**: 8016
- **Key Components**:
  - JWT token management
  - Role-based access control
  - Agent authentication

#### Integrity (`services/platform_services/integrity/`)
- **Purpose**: Data integrity and audit trails
- **Port**: 8003
- **Key Components**:
  - Integrity validation
  - Audit logging
  - Data verification

### Shared Components (`services/shared/`)

Common utilities and middleware used across services:

- **WINA Framework**: Weight Informed Neuron Activation optimization
- **Security Validation**: Input validation and security checks
- **Caching**: Redis-based caching mechanisms
- **Middleware**: Common middleware components
- **Utilities**: Shared utility functions

## Scripts Directory

The `scripts/` directory contains automation and utility scripts:

### Core Scripts
- `lint.py`: Code quality and linting automation
- `test_runner.py`: Comprehensive test execution
- `test_cleanup.py`: Test suite cleanup and organization
- `code_hygiene.py`: Code hygiene and style corrections

### Specialized Scripts
- `acgs_monitoring_dashboard.py`: Real-time monitoring
- `comprehensive_load_test.py`: Performance testing
- `comprehensive_security_scan.py`: Security analysis
- `validate_service_startup.py`: Service validation

## Tests Directory

Comprehensive test organization:

```
tests/
├── unit/                      # Unit tests
│   ├── constitutional_ai/     # Constitutional AI tests
│   ├── policy_governance/     # Policy governance tests
│   ├── governance_synthesis/  # Governance synthesis tests
│   └── shared/               # Shared component tests
├── integration/              # Integration tests
├── e2e/                     # End-to-end tests
├── performance/             # Performance tests
├── security/                # Security tests
├── load/                    # Load testing
└── fixtures/                # Test fixtures and data
```

## Configuration

### Environment Configuration
- `config/test.env`: Test environment template
- `config/production.env`: Production configuration template
- `config/development.env`: Development configuration

### Service Configuration
- Individual service configurations in respective service directories
- Shared configuration in `services/shared/config/`

## Documentation

### Core Documentation
- `README.md`: Project overview and quick start
- `CONTRIBUTING.md`: Contribution guidelines
- `docs/PROJECT_STRUCTURE.md`: This document
- `docs/API_DOCUMENTATION.md`: API reference
- `docs/DEPLOYMENT_GUIDE.md`: Deployment instructions

### Technical Documentation
- Service-specific documentation in each service directory
- Architecture decision records (ADRs)
- Performance benchmarks and targets

## Development Tools

### Code Quality
- **Ruff**: Fast Python linter
- **Black**: Code formatter
- **MyPy**: Type checking
- **Bandit**: Security analysis
- **Pre-commit**: Git hooks

### Testing Tools
- **Pytest**: Test framework
- **Coverage**: Test coverage analysis
- **Locust**: Load testing
- **Factory Boy**: Test data generation

### Monitoring and Analysis
- **Prometheus**: Metrics collection
- **Grafana**: Monitoring dashboards
- **OpenTelemetry**: Distributed tracing

## Naming Conventions

### Services
- Use underscores for service names: `constitutional_ai`, `policy_governance`
- Avoid hyphens in Python module names
- Use descriptive, clear names

### Files and Directories
- Python files: `snake_case.py`
- Test files: `test_*.py` or `*_test.py`
- Configuration files: `lowercase.extension`
- Documentation: `UPPERCASE.md` for important docs, `lowercase.md` for others

### Code
- Classes: `PascalCase`
- Functions and variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private members: `_leading_underscore`

## Port Allocation

Standard port allocation for services:

- **8002**: Constitutional AI Service
- **8003**: Integrity Service / Evolutionary Computation
- **8004**: Formal Verification Service
- **8005**: Governance Synthesis Service
- **8010**: Policy Governance Service
- **8016**: Authentication Service

## Dependencies

### Core Dependencies
- **FastAPI**: Web framework
- **SQLAlchemy**: Database ORM
- **Redis**: Caching and session storage
- **PostgreSQL**: Primary database
- **Pydantic**: Data validation

### AI/ML Dependencies
- **Transformers**: Language models
- **Torch**: Deep learning framework
- **NumPy/SciPy**: Scientific computing
- **Anthropic/OpenAI**: LLM APIs

### Development Dependencies
- **Pytest**: Testing framework
- **Ruff/Black**: Code quality
- **MyPy**: Type checking
- **Pre-commit**: Git hooks

This structure supports the ACGS-2 architecture while maintaining clear separation of concerns and enabling scalable development.
