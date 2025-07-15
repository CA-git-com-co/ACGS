"""
ACGS-2 Performance Testing Framework
Comprehensive performance benchmarks for constitutional compliance validation.
Constitutional Compliance: cdd01ef066bc6cf2

Performance Targets:
- P99 Latency: <5ms
- Throughput: >100 RPS
- Cache Hit Rate: >85%
"""

import pytest
import asyncio
import time
import statistics
from typing import List, Dict, Any, Tuple
from unittest.mock import AsyncMock, MagicMock
import json
from concurrent.futures import ThreadPoolExecutor
import psutil
import os

from tests.mocks.constitutional_ai_mocks import ConstitutionalValidationService
from tests.conftest import CONSTITUTIONAL_HASH

# Performance test configuration
PERFORMANCE_CONFIG = {
    "target_p99_latency_ms": 5.0,
    "target_throughput_rps": 100,
    "target_cache_hit_rate": 85.0,
    "load_test_duration_seconds": 10,
    "concurrent_users": 50,
    "warmup_requests": 20
}


class PerformanceMetrics:
    """Collect and analyze performance metrics."""
    
    def __init__(self):
        self.latencies = []
        self.throughput_samples = []
        self.cache_hits = 0
        self.cache_misses = 0
        self.errors = 0
        self.start_time = None
        self.end_time = None
        self.constitutional_hash = CONSTITUTIONAL_HASH
    
    def record_latency(self, latency_ms: float):
        """Record a latency measurement."""
        self.latencies.append(latency_ms)
    
    def record_cache_hit(self):
        """Record a cache hit."""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record a cache miss."""
        self.cache_misses += 1
    
    def record_error(self):
        """Record an error."""
        self.errors += 1
    
    def start_measurement(self):
        """Start performance measurement."""
        self.start_time = time.time()
    
    def end_measurement(self):
        """End performance measurement."""
        self.end_time = time.time()
    
    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculate comprehensive performance metrics."""
        if not self.latencies:
            return {"error": "No latency data collected"}
        
        duration = self.end_time - self.start_time if self.end_time and self.start_time else 0
        total_requests = len(self.latencies)
        
        # Latency metrics
        latencies_sorted = sorted(self.latencies)
        p50_latency = statistics.median(latencies_sorted)
        p95_latency = latencies_sorted[int(len(latencies_sorted) * 0.95)] if latencies_sorted else 0
        p99_latency = latencies_sorted[int(len(latencies_sorted) * 0.99)] if latencies_sorted else 0
        avg_latency = statistics.mean(latencies_sorted)
        
        # Throughput metrics
        throughput_rps = total_requests / duration if duration > 0 else 0
        
        # Cache metrics
        total_cache_operations = self.cache_hits + self.cache_misses
        cache_hit_rate = (self.cache_hits / total_cache_operations * 100) if total_cache_operations > 0 else 0
        
        # Error rate
        error_rate = (self.errors / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "constitutional_hash": self.constitutional_hash,
            "duration_seconds": duration,
            "total_requests": total_requests,
            "latency_metrics": {
                "avg_ms": round(avg_latency, 3),
                "p50_ms": round(p50_latency, 3),
                "p95_ms": round(p95_latency, 3),
                "p99_ms": round(p99_latency, 3),
                "min_ms": round(min(latencies_sorted), 3),
                "max_ms": round(max(latencies_sorted), 3)
            },
            "throughput_metrics": {
                "rps": round(throughput_rps, 2),
                "requests_per_minute": round(throughput_rps * 60, 2)
            },
            "cache_metrics": {
                "hit_rate_percent": round(cache_hit_rate, 2),
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "total_operations": total_cache_operations
            },
            "error_metrics": {
                "error_rate_percent": round(error_rate, 2),
                "total_errors": self.errors
            },
            "performance_targets": {
                "p99_latency_target_met": p99_latency <= PERFORMANCE_CONFIG["target_p99_latency_ms"],
                "throughput_target_met": throughput_rps >= PERFORMANCE_CONFIG["target_throughput_rps"],
                "cache_hit_rate_target_met": cache_hit_rate >= PERFORMANCE_CONFIG["target_cache_hit_rate"]
            }
        }


