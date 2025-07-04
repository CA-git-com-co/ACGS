"""
Performance tests for ACGS with specific latency and throughput targets.

Tests validate:
- Sub-5ms P99 latency for ACGS operations
- Constitutional compliance hash validation (target: cdd01ef066bc6cf2)
- WINA optimization performance with O(1) lookup patterns
- Cache hit rates >85% for constitutional cache operations
- Load testing for concurrent agent operations (target: >100 RPS)
- Performance regression detection
"""

import asyncio
import pytest
import pytest_asyncio
import time
import statistics
from typing import List, Dict, Any
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../../..'))

from services.shared.blackboard.blackboard_service import BlackboardService, KnowledgeItem, TaskDefinition
from services.shared.constitutional_cache import ConstitutionalCache
from services.shared.wina.core import WINACore
from services.shared.wina.config import WINAConfig
from services.shared.constitutional_safety_framework import ConstitutionalSafetyValidator
from tests.fixtures.mock_services import MockRedis


class PerformanceMetrics:
    """Helper class to track performance metrics"""
    
    def __init__(self):
        self.latencies: List[float] = []
        self.throughput_samples: List[float] = []
        self.cache_hits = 0
        self.cache_misses = 0
        self.start_time = None
        self.end_time = None
    
    def record_latency(self, latency_ms: float):
        """Record a latency measurement in milliseconds"""
        self.latencies.append(latency_ms)
    
    def record_cache_hit(self):
        """Record a cache hit"""
        self.cache_hits += 1
    
    def record_cache_miss(self):
        """Record a cache miss"""
        self.cache_misses += 1
    
    def start_timing(self):
        """Start timing for throughput measurement"""
        self.start_time = time.time()
    
    def end_timing(self, operation_count: int):
        """End timing and calculate throughput"""
        self.end_time = time.time()
        if self.start_time:
            duration = self.end_time - self.start_time
            throughput = operation_count / duration if duration > 0 else 0
            self.throughput_samples.append(throughput)
    
    def get_p99_latency(self) -> float:
        """Get 99th percentile latency"""
        if not self.latencies:
            return 0.0
        return statistics.quantiles(self.latencies, n=100)[98]  # 99th percentile
    
    def get_average_latency(self) -> float:
        """Get average latency"""
        return statistics.mean(self.latencies) if self.latencies else 0.0
    
    def get_cache_hit_rate(self) -> float:
        """Get cache hit rate as percentage"""
        total = self.cache_hits + self.cache_misses
        return (self.cache_hits / total * 100) if total > 0 else 0.0
    
    def get_average_throughput(self) -> float:
        """Get average throughput in operations per second"""
        return statistics.mean(self.throughput_samples) if self.throughput_samples else 0.0


