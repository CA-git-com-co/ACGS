#!/usr/bin/env python3
"""
Comprehensive validation of all 5 governance workflows.
"""

import asyncio
import aiohttp
import time
import json
from typing import Dict, List, Any


class GovernanceWorkflowValidator:
    def __init__(self):
        self.base_urls = {
            "gs_service": "http://localhost:8004",
            "pgc_service": "http://localhost:8005",
        }
        self.results = {}

    async def validate_workflow(
        self,
        session: aiohttp.ClientSession,
        workflow_name: str,
        endpoint: str,
        method: str = "GET",
        data: Dict = None,
    ) -> Dict[str, Any]:
        """Validate a single governance workflow."""
        start_time = time.time()

        try:
            if method.upper() == "POST":
                async with session.post(endpoint, json=data) as response:
                    response_time = (time.time() - start_time) * 1000  # Convert to ms
                    response_data = await response.json()

                    return {
                        "workflow": workflow_name,
                        "status": "success" if response.status == 200 else "failed",
                        "response_time_ms": round(response_time, 2),
                        "http_status": response.status,
                        "data": response_data,
                        "meets_performance_target": response_time < 500,
                    }
            else:
                async with session.get(endpoint) as response:
                    response_time = (time.time() - start_time) * 1000  # Convert to ms
                    response_data = await response.json()

                    return {
                        "workflow": workflow_name,
                        "status": "success" if response.status == 200 else "failed",
                        "response_time_ms": round(response_time, 2),
                        "http_status": response.status,
                        "data": response_data,
                        "meets_performance_target": response_time < 500,
                    }

        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            return {
                "workflow": workflow_name,
                "status": "error",
                "response_time_ms": round(response_time, 2),
                "error": str(e),
                "meets_performance_target": False,
            }

    async def validate_all_workflows(self):
        """Validate all 5 governance workflows."""

        workflows = [
            {
                "name": "Policy Creation",
                "endpoint": f"{self.base_urls['pgc_service']}/api/v1/governance/workflows",
                "method": "POST",
                "data": {
                    "workflow_type": "policy_creation",
                    "title": "Test Policy Creation Workflow",
                    "description": "Validation test for policy creation workflow",
                },
            },
            {
                "name": "Constitutional Compliance",
                "endpoint": f"{self.base_urls['gs_service']}/api/v1/constitutional/validate",
                "method": "GET",
            },
            {
                "name": "Policy Enforcement",
                "endpoint": f"{self.base_urls['pgc_service']}/api/v1/governance/workflows",
                "method": "POST",
                "data": {
                    "workflow_type": "policy_enforcement",
                    "title": "Test Policy Enforcement Workflow",
                    "description": "Validation test for policy enforcement workflow",
                },
            },
            {
                "name": "WINA Oversight",
                "endpoint": f"{self.base_urls['gs_service']}/api/v1/performance",
                "method": "GET",
            },
            {
                "name": "Audit/Transparency",
                "endpoint": f"{self.base_urls['pgc_service']}/api/v1/workflows/audit-transparency",
                "method": "POST",
                "data": {},
            },
        ]

        async with aiohttp.ClientSession() as session:
            print("🔍 Validating Governance Workflows...")
            print("=" * 50)

            results = []
            for workflow in workflows:
                print(f"Testing {workflow['name']}...")
                result = await self.validate_workflow(
                    session,
                    workflow["name"],
                    workflow["endpoint"],
                    workflow.get("method", "GET"),
                    workflow.get("data"),
                )
                results.append(result)

                # Print immediate result
                status_icon = "✅" if result["status"] == "success" else "❌"
                perf_icon = (
                    "🚀" if result.get("meets_performance_target", False) else "⚠️"
                )
                print(f"  {status_icon} Status: {result['status']}")
                print(f"  {perf_icon} Response Time: {result['response_time_ms']}ms")
                print()

            return results

    def generate_report(self, results: List[Dict[str, Any]]):
        """Generate a comprehensive validation report."""

        print("📊 GOVERNANCE WORKFLOWS VALIDATION REPORT")
        print("=" * 60)

        successful_workflows = sum(1 for r in results if r["status"] == "success")
        total_workflows = len(results)
        avg_response_time = sum(r["response_time_ms"] for r in results) / len(results)
        workflows_meeting_perf_target = sum(
            1 for r in results if r.get("meets_performance_target", False)
        )

        print(
            f"📈 Overall Success Rate: {successful_workflows}/{total_workflows} ({(successful_workflows/total_workflows)*100:.1f}%)"
        )
        print(f"⚡ Average Response Time: {avg_response_time:.2f}ms")
        print(
            f"🎯 Performance Target Met: {workflows_meeting_perf_target}/{total_workflows} workflows (<500ms)"
        )
        print()

        print("📋 Individual Workflow Results:")
        print("-" * 40)

        for result in results:
            status_icon = "✅" if result["status"] == "success" else "❌"
            perf_icon = "🚀" if result.get("meets_performance_target", False) else "⚠️"

            print(f"{status_icon} {result['workflow']}")
            print(f"   Response Time: {result['response_time_ms']}ms {perf_icon}")
            print(f"   Status: {result['status']}")

            if result["status"] == "error":
                print(f"   Error: {result.get('error', 'Unknown error')}")
            elif result["status"] == "success":
                print(f"   HTTP Status: {result['http_status']}")
            print()

        # Overall assessment
        print("🎯 ASSESSMENT:")
        if (
            successful_workflows == total_workflows
            and workflows_meeting_perf_target == total_workflows
        ):
            print("✅ ALL GOVERNANCE WORKFLOWS OPERATIONAL AND PERFORMANT")
        elif successful_workflows == total_workflows:
            print("⚠️ All workflows functional but some performance issues")
        elif successful_workflows > 0:
            print("⚠️ Partial functionality - some workflows need attention")
        else:
            print("❌ CRITICAL: No governance workflows are functional")

        return {
            "success_rate": (successful_workflows / total_workflows) * 100,
            "avg_response_time": avg_response_time,
            "performance_compliance": (workflows_meeting_perf_target / total_workflows)
            * 100,
            "all_functional": successful_workflows == total_workflows,
            "all_performant": workflows_meeting_perf_target == total_workflows,
        }


async def main():
    """Main validation function."""
    validator = GovernanceWorkflowValidator()
    results = await validator.validate_all_workflows()
    summary = validator.generate_report(results)

    # Save detailed results
    with open("governance_workflows_validation.json", "w") as f:
        json.dump(
            {"timestamp": time.time(), "summary": summary, "detailed_results": results},
            f,
            indent=2,
        )

    print(f"📄 Detailed results saved to: governance_workflows_validation.json")

    return summary["all_functional"]


if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
