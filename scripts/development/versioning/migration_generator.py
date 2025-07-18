"""
ACGS-1 Migration Generator

Generates automated migration scripts and guides based on API diff analysis,
providing step-by-step migration instructions and code transformations.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from .api_diff import APIChange, ChangeType, DiffReport

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = logging.getLogger(__name__)


class MigrationStepType(str, Enum):
    """Types of migration steps."""

    CODE_CHANGE = "code_change"
    CONFIGURATION = "configuration"
    DATABASE = "database"
    DEPLOYMENT = "deployment"
    VALIDATION = "validation"
    ROLLBACK = "rollback"


@dataclass
class MigrationStep:
    """Represents a single migration step."""

    step_type: MigrationStepType
    title: str
    description: str
    code_before: str | None = None
    code_after: str | None = None
    commands: list[str] = field(default_factory=list)
    validation_checks: list[str] = field(default_factory=list)
    rollback_commands: list[str] = field(default_factory=list)
    estimated_time_minutes: int = 5
    risk_level: str = "low"  # low, medium, high

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "step_type": self.step_type.value,
            "title": self.title,
            "description": self.description,
            "code_before": self.code_before,
            "code_after": self.code_after,
            "commands": self.commands,
            "validation_checks": self.validation_checks,
            "rollback_commands": self.rollback_commands,
            "estimated_time_minutes": self.estimated_time_minutes,
            "risk_level": self.risk_level,
        }


@dataclass
class MigrationScript:
    """Complete migration script with all steps and metadata."""

    source_version: str
    target_version: str
    generated_at: datetime
    title: str
    description: str
    steps: list[MigrationStep] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    estimated_total_time_minutes: int = 0
    risk_assessment: str = "low"

    def add_step(self, step: MigrationStep):
        """Add a migration step."""
        self.steps.append(step)
        self.estimated_total_time_minutes += step.estimated_time_minutes

        # Update risk assessment
        if step.risk_level == "high":
            self.risk_assessment = "high"
        elif step.risk_level == "medium" and self.risk_assessment == "low":
            self.risk_assessment = "medium"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "source_version": self.source_version,
            "target_version": self.target_version,
            "generated_at": self.generated_at.isoformat(),
            "title": self.title,
            "description": self.description,
            "steps": [step.to_dict() for step in self.steps],
            "prerequisites": self.prerequisites,
            "estimated_total_time_minutes": self.estimated_total_time_minutes,
            "risk_assessment": self.risk_assessment,
        }


class MigrationGenerator:
    """
    Generates migration scripts and guides based on API diff reports.

    Creates step-by-step migration instructions including code changes,
    configuration updates, and validation procedures.
    """

    def __init__(self):
        self.code_templates = self._load_code_templates()
        self.migration_patterns = self._load_migration_patterns()

    def generate_migration_script(
        self, diff_report: DiffReport, target_language: str = "python"
    ) -> MigrationScript:
        """
        Generate comprehensive migration script from diff report.

        Args:
            diff_report: API diff analysis report
            target_language: Target programming language for code examples

        Returns:
            Complete migration script with steps
        """
        script = MigrationScript(
            source_version=diff_report.source_version,
            target_version=diff_report.target_version,
            generated_at=datetime.now(timezone.utc),
            title=f"Migration Guide: {diff_report.source_version} → {diff_report.target_version}",
            description=f"Automated migration guide for upgrading from {diff_report.source_version} to {diff_report.target_version}",
        )

        # Add prerequisites
        script.prerequisites = self._generate_prerequisites(diff_report)

        # Generate migration steps based on changes
        self._generate_preparation_steps(script, diff_report)
        self._generate_code_change_steps(script, diff_report, target_language)
        self._generate_configuration_steps(script, diff_report)
        self._generate_validation_steps(script, diff_report)
        self._generate_rollback_steps(script, diff_report)

        logger.info(f"Generated migration script with {len(script.steps)} steps")
        return script

    def _generate_prerequisites(self, diff_report: DiffReport) -> list[str]:
        """Generate list of prerequisites for migration."""
        prerequisites = [
            "Backup current application and database",
            "Ensure test environment is available",
            "Review breaking changes in diff report",
            "Update development tools and dependencies",
        ]

        if diff_report.summary["breaking_changes"] > 0:
            prerequisites.append("Plan for application downtime during migration")

        if diff_report.summary["security_fixes"] > 0:
            prerequisites.append("Review security implications of changes")

        return prerequisites

    def _generate_preparation_steps(
        self, script: MigrationScript, diff_report: DiffReport
    ):
        """Generate preparation steps."""
        # Backup step
        script.add_step(
            MigrationStep(
                step_type=MigrationStepType.DEPLOYMENT,
                title="Create Backup",
                description="Create backup of current application state",
                commands=[
                    "# Backup database",
                    "pg_dump acgs_db > backup_$(date +%Y%m%d_%H%M%S).sql",
                    "# Backup configuration",
                    "cp -r config/ backup_config_$(date +%Y%m%d_%H%M%S)/",
                    "# Tag current version in git",
                    f"git tag backup-{diff_report.source_version}-$(date +%Y%m%d_%H%M%S)",
                ],
                validation_checks=[
                    "Verify backup files exist and are not empty",
                    "Test backup restoration in development environment",
                ],
                estimated_time_minutes=15,
                risk_level="low",
            )
        )

        # Environment preparation
        script.add_step(
            MigrationStep(
                step_type=MigrationStepType.CONFIGURATION,
                title="Prepare Environment",
                description="Update development environment for new version",
                commands=[
                    "# Update dependencies",
                    "pip install --upgrade -r config/environments/requirements.txt",
                    "# Update environment variables",
                    f"export API_VERSION={diff_report.target_version}",
                    "# Clear caches",
                    "redis-cli FLUSHALL",
                ],
                validation_checks=[
                    "Verify all dependencies installed successfully",
                    "Check environment variables are set correctly",
                ],
                estimated_time_minutes=10,
                risk_level="low",
            )
        )

    def _generate_code_change_steps(
        self, script: MigrationScript, diff_report: DiffReport, target_language: str
    ):
        """Generate code change steps based on API changes."""
        breaking_changes = [
            c for c in diff_report.changes if c.change_type == ChangeType.BREAKING
        ]

        for change in breaking_changes:
            if "field" in change.description.lower():
                self._generate_field_change_step(script, change, target_language)
            elif "endpoint" in change.description.lower():
                self._generate_endpoint_change_step(script, change, target_language)
            elif "schema" in change.description.lower():
                self._generate_schema_change_step(script, change, target_language)

    def _generate_field_change_step(
        self, script: MigrationScript, change: APIChange, target_language: str
    ):
        """Generate step for field name changes."""
        if target_language == "python":
            code_before = f"""
