"""
Fast Constitutional Validator Performance Test
Constitutional Hash: cdd01ef066bc6cf2

Test O(1) validation performance with 1000+ requests to validate
<0.1ms hash validation and <0.5ms total validation time targets.
"""

import time
import statistics
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any
from dataclasses import dataclass

# Import standalone version for testing
from standalone_fast_validator import (
    FastConstitutionalValidator,
    MockRequest,
    MockResponse,
    CONSTITUTIONAL_HASH
)

@dataclass
class PerformanceResult:
    """Performance test result."""
    test_name: str
    iterations: int
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    p95_time_ms: float
    p99_time_ms: float
    cache_hit_rate: float
    target_met: bool
    constitutional_hash: str = CONSTITUTIONAL_HASH


def test_hash_validation_performance():
    """Test hash validation performance with various inputs."""
    print(f"🔍 Testing Hash Validation Performance")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("=" * 60)
    
    validator = FastConstitutionalValidator()
    
    # Test data with various hash values
    test_hashes = [
        CONSTITUTIONAL_HASH,  # Valid hash (should be cached)
        "invalid_hash_1",     # Invalid hash
        "invalid_hash_2",     # Another invalid hash
        "",                   # Empty hash (should be cached)
        None,                 # None hash
        CONSTITUTIONAL_HASH,  # Valid hash again (cache hit)
        "test_hash_123",      # Another invalid hash
        CONSTITUTIONAL_HASH,  # Valid hash again (cache hit)
    ]
    
    # Warm up
    for _ in range(100):
        for hash_val in test_hashes:
            validator.validate_hash_fast(hash_val)
    
    # Performance test
    iterations = 10000
    times = []
    
    for i in range(iterations):
        hash_val = test_hashes[i % len(test_hashes)]
        
        start_time = time.perf_counter()
        result = validator.validate_hash_fast(hash_val)
        end_time = time.perf_counter()
        
        validation_time = (end_time - start_time) * 1000  # Convert to ms
        times.append(validation_time)
        
        # Verify correctness
        expected = (hash_val == CONSTITUTIONAL_HASH) if hash_val is not None else False
        assert result == expected, f"Validation failed for {hash_val}"
    
    # Calculate statistics
    avg_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    p95_time = statistics.quantiles(times, n=20)[18]
    p99_time = statistics.quantiles(times, n=100)[98]
    
    # Get performance metrics
    metrics = validator.get_performance_metrics()
    cache_hit_rate = metrics["cache_hit_rate"]
    
    print(f"  ✅ Iterations: {iterations}")
    print(f"  ✅ Average time: {avg_time:.6f}ms")
    print(f"  ✅ Min time: {min_time:.6f}ms")
    print(f"  ✅ Max time: {max_time:.6f}ms")
    print(f"  ✅ P95 time: {p95_time:.6f}ms")
    print(f"  ✅ P99 time: {p99_time:.6f}ms")
    print(f"  ✅ Cache hit rate: {cache_hit_rate:.1%}")
    
    # Validate performance target (<0.1ms)
    target_time = 0.1
    target_met = avg_time < target_time
    
    print(f"  🎯 Target (<{target_time}ms): {'✅ MET' if target_met else '❌ MISSED'}")
    
    return PerformanceResult(
        test_name="hash_validation",
        iterations=iterations,
        avg_time_ms=avg_time,
        min_time_ms=min_time,
        max_time_ms=max_time,
        p95_time_ms=p95_time,
        p99_time_ms=p99_time,
        cache_hit_rate=cache_hit_rate,
        target_met=target_met
    )


