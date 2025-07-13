"""
Real Database Implementation for PGC Service.

Replaces placeholder database operations with actual SQLAlchemy-based
database connectivity and operations for production use.

Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
import os
import pathlib
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import MetaData, create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://pgc_user:pgc_password@postgres:5432/pgc_database",
)
DATABASE_URL_SYNC = os.getenv(
    "DATABASE_URL_SYNC", "postgresql://pgc_user:pgc_password@postgres:5432/pgc_database"
)

# Fallback to SQLite for development
if not DATABASE_URL.startswith(("postgresql", "mysql")):
    DATABASE_URL = "sqlite+aiosqlite:///./pgc_service.db"
    DATABASE_URL_SYNC = "sqlite:///./pgc_service.db"

Base = declarative_base()


class RealDatabaseManager:
    """
    Real database manager using SQLAlchemy for actual database operations.
    Replaces mock database operations with production-ready functionality.
    """

    def __init__(self, database_url: str | None = None):
        """Initialize real database manager with SQLAlchemy engine."""
        self.database_url = database_url or DATABASE_URL
        self.database_url_sync = DATABASE_URL_SYNC
        self.engine = None
        self.sync_engine = None
        self.SessionLocal = None
        self.connected = False

        # Connection settings
        self.connect_args = {}
        if "sqlite" in self.database_url:
            self.connect_args = {"check_same_thread": False, "poolclass": StaticPool}

        logger.info(
            f"Real database manager initialized for {self._mask_url(self.database_url)}"
        )

    def _mask_url(self, url: str) -> str:
        """Mask sensitive information in database URL for logging."""
        if "://" in url:
            scheme, rest = url.split("://", 1)
            if "@" in rest:
                _credentials, host_part = rest.split("@", 1)
                return f"{scheme}://***:***@{host_part}"
        return url

    async def connect(self) -> bool:
        """Connect to database with real SQLAlchemy engine."""
        try:
            # Create async engine
            self.engine = create_async_engine(
                self.database_url,
                echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
                pool_pre_ping=True,
                pool_recycle=300,
                **self.connect_args,
            )

            # Create sync engine for certain operations
            self.sync_engine = create_engine(
                self.database_url_sync,
                echo=os.getenv("DATABASE_ECHO", "false").lower() == "true",
                pool_pre_ping=True,
                pool_recycle=300,
                **self.connect_args,
            )

            # Create session factory
            self.SessionLocal = async_sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )

            # Test connection
            async with self.engine.begin() as conn:
                await conn.execute(text("SELECT 1"))

            self.connected = True
            logger.info("Real database connection established successfully")
            return True

        except Exception as e:
            logger.exception(f"Real database connection failed: {e}")
            self.connected = False
            return False

    async def disconnect(self) -> None:
        """Disconnect from database and cleanup resources."""
        try:
            if self.engine:
                await self.engine.dispose()
                self.engine = None

            if self.sync_engine:
                self.sync_engine.dispose()
                self.sync_engine = None

            self.SessionLocal = None
            self.connected = False
            logger.info("Real database connection closed")

        except Exception as e:
            logger.exception(f"Error disconnecting from database: {e}")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with automatic cleanup."""
        if not self.connected or not self.SessionLocal:
            raise RuntimeError("Database not connected")

        async with self.SessionLocal() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                logger.exception(f"Database session error: {e}")
                raise
            finally:
                await session.close()

    async def execute_query(
        self, query: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        """Execute a raw SQL query and return results."""
        if not self.connected:
            raise RuntimeError("Database not connected")

        try:
            async with self.get_session() as session:
                result = await session.execute(text(query), params or {})

                # Handle different result types
                if result.returns_rows:
                    rows = result.fetchall()
                    # Convert rows to dictionaries
                    columns = result.keys()
                    return [dict(zip(columns, row, strict=False)) for row in rows]
                # For INSERT, UPDATE, DELETE operations
                await session.commit()
                return [{"affected_rows": result.rowcount}]

        except Exception as e:
            logger.exception(f"Query execution failed: {e}")
            logger.debug(f"Query: {query}, Params: {params}")
            raise

    async def execute_transaction(self, operations: list[dict[str, Any]]) -> bool:
        """Execute multiple operations in a single transaction."""
        if not self.connected:
            raise RuntimeError("Database not connected")

        try:
            async with self.get_session() as session, session.begin():
                for operation in operations:
                    query = operation.get("query")
                    params = operation.get("params", {})

                    if not query:
                        raise ValueError("Operation missing 'query' field")

                    await session.execute(text(query), params)

                await session.commit()
                logger.debug(
                    "Transaction completed successfully"
                    f" ({len(operations)} operations)"
                )
                return True

        except Exception as e:
            logger.exception(f"Transaction failed: {e}")
            return False

    async def create_tables(self, metadata: MetaData | None = None) -> bool:
        """Create database tables from metadata."""
        if not self.connected:
            raise RuntimeError("Database not connected")

        try:
            target_metadata = metadata or Base.metadata

            async with self.engine.begin() as conn:
                await conn.run_sync(target_metadata.create_all)

            logger.info("Database tables created successfully")
            return True

        except Exception as e:
            logger.exception(f"Table creation failed: {e}")
            return False

    async def drop_tables(self, metadata: MetaData | None = None) -> bool:
        """Drop database tables."""
        if not self.connected:
            raise RuntimeError("Database not connected")

        try:
            target_metadata = metadata or Base.metadata

            async with self.engine.begin() as conn:
                await conn.run_sync(target_metadata.drop_all)

            logger.info("Database tables dropped successfully")
            return True

        except Exception as e:
            logger.exception(f"Table dropping failed: {e}")
            return False

    async def health_check(self) -> bool:
        """Comprehensive database health check."""
        if not self.connected or not self.engine:
            return False

        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text("SELECT 1 as health"))
                row = result.fetchone()
                return row is not None and row[0] == 1

        except Exception as e:
            logger.exception(f"Database health check failed: {e}")
            return False

    async def get_connection_info(self) -> dict[str, Any]:
        """Get database connection information."""
        if not self.connected:
            return {"connected": False}

        try:
            async with self.engine.begin() as conn:
                # Get database version and basic info
                if "postgresql" in self.database_url:
                    version_result = await conn.execute(text("SELECT version()"))
                    version = version_result.scalar()
                elif "sqlite" in self.database_url:
                    version_result = await conn.execute(text("SELECT sqlite_version()"))
                    version = f"SQLite {version_result.scalar()}"
                else:
                    version = "Unknown"

                return {
                    "connected": True,
                    "database_url": self._mask_url(self.database_url),
                    "database_version": version,
                    "pool_size": getattr(self.engine.pool, "size", "N/A"),
                    "checked_out": getattr(self.engine.pool, "checkedout", "N/A"),
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                }

        except Exception as e:
            logger.exception(f"Failed to get connection info: {e}")
            return {"connected": True, "error": str(e)}

    async def backup_database(self, backup_path: str) -> bool:
        """Create database backup (SQLite only for now)."""
        if "sqlite" not in self.database_url:
            logger.warning("Backup currently only supported for SQLite databases")
            return False

        try:
            import shutil

            # Extract database file path
            db_path = self.database_url.replace("sqlite+aiosqlite:///", "").replace(
                "./", ""
            )

            if pathlib.Path(db_path).exists():
                shutil.copy2(db_path, backup_path)
                logger.info(f"Database backup created: {backup_path}")
                return True
            logger.error(f"Database file not found: {db_path}")
            return False

        except Exception as e:
            logger.exception(f"Database backup failed: {e}")
            return False


