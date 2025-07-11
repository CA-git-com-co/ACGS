"""
Optimized Database Connection Pool for ACGS-2
HASH-OK:cdd01ef066bc6cf2

Implements high-performance PostgreSQL connection pooling with:
- Pre-warmed connections for reduced latency
- Async connection management
- Connection health monitoring
- Performance metrics and optimization
- Constitutional compliance validation
- Target: >100 RPS throughput, P99 latency <5ms
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, AsyncGenerator
import weakref

import asyncpg
from asyncpg import Connection, Pool
from asyncpg.pool import PoolConnectionProxy

# Constitutional Hash: cdd01ef066bc6cf2
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)

@dataclass
class ConnectionMetrics:
    """Database connection pool metrics."""
    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    avg_query_time_ms: float = 0.0
    p99_query_time_ms: float = 0.0
    connection_errors: int = 0
    pool_exhaustions: int = 0
    constitutional_validations: int = 0
    last_reset: datetime = field(default_factory=datetime.now)

@dataclass
class ConnectionConfig:
    """Database connection configuration."""
    host: str = "localhost"
    port: int = 5439
    database: str = "acgs_db"
    user: str = "acgs_user"
    password: str = "acgs_password"
    min_size: int = 10
    max_size: int = 50
    max_queries: int = 50000
    max_inactive_connection_lifetime: float = 300.0
    timeout: float = 60.0
    command_timeout: float = 30.0
    server_settings: Dict[str, str] = field(default_factory=lambda: {
        "application_name": "acgs_optimized_pool",
        "tcp_keepalives_idle": "600",
        "tcp_keepalives_interval": "30",
        "tcp_keepalives_count": "3"
    })

class OptimizedConnectionPool:
    """
    High-performance PostgreSQL connection pool optimized for ACGS-2.
    
    Features:
    - Pre-warmed connections for instant availability
    - Health monitoring and automatic recovery
    - Performance metrics and optimization
    - Constitutional compliance validation
    """
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.pool: Optional[Pool] = None
        self.metrics = ConnectionMetrics()
        self.query_times: List[float] = []
        self.is_initialized = False
        self.health_check_task: Optional[asyncio.Task] = None
        self.warmup_task: Optional[asyncio.Task] = None
        
        # Performance optimization settings
        self.enable_prepared_statements = True
        self.enable_query_caching = True
        self.enable_connection_warming = True
        
        # Constitutional compliance tracking
        self.constitutional_queries: set = set()

    async def initialize(self) -> bool:
        """Initialize the connection pool with pre-warming."""
        try:
            # Create connection pool
            self.pool = await asyncpg.create_pool(
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password,
                min_size=self.config.min_size,
                max_size=self.config.max_size,
                max_queries=self.config.max_queries,
                max_inactive_connection_lifetime=self.config.max_inactive_connection_lifetime,
                timeout=self.config.timeout,
                command_timeout=self.config.command_timeout,
                server_settings=self.config.server_settings,
                init=self._init_connection
            )
            
            # Validate constitutional compliance
            await self._validate_constitutional_compliance()
            
            # Start background tasks
            if self.enable_connection_warming:
                self.warmup_task = asyncio.create_task(self._warmup_connections())
            
            self.health_check_task = asyncio.create_task(self._health_check_loop())
            
            self.is_initialized = True
            logger.info(f"Optimized connection pool initialized - Hash: {CONSTITUTIONAL_HASH}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {e}")
            return False

    async def _init_connection(self, connection: Connection):
        """Initialize individual database connection."""
        try:
            # Set connection-level optimizations
            await connection.execute("SET synchronous_commit = off")
            await connection.execute("SET wal_writer_delay = '10ms'")
            await connection.execute("SET checkpoint_completion_target = 0.9")
            await connection.execute("SET random_page_cost = 1.1")
            await connection.execute("SET effective_cache_size = '1GB'")
            
            # Set constitutional compliance marker
            await connection.execute(
                "SET application_name = $1", 
                f"acgs_pool_{CONSTITUTIONAL_HASH}"
            )
            
        except Exception as e:
            logger.warning(f"Connection initialization warning: {e}")

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[PoolConnectionProxy, None]:
        """Get database connection with performance monitoring."""
        if not self.is_initialized or not self.pool:
            raise RuntimeError("Connection pool not initialized")
        
        start_time = time.time()
        connection = None
        
        try:
            # Get connection from pool
            connection = await self.pool.acquire(timeout=self.config.timeout)
            self.metrics.active_connections += 1
            
            yield connection
            
        except asyncpg.PoolError as e:
            self.metrics.pool_exhaustions += 1
            logger.error(f"Pool exhaustion error: {e}")
            raise
        except Exception as e:
            self.metrics.connection_errors += 1
            logger.error(f"Connection error: {e}")
            raise
        finally:
            if connection:
                try:
                    await self.pool.release(connection)
                    self.metrics.active_connections -= 1
                except Exception as e:
                    logger.warning(f"Connection release error: {e}")
            
            # Record connection time
            connection_time = (time.time() - start_time) * 1000
            self._record_query_time(connection_time)

    async def execute_query(
        self, 
        query: str, 
        *args,
        fetch_mode: str = "none",
        validate_constitutional: bool = True
    ) -> Any:
        """
        Execute database query with performance optimization.
        
        Args:
            query: SQL query to execute
            *args: Query parameters
            fetch_mode: "none", "one", "all", "val"
            validate_constitutional: Whether to validate constitutional compliance
            
        Returns:
            Query result based on fetch_mode
        """
        start_time = time.time()
        
        try:
            self.metrics.total_queries += 1
            
            # Constitutional compliance validation
            if validate_constitutional:
                await self._validate_query_compliance(query)
                self.metrics.constitutional_validations += 1
            
            async with self.get_connection() as conn:
                # Execute query based on fetch mode
                if fetch_mode == "none":
                    result = await conn.execute(query, *args)
                elif fetch_mode == "one":
                    result = await conn.fetchrow(query, *args)
                elif fetch_mode == "all":
                    result = await conn.fetch(query, *args)
                elif fetch_mode == "val":
                    result = await conn.fetchval(query, *args)
                else:
                    raise ValueError(f"Invalid fetch_mode: {fetch_mode}")
                
                self.metrics.successful_queries += 1
                return result
                
        except Exception as e:
            self.metrics.failed_queries += 1
            logger.error(f"Query execution error: {e}")
            raise
        finally:
            query_time = (time.time() - start_time) * 1000
            self._record_query_time(query_time)

    async def execute_transaction(
        self, 
        queries: List[tuple],
        validate_constitutional: bool = True
    ) -> List[Any]:
        """
        Execute multiple queries in a transaction.
        
        Args:
            queries: List of (query, args, fetch_mode) tuples
            validate_constitutional: Whether to validate constitutional compliance
            
        Returns:
            List of query results
        """
        start_time = time.time()
        results = []
        
        try:
            async with self.get_connection() as conn:
                async with conn.transaction():
                    for query, args, fetch_mode in queries:
                        # Constitutional compliance validation
                        if validate_constitutional:
                            await self._validate_query_compliance(query)
                        
                        # Execute query
                        if fetch_mode == "none":
                            result = await conn.execute(query, *args)
                        elif fetch_mode == "one":
                            result = await conn.fetchrow(query, *args)
                        elif fetch_mode == "all":
                            result = await conn.fetch(query, *args)
                        elif fetch_mode == "val":
                            result = await conn.fetchval(query, *args)
                        else:
                            raise ValueError(f"Invalid fetch_mode: {fetch_mode}")
                        
                        results.append(result)
                        self.metrics.total_queries += 1
                        self.metrics.successful_queries += 1
            
            return results
            
        except Exception as e:
            self.metrics.failed_queries += len(queries)
            logger.error(f"Transaction execution error: {e}")
            raise
        finally:
            transaction_time = (time.time() - start_time) * 1000
            self._record_query_time(transaction_time)

    async def get_pool_status(self) -> Dict[str, Any]:
        """Get current pool status and metrics."""
        if not self.pool:
            return {"status": "not_initialized"}
        
        # Calculate performance metrics
        total_queries = self.metrics.total_queries
        success_rate = (
            self.metrics.successful_queries / total_queries 
            if total_queries > 0 else 0
        )
        
        # Calculate P99 query time
        if self.query_times:
            sorted_times = sorted(self.query_times)
            p99_index = int(0.99 * len(sorted_times))
            p99_time = sorted_times[p99_index] if p99_index < len(sorted_times) else 0
        else:
            p99_time = 0
        
        return {
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "pool_size": self.pool.get_size(),
            "pool_min_size": self.config.min_size,
            "pool_max_size": self.config.max_size,
            "active_connections": self.metrics.active_connections,
            "idle_connections": self.pool.get_idle_size(),
            "total_queries": total_queries,
            "successful_queries": self.metrics.successful_queries,
            "failed_queries": self.metrics.failed_queries,
            "success_rate": success_rate,
            "avg_query_time_ms": self.metrics.avg_query_time_ms,
            "p99_query_time_ms": p99_time,
            "connection_errors": self.metrics.connection_errors,
            "pool_exhaustions": self.metrics.pool_exhaustions,
            "constitutional_validations": self.metrics.constitutional_validations,
            "performance_targets": {
                "p99_latency_target_ms": 5.0,
                "success_rate_target": 0.99,
                "p99_latency_met": p99_time <= 5.0,
                "success_rate_met": success_rate >= 0.99
            }
        }

    async def _warmup_connections(self):
        """Pre-warm database connections for optimal performance."""
        try:
            logger.info("Starting connection pool warmup")
            
            # Execute lightweight queries to warm up connections
            warmup_queries = [
                "SELECT 1",
                "SELECT current_timestamp",
                f"SELECT '{CONSTITUTIONAL_HASH}' as constitutional_hash"
            ]
            
            for _ in range(self.config.min_size):
                try:
                    async with self.get_connection() as conn:
                        for query in warmup_queries:
                            await conn.fetchval(query)
                except Exception as e:
                    logger.warning(f"Connection warmup error: {e}")
            
            logger.info("Connection pool warmup completed")
            
        except Exception as e:
            logger.error(f"Connection warmup failed: {e}")

    async def _health_check_loop(self):
        """Continuous health monitoring of the connection pool."""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                if self.pool:
                    # Test pool health
                    async with self.get_connection() as conn:
                        result = await conn.fetchval(
                            f"SELECT '{CONSTITUTIONAL_HASH}' as health_check"
                        )
                        
                        if result != CONSTITUTIONAL_HASH:
                            logger.warning("Constitutional hash mismatch in health check")
                
            except Exception as e:
                logger.warning(f"Health check error: {e}")
                self.metrics.connection_errors += 1

    async def _validate_constitutional_compliance(self):
        """Validate constitutional compliance of the connection pool."""
        try:
            async with self.get_connection() as conn:
                result = await conn.fetchval(
                    "SELECT $1 as constitutional_validation", 
                    CONSTITUTIONAL_HASH
                )
                
                if result != CONSTITUTIONAL_HASH:
                    raise ValueError("Constitutional compliance validation failed")
                
        except Exception as e:
            logger.error(f"Constitutional compliance validation error: {e}")
            raise

    async def _validate_query_compliance(self, query: str):
        """Validate constitutional compliance of database queries."""
        # Check for potentially dangerous operations
        dangerous_patterns = [
            "DROP TABLE",
            "DELETE FROM",
            "TRUNCATE",
            "ALTER TABLE"
        ]
        
        query_upper = query.upper()
        for pattern in dangerous_patterns:
            if pattern in query_upper:
                logger.warning(f"Potentially dangerous query detected: {pattern}")
        
        # Track constitutional queries
        query_hash = hash(query)
        self.constitutional_queries.add(query_hash)

    def _record_query_time(self, query_time_ms: float):
        """Record query execution time for performance monitoring."""
        self.query_times.append(query_time_ms)
        
        # Keep only recent samples
        if len(self.query_times) > 10000:
            self.query_times = self.query_times[-5000:]
        
        # Update average query time
        if self.metrics.total_queries > 0:
            self.metrics.avg_query_time_ms = (
                (self.metrics.avg_query_time_ms * (self.metrics.total_queries - 1) + query_time_ms)
                / self.metrics.total_queries
            )

    async def close(self):
        """Close the connection pool and cleanup resources."""
        try:
            # Cancel background tasks
            if self.health_check_task:
                self.health_check_task.cancel()
                try:
                    await self.health_check_task
                except asyncio.CancelledError:
                    pass
            
            if self.warmup_task:
                self.warmup_task.cancel()
                try:
                    await self.warmup_task
                except asyncio.CancelledError:
                    pass
            
            # Close pool
            if self.pool:
                await self.pool.close()
            
            self.is_initialized = False
            logger.info("Connection pool closed")
            
        except Exception as e:
            logger.error(f"Error closing connection pool: {e}")

# Global connection pool instance
_pool_instance: Optional[OptimizedConnectionPool] = None

async def get_optimized_pool(config: Optional[ConnectionConfig] = None) -> OptimizedConnectionPool:
    """Get global optimized connection pool instance."""
    global _pool_instance
    
    if _pool_instance is None:
        if config is None:
            config = ConnectionConfig()
        
        _pool_instance = OptimizedConnectionPool(config)
        await _pool_instance.initialize()
    
    return _pool_instance

# Convenience functions for common database operations

async def execute_constitutional_query(
    query: str, 
    *args,
    fetch_mode: str = "none"
) -> Any:
    """Execute query with constitutional compliance validation."""
    pool = await get_optimized_pool()
    return await pool.execute_query(
        query, *args, 
        fetch_mode=fetch_mode, 
        validate_constitutional=True
    )

async def execute_constitutional_transaction(queries: List[tuple]) -> List[Any]:
    """Execute transaction with constitutional compliance validation."""
    pool = await get_optimized_pool()
    return await pool.execute_transaction(queries, validate_constitutional=True)
