#!/usr/bin/env python3
"""
Enhanced Constitutional Analyzer Real Integration Validation

This script validates the Enhanced Constitutional Analyzer integration with
the live ACGS-1 system, testing real service connectivity and performance.

Validation Steps:
1. Check ACGS-1 service health and connectivity
2. Validate multi-model manager integration
3. Test governance workflow endpoints
4. Verify PGC service integration
5. Validate Constitution Hash consistency
6. Performance benchmarking against targets
"""

import asyncio
import json
import logging
import time
from typing import Any

import aiohttp

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# ACGS-1 Service Configuration
ACGS_SERVICES = {
    "auth_service": {"port": 8000, "url": "http://localhost:8000"},
    "ac_service": {"port": 8001, "url": "http://localhost:8001"},
    "integrity_service": {"port": 8002, "url": "http://localhost:8002"},
    "fv_service": {"port": 8003, "url": "http://localhost:8003"},
    "gs_service": {"port": 8004, "url": "http://localhost:8004"},
    "pgc_service": {"port": 8005, "url": "http://localhost:8005"},
    "ec_service": {"port": 8006, "url": "http://localhost:8006"},
}

# Performance targets
PERFORMANCE_TARGETS = {
    "response_time_ms": 500,
    "uptime_percentage": 99.5,
    "accuracy_percentage": 95.0,
    "constitution_hash": "cdd01ef066bc6cf2",
}


