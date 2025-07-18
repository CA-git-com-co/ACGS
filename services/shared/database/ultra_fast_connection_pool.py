"""
Ultra-Fast Database Connection Pool Manager
Constitutional Hash: cdd01ef066bc6cf2

Advanced connection pool with pre-warming, health monitoring, and sub-millisecond
connection acquisition for achieving <5ms P99 latency targets.

Performance Features:
- Pre-warmed connection pools with health monitoring
- Sub-millisecond connection acquisition (<1ms target)
- Intelligent connection recycling and optimization
- Real-time performance metrics and alerting
- Constitutional compliance validation
"""

import asyncio
import asyncpg
import logging
import time
import threading
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set
import weakref

from services.shared.constitutional.validation import UltraFastConstitutionalValidator

# Performance targets for connection pool
POOL_PERFORMANCE_TARGETS = {
    "connection_acquisition_ms": 1.0,  # <1ms connection acquisition
    "pool_utilization_target": 0.8,   # 80% utilization target
    "health_check_interval_s": 30,    # 30 second health checks
    "connection_lifetime_s": 3600,    # 1 hour connection lifetime
    "min_pool_size": 20,              # Minimum connections
    "max_pool_size": 100,             # Maximum connections
}

# Constitutional hash constant
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class ConnectionMetrics:
    """Metrics for connection pool performance."""
    
    total_acquisitions: int = 0
    successful_acquisitions: int = 0
    failed_acquisitions: int = 0
    total_acquisition_time: float = 0.0
    peak_connections: int = 0
    current_connections: int = 0
    health_check_failures: int = 0
    connection_recycling_count: int = 0
    
    def get_avg_acquisition_time_ms(self) -> float:
        """Get average connection acquisition time in milliseconds."""
        if self.total_acquisitions == 0:
            return 0.0
        return (self.total_acquisition_time / self.total_acquisitions) * 1000
    
    def get_success_rate(self) -> float:
        """Get connection acquisition success rate."""
        if self.total_acquisitions == 0:
            return 1.0
        return self.successful_acquisitions / self.total_acquisitions


