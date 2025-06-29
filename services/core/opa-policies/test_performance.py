#!/usr/bin/env python3
"""
ACGS-1 Lite Policy Engine Performance Test Suite
Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import statistics
import time
from typing import Dict, List

import httpx
import pytest
from locust import HttpUser, between, task


class PolicyEnginePerformanceTest:
    """Performance testing suite for policy engine optimization"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
        self.constitutional_hash = "cdd01ef066bc6cf2"
    
    async def benchmark_latency(self, num_requests: int = 10000) -> Dict[str, float]:
        """Benchmark policy evaluation latency"""
        latencies = []
        
        test_request = {
            "type": "constitutional_evaluation",
            "constitutional_hash": self.constitutional_hash,
            "action": "data.read_public",
            "context": {
                "environment": {"sandbox_enabled": True, "audit_enabled": True},
                "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
                "responsible_party": "benchmark",
                "explanation": "Performance benchmark test"
            }
        }
        
        async with httpx.AsyncClient() as client:
            # Warm up
            for _ in range(100):
                await client.post(f"{self.base_url}/v1/data/acgs/main/decision", json=test_request)
            
            # Benchmark
            print(f"Running {num_requests} requests for latency benchmark...")
            start_time = time.perf_counter()
            
            for i in range(num_requests):
                if i % 1000 == 0:
                    print(f"Progress: {i}/{num_requests}")
                
                request_start = time.perf_counter()
                response = await client.post(f"{self.base_url}/v1/data/acgs/main/decision", json=test_request)
                request_end = time.perf_counter()
                
                if response.status_code == 200:
                    latency_ms = (request_end - request_start) * 1000
                    latencies.append(latency_ms)
                else:
                    print(f"Request failed: {response.status_code}")
            
            total_time = time.perf_counter() - start_time
        
        # Calculate statistics
        if latencies:
            latencies.sort()
            n = len(latencies)
            
            results = {
                "total_requests": n,
                "total_time_seconds": total_time,
                "rps": n / total_time,
                "avg_latency_ms": statistics.mean(latencies),
                "median_latency_ms": statistics.median(latencies),
                "p50_latency_ms": latencies[int(0.5 * n)],
                "p95_latency_ms": latencies[int(0.95 * n)],
                "p99_latency_ms": latencies[int(0.99 * n)],
                "max_latency_ms": max(latencies),
                "min_latency_ms": min(latencies)
            }
            
            return results
        else:
            return {"error": "No successful requests"}
    
    async def benchmark_cache_performance(self) -> Dict[str, float]:
        """Benchmark cache hit rate and performance"""
        # Same request repeated to test caching
        test_request = {
            "type": "constitutional_evaluation",
            "constitutional_hash": self.constitutional_hash,
            "action": "data.read_public",
            "context": {
                "environment": {"sandbox_enabled": True, "audit_enabled": True},
                "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
                "responsible_party": "cache_test",
                "explanation": "Cache performance test"
            }
        }
        
        async with httpx.AsyncClient() as client:
            # First request (cache miss)
            miss_start = time.perf_counter()
            response = await client.post(f"{self.base_url}/v1/data/acgs/main/decision", json=test_request)
            miss_time = (time.perf_counter() - miss_start) * 1000
            
            # Subsequent requests (cache hits)
            hit_times = []
            for _ in range(100):
                hit_start = time.perf_counter()
                response = await client.post(f"{self.base_url}/v1/data/acgs/main/decision", json=test_request)
                hit_time = (time.perf_counter() - hit_start) * 1000
                hit_times.append(hit_time)
            
            avg_hit_time = statistics.mean(hit_times)
            
            return {
                "cache_miss_latency_ms": miss_time,
                "cache_hit_avg_latency_ms": avg_hit_time,
                "cache_speedup": miss_time / avg_hit_time if avg_hit_time > 0 else 0
            }
    
    async def benchmark_partial_evaluation(self) -> Dict[str, float]:
        """Benchmark partial evaluation performance"""
        # Test safe action (should use partial evaluation)
        safe_request = {
            "type": "constitutional_evaluation",
            "constitutional_hash": self.constitutional_hash,
            "action": "data.read_public",
            "context": {
                "environment": {"sandbox_enabled": True, "audit_enabled": True},
                "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
                "responsible_party": "partial_test",
                "explanation": "Partial evaluation test"
            }
        }
        
        # Test complex action (requires full evaluation)
        complex_request = {
            "type": "evolution_approval",
            "constitutional_hash": self.constitutional_hash,
            "evolution_request": {
                "type": "major_update",
                "constitutional_hash": self.constitutional_hash,
                "changes": {
                    "code_changes": ["Complex algorithm update"],
                    "external_dependencies": ["new_library"],
                    "privilege_escalation": True,
                    "experimental_features": True
                },
                "performance_analysis": {
                    "complexity_delta": 0.3,
                    "memory_delta": 0.2,
                    "latency_delta": 0.1,
                    "resource_delta": 0.15
                },
                "rollback_plan": {
                    "procedure": "Manual rollback with verification",
                    "verification": "Full test suite + manual testing",
                    "timeline": "30 minutes",
                    "dependencies": "Database migration",
                    "tested": True,
                    "automated": False
                }
            }
        }
        
        async with httpx.AsyncClient() as client:
            # Benchmark partial evaluation
            partial_times = []
            for _ in range(100):
                start = time.perf_counter()
                await client.post(f"{self.base_url}/v1/data/acgs/main/decision", json=safe_request)
                partial_times.append((time.perf_counter() - start) * 1000)
            
            # Benchmark full evaluation
            full_times = []
            for _ in range(100):
                start = time.perf_counter()
                await client.post(f"{self.base_url}/v1/data/acgs/main/decision", json=complex_request)
                full_times.append((time.perf_counter() - start) * 1000)
            
            return {
                "partial_eval_avg_ms": statistics.mean(partial_times),
                "full_eval_avg_ms": statistics.mean(full_times),
                "partial_eval_speedup": statistics.mean(full_times) / statistics.mean(partial_times)
            }
    
    async def run_comprehensive_benchmark(self) -> Dict[str, any]:
        """Run all performance benchmarks"""
        print("Starting comprehensive performance benchmark...")
        
        results = {}
        
        # Latency benchmark
        print("\n1. Running latency benchmark...")
        results["latency"] = await self.benchmark_latency(5000)
        
        # Cache performance
        print("\n2. Running cache performance benchmark...")
        results["cache"] = await self.benchmark_cache_performance()
        
        # Partial evaluation
        print("\n3. Running partial evaluation benchmark...")
        results["partial_eval"] = await self.benchmark_partial_evaluation()
        
        # Get current metrics
        print("\n4. Fetching current metrics...")
        async with httpx.AsyncClient() as client:
            metrics_response = await client.get(f"{self.base_url}/v1/metrics")
            if metrics_response.status_code == 200:
                results["current_metrics"] = metrics_response.json()
        
        return results


