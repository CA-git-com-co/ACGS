#!/usr/bin/env python3
"""
ACGS-1 Database Performance Analysis and Optimization
Comprehensive analysis of PostgreSQL performance with optimization recommendations
"""

import asyncio
import json
import logging
import subprocess
from datetime import datetime
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabasePerformanceAnalyzer:
    """Comprehensive database performance analyzer for ACGS-1."""

    def __init__(self):
        self.db_container = "acgs_postgres_db"
        self.db_user = "acgs_user"
        self.db_name = "acgs_pgp_db"
        self.analysis_results = {}

    def execute_db_query(self, query: str) -> Optional[str]:
        """Execute a database query and return results."""
        try:
            cmd = [
                "docker",
                "exec",
                self.db_container,
                "psql",
                "-U",
                self.db_user,
                "-d",
                self.db_name,
                "-t",
                "-c",
                query,
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.warning(f"Query failed: {result.stderr}")
                return None
        except Exception as e:
            logger.error(f"Database query error: {e}")
            return None

    def analyze_database_size_and_structure(self) -> Dict[str, Any]:
        """Analyze database size and table structure."""
        logger.info("📊 Analyzing database size and structure...")

        # Database size
        db_size_query = """
        SELECT pg_size_pretty(pg_database_size(current_database())) as database_size;
        """
        db_size = self.execute_db_query(db_size_query)

        # Table count and sizes
        table_sizes_query = """
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
            pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
        FROM pg_tables 
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
        LIMIT 10;
        """
        table_sizes = self.execute_db_query(table_sizes_query)

        # Index usage statistics
        index_usage_query = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_scan,
            idx_tup_read,
            idx_tup_fetch
        FROM pg_stat_user_indexes
        ORDER BY idx_scan DESC
        LIMIT 10;
        """
        index_usage = self.execute_db_query(index_usage_query)

        return {
            "database_size": db_size,
            "table_sizes": table_sizes,
            "index_usage": index_usage,
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def analyze_query_performance(self) -> Dict[str, Any]:
        """Analyze query performance using pg_stat_statements."""
        logger.info("⚡ Analyzing query performance...")

        # Check if pg_stat_statements is available
        extension_check = self.execute_db_query(
            "SELECT 1 FROM pg_extension WHERE extname = 'pg_stat_statements';"
        )

        if not extension_check:
            logger.warning("pg_stat_statements extension not available")
            return {"error": "pg_stat_statements not available"}

        # Top slow queries
        slow_queries_query = """
        SELECT 
            query,
            calls,
            total_time,
            mean_time,
            rows,
            100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
        FROM pg_stat_statements
        WHERE calls > 10
        ORDER BY mean_time DESC
        LIMIT 10;
        """
        slow_queries = self.execute_db_query(slow_queries_query)

        # Most called queries
        frequent_queries_query = """
        SELECT 
            query,
            calls,
            total_time,
            mean_time,
            rows
        FROM pg_stat_statements
        ORDER BY calls DESC
        LIMIT 10;
        """
        frequent_queries = self.execute_db_query(frequent_queries_query)

        # Query statistics summary
        query_stats_query = """
        SELECT 
            COUNT(*) as total_queries,
            SUM(calls) as total_calls,
            AVG(mean_time) as avg_mean_time,
            MAX(mean_time) as max_mean_time,
            MIN(mean_time) as min_mean_time
        FROM pg_stat_statements;
        """
        query_stats = self.execute_db_query(query_stats_query)

        return {
            "slow_queries": slow_queries,
            "frequent_queries": frequent_queries,
            "query_statistics": query_stats,
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def analyze_connection_and_activity(self) -> Dict[str, Any]:
        """Analyze database connections and activity."""
        logger.info("🔗 Analyzing connections and activity...")

        # Current connections
        connections_query = """
        SELECT 
            state,
            COUNT(*) as connection_count
        FROM pg_stat_activity
        WHERE pid <> pg_backend_pid()
        GROUP BY state;
        """
        connections = self.execute_db_query(connections_query)

        # Long running queries
        long_queries_query = """
        SELECT 
            pid,
            now() - pg_stat_activity.query_start AS duration,
            query,
            state
        FROM pg_stat_activity
        WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
        AND state = 'active';
        """
        long_queries = self.execute_db_query(long_queries_query)

        # Database activity statistics
        activity_stats_query = """
        SELECT 
            numbackends,
            xact_commit,
            xact_rollback,
            blks_read,
            blks_hit,
            tup_returned,
            tup_fetched,
            tup_inserted,
            tup_updated,
            tup_deleted
        FROM pg_stat_database
        WHERE datname = current_database();
        """
        activity_stats = self.execute_db_query(activity_stats_query)

        return {
            "connections": connections,
            "long_running_queries": long_queries,
            "activity_statistics": activity_stats,
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def analyze_cache_performance(self) -> Dict[str, Any]:
        """Analyze database cache performance."""
        logger.info("💾 Analyzing cache performance...")

        # Buffer cache hit ratio
        cache_hit_query = """
        SELECT 
            'Buffer Cache Hit Ratio' as metric,
            ROUND(
                100.0 * sum(blks_hit) / (sum(blks_hit) + sum(blks_read)), 2
            ) as percentage
        FROM pg_stat_database
        WHERE blks_read > 0;
        """
        cache_hit_ratio = self.execute_db_query(cache_hit_query)

        # Table cache statistics
        table_cache_query = """
        SELECT 
            schemaname,
            tablename,
            heap_blks_read,
            heap_blks_hit,
            CASE 
                WHEN heap_blks_hit + heap_blks_read = 0 THEN 0
                ELSE ROUND(100.0 * heap_blks_hit / (heap_blks_hit + heap_blks_read), 2)
            END as cache_hit_ratio
        FROM pg_statio_user_tables
        WHERE heap_blks_read + heap_blks_hit > 0
        ORDER BY cache_hit_ratio ASC
        LIMIT 10;
        """
        table_cache = self.execute_db_query(table_cache_query)

        # Index cache statistics
        index_cache_query = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_blks_read,
            idx_blks_hit,
            CASE 
                WHEN idx_blks_hit + idx_blks_read = 0 THEN 0
                ELSE ROUND(100.0 * idx_blks_hit / (idx_blks_hit + idx_blks_read), 2)
            END as cache_hit_ratio
        FROM pg_statio_user_indexes
        WHERE idx_blks_read + idx_blks_hit > 0
        ORDER BY cache_hit_ratio ASC
        LIMIT 10;
        """
        index_cache = self.execute_db_query(index_cache_query)

        return {
            "buffer_cache_hit_ratio": cache_hit_ratio,
            "table_cache_performance": table_cache,
            "index_cache_performance": index_cache,
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def analyze_locks_and_blocking(self) -> Dict[str, Any]:
        """Analyze database locks and blocking queries."""
        logger.info("🔒 Analyzing locks and blocking...")

        # Current locks
        locks_query = """
        SELECT 
            mode,
            COUNT(*) as lock_count
        FROM pg_locks
        GROUP BY mode
        ORDER BY lock_count DESC;
        """
        locks = self.execute_db_query(locks_query)

        # Blocking queries
        blocking_query = """
        SELECT 
            blocked_locks.pid AS blocked_pid,
            blocked_activity.usename AS blocked_user,
            blocking_locks.pid AS blocking_pid,
            blocking_activity.usename AS blocking_user,
            blocked_activity.query AS blocked_statement,
            blocking_activity.query AS current_statement_in_blocking_process
        FROM pg_catalog.pg_locks blocked_locks
        JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
        JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
            AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
            AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
            AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
            AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
            AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
            AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
            AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
            AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
            AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
            AND blocking_locks.pid != blocked_locks.pid
        JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
        WHERE NOT blocked_locks.granted;
        """
        blocking = self.execute_db_query(blocking_query)

        return {
            "current_locks": locks,
            "blocking_queries": blocking,
            "analysis_timestamp": datetime.now().isoformat(),
        }

    def generate_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Generate optimization recommendations based on analysis."""
        logger.info("💡 Generating optimization recommendations...")

        recommendations = []

        # Analyze cache hit ratio
        cache_analysis = self.analysis_results.get("cache_performance", {})
        cache_hit_ratio = cache_analysis.get("buffer_cache_hit_ratio", "")

        if cache_hit_ratio and "%" in str(cache_hit_ratio):
            try:
                ratio = float(cache_hit_ratio.split()[-1].replace("%", ""))
                if ratio < 95:
                    recommendations.append(
                        {
                            "category": "memory",
                            "priority": "high",
                            "title": "Increase Shared Buffers",
                            "description": f"Cache hit ratio is {ratio}%. Consider increasing shared_buffers.",
                            "action": "ALTER SYSTEM SET shared_buffers = '1GB';",
                        }
                    )
            except:
                pass

        # Check for slow queries
        query_analysis = self.analysis_results.get("query_performance", {})
        if query_analysis.get("query_statistics"):
            recommendations.append(
                {
                    "category": "performance",
                    "priority": "medium",
                    "title": "Query Optimization",
                    "description": "Review slow queries and consider adding indexes or rewriting queries.",
                    "action": "Analyze EXPLAIN plans for slow queries",
                }
            )

        # Connection optimization
        connection_analysis = self.analysis_results.get("connection_activity", {})
        if connection_analysis.get("connections"):
            recommendations.append(
                {
                    "category": "connections",
                    "priority": "medium",
                    "title": "Connection Pool Optimization",
                    "description": "Monitor connection usage and optimize pool settings.",
                    "action": "Review connection pool configuration",
                }
            )

        # General maintenance recommendations
        recommendations.extend(
            [
                {
                    "category": "maintenance",
                    "priority": "low",
                    "title": "Regular VACUUM and ANALYZE",
                    "description": "Schedule regular maintenance operations.",
                    "action": "Set up automated VACUUM and ANALYZE jobs",
                },
                {
                    "category": "monitoring",
                    "priority": "medium",
                    "title": "Performance Monitoring",
                    "description": "Implement continuous performance monitoring.",
                    "action": "Set up Prometheus metrics and Grafana dashboards",
                },
            ]
        )

        return recommendations

    async def run_comprehensive_analysis(self):
        """Run comprehensive database performance analysis."""
        logger.info("🚀 Starting comprehensive database performance analysis")

        try:
            # Run all analyses
            self.analysis_results["database_structure"] = self.analyze_database_size_and_structure()
            self.analysis_results["query_performance"] = self.analyze_query_performance()
            self.analysis_results["connection_activity"] = self.analyze_connection_and_activity()
            self.analysis_results["cache_performance"] = self.analyze_cache_performance()
            self.analysis_results["locks_blocking"] = self.analyze_locks_and_blocking()

            # Generate recommendations
            self.analysis_results["recommendations"] = self.generate_optimization_recommendations()

            # Add summary
            self.analysis_results["analysis_summary"] = {
                "timestamp": datetime.now().isoformat(),
                "database": self.db_name,
                "container": self.db_container,
                "analyses_completed": len(
                    [k for k in self.analysis_results.keys() if k != "analysis_summary"]
                ),
                "recommendations_count": len(self.analysis_results.get("recommendations", [])),
            }

        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            self.analysis_results["error"] = str(e)

    def print_results(self):
        """Print formatted analysis results."""
        print("\n" + "=" * 80)
        print("📊 ACGS-1 DATABASE PERFORMANCE ANALYSIS RESULTS")
        print("=" * 80)

        summary = self.analysis_results.get("analysis_summary", {})
        print(f"\n📋 Analysis Summary:")
        print(f"Database: {summary.get('database', 'unknown')}")
        print(f"Analyses Completed: {summary.get('analyses_completed', 0)}")
        print(f"Recommendations: {summary.get('recommendations_count', 0)}")
        print(f"Timestamp: {summary.get('timestamp', 'unknown')}")

        # Database structure
        structure = self.analysis_results.get("database_structure", {})
        if structure.get("database_size"):
            print(f"\n💾 Database Size: {structure['database_size']}")

        # Cache performance
        cache = self.analysis_results.get("cache_performance", {})
        if cache.get("buffer_cache_hit_ratio"):
            print(f"📈 Buffer Cache Hit Ratio: {cache['buffer_cache_hit_ratio']}")

        # Recommendations
        recommendations = self.analysis_results.get("recommendations", [])
        if recommendations:
            print(f"\n💡 Top Recommendations:")
            print("-" * 50)
            for i, rec in enumerate(recommendations[:5], 1):
                priority_icon = (
                    "🔴"
                    if rec["priority"] == "high"
                    else "🟡" if rec["priority"] == "medium" else "🟢"
                )
                print(f"{i}. {priority_icon} {rec['title']} ({rec['category']})")
                print(f"   {rec['description']}")

        # Performance assessment
        if cache.get("buffer_cache_hit_ratio") and "%" in str(cache["buffer_cache_hit_ratio"]):
            try:
                ratio = float(str(cache["buffer_cache_hit_ratio"]).split()[-1].replace("%", ""))
                if ratio >= 95:
                    print("\n🎉 EXCELLENT: Database cache performance is optimal!")
                elif ratio >= 90:
                    print("\n✅ GOOD: Database performance is solid")
                else:
                    print("\n⚠️  NEEDS OPTIMIZATION: Consider performance improvements")
            except:
                print("\n📊 Database analysis completed successfully")
        else:
            print("\n📊 Database analysis completed successfully")

    def save_results(self, filename: str = "database_performance_analysis.json"):
        """Save analysis results to file."""
        with open(filename, "w") as f:
            json.dump(self.analysis_results, f, indent=2, default=str)
        logger.info(f"Analysis results saved to {filename}")


async def main():
    """Main function to run database performance analysis."""
    analyzer = DatabasePerformanceAnalyzer()
    await analyzer.run_comprehensive_analysis()
    analyzer.print_results()
    analyzer.save_results()


if __name__ == "__main__":
    asyncio.run(main())
