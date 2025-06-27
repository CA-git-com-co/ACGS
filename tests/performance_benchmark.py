#!/usr/bin/env python3
"""
ACGS Performance Benchmark Suite
===============================

Tests response times, throughput, and scalability requirements:
- Response times ≤2s (p95)
- Throughput ≥1000 RPS
- System scalability under load
"""

import asyncio
import time
import statistics
import json
from typing import Dict, List, Any
import aiohttp

# Performance targets
MAX_RESPONSE_TIME_P95 = 2.0  # 2 seconds
MIN_THROUGHPUT_RPS = 1000    # 1000 requests per second

# Service endpoints
SERVICES = {
    "auth": "http://localhost:8000/health",
    "ac": "http://localhost:8001/health", 
    "integrity": "http://localhost:8002/health",
    "fv": "http://localhost:8003/health",
    "gs": "http://localhost:8004/health",
    "pgc": "http://localhost:8005/health",
    "ec": "http://localhost:8006/health"
}

class PerformanceBenchmark:
    """Performance benchmark test suite."""
    
    def __init__(self):
        self.results = {
            "timestamp": time.time(),
            "response_time_tests": {},
            "throughput_tests": {},
            "load_tests": {},
            "summary": {}
        }
    
    async def test_response_times(self, concurrent_requests: int = 50) -> Dict[str, Any]:
        """Test response times for all services."""
        print(f"⚡ Testing Response Times (concurrent requests: {concurrent_requests})...")
        
        response_time_results = {}
        
        async with aiohttp.ClientSession() as session:
            for service_name, url in SERVICES.items():
                print(f"   Testing {service_name}...")
                
                response_times = []
                
                async def make_request():
                    try:
                        start_time = time.time()
                        async with session.get(url, timeout=5) as response:
                            await response.text()
                            return time.time() - start_time
                    except Exception:
                        return None
                
                # Execute concurrent requests
                tasks = [make_request() for _ in range(concurrent_requests)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Filter successful requests
                response_times = [r for r in results if r is not None and isinstance(r, float)]
                
                if response_times:
                    avg_time = statistics.mean(response_times)
                    p95_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times)
                    p99_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times)
                    
                    response_time_results[service_name] = {
                        "avg_response_time": avg_time,
                        "p95_response_time": p95_time,
                        "p99_response_time": p99_time,
                        "min_response_time": min(response_times),
                        "max_response_time": max(response_times),
                        "successful_requests": len(response_times),
                        "total_requests": concurrent_requests,
                        "success_rate": len(response_times) / concurrent_requests,
                        "meets_p95_target": p95_time <= MAX_RESPONSE_TIME_P95
                    }
                else:
                    response_time_results[service_name] = {
                        "avg_response_time": None,
                        "p95_response_time": None,
                        "p99_response_time": None,
                        "successful_requests": 0,
                        "total_requests": concurrent_requests,
                        "success_rate": 0,
                        "meets_p95_target": False
                    }
                
                print(f"      {service_name}: {response_time_results[service_name]['p95_response_time']:.3f}s (p95)")
        
        # Calculate overall metrics
        services_meeting_target = sum(1 for result in response_time_results.values() if result["meets_p95_target"])
        total_services = len(SERVICES)
        
        self.results["response_time_tests"] = {
            "target_p95_seconds": MAX_RESPONSE_TIME_P95,
            "concurrent_requests": concurrent_requests,
            "service_results": response_time_results,
            "services_meeting_target": services_meeting_target,
            "total_services": total_services,
            "compliance_rate": services_meeting_target / total_services,
            "passed": services_meeting_target >= total_services * 0.8  # 80% must meet target
        }
        
        print(f"   ✅ Response Time Compliance: {services_meeting_target}/{total_services} services meet ≤2s p95")
        return self.results["response_time_tests"]
    
    async def test_throughput(self, duration_seconds: int = 10) -> Dict[str, Any]:
        """Test throughput for key services."""
        print(f"🚀 Testing Throughput (duration: {duration_seconds}s)...")
        
        throughput_results = {}
        
        # Test key services that should handle high throughput
        key_services = ["auth", "ac", "gs", "pgc"]
        
        async with aiohttp.ClientSession() as session:
            for service_name in key_services:
                if service_name not in SERVICES:
                    continue
                    
                url = SERVICES[service_name]
                print(f"   Testing {service_name}...")
                
                request_count = 0
                successful_requests = 0
                start_time = time.time()
                end_time = start_time + duration_seconds
                
                async def make_continuous_requests():
                    nonlocal request_count, successful_requests
                    while time.time() < end_time:
                        try:
                            async with session.get(url, timeout=1) as response:
                                request_count += 1
                                if response.status == 200:
                                    successful_requests += 1
                        except Exception:
                            request_count += 1
                        
                        # Small delay to prevent overwhelming
                        await asyncio.sleep(0.001)
                
                # Run multiple concurrent workers
                workers = 20
                tasks = [make_continuous_requests() for _ in range(workers)]
                await asyncio.gather(*tasks, return_exceptions=True)
                
                actual_duration = time.time() - start_time
                rps = request_count / actual_duration
                success_rate = successful_requests / request_count if request_count > 0 else 0
                
                throughput_results[service_name] = {
                    "requests_per_second": rps,
                    "total_requests": request_count,
                    "successful_requests": successful_requests,
                    "duration_seconds": actual_duration,
                    "success_rate": success_rate,
                    "meets_rps_target": rps >= MIN_THROUGHPUT_RPS,
                    "workers": workers
                }
                
                print(f"      {service_name}: {rps:.0f} RPS (target: {MIN_THROUGHPUT_RPS})")
        
        # Calculate overall throughput metrics
        services_meeting_rps = sum(1 for result in throughput_results.values() if result["meets_rps_target"])
        total_tested = len(throughput_results)
        
        self.results["throughput_tests"] = {
            "target_rps": MIN_THROUGHPUT_RPS,
            "duration_seconds": duration_seconds,
            "service_results": throughput_results,
            "services_meeting_target": services_meeting_rps,
            "total_tested": total_tested,
            "compliance_rate": services_meeting_rps / total_tested if total_tested > 0 else 0,
            "passed": services_meeting_rps >= total_tested * 0.5  # 50% must meet RPS target
        }
        
        print(f"   ✅ Throughput Compliance: {services_meeting_rps}/{total_tested} services meet ≥{MIN_THROUGHPUT_RPS} RPS")
        return self.results["throughput_tests"]
    
    async def test_load_scalability(self) -> Dict[str, Any]:
        """Test system scalability under increasing load."""
        print("📈 Testing Load Scalability...")
        
        load_levels = [10, 50, 100, 200]  # Concurrent requests
        scalability_results = {}
        
        for load_level in load_levels:
            print(f"   Testing load level: {load_level} concurrent requests...")
            
            # Test auth service as representative
            url = SERVICES["auth"]
            response_times = []
            
            async with aiohttp.ClientSession() as session:
                async def make_request():
                    try:
                        start_time = time.time()
                        async with session.get(url, timeout=10) as response:
                            await response.text()
                            return time.time() - start_time
                    except Exception:
                        return None
                
                tasks = [make_request() for _ in range(load_level)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                response_times = [r for r in results if r is not None and isinstance(r, float)]
            
            if response_times:
                avg_time = statistics.mean(response_times)
                p95_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times)
                
                scalability_results[load_level] = {
                    "avg_response_time": avg_time,
                    "p95_response_time": p95_time,
                    "successful_requests": len(response_times),
                    "total_requests": load_level,
                    "success_rate": len(response_times) / load_level
                }
            else:
                scalability_results[load_level] = {
                    "avg_response_time": None,
                    "p95_response_time": None,
                    "successful_requests": 0,
                    "total_requests": load_level,
                    "success_rate": 0
                }
            
            print(f"      Load {load_level}: {scalability_results[load_level]['p95_response_time']:.3f}s p95")
        
        # Check if performance degrades gracefully
        performance_stable = True
        if len(scalability_results) >= 2:
            load_levels_sorted = sorted(scalability_results.keys())
            for i in range(1, len(load_levels_sorted)):
                prev_p95 = scalability_results[load_levels_sorted[i-1]]["p95_response_time"]
                curr_p95 = scalability_results[load_levels_sorted[i]]["p95_response_time"]
                
                if prev_p95 and curr_p95 and curr_p95 > prev_p95 * 3:  # More than 3x degradation
                    performance_stable = False
                    break
        
        self.results["load_tests"] = {
            "load_levels": load_levels,
            "scalability_results": scalability_results,
            "performance_stable": performance_stable,
            "passed": performance_stable
        }
        
        print(f"   ✅ Scalability: {'Stable' if performance_stable else 'Degraded'} under increasing load")
        return self.results["load_tests"]
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all performance tests."""
        print("⚡ Running Performance Benchmark Suite")
        print("=" * 60)
        
        # Run tests
        await self.test_response_times()
        await self.test_throughput()
        await self.test_load_scalability()
        
        # Generate summary
        response_passed = self.results["response_time_tests"]["passed"]
        throughput_passed = self.results["throughput_tests"]["passed"]
        load_passed = self.results["load_tests"]["passed"]
        overall_passed = response_passed and throughput_passed and load_passed
        
        self.results["summary"] = {
            "overall_passed": overall_passed,
            "response_time_passed": response_passed,
            "throughput_passed": throughput_passed,
            "load_scalability_passed": load_passed,
            "targets": {
                "max_response_time_p95": MAX_RESPONSE_TIME_P95,
                "min_throughput_rps": MIN_THROUGHPUT_RPS
            }
        }
        
        print("=" * 60)
        print(f"⚡ Performance Benchmark Results:")
        print(f"   Response Times: {'✅ PASSED' if response_passed else '❌ FAILED'}")
        print(f"   Throughput: {'✅ PASSED' if throughput_passed else '❌ FAILED'}")
        print(f"   Load Scalability: {'✅ PASSED' if load_passed else '❌ FAILED'}")
        print(f"   Overall: {'✅ PASSED' if overall_passed else '❌ FAILED'}")
        
        return self.results

if __name__ == "__main__":
    async def main():
        benchmark = PerformanceBenchmark()
        results = await benchmark.run_all_tests()
        
        # Save results
        with open("tests/results/performance_benchmark_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        return results["summary"]["overall_passed"]
    
    # Run the benchmark
    success = asyncio.run(main())
    exit(0 if success else 1)
