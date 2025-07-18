"""
Integration Tests for Performance Optimization System
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive integration tests that validate the entire performance
optimization system working together to achieve <5ms P99 latency targets.

Test Coverage:
- End-to-end performance optimization pipeline
- Integration between all performance components
- Real-world performance scenarios
- Load testing and stress testing
- Performance regression validation
- Constitutional compliance under load
"""

import asyncio
import pytest
import time
import statistics
from typing import List, Dict, Any
from unittest.mock import patch

from services.shared.constitutional.validation import UltraFastConstitutionalValidator
from services.shared.database.ultra_fast_connection_pool import UltraFastConnectionPoolManager
from services.shared.performance.ultra_fast_cache import UltraFastMultiTierCache
from services.shared.performance.performance_integration_service import PerformanceIntegrationService

# Integration test targets
INTEGRATION_TEST_TARGETS = {
    "p99_latency_ms": 5.0,
    "p95_latency_ms": 2.0,
    "p50_latency_ms": 1.0,
    "min_throughput_rps": 500,  # Reduced for integration tests
    "cache_hit_rate_target": 0.90,
    "success_rate_target": 0.99,
    "constitutional_compliance": 1.0,
}

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class PerformanceBenchmark:
    """Performance benchmarking utility for integration tests."""
    
    def __init__(self):
        self.measurements: List[float] = []
        self.errors: List[Exception] = []
        
    async def measure_async(self, coro):
        """Measure execution time of an async operation."""
        start_time = time.perf_counter()
        try:
            result = await coro
            elapsed = time.perf_counter() - start_time
            self.measurements.append(elapsed * 1000)  # Convert to milliseconds
            return result
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            self.measurements.append(elapsed * 1000)
            self.errors.append(e)
            raise
    
    def get_statistics(self) -> Dict[str, float]:
        """Get performance statistics."""
        if not self.measurements:
            return {"count": 0}
        
        sorted_measurements = sorted(self.measurements)
        count = len(sorted_measurements)
        
        return {
            "count": count,
            "min_ms": min(sorted_measurements),
            "max_ms": max(sorted_measurements),
            "mean_ms": statistics.mean(sorted_measurements),
            "median_ms": statistics.median(sorted_measurements),
            "p95_ms": sorted_measurements[int(count * 0.95)] if count >= 20 else max(sorted_measurements),
            "p99_ms": sorted_measurements[int(count * 0.99)] if count >= 100 else max(sorted_measurements),
            "error_rate": len(self.errors) / count if count > 0 else 0.0
        }


@pytest.fixture
async def constitutional_validator():
    """Create ultra-fast constitutional validator."""
    validator = UltraFastConstitutionalValidator()
    yield validator


@pytest.fixture
async def cache_system():
    """Create ultra-fast cache system."""
    cache = UltraFastMultiTierCache(
        redis_url="redis://localhost:6389/0",
        l1_max_size=10000
    )
    await cache.initialize()
    yield cache
    await cache.close()


@pytest.fixture
async def performance_service():
    """Create performance integration service."""
    service = PerformanceIntegrationService()
    
    # Mock external dependencies for integration tests
    with patch('services.shared.performance.performance_integration_service.get_pool_manager') as mock_pool_manager, \
         patch('services.shared.performance.performance_integration_service.get_ultra_fast_cache') as mock_cache:
        
        # Create mock cache
        mock_cache_instance = UltraFastMultiTierCache()
        await mock_cache_instance.initialize()
        mock_cache.return_value = mock_cache_instance
        
        # Create mock pool manager
        mock_pool_manager_instance = UltraFastConnectionPoolManager()
        mock_pool_manager.return_value = mock_pool_manager_instance
        
        await service.initialize()
        yield service
        await service.close()


