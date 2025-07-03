"""
ACGS E2E Test Implementations

This package contains specific test implementations for different aspects
of the ACGS system, organized by functional area.
"""

# Test categories
__test_categories__ = [
    "health",           # Basic health and connectivity tests
    "constitutional",   # Constitutional AI and compliance tests
    "hitl",            # Human-in-the-Loop testing
    "performance",     # Performance and load testing
    "security",        # Security and authentication tests
    "integration",     # Service integration tests
    "governance",      # Multi-agent governance tests
    "infrastructure",  # Infrastructure component tests
]

# Export test discovery helper
def get_test_modules():
    """Get all test modules for discovery."""
    return __test_categories__
