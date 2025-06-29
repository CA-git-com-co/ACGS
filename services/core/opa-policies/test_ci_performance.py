#!/usr/bin/env python3
"""
ACGS-1 Lite CI/CD Performance Test Suite
Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import os
import statistics
import time
from typing import Dict, List, Optional
import pytest
import httpx
from datetime import datetime


# Configuration
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"
BASE_URL = os.getenv("POLICY_ENGINE_URL", "http://localhost:8004")
PERFORMANCE_TARGET_P99_MS = float(os.getenv("PERFORMANCE_TARGET_P99_MS", "5.0"))
CONCURRENCY_LEVELS = [10, 50, 100]
MIN_THROUGHPUT_RPS = 100
MIN_SUCCESS_RATE = 0.99


class PerformanceTestSuite:
    """Comprehensive performance test suite for CI/CD validation"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self.results = {}
    
    async def health_check(self) -> bool:
        """Verify service is healthy before testing"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/v1/data/acgs/main/health")
                if response.status_code == 200:
                    data = response.json()
                    return (
                        data.get("status") == "healthy" and
                        data.get("constitutional_hash") == self.constitutional_hash
                    )
        except Exception:
            pass
        return False
    
    async def single_request_latency_test(self, num_requests: int = 100) -> Dict[str, float]:
        """Test single request latency performance"""
        test_request = {
            "type": "constitutional_evaluation",
            "constitutional_hash": self.constitutional_hash,
            "action": "data.read_public",
            "context": {
                "environment": {"sandbox_enabled": True, "audit_enabled": True},
                "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
                "responsible_party": "ci_test",
                "explanation": "CI latency test"
            }
        }
        
        latencies = []
        errors = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for _ in range(num_requests):
                start = time.perf_counter_ns()
                try:
                    response = await client.post(f"{self.base_url}/v1/data/acgs/main/decision", json=test_request)
                    end = time.perf_counter_ns()
                    
                    if response.status_code == 200:
                        latency_ms = (end - start) / 1_000_000
                        latencies.append(latency_ms)
                    else:
                        errors += 1
                except Exception:
                    errors += 1
        
        if not latencies:
            return {"error": "No successful requests"}
        
        latencies.sort()
        n = len(latencies)
        
        return {
            "total_requests": num_requests,
            "successful_requests": n,
            "error_count": errors,
            "success_rate": n / num_requests,
            "mean_latency_ms": statistics.mean(latencies),
            "median_latency_ms": statistics.median(latencies),
            "p90_latency_ms": latencies[int(0.9 * n)],
            "p95_latency_ms": latencies[int(0.95 * n)],
            "p99_latency_ms": latencies[int(0.99 * n)],
            "max_latency_ms": max(latencies),
            "min_latency_ms": min(latencies)
        }
    
    async def concurrent_load_test(self, concurrency: int, requests_per_user: int = 50) -> Dict[str, float]:
        """Test performance under concurrent load"""
        test_request = {
            "type": "constitutional_evaluation",
            "constitutional_hash": self.constitutional_hash,
            "action": "data.read_public",
            "context": {
                "environment": {"sandbox_enabled": True, "audit_enabled": True},
                "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
                "responsible_party": "concurrent_test",
                "explanation": f"Concurrent test with {concurrency} users"
            }
        }
        
        async def user_session() -> List[float]:
            """Simulate single user session"""
            latencies = []
            async with httpx.AsyncClient(timeout=30.0) as client:
                for _ in range(requests_per_user):
                    start = time.perf_counter_ns()
                    try:
                        response = await client.post(f"{self.base_url}/v1/data/acgs/main/decision", json=test_request)
                        end = time.perf_counter_ns()
                        
                        if response.status_code == 200:
                            latency_ms = (end - start) / 1_000_000
                            latencies.append(latency_ms)
                    except Exception:
                        pass
            return latencies
        
        # Run concurrent users
        start_time = time.perf_counter()
        tasks = [user_session() for _ in range(concurrency)]
        user_results = await asyncio.gather(*tasks)
        total_time = time.perf_counter() - start_time
        
        # Aggregate results
        all_latencies = []
        for user_latencies in user_results:
            all_latencies.extend(user_latencies)
        
        total_requests = concurrency * requests_per_user
        successful_requests = len(all_latencies)
        
        if not all_latencies:
            return {"error": "No successful requests"}
        
        all_latencies.sort()
        n = len(all_latencies)
        
        return {
            "concurrency": concurrency,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": successful_requests / total_requests,
            "total_time_seconds": total_time,
            "requests_per_second": successful_requests / total_time,
            "mean_latency_ms": statistics.mean(all_latencies),
            "p95_latency_ms": all_latencies[int(0.95 * n)],
            "p99_latency_ms": all_latencies[int(0.99 * n)],
            "max_latency_ms": max(all_latencies)
        }
    
    async def mixed_workload_test(self, duration_seconds: int = 60) -> Dict[str, float]:
        """Test mixed workload performance (safe, complex, dangerous actions)"""
        requests = [
            # 70% safe actions
            {
                "type": "constitutional_evaluation",
                "constitutional_hash": self.constitutional_hash,
                "action": "data.read_public",
                "context": {
                    "environment": {"sandbox_enabled": True, "audit_enabled": True},
                    "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
                    "responsible_party": "mixed_test",
                    "explanation": "Safe action test"
                }
            },
            # 20% complex actions
            {
                "type": "evolution_approval",
                "constitutional_hash": self.constitutional_hash,
                "evolution_request": {
                    "type": "patch",
                    "constitutional_hash": self.constitutional_hash,
                    "changes": {"code_changes": ["Minor fix"], "external_dependencies": [], "privilege_escalation": False},
                    "performance_analysis": {"complexity_delta": 0.01, "memory_delta": 0.005, "latency_delta": 0.0, "resource_delta": 0.0},
                    "rollback_plan": {"procedure": "Git revert", "verification": "Tests", "timeline": "5 min", "dependencies": "None", "tested": True, "automated": True}
                }
            },
            # 10% dangerous actions (should be denied)
            {
                "type": "constitutional_evaluation",
                "constitutional_hash": self.constitutional_hash,
                "action": "system.execute_shell",
                "context": {
                    "environment": {"sandbox_enabled": False},
                    "agent": {"trust_level": 0.3}
                }
            }
        ]
        
        weights = [7, 2, 1]  # 70%, 20%, 10%
        total_weight = sum(weights)
        
        latencies = []
        responses_by_type = {"safe": [], "complex": [], "dangerous": []}
        errors = 0
        
        start_time = time.perf_counter()
        request_count = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            while time.perf_counter() - start_time < duration_seconds:
                # Select request type based on weights
                import random
                rand = random.randint(1, total_weight)
                if rand <= weights[0]:
                    request = requests[0]
                    request_type = "safe"
                elif rand <= weights[0] + weights[1]:
                    request = requests[1]
                    request_type = "complex"
                else:
                    request = requests[2]
                    request_type = "dangerous"
                
                req_start = time.perf_counter_ns()
                try:
                    response = await client.post(f"{self.base_url}/v1/data/acgs/main/decision", json=request)
                    req_end = time.perf_counter_ns()
                    
                    if response.status_code == 200:
                        latency_ms = (req_end - req_start) / 1_000_000
                        latencies.append(latency_ms)
                        
                        data = response.json()
                        responses_by_type[request_type].append(data.get("allow", False))
                    else:
                        errors += 1
                except Exception:
                    errors += 1
                
                request_count += 1
                
                # Small delay to avoid overwhelming the service
                await asyncio.sleep(0.01)
        
        actual_duration = time.perf_counter() - start_time
        
        if not latencies:
            return {"error": "No successful requests"}
        
        latencies.sort()
        n = len(latencies)
        
        # Analyze response correctness
        safe_allow_rate = sum(responses_by_type["safe"]) / len(responses_by_type["safe"]) if responses_by_type["safe"] else 0
        dangerous_deny_rate = 1 - (sum(responses_by_type["dangerous"]) / len(responses_by_type["dangerous"])) if responses_by_type["dangerous"] else 1
        
        return {
            "duration_seconds": actual_duration,
            "total_requests": request_count,
            "successful_requests": n,
            "error_count": errors,
            "requests_per_second": n / actual_duration,
            "mean_latency_ms": statistics.mean(latencies),
            "p95_latency_ms": latencies[int(0.95 * n)],
            "p99_latency_ms": latencies[int(0.99 * n)],
            "safe_actions_allowed_rate": safe_allow_rate,
            "dangerous_actions_denied_rate": dangerous_deny_rate,
            "constitutional_compliance_rate": (safe_allow_rate + dangerous_deny_rate) / 2
        }
    
    async def cache_effectiveness_test(self) -> Dict[str, float]:
        """Test cache performance and effectiveness"""
        test_request = {
            "type": "constitutional_evaluation",
            "constitutional_hash": self.constitutional_hash,
            "action": "data.read_public",
            "context": {
                "environment": {"sandbox_enabled": True, "audit_enabled": True},
                "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
                "responsible_party": "cache_test",
                "explanation": "Cache effectiveness test"
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            # First request (cache miss)
            miss_start = time.perf_counter_ns()
            response = await client.post(f"{self.base_url}/v1/data/acgs/main/decision", json=test_request)
            miss_time_ms = (time.perf_counter_ns() - miss_start) / 1_000_000
            
            if response.status_code != 200:
                return {"error": "Cache miss request failed"}
            
            # Multiple subsequent requests (cache hits)
            hit_times = []
            for _ in range(100):
                hit_start = time.perf_counter_ns()
                response = await client.post(f"{self.base_url}/v1/data/acgs/main/decision", json=test_request)
                hit_time_ms = (time.perf_counter_ns() - hit_start) / 1_000_000
                
                if response.status_code == 200:
                    hit_times.append(hit_time_ms)
            
            if not hit_times:
                return {"error": "No successful cache hit requests"}
            
            avg_hit_time = statistics.mean(hit_times)
            
            return {
                "cache_miss_latency_ms": miss_time_ms,
                "cache_hit_avg_latency_ms": avg_hit_time,
                "cache_hit_p99_latency_ms": sorted(hit_times)[int(0.99 * len(hit_times))],
                "cache_speedup_factor": miss_time_ms / avg_hit_time if avg_hit_time > 0 else 0,
                "cache_hit_requests": len(hit_times)
            }


# Pytest fixtures and tests
@pytest.fixture
async def performance_suite():
    """Initialize performance test suite"""
    suite = PerformanceTestSuite()
    
    # Health check
    is_healthy = await suite.health_check()
    if not is_healthy:
        pytest.skip("Policy engine service is not healthy")
    
    return suite


@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_single_request_latency_slo(performance_suite):
    """Test that single request latency meets SLO"""
    results = await performance_suite.single_request_latency_test(200)
    
    assert "error" not in results, "Single request test failed"
    assert results["success_rate"] >= MIN_SUCCESS_RATE, f"Success rate {results['success_rate']:.1%} below {MIN_SUCCESS_RATE:.1%}"
    assert results["p99_latency_ms"] <= PERFORMANCE_TARGET_P99_MS, f"P99 latency {results['p99_latency_ms']:.3f}ms exceeds target {PERFORMANCE_TARGET_P99_MS}ms"
    assert results["mean_latency_ms"] <= PERFORMANCE_TARGET_P99_MS / 2, f"Mean latency {results['mean_latency_ms']:.3f}ms too high"
    
    print(f"\n✅ Single Request Latency Test:")
    print(f"   Success Rate: {results['success_rate']:.1%}")
    print(f"   Mean: {results['mean_latency_ms']:.3f}ms")
    print(f"   P99: {results['p99_latency_ms']:.3f}ms")


@pytest.mark.asyncio
@pytest.mark.benchmark 
async def test_concurrent_performance_scaling(performance_suite):
    """Test that performance scales with concurrent load"""
    results = {}
    
    for concurrency in CONCURRENCY_LEVELS:
        print(f"\n🔄 Testing {concurrency} concurrent users...")
        result = await performance_suite.concurrent_load_test(concurrency, 20)
        
        assert "error" not in result, f"Concurrent test failed at {concurrency} users"
        assert result["success_rate"] >= MIN_SUCCESS_RATE, f"Success rate {result['success_rate']:.1%} below {MIN_SUCCESS_RATE:.1%} at {concurrency} users"
        assert result["p99_latency_ms"] <= PERFORMANCE_TARGET_P99_MS, f"P99 latency {result['p99_latency_ms']:.3f}ms exceeds target at {concurrency} users"
        assert result["requests_per_second"] >= MIN_THROUGHPUT_RPS, f"Throughput {result['requests_per_second']:.0f} RPS below {MIN_THROUGHPUT_RPS} at {concurrency} users"
        
        results[concurrency] = result
        
        print(f"   Success Rate: {result['success_rate']:.1%}")
        print(f"   P99 Latency: {result['p99_latency_ms']:.3f}ms")
        print(f"   Throughput: {result['requests_per_second']:.0f} RPS")
    
    # Check scaling efficiency (throughput should scale reasonably with concurrency)
    if len(results) >= 2:
        low_concurrency = min(results.keys())
        high_concurrency = max(results.keys())
        
        low_rps = results[low_concurrency]["requests_per_second"]
        high_rps = results[high_concurrency]["requests_per_second"]
        
        scaling_factor = high_rps / low_rps
        expected_scaling = high_concurrency / low_concurrency
        scaling_efficiency = scaling_factor / expected_scaling
        
        assert scaling_efficiency >= 0.5, f"Poor scaling efficiency: {scaling_efficiency:.2f} (expected >= 0.5)"
        
        print(f"\n📈 Scaling Analysis:")
        print(f"   {low_concurrency} users: {low_rps:.0f} RPS")
        print(f"   {high_concurrency} users: {high_rps:.0f} RPS")
        print(f"   Scaling efficiency: {scaling_efficiency:.2f}")


@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_mixed_workload_performance(performance_suite):
    """Test performance with mixed workload (safe, complex, dangerous actions)"""
    results = await performance_suite.mixed_workload_test(30)  # 30 second test
    
    assert "error" not in results, "Mixed workload test failed"
    assert results["requests_per_second"] >= MIN_THROUGHPUT_RPS / 2, f"Throughput {results['requests_per_second']:.0f} RPS too low for mixed workload"
    assert results["p99_latency_ms"] <= PERFORMANCE_TARGET_P99_MS, f"P99 latency {results['p99_latency_ms']:.3f}ms exceeds target"
    assert results["constitutional_compliance_rate"] >= 0.95, f"Constitutional compliance {results['constitutional_compliance_rate']:.1%} below 95%"
    
    print(f"\n🎭 Mixed Workload Test:")
    print(f"   Duration: {results['duration_seconds']:.1f}s")
    print(f"   Throughput: {results['requests_per_second']:.0f} RPS")
    print(f"   P99 Latency: {results['p99_latency_ms']:.3f}ms")
    print(f"   Constitutional Compliance: {results['constitutional_compliance_rate']:.1%}")
    print(f"   Safe Actions Allowed: {results['safe_actions_allowed_rate']:.1%}")
    print(f"   Dangerous Actions Denied: {results['dangerous_actions_denied_rate']:.1%}")


@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_cache_effectiveness(performance_suite):
    """Test that caching provides significant performance improvement"""
    results = await performance_suite.cache_effectiveness_test()
    
    assert "error" not in results, "Cache effectiveness test failed"
    assert results["cache_speedup_factor"] >= 2.0, f"Cache speedup {results['cache_speedup_factor']:.1f}x insufficient (expected >= 2x)"
    assert results["cache_hit_avg_latency_ms"] <= PERFORMANCE_TARGET_P99_MS / 2, f"Cache hit latency {results['cache_hit_avg_latency_ms']:.3f}ms too high"
    
    print(f"\n🗄️  Cache Effectiveness Test:")
    print(f"   Cache Miss: {results['cache_miss_latency_ms']:.3f}ms")
    print(f"   Cache Hit Avg: {results['cache_hit_avg_latency_ms']:.3f}ms")
    print(f"   Cache Hit P99: {results['cache_hit_p99_latency_ms']:.3f}ms")
    print(f"   Speedup Factor: {results['cache_speedup_factor']:.1f}x")


@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_service_metrics_validation(performance_suite):
    """Validate service metrics meet targets"""
    # Generate some load first
    await performance_suite.single_request_latency_test(50)
    
    # Get current metrics
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{performance_suite.base_url}/v1/metrics")
        assert response.status_code == 200, "Failed to get service metrics"
        
        metrics = response.json()
        
        # Validate key metrics
        assert metrics["avg_latency_ms"] <= PERFORMANCE_TARGET_P99_MS / 2, f"Average latency {metrics['avg_latency_ms']:.3f}ms too high"
        
        percentiles = metrics["percentiles"]
        assert percentiles["p99"] <= PERFORMANCE_TARGET_P99_MS, f"Service P99 {percentiles['p99']:.3f}ms exceeds target"
        
        # Cache metrics (may be lower in CI)
        cache_hit_rate = metrics.get("cache_hit_rate", 0)
        if cache_hit_rate > 0:
            assert cache_hit_rate >= 0.5, f"Cache hit rate {cache_hit_rate:.1%} too low"
        
        print(f"\n📊 Service Metrics Validation:")
        print(f"   Total Requests: {metrics['request_count']}")
        print(f"   Average Latency: {metrics['avg_latency_ms']:.3f}ms")
        print(f"   P99 Latency: {percentiles['p99']:.3f}ms")
        print(f"   Cache Hit Rate: {cache_hit_rate:.1%}")
        
        targets_met = metrics.get("targets_met", {})
        print(f"   P99 Target Met: {'✅' if targets_met.get('p99_under_1ms') else '❌'}")


if __name__ == "__main__":
    # Run the test suite
    import sys
    
    # Check if service is available
    async def check_service():
        suite = PerformanceTestSuite()
        return await suite.health_check()
    
    if not asyncio.run(check_service()):
        print("❌ Policy engine service is not available")
        sys.exit(1)
    
    # Run pytest with performance focus
    pytest_args = [
        __file__,
        "-v", 
        "-m", "benchmark",
        "--tb=short",
        "--disable-warnings"
    ]
    
    exit_code = pytest.main(pytest_args)
    sys.exit(exit_code)