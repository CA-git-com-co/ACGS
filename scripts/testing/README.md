# ACGS Unified Testing Framework
Constitutional Hash: cdd01ef066bc6cf2

## Overview

The ACGS Unified Testing Framework consolidates all test runners into a single, comprehensive orchestrator with consistent configuration, reporting, and execution patterns.

## Features

- **Unified Test Orchestration**: Single entry point for all test types
- **Parallel Execution**: Non-critical tests can run in parallel
- **Constitutional Compliance**: Built-in constitutional hash validation
- **Service Health Checking**: Automatic service availability verification
- **Comprehensive Reporting**: JSON and text output formats
- **Coverage Integration**: Automatic coverage collection and analysis
- **Flexible Filtering**: Run specific test suites or categories
- **Fail-Fast Mode**: Stop on critical test failures
- **Legacy Migration Support**: Tools to migrate from old test runners

## Quick Start

```bash
# List available test suites
python3 scripts/cli/test.py --list

# Run all tests
python3 scripts/cli/test.py --all

# Run specific test suite
python3 scripts/cli/test.py --suite unit_tests

# Run with parallel execution
python3 scripts/cli/test.py --all --parallel

# Run only critical tests
python3 scripts/cli/test.py --critical-only

# Run with coverage and save results
python3 scripts/cli/test.py --with-coverage --output results.json
```

## Available Test Suites

| Suite | Description | Tags |
|-------|-------------|------|
| `constitutional_compliance` | Constitutional compliance validation | critical |
| `unit_tests` | Unit tests with coverage analysis | coverage |
| `integration_tests` | Service integration tests | |
| `performance_tests` | Performance benchmarks | |
| `security_tests` | Security hardening tests | |
| `multi_tenant_tests` | Multi-tenant isolation tests | |
| `e2e_tests` | End-to-end workflow tests | |

## Architecture

- **`orchestrator.py`**: Main test orchestrator with suite management
- **`cli/test.py`**: Command-line interface for easy access
- **`migrate_legacy_runners.py`**: Migration tools for legacy scripts
- **Core Integration**: Uses shared utilities from `scripts/core/`

## Migration from Legacy Scripts

The framework replaces these legacy test runners:

- `run_comprehensive_tests.py` → `--all`
- `run_improved_tests.py` → `--with-coverage`
- `run_integration_tests.py` → `--suite integration_tests`
- `run_e2e_with_coverage.py` → `--suite e2e_tests`
- `run_testing_suite.py` → `--all --parallel`

Use the migration tool for assistance:

```bash
# Generate migration guide
python3 scripts/testing/migrate_legacy_runners.py --generate-guide

# Create shell aliases
python3 scripts/testing/migrate_legacy_runners.py --create-aliases

# Backup legacy scripts
python3 scripts/testing/migrate_legacy_runners.py --backup-legacy legacy_backup/
```

## Advanced Usage

### Custom Test Suite Configuration

```python
from scripts.testing import ACGSTestOrchestrator, TestSuiteConfig

# Create custom suite
custom_suite = TestSuiteConfig(
    name="custom_tests",
    description="Custom test suite",
    command=["python", "-m", "pytest", "custom_tests/"],
    timeout=600,
    critical=True
)

# Register and run
orchestrator = ACGSTestOrchestrator(Path.cwd())
orchestrator.register_custom_suite(custom_suite)
```

### Programmatic Usage

```python
import asyncio
from scripts.testing import ACGSTestOrchestrator

async def run_tests():
    orchestrator = ACGSTestOrchestrator(project_root)
    orchestrator.register_standard_suites()
    
    result = await orchestrator.run_all_suites(
        suite_filter=["unit_tests", "integration_tests"],
        parallel=True,
        fail_fast=True
    )
    
    return result.overall_success

success = asyncio.run(run_tests())
```

## Output Formats

### Text Output
Human-readable summary with test results, metrics, and status.

### JSON Output
Structured data with complete test results, coverage data, and metrics:

```json
{
  "total_suites": 7,
  "passed_suites": 6,
  "failed_suites": 1,
  "success_rate": 85.7,
  "total_duration_ms": 45230,
  "results": [...]
}
```

## Integration with CI/CD

The unified framework integrates seamlessly with CI/CD pipelines:

```yaml
# Example GitHub Actions usage
- name: Run ACGS Tests
  run: |
    python3 scripts/cli/test.py --all --parallel --fail-fast \
      --format json --output test-results.json
```

## Constitutional Compliance

All test execution maintains constitutional compliance with hash `cdd01ef066bc6cf2`:

- Constitutional hash validation in all outputs
- Service availability checking includes constitutional verification
- Test results include constitutional compliance metadata
- Built-in audit logging with constitutional context

## Performance Targets

The framework enforces ACGS performance targets:

- **P99 Latency**: <5ms for constitutional validation
- **Throughput**: >100 RPS for concurrent operations  
- **Cache Hit Rate**: ≥85% for constitutional decisions
- **Test Coverage**: ≥80% for unit tests

## Support

For questions or issues:

1. Check CLI help: `python3 scripts/cli/test.py --help`
2. Review orchestrator documentation in `orchestrator.py`
3. Use migration tools for transitioning from legacy scripts
4. Validate setup: `python3 scripts/testing/migrate_legacy_runners.py --validate`

---
*ACGS Unified Testing Framework - Constitutional Hash: cdd01ef066bc6cf2*