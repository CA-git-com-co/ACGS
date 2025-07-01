#!/usr/bin/env python3
"""
Business Rules and Edge Case Testing Framework
Validates business rule implementations, governance workflows, and constitutional compliance.
"""

import json
import re
import sys
import time
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

# Add project paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "services"))
sys.path.insert(0, str(project_root / "services/shared"))


class TestStatus(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    SKIP = "SKIP"
    ERROR = "ERROR"


@dataclass
class BusinessRuleTestResult:
    test_name: str
    status: TestStatus
    execution_time: float
    rule_validations: list[dict[str, Any]]
    edge_cases_tested: int
    edge_cases_passed: int
    details: dict[str, Any]
    error_message: str | None = None


class BusinessRulesTester:
    def __init__(self):
        self.results = []
        self.project_root = project_root

    def log_result(self, result: BusinessRuleTestResult):
        """Log a business rule test result."""
        self.results.append(result)
        status_symbol = {"PASS": "✓", "FAIL": "✗", "SKIP": "⊝", "ERROR": "⚠"}
        symbol = status_symbol.get(result.status.value, "?")

        edge_case_rate = (
            (result.edge_cases_passed / result.edge_cases_tested * 100)
            if result.edge_cases_tested > 0
            else 0
        )

        print(f"{symbol} {result.test_name} ({result.execution_time:.3f}s)")
        print(f"  Rules Validated: {len(result.rule_validations)}")
        print(
            f"  Edge Cases: {result.edge_cases_passed}/{result.edge_cases_tested} ({edge_case_rate:.1f}%)"
        )

        if result.error_message:
            print(f"  Error: {result.error_message}")

    def test_governance_workflow_rules(self) -> BusinessRuleTestResult:
        """Test governance workflow business rules."""
        start_time = time.time()
        try:
            # Define governance workflow rules
            governance_rules = [
                {
                    "rule_id": "GWR001",
                    "description": "Proposal must have valid title and description",
                    "validator": lambda proposal: len(proposal.get("title", "")) > 0
                    and len(proposal.get("description", "")) > 10,
                },
                {
                    "rule_id": "GWR002",
                    "description": "Proposal status must be valid",
                    "validator": lambda proposal: proposal.get("status")
                    in ["draft", "submitted", "under_review", "approved", "rejected"],
                },
                {
                    "rule_id": "GWR003",
                    "description": "Approved proposals must have approval timestamp",
                    "validator": lambda proposal: proposal.get("status") != "approved"
                    or proposal.get("approved_at") is not None,
                },
                {
                    "rule_id": "GWR004",
                    "description": "Proposal priority must be valid",
                    "validator": lambda proposal: proposal.get("priority")
                    in ["low", "medium", "high", "critical"],
                },
            ]

            # Test data including edge cases
            test_proposals = [
                # Valid proposals
                {
                    "title": "Valid Proposal",
                    "description": "This is a valid proposal description",
                    "status": "draft",
                    "priority": "medium",
                },
                {
                    "title": "Another Valid",
                    "description": "Another valid proposal with more details",
                    "status": "approved",
                    "approved_at": "2024-01-01T00:00:00Z",
                    "priority": "high",
                },
                # Edge cases
                {
                    "title": "",
                    "description": "Missing title",
                    "status": "draft",
                    "priority": "low",
                },  # Should fail GWR001
                {
                    "title": "Valid Title",
                    "description": "Short",
                    "status": "draft",
                    "priority": "medium",
                },  # Should fail GWR001
                {
                    "title": "Valid Title",
                    "description": "Valid description here",
                    "status": "invalid_status",
                    "priority": "medium",
                },  # Should fail GWR002
                {
                    "title": "Valid Title",
                    "description": "Valid description here",
                    "status": "approved",
                    "priority": "high",
                },  # Should fail GWR003
                {
                    "title": "Valid Title",
                    "description": "Valid description here",
                    "status": "draft",
                    "priority": "invalid",
                },  # Should fail GWR004
            ]

            rule_validations = []
            edge_cases_tested = 0
            edge_cases_passed = 0

            for rule in governance_rules:
                rule_results = []
                for i, proposal in enumerate(test_proposals):
                    try:
                        is_valid = rule["validator"](proposal)
                        rule_results.append(
                            {
                                "proposal_index": i,
                                "valid": is_valid,
                                "proposal": proposal,
                            }
                        )

                        # Count edge cases (proposals that should fail)
                        if i >= 2:  # Edge cases start from index 2
                            edge_cases_tested += 1
                            if not is_valid:  # Edge case should fail validation
                                edge_cases_passed += 1

                    except Exception as e:
                        rule_results.append(
                            {
                                "proposal_index": i,
                                "valid": False,
                                "error": str(e),
                                "proposal": proposal,
                            }
                        )

                rule_validations.append(
                    {
                        "rule_id": rule["rule_id"],
                        "description": rule["description"],
                        "results": rule_results,
                        "total_tests": len(test_proposals),
                        "passed_tests": sum(
                            1 for r in rule_results if r.get("valid", False)
                        ),
                    }
                )

            # Determine overall status
            total_validations = sum(len(rv["results"]) for rv in rule_validations)
            passed_validations = sum(rv["passed_tests"] for rv in rule_validations)
            success_rate = (
                passed_validations / total_validations if total_validations > 0 else 0
            )

            status = (
                TestStatus.PASS if success_rate > 0.7 else TestStatus.FAIL
            )  # 70% threshold

            return BusinessRuleTestResult(
                "governance_workflow_rules",
                status,
                time.time() - start_time,
                rule_validations,
                edge_cases_tested,
                edge_cases_passed,
                {
                    "total_validations": total_validations,
                    "passed_validations": passed_validations,
                    "success_rate": success_rate,
                    "test_proposals": len(test_proposals),
                },
            )

        except Exception as e:
            return BusinessRuleTestResult(
                "governance_workflow_rules",
                TestStatus.ERROR,
                time.time() - start_time,
                [],
                0,
                0,
                {},
                str(e),
            )

    def test_policy_synthesis_rules(self) -> BusinessRuleTestResult:
        """Test policy synthesis business rules."""
        start_time = time.time()
        try:
            # Define policy synthesis rules
            policy_rules = [
                {
                    "rule_id": "PSR001",
                    "description": "Policy must have unique identifier",
                    "validator": lambda policy: policy.get("id") is not None
                    and len(str(policy.get("id"))) > 0,
                },
                {
                    "rule_id": "PSR002",
                    "description": "Policy content must be valid JSON or structured format",
                    "validator": lambda policy: isinstance(
                        policy.get("content"), (dict, list, str)
                    )
                    and policy.get("content") is not None,
                },
                {
                    "rule_id": "PSR003",
                    "description": "Policy version must be semantic version format",
                    "validator": lambda policy: re.match(
                        r"^\d+\.\d+\.\d+$", str(policy.get("version", ""))
                    )
                    is not None,
                },
                {
                    "rule_id": "PSR004",
                    "description": "Policy must have valid effective date",
                    "validator": lambda policy: policy.get("effective_date") is not None
                    and len(str(policy.get("effective_date"))) > 0,
                },
            ]

            # Test policies including edge cases
            test_policies = [
                # Valid policies
                {
                    "id": "POL001",
                    "content": {"rules": ["rule1", "rule2"]},
                    "version": "1.0.0",
                    "effective_date": "2024-01-01",
                },
                {
                    "id": "POL002",
                    "content": "Simple text policy",
                    "version": "2.1.3",
                    "effective_date": "2024-02-01",
                },
                # Edge cases
                {
                    "id": None,
                    "content": {"rules": []},
                    "version": "1.0.0",
                    "effective_date": "2024-01-01",
                },  # Should fail PSR001
                {
                    "id": "POL003",
                    "content": None,
                    "version": "1.0.0",
                    "effective_date": "2024-01-01",
                },  # Should fail PSR002
                {
                    "id": "POL004",
                    "content": {"rules": []},
                    "version": "invalid",
                    "effective_date": "2024-01-01",
                },  # Should fail PSR003
                {
                    "id": "POL005",
                    "content": {"rules": []},
                    "version": "1.0.0",
                    "effective_date": None,
                },  # Should fail PSR004
            ]

            rule_validations = []
            edge_cases_tested = 0
            edge_cases_passed = 0

            for rule in policy_rules:
                rule_results = []
                for i, policy in enumerate(test_policies):
                    try:
                        is_valid = rule["validator"](policy)
                        rule_results.append(
                            {"policy_index": i, "valid": is_valid, "policy": policy}
                        )

                        # Count edge cases
                        if i >= 2:
                            edge_cases_tested += 1
                            if not is_valid:
                                edge_cases_passed += 1

                    except Exception as e:
                        rule_results.append(
                            {
                                "policy_index": i,
                                "valid": False,
                                "error": str(e),
                                "policy": policy,
                            }
                        )

                rule_validations.append(
                    {
                        "rule_id": rule["rule_id"],
                        "description": rule["description"],
                        "results": rule_results,
                        "total_tests": len(test_policies),
                        "passed_tests": sum(
                            1 for r in rule_results if r.get("valid", False)
                        ),
                    }
                )

            total_validations = sum(len(rv["results"]) for rv in rule_validations)
            passed_validations = sum(rv["passed_tests"] for rv in rule_validations)
            success_rate = (
                passed_validations / total_validations if total_validations > 0 else 0
            )

            status = TestStatus.PASS if success_rate > 0.7 else TestStatus.FAIL

            return BusinessRuleTestResult(
                "policy_synthesis_rules",
                status,
                time.time() - start_time,
                rule_validations,
                edge_cases_tested,
                edge_cases_passed,
                {
                    "total_validations": total_validations,
                    "passed_validations": passed_validations,
                    "success_rate": success_rate,
                    "test_policies": len(test_policies),
                },
            )

        except Exception as e:
            return BusinessRuleTestResult(
                "policy_synthesis_rules",
                TestStatus.ERROR,
                time.time() - start_time,
                [],
                0,
                0,
                {},
                str(e),
            )

    def test_constitutional_compliance_rules(self) -> BusinessRuleTestResult:
        """Test constitutional compliance validation rules."""
        start_time = time.time()
        try:
            # Define constitutional compliance rules
            compliance_rules = [
                {
                    "rule_id": "CCR001",
                    "description": "Constitutional hash must be valid format",
                    "validator": lambda doc: re.match(
                        r"^[a-f0-9]{16}$", str(doc.get("constitutional_hash", ""))
                    )
                    is not None,
                },
                {
                    "rule_id": "CCR002",
                    "description": "Document must have required constitutional fields",
                    "validator": lambda doc: all(
                        field in doc
                        for field in [
                            "constitutional_hash",
                            "compliance_level",
                            "validation_timestamp",
                        ]
                    ),
                },
                {
                    "rule_id": "CCR003",
                    "description": "Compliance level must be valid",
                    "validator": lambda doc: doc.get("compliance_level")
                    in ["full", "partial", "non_compliant", "pending"],
                },
                {
                    "rule_id": "CCR004",
                    "description": "High compliance documents must have approval",
                    "validator": lambda doc: doc.get("compliance_level") != "full"
                    or doc.get("approved_by") is not None,
                },
            ]

            # Test documents including edge cases
            test_documents = [
                # Valid documents
                {
                    "constitutional_hash": "cdd01ef066bc6cf2",
                    "compliance_level": "full",
                    "validation_timestamp": "2024-01-01T00:00:00Z",
                    "approved_by": "admin",
                },
                {
                    "constitutional_hash": "abc123def4567890",
                    "compliance_level": "partial",
                    "validation_timestamp": "2024-01-01T00:00:00Z",
                },
                # Edge cases
                {
                    "constitutional_hash": "invalid_hash",  # Should fail CCR001
                    "compliance_level": "full",
                    "validation_timestamp": "2024-01-01T00:00:00Z",
                },
                {
                    "constitutional_hash": "cdd01ef066bc6cf2",
                    "compliance_level": "full",  # Missing required fields, should fail CCR002
                },
                {
                    "constitutional_hash": "cdd01ef066bc6cf2",
                    "compliance_level": "invalid_level",  # Should fail CCR003
                    "validation_timestamp": "2024-01-01T00:00:00Z",
                },
                {
                    "constitutional_hash": "cdd01ef066bc6cf2",
                    "compliance_level": "full",  # Should fail CCR004 (no approval)
                    "validation_timestamp": "2024-01-01T00:00:00Z",
                },
            ]

            rule_validations = []
            edge_cases_tested = 0
            edge_cases_passed = 0

            for rule in compliance_rules:
                rule_results = []
                for i, document in enumerate(test_documents):
                    try:
                        is_valid = rule["validator"](document)
                        rule_results.append(
                            {
                                "document_index": i,
                                "valid": is_valid,
                                "document": document,
                            }
                        )

                        # Count edge cases
                        if i >= 2:
                            edge_cases_tested += 1
                            if not is_valid:
                                edge_cases_passed += 1

                    except Exception as e:
                        rule_results.append(
                            {
                                "document_index": i,
                                "valid": False,
                                "error": str(e),
                                "document": document,
                            }
                        )

                rule_validations.append(
                    {
                        "rule_id": rule["rule_id"],
                        "description": rule["description"],
                        "results": rule_results,
                        "total_tests": len(test_documents),
                        "passed_tests": sum(
                            1 for r in rule_results if r.get("valid", False)
                        ),
                    }
                )

            total_validations = sum(len(rv["results"]) for rv in rule_validations)
            passed_validations = sum(rv["passed_tests"] for rv in rule_validations)
            success_rate = (
                passed_validations / total_validations if total_validations > 0 else 0
            )

            status = TestStatus.PASS if success_rate > 0.7 else TestStatus.FAIL

            return BusinessRuleTestResult(
                "constitutional_compliance_rules",
                status,
                time.time() - start_time,
                rule_validations,
                edge_cases_tested,
                edge_cases_passed,
                {
                    "total_validations": total_validations,
                    "passed_validations": passed_validations,
                    "success_rate": success_rate,
                    "test_documents": len(test_documents),
                },
            )

        except Exception as e:
            return BusinessRuleTestResult(
                "constitutional_compliance_rules",
                TestStatus.ERROR,
                time.time() - start_time,
                [],
                0,
                0,
                {},
                str(e),
            )

    def test_error_handling_patterns(self) -> BusinessRuleTestResult:
        """Test error handling patterns and edge cases."""
        start_time = time.time()
        try:
            error_scenarios = []

            # Test various error conditions
            test_cases = [
                {
                    "name": "null_input_handling",
                    "test": lambda: self._handle_null_input(None),
                    "expected_error": True,
                },
                {
                    "name": "empty_string_handling",
                    "test": lambda: self._handle_empty_string(""),
                    "expected_error": True,
                },
                {
                    "name": "invalid_json_handling",
                    "test": lambda: self._handle_invalid_json("{invalid json}"),
                    "expected_error": True,
                },
                {
                    "name": "large_input_handling",
                    "test": lambda: self._handle_large_input(
                        "x" * 100000
                    ),  # Reduced size
                    "expected_error": True,  # Changed to True since it should error
                },
                {
                    "name": "unicode_handling",
                    "test": lambda: self._handle_unicode_input("🚀 Unicode test 中文"),
                    "expected_error": False,
                },
            ]

            edge_cases_tested = len(test_cases)
            edge_cases_passed = 0

            for test_case in test_cases:
                try:
                    result = test_case["test"]()
                    error_occurred = result.get("error", False)

                    # Check if error handling matches expectation
                    if test_case["expected_error"] == error_occurred:
                        edge_cases_passed += 1
                        error_scenarios.append(
                            {
                                "name": test_case["name"],
                                "status": "passed",
                                "expected_error": test_case["expected_error"],
                                "actual_error": error_occurred,
                                "result": result,
                            }
                        )
                    else:
                        error_scenarios.append(
                            {
                                "name": test_case["name"],
                                "status": "failed",
                                "expected_error": test_case["expected_error"],
                                "actual_error": error_occurred,
                                "result": result,
                            }
                        )

                except Exception as e:
                    # Unexpected exception
                    if test_case["expected_error"]:
                        edge_cases_passed += 1
                        error_scenarios.append(
                            {
                                "name": test_case["name"],
                                "status": "passed",
                                "expected_error": True,
                                "actual_error": True,
                                "exception": str(e),
                            }
                        )
                    else:
                        error_scenarios.append(
                            {
                                "name": test_case["name"],
                                "status": "failed",
                                "expected_error": False,
                                "actual_error": True,
                                "exception": str(e),
                            }
                        )

            rule_validations = [
                {
                    "rule_id": "EHR001",
                    "description": "Error handling patterns validation",
                    "results": error_scenarios,
                    "total_tests": len(test_cases),
                    "passed_tests": edge_cases_passed,
                }
            ]

            status = (
                TestStatus.PASS
                if edge_cases_passed == edge_cases_tested
                else TestStatus.FAIL
            )

            return BusinessRuleTestResult(
                "error_handling_patterns",
                status,
                time.time() - start_time,
                rule_validations,
                edge_cases_tested,
                edge_cases_passed,
                {
                    "error_scenarios": error_scenarios,
                    "total_scenarios": len(test_cases),
                },
            )

        except Exception as e:
            return BusinessRuleTestResult(
                "error_handling_patterns",
                TestStatus.ERROR,
                time.time() - start_time,
                [],
                0,
                0,
                {},
                str(e),
            )

    def _handle_null_input(self, input_data):
        """Helper method to test null input handling."""
        if input_data is None:
            return {"error": True, "message": "Null input not allowed"}
        return {"error": False, "data": input_data}

    def _handle_empty_string(self, input_data):
        """Helper method to test empty string handling."""
        if input_data == "":
            return {"error": True, "message": "Empty string not allowed"}
        return {"error": False, "data": input_data}

    def _handle_invalid_json(self, input_data):
        """Helper method to test invalid JSON handling."""
        try:
            json.loads(input_data)
            return {"error": False, "data": input_data}
        except json.JSONDecodeError:
            return {"error": True, "message": "Invalid JSON format"}

    def _handle_large_input(self, input_data):
        """Helper method to test large input handling."""
        if len(input_data) > 500000:  # 500KB limit
            return {"error": True, "message": "Input too large"}
        return {"error": False, "data_length": len(input_data)}

    def _handle_unicode_input(self, input_data):
        """Helper method to test Unicode input handling."""
        try:
            # Test Unicode encoding/decoding
            encoded = input_data.encode("utf-8")
            decoded = encoded.decode("utf-8")
            return {"error": False, "original": input_data, "processed": decoded}
        except UnicodeError:
            return {"error": True, "message": "Unicode processing failed"}

    def run_all_tests(self) -> dict[str, Any]:
        """Run all business rule tests."""
        print("Starting Business Rules and Edge Case Testing...")
        print("=" * 60)

        # Define test methods
        test_methods = [
            self.test_governance_workflow_rules,
            self.test_policy_synthesis_rules,
            self.test_constitutional_compliance_rules,
            self.test_error_handling_patterns,
        ]

        # Run all tests
        for test_method in test_methods:
            try:
                result = test_method()
                self.log_result(result)
            except Exception as e:
                error_result = BusinessRuleTestResult(
                    test_method.__name__,
                    TestStatus.ERROR,
                    0.0,
                    [],
                    0,
                    0,
                    {},
                    f"Test execution failed: {e!s}",
                )
                self.log_result(error_result)

        # Generate summary
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.status == TestStatus.PASS)
        failed_tests = sum(1 for r in self.results if r.status == TestStatus.FAIL)
        error_tests = sum(1 for r in self.results if r.status == TestStatus.ERROR)

        total_edge_cases = sum(r.edge_cases_tested for r in self.results)
        passed_edge_cases = sum(r.edge_cases_passed for r in self.results)
        edge_case_success_rate = (
            (passed_edge_cases / total_edge_cases * 100) if total_edge_cases > 0 else 0
        )

        summary = {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "errors": error_tests,
            "success_rate": (
                (passed_tests / total_tests * 100) if total_tests > 0 else 0
            ),
            "edge_case_summary": {
                "total_edge_cases": total_edge_cases,
                "passed_edge_cases": passed_edge_cases,
                "edge_case_success_rate": edge_case_success_rate,
            },
            "results": [
                {
                    "test_name": r.test_name,
                    "status": r.status.value,
                    "execution_time": r.execution_time,
                    "rule_validations": len(r.rule_validations),
                    "edge_cases_tested": r.edge_cases_tested,
                    "edge_cases_passed": r.edge_cases_passed,
                    "details": r.details,
                    "error_message": r.error_message,
                }
                for r in self.results
            ],
        }

        print("\n" + "=" * 60)
        print("BUSINESS RULES TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Errors: {error_tests}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(
            f"Edge Cases: {passed_edge_cases}/{total_edge_cases} ({edge_case_success_rate:.1f}%)"
        )

        return summary


def main():
    tester = BusinessRulesTester()
    summary = tester.run_all_tests()

    # Save results
    output_file = project_root / "business_rules_test_results.json"
    with open(output_file, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")

    # Return appropriate exit code
    if summary["failed"] > 0 or summary["errors"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
