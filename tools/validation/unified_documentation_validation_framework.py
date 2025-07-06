#!/usr/bin/env python3
"""
ACGS Unified Documentation Validation Framework
Constitutional Hash: cdd01ef066bc6cf2

This framework consolidates all documentation validation tools into a unified system:
- Enhanced validation with cross-reference checking
- API-code synchronization validation
- Constitutional compliance verification
- Performance target consistency
- Link integrity validation
- Documentation quality metrics
- Automated reporting and remediation suggestions
"""

import json
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

# Configuration
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
REPO_ROOT = Path(__file__).parent.parent.parent
DOCS_DIR = REPO_ROOT / "docs"


# Import validation modules
def import_validation_tools():
    """Import validation tools with proper error handling."""
    tools = {}

    try:
        import importlib.util

        # Import enhanced validation
        enhanced_val_path = Path(__file__).parent / "enhanced_validation.py"
        if enhanced_val_path.exists():
            spec = importlib.util.spec_from_file_location(
                "enhanced_validation", enhanced_val_path
            )
            enhanced_val_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(enhanced_val_module)
            tools["enhanced_validator"] = enhanced_val_module.EnhancedValidator
            print("✅ Enhanced Validator imported")

        # Import consistency validator
        consistency_val_path = (
            Path(__file__).parent / "validate_documentation_consistency.py"
        )
        if consistency_val_path.exists():
            spec = importlib.util.spec_from_file_location(
                "validate_documentation_consistency", consistency_val_path
            )
            consistency_val_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(consistency_val_module)
            tools["consistency_validator"] = (
                consistency_val_module.ACGSDocumentationValidator
            )
            print("✅ Consistency Validator imported")

        # Import cross-reference analyzer
        cross_ref_path = Path(__file__).parent / "advanced_cross_reference_analyzer.py"
        if cross_ref_path.exists():
            spec = importlib.util.spec_from_file_location(
                "advanced_cross_reference_analyzer", cross_ref_path
            )
            cross_ref_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(cross_ref_module)
            tools["cross_ref_analyzer"] = (
                cross_ref_module.AdvancedCrossReferenceAnalyzer
            )
            print("✅ Cross-Reference Analyzer imported")

        # Import API sync validator
        api_sync_path = Path(__file__).parent / "api_code_sync_validator.py"
        if api_sync_path.exists():
            spec = importlib.util.spec_from_file_location(
                "api_code_sync_validator", api_sync_path
            )
            api_sync_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(api_sync_module)
            tools["api_sync_validator"] = api_sync_module.APICodeSyncValidator
            print("✅ API Sync Validator imported")

    except Exception as e:
        print(f"⚠️ Error importing validation tools: {e}")

    return tools


@dataclass
class ValidationResult:
    """Unified validation result structure."""

    validator_name: str
    passed: bool
    total_files: int = 0
    passed_files: int = 0
    failed_files: int = 0
    issues: list[dict[str, Any]] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    error_message: Optional[str] = None


@dataclass
class ValidationSummary:
    """Overall validation summary."""

    total_validators: int
    successful_validators: int
    failed_validators: int
    overall_passed: bool
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    total_files_checked: int
    total_execution_time: float
    constitutional_compliance_rate: float
    results: list[ValidationResult] = field(default_factory=list)


