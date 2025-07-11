"""
ACGS-2 Test Configuration
Constitutional Hash: cdd01ef066bc6cf2
"""

import pytest
from pathlib import Path

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

@pytest.fixture(scope="session")
def constitutional_hash():
    """Provide constitutional hash for all tests"""
    return CONSTITUTIONAL_HASH

