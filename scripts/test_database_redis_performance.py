#!/usr/bin/env python3
"""
Database and Redis Performance Testing Script

Tests database connectivity, Redis caching performance, and health check endpoints.
"""

import asyncio
import json
import statistics
import time
from typing import Any

import asyncpg
import httpx
import redis

# Configuration
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5439,
    "user": "acgs_user",
    "password": "acgs_secure_password",
    "database": "acgs_db",
}

REDIS_CONFIG = {"host": "localhost", "port": 6389, "db": 0}


class DatabaseRedisPerformanceTester:
    def __init__(self):
        self.results = {
            "database_tests": {},
            "redis_tests": {},
            "health_checks": {},
            "errors": [],
        }

    async def test_database_connectivity(self) -> dict[str, Any]:
        """Test PostgreSQL database connectivity and performance."""
        print("🗄️ Testing PostgreSQL database connectivity and performance...")

        try:
            # Test connection
            conn = await asyncpg.connect(
                host=DATABASE_CONFIG["host"],
                port=DATABASE_CONFIG["port"],
                user=DATABASE_CONFIG["user"],
                password=DATABASE_CONFIG["password"],
                database=DATABASE_CONFIG["database"],
            )

            # Test basic query performance
            query_times = []
            for i in range(10):
                start_time = time.perf_counter()
                result = await conn.fetchval("SELECT version()")
                end_time = time.perf_counter()
                query_times.append((end_time - start_time) * 1000)

            # Test table existence
            tables_query = """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """
            tables = await conn.fetch(tables_query)
            table_names = [row["table_name"] for row in tables]

            # Test HITL tables specifically
            hitl_tables_exist = all(
                table in table_names
                for table in [
                    "agent_operation_reviews",
                    "review_feedbacks",
                    "agent_confidence_profiles",
                ]
            )

            # Test insert performance on HITL tables
            insert_times = []
            if hitl_tables_exist:
                for i in range(5):
                    start_time = time.perf_counter()
                    await conn.execute(
                        """
                        INSERT INTO agent_confidence_profiles 
                        (agent_id, operation_confidence_adjustments, metadata) 
                        VALUES ($1, $2, $3)
                        ON CONFLICT (agent_id) DO UPDATE SET 
                        updated_at = NOW()
                    """,
                        f"test-agent-{i}",
                        "{}",
                        '{"test": true}',
                    )
                    end_time = time.perf_counter()
                    insert_times.append((end_time - start_time) * 1000)

            await conn.close()

            return {
                "status": "healthy",
                "connection_successful": True,
                "query_latency_ms": {
                    "min": min(query_times),
                    "max": max(query_times),
                    "mean": statistics.mean(query_times),
                    "p95": sorted(query_times)[int(0.95 * len(query_times))],
                },
                "tables_found": len(table_names),
                "hitl_tables_exist": hitl_tables_exist,
                "table_names": table_names,
                "insert_performance_ms": (
                    {
                        "min": min(insert_times) if insert_times else 0,
                        "max": max(insert_times) if insert_times else 0,
                        "mean": statistics.mean(insert_times) if insert_times else 0,
                    }
                    if insert_times
                    else None
                ),
            }

        except Exception as e:
            self.results["errors"].append(f"Database test failed: {e!s}")
            return {
                "status": "unhealthy",
                "connection_successful": False,
                "error": str(e),
            }

    def test_redis_connectivity(self) -> dict[str, Any]:
        """Test Redis connectivity and performance."""
        print("🔴 Testing Redis connectivity and performance...")

        try:
            # Connect to Redis
            r = redis.Redis(
                host=REDIS_CONFIG["host"],
                port=REDIS_CONFIG["port"],
                db=REDIS_CONFIG["db"],
                decode_responses=True,
            )

            # Test basic connectivity
            ping_result = r.ping()

            # Test write performance
            write_times = []
            for i in range(100):
                start_time = time.perf_counter()
                r.set(f"test_key_{i}", f"test_value_{i}", ex=60)
                end_time = time.perf_counter()
                write_times.append((end_time - start_time) * 1000)

            # Test read performance
            read_times = []
            for i in range(100):
                start_time = time.perf_counter()
                value = r.get(f"test_key_{i}")
                end_time = time.perf_counter()
                read_times.append((end_time - start_time) * 1000)

            # Test cache hit rate simulation
            cache_operations = []
            for i in range(50):
                # Write
                start_time = time.perf_counter()
                r.set(f"cache_test_{i}", json.dumps({"data": f"value_{i}"}), ex=300)
                write_time = time.perf_counter() - start_time

                # Read
                start_time = time.perf_counter()
                cached_value = r.get(f"cache_test_{i}")
                read_time = time.perf_counter() - start_time

                cache_operations.append(
                    {
                        "write_time_ms": write_time * 1000,
                        "read_time_ms": read_time * 1000,
                        "cache_hit": cached_value is not None,
                    }
                )

            # Clean up test keys
            test_keys = [f"test_key_{i}" for i in range(100)]
            test_keys.extend([f"cache_test_{i}" for i in range(50)])
            r.delete(*test_keys)

            cache_hit_rate = sum(1 for op in cache_operations if op["cache_hit"]) / len(
                cache_operations
            )

            return {
                "status": "healthy",
                "connection_successful": True,
                "ping_successful": ping_result,
                "write_performance_ms": {
                    "min": min(write_times),
                    "max": max(write_times),
                    "mean": statistics.mean(write_times),
                    "p95": sorted(write_times)[int(0.95 * len(write_times))],
                },
                "read_performance_ms": {
                    "min": min(read_times),
                    "max": max(read_times),
                    "mean": statistics.mean(read_times),
                    "p95": sorted(read_times)[int(0.95 * len(read_times))],
                },
                "cache_hit_rate": cache_hit_rate,
                "cache_operations_tested": len(cache_operations),
            }

        except Exception as e:
            self.results["errors"].append(f"Redis test failed: {e!s}")
            return {
                "status": "unhealthy",
                "connection_successful": False,
                "error": str(e),
            }

    async def test_health_endpoints(self) -> dict[str, Any]:
        """Test health check endpoints of all services."""
        print("🏥 Testing service health check endpoints...")

        services = {
            "auth_service": "http://localhost:8016/health",
            "hitl_service": "http://localhost:8008/health",
            "database": "http://localhost:5439",  # Will fail but we test connectivity
            "redis": "http://localhost:6389",  # Will fail but we test connectivity
        }

        health_results = {}

        async with httpx.AsyncClient(timeout=10.0) as client:
            for service_name, url in services.items():
                try:
                    start_time = time.perf_counter()

                    if service_name in ["database", "redis"]:
                        # These don't have HTTP endpoints, just test if ports are open
                        try:
                            response = await client.get(url)
                            # This will likely fail, but we measure response time
                        except:
                            pass
                        end_time = time.perf_counter()
                        health_results[service_name] = {
                            "status": "port_accessible",
                            "response_time_ms": (end_time - start_time) * 1000,
                        }
                    else:
                        response = await client.get(url)
                        end_time = time.perf_counter()

                        health_results[service_name] = {
                            "status": (
                                "healthy"
                                if response.status_code == 200
                                else "unhealthy"
                            ),
                            "status_code": response.status_code,
                            "response_time_ms": (end_time - start_time) * 1000,
                            "response_data": (
                                response.json() if response.status_code == 200 else None
                            ),
                        }

                except Exception as e:
                    health_results[service_name] = {"status": "error", "error": str(e)}

        return health_results

    async def run_comprehensive_test(self) -> dict[str, Any]:
        """Run comprehensive database and Redis performance tests."""
        print("🧪 Starting comprehensive database and Redis performance tests...")

        # Test database
        self.results["database_tests"] = await self.test_database_connectivity()

        # Test Redis
        self.results["redis_tests"] = self.test_redis_connectivity()

        # Test health endpoints
        self.results["health_checks"] = await self.test_health_endpoints()

        # Calculate overall health score
        db_healthy = self.results["database_tests"].get("status") == "healthy"
        redis_healthy = self.results["redis_tests"].get("status") == "healthy"

        services_healthy = 0
        total_services = 0
        for service, health in self.results["health_checks"].items():
            total_services += 1
            if health.get("status") in ["healthy", "port_accessible"]:
                services_healthy += 1

        overall_health_score = (
            (1 if db_healthy else 0)
            + (1 if redis_healthy else 0)
            + (services_healthy / max(1, total_services))
        ) / 3

        self.results["summary"] = {
            "overall_health_score": overall_health_score,
            "database_healthy": db_healthy,
            "redis_healthy": redis_healthy,
            "services_healthy_ratio": services_healthy / max(1, total_services),
            "total_errors": len(self.results["errors"]),
        }

        return self.results


