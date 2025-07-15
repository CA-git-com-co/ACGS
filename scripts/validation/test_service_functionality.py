#!/usr/bin/env python3
"""
Service Functionality Test for ACGS-2 Reorganization

Constitutional Hash: cdd01ef066bc6cf2
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def test_docker_compose_files(project_root: Path) -> Tuple[bool, List[str]]:
    """Test that Docker Compose files are valid."""
    issues = []

    compose_files = [
        "config/docker/docker-compose.basic.yml",
        "config/docker/docker-compose.production.yml"
    ]

    for compose_file in compose_files:
        full_path = project_root / compose_file
        if full_path.exists():
            try:
                # Test Docker Compose file syntax
                result = subprocess.run(
                    ["docker-compose", "-f", str(full_path), "config"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0:
                    issues.append(f"Docker Compose validation failed for {compose_file}: {result.stderr}")
            except subprocess.TimeoutExpired:
                issues.append(f"Docker Compose validation timed out for {compose_file}")
            except FileNotFoundError:
                issues.append(f"Docker Compose not found - skipping validation for {compose_file}")
            except Exception as e:
                issues.append(f"Error validating {compose_file}: {e}")
        else:
            issues.append(f"Docker Compose file missing: {compose_file}")

    return len(issues) == 0, issues


def test_environment_files(project_root: Path) -> Tuple[bool, List[str]]:
    """Test that environment files are readable and contain expected variables."""
    issues = []

    env_files = [
        "config/environments/development.env",
        "config/environments/acgs.env",
        "config/environments/template.env"
    ]

    for env_file in env_files:
        full_path = project_root / env_file
        if full_path.exists():
            try:
                content = full_path.read_text(encoding='utf-8')
                # Check for basic environment variables
                if "ENVIRONMENT=" not in content and "ENV=" not in content:
                    issues.append(f"Environment file {env_file} missing ENVIRONMENT variable")
            except Exception as e:
                issues.append(f"Error reading environment file {env_file}: {e}")
        else:
            issues.append(f"Environment file missing: {env_file}")

    return len(issues) == 0, issues


def test_script_executability(project_root: Path) -> Tuple[bool, List[str]]:
    """Test that moved scripts are executable."""
    issues = []

    script_files = [
        "scripts/deployment/deploy_production.sh",
        "scripts/deployment/backup_production.sh",
        "scripts/testing/run_5_tier_deployment_test.sh"
    ]

    for script_file in script_files:
        full_path = project_root / script_file
        if full_path.exists():
            try:
                # Check if file is executable
                if not full_path.stat().st_mode & 0o111:
                    issues.append(f"Script not executable: {script_file}")

                # Test basic syntax for shell scripts
                if script_file.endswith('.sh'):
                    result = subprocess.run(
                        ["bash", "-n", str(full_path)],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        check=False
                    )
                    if result.returncode != 0:
                        issues.append(f"Shell script syntax error in {script_file}: {result.stderr}")

            except subprocess.TimeoutExpired:
                issues.append(f"Script validation timed out for {script_file}")
            except Exception as e:
                issues.append(f"Error testing script {script_file}: {e}")
        else:
            issues.append(f"Script file missing: {script_file}")

    return len(issues) == 0, issues


def test_python_imports(project_root: Path) -> Tuple[bool, List[str]]:
    """Test that Python scripts can be imported without errors."""
    issues = []

    python_scripts = [
        "scripts/monitoring/staging-health-check.py",
        "scripts/validation/validate_documentation.py",
        "scripts/validation/update_reorganization_references.py"
    ]

    for script_file in python_scripts:
        full_path = project_root / script_file
        if full_path.exists():
            try:
                # Test Python syntax
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", str(full_path)],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False
                )
                if result.returncode != 0:
                    issues.append(f"Python syntax error in {script_file}: {result.stderr}")

            except subprocess.TimeoutExpired:
                issues.append(f"Python validation timed out for {script_file}")
            except Exception as e:
                issues.append(f"Error testing Python script {script_file}: {e}")
        else:
            issues.append(f"Python script missing: {script_file}")

    return len(issues) == 0, issues


def main():
    """Main test function."""
    project_root = Path(__file__).parent.parent.parent

    print("🧪 Service Functionality Testing")
    print(f"📁 Project root: {project_root}")
    print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print()

    all_passed = True

    # Run all tests
    tests = [
        ("Docker Compose Files", test_docker_compose_files),
        ("Environment Files", test_environment_files),
        ("Script Executability", test_script_executability),
        ("Python Imports", test_python_imports)
    ]

    for test_name, test_func in tests:
        print(f"🔍 Testing {test_name}...")
        passed, issues = test_func(project_root)

        if passed:
            print(f"✅ {test_name}: PASSED")
        else:
            print(f"❌ {test_name}: FAILED")
            for issue in issues:
                print(f"   • {issue}")
            all_passed = False
        print()

    # Summary
    if all_passed:
        print("🎉 All service functionality tests PASSED!")
        print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        return 0

    print("⚠️  Some service functionality tests FAILED!")
    print("Please address the issues above before proceeding.")
    return 1


if __name__ == "__main__":
    sys.exit(main())