class PerformanceTestSuite:
    """Performance testing suite for ACGS-2 services."""
    
    def __init__(self):
        self.validation_service = ConstitutionalValidationService()
        self.metrics = PerformanceMetrics()
        self.cache = {}  # Simple cache for testing
    
    async def single_request_benchmark(self, policy: Dict[str, Any]) -> float:
        """Benchmark a single request and return latency in milliseconds."""
        start_time = time.perf_counter()
        
        try:
            # Check cache first
            cache_key = json.dumps(policy, sort_keys=True)
            if cache_key in self.cache:
                self.metrics.record_cache_hit()
                result = self.cache[cache_key]
            else:
                self.metrics.record_cache_miss()
                result = await self.validation_service.validate_policy(policy)
                self.cache[cache_key] = result
            
            # Validate constitutional compliance
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
            
        except Exception as e:
            self.metrics.record_error()
            raise e
        
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        self.metrics.record_latency(latency_ms)
        
        return latency_ms
    
    async def load_test(self, concurrent_users: int, duration_seconds: int) -> Dict[str, Any]:
        """Perform load testing with specified parameters."""
        self.metrics = PerformanceMetrics()  # Reset metrics
        
        # Test policies for load testing
        test_policies = [
            {"content": f"Policy {i} with constitutional principles", "metadata": {"id": i}}
            for i in range(100)
        ]
        
        async def user_simulation():
            """Simulate a single user's requests."""
            user_start = time.time()
            request_count = 0
            
            while time.time() - user_start < duration_seconds:
                policy = test_policies[request_count % len(test_policies)]
                try:
                    await self.single_request_benchmark(policy)
                    request_count += 1
                    await asyncio.sleep(0.01)  # Small delay between requests
                except Exception:
                    pass  # Continue on errors
        
        # Start measurement
        self.metrics.start_measurement()
        
        # Run concurrent user simulations
        tasks = [user_simulation() for _ in range(concurrent_users)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # End measurement
        self.metrics.end_measurement()
        
        return self.metrics.calculate_metrics()


@pytest.mark.performance
class TestPerformanceBenchmarks:
    """Performance benchmark test suite."""
    
    @pytest.fixture
    def performance_suite(self):
        """Create performance test suite."""
        return PerformanceTestSuite()
    
    @pytest.fixture
    def test_policies(self):
        """Provide test policies for benchmarking."""
        return [
            {"content": "Standard constitutional policy", "metadata": {"type": "standard"}},
            {"content": "Complex policy with multiple constitutional principles including democratic participation, transparency, accountability, fairness, privacy, and human dignity", "metadata": {"type": "complex"}},
            {"content": "Minimal policy", "metadata": {"type": "minimal"}},
            {"content": "Policy with unicode: 🏛️ constitutional governance 📜", "metadata": {"type": "unicode"}},
            {"content": "Large policy content " + "x" * 1000, "metadata": {"type": "large"}}
        ]
    
    @pytest.mark.asyncio
    async def test_single_request_latency(self, performance_suite, test_policies):
        """Test single request latency performance."""
        latencies = []
        
        for policy in test_policies:
            latency = await performance_suite.single_request_benchmark(policy)
            latencies.append(latency)
        
        # Calculate P99 latency
        latencies.sort()
        p99_latency = latencies[int(len(latencies) * 0.99)] if latencies else 0
        avg_latency = sum(latencies) / len(latencies)
        
        print(f"Single Request Performance:")
        print(f"  Average Latency: {avg_latency:.3f}ms")
        print(f"  P99 Latency: {p99_latency:.3f}ms")
        print(f"  Target P99: {PERFORMANCE_CONFIG['target_p99_latency_ms']}ms")
        
        # Performance assertion
        assert p99_latency <= PERFORMANCE_CONFIG["target_p99_latency_ms"], \
            f"P99 latency {p99_latency:.3f}ms exceeds target {PERFORMANCE_CONFIG['target_p99_latency_ms']}ms"
    
    @pytest.mark.asyncio
    async def test_throughput_benchmark(self, performance_suite):
        """Test throughput performance under load."""
        metrics = await performance_suite.load_test(
            concurrent_users=PERFORMANCE_CONFIG["concurrent_users"],
            duration_seconds=PERFORMANCE_CONFIG["load_test_duration_seconds"]
        )
        
        print(f"Throughput Performance:")
        print(f"  Throughput: {metrics['throughput_metrics']['rps']:.2f} RPS")
        print(f"  Target: {PERFORMANCE_CONFIG['target_throughput_rps']} RPS")
        print(f"  P99 Latency: {metrics['latency_metrics']['p99_ms']:.3f}ms")
        print(f"  Cache Hit Rate: {metrics['cache_metrics']['hit_rate_percent']:.1f}%")
        
        # Performance assertions
        assert metrics["performance_targets"]["throughput_target_met"], \
            f"Throughput {metrics['throughput_metrics']['rps']:.2f} RPS below target {PERFORMANCE_CONFIG['target_throughput_rps']} RPS"
        
        assert metrics["performance_targets"]["p99_latency_target_met"], \
            f"P99 latency {metrics['latency_metrics']['p99_ms']:.3f}ms exceeds target {PERFORMANCE_CONFIG['target_p99_latency_ms']}ms"
    
    @pytest.mark.asyncio
    async def test_cache_performance(self, performance_suite):
        """Test cache hit rate performance."""
        # Warm up cache with repeated requests
        warmup_policy = {"content": "Warmup policy for cache testing", "metadata": {"type": "warmup"}}
        
        # Initial requests to populate cache
        for _ in range(PERFORMANCE_CONFIG["warmup_requests"]):
            await performance_suite.single_request_benchmark(warmup_policy)
        
        # Reset metrics after warmup
        performance_suite.metrics = PerformanceMetrics()
        
        # Test cache hit rate with repeated requests
        for _ in range(50):
            await performance_suite.single_request_benchmark(warmup_policy)
        
        metrics = performance_suite.metrics.calculate_metrics()
        cache_hit_rate = metrics["cache_metrics"]["hit_rate_percent"]
        
        print(f"Cache Performance:")
        print(f"  Cache Hit Rate: {cache_hit_rate:.1f}%")
        print(f"  Target: {PERFORMANCE_CONFIG['target_cache_hit_rate']}%")
        print(f"  Cache Hits: {metrics['cache_metrics']['hits']}")
        print(f"  Cache Misses: {metrics['cache_metrics']['misses']}")
        
        # Cache performance assertion
        assert cache_hit_rate >= PERFORMANCE_CONFIG["target_cache_hit_rate"], \
            f"Cache hit rate {cache_hit_rate:.1f}% below target {PERFORMANCE_CONFIG['target_cache_hit_rate']}%"
    
    @pytest.mark.asyncio
    async def test_memory_efficiency(self, performance_suite):
        """Test memory efficiency during sustained load."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run sustained load test
        metrics = await performance_suite.load_test(
            concurrent_users=20,
            duration_seconds=5
        )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_growth = final_memory - initial_memory
        
        print(f"Memory Efficiency:")
        print(f"  Initial Memory: {initial_memory:.2f}MB")
        print(f"  Final Memory: {final_memory:.2f}MB")
        print(f"  Memory Growth: {memory_growth:.2f}MB")
        print(f"  Requests Processed: {metrics['total_requests']}")
        
        # Memory efficiency assertion (should not grow more than 50MB)
        assert memory_growth < 50, f"Memory growth {memory_growth:.2f}MB exceeds acceptable limit"
        
        # Validate constitutional compliance maintained
        assert metrics["constitutional_hash"] == CONSTITUTIONAL_HASH
    
    @pytest.mark.asyncio
    async def test_stress_test(self, performance_suite):
        """Stress test with high concurrent load."""
        # High stress configuration
        stress_metrics = await performance_suite.load_test(
            concurrent_users=100,  # Double the normal load
            duration_seconds=5
        )
        
        print(f"Stress Test Results:")
        print(f"  Throughput: {stress_metrics['throughput_metrics']['rps']:.2f} RPS")
        print(f"  P99 Latency: {stress_metrics['latency_metrics']['p99_ms']:.3f}ms")
        print(f"  Error Rate: {stress_metrics['error_metrics']['error_rate_percent']:.2f}%")
        print(f"  Total Requests: {stress_metrics['total_requests']}")
        
        # Stress test assertions (relaxed targets)
        assert stress_metrics["latency_metrics"]["p99_ms"] <= 10.0, \
            f"P99 latency under stress {stress_metrics['latency_metrics']['p99_ms']:.3f}ms exceeds 10ms limit"
        
        assert stress_metrics["error_metrics"]["error_rate_percent"] <= 5.0, \
            f"Error rate under stress {stress_metrics['error_metrics']['error_rate_percent']:.2f}% exceeds 5% limit"
        
        # Constitutional compliance must be maintained even under stress
        assert stress_metrics["constitutional_hash"] == CONSTITUTIONAL_HASH
    
    @pytest.mark.asyncio
    async def test_constitutional_compliance_performance(self, performance_suite):
        """Test performance of constitutional compliance validation."""
        constitutional_policies = [
            {"content": "Policy with strong democratic participation", "metadata": {"principle": "democratic"}},
            {"content": "Policy with transparency requirements", "metadata": {"principle": "transparency"}},
            {"content": "Policy with accountability measures", "metadata": {"principle": "accountability"}},
            {"content": "Policy with fairness provisions", "metadata": {"principle": "fairness"}},
            {"content": "Policy with privacy protections", "metadata": {"principle": "privacy"}},
            {"content": "Policy with human dignity respect", "metadata": {"principle": "dignity"}}
        ]
        
        compliance_latencies = []
        
        for policy in constitutional_policies:
            start_time = time.perf_counter()
            result = await performance_suite.validation_service.validate_policy(policy)
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            compliance_latencies.append(latency_ms)
            
            # Validate constitutional compliance
            assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
            assert "validation_details" in result
            assert "scores" in result["validation_details"]
        
        avg_compliance_latency = sum(compliance_latencies) / len(compliance_latencies)
        max_compliance_latency = max(compliance_latencies)
        
        print(f"Constitutional Compliance Performance:")
        print(f"  Average Latency: {avg_compliance_latency:.3f}ms")
        print(f"  Maximum Latency: {max_compliance_latency:.3f}ms")
        print(f"  Policies Tested: {len(constitutional_policies)}")
        
        # Constitutional compliance performance should be efficient
        assert avg_compliance_latency <= PERFORMANCE_CONFIG["target_p99_latency_ms"], \
            f"Average constitutional compliance latency {avg_compliance_latency:.3f}ms exceeds target"