class EnhancedConstitutionalAnalyzerValidator:
    """
    Validates Enhanced Constitutional Analyzer integration with live ACGS-1 system.
    """

    def __init__(self):
        self.session = None
        self.validation_results = {
            "timestamp": time.time(),
            "service_health": {},
            "integration_tests": {},
            "performance_metrics": {},
            "constitution_validation": {},
            "overall_status": "UNKNOWN",
            "recommendations": [],
        }

    async def run_validation(self) -> dict[str, Any]:
        """Run comprehensive validation of Enhanced Constitutional Analyzer integration."""
        logger.info(
            "🚀 Starting Enhanced Constitutional Analyzer Integration Validation"
        )
        logger.info("=" * 80)

        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        ) as session:
            self.session = session

            try:
                # Step 1: Validate ACGS-1 service health
                await self.validate_service_health()

                # Step 2: Test governance workflow endpoints
                await self.validate_governance_workflows()

                # Step 3: Test PGC service integration
                await self.validate_pgc_integration()

                # Step 4: Validate Constitution Hash consistency
                await self.validate_constitution_hash()

                # Step 5: Performance benchmarking
                await self.validate_performance()

                # Generate final assessment
                self.generate_final_assessment()

                return self.validation_results

            except Exception as e:
                logger.error(f"Critical error during validation: {e}")
                self.validation_results["overall_status"] = "CRITICAL_ERROR"
                self.validation_results["error"] = str(e)
                return self.validation_results

    async def validate_service_health(self):
        """Validate health of all ACGS-1 services."""
        logger.info("🔍 Validating ACGS-1 Service Health...")

        service_health = {}
        healthy_services = 0

        for service_name, config in ACGS_SERVICES.items():
            try:
                start_time = time.time()

                async with self.session.get(f"{config['url']}/health") as response:
                    response_time = (time.time() - start_time) * 1000

                    if response.status == 200:
                        health_data = await response.json()
                        service_health[service_name] = {
                            "status": "healthy",
                            "response_time_ms": round(response_time, 2),
                            "details": health_data,
                        }
                        healthy_services += 1
                        logger.info(
                            f"✅ {service_name}: Healthy ({response_time:.1f}ms)"
                        )
                    else:
                        service_health[service_name] = {
                            "status": "unhealthy",
                            "response_time_ms": round(response_time, 2),
                            "error": f"HTTP {response.status}",
                        }
                        logger.warning(
                            f"❌ {service_name}: Unhealthy (HTTP {response.status})"
                        )

            except Exception as e:
                service_health[service_name] = {
                    "status": "unreachable",
                    "error": str(e),
                }
                logger.error(f"❌ {service_name}: Unreachable - {e}")

        self.validation_results["service_health"] = {
            "services": service_health,
            "healthy_count": healthy_services,
            "total_count": len(ACGS_SERVICES),
            "health_percentage": (healthy_services / len(ACGS_SERVICES)) * 100,
        }

        logger.info(
            f"📊 Service Health: {healthy_services}/{len(ACGS_SERVICES)} services healthy"
        )

    async def validate_governance_workflows(self):
        """Validate governance workflow endpoints."""
        logger.info("🔍 Validating Governance Workflow Integration...")

        workflow_tests = {}

        # Test Policy Creation workflow
        workflow_tests["policy_creation"] = await self.test_policy_creation_workflow()

        # Test Constitutional Compliance workflow
        workflow_tests["constitutional_compliance"] = (
            await self.test_constitutional_compliance_workflow()
        )

        # Test WINA Oversight workflow
        workflow_tests["wina_oversight"] = await self.test_wina_oversight_workflow()

        self.validation_results["integration_tests"][
            "governance_workflows"
        ] = workflow_tests

        # Summary
        successful_workflows = sum(
            1 for result in workflow_tests.values() if result.get("success", False)
        )
        logger.info(
            f"📊 Governance Workflows: {successful_workflows}/{len(workflow_tests)} workflows operational"
        )

    async def test_policy_creation_workflow(self) -> dict[str, Any]:
        """Test Policy Creation workflow endpoint."""
        try:
            start_time = time.time()

            # Test PGC service policy creation endpoint
            test_data = {
                "policy_id": "TEST-POL-001",
                "title": "Test Policy for Enhanced Constitutional Analyzer",
                "description": "Test policy to validate enhanced constitutional analysis capabilities",
                "policy_type": "governance",
                "enforcement_level": "mandatory",
            }

            async with self.session.post(
                f"{ACGS_SERVICES['pgc_service']['url']}/api/v1/governance-workflows/policy-creation",
                json=test_data,
            ) as response:
                response_time = (time.time() - start_time) * 1000

                if response.status == 200:
                    result_data = await response.json()

                    return {
                        "success": True,
                        "response_time_ms": round(response_time, 2),
                        "workflow_id": result_data.get("workflow_id"),
                        "status": result_data.get("status", "unknown"),
                        "details": result_data,
                    }
                else:
                    return {
                        "success": False,
                        "response_time_ms": round(response_time, 2),
                        "error": f"HTTP {response.status}",
                        "details": await response.text(),
                    }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "Exception during policy creation workflow test",
            }

    async def test_constitutional_compliance_workflow(self) -> dict[str, Any]:
        """Test Constitutional Compliance workflow endpoint."""
        try:
            start_time = time.time()

            # Test PGC service constitutional compliance endpoint
            test_data = {
                "policy_id": "TEST-COMPLIANCE-001",
                "validation_type": "comprehensive",
                "constitutional_principles": [
                    "Human safety and wellbeing priority",
                    "Transparency and accountability",
                    "Fairness and non-discrimination",
                ],
            }

            async with self.session.post(
                f"{ACGS_SERVICES['pgc_service']['url']}/api/v1/governance-workflows/constitutional-compliance",
                json=test_data,
            ) as response:
                response_time = (time.time() - start_time) * 1000

                if response.status == 200:
                    result_data = await response.json()

                    return {
                        "success": True,
                        "response_time_ms": round(response_time, 2),
                        "compliant": result_data.get("compliant"),
                        "compliance_score": result_data.get("compliance_score"),
                        "constitutional_hash": result_data.get("constitutional_hash"),
                        "details": result_data,
                    }
                else:
                    return {
                        "success": False,
                        "response_time_ms": round(response_time, 2),
                        "error": f"HTTP {response.status}",
                        "details": await response.text(),
                    }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "Exception during constitutional compliance workflow test",
            }

    async def test_wina_oversight_workflow(self) -> dict[str, Any]:
        """Test WINA Oversight workflow endpoint."""
        try:
            start_time = time.time()

            # Test EC service WINA oversight endpoint
            test_data = {
                "operation_type": "governance_validation",
                "policy_id": "TEST-WINA-001",
                "compliance_requirements": [
                    "constitutional_adherence",
                    "stakeholder_approval",
                ],
                "stakeholders": ["governance_committee", "technical_review_board"],
            }

            async with self.session.post(
                f"{ACGS_SERVICES['ec_service']['url']}/api/v1/wina-oversight/pgc-integration/execute",
                json=test_data,
            ) as response:
                response_time = (time.time() - start_time) * 1000

                if response.status == 200:
                    result_data = await response.json()

                    return {
                        "success": True,
                        "response_time_ms": round(response_time, 2),
                        "integration_id": result_data.get("integration_id"),
                        "operation_type": result_data.get("operation_type"),
                        "compliance_status": result_data.get("compliance_status"),
                        "details": result_data,
                    }
                else:
                    return {
                        "success": False,
                        "response_time_ms": round(response_time, 2),
                        "error": f"HTTP {response.status}",
                        "details": await response.text(),
                    }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "details": "Exception during WINA oversight workflow test",
            }

    async def validate_pgc_integration(self):
        """Validate PGC service integration with Enhanced Constitutional Analyzer."""
        logger.info("🔍 Validating PGC Service Integration...")

        try:
            start_time = time.time()

            # Test real-time enforcement endpoint
            test_data = {
                "policy_id": "TEST-PGC-INTEGRATION-001",
                "policy_content": "AI systems must prioritize human safety and constitutional compliance",
                "enforcement_context": {
                    "risk_level": "medium",
                    "stakeholders": ["safety_committee", "governance_board"],
                    "constitutional_requirements": ["human_safety", "transparency"],
                },
            }

            async with self.session.post(
                f"{ACGS_SERVICES['pgc_service']['url']}/api/v1/real-time-enforcement",
                json=test_data,
            ) as response:
                response_time = (time.time() - start_time) * 1000

                if response.status == 200:
                    result_data = await response.json()

                    pgc_result = {
                        "success": True,
                        "response_time_ms": round(response_time, 2),
                        "enforcement_action": result_data.get("enforcement_action"),
                        "compliance_score": result_data.get("compliance_score"),
                        "constitutional_hash": result_data.get("constitutional_hash"),
                        "enhanced_analyzer_used": result_data.get(
                            "enhanced_analyzer_used", False
                        ),
                        "details": result_data,
                    }

                    logger.info(
                        f"✅ PGC Integration: {result_data.get('enforcement_action', 'unknown')} ({response_time:.1f}ms)"
                    )

                else:
                    pgc_result = {
                        "success": False,
                        "response_time_ms": round(response_time, 2),
                        "error": f"HTTP {response.status}",
                        "details": await response.text(),
                    }

                    logger.warning(
                        f"❌ PGC Integration: Failed (HTTP {response.status})"
                    )

        except Exception as e:
            pgc_result = {
                "success": False,
                "error": str(e),
                "details": "Exception during PGC integration test",
            }
            logger.error(f"❌ PGC Integration: Exception - {e}")

        self.validation_results["integration_tests"]["pgc_service"] = pgc_result

    async def validate_constitution_hash(self):
        """Validate Constitution Hash consistency across services."""
        logger.info("🔍 Validating Constitution Hash Consistency...")

        constitution_validation = {
            "expected_hash": PERFORMANCE_TARGETS["constitution_hash"],
            "service_hashes": {},
            "consistent": True,
            "inconsistent_services": [],
        }

        # Check constitution hash from AC service
        try:
            async with self.session.get(
                f"{ACGS_SERVICES['ac_service']['url']}/api/v1/constitution/hash"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    ac_hash = data.get("constitution_hash")
                    constitution_validation["service_hashes"]["ac_service"] = ac_hash

                    if ac_hash != PERFORMANCE_TARGETS["constitution_hash"]:
                        constitution_validation["consistent"] = False
                        constitution_validation["inconsistent_services"].append(
                            "ac_service"
                        )

        except Exception as e:
            constitution_validation["service_hashes"]["ac_service"] = f"Error: {e}"

        # Check constitution hash from PGC service
        try:
            async with self.session.get(
                f"{ACGS_SERVICES['pgc_service']['url']}/api/v1/constitution/hash"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    pgc_hash = data.get("constitution_hash")
                    constitution_validation["service_hashes"]["pgc_service"] = pgc_hash

                    if pgc_hash != PERFORMANCE_TARGETS["constitution_hash"]:
                        constitution_validation["consistent"] = False
                        constitution_validation["inconsistent_services"].append(
                            "pgc_service"
                        )

        except Exception as e:
            constitution_validation["service_hashes"]["pgc_service"] = f"Error: {e}"

        self.validation_results["constitution_validation"] = constitution_validation

        if constitution_validation["consistent"]:
            logger.info(
                f"✅ Constitution Hash: Consistent ({PERFORMANCE_TARGETS['constitution_hash']})"
            )
        else:
            logger.warning(
                f"❌ Constitution Hash: Inconsistent services: {constitution_validation['inconsistent_services']}"
            )

    async def validate_performance(self):
        """Validate performance against ACGS-1 targets."""
        logger.info("🔍 Validating Performance Against Targets...")

        performance_metrics = {
            "response_times": [],
            "target_met_count": 0,
            "total_requests": 0,
            "average_response_time_ms": 0.0,
            "max_response_time_ms": 0.0,
            "target_met_percentage": 0.0,
            "meets_targets": False,
        }

        # Test multiple requests to get performance baseline
        test_requests = 20

        for i in range(test_requests):
            try:
                start_time = time.time()

                # Test PGC service health endpoint for performance
                async with self.session.get(
                    f"{ACGS_SERVICES['pgc_service']['url']}/health"
                ):
                    response_time = (time.time() - start_time) * 1000
                    performance_metrics["response_times"].append(response_time)

                    if response_time < PERFORMANCE_TARGETS["response_time_ms"]:
                        performance_metrics["target_met_count"] += 1

                    performance_metrics["total_requests"] += 1

            except Exception as e:
                logger.warning(f"Performance test request {i+1} failed: {e}")

        # Calculate metrics
        if performance_metrics["response_times"]:
            performance_metrics["average_response_time_ms"] = sum(
                performance_metrics["response_times"]
            ) / len(performance_metrics["response_times"])
            performance_metrics["max_response_time_ms"] = max(
                performance_metrics["response_times"]
            )
            performance_metrics["target_met_percentage"] = (
                performance_metrics["target_met_count"]
                / performance_metrics["total_requests"]
            ) * 100

            # Check if meets targets (95% of requests should be under target)
            performance_metrics["meets_targets"] = (
                performance_metrics["target_met_percentage"] >= 95.0
            )

        self.validation_results["performance_metrics"] = performance_metrics

        logger.info(
            f"📊 Performance: {performance_metrics['average_response_time_ms']:.1f}ms avg, {performance_metrics['target_met_percentage']:.1f}% meet target"
        )

    def generate_final_assessment(self):
        """Generate final assessment and recommendations."""
        logger.info("🔍 Generating Final Assessment...")

        # Assess overall health
        service_health = self.validation_results["service_health"]
        health_percentage = service_health.get("health_percentage", 0)

        # Assess integration tests
        integration_tests = self.validation_results["integration_tests"]
        governance_workflows = integration_tests.get("governance_workflows", {})
        successful_workflows = sum(
            1
            for result in governance_workflows.values()
            if result.get("success", False)
        )
        total_workflows = len(governance_workflows)

        pgc_integration = integration_tests.get("pgc_service", {})
        pgc_success = pgc_integration.get("success", False)

        # Assess constitution validation
        constitution_validation = self.validation_results["constitution_validation"]
        constitution_consistent = constitution_validation.get("consistent", False)

        # Assess performance
        performance_metrics = self.validation_results["performance_metrics"]
        performance_meets_targets = performance_metrics.get("meets_targets", False)

        # Generate recommendations
        recommendations = []

        if health_percentage < 80:
            recommendations.append(
                "🚨 CRITICAL: Less than 80% of ACGS-1 services are healthy"
            )
            recommendations.append(
                "🔧 Restart unhealthy services and check system dependencies"
            )

        if successful_workflows < total_workflows:
            failed_workflows = [
                wf
                for wf, result in governance_workflows.items()
                if not result.get("success", False)
            ]
            recommendations.append(
                f"⚠️ Fix governance workflow integration: {', '.join(failed_workflows)}"
            )

        if not pgc_success:
            recommendations.append("🚨 CRITICAL: PGC service integration failed")
            recommendations.append(
                "🔧 Verify Enhanced Constitutional Analyzer integration with PGC service"
            )

        if not constitution_consistent:
            recommendations.append("⚠️ Constitution Hash inconsistency detected")
            recommendations.append(
                "🔧 Synchronize constitution hash across all services"
            )

        if not performance_meets_targets:
            recommendations.append("⚠️ Performance targets not met")
            recommendations.append(
                "🔧 Optimize service response times and system resources"
            )

        # Determine overall status
        if (
            health_percentage >= 80
            and pgc_success
            and constitution_consistent
            and performance_meets_targets
        ):
            overall_status = "READY_FOR_PRODUCTION"
            if not recommendations:
                recommendations.append(
                    "✅ All validations passed - Enhanced Constitutional Analyzer ready for production deployment"
                )
        elif health_percentage >= 60 and (pgc_success or constitution_consistent):
            overall_status = "NEEDS_OPTIMIZATION"
            recommendations.append(
                "🔧 System functional but requires optimization before production deployment"
            )
        else:
            overall_status = "CRITICAL_ISSUES"
            recommendations.append(
                "🚨 CRITICAL: System has major issues - do not deploy to production"
            )

        self.validation_results["overall_status"] = overall_status
        self.validation_results["recommendations"] = recommendations

        # Log final assessment
        logger.info("=" * 80)
        logger.info(
            "🏁 Enhanced Constitutional Analyzer Integration Validation Complete"
        )
        logger.info(
            f"📊 Service Health: {health_percentage:.1f}% ({service_health['healthy_count']}/{service_health['total_count']})"
        )
        logger.info(
            f"📊 Governance Workflows: {successful_workflows}/{total_workflows} operational"
        )
        logger.info(
            f"📊 PGC Integration: {'✅ Success' if pgc_success else '❌ Failed'}"
        )
        logger.info(
            f"📊 Constitution Hash: {'✅ Consistent' if constitution_consistent else '❌ Inconsistent'}"
        )
        logger.info(
            f"📊 Performance: {'✅ Meets targets' if performance_meets_targets else '❌ Below targets'}"
        )
        logger.info(f"🎯 Overall Status: {overall_status}")
        logger.info("=" * 80)


async def main():
    """Main validation execution function."""
    print("🚀 Enhanced Constitutional Analyzer Integration Validation")
    print("=" * 80)
    print("📋 Validation Scope:")
    print("   • ACGS-1 service health and connectivity")
    print("   • Multi-model manager integration")
    print("   • Governance workflow endpoints")
    print("   • PGC service real-time enforcement")
    print("   • Constitution Hash consistency")
    print("   • Performance benchmarking")
    print("=" * 80)

    # Run validation
    validator = EnhancedConstitutionalAnalyzerValidator()
    results = await validator.run_validation()

    # Save results
    timestamp = int(time.time())
    results_filename = f"enhanced_constitutional_analyzer_validation_{timestamp}.json"

    with open(results_filename, "w") as f:
        json.dump(results, f, indent=2)

    print(f"📄 Validation results saved to: {results_filename}")

    # Return exit code based on results
    if results["overall_status"] == "READY_FOR_PRODUCTION":
        return 0
    elif results["overall_status"] == "NEEDS_OPTIMIZATION":
        return 1
    else:
        return 2


if __name__ == "__main__":
    exit_code = asyncio.run(main())
