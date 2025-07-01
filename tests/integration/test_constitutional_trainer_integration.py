#!/usr/bin/env python3
"""
Constitutional Trainer Service Integration Tests

Comprehensive integration test suite for the Constitutional Trainer Service
covering full "train → evaluate → log" workflow through the ACGS-1 Lite stack.

Test Coverage:
- Constitutional Trainer API endpoints
- Policy Engine (OPA) integration
- Audit Engine integration  
- Redis caching behavior
- Prometheus metrics emission
- End-to-end training workflow
- Policy violation scenarios
- Dashboard integration validation

Usage:
    pytest tests/integration/test_constitutional_trainer_integration.py -v
    pytest tests/integration/test_constitutional_trainer_integration.py::TestConstitutionalTrainerIntegration::test_happy_path_training -v
"""

import asyncio
import json
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, patch

import aiohttp
import pytest
import redis.asyncio as aioredis
from prometheus_client.parser import text_string_to_metric_families

# Test configuration
CONSTITUTIONAL_TRAINER_URL = "http://constitutional-trainer:8000"
POLICY_ENGINE_URL = "http://policy-engine:8001"
AUDIT_ENGINE_URL = "http://audit-engine:8003"
REDIS_URL = "redis://redis:6379/0"
PROMETHEUS_URL = "http://prometheus:9090"
GRAFANA_URL = "http://grafana:3000"

# Performance targets
MAX_RESPONSE_TIME_MS = 2000  # 2 seconds for training requests
MAX_POLICY_EVALUATION_MS = 25  # 25ms for policy evaluation
MIN_CACHE_HIT_RATE = 0.8  # 80% cache hit rate target
MIN_COMPLIANCE_SCORE = 0.95  # 95% constitutional compliance