class PolicyEngineLocustUser(HttpUser):
    """Locust user for load testing"""
    
    wait_time = between(0.1, 0.5)
    
    def on_start(self):
        """Initialize test data"""
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.test_requests = [
            {
                "type": "constitutional_evaluation",
                "constitutional_hash": self.constitutional_hash,
                "action": "data.read_public",
                "context": {
                    "environment": {"sandbox_enabled": True, "audit_enabled": True},
                    "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
                    "responsible_party": "load_test",
                    "explanation": "Load test request"
                }
            },
            {
                "type": "constitutional_evaluation",
                "constitutional_hash": self.constitutional_hash,
                "action": "compute.analyze_metrics",
                "context": {
                    "environment": {"sandbox_enabled": True, "audit_enabled": True},
                    "agent": {"trust_level": 0.85, "requested_resources": {"cpu_cores": 2}},
                    "responsible_party": "analytics",
                    "explanation": "Analytics computation"
                }
            },
            {
                "type": "data_access",
                "constitutional_hash": self.constitutional_hash,
                "data_request": {
                    "data_fields": [{"name": "public_metrics", "classification_level": 0, "category": "analytics"}],
                    "requester_clearance_level": 1,
                    "purpose": "dashboard_display",
                    "allowed_purposes": ["dashboard_display"],
                    "justified_fields": ["public_metrics"],
                    "timestamp": 1704067200,
                    "retention_policy": {"analytics": 2592000},
                    "encryption_config": {"public_metrics": {"encrypted": False}}
                }
            }
        ]
    
    @task(10)
    def evaluate_constitutional_policy(self):
        """Test constitutional policy evaluation (most common)"""
        request = self.test_requests[0]
        self.client.post("/v1/data/acgs/main/decision", json=request, name="constitutional_evaluation")
    
    @task(5)
    def evaluate_data_access_policy(self):
        """Test data access policy evaluation"""
        request = self.test_requests[2]
        self.client.post("/v1/data/acgs/main/decision", json=request, name="data_access_evaluation")
    
    @task(3)
    def evaluate_compute_policy(self):
        """Test compute policy evaluation"""
        request = self.test_requests[1]
        self.client.post("/v1/data/acgs/main/decision", json=request, name="compute_evaluation")
    
    @task(1)
    def health_check(self):
        """Test health endpoint"""
        self.client.get("/v1/data/acgs/main/health", name="health_check")
    
    @task(1)
    def simple_allow_check(self):
        """Test simple allow endpoint"""
        self.client.get(
            f"/v1/data/acgs/main/allow?type=constitutional_evaluation&constitutional_hash={self.constitutional_hash}&action=data.read_public",
            name="simple_allow"
        )


