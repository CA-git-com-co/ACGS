"""
Database Optimization Components for ACGS-PGP Services

This module provides optimized database connection pooling, query performance
enhancements, and unified database access patterns across all services.

CRITICAL: This module also exports the core database components (Base, get_async_db)
that services depend on for backward compatibility.
"""

# Import core database components from the main database module
try:
    from ..database import AsyncSessionLocal, Base, async_engine, get_async_db, metadata

    _core_database_available = True
except ImportError:
    _core_database_available = False
    # Fallback imports for testing environments
    Base = None
    get_async_db = None
    AsyncSessionLocal = None
    async_engine = None
    metadata = None

from .pool_manager import (
    ConnectionPool,
    DatabasePoolManager,
    PoolConfig,
    get_pool_manager,
)

# Export core database components for service compatibility
__all__ = ["ConnectionPool", "DatabasePoolManager", "PoolConfig", "get_pool_manager"]

# Add core database components if available
if _core_database_available:
    __all__.extend(
        ["AsyncSessionLocal", "Base", "async_engine", "get_async_db", "metadata"]
    )

# Optional imports for components that may not be implemented yet
try:
    pass

    __all__.extend(["QueryCache", "QueryMetrics", "QueryOptimizer"])
except ImportError:
    pass

try:
    pass

    __all__.extend(["AsyncDatabaseConnection", "DatabaseConnection"])
except ImportError:
    pass

try:
    pass

    __all__.extend(["Migration", "MigrationManager"])
except ImportError:
    pass

try:
    pass

    __all__.extend(["DatabaseMonitor", "PerformanceMetrics"])
except ImportError:
    pass