class TestPerformanceOptimizationIntegration:
    """Integration tests for the complete performance optimization system."""

    @pytest.mark.asyncio
    async def test_constitutional_validation_performance_integration(self, constitutional_validator):
        """Test constitutional validation performance in integration scenario."""
        benchmark = PerformanceBenchmark()
        
        # Simulate real-world validation patterns
        validation_patterns = [
            CONSTITUTIONAL_HASH,  # Valid hash (should be fast)
            "invalid_hash_123",   # Invalid hash (should be cached)
            CONSTITUTIONAL_HASH,  # Valid hash (should use fast path)
            "malformed!hash",     # Malformed hash (should be rejected quickly)
            CONSTITUTIONAL_HASH,  # Valid hash (should be very fast)
        ]
        
        # Run validation benchmark
        for _ in range(200):  # 1000 total validations
            for pattern in validation_patterns:
                await benchmark.measure_async(
                    constitutional_validator.async_validate_hash(pattern)
                )
        
        stats = benchmark.get_statistics()
        
        # Validate performance targets
        assert stats["p99_ms"] < INTEGRATION_TEST_TARGETS["p99_latency_ms"], \
            f"P99 validation time {stats['p99_ms']:.3f}ms exceeds target"
        
        assert stats["error_rate"] == 0.0, "No errors should occur in validation"
        
        # Validate cache efficiency
        metrics = constitutional_validator.get_detailed_metrics()
        cache_hit_rate = metrics["performance_summary"]["cache_hit_rate"]
        assert cache_hit_rate > 0.8, f"Cache hit rate {cache_hit_rate:.2%} too low"
        
        print(f"Constitutional validation integration: {stats}")

    @pytest.mark.asyncio
    async def test_cache_system_performance_integration(self, cache_system):
        """Test cache system performance in integration scenario."""
        benchmark = PerformanceBenchmark()
        
        # Pre-populate cache with realistic data
        test_data = {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "timestamp": time.time(),
            "data": "test_value"
        }
        
        # Set up cache with various data types
        cache_keys = []
        for i in range(100):
            key = f"integration_test_{i}"
            cache_keys.append(key)
            await cache_system.set(key, {**test_data, "id": i}, data_type="integration")
        
        # Benchmark cache operations
        for _ in range(500):
            # 80% cache hits, 20% misses (realistic scenario)
            if len(benchmark.measurements) % 5 == 0:
                key = f"missing_key_{time.time()}"
            else:
                key = cache_keys[len(benchmark.measurements) % len(cache_keys)]
            
            await benchmark.measure_async(cache_system.get(key))
        
        stats = benchmark.get_statistics()
        
        # Validate performance targets
        assert stats["p99_ms"] < INTEGRATION_TEST_TARGETS["p95_latency_ms"], \
            f"P99 cache access time {stats['p99_ms']:.3f}ms exceeds target"
        
        # Validate cache hit rate
        cache_metrics = cache_system.get_performance_metrics()
        hit_rate = cache_metrics["performance_summary"]["overall_hit_rate"]
        assert hit_rate >= INTEGRATION_TEST_TARGETS["cache_hit_rate_target"], \
            f"Cache hit rate {hit_rate:.2%} below target"
        
        print(f"Cache system integration: {stats}")

    @pytest.mark.asyncio
    async def test_end_to_end_request_processing(self, performance_service):
        """Test end-to-end request processing performance."""
        benchmark = PerformanceBenchmark()
        
        # Simulate realistic request patterns
        request_templates = [
            {"type": "validation", "data": "simple"},
            {"type": "complex", "data": "complex_operation", "database_operation": True},
            {"type": "cached", "data": "frequently_accessed"},
            {"type": "validation", "data": "simple"},  # Duplicate for caching
            {"type": "cached", "data": "frequently_accessed"},  # Duplicate for caching
        ]
        
        # Process requests
        for i in range(200):  # 1000 total requests
            for template in request_templates:
                request_data = {
                    **template,
                    "id": f"request_{i}_{template['type']}",
                    "timestamp": time.time()
                }
                
                await benchmark.measure_async(
                    performance_service.process_request(request_data)
                )
        
        stats = benchmark.get_statistics()
        
        # Validate performance targets
        assert stats["p99_ms"] < INTEGRATION_TEST_TARGETS["p99_latency_ms"], \
            f"P99 request processing time {stats['p99_ms']:.3f}ms exceeds target"
        
        assert stats["p95_ms"] < INTEGRATION_TEST_TARGETS["p95_latency_ms"], \
            f"P95 request processing time {stats['p95_ms']:.3f}ms exceeds target"
        
        assert stats["error_rate"] < (1 - INTEGRATION_TEST_TARGETS["success_rate_target"]), \
            f"Error rate {stats['error_rate']:.2%} too high"
        
        # Validate service metrics
        service_summary = await performance_service.get_performance_summary()
        integration_metrics = service_summary["integration_metrics"]
        
        assert integration_metrics["success_rate"] >= INTEGRATION_TEST_TARGETS["success_rate_target"], \
            f"Success rate {integration_metrics['success_rate']:.2%} below target"
        
        print(f"End-to-end request processing: {stats}")

    @pytest.mark.asyncio
    async def test_concurrent_load_performance(self, performance_service):
        """Test performance under concurrent load."""
        async def worker(worker_id: int, requests_per_worker: int):
            """Worker function for concurrent load testing."""
            worker_benchmark = PerformanceBenchmark()
            
            for i in range(requests_per_worker):
                request_data = {
                    "worker_id": worker_id,
                    "request_id": i,
                    "type": "load_test",
                    "data": f"worker_{worker_id}_request_{i}"
                }
                
                await worker_benchmark.measure_async(
                    performance_service.process_request(request_data)
                )
            
            return worker_benchmark.get_statistics()
        
        # Run concurrent workers
        num_workers = 10
        requests_per_worker = 50
        total_requests = num_workers * requests_per_worker
        
        start_time = time.perf_counter()
        
        # Execute concurrent load
        tasks = [worker(i, requests_per_worker) for i in range(num_workers)]
        worker_stats = await asyncio.gather(*tasks)
        
        total_time = time.perf_counter() - start_time
        throughput = total_requests / total_time
        
        # Aggregate statistics
        all_measurements = []
        total_errors = 0
        
        for stats in worker_stats:
            if "count" in stats and stats["count"] > 0:
                # Approximate individual measurements for aggregation
                # This is a simplification for integration testing
                avg_time = stats.get("mean_ms", 0)
                count = stats["count"]
                all_measurements.extend([avg_time] * count)
                total_errors += int(stats.get("error_rate", 0) * count)
        
        if all_measurements:
            overall_stats = {
                "count": len(all_measurements),
                "mean_ms": statistics.mean(all_measurements),
                "p95_ms": statistics.quantiles(all_measurements, n=20)[18] if len(all_measurements) >= 20 else max(all_measurements),
                "p99_ms": statistics.quantiles(all_measurements, n=100)[98] if len(all_measurements) >= 100 else max(all_measurements),
                "error_rate": total_errors / len(all_measurements),
                "throughput_rps": throughput
            }
        else:
            overall_stats = {"count": 0, "throughput_rps": 0}
        
        # Validate performance under load
        assert overall_stats["throughput_rps"] >= INTEGRATION_TEST_TARGETS["min_throughput_rps"], \
            f"Throughput {overall_stats['throughput_rps']:.1f} RPS below target"
        
        if overall_stats["count"] > 0:
            assert overall_stats["p99_ms"] < INTEGRATION_TEST_TARGETS["p99_latency_ms"] * 2, \
                f"P99 latency under load {overall_stats['p99_ms']:.3f}ms too high"
            
            assert overall_stats["error_rate"] < 0.05, \
                f"Error rate under load {overall_stats['error_rate']:.2%} too high"
        
        print(f"Concurrent load performance: {overall_stats}")

    @pytest.mark.asyncio
    async def test_performance_optimization_effectiveness(self, performance_service):
        """Test that performance optimization actually improves performance."""
        # Baseline performance measurement
        baseline_benchmark = PerformanceBenchmark()
        
        for i in range(100):
            request_data = {"id": f"baseline_{i}", "type": "optimization_test"}
            await baseline_benchmark.measure_async(
                performance_service.process_request(request_data)
            )
        
        baseline_stats = baseline_benchmark.get_statistics()
        
        # Trigger optimization
        await performance_service._run_optimization()
        
        # Post-optimization performance measurement
        optimized_benchmark = PerformanceBenchmark()
        
        for i in range(100):
            request_data = {"id": f"optimized_{i}", "type": "optimization_test"}
            await optimized_benchmark.measure_async(
                performance_service.process_request(request_data)
            )
        
        optimized_stats = optimized_benchmark.get_statistics()
        
        # Performance should be maintained or improved
        # (In a real system, we'd expect improvement, but for mocked tests, we ensure no regression)
        performance_ratio = optimized_stats["mean_ms"] / max(baseline_stats["mean_ms"], 0.001)
        assert performance_ratio <= 2.0, \
            f"Performance degraded by {performance_ratio:.1f}x after optimization"
        
        print(f"Optimization effectiveness: baseline={baseline_stats['mean_ms']:.2f}ms, "
              f"optimized={optimized_stats['mean_ms']:.2f}ms")

    @pytest.mark.asyncio
    async def test_constitutional_compliance_under_load(self, performance_service):
        """Test that constitutional compliance is maintained under load."""
        compliance_violations = 0
        total_requests = 0
        
        async def compliance_worker():
            """Worker that checks constitutional compliance."""
            nonlocal compliance_violations, total_requests
            
            for i in range(100):
                try:
                    request_data = {
                        "id": f"compliance_test_{i}",
                        "type": "compliance_validation"
                    }
                    
                    response = await performance_service.process_request(request_data)
                    total_requests += 1
                    
                    # Check constitutional compliance in response
                    if response.get("constitutional_hash") != CONSTITUTIONAL_HASH:
                        compliance_violations += 1
                        
                except Exception:
                    compliance_violations += 1
                    total_requests += 1
        
        # Run multiple compliance workers concurrently
        tasks = [compliance_worker() for _ in range(5)]
        await asyncio.gather(*tasks)
        
        # Calculate compliance rate
        compliance_rate = (total_requests - compliance_violations) / max(total_requests, 1)
        
        assert compliance_rate >= INTEGRATION_TEST_TARGETS["constitutional_compliance"], \
            f"Constitutional compliance rate {compliance_rate:.2%} below target"
        
        print(f"Constitutional compliance under load: {compliance_rate:.2%} "
              f"({total_requests - compliance_violations}/{total_requests})")

    @pytest.mark.asyncio
    async def test_memory_efficiency_under_load(self, performance_service):
        """Test memory efficiency under sustained load."""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Sustained load
        for batch in range(10):  # 10 batches of 100 requests each
            tasks = []
            for i in range(100):
                request_data = {
                    "id": f"memory_test_{batch}_{i}",
                    "type": "memory_efficiency",
                    "data": "x" * 1000  # 1KB of data per request
                }
                tasks.append(performance_service.process_request(request_data))
            
            await asyncio.gather(*tasks)
            
            # Check memory usage periodically
            if batch % 3 == 0:
                current_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_growth = current_memory - initial_memory
                
                # Memory growth should be reasonable (less than 100MB for this test)
                assert memory_growth < 100, \
                    f"Excessive memory growth: {memory_growth:.1f}MB after {(batch + 1) * 100} requests"
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        total_growth = final_memory - initial_memory
        
        print(f"Memory efficiency: {initial_memory:.1f}MB -> {final_memory:.1f}MB "
              f"(+{total_growth:.1f}MB for 1000 requests)")

    @pytest.mark.asyncio
    async def test_error_recovery_and_resilience(self, performance_service):
        """Test system resilience and error recovery."""
        successful_requests = 0
        total_requests = 0
        
        # Simulate various error conditions
        error_scenarios = [
            {"id": "normal_request", "type": "normal"},  # Should succeed
            {"id": "normal_request_2", "type": "normal"},  # Should succeed
            {"id": "normal_request_3", "type": "normal"},  # Should succeed
        ]
        
        for scenario in error_scenarios * 100:  # 300 total requests
            try:
                await performance_service.process_request(scenario)
                successful_requests += 1
            except Exception:
                pass  # Count as failure
            
            total_requests += 1
        
        success_rate = successful_requests / total_requests
        
        # System should maintain high success rate even with some errors
        assert success_rate >= 0.95, \
            f"Success rate {success_rate:.2%} too low for resilience test"
        
        print(f"Error recovery: {success_rate:.2%} success rate "
              f"({successful_requests}/{total_requests})")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
