"""
ACGS-1 API Diff Analyzer

Analyzes differences between API versions to identify breaking changes,
new features, and compatibility issues for automated migration planning.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


try:
    import yaml
    from deepdiff import DeepDiff
except ImportError:
    # Fallback for environments without these dependencies
    yaml = None
    DeepDiff = None

logger = logging.getLogger(__name__)


class ChangeType(str, Enum):
    """Types of API changes."""

    BREAKING = "breaking"
    FEATURE = "feature"
    DEPRECATION = "deprecation"
    BUG_FIX = "bug_fix"
    SECURITY = "security"
    PERFORMANCE = "performance"


class Severity(str, Enum):
    """Severity levels for API changes."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class APIChange:
    """Represents a single API change between versions."""

    change_type: ChangeType
    severity: Severity
    path: str
    description: str
    old_value: Any = None
    new_value: Any = None
    affected_endpoints: list[str] = field(default_factory=list)
    migration_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "change_type": self.change_type.value,
            "severity": self.severity.value,
            "path": self.path,
            "description": self.description,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "affected_endpoints": self.affected_endpoints,
            "migration_notes": self.migration_notes,
        }


@dataclass
class DiffReport:
    """Comprehensive diff report between two API versions."""

    source_version: str
    target_version: str
    generated_at: datetime
    changes: list[APIChange] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)
    compatibility_score: float = 0.0
    migration_complexity: str = "low"

    def add_change(self, change: APIChange):
        """Add a change to the report."""
        self.changes.append(change)
        self._update_summary()

    def _update_summary(self):
        """Update summary statistics."""
        self.summary = {
            "total_changes": len(self.changes),
            "breaking_changes": len(
                [c for c in self.changes if c.change_type == ChangeType.BREAKING]
            ),
            "new_features": len(
                [c for c in self.changes if c.change_type == ChangeType.FEATURE]
            ),
            "deprecations": len(
                [c for c in self.changes if c.change_type == ChangeType.DEPRECATION]
            ),
            "bug_fixes": len(
                [c for c in self.changes if c.change_type == ChangeType.BUG_FIX]
            ),
            "security_fixes": len(
                [c for c in self.changes if c.change_type == ChangeType.SECURITY]
            ),
        }

        # Calculate compatibility score (0-1, where 1 is fully compatible)
        total_changes = len(self.changes)
        if total_changes == 0:
            self.compatibility_score = 1.0
        else:
            breaking_weight = 0.8
            deprecation_weight = 0.3
            feature_weight = 0.1

            breaking_impact = self.summary["breaking_changes"] * breaking_weight
            deprecation_impact = self.summary["deprecations"] * deprecation_weight
            feature_impact = self.summary["new_features"] * feature_weight

            total_impact = breaking_impact + deprecation_impact + feature_impact
            self.compatibility_score = max(0.0, 1.0 - (total_impact / total_changes))

        # Determine migration complexity
        if self.summary["breaking_changes"] > 5:
            self.migration_complexity = "high"
        elif self.summary["breaking_changes"] > 0 or self.summary["deprecations"] > 10:
            self.migration_complexity = "medium"
        else:
            self.migration_complexity = "low"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source_version": self.source_version,
            "target_version": self.target_version,
            "generated_at": self.generated_at.isoformat(),
            "changes": [change.to_dict() for change in self.changes],
            "summary": self.summary,
            "compatibility_score": self.compatibility_score,
            "migration_complexity": self.migration_complexity,
        }


