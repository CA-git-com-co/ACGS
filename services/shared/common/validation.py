"""
Response validation utilities for ACGS services.
"""

from typing import Any

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def validate_response(response_data: dict[str, Any]) -> bool:
    """Validate service response format."""
    required_fields = ["status"]
    return all(field in response_data for field in required_fields)