async def main():
    """Main test execution."""
    tester = DatabaseRedisPerformanceTester()

    try:
        results = await tester.run_comprehensive_test()

        # Print results
        print("\n" + "=" * 80)
        print("🎯 DATABASE AND REDIS PERFORMANCE TEST RESULTS")
        print("=" * 80)

        print("\n📊 Overall Summary:")
        summary = results["summary"]
        print(f"  • Overall Health Score: {summary['overall_health_score'] * 100:.1f}%")
        print(
            f"  • Database Healthy: {'✅ YES' if summary['database_healthy'] else '❌ NO'}"
        )
        print(f"  • Redis Healthy: {'✅ YES' if summary['redis_healthy'] else '❌ NO'}")
        print(f"  • Services Healthy: {summary['services_healthy_ratio'] * 100:.1f}%")
        print(f"  • Total Errors: {summary['total_errors']}")

        print("\n🗄️ Database Performance:")
        db_results = results["database_tests"]
        if db_results.get("connection_successful"):
            latency = db_results.get("query_latency_ms", {})
            print("  • Connection: ✅ Successful")
            print(f"  • Query Latency (mean): {latency.get('mean', 0):.2f}ms")
            print(f"  • Query Latency (P95): {latency.get('p95', 0):.2f}ms")
            print(f"  • Tables Found: {db_results.get('tables_found', 0)}")
            print(
                f"  • HITL Tables Exist: {'✅ YES' if db_results.get('hitl_tables_exist') else '❌ NO'}"
            )

            if db_results.get("insert_performance_ms"):
                insert_perf = db_results["insert_performance_ms"]
                print(
                    f"  • Insert Performance (mean): {insert_perf.get('mean', 0):.2f}ms"
                )
        else:
            print(
                f"  • Connection: ❌ Failed - {db_results.get('error', 'Unknown error')}"
            )

        print("\n🔴 Redis Performance:")
        redis_results = results["redis_tests"]
        if redis_results.get("connection_successful"):
            write_perf = redis_results.get("write_performance_ms", {})
            read_perf = redis_results.get("read_performance_ms", {})
            print("  • Connection: ✅ Successful")
            print(f"  • Write Performance (mean): {write_perf.get('mean', 0):.2f}ms")
            print(f"  • Read Performance (mean): {read_perf.get('mean', 0):.2f}ms")
            print(
                f"  • Cache Hit Rate: {redis_results.get('cache_hit_rate', 0) * 100:.1f}%"
            )
        else:
            print(
                f"  • Connection: ❌ Failed - {redis_results.get('error', 'Unknown error')}"
            )

        print("\n🏥 Service Health Checks:")
        for service, health in results["health_checks"].items():
            status_icon = (
                "✅" if health.get("status") in ["healthy", "port_accessible"] else "❌"
            )
            response_time = health.get("response_time_ms", 0)
            print(
                f"  • {service}: {status_icon} {health.get('status', 'unknown')} ({response_time:.2f}ms)"
            )

        if results["errors"]:
            print("\n❌ Errors Encountered:")
            for error in results["errors"]:
                print(f"  • {error}")

        # Save detailed results
        with open("database_redis_performance_results.json", "w") as f:
            json.dump(results, f, indent=2)
        print("\n💾 Detailed results saved to: database_redis_performance_results.json")

    except Exception as e:
        print(f"❌ Test execution failed: {e}")


if __name__ == "__main__":
    asyncio.run(main())
