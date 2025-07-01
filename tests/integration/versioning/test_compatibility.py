"""
ACGS-1 API Compatibility Integration Tests

Tests backward compatibility framework including version transitions,
breaking change detection, and migration path validation.
"""

from datetime import datetime

import pytest

from services.shared.versioning.compatibility_manager import (
    BreakingChange,
    CompatibilityLevel,
    CompatibilityRule,
    create_compatibility_manager,
)
from services.shared.versioning.response_transformers import (
    CompatibilityTransformer,
    VersionedResponseBuilder,
)
from services.shared.versioning.version_manager import APIVersion


class TestCompatibilityManager:
    """Test suite for CompatibilityManager functionality."""

    @pytest.fixture
    def compatibility_manager(self):
        """Create test compatibility manager."""
        return create_compatibility_manager("test-service")

    @pytest.fixture
    def sample_versions(self):
        """Sample API versions for testing."""
        return {
            "v1_0_0": APIVersion(1, 0, 0),
            "v1_1_0": APIVersion(1, 1, 0),
            "v2_0_0": APIVersion(2, 0, 0),
            "v2_1_0": APIVersion(2, 1, 0),
        }

    def test_compatibility_rule_registration(self, compatibility_manager):
        """Test registering compatibility rules."""
        rule = CompatibilityRule(
            source_version=APIVersion(1, 0, 0),
            target_version=APIVersion(1, 1, 0),
            compatibility_level=CompatibilityLevel.FULL,
        )

        compatibility_manager.register_compatibility_rule(rule)

        # Verify rule is registered
        retrieved_rule = compatibility_manager.check_compatibility(
            APIVersion(1, 0, 0), APIVersion(1, 1, 0)
        )
        assert retrieved_rule.compatibility_level == CompatibilityLevel.FULL

    def test_major_version_compatibility(self, compatibility_manager, sample_versions):
        """Test compatibility checking for major version changes."""
        rule = compatibility_manager.check_compatibility(
            sample_versions["v1_0_0"], sample_versions["v2_0_0"]
        )

        assert rule.compatibility_level == CompatibilityLevel.BREAKING
        assert len(rule.breaking_changes) > 0
        assert rule.breaking_changes[0].change_type == "major_version_change"

    def test_minor_version_compatibility(self, compatibility_manager, sample_versions):
        """Test compatibility checking for minor version changes."""
        rule = compatibility_manager.check_compatibility(
            sample_versions["v1_0_0"], sample_versions["v1_1_0"]
        )

        assert rule.compatibility_level == CompatibilityLevel.PARTIAL

    def test_patch_version_compatibility(self, compatibility_manager):
        """Test compatibility checking for patch version changes."""
        v1_0_0 = APIVersion(1, 0, 0)
        v1_0_1 = APIVersion(1, 0, 1)

        rule = compatibility_manager.check_compatibility(v1_0_0, v1_0_1)

        assert rule.compatibility_level == CompatibilityLevel.FULL

    def test_deprecation_schedule_creation(
        self, compatibility_manager, sample_versions
    ):
        """Test creation of deprecation schedules."""
        schedule = compatibility_manager.create_deprecation_schedule(
            sample_versions["v1_0_0"], sample_versions["v2_0_0"]
        )

        required_keys = [
            "new_version_release",
            "deprecation_announcement",
            "sunset_notice",
            "sunset_date",
            "migration_deadline",
        ]

        for key in required_keys:
            assert key in schedule
            assert isinstance(schedule[key], datetime)

        # Verify timeline order
        assert schedule["deprecation_announcement"] <= schedule["sunset_notice"]
        assert schedule["sunset_notice"] <= schedule["sunset_date"]
        assert schedule["migration_deadline"] <= schedule["sunset_date"]

    def test_concurrent_version_validation(self, compatibility_manager):
        """Test validation of concurrent version limits."""
        # Test within limits
        versions_within_limit = [
            APIVersion(1, 0, 0),
            APIVersion(1, 1, 0),
            APIVersion(2, 0, 0),
        ]
        assert compatibility_manager.validate_concurrent_versions(versions_within_limit)

        # Test exceeding limits
        versions_exceeding_limit = [
            APIVersion(1, 0, 0),
            APIVersion(2, 0, 0),
            APIVersion(3, 0, 0),
        ]
        assert not compatibility_manager.validate_concurrent_versions(
            versions_exceeding_limit
        )

    def test_breaking_changes_summary(self, compatibility_manager):
        """Test breaking changes summary generation."""
        # Register rule with breaking changes
        breaking_change = BreakingChange(
            change_type="field_removal",
            description="Removed deprecated field",
            affected_endpoints=["/api/v1/users"],
            migration_notes="Use new field instead",
            severity="medium",
        )

        rule = CompatibilityRule(
            source_version=APIVersion(1, 0, 0),
            target_version=APIVersion(2, 0, 0),
            compatibility_level=CompatibilityLevel.BREAKING,
            breaking_changes=[breaking_change],
        )

        compatibility_manager.register_compatibility_rule(rule)

        summary = compatibility_manager.get_breaking_changes_summary(
            APIVersion(1, 0, 0), APIVersion(2, 0, 0)
        )

        assert len(summary) == 1
        assert summary[0]["type"] == "field_removal"
        assert summary[0]["severity"] == "medium"

    def test_compatibility_report_generation(self, compatibility_manager):
        """Test comprehensive compatibility report generation."""
        report = compatibility_manager.create_compatibility_report()

        required_sections = [
            "service",
            "generated_at",
            "policies",
            "compatibility_rules",
            "transformers",
            "summary",
        ]

        for section in required_sections:
            assert section in report

        # Verify policies section
        policies = report["policies"]
        assert "deprecation_period_days" in policies
        assert "sunset_notice_days" in policies
        assert "max_concurrent_versions" in policies

        # Verify summary section
        summary = report["summary"]
        assert "total_rules" in summary
        assert "breaking_changes" in summary
        assert "partial_compatibility" in summary
        assert "full_compatibility" in summary


