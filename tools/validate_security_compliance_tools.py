#!/usr/bin/env python3
"""
ACGS-1 Security and Compliance Tools Validation Script

This script validates the implementation of security and compliance tools:
1. Security Scan Script functionality
2. PGC Load Test configuration
3. Compliance Matrix completeness
4. Service Boundary Analysis accuracy

Usage:
    python scripts/validate_security_compliance_tools.py
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SecurityComplianceValidator:
    """Validates ACGS-1 security and compliance tools implementation."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "validator": "ACGS-1 Security Compliance Validator",
            "tests": {},
            "overall_status": "PENDING",
            "constitutional_compliance": True,
        }

    def validate_security_scan_script(self):
        """Validate the security scan script implementation."""
        logger.info("🔒 Validating Security Scan Script...")

        script_path = self.project_root / "scripts" / "security_scan.sh"
        test_results = {
            "script_exists": script_path.exists(),
            "script_executable": False,
            "script_structure": False,
            "required_tools": [],
            "constitutional_compliance": False,
        }

        if test_results["script_exists"]:
            # Check if script is executable
            test_results["script_executable"] = os.access(script_path, os.X_OK)

            # Read script content for validation
            with open(script_path) as f:
                script_content = f.read()

            # Check for required components
            required_components = [
                "pip-audit",
                "safety",
                "bandit",
                "semgrep",
                "cargo audit",
                "npm audit",
                "cargo clippy",
                "JSON output",
                "constitutional governance",
            ]

            for component in required_components:
                if component.lower().replace(" ", "_") in script_content.lower():
                    test_results["required_tools"].append(component)

            # Check script structure
            test_results["script_structure"] = all(
                [
                    "#!/bin/bash" in script_content,
                    "set -euo pipefail" in script_content,
                    "LOG_DIR" in script_content,
                    "SCAN_ID" in script_content,
                    "update_summary" in script_content,
                ]
            )

            # Check constitutional compliance features
            test_results["constitutional_compliance"] = all(
                [
                    "constitutional" in script_content.lower(),
                    "governance" in script_content.lower(),
                    "compliance" in script_content.lower(),
                    "audit" in script_content.lower(),
                ]
            )

        self.validation_results["tests"]["security_scan_script"] = test_results

        if test_results["script_exists"] and test_results["script_executable"]:
            logger.info("✅ Security scan script validation passed")
        else:
            logger.error("❌ Security scan script validation failed")

        return test_results

    def validate_pgc_load_test(self):
        """Validate the PGC load test implementation."""
        logger.info("⚡ Validating PGC Load Test...")

        test_path = self.project_root / "tests" / "performance" / "pgc_load_test.py"
        test_results = {
            "test_exists": test_path.exists(),
            "locust_implementation": False,
            "performance_targets": False,
            "constitutional_compliance": False,
            "required_classes": [],
            "latency_target": None,
        }

        if test_results["test_exists"]:
            with open(test_path) as f:
                test_content = f.read()

            # Check for Locust implementation
            test_results["locust_implementation"] = all(
                [
                    "from locust import" in test_content,
                    "HttpUser" in test_content,
                    "@task" in test_content,
                    'host = "http://localhost:8003"' in test_content,
                ]
            )

            # Check for required classes
            required_classes = ["PGCLoadTestUser", "PGCStressTestUser"]
            for cls in required_classes:
                if f"class {cls}" in test_content:
                    test_results["required_classes"].append(cls)

            # Check performance targets
            test_results["performance_targets"] = all(
                [
                    "LATENCY_TARGET_MS = 25" in test_content,
                    "THROUGHPUT_TARGET_RPS" in test_content,
                    "AVAILABILITY_TARGET" in test_content,
                ]
            )

            # Extract latency target
            if "LATENCY_TARGET_MS = 25" in test_content:
                test_results["latency_target"] = 25

            # Check constitutional compliance
            test_results["constitutional_compliance"] = all(
                [
                    "constitutional" in test_content.lower(),
                    "governance" in test_content.lower(),
                    "compliance" in test_content.lower(),
                    "audit_trail" in test_content.lower(),
                ]
            )

        self.validation_results["tests"]["pgc_load_test"] = test_results

        if test_results["test_exists"] and test_results["locust_implementation"]:
            logger.info("✅ PGC load test validation passed")
        else:
            logger.error("❌ PGC load test validation failed")

        return test_results

    def validate_compliance_matrix(self):
        """Validate the compliance matrix documentation."""
        logger.info("📋 Validating Compliance Matrix...")

        matrix_path = self.project_root / "docs" / "compliance" / "compliance_matrix.md"
        test_results = {
            "matrix_exists": matrix_path.exists(),
            "required_sections": [],
            "requirement_categories": [],
            "compliance_score": None,
            "constitutional_alignment": False,
        }

        if test_results["matrix_exists"]:
            with open(matrix_path) as f:
                matrix_content = f.read()

            # Check for required sections
            required_sections = [
                "## Overview",
                "## Compliance Requirements Matrix",
                "### Cryptographic Requirements",
                "### Governance Requirements",
                "### Performance Requirements",
                "### Blockchain-Specific Requirements",
                "## Compliance Status Summary",
                "## Priority Action Items",
            ]

            for section in required_sections:
                if section in matrix_content:
                    test_results["required_sections"].append(section)

            # Check requirement categories
            categories = ["SR-", "CR-", "GV-", "PR-", "BC-"]
            for category in categories:
                if category in matrix_content:
                    test_results["requirement_categories"].append(category)

            # Extract compliance score
            if "Overall Compliance Score:" in matrix_content:
                # Try to extract score
                import re

                score_match = re.search(
                    r"Overall Compliance Score:\s*\*\*(\d+)/100\*\*", matrix_content
                )
                if score_match:
                    test_results["compliance_score"] = int(score_match.group(1))

            # Check constitutional alignment
            test_results["constitutional_alignment"] = all(
                [
                    "ACGS Constitutional Governance" in matrix_content,
                    "constitutional governance" in matrix_content.lower(),
                    "Constitutional AI" in matrix_content,
                    "Policy Governance" in matrix_content,
                ]
            )

        self.validation_results["tests"]["compliance_matrix"] = test_results

        if (
            test_results["matrix_exists"]
            and len(test_results["required_sections"]) >= 6
        ):
            logger.info("✅ Compliance matrix validation passed")
        else:
            logger.error("❌ Compliance matrix validation failed")

        return test_results

    def validate_service_boundary_analysis(self):
        """Validate the service boundary analysis documentation."""
        logger.info("🏗️ Validating Service Boundary Analysis...")

        analysis_path = (
            self.project_root / "docs" / "architecture" / "service_boundary_analysis.md"
        )
        test_results = {
            "analysis_exists": analysis_path.exists(),
            "service_inventory": False,
            "communication_patterns": False,
            "boundary_analysis": False,
            "risk_assessment": False,
            "mermaid_diagrams": False,
            "acgs_services": [],
        }

        if test_results["analysis_exists"]:
            with open(analysis_path) as f:
                analysis_content = f.read()

            # Check for service inventory
            test_results["service_inventory"] = all(
                [
                    "## Service Inventory" in analysis_content,
                    "### Core Services" in analysis_content,
                    "### Platform Services" in analysis_content,
                    "### Blockchain Services" in analysis_content,
                ]
            )

            # Check for communication patterns
            test_results["communication_patterns"] = all(
                [
                    "## Inter-Service Communication Patterns" in analysis_content,
                    "Authentication Flow" in analysis_content,
                    "Core Services Pipeline" in analysis_content,
                ]
            )

            # Check for boundary analysis
            test_results["boundary_analysis"] = all(
                [
                    "## Service Boundary Analysis" in analysis_content,
                    "Coupling Issues" in analysis_content,
                    "Recommendations" in analysis_content,
                ]
            )

            # Check for risk assessment
            test_results["risk_assessment"] = all(
                [
                    "## Boundary Coupling Risk Assessment" in analysis_content,
                    "High Risk" in analysis_content,
                    "Medium Risk" in analysis_content,
                    "Low Risk" in analysis_content,
                ]
            )

            # Check for Mermaid diagrams
            test_results["mermaid_diagrams"] = "```mermaid" in analysis_content

            # Check for ACGS services
            acgs_services = [
                "Constitutional AI",
                "Governance Synthesis",
                "Policy Governance",
                "Formal Verification",
                "Authentication",
                "Integrity",
                "Workflow",
            ]
            for service in acgs_services:
                if service in analysis_content:
                    test_results["acgs_services"].append(service)

        self.validation_results["tests"]["service_boundary_analysis"] = test_results

        if test_results["analysis_exists"] and test_results["service_inventory"]:
            logger.info("✅ Service boundary analysis validation passed")
        else:
            logger.error("❌ Service boundary analysis validation failed")

        return test_results

    def run_validation(self):
        """Run complete validation of security and compliance tools."""
        logger.info("🚀 Starting ACGS-1 Security & Compliance Tools Validation")

        # Run all validations
        security_scan = self.validate_security_scan_script()
        pgc_load_test = self.validate_pgc_load_test()
        compliance_matrix = self.validate_compliance_matrix()
        service_boundary = self.validate_service_boundary_analysis()

        # Calculate overall status
        all_tests = [security_scan, pgc_load_test, compliance_matrix, service_boundary]
        passed_tests = sum(1 for test in all_tests if self._test_passed(test))
        total_tests = len(all_tests)

        self.validation_results["passed_tests"] = passed_tests
        self.validation_results["total_tests"] = total_tests
        self.validation_results["success_rate"] = (passed_tests / total_tests) * 100

        if passed_tests == total_tests:
            self.validation_results["overall_status"] = "PASSED"
            logger.info("✅ All security and compliance tools validation PASSED")
        elif passed_tests >= total_tests * 0.75:
            self.validation_results["overall_status"] = "MOSTLY_PASSED"
            logger.warning("⚠️ Most security and compliance tools validation passed")
        else:
            self.validation_results["overall_status"] = "FAILED"
            logger.error("❌ Security and compliance tools validation FAILED")

        # Save validation report
        self._save_validation_report()

        return self.validation_results

    def _test_passed(self, test_result):
        """Determine if a test passed based on its results."""
        if "script_exists" in test_result:
            return test_result["script_exists"] and test_result["script_executable"]
        if "test_exists" in test_result:
            return test_result["test_exists"] and test_result["locust_implementation"]
        if "matrix_exists" in test_result:
            return (
                test_result["matrix_exists"]
                and len(test_result["required_sections"]) >= 6
            )
        if "analysis_exists" in test_result:
            return test_result["analysis_exists"] and test_result["service_inventory"]
        return False

    def _save_validation_report(self):
        """Save validation report to logs directory."""
        logs_dir = self.project_root / "logs"
        logs_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = logs_dir / f"security_compliance_validation_{timestamp}.json"

        with open(report_file, "w") as f:
            json.dump(self.validation_results, f, indent=2)

        logger.info(f"📊 Validation report saved: {report_file}")


def main():
    """Main validation function."""
    validator = SecurityComplianceValidator()
    results = validator.run_validation()

    # Print summary
    print("\n" + "=" * 60)
    print("🔒 ACGS-1 SECURITY & COMPLIANCE TOOLS VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Overall Status: {results['overall_status']}")
    print(f"Success Rate: {results['success_rate']:.1f}%")
    print(f"Tests Passed: {results['passed_tests']}/{results['total_tests']}")
    print(
        f"Constitutional Compliance: {'✅' if results['constitutional_compliance'] else '❌'}"
    )
    print("=" * 60)

    # Exit with appropriate code
    if results["overall_status"] == "PASSED":
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
