"""
Optimized SQLAlchemy Configuration for ACGS
Constitutional hash: cdd01ef066bc6cf2

High-performance database configuration with:
- Proper indexes for hot queries
- selectinload for N+1 prevention
- Async connection pooling
- Query optimization patterns
"""

from typing import Any

import structlog
from sqlalchemy import func, select, text
from sqlalchemy.engine.events import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import joinedload, selectinload
from sqlalchemy.pool import QueuePool

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = structlog.get_logger()


class OptimizedDatabaseConfig:
    """Optimized database configuration with performance tuning."""

    def __init__(
        self,
        database_url: str,
        pool_size: int = 20,
        max_overflow: int = 0,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False,
    ):
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.echo = echo
        self.constitutional_hash = CONSTITUTIONAL_HASH

        self.engine = None
        self.session_factory = None

    async def initialize(self):
        """Initialize optimized async engine and session factory."""

        # Create optimized async engine
        self.engine = create_async_engine(
            self.database_url,
            # Connection pooling optimization
            poolclass=QueuePool,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
            pool_timeout=self.pool_timeout,
            pool_recycle=self.pool_recycle,
            pool_pre_ping=True,
            # Performance settings
            connect_args={
                "command_timeout": 60,
                "server_settings": {
                    "jit": "off",  # Disable JIT for consistent performance
                    "application_name": f"acgs_optimized_{CONSTITUTIONAL_HASH}",
                },
            },
            # Echo for debugging (disable in production)
            echo=self.echo,
            echo_pool=self.echo,
            # Async settings
            future=True,
            # Query optimization
            execution_options={
                "isolation_level": "READ_COMMITTED",
                "autocommit": False,
            },
        )

        # Setup connection event handlers
        self._setup_connection_handlers()

        # Create optimized session factory
        self.session_factory = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,  # Manual flush for better control
            autocommit=False,
        )

        logger.info(
            "Database engine initialized",
            constitutional_hash=self.constitutional_hash,
            pool_size=self.pool_size,
            max_overflow=self.max_overflow,
        )

    def _setup_connection_handlers(self):
        """Setup connection event handlers for optimization."""

        @event.listens_for(self.engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set PostgreSQL connection optimizations."""
            if "postgresql" in self.database_url:
                cursor = dbapi_connection.cursor()
                # Optimize PostgreSQL settings
                cursor.execute("SET statement_timeout = '60s'")
                cursor.execute("SET lock_timeout = '30s'")
                cursor.execute("SET idle_in_transaction_session_timeout = '60s'")
                cursor.close()

        @event.listens_for(self.engine.sync_engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log connection checkout for monitoring."""
            logger.debug(
                "Database connection checked out",
                constitutional_hash=self.constitutional_hash,
            )

    async def get_session(self) -> AsyncSession:
        """Get optimized async session."""
        if not self.session_factory:
            await self.initialize()
        return self.session_factory()

    async def close(self):
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            logger.info(
                "Database engine disposed", constitutional_hash=self.constitutional_hash
            )


class OptimizedQueryPatterns:
    """Optimized query patterns with selectinload and proper indexing."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self.constitutional_hash = CONSTITUTIONAL_HASH

    async def get_with_selectinload(self, model_class, entity_id: Any, *relationships):
        """Get entity with optimized selectinload for relationships."""

        query = select(model_class).where(model_class.id == entity_id)

        # Apply selectinload for each relationship
        for relationship in relationships:
            query = query.options(selectinload(relationship))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_multiple_with_selectinload(
        self, model_class, entity_ids: list[Any], *relationships
    ):
        """Get multiple entities with selectinload optimization."""

        query = select(model_class).where(model_class.id.in_(entity_ids))

        # Apply selectinload for relationships
        for relationship in relationships:
            query = query.options(selectinload(relationship))

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_with_joinedload(self, model_class, entity_id: Any, *relationships):
        """Get entity with joinedload for one-to-one relationships."""

        query = select(model_class).where(model_class.id == entity_id)

        # Apply joinedload for one-to-one relationships
        for relationship in relationships:
            query = query.options(joinedload(relationship))

        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def paginated_query_with_count(
        self,
        model_class,
        filters: dict[str, Any] | None = None,
        page: int = 1,
        page_size: int = 100,
        order_by=None,
    ):
        """Optimized paginated query with efficient count."""

        # Base query
        query = select(model_class)
        count_query = select(func.count(model_class.id))

        # Apply filters
        if filters:
            for field, value in filters.items():
                if hasattr(model_class, field):
                    column = getattr(model_class, field)
                    query = query.where(column == value)
                    count_query = count_query.where(column == value)

        # Get total count
        count_result = await self.session.execute(count_query)
        total_count = count_result.scalar()

        # Apply ordering
        if order_by:
            query = query.order_by(order_by)

        # Apply pagination
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)

        # Execute query
        result = await self.session.execute(query)
        items = result.scalars().all()

        return {
            "items": items,
            "total_count": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": (total_count + page_size - 1) // page_size,
        }

    async def bulk_upsert(
        self, model_class, data_list: list[dict[str, Any]], conflict_columns: list[str]
    ):
        """Optimized bulk upsert using PostgreSQL ON CONFLICT."""

        if not data_list:
            return []

        # Build the bulk insert with ON CONFLICT
        stmt = f"""
        INSERT INTO {model_class.__tablename__}
        ({', '.join(data_list[0].keys())})
        VALUES {', '.join([f"({', '.join([f":{key}_{i}" for key in data.keys()])})"
                          for i, data in enumerate(data_list)])}
        ON CONFLICT ({', '.join(conflict_columns)})
        DO UPDATE SET
        {', '.join([f"{key} = EXCLUDED.{key}" for key in data_list[0].keys()
                   if key not in conflict_columns])},
        updated_at = NOW()
        RETURNING *
        """

        # Flatten parameters
        params = {}
        for i, data in enumerate(data_list):
            for key, value in data.items():
                params[f"{key}_{i}"] = value

        result = await self.session.execute(text(stmt), params)
        await self.session.commit()

        return result.fetchall()

    async def efficient_exists_check(
        self, model_class, filters: dict[str, Any]
    ) -> bool:
        """Efficient exists check using EXISTS clause."""

        exists_query = select(1).select_from(model_class)

        for field, value in filters.items():
            if hasattr(model_class, field):
                column = getattr(model_class, field)
                exists_query = exists_query.where(column == value)

        exists_query = select(exists_query.exists())

        result = await self.session.execute(exists_query)
        return result.scalar()


class IndexOptimizationManager:
    """Database index optimization manager."""

    def __init__(self, engine):
        self.engine = engine
        self.constitutional_hash = CONSTITUTIONAL_HASH

    async def create_performance_indexes(self):
        """Create optimized indexes for hot queries."""

        indexes_sql = [
            # Constitutional hash index
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_constitutional_hash
            ON constitutional_entities (constitutional_hash)
            WHERE constitutional_hash = %s
            """,
            # Composite indexes for common query patterns
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_service_status_timestamp
            ON service_metrics (service_name, status, created_at DESC)
            """,
            # Partial indexes for active records
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_active_policies
            ON policies (id, name, version)
            WHERE status = 'active'
            """,
            # JSON path indexes for constitutional data
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_policy_metadata_hash
            ON policies USING GIN ((metadata->>'constitutional_hash'))
            """,
            # Timeline queries optimization
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_audit_timeline
            ON audit_logs (entity_type, entity_id, created_at DESC)
            """,
            # Performance metrics indexes
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_metrics_service_time
            ON performance_metrics (service_name, metric_type, timestamp DESC)
            """,
            # Full-text search optimization
            """
            CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_policies_search
            ON policies USING GIN (to_tsvector('english', name || ' ' || description))
            """,
        ]

        async with self.engine.begin() as conn:
            for index_sql in indexes_sql:
                try:
                    await conn.execute(text(index_sql), [self.constitutional_hash])
                    logger.info(
                        "Index created successfully",
                        constitutional_hash=self.constitutional_hash,
                    )
                except Exception as e:
                    logger.warning(
                        "Index creation skipped",
                        error=str(e),
                        constitutional_hash=self.constitutional_hash,
                    )

    async def analyze_query_performance(self, query: str, params: dict = None):
        """Analyze query performance with EXPLAIN ANALYZE."""

        explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) {query}"

        async with self.engine.begin() as conn:
            result = await conn.execute(text(explain_query), params or {})
            explain_result = result.fetchone()[0]

            execution_time = explain_result[0]["Execution Time"]
            planning_time = explain_result[0]["Planning Time"]

            logger.info(
                "Query performance analysis",
                execution_time=execution_time,
                planning_time=planning_time,
                constitutional_hash=self.constitutional_hash,
            )

            return {
                "execution_time": execution_time,
                "planning_time": planning_time,
                "plan": explain_result[0]["Plan"],
            }


# Connection pooling utilities
class ConnectionPoolMonitor:
    """Monitor and optimize connection pool performance."""

    def __init__(self, engine):
        self.engine = engine
        self.constitutional_hash = CONSTITUTIONAL_HASH

    def get_pool_status(self) -> dict[str, Any]:
        """Get current connection pool status."""

        pool = self.engine.pool

        return {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "invalid": pool.invalid(),
            "constitutional_hash": self.constitutional_hash,
        }

    async def warm_up_pool(self, target_connections: int = 10):
        """Warm up connection pool with target connections."""

        connections = []
        try:
            for _ in range(target_connections):
                conn = await self.engine.connect()
                connections.append(conn)

            logger.info(
                "Connection pool warmed up",
                target_connections=target_connections,
                constitutional_hash=self.constitutional_hash,
            )

        finally:
            # Close all warming connections
            for conn in connections:
                await conn.close()


# Factory function
async def create_optimized_database(
    database_url: str, **kwargs
) -> OptimizedDatabaseConfig:
    """Factory function to create optimized database configuration."""

    config = OptimizedDatabaseConfig(database_url, **kwargs)
    await config.initialize()

    # Create performance indexes
    index_manager = IndexOptimizationManager(config.engine)
    await index_manager.create_performance_indexes()

    # Warm up connection pool
    pool_monitor = ConnectionPoolMonitor(config.engine)
    await pool_monitor.warm_up_pool()

    logger.info(
        "Optimized database configuration created",
        constitutional_hash=CONSTITUTIONAL_HASH,
    )

    return config


if __name__ == "__main__":
    print("🔧 ACGS Database Optimization Configuration")
    print(f"📋 Constitutional Hash: {CONSTITUTIONAL_HASH}")
    print("=" * 60)
    print("Features:")
    print("- Async connection pooling")
    print("- Optimized indexes for hot queries")
    print("- selectinload for N+1 prevention")
    print("- Bulk operations support")
    print("- Query performance monitoring")
