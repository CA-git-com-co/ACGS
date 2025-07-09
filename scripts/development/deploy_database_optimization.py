#!/usr/bin/env python3
"""
Database Performance Optimization Deployment Script for ACGS-1 Phase A3
Implements comprehensive database optimizations for high-throughput governance operations
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import structlog

from services.shared.database_optimizer import DatabasePerformanceOptimizer

# Configure logging
logging = structlog.get_logger(__name__)


class DatabaseOptimizationDeployer:
    """Deploys comprehensive database optimizations for ACGS-1."""

    def __init__(self):
        self.optimizer = None
        self.deployment_results = {
            "timestamp": datetime.utcnow().isoformat(),
            "phases": {},
            "overall_status": "pending",
            "performance_improvement": {},
            "recommendations": [],
        }

    async def initialize(self):
        """Initialize the database optimizer."""
        try:
            self.optimizer = DatabasePerformanceOptimizer()
            success = await self.optimizer.initialize()
            if not success:
                raise Exception("Failed to initialize database optimizer")

            print("✅ Database optimizer initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize database optimizer: {e}")
            return False

    async def phase_1_baseline_analysis(self):
        """Phase 1: Analyze current database performance."""
        print("\n📊 Phase 1: Baseline Performance Analysis")

        try:
            # Get baseline performance metrics
            baseline_metrics = await self.optimizer.analyze_current_performance()

            # Identify slow queries
            slow_queries = await self.optimizer.identify_slow_queries(threshold_ms=500)

            # Store baseline for comparison
            self.deployment_results["phases"]["phase_1"] = {
                "status": "completed",
                "baseline_metrics": baseline_metrics,
                "slow_queries_count": len(slow_queries),
                "recommendations": [],
            }

            # Print summary
            conn_stats = baseline_metrics.get("connection_stats", {})
            print(
                f"   📈 Active connections: {conn_stats.get('active_connections', 'N/A')}"
            )
            print(
                f"   📈 Total connections: {conn_stats.get('total_connections', 'N/A')}"
            )
            print(f"   🐌 Slow queries found: {len(slow_queries)}")

            db_size = baseline_metrics.get("database_size", {})
            print(f"   💾 Database size: {db_size.get('database_size', 'N/A')}")

            print("✅ Phase 1 completed: Baseline analysis")
            return True

        except Exception as e:
            print(f"❌ Phase 1 failed: {e}")
            self.deployment_results["phases"]["phase_1"] = {
                "status": "failed",
                "error": str(e),
            }
            return False

    async def phase_2_index_optimization(self):
        """Phase 2: Create performance indexes."""
        print("\n🔍 Phase 2: Index Optimization")

        try:
            # Create performance indexes
            index_results = await self.optimizer.create_performance_indexes()

            self.deployment_results["phases"]["phase_2"] = {
                "status": "completed",
                "indexes_created": len(index_results["created"]),
                "indexes_failed": len(index_results["failed"]),
                "indexes_skipped": len(index_results["skipped"]),
                "details": index_results,
            }

            # Print summary
            print(f"   ✅ Indexes created: {len(index_results['created'])}")
            print(f"   ❌ Indexes failed: {len(index_results['failed'])}")
            print(f"   ⏭️  Indexes skipped: {len(index_results['skipped'])}")

            if index_results["created"]:
                print("   📋 Created indexes:")
                for idx in index_results["created"][:5]:  # Show first 5
                    print(f"      - {idx}")
                if len(index_results["created"]) > 5:
                    print(f"      ... and {len(index_results['created']) - 5} more")

            if index_results["failed"]:
                print("   ⚠️  Failed indexes:")
                for failure in index_results["failed"][:3]:  # Show first 3
                    print(f"      - {failure['name']}: {failure['error']}")

            print("✅ Phase 2 completed: Index optimization")
            return True

        except Exception as e:
            print(f"❌ Phase 2 failed: {e}")
            self.deployment_results["phases"]["phase_2"] = {
                "status": "failed",
                "error": str(e),
            }
            return False

    async def phase_3_connection_optimization(self):
        """Phase 3: Optimize connection pool settings."""
        print("\n🔗 Phase 3: Connection Pool Optimization")

        try:
            # Analyze and optimize connection pool
            pool_results = await self.optimizer.optimize_connection_pool()

            self.deployment_results["phases"]["phase_3"] = {
                "status": "completed",
                "current_settings": pool_results["current_settings"],
                "recommended_settings": pool_results["recommended_settings"],
                "applied_changes": pool_results["applied_changes"],
            }

            # Print summary
            print("   📊 Current PostgreSQL settings analyzed")
            print("   💡 Recommendations generated based on system resources")

            current = pool_results["current_settings"]
            recommended = pool_results["recommended_settings"]

            print("   🔧 Key recommendations:")
            for setting, value in recommended.items():
                current_val = current.get(setting, {}).get("value", "unknown")
                print(f"      - {setting}: {current_val} → {value}")

            print("✅ Phase 3 completed: Connection optimization analysis")
            return True

        except Exception as e:
            print(f"❌ Phase 3 failed: {e}")
            self.deployment_results["phases"]["phase_3"] = {
                "status": "failed",
                "error": str(e),
            }
            return False

    async def phase_4_maintenance_operations(self):
        """Phase 4: Perform database maintenance."""
        print("\n🧹 Phase 4: Database Maintenance Operations")

        try:
            # Perform vacuum and analyze
            maintenance_results = await self.optimizer.vacuum_and_analyze()

            self.deployment_results["phases"]["phase_4"] = {
                "status": "completed",
                "vacuum_results": maintenance_results["vacuum_results"],
                "tables_processed": len(maintenance_results["vacuum_results"]),
            }

            # Print summary
            successful_vacuums = [
                r
                for r in maintenance_results["vacuum_results"]
                if r["status"] == "success"
            ]
            failed_vacuums = [
                r
                for r in maintenance_results["vacuum_results"]
                if r["status"] == "failed"
            ]

            print(f"   ✅ Tables vacuumed successfully: {len(successful_vacuums)}")
            print(f"   ❌ Tables failed: {len(failed_vacuums)}")

            if successful_vacuums:
                print("   📋 Successfully processed tables:")
                for result in successful_vacuums[:5]:  # Show first 5
                    print(f"      - {result['table']}")
                if len(successful_vacuums) > 5:
                    print(f"      ... and {len(successful_vacuums) - 5} more")

            print("✅ Phase 4 completed: Database maintenance")
            return True

        except Exception as e:
            print(f"❌ Phase 4 failed: {e}")
            self.deployment_results["phases"]["phase_4"] = {
                "status": "failed",
                "error": str(e),
            }
            return False

    async def phase_5_performance_validation(self):
        """Phase 5: Validate performance improvements."""
        print("\n📈 Phase 5: Performance Validation")

        try:
            # Generate comprehensive performance report
            performance_report = await self.optimizer.generate_performance_report()

            # Compare with baseline if available
            baseline = (
                self.deployment_results["phases"]
                .get("phase_1", {})
                .get("baseline_metrics", {})
            )
            current_metrics = performance_report["performance_metrics"]

            # Calculate improvements
            improvements = {}
            if baseline:
                baseline_conn = baseline.get("connection_stats", {})
                current_conn = current_metrics.get("connection_stats", {})

                if baseline_conn and current_conn:
                    improvements["connection_efficiency"] = {
                        "baseline_active": baseline_conn.get("active_connections", 0),
                        "current_active": current_conn.get("active_connections", 0),
                        "improvement": (
                            "optimized"
                            if current_conn.get("active_connections", 0)
                            <= baseline_conn.get("active_connections", 0)
                            else "increased"
                        ),
                    }

            self.deployment_results["phases"]["phase_5"] = {
                "status": "completed",
                "performance_report": performance_report,
                "optimization_score": performance_report["optimization_score"],
                "improvements": improvements,
            }

            # Print summary
            print(
                f"   📊 Optimization score: {performance_report['optimization_score']}/100"
            )
            print(
                f"   🔍 Recommendations: {len(performance_report['recommendations'])}"
            )

            if performance_report["recommendations"]:
                print("   💡 Key recommendations:")
                for rec in performance_report["recommendations"][:3]:
                    print(f"      - {rec['category']}: {rec['message']}")

            print("✅ Phase 5 completed: Performance validation")
            return True

        except Exception as e:
            print(f"❌ Phase 5 failed: {e}")
            self.deployment_results["phases"]["phase_5"] = {
                "status": "failed",
                "error": str(e),
            }
            return False

    async def generate_deployment_report(self):
        """Generate comprehensive deployment report."""
        print("\n📋 Generating Deployment Report")

        # Calculate overall success
        completed_phases = sum(
            1
            for phase in self.deployment_results["phases"].values()
            if phase.get("status") == "completed"
        )
        total_phases = len(self.deployment_results["phases"])

        success_rate = (
            (completed_phases / total_phases * 100) if total_phases > 0 else 0
        )

        self.deployment_results["overall_status"] = (
            "success"
            if success_rate >= 80
            else "partial" if success_rate >= 60 else "failed"
        )
        self.deployment_results["success_rate"] = success_rate

        # Save report
        report_path = project_root / "logs" / "database_optimization_report.json"
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(self.deployment_results, f, indent=2, default=str)

        print(f"   📄 Report saved to: {report_path}")
        print(f"   📊 Overall success rate: {success_rate:.1f}%")
        print(f"   ✅ Completed phases: {completed_phases}/{total_phases}")

        return self.deployment_results

    async def deploy_optimizations(self):
        """Deploy all database optimizations."""
        print("🚀 Starting ACGS-1 Database Performance Optimization Deployment")
        print("=" * 70)

        start_time = time.time()

        # Initialize
        if not await self.initialize():
            return False

        # Execute phases
        phases = [
            self.phase_1_baseline_analysis,
            self.phase_2_index_optimization,
            self.phase_3_connection_optimization,
            self.phase_4_maintenance_operations,
            self.phase_5_performance_validation,
        ]

        for i, phase in enumerate(phases, 1):
            print(f"\n⏳ Executing Phase {i}/{len(phases)}...")
            success = await phase()
            if not success:
                print(f"⚠️  Phase {i} failed, continuing with remaining phases...")

        # Generate final report
        await self.generate_deployment_report()

        duration = time.time() - start_time
        print(
            f"\n🎉 Database optimization deployment completed in {duration:.2f} seconds"
        )

        # Print final summary
        overall_status = self.deployment_results["overall_status"]
        if overall_status == "success":
            print("✅ Deployment successful - Database optimizations applied")
        elif overall_status == "partial":
            print("⚠️  Deployment partially successful - Some optimizations applied")
        else:
            print("❌ Deployment failed - Manual intervention required")

        return overall_status in ["success", "partial"]


async def main():
    """Main deployment function."""
    deployer = DatabaseOptimizationDeployer()
    success = await deployer.deploy_optimizations()
    return 0 if success else 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
