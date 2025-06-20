"""
Database Connection Management

SQLAlchemy connection pooling and session management for ACGS-PGP v8.
"""

import logging
import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Database connection manager with connection pooling and health monitoring.

    Provides both sync and async database connections with proper resource management
    and constitutional compliance validation.
    """

    def __init__(
        self,
        database_url: str,
        pool_size: int = 20,
        max_overflow: int = 30,
        pool_timeout: int = 30,
        pool_recycle: int = 3600,
        echo: bool = False,
    ):
        """Initialize database manager with connection pooling."""
        self.database_url = database_url
        self.pool_size = pool_size
        self.max_overflow = max_overflow
        self.pool_timeout = pool_timeout
        self.pool_recycle = pool_recycle
        self.echo = echo

        # Create engines
        self._sync_engine = None
        self._async_engine = None
        self._sync_session_factory = None
        self._async_session_factory = None

        # Constitutional compliance
        self.constitutional_hash = "cdd01ef066bc6cf2"

        logger.info("Database manager initialized")

    def initialize_sync_engine(self):
        """Initialize synchronous database engine."""
        if self._sync_engine is None:
            self._sync_engine = create_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                echo=self.echo,
                # Connection pool settings
                pool_pre_ping=True,  # Validate connections before use
                pool_reset_on_return="commit",  # Reset connections on return
            )

            # Add connection event listeners
            @event.listens_for(self._sync_engine, "connect")
            def set_sqlite_pragma(dbapi_connection, connection_record):
                """Set database-specific settings on connection."""
                if "postgresql" in self.database_url:
                    # PostgreSQL-specific settings
                    cursor = dbapi_connection.cursor()
                    cursor.execute("SET timezone TO 'timezone.utc'")
                    cursor.execute("SET statement_timeout = '30s'")
                    cursor.close()

            self._sync_session_factory = sessionmaker(
                bind=self._sync_engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )

            logger.info("Synchronous database engine initialized")

    def initialize_async_engine(self):
        """Initialize asynchronous database engine."""
        if self._async_engine is None:
            # Convert sync URL to async URL
            async_url = self.database_url.replace("postgresql://", "postgresql+asyncpg://")

            self._async_engine = create_async_engine(
                async_url,
                pool_size=self.pool_size,
                max_overflow=self.max_overflow,
                pool_timeout=self.pool_timeout,
                pool_recycle=self.pool_recycle,
                echo=self.echo,
                # Connection pool settings
                pool_pre_ping=True,
                pool_reset_on_return="commit",
            )

            self._async_session_factory = async_sessionmaker(
                bind=self._async_engine,
                class_=AsyncSession,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )

            logger.info("Asynchronous database engine initialized")

    def get_sync_session(self) -> Session:
        """Get synchronous database session."""
        if self._sync_session_factory is None:
            self.initialize_sync_engine()
        return self._sync_session_factory()

    def get_async_session(self) -> AsyncSession:
        """Get asynchronous database session."""
        if self._async_session_factory is None:
            self.initialize_async_engine()
        return self._async_session_factory()

    @asynccontextmanager
    async def async_session_scope(self) -> AsyncGenerator[AsyncSession, None]:
        """Async context manager for database sessions with automatic cleanup."""
        session = self.get_async_session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    def sync_session_scope(self):
        """Context manager for synchronous database sessions with automatic cleanup."""
        session = self.get_sync_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    async def health_check(self) -> dict:
        """Perform database health check."""
        health_status = {
            "status": "healthy",
            "constitutional_hash": self.constitutional_hash,
            "connection_pool": {},
            "timestamp": None,
        }

        try:
            # Check async connection
            if self._async_engine:
                async with self.async_session_scope() as session:
                    result = await session.execute("SELECT 1 as health_check")
                    health_check_result = result.scalar()

                    if health_check_result == 1:
                        health_status["connection_pool"]["async"] = {
                            "status": "healthy",
                            "pool_size": self._async_engine.pool.size(),
                            "checked_in": self._async_engine.pool.checkedin(),
                            "checked_out": self._async_engine.pool.checkedout(),
                        }
                    else:
                        health_status["status"] = "unhealthy"
                        health_status["connection_pool"]["async"] = {"status": "unhealthy"}

            # Check sync connection
            if self._sync_engine:
                with self.sync_session_scope() as session:
                    result = session.execute("SELECT 1 as health_check")
                    health_check_result = result.scalar()

                    if health_check_result == 1:
                        health_status["connection_pool"]["sync"] = {
                            "status": "healthy",
                            "pool_size": self._sync_engine.pool.size(),
                            "checked_in": self._sync_engine.pool.checkedin(),
                            "checked_out": self._sync_engine.pool.checkedout(),
                        }
                    else:
                        health_status["status"] = "unhealthy"
                        health_status["connection_pool"]["sync"] = {"status": "unhealthy"}

            from datetime import datetime

            health_status["timestamp"] = datetime.utcnow().isoformat()

        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            logger.error(f"Database health check failed: {e}")

        return health_status

    async def close(self):
        """Close database connections and clean up resources."""
        try:
            if self._async_engine:
                await self._async_engine.dispose()
                logger.info("Async database engine disposed")

            if self._sync_engine:
                self._sync_engine.dispose()
                logger.info("Sync database engine disposed")

        except Exception as e:
            logger.error(f"Error closing database connections: {e}")


# Global database manager instance
_db_manager: DatabaseManager | None = None


def initialize_database(
    database_url: str | None = None,
    pool_size: int = 20,
    max_overflow: int = 30,
    pool_timeout: int = 30,
    pool_recycle: int = 3600,
    echo: bool = False,
) -> DatabaseManager:
    """Initialize global database manager."""
    global _db_manager

    if database_url is None:
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://acgs_user:acgs_password@localhost:5432/acgs_db",
        )

    _db_manager = DatabaseManager(
        database_url=database_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
        echo=echo,
    )

    return _db_manager


def get_database_manager() -> DatabaseManager:
    """Get global database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = initialize_database()
    return _db_manager


async def get_database_session() -> AsyncSession:
    """Get async database session for dependency injection."""
    db_manager = get_database_manager()
    return db_manager.get_async_session()


def get_sync_database_session() -> Session:
    """Get sync database session."""
    db_manager = get_database_manager()
    return db_manager.get_sync_session()