class UnifiedDocumentationValidationFramework:
    """Unified framework for all documentation validation."""

    def __init__(self):
        self.validation_tools = import_validation_tools()
        self.results: list[ValidationResult] = []
        self.summary: Optional[ValidationSummary] = None

    def run_enhanced_validation(self) -> ValidationResult:
        """Run enhanced validation checks."""
        print("🔍 Running enhanced documentation validation...")
        start_time = time.time()

        result = ValidationResult(validator_name="Enhanced Validation", passed=False)

        try:
            if "enhanced_validator" in self.validation_tools:
                validator = self.validation_tools["enhanced_validator"]()
                validation_result = validator.validate_all_files(max_workers=4)

                result.total_files = validation_result.total_files
                result.passed_files = validation_result.passed_files
                result.failed_files = validation_result.failed_files
                result.passed = validation_result.failed_files == 0
                result.issues = validation_result.issues
                result.metrics = {
                    "performance": (
                        f"{validation_result.total_files / validation_result.get_duration():.1f} files/second"
                    ),
                    "success_rate": (
                        f"{(validation_result.passed_files / validation_result.total_files * 100):.1f}%"
                    ),
                }

                print(
                    "  ✅ Enhanced validation:"
                    f" {result.passed_files}/{result.total_files} files passed"
                )
            else:
                result.error_message = "Enhanced validator not available"
                print("  ⚠️ Enhanced validator not available")

        except Exception as e:
            result.error_message = str(e)
            print(f"  ❌ Enhanced validation failed: {e}")

        result.execution_time = time.time() - start_time
        return result

    def run_consistency_validation(self) -> ValidationResult:
        """Run documentation consistency validation."""
        print("🔍 Running consistency validation...")
        start_time = time.time()

        result = ValidationResult(validator_name="Consistency Validation", passed=False)

        try:
            if "consistency_validator" in self.validation_tools:
                validator = self.validation_tools["consistency_validator"]()
                validation_results = validator.run_all_validations()

                passed_count = sum(1 for r in validation_results if r.passed)
                total_count = len(validation_results)

                result.total_files = total_count
                result.passed_files = passed_count
                result.failed_files = total_count - passed_count
                result.passed = passed_count == total_count

                # Convert validation results to issues
                for val_result in validation_results:
                    if not val_result.passed:
                        for issue in val_result.issues_found:
                            result.issues.append({
                                "severity": "HIGH",
                                "category": "consistency",
                                "message": issue,
                                "validator": val_result.check_name,
                            })

                result.metrics = {
                    "consistency_rate": f"{(passed_count / total_count * 100):.1f}%",
                    "checks_performed": total_count,
                }

                print(
                    f"  ✅ Consistency validation: {passed_count}/{total_count} checks"
                    " passed"
                )
            else:
                result.error_message = "Consistency validator not available"
                print("  ⚠️ Consistency validator not available")

        except Exception as e:
            result.error_message = str(e)
            print(f"  ❌ Consistency validation failed: {e}")

        result.execution_time = time.time() - start_time
        return result

    def run_cross_reference_validation(self) -> ValidationResult:
        """Run cross-reference validation."""
        print("🔍 Running cross-reference validation...")
        start_time = time.time()

        result = ValidationResult(
            validator_name="Cross-Reference Validation", passed=False
        )

        try:
            if "cross_ref_analyzer" in self.validation_tools:
                analyzer = self.validation_tools["cross_ref_analyzer"]()
                analysis_results = analyzer.run_comprehensive_analysis(max_workers=2)

                total_issues = analysis_results["summary"]["total_issues"]
                critical_issues = analysis_results["summary"]["critical_issues"]
                high_issues = analysis_results["summary"]["high_issues"]

                result.total_files = analysis_results["summary"]["total_documents"]
                result.passed = total_issues == 0
                result.issues = analysis_results["validation_issues"]
                result.metrics = {
                    "total_cross_references": analysis_results["summary"][
                        "total_cross_references"
                    ],
                    "semantic_relationships": analysis_results["summary"][
                        "semantic_relationships"
                    ],
                    "orphaned_documents": analysis_results["dependency_graph"][
                        "metrics"
                    ]["orphaned_documents"],
                    "connected_components": analysis_results["dependency_graph"][
                        "metrics"
                    ]["connected_components"],
                }

                print(f"  ✅ Cross-reference analysis: {total_issues} issues found")
            else:
                result.error_message = "Cross-reference analyzer not available"
                print("  ⚠️ Cross-reference analyzer not available")

        except Exception as e:
            result.error_message = str(e)
            print(f"  ❌ Cross-reference validation failed: {e}")

        result.execution_time = time.time() - start_time
        return result

    def run_api_sync_validation(self) -> ValidationResult:
        """Run API-code synchronization validation."""
        print("🔍 Running API-code synchronization validation...")
        start_time = time.time()

        result = ValidationResult(
            validator_name="API-Code Sync Validation", passed=False
        )

        try:
            if "api_sync_validator" in self.validation_tools:
                validator = self.validation_tools["api_sync_validator"]()
                sync_results = validator.analyze_all_services()

                total_issues = sync_results["total_issues"]
                critical_issues = sync_results["issues_by_severity"].get("CRITICAL", 0)
                high_issues = sync_results["issues_by_severity"].get("HIGH", 0)

                result.total_files = (
                    sync_results["services_analyzed"] + sync_results["docs_analyzed"]
                )
                result.passed = total_issues == 0
                result.issues = sync_results["sync_issues"]
                result.metrics = {
                    "services_analyzed": sync_results["services_analyzed"],
                    "docs_analyzed": sync_results["docs_analyzed"],
                    "endpoints_sync_rate": self._calculate_endpoint_sync_rate(
                        sync_results["service_summaries"]
                    ),
                }

                print(f"  ✅ API sync validation: {total_issues} issues found")
            else:
                result.error_message = "API sync validator not available"
                print("  ⚠️ API sync validator not available")

        except Exception as e:
            result.error_message = str(e)
            print(f"  ❌ API sync validation failed: {e}")

        result.execution_time = time.time() - start_time
        return result

    def _calculate_endpoint_sync_rate(self, service_summaries: dict[str, Any]) -> float:
        """Calculate overall endpoint synchronization rate."""
        total_impl = 0
        total_docs = 0

        for summary in service_summaries.values():
            total_impl += summary["endpoints_implemented"]
            total_docs += summary["endpoints_documented"]

        if total_impl == 0 and total_docs == 0:
            return 100.0

        total_max = max(total_impl, total_docs)
        total_min = min(total_impl, total_docs)

        return (total_min / total_max * 100) if total_max > 0 else 100.0

    def run_constitutional_compliance_check(self) -> ValidationResult:
        """Run constitutional compliance verification."""
        print("🔍 Running constitutional compliance check...")
        start_time = time.time()

        result = ValidationResult(
            validator_name="Constitutional Compliance", passed=False
        )

        try:
            # Find all markdown files
            md_files = list(DOCS_DIR.rglob("*.md"))
            total_files = len(md_files)
            compliant_files = 0
            non_compliant_files = []

            for md_file in md_files:
                try:
                    with open(md_file, encoding="utf-8") as f:
                        content = f.read()

                    if CONSTITUTIONAL_HASH in content:
                        compliant_files += 1
                    else:
                        non_compliant_files.append(str(md_file.relative_to(REPO_ROOT)))
                        result.issues.append({
                            "severity": "HIGH",
                            "category": "constitutional_compliance",
                            "message": (
                                "Missing constitutional hash:"
                                f" {md_file.relative_to(REPO_ROOT)}"
                            ),
                            "file": str(md_file.relative_to(REPO_ROOT)),
                        })
                except Exception as e:
                    result.issues.append({
                        "severity": "ERROR",
                        "category": "file_access",
                        "message": (
                            f"Could not read file {md_file.relative_to(REPO_ROOT)}: {e}"
                        ),
                        "file": str(md_file.relative_to(REPO_ROOT)),
                    })

            result.total_files = total_files
            result.passed_files = compliant_files
            result.failed_files = total_files - compliant_files
            result.passed = result.failed_files == 0
            result.metrics = {
                "compliance_rate": f"{(compliant_files / total_files * 100):.1f}%",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "non_compliant_files": len(non_compliant_files),
            }

            print(
                f"  ✅ Constitutional compliance: {compliant_files}/{total_files} files"
                " compliant"
            )

        except Exception as e:
            result.error_message = str(e)
            print(f"  ❌ Constitutional compliance check failed: {e}")

        result.execution_time = time.time() - start_time
        return result

    def run_comprehensive_validation(self) -> ValidationSummary:
        """Run all validation checks comprehensively."""
        print("🚀 ACGS Unified Documentation Validation Framework")
        print("=" * 70)
        print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print(f"Repository: {REPO_ROOT}")
        print(f"Available Validators: {len(self.validation_tools)}")
        print()

        start_time = time.time()

        # Run all validation checks
        validators = [
            self.run_enhanced_validation,
            self.run_consistency_validation,
            self.run_cross_reference_validation,
            self.run_api_sync_validation,
            self.run_constitutional_compliance_check,
        ]

        # Execute validators in parallel where possible
        with ThreadPoolExecutor(max_workers=3) as executor:
            future_to_validator = {
                executor.submit(validator): validator.__name__
                for validator in validators
            }

            for future in as_completed(future_to_validator):
                validator_name = future_to_validator[future]
                try:
                    result = future.result()
                    self.results.append(result)
                except Exception as e:
                    error_result = ValidationResult(
                        validator_name=validator_name,
                        passed=False,
                        error_message=str(e),
                    )
                    self.results.append(error_result)
                    print(f"  ❌ {validator_name} failed: {e}")

        total_execution_time = time.time() - start_time

        # Calculate summary
        successful_validators = len([
            r for r in self.results if r.error_message is None
        ])
        failed_validators = len([
            r for r in self.results if r.error_message is not None
        ])
        overall_passed = all(r.passed for r in self.results if r.error_message is None)

        # Count issues by severity
        all_issues = []
        for result in self.results:
            all_issues.extend(result.issues)

        severity_counts = defaultdict(int)
        for issue in all_issues:
            severity_counts[issue.get("severity", "UNKNOWN")] += 1

        # Calculate constitutional compliance rate
        const_result = next(
            (
                r
                for r in self.results
                if r.validator_name == "Constitutional Compliance"
            ),
            None,
        )
        const_compliance_rate = 0.0
        if const_result and const_result.total_files > 0:
            const_compliance_rate = (
                const_result.passed_files / const_result.total_files
            ) * 100

        # Calculate total files checked
        total_files = sum(r.total_files for r in self.results if r.total_files > 0)

        self.summary = ValidationSummary(
            total_validators=len(self.results),
            successful_validators=successful_validators,
            failed_validators=failed_validators,
            overall_passed=overall_passed,
            total_issues=len(all_issues),
            critical_issues=severity_counts["CRITICAL"],
            high_issues=severity_counts["HIGH"],
            medium_issues=severity_counts["MEDIUM"],
            low_issues=severity_counts["LOW"],
            total_files_checked=total_files,
            total_execution_time=total_execution_time,
            constitutional_compliance_rate=const_compliance_rate,
            results=self.results,
        )

        return self.summary

    def generate_comprehensive_report(self) -> str:
        """Generate comprehensive validation report."""
        if not self.summary:
            return "No validation summary available"

        summary = self.summary

        report = f"""# ACGS Unified Documentation Validation Report

<!-- Constitutional Hash: {CONSTITUTIONAL_HASH} -->

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Constitutional Hash**: `{CONSTITUTIONAL_HASH}`
**Validation Duration**: {summary.total_execution_time:.2f} seconds

## Executive Summary

| Metric | Value |
|--------|-------|
| Overall Status | {'✅ PASSED' if summary.overall_passed else '❌ FAILED'} |
| Validators Run | {summary.successful_validators}/{summary.total_validators} |
| Total Files Checked | {summary.total_files_checked} |
| Total Issues Found | {summary.total_issues} |
| Critical Issues | {summary.critical_issues} |
| High Priority Issues | {summary.high_issues} |
| Medium Priority Issues | {summary.medium_issues} |
| Low Priority Issues | {summary.low_issues} |
| Constitutional Compliance | {summary.constitutional_compliance_rate:.1f}% |

## Validation Results

"""

        # Individual validator results
        for result in summary.results:
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            if result.error_message:
                status = "⚠️ ERROR"

            report += f"### {result.validator_name}\n\n"
            report += f"**Status**: {status}\n"
            report += f"**Execution Time**: {result.execution_time:.2f} seconds\n"

            if result.error_message:
                report += f"**Error**: {result.error_message}\n"
            else:
                if result.total_files > 0:
                    report += f"**Files Processed**: {result.total_files}\n"
                    report += (
                        "**Success Rate**:"
                        f" {(result.passed_files / result.total_files * 100):.1f}%\n"
                    )

                if result.metrics:
                    report += "**Metrics**:\n"
                    for key, value in result.metrics.items():
                        report += f"- {key.replace('_', ' ').title()}: {value}\n"

                if result.issues:
                    report += f"**Issues Found**: {len(result.issues)}\n"

            report += "\n"

        # Issues by category
        if summary.total_issues > 0:
            report += "## Issues by Category\n\n"

            category_counts = defaultdict(int)
            for result in summary.results:
                for issue in result.issues:
                    category_counts[issue.get("category", "unknown")] += 1

            for category, count in sorted(category_counts.items()):
                report += (
                    f"- **{category.replace('_', ' ').title()}**: {count} issues\n"
                )

            # Top issues by severity
            report += "\n## Critical and High Priority Issues\n\n"

            critical_high_issues = []
            for result in summary.results:
                for issue in result.issues:
                    if issue.get("severity") in ["CRITICAL", "HIGH"]:
                        critical_high_issues.append((result.validator_name, issue))

            for validator_name, issue in critical_high_issues[:20]:  # Show top 20
                report += (
                    f"**{validator_name}** -"
                    f" {issue.get('category', 'unknown').replace('_', ' ')}\n"
                )
                report += f"- {issue.get('message', 'No message')}\n"
                if "file" in issue:
                    report += f"- 📄 File: {issue['file']}\n"
                report += "\n"

        # Recommendations
        report += "## Recommendations\n\n"

        if summary.critical_issues > 0:
            report += (
                f"🚨 **CRITICAL**: Address {summary.critical_issues} critical issues"
                " immediately before deployment.\n\n"
            )

        if summary.high_issues > 0:
            report += (
                f"⚠️ **HIGH**: Resolve {summary.high_issues} high-priority issues.\n\n"
            )

        if summary.constitutional_compliance_rate < 100:
            missing_files = int(
                (100 - summary.constitutional_compliance_rate)
                / 100
                * summary.total_files_checked
            )
            report += (
                "📋 **CONSTITUTIONAL**: Add constitutional hash to"
                f" ~{missing_files} files.\n\n"
            )

        if summary.failed_validators > 0:
            report += (
                f"🔧 **TOOLS**: Fix {summary.failed_validators} failed validators.\n\n"
            )

        if summary.total_issues == 0 and summary.overall_passed:
            report += (
                "✅ **EXCELLENT**: All documentation validation checks passed"
                " successfully.\n\n"
            )

        # Performance metrics
        report += "## Performance Metrics\n\n"

        fastest_validator = min(
            summary.results, key=lambda x: x.execution_time, default=None
        )
        slowest_validator = max(
            summary.results, key=lambda x: x.execution_time, default=None
        )

        if fastest_validator and slowest_validator:
            report += (
                "- **Fastest Validator**:"
                f" {fastest_validator.validator_name} ({fastest_validator.execution_time:.2f}s)\n"
            )
            report += (
                "- **Slowest Validator**:"
                f" {slowest_validator.validator_name} ({slowest_validator.execution_time:.2f}s)\n"
            )

        report += (
            f"- **Total Execution Time**: {summary.total_execution_time:.2f} seconds\n"
        )
        report += (
            "- **Average Validator Time**:"
            f" {(summary.total_execution_time / summary.total_validators):.2f} seconds\n"
        )

        if summary.total_files_checked > 0:
            report += (
                "- **Files per Second**:"
                f" {(summary.total_files_checked / summary.total_execution_time):.1f}\n"
            )

        report += f"""

---

**Unified Documentation Validation**: Generated by ACGS Unified Documentation Validation Framework
**Constitutional Hash**: `{CONSTITUTIONAL_HASH}` ✅
**Framework Version**: 1.0.0
**Validation Coverage**: {summary.successful_validators}/{summary.total_validators} validators
"""

        return report

    def save_results(self, output_path: Optional[Path] = None) -> Path:
        """Save validation results to file."""
        if not output_path:
            output_path = (
                REPO_ROOT
                / "validation_reports"
                / f"unified_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        report = self.generate_comprehensive_report()
        with open(output_path, "w") as f:
            f.write(report)

        return output_path

    def save_json_results(self, output_path: Optional[Path] = None) -> Path:
        """Save validation results as JSON."""
        if not output_path:
            output_path = (
                REPO_ROOT
                / "validation_reports"
                / f"unified_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert results to JSON-serializable format
        json_data = {
            "timestamp": datetime.now().isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "summary": {
                "total_validators": self.summary.total_validators,
                "successful_validators": self.summary.successful_validators,
                "failed_validators": self.summary.failed_validators,
                "overall_passed": self.summary.overall_passed,
                "total_issues": self.summary.total_issues,
                "critical_issues": self.summary.critical_issues,
                "high_issues": self.summary.high_issues,
                "medium_issues": self.summary.medium_issues,
                "low_issues": self.summary.low_issues,
                "total_files_checked": self.summary.total_files_checked,
                "total_execution_time": self.summary.total_execution_time,
                "constitutional_compliance_rate": (
                    self.summary.constitutional_compliance_rate
                ),
            },
            "results": [
                {
                    "validator_name": result.validator_name,
                    "passed": result.passed,
                    "total_files": result.total_files,
                    "passed_files": result.passed_files,
                    "failed_files": result.failed_files,
                    "issues": result.issues,
                    "metrics": result.metrics,
                    "execution_time": result.execution_time,
                    "error_message": result.error_message,
                }
                for result in self.summary.results
            ],
        }

        with open(output_path, "w") as f:
            json.dump(json_data, f, indent=2)

        return output_path


def main():
    """Main execution function."""
    import argparse

    parser = argparse.ArgumentParser(
        description="ACGS Unified Documentation Validation Framework"
    )
    parser.add_argument("--output", type=Path, help="Output file for validation report")
    parser.add_argument(
        "--json", action="store_true", help="Also save results in JSON format"
    )
    parser.add_argument(
        "--json-only", action="store_true", help="Save only JSON results"
    )

    args = parser.parse_args()

    # Run comprehensive validation
    framework = UnifiedDocumentationValidationFramework()
    summary = framework.run_comprehensive_validation()

    # Print summary
    print("\n" + "=" * 70)
    print("📊 VALIDATION SUMMARY")
    print("=" * 70)

    print(
        "🔍 Validators:"
        f" {summary.successful_validators}/{summary.total_validators} successful"
    )
    print(f"📄 Files Checked: {summary.total_files_checked}")
    print(f"⚠️ Total Issues: {summary.total_issues}")
    print(
        f"🚨 Critical: {summary.critical_issues}, High: {summary.high_issues}, Medium:"
        f" {summary.medium_issues}, Low: {summary.low_issues}"
    )
    print(
        f"📋 Constitutional Compliance: {summary.constitutional_compliance_rate:.1f}%"
    )
    print(f"⏱️ Total Time: {summary.total_execution_time:.2f} seconds")
    print(f"✅ Overall Status: {'PASSED' if summary.overall_passed else 'FAILED'}")

    # Save results
    if not args.json_only:
        report_path = framework.save_results(args.output)
        print(f"\n📄 Validation report saved to: {report_path}")

    if args.json or args.json_only:
        json_path = framework.save_json_results()
        print(f"📊 JSON results saved to: {json_path}")

    print(f"\n🔗 Constitutional Hash: {CONSTITUTIONAL_HASH}")

    # Exit with appropriate code
    if summary.critical_issues > 0:
        print(
            f"\n🚨 {summary.critical_issues} CRITICAL issues require immediate"
            " attention!"
        )
        return 2
    elif summary.high_issues > 0:
        print(f"\n⚠️ {summary.high_issues} HIGH priority issues should be addressed")
        return 1
    elif not summary.overall_passed:
        print("\n❌ Some validators failed to complete")
        return 1
    else:
        print("\n🎉 All documentation validation checks passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
