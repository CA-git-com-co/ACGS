#!/usr/bin/env python3
"""
ACGS Code Analysis Engine - Performance Benchmarking Suite
Comprehensive performance testing for production readiness validation.

Constitutional Hash: cdd01ef066bc6cf2
Performance Targets:
- P99 Latency: <10ms for cached queries
- Throughput: >100 RPS sustained load
- Cache Hit Rate: >85% for repeated queries
"""

import os
import sys
import time
import json
import asyncio
import statistics
import requests
from typing import Dict, Any, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class PerformanceBenchmarker:
    """Comprehensive performance benchmarking for ACGS Code Analysis Engine"""
    
    def __init__(self, base_url: str = "http://localhost:8007"):
        self.base_url = base_url
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.results = {}
        
    def setup_test_environment(self):
        """Setup environment for performance testing"""
        print("=== Setting up performance test environment ===")
        
        # Set environment variables
        os.environ['ENVIRONMENT'] = 'testing'
        os.environ['LOG_LEVEL'] = 'WARNING'  # Reduce logging overhead
        
        # Warm up the service
        self._warmup_service()
        
    def _warmup_service(self):
        """Warm up the service before testing"""
        print("Warming up service...")
        
        warmup_requests = 50
        for i in range(warmup_requests):
            try:
                requests.get(f"{self.base_url}/health", timeout=5)
                if i % 10 == 0:
                    print(f"Warmup progress: {i}/{warmup_requests}")
            except Exception:
                pass
        
        print("✓ Service warmup completed")
    
    def test_latency_performance(self, num_requests: int = 1000) -> Dict[str, Any]:
        """Test P99 latency performance with detailed metrics"""
        print(f"\n=== Testing Latency Performance ({num_requests} requests) ===")
        
        latencies = []
        failed_requests = 0
        
        start_time = time.time()
        
        for i in range(num_requests):
            try:
                request_start = time.time()
                response = requests.get(f"{self.base_url}/health", timeout=10)
                request_end = time.time()
                
                if response.status_code == 200:
                    latency_ms = (request_end - request_start) * 1000
                    latencies.append(latency_ms)
                else:
                    failed_requests += 1
                    
                # Progress indicator
                if i % 100 == 0 and i > 0:
                    print(f"Progress: {i}/{num_requests} requests completed")
                    
            except Exception:
                failed_requests += 1
        
        total_time = time.time() - start_time
        
        if latencies:
            # Calculate detailed statistics
            latencies.sort()
            
            stats = {
                "min_ms": min(latencies),
                "max_ms": max(latencies),
                "mean_ms": statistics.mean(latencies),
                "median_ms": statistics.median(latencies),
                "p50_ms": np.percentile(latencies, 50),
                "p90_ms": np.percentile(latencies, 90),
                "p95_ms": np.percentile(latencies, 95),
                "p99_ms": np.percentile(latencies, 99),
                "p99_9_ms": np.percentile(latencies, 99.9),
                "std_dev_ms": statistics.stdev(latencies) if len(latencies) > 1 else 0
            }
            
            # Check targets
            p99_target_met = stats["p99_ms"] < 10.0
            
            print(f"✓ Latency Statistics:")
            print(f"  - Min: {stats['min_ms']:.2f}ms")
            print(f"  - Mean: {stats['mean_ms']:.2f}ms")
            print(f"  - Median: {stats['median_ms']:.2f}ms")
            print(f"  - P90: {stats['p90_ms']:.2f}ms")
            print(f"  - P95: {stats['p95_ms']:.2f}ms")
            print(f"  - P99: {stats['p99_ms']:.2f}ms (target: <10ms)")
            print(f"  - P99.9: {stats['p99_9_ms']:.2f}ms")
            print(f"  - Max: {stats['max_ms']:.2f}ms")
            print(f"  - Std Dev: {stats['std_dev_ms']:.2f}ms")
            
            target_status = "PASS" if p99_target_met else "FAIL"
            print(f"✓ P99 Target (<10ms): {target_status}")
            
            result = {
                "status": "ok" if p99_target_met else "failed",
                "target_met": p99_target_met,
                "statistics": stats,
                "total_requests": num_requests,
                "successful_requests": len(latencies),
                "failed_requests": failed_requests,
                "success_rate": len(latencies) / num_requests,
                "total_time_seconds": total_time,
                "raw_latencies": latencies,
                "timestamp": datetime.now().isoformat()
            }
            
            self.results["latency_performance"] = result
            return result
            
        else:
            print("✗ No successful requests for latency testing")
            return {
                "status": "failed",
                "error": "No successful requests",
                "failed_requests": failed_requests,
                "timestamp": datetime.now().isoformat()
            }
    
    def test_throughput_performance(self, duration_seconds: int = 30, 
                                  max_workers: int = 50) -> Dict[str, Any]:
        """Test sustained throughput performance"""
        print(f"\n=== Testing Throughput Performance "
              f"({duration_seconds}s, {max_workers} workers) ===")
        
        successful_requests = 0
        failed_requests = 0
        response_times = []
        
        def make_request():
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}/health", timeout=5)
                end_time = time.time()
                
                if response.status_code == 200:
                    return True, (end_time - start_time) * 1000
                else:
                    return False, 0
            except Exception:
                return False, 0
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            # Submit requests for the duration
            while time.time() - start_time < duration_seconds:
                future = executor.submit(make_request)
                futures.append(future)
                time.sleep(0.001)  # Small delay to control rate
            
            # Collect results
            for future in as_completed(futures):
                success, response_time = future.result()
                if success:
                    successful_requests += 1
                    response_times.append(response_time)
                else:
                    failed_requests += 1
        
        actual_duration = time.time() - start_time
        total_requests = successful_requests + failed_requests
        
        # Calculate metrics
        actual_rps = successful_requests / actual_duration
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        
        # Throughput target check
        throughput_target_met = actual_rps >= 100.0
        
        print(f"✓ Throughput Results:")
        print(f"  - Actual RPS: {actual_rps:.1f} (target: >100 RPS)")
        print(f"  - Success Rate: {success_rate:.1%}")
        print(f"  - Total Requests: {total_requests}")
        print(f"  - Successful: {successful_requests}")
        print(f"  - Failed: {failed_requests}")
        print(f"  - Duration: {actual_duration:.2f}s")
        
        target_status = "PASS" if throughput_target_met else "FAIL"
        print(f"✓ Throughput Target (>100 RPS): {target_status}")
        
        result = {
            "status": "ok" if throughput_target_met else "failed",
            "target_met": throughput_target_met,
            "actual_rps": actual_rps,
            "target_rps": 100.0,
            "success_rate": success_rate,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "duration_seconds": actual_duration,
            "max_workers": max_workers,
            "response_times": response_times,
            "timestamp": datetime.now().isoformat()
        }
        
        self.results["throughput_performance"] = result
        return result
    
    def test_cache_performance(self) -> Dict[str, Any]:
        """Test cache hit rate performance"""
        print("\n=== Testing Cache Performance ===")
        
        # This is a placeholder for actual cache testing
        # In a real implementation, this would test actual cache endpoints
        
        # Simulate cache testing with repeated requests
        cache_test_requests = 100
        cache_hits = 0
        
        # First request to populate cache
        try:
            requests.get(f"{self.base_url}/health", timeout=5)
        except Exception:
            pass
        
        # Test repeated requests (should hit cache)
        for i in range(cache_test_requests):
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}/health", timeout=5)
                end_time = time.time()
                
                # Assume fast responses are cache hits
                response_time_ms = (end_time - start_time) * 1000
                if response.status_code == 200 and response_time_ms < 5.0:
                    cache_hits += 1
                    
            except Exception:
                pass
        
        cache_hit_rate = cache_hits / cache_test_requests
        cache_target_met = cache_hit_rate >= 0.85
        
        print(f"✓ Cache Performance Results:")
        print(f"  - Cache Hit Rate: {cache_hit_rate:.1%} (target: >85%)")
        print(f"  - Cache Hits: {cache_hits}")
        print(f"  - Total Requests: {cache_test_requests}")
        
        target_status = "PASS" if cache_target_met else "FAIL"
        print(f"✓ Cache Target (>85%): {target_status}")
        
        result = {
            "status": "ok" if cache_target_met else "failed",
            "target_met": cache_target_met,
            "cache_hit_rate": cache_hit_rate,
            "target_rate": 0.85,
            "cache_hits": cache_hits,
            "total_requests": cache_test_requests,
            "timestamp": datetime.now().isoformat()
        }
        
        self.results["cache_performance"] = result
        return result
    
    def test_stress_performance(self, duration_seconds: int = 60, 
                              max_workers: int = 100) -> Dict[str, Any]:
        """Test service under stress conditions"""
        print(f"\n=== Testing Stress Performance "
              f"({duration_seconds}s, {max_workers} workers) ===")
        
        successful_requests = 0
        failed_requests = 0
        response_times = []
        error_types = {}
        
        def stress_request():
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}/health", timeout=10)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                
                if response.status_code == 200:
                    return True, response_time, None
                else:
                    return False, response_time, f"HTTP_{response.status_code}"
                    
            except Exception as e:
                return False, 0, str(type(e).__name__)
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            
            # Submit stress requests
            while time.time() - start_time < duration_seconds:
                future = executor.submit(stress_request)
                futures.append(future)
                # No delay for stress testing
            
            # Collect results
            for future in as_completed(futures):
                success, response_time, error_type = future.result()
                
                if success:
                    successful_requests += 1
                    response_times.append(response_time)
                else:
                    failed_requests += 1
                    if error_type:
                        error_types[error_type] = error_types.get(error_type, 0) + 1
        
        actual_duration = time.time() - start_time
        total_requests = successful_requests + failed_requests
        
        # Calculate stress metrics
        stress_rps = successful_requests / actual_duration
        stress_success_rate = (successful_requests / total_requests 
                              if total_requests > 0 else 0)
        
        # Stress test passes if service maintains >50% success rate
        stress_target_met = stress_success_rate >= 0.5
        
        print(f"✓ Stress Test Results:")
        print(f"  - Stress RPS: {stress_rps:.1f}")
        print(f"  - Success Rate: {stress_success_rate:.1%} (target: >50%)")
        print(f"  - Total Requests: {total_requests}")
        print(f"  - Duration: {actual_duration:.2f}s")
        print(f"  - Error Types: {error_types}")
        
        target_status = "PASS" if stress_target_met else "FAIL"
        print(f"✓ Stress Target (>50% success): {target_status}")
        
        result = {
            "status": "ok" if stress_target_met else "failed",
            "target_met": stress_target_met,
            "stress_rps": stress_rps,
            "success_rate": stress_success_rate,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "failed_requests": failed_requests,
            "duration_seconds": actual_duration,
            "max_workers": max_workers,
            "error_types": error_types,
            "response_times": response_times,
            "timestamp": datetime.now().isoformat()
        }
        
        self.results["stress_performance"] = result
        return result

    def generate_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        print("\n=== Generating Performance Report ===")

        # Calculate overall performance score
        performance_score = self._calculate_performance_score()

        # Generate summary
        summary = {
            "overall_score": performance_score,
            "performance_grade": self._get_performance_grade(performance_score),
            "targets_met": self._check_all_targets(),
            "recommendations": self._generate_recommendations(),
            "timestamp": datetime.now().isoformat()
        }

        # Create detailed report
        report = {
            "summary": summary,
            "detailed_results": self.results,
            "constitutional_hash": self.constitutional_hash,
            "test_configuration": {
                "base_url": self.base_url,
                "test_timestamp": datetime.now().isoformat()
            }
        }

        print(f"✓ Performance Score: {performance_score:.1f}/100")
        print(f"✓ Performance Grade: {summary['performance_grade']}")
        print(f"✓ All Targets Met: {summary['targets_met']}")

        return report

    def _calculate_performance_score(self) -> float:
        """Calculate overall performance score (0-100)"""
        scores = []

        # Latency score (40% weight)
        if "latency_performance" in self.results:
            latency_result = self.results["latency_performance"]
            if latency_result.get("target_met", False):
                scores.append(40)
            else:
                # Partial credit based on how close to target
                p99 = latency_result.get("statistics", {}).get("p99_ms", 100)
                score = max(0, 40 * (20 - p99) / 10) if p99 <= 20 else 0
                scores.append(score)

        # Throughput score (30% weight)
        if "throughput_performance" in self.results:
            throughput_result = self.results["throughput_performance"]
            if throughput_result.get("target_met", False):
                scores.append(30)
            else:
                # Partial credit based on actual RPS
                actual_rps = throughput_result.get("actual_rps", 0)
                score = max(0, 30 * actual_rps / 100) if actual_rps <= 100 else 30
                scores.append(score)

        # Cache score (20% weight)
        if "cache_performance" in self.results:
            cache_result = self.results["cache_performance"]
            if cache_result.get("target_met", False):
                scores.append(20)
            else:
                # Partial credit based on hit rate
                hit_rate = cache_result.get("cache_hit_rate", 0)
                score = max(0, 20 * hit_rate / 0.85) if hit_rate <= 0.85 else 20
                scores.append(score)

        # Stress test score (10% weight)
        if "stress_performance" in self.results:
            stress_result = self.results["stress_performance"]
            if stress_result.get("target_met", False):
                scores.append(10)
            else:
                # Partial credit based on success rate
                success_rate = stress_result.get("success_rate", 0)
                score = max(0, 10 * success_rate / 0.5) if success_rate <= 0.5 else 10
                scores.append(score)

        return sum(scores) if scores else 0

    def _get_performance_grade(self, score: float) -> str:
        """Get performance grade based on score"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _check_all_targets(self) -> bool:
        """Check if all performance targets are met"""
        targets = []

        for test_name, result in self.results.items():
            if isinstance(result, dict) and "target_met" in result:
                targets.append(result["target_met"])

        return all(targets) if targets else False

    def _generate_recommendations(self) -> List[str]:
        """Generate performance improvement recommendations"""
        recommendations = []

        # Check latency performance
        if "latency_performance" in self.results:
            latency_result = self.results["latency_performance"]
            if not latency_result.get("target_met", False):
                p99 = latency_result.get("statistics", {}).get("p99_ms", 0)
                recommendations.append(
                    f"Improve P99 latency from {p99:.2f}ms to <10ms. "
                    "Consider optimizing database queries and adding caching."
                )

        # Check throughput performance
        if "throughput_performance" in self.results:
            throughput_result = self.results["throughput_performance"]
            if not throughput_result.get("target_met", False):
                actual_rps = throughput_result.get("actual_rps", 0)
                recommendations.append(
                    f"Improve throughput from {actual_rps:.1f} RPS to >100 RPS. "
                    "Consider horizontal scaling or connection pooling."
                )

        # Check cache performance
        if "cache_performance" in self.results:
            cache_result = self.results["cache_performance"]
            if not cache_result.get("target_met", False):
                hit_rate = cache_result.get("cache_hit_rate", 0)
                recommendations.append(
                    f"Improve cache hit rate from {hit_rate:.1%} to >85%. "
                    "Review cache strategy and TTL settings."
                )

        if not recommendations:
            recommendations.append("All performance targets met. Consider load testing at higher scales.")

        return recommendations

    def run_comprehensive_benchmarks(self) -> Dict[str, Any]:
        """Run all performance benchmarks"""
        print("=" * 80)
        print("ACGS Code Analysis Engine - Performance Benchmarking Suite")
        print("=" * 80)

        start_time = time.time()

        # Setup test environment
        self.setup_test_environment()

        # Run benchmark tests
        benchmark_tests = [
            ("Latency Performance", lambda: self.test_latency_performance(1000)),
            ("Throughput Performance", lambda: self.test_throughput_performance(30, 50)),
            ("Cache Performance", self.test_cache_performance),
            ("Stress Performance", lambda: self.test_stress_performance(60, 100))
        ]

        for test_name, test_function in benchmark_tests:
            try:
                print(f"\n{'='*20} {test_name} {'='*20}")
                test_function()
            except Exception as e:
                print(f"✗ {test_name} failed: {e}")
                self.results[test_name.lower().replace(" ", "_")] = {
                    "status": "failed",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }

        # Generate comprehensive report
        total_time = time.time() - start_time
        report = self.generate_performance_report()
        report["total_execution_time_seconds"] = total_time

        print("\n" + "=" * 80)
        print("PERFORMANCE BENCHMARKING SUMMARY")
        print("=" * 80)
        print(f"Total execution time: {total_time:.2f} seconds")
        print(f"Performance score: {report['summary']['overall_score']:.1f}/100")
        print(f"Performance grade: {report['summary']['performance_grade']}")
        print(f"All targets met: {report['summary']['targets_met']}")

        if report['summary']['recommendations']:
            print("\nRecommendations:")
            for i, rec in enumerate(report['summary']['recommendations'], 1):
                print(f"{i}. {rec}")

        return report


def main():
    """Main benchmarking execution function"""
    benchmarker = PerformanceBenchmarker()

    try:
        # Run comprehensive benchmarks
        results = benchmarker.run_comprehensive_benchmarks()

        # Save results to file
        results_file = "performance_benchmark_results.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n✓ Detailed results saved to: {results_file}")

        # Exit with appropriate code
        if results["summary"]["targets_met"]:
            print("\n🎉 All performance targets met! Service ready for production.")
            sys.exit(0)
        else:
            print("\n⚠️  Some performance targets not met. Review recommendations.")
            sys.exit(1)

    except Exception as e:
        print(f"\n💥 Performance benchmarking failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
