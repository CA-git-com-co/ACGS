"""
Database Connection Pool Manager for ACGS-PGP Services

Provides optimized connection pooling to eliminate redundant database
connections and improve performance across all services.
"""

import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncGenerator, Dict, List, Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import QueuePool

from ..common.error_handling import DatabaseError

# Import DatabaseInterface with try/except to avoid circular imports
try:
    from ..di.interfaces import DatabaseInterface
except ImportError:
    # Define a minimal interface if DI module is not available
    class DatabaseInterface:
        async def connect(self):
            # requires: Valid input parameters
            # ensures: Correct function execution
            # sha256: func_hash
            pass

        async def disconnect(self):
            # requires: Valid input parameters
            # ensures: Correct function execution
            # sha256: func_hash
            pass

        async def execute_query(self, query, params=None):
            # requires: Valid input parameters
            # ensures: Correct function execution
            # sha256: func_hash
            pass

        async def execute_command(self, command, params=None):
            # requires: Valid input parameters
            # ensures: Correct function execution
            # sha256: func_hash
            pass

        async def begin_transaction(self):
            # requires: Valid input parameters
            # ensures: Correct function execution
            # sha256: func_hash
            pass

        async def health_check(self):
            # requires: Valid input parameters
            # ensures: Correct function execution
            # sha256: func_hash
            pass


logger = logging.getLogger(__name__)


@dataclass
class PoolConfig:
    """Enhanced database pool configuration for Phase 2 performance optimization."""

    # Phase 2 enhanced connection pool settings for >1000 concurrent users
    min_connections: int = 10  # Increased from 5 for better baseline performance
    max_connections: int = 30  # Increased from 20 for higher concurrency
    max_overflow: int = 20  # Increased from 10 for burst capacity
    pool_timeout: float = 20.0  # Reduced from 30.0 for faster failover
    pool_recycle: int = 1800  # Reduced from 3600 (30 minutes) for fresher connections
    pool_pre_ping: bool = True
    echo: bool = False
    echo_pool: bool = False

    # Phase 2 performance enhancements
    pool_reset_on_return: str = "commit"  # Reset connections on return
    pool_invalidate_on_disconnect: bool = True  # Invalidate on disconnect
    connect_timeout: int = 10  # Connection timeout in seconds
    query_timeout: int = 30  # Query timeout in seconds
    statement_timeout: int = 60000  # PostgreSQL statement timeout (ms)
    idle_in_transaction_session_timeout: int = 300000  # 5 minutes (ms)


@dataclass
class ConnectionMetrics:
    """Connection pool metrics."""

    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    checked_out_connections: int = 0
    overflow_connections: int = 0
    pool_hits: int = 0
    pool_misses: int = 0
    connection_errors: int = 0
    query_count: int = 0
    total_query_time: float = 0.0

    @property
    def average_query_time(self) -> float:
        """Calculate average query time."""
        return self.total_query_time / max(self.query_count, 1)

    @property
    def pool_utilization(self) -> float:
        """Calculate pool utilization percentage."""
        return (self.active_connections / max(self.total_connections, 1)) * 100


