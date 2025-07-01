"""
ACGS-1 Backward Compatibility Manager

Manages backward compatibility between API versions with comprehensive
transformation rules, deprecation policies, and migration support.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set

from .response_transformers import CompatibilityTransformer, ResponseTransformer
from .version_manager import APIVersion, VersionCompatibility, VersionStatus

logger = logging.getLogger(__name__)


class CompatibilityLevel(str, Enum):
    """Levels of backward compatibility."""

    FULL = "full"  # 100% backward compatible
    PARTIAL = "partial"  # Some features may not work
    BREAKING = "breaking"  # Requires client changes
    NONE = "none"  # No compatibility


@dataclass
class BreakingChange:
    """Represents a breaking change between versions."""

    change_type: str  # "field_removed", "field_renamed", "type_changed", etc.
    description: str
    affected_endpoints: List[str]
    migration_notes: str
    severity: str = "medium"  # "low", "medium", "high", "critical"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "type": self.change_type,
            "description": self.description,
            "affected_endpoints": self.affected_endpoints,
            "migration_notes": self.migration_notes,
            "severity": self.severity,
        }


@dataclass
class CompatibilityRule:
    """Defines compatibility rules between specific versions."""

    source_version: APIVersion
    target_version: APIVersion
    compatibility_level: CompatibilityLevel
    transformer: Optional[ResponseTransformer] = None
    breaking_changes: List[BreakingChange] = field(default_factory=list)
    migration_guide_url: Optional[str] = None

    def is_compatible(self) -> bool:
        """Check if versions are compatible."""
        return self.compatibility_level in [
            CompatibilityLevel.FULL,
            CompatibilityLevel.PARTIAL,
        ]


class CompatibilityManager:
    """
    Manages backward compatibility between API versions.

    Features:
    - Version compatibility matrix
    - Automatic transformation rules
    - Breaking change tracking
    - Migration path generation
    - Deprecation policy enforcement
    """

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.compatibility_rules: Dict[str, CompatibilityRule] = {}
        self.transformers: Dict[str, ResponseTransformer] = {}

        # Deprecation policies
        self.deprecation_period_days = 180  # 6 months
        self.sunset_notice_days = 30  # 30 days advance notice
        self.max_concurrent_versions = 2  # Maximum supported versions

        logger.info(f"CompatibilityManager initialized for {service_name}")

    def register_compatibility_rule(self, rule: CompatibilityRule):
        """Register a compatibility rule between versions."""
        rule_key = f"{rule.source_version}->{rule.target_version}"
        self.compatibility_rules[rule_key] = rule

        # Register transformer if provided
        if rule.transformer:
            self.transformers[rule_key] = rule.transformer

        logger.info(
            f"Registered compatibility rule: {rule_key} "
            f"(level: {rule.compatibility_level.value})"
        )

    def check_compatibility(
        self, source_version: APIVersion, target_version: APIVersion
    ) -> CompatibilityRule:
        """
        Check compatibility between two versions.

        Returns compatibility rule or creates a default one.
        """
        rule_key = f"{source_version}->{target_version}"

        if rule_key in self.compatibility_rules:
            return self.compatibility_rules[rule_key]

        # Generate default compatibility rule
        return self._generate_default_compatibility_rule(source_version, target_version)

    def _generate_default_compatibility_rule(
        self, source_version: APIVersion, target_version: APIVersion
    ) -> CompatibilityRule:
        """Generate default compatibility rule based on semantic versioning."""
        if source_version.major != target_version.major:
            # Major version change - breaking compatibility
            return CompatibilityRule(
                source_version=source_version,
                target_version=target_version,
                compatibility_level=CompatibilityLevel.BREAKING,
                breaking_changes=[
                    BreakingChange(
                        change_type="major_version_change",
                        description=f"Major version change from {source_version.major} to {target_version.major}",
                        affected_endpoints=["*"],
                        migration_notes="Review all API calls for breaking changes",
                        severity="high",
                    )
                ],
            )
        elif source_version.minor != target_version.minor:
            # Minor version change - partial compatibility
            return CompatibilityRule(
                source_version=source_version,
                target_version=target_version,
                compatibility_level=CompatibilityLevel.PARTIAL,
            )
        else:
            # Patch version change - full compatibility
            return CompatibilityRule(
                source_version=source_version,
                target_version=target_version,
                compatibility_level=CompatibilityLevel.FULL,
            )

    def get_migration_path(
        self, from_version: APIVersion, to_version: APIVersion
    ) -> List[CompatibilityRule]:
        """
        Generate migration path between versions.

        Returns list of compatibility rules representing the migration steps.
        """
        # For now, direct migration only
        # Future enhancement: multi-step migration paths
        rule = self.check_compatibility(from_version, to_version)
        return [rule]

    def create_deprecation_schedule(
        self, current_version: APIVersion, new_version: APIVersion
    ) -> Dict[str, datetime]:
        """
        Create deprecation schedule for version transition.

        Returns schedule with key dates for deprecation process.
        """
        now = datetime.now(timezone.utc)

        # Calculate deprecation timeline
        deprecation_start = now
        sunset_notice = now + timedelta(
            days=self.deprecation_period_days - self.sunset_notice_days
        )
        sunset_date = now + timedelta(days=self.deprecation_period_days)

        return {
            "new_version_release": now,
            "deprecation_announcement": deprecation_start,
            "sunset_notice": sunset_notice,
            "sunset_date": sunset_date,
            "migration_deadline": sunset_date - timedelta(days=7),  # 1 week buffer
        }

    def validate_concurrent_versions(self, active_versions: List[APIVersion]) -> bool:
        """
        Validate that the number of concurrent versions doesn't exceed policy.

        Returns True if within limits, False otherwise.
        """
        major_versions = set(v.major for v in active_versions)

        if len(major_versions) > self.max_concurrent_versions:
            logger.warning(
                f"Too many concurrent major versions: {len(major_versions)} > {self.max_concurrent_versions}"
            )
            return False

        return True

    def get_breaking_changes_summary(
        self, from_version: APIVersion, to_version: APIVersion
    ) -> List[Dict[str, Any]]:
        """Get summary of breaking changes between versions."""
        rule = self.check_compatibility(from_version, to_version)
        return [change.to_dict() for change in rule.breaking_changes]

    def create_compatibility_report(self) -> Dict[str, Any]:
        """Create comprehensive compatibility report."""
        report = {
            "service": self.service_name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "policies": {
                "deprecation_period_days": self.deprecation_period_days,
                "sunset_notice_days": self.sunset_notice_days,
                "max_concurrent_versions": self.max_concurrent_versions,
            },
            "compatibility_rules": {},
            "transformers": list(self.transformers.keys()),
            "summary": {
                "total_rules": len(self.compatibility_rules),
                "breaking_changes": 0,
                "partial_compatibility": 0,
                "full_compatibility": 0,
            },
        }

        # Process compatibility rules
        for rule_key, rule in self.compatibility_rules.items():
            report["compatibility_rules"][rule_key] = {
                "source_version": str(rule.source_version),
                "target_version": str(rule.target_version),
                "compatibility_level": rule.compatibility_level.value,
                "breaking_changes_count": len(rule.breaking_changes),
                "has_transformer": rule.transformer is not None,
                "migration_guide": rule.migration_guide_url,
            }

            # Update summary
            if rule.compatibility_level == CompatibilityLevel.BREAKING:
                report["summary"]["breaking_changes"] += 1
            elif rule.compatibility_level == CompatibilityLevel.PARTIAL:
                report["summary"]["partial_compatibility"] += 1
            elif rule.compatibility_level == CompatibilityLevel.FULL:
                report["summary"]["full_compatibility"] += 1

        return report


# Pre-built compatibility rules for common ACGS-1 version transitions
def create_acgs_compatibility_rules() -> List[CompatibilityRule]:
    """Create standard compatibility rules for ACGS-1 services."""
    rules = []

    # v1.x -> v2.x (Major breaking change)
    v1_to_v2_rule = CompatibilityRule(
        source_version=APIVersion(1, 0, 0),
        target_version=APIVersion(2, 0, 0),
        compatibility_level=CompatibilityLevel.BREAKING,
        transformer=CompatibilityTransformer(
            source_version=APIVersion(1, 0, 0),
            target_version=APIVersion(2, 0, 0),
            field_mappings={
                "user_id": "userId",
                "created_at": "createdAt",
                "updated_at": "updatedAt",
            },
            removed_fields=["legacy_field"],
            added_fields={"api_version": "v2.0.0"},
        ),
        breaking_changes=[
            BreakingChange(
                change_type="field_naming_convention",
                description="Changed from snake_case to camelCase",
                affected_endpoints=["*"],
                migration_notes="Update field names in client code",
                severity="medium",
            ),
            BreakingChange(
                change_type="field_removal",
                description="Removed legacy_field from all responses",
                affected_endpoints=["*"],
                migration_notes="Remove references to legacy_field",
                severity="low",
            ),
        ],
        migration_guide_url="https://docs.acgs.ai/migration/v1-to-v2",
    )
    rules.append(v1_to_v2_rule)

    # v2.0 -> v2.1 (Minor compatible change)
    v2_0_to_v2_1_rule = CompatibilityRule(
        source_version=APIVersion(2, 0, 0),
        target_version=APIVersion(2, 1, 0),
        compatibility_level=CompatibilityLevel.FULL,
        transformer=CompatibilityTransformer(
            source_version=APIVersion(2, 0, 0),
            target_version=APIVersion(2, 1, 0),
            added_fields={"enhanced_metadata": True, "performance_metrics": {}},
        ),
    )
    rules.append(v2_0_to_v2_1_rule)

    return rules


# Factory function for creating compatibility manager
def create_compatibility_manager(service_name: str) -> CompatibilityManager:
    """
    Factory function to create compatibility manager with ACGS-1 defaults.

    Args:
        service_name: Name of the service

    Returns:
        Configured CompatibilityManager instance
    """
    manager = CompatibilityManager(service_name)

    # Register standard ACGS-1 compatibility rules
    for rule in create_acgs_compatibility_rules():
        manager.register_compatibility_rule(rule)

    return manager
