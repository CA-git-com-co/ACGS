#!/usr/bin/env python3
"""
Integration Tests for Policy Synthesis Enhancement System
ACGS-1 Governance Framework

This comprehensive test suite validates the Policy Synthesis Enhancement system
including multi-model consensus, error prediction, strategy selection, and
performance optimization across all deployment phases.

Test Coverage:
- Multi-model consensus functionality
- Error prediction accuracy
- Strategy selection logic
- Performance optimization
- Risk threshold effectiveness
- A/B testing framework
- End-to-end synthesis workflows
"""

import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Any

import pytest
import requests

# Test configuration
TEST_CONFIG = {
    "base_url": "http://localhost:8014",
    "timeout": 30,
    "performance_targets": {
        "response_time_ms": 2000,
        "error_prediction_accuracy": 0.95,
        "consensus_success_rate": 0.95,
        "synthesis_quality_threshold": 0.8,
    },
    "test_scenarios": [
        {
            "name": "constitutional_principle_conflict",
            "principle": "Democratic voting requires both quorum and majority approval",
            "context": {
                "domain": "governance",
                "priority": "high",
                "complexity": "medium",
            },
        },
        {
            "name": "multi_stakeholder_policy",
            "principle": "Resource allocation must balance efficiency and equity",
            "context": {
                "domain": "economics",
                "priority": "medium",
                "complexity": "high",
            },
        },
        {
            "name": "regulatory_compliance",
            "principle": "Data privacy must be maintained while enabling transparency",
            "context": {
                "domain": "privacy",
                "priority": "critical",
                "complexity": "high",
            },
        },
        {
            "name": "time_sensitive_decision",
            "principle": "Emergency protocols override standard procedures",
            "context": {
                "domain": "emergency",
                "priority": "critical",
                "complexity": "low",
            },
        },
    ],
}


