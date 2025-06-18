# ACGS-1 Test Execution Makefile

.PHONY: test test-unit test-integration test-e2e test-performance test-security test-coverage

# Run all tests
test:
	pytest tests/ -v

# Run unit tests
test-unit:
	pytest tests/unit/ -v -m unit

# Run integration tests  
test-integration:
	pytest tests/integration/ -v -m integration

# Run end-to-end tests
test-e2e:
	pytest tests/e2e/ -v -m e2e

# Run performance tests
test-performance:
	pytest tests/performance/ -v -m performance

# Run security tests
test-security:
	pytest tests/security/ -v -m security

# Generate coverage report
test-coverage:
	pytest tests/ --cov=services --cov=scripts --cov-report=html --cov-report=term

# Run Anchor program tests
test-anchor:
	cd blockchain && anchor test

# Run all tests including blockchain
test-all: test test-anchor

# Clean test artifacts
clean-test:
	rm -rf tests/coverage/
	rm -rf .pytest_cache/
	rm -rf .coverage