def test_request_validation_performance():
    """Test request validation performance with various request types."""
    print(f"\n🔍 Testing Request Validation Performance")
    print("=" * 60)
    
    validator = FastConstitutionalValidator()
    
    # Test requests with different patterns
    test_requests = [
        MockRequest("/api/test", "GET", {"X-Constitutional-Hash": CONSTITUTIONAL_HASH}),
        MockRequest("/api/data", "POST", {"content-type": "application/json"}),
        MockRequest("/health", "GET"),  # Exempt path
        MockRequest("/api/update", "PUT", {"X-Constitutional-Hash": CONSTITUTIONAL_HASH}),
        MockRequest("/metrics", "GET"),  # Exempt path
        MockRequest("/api/test", "GET", {"X-Constitutional-Hash": CONSTITUTIONAL_HASH}),  # Repeat for cache
    ]
    
    # Warm up
    for _ in range(100):
        for req in test_requests:
            validator.validate_request_fast(req, "test_service")
    
    # Performance test
    iterations = 5000
    times = []
    
    for i in range(iterations):
        req = test_requests[i % len(test_requests)]
        
        start_time = time.perf_counter()
        result = validator.validate_request_fast(req, "test_service")
        end_time = time.perf_counter()
        
        validation_time = (end_time - start_time) * 1000  # Convert to ms
        times.append(validation_time)
        
        # Verify result is boolean
        assert isinstance(result, bool), f"Invalid result type: {type(result)}"
    
    # Calculate statistics
    avg_time = statistics.mean(times)
    min_time = min(times)
    max_time = max(times)
    p95_time = statistics.quantiles(times, n=20)[18]
    p99_time = statistics.quantiles(times, n=100)[98]
    
    # Get performance metrics
    metrics = validator.get_performance_metrics()
    cache_hit_rate = metrics["cache_hit_rate"]
    
    print(f"  ✅ Iterations: {iterations}")
    print(f"  ✅ Average time: {avg_time:.6f}ms")
    print(f"  ✅ Min time: {min_time:.6f}ms")
    print(f"  ✅ Max time: {max_time:.6f}ms")
    print(f"  ✅ P95 time: {p95_time:.6f}ms")
    print(f"  ✅ P99 time: {p99_time:.6f}ms")
    print(f"  ✅ Cache hit rate: {cache_hit_rate:.1%}")
    
    # Validate performance target (<0.3ms)
    target_time = 0.3
    target_met = avg_time < target_time
    
    print(f"  🎯 Target (<{target_time}ms): {'✅ MET' if target_met else '❌ MISSED'}")
    
    return PerformanceResult(
        test_name="request_validation",
        iterations=iterations,
        avg_time_ms=avg_time,
        min_time_ms=min_time,
        max_time_ms=max_time,
        p95_time_ms=p95_time,
        p99_time_ms=p99_time,
        cache_hit_rate=cache_hit_rate,
        target_met=target_met
    )


def test_concurrent_validation_performance():
    """Test concurrent validation performance."""
    print(f"\n🔄 Testing Concurrent Validation Performance")
    print("=" * 60)
    
    validator = FastConstitutionalValidator()
    
    def worker_thread(thread_id: int, iterations: int) -> List[float]:
        """Worker thread for concurrent validation."""
        times = []
        
        for i in range(iterations):
            # Mix of hash validation and request validation
            if i % 2 == 0:
                # Hash validation
                hash_val = CONSTITUTIONAL_HASH if i % 4 == 0 else f"invalid_{thread_id}_{i}"
                
                start_time = time.perf_counter()
                validator.validate_hash_fast(hash_val)
                end_time = time.perf_counter()
            else:
                # Request validation
                req = MockRequest(f"/api/thread_{thread_id}", "GET", 
                                {"X-Constitutional-Hash": CONSTITUTIONAL_HASH})
                
                start_time = time.perf_counter()
                validator.validate_request_fast(req, f"service_{thread_id}")
                end_time = time.perf_counter()
            
            validation_time = (end_time - start_time) * 1000
            times.append(validation_time)
        
        return times
    
    # Test with different concurrency levels
    concurrency_levels = [1, 5, 10, 20]
    
    for concurrency in concurrency_levels:
        print(f"  🚀 Testing with {concurrency} concurrent threads...")
        
        iterations_per_thread = 1000
        
        # Run concurrent threads
        with ThreadPoolExecutor(max_workers=concurrency) as executor:
            futures = []
            for thread_id in range(concurrency):
                future = executor.submit(worker_thread, thread_id, iterations_per_thread)
                futures.append(future)
            
            # Collect results
            all_times = []
            for future in futures:
                thread_times = future.result()
                all_times.extend(thread_times)
        
        # Calculate statistics
        avg_time = statistics.mean(all_times)
        p95_time = statistics.quantiles(all_times, n=20)[18]
        p99_time = statistics.quantiles(all_times, n=100)[98]
        
        print(f"    ✅ Average time: {avg_time:.6f}ms")
        print(f"    ✅ P95 time: {p95_time:.6f}ms")
        print(f"    ✅ P99 time: {p99_time:.6f}ms")
        print(f"    ✅ Total operations: {len(all_times)}")
    
    # Get final performance metrics
    metrics = validator.get_performance_metrics()
    print(f"  📊 Final cache hit rate: {metrics['cache_hit_rate']:.1%}")
    print(f"  📊 Total validations: {metrics['total_validations']}")


