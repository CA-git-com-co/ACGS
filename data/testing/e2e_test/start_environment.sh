#!/bin/bash
# Lightweight test environment for e2e_test
# Constitutional Hash: cdd01ef066bc6cf2

export ACGS_ENV=e2e_test
export CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
export ACGS_TEST_MODE=true

# Start minimal services for testing
echo "Starting lightweight test environment: e2e_test"
echo "Constitutional Hash: cdd01ef066bc6cf2"

# Create test database if needed
if [ "postgresql_replica" = "sqlite_memory" ]; then
    export DATABASE_URL="sqlite:///:memory:"
else
    export DATABASE_URL="sqlite:///data/testing/e2e_test/test.db"
fi

# Set Redis configuration
export REDIS_URL="redis://localhost:6379/0"

echo "Environment e2e_test ready for testing"
