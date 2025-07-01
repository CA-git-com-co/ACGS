"""
System-wide Performance Tests for DGM Service.

Tests overall system performance including:
- Memory usage optimization
- CPU utilization
- Resource cleanup
- Garbage collection impact
- System stability under load
"""

import asyncio
import gc
import random
import statistics
import time

import psutil
import pytest
from dgm_service.core.dgm_engine import DGMEngine
from dgm_service.core.performance_monitor import PerformanceMonitor
from dgm_service.database import database_manager


class SystemPerformanceTest:
    """System performance testing utilities."""

    def __init__(self):
        self.process = psutil.Process()
        self.initial_memory = None
        self.initial_cpu = None

    def get_system_metrics(self) -> dict:
        """Get current system metrics."""
        return {
            "memory_mb": self.process.memory_info().rss / (1024 * 1024),
            "memory_percent": self.process.memory_percent(),
            "cpu_percent": self.process.cpu_percent(),
            "num_threads": self.process.num_threads(),
            "num_fds": (
                self.process.num_fds() if hasattr(self.process, "num_fds") else 0
            ),
            "connections": (
                len(self.process.connections())
                if hasattr(self.process, "connections")
                else 0
            ),
        }

    def start_monitoring(self):
        """Start system monitoring."""
        self.initial_memory = self.process.memory_info().rss / (1024 * 1024)
        self.initial_cpu = self.process.cpu_percent()

    async def memory_stress_test(self, iterations: int = 1000) -> dict:
        """Test memory usage under stress."""
        start_metrics = self.get_system_metrics()
        memory_samples = []

        # Create memory pressure
        large_objects = []

        for i in range(iterations):
            # Create some objects to stress memory
            large_objects.append([random.randint(1, 1000) for _ in range(1000)])

            if i % 100 == 0:
                current_memory = self.process.memory_info().rss / (1024 * 1024)
                memory_samples.append(current_memory)

                # Trigger garbage collection periodically
                if i % 500 == 0:
                    gc.collect()

        # Final cleanup
        large_objects.clear()
        gc.collect()

        end_metrics = self.get_system_metrics()

        return {
            "start_memory_mb": start_metrics["memory_mb"],
            "end_memory_mb": end_metrics["memory_mb"],
            "peak_memory_mb": (
                max(memory_samples) if memory_samples else start_metrics["memory_mb"]
            ),
            "memory_growth_mb": end_metrics["memory_mb"] - start_metrics["memory_mb"],
            "iterations": iterations,
            "memory_samples": memory_samples,
        }

    async def cpu_stress_test(self, duration_seconds: int = 30) -> dict:
        """Test CPU usage under computational load."""
        start_time = time.time()
        start_metrics = self.get_system_metrics()
        cpu_samples = []

        # CPU-intensive work
        while time.time() - start_time < duration_seconds:
            # Simulate computational work
            result = sum(i * i for i in range(10000))

            # Sample CPU usage
            cpu_percent = self.process.cpu_percent()
            cpu_samples.append(cpu_percent)

            # Small delay to allow sampling
            await asyncio.sleep(0.1)

        end_metrics = self.get_system_metrics()

        return {
            "duration_seconds": duration_seconds,
            "start_cpu_percent": start_metrics["cpu_percent"],
            "end_cpu_percent": end_metrics["cpu_percent"],
            "avg_cpu_percent": statistics.mean(cpu_samples) if cpu_samples else 0,
            "max_cpu_percent": max(cpu_samples) if cpu_samples else 0,
            "cpu_samples": cpu_samples,
        }


@pytest.fixture
def system_test():
    """Fixture for system performance testing."""
    test = SystemPerformanceTest()
    test.start_monitoring()
    return test


@pytest.mark.performance
@pytest.mark.asyncio
async def test_memory_usage_baseline(system_test):
    """Test baseline memory usage."""
    metrics = system_test.get_system_metrics()

    # Memory usage should be reasonable for a Python service
    assert (
        metrics["memory_mb"] < 500
    ), f"Baseline memory usage too high: {metrics['memory_mb']}MB"
    assert (
        metrics["memory_percent"] < 10
    ), f"Memory percentage too high: {metrics['memory_percent']}%"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_thread_count_reasonable(system_test):
    """Test that thread count is reasonable."""
    metrics = system_test.get_system_metrics()

    # Should not have excessive threads
    assert metrics["num_threads"] < 50, f"Too many threads: {metrics['num_threads']}"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_file_descriptor_usage(system_test):
    """Test file descriptor usage."""
    metrics = system_test.get_system_metrics()

    # Should not leak file descriptors
    if metrics["num_fds"] > 0:  # Only test if available on platform
        assert (
            metrics["num_fds"] < 1000
        ), f"Too many file descriptors: {metrics['num_fds']}"


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
async def test_memory_stress_resilience(system_test):
    """Test memory usage under stress."""
    result = await system_test.memory_stress_test(iterations=2000)

    # Memory growth should be controlled
    assert (
        result["memory_growth_mb"] < 100
    ), f"Memory growth too high: {result['memory_growth_mb']}MB"
    assert (
        result["peak_memory_mb"] < 1000
    ), f"Peak memory usage too high: {result['peak_memory_mb']}MB"

    # Memory should be released after stress test
    final_memory = system_test.get_system_metrics()["memory_mb"]
    assert (
        final_memory < result["peak_memory_mb"]
    ), "Memory not properly released after stress test"


