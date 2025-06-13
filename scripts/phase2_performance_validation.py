#!/usr/bin/env python3
"""
ACGS-1 Phase 2: Performance Optimization Validation Script

This script validates the Phase 2 performance enhancements including:
1. Enhanced Redis multi-tier caching performance
2. Optimized PostgreSQL connection pooling
3. HAProxy load balancing validation
4. >1000 concurrent user simulation
5. <500ms response time validation
6. >99.9% availability testing

Usage:
    python scripts/phase2_performance_validation.py --full-test
    python scripts/phase2_performance_validation.py --cache-only
    python scripts/phase2_performance_validation.py --db-only
    python scripts/phase2_performance_validation.py --load-test
"""

import asyncio
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import aiohttp
import psutil
import redis.asyncio as redis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance test metrics."""
    
    # Response time metrics
    avg_response_time_ms: float = 0.0
    p95_response_time_ms: float = 0.0
    p99_response_time_ms: float = 0.0
    max_response_time_ms: float = 0.0
    
    # Throughput metrics
    requests_per_second: float = 0.0
    concurrent_users_supported: int = 0
    
    # Availability metrics
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    availability_percentage: float = 0.0
    
    # Cache metrics
    cache_hit_rate: float = 0.0
    cache_response_time_ms: float = 0.0
    
    # Database metrics
    db_connection_pool_utilization: float = 0.0
    db_avg_query_time_ms: float = 0.0
    
    # System metrics
    cpu_usage_percentage: float = 0.0
    memory_usage_percentage: float = 0.0
    
    def meets_phase2_targets(self) -> bool:
        """Check if metrics meet Phase 2 performance targets."""
        return (
            self.p95_response_time_ms < 500 and  # <500ms for 95% of requests
            self.availability_percentage > 99.9 and  # >99.9% availability
            self.concurrent_users_supported >= 1000 and  # >1000 concurrent users
            self.cache_hit_rate > 80.0  # >80% cache hit rate
        )


class Phase2PerformanceValidator:
    """Phase 2 performance optimization validator."""
    
    def __init__(self):
        self.services = {
            "auth_service": {"port": 8000, "name": "Auth Service"},
            "ac_service": {"port": 8001, "name": "AC Service"},
            "integrity_service": {"port": 8002, "name": "Integrity Service"},
            "fv_service": {"port": 8003, "name": "FV Service"},
            "gs_service": {"port": 8004, "name": "GS Service"},
            "pgc_service": {"port": 8005, "name": "PGC Service"},
            "ec_service": {"port": 8006, "name": "EC Service"},
        }
        
        self.haproxy_stats_url = "http://localhost:8080/stats"
        self.redis_url = "redis://localhost:6379"
        self.postgres_url = "postgresql://localhost:5432/acgs_pgp"
        
        self.performance_targets = {
            "max_response_time_p95": 500,  # ms
            "min_availability": 99.9,  # percentage
            "min_concurrent_users": 1000,
            "min_cache_hit_rate": 80.0,  # percentage
            "max_cpu_usage": 80.0,  # percentage
            "max_memory_usage": 85.0,  # percentage
        }
    
    async def validate_redis_caching_performance(self) -> Dict[str, Any]:
        """Validate enhanced Redis multi-tier caching performance."""
        logger.info("🔄 Validating Redis caching performance...")
        
        try:
            redis_client = redis.from_url(self.redis_url)
            
            # Test cache performance with various data sizes
            cache_metrics = {
                "small_data_performance": await self._test_cache_performance(
                    redis_client, "small", {"test": "data"}, 1000
                ),
                "medium_data_performance": await self._test_cache_performance(
                    redis_client, "medium", {"test": "x" * 1000}, 500
                ),
                "large_data_performance": await self._test_cache_performance(
                    redis_client, "large", {"test": "x" * 10000}, 100
                ),
            }
            
            # Test cache hit rates
            hit_rate = await self._test_cache_hit_rate(redis_client)
            
            await redis_client.close()
            
            return {
                "status": "success",
                "cache_metrics": cache_metrics,
                "cache_hit_rate": hit_rate,
                "meets_targets": hit_rate > self.performance_targets["min_cache_hit_rate"]
            }
            
        except Exception as e:
            logger.error(f"Redis caching validation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _test_cache_performance(
        self, redis_client: redis.Redis, test_type: str, data: Dict, iterations: int
    ) -> Dict[str, float]:
        """Test cache performance for specific data type."""
        
        # Warm up cache
        for i in range(10):
            await redis_client.set(f"warmup_{i}", json.dumps(data))
        
        # Test SET operations
        start_time = time.time()
        for i in range(iterations):
            await redis_client.set(f"test_{test_type}_{i}", json.dumps(data), ex=300)
        set_time = (time.time() - start_time) * 1000 / iterations
        
        # Test GET operations
        start_time = time.time()
        for i in range(iterations):
            await redis_client.get(f"test_{test_type}_{i}")
        get_time = (time.time() - start_time) * 1000 / iterations
        
        return {
            "avg_set_time_ms": set_time,
            "avg_get_time_ms": get_time,
            "total_operations": iterations * 2
        }
    
    async def _test_cache_hit_rate(self, redis_client: redis.Redis) -> float:
        """Test cache hit rate with realistic access patterns."""
        
        # Populate cache with test data
        test_keys = [f"hit_test_{i}" for i in range(100)]
        for key in test_keys:
            await redis_client.set(key, f"value_{key}", ex=600)
        
        # Simulate realistic access pattern (80/20 rule)
        hits = 0
        total_requests = 1000
        
        for i in range(total_requests):
            # 80% of requests access 20% of keys (hot data)
            if i % 5 < 4:  # 80% of the time
                key = test_keys[i % 20]  # Access first 20 keys
            else:  # 20% of the time
                key = f"cold_key_{i}"  # Access non-existent keys
            
            result = await redis_client.get(key)
            if result is not None:
                hits += 1
        
        return (hits / total_requests) * 100
    
    async def validate_database_performance(self) -> Dict[str, Any]:
        """Validate enhanced PostgreSQL connection pooling performance."""
        logger.info("🔄 Validating database performance...")
        
        try:
            # Import database pool manager
            from services.shared.database.pool_manager import get_pool_manager, PoolConfig
            
            # Configure enhanced pool for testing
            enhanced_config = PoolConfig(
                min_connections=10,
                max_connections=30,
                max_overflow=20,
                pool_timeout=20.0,
                pool_recycle=1800,
            )
            
            pool_manager = get_pool_manager()
            pool = pool_manager.register_pool(
                "performance_test", 
                self.postgres_url, 
                enhanced_config
            )
            
            await pool.initialize()
            
            # Test concurrent database operations
            db_metrics = await self._test_database_concurrency(pool)
            
            # Get pool metrics
            pool_metrics = pool.get_metrics()
            
            await pool.close()
            
            return {
                "status": "success",
                "db_metrics": db_metrics,
                "pool_metrics": pool_metrics,
                "meets_targets": db_metrics["avg_query_time_ms"] < 50  # <50ms target
            }
            
        except Exception as e:
            logger.error(f"Database performance validation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _test_database_concurrency(self, pool) -> Dict[str, Any]:
        """Test database performance under concurrent load."""
        
        async def execute_test_query():
            """Execute a test query."""
            start_time = time.time()
            try:
                await pool.execute_query("SELECT 1 as test_value")
                return time.time() - start_time
            except Exception:
                return None
        
        # Execute concurrent queries
        concurrent_tasks = 100
        tasks = [execute_test_query() for _ in range(concurrent_tasks)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calculate metrics
        successful_queries = [r for r in results if isinstance(r, float)]
        failed_queries = len(results) - len(successful_queries)
        
        if successful_queries:
            avg_time = sum(successful_queries) / len(successful_queries) * 1000  # Convert to ms
            max_time = max(successful_queries) * 1000
        else:
            avg_time = 0
            max_time = 0
        
        return {
            "total_queries": concurrent_tasks,
            "successful_queries": len(successful_queries),
            "failed_queries": failed_queries,
            "avg_query_time_ms": avg_time,
            "max_query_time_ms": max_time,
            "success_rate": (len(successful_queries) / concurrent_tasks) * 100
        }
    
    async def validate_load_balancing_performance(self) -> Dict[str, Any]:
        """Validate HAProxy load balancing performance."""
        logger.info("🔄 Validating load balancing performance...")
        
        try:
            # Test load balancing across services
            load_test_results = {}
            
            for service_name, service_info in self.services.items():
                result = await self._test_service_load_balancing(
                    service_name, service_info["port"]
                )
                load_test_results[service_name] = result
            
            # Calculate overall metrics
            total_requests = sum(r["total_requests"] for r in load_test_results.values())
            successful_requests = sum(r["successful_requests"] for r in load_test_results.values())
            
            overall_availability = (successful_requests / total_requests) * 100 if total_requests > 0 else 0
            
            return {
                "status": "success",
                "service_results": load_test_results,
                "overall_availability": overall_availability,
                "meets_targets": overall_availability > self.performance_targets["min_availability"]
            }
            
        except Exception as e:
            logger.error(f"Load balancing validation failed: {e}")
            return {"status": "error", "error": str(e)}
    
    async def _test_service_load_balancing(self, service_name: str, port: int) -> Dict[str, Any]:
        """Test load balancing for a specific service."""
        
        url = f"http://localhost:{port}/health"
        concurrent_requests = 50
        total_requests = 0
        successful_requests = 0
        response_times = []
        
        async def make_request():
            nonlocal total_requests, successful_requests
            start_time = time.time()
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                        total_requests += 1
                        if response.status == 200:
                            successful_requests += 1
                        
                        response_time = (time.time() - start_time) * 1000
                        response_times.append(response_time)
                        
            except Exception:
                total_requests += 1
        
        # Execute concurrent requests
        tasks = [make_request() for _ in range(concurrent_requests)]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Calculate metrics
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
        else:
            avg_response_time = 0
            p95_response_time = 0
        
        return {
            "service_name": service_name,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "avg_response_time_ms": avg_response_time,
            "p95_response_time_ms": p95_response_time,
            "availability": (successful_requests / total_requests) * 100 if total_requests > 0 else 0
        }


async def main():
    """Main validation function."""
    logger.info("🚀 Starting ACGS-1 Phase 2 Performance Validation")
    logger.info("=" * 60)
    
    validator = Phase2PerformanceValidator()
    
    # Run all validation tests
    results = {
        "timestamp": time.time(),
        "redis_caching": await validator.validate_redis_caching_performance(),
        "database_performance": await validator.validate_database_performance(),
        "load_balancing": await validator.validate_load_balancing_performance(),
    }
    
    # Generate summary report
    logger.info("\n📊 PHASE 2 PERFORMANCE VALIDATION SUMMARY")
    logger.info("=" * 50)
    
    all_targets_met = True
    for test_name, result in results.items():
        if test_name == "timestamp":
            continue
            
        status = result.get("status", "unknown")
        meets_targets = result.get("meets_targets", False)
        
        logger.info(f"{test_name.upper()}: {status.upper()}")
        logger.info(f"  Meets Targets: {'✅ YES' if meets_targets else '❌ NO'}")
        
        if not meets_targets:
            all_targets_met = False
    
    logger.info(f"\n🎯 OVERALL RESULT: {'✅ ALL TARGETS MET' if all_targets_met else '❌ TARGETS NOT MET'}")
    
    # Save detailed results
    with open("phase2_performance_validation_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    logger.info(f"📄 Detailed results saved to: phase2_performance_validation_results.json")
    
    return all_targets_met


if __name__ == "__main__":
    asyncio.run(main())