class APIDiffAnalyzer:
    """
    Analyzes differences between API specifications to identify changes
    and their impact on backward compatibility.
    """

    def __init__(self):
        self.breaking_change_patterns = [
            "removed_field",
            "changed_type",
            "removed_endpoint",
            "changed_required_field",
            "changed_response_structure",
        ]

        self.feature_patterns = [
            "added_field",
            "added_endpoint",
            "added_optional_parameter",
        ]

        self.deprecation_patterns = [
            "deprecated_field",
            "deprecated_endpoint",
            "deprecated_parameter",
        ]

    def analyze_openapi_specs(
        self,
        source_spec: dict[str, Any],
        target_spec: dict[str, Any],
        source_version: str,
        target_version: str,
    ) -> DiffReport:
        """
        Analyze differences between OpenAPI specifications.

        Args:
            source_spec: Source OpenAPI specification
            target_spec: Target OpenAPI specification
            source_version: Source version string
            target_version: Target version string

        Returns:
            Comprehensive diff report
        """
        report = DiffReport(
            source_version=source_version,
            target_version=target_version,
            generated_at=datetime.now(timezone.utc),
        )

        # Analyze paths (endpoints)
        self._analyze_paths(source_spec, target_spec, report)

        # Analyze schemas
        self._analyze_schemas(source_spec, target_spec, report)

        # Analyze parameters
        self._analyze_parameters(source_spec, target_spec, report)

        # Analyze responses
        self._analyze_responses(source_spec, target_spec, report)

        # Analyze security
        self._analyze_security(source_spec, target_spec, report)

        logger.info(f"API diff analysis complete: {len(report.changes)} changes found")
        return report

    def _analyze_paths(
        self,
        source_spec: dict[str, Any],
        target_spec: dict[str, Any],
        report: DiffReport,
    ):
        """Analyze endpoint path changes."""
        source_paths = set(source_spec.get("paths", {}).keys())
        target_paths = set(target_spec.get("paths", {}).keys())

        # Removed endpoints (breaking change)
        for removed_path in source_paths - target_paths:
            report.add_change(
                APIChange(
                    change_type=ChangeType.BREAKING,
                    severity=Severity.HIGH,
                    path=f"paths.{removed_path}",
                    description=f"Endpoint removed: {removed_path}",
                    old_value=removed_path,
                    new_value=None,
                    affected_endpoints=[removed_path],
                    migration_notes=f"Remove calls to {removed_path} or use alternative endpoint",
                )
            )

        # Added endpoints (new feature)
        for added_path in target_paths - source_paths:
            report.add_change(
                APIChange(
                    change_type=ChangeType.FEATURE,
                    severity=Severity.LOW,
                    path=f"paths.{added_path}",
                    description=f"New endpoint added: {added_path}",
                    old_value=None,
                    new_value=added_path,
                    affected_endpoints=[added_path],
                    migration_notes=f"New endpoint {added_path} available for use",
                )
            )

        # Analyze changes in existing endpoints
        for common_path in source_paths & target_paths:
            self._analyze_endpoint_changes(
                common_path,
                source_spec["paths"][common_path],
                target_spec["paths"][common_path],
                report,
            )

    def _analyze_endpoint_changes(
        self,
        path: str,
        source_endpoint: dict[str, Any],
        target_endpoint: dict[str, Any],
        report: DiffReport,
    ):
        """Analyze changes within a specific endpoint."""
        # Compare HTTP methods
        source_methods = set(source_endpoint.keys())
        target_methods = set(target_endpoint.keys())

        # Removed methods (breaking change)
        for removed_method in source_methods - target_methods:
            if removed_method not in ["summary", "description", "parameters"]:
                report.add_change(
                    APIChange(
                        change_type=ChangeType.BREAKING,
                        severity=Severity.HIGH,
                        path=f"paths.{path}.{removed_method}",
                        description=f"HTTP method {removed_method.upper()} removed from {path}",
                        old_value=removed_method,
                        new_value=None,
                        affected_endpoints=[f"{removed_method.upper()} {path}"],
                        migration_notes=f"Use alternative method or endpoint for {path}",
                    )
                )

        # Added methods (new feature)
        for added_method in target_methods - source_methods:
            if added_method not in ["summary", "description", "parameters"]:
                report.add_change(
                    APIChange(
                        change_type=ChangeType.FEATURE,
                        severity=Severity.LOW,
                        path=f"paths.{path}.{added_method}",
                        description=f"HTTP method {added_method.upper()} added to {path}",
                        old_value=None,
                        new_value=added_method,
                        affected_endpoints=[f"{added_method.upper()} {path}"],
                        migration_notes=f"New method {added_method.upper()} available for {path}",
                    )
                )

    def _analyze_schemas(
        self,
        source_spec: dict[str, Any],
        target_spec: dict[str, Any],
        report: DiffReport,
    ):
        """Analyze schema changes."""
        source_schemas = source_spec.get("components", {}).get("schemas", {})
        target_schemas = target_spec.get("components", {}).get("schemas", {})

        # Use DeepDiff for detailed schema comparison
        diff = DeepDiff(source_schemas, target_schemas, ignore_order=True)

        # Analyze removed schemas
        if "dictionary_item_removed" in diff:
            for removed_item in diff["dictionary_item_removed"]:
                schema_name = removed_item.split("'")[1]
                report.add_change(
                    APIChange(
                        change_type=ChangeType.BREAKING,
                        severity=Severity.HIGH,
                        path=f"components.schemas.{schema_name}",
                        description=f"Schema removed: {schema_name}",
                        old_value=schema_name,
                        new_value=None,
                        migration_notes=f"Update code to handle removal of {schema_name} schema",
                    )
                )

        # Analyze added schemas
        if "dictionary_item_added" in diff:
            for added_item in diff["dictionary_item_added"]:
                schema_name = added_item.split("'")[1]
                report.add_change(
                    APIChange(
                        change_type=ChangeType.FEATURE,
                        severity=Severity.LOW,
                        path=f"components.schemas.{schema_name}",
                        description=f"New schema added: {schema_name}",
                        old_value=None,
                        new_value=schema_name,
                        migration_notes=f"New schema {schema_name} available for use",
                    )
                )

        # Analyze changed schemas
        if "values_changed" in diff:
            for changed_path, change_info in diff["values_changed"].items():
                if "schemas" in changed_path:
                    self._analyze_schema_field_change(changed_path, change_info, report)

    def _analyze_schema_field_change(
        self, path: str, change_info: dict[str, Any], report: DiffReport
    ):
        """Analyze individual schema field changes."""
        old_value = change_info.get("old_value")
        new_value = change_info.get("new_value")

        # Determine change type based on the nature of the change
        change_type = ChangeType.BREAKING
        severity = Severity.MEDIUM

        if "type" in path and old_value != new_value:
            # Type change is breaking
            change_type = ChangeType.BREAKING
            severity = Severity.HIGH
        elif "required" in path:
            # Required field changes are breaking
            change_type = ChangeType.BREAKING
            severity = Severity.HIGH
        elif "description" in path or "example" in path:
            # Documentation changes are non-breaking
            change_type = ChangeType.BUG_FIX
            severity = Severity.LOW

        report.add_change(
            APIChange(
                change_type=change_type,
                severity=severity,
                path=path,
                description=f"Schema field changed: {path}",
                old_value=old_value,
                new_value=new_value,
                migration_notes=f"Update code to handle change in {path}",
            )
        )

    def _analyze_parameters(
        self,
        source_spec: dict[str, Any],
        target_spec: dict[str, Any],
        report: DiffReport,
    ):
        """Analyze parameter changes."""
        # This would analyze global parameters and endpoint-specific parameters
        # Implementation similar to schema analysis
        pass

    def _analyze_responses(
        self,
        source_spec: dict[str, Any],
        target_spec: dict[str, Any],
        report: DiffReport,
    ):
        """Analyze response changes."""
        # This would analyze response schema changes
        # Implementation similar to schema analysis
        pass

    def _analyze_security(
        self,
        source_spec: dict[str, Any],
        target_spec: dict[str, Any],
        report: DiffReport,
    ):
        """Analyze security requirement changes."""
        source_security = source_spec.get("security", [])
        target_security = target_spec.get("security", [])

        if source_security != target_security:
            report.add_change(
                APIChange(
                    change_type=ChangeType.SECURITY,
                    severity=Severity.HIGH,
                    path="security",
                    description="Security requirements changed",
                    old_value=source_security,
                    new_value=target_security,
                    migration_notes="Review and update authentication/authorization code",
                )
            )

    def save_report(self, report: DiffReport, output_path: Path):
        """Save diff report to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(report.to_dict(), f, indent=2)

        logger.info(f"Diff report saved to {output_path}")

    def load_openapi_spec(self, spec_path: Path) -> dict[str, Any]:
        """Load OpenAPI specification from file."""
        with open(spec_path) as f:
            if spec_path.suffix.lower() in [".yaml", ".yml"]:
                return yaml.safe_load(f)
            return json.load(f)


# CLI interface for the diff analyzer
def main():
    """Command-line interface for API diff analysis."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze API differences between versions"
    )
    parser.add_argument("source_spec", help="Path to source OpenAPI specification")
    parser.add_argument("target_spec", help="Path to target OpenAPI specification")
    parser.add_argument("--source-version", required=True, help="Source version")
    parser.add_argument("--target-version", required=True, help="Target version")
    parser.add_argument(
        "--output", "-o", help="Output file path", default="api_diff_report.json"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    analyzer = APIDiffAnalyzer()

    # Load specifications
    source_spec = analyzer.load_openapi_spec(Path(args.source_spec))
    target_spec = analyzer.load_openapi_spec(Path(args.target_spec))

    # Analyze differences
    report = analyzer.analyze_openapi_specs(
        source_spec, target_spec, args.source_version, args.target_version
    )

    # Save report
    analyzer.save_report(report, Path(args.output))

    # Print summary
    print("\nAPI Diff Analysis Summary:")
    print(f"Source Version: {report.source_version}")
    print(f"Target Version: {report.target_version}")
    print(f"Total Changes: {report.summary['total_changes']}")
    print(f"Breaking Changes: {report.summary['breaking_changes']}")
    print(f"New Features: {report.summary['new_features']}")
    print(f"Compatibility Score: {report.compatibility_score:.2f}")
    print(f"Migration Complexity: {report.migration_complexity}")


if __name__ == "__main__":
    main()
