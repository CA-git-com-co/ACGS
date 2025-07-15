#!/usr/bin/env python3
"""
Update CI/CD workflows for ACGS-2 reorganization

Constitutional Hash: cdd01ef066bc6cf2
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def fix_corrupted_references(project_root: Path) -> Tuple[bool, List[str]]:
    """Fix corrupted references in CI/CD workflows."""
    issues = []

    # Find all workflow files
    workflow_dir = project_root / ".github" / "workflows"
    if not workflow_dir.exists():
        issues.append("GitHub workflows directory not found")
        return False, issues

    workflow_files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))

    for workflow_file in workflow_files:
        try:
            content = workflow_file.read_text(encoding='utf-8')
            original_content = content

            # Fix corrupted environment references
            content = content.replace(
                "stepsconfig/environments/development.environment_detection.outputsconfig/environments/development.environment",
                "steps.environment_detection.outputs.environment"
            )
            content = content.replace(
                "stepsconfig/environments/development.environment_detection.outputs.strategy",
                "steps.environment_detection.outputs.strategy"
            )
            content = content.replace(
                "stepsconfig/environments/development.environment_detection.outputs.should_deploy",
                "steps.environment_detection.outputs.should_deploy"
            )
            content = content.replace(
                "github.event.inputsconfig/environments/development.environment",
                "github.event.inputs.environment"
            )

            # Update Docker Compose file paths
            content = content.replace(
                "docker-compose.production.yml",
                "config/docker/docker-compose.production.yml"
            )
            content = content.replace(
                "docker-compose.basic.yml",
                "config/docker/docker-compose.basic.yml"
            )

            # Update environment file references
            content = content.replace(
                'env_file: ".env"',
                'env_file: "config/environments/development.env"'
            )
            content = content.replace(
                'env_file: .env',
                'env_file: config/environments/development.env'
            )

            # Update script references
            content = content.replace(
                "./deploy_production.sh",
                "./scripts/deployment/deploy_production.sh"
            )
            content = content.replace(
                "./backup_production.sh",
                "./scripts/deployment/backup_production.sh"
            )
            content = content.replace(
                "./staging-health-check.py",
                "./scripts/monitoring/staging-health-check.py"
            )

            if content != original_content:
                workflow_file.write_text(content, encoding='utf-8')
                issues.append(f"Updated workflow file: {workflow_file.name}")

        except Exception as e:
            issues.append(f"Error updating workflow {workflow_file.name}: {e}")

    return True, issues


def validate_workflow_syntax(project_root: Path) -> Tuple[bool, List[str]]:
    """Validate that workflow files have valid YAML syntax."""
    issues = []

    try:
        import yaml
    except ImportError:
        issues.append("PyYAML not available - skipping YAML validation")
        return True, issues

    workflow_dir = project_root / ".github" / "workflows"
    if not workflow_dir.exists():
        issues.append("GitHub workflows directory not found")
        return False, issues

    workflow_files = list(workflow_dir.glob("*.yml")) + list(workflow_dir.glob("*.yaml"))

    for workflow_file in workflow_files:
        try:
            content = workflow_file.read_text(encoding='utf-8')
            yaml.safe_load(content)
        except yaml.YAMLError as e:
            issues.append(f"YAML syntax error in {workflow_file.name}: {e}")
        except Exception as e:
            issues.append(f"Error validating {workflow_file.name}: {e}")

    return len([issue for issue in issues if "syntax error" in issue]) == 0, issues


def update_deployment_scripts(project_root: Path) -> Tuple[bool, List[str]]:
    """Update deployment scripts to use new paths."""
    issues = []

    deployment_scripts = [
        "scripts/deployment/deploy_production.sh",
        "scripts/deployment/backup_production.sh"
    ]

    for script_path in deployment_scripts:
        full_path = project_root / script_path
        if full_path.exists():
            try:
                content = full_path.read_text(encoding='utf-8')
                original_content = content

                # Update Docker Compose references
                content = content.replace(
                    "docker-compose.production.yml",
                    "config/docker/docker-compose.production.yml"
                )
                content = content.replace(
                    "docker-compose.basic.yml",
                    "config/docker/docker-compose.basic.yml"
                )

                # Update environment file references
                content = content.replace(
                    ".env.production",
                    "config/environments/production.env.backup"
                )
                content = content.replace(
                    ".env",
                    "config/environments/development.env"
                )

                if content != original_content:
                    full_path.write_text(content, encoding='utf-8')
                    issues.append(f"Updated deployment script: {script_path}")

            except Exception as e:
                issues.append(f"Error updating deployment script {script_path}: {e}")
        else:
            issues.append(f"Deployment script not found: {script_path}")

    return True, issues


def main():
    """Main function to update CI/CD workflows."""
    project_root = Path(__file__).parent.parent.parent

    print("🔧 Updating CI/CD Workflows and Deployment Scripts")
    print(f"📁 Project root: {project_root}")
    print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print()

    all_passed = True

    # Run all updates
    updates = [
        ("Fix Corrupted References", fix_corrupted_references),
        ("Validate Workflow Syntax", validate_workflow_syntax),
        ("Update Deployment Scripts", update_deployment_scripts)
    ]

    for update_name, update_func in updates:
        print(f"🔍 {update_name}...")
        passed, issues = update_func(project_root)

        if passed:
            print(f"✅ {update_name}: COMPLETED")
            for issue in issues:
                if "Updated" in issue or "syntax error" not in issue:
                    print(f"   • {issue}")
        else:
            print(f"❌ {update_name}: FAILED")
            for issue in issues:
                print(f"   • {issue}")
            all_passed = False
        print()

    # Summary
    if all_passed:
        print("🎉 All CI/CD workflow updates COMPLETED!")
        print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        return 0

    print("⚠️  Some CI/CD workflow updates FAILED!")
    print("Please address the issues above before proceeding.")
    return 1


if __name__ == "__main__":
    sys.exit(main())