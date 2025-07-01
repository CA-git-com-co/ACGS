#!/usr/bin/env python3
"""
ACGS-1 Backward Compatibility Validation Script

Comprehensive testing of all 86 API endpoints across 8 services to ensure
zero breaking changes when versioning middleware is enabled.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EndpointTest:
    """Represents a single endpoint test case."""

    service: str
    endpoint: str
    method: str
    test_data: Optional[Dict[str, Any]] = None
    expected_status: int = 200
    auth_required: bool = True
    version_header: Optional[str] = None


@dataclass
class CompatibilityTestResult:
    """Results of backward compatibility testing."""

    endpoint: str
    method: str
    service: str
    success: bool
    response_time_ms: float
    status_code: int
    error_message: Optional[str] = None
    version_detected: Optional[str] = None
    headers_present: Dict[str, bool] = field(default_factory=dict)


class BackwardCompatibilityValidator:
    """
    Validates backward compatibility across all ACGS-1 services.

    Tests all existing endpoints to ensure they continue functioning
    with the new versioning middleware without breaking changes.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results: List[CompatibilityTestResult] = []
        self.services = [
            "constitutional-ai",
            "authentication",
            "formal-verification",
            "governance-synthesis",
            "policy-governance",
            "evolutionary-computation",
            "dgm-service",
            "integrity-service",
        ]

        # Load endpoint definitions
        self.endpoints = self._load_endpoint_definitions()

    def _load_endpoint_definitions(self) -> List[EndpointTest]:
        """Load all endpoint definitions for testing."""
        endpoints = []

        # Constitutional AI Service (12 endpoints)
        endpoints.extend(
            [
                EndpointTest("constitutional-ai", "/api/v1/principles", "GET"),
                EndpointTest(
                    "constitutional-ai",
                    "/api/v1/principles",
                    "POST",
                    {"content": "Test principle", "category": "ethics"},
                ),
                EndpointTest("constitutional-ai", "/api/v1/principles/{id}", "GET"),
                EndpointTest(
                    "constitutional-ai",
                    "/api/v1/principles/{id}",
                    "PUT",
                    {"content": "Updated principle"},
                ),
                EndpointTest("constitutional-ai", "/api/v1/principles/{id}", "DELETE"),
                EndpointTest(
                    "constitutional-ai",
                    "/api/v1/validate",
                    "POST",
                    {"text": "Test validation", "principles": ["ethics"]},
                ),
                EndpointTest(
                    "constitutional-ai",
                    "/api/v1/analyze",
                    "POST",
                    {"content": "Test analysis"},
                ),
                EndpointTest("constitutional-ai", "/api/v1/recommendations", "GET"),
                EndpointTest("constitutional-ai", "/api/v1/constitution", "GET"),
                EndpointTest(
                    "constitutional-ai",
                    "/api/v1/constitution/validate",
                    "POST",
                    {"constitution": "test constitution"},
                ),
                EndpointTest(
                    "constitutional-ai", "/api/v1/health", "GET", auth_required=False
                ),
                EndpointTest(
                    "constitutional-ai", "/api/v1/metrics", "GET", auth_required=False
                ),
            ]
        )

        # Authentication Service (8 endpoints)
        endpoints.extend(
            [
                EndpointTest(
                    "authentication",
                    "/api/v1/auth/login",
                    "POST",
                    {"username": "test", "password": "test"},
                    auth_required=False,
                ),
                EndpointTest("authentication", "/api/v1/auth/logout", "POST"),
                EndpointTest("authentication", "/api/v1/auth/refresh", "POST"),
                EndpointTest("authentication", "/api/v1/auth/validate", "POST"),
                EndpointTest("authentication", "/api/v1/users", "GET"),
                EndpointTest(
                    "authentication",
                    "/api/v1/users",
                    "POST",
                    {"username": "newuser", "email": "test@example.com"},
                ),
                EndpointTest("authentication", "/api/v1/users/{id}", "GET"),
                EndpointTest(
                    "authentication", "/api/v1/health", "GET", auth_required=False
                ),
            ]
        )

        # Formal Verification Service (10 endpoints)
        endpoints.extend(
            [
                EndpointTest(
                    "formal-verification",
                    "/api/v1/verify",
                    "POST",
                    {"specification": "test spec", "implementation": "test impl"},
                ),
                EndpointTest("formal-verification", "/api/v1/proofs", "GET"),
                EndpointTest(
                    "formal-verification",
                    "/api/v1/proofs",
                    "POST",
                    {"theorem": "test theorem", "proof": "test proof"},
                ),
                EndpointTest("formal-verification", "/api/v1/proofs/{id}", "GET"),
                EndpointTest("formal-verification", "/api/v1/theorems", "GET"),
                EndpointTest(
                    "formal-verification",
                    "/api/v1/theorems",
                    "POST",
                    {"name": "test theorem", "statement": "test statement"},
                ),
                EndpointTest("formal-verification", "/api/v1/models", "GET"),
                EndpointTest(
                    "formal-verification", "/api/v1/models/{id}/verify", "POST"
                ),
                EndpointTest("formal-verification", "/api/v1/specifications", "GET"),
                EndpointTest(
                    "formal-verification", "/api/v1/health", "GET", auth_required=False
                ),
            ]
        )

        # Governance Synthesis Service (15 endpoints)
        endpoints.extend(
            [
                EndpointTest("governance-synthesis", "/api/v1/policies", "GET"),
                EndpointTest(
                    "governance-synthesis",
                    "/api/v1/policies",
                    "POST",
                    {"title": "Test Policy", "content": "Test content"},
                ),
                EndpointTest("governance-synthesis", "/api/v1/policies/{id}", "GET"),
                EndpointTest("governance-synthesis", "/api/v1/policies/{id}", "PUT"),
                EndpointTest("governance-synthesis", "/api/v1/policies/{id}", "DELETE"),
                EndpointTest(
                    "governance-synthesis",
                    "/api/v1/synthesis",
                    "POST",
                    {"inputs": ["input1", "input2"]},
                ),
                EndpointTest(
                    "governance-synthesis",
                    "/api/v1/consensus",
                    "POST",
                    {"proposals": ["proposal1", "proposal2"]},
                ),
                EndpointTest("governance-synthesis", "/api/v1/frameworks", "GET"),
                EndpointTest("governance-synthesis", "/api/v1/frameworks", "POST"),
                EndpointTest("governance-synthesis", "/api/v1/frameworks/{id}", "GET"),
                EndpointTest("governance-synthesis", "/api/v1/voting", "POST"),
                EndpointTest(
                    "governance-synthesis", "/api/v1/voting/{id}/results", "GET"
                ),
                EndpointTest("governance-synthesis", "/api/v1/stakeholders", "GET"),
                EndpointTest("governance-synthesis", "/api/v1/stakeholders", "POST"),
                EndpointTest(
                    "governance-synthesis", "/api/v1/health", "GET", auth_required=False
                ),
            ]
        )

        # Policy Governance Service (20 endpoints)
        endpoints.extend(
            [
                EndpointTest("policy-governance", "/api/v1/governance", "GET"),
                EndpointTest("policy-governance", "/api/v1/governance/rules", "GET"),
                EndpointTest("policy-governance", "/api/v1/governance/rules", "POST"),
                EndpointTest(
                    "policy-governance", "/api/v1/governance/rules/{id}", "GET"
                ),
                EndpointTest(
                    "policy-governance", "/api/v1/governance/rules/{id}", "PUT"
                ),
                EndpointTest(
                    "policy-governance", "/api/v1/governance/rules/{id}", "DELETE"
                ),
                EndpointTest("policy-governance", "/api/v1/compliance", "GET"),
                EndpointTest("policy-governance", "/api/v1/compliance/check", "POST"),
                EndpointTest("policy-governance", "/api/v1/compliance/reports", "GET"),
                EndpointTest("policy-governance", "/api/v1/enforcement", "GET"),
                EndpointTest(
                    "policy-governance", "/api/v1/enforcement/actions", "POST"
                ),
                EndpointTest(
                    "policy-governance", "/api/v1/enforcement/violations", "GET"
                ),
                EndpointTest("policy-governance", "/api/v1/quantum/coherence", "GET"),
                EndpointTest(
                    "policy-governance", "/api/v1/quantum/entanglement", "POST"
                ),
                EndpointTest(
                    "policy-governance", "/api/v1/quantum/superposition", "GET"
                ),
                EndpointTest(
                    "policy-governance", "/api/v1/semantic/fault-tolerance", "GET"
                ),
                EndpointTest(
                    "policy-governance", "/api/v1/semantic/validation", "POST"
                ),
                EndpointTest("policy-governance", "/api/v1/adaptive/learning", "POST"),
                EndpointTest("policy-governance", "/api/v1/adaptive/evolution", "GET"),
                EndpointTest(
                    "policy-governance", "/api/v1/health", "GET", auth_required=False
                ),
            ]
        )

        # Evolutionary Computation Service (8 endpoints)
        endpoints.extend(
            [
                EndpointTest("evolutionary-computation", "/api/v1/evolution", "POST"),
                EndpointTest("evolutionary-computation", "/api/v1/populations", "GET"),
                EndpointTest("evolutionary-computation", "/api/v1/populations", "POST"),
                EndpointTest(
                    "evolutionary-computation", "/api/v1/populations/{id}", "GET"
                ),
                EndpointTest("evolutionary-computation", "/api/v1/fitness", "POST"),
                EndpointTest("evolutionary-computation", "/api/v1/mutations", "POST"),
                EndpointTest("evolutionary-computation", "/api/v1/crossover", "POST"),
                EndpointTest(
                    "evolutionary-computation",
                    "/api/v1/health",
                    "GET",
                    auth_required=False,
                ),
            ]
        )

        # DGM Service (7 endpoints)
        endpoints.extend(
            [
                EndpointTest("dgm-service", "/api/v1/machines", "GET"),
                EndpointTest("dgm-service", "/api/v1/machines", "POST"),
                EndpointTest("dgm-service", "/api/v1/machines/{id}", "GET"),
                EndpointTest("dgm-service", "/api/v1/machines/{id}/execute", "POST"),
                EndpointTest("dgm-service", "/api/v1/godel/theorems", "GET"),
                EndpointTest("dgm-service", "/api/v1/darwin/evolution", "POST"),
                EndpointTest(
                    "dgm-service", "/api/v1/health", "GET", auth_required=False
                ),
            ]
        )

        # Integrity Service (6 endpoints)
        endpoints.extend(
            [
                EndpointTest("integrity-service", "/api/v1/integrity", "GET"),
                EndpointTest("integrity-service", "/api/v1/integrity/check", "POST"),
                EndpointTest("integrity-service", "/api/v1/integrity/verify", "POST"),
                EndpointTest("integrity-service", "/api/v1/integrity/reports", "GET"),
                EndpointTest(
                    "integrity-service", "/api/v1/integrity/violations", "GET"
                ),
                EndpointTest(
                    "integrity-service", "/api/v1/health", "GET", auth_required=False
                ),
            ]
        )

        logger.info(
            f"Loaded {len(endpoints)} endpoint definitions across {len(self.services)} services"
        )
        return endpoints

    async def run_compatibility_tests(self) -> Dict[str, Any]:
        """Run comprehensive backward compatibility tests."""
        logger.info("🔍 Starting backward compatibility validation...")

        start_time = time.time()

        # Test without versioning middleware (baseline)
        baseline_results = await self._test_endpoints_baseline()

        # Test with versioning middleware enabled
        versioned_results = await self._test_endpoints_with_versioning()

        # Compare results
        comparison_report = self._compare_results(baseline_results, versioned_results)

        end_time = time.time()

        # Generate comprehensive report
        report = {
            "test_summary": {
                "total_endpoints": len(self.endpoints),
                "total_services": len(self.services),
                "test_duration_seconds": round(end_time - start_time, 2),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "baseline_results": baseline_results,
            "versioned_results": versioned_results,
            "compatibility_analysis": comparison_report,
            "success_criteria": {
                "zero_breaking_changes": comparison_report["breaking_changes"] == 0,
                "performance_degradation_under_5ms": comparison_report[
                    "avg_latency_increase_ms"
                ]
                < 5.0,
                "all_endpoints_functional": comparison_report[
                    "functional_endpoints_percentage"
                ]
                >= 99.0,
            },
        }

        logger.info(
            f"✅ Compatibility validation completed in {report['test_summary']['test_duration_seconds']}s"
        )
        return report

    async def _test_endpoints_baseline(self) -> Dict[str, Any]:
        """Test all endpoints without versioning middleware (baseline)."""
        logger.info("📊 Testing baseline (without versioning middleware)...")

        results = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for endpoint_test in self.endpoints:
                result = await self._test_single_endpoint(
                    client, endpoint_test, baseline=True
                )
                results.append(result)

        return self._aggregate_results(results, "baseline")

    async def _test_endpoints_with_versioning(self) -> Dict[str, Any]:
        """Test all endpoints with versioning middleware enabled."""
        logger.info("🔄 Testing with versioning middleware enabled...")

        results = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for endpoint_test in self.endpoints:
                result = await self._test_single_endpoint(
                    client, endpoint_test, baseline=False
                )
                results.append(result)

        return self._aggregate_results(results, "versioned")

    async def _test_single_endpoint(
        self,
        client: httpx.AsyncClient,
        endpoint_test: EndpointTest,
        baseline: bool = False,
    ) -> CompatibilityTestResult:
        """Test a single endpoint and return results."""
        start_time = time.time()

        try:
            # Prepare request
            url = f"{self.base_url}/{endpoint_test.service}{endpoint_test.endpoint}"
            headers = {}

            # Add authentication if required
            if endpoint_test.auth_required:
                headers["Authorization"] = "Bearer test-token"

            # Add version header for versioned tests
            if not baseline and endpoint_test.version_header:
                headers["API-Version"] = endpoint_test.version_header
            elif not baseline:
                headers["API-Version"] = "v1.0.0"  # Default version

            # Make request
            if endpoint_test.method == "GET":
                response = await client.get(url, headers=headers)
            elif endpoint_test.method == "POST":
                response = await client.post(
                    url, headers=headers, json=endpoint_test.test_data
                )
            elif endpoint_test.method == "PUT":
                response = await client.put(
                    url, headers=headers, json=endpoint_test.test_data
                )
            elif endpoint_test.method == "DELETE":
                response = await client.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {endpoint_test.method}")

            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            # Check for version headers in response
            version_headers = {
                "api_version_present": "API-Version" in response.headers,
                "x_api_version_present": "X-API-Version" in response.headers,
                "deprecation_present": "Deprecation" in response.headers,
                "sunset_present": "Sunset" in response.headers,
            }

            return CompatibilityTestResult(
                endpoint=endpoint_test.endpoint,
                method=endpoint_test.method,
                service=endpoint_test.service,
                success=response.status_code == endpoint_test.expected_status,
                response_time_ms=response_time_ms,
                status_code=response.status_code,
                version_detected=response.headers.get("API-Version"),
                headers_present=version_headers,
            )

        except Exception as e:
            end_time = time.time()
            response_time_ms = (end_time - start_time) * 1000

            return CompatibilityTestResult(
                endpoint=endpoint_test.endpoint,
                method=endpoint_test.method,
                service=endpoint_test.service,
                success=False,
                response_time_ms=response_time_ms,
                status_code=0,
                error_message=str(e),
            )

    def _aggregate_results(
        self, results: List[CompatibilityTestResult], test_type: str
    ) -> Dict[str, Any]:
        """Aggregate test results into summary statistics."""
        total_tests = len(results)
        successful_tests = len([r for r in results if r.success])
        failed_tests = total_tests - successful_tests

        response_times = [r.response_time_ms for r in results if r.success]
        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0
        )

        # Group by service
        service_results = {}
        for result in results:
            if result.service not in service_results:
                service_results[result.service] = {
                    "total": 0,
                    "successful": 0,
                    "failed": 0,
                }

            service_results[result.service]["total"] += 1
            if result.success:
                service_results[result.service]["successful"] += 1
            else:
                service_results[result.service]["failed"] += 1

        return {
            "test_type": test_type,
            "summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate_percentage": (
                    (successful_tests / total_tests) * 100 if total_tests > 0 else 0
                ),
                "average_response_time_ms": round(avg_response_time, 2),
            },
            "service_breakdown": service_results,
            "detailed_results": [
                {
                    "endpoint": r.endpoint,
                    "method": r.method,
                    "service": r.service,
                    "success": r.success,
                    "response_time_ms": r.response_time_ms,
                    "status_code": r.status_code,
                    "error_message": r.error_message,
                    "version_detected": r.version_detected,
                    "headers_present": r.headers_present,
                }
                for r in results
            ],
        }

    def _compare_results(
        self, baseline: Dict[str, Any], versioned: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compare baseline and versioned results to identify breaking changes."""
        baseline_success = baseline["summary"]["successful_tests"]
        versioned_success = versioned["summary"]["successful_tests"]

        baseline_avg_time = baseline["summary"]["average_response_time_ms"]
        versioned_avg_time = versioned["summary"]["average_response_time_ms"]

        # Identify breaking changes (endpoints that worked in baseline but failed with versioning)
        breaking_changes = []
        for i, baseline_result in enumerate(baseline["detailed_results"]):
            versioned_result = versioned["detailed_results"][i]

            if baseline_result["success"] and not versioned_result["success"]:
                breaking_changes.append(
                    {
                        "endpoint": baseline_result["endpoint"],
                        "method": baseline_result["method"],
                        "service": baseline_result["service"],
                        "baseline_status": baseline_result["status_code"],
                        "versioned_status": versioned_result["status_code"],
                        "error": versioned_result["error_message"],
                    }
                )

        return {
            "breaking_changes": len(breaking_changes),
            "breaking_change_details": breaking_changes,
            "functional_endpoints_percentage": (
                (versioned_success / baseline_success) * 100
                if baseline_success > 0
                else 0
            ),
            "avg_latency_increase_ms": versioned_avg_time - baseline_avg_time,
            "performance_impact_percentage": (
                ((versioned_avg_time - baseline_avg_time) / baseline_avg_time) * 100
                if baseline_avg_time > 0
                else 0
            ),
        }

    def save_report(self, report: Dict[str, Any], output_path: Path):
        """Save compatibility test report to file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"📄 Compatibility report saved to {output_path}")


