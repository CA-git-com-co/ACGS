#!/usr/bin/env python3
"""
ACGS-1 End-to-End Test Suite Audit

This script performs a comprehensive audit of the end-to-end test suite,
analyzing code quality, coverage, architecture, and compliance with
ACGS-1 testing standards.

Features:
- Code quality analysis
- Test coverage assessment
- Architecture validation
- Performance analysis
- Security compliance check
- Documentation completeness

Usage:
    python tests/e2e/audit_test_suite.py

Formal Verification Comments:
# requires: Test suite files available, Python environment configured
# ensures: Comprehensive audit completed, recommendations provided
# sha256: test_suite_audit_v3.0
"""

import ast
import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TestSuiteAuditor:
    """
    Comprehensive auditor for ACGS-1 end-to-end test suite.

    This auditor analyzes the test suite for:
    - Code quality and best practices
    - Test coverage and completeness
    - Architecture and design patterns
    - Performance considerations
    - Security compliance
    - Documentation quality
    """

    def __init__(self):
        self.audit_start_time = time.time()
        self.test_suite_path = Path("tests/e2e")
        self.audit_results = {
            "audit_metadata": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "auditor_version": "3.0",
                "audit_scope": "ACGS-1 End-to-End Test Suite",
            },
            "code_quality": {},
            "test_coverage": {},
            "architecture": {},
            "performance": {},
            "security": {},
            "documentation": {},
            "recommendations": [],
            "summary": {},
        }

    def run_comprehensive_audit(self) -> Dict[str, Any]:
        """
        Execute comprehensive audit of the test suite.

        # requires: Test suite files accessible
        # ensures: Complete audit analysis performed
        # sha256: comprehensive_audit_v3.0
        """
        logger.info("🔍 Starting ACGS-1 Test Suite Comprehensive Audit")
        logger.info("=" * 60)

        try:
            # Phase 1: Code Quality Analysis
            logger.info("📊 Phase 1: Code Quality Analysis")
            self._analyze_code_quality()

            # Phase 2: Test Coverage Assessment
            logger.info("\n📈 Phase 2: Test Coverage Assessment")
            self._analyze_test_coverage()

            # Phase 3: Architecture Validation
            logger.info("\n🏗️ Phase 3: Architecture Validation")
            self._analyze_architecture()

            # Phase 4: Performance Analysis
            logger.info("\n⚡ Phase 4: Performance Analysis")
            self._analyze_performance()

            # Phase 5: Security Compliance
            logger.info("\n🔒 Phase 5: Security Compliance")
            self._analyze_security()

            # Phase 6: Documentation Quality
            logger.info("\n📚 Phase 6: Documentation Quality")
            self._analyze_documentation()

            # Phase 7: Generate Recommendations
            logger.info("\n💡 Phase 7: Generate Recommendations")
            self._generate_recommendations()

            # Phase 8: Create Summary
            self._create_audit_summary()

            # Save audit report
            self._save_audit_report()

            logger.info("\n✅ Comprehensive audit completed successfully!")
            return self.audit_results

        except Exception as e:
            logger.error(f"❌ Audit failed: {str(e)}")
            return {"error": str(e)}

    def _analyze_code_quality(self):
        """Analyze code quality metrics."""
        try:
            python_files = list(self.test_suite_path.glob("**/*.py"))

            code_metrics = {
                "total_files": len(python_files),
                "total_lines": 0,
                "total_functions": 0,
                "total_classes": 0,
                "complexity_scores": [],
                "docstring_coverage": 0,
                "type_hint_coverage": 0,
                "file_analysis": [],
            }

            for file_path in python_files:
                if file_path.name.startswith("."):
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    # Parse AST
                    tree = ast.parse(content)

                    # Count lines
                    lines = len(content.splitlines())
                    code_metrics["total_lines"] += lines

                    # Analyze AST
                    file_analysis = self._analyze_file_ast(tree, file_path.name)
                    code_metrics["total_functions"] += file_analysis["functions"]
                    code_metrics["total_classes"] += file_analysis["classes"]
                    code_metrics["file_analysis"].append(
                        {"file": file_path.name, "lines": lines, **file_analysis}
                    )

                except Exception as e:
                    logger.warning(f"⚠️ Could not analyze {file_path.name}: {str(e)}")

            # Calculate averages
            if code_metrics["total_files"] > 0:
                code_metrics["avg_lines_per_file"] = (
                    code_metrics["total_lines"] / code_metrics["total_files"]
                )
                code_metrics["avg_functions_per_file"] = (
                    code_metrics["total_functions"] / code_metrics["total_files"]
                )

            self.audit_results["code_quality"] = code_metrics

            logger.info(f"  ✅ Analyzed {code_metrics['total_files']} Python files")
            logger.info(f"  📏 Total lines of code: {code_metrics['total_lines']}")
            logger.info(f"  🔧 Total functions: {code_metrics['total_functions']}")
            logger.info(f"  🏗️ Total classes: {code_metrics['total_classes']}")

        except Exception as e:
            logger.error(f"❌ Code quality analysis failed: {str(e)}")

    def _analyze_file_ast(self, tree: ast.AST, filename: str) -> Dict[str, Any]:
        """Analyze AST of a single file."""
        analysis = {
            "functions": 0,
            "classes": 0,
            "async_functions": 0,
            "docstrings": 0,
            "type_hints": 0,
            "complexity_estimate": 0,
            "formal_verification_comments": 0,
            "test_methods": 0,
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                analysis["functions"] += 1
                if node.name.startswith("test_"):
                    analysis["test_methods"] += 1
                if ast.get_docstring(node):
                    analysis["docstrings"] += 1
                if node.returns:
                    analysis["type_hints"] += 1

            elif isinstance(node, ast.AsyncFunctionDef):
                analysis["async_functions"] += 1
                if ast.get_docstring(node):
                    analysis["docstrings"] += 1

            elif isinstance(node, ast.ClassDef):
                analysis["classes"] += 1
                if ast.get_docstring(node):
                    analysis["docstrings"] += 1

            elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                analysis["complexity_estimate"] += 1

        # Check for formal verification comments
        try:
            with open(self.test_suite_path / filename, "r") as f:
                content = f.read()
                analysis["formal_verification_comments"] = len(
                    re.findall(r"#\s*(requires|ensures|sha256):", content)
                )
        except:
            pass

        return analysis

    def _analyze_test_coverage(self):
        """Analyze test coverage and completeness."""
        try:
            coverage_analysis = {
                "test_scenarios": [],
                "service_coverage": {},
                "workflow_coverage": {},
                "assertion_patterns": [],
                "mock_usage": 0,
                "integration_tests": 0,
                "unit_tests": 0,
            }

            # Define expected test scenarios
            expected_scenarios = [
                "authentication_workflow",
                "policy_creation",
                "constitutional_compliance",
                "blockchain_integration",
                "service_integration",
                "performance_validation",
                "security_validation",
                "emergency_governance",
                "appeals_resolution",
            ]

            # Analyze test files
            test_files = list(self.test_suite_path.glob("**/test_*.py"))

            for test_file in test_files:
                try:
                    with open(test_file, "r") as f:
                        content = f.read()

                    # Check for test scenarios
                    for scenario in expected_scenarios:
                        if scenario in content.lower():
                            if scenario not in coverage_analysis["test_scenarios"]:
                                coverage_analysis["test_scenarios"].append(scenario)

                    # Count assertion patterns
                    assertions = re.findall(r"assert\s+", content)
                    coverage_analysis["assertion_patterns"].extend(assertions)

                    # Check for mock usage
                    if "mock" in content.lower() or "patch" in content.lower():
                        coverage_analysis["mock_usage"] += 1

                    # Classify test types
                    if (
                        "integration" in test_file.name.lower()
                        or "e2e" in test_file.name.lower()
                    ):
                        coverage_analysis["integration_tests"] += 1
                    else:
                        coverage_analysis["unit_tests"] += 1

                except Exception as e:
                    logger.warning(
                        f"⚠️ Could not analyze test file {test_file.name}: {str(e)}"
                    )

            # Calculate coverage percentages
            scenario_coverage = len(coverage_analysis["test_scenarios"]) / len(
                expected_scenarios
            )
            coverage_analysis["scenario_coverage_percent"] = scenario_coverage * 100

            self.audit_results["test_coverage"] = coverage_analysis

            logger.info(f"  ✅ Test scenario coverage: {scenario_coverage:.1%}")
            logger.info(
                f"  🧪 Integration tests: {coverage_analysis['integration_tests']}"
            )
            logger.info(f"  🔬 Unit tests: {coverage_analysis['unit_tests']}")
            logger.info(f"  🎭 Mock usage: {coverage_analysis['mock_usage']} files")

        except Exception as e:
            logger.error(f"❌ Test coverage analysis failed: {str(e)}")

    def _analyze_architecture(self):
        """Analyze test suite architecture and design patterns."""
        try:
            architecture_analysis = {
                "design_patterns": [],
                "modularity_score": 0,
                "dependency_analysis": {},
                "file_organization": {},
                "inheritance_hierarchy": [],
                "async_usage": 0,
            }

            # Analyze file organization
            directories = [d for d in self.test_suite_path.iterdir() if d.is_dir()]
            files = [
                f
                for f in self.test_suite_path.iterdir()
                if f.is_file() and f.suffix == ".py"
            ]

            architecture_analysis["file_organization"] = {
                "total_directories": len(directories),
                "total_files": len(files),
                "directory_structure": [d.name for d in directories],
                "main_files": [f.name for f in files],
            }

            # Check for design patterns
            pattern_indicators = {
                "Factory Pattern": ["factory", "create_"],
                "Builder Pattern": ["builder", "build_"],
                "Observer Pattern": ["observer", "notify", "subscribe"],
                "Strategy Pattern": ["strategy", "algorithm"],
                "Template Method": ["template", "abstract"],
                "Singleton Pattern": ["singleton", "_instance"],
            }

            for file_path in self.test_suite_path.glob("**/*.py"):
                try:
                    with open(file_path, "r") as f:
                        content = f.read().lower()

                    for pattern, indicators in pattern_indicators.items():
                        if any(indicator in content for indicator in indicators):
                            if pattern not in architecture_analysis["design_patterns"]:
                                architecture_analysis["design_patterns"].append(pattern)

                    # Count async usage
                    if "async def" in content:
                        architecture_analysis["async_usage"] += 1

                except Exception as e:
                    continue

            # Calculate modularity score based on file organization
            modularity_factors = [
                len(directories) > 0,  # Has subdirectories
                len(files) < 10,  # Not too many files in root
                "modules" in [d.name for d in directories],  # Has modules directory
                "fixtures" in [d.name for d in directories]
                or "utils" in [d.name for d in directories],  # Has support directories
            ]

            architecture_analysis["modularity_score"] = sum(modularity_factors) / len(
                modularity_factors
            )

            self.audit_results["architecture"] = architecture_analysis

            logger.info(
                f"  ✅ Modularity score: {architecture_analysis['modularity_score']:.1%}"
            )
            logger.info(
                f"  🏗️ Design patterns found: {len(architecture_analysis['design_patterns'])}"
            )
            logger.info(
                f"  ⚡ Async usage: {architecture_analysis['async_usage']} files"
            )

        except Exception as e:
            logger.error(f"❌ Architecture analysis failed: {str(e)}")

    def _analyze_performance(self):
        """Analyze performance considerations in tests."""
        try:
            performance_analysis = {
                "timeout_configurations": [],
                "performance_assertions": 0,
                "load_testing_indicators": 0,
                "resource_monitoring": 0,
                "optimization_patterns": [],
            }

            performance_keywords = [
                "timeout",
                "response_time",
                "performance",
                "benchmark",
                "load",
                "stress",
                "concurrent",
                "parallel",
                "async",
                "memory",
                "cpu",
                "resource",
            ]

            for file_path in self.test_suite_path.glob("**/*.py"):
                try:
                    with open(file_path, "r") as f:
                        content = f.read()

                    # Check for performance-related code
                    for keyword in performance_keywords:
                        if keyword in content.lower():
                            if (
                                keyword
                                not in performance_analysis["optimization_patterns"]
                            ):
                                performance_analysis["optimization_patterns"].append(
                                    keyword
                                )

                    # Count timeout configurations
                    timeouts = re.findall(r"timeout[=\s]*(\d+)", content, re.IGNORECASE)
                    performance_analysis["timeout_configurations"].extend(timeouts)

                    # Count performance assertions
                    perf_assertions = re.findall(
                        r"assert.*(?:time|performance|speed|latency)",
                        content,
                        re.IGNORECASE,
                    )
                    performance_analysis["performance_assertions"] += len(
                        perf_assertions
                    )

                except Exception as e:
                    continue

            self.audit_results["performance"] = performance_analysis

            logger.info(
                f"  ✅ Performance patterns: {len(performance_analysis['optimization_patterns'])}"
            )
            logger.info(
                f"  ⏱️ Timeout configurations: {len(performance_analysis['timeout_configurations'])}"
            )
            logger.info(
                f"  📊 Performance assertions: {performance_analysis['performance_assertions']}"
            )

        except Exception as e:
            logger.error(f"❌ Performance analysis failed: {str(e)}")

    def _analyze_security(self):
        """Analyze security considerations in tests."""
        try:
            security_analysis = {
                "authentication_tests": 0,
                "authorization_tests": 0,
                "input_validation_tests": 0,
                "crypto_usage": 0,
                "security_assertions": 0,
                "vulnerability_patterns": [],
            }

            security_keywords = [
                "auth",
                "token",
                "jwt",
                "password",
                "crypto",
                "encrypt",
                "security",
                "vulnerability",
                "injection",
                "xss",
                "csrf",
            ]

            for file_path in self.test_suite_path.glob("**/*.py"):
                try:
                    with open(file_path, "r") as f:
                        content = f.read().lower()

                    # Count security-related tests
                    if "auth" in content:
                        security_analysis["authentication_tests"] += 1
                    if "authorization" in content or "permission" in content:
                        security_analysis["authorization_tests"] += 1
                    if "validation" in content and "input" in content:
                        security_analysis["input_validation_tests"] += 1
                    if "crypto" in content or "encrypt" in content:
                        security_analysis["crypto_usage"] += 1

                    # Count security assertions
                    security_assertions = re.findall(
                        r"assert.*(?:secure|auth|token|permission)", content
                    )
                    security_analysis["security_assertions"] += len(security_assertions)

                except Exception as e:
                    continue

            self.audit_results["security"] = security_analysis

            logger.info(
                f"  ✅ Authentication tests: {security_analysis['authentication_tests']}"
            )
            logger.info(
                f"  🔐 Authorization tests: {security_analysis['authorization_tests']}"
            )
            logger.info(
                f"  🛡️ Security assertions: {security_analysis['security_assertions']}"
            )

        except Exception as e:
            logger.error(f"❌ Security analysis failed: {str(e)}")

    def _analyze_documentation(self):
        """Analyze documentation quality."""
        try:
            doc_analysis = {
                "readme_files": 0,
                "docstring_coverage": 0,
                "comment_density": 0,
                "formal_verification_comments": 0,
                "usage_examples": 0,
                "documentation_files": [],
            }

            # Find documentation files
            doc_files = list(self.test_suite_path.glob("**/*.md")) + list(
                self.test_suite_path.glob("**/*.rst")
            )
            doc_analysis["documentation_files"] = [f.name for f in doc_files]
            doc_analysis["readme_files"] = len(
                [f for f in doc_files if "readme" in f.name.lower()]
            )

            # Analyze Python files for documentation
            total_functions = 0
            documented_functions = 0
            total_lines = 0
            comment_lines = 0

            for file_path in self.test_suite_path.glob("**/*.py"):
                try:
                    with open(file_path, "r") as f:
                        content = f.read()
                        lines = content.splitlines()

                    total_lines += len(lines)
                    comment_lines += len(
                        [line for line in lines if line.strip().startswith("#")]
                    )

                    # Parse AST for docstrings
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            total_functions += 1
                            if ast.get_docstring(node):
                                documented_functions += 1

                    # Count formal verification comments
                    fv_comments = len(
                        re.findall(r"#\s*(requires|ensures|sha256):", content)
                    )
                    doc_analysis["formal_verification_comments"] += fv_comments

                    # Count usage examples
                    examples = len(
                        re.findall(r"(?:example|usage|demo)", content, re.IGNORECASE)
                    )
                    doc_analysis["usage_examples"] += examples

                except Exception as e:
                    continue

            # Calculate percentages
            if total_functions > 0:
                doc_analysis["docstring_coverage"] = (
                    documented_functions / total_functions
                )
            if total_lines > 0:
                doc_analysis["comment_density"] = comment_lines / total_lines

            self.audit_results["documentation"] = doc_analysis

            logger.info(f"  ✅ README files: {doc_analysis['readme_files']}")
            logger.info(
                f"  📝 Docstring coverage: {doc_analysis['docstring_coverage']:.1%}"
            )
            logger.info(f"  💬 Comment density: {doc_analysis['comment_density']:.1%}")
            logger.info(
                f"  🔍 Formal verification comments: {doc_analysis['formal_verification_comments']}"
            )

        except Exception as e:
            logger.error(f"❌ Documentation analysis failed: {str(e)}")

    def _generate_recommendations(self):
        """Generate recommendations based on audit findings."""
        recommendations = []

        # Code quality recommendations
        code_quality = self.audit_results.get("code_quality", {})
        if code_quality.get("total_functions", 0) > 0:
            avg_lines = code_quality.get("avg_lines_per_file", 0)
            if avg_lines > 500:
                recommendations.append(
                    {
                        "category": "Code Quality",
                        "priority": "Medium",
                        "issue": "Large file sizes detected",
                        "recommendation": f"Consider breaking down files with >500 lines (avg: {avg_lines:.0f})",
                        "impact": "Maintainability",
                    }
                )

        # Test coverage recommendations
        test_coverage = self.audit_results.get("test_coverage", {})
        scenario_coverage = test_coverage.get("scenario_coverage_percent", 0)
        if scenario_coverage < 80:
            recommendations.append(
                {
                    "category": "Test Coverage",
                    "priority": "High",
                    "issue": "Low test scenario coverage",
                    "recommendation": f"Increase test scenario coverage from {scenario_coverage:.1f}% to >80%",
                    "impact": "Quality Assurance",
                }
            )

        # Architecture recommendations
        architecture = self.audit_results.get("architecture", {})
        modularity_score = architecture.get("modularity_score", 0)
        if modularity_score < 0.7:
            recommendations.append(
                {
                    "category": "Architecture",
                    "priority": "Medium",
                    "issue": "Low modularity score",
                    "recommendation": f"Improve code organization (current: {modularity_score:.1%})",
                    "impact": "Maintainability",
                }
            )

        # Performance recommendations
        performance = self.audit_results.get("performance", {})
        if performance.get("performance_assertions", 0) < 5:
            recommendations.append(
                {
                    "category": "Performance",
                    "priority": "Medium",
                    "issue": "Few performance assertions",
                    "recommendation": "Add more performance validation assertions",
                    "impact": "Performance Monitoring",
                }
            )

        # Security recommendations
        security = self.audit_results.get("security", {})
        if security.get("authentication_tests", 0) < 3:
            recommendations.append(
                {
                    "category": "Security",
                    "priority": "High",
                    "issue": "Insufficient authentication tests",
                    "recommendation": "Add comprehensive authentication test coverage",
                    "impact": "Security Assurance",
                }
            )

        # Documentation recommendations
        documentation = self.audit_results.get("documentation", {})
        docstring_coverage = documentation.get("docstring_coverage", 0)
        if docstring_coverage < 0.8:
            recommendations.append(
                {
                    "category": "Documentation",
                    "priority": "Medium",
                    "issue": "Low docstring coverage",
                    "recommendation": f"Increase docstring coverage from {docstring_coverage:.1%} to >80%",
                    "impact": "Code Documentation",
                }
            )

        self.audit_results["recommendations"] = recommendations

        logger.info(f"  ✅ Generated {len(recommendations)} recommendations")
        for rec in recommendations[:3]:  # Show top 3
            logger.info(f"    • {rec['category']}: {rec['issue']}")

    def _create_audit_summary(self):
        """Create comprehensive audit summary."""
        audit_duration = time.time() - self.audit_start_time

        # Calculate overall scores
        code_quality_score = min(
            1.0,
            self.audit_results.get("code_quality", {}).get("total_functions", 0) / 50,
        )
        test_coverage_score = (
            self.audit_results.get("test_coverage", {}).get(
                "scenario_coverage_percent", 0
            )
            / 100
        )
        architecture_score = self.audit_results.get("architecture", {}).get(
            "modularity_score", 0
        )
        documentation_score = self.audit_results.get("documentation", {}).get(
            "docstring_coverage", 0
        )

        overall_score = (
            code_quality_score
            + test_coverage_score
            + architecture_score
            + documentation_score
        ) / 4

        summary = {
            "audit_duration_seconds": audit_duration,
            "overall_score": overall_score,
            "grade": self._calculate_grade(overall_score),
            "scores": {
                "code_quality": code_quality_score,
                "test_coverage": test_coverage_score,
                "architecture": architecture_score,
                "documentation": documentation_score,
            },
            "total_recommendations": len(self.audit_results.get("recommendations", [])),
            "high_priority_issues": len(
                [
                    r
                    for r in self.audit_results.get("recommendations", [])
                    if r.get("priority") == "High"
                ]
            ),
            "audit_status": "completed",
        }

        self.audit_results["summary"] = summary

        logger.info(f"\n📊 AUDIT SUMMARY:")
        logger.info(f"  Overall Score: {overall_score:.1%} (Grade: {summary['grade']})")
        logger.info(f"  Duration: {audit_duration:.2f}s")
        logger.info(
            f"  Recommendations: {summary['total_recommendations']} ({summary['high_priority_issues']} high priority)"
        )

    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade from score."""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"

    def _save_audit_report(self):
        """Save comprehensive audit report."""
        try:
            # Create results directory
            results_dir = Path("tests/results")
            results_dir.mkdir(exist_ok=True)

            # Save JSON report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = results_dir / f"test_suite_audit_report_{timestamp}.json"

            with open(report_file, "w") as f:
                json.dump(self.audit_results, f, indent=2, default=str)

            logger.info(f"📋 Audit report saved: {report_file}")

        except Exception as e:
            logger.error(f"❌ Could not save audit report: {str(e)}")


def main():
    """Main function for running test suite audit."""
    auditor = TestSuiteAuditor()
    results = auditor.run_comprehensive_audit()

    if "error" in results:
        print(f"\n❌ Audit failed: {results['error']}")
        exit(1)
    else:
        summary = results.get("summary", {})
        grade = summary.get("grade", "F")
        score = summary.get("overall_score", 0)

        print(f"\n🎯 Test Suite Audit Complete!")
        print(f"📊 Overall Score: {score:.1%} (Grade: {grade})")

        if grade in ["A", "B"]:
            print("🎉 Excellent test suite quality!")
            exit(0)
        elif grade == "C":
            print("✅ Good test suite with room for improvement")
            exit(0)
        else:
            print("⚠️ Test suite needs significant improvements")
            exit(1)


if __name__ == "__main__":
    main()