class ConnectionPool:
    """
    Database connection pool with monitoring and optimization.
    """

    def __init__(self, database_url: str, config: Optional[PoolConfig] = None):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Initialize connection pool.

        Args:
            database_url: Database connection URL
            config: Pool configuration
        """
        self.database_url = database_url
        self.config = config or PoolConfig()
        self.metrics = ConnectionMetrics()

        # Enhanced SQLAlchemy async engine for Phase 2 performance optimization
        self.engine = create_async_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=self.config.min_connections,
            max_overflow=self.config.max_overflow,
            pool_timeout=self.config.pool_timeout,
            pool_recycle=self.config.pool_recycle,
            pool_pre_ping=self.config.pool_pre_ping,
            pool_reset_on_return=self.config.pool_reset_on_return,
            pool_invalidate_on_disconnect=self.config.pool_invalidate_on_disconnect,
            echo=self.config.echo,
            echo_pool=self.config.echo_pool,
            # Enhanced connection arguments for performance
            connect_args={
                "server_settings": {
                    "application_name": "acgs_phase2_enhanced",
                    "jit": "off",  # Disable JIT for consistent performance
                    "statement_timeout": str(self.config.statement_timeout),
                    "idle_in_transaction_session_timeout": str(
                        self.config.idle_in_transaction_session_timeout
                    ),
                },
                "command_timeout": self.config.query_timeout,
            },
        )

        # Session factory
        self.session_factory = async_sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

        self._initialized = False

    async def initialize(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize the connection pool."""
        if self._initialized:
            return

        try:
            # Test connection
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))

            self._initialized = True
            logger.info(f"Database pool initialized: {self.database_url}")

        except Exception as e:
            raise DatabaseError(
                f"Failed to initialize database pool: {str(e)}",
                operation="initialize_pool",
            )

    async def close(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Close the connection pool."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database pool closed")

    @asynccontextmanager
    async def get_connection(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Get a database connection from the pool.

        Yields:
            Database connection
        """
        start_time = time.time()
        connection = None

        try:
            async with self.engine.begin() as connection:
                self.metrics.active_connections += 1
                self.metrics.pool_hits += 1
                yield connection

        except Exception as e:
            self.metrics.connection_errors += 1
            raise DatabaseError(f"Database connection error: {str(e)}", operation="get_connection")

        finally:
            if connection:
                self.metrics.active_connections -= 1

            # Update timing metrics
            query_time = time.time() - start_time
            self.metrics.query_count += 1
            self.metrics.total_query_time += query_time

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Get a database session from the pool.

        Yields:
            Database session
        """
        start_time = time.time()
        session = None

        try:
            session = self.session_factory()
            self.metrics.active_connections += 1
            self.metrics.pool_hits += 1
            yield session
            await session.commit()

        except Exception as e:
            if session:
                await session.rollback()
            self.metrics.connection_errors += 1
            raise DatabaseError(f"Database session error: {str(e)}", operation="get_session")

        finally:
            if session:
                await session.close()
                self.metrics.active_connections -= 1

            # Update timing metrics
            query_time = time.time() - start_time
            self.metrics.query_count += 1
            self.metrics.total_query_time += query_time

    async def execute_query(
        self, query: str, params: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a query and return results.

        Args:
            query: SQL query to execute
            params: Query parameters

        Returns:
            Query results as list of dictionaries
        """
        async with self.get_connection() as conn:
            result = await conn.execute(text(query), params or {})
            return [dict(row) for row in result.fetchall()]

    async def execute_command(self, command: str, params: Dict[str, Any] = None) -> int:
        """
        Execute a command and return affected rows.

        Args:
            command: SQL command to execute
            params: Command parameters

        Returns:
            Number of affected rows
        """
        async with self.get_connection() as conn:
            result = await conn.execute(text(command), params or {})
            return result.rowcount

    def get_metrics(self) -> Dict[str, Any]:
        """Get connection pool metrics."""
        pool = self.engine.pool

        # Update pool metrics
        self.metrics.total_connections = pool.size()
        self.metrics.checked_out_connections = pool.checkedout()
        self.metrics.overflow_connections = pool.overflow()
        self.metrics.idle_connections = pool.checkedin()

        return {
            "total_connections": self.metrics.total_connections,
            "active_connections": self.metrics.active_connections,
            "idle_connections": self.metrics.idle_connections,
            "checked_out_connections": self.metrics.checked_out_connections,
            "overflow_connections": self.metrics.overflow_connections,
            "pool_utilization": self.metrics.pool_utilization,
            "pool_hits": self.metrics.pool_hits,
            "pool_misses": self.metrics.pool_misses,
            "connection_errors": self.metrics.connection_errors,
            "query_count": self.metrics.query_count,
            "total_query_time": self.metrics.total_query_time,
            "average_query_time": self.metrics.average_query_time,
        }

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on the connection pool."""
        try:
            start_time = time.time()

            async with self.get_connection() as conn:
                await conn.execute(text("SELECT 1"))

            response_time = time.time() - start_time

            return {
                "status": "healthy",
                "response_time": response_time,
                "metrics": self.get_metrics(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "metrics": self.get_metrics(),
            }


class DatabasePoolManager:
    """
    Manager for multiple database connection pools.

    Provides centralized management of database connections across
    all ACGS services with optimization and monitoring.
    """

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize the pool manager."""
        self.pools: Dict[str, ConnectionPool] = {}
        self.default_config = PoolConfig()

    def register_pool(
        self, name: str, database_url: str, config: PoolConfig = None
    ) -> ConnectionPool:
        """
        Register a new database pool.

        Args:
            name: Pool name/identifier
            database_url: Database connection URL
            config: Pool configuration

        Returns:
            Created connection pool
        """
        if name in self.pools:
            logger.warning(f"Overriding existing pool: {name}")

        pool = ConnectionPool(database_url, config or self.default_config)
        self.pools[name] = pool

        logger.info(f"Registered database pool: {name}")
        return pool

    def get_pool(self, name: str) -> Optional[ConnectionPool]:
        """
        Get a database pool by name.

        Args:
            name: Pool name

        Returns:
            Connection pool or None if not found
        """
        return self.pools.get(name)

    async def initialize_all(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize all registered pools."""
        for name, pool in self.pools.items():
            try:
                await pool.initialize()
                logger.info(f"Initialized pool: {name}")
            except Exception as e:
                logger.error(f"Failed to initialize pool {name}: {e}")
                raise

    async def close_all(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Close all registered pools."""
        for name, pool in self.pools.items():
            try:
                await pool.close()
                logger.info(f"Closed pool: {name}")
            except Exception as e:
                logger.error(f"Error closing pool {name}: {e}")

        self.pools.clear()

    @asynccontextmanager
    async def get_connection(self, pool_name: str = "default"):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """
        Get a connection from a specific pool.

        Args:
            pool_name: Name of the pool to get connection from

        Yields:
            Database connection
        """
        pool = self.get_pool(pool_name)
        if not pool:
            raise DatabaseError(
                f"Database pool '{pool_name}' not found", operation="get_connection"
            )

        async with pool.get_connection() as conn:
            yield conn

    @asynccontextmanager
    async def get_session(self, pool_name: str = "default") -> AsyncGenerator[AsyncSession, None]:
        """
        Get a session from a specific pool.

        Args:
            pool_name: Name of the pool to get session from

        Yields:
            Database session
        """
        pool = self.get_pool(pool_name)
        if not pool:
            raise DatabaseError(f"Database pool '{pool_name}' not found", operation="get_session")

        async with pool.get_session() as session:
            yield session

    async def execute_query(
        self, query: str, params: Dict[str, Any] = None, pool_name: str = "default"
    ) -> List[Dict[str, Any]]:
        """
        Execute a query on a specific pool.

        Args:
            query: SQL query to execute
            params: Query parameters
            pool_name: Pool to execute on

        Returns:
            Query results
        """
        pool = self.get_pool(pool_name)
        if not pool:
            raise DatabaseError(f"Database pool '{pool_name}' not found", operation="execute_query")

        return await pool.execute_query(query, params)

    async def execute_command(
        self, command: str, params: Dict[str, Any] = None, pool_name: str = "default"
    ) -> int:
        """
        Execute a command on a specific pool.

        Args:
            command: SQL command to execute
            params: Command parameters
            pool_name: Pool to execute on

        Returns:
            Number of affected rows
        """
        pool = self.get_pool(pool_name)
        if not pool:
            raise DatabaseError(
                f"Database pool '{pool_name}' not found", operation="execute_command"
            )

        return await pool.execute_command(command, params)

    def get_all_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Get metrics from all pools."""
        return {name: pool.get_metrics() for name, pool in self.pools.items()}

    async def health_check_all(self) -> Dict[str, Dict[str, Any]]:
        """Perform health check on all pools."""
        results = {}

        for name, pool in self.pools.items():
            results[name] = await pool.health_check()

        return results


# Global pool manager instance
_pool_manager: Optional[DatabasePoolManager] = None


def get_pool_manager() -> DatabasePoolManager:
    """
    Get the global database pool manager.

    Returns:
        Database pool manager instance
    """
    global _pool_manager

    if _pool_manager is None:
        _pool_manager = DatabasePoolManager()

    return _pool_manager
