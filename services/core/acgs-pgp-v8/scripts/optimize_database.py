#!/usr/bin/env python3
"""
Database Optimization Script for ACGS-PGP v8

Applies comprehensive database optimizations including connection pooling,
indexing, PostgreSQL settings, and performance monitoring setup.
"""

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from database.optimization import DatabaseOptimizer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('database_optimization.log')
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Main optimization function."""
    parser = argparse.ArgumentParser(description="Optimize ACGS-PGP v8 database")
    parser.add_argument(
        "--database-url",
        type=str,
        default=os.getenv("DATABASE_URL", "postgresql://acgs_user:acgs_password@localhost:5432/acgs_db"),
        help="Database connection URL"
    )
    parser.add_argument(
        "--slow-query-threshold",
        type=float,
        default=1.0,
        help="Slow query threshold in seconds"
    )
    parser.add_argument(
        "--operations",
        nargs="+",
        choices=["indexes", "settings", "statistics", "all"],
        default=["all"],
        help="Optimization operations to perform"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing"
    )
    
    args = parser.parse_args()
    
    logger.info("Starting ACGS-PGP v8 database optimization")
    logger.info(f"Database URL: {args.database_url}")
    logger.info(f"Operations: {args.operations}")
    logger.info(f"Dry run: {args.dry_run}")
    
    try:
        # Initialize optimizer
        optimizer = DatabaseOptimizer(
            database_url=args.database_url,
            slow_query_threshold=args.slow_query_threshold
        )
        
        # Determine operations to perform
        if "all" in args.operations:
            operations = ["indexes", "settings", "statistics"]
        else:
            operations = args.operations
        
        # Perform optimizations
        if "indexes" in operations:
            logger.info("🔍 Creating performance indexes...")
            if not args.dry_run:
                await optimizer.create_performance_indexes(args.database_url)
                logger.info("✅ Performance indexes created")
            else:
                logger.info("📋 Would create performance indexes")
        
        if "settings" in operations:
            logger.info("⚙️ Optimizing PostgreSQL settings...")
            if not args.dry_run:
                await optimizer.optimize_postgresql_settings(args.database_url)
                logger.info("✅ PostgreSQL settings optimized")
            else:
                logger.info("📋 Would optimize PostgreSQL settings")
        
        if "statistics" in operations:
            logger.info("📊 Updating table statistics...")
            if not args.dry_run:
                await optimizer.analyze_table_statistics(args.database_url)
                logger.info("✅ Table statistics updated")
            else:
                logger.info("📋 Would update table statistics")
        
        # Display optimization summary
        logger.info("📈 Database optimization completed successfully!")
        
        if not args.dry_run:
            # Show performance summary
            summary = optimizer.get_performance_summary()
            print_optimization_summary(summary)
        
        # Cleanup
        await optimizer.cleanup()
        
    except Exception as e:
        logger.error(f"Database optimization failed: {e}")
        sys.exit(1)


def print_optimization_summary(summary: dict):
    """Print optimization summary."""
    print("\n" + "="*60)
    print("ACGS-PGP v8 Database Optimization Summary")
    print("="*60)
    
    print(f"\n📊 Query Performance:")
    print(f"  Total Queries: {summary['total_queries']}")
    print(f"  Total Execution Time: {summary['total_execution_time']:.3f}s")
    print(f"  Average Query Time: {summary['average_query_time']:.3f}s")
    print(f"  Slow Queries: {summary['slow_query_count']} ({summary['slow_query_percentage']:.1f}%)")
    
    print(f"\n🔍 Query Types:")
    for qtype, count in summary['query_types'].items():
        print(f"  {qtype}: {count}")
    
    print(f"\n🔗 Connection Pools: {summary['pool_metrics_count']}")
    print(f"📅 Summary Generated: {summary['timestamp']}")
    
    print("\n" + "="*60)


async def test_database_performance():
    """Test database performance after optimization."""
    logger.info("🧪 Testing database performance...")
    
    try:
        import asyncpg
        import time
        
        database_url = os.getenv("DATABASE_URL", "postgresql://acgs_user:acgs_password@localhost:5432/acgs_db")
        
        # Test connection performance
        start_time = time.time()
        conn = await asyncpg.connect(database_url)
        connection_time = time.time() - start_time
        
        # Test simple query performance
        start_time = time.time()
        result = await conn.fetchval("SELECT 1")
        query_time = time.time() - start_time
        
        # Test complex query performance (if tables exist)
        try:
            start_time = time.time()
            count = await conn.fetchval("""
                SELECT COUNT(*) FROM policy_generations 
                WHERE created_at > NOW() - INTERVAL '1 day'
            """)
            complex_query_time = time.time() - start_time
        except Exception:
            complex_query_time = None
            count = None
        
        await conn.close()
        
        # Print performance results
        print(f"\n🚀 Performance Test Results:")
        print(f"  Connection Time: {connection_time*1000:.2f}ms")
        print(f"  Simple Query Time: {query_time*1000:.2f}ms")
        if complex_query_time is not None:
            print(f"  Complex Query Time: {complex_query_time*1000:.2f}ms")
            print(f"  Recent Policies: {count}")
        
        # Performance benchmarks
        if connection_time < 0.1:
            print("  ✅ Connection performance: Excellent")
        elif connection_time < 0.5:
            print("  ⚠️ Connection performance: Good")
        else:
            print("  ❌ Connection performance: Needs improvement")
        
        if query_time < 0.01:
            print("  ✅ Query performance: Excellent")
        elif query_time < 0.05:
            print("  ⚠️ Query performance: Good")
        else:
            print("  ❌ Query performance: Needs improvement")
        
    except Exception as e:
        logger.error(f"Performance test failed: {e}")


async def create_monitoring_views():
    """Create database monitoring views for ongoing performance tracking."""
    logger.info("📊 Creating monitoring views...")
    
    monitoring_views = [
        # Connection pool monitoring view
        """
        CREATE OR REPLACE VIEW v_connection_pool_stats AS
        SELECT 
            datname as database_name,
            numbackends as active_connections,
            xact_commit as transactions_committed,
            xact_rollback as transactions_rolled_back,
            blks_read as blocks_read,
            blks_hit as blocks_hit,
            CASE 
                WHEN blks_read + blks_hit > 0 
                THEN ROUND((blks_hit::float / (blks_read + blks_hit)) * 100, 2)
                ELSE 0 
            END as cache_hit_ratio
        FROM pg_stat_database 
        WHERE datname = current_database();
        """,
        
        # Query performance monitoring view
        """
        CREATE OR REPLACE VIEW v_query_performance AS
        SELECT 
            query,
            calls,
            total_time,
            mean_time,
            min_time,
            max_time,
            stddev_time,
            CASE 
                WHEN mean_time > 1000 THEN 'SLOW'
                WHEN mean_time > 100 THEN 'MODERATE'
                ELSE 'FAST'
            END as performance_category
        FROM pg_stat_statements 
        WHERE query NOT LIKE '%pg_stat_statements%'
        ORDER BY total_time DESC
        LIMIT 50;
        """,
        
        # Index usage monitoring view
        """
        CREATE OR REPLACE VIEW v_index_usage AS
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_scan as index_scans,
            idx_tup_read as tuples_read,
            idx_tup_fetch as tuples_fetched,
            CASE 
                WHEN idx_scan = 0 THEN 'UNUSED'
                WHEN idx_scan < 100 THEN 'LOW_USAGE'
                ELSE 'ACTIVE'
            END as usage_category
        FROM pg_stat_user_indexes
        ORDER BY idx_scan DESC;
        """,
        
        # Table statistics view
        """
        CREATE OR REPLACE VIEW v_table_stats AS
        SELECT 
            schemaname,
            tablename,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            n_live_tup as live_tuples,
            n_dead_tup as dead_tuples,
            CASE 
                WHEN n_live_tup > 0 
                THEN ROUND((n_dead_tup::float / n_live_tup) * 100, 2)
                ELSE 0 
            END as dead_tuple_ratio,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze
        FROM pg_stat_user_tables
        ORDER BY n_live_tup DESC;
        """
    ]
    
    try:
        import asyncpg
        database_url = os.getenv("DATABASE_URL", "postgresql://acgs_user:acgs_password@localhost:5432/acgs_db")
        
        conn = await asyncpg.connect(database_url)
        
        for view_sql in monitoring_views:
            try:
                await conn.execute(view_sql)
                logger.info("✅ Monitoring view created")
            except Exception as e:
                logger.warning(f"Failed to create monitoring view: {e}")
        
        await conn.close()
        logger.info("📊 Monitoring views setup completed")
        
    except Exception as e:
        logger.error(f"Failed to create monitoring views: {e}")


if __name__ == "__main__":
    # Check if we should run performance tests
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        asyncio.run(test_database_performance())
    elif len(sys.argv) > 1 and sys.argv[1] == "monitor":
        asyncio.run(create_monitoring_views())
    else:
        asyncio.run(main())