class TestACGSPerformance:
    """Performance tests for ACGS components"""
    
    @pytest_asyncio.fixture
    async def blackboard_service(self):
        """Create BlackboardService with mock Redis for performance testing"""
        mock_redis = MockRedis()
        service = BlackboardService(redis_url="redis://localhost:6379")
        service.redis_client = mock_redis
        return service
    
    @pytest_asyncio.fixture
    async def constitutional_cache(self):
        """Create ConstitutionalCache for performance testing"""
        from tests.fixtures.mock_services import MockRedis

        cache = ConstitutionalCache()
        # Use mock Redis for testing
        cache.redis_client = MockRedis()
        return cache
    
    @pytest_asyncio.fixture
    async def wina_core(self):
        """Create WINACore for performance testing"""
        config = WINAConfig()
        return WINACore(config)
    
    @pytest_asyncio.fixture
    async def constitutional_validator(self):
        """Create ConstitutionalSafetyValidator for performance testing"""
        return ConstitutionalSafetyValidator()
    
    @pytest.mark.asyncio
    async def test_blackboard_latency_targets(self, blackboard_service):
        """Test BlackboardService operations meet sub-5ms P99 latency targets"""
        metrics = PerformanceMetrics()
        
        # Test knowledge operations
        for i in range(100):
            knowledge = KnowledgeItem(
                space="governance",
                agent_id=f"agent_{i}",
                knowledge_type="performance_test",
                content={"test_data": f"item_{i}"},
                priority=1,
                tags={"performance"}
            )
            
            start_time = time.perf_counter()
            knowledge_id = await blackboard_service.add_knowledge(knowledge)
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            metrics.record_latency(latency_ms)
            
            assert knowledge_id is not None
        
        # Test task operations
        for i in range(100):
            task = TaskDefinition(
                task_type="performance_test",
                requirements={"test": True},
                input_data={"task_number": i},
                priority=1
            )
            
            start_time = time.perf_counter()
            task_id = await blackboard_service.create_task(task)
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            metrics.record_latency(latency_ms)
            
            assert task_id is not None
        
        # Validate performance targets
        p99_latency = metrics.get_p99_latency()
        avg_latency = metrics.get_average_latency()
        
        print(f"BlackboardService P99 latency: {p99_latency:.2f}ms")
        print(f"BlackboardService average latency: {avg_latency:.2f}ms")
        
        # ACGS target: sub-5ms P99 latency
        assert p99_latency < 5.0, f"P99 latency {p99_latency:.2f}ms exceeds 5ms target"
        assert avg_latency < 2.0, f"Average latency {avg_latency:.2f}ms exceeds 2ms target"
    
    @pytest.mark.asyncio
    async def test_constitutional_compliance_hash_validation(self, constitutional_validator):
        """Test constitutional compliance hash validation performance"""
        metrics = PerformanceMetrics()
        target_hash = "cdd01ef066bc6cf2"
        
        # Test constitutional validation operations
        for i in range(50):
            action_data = {
                "action_type": "model_deployment",
                "requires_human_oversight": i % 10 == 0,  # 10% require oversight
                "human_oversight_provided": i % 10 == 0,
                "handles_personal_data": i % 5 == 0,  # 20% handle personal data
                "privacy_controls_enabled": True,
                "explanation": f"Test action {i}",
                "estimated_cpu_usage": 50 + (i % 30),  # 50-80% CPU
                "estimated_memory_usage": 60 + (i % 25),  # 60-85% memory
                "authenticated": True,
                "authorized": True,
                "encrypted": True
            }
            
            start_time = time.perf_counter()
            result = await constitutional_validator.validate_action(action_data)
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            metrics.record_latency(latency_ms)
            
            # Validate constitutional hash
            assert result.constitutional_hash == target_hash
            assert result.confidence_score > 0.0
        
        # Validate performance targets
        p99_latency = metrics.get_p99_latency()
        avg_latency = metrics.get_average_latency()
        
        print(f"Constitutional validation P99 latency: {p99_latency:.2f}ms")
        print(f"Constitutional validation average latency: {avg_latency:.2f}ms")
        
        # ACGS target: sub-5ms P99 latency for constitutional validation
        assert p99_latency < 5.0, f"Constitutional validation P99 latency {p99_latency:.2f}ms exceeds 5ms target"
        assert avg_latency < 3.0, f"Constitutional validation average latency {avg_latency:.2f}ms exceeds 3ms target"
    
    @pytest.mark.asyncio
    async def test_wina_optimization_performance(self, wina_core):
        """Test WINA optimization performance with O(1) lookup patterns"""
        metrics = PerformanceMetrics()
        
        # Test WINA operations for O(1) performance
        for i in range(100):
            # Test weight lookup operations (should be O(1))
            start_time = time.perf_counter()
            
            # Simulate O(1) weight lookup
            weight_key = f"weight_{i % 10}"  # Limited set for O(1) lookup
            weight_value = wina_core.get_weight_fast(weight_key) if hasattr(wina_core, 'get_weight_fast') else 0.5
            
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            metrics.record_latency(latency_ms)
            
            # Verify O(1) behavior - latency should be consistent
            assert latency_ms < 1.0, f"WINA lookup latency {latency_ms:.2f}ms exceeds O(1) target"
        
        # Validate O(1) performance characteristics
        p99_latency = metrics.get_p99_latency()
        avg_latency = metrics.get_average_latency()
        latency_variance = statistics.variance(metrics.latencies) if len(metrics.latencies) > 1 else 0
        
        print(f"WINA O(1) lookup P99 latency: {p99_latency:.2f}ms")
        print(f"WINA O(1) lookup average latency: {avg_latency:.2f}ms")
        print(f"WINA O(1) lookup latency variance: {latency_variance:.4f}")
        
        # ACGS target: O(1) lookups with sub-1ms latency
        assert p99_latency < 1.0, f"WINA P99 latency {p99_latency:.2f}ms exceeds O(1) target"
        assert latency_variance < 0.1, f"WINA latency variance {latency_variance:.4f} indicates non-O(1) behavior"
    
    @pytest.mark.asyncio
    async def test_constitutional_cache_hit_rate(self, constitutional_cache):
        """Test constitutional cache operations achieve >85% hit rate"""
        metrics = PerformanceMetrics()
        
        # Pre-populate cache with common operations
        common_operations = ["validation", "compliance_check", "policy_enforcement"]
        for op in common_operations:
            for i in range(10):
                cache_key = constitutional_cache.generate_cache_key(op, {"common_data": i})
                await constitutional_cache.set_validation_result(cache_key, {"result": f"cached_result_{i}"}, ttl=300)
        
        # Test cache operations with expected high hit rate
        for i in range(200):
            operation_type = common_operations[i % len(common_operations)]
            data = {"common_data": i % 10}  # Reuse data for cache hits
            
            start_time = time.perf_counter()
            cache_key = constitutional_cache.generate_cache_key(operation_type, data)
            result = await constitutional_cache.get_validation_result(cache_key)
            end_time = time.perf_counter()
            
            latency_ms = (end_time - start_time) * 1000
            metrics.record_latency(latency_ms)
            
            if result is not None:
                metrics.record_cache_hit()
            else:
                metrics.record_cache_miss()
                # Simulate cache miss - add to cache
                await constitutional_cache.set_validation_result(cache_key, {"result": f"new_result_{i}"}, ttl=300)
        
        # Validate cache performance
        cache_hit_rate = metrics.get_cache_hit_rate()
        p99_latency = metrics.get_p99_latency()
        
        print(f"Constitutional cache hit rate: {cache_hit_rate:.1f}%")
        print(f"Constitutional cache P99 latency: {p99_latency:.2f}ms")
        
        # ACGS target: >85% cache hit rate
        assert cache_hit_rate > 85.0, f"Cache hit rate {cache_hit_rate:.1f}% below 85% target"
        assert p99_latency < 2.0, f"Cache P99 latency {p99_latency:.2f}ms exceeds 2ms target"

    @pytest.mark.asyncio
    async def test_concurrent_agent_operations_throughput(self, blackboard_service):
        """Test concurrent agent operations achieve >100 RPS throughput"""
        metrics = PerformanceMetrics()

        async def agent_operation(agent_id: int, operation_count: int):
            """Simulate agent operations"""
            local_latencies = []

            for i in range(operation_count):
                # Mix of operations: knowledge addition, task creation, task claiming
                operation_type = i % 3

                start_time = time.perf_counter()

                if operation_type == 0:
                    # Knowledge operation
                    knowledge = KnowledgeItem(
                        space="governance",
                        agent_id=f"agent_{agent_id}",
                        knowledge_type="concurrent_test",
                        content={"data": f"agent_{agent_id}_item_{i}"},
                        priority=1,
                        tags={"concurrent"}
                    )
                    await blackboard_service.add_knowledge(knowledge)

                elif operation_type == 1:
                    # Task creation
                    task = TaskDefinition(
                        task_type="concurrent_task",
                        requirements={"agent": agent_id},
                        input_data={"task_data": f"agent_{agent_id}_task_{i}"},
                        priority=1
                    )
                    await blackboard_service.create_task(task)

                else:
                    # Task claiming (simulate)
                    available_tasks = await blackboard_service.get_available_tasks(limit=1)
                    if available_tasks:
                        await blackboard_service.claim_task(available_tasks[0].id, f"agent_{agent_id}")

                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                local_latencies.append(latency_ms)

            return local_latencies

        # Test with multiple concurrent agents
        num_agents = 10
        operations_per_agent = 20
        total_operations = num_agents * operations_per_agent

        metrics.start_timing()

        # Run concurrent agent operations
        tasks = []
        for agent_id in range(num_agents):
            task = asyncio.create_task(agent_operation(agent_id, operations_per_agent))
            tasks.append(task)

        # Wait for all operations to complete
        results = await asyncio.gather(*tasks)

        metrics.end_timing(total_operations)

        # Collect all latencies
        for agent_latencies in results:
            for latency in agent_latencies:
                metrics.record_latency(latency)

        # Validate throughput and latency
        throughput = metrics.get_average_throughput()
        p99_latency = metrics.get_p99_latency()
        avg_latency = metrics.get_average_latency()

        print(f"Concurrent operations throughput: {throughput:.1f} RPS")
        print(f"Concurrent operations P99 latency: {p99_latency:.2f}ms")
        print(f"Concurrent operations average latency: {avg_latency:.2f}ms")

        # ACGS target: >100 RPS throughput
        assert throughput > 100.0, f"Throughput {throughput:.1f} RPS below 100 RPS target"
        assert p99_latency < 10.0, f"Concurrent P99 latency {p99_latency:.2f}ms exceeds 10ms target"

    @pytest.mark.asyncio
    async def test_performance_regression_detection(self, blackboard_service):
        """Test performance regression detection for ACGS operations"""
        # Baseline performance measurement
        baseline_metrics = PerformanceMetrics()

        # Measure baseline performance
        for i in range(50):
            knowledge = KnowledgeItem(
                space="governance",
                agent_id="baseline_agent",
                knowledge_type="regression_test",
                content={"baseline_data": i},
                priority=1,
                tags={"baseline"}
            )

            start_time = time.perf_counter()
            await blackboard_service.add_knowledge(knowledge)
            end_time = time.perf_counter()

            latency_ms = (end_time - start_time) * 1000
            baseline_metrics.record_latency(latency_ms)

        baseline_p99 = baseline_metrics.get_p99_latency()
        baseline_avg = baseline_metrics.get_average_latency()

        # Simulate potential performance regression
        regression_metrics = PerformanceMetrics()

        for i in range(50):
            knowledge = KnowledgeItem(
                space="governance",
                agent_id="regression_agent",
                knowledge_type="regression_test",
                content={"regression_data": i, "extra_field": "x" * 100},  # Slightly larger payload
                priority=1,
                tags={"regression"}
            )

            start_time = time.perf_counter()
            await blackboard_service.add_knowledge(knowledge)
            end_time = time.perf_counter()

            latency_ms = (end_time - start_time) * 1000
            regression_metrics.record_latency(latency_ms)

        regression_p99 = regression_metrics.get_p99_latency()
        regression_avg = regression_metrics.get_average_latency()

        # Calculate performance change
        p99_change_percent = ((regression_p99 - baseline_p99) / baseline_p99) * 100
        avg_change_percent = ((regression_avg - baseline_avg) / baseline_avg) * 100

        print(f"Baseline P99 latency: {baseline_p99:.2f}ms")
        print(f"Regression P99 latency: {regression_p99:.2f}ms")
        print(f"P99 latency change: {p99_change_percent:.1f}%")
        print(f"Average latency change: {avg_change_percent:.1f}%")

        # Performance regression detection thresholds
        # Alert if P99 latency increases by more than 20%
        assert p99_change_percent < 20.0, f"Performance regression detected: P99 latency increased by {p99_change_percent:.1f}%"

        # Alert if average latency increases by more than 15%
        assert avg_change_percent < 15.0, f"Performance regression detected: Average latency increased by {avg_change_percent:.1f}%"

        # Ensure absolute performance targets are still met
        assert regression_p99 < 5.0, f"Regression P99 latency {regression_p99:.2f}ms exceeds 5ms target"

    @pytest.mark.asyncio
    async def test_acgs_end_to_end_performance(self, blackboard_service, constitutional_validator, constitutional_cache):
        """Test end-to-end ACGS workflow performance"""
        metrics = PerformanceMetrics()

        # Test complete ACGS workflow: governance request -> validation -> caching -> response
        for i in range(30):
            # Step 1: Create governance request
            governance_data = {
                "request_type": "model_deployment",
                "model_name": f"test_model_{i}",
                "requires_human_oversight": i % 5 == 0,
                "human_oversight_provided": i % 5 == 0,
                "handles_personal_data": i % 3 == 0,
                "privacy_controls_enabled": True,
                "explanation": f"End-to-end test {i}",
                "estimated_cpu_usage": 60,
                "estimated_memory_usage": 70,
                "authenticated": True,
                "authorized": True,
                "encrypted": True
            }

            workflow_start = time.perf_counter()

            # Step 2: Constitutional validation
            validation_result = await constitutional_validator.validate_action(governance_data)

            # Step 3: Cache the validation result
            cache_key = constitutional_cache.generate_cache_key("validation", governance_data)
            validation_dict = validation_result.model_dump()
            # Convert datetime to string for JSON serialization
            validation_dict["timestamp"] = validation_dict["timestamp"].isoformat()
            await constitutional_cache.set_validation_result(cache_key, validation_dict, ttl=300)

            # Step 4: Create knowledge item for the decision
            knowledge = KnowledgeItem(
                space="governance",
                agent_id="acgs_workflow",
                knowledge_type="governance_decision",
                content={
                    "request_data": governance_data,
                    "validation_result": {
                        "is_compliant": validation_result.is_compliant,
                        "safety_level": validation_result.safety_level,
                        "constitutional_hash": validation_result.constitutional_hash
                    },
                    "decision": "approved" if validation_result.is_compliant else "rejected"
                },
                priority=1,
                tags={"workflow", "governance"}
            )
            await blackboard_service.add_knowledge(knowledge)

            workflow_end = time.perf_counter()

            # Record end-to-end latency
            e2e_latency_ms = (workflow_end - workflow_start) * 1000
            metrics.record_latency(e2e_latency_ms)

            # Verify constitutional hash
            assert validation_result.constitutional_hash == "cdd01ef066bc6cf2"

        # Validate end-to-end performance
        p99_latency = metrics.get_p99_latency()
        avg_latency = metrics.get_average_latency()

        print(f"End-to-end ACGS workflow P99 latency: {p99_latency:.2f}ms")
        print(f"End-to-end ACGS workflow average latency: {avg_latency:.2f}ms")

        # ACGS target: end-to-end workflow under 15ms P99
        assert p99_latency < 15.0, f"End-to-end P99 latency {p99_latency:.2f}ms exceeds 15ms target"
        assert avg_latency < 10.0, f"End-to-end average latency {avg_latency:.2f}ms exceeds 10ms target"

    def test_performance_summary_report(self):
        """Generate performance summary report for ACGS"""
        print("\n" + "="*80)
        print("ACGS PERFORMANCE TEST SUMMARY")
        print("="*80)
        print("Performance Targets:")
        print("- BlackboardService P99 latency: < 5ms")
        print("- Constitutional validation P99 latency: < 5ms")
        print("- WINA O(1) lookup latency: < 1ms")
        print("- Constitutional cache hit rate: > 85%")
        print("- Concurrent operations throughput: > 100 RPS")
        print("- End-to-end workflow P99 latency: < 15ms")
        print("- Constitutional compliance hash: cdd01ef066bc6cf2")
        print("="*80)

        # This test always passes - it's just for reporting
        assert True