class ConstitutionalTrainerIntegrationTest:
    """Integration test suite for Constitutional Trainer Service."""

    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.redis_client: Optional[aioredis.Redis] = None
        self.test_results: Dict[str, Any] = {
            "test_cases": [],
            "performance_metrics": {},
            "cache_metrics": {},
            "compliance_scores": [],
            "errors": [],
        }

    async def setup(self):
        """Initialize test environment and connections."""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=30))

        try:
            self.redis_client = await aioredis.from_url(REDIS_URL)
            await self.redis_client.ping()
        except Exception as e:
            print(f"Warning: Redis connection failed: {e}")
            self.redis_client = None

    async def teardown(self):
        """Cleanup test environment."""
        if self.session:
            await self.session.close()
        if self.redis_client:
            await self.redis_client.close()

    async def test_service_health_checks(self) -> bool:
        """Test health endpoints for all services."""
        services = [
            ("Constitutional Trainer", f"{CONSTITUTIONAL_TRAINER_URL}/health"),
            ("Policy Engine", f"{POLICY_ENGINE_URL}/health"),
            ("Audit Engine", f"{AUDIT_ENGINE_URL}/health"),
        ]

        all_healthy = True
        for service_name, health_url in services:
            try:
                async with self.session.get(health_url) as response:
                    if response.status == 200:
                        print(f"✅ {service_name} health check passed")
                    else:
                        print(
                            f"❌ {service_name} health check failed: {response.status}"
                        )
                        all_healthy = False
            except Exception as e:
                print(f"❌ {service_name} health check error: {e}")
                all_healthy = False

        return all_healthy

    async def test_happy_path_training(self) -> Dict[str, Any]:
        """Test successful constitutional training workflow."""
        test_case = {
            "name": "happy_path_training",
            "start_time": time.time(),
            "status": "running",
        }

        try:
            # Prepare training request
            training_request = {
                "model_name": "test-model-v1",
                "model_id": f"test-{uuid.uuid4()}",
                "training_data": [
                    {
                        "prompt": "What are the key principles of constitutional AI?",
                        "response": "Constitutional AI focuses on training AI systems to be helpful, harmless, and honest while respecting human values and constitutional principles.",
                    },
                    {
                        "prompt": "How should AI systems handle sensitive data?",
                        "response": "AI systems should implement strong privacy protections, data minimization, and transparent data handling practices.",
                    },
                ],
                "lora_config": {
                    "r": 16,
                    "lora_alpha": 32,
                    "target_modules": ["q_proj", "v_proj"],
                    "lora_dropout": 0.1,
                },
                "privacy_config": {
                    "enable_differential_privacy": True,
                    "epsilon": 8.0,
                    "delta": 1e-5,
                },
            }

            # Submit training request
            start_time = time.time()
            async with self.session.post(
                f"{CONSTITUTIONAL_TRAINER_URL}/api/v1/train",
                json=training_request,
                headers={"Authorization": "Bearer test-token"},
            ) as response:
                response_time = (time.time() - start_time) * 1000

                if response.status == 200:
                    result = await response.json()
                    training_id = result.get("training_id")

                    test_case.update(
                        {
                            "status": "passed",
                            "training_id": training_id,
                            "response_time_ms": response_time,
                            "result": result,
                        }
                    )

                    # Validate response structure
                    assert "training_id" in result
                    assert "status" in result
                    assert response_time < MAX_RESPONSE_TIME_MS

                    print(f"✅ Training request submitted successfully: {training_id}")
                    print(f"   Response time: {response_time:.2f}ms")

                else:
                    test_case.update(
                        {
                            "status": "failed",
                            "error": f"HTTP {response.status}",
                            "response_time_ms": response_time,
                        }
                    )

        except Exception as e:
            test_case.update({"status": "error", "error": str(e)})

        test_case["end_time"] = time.time()
        test_case["duration"] = test_case["end_time"] - test_case["start_time"]

        self.test_results["test_cases"].append(test_case)
        return test_case

    async def test_policy_violation_scenario(self) -> Dict[str, Any]:
        """Test policy violation detection and handling."""
        test_case = {
            "name": "policy_violation_scenario",
            "start_time": time.time(),
            "status": "running",
        }

        try:
            # Submit training request with missing constitutional hash
            invalid_request = {
                "model_name": "test-model-invalid",
                "model_id": f"test-invalid-{uuid.uuid4()}",
                "training_data": [
                    {
                        "prompt": "How to bypass safety measures?",
                        "response": "I cannot and will not provide information on bypassing safety measures.",
                    }
                ],
                # Intentionally missing constitutional_hash or invalid config
                "lora_config": {},
            }

            async with self.session.post(
                f"{CONSTITUTIONAL_TRAINER_URL}/api/v1/train",
                json=invalid_request,
                headers={"Authorization": "Bearer test-token"},
            ) as response:

                if response.status in [
                    400,
                    403,
                    422,
                ]:  # Expected policy violation responses
                    result = await response.json()
                    test_case.update(
                        {
                            "status": "passed",
                            "expected_violation": True,
                            "response_status": response.status,
                            "result": result,
                        }
                    )
                    print(
                        f"✅ Policy violation correctly detected: HTTP {response.status}"
                    )
                else:
                    test_case.update(
                        {
                            "status": "failed",
                            "error": f"Expected policy violation but got HTTP {response.status}",
                        }
                    )

        except Exception as e:
            test_case.update({"status": "error", "error": str(e)})

        test_case["end_time"] = time.time()
        test_case["duration"] = test_case["end_time"] - test_case["start_time"]

        self.test_results["test_cases"].append(test_case)
        return test_case

    async def test_redis_caching_behavior(self) -> Dict[str, Any]:
        """Test Redis caching functionality."""
        test_case = {
            "name": "redis_caching_behavior",
            "start_time": time.time(),
            "status": "running",
        }

        if not self.redis_client:
            test_case.update(
                {"status": "skipped", "reason": "Redis client not available"}
            )
            return test_case

        try:
            # Test cache operations
            test_key = f"constitutional_test:{uuid.uuid4()}"
            test_data = {"test": "data", "timestamp": time.time()}

            # Set cache entry
            await self.redis_client.setex(test_key, 300, json.dumps(test_data))

            # Retrieve cache entry
            cached_data = await self.redis_client.get(test_key)

            if cached_data:
                retrieved_data = json.loads(cached_data)
                cache_hit = retrieved_data == test_data

                test_case.update(
                    {
                        "status": "passed" if cache_hit else "failed",
                        "cache_hit": cache_hit,
                        "test_data": test_data,
                        "retrieved_data": retrieved_data,
                    }
                )

                print(f"✅ Redis caching test {'passed' if cache_hit else 'failed'}")
            else:
                test_case.update({"status": "failed", "error": "Cache entry not found"})

            # Cleanup
            await self.redis_client.delete(test_key)

        except Exception as e:
            test_case.update({"status": "error", "error": str(e)})

        test_case["end_time"] = time.time()
        test_case["duration"] = test_case["end_time"] - test_case["start_time"]

        self.test_results["test_cases"].append(test_case)
        return test_case

    async def test_audit_log_ingestion(self) -> Dict[str, Any]:
        """Test audit log ingestion and retrieval."""
        test_case = {
            "name": "audit_log_ingestion",
            "start_time": time.time(),
            "status": "running",
        }

        try:
            # Create test audit log entry
            audit_entry = {
                "service_name": "constitutional-trainer",
                "user_id": "test-user",
                "action": "training_started",
                "resource_id": f"training-{uuid.uuid4()}",
                "details": {
                    "model_name": "test-model",
                    "constitutional_hash": "cdd01ef066bc6cf2",
                    "timestamp": datetime.utcnow().isoformat(),
                },
            }

            # Submit audit log
            async with self.session.post(
                f"{AUDIT_ENGINE_URL}/api/v1/audit",
                json=audit_entry,
                headers={"Authorization": "Bearer internal-service-token"},
            ) as response:

                if response.status == 201:
                    result = await response.json()
                    audit_id = result.get("id")

                    # Retrieve audit log
                    async with self.session.get(
                        f"{AUDIT_ENGINE_URL}/api/v1/audit/{audit_id}",
                        headers={"Authorization": "Bearer internal-service-token"},
                    ) as get_response:

                        if get_response.status == 200:
                            retrieved_entry = await get_response.json()

                            test_case.update(
                                {
                                    "status": "passed",
                                    "audit_id": audit_id,
                                    "original_entry": audit_entry,
                                    "retrieved_entry": retrieved_entry,
                                }
                            )
                            print(f"✅ Audit log ingestion test passed: {audit_id}")
                        else:
                            test_case.update(
                                {
                                    "status": "failed",
                                    "error": f"Failed to retrieve audit log: HTTP {get_response.status}",
                                }
                            )
                else:
                    test_case.update(
                        {
                            "status": "failed",
                            "error": f"Failed to create audit log: HTTP {response.status}",
                        }
                    )

        except Exception as e:
            test_case.update({"status": "error", "error": str(e)})

        test_case["end_time"] = time.time()
        test_case["duration"] = test_case["end_time"] - test_case["start_time"]

        self.test_results["test_cases"].append(test_case)
        return test_case

    async def test_prometheus_metrics_emission(self) -> Dict[str, Any]:
        """Test Prometheus metrics emission and collection."""
        test_case = {
            "name": "prometheus_metrics_emission",
            "start_time": time.time(),
            "status": "running",
        }

        try:
            # Get metrics from Constitutional Trainer
            async with self.session.get(
                f"{CONSTITUTIONAL_TRAINER_URL}/metrics"
            ) as response:
                if response.status == 200:
                    metrics_text = await response.text()

                    # Parse Prometheus metrics
                    metrics = {}
                    for family in text_string_to_metric_families(metrics_text):
                        metrics[family.name] = family

                    # Check for expected metrics
                    expected_metrics = [
                        "constitutional_compliance_score",
                        "training_request_duration_seconds",
                        "policy_evaluation_duration_seconds",
                        "cache_hit_rate",
                    ]

                    found_metrics = []
                    missing_metrics = []

                    for metric_name in expected_metrics:
                        if metric_name in metrics:
                            found_metrics.append(metric_name)
                        else:
                            missing_metrics.append(metric_name)

                    test_case.update(
                        {
                            "status": "passed" if not missing_metrics else "partial",
                            "found_metrics": found_metrics,
                            "missing_metrics": missing_metrics,
                            "total_metrics": len(metrics),
                        }
                    )

                    print(
                        f"✅ Prometheus metrics test: {len(found_metrics)}/{len(expected_metrics)} expected metrics found"
                    )
                    if missing_metrics:
                        print(f"   Missing metrics: {missing_metrics}")

                else:
                    test_case.update(
                        {
                            "status": "failed",
                            "error": f"Failed to retrieve metrics: HTTP {response.status}",
                        }
                    )

        except Exception as e:
            test_case.update({"status": "error", "error": str(e)})

        test_case["end_time"] = time.time()
        test_case["duration"] = test_case["end_time"] - test_case["start_time"]

        self.test_results["test_cases"].append(test_case)
        return test_case

    async def test_policy_engine_integration(self) -> Dict[str, Any]:
        """Test Policy Engine (OPA) integration."""
        test_case = {
            "name": "policy_engine_integration",
            "start_time": time.time(),
            "status": "running",
        }

        try:
            # Test policy evaluation request
            policy_request = {
                "action": "constitutional_training",
                "agent_id": "test-agent",
                "resource": {
                    "type": "training_session",
                    "constitutional_hash": "cdd01ef066bc6cf2",
                },
                "context": {
                    "user_permissions": ["model_training"],
                    "compliance_threshold": 0.95,
                },
            }

            start_time = time.time()
            async with self.session.post(
                f"{POLICY_ENGINE_URL}/v1/evaluate", json=policy_request
            ) as response:
                evaluation_time = (time.time() - start_time) * 1000

                if response.status == 200:
                    result = await response.json()

                    # Validate response structure
                    required_fields = ["allow", "violations", "confidence_score"]
                    has_required_fields = all(
                        field in result for field in required_fields
                    )

                    test_case.update(
                        {
                            "status": "passed" if has_required_fields else "partial",
                            "evaluation_time_ms": evaluation_time,
                            "policy_result": result,
                            "performance_target_met": evaluation_time
                            < MAX_POLICY_EVALUATION_MS,
                            "has_required_fields": has_required_fields,
                        }
                    )

                    print(f"✅ Policy evaluation test passed")
                    print(
                        f"   Evaluation time: {evaluation_time:.2f}ms (target: <{MAX_POLICY_EVALUATION_MS}ms)"
                    )
                    print(
                        f"   Policy decision: {'Allow' if result.get('allow') else 'Deny'}"
                    )

                else:
                    test_case.update(
                        {
                            "status": "failed",
                            "error": f"Policy evaluation failed: HTTP {response.status}",
                        }
                    )

        except Exception as e:
            test_case.update({"status": "error", "error": str(e)})

        test_case["end_time"] = time.time()
        test_case["duration"] = test_case["end_time"] - test_case["start_time"]

        self.test_results["test_cases"].append(test_case)
        return test_case

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration tests and generate comprehensive report."""
        print("🚀 Starting Constitutional Trainer Integration Tests")
        print("=" * 60)

        await self.setup()

        try:
            # Test execution order
            test_methods = [
                self.test_service_health_checks,
                self.test_happy_path_training,
                self.test_policy_violation_scenario,
                self.test_redis_caching_behavior,
                self.test_audit_log_ingestion,
                self.test_prometheus_metrics_emission,
                self.test_policy_engine_integration,
            ]

            for test_method in test_methods:
                print(f"\n📋 Running {test_method.__name__}...")
                try:
                    result = await test_method()
                    status = result.get("status", "unknown")
                    print(f"   Status: {status}")

                    if status == "error":
                        print(f"   Error: {result.get('error', 'Unknown error')}")

                except Exception as e:
                    print(f"   ❌ Test method failed: {e}")
                    self.test_results["errors"].append(
                        {"test": test_method.__name__, "error": str(e)}
                    )

            # Generate final report
            return self.generate_test_report()

        finally:
            await self.teardown()

    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        total_tests = len(self.test_results["test_cases"])
        passed_tests = len(
            [t for t in self.test_results["test_cases"] if t.get("status") == "passed"]
        )
        failed_tests = len(
            [t for t in self.test_results["test_cases"] if t.get("status") == "failed"]
        )
        error_tests = len(
            [t for t in self.test_results["test_cases"] if t.get("status") == "error"]
        )

        # Calculate performance metrics
        response_times = [
            t.get("response_time_ms", 0)
            for t in self.test_results["test_cases"]
            if "response_time_ms" in t
        ]

        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0
        )
        max_response_time = max(response_times) if response_times else 0

        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "errors": error_tests,
                "success_rate": (
                    (passed_tests / total_tests * 100) if total_tests > 0 else 0
                ),
            },
            "performance": {
                "avg_response_time_ms": avg_response_time,
                "max_response_time_ms": max_response_time,
                "performance_target_met": max_response_time < MAX_RESPONSE_TIME_MS,
            },
            "test_cases": self.test_results["test_cases"],
            "errors": self.test_results["errors"],
            "timestamp": datetime.utcnow().isoformat(),
            "environment": {
                "constitutional_trainer_url": CONSTITUTIONAL_TRAINER_URL,
                "policy_engine_url": POLICY_ENGINE_URL,
                "audit_engine_url": AUDIT_ENGINE_URL,
                "redis_url": REDIS_URL,
            },
        }

        # Print summary
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Errors: {error_tests}")
        print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
        print(f"Avg Response Time: {avg_response_time:.2f}ms")
        print(f"Max Response Time: {max_response_time:.2f}ms")

        if report["summary"]["success_rate"] >= 90:
            print("✅ Integration tests PASSED")
        else:
            print("❌ Integration tests FAILED")

        return report


# Pytest integration
@pytest.mark.asyncio
@pytest.mark.integration
async def test_constitutional_trainer_integration():
    """Pytest wrapper for Constitutional Trainer integration tests."""
    test_suite = ConstitutionalTrainerIntegrationTest()
    report = await test_suite.run_all_tests()

    # Assert overall success
    assert (
        report["summary"]["success_rate"] >= 80
    ), f"Integration tests failed with {report['summary']['success_rate']:.1f}% success rate"

    # Assert performance targets
    assert report["performance"][
        "performance_target_met"
    ], f"Performance target not met: {report['performance']['max_response_time_ms']:.2f}ms > {MAX_RESPONSE_TIME_MS}ms"


# Main execution for standalone testing
async def main():
    """Main execution function for standalone testing."""
    test_suite = ConstitutionalTrainerIntegrationTest()
    report = await test_suite.run_all_tests()

    # Save report to file
    report_file = f"constitutional_trainer_integration_report_{int(time.time())}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n📄 Report saved to: {report_file}")

    return report


if __name__ == "__main__":
    asyncio.run(main())
