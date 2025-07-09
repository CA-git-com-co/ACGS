#!/usr/bin/env python3
"""
Test constitutional middleware performance metrics integration.
Constitutional Hash: cdd01ef066bc6cf2

Validates that performance metrics are properly collected and reported.
"""

import asyncio
import sys
import time
from unittest.mock import MagicMock

# Add project root to path
sys.path.insert(0, '/home/dislove/ACGS-2')

from services.shared.middleware.constitutional_performance_metrics import (
    ConstitutionalPerformanceCollector,
    ConstitutionalPerformanceTracker,
    get_performance_collector,
    CONSTITUTIONAL_HASH,
)

def test_performance_collector():
    """Test basic performance collector functionality."""
    print("HASH-OK:cdd01ef066bc6cf2")
    print("Testing Constitutional Performance Collector")
    print("=" * 50)
    
    # Create collector
    collector = ConstitutionalPerformanceCollector("test-service")
    
    # Test validation time recording
    print("1. Testing validation time recording...")
    for i in range(10):
        validation_time = 0.1 + (i * 0.05)  # 0.1ms to 0.55ms
        collector.record_validation_time(validation_time, "header", "success")
    
    # Test cache metrics
    print("2. Testing cache metrics...")
    for i in range(20):
        if i % 3 == 0:  # 33% miss rate
            collector.record_cache_miss("hash")
        else:
            collector.record_cache_hit("hash")
    
    # Test compliance recording
    print("3. Testing compliance recording...")
    for i in range(15):
        collector.record_compliance_result(i % 10 != 0)  # 90% compliance
    
    # Get performance summary
    summary = collector.get_performance_summary()
    
    print("4. Performance Summary:")
    print(f"   Service: {summary['service']}")
    print(f"   Constitutional Hash: {summary['constitutional_hash']}")
    print(f"   Average validation time: {summary['performance']['average_validation_time_ms']:.3f}ms")
    print(f"   P95 validation time: {summary['performance']['p95_validation_time_ms']:.3f}ms")
    print(f"   P99 validation time: {summary['performance']['p99_validation_time_ms']:.3f}ms")
    print(f"   Target met: {summary['performance']['target_met']}")
    print(f"   Cache hit rate: {summary['cache']['hit_rate_percent']:.1f}%")
    print(f"   Compliance rate: {summary['compliance']['rate_percent']:.1f}%")
    
    # Validate results
    assert summary['constitutional_hash'] == CONSTITUTIONAL_HASH
    assert summary['performance']['average_validation_time_ms'] > 0
    assert summary['cache']['hit_rate_percent'] > 60  # Should be ~67%
    assert summary['compliance']['rate_percent'] > 85  # Should be ~90%
    
    print("✅ Performance collector test passed")
    return True


def test_performance_tracker():
    """Test performance tracker context manager."""
    print("\n5. Testing Performance Tracker...")
    
    # Test successful validation
    with ConstitutionalPerformanceTracker(
        "test-service", "full", "/test", "POST"
    ) as tracker:
        time.sleep(0.001)  # Simulate 1ms work
        tracker.record_cache_hit("hash")
        tracker.record_compliance_result(True)
    
    # Test with error
    try:
        with ConstitutionalPerformanceTracker(
            "test-service", "header", "/error", "GET"
        ) as tracker:
            tracker.record_cache_miss("hash")
            tracker.record_compliance_result(False)
            raise ValueError("Test error")
    except ValueError:
        pass  # Expected
    
    # Get collector and check metrics
    collector = get_performance_collector("test-service")
    summary = collector.get_performance_summary()
    
    print(f"   Total validations: {summary['compliance']['total_validations']}")
    print(f"   Cache requests: {summary['cache']['total_requests']}")
    
    assert summary['compliance']['total_validations'] > 0
    assert summary['cache']['total_requests'] > 0
    
    print("✅ Performance tracker test passed")
    return True


def test_metrics_integration():
    """Test metrics integration with mock FastAPI app."""
    print("\n6. Testing Metrics Integration...")
    
    # Mock FastAPI app
    class MockApp:
        def __init__(self):
            self.routes = []
        
        def get(self, path):
            def decorator(func):
                self.routes.append((path, func))
                return func
            return decorator
    
    # Import and test setup
    from services.shared.middleware.constitutional_performance_metrics import (
        setup_constitutional_metrics_endpoint
    )
    
    app = MockApp()
    setup_constitutional_metrics_endpoint(app)
    
    # Verify endpoints were added
    assert len(app.routes) == 2
    paths = [route[0] for route in app.routes]
    assert "/constitutional/metrics" in paths
    assert "/constitutional/metrics/summary" in paths
    
    print("   ✅ Metrics endpoints configured")
    
    # Test metrics endpoint function
    metrics_func = None
    summary_func = None
    for path, func in app.routes:
        if path == "/constitutional/metrics":
            metrics_func = func
        elif path == "/constitutional/metrics/summary":
            summary_func = func
    
    # Test summary endpoint
    if summary_func:
        result = asyncio.run(summary_func())
        assert "constitutional_hash" in result
        assert result["constitutional_hash"] == CONSTITUTIONAL_HASH
        assert "services" in result
        assert "system_status" in result
        print("   ✅ Summary endpoint working")
    
    print("✅ Metrics integration test passed")
    return True


def test_performance_targets():
    """Test performance target validation."""
    print("\n7. Testing Performance Targets...")
    
    collector = ConstitutionalPerformanceCollector("target-test")
    
    # Record fast validations (should meet target)
    for _ in range(100):
        collector.record_validation_time(0.1, "fast", "success")  # 0.1ms
    
    summary = collector.get_performance_summary()
    fast_target_met = summary['performance']['target_met']
    
    # Record slow validations (should not meet target)
    for _ in range(100):
        collector.record_validation_time(1.0, "slow", "success")  # 1.0ms
    
    summary = collector.get_performance_summary()
    mixed_target_met = summary['performance']['target_met']
    
    print(f"   Fast validations target met: {fast_target_met}")
    print(f"   Mixed validations target met: {mixed_target_met}")
    
    # Fast should meet target, mixed should not
    assert fast_target_met == True
    assert mixed_target_met == False
    
    print("✅ Performance targets test passed")
    return True


def main():
    """Run all performance metrics tests."""
    print("Constitutional Middleware Performance Metrics Test Suite")
    print("Constitutional Hash: cdd01ef066bc6cf2")
    print("=" * 60)
    
    tests = [
        test_performance_collector,
        test_performance_tracker,
        test_metrics_integration,
        test_performance_targets,
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{len(tests)} passed")
    
    if passed == len(tests):
        print("🎉 ALL TESTS PASSED!")
        print("✅ Performance metrics integration working correctly")
        print("✅ Constitutional compliance tracking enabled")
        print("✅ Cache hit rate monitoring active")
        print("✅ Validation time tracking operational")
        print("HASH-OK:cdd01ef066bc6cf2")
        return 0
    else:
        print("❌ Some tests failed - check implementation")
        return 1


if __name__ == "__main__":
    sys.exit(main())
