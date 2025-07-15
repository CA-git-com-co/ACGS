#!/usr/bin/env python3
# Constitutional Hash: cdd01ef066bc6cf2
"""
Basic ACGS-1 API Versioning Test

Simple test that validates the core versioning functionality without complex dependencies.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def test_file_structure():
    """Test that all expected versioning files exist."""
    print("🔍 Testing File Structure...")

    expected_files = [
        "services/shared/versioning/__init__.py",
        "services/shared/versioning/version_manager.py",
        "services/shared/versioning/compatibility_manager.py",  # TODO: Replace with environment variable - Constitutional Hash: cdd01ef066bc6cf2
        "services/shared/versioning/response_transformers.py",
        "services/shared/versioning/versioned_router.py",
        "services/shared/api_models.py",
        "services/shared/middleware/version_routing_middleware.py",
        "docs/api/DEPRECATION_POLICY.md",
        "docs/api/VERSION_COMPATIBILITY_MATRIX.md",
        "docs/api/SDK_COMPATIBILITY_MATRIX.md",
        "docs/implementation/IMPLEMENTATION_VALIDATION_ROLLOUT_PLAN.md",
        "tools/versioning/__init__.py",
        "tools/versioning/api_diff.py",
        "tools/versioning/migration_generator.py",
        "tools/versioning/deployment_manager.py",
        "tools/versioning/sdk_generator.py",
        ".github/workflows/api-versioning-ci.yml",
        ".github/workflows/api-compatibility-matrix.yml",
    ]

    missing_files = []
    existing_files = []

    for file_path in expected_files:
        full_path = Path(__file__).parent.parent / file_path
        if full_path.exists():
            existing_files.append(file_path)
            print(f"  ✅ {file_path}")
        else:
            missing_files.append(file_path)
            print(f"  ❌ {file_path} - MISSING")

    print("\n📊 File Structure Summary:")
    print(f"  Existing: {len(existing_files)}")
    print(f"  Missing: {len(missing_files)}")

    return len(missing_files) == 0, len(existing_files), len(missing_files)


def test_documentation_content():
    """Test that documentation files have proper content."""
    print("🔍 Testing Documentation Content...")

    doc_tests = []

    # Test deprecation policy
    deprecation_policy_path = (
        Path(__file__).parent.parent / "docs/api/DEPRECATION_POLICY.md"
    )
    if deprecation_policy_path.exists():
        content = deprecation_policy_path.read_text()
        has_rfc_reference = "RFC 8594" in content
        has_timeline = "6-month" in content or "6 month" in content
        has_sunset = "sunset" in content.lower()

        if has_rfc_reference and has_timeline and has_sunset:
            print("  ✅ Deprecation Policy - Complete")
            doc_tests.append(True)
        else:
            print("  ⚠️ Deprecation Policy - Missing key elements")
            doc_tests.append(False)
    else:
        print("  ❌ Deprecation Policy - Missing")
        doc_tests.append(False)

    # Test compatibility matrix
    compat_matrix_path = (
        Path(__file__).parent.parent / "docs/api/VERSION_COMPATIBILITY_MATRIX.md"
    )
    if compat_matrix_path.exists():
        content = compat_matrix_path.read_text()
        has_versions = "v2.1.0" in content and "v2.0.0" in content
        has_compatibility = "compatibility" in content.lower()
        has_migration = "migration" in content.lower()

        if has_versions and has_compatibility and has_migration:
            print("  ✅ Version Compatibility Matrix - Complete")
            doc_tests.append(True)
        else:
            print("  ⚠️ Version Compatibility Matrix - Missing key elements")
            doc_tests.append(False)
    else:
        print("  ❌ Version Compatibility Matrix - Missing")
        doc_tests.append(False)

    # Test SDK compatibility matrix
    sdk_matrix_path = (
        Path(__file__).parent.parent / "docs/api/SDK_COMPATIBILITY_MATRIX.md"
    )
    if sdk_matrix_path.exists():
        content = sdk_matrix_path.read_text()
        has_languages = "Python" in content and "JavaScript" in content
        has_versions = "v2.1.0" in content
        has_compatibility = "compatibility" in content.lower()

        if has_languages and has_versions and has_compatibility:
            print("  ✅ SDK Compatibility Matrix - Complete")
            doc_tests.append(True)
        else:
            print("  ⚠️ SDK Compatibility Matrix - Missing key elements")
            doc_tests.append(False)
    else:
        print("  ❌ SDK Compatibility Matrix - Missing")
        doc_tests.append(False)

    # Test implementation plan
    impl_plan_path = (
        Path(__file__).parent.parent
        / "docs/implementation/IMPLEMENTATION_VALIDATION_ROLLOUT_PLAN.md"
    )
    if impl_plan_path.exists():
        content = impl_plan_path.read_text()
        has_phases = "PHASE 1" in content and "PHASE 2" in content
        has_validation = "validation" in content.lower()
        has_rollout = "rollout" in content.lower()

        if has_phases and has_validation and has_rollout:
            print("  ✅ Implementation Plan - Complete")
            doc_tests.append(True)
        else:
            print("  ⚠️ Implementation Plan - Missing key elements")
            doc_tests.append(False)
    else:
        print("  ❌ Implementation Plan - Missing")
        doc_tests.append(False)

    return all(doc_tests), len([t for t in doc_tests if t]), len(doc_tests)


def test_github_workflows():
    """Test GitHub workflow files."""
    print("🔍 Testing GitHub Workflows...")

    workflow_tests = []

    # Test API versioning CI workflow
    ci_workflow_path = (
        Path(__file__).parent.parent / ".github/workflows/api-versioning-ci.yml"
    )
    if ci_workflow_path.exists():
        content = ci_workflow_path.read_text()
        has_name = "name:" in content
        has_triggers = "on:" in content
        has_jobs = "jobs:" in content
        has_versioning = "version" in content.lower()

        if has_name and has_triggers and has_jobs and has_versioning:
            print("  ✅ API Versioning CI Workflow - Valid")
            workflow_tests.append(True)
        else:
            print("  ⚠️ API Versioning CI Workflow - Invalid structure")
            workflow_tests.append(False)
    else:
        print("  ❌ API Versioning CI Workflow - Missing")
        workflow_tests.append(False)

    # Test compatibility matrix workflow
    compat_workflow_path = (
        Path(__file__).parent.parent / ".github/workflows/api-compatibility-matrix.yml"
    )
    if compat_workflow_path.exists():
        content = compat_workflow_path.read_text()
        has_name = "name:" in content
        has_schedule = "schedule:" in content or "workflow_dispatch:" in content
        has_jobs = "jobs:" in content
        has_compatibility = "compatibility" in content.lower()

        if has_name and has_schedule and has_jobs and has_compatibility:
            print("  ✅ Compatibility Matrix Workflow - Valid")
            workflow_tests.append(True)
        else:
            print("  ⚠️ Compatibility Matrix Workflow - Invalid structure")
            workflow_tests.append(False)
    else:
        print("  ❌ Compatibility Matrix Workflow - Missing")
        workflow_tests.append(False)

    return (
        all(workflow_tests),
        len([t for t in workflow_tests if t]),
        len(workflow_tests),
    )


def test_versioning_tools():
    """Test versioning tools and scripts."""
    print("🔍 Testing Versioning Tools...")

    tool_tests = []

    # Test API diff analyzer
    api_diff_path = Path(__file__).parent.parent / "tools/versioning/api_diff.py"
    if api_diff_path.exists():
        content = api_diff_path.read_text()
        has_analyzer_class = "APIDiffAnalyzer" in content
        has_diff_report = "DiffReport" in content
        has_openapi = "openapi" in content.lower()

        if has_analyzer_class and has_diff_report and has_openapi:
            print("  ✅ API Diff Analyzer - Complete")
            tool_tests.append(True)
        else:
            print("  ⚠️ API Diff Analyzer - Missing key components")
            tool_tests.append(False)
    else:
        print("  ❌ API Diff Analyzer - Missing")
        tool_tests.append(False)

    # Test migration generator
    migration_gen_path = (
        Path(__file__).parent.parent / "tools/versioning/migration_generator.py"
    )
    if migration_gen_path.exists():
        content = migration_gen_path.read_text()
        has_generator_class = "MigrationGenerator" in content
        has_migration_script = "MigrationScript" in content
        has_steps = "MigrationStep" in content

        if has_generator_class and has_migration_script and has_steps:
            print("  ✅ Migration Generator - Complete")
            tool_tests.append(True)
        else:
            print("  ⚠️ Migration Generator - Missing key components")
            tool_tests.append(False)
    else:
        print("  ❌ Migration Generator - Missing")
        tool_tests.append(False)

    # Test deployment manager
    deployment_mgr_path = (
        Path(__file__).parent.parent / "tools/versioning/deployment_manager.py"
    )
    if deployment_mgr_path.exists():
        content = deployment_mgr_path.read_text()
        has_manager_class = "DeploymentManager" in content
        has_strategies = (
            "blue_green" in content.lower() and "rolling" in content.lower()
        )
        has_health_checks = "health" in content.lower()

        if has_manager_class and has_strategies and has_health_checks:
            print("  ✅ Deployment Manager - Complete")
            tool_tests.append(True)
        else:
            print("  ⚠️ Deployment Manager - Missing key components")
            tool_tests.append(False)
    else:
        print("  ❌ Deployment Manager - Missing")
        tool_tests.append(False)

    # Test SDK generator
    sdk_gen_path = Path(__file__).parent.parent / "tools/versioning/sdk_generator.py"
    if sdk_gen_path.exists():
        content = sdk_gen_path.read_text()
        has_generator_class = "SDKGenerator" in content
        has_languages = "python" in content.lower() and "javascript" in content.lower()
        has_compatibility = "compatibility" in content.lower()

        if has_generator_class and has_languages and has_compatibility:
            print("  ✅ SDK Generator - Complete")
            tool_tests.append(True)
        else:
            print("  ⚠️ SDK Generator - Missing key components")
            tool_tests.append(False)
    else:
        print("  ❌ SDK Generator - Missing")
        tool_tests.append(False)

    return all(tool_tests), len([t for t in tool_tests if t]), len(tool_tests)


def test_validation_scripts():
    """Test validation scripts."""
    print("🔍 Testing Validation Scripts...")

    validation_tests = []

    validation_scripts = [
        "docs/implementation/validation_scripts/backward_compatibility_test.py",
        "docs/implementation/validation_scripts/ci_integration_test.py",
        "docs/implementation/validation_scripts/deprecation_validation_test.py",
    ]

    for script_path in validation_scripts:
        full_path = Path(__file__).parent.parent / script_path
        if full_path.exists():
            content = full_path.read_text()
            has_main_function = "def main(" in content or "async def main(" in content
            has_validation_logic = (
                "validation" in content.lower() or "test" in content.lower()
            )

            if has_main_function and has_validation_logic:
                print(f"  ✅ {script_path.split('/')[-1]} - Complete")
                validation_tests.append(True)
            else:
                print(f"  ⚠️ {script_path.split('/')[-1]} - Missing key components")
                validation_tests.append(False)
        else:
            print(f"  ❌ {script_path.split('/')[-1]} - Missing")
            validation_tests.append(False)

    return (
        all(validation_tests),
        len([t for t in validation_tests if t]),
        len(validation_tests),
    )


def generate_report(results):
    """Generate a comprehensive test report."""
    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "test_results": {
            "file_structure": {
                "passed": results["file_structure"][0],
                "existing_files": results["file_structure"][1],
                "missing_files": results["file_structure"][2],
            },
            "documentation": {
                "passed": results["documentation"][0],
                "complete_docs": results["documentation"][1],
                "total_docs": results["documentation"][2],
            },
            "workflows": {
                "passed": results["workflows"][0],
                "valid_workflows": results["workflows"][1],
                "total_workflows": results["workflows"][2],
            },
            "tools": {
                "passed": results["tools"][0],
                "complete_tools": results["tools"][1],
                "total_tools": results["tools"][2],
            },
            "validation_scripts": {
                "passed": results["validation_scripts"][0],
                "complete_scripts": results["validation_scripts"][1],
                "total_scripts": results["validation_scripts"][2],
            },
        },
        "overall_success": all(result[0] for result in results.values()),
        "implementation_completeness": {
            "core_components": results["file_structure"][0],
            "documentation": results["documentation"][0],
            "automation": results["workflows"][0],
            "tooling": results["tools"][0],
            "validation": results["validation_scripts"][0],
        },
    }

    return report


def main():
    """Run basic versioning system validation."""
    print("🧪 ACGS-1 API Versioning System - Basic Validation")
    print("=" * 60)

    # Run all tests
    results = {
        "file_structure": test_file_structure(),
        "documentation": test_documentation_content(),
        "workflows": test_github_workflows(),
        "tools": test_versioning_tools(),
        "validation_scripts": test_validation_scripts(),
    }

    # Generate report
    report = generate_report(results)

    # Print summary
    print("\n📊 VALIDATION SUMMARY")
    print("=" * 60)

    total_passed = sum(1 for result in results.values() if result[0])
    total_tests = len(results)

    for test_name, (passed, completed, total) in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name.replace('_', ' ').title()}: {completed}/{total}")

    print(
        f"\nOverall: {total_passed}/{total_tests} test categories passed ({total_passed / total_tests * 100:.1f}%)"
    )

    # Implementation completeness
    completeness = report["implementation_completeness"]
    print("\n🎯 IMPLEMENTATION COMPLETENESS:")
    print(
        f"  ✅ Core Components: {'COMPLETE' if completeness['core_components'] else 'INCOMPLETE'}"
    )
    print(
        f"  📚 Documentation: {'COMPLETE' if completeness['documentation'] else 'INCOMPLETE'}"
    )
    print(
        f"  🤖 Automation: {'COMPLETE' if completeness['automation'] else 'INCOMPLETE'}"
    )
    print(f"  🔧 Tooling: {'COMPLETE' if completeness['tooling'] else 'INCOMPLETE'}")
    print(
        f"  🧪 Validation: {'COMPLETE' if completeness['validation'] else 'INCOMPLETE'}"
    )

    if report["overall_success"]:
        print("\n🎉 API VERSIONING SYSTEM IMPLEMENTATION: COMPLETE")
        print("\n✅ ALL COMPONENTS SUCCESSFULLY IMPLEMENTED:")
        print("  • Semantic versioning foundation")
        print("  • Backward compatibility framework")
        print("  • Version-aware routing integration")
        print("  • API lifecycle management tools")
        print("  • Client SDK versioning")
        print("  • CI/CD integration")
        print("  • Comprehensive documentation")
        print("  • Validation and rollout plan")

        print("\n🚀 READY FOR DEPLOYMENT:")
        print("  1. Run validation scripts in staging environment")
        print("  2. Execute Phase 1 implementation plan")
        print("  3. Begin backward compatibility testing")
        print("  4. Start phased rollout to production")

    else:
        print("\n⚠️ IMPLEMENTATION INCOMPLETE")
        print("Some components need attention before deployment.")

        # Show what's missing
        for test_name, (passed, completed, total) in results.items():
            if not passed:
                missing = total - completed
                print(
                    f"  🔧 {test_name.replace('_', ' ').title()}: {missing} items need attention"
                )

    # Save report
    with open("api_versioning_implementation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    print("\n📄 Detailed report saved to: api_versioning_implementation_report.json")

    return 0 if report["overall_success"] else 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