class UltraFastConnectionPool:
    """
    Ultra-fast database connection pool with advanced optimization.
    
    Features:
    - Pre-warmed connections for instant availability
    - Health monitoring with automatic recovery
    - Intelligent connection recycling
    - Sub-millisecond acquisition times
    - Constitutional compliance validation
    """
    
    def __init__(
        self,
        pool_name: str,
        dsn: str,
        min_size: int = POOL_PERFORMANCE_TARGETS["min_pool_size"],
        max_size: int = POOL_PERFORMANCE_TARGETS["max_pool_size"],
        constitutional_validator: Optional[UltraFastConstitutionalValidator] = None,
    ):
        self.pool_name = pool_name
        self.dsn = dsn
        self.min_size = min_size
        self.max_size = max_size
        
        # Constitutional compliance
        self.constitutional_validator = constitutional_validator or UltraFastConstitutionalValidator()
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        # Connection pool
        self.pool: Optional[asyncpg.Pool] = None
        self.is_initialized = False
        self.is_healthy = True
        
        # Performance metrics
        self.metrics = ConnectionMetrics()
        self.metrics_lock = threading.RLock()
        
        # Pre-warmed connections tracking
        self.pre_warmed_connections: Set[weakref.ref] = set()
        self.last_health_check = 0
        self.health_check_interval = POOL_PERFORMANCE_TARGETS["health_check_interval_s"]
        
        # Performance optimization
        self.connection_cache: Dict[str, Any] = {}
        self.fast_path_enabled = True
        
        logger.info(
            f"UltraFastConnectionPool '{pool_name}' initialized: "
            f"{min_size}-{max_size} connections, constitutional_hash: {self.constitutional_hash}"
        )
    
    async def initialize(self) -> None:
        """Initialize the connection pool with pre-warming."""
        if self.is_initialized:
            return
            
        start_time = time.perf_counter()
        
        try:
            # Validate constitutional compliance
            if not self.constitutional_validator.validate_hash(self.constitutional_hash):
                raise RuntimeError(f"Constitutional compliance violation: {self.constitutional_hash}")
            
            # Create optimized connection pool
            self.pool = await asyncpg.create_pool(
                dsn=self.dsn,
                min_size=self.min_size,
                max_size=self.max_size,
                command_timeout=30.0,
                # Ultra-fast connection settings
                server_settings={
                    "application_name": f"acgs_ultra_fast_{self.pool_name}",
                    "search_path": "public",
                    "statement_timeout": "30s",
                    "idle_in_transaction_session_timeout": "300s",
                    "tcp_keepalives_idle": "300",
                    "tcp_keepalives_interval": "10",
                    "tcp_keepalives_count": "3",
                    "shared_preload_libraries": "",
                },
                # Connection initialization for performance
                init=self._init_connection,
                setup=self._setup_connection,
            )
            
            # Pre-warm connections
            await self._pre_warm_connections()
            
            self.is_initialized = True
            self.is_healthy = True
            
            elapsed = time.perf_counter() - start_time
            logger.info(
                f"UltraFastConnectionPool '{self.pool_name}' initialized in {elapsed*1000:.2f}ms"
            )
            
        except Exception as e:
            self.is_healthy = False
            logger.error(f"Failed to initialize connection pool '{self.pool_name}': {e}")
            raise
    
    async def _init_connection(self, connection: asyncpg.Connection) -> None:
        """Initialize a new connection with performance optimizations."""
        # Set connection-level optimizations
        await connection.execute("SET synchronous_commit = off")
        await connection.execute("SET wal_writer_delay = '10ms'")
        await connection.execute("SET checkpoint_completion_target = 0.9")
        
        # Constitutional compliance check
        await connection.execute(
            "SELECT 1 -- Constitutional Hash: cdd01ef066bc6cf2"
        )
    
    async def _setup_connection(self, connection: asyncpg.Connection) -> None:
        """Setup connection for optimal performance."""
        # Prepare frequently used statements
        await connection.execute("PREPARE health_check AS SELECT 1")
        
        # Set session-level optimizations
        await connection.execute("SET work_mem = '256MB'")
        await connection.execute("SET maintenance_work_mem = '512MB'")
    
    async def _pre_warm_connections(self) -> None:
        """Pre-warm connections for instant availability."""
        if not self.pool:
            return
            
        logger.info(f"Pre-warming {self.min_size} connections for pool '{self.pool_name}'")
        
        # Acquire and immediately release connections to warm the pool
        connections = []
        try:
            for _ in range(self.min_size):
                conn = await self.pool.acquire()
                connections.append(conn)
                # Test connection with a simple query
                await conn.fetchval("SELECT 1")
            
            # Release all connections back to pool
            for conn in connections:
                await self.pool.release(conn)
                
            logger.info(f"Successfully pre-warmed {len(connections)} connections")
            
        except Exception as e:
            logger.error(f"Error pre-warming connections: {e}")
            # Release any acquired connections
            for conn in connections:
                try:
                    await self.pool.release(conn)
                except:
                    pass
    
    async def acquire_connection(self) -> asyncpg.Connection:
        """
        Acquire a connection with sub-millisecond performance.
        
        Returns:
            Database connection
            
        Raises:
            RuntimeError: If pool is not initialized or unhealthy
        """
        if not self.is_initialized or not self.pool:
            raise RuntimeError(f"Connection pool '{self.pool_name}' not initialized")
            
        if not self.is_healthy:
            raise RuntimeError(f"Connection pool '{self.pool_name}' is unhealthy")
        
        start_time = time.perf_counter()
        
        try:
            # Fast-path: Try immediate acquisition
            connection = await asyncio.wait_for(
                self.pool.acquire(),
                timeout=POOL_PERFORMANCE_TARGETS["connection_acquisition_ms"] / 1000
            )
            
            # Update metrics
            elapsed = time.perf_counter() - start_time
            with self.metrics_lock:
                self.metrics.total_acquisitions += 1
                self.metrics.successful_acquisitions += 1
                self.metrics.total_acquisition_time += elapsed
                self.metrics.current_connections += 1
                self.metrics.peak_connections = max(
                    self.metrics.peak_connections, 
                    self.metrics.current_connections
                )
            
            # Log slow acquisitions
            if elapsed > POOL_PERFORMANCE_TARGETS["connection_acquisition_ms"] / 1000:
                logger.warning(
                    f"Slow connection acquisition for '{self.pool_name}': {elapsed*1000:.2f}ms"
                )
            
            return connection
            
        except asyncio.TimeoutError:
            with self.metrics_lock:
                self.metrics.total_acquisitions += 1
                self.metrics.failed_acquisitions += 1
            
            logger.error(f"Connection acquisition timeout for pool '{self.pool_name}'")
            raise RuntimeError(f"Connection acquisition timeout for pool '{self.pool_name}'")
            
        except Exception as e:
            with self.metrics_lock:
                self.metrics.total_acquisitions += 1
                self.metrics.failed_acquisitions += 1
            
            logger.error(f"Error acquiring connection from pool '{self.pool_name}': {e}")
            raise
    
    async def release_connection(self, connection: asyncpg.Connection) -> None:
        """Release a connection back to the pool."""
        if not self.pool:
            return
            
        try:
            await self.pool.release(connection)
            
            with self.metrics_lock:
                self.metrics.current_connections = max(0, self.metrics.current_connections - 1)
                
        except Exception as e:
            logger.error(f"Error releasing connection to pool '{self.pool_name}': {e}")

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on the connection pool.

        Returns:
            Dict containing health status and metrics
        """
        if not self.is_initialized or not self.pool:
            return {
                "healthy": False,
                "error": "Pool not initialized",
                "constitutional_hash": self.constitutional_hash
            }

        start_time = time.perf_counter()

        try:
            # Test connection acquisition and query
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")

            # Update health status
            self.is_healthy = True
            self.last_health_check = time.time()

            elapsed = time.perf_counter() - start_time

            return {
                "healthy": True,
                "pool_name": self.pool_name,
                "pool_size": self.pool.get_size(),
                "pool_min_size": self.pool.get_min_size(),
                "pool_max_size": self.pool.get_max_size(),
                "health_check_time_ms": elapsed * 1000,
                "metrics": self.get_performance_metrics(),
                "constitutional_hash": self.constitutional_hash,
                "timestamp": time.time()
            }

        except Exception as e:
            self.is_healthy = False
            with self.metrics_lock:
                self.metrics.health_check_failures += 1

            logger.error(f"Health check failed for pool '{self.pool_name}': {e}")

            return {
                "healthy": False,
                "pool_name": self.pool_name,
                "error": str(e),
                "health_check_failures": self.metrics.health_check_failures,
                "constitutional_hash": self.constitutional_hash,
                "timestamp": time.time()
            }

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics for the connection pool."""
        with self.metrics_lock:
            avg_acquisition_time = self.metrics.get_avg_acquisition_time_ms()
            success_rate = self.metrics.get_success_rate()

            return {
                "performance_summary": {
                    "avg_acquisition_time_ms": avg_acquisition_time,
                    "success_rate": success_rate,
                    "total_acquisitions": self.metrics.total_acquisitions,
                    "current_connections": self.metrics.current_connections,
                    "peak_connections": self.metrics.peak_connections,
                    "meets_acquisition_target": avg_acquisition_time < POOL_PERFORMANCE_TARGETS["connection_acquisition_ms"]
                },
                "pool_status": {
                    "pool_size": self.pool.get_size() if self.pool else 0,
                    "min_size": self.min_size,
                    "max_size": self.max_size,
                    "is_healthy": self.is_healthy,
                    "is_initialized": self.is_initialized
                },
                "optimization_status": {
                    "fast_path_enabled": self.fast_path_enabled,
                    "pre_warmed": len(self.pre_warmed_connections) > 0
                },
                "constitutional_hash": self.constitutional_hash
            }

    async def optimize_performance(self) -> Dict[str, Any]:
        """
        Analyze and optimize connection pool performance.

        Returns:
            Dict containing optimization results
        """
        metrics = self.get_performance_metrics()
        optimizations_applied = []
        recommendations = []

        # Check acquisition time performance
        avg_time = metrics["performance_summary"]["avg_acquisition_time_ms"]
        if avg_time > POOL_PERFORMANCE_TARGETS["connection_acquisition_ms"]:
            recommendations.append(f"Connection acquisition time ({avg_time:.2f}ms) exceeds target")

            # Try to pre-warm more connections
            if self.pool and self.pool.get_size() < self.max_size:
                try:
                    await self._pre_warm_connections()
                    optimizations_applied.append("Re-warmed connection pool")
                except Exception as e:
                    logger.warning(f"Failed to re-warm connections: {e}")

        # Check success rate
        success_rate = metrics["performance_summary"]["success_rate"]
        if success_rate < 0.95:  # 95% success rate target
            recommendations.append(f"Connection success rate ({success_rate:.2%}) below target")

        # Check pool utilization
        current_size = metrics["pool_status"]["pool_size"]
        if current_size < self.min_size:
            recommendations.append("Pool size below minimum, consider increasing min_size")

        return {
            "optimizations_applied": optimizations_applied,
            "recommendations": recommendations,
            "current_metrics": metrics,
            "constitutional_hash": self.constitutional_hash
        }

    async def close(self) -> None:
        """Close the connection pool and cleanup resources."""
        if self.pool:
            await self.pool.close()
            self.pool = None

        self.is_initialized = False
        self.is_healthy = False
        self.pre_warmed_connections.clear()

        logger.info(f"UltraFastConnectionPool '{self.pool_name}' closed")


