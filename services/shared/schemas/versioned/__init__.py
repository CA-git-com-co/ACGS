"""
ACGS-1 Versioned Schemas

Version-specific Pydantic schemas for API requests and responses,
ensuring type safety and validation across different API versions.
"""

from .base_schemas import *
from .v1_schemas import *
from .v2_schemas import *

__all__ = [
    # Base schemas
    "BaseVersionedModel",
    "VersionedResponse",
    "VersionedRequest",
    # V1 schemas
    "V1UserModel",
    "V1PrincipleModel",
    "V1PolicyModel",
    "V1ResponseModel",
    # V2 schemas
    "V2UserModel",
    "V2PrincipleModel",
    "V2PolicyModel",
    "V2ResponseModel",
    # Schema utilities
    "get_schema_for_version",
    "validate_version_compatibility",
]