async def main():
    """Main function to run backward compatibility validation."""
    validator = BackwardCompatibilityValidator()

    # Run comprehensive compatibility tests
    report = await validator.run_compatibility_tests()

    # Save report
    output_path = Path("docs/implementation/reports/backward_compatibility_report.json")
    validator.save_report(report, output_path)

    # Print summary
    print("\n" + "=" * 80)
    print("ACGS-1 BACKWARD COMPATIBILITY VALIDATION SUMMARY")
    print("=" * 80)

    summary = report["test_summary"]
    print(f"📊 Total Endpoints Tested: {summary['total_endpoints']}")
    print(f"🏢 Services Covered: {summary['total_services']}")
    print(f"⏱️  Test Duration: {summary['test_duration_seconds']}s")

    criteria = report["success_criteria"]
    print(f"\n🎯 SUCCESS CRITERIA:")
    print(
        f"   ✅ Zero Breaking Changes: {'PASS' if criteria['zero_breaking_changes'] else 'FAIL'}"
    )
    print(
        f"   ⚡ Performance Impact <5ms: {'PASS' if criteria['performance_degradation_under_5ms'] else 'FAIL'}"
    )
    print(
        f"   🔧 All Endpoints Functional: {'PASS' if criteria['all_endpoints_functional'] else 'FAIL'}"
    )

    analysis = report["compatibility_analysis"]
    print(f"\n📈 COMPATIBILITY ANALYSIS:")
    print(f"   Breaking Changes: {analysis['breaking_changes']}")
    print(
        f"   Functional Endpoints: {analysis['functional_endpoints_percentage']:.1f}%"
    )
    print(f"   Avg Latency Increase: {analysis['avg_latency_increase_ms']:.2f}ms")

    if analysis["breaking_changes"] > 0:
        print(f"\n⚠️  BREAKING CHANGES DETECTED:")
        for change in analysis["breaking_change_details"]:
            print(f"   - {change['method']} {change['endpoint']} ({change['service']})")
            print(
                f"     Status: {change['baseline_status']} → {change['versioned_status']}"
            )
            if change["error"]:
                print(f"     Error: {change['error']}")

    print("\n" + "=" * 80)

    # Return exit code based on success criteria
    all_criteria_passed = all(criteria.values())
    return 0 if all_criteria_passed else 1


if __name__ == "__main__":
    import sys

    exit_code = asyncio.run(main())
    sys.exit(exit_code)
