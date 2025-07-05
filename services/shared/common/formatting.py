"""
Response formatting utilities for ACGS services.
"""

from typing import Any, Dict

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def format_response(data: Any, status: str = "success") -> Dict[str, Any]:
    """Format service response consistently."""
    return {
        "status": status,
        "data": data,
        "constitutional_hash": CONSTITUTIONAL_HASH
    }