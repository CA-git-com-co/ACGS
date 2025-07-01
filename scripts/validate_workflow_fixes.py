#!/usr/bin/env python3
"""
GitHub Actions Workflow Validation Script
Validates that all workflow fixes have been applied correctly and tests critical functionality.
"""

import os
import re
import yaml
import json
from pathlib import Path
from typing import Dict, List, Tuple


def validate_deprecated_actions(content: str, filepath: str) -> List[str]:
    """Validate that deprecated actions have been updated"""
    issues = []

    deprecated_patterns = [
        (r"actions/upload-artifact@v[123]", "actions/upload-artifact should be v4"),
        (r"actions/checkout@v[123]", "actions/checkout should be v4"),
        (r"actions/setup-node@v[123]", "actions/setup-node should be v4"),
        (r"actions/setup-python@v[1234]", "actions/setup-python should be v5"),
        (r"docker/build-push-action@v[12345]", "docker/build-push-action should be v6"),
        (r"codecov/codecov-action@v[1234]", "codecov/codecov-action should be v5"),
    ]

    for pattern, message in deprecated_patterns:
        if re.search(pattern, content):
            issues.append(f"❌ {message} in {filepath}")

    return issues


def validate_connectivity_checks(content: str, filepath: str) -> List[str]:
    """Validate that ping-based connectivity has been replaced with HTTP"""
    issues = []

    # Check for remaining ping commands
    if re.search(r"ping -c \d+ \w+", content):
        issues.append(f"❌ Ping-based connectivity still present in {filepath}")

    # Check for proper HTTP-based connectivity
    if "github.com" in content and not re.search(r"curl.*api\.github\.com", content):
        if "ping" in content:
            issues.append(f"⚠️  GitHub connectivity should use HTTP API in {filepath}")

    return issues


def validate_cargo_configuration(content: str, filepath: str) -> List[str]:
    """Validate CARGO_INCREMENTAL configuration"""
    issues = []

    # Check for conflicting CARGO_INCREMENTAL settings
    if re.search(r"CARGO_INCREMENTAL:\s*1", content) and "sccache" in content.lower():
        issues.append(f"❌ CARGO_INCREMENTAL=1 conflicts with sccache in {filepath}")

    return issues


def validate_timeout_protections(content: str, filepath: str) -> List[str]:
    """Validate that timeout protections are in place"""
    issues = []

    # Check for curl commands without timeouts
    curl_matches = re.findall(r"curl [^|&\n]*", content)
    for match in curl_matches:
        if "timeout" not in match and "github.com" in match:
            issues.append(
                f"⚠️  Curl command without timeout in {filepath}: {match[:50]}..."
            )

    return issues


def validate_error_handling(content: str, filepath: str) -> List[str]:
    """Validate error handling and retry mechanisms"""
    issues = []

    # Check for critical operations without error handling
    critical_operations = ["npm install", "cargo install", "anchor build"]
    for operation in critical_operations:
        if operation in content and "retry" not in content.lower():
            issues.append(
                f"ℹ️  Consider adding retry logic for '{operation}' in {filepath}"
            )

    return issues


def validate_workflow_syntax(filepath: str) -> List[str]:
    """Validate YAML syntax and basic workflow structure"""
    issues = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            workflow = yaml.safe_load(f)

        # Basic structure validation
        if "name" not in workflow:
            issues.append(f"❌ Missing workflow name in {filepath}")

        if "on" not in workflow:
            issues.append(f"❌ Missing trigger configuration in {filepath}")

        if "jobs" not in workflow:
            issues.append(f"❌ Missing jobs configuration in {filepath}")

        # Check for required permissions
        if "permissions" not in workflow:
            issues.append(f"ℹ️  Consider adding permissions section in {filepath}")

    except yaml.YAMLError as e:
        issues.append(f"❌ YAML syntax error in {filepath}: {e}")
    except Exception as e:
        issues.append(f"❌ Error reading {filepath}: {e}")

    return issues


def check_dependency_files() -> List[str]:
    """Check for missing dependency files"""
    issues = []

    # Check for root-level dependency files
    if not Path("requirements.txt").exists():
        issues.append("❌ Missing root-level requirements.txt")

    if not Path("package-lock.json").exists():
        issues.append("❌ Missing root-level package-lock.json")

    # Check for workspace-specific dependency files
    workspaces = ["applications", "blockchain"]
    for workspace in workspaces:
        workspace_path = Path(workspace)
        if workspace_path.exists():
            if not (workspace_path / "package-lock.json").exists():
                issues.append(f"⚠️  Missing package-lock.json in {workspace}")

    return issues


