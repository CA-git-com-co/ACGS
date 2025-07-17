"""
Blockchain Audit Service Application Package
Constitutional Hash: cdd01ef066bc6cf2
"""

__version__ = "1.0.0"
__author__ = "ACGS-2 Development Team"
__description__ = "Blockchain audit and logging service for ACGS-2"

from .models.schemas import CONSTITUTIONAL_HASH

__all__ = [
    "__version__",
    "__author__", 
    "__description__",
    "CONSTITUTIONAL_HASH"
]