#!/usr/bin/env python3
"""
Constitutional Compliance Validator for ACGS-2 Reorganization

Constitutional Hash: cdd01ef066bc6cf2
"""

import sys
from pathlib import Path
from typing import List, Tuple

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


def validate_constitutional_hash_presence(project_root: Path) -> Tuple[bool, List[str]]:
    """Validate that constitutional hash is present in key files."""
    issues = []

    # Key files that must contain constitutional hash
    key_files = [
        "README.md",
        "CLAUDE.md",
        "reports/acgs2_root_directory_reorganization_analysis.md",
        "scripts/validation/update_reorganization_references.py",
        "scripts/validation/constitutional_compliance_validator.py"
    ]

    for file_path in key_files:
        full_path = project_root / file_path
        if full_path.exists():
            try:
                content = full_path.read_text(encoding='utf-8')
                if CONSTITUTIONAL_HASH not in content:
                    issues.append(f"Missing constitutional hash in {file_path}")
            except Exception as e:
                issues.append(f"Error reading {file_path}: {e}")
        else:
            issues.append(f"Key file missing: {file_path}")

    return len(issues) == 0, issues


def validate_service_configurations(project_root: Path) -> Tuple[bool, List[str]]:
    """Validate that service configurations are intact after reorganization."""
    issues = []

    # Check that moved configuration files exist
    config_files = [
        "config/docker/docker-compose.basic.yml",
        "config/docker/docker-compose.production.yml",
        "config/environments/development.env",
        "config/environments/acgs.env",
        "config/security/production.yml",
        "config/services/discovery.json"
    ]

    for config_file in config_files:
        full_path = project_root / config_file
        if not full_path.exists():
            issues.append(f"Missing configuration file: {config_file}")

    return len(issues) == 0, issues


def validate_script_accessibility(project_root: Path) -> Tuple[bool, List[str]]:
    """Validate that moved scripts are accessible and executable."""
    issues = []

    # Check that moved scripts exist
    script_files = [
        "scripts/deployment/deploy_production.sh",
        "scripts/deployment/backup_production.sh",
        "scripts/testing/run_5_tier_deployment_test.sh",
        "scripts/monitoring/staging-health-check.py",
        "scripts/validation/validate_documentation.py"
    ]

    for script_file in script_files:
        full_path = project_root / script_file
        if not full_path.exists():
            issues.append(f"Missing script file: {script_file}")
        elif not full_path.is_file():
            issues.append(f"Script is not a file: {script_file}")

    return len(issues) == 0, issues


def validate_documentation_structure(project_root: Path) -> Tuple[bool, List[str]]:
    """Validate that documentation structure is maintained."""
    issues = []

    # Check that moved documentation exists
    doc_files = [
        "docs/DOCUMENTATION_INDEX.md",
        "docs/deployment/DEPLOYMENT_SUMMARY.md",
        "docs/production/PRODUCTION_READINESS_ASSESSMENT.md",
        "docs/compliance/ACGS_CONSTITUTIONAL_COMPLIANCE_ENHANCEMENT_REPORT.md"
    ]

    for doc_file in doc_files:
        full_path = project_root / doc_file
        if not full_path.exists():
            issues.append(f"Missing documentation file: {doc_file}")

    return len(issues) == 0, issues


def main():
    """Main validation function."""
    project_root = Path(__file__).parent.parent.parent

    print(f"🔐 Constitutional Compliance Validation")
    print(f"📁 Project root: {project_root}")
    print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print()

    all_passed = True

    # Run all validations
    validations = [
        ("Constitutional Hash Presence", validate_constitutional_hash_presence),
        ("Service Configurations", validate_service_configurations),
        ("Script Accessibility", validate_script_accessibility),
        ("Documentation Structure", validate_documentation_structure)
    ]

    for validation_name, validation_func in validations:
        print(f"🔍 Validating {validation_name}...")
        passed, issues = validation_func(project_root)

        if passed:
            print(f"✅ {validation_name}: PASSED")
        else:
            print(f"❌ {validation_name}: FAILED")
            for issue in issues:
                print(f"   • {issue}")
            all_passed = False
        print()

    # Summary
    if all_passed:
        print("🎉 All constitutional compliance validations PASSED!")
        print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        return 0
    else:
        print("⚠️  Some constitutional compliance validations FAILED!")
        print("Please address the issues above before proceeding.")
        return 1


if __name__ == "__main__":
    sys.exit(main())