def validate_workflow_file(filepath: Path) -> Dict[str, List[str]]:
    """Validate a single workflow file"""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    validation_results = {
        "deprecated_actions": validate_deprecated_actions(content, str(filepath)),
        "connectivity_checks": validate_connectivity_checks(content, str(filepath)),
        "cargo_configuration": validate_cargo_configuration(content, str(filepath)),
        "timeout_protections": validate_timeout_protections(content, str(filepath)),
        "error_handling": validate_error_handling(content, str(filepath)),
        "workflow_syntax": validate_workflow_syntax(filepath),
    }

    return validation_results


def generate_validation_report(
    results: Dict[str, Dict[str, List[str]]], dependency_issues: List[str]
) -> str:
    """Generate a comprehensive validation report"""
    report = """# GitHub Actions Workflow Validation Report

## Summary
"""

    total_issues = sum(
        len(issues)
        for file_results in results.values()
        for issues in file_results.values()
    )
    total_issues += len(dependency_issues)

    if total_issues == 0:
        report += "✅ **All validations passed!** No issues found.\n\n"
    else:
        report += f"⚠️  **{total_issues} issues found** across workflow files.\n\n"

    # Dependency files section
    report += "## Dependency Files\n"
    if dependency_issues:
        for issue in dependency_issues:
            report += f"- {issue}\n"
    else:
        report += "✅ All required dependency files are present.\n"
    report += "\n"

    # Per-file validation results
    report += "## Workflow File Validation\n"
    for filepath, file_results in results.items():
        file_issues = sum(len(issues) for issues in file_results.values())
        if file_issues > 0:
            report += f"\n### {filepath} ({file_issues} issues)\n"
            for category, issues in file_results.items():
                if issues:
                    report += f"\n**{category.replace('_', ' ').title()}:**\n"
                    for issue in issues:
                        report += f"- {issue}\n"
        else:
            report += f"- ✅ {filepath}: No issues found\n"

    # Recommendations section
    report += "\n## Recommendations\n"
    if total_issues > 0:
        report += """
1. **Critical Issues**: Fix all ❌ issues immediately
2. **Warnings**: Address ⚠️  issues for improved reliability
3. **Suggestions**: Consider ℹ️  suggestions for best practices
4. **Testing**: Run manual workflow triggers to validate fixes
5. **Monitoring**: Set up workflow success rate monitoring
"""
    else:
        report += """
1. **Testing**: Run manual workflow triggers to validate all fixes
2. **Monitoring**: Set up workflow success rate monitoring
3. **Maintenance**: Regular review of workflow performance metrics
"""

    return report


def main():
    """Main validation function"""
    print("🔍 Starting GitHub Actions workflow validation...")

    # Find all workflow files
    workflow_dir = Path(".github/workflows")
    if not workflow_dir.exists():
        print("❌ .github/workflows directory not found!")
        return

    workflow_files = list(workflow_dir.glob("*.yml")) + list(
        workflow_dir.glob("*.yaml")
    )

    if not workflow_files:
        print("❌ No workflow files found!")
        return

    print(f"📁 Validating {len(workflow_files)} workflow files...")

    # Validate dependency files
    dependency_issues = check_dependency_files()

    # Validate each workflow file
    results = {}
    for workflow_file in workflow_files:
        print(f"🔍 Validating {workflow_file.name}...")
        results[str(workflow_file)] = validate_workflow_file(workflow_file)

    # Generate and save report
    report = generate_validation_report(results, dependency_issues)

    with open("GITHUB_ACTIONS_VALIDATION_REPORT.md", "w") as f:
        f.write(report)

    print(f"\n✅ Validation completed!")
    print(f"📄 Report saved: GITHUB_ACTIONS_VALIDATION_REPORT.md")

    # Print summary
    total_issues = sum(
        len(issues)
        for file_results in results.values()
        for issues in file_results.values()
    )
    total_issues += len(dependency_issues)

    if total_issues == 0:
        print("🎉 All validations passed! Workflows are ready for testing.")
    else:
        print(f"⚠️  Found {total_issues} issues that need attention.")


if __name__ == "__main__":
    main()
