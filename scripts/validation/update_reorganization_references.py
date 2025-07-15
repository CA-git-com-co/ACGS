#!/usr/bin/env python3
"""
Update file references after ACGS-2 root directory reorganization.

Constitutional Hash: cdd01ef066bc6cf2
"""

import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Path mappings for reorganization
PATH_MAPPINGS = {
    # Docker configurations
    "config/docker/docker-compose.basic.yml": "config/docker/config/docker/docker-compose.basic.yml",
    "config/docker/docker-compose.production.yml": "config/docker/config/docker/docker-compose.production.yml",
    "config/docker/Dockerfile.uv": "config/docker/config/docker/Dockerfile.uv",

    # Environment files
    "config/environments/development.env": "config/environments/developmentconfig/environments/development.env",
    "config/environments/developmentconfig/environments/acgs.env": "config/environments/acgsconfig/environments/development.env",
    "config/environments/developmentconfig/environments/template.env": "config/environments/templateconfig/environments/development.env",
    "config/environments/developmentconfig/environments/example.env": "config/environments/exampleconfig/environments/development.env",
    "config/environments/developmentconfig/environments/acgsconfig/environments/example.env": "config/environments/acgs.exampleconfig/environments/development.env",
    "config/environments/developmentconfig/environments/integrity.env": "config/environments/integrityconfig/environments/development.env",
    "config/environments/developmentconfig/environments/production.template.env": "config/environments/production.templateconfig/environments/development.env",
    "config/environments/developmentconfig/environments/sentry.example.env": "config/environments/sentry.exampleconfig/environments/development.env",
    "config/environments/developmentconfig/environments/test.env": "config/environments/testconfig/environments/development.env",
    "config/environments/developmentconfig/environments/production.env.backup": "config/environments/productionconfig/environments/development.env.backup",

    # Security configurations
    "config/security/production.yml": "config/security/production.yml",

    # Service configurations
    "config/services/discovery.json": "config/services/discovery.json",
    "config/validation/workflow-integration.json": "config/validation/workflow-integration.json",

    # Scripts
    "scripts/deployment/backup_production.sh": "scripts/deployment/scripts/deployment/backup_production.sh",
    "scripts/deployment/deploy_constitutional_hash.py": "scripts/deployment/scripts/deployment/deploy_constitutional_hash.py",
    "scripts/deployment/deploy_production.sh": "scripts/deployment/scripts/deployment/deploy_production.sh",
    "scripts/deployment/rollback_production.sh": "scripts/deployment/scripts/deployment/rollback_production.sh",
    "scripts/testing/run_5_tier_deployment_test.sh": "scripts/testing/scripts/testing/run_5_tier_deployment_test.sh",
    "scripts/testing/run_demo_deployment.sh": "scripts/testing/scripts/testing/run_demo_deployment.sh",
    "scripts/monitoring/staging-health-check.py": "scripts/monitoring/scripts/monitoring/staging-health-check.py",
    "scripts/testing/test_5_tier_router.py": "scripts/testing/scripts/testing/test_5_tier_router.py",
    "scripts/validation/validate_documentation.py": "scripts/validation/scripts/validation/validate_documentation.py",

    # Documentation files
    "docs/reports/ACGS_2_COMPREHENSIVE_REMEDIATION_SUMMARY.md": (
        "docs/reports/docs/reports/ACGS_2_COMPREHENSIVE_REMEDIATION_SUMMARY.md"
    ),
    "docs/compliance/ACGS_CONSTITUTIONAL_COMPLIANCE_ENHANCEMENT_REPORT.md": (
        "docs/compliance/docs/compliance/ACGS_CONSTITUTIONAL_COMPLIANCE_ENHANCEMENT_REPORT.md"
    ),
    "docs/deployment/DEPLOYMENT_SUMMARY.md": "docs/deployment/docs/deployment/DEPLOYMENT_SUMMARY.md",
    "docs/DOCUMENTATION_INDEX.md": "docs/docs/DOCUMENTATION_INDEX.md",
    "docs/deployment/FINAL_DEPLOYMENT_REPORT.md": "docs/deployment/docs/deployment/FINAL_DEPLOYMENT_REPORT.md",
    "docs/production/PRODUCTION_READINESS_ASSESSMENT.md": "docs/production/docs/production/PRODUCTION_READINESS_ASSESSMENT.md",
    "docs/integration/README_SENTRY_INTEGRATION.md": "docs/integration/docs/integration/README_SENTRY_INTEGRATION.md",
    "docs/maintenance/WORKFLOW_FIXES_SUMMARY.md": "docs/maintenance/docs/maintenance/WORKFLOW_FIXES_SUMMARY.md",

    # Reports and logs
    "logs/comprehensive_training.log": "logs/logs/comprehensive_training.log",
    "reports/stress_test_report.html": "reports/reports/stress_test_report.html",
    "reports/coverage/htmlcov/": "reports/coverage/reports/coverage/htmlcov/",
}


