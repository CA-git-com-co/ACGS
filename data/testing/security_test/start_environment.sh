#!/bin/bash
# Lightweight test environment for security_test
# Constitutional Hash: cdd01ef066bc6cf2

export ACGS_ENV=security_test
export CONSTITUTIONAL_HASH=cdd01ef066bc6cf2
export ACGS_TEST_MODE=true

# Start minimal services for testing
echo "Starting lightweight test environment: security_test"
echo "Constitutional Hash: cdd01ef066bc6cf2"

# Create test database if needed
if [ "postgresql_encrypted" = "sqlite_memory" ]; then
    export DATABASE_URL="sqlite:///:memory:"
else
    export DATABASE_URL="sqlite:///data/testing/security_test/test.db"
fi

# Set Redis configuration
export REDIS_URL="redis://localhost:6379/0"

echo "Environment security_test ready for testing"
