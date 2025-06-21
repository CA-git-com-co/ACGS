# DGM Service Test Suite

Comprehensive testing framework for the Darwin Gödel Machine Service with >90% code coverage target.

## Overview

This test suite provides comprehensive testing for all DGM service components including:

- **Unit Tests**: Individual component testing with mocking
- **Integration Tests**: Service interaction testing
- **Constitutional Compliance Tests**: Governance validation testing
- **Performance Tests**: Load and benchmark testing
- **Security Tests**: Security vulnerability testing
- **End-to-End Tests**: Full workflow testing

## Test Structure

```
tests/
├── conftest.py                 # Test configuration and fixtures
├── test_basic.py              # Basic infrastructure tests
├── run_tests.py               # Test runner script
├── unit/                      # Unit tests
│   ├── core/                  # Core component tests
│   │   ├── test_dgm_engine.py
│   │   ├── test_constitutional_validator.py
│   │   └── test_performance_monitor.py
│   ├── api/                   # API endpoint tests
│   │   └── test_dgm_endpoints.py
│   ├── models/                # Database model tests
│   │   └── test_models.py
│   ├── auth/                  # Authentication tests
│   ├── database/              # Database tests
│   ├── monitoring/            # Monitoring tests
│   └── utils/                 # Utility tests
├── integration/               # Integration tests
├── e2e/                      # End-to-end tests
└── fixtures/                 # Test data fixtures
```

## Running Tests

### Prerequisites

1. Ensure you're in the DGM service directory:

   ```bash
   cd services/core/dgm-service
   ```

2. Activate the virtual environment:
   ```bash
   source ../../../.venv/bin/activate
   ```

### Basic Test Execution

Run all tests:

```bash
python tests/run_tests.py --all
```

Run specific test suites:

```bash
# Unit tests only
python tests/run_tests.py --unit

# Integration tests only
python tests/run_tests.py --integration

# Constitutional compliance tests
python tests/run_tests.py --constitutional

# Performance tests
python tests/run_tests.py --performance

# Security tests
python tests/run_tests.py --security
```

### Using pytest directly

Run all unit tests:

```bash
../../../.venv/bin/pytest tests/unit/ -v
```

Run specific test file:

```bash
../../../.venv/bin/pytest tests/test_basic.py -v
```

Run tests with coverage:

```bash
../../../.venv/bin/pytest tests/unit/ --cov=dgm_service --cov-report=html
```

Run tests with specific markers:

```bash
../../../.venv/bin/pytest -m unit -v
../../../.venv/bin/pytest -m constitutional -v
../../../.venv/bin/pytest -m performance -v
```

## Test Categories

### Unit Tests (`@pytest.mark.unit`)

Test individual components in isolation with comprehensive mocking:

- **DGM Engine**: Core improvement algorithms, bandit strategies, safety mechanisms
- **Constitutional Validator**: Compliance checking, governance validation
- **Performance Monitor**: Metrics collection, alerting, reporting
- **API Endpoints**: Request/response handling, validation, error handling
- **Database Models**: Data integrity, relationships, constraints
- **Authentication**: JWT validation, permissions, security

### Integration Tests (`@pytest.mark.integration`)

Test component interactions and service integrations:

- Database connectivity and operations
- External service communication (Auth, AC, GS services)
- Cache layer integration
- Message queue integration
- File system operations

### Constitutional Compliance Tests (`@pytest.mark.constitutional`)

Specialized tests for governance and constitutional compliance:

- Proposal validation against constitutional principles
- Execution compliance verification
- Audit trail integrity
- Democratic governance workflows
- Safety constraint enforcement

### Performance Tests (`@pytest.mark.performance`)

Performance and load testing:

- Response time benchmarks
- Throughput testing
- Memory usage profiling
- Concurrent request handling
- Database query performance

### Security Tests (`@pytest.mark.security`)

Security vulnerability testing:

- Authentication bypass attempts
- Authorization validation
- Input sanitization
- SQL injection prevention
- XSS protection
- Rate limiting