def find_files_with_references(project_root: Path) -> List[Path]:
    """Find files that might contain references to moved files."""
    file_patterns = [
        "*.py", "*.sh", "*.yml", "*.yaml", "*.json", "*.md",
        "*.txt", "*.toml", "*.cfg", "*.ini", "Dockerfile*", "Makefile"
    ]

    files_to_check = []
    exclude_dirs = {
        "__pycache__", ".git", "node_modules", "target",
        ".pytest_cache", "htmlcov", "logs", "archive"
    }

    for pattern in file_patterns:
        for file_path in project_root.rglob(pattern):
            # Skip files in excluded directories
            if any(excluded in file_path.parts for excluded in exclude_dirs):
                continue
            files_to_check.append(file_path)

    return files_to_check


def update_file_references(file_path: Path, mappings: Dict[str, str]) -> Tuple[bool, List[str]]:
    """Update file references in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        changes = []

        # Update each mapping
        for old_path, new_path in mappings.items():
            # Direct path references
            if old_path in content:
                content = content.replace(old_path, new_path)
                changes.append(f"{old_path} → {new_path}")

            # Quoted path references
            quoted_old = f'"{old_path}"'
            quoted_new = f'"{new_path}"'
            if quoted_old in content:
                content = content.replace(quoted_old, quoted_new)
                changes.append(f"{quoted_old} → {quoted_new}")

            # Single quoted path references
            single_quoted_old = f"'{old_path}'"
            single_quoted_new = f"'{new_path}'"
            if single_quoted_old in content:
                content = content.replace(single_quoted_old, single_quoted_new)
                changes.append(f"{single_quoted_old} → {single_quoted_new}")

        # Write back if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, changes

        return False, []

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False, []


def main():
    """Main function to update all file references."""
    project_root = Path(__file__).parent.parent.parent

    print(f"🔄 Updating file references after reorganization...")
    print(f"📁 Project root: {project_root}")
    print(f"🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")

    # Find all files that might contain references
    files_to_check = find_files_with_references(project_root)
    print(f"📊 Found {len(files_to_check)} files to check")

    updated_files = 0
    total_changes = 0

    # Update each file
    for file_path in files_to_check:
        was_updated, changes = update_file_references(file_path, PATH_MAPPINGS)

        if was_updated:
            updated_files += 1
            total_changes += len(changes)
            relative_path = file_path.relative_to(project_root)
            print(f"✅ Updated {relative_path}")
            for change in changes:
                print(f"   • {change}")

    print(f"\n📈 Summary:")
    print(f"   • Files checked: {len(files_to_check)}")
    print(f"   • Files updated: {updated_files}")
    print(f"   • Total changes: {total_changes}")
    print(f"   • Constitutional Hash: {CONSTITUTIONAL_HASH}")


if __name__ == "__main__":
    main()