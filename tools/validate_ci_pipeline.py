#!/usr/bin/env python3
"""
ACGS-1 CI/CD Pipeline Validation Script

This script validates the GitHub Actions CI/CD pipeline configuration
and ensures all workflows are properly configured for the project structure.
"""

import sys
from pathlib import Path
from typing import Any

import yaml

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



class CIPipelineValidator:
    def __init__(self, repo_root: str = "."):
        self.repo_root = Path(repo_root)
        self.workflows_dir = self.repo_root / ".github" / "workflows"
        self.errors = []
        self.warnings = []
        self.info = []

    def log_error(self, message: str):
        """Log an error message"""
        self.errors.append(f"❌ ERROR: {message}")
        print(f"❌ ERROR: {message}")

    def log_warning(self, message: str):
        """Log a warning message"""
        self.warnings.append(f"⚠️  WARNING: {message}")
        print(f"⚠️  WARNING: {message}")

    def log_info(self, message: str):
        """Log an info message"""
        self.info.append(f"ℹ️  INFO: {message}")
        print(f"ℹ️  INFO: {message}")

    def validate_workflow_syntax(self, workflow_file: Path) -> bool:
        """Validate YAML syntax of workflow file"""
        try:
            with open(workflow_file) as f:
                yaml.safe_load(f)
            self.log_info(f"Workflow {workflow_file.name} has valid YAML syntax")
            return True
        except yaml.YAMLError as e:
            self.log_error(f"Invalid YAML syntax in {workflow_file.name}: {e}")
            return False
        except Exception as e:
            self.log_error(f"Error reading {workflow_file.name}: {e}")
            return False

    def validate_project_structure(self) -> dict[str, bool]:
        """Validate that referenced paths in workflows exist"""
        structure = {
            "blockchain_dir": (self.repo_root / "blockchain").exists(),
            "blockchain_anchor_toml": (
                self.repo_root / "blockchain" / "Anchor.toml"
            ).exists(),
            "blockchain_package_json": (
                self.repo_root / "blockchain" / "package.json"
            ).exists(),
            "quantumagi_dir": (self.repo_root / "quantumagi_core").exists(),
            "quantumagi_anchor_toml": (
                self.repo_root / "quantumagi_core" / "Anchor.toml"
            ).exists(),
            "services_dir": (self.repo_root / "services").exists(),
            "src_backend_dir": (self.repo_root / "src" / "backend").exists(),
            "ec_service_dockerfile": (
                self.repo_root / "src" / "backend" / "ec_service" / "Dockerfile"
            ).exists(),
            "tests_dir": (self.repo_root / "tests").exists(),
            "requirements_test": (self.repo_root / "requirements-test.txt").exists(),
        }

        for item, exists in structure.items():
            if exists:
                self.log_info(f"Project structure: {item} exists")
            else:
                self.log_warning(f"Project structure: {item} missing")

        return structure

    def validate_workflow_dependencies(
        self, workflow_content: dict[str, Any], workflow_name: str
    ):
        """Validate job dependencies in workflow"""
        if "jobs" not in workflow_content:
            self.log_error(f"{workflow_name}: No jobs defined")
            return

        jobs = workflow_content["jobs"]
        job_names = set(jobs.keys())

        for job_name, job_config in jobs.items():
            if "needs" in job_config:
                needs = job_config["needs"]
                if isinstance(needs, str):
                    needs = [needs]
                elif isinstance(needs, list):
                    pass
                else:
                    self.log_error(
                        f"{workflow_name}: Invalid 'needs' format in job {job_name}"
                    )
                    continue

                for dependency in needs:
                    if dependency not in job_names:
                        self.log_error(
                            f"{workflow_name}: Job {job_name} depends on non-existent job {dependency}"
                        )
                    else:
                        self.log_info(
                            f"{workflow_name}: Job dependency {job_name} -> {dependency} is valid"
                        )

    def validate_action_versions(
        self, workflow_content: dict[str, Any], workflow_name: str
    ):
        """Validate that GitHub Actions use recent versions"""
        recommended_versions = {
            "actions/checkout": "v4",
            "actions/setup-python": "v5",
            "actions/setup-node": "v4",
            "actions/cache": "v4",
            "docker/setup-buildx-action": "v3",
            "docker/login-action": "v3",
            "docker/build-push-action": "v6",
            "github/codeql-action/init": "v3",
            "github/codeql-action/analyze": "v3",
            "github/codeql-action/upload-sarif": "v3",
        }

        def check_steps(steps, job_name=""):
            if not isinstance(steps, list):
                return

            for step in steps:
                if "uses" in step:
                    action = step["uses"]
                    if "@" in action:
                        action_name, version = action.rsplit("@", 1)
                        if action_name in recommended_versions:
                            recommended = recommended_versions[action_name]
                            if version != recommended:
                                self.log_warning(
                                    f"{workflow_name}: {job_name} uses {action_name}@{version}, recommended: @{recommended}"
                                )
                            else:
                                self.log_info(
                                    f"{workflow_name}: {job_name} uses recommended version of {action_name}"
                                )

        if "jobs" in workflow_content:
            for job_name, job_config in workflow_content["jobs"].items():
                if "steps" in job_config:
                    check_steps(job_config["steps"], job_name)

    def validate_environment_variables(
        self, workflow_content: dict[str, Any], workflow_name: str
    ):
        """Validate environment variables are properly defined"""
        required_env_vars = {
            "ci.yml": [
                "REGISTRY",
                "IMAGE_NAME",
                "SOLANA_CLI_VERSION",
                "ANCHOR_CLI_VERSION",
            ],
            "solana-anchor.yml": [
                "SOLANA_CLI_VERSION",
                "ANCHOR_CLI_VERSION",
                "NODE_VERSION",
            ],
            "production-deploy.yml": ["REGISTRY", "IMAGE_NAME"],
        }

        if workflow_name in required_env_vars:
            env_vars = workflow_content.get("env", {})
            for required_var in required_env_vars[workflow_name]:
                if required_var in env_vars:
                    self.log_info(
                        f"{workflow_name}: Required environment variable {required_var} is defined"
                    )
                else:
                    self.log_error(
                        f"{workflow_name}: Missing required environment variable {required_var}"
                    )

    def validate_workflow_triggers(
        self, workflow_content: dict[str, Any], workflow_name: str
    ):
        """Validate workflow triggers are appropriate"""
        # Handle YAML parsing quirk where 'on:' becomes boolean True
        triggers = None
        if "on" in workflow_content:
            triggers = workflow_content["on"]
        elif True in workflow_content:
            triggers = workflow_content[True]

        if triggers is None:
            self.log_error(f"{workflow_name}: No triggers defined")
            return

        # Handle different trigger formats
        if isinstance(triggers, dict):
            if "push" in triggers or "pull_request" in triggers:
                self.log_info(f"{workflow_name}: Has appropriate push/PR triggers")
            elif "workflow_dispatch" in triggers:
                self.log_info(f"{workflow_name}: Has manual workflow dispatch trigger")
            elif "schedule" in triggers:
                self.log_info(f"{workflow_name}: Has scheduled trigger")
            else:
                self.log_warning(
                    f"{workflow_name}: Missing standard triggers (push/PR)"
                )

            # Check for path filters on Solana workflow
            if workflow_name == "solana-anchor.yml":
                if "push" in triggers and "paths" in triggers["push"]:
                    self.log_info(
                        f"{workflow_name}: Has path filters for Solana-specific changes"
                    )
                else:
                    self.log_warning(
                        f"{workflow_name}: Missing path filters for Solana changes"
                    )
        elif isinstance(triggers, list):
            # Handle list format like [push, pull_request]
            if "push" in triggers or "pull_request" in triggers:
                self.log_info(f"{workflow_name}: Has appropriate push/PR triggers")
            else:
                self.log_warning(f"{workflow_name}: Missing push/PR triggers")
        else:
            self.log_warning(
                f"{workflow_name}: Unusual trigger format: {type(triggers)}"
            )

    def run_validation(self) -> bool:
        """Run complete validation of CI/CD pipeline"""
        print("🔍 Starting ACGS-1 CI/CD Pipeline Validation...")
        print("=" * 60)

        # Check if workflows directory exists
        if not self.workflows_dir.exists():
            self.log_error("GitHub workflows directory does not exist")
            return False

        # Validate project structure
        print("\n📁 Validating Project Structure...")
        self.validate_project_structure()

        # Find all workflow files
        workflow_files = list(self.workflows_dir.glob("*.yml")) + list(
            self.workflows_dir.glob("*.yaml")
        )

        if not workflow_files:
            self.log_error("No workflow files found")
            return False

        print(f"\n🔧 Found {len(workflow_files)} workflow files")

        # Validate each workflow
        for workflow_file in workflow_files:
            print(f"\n📋 Validating {workflow_file.name}...")

            # Validate YAML syntax
            if not self.validate_workflow_syntax(workflow_file):
                continue

            # Load and validate workflow content
            try:
                with open(workflow_file) as f:
                    workflow_content = yaml.safe_load(f)

                self.validate_workflow_dependencies(
                    workflow_content, workflow_file.name
                )
                self.validate_action_versions(workflow_content, workflow_file.name)
                self.validate_environment_variables(
                    workflow_content, workflow_file.name
                )
                self.validate_workflow_triggers(workflow_content, workflow_file.name)

            except Exception as e:
                self.log_error(f"Error validating {workflow_file.name}: {e}")

        # Generate summary
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)

        print(f"✅ Info messages: {len(self.info)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")

        if self.errors:
            print("\n❌ CRITICAL ISSUES FOUND:")
            for error in self.errors:
                print(f"  {error}")

        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")

        # Determine overall result
        success = len(self.errors) == 0

        if success:
            print("\n🎉 CI/CD Pipeline validation PASSED!")
            print("All workflows are properly configured.")
        else:
            print("\n💥 CI/CD Pipeline validation FAILED!")
            print("Please fix the errors above before proceeding.")

        return success


def main():
    """Main function"""
    validator = CIPipelineValidator()
    success = validator.run_validation()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
