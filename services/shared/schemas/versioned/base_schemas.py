"""
ACGS-1 Base Versioned Schemas

Base classes and utilities for version-specific schema definitions.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional, Type, Union

from pydantic import BaseModel, Field, validator

from ...versioning.version_manager import APIVersion


class BaseVersionedModel(BaseModel, ABC):
    """
    Abstract base class for all versioned models.

    Provides common functionality for version-aware schema validation
    and transformation between different API versions.
    """

    class Config:
        # Allow extra fields for forward compatibility
        extra = "allow"
        # Use enum values for serialization
        use_enum_values = True
        # Validate assignment
        validate_assignment = True
        # JSON encoders for common types
        json_encoders = {datetime: lambda v: v.isoformat()}

    @classmethod
    @abstractmethod
    def get_version(cls) -> APIVersion:
        """Return the API version this schema represents."""
        pass

    @classmethod
    @abstractmethod
    def get_compatible_versions(cls) -> list[APIVersion]:
        """Return list of compatible API versions."""
        pass

    @abstractmethod
    def to_version(self, target_version: APIVersion) -> "BaseVersionedModel":
        """Transform this model to a different API version."""
        pass

    def is_compatible_with(self, version: APIVersion) -> bool:
        """Check if this model is compatible with given version."""
        return version in self.get_compatible_versions()


class VersionedResponse(BaseModel):
    """
    Generic versioned response wrapper.

    Wraps any response data with version metadata and compatibility information.
    """

    data: Any
    version: str = Field(..., description="API version used for this response")
    compatible_versions: list[str] = Field(
        default_factory=list, description="List of compatible API versions"
    )
    deprecation_info: Optional[Dict[str, Any]] = Field(
        None, description="Deprecation information if version is deprecated"
    )
    transformation_applied: bool = Field(
        False, description="Whether version transformation was applied"
    )

    @validator("version")
    def validate_version_format(cls, v):
        """Validate version format."""
        try:
            APIVersion.from_string(v)
            return v
        except Exception:
            raise ValueError(f"Invalid version format: {v}")


class VersionedRequest(BaseModel):
    """
    Generic versioned request wrapper.

    Wraps request data with version information for processing.
    """

    data: Any
    requested_version: Optional[str] = Field(None, description="Explicitly requested API version")
    client_version: Optional[str] = Field(None, description="Client SDK version")
    compatibility_mode: bool = Field(
        False, description="Enable compatibility mode for version mismatches"
    )


# Schema registry for version mapping
class SchemaRegistry:
    """
    Registry for managing version-specific schemas.

    Provides utilities for schema lookup, validation, and transformation
    across different API versions.
    """

    def __init__(self):
        self._schemas: Dict[str, Dict[str, Type[BaseVersionedModel]]] = {}
        # Structure: {model_name: {version: schema_class}}

    def register_schema(
        self,
        model_name: str,
        version: Union[str, APIVersion],
        schema_class: Type[BaseVersionedModel],
    ):
        """Register a schema for a specific model and version."""
        if isinstance(version, APIVersion):
            version = str(version)

        if model_name not in self._schemas:
            self._schemas[model_name] = {}

        self._schemas[model_name][version] = schema_class

    def get_schema(
        self, model_name: str, version: Union[str, APIVersion]
    ) -> Optional[Type[BaseVersionedModel]]:
        """Get schema class for specific model and version."""
        if isinstance(version, APIVersion):
            version = str(version)

        return self._schemas.get(model_name, {}).get(version)

    def get_compatible_schema(
        self, model_name: str, version: Union[str, APIVersion]
    ) -> Optional[Type[BaseVersionedModel]]:
        """
        Get compatible schema for model and version.

        If exact version not found, returns highest compatible version.
        """
        if isinstance(version, str):
            version = APIVersion.from_string(version)

        model_schemas = self._schemas.get(model_name, {})
        if not model_schemas:
            return None

        # Try exact match first
        exact_schema = model_schemas.get(str(version))
        if exact_schema:
            return exact_schema

        # Find compatible versions
        compatible_schemas = []
        for schema_version_str, schema_class in model_schemas.items():
            schema_version = APIVersion.from_string(schema_version_str)
            if schema_version.is_compatible_with(version):
                compatible_schemas.append((schema_version, schema_class))

        if compatible_schemas:
            # Return highest compatible version
            compatible_schemas.sort(key=lambda x: x[0], reverse=True)
            return compatible_schemas[0][1]

        return None

    def list_versions(self, model_name: str) -> list[str]:
        """List all available versions for a model."""
        return list(self._schemas.get(model_name, {}).keys())

    def list_models(self) -> list[str]:
        """List all registered model names."""
        return list(self._schemas.keys())


# Global schema registry instance
schema_registry = SchemaRegistry()


# Utility functions
def get_schema_for_version(
    model_name: str, version: Union[str, APIVersion]
) -> Optional[Type[BaseVersionedModel]]:
    """Get schema class for specific model and version."""
    return schema_registry.get_schema(model_name, version)


def validate_version_compatibility(
    model: BaseVersionedModel, target_version: Union[str, APIVersion]
) -> bool:
    """Validate if model is compatible with target version."""
    if isinstance(target_version, str):
        target_version = APIVersion.from_string(target_version)

    return model.is_compatible_with(target_version)


def transform_model_to_version(
    model: BaseVersionedModel, target_version: Union[str, APIVersion]
) -> BaseVersionedModel:
    """Transform model to target version."""
    if isinstance(target_version, str):
        target_version = APIVersion.from_string(target_version)

    return model.to_version(target_version)


# Decorators for schema registration
def versioned_schema(model_name: str, version: Union[str, APIVersion]):
    """
    Decorator to register a schema class with the global registry.

    Usage:
        @versioned_schema("User", "v1.0.0")
        class V1UserModel(BaseVersionedModel):
            ...
    """

    def decorator(schema_class: Type[BaseVersionedModel]):
        schema_registry.register_schema(model_name, version, schema_class)
        return schema_class

    return decorator


# Common field definitions for reuse across versions
class CommonFields:
    """Common field definitions used across different schema versions."""

    # Timestamp fields
    created_at_v1 = Field(..., description="Creation timestamp (v1.x format)", alias="created_at")

    created_at_v2 = Field(..., description="Creation timestamp (v2.x format)", alias="createdAt")

    updated_at_v1 = Field(..., description="Update timestamp (v1.x format)", alias="updated_at")

    updated_at_v2 = Field(..., description="Update timestamp (v2.x format)", alias="updatedAt")

    # ID fields
    user_id_v1 = Field(..., description="User identifier (v1.x format)", alias="user_id")

    user_id_v2 = Field(..., description="User identifier (v2.x format)", alias="userId")

    # Version metadata
    api_version = Field(..., description="API version for this response")

    schema_version = Field(..., description="Schema version for this model")


# Base response models for different versions
class V1BaseResponse(BaseVersionedModel):
    """Base response model for v1.x APIs."""

    @classmethod
    def get_version(cls) -> APIVersion:
        return APIVersion(1, 0, 0)

    @classmethod
    def get_compatible_versions(cls) -> list[APIVersion]:
        return [APIVersion(1, 0, 0), APIVersion(1, 1, 0), APIVersion(1, 2, 0)]


class V2BaseResponse(BaseVersionedModel):
    """Base response model for v2.x APIs."""

    api_version: str = Field(default="v2.0.0", description="API version")

    @classmethod
    def get_version(cls) -> APIVersion:
        return APIVersion(2, 0, 0)

    @classmethod
    def get_compatible_versions(cls) -> list[APIVersion]:
        return [APIVersion(2, 0, 0), APIVersion(2, 1, 0)]
