"""
Database and Caching Performance Optimizer
Constitutional Hash: cdd01ef066bc6cf2

Optimizations for PostgreSQL (5440) and Redis (6390) to achieve P99 <5ms latency.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

import asyncpg
import aioredis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import QueuePool

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class OptimizedDatabaseConfig:
    """Optimized database configuration for >100 RPS performance."""
    
    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # PostgreSQL optimization settings
        self.postgresql_config = {
            "host": "localhost",
            "port": 5440,
            "database": "acgs_db",
            "user": "acgs_user",
            "password": "acgs_password",
            
            # Connection pool optimization for >100 RPS
            "pool_size": 50,  # Increased from 10-20
            "max_overflow": 20,  # Increased from 5-10
            "pool_timeout": 10,  # Reduced from 20
            "pool_recycle": 1800,  # 30 minutes
            "pool_pre_ping": True,
            
            # Performance settings
            "connect_args": {
                "server_settings": {
                    "jit": "off",  # Disable JIT for consistent latency
                    "shared_preload_libraries": "pg_stat_statements",
                    "max_connections": "200",
                    "shared_buffers": "256MB",
                    "effective_cache_size": "1GB",
                    "work_mem": "4MB",
                    "maintenance_work_mem": "64MB",
                    "checkpoint_completion_target": "0.9",
                    "wal_buffers": "16MB",
                    "default_statistics_target": "100"
                }
            }
        }
        
        # Redis optimization settings
        self.redis_config = {
            "host": "localhost",
            "port": 6390,
            "db": 0,
            "password": "redis_password",
            
            # Connection pool optimization
            "connection_pool_size": 50,  # Increased from 10
            "max_connections": 100,
            "retry_on_timeout": True,
            "socket_keepalive": True,
            "socket_keepalive_options": {},
            
            # Performance settings
            "decode_responses": False,  # Faster binary operations
            "encoding": "utf-8",
            "socket_connect_timeout": 5,
            "socket_timeout": 5,
        }


class HighPerformanceConnectionPool:
    """High-performance connection pool manager."""
    
    def __init__(self, config: OptimizedDatabaseConfig):
        self.config = config
        self.postgresql_engine = None
        self.redis_pool = None
        self.performance_metrics = {
            "postgresql_connections_active": 0,
            "redis_connections_active": 0,
            "avg_connection_time_ms": 0.0,
            "total_connections": 0
        }
        self.constitutional_hash = CONSTITUTIONAL_HASH
    
    async def initialize(self):
        """Initialize optimized connection pools."""
        # PostgreSQL engine with optimized settings
        database_url = (
            f"postgresql+asyncpg://"
            f"{self.config.postgresql_config['user']}:"
            f"{self.config.postgresql_config['password']}@"
            f"{self.config.postgresql_config['host']}:"
            f"{self.config.postgresql_config['port']}/"
            f"{self.config.postgresql_config['database']}"
        )
        
        self.postgresql_engine = create_async_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=self.config.postgresql_config["pool_size"],
            max_overflow=self.config.postgresql_config["max_overflow"],
            pool_timeout=self.config.postgresql_config["pool_timeout"],
            pool_recycle=self.config.postgresql_config["pool_recycle"],
            pool_pre_ping=self.config.postgresql_config["pool_pre_ping"],
            echo=False,  # Disable SQL logging for performance
            future=True
        )
        
        # Redis connection pool
        self.redis_pool = aioredis.ConnectionPool.from_url(
            f"redis://:{self.config.redis_config['password']}@"
            f"{self.config.redis_config['host']}:"
            f"{self.config.redis_config['port']}/"
            f"{self.config.redis_config['db']}",
            max_connections=self.config.redis_config["connection_pool_size"],
            retry_on_timeout=self.config.redis_config["retry_on_timeout"],
            socket_keepalive=self.config.redis_config["socket_keepalive"],
            socket_connect_timeout=self.config.redis_config["socket_connect_timeout"],
            socket_timeout=self.config.redis_config["socket_timeout"]
        )
    
    @asynccontextmanager
    async def get_postgresql_session(self):
        """Get optimized PostgreSQL session with performance tracking."""
        start_time = time.perf_counter()
        
        async with AsyncSession(self.postgresql_engine) as session:
            try:
                self.performance_metrics["postgresql_connections_active"] += 1
                yield session
            finally:
                self.performance_metrics["postgresql_connections_active"] -= 1
                connection_time = (time.perf_counter() - start_time) * 1000
                self._update_connection_metrics(connection_time)
    
    @asynccontextmanager
    async def get_redis_client(self):
        """Get optimized Redis client with performance tracking."""
        start_time = time.perf_counter()
        
        redis_client = aioredis.Redis(connection_pool=self.redis_pool)
        try:
            self.performance_metrics["redis_connections_active"] += 1
            yield redis_client
        finally:
            self.performance_metrics["redis_connections_active"] -= 1
            await redis_client.close()
            connection_time = (time.perf_counter() - start_time) * 1000
            self._update_connection_metrics(connection_time)
    
    def _update_connection_metrics(self, connection_time_ms: float):
        """Update connection performance metrics."""
        self.performance_metrics["total_connections"] += 1
        total_time = (
            self.performance_metrics["avg_connection_time_ms"] * 
            (self.performance_metrics["total_connections"] - 1) + 
            connection_time_ms
        )
        self.performance_metrics["avg_connection_time_ms"] = (
            total_time / self.performance_metrics["total_connections"]
        )
    
    async def get_performance_metrics(self) -> dict:
        """Get connection pool performance metrics."""
        return {
            **self.performance_metrics,
            "constitutional_hash": self.constitutional_hash,
            "postgresql_pool_size": self.config.postgresql_config["pool_size"],
            "redis_pool_size": self.config.redis_config["connection_pool_size"]
        }


class OptimizedCacheManager:
    """High-performance cache manager with multi-tier strategy."""
    
    def __init__(self, redis_pool):
        self.redis_pool = redis_pool
        self.local_cache: Dict[str, Any] = {}  # L1 cache
        self.cache_stats = {
            "l1_hits": 0,
            "l2_hits": 0,
            "misses": 0,
            "total_requests": 0
        }
        self.constitutional_hash = CONSTITUTIONAL_HASH
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value with L1/L2 cache strategy."""
        self.cache_stats["total_requests"] += 1
        
        # L1 Cache: Local memory (fastest)
        if key in self.local_cache:
            self.cache_stats["l1_hits"] += 1
            return self.local_cache[key]
        
        # L2 Cache: Redis
        async with aioredis.Redis(connection_pool=self.redis_pool) as redis:
            try:
                value = await redis.get(key)
                if value:
                    self.cache_stats["l2_hits"] += 1
                    # Promote to L1 cache
                    self.local_cache[key] = value
                    return value
            except Exception:
                pass  # Cache miss
        
        self.cache_stats["misses"] += 1
        return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in both cache tiers."""
        # L1 Cache
        self.local_cache[key] = value
        
        # L2 Cache
        async with aioredis.Redis(connection_pool=self.redis_pool) as redis:
            try:
                await redis.setex(key, ttl, value)
            except Exception:
                pass  # Cache write failure
    
    def get_cache_hit_rate(self) -> float:
        """Calculate cache hit rate."""
        total_hits = self.cache_stats["l1_hits"] + self.cache_stats["l2_hits"]
        return total_hits / max(1, self.cache_stats["total_requests"])
    
    def get_cache_stats(self) -> dict:
        """Get detailed cache statistics."""
        return {
            **self.cache_stats,
            "hit_rate": self.get_cache_hit_rate(),
            "constitutional_hash": self.constitutional_hash
        }


# Usage example for ACGS services
async def setup_optimized_database_infrastructure():
    """Setup optimized database infrastructure for ACGS services."""
    config = OptimizedDatabaseConfig()
    connection_pool = HighPerformanceConnectionPool(config)
    await connection_pool.initialize()
    
    cache_manager = OptimizedCacheManager(connection_pool.redis_pool)
    
    return connection_pool, cache_manager


# Performance monitoring configuration
DATABASE_PERFORMANCE_TARGETS = {
    "postgresql_connection_time_ms": 2.0,  # Target <2ms connection time
    "redis_connection_time_ms": 1.0,      # Target <1ms connection time
    "cache_hit_rate_target": 0.85,        # Target >85% cache hit rate
    "concurrent_connections_target": 100,  # Support >100 concurrent connections
    "constitutional_hash": CONSTITUTIONAL_HASH
}
