#!/usr/bin/env python3
"""
ACGS Unified Performance Suite
Constitutional Hash: cdd01ef066bc6cf2

Consolidates and optimizes performance-critical tools for ACGS targets:
- P99 <5ms latency
- >100 RPS throughput
- >85% cache hit rate

Features:
- Async/await throughout for optimal performance
- Connection pooling for database operations
- Real-time metrics collection and monitoring
- Constitutional compliance validation
- Unified performance dashboard
"""

import asyncio
import json
import logging
import statistics
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import aiohttp
import redis.asyncio as aioredis
import asyncpg
import psutil
from pydantic import BaseModel

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# ACGS service configuration
ACGS_SERVICES = {
    "auth": {"port": 8016, "name": "Auth Service"},
    "constitutional_ai": {"port": 8001, "name": "Constitutional AI"},
    "integrity": {"port": 8002, "name": "Integrity Service"},
    "formal_verification": {"port": 8003, "name": "Formal Verification"},
    "governance_synthesis": {"port": 8004, "name": "Governance Synthesis"},
    "policy_governance": {"port": 8005, "name": "Policy Governance"},
    "evolutionary_computation": {"port": 8006, "name": "Evolutionary Computation"},
}

# Performance targets
PERFORMANCE_TARGETS = {
    "p99_latency_ms": 5.0,
    "min_throughput_rps": 100.0,
    "min_cache_hit_rate": 0.85,
    "max_cpu_percent": 80.0,
    "max_memory_percent": 85.0,
}

# Database configuration
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5439,
    "database": "acgs_db",
    "user": "acgs_user",
    "password": "acgs_secure_password",
    "min_size": 5,
    "max_size": 20,
    "command_timeout": 5,
}