class TestCompatibilityTransformer:
    """Test suite for compatibility transformers."""

    @pytest.fixture
    def sample_transformer(self):
        """Create sample compatibility transformer."""
        return CompatibilityTransformer(
            source_version=APIVersion(1, 0, 0),
            target_version=APIVersion(2, 0, 0),
            field_mappings={"user_id": "userId", "created_at": "createdAt"},
            removed_fields=["legacy_field"],
            added_fields={"api_version": "v2.0.0"},
        )

    def test_field_mapping_transformation(self, sample_transformer):
        """Test field name mapping transformation."""
        input_data = {
            "user_id": 123,
            "created_at": "2025-06-22T10:00:00Z",
            "name": "Test User",
        }

        transformed = sample_transformer.transform(input_data)

        assert "userId" in transformed
        assert "createdAt" in transformed
        assert "user_id" not in transformed
        assert "created_at" not in transformed
        assert transformed["userId"] == 123
        assert transformed["name"] == "Test User"

    def test_field_removal_transformation(self, sample_transformer):
        """Test field removal transformation."""
        input_data = {
            "user_id": 123,
            "legacy_field": "deprecated_value",
            "name": "Test User",
        }

        transformed = sample_transformer.transform(input_data)

        assert "legacy_field" not in transformed
        assert "userId" in transformed
        assert "name" in transformed

    def test_field_addition_transformation(self, sample_transformer):
        """Test field addition transformation."""
        input_data = {"user_id": 123, "name": "Test User"}

        transformed = sample_transformer.transform(input_data)

        assert "api_version" in transformed
        assert transformed["api_version"] == "v2.0.0"

    def test_transformer_compatibility_check(self, sample_transformer):
        """Test transformer compatibility checking."""
        assert sample_transformer.can_transform(
            APIVersion(1, 0, 0), APIVersion(2, 0, 0)
        )

        assert not sample_transformer.can_transform(
            APIVersion(1, 1, 0), APIVersion(2, 0, 0)
        )


class TestVersionedResponseBuilder:
    """Test suite for versioned response builder."""

    @pytest.fixture
    def response_builder(self):
        """Create test response builder."""
        return VersionedResponseBuilder("test-service", "1.0.0")

    @pytest.fixture
    def sample_transformer(self):
        """Create sample transformer for testing."""
        return CompatibilityTransformer(
            source_version=APIVersion(1, 0, 0),
            target_version=APIVersion(2, 0, 0),
            field_mappings={"user_id": "userId"},
        )

    def test_transformer_registration(self, response_builder, sample_transformer):
        """Test transformer registration."""
        response_builder.register_transformer(sample_transformer)

        # Verify transformer is registered
        found_transformer = response_builder._find_transformer(
            APIVersion(1, 0, 0), APIVersion(2, 0, 0)
        )
        assert found_transformer is not None
        assert found_transformer == sample_transformer

    def test_response_building_with_transformation(
        self, response_builder, sample_transformer
    ):
        """Test response building with version transformation."""
        response_builder.register_transformer(sample_transformer)

        from services.shared.api_models import APIStatus

        response = response_builder.build_response(
            status=APIStatus.SUCCESS,
            data={"user_id": 123, "name": "Test"},
            request_version=APIVersion(1, 0, 0),
            target_version=APIVersion(2, 0, 0),
        )

        assert response.status == APIStatus.SUCCESS
        assert "userId" in response.data
        assert "user_id" not in response.data
        assert response.data["userId"] == 123

    def test_response_building_without_transformation(self, response_builder):
        """Test response building without version transformation."""
        from services.shared.api_models import APIStatus

        response = response_builder.build_response(
            status=APIStatus.SUCCESS,
            data={"user_id": 123, "name": "Test"},
            target_version=APIVersion(1, 0, 0),
        )

        assert response.status == APIStatus.SUCCESS
        assert response.data["user_id"] == 123
        assert "userId" not in response.data


@pytest.mark.integration
class TestCompatibilityIntegration:
    """Integration tests for complete compatibility workflow."""

    def test_end_to_end_compatibility_workflow(self):
        """Test complete compatibility workflow from detection to response."""
        # Create compatibility manager
        manager = create_compatibility_manager("integration-test-service")

        # Create response builder
        builder = VersionedResponseBuilder("integration-test-service")

        # Register transformer
        transformer = CompatibilityTransformer(
            source_version=APIVersion(1, 0, 0),
            target_version=APIVersion(2, 0, 0),
            field_mappings={"user_id": "userId"},
        )
        builder.register_transformer(transformer)

        # Test compatibility check
        rule = manager.check_compatibility(APIVersion(1, 0, 0), APIVersion(2, 0, 0))
        assert rule.compatibility_level == CompatibilityLevel.BREAKING

        # Test response transformation
        from services.shared.api_models import APIStatus

        response = builder.build_response(
            status=APIStatus.SUCCESS,
            data={"user_id": 123, "name": "Test"},
            request_version=APIVersion(1, 0, 0),
            target_version=APIVersion(2, 0, 0),
        )

        assert response.data["userId"] == 123
        assert "user_id" not in response.data
