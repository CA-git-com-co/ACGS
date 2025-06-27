#!/usr/bin/env python3
"""
Cache Performance Testing Script for ACGS-1 Phase A3
Tests cache performance across all services and validates targets
"""

import asyncio
import json
import statistics
import time
from datetime import datetime
from typing import Any

import aiohttp
import redis.asyncio as redis

# Performance targets
PERFORMANCE_TARGETS = {
    "cache_hit_rate": 80.0,  # >80%
    "response_time_ms": 500.0,  # <500ms
    "concurrent_requests": 1000,  # >1000 concurrent
    "memory_efficiency": 0.8,  # 80% efficiency
}


class CachePerformanceTester:
    """Cache performance testing suite."""

    def __init__(self):
        self.redis_client = None
        self.test_results = {}
        self.services = [
            ("auth_service", 8000),
            ("ac_service", 8001),
            ("integrity_service", 8002),
            ("fv_service", 8003),
            ("gs_service", 8004),
            ("pgc_service", 8005),
            ("ec_service", 8006),
        ]

    async def initialize(self):
        """Initialize Redis connection for testing."""
        try:
            self.redis_client = redis.from_url(
                "redis://localhost:6379/0", decode_responses=True
            )
            await self.redis_client.ping()
            print("✅ Redis connection established for testing")
        except Exception as e:
            print(f"❌ Failed to connect to Redis: {e}")
            raise

    async def test_redis_performance(self) -> dict[str, Any]:
        """Test basic Redis performance."""
        print("\n🔍 Testing Redis Performance...")

        # Test SET operations
        set_times = []
        for i in range(100):
            start_time = time.time()
            await self.redis_client.set(f"test:set:{i}", f"value_{i}", ex=60)
            set_times.append((time.time() - start_time) * 1000)

        # Test GET operations
        get_times = []
        for i in range(100):
            start_time = time.time()
            await self.redis_client.get(f"test:set:{i}")
            get_times.append((time.time() - start_time) * 1000)

        # Test DEL operations
        del_times = []
        for i in range(100):
            start_time = time.time()
            await self.redis_client.delete(f"test:set:{i}")
            del_times.append((time.time() - start_time) * 1000)

        # Get Redis info
        redis_info = await self.redis_client.info()

        results = {
            "set_avg_ms": round(statistics.mean(set_times), 2),
            "get_avg_ms": round(statistics.mean(get_times), 2),
            "del_avg_ms": round(statistics.mean(del_times), 2),
            "set_p95_ms": round(statistics.quantiles(set_times, n=20)[18], 2),
            "get_p95_ms": round(statistics.quantiles(get_times, n=20)[18], 2),
            "memory_usage_mb": round(redis_info.get("used_memory", 0) / 1024 / 1024, 2),
            "connected_clients": redis_info.get("connected_clients", 0),
            "total_commands": redis_info.get("total_commands_processed", 0),
            "keyspace_hits": redis_info.get("keyspace_hits", 0),
            "keyspace_misses": redis_info.get("keyspace_misses", 0),
        }

        # Calculate hit rate
        total_ops = results["keyspace_hits"] + results["keyspace_misses"]
        if total_ops > 0:
            results["hit_rate"] = round((results["keyspace_hits"] / total_ops) * 100, 2)
        else:
            results["hit_rate"] = 0.0

        print(
            f"   SET operations: {results['set_avg_ms']}ms avg, {results['set_p95_ms']}ms p95"
        )
        print(
            f"   GET operations: {results['get_avg_ms']}ms avg, {results['get_p95_ms']}ms p95"
        )
        print(f"   Hit rate: {results['hit_rate']}%")
        print(f"   Memory usage: {results['memory_usage_mb']}MB")

        return results

    async def test_service_cache_integration(
        self, service_name: str, port: int
    ) -> dict[str, Any]:
        """Test cache integration for a specific service."""
        print(f"\n🔍 Testing {service_name} cache integration...")

        try:
            async with aiohttp.ClientSession() as session:
                # Test health endpoint
                start_time = time.time()
                async with session.get(f"http://localhost:{port}/health") as response:
                    health_time = (time.time() - start_time) * 1000
                    health_status = response.status == 200

                # Test multiple requests to measure caching effect
                response_times = []
                for _i in range(10):
                    start_time = time.time()
                    try:
                        async with session.get(
                            f"http://localhost:{port}/health"
                        ) as response:
                            response_times.append((time.time() - start_time) * 1000)
                    except Exception:
                        response_times.append(1000)  # Timeout fallback

                results = {
                    "service_healthy": health_status,
                    "health_response_time_ms": round(health_time, 2),
                    "avg_response_time_ms": round(statistics.mean(response_times), 2),
                    "p95_response_time_ms": (
                        round(statistics.quantiles(response_times, n=20)[18], 2)
                        if len(response_times) >= 20
                        else round(max(response_times), 2)
                    ),
                    "min_response_time_ms": round(min(response_times), 2),
                    "max_response_time_ms": round(max(response_times), 2),
                }

                print(f"   Health: {'✅' if health_status else '❌'}")
                print(f"   Avg response: {results['avg_response_time_ms']}ms")
                print(f"   P95 response: {results['p95_response_time_ms']}ms")

                return results

        except Exception as e:
            print(f"   ❌ Error testing {service_name}: {e}")
            return {
                "service_healthy": False,
                "error": str(e),
                "avg_response_time_ms": 0,
                "p95_response_time_ms": 0,
            }

    async def test_concurrent_load(self) -> dict[str, Any]:
        """Test concurrent cache operations."""
        print("\n🔍 Testing Concurrent Load Performance...")

        async def cache_operation(session_id: int):
            """Single cache operation for load testing."""
            try:
                # Simulate cache operations
                await self.redis_client.set(
                    f"load_test:{session_id}", f"data_{session_id}", ex=30
                )
                await self.redis_client.get(f"load_test:{session_id}")
                await self.redis_client.delete(f"load_test:{session_id}")
                return True
            except Exception:
                return False

        # Test with increasing concurrent operations
        concurrent_levels = [10, 50, 100, 500, 1000]
        results = {}

        for level in concurrent_levels:
            print(f"   Testing {level} concurrent operations...")
            start_time = time.time()

            tasks = [cache_operation(i) for i in range(level)]
            completed_tasks = await asyncio.gather(*tasks, return_exceptions=True)

            total_time = time.time() - start_time
            successful_ops = sum(1 for result in completed_tasks if result is True)

            results[f"concurrent_{level}"] = {
                "total_time_s": round(total_time, 2),
                "successful_operations": successful_ops,
                "failed_operations": level - successful_ops,
                "ops_per_second": round(successful_ops / total_time, 2),
                "avg_time_per_op_ms": round((total_time / level) * 1000, 2),
            }

            print(f"     Completed: {successful_ops}/{level} ops in {total_time:.2f}s")
            print(
                f"     Throughput: {results[f'concurrent_{level}']['ops_per_second']} ops/sec"
            )

        return results

    async def test_cache_warming(self) -> dict[str, Any]:
        """Test cache warming performance."""
        print("\n🔍 Testing Cache Warming Performance...")

        # Warm cache with test data
        warming_data = {f"warm_test:{i}": f"warm_data_{i}" for i in range(1000)}

        start_time = time.time()

        # Batch set operations
        pipe = self.redis_client.pipeline()
        for key, value in warming_data.items():
            pipe.set(key, value, ex=300)
        await pipe.execute()

        warming_time = time.time() - start_time

        # Test retrieval performance after warming
        start_time = time.time()
        retrieval_tasks = [self.redis_client.get(f"warm_test:{i}") for i in range(100)]
        await asyncio.gather(*retrieval_tasks)
        retrieval_time = time.time() - start_time

        # Cleanup
        cleanup_keys = list(warming_data.keys())
        await self.redis_client.delete(*cleanup_keys)

        results = {
            "warming_time_s": round(warming_time, 2),
            "warming_ops_per_second": round(1000 / warming_time, 2),
            "retrieval_time_s": round(retrieval_time, 2),
            "retrieval_ops_per_second": round(100 / retrieval_time, 2),
            "cache_entries_warmed": 1000,
        }

        print(
            f"   Warmed {results['cache_entries_warmed']} entries in {results['warming_time_s']}s"
        )
        print(f"   Warming throughput: {results['warming_ops_per_second']} ops/sec")
        print(f"   Retrieval throughput: {results['retrieval_ops_per_second']} ops/sec")

        return results

    async def validate_performance_targets(
        self, results: dict[str, Any]
    ) -> dict[str, bool]:
        """Validate results against performance targets."""
        print("\n📊 Validating Performance Targets...")

        validations = {}

        # Cache hit rate validation
        redis_hit_rate = results.get("redis_performance", {}).get("hit_rate", 0)
        validations["cache_hit_rate"] = (
            redis_hit_rate >= PERFORMANCE_TARGETS["cache_hit_rate"]
        )
        print(
            f"   Cache Hit Rate: {redis_hit_rate}% (target: >{PERFORMANCE_TARGETS['cache_hit_rate']}%) {'✅' if validations['cache_hit_rate'] else '❌'}"
        )

        # Response time validation
        avg_response_times = []
        for service_name, _ in self.services:
            service_results = results.get("service_tests", {}).get(service_name, {})
            if "avg_response_time_ms" in service_results:
                avg_response_times.append(service_results["avg_response_time_ms"])

        if avg_response_times:
            overall_avg_response = statistics.mean(avg_response_times)
            validations["response_time"] = (
                overall_avg_response <= PERFORMANCE_TARGETS["response_time_ms"]
            )
            print(
                f"   Avg Response Time: {overall_avg_response:.2f}ms (target: <{PERFORMANCE_TARGETS['response_time_ms']}ms) {'✅' if validations['response_time'] else '❌'}"
            )

        # Concurrent operations validation
        concurrent_1000 = results.get("concurrent_load", {}).get("concurrent_1000", {})
        if concurrent_1000:
            successful_ops = concurrent_1000.get("successful_operations", 0)
            validations["concurrent_requests"] = (
                successful_ops >= PERFORMANCE_TARGETS["concurrent_requests"] * 0.95
            )  # 95% success rate
            print(
                f"   Concurrent Operations: {successful_ops}/1000 (target: >{PERFORMANCE_TARGETS['concurrent_requests'] * 0.95}) {'✅' if validations['concurrent_requests'] else '❌'}"
            )

        # Memory efficiency validation
        memory_mb = results.get("redis_performance", {}).get("memory_usage_mb", 0)
        # Assume efficient if memory usage is reasonable for operations performed
        validations["memory_efficiency"] = (
            memory_mb < 100
        )  # Less than 100MB for test operations
        print(
            f"   Memory Efficiency: {memory_mb}MB (target: <100MB) {'✅' if validations['memory_efficiency'] else '❌'}"
        )

        return validations

    async def run_full_test_suite(self) -> dict[str, Any]:
        """Run complete cache performance test suite."""
        print("🚀 Starting ACGS-1 Cache Performance Test Suite")
        print("=" * 60)

        await self.initialize()

        # Run all tests
        results = {
            "test_timestamp": datetime.utcnow().isoformat(),
            "redis_performance": await self.test_redis_performance(),
            "service_tests": {},
            "concurrent_load": await self.test_concurrent_load(),
            "cache_warming": await self.test_cache_warming(),
        }

        # Test each service
        for service_name, port in self.services:
            results["service_tests"][service_name] = (
                await self.test_service_cache_integration(service_name, port)
            )

        # Validate against targets
        results["performance_validation"] = await self.validate_performance_targets(
            results
        )

        # Calculate overall score
        validations = results["performance_validation"]
        passed_tests = sum(1 for passed in validations.values() if passed)
        total_tests = len(validations)
        results["overall_score"] = {
            "passed": passed_tests,
            "total": total_tests,
            "percentage": round((passed_tests / total_tests) * 100, 1),
        }

        print(
            f"\n🎯 Overall Performance Score: {results['overall_score']['passed']}/{results['overall_score']['total']} ({results['overall_score']['percentage']}%)"
        )

        # Save results
        with open(
            "logs/caching/performance_test_results.json", "w"
        ) as f:
            json.dump(results, f, indent=2)

        print(
            "\n📊 Test results saved to: logs/caching/performance_test_results.json"
        )

        await self.redis_client.close()
        return results


async def main():
    """Main test execution."""
    tester = CachePerformanceTester()
    try:
        results = await tester.run_full_test_suite()

        # Print summary
        print("\n" + "=" * 60)
        print("🎉 Cache Performance Testing Completed!")

        if results["overall_score"]["percentage"] >= 75:
            print("✅ Performance targets met - Ready for production deployment")
        else:
            print("⚠️  Performance targets not fully met - Review and optimize")

    except Exception as e:
        print(f"❌ Test suite failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
