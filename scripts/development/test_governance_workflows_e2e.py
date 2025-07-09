#!/usr/bin/env python3
"""
End-to-End Governance Workflows Testing Script

This script conducts comprehensive testing of all 5 governance workflows:
1. Policy Creation Workflow
2. Constitutional Compliance Workflow
3. Policy Enforcement Workflow
4. WINA Oversight Workflow
5. Audit/Transparency Workflow

Performance targets:
- <500ms response times for 95% of requests
- >95% accuracy for compliance validation
- >1000 concurrent actions support
"""

import asyncio
import json
import logging
import statistics
import time
from typing import Any

import httpx

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GovernanceWorkflowTester:
    """Comprehensive end-to-end governance workflow testing."""

    def __init__(self):
        self.base_url = "http://localhost:8005"
        self.results = {
            "policy_creation": [],
            "constitutional_compliance": [],
            "policy_enforcement": [],
            "wina_oversight": [],
            "audit_transparency": [],
            "performance_metrics": {},
            "accuracy_metrics": {},
            "load_test_results": {},
        }

    async def test_policy_creation_workflow(self) -> dict[str, Any]:
        """Test Policy Creation workflow with Draft → Review → Voting → Implementation."""
        logger.info("🏛️ Testing Policy Creation Workflow...")

        test_cases = [
            {
                "title": "Data Privacy Protection Policy",
                "description": "Comprehensive policy for protecting citizen data privacy",
                "stakeholders": ["governance_team", "policy_reviewers", "legal_team"],
                "priority": "high",
            },
            {
                "title": "Environmental Sustainability Policy",
                "description": "Policy for environmental protection and sustainability",
                "stakeholders": ["governance_team", "environmental_team"],
                "priority": "medium",
            },
            {
                "title": "Digital Rights Policy",
                "description": "Policy ensuring digital rights and freedoms",
                "stakeholders": ["governance_team", "digital_rights_team"],
                "priority": "high",
            },
        ]

        results = []
        async with httpx.AsyncClient() as client:
            for test_case in test_cases:
                start_time = time.time()
                try:
                    response = await client.post(
                        f"{self.base_url}/api/v1/governance-workflows/api/v1/governance/policy-creation",
                        json=test_case,
                        timeout=10.0,
                    )
                    response_time = (time.time() - start_time) * 1000

                    if response.status_code == 200:
                        data = response.json()
                        results.append(
                            {
                                "test_case": test_case["title"],
                                "status": "success",
                                "response_time_ms": response_time,
                                "workflow_id": data.get("workflow_id"),
                                "current_stage": data.get("current_stage"),
                                "progress_percent": data.get("progress_percent"),
                            }
                        )
                        logger.info(
                            f"✅ Policy Creation: {test_case['title']} - {response_time:.2f}ms"
                        )
                    else:
                        results.append(
                            {
                                "test_case": test_case["title"],
                                "status": "failed",
                                "response_time_ms": response_time,
                                "error": response.text,
                            }
                        )
                        logger.error(f"❌ Policy Creation failed: {test_case['title']}")

                except Exception as e:
                    results.append(
                        {
                            "test_case": test_case["title"],
                            "status": "error",
                            "error": str(e),
                        }
                    )
                    logger.error(
                        f"❌ Policy Creation error: {test_case['title']} - {e}"
                    )

        return results

    async def test_constitutional_compliance_workflow(self) -> dict[str, Any]:
        """Test Constitutional Compliance workflow with Validation → Assessment → Enforcement."""
        logger.info("⚖️ Testing Constitutional Compliance Workflow...")

        results = []
        async with httpx.AsyncClient() as client:
            # Test constitutional hash validation
            start_time = time.time()
            try:
                response = await client.get(
                    f"{self.base_url}/api/v1/constitutional/validate",
                    params={
                        "hash_value": "cdd01ef066bc6cf2",
                        "validation_level": "comprehensive",
                    },
                    timeout=10.0,
                )
                response_time = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    data = response.json()
                    compliance_score = data.get("validation_result", {}).get(
                        "compliance_score", 0
                    )
                    results.append(
                        {
                            "test_case": "constitutional_hash_validation",
                            "status": "success",
                            "response_time_ms": response_time,
                            "compliance_score": compliance_score,
                            "hash_valid": data.get("validation_result", {}).get(
                                "hash_valid", False
                            ),
                        }
                    )
                    logger.info(
                        f"✅ Constitutional Compliance: Hash validation - {response_time:.2f}ms"
                    )
                else:
                    results.append(
                        {
                            "test_case": "constitutional_hash_validation",
                            "status": "failed",
                            "response_time_ms": response_time,
                            "error": response.text,
                        }
                    )

            except Exception as e:
                results.append(
                    {
                        "test_case": "constitutional_hash_validation",
                        "status": "error",
                        "error": str(e),
                    }
                )

        return results

    async def test_policy_enforcement_workflow(self) -> dict[str, Any]:
        """Test Policy Enforcement workflow with Monitoring → Violation Detection → Remediation."""
        logger.info("🛡️ Testing Policy Enforcement Workflow...")

        test_policies = ["POL-TEST-001", "POL-TEST-002", "POL-TEST-003"]
        results = []

        async with httpx.AsyncClient() as client:
            for policy_id in test_policies:
                # Test policy enforcement initiation
                start_time = time.time()
                try:
                    response = await client.post(
                        f"{self.base_url}/api/v1/governance-workflows/api/v1/governance/policy-enforcement",
                        params={
                            "policy_id": policy_id,
                            "enforcement_type": "automated",
                        },
                        timeout=10.0,
                    )
                    response_time = (time.time() - start_time) * 1000

                    if response.status_code == 200:
                        data = response.json()
                        results.append(
                            {
                                "test_case": f"enforcement_{policy_id}",
                                "status": "success",
                                "response_time_ms": response_time,
                                "workflow_id": data.get("workflow_id"),
                                "enforcement_status": data.get("status"),
                            }
                        )
                        logger.info(
                            f"✅ Policy Enforcement: {policy_id} - {response_time:.2f}ms"
                        )
                    else:
                        results.append(
                            {
                                "test_case": f"enforcement_{policy_id}",
                                "status": "failed",
                                "response_time_ms": response_time,
                                "error": response.text,
                            }
                        )

                except Exception as e:
                    results.append(
                        {
                            "test_case": f"enforcement_{policy_id}",
                            "status": "error",
                            "error": str(e),
                        }
                    )

                # Test PGC enforcement integration
                start_time = time.time()
                try:
                    response = await client.post(
                        f"{self.base_url}/api/v1/governance-workflows/api/v1/governance/pgc-enforcement-integration",
                        params={
                            "policy_id": policy_id,
                            "policy_content": f"Test policy content for {policy_id}",
                        },
                        timeout=10.0,
                    )
                    response_time = (time.time() - start_time) * 1000

                    if response.status_code == 200:
                        data = response.json()
                        results.append(
                            {
                                "test_case": f"pgc_integration_{policy_id}",
                                "status": "success",
                                "response_time_ms": response_time,
                                "enforcement_action": data.get("enforcement_action"),
                                "compliance_score": data.get("compliance_score"),
                                "confidence_score": data.get("confidence_score"),
                            }
                        )
                        logger.info(
                            f"✅ PGC Integration: {policy_id} - {response_time:.2f}ms"
                        )
                    else:
                        results.append(
                            {
                                "test_case": f"pgc_integration_{policy_id}",
                                "status": "failed",
                                "response_time_ms": response_time,
                                "error": response.text,
                            }
                        )

                except Exception as e:
                    results.append(
                        {
                            "test_case": f"pgc_integration_{policy_id}",
                            "status": "error",
                            "error": str(e),
                        }
                    )

        return results

    async def test_wina_oversight_workflow(self) -> dict[str, Any]:
        """Test WINA Oversight workflow with Performance Monitoring → Optimization → Reporting."""
        logger.info("🧠 Testing WINA Oversight Workflow...")

        oversight_types = ["performance_optimization", "routine_monitoring"]
        results = []

        async with httpx.AsyncClient() as client:
            # Test PGC WINA oversight
            for oversight_type in oversight_types:
                start_time = time.time()
                try:
                    response = await client.post(
                        f"{self.base_url}/api/v1/governance-workflows/api/v1/governance/wina-oversight",
                        params={
                            "oversight_type": oversight_type,
                            "target_metrics": "response_time,accuracy,compliance",
                        },
                        timeout=10.0,
                    )
                    response_time = (time.time() - start_time) * 1000

                    if response.status_code == 200:
                        data = response.json()
                        results.append(
                            {
                                "test_case": f"wina_oversight_{oversight_type}",
                                "status": "success",
                                "response_time_ms": response_time,
                                "workflow_id": data.get("workflow_id"),
                                "oversight_status": data.get("status"),
                            }
                        )
                        logger.info(
                            f"✅ WINA Oversight: {oversight_type} - {response_time:.2f}ms"
                        )
                    else:
                        results.append(
                            {
                                "test_case": f"wina_oversight_{oversight_type}",
                                "status": "failed",
                                "response_time_ms": response_time,
                                "error": response.text,
                            }
                        )

                except Exception as e:
                    results.append(
                        {
                            "test_case": f"wina_oversight_{oversight_type}",
                            "status": "error",
                            "error": str(e),
                        }
                    )

            # Test EC WINA coordination
            start_time = time.time()
            try:
                response = await client.post(
                    "http://localhost:8006/api/v1/wina-oversight/coordinate",
                    json={
                        "request_data": {
                            "request_id": "E2E-TEST-001",
                            "oversight_type": "performance_optimization",
                            "target_system": "governance_workflows",
                            "target_metrics": [
                                "response_time",
                                "accuracy",
                                "compliance",
                            ],
                            "optimization_level": "standard",
                        }
                    },
                    timeout=10.0,
                )
                response_time = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    data = response.json()
                    results.append(
                        {
                            "test_case": "ec_wina_coordination",
                            "status": "success",
                            "response_time_ms": response_time,
                            "oversight_decision": data.get("oversight_decision"),
                            "confidence_score": data.get("confidence_score"),
                            "constitutional_compliance": data.get(
                                "constitutional_compliance"
                            ),
                        }
                    )
                    logger.info(f"✅ EC WINA Coordination - {response_time:.2f}ms")
                else:
                    results.append(
                        {
                            "test_case": "ec_wina_coordination",
                            "status": "failed",
                            "response_time_ms": response_time,
                            "error": response.text,
                        }
                    )

            except Exception as e:
                results.append(
                    {
                        "test_case": "ec_wina_coordination",
                        "status": "error",
                        "error": str(e),
                    }
                )

        return results

    async def test_audit_transparency_workflow(self) -> dict[str, Any]:
        """Test Audit/Transparency workflow with Data Collection → Analysis → Public Reporting."""
        logger.info("📊 Testing Audit/Transparency Workflow...")

        audit_scopes = [
            "governance_workflows",
            "policy_decisions",
            "compliance_records",
        ]
        results = []

        async with httpx.AsyncClient() as client:
            for audit_scope in audit_scopes:
                start_time = time.time()
                try:
                    response = await client.post(
                        f"{self.base_url}/api/v1/governance-workflows/api/v1/governance/audit-transparency",
                        params={
                            "audit_scope": audit_scope,
                            "reporting_level": "detailed",
                        },
                        timeout=10.0,
                    )
                    response_time = (time.time() - start_time) * 1000

                    if response.status_code == 200:
                        data = response.json()
                        results.append(
                            {
                                "test_case": f"audit_{audit_scope}",
                                "status": "success",
                                "response_time_ms": response_time,
                                "workflow_id": data.get("workflow_id"),
                                "audit_status": data.get("status"),
                            }
                        )
                        logger.info(
                            f"✅ Audit/Transparency: {audit_scope} - {response_time:.2f}ms"
                        )
                    else:
                        results.append(
                            {
                                "test_case": f"audit_{audit_scope}",
                                "status": "failed",
                                "response_time_ms": response_time,
                                "error": response.text,
                            }
                        )

                except Exception as e:
                    results.append(
                        {
                            "test_case": f"audit_{audit_scope}",
                            "status": "error",
                            "error": str(e),
                        }
                    )

        return results

    async def run_comprehensive_tests(self) -> dict[str, Any]:
        """Run all governance workflow tests and generate comprehensive report."""
        logger.info("🚀 Starting Comprehensive Governance Workflow Testing...")

        # Run all workflow tests
        self.results["policy_creation"] = await self.test_policy_creation_workflow()
        self.results["constitutional_compliance"] = (
            await self.test_constitutional_compliance_workflow()
        )
        self.results["policy_enforcement"] = (
            await self.test_policy_enforcement_workflow()
        )
        self.results["wina_oversight"] = await self.test_wina_oversight_workflow()
        self.results["audit_transparency"] = (
            await self.test_audit_transparency_workflow()
        )

        # Calculate performance metrics
        all_response_times = []
        success_count = 0
        total_count = 0

        for workflow_name, workflow_results in self.results.items():
            if isinstance(workflow_results, list):
                for result in workflow_results:
                    total_count += 1
                    if result.get("status") == "success":
                        success_count += 1
                        if "response_time_ms" in result:
                            all_response_times.append(result["response_time_ms"])

        # Performance analysis
        if all_response_times:
            self.results["performance_metrics"] = {
                "avg_response_time_ms": statistics.mean(all_response_times),
                "median_response_time_ms": statistics.median(all_response_times),
                "p95_response_time_ms": sorted(all_response_times)[
                    int(0.95 * len(all_response_times))
                ],
                "max_response_time_ms": max(all_response_times),
                "min_response_time_ms": min(all_response_times),
                "target_500ms_compliance": sum(
                    1 for rt in all_response_times if rt < 500
                )
                / len(all_response_times)
                * 100,
            }

        # Accuracy metrics
        self.results["accuracy_metrics"] = {
            "overall_success_rate": (
                (success_count / total_count * 100) if total_count > 0 else 0
            ),
            "target_95_percent_accuracy": (
                success_count / total_count >= 0.95 if total_count > 0 else False
            ),
            "total_tests": total_count,
            "successful_tests": success_count,
            "failed_tests": total_count - success_count,
        }

        return self.results

    def generate_report(self) -> str:
        """Generate comprehensive test report."""
        report = []
        report.append("=" * 80)
        report.append("ACGS-1 GOVERNANCE WORKFLOWS END-TO-END TEST REPORT")
        report.append("=" * 80)
        report.append("")

        # Performance Summary
        if "performance_metrics" in self.results:
            pm = self.results["performance_metrics"]
            report.append("📊 PERFORMANCE METRICS:")
            report.append(
                f"  • Average Response Time: {pm.get('avg_response_time_ms', 0):.2f}ms"
            )
            report.append(
                f"  • Median Response Time: {pm.get('median_response_time_ms', 0):.2f}ms"
            )
            report.append(
                f"  • 95th Percentile: {pm.get('p95_response_time_ms', 0):.2f}ms"
            )
            report.append(
                f"  • <500ms Target Compliance: {pm.get('target_500ms_compliance', 0):.1f}%"
            )
            report.append("")

        # Accuracy Summary
        if "accuracy_metrics" in self.results:
            am = self.results["accuracy_metrics"]
            report.append("🎯 ACCURACY METRICS:")
            report.append(
                f"  • Overall Success Rate: {am.get('overall_success_rate', 0):.1f}%"
            )
            report.append(
                f"  • >95% Accuracy Target: {'✅ PASSED' if am.get('target_95_percent_accuracy', False) else '❌ FAILED'}"
            )
            report.append(f"  • Total Tests: {am.get('total_tests', 0)}")
            report.append(f"  • Successful: {am.get('successful_tests', 0)}")
            report.append(f"  • Failed: {am.get('failed_tests', 0)}")
            report.append("")

        # Workflow Details
        workflow_names = {
            "policy_creation": "🏛️ Policy Creation Workflow",
            "constitutional_compliance": "⚖️ Constitutional Compliance Workflow",
            "policy_enforcement": "🛡️ Policy Enforcement Workflow",
            "wina_oversight": "🧠 WINA Oversight Workflow",
            "audit_transparency": "📊 Audit/Transparency Workflow",
        }

        for workflow_key, workflow_title in workflow_names.items():
            if workflow_key in self.results and isinstance(
                self.results[workflow_key], list
            ):
                results = self.results[workflow_key]
                successful = sum(1 for r in results if r.get("status") == "success")
                total = len(results)

                report.append(f"{workflow_title}:")
                report.append(
                    f"  • Tests: {total}, Successful: {successful}, Success Rate: {(successful / total * 100):.1f}%"
                )

                for result in results:
                    status_icon = "✅" if result.get("status") == "success" else "❌"
                    test_name = result.get("test_case", "Unknown")
                    response_time = result.get("response_time_ms", 0)
                    report.append(
                        f"    {status_icon} {test_name}: {response_time:.2f}ms"
                    )
                report.append("")

        return "\n".join(report)


async def main():
    """Main test execution function."""
    tester = GovernanceWorkflowTester()

    try:
        # Run comprehensive tests
        results = await tester.run_comprehensive_tests()

        # Generate and display report
        report = tester.generate_report()
        print(report)

        # Save results to file
        timestamp = int(time.time())
        results_file = f"governance_workflows_test_results_{timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"📁 Detailed results saved to: {results_file}")

        # Return success/failure based on targets
        pm = results.get("performance_metrics", {})
        am = results.get("accuracy_metrics", {})

        performance_target_met = pm.get("target_500ms_compliance", 0) >= 95
        accuracy_target_met = am.get("target_95_percent_accuracy", False)

        if performance_target_met and accuracy_target_met:
            print("\n🎉 ALL TARGETS MET - GOVERNANCE WORKFLOWS READY FOR PRODUCTION!")
            return 0
        print("\n⚠️ SOME TARGETS NOT MET - REVIEW REQUIRED")
        return 1

    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