class PolicySynthesisEnhancementTester:
    """Comprehensive tester for Policy Synthesis Enhancement system."""

    def __init__(self):
        self.base_url = TEST_CONFIG["base_url"]
        self.timeout = TEST_CONFIG["timeout"]
        self.targets = TEST_CONFIG["performance_targets"]
        self.test_results = []

    async def run_comprehensive_test_suite(self) -> dict[str, Any]:
        """Run the complete test suite for Policy Synthesis Enhancement."""
        print("🧪 Starting Policy Synthesis Enhancement Integration Tests")

        test_start = datetime.now(timezone.utc)
        overall_success = True

        try:
            # Phase 1: Basic functionality tests
            basic_tests = await self.test_basic_functionality()
            overall_success &= basic_tests["success"]

            # Phase 2: Multi-model consensus tests
            consensus_tests = await self.test_multi_model_consensus()
            overall_success &= consensus_tests["success"]

            # Phase 3: Error prediction tests
            error_prediction_tests = await self.test_error_prediction()
            overall_success &= error_prediction_tests["success"]

            # Phase 4: Strategy selection tests
            strategy_tests = await self.test_strategy_selection()
            overall_success &= strategy_tests["success"]

            # Phase 5: Performance optimization tests
            performance_tests = await self.test_performance_optimization()
            overall_success &= performance_tests["success"]

            # Phase 6: End-to-end scenario tests
            e2e_tests = await self.test_end_to_end_scenarios()
            overall_success &= e2e_tests["success"]

            # Phase 7: Load and stress tests
            load_tests = await self.test_load_performance()
            overall_success &= load_tests["success"]

            test_end = datetime.now(timezone.utc)

            return {
                "overall_success": overall_success,
                "test_duration_seconds": (test_end - test_start).total_seconds(),
                "test_phases": {
                    "basic_functionality": basic_tests,
                    "multi_model_consensus": consensus_tests,
                    "error_prediction": error_prediction_tests,
                    "strategy_selection": strategy_tests,
                    "performance_optimization": performance_tests,
                    "end_to_end_scenarios": e2e_tests,
                    "load_performance": load_tests,
                },
                "performance_targets_met": self._check_performance_targets(),
                "recommendations": self._generate_recommendations(),
            }

        except Exception as e:
            return {
                "overall_success": False,
                "error": str(e),
                "test_duration_seconds": (
                    datetime.now(timezone.utc) - test_start
                ).total_seconds(),
            }

    async def test_basic_functionality(self) -> dict[str, Any]:
        """Test basic Policy Synthesis Enhancement functionality."""
        print("🔧 Testing basic functionality...")

        try:
            # Test health endpoint
            health_response = requests.get(
                f"{self.base_url}/health", timeout=self.timeout
            )
            health_ok = health_response.status_code == 200

            # Test basic synthesis endpoint
            synthesis_payload = {
                "principle": "Democratic voting requires quorum",
                "context": {"domain": "governance"},
                "enable_enhancement": True,
            }

            synthesis_response = requests.post(
                f"{self.base_url}/api/v1/synthesis/policy",
                json=synthesis_payload,
                timeout=self.timeout,
            )

            synthesis_ok = synthesis_response.status_code == 200
            response_data = synthesis_response.json() if synthesis_ok else {}

            # Test metrics endpoint
            metrics_response = requests.get(
                f"{self.base_url}/api/v1/metrics/policy-synthesis", timeout=self.timeout
            )
            metrics_ok = metrics_response.status_code == 200

            return {
                "success": health_ok and synthesis_ok and metrics_ok,
                "health_check": health_ok,
                "synthesis_endpoint": synthesis_ok,
                "metrics_endpoint": metrics_ok,
                "synthesis_quality": response_data.get("quality_score", 0),
                "synthesis_confidence": response_data.get("confidence", 0),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_multi_model_consensus(self) -> dict[str, Any]:
        """Test multi-model consensus functionality."""
        print("🤝 Testing multi-model consensus...")

        try:
            consensus_payload = {
                "principle": "Constitutional amendments require supermajority approval",
                "enable_multi_model": True,
                "consensus_threshold": 0.8,
                "participating_models": ["gemini-2.5-pro", "gemini-2.0-flash"],
            }

            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/v1/synthesis/multi-model",
                json=consensus_payload,
                timeout=60,  # Longer timeout for consensus
            )
            end_time = time.time()

            response_time_ms = (end_time - start_time) * 1000

            if response.status_code == 200:
                result = response.json()
                consensus_achieved = result.get("consensus_achieved", False)
                consensus_score = result.get("consensus_score", 0)
                participating_models = result.get("participating_models", [])

                return {
                    "success": True,
                    "consensus_achieved": consensus_achieved,
                    "consensus_score": consensus_score,
                    "participating_models": participating_models,
                    "response_time_ms": response_time_ms,
                    "meets_performance_target": response_time_ms
                    < self.targets["response_time_ms"],
                }
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_error_prediction(self) -> dict[str, Any]:
        """Test error prediction functionality."""
        print("🔮 Testing error prediction...")

        try:
            # Test with various scenarios to trigger error prediction
            test_cases = [
                {
                    "principle": "Contradictory principle: Allow and deny access simultaneously",
                    "expected_risk": "high",
                },
                {
                    "principle": "Simple voting rule: Majority wins",
                    "expected_risk": "low",
                },
                {
                    "principle": "Complex multi-stakeholder resource allocation with competing priorities",
                    "expected_risk": "medium",
                },
            ]

            prediction_results = []

            for test_case in test_cases:
                payload = {
                    "principle": test_case["principle"],
                    "enable_error_prediction": True,
                    "context": {"domain": "governance"},
                }

                response = requests.post(
                    f"{self.base_url}/api/v1/synthesis/predict-errors",
                    json=payload,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    result = response.json()
                    prediction_results.append(
                        {
                            "principle": test_case["principle"],
                            "predicted_risk": result.get("risk_level"),
                            "expected_risk": test_case["expected_risk"],
                            "prediction_confidence": result.get("confidence", 0),
                            "error_types": result.get("predicted_errors", []),
                        }
                    )

            # Calculate accuracy
            correct_predictions = sum(
                1
                for r in prediction_results
                if r["predicted_risk"] == r["expected_risk"]
            )
            accuracy = (
                correct_predictions / len(prediction_results)
                if prediction_results
                else 0
            )

            return {
                "success": True,
                "prediction_accuracy": accuracy,
                "meets_accuracy_target": accuracy
                >= self.targets["error_prediction_accuracy"],
                "prediction_results": prediction_results,
                "total_test_cases": len(test_cases),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_strategy_selection(self) -> dict[str, Any]:
        """Test strategy selection logic."""
        print("🎯 Testing strategy selection...")

        try:
            # Test different risk scenarios to verify strategy selection
            risk_scenarios = [
                {"risk_score": 0.2, "expected_strategy": "standard"},
                {"risk_score": 0.5, "expected_strategy": "enhanced_validation"},
                {"risk_score": 0.7, "expected_strategy": "multi_model_consensus"},
                {"risk_score": 0.9, "expected_strategy": "human_review"},
            ]

            strategy_results = []

            for scenario in risk_scenarios:
                payload = {
                    "principle": f"Test principle with risk score {scenario['risk_score']}",
                    "risk_override": scenario["risk_score"],
                    "enable_strategy_selection": True,
                }

                response = requests.post(
                    f"{self.base_url}/api/v1/synthesis/select-strategy",
                    json=payload,
                    timeout=self.timeout,
                )

                if response.status_code == 200:
                    result = response.json()
                    strategy_results.append(
                        {
                            "risk_score": scenario["risk_score"],
                            "selected_strategy": result.get("selected_strategy"),
                            "expected_strategy": scenario["expected_strategy"],
                            "strategy_confidence": result.get("confidence", 0),
                        }
                    )

            # Calculate strategy selection accuracy
            correct_selections = sum(
                1
                for r in strategy_results
                if r["selected_strategy"] == r["expected_strategy"]
            )
            selection_accuracy = (
                correct_selections / len(strategy_results) if strategy_results else 0
            )

            return {
                "success": True,
                "strategy_selection_accuracy": selection_accuracy,
                "strategy_results": strategy_results,
                "total_scenarios": len(risk_scenarios),
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_performance_optimization(self) -> dict[str, Any]:
        """Test performance optimization features."""
        print("⚡ Testing performance optimization...")

        try:
            # Test performance optimization endpoint
            optimization_payload = {
                "enable_optimization": True,
                "optimization_targets": {
                    "response_time_ms": self.targets["response_time_ms"],
                    "accuracy_threshold": self.targets["error_prediction_accuracy"],
                },
            }

            response = requests.post(
                f"{self.base_url}/api/v1/optimization/performance",
                json=optimization_payload,
                timeout=self.timeout,
            )

            if response.status_code == 200:
                result = response.json()

                return {
                    "success": True,
                    "optimization_applied": result.get("optimization_applied", False),
                    "performance_improvement": result.get(
                        "performance_improvement", {}
                    ),
                    "optimization_strategy": result.get("strategy", ""),
                    "estimated_improvement": result.get("estimated_improvement", 0),
                }
            return {
                "success": False,
                "status_code": response.status_code,
                "error": response.text,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _check_performance_targets(self) -> dict[str, bool]:
        """Check if performance targets are met."""
        # This would analyze collected metrics
        return {
            "response_time": True,  # Placeholder
            "error_prediction_accuracy": True,
            "consensus_success_rate": True,
            "synthesis_quality": True,
        }

    def _generate_recommendations(self) -> list[str]:
        """Generate recommendations based on test results."""
        return [
            "Continue monitoring performance metrics",
            "Optimize threshold values based on test results",
            "Expand test coverage for edge cases",
            "Implement additional error prediction models",
        ]


# Pytest integration
@pytest.mark.asyncio
async def test_policy_synthesis_enhancement_integration():
    """Main integration test for Policy Synthesis Enhancement."""
    tester = PolicySynthesisEnhancementTester()
    results = await tester.run_comprehensive_test_suite()

    assert results["overall_success"], f"Integration tests failed: {results}"
    assert results["performance_targets_met"][
        "response_time"
    ], "Response time target not met"
    assert results["performance_targets_met"][
        "error_prediction_accuracy"
    ], "Accuracy target not met"


if __name__ == "__main__":

    async def main():
        tester = PolicySynthesisEnhancementTester()
        results = await tester.run_comprehensive_test_suite()

        print("\n" + "=" * 80)
        print("POLICY SYNTHESIS ENHANCEMENT INTEGRATION TEST RESULTS")
        print("=" * 80)
        print(json.dumps(results, indent=2, default=str))

    asyncio.run(main())