class DatabaseConnectionPool:
    """
    Database connection pool manager for handling multiple connections
    and connection lifecycle management.
    """

    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.managers: dict[str, RealDatabaseManager] = {}
        self.default_manager: RealDatabaseManager | None = None

    async def get_manager(self, name: str = "default") -> RealDatabaseManager:
        """Get or create a database manager by name."""
        if name not in self.managers:
            self.managers[name] = RealDatabaseManager()
            if not await self.managers[name].connect():
                raise RuntimeError(f"Failed to connect database manager: {name}")

        if name == "default":
            self.default_manager = self.managers[name]

        return self.managers[name]

    async def close_all(self) -> None:
        """Close all database connections."""
        for name, manager in self.managers.items():
            try:
                await manager.disconnect()
                logger.info(f"Closed database manager: {name}")
            except Exception as e:
                logger.exception(f"Error closing database manager {name}: {e}")

        self.managers.clear()
        self.default_manager = None


# Global instances
_db_manager: RealDatabaseManager | None = None
_connection_pool: DatabaseConnectionPool | None = None


def get_real_database_manager() -> RealDatabaseManager:
    """Get or create real database manager singleton."""
    global _db_manager
    if _db_manager is None:
        _db_manager = RealDatabaseManager()
    return _db_manager


async def initialize_real_database() -> bool:
    """Initialize real database connection."""
    db_manager = get_real_database_manager()
    success = await db_manager.connect()
    if success:
        logger.info("Real database initialized successfully")
    else:
        logger.error("Failed to initialize real database")
    return success


async def close_real_database() -> None:
    """Close real database connection."""
    global _db_manager
    if _db_manager:
        await _db_manager.disconnect()
        _db_manager = None
        logger.info("Real database connection closed")


async def get_real_database_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session from the global manager."""
    db_manager = get_real_database_manager()
    if not db_manager.connected:
        raise RuntimeError(
            "Database not connected. Call initialize_real_database() first."
        )

    async with db_manager.get_session() as session:
        yield session


# Compatibility functions for backward compatibility
DatabaseManager = RealDatabaseManager
get_database_manager = get_real_database_manager
initialize_database = initialize_real_database
close_database = close_real_database
