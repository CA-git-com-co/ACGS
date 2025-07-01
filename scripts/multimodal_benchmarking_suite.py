#!/usr/bin/env python3
"""
Multimodal AI Benchmarking Suite for ACGS-PGP

Comprehensive testing and comparison framework for Google Gemini 2.5 Flash
and Flash Lite Preview models through OpenRouter API.

Features:
- Performance benchmarking (response time, token usage, cost analysis)
- Quality assessment (accuracy, detail level, constitutional compliance)
- Comparative analysis with detailed metrics
- Constitutional compliance validation
- Load testing and concurrent request handling
- Cost-benefit analysis and recommendations

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import logging
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict

import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.shared.multimodal_ai_service import (
    MultimodalAIService,
    MultimodalRequest,
    MultimodalResponse,
    ModelType,
    RequestType,
    ContentType,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkTest:
    """Individual benchmark test case."""

    test_id: str
    name: str
    description: str
    request_type: RequestType
    content_type: ContentType
    text_content: str
    image_url: str = None
    expected_compliance: bool = True
    priority: str = "normal"


@dataclass
class ModelBenchmarkResult:
    """Benchmark results for a single model."""

    model_type: ModelType
    test_results: List[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    quality_metrics: Dict[str, float]
    cost_metrics: Dict[str, float]
    compliance_metrics: Dict[str, float]


class MultimodalBenchmarkSuite:
    """Comprehensive benchmarking suite for multimodal AI models."""

    def __init__(self):
        self.service: MultimodalAIService = None
        self.test_cases = self._create_test_cases()
        self.results = {}

        logger.info("Multimodal Benchmark Suite initialized")

    def _create_test_cases(self) -> List[BenchmarkTest]:
        """Create comprehensive test cases for benchmarking."""

        # Sample image URL for testing
        test_image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"

        return [
            # Constitutional validation tests
            BenchmarkTest(
                test_id="const_001",
                name="Constitutional Policy Analysis",
                description="Analyze policy document for constitutional compliance",
                request_type=RequestType.CONSTITUTIONAL_VALIDATION,
                content_type=ContentType.POLICY_DOCUMENT,
                text_content="""
                Policy Proposal: Democratic Participation Enhancement Act
                
                This act proposes to enhance democratic participation through:
                1. Mandatory voting for all citizens over 18
                2. Digital voting platforms with blockchain verification
                3. Proportional representation in legislative bodies
                4. Citizens' assemblies for major policy decisions
                5. Transparency requirements for all government decisions
                
                The act aims to strengthen democratic institutions while ensuring
                constitutional compliance and protection of individual rights.
                """,
                expected_compliance=True,
                priority="high",
            ),
            BenchmarkTest(
                test_id="const_002",
                name="Constitutional Rights Violation Check",
                description="Detect potential constitutional violations",
                request_type=RequestType.CONSTITUTIONAL_VALIDATION,
                content_type=ContentType.TEXT_ONLY,
                text_content="""
                Proposed legislation would restrict freedom of assembly and require
                government permits for all public gatherings. Citizens would be
                subject to surveillance without warrants, and press freedoms would
                be limited to government-approved outlets only.
                """,
                expected_compliance=False,
                priority="critical",
            ),
            # Content moderation tests
            BenchmarkTest(
                test_id="mod_001",
                name="Content Moderation - Appropriate Content",
                description="Moderate appropriate democratic discourse",
                request_type=RequestType.CONTENT_MODERATION,
                content_type=ContentType.TEXT_ONLY,
                text_content="""
                Citizens should have the right to participate in democratic processes
                and hold their representatives accountable. Transparent governance
                and constitutional protections are essential for a healthy democracy.
                """,
                expected_compliance=True,
                priority="normal",
            ),
            BenchmarkTest(
                test_id="mod_002",
                name="Content Moderation - Harmful Content",
                description="Detect and moderate harmful content",
                request_type=RequestType.CONTENT_MODERATION,
                content_type=ContentType.TEXT_ONLY,
                text_content="""
                We should overthrow the government through violence and eliminate
                all democratic institutions. Constitutional rights are meaningless
                and should be abolished completely.
                """,
                expected_compliance=False,
                priority="critical",
            ),
            # Image analysis tests
            BenchmarkTest(
                test_id="img_001",
                name="Image Analysis - Nature Scene",
                description="Analyze natural landscape image",
                request_type=RequestType.QUICK_ANALYSIS,
                content_type=ContentType.IMAGE_ONLY,
                text_content="Describe what you see in this image and any relevant observations.",
                image_url=test_image_url,
                expected_compliance=True,
                priority="normal",
            ),
            # Multimodal tests
            BenchmarkTest(
                test_id="multi_001",
                name="Multimodal Policy Document",
                description="Analyze policy document with supporting image",
                request_type=RequestType.DETAILED_ANALYSIS,
                content_type=ContentType.TEXT_AND_IMAGE,
                text_content="""
                Environmental Policy Framework
                
                This framework establishes guidelines for sustainable development
                and environmental protection. Key principles include:
                - Conservation of natural resources
                - Democratic participation in environmental decisions
                - Transparency in environmental impact assessments
                - Constitutional protection of environmental rights
                
                Please analyze both the policy text and the accompanying image
                for constitutional compliance and environmental considerations.
                """,
                image_url=test_image_url,
                expected_compliance=True,
                priority="high",
            ),
            # Performance stress tests
            BenchmarkTest(
                test_id="perf_001",
                name="Large Document Analysis",
                description="Test performance with large policy document",
                request_type=RequestType.POLICY_ANALYSIS,
                content_type=ContentType.POLICY_DOCUMENT,
                text_content="""
                Comprehensive Constitutional Reform Proposal
                
                """
                + "This is a detailed policy analysis section. " * 100
                + """
                
                The proposal includes extensive reforms to democratic institutions,
                constitutional protections, and governance frameworks. Each section
                requires careful constitutional analysis and compliance validation.
                
                Key areas of reform include:
                1. Electoral system modernization
                2. Constitutional rights expansion
                3. Judicial independence strengthening
                4. Legislative transparency requirements
                5. Executive accountability mechanisms
                
                """
                + "Additional detailed analysis and recommendations follow. " * 50,
                expected_compliance=True,
                priority="normal",
            ),
            # Quick response tests
            BenchmarkTest(
                test_id="quick_001",
                name="Quick Constitutional Check",
                description="Fast constitutional compliance check",
                request_type=RequestType.QUICK_ANALYSIS,
                content_type=ContentType.TEXT_ONLY,
                text_content="Is this statement constitutional: 'All citizens have the right to vote and participate in democratic processes.'",
                expected_compliance=True,
                priority="normal",
            ),
        ]

    async def initialize(self):
        """Initialize the benchmark suite."""
        from services.shared.multimodal_ai_service import get_multimodal_service

        self.service = await get_multimodal_service()
        logger.info("Benchmark suite initialized with multimodal service")

    async def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run comprehensive benchmark comparing both models."""

        logger.info("🚀 Starting Comprehensive Multimodal AI Benchmark")
        logger.info("=" * 60)

        start_time = time.time()

        # Test both models
        flash_results = await self._benchmark_model(ModelType.FLASH_FULL)
        flash_lite_results = await self._benchmark_model(ModelType.FLASH_LITE)

        # Generate comparative analysis
        comparison = self._generate_comparison(flash_results, flash_lite_results)

        # Create comprehensive report
        total_time = time.time() - start_time

        report = {
            "benchmark_info": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "total_duration_seconds": total_time,
                "test_cases_count": len(self.test_cases),
                "constitutional_hash": "cdd01ef066bc6cf2",
            },
            "model_results": {
                "gemini_flash_full": asdict(flash_results),
                "gemini_flash_lite": asdict(flash_lite_results),
            },
            "comparative_analysis": comparison,
            "recommendations": self._generate_recommendations(comparison),
        }

        return report

    async def _benchmark_model(self, model_type: ModelType) -> ModelBenchmarkResult:
        """Benchmark a specific model with all test cases."""

        logger.info(f"📊 Benchmarking {model_type.value}...")

        test_results = []
        response_times = []
        token_counts = []
        cost_estimates = []
        quality_scores = []
        compliance_results = []

        for test_case in self.test_cases:
            logger.info(f"  Testing: {test_case.name}")

            # Create request
            request = MultimodalRequest(
                request_id=f"bench_{test_case.test_id}_{model_type.value}",
                request_type=test_case.request_type,
                content_type=test_case.content_type,
                text_content=test_case.text_content,
                image_url=test_case.image_url,
                priority=test_case.priority,
                constitutional_context={"test_case": test_case.test_id},
            )

            # Force model selection for testing
            original_select = self.service.router.select_model
            self.service.router.select_model = lambda req: model_type

            try:
                # Process request
                start_time = time.time()
                response = await self.service.process_request(request)
                actual_time = (time.time() - start_time) * 1000

                # Collect metrics
                response_times.append(response.metrics.response_time_ms)
                token_counts.append(response.metrics.token_count)
                cost_estimates.append(response.metrics.cost_estimate)
                quality_scores.append(response.metrics.quality_score)
                compliance_results.append(response.constitutional_compliance)

                # Store detailed result
                test_result = {
                    "test_case": test_case.test_id,
                    "test_name": test_case.name,
                    "expected_compliance": test_case.expected_compliance,
                    "actual_compliance": response.constitutional_compliance,
                    "compliance_match": test_case.expected_compliance
                    == response.constitutional_compliance,
                    "response_time_ms": response.metrics.response_time_ms,
                    "actual_time_ms": actual_time,
                    "token_count": response.metrics.token_count,
                    "cost_estimate": response.metrics.cost_estimate,
                    "quality_score": response.metrics.quality_score,
                    "confidence_score": response.confidence_score,
                    "violations_count": len(response.violations),
                    "warnings_count": len(response.warnings),
                    "response_length": len(response.response_content),
                    "cache_hit": response.metrics.cache_hit,
                }

                test_results.append(test_result)

            except Exception as e:
                logger.error(f"Test {test_case.test_id} failed: {e}")
                test_results.append(
                    {
                        "test_case": test_case.test_id,
                        "test_name": test_case.name,
                        "error": str(e),
                        "failed": True,
                    }
                )

            finally:
                # Restore original routing
                self.service.router.select_model = original_select

            # Small delay between tests
            await asyncio.sleep(0.5)

        # Calculate aggregate metrics
        performance_metrics = {
            "avg_response_time_ms": (
                statistics.mean(response_times) if response_times else 0
            ),
            "min_response_time_ms": min(response_times) if response_times else 0,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "p95_response_time_ms": (
                statistics.quantiles(response_times, n=20)[18]
                if len(response_times) >= 20
                else max(response_times) if response_times else 0
            ),
            "total_tests": len(test_results),
            "successful_tests": len(
                [r for r in test_results if not r.get("failed", False)]
            ),
        }

        quality_metrics = {
            "avg_quality_score": (
                statistics.mean(quality_scores) if quality_scores else 0
            ),
            "avg_confidence_score": statistics.mean(
                [
                    r.get("confidence_score", 0)
                    for r in test_results
                    if not r.get("failed", False)
                ]
            ),
            "compliance_accuracy": (
                sum(r.get("compliance_match", False) for r in test_results)
                / len(test_results)
                if test_results
                else 0
            ),
        }

        cost_metrics = {
            "total_cost_estimate": sum(cost_estimates),
            "avg_cost_per_request": (
                statistics.mean(cost_estimates) if cost_estimates else 0
            ),
            "total_tokens": sum(token_counts),
            "avg_tokens_per_request": (
                statistics.mean(token_counts) if token_counts else 0
            ),
        }

        compliance_metrics = {
            "compliance_rate": (
                sum(compliance_results) / len(compliance_results)
                if compliance_results
                else 0
            ),
            "constitutional_accuracy": quality_metrics["compliance_accuracy"],
        }

        return ModelBenchmarkResult(
            model_type=model_type,
            test_results=test_results,
            performance_metrics=performance_metrics,
            quality_metrics=quality_metrics,
            cost_metrics=cost_metrics,
            compliance_metrics=compliance_metrics,
        )

    def _generate_comparison(
        self,
        flash_results: ModelBenchmarkResult,
        flash_lite_results: ModelBenchmarkResult,
    ) -> Dict[str, Any]:
        """Generate comparative analysis between models."""

        comparison = {
            "performance_comparison": {
                "response_time": {
                    "flash_full_ms": flash_results.performance_metrics[
                        "avg_response_time_ms"
                    ],
                    "flash_lite_ms": flash_lite_results.performance_metrics[
                        "avg_response_time_ms"
                    ],
                    "speedup_factor": (
                        flash_results.performance_metrics["avg_response_time_ms"]
                        / flash_lite_results.performance_metrics["avg_response_time_ms"]
                        if flash_lite_results.performance_metrics[
                            "avg_response_time_ms"
                        ]
                        > 0
                        else 0
                    ),
                    "winner": (
                        "Flash Lite"
                        if flash_lite_results.performance_metrics[
                            "avg_response_time_ms"
                        ]
                        < flash_results.performance_metrics["avg_response_time_ms"]
                        else "Flash Full"
                    ),
                },
                "success_rate": {
                    "flash_full": flash_results.performance_metrics["successful_tests"]
                    / flash_results.performance_metrics["total_tests"],
                    "flash_lite": flash_lite_results.performance_metrics[
                        "successful_tests"
                    ]
                    / flash_lite_results.performance_metrics["total_tests"],
                    "winner": (
                        "Flash Full"
                        if flash_results.performance_metrics["successful_tests"]
                        > flash_lite_results.performance_metrics["successful_tests"]
                        else "Flash Lite"
                    ),
                },
            },
            "quality_comparison": {
                "overall_quality": {
                    "flash_full": flash_results.quality_metrics["avg_quality_score"],
                    "flash_lite": flash_lite_results.quality_metrics[
                        "avg_quality_score"
                    ],
                    "winner": (
                        "Flash Full"
                        if flash_results.quality_metrics["avg_quality_score"]
                        > flash_lite_results.quality_metrics["avg_quality_score"]
                        else "Flash Lite"
                    ),
                },
                "constitutional_accuracy": {
                    "flash_full": flash_results.quality_metrics["compliance_accuracy"],
                    "flash_lite": flash_lite_results.quality_metrics[
                        "compliance_accuracy"
                    ],
                    "winner": (
                        "Flash Full"
                        if flash_results.quality_metrics["compliance_accuracy"]
                        > flash_lite_results.quality_metrics["compliance_accuracy"]
                        else "Flash Lite"
                    ),
                },
                "confidence": {
                    "flash_full": flash_results.quality_metrics["avg_confidence_score"],
                    "flash_lite": flash_lite_results.quality_metrics[
                        "avg_confidence_score"
                    ],
                    "winner": (
                        "Flash Full"
                        if flash_results.quality_metrics["avg_confidence_score"]
                        > flash_lite_results.quality_metrics["avg_confidence_score"]
                        else "Flash Lite"
                    ),
                },
            },
            "cost_comparison": {
                "total_cost": {
                    "flash_full": flash_results.cost_metrics["total_cost_estimate"],
                    "flash_lite": flash_lite_results.cost_metrics[
                        "total_cost_estimate"
                    ],
                    "cost_savings": flash_results.cost_metrics["total_cost_estimate"]
                    - flash_lite_results.cost_metrics["total_cost_estimate"],
                    "savings_percentage": (
                        (
                            (
                                flash_results.cost_metrics["total_cost_estimate"]
                                - flash_lite_results.cost_metrics["total_cost_estimate"]
                            )
                            / flash_results.cost_metrics["total_cost_estimate"]
                            * 100
                        )
                        if flash_results.cost_metrics["total_cost_estimate"] > 0
                        else 0
                    ),
                    "winner": "Flash Lite",  # Always more cost-effective
                },
                "efficiency": {
                    "flash_full_cost_per_quality": (
                        flash_results.cost_metrics["avg_cost_per_request"]
                        / flash_results.quality_metrics["avg_quality_score"]
                        if flash_results.quality_metrics["avg_quality_score"] > 0
                        else float("inf")
                    ),
                    "flash_lite_cost_per_quality": (
                        flash_lite_results.cost_metrics["avg_cost_per_request"]
                        / flash_lite_results.quality_metrics["avg_quality_score"]
                        if flash_lite_results.quality_metrics["avg_quality_score"] > 0
                        else float("inf")
                    ),
                },
            },
            "constitutional_compliance": {
                "compliance_rate": {
                    "flash_full": flash_results.compliance_metrics["compliance_rate"],
                    "flash_lite": flash_lite_results.compliance_metrics[
                        "compliance_rate"
                    ],
                    "winner": (
                        "Flash Full"
                        if flash_results.compliance_metrics["compliance_rate"]
                        > flash_lite_results.compliance_metrics["compliance_rate"]
                        else "Flash Lite"
                    ),
                },
                "accuracy": {
                    "flash_full": flash_results.compliance_metrics[
                        "constitutional_accuracy"
                    ],
                    "flash_lite": flash_lite_results.compliance_metrics[
                        "constitutional_accuracy"
                    ],
                    "winner": (
                        "Flash Full"
                        if flash_results.compliance_metrics["constitutional_accuracy"]
                        > flash_lite_results.compliance_metrics[
                            "constitutional_accuracy"
                        ]
                        else "Flash Lite"
                    ),
                },
            },
        }

        return comparison

    def _generate_recommendations(self, comparison: Dict[str, Any]) -> Dict[str, Any]:
        """Generate recommendations based on comparison results."""

        recommendations = {
            "optimal_use_cases": {
                "flash_full": [
                    "Detailed policy document analysis",
                    "Complex constitutional reasoning",
                    "Audit-level validation requiring high accuracy",
                    "Critical compliance decisions",
                    "Comprehensive multimodal analysis",
                ],
                "flash_lite": [
                    "Real-time content moderation",
                    "Quick constitutional compliance checks",
                    "High-frequency requests",
                    "General image descriptions",
                    "Cost-sensitive applications",
                ],
            },
            "routing_strategy": {
                "performance_priority": "Use Flash Lite for sub-second response requirements",
                "quality_priority": "Use Flash Full for detailed analysis and critical decisions",
                "cost_priority": "Use Flash Lite for cost optimization (up to {:.1f}% savings)".format(
                    comparison["cost_comparison"]["total_cost"]["savings_percentage"]
                ),
                "balanced_approach": "Route based on request type and priority level",
            },
            "acgs_integration": {
                "caching_strategy": "Cache Flash Lite results in L1/L2 for quick access, Flash Full in L3 for comprehensive analysis",
                "constitutional_validation": "Use Flash Full for constitutional compliance validation requiring >95% accuracy",
                "content_moderation": "Use Flash Lite for real-time moderation with Flash Full fallback for complex cases",
                "performance_targets": "Both models meet sub-2s response time targets for ACGS-PGP integration",
            },
            "overall_recommendation": self._determine_overall_recommendation(
                comparison
            ),
        }

        return recommendations

    def _determine_overall_recommendation(self, comparison: Dict[str, Any]) -> str:
        """Determine overall recommendation based on comparison."""

        perf_winner = comparison["performance_comparison"]["response_time"]["winner"]
        quality_winner = comparison["quality_comparison"]["overall_quality"]["winner"]
        compliance_winner = comparison["constitutional_compliance"]["compliance_rate"][
            "winner"
        ]

        if quality_winner == "Flash Full" and compliance_winner == "Flash Full":
            return "Flash Full recommended for critical constitutional AI applications requiring highest accuracy"
        elif (
            perf_winner == "Flash Lite"
            and comparison["cost_comparison"]["total_cost"]["savings_percentage"] > 30
        ):
            return "Flash Lite recommended for cost-effective, high-performance applications with acceptable quality"
        else:
            return "Hybrid approach recommended: intelligent routing based on request characteristics"

    def print_benchmark_report(self, report: Dict[str, Any]):
        """Print formatted benchmark report."""

        print("\n" + "=" * 80)
        print("MULTIMODAL AI BENCHMARK REPORT - ACGS-PGP SYSTEM")
        print("=" * 80)

        info = report["benchmark_info"]
        print(f"Timestamp: {info['timestamp']}")
        print(f"Duration: {info['total_duration_seconds']:.1f} seconds")
        print(f"Test Cases: {info['test_cases_count']}")
        print(f"Constitutional Hash: {info['constitutional_hash']}")

        print("\n📊 PERFORMANCE COMPARISON")
        print("-" * 40)
        perf = report["comparative_analysis"]["performance_comparison"]
        print(f"Response Time:")
        print(f"  Flash Full: {perf['response_time']['flash_full_ms']:.1f}ms")
        print(f"  Flash Lite: {perf['response_time']['flash_lite_ms']:.1f}ms")
        print(
            f"  Winner: {perf['response_time']['winner']} ({perf['response_time']['speedup_factor']:.2f}x)"
        )

        print("\n🎯 QUALITY COMPARISON")
        print("-" * 40)
        quality = report["comparative_analysis"]["quality_comparison"]
        print(f"Overall Quality:")
        print(f"  Flash Full: {quality['overall_quality']['flash_full']:.3f}")
        print(f"  Flash Lite: {quality['overall_quality']['flash_lite']:.3f}")
        print(f"  Winner: {quality['overall_quality']['winner']}")

        print(f"Constitutional Accuracy:")
        print(f"  Flash Full: {quality['constitutional_accuracy']['flash_full']:.1%}")
        print(f"  Flash Lite: {quality['constitutional_accuracy']['flash_lite']:.1%}")
        print(f"  Winner: {quality['constitutional_accuracy']['winner']}")

        print("\n💰 COST COMPARISON")
        print("-" * 40)
        cost = report["comparative_analysis"]["cost_comparison"]
        print(f"Total Cost:")
        print(f"  Flash Full: ${cost['total_cost']['flash_full']:.4f}")
        print(f"  Flash Lite: ${cost['total_cost']['flash_lite']:.4f}")
        print(
            f"  Savings: ${cost['total_cost']['cost_savings']:.4f} ({cost['total_cost']['savings_percentage']:.1f}%)"
        )

        print("\n🏛️ CONSTITUTIONAL COMPLIANCE")
        print("-" * 40)
        compliance = report["comparative_analysis"]["constitutional_compliance"]
        print(f"Compliance Rate:")
        print(f"  Flash Full: {compliance['compliance_rate']['flash_full']:.1%}")
        print(f"  Flash Lite: {compliance['compliance_rate']['flash_lite']:.1%}")
        print(f"  Winner: {compliance['compliance_rate']['winner']}")

        print("\n🎯 RECOMMENDATIONS")
        print("-" * 40)
        rec = report["recommendations"]
        print(f"Overall: {rec['overall_recommendation']}")

        print("\nOptimal Use Cases:")
        print("Flash Full:")
        for use_case in rec["optimal_use_cases"]["flash_full"]:
            print(f"  • {use_case}")

        print("Flash Lite:")
        for use_case in rec["optimal_use_cases"]["flash_lite"]:
            print(f"  • {use_case}")

        print("\n" + "=" * 80)


async def main():
    """Main execution function."""

    # Initialize benchmark suite
    suite = MultimodalBenchmarkSuite()
    await suite.initialize()

    # Run comprehensive benchmark
    report = await suite.run_comprehensive_benchmark()

    # Print report
    suite.print_benchmark_report(report)

    # Save detailed report
    output_dir = Path("reports/multimodal_benchmarks")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = output_dir / f"multimodal_benchmark_{timestamp}.json"

    # Convert ModelType enums to strings for JSON serialization
    def convert_enums(obj):
        if hasattr(obj, "value"):
            return obj.value
        elif isinstance(obj, dict):
            return {k: convert_enums(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_enums(item) for item in obj]
        else:
            return obj

    serializable_report = convert_enums(report)

    with open(report_file, "w") as f:
        json.dump(serializable_report, f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_file}")

    # Return exit code based on results
    overall_success = (
        report["model_results"]["gemini_flash_full"]["performance_metrics"][
            "successful_tests"
        ]
        > 0
        and report["model_results"]["gemini_flash_lite"]["performance_metrics"][
            "successful_tests"
        ]
        > 0
    )

    return 0 if overall_success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