@pytest.mark.performance
@pytest.mark.slow
@pytest.mark.asyncio
async def test_cpu_usage_under_load(system_test):
    """Test CPU usage under computational load."""
    result = await system_test.cpu_stress_test(duration_seconds=15)

    # CPU usage should be reasonable and not spike excessively
    assert (
        result["avg_cpu_percent"] < 80
    ), f"Average CPU usage too high: {result['avg_cpu_percent']}%"
    assert (
        result["max_cpu_percent"] < 95
    ), f"Peak CPU usage too high: {result['max_cpu_percent']}%"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_dgm_engine_performance():
    """Test DGM engine performance."""
    engine = DGMEngine()

    # Test engine initialization time
    start_time = time.perf_counter()
    await engine.initialize()
    init_time = (time.perf_counter() - start_time) * 1000

    assert init_time < 1000, f"DGM engine initialization too slow: {init_time}ms"

    # Test status retrieval performance
    start_time = time.perf_counter()
    status = await engine.get_status()
    status_time = (time.perf_counter() - start_time) * 1000

    assert status_time < 100, f"DGM engine status retrieval too slow: {status_time}ms"
    assert status is not None, "DGM engine status should not be None"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_performance_monitor_efficiency():
    """Test performance monitor efficiency."""
    monitor = PerformanceMonitor()

    # Test metrics collection performance
    start_time = time.perf_counter()
    metrics = await monitor.get_current_metrics()
    collection_time = (time.perf_counter() - start_time) * 1000

    assert collection_time < 200, f"Metrics collection too slow: {collection_time}ms"
    assert metrics is not None, "Metrics should not be None"

    # Test metrics aggregation performance
    start_time = time.perf_counter()
    summary = await monitor.get_metrics_summary(
        start_time=time.time() - 3600,
        end_time=time.time(),  # Last hour
    )
    aggregation_time = (time.perf_counter() - start_time) * 1000

    assert aggregation_time < 500, f"Metrics aggregation too slow: {aggregation_time}ms"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_database_connection_efficiency():
    """Test database connection efficiency."""
    # Test connection establishment time
    start_time = time.perf_counter()
    await database_manager.initialize()
    init_time = (time.perf_counter() - start_time) * 1000

    assert init_time < 2000, f"Database initialization too slow: {init_time}ms"

    # Test session creation performance
    session_times = []
    for _ in range(10):
        start_time = time.perf_counter()
        async with database_manager.get_session() as session:
            await session.execute("SELECT 1")
        session_time = (time.perf_counter() - start_time) * 1000
        session_times.append(session_time)

    avg_session_time = statistics.mean(session_times)
    assert avg_session_time < 50, f"Average session time too slow: {avg_session_time}ms"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_garbage_collection_impact():
    """Test garbage collection impact on performance."""
    # Measure performance before GC
    start_time = time.perf_counter()
    for _ in range(1000):
        data = [i for i in range(100)]
        del data
    pre_gc_time = time.perf_counter() - start_time

    # Force garbage collection
    gc_start = time.perf_counter()
    gc.collect()
    gc_time = (time.perf_counter() - gc_start) * 1000

    # Measure performance after GC
    start_time = time.perf_counter()
    for _ in range(1000):
        data = [i for i in range(100)]
        del data
    post_gc_time = time.perf_counter() - start_time

    # GC should not take too long
    assert gc_time < 100, f"Garbage collection too slow: {gc_time}ms"

    # Performance should not degrade significantly after GC
    performance_ratio = post_gc_time / pre_gc_time
    assert (
        performance_ratio < 2.0
    ), f"Performance degraded too much after GC: {performance_ratio}x"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_concurrent_operations_system_impact():
    """Test system impact of concurrent operations."""
    initial_metrics = psutil.Process().memory_info().rss / (1024 * 1024)

    async def worker_task():
        # Simulate concurrent work
        for _ in range(100):
            data = [random.randint(1, 1000) for _ in range(1000)]
            await asyncio.sleep(0.01)
            del data

    # Run concurrent tasks
    start_time = time.perf_counter()
    tasks = [worker_task() for _ in range(20)]
    await asyncio.gather(*tasks)
    execution_time = time.perf_counter() - start_time

    final_metrics = psutil.Process().memory_info().rss / (1024 * 1024)
    memory_growth = final_metrics - initial_metrics

    # Concurrent operations should complete efficiently
    assert execution_time < 30, f"Concurrent operations too slow: {execution_time}s"
    assert (
        memory_growth < 50
    ), f"Memory growth too high during concurrent ops: {memory_growth}MB"


@pytest.mark.performance
@pytest.mark.asyncio
async def test_resource_cleanup_efficiency():
    """Test resource cleanup efficiency."""
    initial_metrics = psutil.Process().memory_info().rss / (1024 * 1024)

    # Create and cleanup resources
    resources = []
    for i in range(1000):
        resource = {
            "id": i,
            "data": [random.randint(1, 1000) for _ in range(100)],
            "timestamp": time.time(),
        }
        resources.append(resource)

    peak_memory = psutil.Process().memory_info().rss / (1024 * 1024)

    # Cleanup resources
    cleanup_start = time.perf_counter()
    resources.clear()
    gc.collect()
    cleanup_time = (time.perf_counter() - cleanup_start) * 1000

    final_memory = psutil.Process().memory_info().rss / (1024 * 1024)

    # Cleanup should be efficient
    assert cleanup_time < 100, f"Resource cleanup too slow: {cleanup_time}ms"

    # Memory should be mostly reclaimed
    memory_reclaimed = peak_memory - final_memory
    memory_growth = peak_memory - initial_metrics
    reclaim_ratio = memory_reclaimed / memory_growth if memory_growth > 0 else 1.0

    assert reclaim_ratio > 0.7, f"Memory reclaim ratio too low: {reclaim_ratio:.2f}"
