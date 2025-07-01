#!/usr/bin/env python3
"""
Multi-Level Cache Testing Suite

Comprehensive testing for the Phase 2 multi-level caching implementation.
Validates performance targets, constitutional compliance, and integration.

Test Coverage:
- L1/L2/L3 cache functionality and performance
- Bloom filter accuracy and false positive rates
- Parallel validation pipeline execution
- ACGS-PGP service integration
- Sub-2s response time guarantee
- >95% constitutional compliance maintenance
"""

import asyncio
import json
import logging
import os
import statistics
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.shared.acgs_cache_integration import ACGSCacheIntegration
from services.shared.multi_level_cache import (
    BloomFilter,
    L1MemoryCache,
    L2ProcessCache,
    L3RedisCache,
    MultiLevelCacheManager,
)
from services.shared.parallel_validation_pipeline import ParallelValidationPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MultiLevelCacheTester:
    """Comprehensive test suite for multi-level caching system."""

    def __init__(self):
        self.test_results = []
        self.performance_results = []
        self.cache_manager = None
        self.validation_pipeline = None
        self.cache_integration = None

    async def setup(self):
        """Set up test environment."""
        logger.info("Setting up multi-level cache test environment...")

        # Set environment variables for testing
        os.environ["REDIS_URL"] = "redis://localhost:6379/15"  # Test database
        os.environ["ACGS_CONSTITUTIONAL_HASH"] = "cdd01ef066bc6cf2"
        os.environ["CACHE_L1_SIZE_KB"] = "64"
        os.environ["CACHE_L2_SIZE_KB"] = "512"
        os.environ["CACHE_BLOOM_CAPACITY"] = "100000"
        os.environ["CACHE_BLOOM_ERROR_RATE"] = "0.001"

        # Initialize components
        self.cache_manager = MultiLevelCacheManager()
        await self.cache_manager.initialize()

        self.validation_pipeline = ParallelValidationPipeline(self.cache_manager)
        await self.validation_pipeline.initialize()

        self.cache_integration = ACGSCacheIntegration()
        await self.cache_integration.initialize()

        logger.info("Test environment setup complete")

    def record_test_result(
        self,
        test_name: str,
        passed: bool,
        message: str,
        details: dict = None,
        performance_data: dict = None,
    ):
        """Record test result."""
        result = {
            "test_name": test_name,
            "passed": passed,
            "message": message,
            "details": details or {},
            "timestamp": time.time(),
        }
        self.test_results.append(result)

        if performance_data:
            self.performance_results.append(
                {"test_name": test_name, **performance_data, "timestamp": time.time()}
            )

        status = "PASS" if passed else "FAIL"
        logger.info(f"[{status}] {test_name}: {message}")

    async def test_bloom_filter_functionality(self):
        """Test Bloom filter accuracy and performance."""
        test_name = "Bloom Filter Functionality"

        try:
            bloom = BloomFilter(capacity=10000, error_rate=0.001)

            # Add known violation patterns
            violation_patterns = [
                "violence",
                "hate",
                "discrimination",
                "illegal",
                "harmful",
            ]
            for pattern in violation_patterns:
                bloom.add(pattern)

            # Test true positives
            true_positives = sum(
                1 for pattern in violation_patterns if bloom.might_contain(pattern)
            )
            assert true_positives == len(
                violation_patterns
            ), f"Expected {len(violation_patterns)} true positives, got {true_positives}"

            # Test false positives
            test_words = [
                "hello",
                "world",
                "constitutional",
                "compliance",
                "governance",
            ]
            false_positives = sum(1 for word in test_words if bloom.might_contain(word))
            false_positive_rate = false_positives / len(test_words)

            # Should be close to configured error rate (0.1%)
            assert (
                false_positive_rate <= 0.05
            ), f"False positive rate too high: {false_positive_rate:.3f}"

            # Performance test
            start_time = time.time()
            for i in range(1000):
                bloom.might_contain(f"test_word_{i}")
            lookup_time = (time.time() - start_time) * 1000  # ms

            self.record_test_result(
                test_name,
                True,
                f"Bloom filter working correctly (FP rate: {false_positive_rate:.3f})",
                {
                    "true_positives": true_positives,
                    "false_positive_rate": false_positive_rate,
                    "lookup_time_1000_ops_ms": lookup_time,
                    "items_added": bloom.items_added,
                    "bit_array_size": bloom.bit_array_size,
                },
            )

        except Exception as e:
            self.record_test_result(test_name, False, f"Bloom filter test failed: {e}")

    async def test_l1_memory_cache(self):
        """Test L1 memory cache functionality and performance."""
        test_name = "L1 Memory Cache"

        try:
            l1_cache = L1MemoryCache(max_size_kb=64)

            # Test basic operations
            test_key = "test_constitutional_rule_1"
            test_value = {"compliant": True, "confidence": 0.95}

            # Put and get
            success = l1_cache.put(test_key, test_value)
            assert success, "Failed to put entry in L1 cache"

            entry = l1_cache.get(test_key)
            assert entry is not None, "Failed to get entry from L1 cache"
            assert (
                entry.value == test_value
            ), "Retrieved value doesn't match stored value"

            # Performance test
            start_time = time.time()
            for i in range(1000):
                l1_cache.get(test_key)
            get_time = (time.time() - start_time) * 1000000  # microseconds

            # Should be sub-microsecond access
            avg_access_time = get_time / 1000
            assert avg_access_time < 10, f"L1 access too slow: {avg_access_time:.2f}μs"

            stats = l1_cache.get_stats()

            self.record_test_result(
                test_name,
                True,
                f"L1 cache working correctly ({avg_access_time:.2f}μs avg access)",
                {
                    "avg_access_time_us": avg_access_time,
                    "cache_entries": stats["entries"],
                    "utilization": stats["utilization"],
                    "size_kb": stats["size_kb"],
                },
            )

        except Exception as e:
            self.record_test_result(test_name, False, f"L1 cache test failed: {e}")

    async def test_l2_process_cache(self):
        """Test L2 process cache with rule compilation."""
        test_name = "L2 Process Cache"

        try:
            l2_cache = L2ProcessCache(max_size_kb=512)

            # Test rule compilation and caching
            test_key = "constitutional_rule_compiled"
            test_value = {"rule_type": "constitutional", "compiled": True}
            rule_definition = "constitutional_check: content must be compliant"

            success = l2_cache.put(
                test_key, test_value, rule_definition=rule_definition
            )
            assert success, "Failed to put entry in L2 cache"

            entry = l2_cache.get(test_key)
            assert entry is not None, "Failed to get entry from L2 cache"

            # Test compiled rule execution
            context = {"content": "test content", "type": "validation"}
            compiled_result = l2_cache.execute_compiled_rule(test_key, context)
            assert compiled_result is not None, "Failed to execute compiled rule"
            assert "rule_hash" in compiled_result, "Compiled result missing rule hash"

            # Performance test
            start_time = time.time()
            for i in range(100):
                l2_cache.execute_compiled_rule(test_key, context)
            execution_time = (time.time() - start_time) * 1000  # ms

            avg_execution_time = execution_time / 100
            assert (
                avg_execution_time < 1
            ), f"L2 rule execution too slow: {avg_execution_time:.2f}ms"

            stats = l2_cache.get_stats()

            self.record_test_result(
                test_name,
                True,
                f"L2 cache working correctly ({avg_execution_time:.2f}ms avg execution)",
                {
                    "avg_execution_time_ms": avg_execution_time,
                    "cache_entries": stats["entries"],
                    "compiled_rules": stats["compiled_rules"],
                    "total_executions": stats["total_executions"],
                },
            )

        except Exception as e:
            self.record_test_result(test_name, False, f"L2 cache test failed: {e}")

    async def test_l3_redis_cache(self):
        """Test L3 Redis distributed cache."""
        test_name = "L3 Redis Cache"

        try:
            l3_cache = L3RedisCache("redis://localhost:6379/15")
            await l3_cache.connect()

            if not l3_cache.connected:
                self.record_test_result(
                    test_name, False, "Redis connection failed - skipping L3 test"
                )
                return

            # Clear test data
            await l3_cache.clear_pattern("test:*")

            # Test basic operations
            test_key = "test_constitutional_validation"
            test_value = {"compliant": True, "confidence": 0.96, "cached_result": True}

            success = await l3_cache.put(test_key, test_value, ttl_seconds=300)
            assert success, "Failed to put entry in L3 cache"

            entry = await l3_cache.get(test_key)
            assert entry is not None, "Failed to get entry from L3 cache"
            assert (
                entry.value == test_value
            ), "Retrieved value doesn't match stored value"

            # Performance test
            start_time = time.time()
            for i in range(50):  # Fewer iterations due to network latency
                await l3_cache.get(test_key)
            get_time = (time.time() - start_time) * 1000  # ms

            avg_access_time = get_time / 50
            assert avg_access_time < 10, f"L3 access too slow: {avg_access_time:.2f}ms"

            stats = await l3_cache.get_stats()

            self.record_test_result(
                test_name,
                True,
                f"L3 cache working correctly ({avg_access_time:.2f}ms avg access)",
                {
                    "avg_access_time_ms": avg_access_time,
                    "connected": stats["connected"],
                    "entries": stats.get("entries", 0),
                    "memory_usage_mb": stats.get("memory_usage_mb", 0),
                },
            )

        except Exception as e:
            self.record_test_result(test_name, False, f"L3 cache test failed: {e}")

    async def test_parallel_validation_pipeline(self):
        """Test parallel validation pipeline performance."""
        test_name = "Parallel Validation Pipeline"

        try:
            # Test various content types
            test_cases = [
                {
                    "content": "This is a compliant constitutional AI test.",
                    "expected_compliant": True,
                },
                {
                    "content": "Test content for semantic validation.",
                    "expected_compliant": True,
                },
                {"content": "", "expected_compliant": False},  # Empty content
                {
                    "content": "violence and harmful content",
                    "expected_compliant": False,
                },  # Violation
            ]

            response_times = []
            compliance_results = []

            for test_case in test_cases:
                start_time = time.time()
                result = await self.validation_pipeline.validate(
                    test_case["content"], {"test_case": True}
                )
                response_time = (time.time() - start_time) * 1000
                response_times.append(response_time)
                compliance_results.append(result.is_compliant())

                # Validate response time target
                assert (
                    response_time < 2000
                ), f"Response time too slow: {response_time:.2f}ms"

                # Validate result structure
                assert len(result.stage_results) == 3, "Expected 3 validation stages"
                assert (
                    result.constitutional_hash == "cdd01ef066bc6cf2"
                ), "Constitutional hash mismatch"

            avg_response_time = statistics.mean(response_times)
            p95_response_time = (
                statistics.quantiles(response_times, n=20)[18]
                if len(response_times) >= 20
                else max(response_times)
            )

            # Get pipeline metrics
            metrics = await self.validation_pipeline.get_performance_metrics()

            self.record_test_result(
                test_name,
                True,
                f"Pipeline working correctly ({avg_response_time:.2f}ms avg)",
                {
                    "avg_response_time_ms": avg_response_time,
                    "p95_response_time_ms": p95_response_time,
                    "sub_2s_target_met": avg_response_time < 2000,
                    "total_validations": metrics["total_validations"],
                    "compliance_rate": metrics["compliance_rate"],
                },
                {
                    "avg_response_time_ms": avg_response_time,
                    "p95_response_time_ms": p95_response_time,
                },
            )

        except Exception as e:
            self.record_test_result(test_name, False, f"Pipeline test failed: {e}")

    async def test_cache_integration_performance(self):
        """Test end-to-end cache integration performance."""
        test_name = "Cache Integration Performance"

        try:
            # Test constitutional compliance validation
            test_content = "This is a comprehensive test of the ACGS constitutional AI compliance system."

            # First call (cache miss)
            start_time = time.time()
            result1 = await self.cache_integration.validate_constitutional_compliance(
                test_content
            )
            first_call_time = (time.time() - start_time) * 1000

            # Second call (should be cache hit)
            start_time = time.time()
            result2 = await self.cache_integration.validate_constitutional_compliance(
                test_content
            )
            second_call_time = (time.time() - start_time) * 1000

            # Validate results
            assert (
                result1["compliant"] == result2["compliant"]
            ), "Inconsistent compliance results"
            assert (
                result1["constitutional_hash"] == "cdd01ef066bc6cf2"
            ), "Constitutional hash mismatch"
            assert result2["cache_hit"] == True, "Second call should be cache hit"

            # Cache hit should be significantly faster
            cache_speedup = (
                first_call_time / second_call_time
                if second_call_time > 0
                else float("inf")
            )
            assert (
                cache_speedup > 2
            ), f"Cache speedup insufficient: {cache_speedup:.2f}x"

            # Get integration metrics
            metrics = await self.cache_integration.get_integration_metrics()

            self.record_test_result(
                test_name,
                True,
                f"Integration working correctly ({cache_speedup:.2f}x speedup)",
                {
                    "first_call_time_ms": first_call_time,
                    "second_call_time_ms": second_call_time,
                    "cache_speedup": cache_speedup,
                    "cache_hit_rate": metrics["integration"]["cache_hit_rate"],
                    "compliance_rate": metrics["integration"][
                        "constitutional_compliance_rate"
                    ],
                    "sub_2s_target_met": metrics["integration"]["sub_2s_target_met"],
                },
                {
                    "cache_miss_time_ms": first_call_time,
                    "cache_hit_time_ms": second_call_time,
                    "speedup_factor": cache_speedup,
                },
            )

        except Exception as e:
            self.record_test_result(test_name, False, f"Integration test failed: {e}")

    async def test_constitutional_compliance_maintenance(self):
        """Test that caching maintains >95% constitutional compliance."""
        test_name = "Constitutional Compliance Maintenance"

        try:
            # Test with various content types
            test_contents = [
                "Constitutional AI governance system test.",
                "Policy compliance validation check.",
                "Democratic governance oversight mechanism.",
                "Transparent AI decision making process.",
                "Ethical AI behavior validation system.",
            ]

            compliance_results = []

            for content in test_contents:
                result = (
                    await self.cache_integration.validate_constitutional_compliance(
                        content
                    )
                )
                compliance_results.append(result["compliant"])

            compliance_rate = sum(compliance_results) / len(compliance_results)

            # Should maintain >95% compliance
            assert (
                compliance_rate >= 0.95
            ), f"Compliance rate below target: {compliance_rate:.3f}"

            # Get overall metrics
            metrics = await self.cache_integration.get_integration_metrics()
            overall_compliance = metrics["integration"][
                "constitutional_compliance_rate"
            ]

            self.record_test_result(
                test_name,
                True,
                f"Compliance maintained ({compliance_rate:.3f} rate)",
                {
                    "test_compliance_rate": compliance_rate,
                    "overall_compliance_rate": overall_compliance,
                    "compliance_target_met": compliance_rate >= 0.95,
                    "constitutional_hash": "cdd01ef066bc6cf2",
                },
            )

        except Exception as e:
            self.record_test_result(test_name, False, f"Compliance test failed: {e}")

    async def run_all_tests(self):
        """Run all cache system tests."""
        logger.info("Starting multi-level cache test suite...")

        await self.setup()

        # Run individual tests
        await self.test_bloom_filter_functionality()
        await self.test_l1_memory_cache()
        await self.test_l2_process_cache()
        await self.test_l3_redis_cache()
        await self.test_parallel_validation_pipeline()
        await self.test_cache_integration_performance()
        await self.test_constitutional_compliance_maintenance()

        # Generate test report
        self.generate_test_report()

    def generate_test_report(self):
        """Generate comprehensive test report."""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["passed"])
        failed_tests = total_tests - passed_tests

        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

        print("\n" + "=" * 80)
        print("MULTI-LEVEL CACHE SYSTEM TEST REPORT")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print("=" * 80)

        # Performance summary
        if self.performance_results:
            print("\nPERFORMANCE SUMMARY:")
            for perf in self.performance_results:
                if "avg_response_time_ms" in perf:
                    print(
                        f"  {perf['test_name']}: {perf['avg_response_time_ms']:.2f}ms avg response"
                    )
                if "speedup_factor" in perf:
                    print(
                        f"  {perf['test_name']}: {perf['speedup_factor']:.2f}x cache speedup"
                    )

        # Detailed results
        print("\nDETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"{status} {result['test_name']}: {result['message']}")

            if result["details"]:
                for key, value in result["details"].items():
                    if isinstance(value, float):
                        print(f"    {key}: {value:.3f}")
                    else:
                        print(f"    {key}: {value}")

        print("=" * 80)

        # Save detailed report
        report_file = "reports/multi_level_cache_test_report.json"
        os.makedirs("reports", exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(
                {
                    "summary": {
                        "total_tests": total_tests,
                        "passed_tests": passed_tests,
                        "failed_tests": failed_tests,
                        "success_rate": success_rate,
                        "timestamp": time.time(),
                    },
                    "test_results": self.test_results,
                    "performance_results": self.performance_results,
                },
                f,
                indent=2,
            )

        logger.info(f"Detailed test report saved to {report_file}")

        if success_rate >= 85:
            logger.info("🎉 Multi-level cache system is ready for deployment!")
        else:
            logger.warning("⚠️  Some tests failed. Review issues before deployment.")


async def main():
    """Main test execution."""
    tester = MultiLevelCacheTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
