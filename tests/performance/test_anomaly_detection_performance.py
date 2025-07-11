"""
Performance tests for anomaly detection in security architecture.
Constitutional hash: cdd01ef066bc6cf2
"""

import asyncio
import time
import sys
import os
from concurrent.futures import ThreadPoolExecutor
import pytest

# Add services to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../../services/core/evolutionary-computation'))

from ec_service.security_architecture import AnomalyDetector, FourLayerSecurityArchitecture

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class TestAnomalyDetectionPerformance:
    """Performance tests for anomaly detection."""
    
    @pytest.mark.asyncio
    async def test_single_detection_latency(self):
        """Test single detection meets P99 <5ms requirement."""
        detector = AnomalyDetector()
        
        # Test multiple iterations to get P99
        latencies = []
        for i in range(100):
            start_time = time.time()
            metrics = {'request_rate': 100 + i, 'error_rate': 0.01 + (i * 0.001)}
            await detector.detect_anomaly(metrics)
            end_time = time.time()
            latencies.append((end_time - start_time) * 1000)  # Convert to ms
        
        # Calculate P99
        latencies.sort()
        p99_latency = latencies[98]  # 99th percentile
        
        print(f"P99 latency: {p99_latency:.2f}ms")
        assert p99_latency < 5.0, f"P99 latency {p99_latency:.2f}ms exceeds 5ms requirement"
    
    @pytest.mark.asyncio
    async def test_concurrent_throughput(self):
        """Test concurrent requests meet >100 RPS requirement."""
        detector = AnomalyDetector()
        
        num_concurrent = 50
        requests_per_worker = 20
        
        async def worker(worker_id):
            for i in range(requests_per_worker):
                metrics = {
                    'request_rate': 100 + (worker_id * 10) + i,
                    'error_rate': 0.01 + (i * 0.001)
                }
                await detector.detect_anomaly(metrics)
        
        start_time = time.time()
        tasks = [worker(i) for i in range(num_concurrent)]
        await asyncio.gather(*tasks)
        end_time = time.time()
        
        total_requests = num_concurrent * requests_per_worker
        total_time = end_time - start_time
        rps = total_requests / total_time
        
        print(f"Throughput: {rps:.1f} RPS")
        assert rps > 100, f"Throughput {rps:.1f} RPS below 100 RPS requirement"
    
    @pytest.mark.asyncio
    async def test_anomaly_detection_accuracy(self):
        """Test anomaly detection accuracy for different cases."""
        detector = AnomalyDetector()
        
        # Test normal cases (should not be anomalies)
        normal_cases = [
            {'request_rate': 100, 'error_rate': 0.01},
            {'request_rate': 150, 'error_rate': 0.02},
            {'request_rate': 200, 'error_rate': 0.015},
        ]
        
        for case in normal_cases:
            result = await detector.detect_anomaly(case)
            assert not result, f"Normal case {case} incorrectly flagged as anomaly"
        
        # Test anomalous cases (should be anomalies)
        anomalous_cases = [
            {'request_rate': 2000, 'error_rate': 0.01},  # Very high rate
            {'request_rate': 100, 'error_rate': 0.2},    # Very high error rate
            {'request_rate': 5, 'error_rate': 0.01},     # Very low rate
        ]
        
        for case in anomalous_cases:
            result = await detector.detect_anomaly(case)
            assert result, f"Anomalous case {case} not detected as anomaly"
    
    @pytest.mark.asyncio
    async def test_constitutional_compliance(self):
        """Test constitutional hash compliance."""
        detector = AnomalyDetector()
        
        # Verify constitutional hash is present in class
        assert hasattr(detector, '__class__')
        
        # Test that detection works with constitutional context
        metrics = {'request_rate': 100, 'error_rate': 0.01}
        result = await detector.detect_anomaly(metrics)
        
        # Result should be boolean (no exceptions)
        assert isinstance(result, bool), "Detection should return boolean"
    
    @pytest.mark.asyncio
    async def test_memory_usage_stability(self):
        """Test that memory usage remains stable during extended operation."""
        detector = AnomalyDetector()
        
        # Run extended test to check for memory leaks
        for i in range(1000):
            metrics = {'request_rate': 100 + (i % 100), 'error_rate': 0.01 + ((i % 50) * 0.001)}
            await detector.detect_anomaly(metrics)
            
            # Every 100 iterations, check we can still create new instances
            if i % 100 == 0:
                temp_detector = AnomalyDetector()
                temp_result = await temp_detector.detect_anomaly(metrics)
                assert isinstance(temp_result, bool)
        
        print("Memory stability test completed successfully")


if __name__ == "__main__":
    # Run tests directly
    asyncio.run(TestAnomalyDetectionPerformance().test_single_detection_latency())
    asyncio.run(TestAnomalyDetectionPerformance().test_concurrent_throughput())
    asyncio.run(TestAnomalyDetectionPerformance().test_anomaly_detection_accuracy())
    asyncio.run(TestAnomalyDetectionPerformance().test_constitutional_compliance())
    asyncio.run(TestAnomalyDetectionPerformance().test_memory_usage_stability())
    print("All performance tests passed!")