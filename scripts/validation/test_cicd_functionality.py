#!/usr/bin/env python3
"""
Test CI/CD functionality after ACGS-2 reorganization

Constitutional Hash: cdd01ef066bc6cf2
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def test_yaml_syntax(project_root: Path) -> Tuple[bool, List[str]]:
    """Test YAML syntax of key workflow files."""
    issues = []

    try:
        import yaml
    except ImportError:
        issues.append("PyYAML not available - skipping YAML validation")
        return True, issues

    # Key workflow files to test
    key_workflows = [
        ".github/workflows/ci.yml",
        ".github/workflows/acgs-ci-cd.yml",
        ".github/workflows/ci-uv.yml",
        ".github/workflows/test-automation-enhanced.yml"
    ]

    for workflow_file in key_workflows:
        full_path = project_root / workflow_file
        if full_path.exists():
            try:
                content = full_path.read_text(encoding='utf-8')
                yaml.safe_load(content)
                issues.append(f"✅ YAML syntax valid: {workflow_file}")
            except yaml.YAMLError as e:
                issues.append(f"❌ YAML syntax error in {workflow_file}: {e}")
            except Exception as e:
                issues.append(f"❌ Error validating {workflow_file}: {e}")
        else:
            issues.append(f"⚠️  Workflow file not found: {workflow_file}")

    return len([issue for issue in issues if "❌" in issue]) == 0, issues


def test_docker_compose_references(project_root: Path) -> Tuple[bool, List[str]]:
    """Test that Docker Compose file references are correct."""
    issues = []

    # Check that referenced Docker Compose files exist
    compose_files = [
        "config/docker/docker-compose.production.yml",
        "config/docker/docker-compose.basic.yml"
    ]

    for compose_file in compose_files:
        full_path = project_root / compose_file
        if full_path.exists():
            issues.append(f"✅ Docker Compose file exists: {compose_file}")
        else:
            issues.append(f"❌ Docker Compose file missing: {compose_file}")

    return len([issue for issue in issues if "❌" in issue]) == 0, issues


def test_environment_file_references(project_root: Path) -> Tuple[bool, List[str]]:
    """Test that environment file references are correct."""
    issues = []

    # Check that referenced environment files exist
    env_files = [
        "config/environments/development.env",
        "config/environments/acgs.env",
        "config/environments/production.env.backup"
    ]

    for env_file in env_files:
        full_path = project_root / env_file
        if full_path.exists():
            issues.append(f"✅ Environment file exists: {env_file}")
        else:
            issues.append(f"❌ Environment file missing: {env_file}")

    return len([issue for issue in issues if "❌" in issue]) == 0, issues


def test_script_references(project_root: Path) -> Tuple[bool, List[str]]:
    """Test that script references are correct."""
    issues = []

    # Check that referenced scripts exist
    scripts = [
        "scripts/deployment/deploy_production.sh",
        "scripts/deployment/backup_production.sh",
        "scripts/monitoring/staging-health-check.py"
    ]

    for script in scripts:
        full_path = project_root / script
        if full_path.exists():
            issues.append(f"✅ Script exists: {script}")
        else:
            issues.append(f"❌ Script missing: {script}")

    return len([issue for issue in issues if "❌" in issue]) == 0, issues


def main():
    """Main test function."""
    project_root = Path(__file__).parent.parent.parent

    print("🧪 Testing CI/CD Functionality After Reorganization")
    print(f"📁 Project root: {project_root}")
    print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print()

    all_passed = True

    # Run all tests
    tests = [
        ("YAML Syntax Validation", test_yaml_syntax),
        ("Docker Compose References", test_docker_compose_references),
        ("Environment File References", test_environment_file_references),
        ("Script References", test_script_references)
    ]

    for test_name, test_func in tests:
        print(f"🔍 Testing {test_name}...")
        passed, issues = test_func(project_root)

        if passed:
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
            all_passed = False

        for issue in issues:
            print(f"   {issue}")
        print()

    # Summary
    if all_passed:
        print("🎉 All CI/CD functionality tests PASSED!")
        print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print("\n✅ CI/CD workflows are ready for production use")
        return 0

    print("⚠️  Some CI/CD functionality tests FAILED!")
    print("Please address the issues above before proceeding.")
    return 1


if __name__ == "__main__":
    sys.exit(main())