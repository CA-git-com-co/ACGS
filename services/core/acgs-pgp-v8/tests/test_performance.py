"""
Performance Tests for ACGS-PGP v8

Load testing, stress testing, and performance validation for system components.
"""

import pytest
import pytest_asyncio
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
import statistics
from typing import List

from src.generation_engine.engine import GenerationEngine, GenerationConfig, PolicyGenerationRequest
from src.caching.cache_manager import CacheManager


@pytest.mark.performance
class TestPerformanceTargets:
    """Performance tests for ACGS-PGP v8 system targets."""
    
    @pytest_asyncio.fixture
    async def performance_engine(self, test_config):
        """Set up generation engine for performance testing."""
        config = GenerationConfig(
            gs_service_url=test_config["gs_service_url"],
            pgc_service_url=test_config["pgc_service_url"],
            constitutional_hash=test_config["constitutional_hash"]
        )
        
        engine = GenerationEngine(config)
        yield engine
        await engine.close()
    
    async def test_response_time_target(self, performance_engine, sample_policy_request, test_metrics):
        """Test <500ms response time target for policy generation."""
        response_times = []
        
        # Run 10 policy generations to get average response time
        for i in range(10):
            with patch('src.generation_engine.engine.httpx.AsyncClient') as mock_client:
                # Mock fast response
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "compliance_score": 0.85,
                    "validation_result": "compliant",
                    "constitutional_hash": "cdd01ef066bc6cf2"
                }
                
                mock_client_instance = AsyncMock()
                mock_client_instance.post.return_value = mock_response
                mock_client.return_value.__aenter__.return_value = mock_client_instance
                
                # Measure response time
                start_time = datetime.now()
                
                request = PolicyGenerationRequest(**sample_policy_request)
                response = await performance_engine.generate_policy(request)
                
                end_time = datetime.now()
                response_time_ms = (end_time - start_time).total_seconds() * 1000
                
                response_times.append(response_time_ms)
                test_metrics.record_response_time(response_time_ms)
        
        # Calculate statistics
        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        max_response_time = max(response_times)
        
        # Verify performance targets
        assert avg_response_time <= 500.0, f"Average response time {avg_response_time}ms exceeds 500ms target"
        assert p95_response_time <= 750.0, f"95th percentile response time {p95_response_time}ms exceeds 750ms"
        assert max_response_time <= 1000.0, f"Max response time {max_response_time}ms exceeds 1000ms"
        
        print(f"Performance Results:")
        print(f"  Average response time: {avg_response_time:.2f}ms")
        print(f"  95th percentile: {p95_response_time:.2f}ms")
        print(f"  Max response time: {max_response_time:.2f}ms")
    
    async def test_concurrent_policy_generation(self, performance_engine, sample_policy_request):
        """Test concurrent policy generation performance."""
        concurrent_requests = 10
        
        async def generate_policy_task():
            """Single policy generation task."""
            with patch('src.generation_engine.engine.httpx.AsyncClient') as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "compliance_score": 0.85,
                    "validation_result": "compliant",
                    "constitutional_hash": "cdd01ef066bc6cf2"
                }
                
                mock_client_instance = AsyncMock()
                mock_client_instance.post.return_value = mock_response
                mock_client.return_value.__aenter__.return_value = mock_client_instance
                
                request = PolicyGenerationRequest(**sample_policy_request)
                start_time = datetime.now()
                response = await performance_engine.generate_policy(request)
                end_time = datetime.now()
                
                return {
                    "response": response,
                    "duration_ms": (end_time - start_time).total_seconds() * 1000
                }
        
        # Run concurrent requests
        start_time = datetime.now()
        tasks = [generate_policy_task() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks)
        end_time = datetime.now()
        
        total_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Verify all requests completed successfully
        assert len(results) == concurrent_requests
        for result in results:
            assert result["response"].generation_id is not None
            assert result["response"].constitutional_compliance_score >= 0.8
        
        # Calculate performance metrics
        individual_times = [result["duration_ms"] for result in results]
        avg_individual_time = statistics.mean(individual_times)
        throughput = concurrent_requests / (total_time_ms / 1000)  # requests per second
        
        # Verify performance targets
        assert avg_individual_time <= 1000.0, f"Average concurrent response time {avg_individual_time}ms too high"
        assert throughput >= 5.0, f"Throughput {throughput} req/s below target of 5 req/s"
        
        print(f"Concurrent Performance Results:")
        print(f"  Concurrent requests: {concurrent_requests}")
        print(f"  Total time: {total_time_ms:.2f}ms")
        print(f"  Average individual time: {avg_individual_time:.2f}ms")
        print(f"  Throughput: {throughput:.2f} req/s")
    
    async def test_cache_performance(self, test_config):
        """Test cache performance targets."""
        cache_manager = CacheManager(
            redis_url=test_config["redis_url"],
            constitutional_hash=test_config["constitutional_hash"]
        )
        
        # Mock cache operations for performance testing
        with patch.object(cache_manager, 'initialize', new_callable=AsyncMock):
            with patch.object(cache_manager, 'get', new_callable=AsyncMock) as mock_get:
                with patch.object(cache_manager, 'set', new_callable=AsyncMock) as mock_set:
                    
                    await cache_manager.initialize()
                    
                    # Configure mock responses for cache hits/misses
                    cache_data = {"test": "data"}
                    mock_get.side_effect = [None, cache_data, cache_data, None, cache_data]  # 60% hit rate
                    mock_set.return_value = True
                    
                    # Simulate cache operations
                    cache_operations = []
                    for i in range(100):
                        start_time = datetime.now()
                        
                        # Simulate cache get
                        result = await cache_manager.get(f"test_key_{i % 20}", prefix="test")
                        
                        if result is None:
                            # Cache miss - set data
                            await cache_manager.set(f"test_key_{i % 20}", cache_data, prefix="test")
                        
                        end_time = datetime.now()
                        operation_time_ms = (end_time - start_time).total_seconds() * 1000
                        cache_operations.append(operation_time_ms)
                    
                    # Calculate cache performance
                    avg_cache_time = statistics.mean(cache_operations)
                    max_cache_time = max(cache_operations)
                    
                    # Verify cache performance targets
                    assert avg_cache_time <= 10.0, f"Average cache operation time {avg_cache_time}ms exceeds 10ms"
                    assert max_cache_time <= 50.0, f"Max cache operation time {max_cache_time}ms exceeds 50ms"
                    
                    print(f"Cache Performance Results:")
                    print(f"  Average cache operation time: {avg_cache_time:.2f}ms")
                    print(f"  Max cache operation time: {max_cache_time:.2f}ms")
        
        await cache_manager.close()
    
    async def test_memory_usage(self, performance_engine, sample_policy_request):
        """Test memory usage during policy generation."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Generate multiple policies to test memory usage
        for i in range(20):
            with patch('src.generation_engine.engine.httpx.AsyncClient') as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "compliance_score": 0.85,
                    "validation_result": "compliant",
                    "constitutional_hash": "cdd01ef066bc6cf2"
                }
                
                mock_client_instance = AsyncMock()
                mock_client_instance.post.return_value = mock_response
                mock_client.return_value.__aenter__.return_value = mock_client_instance
                
                request = PolicyGenerationRequest(**sample_policy_request)
                response = await performance_engine.generate_policy(request)
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Verify memory usage is reasonable
        assert memory_increase <= 100.0, f"Memory increase {memory_increase}MB exceeds 100MB limit"
        
        print(f"Memory Usage Results:")
        print(f"  Initial memory: {initial_memory:.2f}MB")
        print(f"  Final memory: {final_memory:.2f}MB")
        print(f"  Memory increase: {memory_increase:.2f}MB")
    
    async def test_constitutional_compliance_performance(self, performance_engine, sample_policy_request):
        """Test constitutional compliance validation performance."""
        compliance_times = []
        compliance_scores = []
        
        # Test compliance validation performance
        for i in range(20):
            with patch('src.generation_engine.engine.httpx.AsyncClient') as mock_client:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {
                    "compliance_score": 0.80 + (i % 10) * 0.02,  # Vary scores
                    "validation_result": "compliant",
                    "constitutional_hash": "cdd01ef066bc6cf2"
                }
                
                mock_client_instance = AsyncMock()
                mock_client_instance.post.return_value = mock_response
                mock_client.return_value.__aenter__.return_value = mock_client_instance
                
                start_time = datetime.now()
                
                # Test constitutional compliance validation
                test_content = f"Test policy content {i}"
                compliance_result = await performance_engine._validate_constitutional_compliance(test_content)
                
                end_time = datetime.now()
                validation_time_ms = (end_time - start_time).total_seconds() * 1000
                
                compliance_times.append(validation_time_ms)
                compliance_scores.append(compliance_result["compliance_score"])
        
        # Calculate performance metrics
        avg_compliance_time = statistics.mean(compliance_times)
        avg_compliance_score = statistics.mean(compliance_scores)
        
        # Verify performance targets
        assert avg_compliance_time <= 200.0, f"Average compliance validation time {avg_compliance_time}ms exceeds 200ms"
        assert avg_compliance_score >= 0.8, f"Average compliance score {avg_compliance_score} below 80%"
        
        print(f"Constitutional Compliance Performance:")
        print(f"  Average validation time: {avg_compliance_time:.2f}ms")
        print(f"  Average compliance score: {avg_compliance_score:.2f}")


@pytest.mark.performance
class TestStressTests:
    """Stress tests for system limits and failure scenarios."""
    
    async def test_high_load_stress(self, test_config, sample_policy_request):
        """Test system behavior under high load."""
        config = GenerationConfig(
            gs_service_url=test_config["gs_service_url"],
            pgc_service_url=test_config["pgc_service_url"],
            constitutional_hash=test_config["constitutional_hash"]
        )
        
        engine = GenerationEngine(config)
        
        try:
            # Simulate high load with many concurrent requests
            concurrent_requests = 50
            
            async def stress_task():
                with patch('src.generation_engine.engine.httpx.AsyncClient') as mock_client:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {
                        "compliance_score": 0.85,
                        "validation_result": "compliant",
                        "constitutional_hash": "cdd01ef066bc6cf2"
                    }
                    
                    mock_client_instance = AsyncMock()
                    mock_client_instance.post.return_value = mock_response
                    mock_client.return_value.__aenter__.return_value = mock_client_instance
                    
                    request = PolicyGenerationRequest(**sample_policy_request)
                    return await engine.generate_policy(request)
            
            # Run stress test
            start_time = datetime.now()
            tasks = [stress_task() for _ in range(concurrent_requests)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = datetime.now()
            
            # Analyze results
            successful_requests = [r for r in results if not isinstance(r, Exception)]
            failed_requests = [r for r in results if isinstance(r, Exception)]
            
            success_rate = len(successful_requests) / len(results) * 100
            total_time = (end_time - start_time).total_seconds()
            
            # Verify stress test results
            assert success_rate >= 95.0, f"Success rate {success_rate}% below 95% under stress"
            assert total_time <= 30.0, f"Stress test took {total_time}s, exceeds 30s limit"
            
            print(f"Stress Test Results:")
            print(f"  Concurrent requests: {concurrent_requests}")
            print(f"  Success rate: {success_rate:.1f}%")
            print(f"  Total time: {total_time:.2f}s")
            print(f"  Failed requests: {len(failed_requests)}")
            
        finally:
            await engine.close()
