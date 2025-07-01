"""
ACGS-1 API Response Transformers

Provides version-aware response transformation and backward compatibility
for API responses, working with the existing unified response format.
"""

import logging
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

from ..api_models import APIError, APIMetadata, APIResponse, APIStatus
from .version_manager import APIVersion, VersionCompatibility

logger = logging.getLogger(__name__)


class ResponseTransformer(ABC):
    """Abstract base class for version-specific response transformers."""

    def __init__(self, source_version: APIVersion, target_version: APIVersion):
        self.source_version = source_version
        self.target_version = target_version

    @abstractmethod
    def transform(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Transform response data from source to target version."""
        pass

    @abstractmethod
    def can_transform(self, source: APIVersion, target: APIVersion) -> bool:
        """Check if this transformer can handle the version transformation."""
        pass


class CompatibilityTransformer(ResponseTransformer):
    """
    Handles backward compatibility transformations between API versions.

    Supports common transformation patterns:
    - Field renaming
    - Field removal/addition
    - Data structure changes
    - Format conversions
    """

    def __init__(
        self,
        source_version: APIVersion,
        target_version: APIVersion,
        field_mappings: dict[str, str] | None = None,
        removed_fields: list[str] | None = None,
        added_fields: dict[str, Any] | None = None,
        custom_transformers: dict[str, Callable] | None = None,
    ):
        super().__init__(source_version, target_version)
        self.field_mappings = field_mappings or {}
        self.removed_fields = removed_fields or []
        self.added_fields = added_fields or {}
        self.custom_transformers = custom_transformers or {}

    def transform(self, response_data: dict[str, Any]) -> dict[str, Any]:
        """Apply compatibility transformations to response data."""
        transformed_data = response_data.copy()

        # Apply field mappings (rename fields)
        for old_field, new_field in self.field_mappings.items():
            if old_field in transformed_data:
                transformed_data[new_field] = transformed_data.pop(old_field)

        # Remove deprecated fields
        for field in self.removed_fields:
            transformed_data.pop(field, None)

        # Add new fields with default values
        for field, default_value in self.added_fields.items():
            if field not in transformed_data:
                transformed_data[field] = default_value

        # Apply custom transformations
        for field, transformer in self.custom_transformers.items():
            if field in transformed_data:
                try:
                    transformed_data[field] = transformer(transformed_data[field])
                except Exception as e:
                    logger.warning(
                        f"Custom transformation failed for field {field}: {e}"
                    )

        return transformed_data

    def can_transform(self, source: APIVersion, target: APIVersion) -> bool:
        """Check if this transformer can handle the version transformation."""
        return source == self.source_version and target == self.target_version


class VersionedResponseBuilder:
    """
    Builds version-aware API responses with proper transformation and headers.

    Integrates with existing APIResponse structure while adding versioning capabilities.
    """

    def __init__(self, service_name: str, service_version: str = "3.0.0"):
        self.service_name = service_name
        self.service_version = service_version
        self.transformers: list[ResponseTransformer] = []

    def register_transformer(self, transformer: ResponseTransformer):
        """Register a response transformer for version compatibility."""
        self.transformers.append(transformer)
        logger.info(
            f"Registered transformer: {transformer.source_version} -> {transformer.target_version}"
        )

    def build_response(
        self,
        status: APIStatus,
        data: Any = None,
        error: APIError | None = None,
        request_version: APIVersion | None = None,
        target_version: APIVersion | None = None,
        correlation_id: str | None = None,
        response_time_ms: float | None = None,
        compatibility_info: VersionCompatibility | None = None,
    ) -> APIResponse:
        """
        Build a version-aware API response.

        Args:
            status: Response status
            data: Response data
            error: Error information (if status is ERROR)
            request_version: Version requested by client
            target_version: Version to transform response to
            correlation_id: Request correlation ID
            response_time_ms: Response time in milliseconds
            compatibility_info: Version compatibility information
        """
        # Create metadata with version information
        metadata = APIMetadata(
            service_name=self.service_name,
            service_version=self.service_version,
            api_version=str(target_version) if target_version else "v1",
            correlation_id=correlation_id,
            response_time_ms=response_time_ms,
        )

        # Transform data if version transformation is needed
        transformed_data = data
        if (
            request_version
            and target_version
            and request_version != target_version
            and data is not None
        ):
            transformed_data = self._transform_data(
                data, request_version, target_version
            )

        # Create base response
        response = APIResponse(
            status=status, data=transformed_data, error=error, metadata=metadata
        )

        return response

    def _transform_data(
        self, data: Any, source_version: APIVersion, target_version: APIVersion
    ) -> Any:
        """Transform response data between versions."""
        if not isinstance(data, dict):
            return data

        # Find appropriate transformer
        transformer = self._find_transformer(source_version, target_version)
        if transformer:
            try:
                return transformer.transform(data)
            except Exception as e:
                logger.error(f"Response transformation failed: {e}")
                # Return original data if transformation fails
                return data

        # No transformer found, return original data
        logger.warning(f"No transformer found for {source_version} -> {target_version}")
        return data

    def _find_transformer(
        self, source_version: APIVersion, target_version: APIVersion
    ) -> ResponseTransformer | None:
        """Find a suitable transformer for the version pair."""
        for transformer in self.transformers:
            if transformer.can_transform(source_version, target_version):
                return transformer
        return None

    def create_deprecation_response(
        self, compatibility_info: VersionCompatibility, original_response: APIResponse
    ) -> dict[str, Any]:
        """
        Create response with deprecation warnings and migration information.

        Adds deprecation metadata to the response without breaking existing structure.
        """
        response_dict = original_response.dict()

        # Add deprecation information to metadata
        if "deprecation" not in response_dict["metadata"]:
            response_dict["metadata"]["deprecation"] = {}

        deprecation_info = {
            "is_deprecated": compatibility_info.is_deprecated(),
            "deprecated_since": (
                compatibility_info.deprecated_since.isoformat()
                if compatibility_info.deprecated_since
                else None
            ),
            "sunset_date": (
                compatibility_info.sunset_date.isoformat()
                if compatibility_info.sunset_date
                else None
            ),
            "days_until_sunset": compatibility_info.days_until_sunset(),
            "migration_guide": compatibility_info.migration_guide_url,
            "breaking_changes": compatibility_info.breaking_changes,
        }

        response_dict["metadata"]["deprecation"] = deprecation_info

        return response_dict


# Pre-built transformers for common version transitions
class V1ToV2Transformer(CompatibilityTransformer):
    """Example transformer for v1 to v2 API transition."""

    def __init__(self):
        super().__init__(
            source_version=APIVersion(1, 0, 0),
            target_version=APIVersion(2, 0, 0),
            field_mappings={
                "user_id": "userId",  # camelCase conversion
                "created_at": "createdAt",
                "updated_at": "updatedAt",
            },
            removed_fields=["legacy_field"],
            added_fields={"api_version": "v2.0.0", "schema_version": "2.0"},
        )


class V2ToV1Transformer(CompatibilityTransformer):
    """Example transformer for v2 to v1 API backward compatibility."""

    def __init__(self):
        super().__init__(
            source_version=APIVersion(2, 0, 0),
            target_version=APIVersion(1, 0, 0),
            field_mappings={
                "userId": "user_id",  # snake_case conversion
                "createdAt": "created_at",
                "updatedAt": "updated_at",
            },
            removed_fields=["api_version", "schema_version"],
            added_fields={"legacy_field": "deprecated_value"},
        )


# Factory function for creating response builders
def create_versioned_response_builder(
    service_name: str,
    service_version: str = "3.0.0",
    register_default_transformers: bool = True,
) -> VersionedResponseBuilder:
    """
    Factory function to create a versioned response builder with default transformers.

    Args:
        service_name: Name of the service
        service_version: Version of the service
        register_default_transformers: Whether to register common transformers

    Returns:
        Configured VersionedResponseBuilder instance
    """
    builder = VersionedResponseBuilder(service_name, service_version)

    if register_default_transformers:
        # Register common transformers
        builder.register_transformer(V1ToV2Transformer())
        builder.register_transformer(V2ToV1Transformer())

    return builder
