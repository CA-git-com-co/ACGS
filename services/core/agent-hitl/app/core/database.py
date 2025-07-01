"""
Agent HITL Service Database Configuration

Database setup and connection management for the Agent HITL service.
"""

import logging
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from ..models.hitl_models import Base
from .config import get_settings

logger = logging.getLogger(__name__)

# Global database engine and session maker
engine = None
async_session_maker = None


def get_database_url() -> str:
    """Get database URL from settings."""
    settings = get_settings()
    return settings.DATABASE_URL


def create_engine():
    """Create database engine."""
    global engine

    if engine is None:
        database_url = get_database_url()

        engine = create_async_engine(
            database_url,
            echo=False,  # Set to True for SQL debugging
            poolclass=NullPool,  # Use NullPool for async
            pool_pre_ping=True,
            pool_recycle=3600,  # Recycle connections every hour
            connect_args={
                "server_settings": {
                    "application_name": "agent-hitl-service",
                }
            },
        )

        logger.info("✅ Database engine created")

    return engine


def create_session_maker():
    """Create async session maker."""
    global async_session_maker

    if async_session_maker is None:
        engine = create_engine()
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=True,
            autocommit=False,
        )

        logger.info("✅ Database session maker created")

    return async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session.

    Yields:
        AsyncSession: Database session
    """
    session_maker = create_session_maker()

    async with session_maker() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def create_tables():
    """Create database tables."""
    try:
        engine = create_engine()

        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)

        logger.info("✅ Database tables created/verified")

    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise


async def drop_tables():
    """Drop all database tables (for testing)."""
    try:
        engine = create_engine()

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

        logger.info("✅ Database tables dropped")

    except Exception as e:
        logger.error(f"❌ Failed to drop database tables: {e}")
        raise


async def check_database_connection():
    """Check database connectivity."""
    try:
        session_maker = create_session_maker()

        async with session_maker() as session:
            # Simple query to test connection
            result = await session.execute("SELECT 1")
            result.scalar()

        logger.info("✅ Database connection verified")
        return True

    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


async def get_database_info():
    """Get database information."""
    try:
        session_maker = create_session_maker()

        async with session_maker() as session:
            # Get database version
            result = await session.execute("SELECT version()")
            version = result.scalar()

            # Get current database name
            result = await session.execute("SELECT current_database()")
            database_name = result.scalar()

            # Get current user
            result = await session.execute("SELECT current_user")
            current_user = result.scalar()

            return {
                "version": version,
                "database_name": database_name,
                "current_user": current_user,
                "url": (
                    get_database_url().split("@")[1]
                    if "@" in get_database_url()
                    else "unknown"
                ),
            }

    except Exception as e:
        logger.error(f"❌ Failed to get database info: {e}")
        return {"error": str(e)}


# Database health check
async def database_health_check():
    """Perform database health check."""
    try:
        # Check basic connectivity
        connection_ok = await check_database_connection()
        if not connection_ok:
            return {"status": "unhealthy", "error": "Database connection failed"}

        # Get database info
        db_info = await get_database_info()

        # Check if tables exist
        session_maker = create_session_maker()
        async with session_maker() as session:
            # Check if main tables exist
            result = await session.execute(
                """
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('agent_operation_requests', 'hitl_decisions', 'agent_confidence_profiles')
            """
            )
            tables = [row[0] for row in result.fetchall()]

        return {
            "status": "healthy",
            "database_info": db_info,
            "tables_exist": len(tables),
            "expected_tables": 3,
            "tables": tables,
        }

    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}


# Initialize database on module import
def init_database():
    """Initialize database components."""
    try:
        create_engine()
        create_session_maker()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


# Auto-initialize when module is imported
init_database()
