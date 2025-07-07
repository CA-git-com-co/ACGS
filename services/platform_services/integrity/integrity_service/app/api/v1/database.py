"""
Database dependency for ACGS Integrity Service API endpoints.
Constitutional Hash: cdd01ef066bc6cf2
"""

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = (
    "postgresql+asyncpg://acgs_user:acgs_password@localhost:5439/acgs_integrity"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
)

# Create async session factory
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get async database session.

    Yields:
        AsyncSession: Database session
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()


async def init_database():
    """Initialize database tables."""
    try:
        from ...models import Base

        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")

    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def check_database_connection() -> bool:
    """
    Check if database connection is working.

    Returns:
        bool: True if connection is working, False otherwise
    """
    try:
        async with AsyncSessionLocal() as session:
            # Simple query to test connection
            result = await session.execute("SELECT 1")
            return result.scalar() == 1
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False


async def get_database_stats() -> dict:
    """
    Get database statistics.

    Returns:
        dict: Database statistics
    """
    try:
        async with AsyncSessionLocal() as session:
            # Get basic database info
            stats = {
                "connection_status": "connected",
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "engine_pool_size": engine.pool.size(),
                "engine_pool_checked_in": engine.pool.checkedin(),
                "engine_pool_checked_out": engine.pool.checkedout(),
            }

            return stats

    except Exception as e:
        logger.error(f"Failed to get database stats: {e}")
        return {
            "connection_status": "error",
            "error": str(e),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }


# Health check function for database
async def database_health_check() -> dict:
    """
    Perform database health check.

    Returns:
        dict: Health check results
    """
    try:
        is_connected = await check_database_connection()
        stats = await get_database_stats()

        return {
            "status": "healthy" if is_connected else "unhealthy",
            "connection": "connected" if is_connected else "disconnected",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "stats": stats,
        }

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "status": "unhealthy",
            "connection": "error",
            "error": str(e),
            "constitutional_hash": CONSTITUTIONAL_HASH,
        }


# Cleanup function
async def close_database():
    """Close database connections."""
    try:
        await engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
