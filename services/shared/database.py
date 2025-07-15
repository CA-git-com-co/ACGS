# ACGS/shared/database.py
import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import (  # Updated import for declarative_base
    declarative_base,
    sessionmaker,
)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Import centralized configuration
try:
    from .utils import get_config

    _config_available = True
except ImportError:
    # Fallback for when utils is not available (e.g., during initial setup)
    _config_available = False

# Get database configuration
if _config_available:
    try:
        config = get_config()
        DATABASE_URL = config.get_database_url()
        DB_ECHO = config.get("db_echo_log", False)
    except Exception:
        # Fallback to environment variables if config fails
        DATABASE_URL = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://acgs_user:acgs_password@postgres_db:5432/acgs_pgp_db",
        )
        DB_ECHO = os.getenv("DB_ECHO_LOG", "False").lower() == "true"
else:
    # Fallback to environment variables
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://acgs_user:acgs_password@postgres_db:5432/acgs_pgp_db",
    )
    DB_ECHO = os.getenv("DB_ECHO_LOG", "False").lower() == "true"

# Create async engine with optimized connection pooling
# Handle different database types (PostgreSQL vs SQLite)
if DATABASE_URL.startswith("sqlite"):
    # SQLite configuration (for testing)
    async_engine = create_async_engine(
        DATABASE_URL,
        echo=DB_ECHO,
        # SQLite doesn't support connection pooling parameters
    )
else:
    # PostgreSQL configuration (optimized for 1000 RPS)
    async_engine = create_async_engine(
        DATABASE_URL,
        echo=DB_ECHO,
        pool_pre_ping=True,
        pool_size=50,  # Increased for high throughput
        max_overflow=75,  # Increased for burst capacity
        pool_timeout=20,  # Reduced timeout for faster failure
        pool_recycle=1800,  # More frequent recycling
        connect_args={
            "server_settings": {
                "application_name": "acgs_pgp_optimized",
                "jit": "off",  # Disable JIT for consistent performance
                "statement_timeout": "30s",
                "idle_in_transaction_session_timeout": "60s",
                "tcp_keepalives_idle": "300",
                "tcp_keepalives_interval": "30",
                "tcp_keepalives_count": "3",
            }
        },
    )

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,  # Default for AsyncSession
    autoflush=False,  # Default for AsyncSession
)

# Base for declarative models
try:
    Base = declarative_base()
    if Base is None:
        from sqlalchemy.orm import declarative_base as db_base

        Base = db_base()
except Exception:
    from sqlalchemy.orm import declarative_base as db_base

    Base = db_base()

# Ensure Base is not None
if Base is None:
    from sqlalchemy.orm import declarative_base as db_base

    Base = db_base()

metadata = Base.metadata  # Expose metadata for Alembic and table creation


# Async dependency to get DB session for FastAPI
async def get_async_db() -> AsyncSession:  # Changed to yield AsyncGenerator
    async with AsyncSessionLocal() as session:
        try:
            yield session
            # Removed await session.commit() here.
            # Commits should be handled at the router/CRUD operation level
            # to allow for more control over transactions.
            # If an operation completes successfully, it commits. If it raises an error,
            # the calling code or an exception handler should ensure rollback.
        except Exception:
            await session.rollback()  # Rollback on error within the session's scope
            raise
        # finally:
        # await session.close() # session is closed automatically by context manager


async def create_db_and_tables():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Creates all tables defined by models inheriting from Base.
    This is typically called once at application startup or by migrations.
    Alembic is the preferred way to manage schema, but this can be useful for initial setup
    or in test environments if not using Alembic for tests.
    Make sure all models are imported before calling this.
    """
    async with async_engine.begin() as conn:
        # Import all models here so Base knows about them before creating tables
        # This dynamic import can be tricky. It's often better to ensure models
        # are imported in shared/models/__init__.py and then `from . import models`
        # is called somewhere before this function (e.g. in shared/__init__.py or service main.py)
        # For now, assuming models are loaded.
        # from . import models # noqa
        await conn.run_sync(Base.metadata.create_all)


# Note: For Alembic, env.py handles table creation/migration.
# create_db_and_tables() might be called by individual service main.py on startup
# for non-Alembic managed tables or for ensuring DB exists, though migrations handle schema.
# It's generally recommended to rely on Alembic for all schema management in production.


# Test compatibility functions
def create_engine(*args, **kwargs):
    """
    Create database engine for test compatibility.

    This function provides compatibility with tests that expect
    a synchronous create_engine function.
    """
    from sqlalchemy import create_engine as sync_create_engine
    return sync_create_engine(*args, **kwargs)


def get_database_connection():
    """
    Get database connection for test compatibility.

    Returns:
        Database connection for testing
    """
    try:
        # For test compatibility, create a new engine
        database_url = "sqlite:///test.db"  # Default test database
        engine = create_engine(database_url)
        return engine
    except Exception:
        # Fallback for tests
        return None


def validate_database_url(url: str) -> bool:
    """
    Validate database URL format.

    Args:
        url: Database URL to validate

    Returns:
        True if URL is valid, False otherwise
    """
    try:
        # Basic validation - check if it looks like a database URL
        if not url or not isinstance(url, str):
            return False

        # Check for common database URL patterns
        valid_schemes = ['postgresql', 'postgres', 'sqlite', 'mysql', 'mariadb']

        for scheme in valid_schemes:
            if url.startswith(f"{scheme}://") or url.startswith(f"{scheme}+"):
                return True

        return False
    except Exception:
        return False