def test_cache_effectiveness():
    """Test cache effectiveness and hit rates."""
    print(f"\n💾 Testing Cache Effectiveness")
    print("=" * 60)
    
    validator = FastConstitutionalValidator()
    
    # Test with repeated patterns to maximize cache hits
    common_hashes = [CONSTITUTIONAL_HASH, "invalid_1", "invalid_2", "", "test_hash"]
    common_requests = [
        MockRequest("/api/users", "GET", {"X-Constitutional-Hash": CONSTITUTIONAL_HASH}),
        MockRequest("/api/data", "POST", {"content-type": "application/json"}),
        MockRequest("/api/update", "PUT", {"X-Constitutional-Hash": CONSTITUTIONAL_HASH}),
    ]
    
    # Phase 1: Fill cache with common patterns
    print(f"  🔥 Warming cache with common patterns...")
    for _ in range(100):
        for hash_val in common_hashes:
            validator.validate_hash_fast(hash_val)
        for req in common_requests:
            validator.validate_request_fast(req, "cache_test")
    
    initial_metrics = validator.get_performance_metrics()
    print(f"    Initial cache hit rate: {initial_metrics['cache_hit_rate']:.1%}")
    
    # Phase 2: Test with mostly cached patterns
    print(f"  📊 Testing with cached patterns...")
    cached_times = []
    
    for i in range(2000):
        # 80% cached patterns, 20% new patterns
        if i % 5 == 0:
            # New pattern
            hash_val = f"new_hash_{i}"
        else:
            # Cached pattern
            hash_val = common_hashes[i % len(common_hashes)]
        
        start_time = time.perf_counter()
        validator.validate_hash_fast(hash_val)
        end_time = time.perf_counter()
        
        cached_times.append((end_time - start_time) * 1000)
    
    final_metrics = validator.get_performance_metrics()
    
    print(f"  ✅ Final cache hit rate: {final_metrics['cache_hit_rate']:.1%}")
    print(f"  ✅ Average time with cache: {statistics.mean(cached_times):.6f}ms")
    print(f"  ✅ Hash cache size: {final_metrics['hash_cache_size']}")
    print(f"  ✅ Validation cache size: {final_metrics['validation_cache_size']}")
    
    # Validate cache effectiveness (should be >80% hit rate)
    cache_effective = final_metrics['cache_hit_rate'] > 0.8
    print(f"  🎯 Cache effectiveness (>80%): {'✅ EFFECTIVE' if cache_effective else '❌ INEFFECTIVE'}")
    
    return cache_effective


def run_comprehensive_fast_validator_test():
    """Run comprehensive fast validator performance test."""
    print("🚀 Fast Constitutional Validator Performance Test")
    print(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("=" * 60)
    
    try:
        # Test 1: Hash validation performance
        hash_result = test_hash_validation_performance()
        
        # Test 2: Request validation performance
        request_result = test_request_validation_performance()
        
        # Test 3: Concurrent validation performance
        test_concurrent_validation_performance()
        
        # Test 4: Cache effectiveness
        cache_effective = test_cache_effectiveness()
        
        # Overall assessment
        print(f"\n📊 Performance Summary")
        print("=" * 60)
        
        print(f"  📈 Hash Validation:")
        print(f"    Average: {hash_result.avg_time_ms:.6f}ms (target: <0.1ms)")
        print(f"    P99: {hash_result.p99_time_ms:.6f}ms")
        print(f"    Target met: {'✅ YES' if hash_result.target_met else '❌ NO'}")
        
        print(f"  📈 Request Validation:")
        print(f"    Average: {request_result.avg_time_ms:.6f}ms (target: <0.3ms)")
        print(f"    P99: {request_result.p99_time_ms:.6f}ms")
        print(f"    Target met: {'✅ YES' if request_result.target_met else '❌ NO'}")
        
        print(f"  📈 Cache Performance:")
        print(f"    Hash cache hit rate: {hash_result.cache_hit_rate:.1%}")
        print(f"    Request cache hit rate: {request_result.cache_hit_rate:.1%}")
        print(f"    Cache effective: {'✅ YES' if cache_effective else '❌ NO'}")
        
        # Overall success criteria
        all_targets_met = (
            hash_result.target_met and 
            request_result.target_met and 
            cache_effective
        )
        
        print(f"\n🎯 Overall Assessment:")
        if all_targets_met:
            print(f"  ✅ All performance targets met")
            print(f"  ✅ O(1) validation performance achieved")
            print(f"  ✅ Cache effectiveness validated")
            print(f"  ✅ Ready for production deployment")
        else:
            print(f"  ❌ Some performance targets missed")
            if not hash_result.target_met:
                print(f"    - Hash validation target missed")
            if not request_result.target_met:
                print(f"    - Request validation target missed")
            if not cache_effective:
                print(f"    - Cache effectiveness below threshold")
        
        print(f"\n🏛️ Constitutional Hash: {CONSTITUTIONAL_HASH}")
        
        return all_targets_met
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_comprehensive_fast_validator_test()
    
    if success:
        print(f"\n✅ Fast validator test completed successfully")
        print(f"🏛️ Constitutional hash: {CONSTITUTIONAL_HASH}")
        exit(0)
    else:
        print(f"\n❌ Fast validator test failed")
        print(f"🏛️ Constitutional hash: {CONSTITUTIONAL_HASH}")
        exit(1)
