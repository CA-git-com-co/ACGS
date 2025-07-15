#!/usr/bin/env python3
"""
Database Query Optimization for ACGS-2
Implements query optimization strategies and indexing.
"""

import asyncio
import logging

import asyncpg

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = logging.getLogger(__name__)


class DatabaseQueryOptimizer:
    """Optimizes database queries and implements performance improvements."""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection_pool = None

    async def initialize_pool(self):
        """Initialize database connection pool."""
        self.connection_pool = await asyncpg.create_pool(
            self.database_url, min_size=10, max_size=20, command_timeout=60
        )

    async def create_performance_indexes(self):
        """Create performance-optimized indexes."""
        indexes = [
            # Constitutional AI indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_user_id ON conversations(user_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_created_at ON conversations(created_at)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_status ON conversations(status)",
            # Policy Governance indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_policies_status ON policies(status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_policies_created_at ON policies(created_at)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_policy_evaluations_policy_id ON policy_evaluations(policy_id)",
            # Governance Synthesis indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_synthesis_requests_status ON synthesis_requests(status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_synthesis_requests_created_at ON synthesis_requests(created_at)",
            # User and session indexes
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_expires_at ON sessions(expires_at)",
            # Composite indexes for common queries
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_user_status ON conversations(user_id, status)",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_policies_status_created ON policies(status, created_at)",
        ]

        async with self.connection_pool.acquire() as conn:
            for index_sql in indexes:
                try:
                    await conn.execute(index_sql)
                    logger.info(f"Created index: {index_sql.split()[-1]}")
                except Exception as e:
                    logger.warning(f"Index creation failed: {e}")

    async def optimize_table_statistics(self):
        """Update table statistics for query planner."""
        tables = [
            "conversations",
            "policies",
            "policy_evaluations",
            "synthesis_requests",
            "users",
            "sessions",
        ]

        async with self.connection_pool.acquire() as conn:
            for table in tables:
                try:
                    await conn.execute(f"ANALYZE {table}")
                    logger.info(f"Updated statistics for table: {table}")
                except Exception as e:
                    logger.warning(f"Statistics update failed for {table}: {e}")

    async def create_materialized_views(self):
        """Create materialized views for complex queries."""
        materialized_views = [
            """
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_user_activity_summary AS
            SELECT
                u.id as user_id,
                u.email,
                COUNT(DISTINCT c.id) as conversation_count,
                COUNT(DISTINCT p.id) as policy_count,
                MAX(c.created_at) as last_conversation,
                MAX(p.created_at) as last_policy
            FROM users u
            LEFT JOIN conversations c ON u.id = c.user_id
            LEFT JOIN policies p ON u.id = p.created_by
            GROUP BY u.id, u.email
            """,
            """
            CREATE MATERIALIZED VIEW IF NOT EXISTS mv_policy_performance_metrics AS
            SELECT
                p.id as policy_id,
                p.title,
                COUNT(pe.id) as evaluation_count,
                AVG(pe.compliance_score) as avg_compliance_score,
                MAX(pe.created_at) as last_evaluation
            FROM policies p
            LEFT JOIN policy_evaluations pe ON p.id = pe.policy_id
            GROUP BY p.id, p.title
            """,
        ]

        async with self.connection_pool.acquire() as conn:
            for view_sql in materialized_views:
                try:
                    await conn.execute(view_sql)
                    logger.info("Created materialized view")
                except Exception as e:
                    logger.warning(f"Materialized view creation failed: {e}")

    async def refresh_materialized_views(self):
        """Refresh materialized views."""
        views = ["mv_user_activity_summary", "mv_policy_performance_metrics"]

        async with self.connection_pool.acquire() as conn:
            for view in views:
                try:
                    await conn.execute(f"REFRESH MATERIALIZED VIEW CONCURRENTLY {view}")
                    logger.info(f"Refreshed materialized view: {view}")
                except Exception as e:
                    logger.warning(f"View refresh failed for {view}: {e}")


async def main():
    """Main database optimization function."""
    database_url = os.environ.get("DATABASE_URL")

    optimizer = DatabaseQueryOptimizer(database_url)
    await optimizer.initialize_pool()

    print("🗄️ Starting database optimization...")

    # Create performance indexes
    await optimizer.create_performance_indexes()

    # Update table statistics
    await optimizer.optimize_table_statistics()

    # Create materialized views
    await optimizer.create_materialized_views()

    print("✅ Database optimization completed")


if __name__ == "__main__":
    asyncio.run(main())
