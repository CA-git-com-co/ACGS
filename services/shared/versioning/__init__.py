"""
ACGS-1 API Versioning Framework

This module provides comprehensive API versioning capabilities for all ACGS-1 services,
building upon the existing robust API infrastructure with semantic versioning,
backward compatibility, and lifecycle management.
"""

from .response_transformers import (
    CompatibilityTransformer,
    ResponseTransformer,
    VersionedResponseBuilder,
)
from .version_manager import (
    APIVersion,
    DeprecatedVersionError,
    UnsupportedVersionError,
    VersionCompatibility,
    VersionManager,
    VersionPolicy,
    VersionValidationError,
)

__all__ = [
    "APIVersion",
    "VersionManager",
    "VersionPolicy",
    "VersionCompatibility",
    "VersionValidationError",
    "UnsupportedVersionError",
    "DeprecatedVersionError",
    "ResponseTransformer",
    "VersionedResponseBuilder",
    "CompatibilityTransformer",
]

__version__ = "1.0.0"
