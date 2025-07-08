#!/usr/bin/env python3
"""
Health Check Script for ACGS Services

Performs comprehensive health checks on all ACGS services including:
- Service availability and response times
- Database connectivity
- Redis cache connectivity
- Constitutional compliance validation
- Performance metrics validation

Constitutional Hash: cdd01ef066bc6cf2

Usage:
    python scripts/health_check.py [options]
"""

import argparse
import asyncio
import json
import sys
import time

import httpx

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Service endpoints for health checks
SERVICES = {
    "auth_service": "http://localhost:8016",
    "constitutional_ai": "http://localhost:8001",
    "integrity_service": "http://localhost:8002",
    "formal_verification": "http://localhost:8003",
    "governance_synthesis": "http://localhost:8004",
    "policy_governance": "http://localhost:8005",
    "evolutionary_computation": "http://localhost:8006",
}

# Infrastructure endpoints
INFRASTRUCTURE = {
    "postgres": {"host": "localhost", "port": 5439, "database": "acgs_db"},
    "redis": {"host": "localhost", "port": 6389},
}

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    "response_time_ms": 100,  # Max response time for health checks
    "memory_usage_percent": 80,  # Max memory usage
    "cpu_usage_percent": 70,  # Max CPU usage
}


class HealthChecker:
    """Comprehensive health checker for ACGS services."""

    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self.results = {}
        self.overall_healthy = True

    async def check_all_services(self, check_performance: bool = True) -> bool:
        """Check health of all ACGS services."""
        print("🏥 ACGS Services Health Check")
        print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
        print("=" * 60)

        # Check services
        print("🔍 Checking ACGS Services...")
        for service_name, endpoint in SERVICES.items():
            healthy = await self._check_service_health(service_name, endpoint)
            self.overall_healthy = self.overall_healthy and healthy

        # Check infrastructure
        print("\n🏗️  Checking Infrastructure...")
        for infra_name, config in INFRASTRUCTURE.items():
            healthy = await self._check_infrastructure_health(infra_name, config)
            self.overall_healthy = self.overall_healthy and healthy

        # Check system performance
        if check_performance:
            print("\n⚡ Checking System Performance...")
            self._check_system_performance()

        # Generate summary
        self._generate_health_summary()

        return self.overall_healthy

    async def _check_service_health(self, service_name: str, endpoint: str) -> bool:
        """Check health of a specific service."""
        print(f"  🔍 {service_name}...", end=" ")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                start_time = time.time()
                response = await client.get(f"{endpoint}/health")
                response_time = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    health_data = response.json()

                    # Validate constitutional hash
                    constitutional_hash = health_data.get("constitutional_hash")
                    if constitutional_hash != CONSTITUTIONAL_HASH:
                        print(f"❌ Invalid constitutional hash: {constitutional_hash}")
                        self.results[service_name] = {
                            "status": "unhealthy",
                            "error": "invalid_constitutional_hash",
                            "constitutional_hash": constitutional_hash,
                        }
                        return False

                    # Check response time
                    if response_time > PERFORMANCE_THRESHOLDS["response_time_ms"]:
                        print(f"⚠️  Slow response ({response_time:.1f}ms)")
                        self.results[service_name] = {
                            "status": "degraded",
                            "response_time_ms": response_time,
                            "constitutional_hash": constitutional_hash,
                            "warning": "slow_response",
                        }
                        return True  # Still healthy but degraded
                    else:
                        print(f"✅ Healthy ({response_time:.1f}ms)")
                        self.results[service_name] = {
                            "status": "healthy",
                            "response_time_ms": response_time,
                            "constitutional_hash": constitutional_hash,
                        }
                        return True
                else:
                    print(f"❌ HTTP {response.status_code}")
                    self.results[service_name] = {
                        "status": "unhealthy",
                        "http_status": response.status_code,
                    }
                    return False

        except httpx.TimeoutException:
            print("❌ Timeout")
            self.results[service_name] = {"status": "unhealthy", "error": "timeout"}
            return False
        except httpx.ConnectError:
            print("❌ Connection failed")
            self.results[service_name] = {
                "status": "unhealthy",
                "error": "connection_failed",
            }
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            self.results[service_name] = {"status": "error", "error": str(e)}
            return False

    async def _check_infrastructure_health(self, infra_name: str, config: dict) -> bool:
        """Check health of infrastructure components."""
        print(f"  🔍 {infra_name}...", end=" ")

        if infra_name == "postgres":
            return await self._check_postgres_health(config)
        elif infra_name == "redis":
            return await self._check_redis_health(config)
        else:
            print(f"⚠️  Unknown infrastructure: {infra_name}")
            return False

    async def _check_postgres_health(self, config: dict) -> bool:
        """Check PostgreSQL database health."""
        try:
            # Simple connection test using subprocess
            import subprocess

            result = subprocess.run(
                [
                    "pg_isready",
                    "-h",
                    config["host"],
                    "-p",
                    str(config["port"]),
                    "-d",
                    config["database"],
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                print("✅ Connected")
                self.results["postgres"] = {"status": "healthy"}
                return True
            else:
                print("❌ Connection failed")
                self.results["postgres"] = {
                    "status": "unhealthy",
                    "error": "connection_failed",
                }
                return False

        except FileNotFoundError:
            print("⚠️  pg_isready not available, skipping")
            return True  # Don't fail if tool not available
        except Exception as e:
            print(f"❌ {e}")
            self.results["postgres"] = {"status": "unhealthy", "error": str(e)}
            return False

    async def _check_redis_health(self, config: dict) -> bool:
        """Check Redis cache health."""
        try:
            # Simple connection test using subprocess
            import subprocess

            result = subprocess.run(
                ["redis-cli", "-h", config["host"], "-p", str(config["port"]), "ping"],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0 and "PONG" in result.stdout:
                print("✅ Connected")
                self.results["redis"] = {"status": "healthy"}
                return True
            else:
                print("❌ Connection failed")
                self.results["redis"] = {
                    "status": "unhealthy",
                    "error": "connection_failed",
                }
                return False

        except FileNotFoundError:
            print("⚠️  redis-cli not available, skipping")
            return True  # Don't fail if tool not available
        except Exception as e:
            print(f"❌ {e}")
            self.results["redis"] = {"status": "unhealthy", "error": str(e)}
            return False

    def _check_system_performance(self):
        """Check system performance metrics."""
        try:
            import psutil

            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            print(f"  🖥️  CPU Usage: {cpu_percent:.1f}%", end="")
            if cpu_percent > PERFORMANCE_THRESHOLDS["cpu_usage_percent"]:
                print(" ⚠️  High")
            else:
                print(" ✅")

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            print(f"  💾 Memory Usage: {memory_percent:.1f}%", end="")
            if memory_percent > PERFORMANCE_THRESHOLDS["memory_usage_percent"]:
                print(" ⚠️  High")
            else:
                print(" ✅")

            # Disk usage
            disk = psutil.disk_usage("/")
            disk_percent = (disk.used / disk.total) * 100
            print(f"  💿 Disk Usage: {disk_percent:.1f}%", end="")
            if disk_percent > 80:
                print(" ⚠️  High")
            else:
                print(" ✅")

            self.results["system_performance"] = {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "disk_percent": disk_percent,
            }

        except ImportError:
            print("  ⚠️  psutil not available, skipping system metrics")
        except Exception as e:
            print(f"  ❌ Error checking system performance: {e}")

    def _generate_health_summary(self):
        """Generate health check summary."""
        print("\n" + "=" * 60)
        print("📊 Health Check Summary")
        print("=" * 60)

        # Count statuses
        healthy_count = sum(
            1
            for r in self.results.values()
            if isinstance(r, dict) and r.get("status") == "healthy"
        )
        degraded_count = sum(
            1
            for r in self.results.values()
            if isinstance(r, dict) and r.get("status") == "degraded"
        )
        unhealthy_count = sum(
            1
            for r in self.results.values()
            if isinstance(r, dict) and r.get("status") in ["unhealthy", "error"]
        )

        total_services = len(SERVICES) + len(INFRASTRUCTURE)

        print("📈 Services Status:")
        print(f"  ✅ Healthy: {healthy_count}")
        print(f"  ⚠️  Degraded: {degraded_count}")
        print(f"  ❌ Unhealthy: {unhealthy_count}")
        print(f"  📊 Total: {total_services}")

        # Overall status
        if unhealthy_count == 0:
            if degraded_count == 0:
                print("\n🎉 All services healthy!")
            else:
                print("\n⚠️  Some services degraded but operational")
        else:
            print(f"\n❌ {unhealthy_count} services unhealthy")

        print(f"\n🔐 Constitutional Hash: {CONSTITUTIONAL_HASH}")


async def main():
    """Main entry point for health check."""
    parser = argparse.ArgumentParser(description="ACGS Services Health Check")
    parser.add_argument(
        "--timeout", type=float, default=30.0, help="Timeout for health checks"
    )
    parser.add_argument(
        "--all-services", action="store_true", help="Check all services"
    )
    parser.add_argument(
        "--no-performance", action="store_true", help="Skip performance checks"
    )
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--service", help="Check specific service only")

    args = parser.parse_args()

    # Initialize health checker
    checker = HealthChecker(timeout=args.timeout)

    # Run health checks
    try:
        if args.service:
            # Check specific service
            if args.service in SERVICES:
                healthy = await checker._check_service_health(
                    args.service, SERVICES[args.service]
                )
            else:
                print(f"❌ Unknown service: {args.service}")
                sys.exit(1)
        else:
            # Check all services
            healthy = await checker.check_all_services(
                check_performance=not args.no_performance
            )

        # Output results
        if args.json:
            print(json.dumps(checker.results, indent=2))

        # Exit with appropriate code
        if healthy:
            sys.exit(0)
        else:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n⏹️  Health check interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n💥 Health check failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
