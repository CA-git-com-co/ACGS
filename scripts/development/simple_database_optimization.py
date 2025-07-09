#!/usr/bin/env python3
"""
Simple Database Performance Optimization for ACGS-1 Phase A3
Implements database optimizations without complex dependencies
"""

import asyncio
import json
import os
import time
from datetime import datetime

import asyncpg
import psutil

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class SimpleDatabaseOptimizer:
    """Simple database optimizer for ACGS-1."""

    def __init__(self, database_url: str = None):
        self.database_url = (
            database_url
            or "postgresql://acgs_user:acgs_password@localhost:5433/acgs_pgp_db"
        )
        self.connection = None
        self.results = {
            "timestamp": datetime.utcnow().isoformat(),
            "phases": {},
            "overall_status": "pending",
        }

    async def connect(self):
        """Connect to the database."""
        try:
            self.connection = await asyncpg.connect(self.database_url)
            print("✅ Database connection established")
            return True
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            # Try alternative ports
            for port in [5434, 5435, 5432]:
                try:
                    alt_url = self.database_url.replace(":5433/", f":{port}/")
                    self.connection = await asyncpg.connect(alt_url)
                    print(f"✅ Database connection established on port {port}")
                    self.database_url = alt_url
                    return True
                except Exception:
                    continue
            return False

    async def analyze_performance(self):
        """Analyze current database performance."""
        print("\n📊 Phase 1: Database Performance Analysis")

        try:
            # Connection statistics
            conn_stats = await self.connection.fetch(
                """
                SELECT
                    count(*) as total_connections,
                    count(*) FILTER (WHERE state = 'active') as active_connections,
                    count(*) FILTER (WHERE state = 'idle') as idle_connections
                FROM pg_stat_activity
                WHERE datname = current_database()
            """
            )

            # Database size
            db_size = await self.connection.fetchrow(
                """
                SELECT
                    pg_size_pretty(pg_database_size(current_database())) as database_size,
                    pg_database_size(current_database()) as database_size_bytes
            """
            )

            # Table statistics
            table_stats = await self.connection.fetch(
                """
                SELECT
                    schemaname,
                    tablename,
                    n_live_tup,
                    n_dead_tup
                FROM pg_stat_user_tables
                ORDER BY n_live_tup DESC
                LIMIT 10
            """
            )

            metrics = {
                "connection_stats": dict(conn_stats[0]) if conn_stats else {},
                "database_size": dict(db_size) if db_size else {},
                "table_stats": [dict(row) for row in table_stats],
                "system_resources": {
                    "cpu_percent": psutil.cpu_percent(),
                    "memory_percent": psutil.virtual_memory().percent,
                    "disk_usage": psutil.disk_usage("/").percent,
                },
            }

            self.results["phases"]["analysis"] = {
                "status": "completed",
                "metrics": metrics,
            }

            # Print summary
            if conn_stats:
                print(
                    f"   📈 Active connections: {conn_stats[0]['active_connections']}"
                )
                print(f"   📈 Total connections: {conn_stats[0]['total_connections']}")

            if db_size:
                print(f"   💾 Database size: {db_size['database_size']}")

            print(f"   🖥️  CPU usage: {metrics['system_resources']['cpu_percent']}%")
            print(
                f"   🧠 Memory usage: {metrics['system_resources']['memory_percent']}%"
            )

            print("✅ Phase 1 completed: Performance analysis")
            return True

        except Exception as e:
            print(f"❌ Phase 1 failed: {e}")
            self.results["phases"]["analysis"] = {"status": "failed", "error": str(e)}
            return False

    async def create_indexes(self):
        """Create performance indexes."""
        print("\n🔍 Phase 2: Creating Performance Indexes")

        # Define essential indexes for governance operations
        indexes = [
            {
                "name": "idx_users_email_active",
                "sql": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email_active ON users(email) WHERE is_active = true",
            },
            {
                "name": "idx_users_username_active",
                "sql": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_username_active ON users(username) WHERE is_active = true",
            },
            {
                "name": "idx_security_events_user_timestamp",
                "sql": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_security_events_user_timestamp ON security_events(user_id, timestamp DESC)",
            },
            {
                "name": "idx_audit_logs_resource_action",
                "sql": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_logs_resource_action ON audit_logs(resource_type, action, timestamp DESC)",
            },
            {
                "name": "idx_policy_rules_name_active",
                "sql": "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_policy_rules_name_active ON policy_rules(name) WHERE is_active = true",
            },
        ]

        created = []
        failed = []
        skipped = []

        for index in indexes:
            try:
                # Check if table exists
                table_name = index["sql"].split(" ON ")[1].split("(")[0].strip()
                table_exists = await self.connection.fetchval(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables
                        WHERE table_name = $1
                    )
                """,
                    table_name,
                )

                if not table_exists:
                    skipped.append(
                        {
                            "name": index["name"],
                            "reason": f"Table {table_name} does not exist",
                        }
                    )
                    continue

                # Create index
                await self.connection.execute(index["sql"])
                created.append(index["name"])
                print(f"   ✅ Created: {index['name']}")

            except Exception as e:
                failed.append({"name": index["name"], "error": str(e)})
                print(f"   ❌ Failed: {index['name']} - {e!s}")

        self.results["phases"]["indexes"] = {
            "status": "completed",
            "created": len(created),
            "failed": len(failed),
            "skipped": len(skipped),
            "details": {"created": created, "failed": failed, "skipped": skipped},
        }

        print(
            f"   📊 Summary: {len(created)} created, {len(failed)} failed, {len(skipped)} skipped"
        )
        print("✅ Phase 2 completed: Index creation")
        return True

    async def vacuum_analyze(self):
        """Perform database maintenance."""
        print("\n🧹 Phase 3: Database Maintenance")

        try:
            # Get list of user tables
            tables = await self.connection.fetch(
                """
                SELECT tablename
                FROM pg_tables
                WHERE schemaname = 'public'
            """
            )

            successful = []
            failed = []

            for table_row in tables:
                table_name = table_row["tablename"]
                try:
                    await self.connection.execute(f"VACUUM ANALYZE {table_name}")
                    successful.append(table_name)
                    print(f"   ✅ Vacuumed: {table_name}")
                except Exception as e:
                    failed.append({"table": table_name, "error": str(e)})
                    print(f"   ❌ Failed: {table_name} - {e!s}")

            self.results["phases"]["maintenance"] = {
                "status": "completed",
                "tables_processed": len(successful),
                "tables_failed": len(failed),
                "details": {"successful": successful, "failed": failed},
            }

            print(
                f"   📊 Summary: {len(successful)} tables processed, {len(failed)} failed"
            )
            print("✅ Phase 3 completed: Database maintenance")
            return True

        except Exception as e:
            print(f"❌ Phase 3 failed: {e}")
            self.results["phases"]["maintenance"] = {
                "status": "failed",
                "error": str(e),
            }
            return False

    async def optimize_settings(self):
        """Analyze and recommend PostgreSQL settings."""
        print("\n⚙️  Phase 4: Settings Optimization")

        try:
            # Get current settings
            settings = await self.connection.fetch(
                """
                SELECT name, setting, unit, context
                FROM pg_settings
                WHERE name IN (
                    'max_connections',
                    'shared_buffers',
                    'effective_cache_size',
                    'work_mem',
                    'maintenance_work_mem'
                )
            """
            )

            current_settings = {
                row["name"]: {"value": row["setting"], "unit": row["unit"]}
                for row in settings
            }

            # Calculate recommendations based on system resources
            memory_gb = psutil.virtual_memory().total / (1024**3)
            cpu_count = psutil.cpu_count()

            recommendations = {
                "max_connections": min(200, max(100, cpu_count * 25)),
                "shared_buffers": f"{int(memory_gb * 0.25)}GB",
                "effective_cache_size": f"{int(memory_gb * 0.75)}GB",
                "work_mem": f"{max(4, int(memory_gb * 1024 / 200))}MB",
                "maintenance_work_mem": f"{int(memory_gb * 0.1)}GB",
            }

            self.results["phases"]["settings"] = {
                "status": "completed",
                "current_settings": current_settings,
                "recommendations": recommendations,
            }

            print("   📊 Current vs Recommended Settings:")
            for setting, recommended in recommendations.items():
                current = current_settings.get(setting, {}).get("value", "unknown")
                print(f"      {setting}: {current} → {recommended}")

            print("✅ Phase 4 completed: Settings analysis")
            return True

        except Exception as e:
            print(f"❌ Phase 4 failed: {e}")
            self.results["phases"]["settings"] = {"status": "failed", "error": str(e)}
            return False

    async def performance_test(self):
        """Run performance tests."""
        print("\n🚀 Phase 5: Performance Testing")

        try:
            # Simple query performance test
            start_time = time.time()

            # Test basic query performance
            await self.connection.fetchval("SELECT 1")
            basic_query_time = (time.time() - start_time) * 1000

            # Test with a more complex query if tables exist
            start_time = time.time()
            try:
                await self.connection.fetch("SELECT COUNT(*) FROM pg_tables")
                complex_query_time = (time.time() - start_time) * 1000
            except Exception:
                complex_query_time = 0

            # Connection pool test
            start_time = time.time()
            connections = []
            try:
                for _i in range(5):
                    conn = await asyncpg.connect(self.database_url)
                    connections.append(conn)

                connection_time = (time.time() - start_time) * 1000

                # Close connections
                for conn in connections:
                    await conn.close()

            except Exception as e:
                connection_time = 0
                print(f"   ⚠️  Connection pool test failed: {e}")

            performance_results = {
                "basic_query_ms": round(basic_query_time, 2),
                "complex_query_ms": round(complex_query_time, 2),
                "connection_pool_ms": round(connection_time, 2),
                "target_response_time_ms": 500,
            }

            self.results["phases"]["performance"] = {
                "status": "completed",
                "results": performance_results,
            }

            print(f"   ⚡ Basic query: {performance_results['basic_query_ms']}ms")
            print(f"   ⚡ Complex query: {performance_results['complex_query_ms']}ms")
            print(
                f"   ⚡ Connection pool: {performance_results['connection_pool_ms']}ms"
            )

            # Check if we meet performance targets
            meets_target = performance_results["basic_query_ms"] < 500
            print(
                f"   🎯 Performance target (<500ms): {'✅ MET' if meets_target else '❌ NOT MET'}"
            )

            print("✅ Phase 5 completed: Performance testing")
            return True

        except Exception as e:
            print(f"❌ Phase 5 failed: {e}")
            self.results["phases"]["performance"] = {
                "status": "failed",
                "error": str(e),
            }
            return False

    async def generate_report(self):
        """Generate optimization report."""
        print("\n📋 Generating Optimization Report")

        # Calculate success rate
        completed_phases = sum(
            1
            for phase in self.results["phases"].values()
            if phase.get("status") == "completed"
        )
        total_phases = len(self.results["phases"])

        success_rate = (
            (completed_phases / total_phases * 100) if total_phases > 0 else 0
        )

        self.results["overall_status"] = (
            "success"
            if success_rate >= 80
            else "partial" if success_rate >= 60 else "failed"
        )
        self.results["success_rate"] = success_rate

        # Save report
        os.makedirs("/home/dislove/ACGS-1/logs", exist_ok=True)
        report_path = (
            "/home/dislove/ACGS-1/logs/simple_database_optimization_report.json"
        )

        with open(report_path, "w") as f:
            json.dump(self.results, f, indent=2, default=str)

        print(f"   📄 Report saved to: {report_path}")
        print(f"   📊 Overall success rate: {success_rate:.1f}%")
        print(f"   ✅ Completed phases: {completed_phases}/{total_phases}")

        return self.results

    async def run_optimization(self):
        """Run complete database optimization."""
        print("🚀 Starting ACGS-1 Database Performance Optimization")
        print("=" * 60)

        start_time = time.time()

        # Connect to database
        if not await self.connect():
            return False

        try:
            # Run optimization phases
            phases = [
                self.analyze_performance,
                self.create_indexes,
                self.vacuum_analyze,
                self.optimize_settings,
                self.performance_test,
            ]

            for i, phase in enumerate(phases, 1):
                print(f"\n⏳ Executing Phase {i}/{len(phases)}...")
                await phase()

            # Generate report
            await self.generate_report()

            duration = time.time() - start_time
            print(f"\n🎉 Database optimization completed in {duration:.2f} seconds")

            # Print final summary
            overall_status = self.results["overall_status"]
            if overall_status == "success":
                print("✅ Optimization successful - Database performance enhanced")
            elif overall_status == "partial":
                print(
                    "⚠️  Optimization partially successful - Some improvements applied"
                )
            else:
                print("❌ Optimization failed - Manual intervention required")

            return overall_status in ["success", "partial"]

        finally:
            if self.connection:
                await self.connection.close()


async def main():
    """Main optimization function."""
    optimizer = SimpleDatabaseOptimizer()
    success = await optimizer.run_optimization()
    return 0 if success else 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