# Redis configuration
REDIS_CONFIG = {
    "url": "redis://localhost:6389/0",
    "encoding": "utf-8",
    "decode_responses": True,
}

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics data structure."""

    timestamp: datetime
    service_name: str
    latency_ms: float
    throughput_rps: float
    cache_hit_rate: float
    cpu_percent: float
    memory_percent: float
    error_count: int
    constitutional_hash: str = CONSTITUTIONAL_HASH


class ACGSPerformanceSuite:
    """Unified ACGS performance testing and monitoring suite."""

    def __init__(self):
        self.db_pool: Optional[asyncpg.Pool] = None
        self.redis_client: Optional[aioredis.Redis] = None
        self.session: Optional[aiohttp.ClientSession] = None
        self.metrics_history: List[PerformanceMetrics] = []
        self.start_time = time.perf_counter()

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()

    async def initialize(self):
        """Initialize connections and resources."""
        logger.info("🚀 Initializing ACGS Performance Suite...")

        # Initialize database pool
        try:
            self.db_pool = await asyncpg.create_pool(**DATABASE_CONFIG)
            logger.info("✅ Database connection pool initialized")
        except Exception as e:
            logger.error(f"❌ Database pool initialization failed: {e}")

        # Initialize Redis client
        try:
            self.redis_client = await aioredis.from_url(**REDIS_CONFIG)
            await self.redis_client.ping()
            logger.info("✅ Redis client initialized")
        except Exception as e:
            logger.error(f"❌ Redis client initialization failed: {e}")

        # Initialize HTTP session
        timeout = aiohttp.ClientTimeout(total=10)
        self.session = aiohttp.ClientSession(timeout=timeout)
        logger.info("✅ HTTP session initialized")

    async def cleanup(self):
        """Cleanup resources."""
        logger.info("🧹 Cleaning up resources...")

        if self.session:
            await self.session.close()

        if self.redis_client:
            await self.redis_client.close()

        if self.db_pool:
            await self.db_pool.close()

        logger.info("✅ Cleanup completed")

    async def run_comprehensive_performance_test(self) -> Dict[str, Any]:
        """Run comprehensive performance test suite."""
        logger.info("🎯 Starting comprehensive performance test...")

        results = {
            "test_start": datetime.now(timezone.utc).isoformat(),
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "service_health": {},
            "load_test_results": {},
            "cache_performance": {},
            "database_performance": {},
            "system_metrics": {},
            "performance_summary": {},
        }

        try:
            # Test service health with concurrent checks
            results["service_health"] = await self._test_service_health()

            # Run load tests
            results["load_test_results"] = await self._run_load_tests()

            # Test cache performance
            results["cache_performance"] = await self._test_cache_performance()

            # Test database performance
            results["database_performance"] = await self._test_database_performance()

            # Collect system metrics
            results["system_metrics"] = await self._collect_system_metrics()

            # Generate performance summary
            results["performance_summary"] = self._generate_performance_summary(results)

            # Save results
            await self._save_results(results)

            logger.info("✅ Comprehensive performance test completed")
            return results

        except Exception as e:
            logger.error(f"❌ Performance test failed: {e}")
            raise

    async def _test_service_health(self) -> Dict[str, Any]:
        """Test health of all ACGS services concurrently."""
        logger.info("🏥 Testing service health...")

        async def check_service(
            service_name: str, config: Dict[str, Any]
        ) -> Dict[str, Any]:
            """Check individual service health."""
            start_time = time.perf_counter()

            try:
                url = f"http://localhost:{config['port']}/health"
                async with self.session.get(url) as response:
                    latency_ms = (time.perf_counter() - start_time) * 1000

                    return {
                        "service": service_name,
                        "status": "healthy" if response.status == 200 else "unhealthy",
                        "latency_ms": round(latency_ms, 2),
                        "status_code": response.status,
                        "meets_target": latency_ms
                        < PERFORMANCE_TARGETS["p99_latency_ms"],
                    }

            except Exception as e:
                latency_ms = (time.perf_counter() - start_time) * 1000
                return {
                    "service": service_name,
                    "status": "error",
                    "latency_ms": round(latency_ms, 2),
                    "error": str(e),
                    "meets_target": False,
                }

        # Run health checks concurrently
        tasks = [check_service(name, config) for name, config in ACGS_SERVICES.items()]

        health_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        healthy_services = sum(
            1 for r in health_results if r.get("status") == "healthy"
        )
        total_services = len(ACGS_SERVICES)
        avg_latency = statistics.mean([r.get("latency_ms", 0) for r in health_results])

        return {
            "healthy_services": healthy_services,
            "total_services": total_services,
            "health_percentage": (healthy_services / total_services) * 100,
            "average_latency_ms": round(avg_latency, 2),
            "services": health_results,
            "meets_targets": all(r.get("meets_target", False) for r in health_results),
        }

    async def _run_load_tests(self) -> Dict[str, Any]:
        """Run concurrent load tests."""
        logger.info("⚡ Running load tests...")

        async def load_test_worker(
            worker_id: int, duration_seconds: int = 30
        ) -> Dict[str, Any]:
            """Individual load test worker."""
            requests_made = 0
            successful_requests = 0
            total_latency = 0
            errors = []

            end_time = time.time() + duration_seconds

            while time.time() < end_time:
                start_time = time.perf_counter()

                try:
                    # Test random service
                    service_name = list(ACGS_SERVICES.keys())[
                        requests_made % len(ACGS_SERVICES)
                    ]
                    service_config = ACGS_SERVICES[service_name]
                    url = f"http://localhost:{service_config['port']}/health"

                    async with self.session.get(url) as response:
                        latency_ms = (time.perf_counter() - start_time) * 1000
                        total_latency += latency_ms

                        if response.status == 200:
                            successful_requests += 1
                        else:
                            errors.append(f"HTTP {response.status}")

                except Exception as e:
                    errors.append(str(e))

                requests_made += 1

                # Small delay to prevent overwhelming
                await asyncio.sleep(0.01)

            return {
                "worker_id": worker_id,
                "requests_made": requests_made,
                "successful_requests": successful_requests,
                "avg_latency_ms": (
                    total_latency / requests_made if requests_made > 0 else 0
                ),
                "error_count": len(errors),
                "rps": requests_made / duration_seconds,
            }

        # Run concurrent workers
        num_workers = 10
        duration = 30

        tasks = [load_test_worker(i, duration) for i in range(num_workers)]
        worker_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        total_requests = sum(r.get("requests_made", 0) for r in worker_results)
        total_successful = sum(r.get("successful_requests", 0) for r in worker_results)
        total_rps = sum(r.get("rps", 0) for r in worker_results)
        avg_latency = statistics.mean(
            [r.get("avg_latency_ms", 0) for r in worker_results]
        )

        return {
            "duration_seconds": duration,
            "concurrent_workers": num_workers,
            "total_requests": total_requests,
            "successful_requests": total_successful,
            "success_rate": (
                (total_successful / total_requests) * 100 if total_requests > 0 else 0
            ),
            "total_rps": round(total_rps, 2),
            "average_latency_ms": round(avg_latency, 2),
            "meets_rps_target": total_rps >= PERFORMANCE_TARGETS["min_throughput_rps"],
            "meets_latency_target": avg_latency
            <= PERFORMANCE_TARGETS["p99_latency_ms"],
            "worker_results": worker_results,
        }

    async def _test_cache_performance(self) -> Dict[str, Any]:
        """Test Redis cache performance."""
        logger.info("🗄️ Testing cache performance...")

        if not self.redis_client:
            return {"error": "Redis client not available"}

        try:
            # Test cache operations
            cache_operations = 1000
            cache_hits = 0
            cache_misses = 0
            total_latency = 0

            # Populate cache
            for i in range(100):
                key = f"test_key_{i}"
                value = f"test_value_{i}_{CONSTITUTIONAL_HASH}"
                await self.redis_client.set(key, value, ex=300)  # 5 min TTL

            # Test cache performance
            for i in range(cache_operations):
                start_time = time.perf_counter()

                # Mix of hits and misses
                key = f"test_key_{i % 150}"  # 100 hits, 50 misses
                result = await self.redis_client.get(key)

                latency_ms = (time.perf_counter() - start_time) * 1000
                total_latency += latency_ms

                if result:
                    cache_hits += 1
                else:
                    cache_misses += 1

            # Calculate metrics
            hit_rate = (cache_hits / cache_operations) * 100
            avg_latency = total_latency / cache_operations

            # Get Redis info
            redis_info = await self.redis_client.info("memory")
            memory_usage = redis_info.get("used_memory", 0)

            return {
                "total_operations": cache_operations,
                "cache_hits": cache_hits,
                "cache_misses": cache_misses,
                "hit_rate_percent": round(hit_rate, 2),
                "average_latency_ms": round(avg_latency, 2),
                "memory_usage_bytes": memory_usage,
                "meets_hit_rate_target": hit_rate
                >= (PERFORMANCE_TARGETS["min_cache_hit_rate"] * 100),
                "meets_latency_target": avg_latency
                <= PERFORMANCE_TARGETS["p99_latency_ms"],
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

        except Exception as e:
            logger.error(f"Cache performance test failed: {e}")
            return {"error": str(e)}

    async def _test_database_performance(self) -> Dict[str, Any]:
        """Test database performance with connection pooling."""
        logger.info("🗃️ Testing database performance...")

        if not self.db_pool:
            return {"error": "Database pool not available"}

        try:
            # Test database operations
            operations = 100
            successful_operations = 0
            total_latency = 0

            async def db_operation(operation_id: int) -> float:
                """Single database operation."""
                start_time = time.perf_counter()

                async with self.db_pool.acquire() as conn:
                    # Simple query to test performance
                    await conn.fetchval(
                        "SELECT $1 as hash, $2 as op_id, NOW()",
                        CONSTITUTIONAL_HASH,
                        operation_id,
                    )

                return (time.perf_counter() - start_time) * 1000

            # Run concurrent database operations
            tasks = [db_operation(i) for i in range(operations)]
            latencies = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            successful_latencies = [
                latency for latency in latencies if isinstance(latency, (int, float))
            ]
            successful_operations = len(successful_latencies)
            total_latency = sum(successful_latencies)
            avg_latency = (
                total_latency / successful_operations
                if successful_operations > 0
                else 0
            )

            # Get pool stats
            pool_size = self.db_pool.get_size()
            pool_idle = self.db_pool.get_idle_size()

            return {
                "total_operations": operations,
                "successful_operations": successful_operations,
                "success_rate": (successful_operations / operations) * 100,
                "average_latency_ms": round(avg_latency, 2),
                "pool_size": pool_size,
                "pool_idle": pool_idle,
                "pool_utilization": (
                    ((pool_size - pool_idle) / pool_size) * 100 if pool_size > 0 else 0
                ),
                "meets_latency_target": avg_latency
                <= PERFORMANCE_TARGETS["p99_latency_ms"],
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

        except Exception as e:
            logger.error(f"Database performance test failed: {e}")
            return {"error": str(e)}

    async def _collect_system_metrics(self) -> Dict[str, Any]:
        """Collect system performance metrics."""
        logger.info("📊 Collecting system metrics...")

        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()

            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available

            # Disk metrics
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100

            # Network metrics (if available)
            try:
                network = psutil.net_io_counters()
                network_sent = network.bytes_sent
                network_recv = network.bytes_recv
            except Exception:
                network_sent = network_recv = 0

            return {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "cpu": {
                    "percent": round(cpu_percent, 2),
                    "count": cpu_count,
                    "meets_target": cpu_percent
                    <= PERFORMANCE_TARGETS["max_cpu_percent"],
                },
                "memory": {
                    "percent": round(memory_percent, 2),
                    "available_bytes": memory_available,
                    "total_bytes": memory.total,
                    "meets_target": memory_percent
                    <= PERFORMANCE_TARGETS["max_memory_percent"],
                },
                "disk": {
                    "percent": round(disk_percent, 2),
                    "free_bytes": disk.free,
                    "total_bytes": disk.total,
                },
                "network": {
                    "bytes_sent": network_sent,
                    "bytes_received": network_recv,
                },
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

        except Exception as e:
            logger.error(f"System metrics collection failed: {e}")
            return {"error": str(e)}

    def _generate_performance_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate performance summary and recommendations."""
        logger.info("📋 Generating performance summary...")

        try:
            # Extract key metrics
            service_health = results.get("service_health", {})
            load_test = results.get("load_test_results", {})
            cache_perf = results.get("cache_performance", {})
            db_perf = results.get("database_performance", {})
            system_metrics = results.get("system_metrics", {})

            # Calculate overall scores
            health_score = service_health.get("health_percentage", 0)
            performance_score = 0

            # Performance scoring
            if load_test.get("meets_rps_target", False):
                performance_score += 25
            if load_test.get("meets_latency_target", False):
                performance_score += 25
            if cache_perf.get("meets_hit_rate_target", False):
                performance_score += 25
            if db_perf.get("meets_latency_target", False):
                performance_score += 25

            # System resource scoring
            resource_score = 0
            cpu_ok = system_metrics.get("cpu", {}).get("meets_target", False)
            memory_ok = system_metrics.get("memory", {}).get("meets_target", False)

            if cpu_ok:
                resource_score += 50
            if memory_ok:
                resource_score += 50

            # Overall assessment
            overall_score = (health_score + performance_score + resource_score) / 3

            # Generate recommendations
            recommendations = []

            if not load_test.get("meets_rps_target", False):
                recommendations.append(
                    "Optimize service throughput for >100 RPS target"
                )
            if not load_test.get("meets_latency_target", False):
                recommendations.append("Reduce P99 latency to <5ms target")
            if not cache_perf.get("meets_hit_rate_target", False):
                recommendations.append("Improve cache hit rate to >85% target")
            if not cpu_ok:
                recommendations.append("Optimize CPU usage to <80% target")
            if not memory_ok:
                recommendations.append("Optimize memory usage to <85% target")

            return {
                "overall_score": round(overall_score, 2),
                "health_score": round(health_score, 2),
                "performance_score": performance_score,
                "resource_score": resource_score,
                "meets_all_targets": overall_score >= 90,
                "recommendations": recommendations,
                "summary": {
                    "services_healthy": service_health.get("healthy_services", 0),
                    "total_services": service_health.get("total_services", 0),
                    "avg_latency_ms": load_test.get("average_latency_ms", 0),
                    "throughput_rps": load_test.get("total_rps", 0),
                    "cache_hit_rate": cache_perf.get("hit_rate_percent", 0),
                    "cpu_usage": system_metrics.get("cpu", {}).get("percent", 0),
                    "memory_usage": system_metrics.get("memory", {}).get("percent", 0),
                },
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

        except Exception as e:
            logger.error(f"Performance summary generation failed: {e}")
            return {"error": str(e)}

    async def _save_results(self, results: Dict[str, Any]):
        """Save performance test results."""
        logger.info("💾 Saving performance test results...")

        try:
            # Create results directory
            results_dir = Path("reports/performance")
            results_dir.mkdir(parents=True, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = f"acgs_performance_test_{timestamp}.json"
            filepath = results_dir / filename

            # Save results
            with open(filepath, "w") as f:
                json.dump(results, f, indent=2, default=str)

            logger.info(f"✅ Results saved to {filepath}")

            # Also save latest results
            latest_filepath = results_dir / "latest_performance_test.json"
            with open(latest_filepath, "w") as f:
                json.dump(results, f, indent=2, default=str)

        except Exception as e:
            logger.error(f"Failed to save results: {e}")

    async def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous performance monitoring."""
        logger.info(
            f"🔄 Starting continuous monitoring (interval: {interval_seconds}s)..."
        )

        try:
            while True:
                # Run lightweight performance check
                start_time = time.perf_counter()

                # Quick health check
                health_results = await self._test_service_health()

                # Quick system metrics
                system_metrics = await self._collect_system_metrics()

                # Calculate monitoring latency
                monitoring_latency = (time.perf_counter() - start_time) * 1000

                # Create monitoring record
                monitoring_record = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "monitoring_latency_ms": round(monitoring_latency, 2),
                    "health_summary": {
                        "healthy_services": health_results.get("healthy_services", 0),
                        "total_services": health_results.get("total_services", 0),
                        "avg_latency_ms": health_results.get("average_latency_ms", 0),
                    },
                    "system_summary": {
                        "cpu_percent": system_metrics.get("cpu", {}).get("percent", 0),
                        "memory_percent": system_metrics.get("memory", {}).get(
                            "percent", 0
                        ),
                    },
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                }

                # Log monitoring status
                logger.info(
                    f"Monitor: {health_results.get('healthy_services', 0)}/"
                    f"{health_results.get('total_services', 0)} services healthy, "
                    f"CPU: {system_metrics.get('cpu', {}).get('percent', 0):.1f}%, "
                    f"Memory: {system_metrics.get('memory', {}).get('percent', 0):.1f}%"
                )

                # Save monitoring record
                await self._save_monitoring_record(monitoring_record)

                # Wait for next interval
                await asyncio.sleep(interval_seconds)

        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitoring failed: {e}")
            raise

    async def _save_monitoring_record(self, record: Dict[str, Any]):
        """Save monitoring record."""
        try:
            # Create monitoring directory
            monitoring_dir = Path("reports/monitoring")
            monitoring_dir.mkdir(parents=True, exist_ok=True)

            # Append to daily monitoring log
            date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
            log_file = monitoring_dir / f"monitoring_{date_str}.jsonl"

            with open(log_file, "a") as f:
                f.write(json.dumps(record, default=str) + "\n")

        except Exception as e:
            logger.error(f"Failed to save monitoring record: {e}")


async def main():
    """Main function for running performance tests."""
    logger.info("🚀 ACGS Performance Suite Starting...")

    async with ACGSPerformanceSuite() as suite:
        try:
            # Run comprehensive performance test
            results = await suite.run_comprehensive_performance_test()

            # Print summary
            summary = results.get("performance_summary", {})
            print("\n" + "=" * 60)
            print("🎯 ACGS PERFORMANCE TEST SUMMARY")
            print("=" * 60)
            print(f"Overall Score: {summary.get('overall_score', 0):.1f}/100")
            print(
                f"Services Healthy: {summary.get('summary', {}).get('services_healthy', 0)}/{summary.get('summary', {}).get('total_services', 0)}"
            )
            print(
                f"Throughput: {summary.get('summary', {}).get('throughput_rps', 0):.1f} RPS"
            )
            print(
                f"Avg Latency: {summary.get('summary', {}).get('avg_latency_ms', 0):.2f} ms"
            )
            print(
                f"Cache Hit Rate: {summary.get('summary', {}).get('cache_hit_rate', 0):.1f}%"
            )
            print(f"CPU Usage: {summary.get('summary', {}).get('cpu_usage', 0):.1f}%")
            print(
                f"Memory Usage: {summary.get('summary', {}).get('memory_usage', 0):.1f}%"
            )

            # Print recommendations
            recommendations = summary.get("recommendations", [])
            if recommendations:
                print("\n📋 RECOMMENDATIONS:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec}")
            else:
                print("\n✅ All performance targets met!")

            print(f"\n🏛️ Constitutional Hash: {CONSTITUTIONAL_HASH}")
            print("=" * 60)

        except Exception as e:
            logger.error(f"❌ Performance test failed: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(main())