# Before (v{script.source_version})
response = api_client.get_user(user_id=123)
user_id = response['user_id']
created_at = response['created_at']
"""

            code_after = f"""
# After (v{script.target_version})
response = api_client.get_user(user_id=123)
user_id = response['userId']  # Changed from user_id
created_at = response['createdAt']  # Changed from created_at
"""
        elif target_language == "javascript":
            code_before = f"""
// Before (v{script.source_version})
const response = await apiClient.getUser(123);
const userId = response.user_id;
const createdAt = response.created_at;
"""

            code_after = f"""
// After (v{script.target_version})
const response = await apiClient.getUser(123);
const userId = response.userId;  // Changed from user_id
const createdAt = response.createdAt;  // Changed from created_at
"""
        else:
            code_before = "# Language-specific example not available"
            code_after = "# Language-specific example not available"

        script.add_step(
            MigrationStep(
                step_type=MigrationStepType.CODE_CHANGE,
                title=f"Update Field Names: {change.path}",
                description=change.description,
                code_before=code_before,
                code_after=code_after,
                validation_checks=[
                    "Run unit tests to verify field access",
                    "Test API responses in development environment",
                ],
                estimated_time_minutes=20,
                risk_level="medium",
            )
        )

    def _generate_endpoint_change_step(
        self, script: MigrationScript, change: APIChange, target_language: str
    ):
        """Generate step for endpoint changes."""
        script.add_step(
            MigrationStep(
                step_type=MigrationStepType.CODE_CHANGE,
                title=f"Update Endpoint Usage: {change.path}",
                description=change.description,
                code_before=f"# Remove calls to {change.old_value}",
                code_after="# Use alternative endpoint or method",
                validation_checks=[
                    "Verify all endpoint calls updated",
                    "Test new endpoint functionality",
                ],
                estimated_time_minutes=30,
                risk_level="high",
            )
        )

    def _generate_schema_change_step(
        self, script: MigrationScript, change: APIChange, target_language: str
    ):
        """Generate step for schema changes."""
        script.add_step(
            MigrationStep(
                step_type=MigrationStepType.CODE_CHANGE,
                title=f"Update Schema Handling: {change.path}",
                description=change.description,
                validation_checks=[
                    "Validate schema changes with test data",
                    "Update data models and serializers",
                ],
                estimated_time_minutes=25,
                risk_level="medium",
            )
        )

    def _generate_configuration_steps(
        self, script: MigrationScript, diff_report: DiffReport
    ):
        """Generate configuration update steps."""
        script.add_step(
            MigrationStep(
                step_type=MigrationStepType.CONFIGURATION,
                title="Update API Configuration",
                description="Update API version and configuration settings",
                commands=[
                    "# Update API version in configuration",
                    f"sed -i 's/api_version: {diff_report.source_version}/api_version: {diff_report.target_version}/g' config.yaml",
                    "# Update client configurations",
                    "# Update load balancer settings if needed",
                ],
                validation_checks=[
                    "Verify configuration files updated correctly",
                    "Test configuration loading",
                ],
                estimated_time_minutes=10,
                risk_level="low",
            )
        )

    def _generate_validation_steps(
        self, script: MigrationScript, diff_report: DiffReport
    ):
        """Generate validation and testing steps."""
        script.add_step(
            MigrationStep(
                step_type=MigrationStepType.VALIDATION,
                title="Run Migration Tests",
                description="Validate migration success with comprehensive testing",
                commands=[
                    "# Run unit tests",
                    "python -m pytest tests/",
                    "# Run integration tests",
                    "python -m pytest tests/integration/",
                    "# Run API compatibility tests",
                    "python -m pytest tests/api_compatibility/",
                ],
                validation_checks=[
                    "All tests pass successfully",
                    "API responses match expected format",
                    "Performance metrics within acceptable range",
                ],
                estimated_time_minutes=30,
                risk_level="medium",
            )
        )

    def _generate_rollback_steps(
        self, script: MigrationScript, diff_report: DiffReport
    ):
        """Generate rollback procedure steps."""
        script.add_step(
            MigrationStep(
                step_type=MigrationStepType.ROLLBACK,
                title="Rollback Procedure (if needed)",
                description="Steps to rollback migration if issues occur",
                commands=[
                    "# Stop application",
                    "systemctl stop acgs-service",
                    "# Restore from backup",
                    "psql acgs_db < backup_*.sql",
                    "# Restore configuration",
                    "cp -r backup_config_*/ config/",
                    "# Restart with previous version",
                    "systemctl start acgs-service",
                ],
                rollback_commands=["# This IS the rollback procedure"],
                validation_checks=[
                    "Application starts successfully",
                    "All services responding correctly",
                    "Data integrity verified",
                ],
                estimated_time_minutes=20,
                risk_level="high",
            )
        )

    def _load_code_templates(self) -> dict[str, str]:
        """Load code transformation templates."""
        return {
            "field_rename_python": """
