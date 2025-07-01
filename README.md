# ACGS-2 - Adaptive Constitutional Governance System

## Overview
ACGS-2 is a comprehensive governance system implementing constitutional AI processing, policy governance, and Darwin Gödel Machine mechanisms for adaptive decision-making.

## Architecture
- **Core Services**: Constitutional AI, Policy Governance, Evolutionary Computation
- **Shared Components**: Security validation, optimized caching, business rules
- **Platform Services**: Authentication, monitoring, storage abstraction

## Getting Started

### Prerequisites
- Python 3.9+ (see `pyproject.toml` for exact version, e.g., >=3.10)
- Poetry or a recent version of pip that supports `pyproject.toml`

### Installation
Clone the repository and navigate into the project directory:
```bash
git clone <repository-url> # Replace <repository-url> with the actual URL
cd ACGS-2
```

Install the project in editable mode along with its test and development dependencies:
```bash
pip install -e .[test,dev]
```
This command installs all necessary packages for running the application, tests, linters, and other development tools, as defined in `pyproject.toml`.

### Environment Configuration
Copy `config/services/backups/.env` as a template and set the required API keys
via environment variables. The file is excluded from version control, so
configure keys locally or through your CI/CD secrets.

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=services --cov-report=html
```

## Development

### Code Quality
- This project uses **Black** for code formatting, **Ruff** for linting (including import sorting), and **Mypy** for type checking.
- Configurations for these tools are in `pyproject.toml`.
- Follow the code quality guidelines in `docs/code_quality_guidelines.md`.
- Use pre-commit hooks to automatically format and lint your code before committing: `pre-commit install`.
- Run tests before committing.

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
