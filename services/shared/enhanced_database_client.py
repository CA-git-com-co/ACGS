"""
ACGS-1 Enhanced Database Client with Resilience
Phase 2 - Enterprise Scalability & Performance

Production-ready database client with connection pooling, retry mechanisms,
circuit breakers, and comprehensive monitoring for >99.9% availability.
"""

import logging
import os
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Union

import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from infrastructure.database.read_replica_config import (
    ReadReplicaRouter,
    get_default_read_replica_config,
)

from .database_resilience import (
    get_resilience_manager,
)

logger = logging.getLogger(__name__)


class EnhancedDatabaseClient:
    """Enhanced database client with enterprise-grade resilience and performance."""

    def __init__(
        self,
        service_name: str,
        database_url: str = None,
        pool_size: int = 30,
        max_overflow: int = 20,
        pool_timeout: float = 20.0,
        pool_recycle: int = 1800,
    ):
        self.service_name = service_name
        self.database_url = database_url or self._get_database_url()

        # Pool configuration optimized for enterprise workload
        self.pool_config = {
            "pool_size": pool_size,
            "max_overflow": max_overflow,
            "pool_timeout": pool_timeout,
            "pool_recycle": pool_recycle,
            "pool_pre_ping": True,
            "poolclass": QueuePool,
        }

        # Initialize resilience manager
        self.resilience_manager = get_resilience_manager(service_name)

        # Initialize read replica router
        self.read_replica_config = get_default_read_replica_config()
        self.replica_router = ReadReplicaRouter(self.read_replica_config)

        # Database engines and sessions
        self._async_engine = None
        self._async_session_factory = None
        self._raw_connection_pool = None

        # Read replica connection pools
        self._read_replica_pools = {}

        logger.info(f"Enhanced database client initialized for {service_name}")

    def _get_database_url(self) -> str:
        """Get database URL with PgBouncer support."""
        # Check for PgBouncer configuration first
        if os.getenv("PGBOUNCER_ENABLED", "false").lower() == "true":
            host = os.getenv("PGBOUNCER_HOST", "localhost")
            port = os.getenv("PGBOUNCER_PORT", "6432")
            user = os.getenv("DB_USER", "acgs_user")
            password = os.getenv("DB_PASSWORD", "acgs_password")
            database = os.getenv("DB_NAME", "acgs_db")

            return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}"

        # Fallback to direct database connection
        return os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://acgs_user:acgs_password@localhost:5432/acgs_db",
        )

    async def initialize(self):
        """Initialize database connections and pools."""
        try:
            # Create async engine with resilience
            self._async_engine = create_async_engine(
                self.database_url,
                echo=False,
                **self.pool_config,
                connect_args={
                    "server_settings": {
                        "application_name": f"acgs_{self.service_name}",
                        "jit": "off",
                    }
                },
            )

            # Create session factory
            self._async_session_factory = sessionmaker(
                bind=self._async_engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )

            # Initialize raw connection pool for high-performance operations
            await self._initialize_raw_pool()

            logger.info(
                f"Database client initialized successfully for {self.service_name}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize database client: {e}")
            raise

    async def _initialize_raw_pool(self):
        """Initialize raw asyncpg connection pool."""
        try:
            # Parse database URL for asyncpg
            url_parts = self.database_url.replace(
                "postgresql+asyncpg://", "postgresql://"
            )

            self._raw_connection_pool = await asyncpg.create_pool(
                url_parts,
                min_size=self.pool_config["pool_size"] // 2,
                max_size=self.pool_config["pool_size"],
                command_timeout=30,
                server_settings={
                    "application_name": f"acgs_{self.service_name}_raw",
                    "jit": "off",
                },
            )

            logger.info("Raw connection pool initialized")

        except Exception as e:
            logger.warning(f"Failed to initialize raw connection pool: {e}")

    @asynccontextmanager
    async def get_session(self):
        """Get SQLAlchemy async session with resilience."""
        if not self._async_session_factory:
            await self.initialize()

        async def create_session():
            return self._async_session_factory()

        async with self.resilience_manager.resilient_connection(
            create_session
        ) as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    @asynccontextmanager
    async def get_raw_connection(self):
        """Get raw asyncpg connection with resilience."""
        if not self._raw_connection_pool:
            await self._initialize_raw_pool()

        async def get_connection():
            return await self._raw_connection_pool.acquire()

        async with self.resilience_manager.resilient_connection(
            get_connection
        ) as connection:
            try:
                yield connection
            finally:
                await self._raw_connection_pool.release(connection)

    @asynccontextmanager
    async def _get_replica_connection(self, node):
        """Get connection to a specific replica node."""
        node_key = f"{node.host}:{node.port}"

        # Get or create connection pool for this replica
        if node_key not in self._read_replica_pools:
            try:
                self._read_replica_pools[node_key] = await asyncpg.create_pool(
                    node.get_connection_url(),
                    min_size=5,
                    max_size=20,
                    command_timeout=30,
                    server_settings={
                        "application_name": f"acgs_{self.service_name}_replica",
                        "jit": "off",
                    },
                )
            except Exception as e:
                logger.error(f"Failed to create replica pool for {node_key}: {e}")
                raise

        # Get connection from pool
        pool = self._read_replica_pools[node_key]
        connection = await pool.acquire()

        try:
            # Track connection count
            self.replica_router.increment_connection_count(node)
            yield connection
        finally:
            # Release connection and update count
            await pool.release(connection)
            self.replica_router.decrement_connection_count(node)

    async def execute_query(
        self,
        query: str,
        params: Optional[Union[Dict, List]] = None,
        use_raw: bool = False,
    ) -> Any:
        """Execute query with resilience and performance optimization."""
        if use_raw and self._raw_connection_pool:
            async with self.get_raw_connection() as conn:
                if params:
                    return await conn.execute(
                        query, *params if isinstance(params, list) else params
                    )
                return await conn.execute(query)
        else:
            async with self.get_session() as session:
                result = await session.execute(query, params or {})
                return result

    async def fetch_one(
        self, query: str, params: Optional[Union[Dict, List]] = None
    ) -> Optional[Dict[str, Any]]:
        """Fetch single record with resilience."""
        async with self.get_raw_connection() as conn:
            if params:
                row = await conn.fetchrow(
                    query, *params if isinstance(params, list) else params
                )
            else:
                row = await conn.fetchrow(query)

            return dict(row) if row else None

    async def fetch_all(
        self,
        query: str,
        params: Optional[Union[Dict, List]] = None,
        use_read_replica: bool = True,
    ) -> List[Dict[str, Any]]:
        """Fetch all records with resilience and optional read replica routing."""
        if use_read_replica and self.read_replica_config.read_replicas:
            # Use read replica for read operations
            try:
                read_node = await self.replica_router.get_read_connection()
                async with self._get_replica_connection(read_node) as conn:
                    if params:
                        rows = await conn.fetch(
                            query, *params if isinstance(params, list) else params
                        )
                    else:
                        rows = await conn.fetch(query)
                    return [dict(row) for row in rows]
            except Exception as e:
                logger.warning(f"Read replica failed, falling back to primary: {e}")

        # Fallback to primary connection
        async with self.get_raw_connection() as conn:
            if params:
                rows = await conn.fetch(
                    query, *params if isinstance(params, list) else params
                )
            else:
                rows = await conn.fetch(query)

            return [dict(row) for row in rows]

    async def execute_transaction(self, operations: List[Dict[str, Any]]) -> bool:
        """Execute multiple operations in a transaction with resilience."""

        async def _execute_transaction():
            async with self.get_raw_connection() as conn:
                async with conn.transaction():
                    for operation in operations:
                        query = operation.get("query")
                        params = operation.get("params", [])

                        if params:
                            await conn.execute(query, *params)
                        else:
                            await conn.execute(query)
            return True

        return await self.resilience_manager.execute_with_resilience(
            _execute_transaction
        )

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        health_status = {
            "service": self.service_name,
            "database_url": (
                self.database_url.split("@")[1]
                if "@" in self.database_url
                else "unknown"
            ),
            "status": "unknown",
            "connection_pools": {},
            "resilience": self.resilience_manager.get_health_status(),
        }

        try:
            # Test SQLAlchemy connection
            if self._async_engine:
                async with self._async_engine.begin() as conn:
                    result = await conn.execute("SELECT 1 as test")
                    test_value = result.scalar()

                health_status["connection_pools"]["sqlalchemy"] = {
                    "status": "healthy" if test_value == 1 else "unhealthy",
                    "pool_size": self._async_engine.pool.size(),
                    "checked_out": self._async_engine.pool.checkedout(),
                }

            # Test raw connection pool
            if self._raw_connection_pool:
                async with self._raw_connection_pool.acquire() as conn:
                    test_value = await conn.fetchval("SELECT 1")

                health_status["connection_pools"]["asyncpg"] = {
                    "status": "healthy" if test_value == 1 else "unhealthy",
                    "pool_size": self._raw_connection_pool.get_size(),
                    "free_connections": self._raw_connection_pool.get_idle_size(),
                }

            # Overall status
            all_healthy = all(
                pool.get("status") == "healthy"
                for pool in health_status["connection_pools"].values()
            )
            health_status["status"] = "healthy" if all_healthy else "degraded"

        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            logger.error(f"Database health check failed: {e}")

        return health_status

    async def close(self):
        """Close all database connections."""
        try:
            if self._raw_connection_pool:
                await self._raw_connection_pool.close()
                logger.info("Raw connection pool closed")

            if self._async_engine:
                await self._async_engine.dispose()
                logger.info("SQLAlchemy engine disposed")

        except Exception as e:
            logger.error(f"Error closing database connections: {e}")


# Global database clients for each service
_database_clients: Dict[str, EnhancedDatabaseClient] = {}


async def get_database_client(service_name: str) -> EnhancedDatabaseClient:
    """Get or create enhanced database client for a service."""
    if service_name not in _database_clients:
        client = EnhancedDatabaseClient(service_name)
        await client.initialize()
        _database_clients[service_name] = client

    return _database_clients[service_name]


async def close_all_database_clients():
    """Close all database clients."""
    for client in _database_clients.values():
        await client.close()

    _database_clients.clear()
    logger.info("All database clients closed")
