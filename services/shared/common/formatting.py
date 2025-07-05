"""
Response formatting utilities for ACGS services.
"""

from typing import Any

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def format_response(data: Any, status: str = "success") -> dict[str, Any]:
    """Format service response consistently."""
    return {"status": status, "data": data, "constitutional_hash": CONSTITUTIONAL_HASH}
