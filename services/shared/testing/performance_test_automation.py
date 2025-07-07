"""
ACGS Performance Test Automation
Constitutional Hash: cdd01ef066bc6cf2

This module provides automated performance testing to validate ACGS
performance targets: P99 <5ms latency, >100 RPS throughput, >85% cache hit rate.
"""

import asyncio
import logging
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional, Tuple

import aioredis
import httpx
import psutil

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for a test run."""

    test_name: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float

    # Latency metrics
    latencies_ms: List[float] = field(default_factory=list)
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    avg_latency_ms: float = 0.0
    max_latency_ms: float = 0.0

    # Throughput metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    requests_per_second: float = 0.0

    # Cache metrics
    cache_hits: int = 0
    cache_misses: int = 0
    cache_hit_rate: float = 0.0

    # Resource metrics
    cpu_usage_percent: float = 0.0
    memory_usage_mb: float = 0.0

    # Constitutional compliance
    constitutional_hash: str = "cdd01ef066bc6cf2"
    compliance_violations: int = 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        return (
            self.successful_requests / self.total_requests
            if self.total_requests > 0
            else 0.0
        )

    @property
    def meets_latency_target(self) -> bool:
        """Check if P99 latency meets <5ms target."""
        return self.p99_latency_ms < 5.0

    @property
    def meets_throughput_target(self) -> bool:
        """Check if throughput meets >100 RPS target."""
        return self.requests_per_second >= 100.0

    @property
    def meets_cache_target(self) -> bool:
        """Check if cache hit rate meets >85% target."""
        return self.cache_hit_rate >= 0.85

    @property
    def meets_all_targets(self) -> bool:
        """Check if all performance targets are met."""
        return (
            self.meets_latency_target
            and self.meets_throughput_target
            and self.meets_cache_target
            and self.compliance_violations == 0
        )


@dataclass
class PerformanceTestConfig:
    """Configuration for performance tests."""

    test_name: str
    target_url: str
    method: str = "GET"
    payload: Optional[Dict[str, Any]] = None
    headers: Optional[Dict[str, str]] = None

    # Test parameters
    duration_seconds: int = 60
    concurrent_users: int = 10
    ramp_up_seconds: int = 10

    # Performance targets
    target_p99_latency_ms: float = 5.0
    target_rps: float = 100.0
    target_cache_hit_rate: float = 0.85

    # Constitutional compliance
    validate_compliance: bool = True
    constitutional_hash: str = "cdd01ef066bc6cf2"


class PerformanceTestAutomation:
    """Automated performance testing for ACGS services."""

    CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.redis_client: Optional[aioredis.Redis] = None

    async def setup_redis_monitoring(self, redis_url: str):
        """Setup Redis client for cache monitoring."""
        try:
            self.redis_client = aioredis.from_url(redis_url, decode_responses=True)
            await self.redis_client.ping()
            logger.info("Redis monitoring setup successful")
        except Exception as e:
            logger.warning(f"Redis monitoring setup failed: {e}")
            self.redis_client = None

    async def run_latency_test(
        self, config: PerformanceTestConfig, num_requests: int = 1000
    ) -> PerformanceMetrics:
        """Run latency performance test."""
        logger.info(f"Starting latency test: {config.test_name}")

        start_time = datetime.utcnow()
        latencies = []
        successful_requests = 0
        failed_requests = 0
        compliance_violations = 0

        async with httpx.AsyncClient(timeout=30.0) as client:
            for i in range(num_requests):
                request_start = time.perf_counter()

                try:
                    if config.method.upper() == "GET":
                        response = await client.get(
                            config.target_url, headers=config.headers
                        )
                    elif config.method.upper() == "POST":
                        response = await client.post(
                            config.target_url,
                            json=config.payload,
                            headers=config.headers,
                        )
                    else:
                        response = await client.request(
                            config.method,
                            config.target_url,
                            json=config.payload,
                            headers=config.headers,
                        )

                    request_end = time.perf_counter()
                    latency_ms = (request_end - request_start) * 1000
                    latencies.append(latency_ms)

                    if response.status_code < 400:
                        successful_requests += 1
                    else:
                        failed_requests += 1

                    # Validate constitutional compliance
                    if config.validate_compliance:
                        if not self._validate_response_compliance(response):
                            compliance_violations += 1

                except Exception as e:
                    request_end = time.perf_counter()
                    latency_ms = (request_end - request_start) * 1000
                    latencies.append(latency_ms)
                    failed_requests += 1
                    logger.debug(f"Request {i} failed: {e}")

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        # Calculate metrics
        metrics = PerformanceMetrics(
            test_name=config.test_name,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            latencies_ms=latencies,
            total_requests=num_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            requests_per_second=num_requests / duration if duration > 0 else 0,
            compliance_violations=compliance_violations,
            constitutional_hash=self.CONSTITUTIONAL_HASH,
        )

        if latencies:
            metrics.avg_latency_ms = statistics.mean(latencies)
            metrics.max_latency_ms = max(latencies)

            # Calculate percentiles
            sorted_latencies = sorted(latencies)
            metrics.p50_latency_ms = statistics.median(sorted_latencies)

            if len(sorted_latencies) >= 20:  # Need enough samples for percentiles
                metrics.p95_latency_ms = statistics.quantiles(sorted_latencies, n=20)[
                    18
                ]  # 95th percentile
                metrics.p99_latency_ms = statistics.quantiles(sorted_latencies, n=100)[
                    98
                ]  # 99th percentile

        logger.info(
            f"Latency test completed: {config.test_name} - "
            f"P99: {metrics.p99_latency_ms:.2f}ms, "
            f"Success rate: {metrics.success_rate:.2%}"
        )

        self.metrics.append(metrics)
        return metrics

    async def run_throughput_test(
        self, config: PerformanceTestConfig
    ) -> PerformanceMetrics:
        """Run throughput performance test with concurrent requests."""
        logger.info(f"Starting throughput test: {config.test_name}")

        start_time = datetime.utcnow()

        # Track metrics across all concurrent workers
        all_latencies = []
        total_successful = 0
        total_failed = 0
        total_requests = 0
        compliance_violations = 0

        async def worker(
            worker_id: int, duration: float
        ) -> Tuple[List[float], int, int, int, int]:
            """Worker function for concurrent requests."""
            worker_latencies = []
            worker_successful = 0
            worker_failed = 0
            worker_requests = 0
            worker_violations = 0

            worker_end_time = time.time() + duration

            async with httpx.AsyncClient(timeout=30.0) as client:
                while time.time() < worker_end_time:
                    request_start = time.perf_counter()

                    try:
                        if config.method.upper() == "GET":
                            response = await client.get(
                                config.target_url, headers=config.headers
                            )
                        elif config.method.upper() == "POST":
                            response = await client.post(
                                config.target_url,
                                json=config.payload,
                                headers=config.headers,
                            )
                        else:
                            response = await client.request(
                                config.method,
                                config.target_url,
                                json=config.payload,
                                headers=config.headers,
                            )

                        request_end = time.perf_counter()
                        latency_ms = (request_end - request_start) * 1000
                        worker_latencies.append(latency_ms)
                        worker_requests += 1

                        if response.status_code < 400:
                            worker_successful += 1
                        else:
                            worker_failed += 1

                        # Validate constitutional compliance
                        if config.validate_compliance:
                            if not self._validate_response_compliance(response):
                                worker_violations += 1

                    except Exception as e:
                        request_end = time.perf_counter()
                        latency_ms = (request_end - request_start) * 1000
                        worker_latencies.append(latency_ms)
                        worker_requests += 1
                        worker_failed += 1
                        logger.debug(f"Worker {worker_id} request failed: {e}")

            return (
                worker_latencies,
                worker_successful,
                worker_failed,
                worker_requests,
                worker_violations,
            )

        # Run concurrent workers
        tasks = []
        for i in range(config.concurrent_users):
            task = asyncio.create_task(worker(i, config.duration_seconds))
            tasks.append(task)

        # Wait for all workers to complete
        results = await asyncio.gather(*tasks)

        # Aggregate results
        for latencies, successful, failed, requests, violations in results:
            all_latencies.extend(latencies)
            total_successful += successful
            total_failed += failed
            total_requests += requests
            compliance_violations += violations

        end_time = datetime.utcnow()
        actual_duration = (end_time - start_time).total_seconds()

        # Calculate metrics
        metrics = PerformanceMetrics(
            test_name=config.test_name,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=actual_duration,
            latencies_ms=all_latencies,
            total_requests=total_requests,
            successful_requests=total_successful,
            failed_requests=total_failed,
            requests_per_second=(
                total_requests / actual_duration if actual_duration > 0 else 0
            ),
            compliance_violations=compliance_violations,
            constitutional_hash=self.CONSTITUTIONAL_HASH,
        )

        if all_latencies:
            metrics.avg_latency_ms = statistics.mean(all_latencies)
            metrics.max_latency_ms = max(all_latencies)

            sorted_latencies = sorted(all_latencies)
            metrics.p50_latency_ms = statistics.median(sorted_latencies)

            if len(sorted_latencies) >= 20:
                metrics.p95_latency_ms = statistics.quantiles(sorted_latencies, n=20)[
                    18
                ]
                metrics.p99_latency_ms = statistics.quantiles(sorted_latencies, n=100)[
                    98
                ]

        logger.info(
            f"Throughput test completed: {config.test_name} - "
            f"RPS: {metrics.requests_per_second:.1f}, "
            f"P99: {metrics.p99_latency_ms:.2f}ms"
        )

        self.metrics.append(metrics)
        return metrics

    async def run_cache_performance_test(
        self, config: PerformanceTestConfig, cache_test_operations: List[Callable]
    ) -> PerformanceMetrics:
        """Run cache performance test to validate hit rate."""
        logger.info(f"Starting cache performance test: {config.test_name}")

        if not self.redis_client:
            logger.warning("Redis client not available for cache testing")
            return PerformanceMetrics(
                test_name=config.test_name,
                start_time=datetime.utcnow(),
                end_time=datetime.utcnow(),
                duration_seconds=0.0,
                constitutional_hash=self.CONSTITUTIONAL_HASH,
            )

        start_time = datetime.utcnow()

        # Get initial Redis stats
        initial_stats = await self._get_redis_stats()

        # Run cache operations
        for operation in cache_test_operations:
            try:
                await operation(self.redis_client)
            except Exception as e:
                logger.debug(f"Cache operation failed: {e}")

        # Get final Redis stats
        final_stats = await self._get_redis_stats()

        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()

        # Calculate cache metrics
        cache_hits = final_stats.get("keyspace_hits", 0) - initial_stats.get(
            "keyspace_hits", 0
        )
        cache_misses = final_stats.get("keyspace_misses", 0) - initial_stats.get(
            "keyspace_misses", 0
        )
        total_cache_operations = cache_hits + cache_misses
        cache_hit_rate = (
            cache_hits / total_cache_operations if total_cache_operations > 0 else 0.0
        )

        metrics = PerformanceMetrics(
            test_name=config.test_name,
            start_time=start_time,
            end_time=end_time,
            duration_seconds=duration,
            cache_hits=cache_hits,
            cache_misses=cache_misses,
            cache_hit_rate=cache_hit_rate,
            constitutional_hash=self.CONSTITUTIONAL_HASH,
        )

        logger.info(
            f"Cache performance test completed: {config.test_name} - "
            f"Hit rate: {cache_hit_rate:.2%} ({cache_hits}/{total_cache_operations})"
        )

        self.metrics.append(metrics)
        return metrics

    async def run_comprehensive_performance_test(
        self, service_name: str, service_configs: List[PerformanceTestConfig]
    ) -> Dict[str, PerformanceMetrics]:
        """Run comprehensive performance test suite for a service."""
        logger.info(f"Starting comprehensive performance test for {service_name}")

        results = {}

        for config in service_configs:
            try:
                # Run latency test
                latency_config = PerformanceTestConfig(
                    test_name=f"{config.test_name}_latency",
                    target_url=config.target_url,
                    method=config.method,
                    payload=config.payload,
                    headers=config.headers,
                    validate_compliance=config.validate_compliance,
                )
                latency_metrics = await self.run_latency_test(latency_config, 1000)
                results[f"{config.test_name}_latency"] = latency_metrics

                # Run throughput test
                throughput_config = PerformanceTestConfig(
                    test_name=f"{config.test_name}_throughput",
                    target_url=config.target_url,
                    method=config.method,
                    payload=config.payload,
                    headers=config.headers,
                    duration_seconds=30,  # Shorter duration for throughput test
                    concurrent_users=20,
                    validate_compliance=config.validate_compliance,
                )
                throughput_metrics = await self.run_throughput_test(throughput_config)
                results[f"{config.test_name}_throughput"] = throughput_metrics

            except Exception as e:
                logger.error(f"Performance test failed for {config.test_name}: {e}")

        logger.info(f"Comprehensive performance test completed for {service_name}")
        return results

    def _validate_response_compliance(self, response: httpx.Response) -> bool:
        """Validate constitutional compliance in response."""
        try:
            # Check headers
            if (
                response.headers.get("X-Constitutional-Hash")
                != self.CONSTITUTIONAL_HASH
            ):
                return False

            if response.headers.get("X-Constitutional-Compliance") != "verified":
                return False

            # Check JSON body if applicable
            if response.headers.get("content-type", "").startswith("application/json"):
                data = response.json()
                if isinstance(data, dict):
                    if data.get("constitutional_hash") != self.CONSTITUTIONAL_HASH:
                        return False

            return True

        except Exception:
            return False

    async def _get_redis_stats(self) -> Dict[str, Any]:
        """Get Redis statistics."""
        try:
            if self.redis_client:
                info = await self.redis_client.info()
                return {
                    "keyspace_hits": int(info.get("keyspace_hits", 0)),
                    "keyspace_misses": int(info.get("keyspace_misses", 0)),
                    "used_memory": int(info.get("used_memory", 0)),
                    "connected_clients": int(info.get("connected_clients", 0)),
                }
        except Exception as e:
            logger.debug(f"Failed to get Redis stats: {e}")

        return {}

    def generate_performance_report(
        self, service_name: str, metrics_dict: Dict[str, PerformanceMetrics]
    ) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        report = {
            "service_name": service_name,
            "constitutional_hash": self.CONSTITUTIONAL_HASH,
            "test_timestamp": datetime.utcnow().isoformat(),
            "summary": {
                "total_tests": len(metrics_dict),
                "tests_meeting_all_targets": sum(
                    1 for m in metrics_dict.values() if m.meets_all_targets
                ),
                "overall_compliance_rate": 1.0
                - (
                    sum(m.compliance_violations for m in metrics_dict.values())
                    / max(sum(m.total_requests for m in metrics_dict.values()), 1)
                ),
            },
            "performance_targets": {
                "latency_target_ms": 5.0,
                "throughput_target_rps": 100.0,
                "cache_hit_rate_target": 0.85,
            },
            "test_results": {},
        }

        for test_name, metrics in metrics_dict.items():
            report["test_results"][test_name] = {
                "meets_all_targets": metrics.meets_all_targets,
                "latency": {
                    "p99_ms": metrics.p99_latency_ms,
                    "p95_ms": metrics.p95_latency_ms,
                    "avg_ms": metrics.avg_latency_ms,
                    "meets_target": metrics.meets_latency_target,
                },
                "throughput": {
                    "rps": metrics.requests_per_second,
                    "success_rate": metrics.success_rate,
                    "meets_target": metrics.meets_throughput_target,
                },
                "cache": {
                    "hit_rate": metrics.cache_hit_rate,
                    "hits": metrics.cache_hits,
                    "misses": metrics.cache_misses,
                    "meets_target": metrics.meets_cache_target,
                },
                "compliance": {
                    "violations": metrics.compliance_violations,
                    "total_requests": metrics.total_requests,
                    "compliance_rate": 1.0
                    - (metrics.compliance_violations / max(metrics.total_requests, 1)),
                },
            }

        return report
