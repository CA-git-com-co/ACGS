#!/usr/bin/env python3
"""
ACGS-1 Lite Policy Engine Optimization Benchmark Script
Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import statistics
import time
from typing import Dict, List
import sys
import argparse

import httpx


class PolicyEngineBenchmark:
    """Comprehensive benchmark suite for policy engine optimization"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.results = {}
    
    def print_header(self):
        """Print benchmark header"""
        print("="*80)
        print("ACGS-1 Lite Policy Engine Optimization Benchmark")
        print(f"Constitutional Hash: {self.constitutional_hash}")
        print(f"Target URL: {self.base_url}")
        print("="*80)
    
    async def check_service_health(self) -> bool:
        """Check if the policy engine service is healthy"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/v1/data/acgs/main/health")
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Service is healthy")
                    print(f"   Version: {data.get('version', 'unknown')}")
                    print(f"   Constitutional Hash: {data.get('constitutional_hash', 'unknown')}")
                    return True
                else:
                    print(f"❌ Service health check failed: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ Failed to connect to service: {e}")
            return False
    
    async def warm_up_service(self, num_requests: int = 100):
        """Warm up the service to ensure stable measurements"""
        print(f"\n🔥 Warming up service with {num_requests} requests...")
        
        warm_up_request = {
            "type": "constitutional_evaluation",
            "constitutional_hash": self.constitutional_hash,
            "action": "data.read_public",
            "context": {
                "environment": {"sandbox_enabled": True, "audit_enabled": True},
                "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
                "responsible_party": "warmup",
                "explanation": "Service warm-up request"
            }
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(num_requests):
                if i % 20 == 0:
                    print(f"   Warm-up progress: {i}/{num_requests}")
                try:
                    await client.post(f"{self.base_url}/v1/data/acgs/main/decision", json=warm_up_request)
                except Exception as e:
                    print(f"   Warm-up request {i} failed: {e}")
        
        print("✅ Warm-up completed")
    
    async def benchmark_baseline_latency(self, num_requests: int = 5000) -> Dict[str, float]:
        """Benchmark baseline policy evaluation latency"""
        print(f"\n📊 Running baseline latency benchmark ({num_requests} requests)...")
        
        test_request = {
            "type": "constitutional_evaluation",
            "constitutional_hash": self.constitutional_hash,
            "action": "data.read_public",
            "context": {
                "environment": {"sandbox_enabled": True, "audit_enabled": True},
                "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
                "responsible_party": "benchmark",
                "explanation": "Baseline latency benchmark"
            }
        }
        
        latencies = []
        errors = 0
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            start_time = time.perf_counter()
            
            for i in range(num_requests):
                if i % 500 == 0 and i > 0:
                    print(f"   Progress: {i}/{num_requests} ({i/num_requests*100:.1f}%)")
                
                request_start = time.perf_counter_ns()
                try:
                    response = await client.post(f"{self.base_url}/v1/data/acgs/main/decision", json=test_request)
                    request_end = time.perf_counter_ns()
                    
                    if response.status_code == 200:
                        latency_ms = (request_end - request_start) / 1_000_000
                        latencies.append(latency_ms)
                    else:
                        errors += 1
                        print(f"   Request {i} failed: {response.status_code}")
                except Exception as e:
                    errors += 1
                    request_end = time.perf_counter_ns()
                    print(f"   Request {i} error: {e}")
            
            total_time = time.perf_counter() - start_time
        
        if not latencies:
            return {"error": "No successful requests", "total_errors": errors}
        
        # Calculate statistics
        latencies.sort()
        n = len(latencies)
        
        results = {
            "total_requests": num_requests,
            "successful_requests": n,
            "failed_requests": errors,
            "total_time_seconds": total_time,
            "requests_per_second": n / total_time,
            "avg_latency_ms": statistics.mean(latencies),
            "median_latency_ms": statistics.median(latencies),
            "p50_latency_ms": latencies[int(0.5 * n)],
            "p90_latency_ms": latencies[int(0.9 * n)],
            "p95_latency_ms": latencies[int(0.95 * n)],
            "p99_latency_ms": latencies[int(0.99 * n)],
            "p999_latency_ms": latencies[int(0.999 * n)] if n >= 1000 else latencies[-1],
            "max_latency_ms": max(latencies),
            "min_latency_ms": min(latencies),
            "std_dev_ms": statistics.stdev(latencies) if n > 1 else 0.0
        }
        
        print(f"✅ Baseline benchmark completed: {results['requests_per_second']:.0f} RPS, P99: {results['p99_latency_ms']:.3f}ms")
        return results
    
    async def benchmark_cache_effectiveness(self) -> Dict[str, float]:
        """Benchmark cache hit rates and performance impact"""
        print(f"\n🗄️  Running cache effectiveness benchmark...")
        
        # Test request that should be cacheable
        cacheable_request = {
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
            response = await client.post(f"{self.base_url}/v1/data/acgs/main/decision", json=cacheable_request)
            miss_time_ms = (time.perf_counter_ns() - miss_start) / 1_000_000
            
            if response.status_code != 200:
                return {"error": f"Cache miss request failed: {response.status_code}"}
            
            # Multiple subsequent requests (cache hits)
            hit_times = []
            for _ in range(200):
                hit_start = time.perf_counter_ns()
                response = await client.post(f"{self.base_url}/v1/data/acgs/main/decision", json=cacheable_request)
                hit_time_ms = (time.perf_counter_ns() - hit_start) / 1_000_000
                
                if response.status_code == 200:
                    hit_times.append(hit_time_ms)
            
            if not hit_times:
                return {"error": "No successful cache hit requests"}
            
            avg_hit_time = statistics.mean(hit_times)
            p99_hit_time = sorted(hit_times)[int(0.99 * len(hit_times))]
            
            results = {
                "cache_miss_latency_ms": miss_time_ms,
                "cache_hit_avg_latency_ms": avg_hit_time,
                "cache_hit_p99_latency_ms": p99_hit_time,
                "cache_speedup_factor": miss_time_ms / avg_hit_time if avg_hit_time > 0 else 0,
                "cache_hit_requests": len(hit_times)
            }
            
            print(f"✅ Cache benchmark completed: {results['cache_speedup_factor']:.1f}x speedup")
            return results
    
    async def benchmark_different_scenarios(self) -> Dict[str, Dict[str, float]]:
        """Benchmark different policy evaluation scenarios"""
        print(f"\n🎭 Running multi-scenario benchmark...")
        
        scenarios = {
            "safe_action": {
                "type": "constitutional_evaluation",
                "constitutional_hash": self.constitutional_hash,
                "action": "data.read_public",
                "context": {
                    "environment": {"sandbox_enabled": True, "audit_enabled": True},
                    "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
                    "responsible_party": "test", "explanation": "Safe action test"
                }
            },
            "dangerous_action": {
                "type": "constitutional_evaluation",
                "constitutional_hash": self.constitutional_hash,
                "action": "system.execute_shell",
                "context": {
                    "environment": {"sandbox_enabled": True},
                    "agent": {"trust_level": 0.5}
                }
            },
            "data_access": {
                "type": "data_access",
                "constitutional_hash": self.constitutional_hash,
                "data_request": {
                    "data_fields": [{"name": "public_data", "classification_level": 0, "category": "public"}],
                    "requester_clearance_level": 1,
                    "purpose": "display",
                    "allowed_purposes": ["display"],
                    "justified_fields": ["public_data"],
                    "timestamp": 1704067200,
                    "retention_policy": {"public": 86400},
                    "encryption_config": {"public_data": {"encrypted": False}}
                }
            },
            "evolution_approval": {
                "type": "evolution_approval",
                "constitutional_hash": self.constitutional_hash,
                "evolution_request": {
                    "type": "patch",
                    "constitutional_hash": self.constitutional_hash,
                    "changes": {"code_changes": ["Bug fix"], "external_dependencies": [], "privilege_escalation": False},
                    "performance_analysis": {"complexity_delta": 0.01, "memory_delta": 0.005, "latency_delta": 0.0, "resource_delta": 0.0},
                    "rollback_plan": {"procedure": "Git revert", "verification": "Tests", "timeline": "5 min", "dependencies": "None", "tested": True, "automated": True}
                }
            }
        }
        
        results = {}
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for scenario_name, scenario_request in scenarios.items():
                print(f"   Testing scenario: {scenario_name}")
                
                latencies = []
                num_requests = 100
                
                for _ in range(num_requests):
                    start = time.perf_counter_ns()
                    response = await client.post(f"{self.base_url}/v1/data/acgs/main/decision", json=scenario_request)
                    end = time.perf_counter_ns()
                    
                    if response.status_code == 200:
                        latencies.append((end - start) / 1_000_000)
                
                if latencies:
                    latencies.sort()
                    n = len(latencies)
                    results[scenario_name] = {
                        "successful_requests": n,
                        "avg_latency_ms": statistics.mean(latencies),
                        "p50_latency_ms": latencies[int(0.5 * n)],
                        "p95_latency_ms": latencies[int(0.95 * n)],
                        "p99_latency_ms": latencies[int(0.99 * n)],
                        "max_latency_ms": max(latencies),
                        "min_latency_ms": min(latencies)
                    }
                else:
                    results[scenario_name] = {"error": "No successful requests"}
        
        print(f"✅ Multi-scenario benchmark completed")
        return results
    
    async def benchmark_concurrent_load(self, concurrent_users: int = 50, requests_per_user: int = 100) -> Dict[str, float]:
        """Benchmark concurrent load handling"""
        print(f"\n⚡ Running concurrent load benchmark ({concurrent_users} users, {requests_per_user} requests each)...")
        
        test_request = {
            "type": "constitutional_evaluation",
            "constitutional_hash": self.constitutional_hash,
            "action": "data.read_public",
            "context": {
                "environment": {"sandbox_enabled": True, "audit_enabled": True},
                "agent": {"trust_level": 0.9, "requested_resources": {"cpu_cores": 1}},
                "responsible_party": "load_test",
                "explanation": "Concurrent load test"
            }
        }
        
        async def user_session(user_id: int) -> List[float]:
            """Simulate a single user session"""
            latencies = []
            async with httpx.AsyncClient(timeout=30.0) as client:
                for _ in range(requests_per_user):
                    start = time.perf_counter_ns()
                    try:
                        response = await client.post(f"{self.base_url}/v1/data/acgs/main/decision", json=test_request)
                        end = time.perf_counter_ns()
                        if response.status_code == 200:
                            latencies.append((end - start) / 1_000_000)
                    except Exception as e:
                        print(f"   User {user_id} request failed: {e}")
            return latencies
        
        # Run concurrent users
        start_time = time.perf_counter()
        tasks = [user_session(i) for i in range(concurrent_users)]
        user_results = await asyncio.gather(*tasks)
        total_time = time.perf_counter() - start_time
        
        # Aggregate results
        all_latencies = []
        total_requests = 0
        successful_requests = 0
        
        for user_latencies in user_results:
            all_latencies.extend(user_latencies)
            total_requests += requests_per_user
            successful_requests += len(user_latencies)
        
        if not all_latencies:
            return {"error": "No successful requests"}
        
        all_latencies.sort()
        n = len(all_latencies)
        
        results = {
            "concurrent_users": concurrent_users,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": total_requests - successful_requests,
            "total_time_seconds": total_time,
            "overall_rps": successful_requests / total_time,
            "avg_latency_ms": statistics.mean(all_latencies),
            "p50_latency_ms": all_latencies[int(0.5 * n)],
            "p95_latency_ms": all_latencies[int(0.95 * n)],
            "p99_latency_ms": all_latencies[int(0.99 * n)],
            "max_latency_ms": max(all_latencies)
        }
        
        print(f"✅ Concurrent load benchmark completed: {results['overall_rps']:.0f} RPS")
        return results
    
    async def get_service_metrics(self) -> Dict[str, any]:
        """Get current service metrics"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{self.base_url}/v1/metrics")
                if response.status_code == 200:
                    return response.json()
                else:
                    return {"error": f"Metrics request failed: {response.status_code}"}
        except Exception as e:
            return {"error": f"Failed to get metrics: {e}"}
    
    def print_results(self):
        """Print comprehensive benchmark results"""
        print("\n" + "="*80)
        print("BENCHMARK RESULTS SUMMARY")
        print("="*80)
        
        # Baseline latency results
        if "baseline" in self.results:
            baseline = self.results["baseline"]
            print(f"\n📊 BASELINE LATENCY PERFORMANCE:")
            print(f"   Total Requests: {baseline.get('total_requests', 0)}")
            print(f"   Success Rate:   {baseline.get('successful_requests', 0)}/{baseline.get('total_requests', 0)} ({baseline.get('successful_requests', 0)/baseline.get('total_requests', 1)*100:.1f}%)")
            print(f"   Throughput:     {baseline.get('requests_per_second', 0):.0f} RPS")
            print(f"   Average:        {baseline.get('avg_latency_ms', 0):.3f} ms")
            print(f"   P50:            {baseline.get('p50_latency_ms', 0):.3f} ms")
            print(f"   P95:            {baseline.get('p95_latency_ms', 0):.3f} ms")
            print(f"   P99:            {baseline.get('p99_latency_ms', 0):.3f} ms")
            print(f"   P99.9:          {baseline.get('p999_latency_ms', 0):.3f} ms")
            print(f"   Max:            {baseline.get('max_latency_ms', 0):.3f} ms")
            print(f"   Std Dev:        {baseline.get('std_dev_ms', 0):.3f} ms")
        
        # Cache effectiveness results
        if "cache" in self.results:
            cache = self.results["cache"]
            print(f"\n🗄️  CACHE EFFECTIVENESS:")
            print(f"   Cache Miss:     {cache.get('cache_miss_latency_ms', 0):.3f} ms")
            print(f"   Cache Hit Avg:  {cache.get('cache_hit_avg_latency_ms', 0):.3f} ms")
            print(f"   Cache Hit P99:  {cache.get('cache_hit_p99_latency_ms', 0):.3f} ms")
            print(f"   Speedup Factor: {cache.get('cache_speedup_factor', 0):.1f}x")
        
        # Scenario results
        if "scenarios" in self.results:
            scenarios = self.results["scenarios"]
            print(f"\n🎭 SCENARIO PERFORMANCE:")
            for scenario_name, scenario_data in scenarios.items():
                if "error" not in scenario_data:
                    print(f"   {scenario_name.replace('_', ' ').title()}:")
                    print(f"     P99: {scenario_data.get('p99_latency_ms', 0):.3f} ms")
                    print(f"     Avg: {scenario_data.get('avg_latency_ms', 0):.3f} ms")
        
        # Concurrent load results
        if "concurrent" in self.results:
            concurrent = self.results["concurrent"]
            print(f"\n⚡ CONCURRENT LOAD PERFORMANCE:")
            print(f"   Concurrent Users: {concurrent.get('concurrent_users', 0)}")
            print(f"   Success Rate:     {concurrent.get('successful_requests', 0)}/{concurrent.get('total_requests', 0)} ({concurrent.get('successful_requests', 0)/concurrent.get('total_requests', 1)*100:.1f}%)")
            print(f"   Overall RPS:      {concurrent.get('overall_rps', 0):.0f}")
            print(f"   P99 Latency:      {concurrent.get('p99_latency_ms', 0):.3f} ms")
            print(f"   Max Latency:      {concurrent.get('max_latency_ms', 0):.3f} ms")
        
        # Service metrics
        if "service_metrics" in self.results:
            metrics = self.results["service_metrics"]
            if "error" not in metrics:
                targets = metrics.get("targets_met", {})
                print(f"\n📈 SERVICE METRICS:")
                print(f"   Total Requests:    {metrics.get('request_count', 0)}")
                print(f"   Cache Hit Rate:    {metrics.get('cache_hit_rate', 0):.1%}")
                print(f"   L1 Hit Rate:       {metrics.get('l1_hit_rate', 0):.1%}")
                print(f"   L2 Hit Rate:       {metrics.get('l2_hit_rate', 0):.1%}")
                print(f"   Partial Eval Rate: {metrics.get('partial_eval_rate', 0):.1%}")
                
                print(f"\n🎯 TARGET ACHIEVEMENT:")
                print(f"   P50 < 0.5ms:  {'✅' if targets.get('p50_under_0_5ms') else '❌'}")
                print(f"   P95 < 0.8ms:  {'✅' if targets.get('p95_under_0_8ms') else '❌'}")
                print(f"   P99 < 1.0ms:  {'✅' if targets.get('p99_under_1ms') else '❌'}")
                print(f"   Cache > 95%:  {'✅' if targets.get('cache_hit_rate_over_95') else '❌'}")
        
        print(f"\n🔒 Constitutional Hash: {self.constitutional_hash}")
        print("="*80)
    
    async def run_full_benchmark(self):
        """Run the complete benchmark suite"""
        self.print_header()
        
        # Check service health
        if not await self.check_service_health():
            print("❌ Cannot proceed with benchmark - service is not healthy")
            sys.exit(1)
        
        # Warm up service
        await self.warm_up_service()
        
        # Run baseline benchmark
        self.results["baseline"] = await self.benchmark_baseline_latency()
        
        # Run cache effectiveness benchmark
        self.results["cache"] = await self.benchmark_cache_effectiveness()
        
        # Run scenario benchmarks
        self.results["scenarios"] = await self.benchmark_different_scenarios()
        
        # Run concurrent load benchmark
        self.results["concurrent"] = await self.benchmark_concurrent_load()
        
        # Get service metrics
        self.results["service_metrics"] = await self.get_service_metrics()
        
        # Print results
        self.print_results()
        
        return self.results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ACGS-1 Lite Policy Engine Benchmark")
    parser.add_argument("--url", default="http://localhost:8004", help="Base URL of the policy engine service")
    parser.add_argument("--requests", type=int, default=5000, help="Number of requests for baseline benchmark")
    parser.add_argument("--concurrent-users", type=int, default=50, help="Number of concurrent users for load test")
    parser.add_argument("--requests-per-user", type=int, default=100, help="Number of requests per user in load test")
    
    args = parser.parse_args()
    
    benchmark = PolicyEngineBenchmark(args.url)
    
    async def run_benchmark():
        return await benchmark.run_full_benchmark()
    
    try:
        results = asyncio.run(run_benchmark())
    except KeyboardInterrupt:
        print("\n❌ Benchmark interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        sys.exit(1)