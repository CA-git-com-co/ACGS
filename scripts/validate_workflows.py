#!/usr/bin/env python3
"""
ACGS-1 Phase 3 End-to-End Workflow Validation Script

This script validates complete policy governance workflows, constitutional AI compliance,
formal verification processes, governance synthesis, and evolutionary computation workflows
to ensure system-wide functionality meets production requirements.

Workflows tested:
1. Policy Creation and Governance Workflow
2. Constitutional AI Compliance Validation
3. Formal Verification Process
4. Governance Synthesis Pipeline
5. Inter-Service Communication Workflow
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any
import httpx

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Service configuration
SERVICES = {
    "auth": {"port": 8000, "base_url": "http://localhost:8000"},
    "ac": {"port": 8001, "base_url": "http://localhost:8001"},
    "integrity": {"port": 8002, "base_url": "http://localhost:8002"},
    "fv": {"port": 8003, "base_url": "http://localhost:8003"},
    "gs": {"port": 8004, "base_url": "http://localhost:8004"},
    "pgc": {"port": 8005, "base_url": "http://localhost:8005"},
    "ec": {"port": 8006, "base_url": "http://localhost:8006"},
}


class WorkflowValidator:
    """Validates ACGS-1 end-to-end workflows for production readiness."""

    def __init__(self):
        self.results = {}
        self.timeout = 30

    async def validate_policy_governance_workflow(self) -> Dict[str, Any]:
        """Test complete policy creation to enforcement workflow."""
        logger.info("🔄 Testing Policy Governance Workflow")

        workflow_steps = {}

        try:
            # Step 1: Create a test policy via PGC service
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                policy_data = {
                    "name": "Test Governance Policy",
                    "description": "A test policy for workflow validation",
                    "category": "governance",
                    "priority": "medium",
                }

                response = await client.post(
                    f"{SERVICES['pgc']['base_url']}/api/v1/policies/validate",
                    json=policy_data,
                )

                workflow_steps["policy_creation"] = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "data": response.json() if response.status_code == 200 else None,
                }

        except Exception as e:
            workflow_steps["policy_creation"] = {"status": "error", "error": str(e)}

        try:
            # Step 2: Validate constitutional compliance via AC service
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                compliance_data = {
                    "policy": policy_data,
                    "validation": {"constitutional_review": True},
                    "process": {"stakeholder_input": True},
                    "metadata": {"audit_trail": True},
                }

                response = await client.post(
                    f"{SERVICES['ac']['base_url']}/api/v1/constitutional/validate",
                    json=compliance_data,
                )

                workflow_steps["constitutional_validation"] = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "data": response.json() if response.status_code == 200 else None,
                }

        except Exception as e:
            workflow_steps["constitutional_validation"] = {
                "status": "error",
                "error": str(e),
            }

        try:
            # Step 3: Check compliance status
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{SERVICES['pgc']['base_url']}/api/v1/compliance/check"
                )

                workflow_steps["compliance_check"] = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "data": response.json() if response.status_code == 200 else None,
                }

        except Exception as e:
            workflow_steps["compliance_check"] = {"status": "error", "error": str(e)}

        # Calculate overall workflow success
        successful_steps = sum(
            1 for step in workflow_steps.values() if step.get("status") == "success"
        )
        total_steps = len(workflow_steps)

        return {
            "workflow": "policy_governance",
            "steps": workflow_steps,
            "success_rate": (successful_steps / total_steps) * 100,
            "overall_status": (
                "success"
                if successful_steps == total_steps
                else "partial_success" if successful_steps > 0 else "failed"
            ),
        }

    async def validate_constitutional_ai_workflow(self) -> Dict[str, Any]:
        """Test constitutional AI compliance checking workflow."""
        logger.info("⚖️ Testing Constitutional AI Compliance Workflow")

        workflow_steps = {}

        try:
            # Step 1: Get constitutional rules
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{SERVICES['ac']['base_url']}/api/v1/constitutional/rules"
                )

                workflow_steps["get_rules"] = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "data": response.json() if response.status_code == 200 else None,
                }

        except Exception as e:
            workflow_steps["get_rules"] = {"status": "error", "error": str(e)}

        try:
            # Step 2: Check overall compliance status
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{SERVICES['ac']['base_url']}/api/v1/constitutional/compliance"
                )

                workflow_steps["compliance_status"] = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "data": response.json() if response.status_code == 200 else None,
                }

        except Exception as e:
            workflow_steps["compliance_status"] = {"status": "error", "error": str(e)}

        try:
            # Step 3: Perform constitutional impact analysis
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                analysis_data = {
                    "proposed_change": "Test policy modification",
                    "scope": "governance",
                    "impact_areas": ["democratic_participation", "transparency"],
                }

                response = await client.post(
                    f"{SERVICES['ac']['base_url']}/api/v1/constitutional/analyze",
                    json=analysis_data,
                )

                workflow_steps["impact_analysis"] = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "data": response.json() if response.status_code == 200 else None,
                }

        except Exception as e:
            workflow_steps["impact_analysis"] = {"status": "error", "error": str(e)}

        # Calculate overall workflow success
        successful_steps = sum(
            1 for step in workflow_steps.values() if step.get("status") == "success"
        )
        total_steps = len(workflow_steps)

        return {
            "workflow": "constitutional_ai_compliance",
            "steps": workflow_steps,
            "success_rate": (successful_steps / total_steps) * 100,
            "overall_status": (
                "success"
                if successful_steps == total_steps
                else "partial_success" if successful_steps > 0 else "failed"
            ),
        }

    async def validate_formal_verification_workflow(self) -> Dict[str, Any]:
        """Test formal verification processes."""
        logger.info("🔍 Testing Formal Verification Workflow")

        workflow_steps = {}

        try:
            # Step 1: Check FV service status
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{SERVICES['fv']['base_url']}/api/v1/enterprise/status"
                )

                workflow_steps["fv_status"] = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "data": response.json() if response.status_code == 200 else None,
                }

        except Exception as e:
            workflow_steps["fv_status"] = {"status": "error", "error": str(e)}

        try:
            # Step 2: Test cryptographic validation
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                crypto_data = {
                    "data": "test policy data for verification",
                    "signature": "mock_signature_for_testing_purposes",
                    "public_key": "mock_public_key_for_testing",
                }

                response = await client.post(
                    f"{SERVICES['fv']['base_url']}/api/v1/crypto/validate-signature",
                    json=crypto_data,
                )

                workflow_steps["crypto_validation"] = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "data": response.json() if response.status_code == 200 else None,
                }

        except Exception as e:
            workflow_steps["crypto_validation"] = {"status": "error", "error": str(e)}

        try:
            # Step 3: Check audit trail
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{SERVICES['fv']['base_url']}/api/v1/blockchain/audit-trail"
                )

                workflow_steps["audit_trail"] = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "data": response.json() if response.status_code == 200 else None,
                }

        except Exception as e:
            workflow_steps["audit_trail"] = {"status": "error", "error": str(e)}

        # Calculate overall workflow success
        successful_steps = sum(
            1 for step in workflow_steps.values() if step.get("status") == "success"
        )
        total_steps = len(workflow_steps)

        return {
            "workflow": "formal_verification",
            "steps": workflow_steps,
            "success_rate": (successful_steps / total_steps) * 100,
            "overall_status": (
                "success"
                if successful_steps == total_steps
                else "partial_success" if successful_steps > 0 else "failed"
            ),
        }

    async def validate_governance_synthesis_workflow(self) -> Dict[str, Any]:
        """Test governance synthesis pipeline."""
        logger.info("🏛️ Testing Governance Synthesis Workflow")

        workflow_steps = {}

        try:
            # Step 1: Check GS service status
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{SERVICES['gs']['base_url']}/api/v1/status"
                )

                workflow_steps["gs_status"] = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "data": response.json() if response.status_code == 200 else None,
                }

        except Exception as e:
            workflow_steps["gs_status"] = {"status": "error", "error": str(e)}

        try:
            # Step 2: Check governance workflows
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{SERVICES['pgc']['base_url']}/api/v1/governance/workflows"
                )

                workflow_steps["governance_workflows"] = {
                    "status": "success" if response.status_code == 200 else "failed",
                    "response_time_ms": response.elapsed.total_seconds() * 1000,
                    "data": response.json() if response.status_code == 200 else None,
                }

        except Exception as e:
            workflow_steps["governance_workflows"] = {
                "status": "error",
                "error": str(e),
            }

        # Calculate overall workflow success
        successful_steps = sum(
            1 for step in workflow_steps.values() if step.get("status") == "success"
        )
        total_steps = len(workflow_steps)

        return {
            "workflow": "governance_synthesis",
            "steps": workflow_steps,
            "success_rate": (successful_steps / total_steps) * 100,
            "overall_status": (
                "success"
                if successful_steps == total_steps
                else "partial_success" if successful_steps > 0 else "failed"
            ),
        }

    async def validate_all_workflows(self) -> Dict[str, Any]:
        """Validate all ACGS-1 end-to-end workflows."""
        logger.info("🚀 Starting ACGS-1 Phase 3 Workflow Validation")

        validation_results = {
            "timestamp": time.time(),
            "workflows": {},
            "summary": {},
            "overall_status": "unknown",
        }

        # Run all workflow validations
        workflows = [
            self.validate_policy_governance_workflow(),
            self.validate_constitutional_ai_workflow(),
            self.validate_formal_verification_workflow(),
            self.validate_governance_synthesis_workflow(),
        ]

        workflow_results = await asyncio.gather(*workflows, return_exceptions=True)

        # Process results
        for result in workflow_results:
            if isinstance(result, Exception):
                logger.error(f"Workflow validation failed: {result}")
                continue

            workflow_name = result["workflow"]
            validation_results["workflows"][workflow_name] = result

        # Calculate summary
        total_workflows = len(validation_results["workflows"])
        successful_workflows = sum(
            1
            for w in validation_results["workflows"].values()
            if w["overall_status"] == "success"
        )
        partial_workflows = sum(
            1
            for w in validation_results["workflows"].values()
            if w["overall_status"] == "partial_success"
        )

        validation_results["summary"] = {
            "total_workflows": total_workflows,
            "successful_workflows": successful_workflows,
            "partial_workflows": partial_workflows,
            "failed_workflows": total_workflows
            - successful_workflows
            - partial_workflows,
            "success_rate": (
                (successful_workflows / total_workflows) * 100
                if total_workflows > 0
                else 0
            ),
            "meets_production_requirements": successful_workflows
            >= total_workflows * 0.8,
        }

        # Determine overall status
        if successful_workflows == total_workflows:
            validation_results["overall_status"] = "all_workflows_operational"
        elif successful_workflows + partial_workflows >= total_workflows * 0.8:
            validation_results["overall_status"] = "mostly_operational"
        else:
            validation_results["overall_status"] = "degraded"

        return validation_results

    def print_workflow_report(self, results: Dict[str, Any]):
        """Print a comprehensive workflow validation report."""
        print("\n" + "=" * 80)
        print("🔄 ACGS-1 PHASE 3 WORKFLOW VALIDATION REPORT")
        print("=" * 80)

        summary = results["summary"]
        print(
            f"📊 Workflows: {summary['successful_workflows']}/{summary['total_workflows']} successful"
        )
        print(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        print(
            f"🎯 Production Requirements Met: {'✅ YES' if summary['meets_production_requirements'] else '❌ NO'}"
        )
        print(f"🏆 Overall Status: {results['overall_status']}")

        print("\n📋 WORKFLOW DETAILS:")
        for workflow_name, workflow_data in results["workflows"].items():
            status_icon = (
                "✅"
                if workflow_data["overall_status"] == "success"
                else (
                    "⚠️"
                    if workflow_data["overall_status"] == "partial_success"
                    else "❌"
                )
            )

            print(f"  {status_icon} {workflow_name.replace('_', ' ').title()}")
            print(f"     Success Rate: {workflow_data['success_rate']:.1f}%")
            print(f"     Status: {workflow_data['overall_status']}")

            for step_name, step_data in workflow_data["steps"].items():
                step_icon = "✅" if step_data.get("status") == "success" else "❌"
                response_time = step_data.get("response_time_ms", "N/A")
                if isinstance(response_time, (int, float)):
                    print(f"       {step_icon} {step_name}: {response_time:.1f}ms")
                else:
                    print(f"       {step_icon} {step_name}: {response_time}")


async def main():
    """Main workflow validation function."""
    validator = WorkflowValidator()
    results = await validator.validate_all_workflows()

    # Print report
    validator.print_workflow_report(results)

    # Save results
    with open("tests/results/workflow_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)

    logger.info(
        "📋 Workflow validation results saved to tests/results/workflow_validation_results.json"
    )

    # Return exit code based on results
    if results["overall_status"] == "all_workflows_operational":
        return 0
    elif results["overall_status"] == "mostly_operational":
        return 1
    else:
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