# Update field access
old_field = response['{old_name}']
# Change to:
new_field = response['{new_name}']
""",
            "field_rename_javascript": """
// Update field access
const oldField = response.{old_name};
// Change to:
const newField = response.{new_name};
""",
        }

    def _load_migration_patterns(self) -> dict[str, Any]:
        """Load common migration patterns."""
        return {
            "snake_to_camel": {
                "pattern": r"(\w+)_(\w+)",
                "replacement": r"\1\2.capitalize()",
            },
            "camel_to_snake": {
                "pattern": r"([a-z0-9])([A-Z])",
                "replacement": r"\1_\2.lower()",
            },
        }

    def save_migration_script(self, script: MigrationScript, output_path: Path):
        """Save migration script to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Save as JSON
        import json

        with open(output_path.with_suffix(".json"), "w") as f:
            json.dump(script.to_dict(), f, indent=2)

        # Save as Markdown
        self._save_as_markdown(script, output_path.with_suffix(".md"))

        logger.info(f"Migration script saved to {output_path}")

    def _save_as_markdown(self, script: MigrationScript, output_path: Path):
        """Save migration script as Markdown documentation."""
        with open(output_path, "w") as f:
            f.write(f"# {script.title}\n\n")
            f.write(f"{script.description}\n\n")
            f.write(f"**Generated:** {script.generated_at.isoformat()}\n")
            f.write(
                f"**Estimated Time:** {script.estimated_total_time_minutes} minutes\n"
            )
            f.write(f"**Risk Level:** {script.risk_assessment}\n\n")

            f.write("## Prerequisites\n\n")
            for prereq in script.prerequisites:
                f.write(f"- {prereq}\n")
            f.write("\n")

            f.write("## Migration Steps\n\n")
            for i, step in enumerate(script.steps, 1):
                f.write(f"### Step {i}: {step.title}\n\n")
                f.write(f"{step.description}\n\n")

                if step.code_before or step.code_after:
                    if step.code_before:
                        f.write("**Before:**\n```\n")
                        f.write(step.code_before)
                        f.write("\n```\n\n")

                    if step.code_after:
                        f.write("**After:**\n```\n")
                        f.write(step.code_after)
                        f.write("\n```\n\n")

                if step.commands:
                    f.write("**Commands:**\n```bash\n")
                    f.write("\n".join(step.commands))
                    f.write("\n```\n\n")

                if step.validation_checks:
                    f.write("**Validation:**\n")
                    for check in step.validation_checks:
                        f.write(f"- {check}\n")
                    f.write("\n")

                f.write(f"**Estimated Time:** {step.estimated_time_minutes} minutes\n")
                f.write(f"**Risk Level:** {step.risk_level}\n\n")
                f.write("---\n\n")