## Test Configuration

### Markers

Tests are categorized using pytest markers:

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.e2e` - End-to-end tests
- `@pytest.mark.constitutional` - Constitutional compliance tests
- `@pytest.mark.performance` - Performance tests
- `@pytest.mark.security` - Security tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.database` - Database-dependent tests

### Fixtures

Key test fixtures available:

- `test_db_session` - Test database session
- `test_client` - FastAPI test client
- `async_test_client` - Async HTTP test client
- `mock_dgm_engine` - Mocked DGM engine
- `mock_constitutional_validator` - Mocked validator
- `mock_performance_monitor` - Mocked monitor
- `test_data_factory` - Test data generation
- `temp_workspace` - Temporary file workspace

## Coverage Requirements

The test suite maintains >90% code coverage with the following targets:

- **Core Components**: >95% coverage
- **API Endpoints**: >90% coverage
- **Database Models**: >90% coverage
- **Authentication**: >95% coverage
- **Utilities**: >85% coverage

### Coverage Reports

Generate coverage reports:

```bash
../../../.venv/bin/pytest tests/unit/ --cov=dgm_service --cov-report=html --cov-report=term-missing
```

View HTML coverage report:

```bash
open htmlcov/index.html
```

## Test Data Management

### Factories

Use test data factories for consistent test data:

```python
def test_dgm_archive_creation(test_data_factory):
    archive_data = test_data_factory.create_dgm_archive(
        improvement_type="custom_optimization"
    )
    assert archive_data["improvement_type"] == "custom_optimization"
```

### Fixtures

Use fixtures for reusable test setup:

```python
@pytest.fixture
def sample_improvement_request():
    return {
        "target_services": ["gs-service"],
        "priority": "medium",
        "strategy_hint": "performance_optimization"
    }
```

## Continuous Integration

The test suite is designed for CI/CD integration:

### GitHub Actions

```yaml
- name: Run DGM Service Tests
  run: |
    cd services/core/dgm-service
    python tests/run_tests.py --all --parallel
```

### Test Reports

- JUnit XML reports for CI integration
- HTML coverage reports
- Performance benchmark reports
- Security scan reports

## Best Practices

### Writing Tests

1. **Use descriptive test names**: `test_dgm_engine_generates_valid_proposal_with_safety_constraints`
2. **Follow AAA pattern**: Arrange, Act, Assert
3. **Mock external dependencies**: Use `AsyncMock` for async operations
4. **Test edge cases**: Include boundary conditions and error scenarios
5. **Maintain test isolation**: Each test should be independent

### Test Organization

1. **Group related tests**: Use test classes for logical grouping
2. **Use appropriate markers**: Mark tests with relevant categories
3. **Keep tests focused**: One concept per test method
4. **Document complex tests**: Add docstrings for complex test scenarios

### Performance Considerations

1. **Use fast tests for development**: Mark slow tests appropriately
2. **Parallel execution**: Use `-n auto` for parallel test execution
3. **Database optimization**: Use in-memory databases for unit tests
4. **Mock heavy operations**: Mock expensive operations in unit tests

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure virtual environment is activated
2. **Database connection**: Check test database configuration
3. **Async test failures**: Verify `pytest-asyncio` is installed
4. **Coverage gaps**: Use `--cov-report=term-missing` to identify gaps

### Debug Mode

Run tests in debug mode:

```bash
../../../.venv/bin/pytest tests/unit/core/test_dgm_engine.py::TestDGMEngine::test_initialization -v -s --pdb
```

### Logging

Enable test logging:

```bash
../../../.venv/bin/pytest tests/ -v --log-cli-level=DEBUG
```

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure >90% coverage for new code
3. Add appropriate test markers
4. Update test documentation
5. Run full test suite before committing

## Test Metrics

Current test metrics:

- **Total Tests**: 50+ comprehensive tests
- **Coverage**: >90% target
- **Performance**: <30s full test suite execution
- **Reliability**: >99% test success rate
