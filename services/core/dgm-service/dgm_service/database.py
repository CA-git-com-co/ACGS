"""
Database configuration and connection management for DGM Service.
"""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import asyncpg
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from .config import settings

logger = logging.getLogger(__name__)

# Global database engine and session factory
engine = None
async_session_factory = None
metadata = MetaData(schema="dgm")


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self):
        self.engine = None
        self.session_factory = None
        self._initialized = False

    async def initialize(self):
        """Initialize database engine and session factory."""
        if self._initialized:
            return

        try:
            # Create async engine
            self.engine = create_async_engine(
                settings.DATABASE_URL,
                pool_size=settings.DATABASE_POOL_SIZE,
                max_overflow=settings.DATABASE_MAX_OVERFLOW,
                pool_timeout=settings.DATABASE_POOL_TIMEOUT,
                pool_recycle=settings.DATABASE_POOL_RECYCLE,
                echo=settings.DEBUG,
                poolclass=NullPool if settings.ENVIRONMENT == "test" else None,
            )

            # Create session factory
            self.session_factory = async_sessionmaker(
                bind=self.engine, class_=AsyncSession, expire_on_commit=False
            )

            # Test connection
            async with self.engine.begin() as conn:
                await conn.execute("SELECT 1")

            logger.info("Database initialized successfully")
            self._initialized = True

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def close(self):
        """Close database connections."""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connections closed")

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get database session with automatic cleanup."""
        if not self._initialized:
            await self.initialize()

        async with self.session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    async def health_check(self) -> bool:
        """Check database health."""
        try:
            async with self.get_session() as session:
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global database manager instance
database_manager = DatabaseManager()


# Convenience function for getting database sessions
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session - convenience function."""
    async with database_manager.get_session() as session:
        yield session


# Database initialization function
async def init_database():
    """Initialize database with schema and tables."""
    try:
        # Connect to database
        conn = await asyncpg.connect(settings.DATABASE_URL)

        # Read and execute initialization script
        with open("scripts/init-db.sql") as f:
            init_script = f.read()

        await conn.execute(init_script)
        await conn.close()

        logger.info("Database schema initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database schema: {e}")
        raise


# Database migration functions
async def run_migrations():
    """Run database migrations."""
    try:
        # In production, this would use Alembic
        # For now, we'll just ensure the schema is up to date
        await init_database()
        logger.info("Database migrations completed")

    except Exception as e:
        logger.error(f"Database migration failed: {e}")
        raise


async def check_database_version():
    """Check database schema version."""
    try:
        async with database_manager.get_session() as session:
            # Check if our tables exist
            result = await session.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'dgm'
            """
            )
            tables = [row[0] for row in result.fetchall()]

            expected_tables = [
                "dgm_archive",
                "performance_metrics",
                "constitutional_compliance_log",
                "bandit_state",
                "improvement_workspace",
                "system_configuration",
            ]

            missing_tables = set(expected_tables) - set(tables)
            if missing_tables:
                logger.warning(f"Missing database tables: {missing_tables}")
                return False

            logger.info("Database schema version check passed")
            return True

    except Exception as e:
        logger.error(f"Database version check failed: {e}")
        return False


# Connection pool monitoring
async def get_pool_stats():
    """Get database connection pool statistics."""
    if not database_manager.engine:
        return {}

    pool = database_manager.engine.pool
    return {
        "pool_size": pool.size(),
        "checked_in": pool.checkedin(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "invalid": pool.invalid(),
    }


# Database cleanup functions
async def cleanup_old_data():
    """Clean up old data based on retention policies."""
    try:
        async with database_manager.get_session() as session:
            # Clean up old performance metrics (older than 90 days)
            await session.execute(
                """
                DELETE FROM dgm.performance_metrics 
                WHERE created_at < NOW() - INTERVAL '90 days'
            """
            )

            # Clean up old compliance logs (older than 1 year)
            await session.execute(
                """
                DELETE FROM dgm.constitutional_compliance_log 
                WHERE created_at < NOW() - INTERVAL '1 year'
            """
            )

            # Clean up completed workspaces (older than 30 days)
            await session.execute(
                """
                DELETE FROM dgm.improvement_workspace 
                WHERE status = 'completed' 
                AND updated_at < NOW() - INTERVAL '30 days'
            """
            )

            await session.commit()
            logger.info("Database cleanup completed")

    except Exception as e:
        logger.error(f"Database cleanup failed: {e}")
        raise


# Database backup functions
async def create_backup():
    """Create database backup."""
    try:
        # This would integrate with pg_dump or similar tools
        # For now, just log the action
        logger.info("Database backup initiated")
        # Implementation would depend on deployment environment

    except Exception as e:
        logger.error(f"Database backup failed: {e}")
        raise
