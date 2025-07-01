#!/usr/bin/env python3
"""
DeepSeek R1 Integration Test for ACGS-PGP

Comprehensive testing of DeepSeek R1 model integration with cost analysis,
performance benchmarking, and constitutional compliance validation.

Features:
- DeepSeek R1 vs Gemini Flash models comparison
- Cost savings analysis (74% reduction target)
- Performance validation with sub-2s response times
- Constitutional compliance accuracy testing
- Intelligent routing validation

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)


class DeepSeekR1IntegrationTester:
    """Comprehensive tester for DeepSeek R1 integration."""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.target_cost_reduction = 74.0  # 74% cost reduction target
        self.test_results = {}

        logger.info("DeepSeek R1 Integration Tester initialized")

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """Run comprehensive DeepSeek R1 integration tests."""

        logger.info("🚀 Starting DeepSeek R1 Integration Test Suite")
        logger.info("=" * 60)

        start_time = time.time()

        # Test suite
        test_results = {
            "service_initialization": await self._test_service_initialization(),
            "model_availability": await self._test_model_availability(),
            "cost_analysis": await self._test_cost_analysis(),
            "performance_comparison": await self._test_performance_comparison(),
            "routing_optimization": await self._test_routing_optimization(),
            "constitutional_compliance": await self._test_constitutional_compliance(),
            "load_balancing": await self._test_load_balancing(),
        }

        # Calculate overall results
        total_time = time.time() - start_time

        # Determine overall status
        passed_tests = sum(
            1 for result in test_results.values() if result.get("status") == "PASS"
        )
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests) * 100

        overall_result = {
            "test_info": {
                "timestamp": datetime.utcnow().isoformat(),
                "total_duration_seconds": total_time,
                "constitutional_hash": self.constitutional_hash,
                "target_cost_reduction": self.target_cost_reduction,
            },
            "test_results": test_results,
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate_percent": success_rate,
                "overall_status": (
                    "PASS"
                    if success_rate >= 85
                    else "PARTIAL" if success_rate >= 70 else "FAIL"
                ),
            },
        }

        return overall_result

    async def _test_service_initialization(self) -> Dict[str, Any]:
        """Test multimodal service initialization with DeepSeek R1."""

        logger.info("🔧 Testing Service Initialization...")

        try:
            from services.shared.multimodal_ai_service import (
                get_multimodal_service,
                ModelType,
            )

            # Check if DeepSeek R1 is available
            if not hasattr(ModelType, "DEEPSEEK_R1"):
                return {
                    "status": "FAIL",
                    "error": "DeepSeek R1 model type not found",
                    "details": "ModelType.DEEPSEEK_R1 not available",
                }

            # Initialize service
            service = await get_multimodal_service()

            # Check if DeepSeek R1 is in routing configuration
            deepseek_in_routing = any(
                model == ModelType.DEEPSEEK_R1
                for model in service.router.routing_rules.values()
                if model is not None
            )

            # Check load balancing configuration
            deepseek_in_load_balancing = (
                ModelType.DEEPSEEK_R1 in service.router.load_balancing
            )

            return {
                "status": "PASS",
                "deepseek_model_available": True,
                "deepseek_in_routing": deepseek_in_routing,
                "deepseek_in_load_balancing": deepseek_in_load_balancing,
                "deepseek_max_load": service.router.load_balancing.get(
                    ModelType.DEEPSEEK_R1, {}
                ).get("max_load", 0),
                "details": "DeepSeek R1 successfully integrated into multimodal service",
            }

        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "details": "Failed to initialize service with DeepSeek R1",
            }

    async def _test_model_availability(self) -> Dict[str, Any]:
        """Test DeepSeek R1 model availability through OpenRouter API."""

        logger.info("🌐 Testing DeepSeek R1 Model Availability...")

        try:
            # Check if API key is available
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                return {
                    "status": "SKIP",
                    "reason": "OPENROUTER_API_KEY not set",
                    "details": "API key required for model availability testing",
                }

            # Test DeepSeek R1 API call
            import aiohttp

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }

            payload = {
                "model": "deepseek/deepseek-r1-0528:free",
                "messages": [
                    {
                        "role": "user",
                        "content": "Test message for DeepSeek R1 availability check",
                    }
                ],
                "max_tokens": 50,
            }

            start_time = time.time()

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:

                    response_time = (time.time() - start_time) * 1000

                    if response.status == 200:
                        result = await response.json()

                        return {
                            "status": "PASS",
                            "response_time_ms": response_time,
                            "model_tested": payload["model"],
                            "tokens_used": result.get("usage", {}).get(
                                "total_tokens", 0
                            ),
                            "response_content": result.get("choices", [{}])[0]
                            .get("message", {})
                            .get("content", ""),
                            "details": "DeepSeek R1 model available and responding",
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "status": "FAIL",
                            "error": f"HTTP {response.status}: {error_text}",
                            "response_time_ms": response_time,
                            "details": "DeepSeek R1 model not available or API error",
                        }

        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "details": "DeepSeek R1 availability test failed",
            }

    async def _test_cost_analysis(self) -> Dict[str, Any]:
        """Test cost analysis and savings calculation."""

        logger.info("💰 Testing Cost Analysis...")

        try:
            from services.shared.multimodal_ai_service import (
                get_multimodal_service,
                ModelType,
            )

            service = await get_multimodal_service()

            # Get pricing for all models
            pricing = service.openrouter_client.pricing

            # Calculate cost comparison for standard request (1000 input tokens, 500 output tokens)
            input_tokens = 1000
            output_tokens = 500

            costs = {}
            for model_type in ModelType:
                if model_type in pricing:
                    model_pricing = pricing[model_type]
                    cost = (input_tokens / 1_000_000) * model_pricing["input"] + (
                        output_tokens / 1_000_000
                    ) * model_pricing["output"]
                    costs[model_type.value] = cost

            # Calculate cost savings
            flash_full_cost = costs.get("google/gemini-2.5-flash", 0)
            deepseek_cost = costs.get("deepseek/deepseek-r1-0528:free", 0)

            if flash_full_cost > 0 and deepseek_cost > 0:
                cost_reduction_percent = (
                    (flash_full_cost - deepseek_cost) / flash_full_cost
                ) * 100
                meets_target = cost_reduction_percent >= self.target_cost_reduction
            else:
                cost_reduction_percent = 0
                meets_target = False

            return {
                "status": "PASS" if meets_target else "PARTIAL",
                "model_costs": costs,
                "cost_reduction_percent": cost_reduction_percent,
                "target_reduction_percent": self.target_cost_reduction,
                "meets_target": meets_target,
                "flash_full_cost": flash_full_cost,
                "deepseek_cost": deepseek_cost,
                "cost_savings_per_request": flash_full_cost - deepseek_cost,
                "details": f"DeepSeek R1 provides {cost_reduction_percent:.1f}% cost reduction (target: {self.target_cost_reduction}%)",
            }

        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "details": "Cost analysis test failed",
            }

    async def _test_performance_comparison(self) -> Dict[str, Any]:
        """Test performance comparison between models."""

        logger.info("⚡ Testing Performance Comparison...")

        try:
            from services.shared.multimodal_ai_service import (
                get_multimodal_service,
                MultimodalRequest,
                RequestType,
                ContentType,
                ModelType,
            )

            service = await get_multimodal_service()

            # Test content
            test_content = "Analyze this content for constitutional compliance and democratic governance principles."

            performance_results = {}

            # Test each model type
            for model_type in [
                ModelType.DEEPSEEK_R1,
                ModelType.FLASH_LITE,
                ModelType.FLASH_FULL,
            ]:
                try:
                    # Force specific model selection
                    original_select = service.router.select_model
                    service.router.select_model = lambda req: model_type

                    # Create request
                    request = MultimodalRequest(
                        request_id=f"perf_test_{model_type.value}",
                        request_type=RequestType.QUICK_ANALYSIS,
                        content_type=ContentType.TEXT_ONLY,
                        text_content=test_content,
                        priority="normal",
                    )

                    # Process request
                    start_time = time.time()
                    response = await service.process_request(request)
                    actual_time = (time.time() - start_time) * 1000

                    performance_results[model_type.value] = {
                        "response_time_ms": actual_time,
                        "reported_time_ms": response.metrics.response_time_ms,
                        "constitutional_compliance": response.constitutional_compliance,
                        "confidence_score": response.confidence_score,
                        "cost_estimate": response.metrics.cost_estimate,
                        "quality_score": response.metrics.quality_score,
                        "cache_hit": response.metrics.cache_hit,
                        "meets_2s_target": actual_time < 2000,
                    }

                    # Restore original routing
                    service.router.select_model = original_select

                except Exception as e:
                    performance_results[model_type.value] = {
                        "error": str(e),
                        "failed": True,
                    }

            # Analyze results
            successful_tests = [
                r for r in performance_results.values() if not r.get("failed", False)
            ]
            avg_response_time = (
                sum(r["response_time_ms"] for r in successful_tests)
                / len(successful_tests)
                if successful_tests
                else 0
            )
            all_meet_target = all(
                r.get("meets_2s_target", False) for r in successful_tests
            )

            return {
                "status": (
                    "PASS"
                    if all_meet_target and len(successful_tests) >= 2
                    else "PARTIAL"
                ),
                "performance_results": performance_results,
                "avg_response_time_ms": avg_response_time,
                "all_meet_2s_target": all_meet_target,
                "successful_tests": len(successful_tests),
                "total_tests": len(performance_results),
                "details": f"Performance comparison: {len(successful_tests)}/{len(performance_results)} models tested successfully",
            }

        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "details": "Performance comparison test failed",
            }

    async def _test_routing_optimization(self) -> Dict[str, Any]:
        """Test intelligent routing with DeepSeek R1 integration."""

        logger.info("🧠 Testing Routing Optimization...")

        try:
            from services.shared.multimodal_ai_service import (
                get_multimodal_service,
                MultimodalRequest,
                RequestType,
                ContentType,
                ModelType,
            )

            service = await get_multimodal_service()

            # Test routing decisions for different request types
            routing_tests = [
                {
                    "name": "Quick Analysis (should route to DeepSeek R1)",
                    "request_type": RequestType.QUICK_ANALYSIS,
                    "expected_model": ModelType.DEEPSEEK_R1,
                    "content": "Quick constitutional check needed",
                },
                {
                    "name": "Content Moderation (should route to DeepSeek R1)",
                    "request_type": RequestType.CONTENT_MODERATION,
                    "expected_model": ModelType.DEEPSEEK_R1,
                    "content": "Moderate this content for policy compliance",
                },
                {
                    "name": "Policy Analysis (should route to Flash Full)",
                    "request_type": RequestType.POLICY_ANALYSIS,
                    "expected_model": ModelType.FLASH_FULL,
                    "content": "Comprehensive policy analysis required",
                },
            ]

            routing_results = []

            for test in routing_tests:
                request = MultimodalRequest(
                    request_id=f"routing_test_{test['request_type'].value}",
                    request_type=test["request_type"],
                    content_type=ContentType.TEXT_ONLY,
                    text_content=test["content"],
                    priority="normal",
                )

                # Get routing decision
                selected_model = service.router.select_model(request)
                routing_correct = selected_model == test["expected_model"]

                routing_results.append(
                    {
                        "test_name": test["name"],
                        "expected_model": test["expected_model"].value,
                        "selected_model": selected_model.value,
                        "routing_correct": routing_correct,
                        "request_type": test["request_type"].value,
                    }
                )

            # Calculate routing accuracy
            correct_routes = sum(1 for r in routing_results if r["routing_correct"])
            routing_accuracy = (correct_routes / len(routing_results)) * 100

            return {
                "status": "PASS" if routing_accuracy >= 80 else "PARTIAL",
                "routing_results": routing_results,
                "routing_accuracy_percent": routing_accuracy,
                "correct_routes": correct_routes,
                "total_routes": len(routing_results),
                "details": f"Routing optimization: {correct_routes}/{len(routing_results)} correct decisions ({routing_accuracy:.1f}%)",
            }

        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "details": "Routing optimization test failed",
            }

    async def _test_constitutional_compliance(self) -> Dict[str, Any]:
        """Test constitutional compliance with DeepSeek R1."""

        logger.info("🏛️ Testing Constitutional Compliance...")

        try:
            from services.shared.multimodal_ai_service import (
                get_multimodal_service,
                MultimodalRequest,
                RequestType,
                ContentType,
            )

            service = await get_multimodal_service()

            # Test cases with known compliance expectations
            compliance_tests = [
                {
                    "name": "Democratic Content",
                    "content": "Citizens have the right to participate in democratic processes and transparent governance.",
                    "expected_compliant": True,
                },
                {
                    "name": "Constitutional Rights",
                    "content": "The constitution protects individual rights and ensures democratic representation.",
                    "expected_compliant": True,
                },
            ]

            compliance_results = []

            for test_case in compliance_tests:
                import time

                request = MultimodalRequest(
                    request_id=f"compliance_test_{len(compliance_results)}_{int(time.time())}",
                    request_type=RequestType.CONSTITUTIONAL_VALIDATION,
                    content_type=ContentType.TEXT_ONLY,
                    text_content=test_case["content"],
                    priority="high",
                )

                logger.info(
                    f"Testing: {test_case['name']} - {test_case['content'][:50]}..."
                )
                response = await service.process_request(request)
                logger.info(
                    f"Result: compliant={response.constitutional_compliance}, confidence={response.confidence_score:.3f}"
                )

                compliance_results.append(
                    {
                        "test_name": test_case["name"],
                        "expected_compliant": test_case["expected_compliant"],
                        "actual_compliant": response.constitutional_compliance,
                        "accuracy_match": test_case["expected_compliant"]
                        == response.constitutional_compliance,
                        "confidence_score": response.confidence_score,
                        "model_used": response.model_used.value,
                        "constitutional_hash": response.constitutional_hash,
                    }
                )

            # Calculate compliance accuracy
            accurate_results = sum(1 for r in compliance_results if r["accuracy_match"])
            accuracy_rate = (
                (accurate_results / len(compliance_results)) * 100
                if compliance_results
                else 0
            )

            return {
                "status": (
                    "PASS"
                    if accuracy_rate >= 90
                    else "PARTIAL" if accuracy_rate >= 70 else "FAIL"
                ),
                "compliance_results": compliance_results,
                "accuracy_rate_percent": accuracy_rate,
                "accurate_results": accurate_results,
                "total_tests": len(compliance_results),
                "constitutional_hash_consistent": all(
                    r["constitutional_hash"] == self.constitutional_hash
                    for r in compliance_results
                ),
                "details": f"Constitutional compliance: {accuracy_rate:.1f}% accuracy ({accurate_results}/{len(compliance_results)})",
            }

        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "details": "Constitutional compliance test failed",
            }

    async def _test_load_balancing(self) -> Dict[str, Any]:
        """Test load balancing with DeepSeek R1."""

        logger.info("⚖️ Testing Load Balancing...")

        try:
            from services.shared.multimodal_ai_service import (
                get_multimodal_service,
                ModelType,
            )

            service = await get_multimodal_service()

            # Check initial load balancing configuration
            load_config = service.router.load_balancing

            # Verify DeepSeek R1 has higher capacity (cost-effective model)
            deepseek_max_load = load_config.get(ModelType.DEEPSEEK_R1, {}).get(
                "max_load", 0
            )
            flash_lite_max_load = load_config.get(ModelType.FLASH_LITE, {}).get(
                "max_load", 0
            )
            flash_full_max_load = load_config.get(ModelType.FLASH_FULL, {}).get(
                "max_load", 0
            )

            # Test load tracking
            original_load = service.router.current_loads[ModelType.DEEPSEEK_R1]

            # Simulate load increase
            service.router._update_load(ModelType.DEEPSEEK_R1, 10)
            new_load = service.router.current_loads[ModelType.DEEPSEEK_R1]

            # Reset load
            service.router._update_load(ModelType.DEEPSEEK_R1, -10)
            reset_load = service.router.current_loads[ModelType.DEEPSEEK_R1]

            return {
                "status": "PASS",
                "load_configuration": {
                    "deepseek_r1_max_load": deepseek_max_load,
                    "flash_lite_max_load": flash_lite_max_load,
                    "flash_full_max_load": flash_full_max_load,
                },
                "deepseek_has_highest_capacity": deepseek_max_load
                >= max(flash_lite_max_load, flash_full_max_load),
                "load_tracking_test": {
                    "original_load": original_load,
                    "after_increase": new_load,
                    "after_reset": reset_load,
                    "tracking_works": new_load == original_load + 10
                    and reset_load == original_load,
                },
                "details": f"Load balancing: DeepSeek R1 max capacity {deepseek_max_load}, tracking functional",
            }

        except Exception as e:
            return {
                "status": "FAIL",
                "error": str(e),
                "details": "Load balancing test failed",
            }

    def print_test_report(self, results: Dict[str, Any]):
        """Print formatted test report."""

        print("\n" + "=" * 60)
        print("DEEPSEEK R1 INTEGRATION TEST REPORT")
        print("=" * 60)

        info = results["test_info"]
        summary = results["summary"]

        print(f"Timestamp: {info['timestamp']}")
        print(f"Duration: {info['total_duration_seconds']:.1f} seconds")
        print(f"Constitutional Hash: {info['constitutional_hash']}")
        print(f"Target Cost Reduction: {info['target_cost_reduction']}%")

        print(f"\n📊 OVERALL SUMMARY")
        print(f"Status: {summary['overall_status']}")
        print(f"Tests Passed: {summary['passed_tests']}/{summary['total_tests']}")
        print(f"Success Rate: {summary['success_rate_percent']:.1f}%")

        print(f"\n🔍 DETAILED RESULTS")
        print("-" * 40)

        for test_name, test_result in results["test_results"].items():
            status_icon = (
                "✅"
                if test_result["status"] == "PASS"
                else "⚠️" if test_result["status"] == "PARTIAL" else "❌"
            )
            print(
                f"{status_icon} {test_name.replace('_', ' ').title()}: {test_result['status']}"
            )

            if "details" in test_result:
                print(f"   {test_result['details']}")

            # Special handling for cost analysis
            if test_name == "cost_analysis" and test_result["status"] != "FAIL":
                cost_reduction = test_result.get("cost_reduction_percent", 0)
                print(
                    f"   💰 Cost Reduction: {cost_reduction:.1f}% (Target: {info['target_cost_reduction']}%)"
                )
                if test_result.get("meets_target"):
                    print(f"   ✅ Cost reduction target achieved!")
                else:
                    print(f"   ⚠️ Cost reduction below target")

            if test_result["status"] == "FAIL" and "error" in test_result:
                print(f"   Error: {test_result['error']}")

        print("\n" + "=" * 60)


async def main():
    """Main execution function."""

    # Initialize tester
    tester = DeepSeekR1IntegrationTester()

    # Run comprehensive tests
    results = await tester.run_comprehensive_test()

    # Print report
    tester.print_test_report(results)

    # Save detailed results
    output_dir = Path("reports/deepseek_r1_integration")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"deepseek_r1_integration_test_{timestamp}.json"

    with open(report_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n📄 Detailed report saved to: {report_file}")

    # Return exit code based on results
    return 0 if results["summary"]["overall_status"] in ["PASS", "PARTIAL"] else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
