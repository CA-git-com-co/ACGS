# ACGS-2 - Adaptive Constitutional Governance System

## Overview
ACGS-2 is a comprehensive governance system implementing constitutional AI processing, policy governance, and Darwin Gödel Machine mechanisms for adaptive decision-making.

## Architecture
- **Core Services**: Constitutional AI, Policy Governance, Evolutionary Computation
- **Shared Components**: Security validation, optimized caching, business rules
- **Platform Services**: Authentication, monitoring, storage abstraction

## Getting Started

### Prerequisites
- Python 3.9+
- Required dependencies (see requirements.txt)

### Installation
```bash
git clone <repository-url>
cd ACGS-2
pip install -r requirements.txt
```

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=services --cov-report=html
# Generate JSON coverage report
python -m pytest --cov=services --cov-report=json:coverage.json
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

### Code Quality
- Follow the code quality guidelines in `docs/code_quality_guidelines.md`
- Use pre-commit hooks: `pre-commit install`
- Run tests before committing

### Testing
- Maintain 80% test coverage
- Write unit tests for all public functions
- Include integration tests for component interactions

### Security
- All inputs must be validated using the security validation module
- Follow secure coding practices
- Regular security audits required

## Performance Targets
- Sub-5ms P99 latency for WINA operations
- O(1) lookup performance for cached operations
- 80%+ cache hit rates
- Support for 1000+ concurrent operations

## Contributing
1. Create feature branch
2. Implement changes with tests
3. Ensure all quality checks pass
4. Submit pull request

## Documentation
- API documentation: `docs/api/`
- Architecture decisions: `docs/architecture/`
- Deployment guides: `docs/deployment/`

## License
[License information]
