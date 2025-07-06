#!/usr/bin/env python3
"""
ACGS Constitutional Compliance Remediation Script
Constitutional Hash: cdd01ef066bc6cf2

This script adds the constitutional hash to all documentation files that are missing it,
ensuring 100% compliance across all 108 documentation files.
"""

import sys
from pathlib import Path

# Configuration
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REPO_ROOT = Path(__file__).parent.parent
DOCS_DIR = REPO_ROOT / "docs"

# Files that are missing the constitutional hash (from validation)
MISSING_HASH_FILES = [
    "docs/deployment/ACGS_GITOPS_DEPLOYMENT_GUIDE.md",
    "docs/deployment/WORKFLOW_TRANSITION_GUIDE.md",
    "docs/deployment/BRANCH_PROTECTION_GUIDE.md",
    "docs/deployment/MIGRATION_GUIDE_OPENCODE.md",
    "docs/ACADEMIC_PAPER_ENHANCEMENT_GUIDE.md",
    "docs/performance_benchmarking_plan.md",
    "docs/openrouter_integration.md",
    "docs/acge.md",
    "docs/WORKFLOW_MODERNIZATION_REPORT.md",
    "docs/emergency_rollback_procedures.md",
    "docs/implementation/ACGS_CODE_ANALYSIS_ENGINE_IMPLEMENTATION_PLAN.md",
    "docs/architecture/ACGS_CLAUDIA_INTEGRATION_ARCHITECTURE.md",
    "docs/architecture/NEXT_PHASE_ROADMAP.md",
    "docs/architecture/ACGS_2_COMPLETE_IMPLEMENTATION_REPORT.md",
    "docs/architecture/ACGS_PAPER_UPDATE_SUMMARY.md",
    "docs/architecture/ACGS_R_MARKDOWN_ANALYSIS_AUDIT_REPORT.md",
    "docs/ACGE_COST_ANALYSIS_ROI_PROJECTIONS.md",
    "docs/phase1_completion_report.md",
    "docs/Robust Application Context Layer Design_.md",
    "docs/risk_assessed_migration_plan.md",
    "docs/security/SECURITY.md",
    "docs/security/SECURITY_REMEDIATION_REPORT.md",
    "docs/workflow_fixes_summary.md",
    "docs/CI_CD_FIXES_REPORT.md",
    "docs/WORKFLOW_OPTIMIZATION_REPORT.md",
    "docs/DEPENDENCIES.md",
    "docs/api/api-docs-index.md",
    "docs/security_validation_completion_report.md",
    "docs/workflow_validation_summary.md",
    "docs/workflow_systematic_fixes_final_report.md",
    "docs/TEST_IMPROVEMENTS_SUMMARY.md",
    "docs/README.md",
    "docs/DEPENDENCY_MANAGEMENT_COMPLETE.md",
    "docs/cost_benefit_analysis.md",
    "docs/PYTEST_WARNING_FIXES.md",
    "docs/free_model_usage.md",
    "docs/COST_OPTIMIZATION_SUMMARY.md",
    "docs/phase2_completion_report.md",
    "docs/Tasks_2025-07-01T01-27-55.md",
    "docs/executive_summary.md",
    "docs/CHANGELOG.md",
]


def add_constitutional_hash_to_file(file_path: Path) -> tuple[bool, str]:
    """
    Add constitutional hash to a markdown file.

    Args:
        file_path: Path to the markdown file

    Returns:
        Tuple of (success, message)
    """
    try:
        if not file_path.exists():
            return False, f"File does not exist: {file_path}"

        # Read the file content
        with open(file_path, encoding="utf-8") as f:
            content = f.read()

        # Check if constitutional hash already exists
        if CONSTITUTIONAL_HASH in content:
            return True, f"Constitutional hash already present in {file_path.name}"

        # Determine where to add the constitutional hash
        lines = content.split("\n")

        # Strategy 1: Add after the first heading if it exists
        insert_index = 0
        constitutional_comment = f"<!-- Constitutional Hash: {CONSTITUTIONAL_HASH} -->"

        # Find the first heading
        for i, line in enumerate(lines):
            if line.strip().startswith("#"):
                insert_index = i + 1
                break

        # If no heading found, add at the beginning
        if insert_index == 0:
            lines.insert(0, constitutional_comment)
            lines.insert(1, "")
        else:
            lines.insert(insert_index, "")
            lines.insert(insert_index + 1, constitutional_comment)
            lines.insert(insert_index + 2, "")

        # Write the updated content back
        updated_content = "\n".join(lines)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(updated_content)

        return True, f"Successfully added constitutional hash to {file_path.name}"

    except Exception as e:
        return False, f"Error processing {file_path.name}: {e!s}"


def main():
    """Main execution function."""
    print("🚀 ACGS Constitutional Compliance Remediation")
    print("=" * 50)
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print(f"Repository Root: {REPO_ROOT}")
    print(f"Files to process: {len(MISSING_HASH_FILES)}")
    print()

    success_count = 0
    error_count = 0
    errors = []

    for file_rel_path in MISSING_HASH_FILES:
        file_path = REPO_ROOT / file_rel_path
        success, message = add_constitutional_hash_to_file(file_path)

        if success:
            print(f"✅ {message}")
            success_count += 1
        else:
            print(f"❌ {message}")
            error_count += 1
            errors.append(message)

    print()
    print("=" * 50)
    print("📊 REMEDIATION SUMMARY")
    print("=" * 50)
    print(f"✅ Successfully processed: {success_count} files")
    print(f"❌ Errors encountered: {error_count} files")
    print(f"📈 Success rate: {(success_count / len(MISSING_HASH_FILES)) * 100:.1f}%")

    if errors:
        print("\n🔍 ERRORS ENCOUNTERED:")
        for error in errors:
            print(f"  - {error}")

    # Verify the results
    print("\n🔍 VERIFICATION")
    print("=" * 30)

    # Count files with constitutional hash after remediation
    total_docs = 0
    docs_with_hash = 0

    for md_file in DOCS_DIR.rglob("*.md"):
        total_docs += 1
        try:
            with open(md_file, encoding="utf-8") as f:
                if CONSTITUTIONAL_HASH in f.read():
                    docs_with_hash += 1
        except Exception:
            pass

    compliance_percentage = (docs_with_hash / total_docs) * 100 if total_docs > 0 else 0

    print(f"📄 Total documentation files: {total_docs}")
    print(f"✅ Files with constitutional hash: {docs_with_hash}")
    print(f"📊 Compliance percentage: {compliance_percentage:.1f}%")

    if compliance_percentage == 100.0:
        print("\n🎉 SUCCESS: 100% constitutional compliance achieved!")
        return 0
    else:
        print(
            f"\n⚠️  WARNING: {total_docs - docs_with_hash} files still missing"
            " constitutional hash"
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