# Pytest benchmarks
@pytest.mark.asyncio
async def test_policy_evaluation_latency(benchmark):
    """Benchmark single policy evaluation latency"""
    tester = PolicyEnginePerformanceTest()
    
    test_request = {
        "type": "constitutional_evaluation",
        "constitutional_hash": "cdd01ef066bc6cf2",
        "action": "data.read_public",
        "context": {
            "environment": {"sandbox_enabled": True, "audit_enabled": True},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
            "responsible_party": "pytest",
            "explanation": "Pytest benchmark"
        }
    }
    
    async def evaluate_once():
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{tester.base_url}/v1/data/acgs/main/decision", json=test_request)
            return response.json()
    
    result = benchmark(lambda: asyncio.run(evaluate_once()))
    assert result["allow"] is not None


@pytest.mark.asyncio
async def test_batch_processing_performance():
    """Test batch processing performance"""
    tester = PolicyEnginePerformanceTest()
    
    # Send multiple concurrent requests
    test_request = {
        "type": "constitutional_evaluation",
        "constitutional_hash": "cdd01ef066bc6cf2",
        "action": "data.read_public",
        "context": {
            "environment": {"sandbox_enabled": True, "audit_enabled": True},
            "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
            "responsible_party": "batch_test",
            "explanation": "Batch processing test"
        }
    }
    
    async with httpx.AsyncClient() as client:
        # Send 50 concurrent requests
        tasks = []
        start_time = time.perf_counter()
        
        for i in range(50):
            task = client.post(f"{tester.base_url}/v1/data/acgs/main/decision", json=test_request)
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks)
        total_time = time.perf_counter() - start_time
        
        # Verify all requests succeeded
        success_count = sum(1 for r in responses if r.status_code == 200)
        assert success_count == 50
        
        # Check throughput
        throughput = 50 / total_time
        print(f"Batch throughput: {throughput:.2f} RPS")
        assert throughput > 100  # Should handle at least 100 RPS


if __name__ == "__main__":
    async def main():
        tester = PolicyEnginePerformanceTest()
        results = await tester.run_comprehensive_benchmark()
        
        print("\n" + "="*60)
        print("ACGS-1 Lite Policy Engine Performance Results")
        print("="*60)
        
        # Print latency results
        latency = results.get("latency", {})
        print(f"\nLatency Benchmark ({latency.get('total_requests', 0)} requests):")
        print(f"  Average: {latency.get('avg_latency_ms', 0):.3f} ms")
        print(f"  P50:     {latency.get('p50_latency_ms', 0):.3f} ms")
        print(f"  P95:     {latency.get('p95_latency_ms', 0):.3f} ms")
        print(f"  P99:     {latency.get('p99_latency_ms', 0):.3f} ms")
        print(f"  RPS:     {latency.get('rps', 0):.0f}")
        
        # Print cache results
        cache = results.get("cache", {})
        print(f"\nCache Performance:")
        print(f"  Cache miss: {cache.get('cache_miss_latency_ms', 0):.3f} ms")
        print(f"  Cache hit:  {cache.get('cache_hit_avg_latency_ms', 0):.3f} ms")
        print(f"  Speedup:    {cache.get('cache_speedup', 0):.1f}x")
        
        # Print partial evaluation results
        partial = results.get("partial_eval", {})
        print(f"\nPartial Evaluation:")
        print(f"  Partial eval: {partial.get('partial_eval_avg_ms', 0):.3f} ms")
        print(f"  Full eval:    {partial.get('full_eval_avg_ms', 0):.3f} ms")
        print(f"  Speedup:      {partial.get('partial_eval_speedup', 0):.1f}x")
        
        # Print current metrics
        metrics = results.get("current_metrics", {})
        if metrics:
            percentiles = metrics.get("percentiles", {})
            targets = metrics.get("targets_met", {})
            
            print(f"\nCurrent Service Metrics:")
            print(f"  Total requests: {metrics.get('request_count', 0)}")
            print(f"  Cache hit rate: {metrics.get('cache_hit_rate', 0):.1%}")
            print(f"  Partial eval rate: {metrics.get('partial_eval_rate', 0):.1%}")
            
            print(f"\nTarget Achievement:")
            print(f"  P50 < 0.5ms: {'✅' if targets.get('p50_under_0_5ms') else '❌'} ({percentiles.get('p50', 0):.3f} ms)")
            print(f"  P95 < 0.8ms: {'✅' if targets.get('p95_under_0_8ms') else '❌'} ({percentiles.get('p95', 0):.3f} ms)")
            print(f"  P99 < 1.0ms: {'✅' if targets.get('p99_under_1ms') else '❌'} ({percentiles.get('p99', 0):.3f} ms)")
            print(f"  Cache > 95%: {'✅' if targets.get('cache_hit_rate_over_95') else '❌'} ({metrics.get('cache_hit_rate', 0):.1%})")
        
        print(f"\nConstitutional Hash: {tester.constitutional_hash}")
        print("="*60)
    
    asyncio.run(main())