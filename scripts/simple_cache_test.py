#!/usr/bin/env python3
"""
Simple Cache Performance Test for ACGS-1 Phase A3
Tests basic Redis performance without external dependencies
"""

import json
import statistics
import time
from datetime import datetime

import redis


def test_redis_performance():
    """Test basic Redis performance."""
    print("🔍 Testing Redis Performance...")

    try:
        # Connect to Redis
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        r.ping()
        print("✅ Redis connection established")
    except Exception as e:
        print(f"❌ Failed to connect to Redis: {e}")
        return None

    # Test SET operations
    print("   Testing SET operations...")
    set_times = []
    for i in range(100):
        start_time = time.time()
        r.set(f"test:set:{i}", f"value_{i}", ex=60)
        set_times.append((time.time() - start_time) * 1000)

    # Test GET operations
    print("   Testing GET operations...")
    get_times = []
    for i in range(100):
        start_time = time.time()
        r.get(f"test:set:{i}")
        get_times.append((time.time() - start_time) * 1000)

    # Test DEL operations
    print("   Testing DEL operations...")
    del_times = []
    for i in range(100):
        start_time = time.time()
        r.delete(f"test:set:{i}")
        del_times.append((time.time() - start_time) * 1000)

    # Get Redis info
    redis_info = r.info()

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
    print(f"   DEL operations: {results['del_avg_ms']}ms avg")
    print(f"   Hit rate: {results['hit_rate']}%")
    print(f"   Memory usage: {results['memory_usage_mb']}MB")
    print(f"   Connected clients: {results['connected_clients']}")

    return results


def test_cache_warming():
    """Test cache warming performance."""
    print("\n🔍 Testing Cache Warming Performance...")

    try:
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)

        # Warm cache with test data
        start_time = time.time()

        # Use pipeline for batch operations
        pipe = r.pipeline()
        for i in range(1000):
            pipe.set(f"warm_test:{i}", f"warm_data_{i}", ex=300)
        pipe.execute()

        warming_time = time.time() - start_time

        # Test retrieval performance after warming
        start_time = time.time()
        for i in range(100):
            r.get(f"warm_test:{i}")
        retrieval_time = time.time() - start_time

        # Cleanup
        cleanup_keys = [f"warm_test:{i}" for i in range(1000)]
        r.delete(*cleanup_keys)

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

    except Exception as e:
        print(f"   ❌ Cache warming test failed: {e}")
        return None


def test_service_health():
    """Test service health endpoints."""
    print("\n🔍 Testing Service Health...")

    import urllib.error
    import urllib.request

    services = [
        ("auth_service", 8000),
        ("ac_service", 8001),
        ("integrity_service", 8002),
        ("fv_service", 8003),
        ("gs_service", 8004),
        ("pgc_service", 8005),
        ("ec_service", 8006),
    ]

    healthy_services = 0
    service_results = {}

    for service_name, port in services:
        try:
            start_time = time.time()
            with urllib.request.urlopen(
                f"http://localhost:{port}/health", timeout=5
            ) as response:
                response_time = (time.time() - start_time) * 1000
                if response.status == 200:
                    print(
                        f"   ✅ {service_name} (port {port}): Healthy ({response_time:.1f}ms)"
                    )
                    healthy_services += 1
                    service_results[service_name] = {
                        "healthy": True,
                        "response_time_ms": round(response_time, 1),
                    }
                else:
                    print(
                        f"   ❌ {service_name} (port {port}): Unhealthy (status {response.status})"
                    )
                    service_results[service_name] = {
                        "healthy": False,
                        "status_code": response.status,
                    }
        except Exception as e:
            print(f"   ❌ {service_name} (port {port}): Not responding ({str(e)})")
            service_results[service_name] = {"healthy": False, "error": str(e)}

    print(
        f"\n   📊 Service Health Summary: {healthy_services}/{len(services)} services healthy"
    )

    return {
        "healthy_services": healthy_services,
        "total_services": len(services),
        "health_percentage": round((healthy_services / len(services)) * 100, 1),
        "service_details": service_results,
    }


def validate_performance_targets(results):
    """Validate results against performance targets."""
    print("\n📊 Validating Performance Targets...")

    validations = {}

    # Response time validation (target: <500ms for cache operations)
    redis_perf = results.get("redis_performance", {})
    avg_cache_time = (
        redis_perf.get("get_avg_ms", 0) + redis_perf.get("set_avg_ms", 0)
    ) / 2
    validations["cache_response_time"] = avg_cache_time <= 500
    print(
        f"   Cache Response Time: {avg_cache_time:.2f}ms (target: <500ms) {'✅' if validations['cache_response_time'] else '❌'}"
    )

    # Memory efficiency validation
    memory_mb = redis_perf.get("memory_usage_mb", 0)
    validations["memory_efficiency"] = (
        memory_mb < 100
    )  # Less than 100MB for test operations
    print(
        f"   Memory Efficiency: {memory_mb}MB (target: <100MB) {'✅' if validations['memory_efficiency'] else '❌'}"
    )

    # Service health validation (target: >50% services healthy)
    service_health = results.get("service_health", {})
    health_percentage = service_health.get("health_percentage", 0)
    validations["service_health"] = health_percentage >= 50
    print(
        f"   Service Health: {health_percentage}% (target: >50%) {'✅' if validations['service_health'] else '❌'}"
    )

    # Cache warming performance (target: >500 ops/sec)
    cache_warming = results.get("cache_warming", {})
    warming_ops = cache_warming.get("warming_ops_per_second", 0)
    validations["cache_warming"] = warming_ops >= 500
    print(
        f"   Cache Warming: {warming_ops} ops/sec (target: >500 ops/sec) {'✅' if validations['cache_warming'] else '❌'}"
    )

    return validations


def main():
    """Main test execution."""
    print("🚀 Starting ACGS-1 Simple Cache Performance Test")
    print("=" * 60)

    # Run all tests
    results = {
        "test_timestamp": datetime.utcnow().isoformat(),
        "redis_performance": test_redis_performance(),
        "cache_warming": test_cache_warming(),
        "service_health": test_service_health(),
    }

    # Validate against targets
    if results["redis_performance"]:
        results["performance_validation"] = validate_performance_targets(results)

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
    else:
        print("\n❌ Redis performance test failed - cannot validate targets")
        return 1

    # Save results
    try:
        with open(
            "/home/dislove/ACGS-1/logs/caching/simple_performance_test_results.json",
            "w",
        ) as f:
            json.dump(results, f, indent=2)
        print(
            f"\n📊 Test results saved to: /home/dislove/ACGS-1/logs/caching/simple_performance_test_results.json"
        )
    except Exception as e:
        print(f"⚠️  Could not save results: {e}")

    # Print summary
    print("\n" + "=" * 60)
    print("🎉 Simple Cache Performance Testing Completed!")

    if results.get("overall_score", {}).get("percentage", 0) >= 75:
        print("✅ Performance targets met - Advanced caching is operational")
        return 0
    else:
        print("⚠️  Some performance targets not met - Review and optimize")
        return 1


if __name__ == "__main__":
    exit(main())
