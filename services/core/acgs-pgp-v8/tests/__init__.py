"""
Test Suite for ACGS-PGP v8

Comprehensive testing framework for Quantum-Inspired Semantic Fault Tolerance System.
"""

# Test configuration
TEST_CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
TEST_REDIS_URL = "redis://localhost:6379/1"  # Use different DB for tests
TEST_DATABASE_URL = "postgresql://acgs_user:acgs_password@localhost:5432/acgs_test_db"

# Test data constants
SAMPLE_POLICY_REQUEST = {
    "title": "Test Data Privacy Policy",
    "description": "Comprehensive test policy for data privacy and protection",
    "stakeholders": ["citizens", "government", "businesses"],
    "constitutional_principles": ["privacy", "transparency", "accountability"],
    "priority": "high",
    "context": {
        "domain": "data_protection",
        "jurisdiction": "federal",
        "urgency": "normal",
    },
}

SAMPLE_ERROR_DATA = {
    "message": "Constitutional compliance validation failed",
    "context": {
        "service": "acgs-pgp-v8",
        "operation": "policy_generation",
        "constitutional_hash": TEST_CONSTITUTIONAL_HASH,
    },
    "stack_trace": "Traceback (most recent call last)...",
}


# Test utilities
def get_test_config():
    """Get test configuration for ACGS-PGP v8 components."""
    return {
        "constitutional_hash": TEST_CONSTITUTIONAL_HASH,
        "redis_url": TEST_REDIS_URL,
        "database_url": TEST_DATABASE_URL,
        "gs_service_url": "http://localhost:8004",
        "pgc_service_url": "http://localhost:8005",
        "auth_service_url": "http://localhost:8000",
    }