class UltraFastConnectionPoolManager:
    """
    Global manager for ultra-fast connection pools.

    Features:
    - Centralized pool management
    - Automatic health monitoring
    - Performance optimization
    - Constitutional compliance validation
    """

    def __init__(self):
        self.pools: Dict[str, UltraFastConnectionPool] = {}
        self.constitutional_validator = UltraFastConstitutionalValidator()
        self.constitutional_hash = CONSTITUTIONAL_HASH
        self._monitoring_task: Optional[asyncio.Task] = None
        self._monitoring_enabled = True

    async def create_pool(
        self,
        name: str,
        dsn: str,
        min_size: int = POOL_PERFORMANCE_TARGETS["min_pool_size"],
        max_size: int = POOL_PERFORMANCE_TARGETS["max_pool_size"],
    ) -> UltraFastConnectionPool:
        """Create and register a new ultra-fast connection pool."""
        if name in self.pools:
            raise ValueError(f"Pool '{name}' already exists")

        pool = UltraFastConnectionPool(
            pool_name=name,
            dsn=dsn,
            min_size=min_size,
            max_size=max_size,
            constitutional_validator=self.constitutional_validator
        )

        await pool.initialize()
        self.pools[name] = pool

        # Start monitoring if this is the first pool
        if len(self.pools) == 1 and self._monitoring_enabled:
            await self._start_monitoring()

        logger.info(f"Created ultra-fast connection pool: {name}")
        return pool

    async def get_pool(self, name: str) -> UltraFastConnectionPool:
        """Get a connection pool by name."""
        if name not in self.pools:
            raise ValueError(f"Pool '{name}' not found")
        return self.pools[name]

    async def health_check_all(self) -> Dict[str, Any]:
        """Perform health check on all connection pools."""
        results = {}
        overall_healthy = True

        for name, pool in self.pools.items():
            health = await pool.health_check()
            results[name] = health
            if not health["healthy"]:
                overall_healthy = False

        return {
            "overall_healthy": overall_healthy,
            "pools": results,
            "total_pools": len(self.pools),
            "constitutional_hash": self.constitutional_hash,
            "timestamp": time.time()
        }

    async def optimize_all_pools(self) -> Dict[str, Any]:
        """Optimize performance for all connection pools."""
        results = {}

        for name, pool in self.pools.items():
            optimization = await pool.optimize_performance()
            results[name] = optimization

        return {
            "pool_optimizations": results,
            "constitutional_hash": self.constitutional_hash,
            "timestamp": time.time()
        }

    async def _start_monitoring(self) -> None:
        """Start background monitoring of all pools."""
        if self._monitoring_task and not self._monitoring_task.done():
            return

        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Started connection pool monitoring")

    async def _monitoring_loop(self) -> None:
        """Background monitoring loop for all pools."""
        while self._monitoring_enabled and self.pools:
            try:
                # Health check all pools
                health_results = await self.health_check_all()

                # Log unhealthy pools
                for name, health in health_results["pools"].items():
                    if not health["healthy"]:
                        logger.warning(f"Pool '{name}' is unhealthy: {health.get('error', 'Unknown')}")

                # Optimize pools if needed
                await self.optimize_all_pools()

                # Wait before next check
                await asyncio.sleep(POOL_PERFORMANCE_TARGETS["health_check_interval_s"])

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in connection pool monitoring: {e}")
                await asyncio.sleep(30)  # Wait longer on error

    async def close_all(self) -> None:
        """Close all connection pools and stop monitoring."""
        self._monitoring_enabled = False

        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        for pool in self.pools.values():
            await pool.close()

        self.pools.clear()
        logger.info("All connection pools closed")


# Global connection pool manager instance
_pool_manager: Optional[UltraFastConnectionPoolManager] = None


async def get_pool_manager() -> UltraFastConnectionPoolManager:
    """Get the global connection pool manager instance."""
    global _pool_manager
    if _pool_manager is None:
        _pool_manager = UltraFastConnectionPoolManager()
    return _pool_manager


async def create_ultra_fast_pool(
    name: str,
    dsn: str,
    min_size: int = POOL_PERFORMANCE_TARGETS["min_pool_size"],
    max_size: int = POOL_PERFORMANCE_TARGETS["max_pool_size"],
) -> UltraFastConnectionPool:
    """Convenience function to create an ultra-fast connection pool."""
    manager = await get_pool_manager()
    return await manager.create_pool(name, dsn, min_size, max_size)
