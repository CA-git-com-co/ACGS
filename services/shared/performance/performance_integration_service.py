"""
Performance Integration Service
Constitutional Hash: cdd01ef066bc6cf2

Centralized service that integrates all performance optimizations:
- Ultra-fast constitutional validation
- Advanced connection pooling
- Multi-tier caching
- Real-time performance monitoring
- Automated optimization

This service orchestrates all performance components to achieve <5ms P99 latency.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import threading

from services.shared.constitutional.validation import UltraFastConstitutionalValidator
from services.shared.database.ultra_fast_connection_pool import (
    UltraFastConnectionPoolManager,
    get_pool_manager
)
from services.shared.performance.ultra_fast_cache import (
    UltraFastMultiTierCache,
    get_ultra_fast_cache
)

# Performance targets
INTEGRATION_PERFORMANCE_TARGETS = {
    "p99_latency_ms": 5.0,
    "p95_latency_ms": 2.0,
    "p50_latency_ms": 1.0,
    "min_throughput_rps": 1000,
    "cache_hit_rate_target": 0.95,
    "constitutional_compliance": 1.0,
    "optimization_interval_s": 60,  # Optimize every minute
    "monitoring_interval_s": 30,    # Monitor every 30 seconds
}

# Constitutional hash constant
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics."""
    
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    
    constitutional_validations: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    db_connections_acquired: int = 0
    
    optimization_runs: int = 0
    last_optimization: float = 0.0
    
    def add_request(self, response_time: float, success: bool = True) -> None:
        """Add request metrics."""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        self.total_response_time += response_time
        self.min_response_time = min(self.min_response_time, response_time)
        self.max_response_time = max(self.max_response_time, response_time)
    
    def get_avg_response_time_ms(self) -> float:
        """Get average response time in milliseconds."""
        if self.total_requests == 0:
            return 0.0
        return (self.total_response_time / self.total_requests) * 1000
    
    def get_success_rate(self) -> float:
        """Get request success rate."""
        if self.total_requests == 0:
            return 1.0
        return self.successful_requests / self.total_requests
    
    def get_cache_hit_rate(self) -> float:
        """Get cache hit rate."""
        total_cache_requests = self.cache_hits + self.cache_misses
        if total_cache_requests == 0:
            return 0.0
        return self.cache_hits / total_cache_requests


class PerformanceIntegrationService:
    """
    Centralized performance integration service.
    
    Features:
    - Orchestrates all performance components
    - Real-time performance monitoring
    - Automated optimization
    - Constitutional compliance validation
    - Performance regression detection
    """
    
    def __init__(self):
        # Core components
        self.constitutional_validator = UltraFastConstitutionalValidator()
        self.pool_manager: Optional[UltraFastConnectionPoolManager] = None
        self.cache: Optional[UltraFastMultiTierCache] = None
        
        # Performance tracking
        self.metrics = PerformanceMetrics()
        self.metrics_lock = threading.RLock()
        
        # Monitoring and optimization
        self._monitoring_task: Optional[asyncio.Task] = None
        self._optimization_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Performance history for regression detection
        self.performance_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000
        
        # Constitutional compliance
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        logger.info(f"PerformanceIntegrationService initialized with constitutional_hash: {self.constitutional_hash}")
    
    async def initialize(self) -> None:
        """Initialize all performance components."""
        try:
            # Validate constitutional compliance
            if not self.constitutional_validator.validate_hash(self.constitutional_hash):
                raise RuntimeError(f"Constitutional compliance violation: {self.constitutional_hash}")
            
            # Initialize connection pool manager
            self.pool_manager = await get_pool_manager()
            
            # Initialize cache
            self.cache = await get_ultra_fast_cache()
            
            # Start monitoring and optimization
            self._running = True
            await self._start_background_tasks()
            
            logger.info("PerformanceIntegrationService fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize PerformanceIntegrationService: {e}")
            raise
    
    async def _start_background_tasks(self) -> None:
        """Start background monitoring and optimization tasks."""
        if not self._running:
            return
        
        # Start monitoring task
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        # Start optimization task
        self._optimization_task = asyncio.create_task(self._optimization_loop())
        
        logger.info("Background performance tasks started")
    
    async def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while self._running:
            try:
                await self._collect_performance_metrics()
                await asyncio.sleep(INTEGRATION_PERFORMANCE_TARGETS["monitoring_interval_s"])
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(30)
    
    async def _optimization_loop(self) -> None:
        """Background optimization loop."""
        while self._running:
            try:
                await self._run_optimization()
                await asyncio.sleep(INTEGRATION_PERFORMANCE_TARGETS["optimization_interval_s"])
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}")
                await asyncio.sleep(60)
    
    async def _collect_performance_metrics(self) -> None:
        """Collect metrics from all performance components."""
        try:
            current_metrics = {
                "timestamp": time.time(),
                "constitutional_hash": self.constitutional_hash
            }
            
            # Collect constitutional validator metrics
            if self.constitutional_validator:
                validator_metrics = self.constitutional_validator.get_detailed_metrics()
                current_metrics["constitutional_validator"] = validator_metrics
            
            # Collect connection pool metrics
            if self.pool_manager:
                pool_health = await self.pool_manager.health_check_all()
                current_metrics["connection_pools"] = pool_health
            
            # Collect cache metrics
            if self.cache:
                cache_metrics = self.cache.get_performance_metrics()
                current_metrics["cache"] = cache_metrics
            
            # Collect integration metrics
            with self.metrics_lock:
                current_metrics["integration"] = {
                    "total_requests": self.metrics.total_requests,
                    "success_rate": self.metrics.get_success_rate(),
                    "avg_response_time_ms": self.metrics.get_avg_response_time_ms(),
                    "cache_hit_rate": self.metrics.get_cache_hit_rate(),
                    "constitutional_validations": self.metrics.constitutional_validations
                }
            
            # Store in history
            self.performance_history.append(current_metrics)
            
            # Limit history size
            if len(self.performance_history) > self.max_history_size:
                self.performance_history = self.performance_history[-self.max_history_size:]
            
            # Check for performance regressions
            await self._check_performance_regression(current_metrics)
            
        except Exception as e:
            logger.error(f"Error collecting performance metrics: {e}")
    
    async def _run_optimization(self) -> None:
        """Run optimization on all performance components."""
        try:
            optimizations_applied = []
            
            # Optimize constitutional validator
            if self.constitutional_validator:
                validator_opt = self.constitutional_validator.optimize_performance()
                if validator_opt["optimizations_applied"]:
                    optimizations_applied.extend(validator_opt["optimizations_applied"])
            
            # Optimize connection pools
            if self.pool_manager:
                pool_opt = await self.pool_manager.optimize_all_pools()
                for pool_name, opt_result in pool_opt["pool_optimizations"].items():
                    if opt_result["optimizations_applied"]:
                        optimizations_applied.extend([f"{pool_name}: {opt}" for opt in opt_result["optimizations_applied"]])
            
            # Optimize cache
            if self.cache:
                cache_opt = await self.cache.optimize_performance()
                if cache_opt["optimizations_applied"]:
                    optimizations_applied.extend(cache_opt["optimizations_applied"])
            
            # Update optimization metrics
            with self.metrics_lock:
                self.metrics.optimization_runs += 1
                self.metrics.last_optimization = time.time()
            
            if optimizations_applied:
                logger.info(f"Applied optimizations: {optimizations_applied}")
            
        except Exception as e:
            logger.error(f"Error running optimization: {e}")
    
    async def _check_performance_regression(self, current_metrics: Dict[str, Any]) -> None:
        """Check for performance regressions."""
        if len(self.performance_history) < 10:
            return  # Need more history
        
        try:
            # Get recent average performance
            recent_metrics = self.performance_history[-10:]
            
            # Check response time regression
            recent_avg_times = [
                m.get("integration", {}).get("avg_response_time_ms", 0)
                for m in recent_metrics
            ]
            
            if recent_avg_times:
                recent_avg = sum(recent_avg_times) / len(recent_avg_times)
                current_avg = current_metrics.get("integration", {}).get("avg_response_time_ms", 0)
                
                # Alert if current performance is 50% worse than recent average
                if current_avg > recent_avg * 1.5 and current_avg > INTEGRATION_PERFORMANCE_TARGETS["p95_latency_ms"]:
                    logger.warning(
                        f"Performance regression detected: "
                        f"Current avg response time {current_avg:.2f}ms vs recent avg {recent_avg:.2f}ms"
                    )
            
        except Exception as e:
            logger.error(f"Error checking performance regression: {e}")
    
    async def process_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a request with full performance optimization.
        
        Args:
            request_data: Request data to process
            
        Returns:
            Processed response with performance metrics
        """
        start_time = time.perf_counter()
        
        try:
            # 1. Constitutional validation
            is_valid = self.constitutional_validator.validate_hash(self.constitutional_hash)
            if not is_valid:
                raise ValueError("Constitutional compliance violation")
            
            with self.metrics_lock:
                self.metrics.constitutional_validations += 1
            
            # 2. Cache lookup
            cache_key = f"request:{hash(str(sorted(request_data.items())))}"
            cached_result = None
            
            if self.cache:
                cached_result = await self.cache.get(cache_key, data_type="request")
                if cached_result:
                    with self.metrics_lock:
                        self.metrics.cache_hits += 1
                else:
                    with self.metrics_lock:
                        self.metrics.cache_misses += 1
            
            # 3. Process request if not cached
            if cached_result is None:
                # Simulate processing with database connection if needed
                if self.pool_manager and "database_operation" in request_data:
                    try:
                        pool = await self.pool_manager.get_pool("default")
                        conn = await pool.acquire_connection()
                        # Simulate database operation
                        await asyncio.sleep(0.001)  # 1ms simulation
                        await pool.release_connection(conn)
                        
                        with self.metrics_lock:
                            self.metrics.db_connections_acquired += 1
                    except Exception as e:
                        logger.warning(f"Database operation failed: {e}")
                
                # Create response
                response = {
                    "processed": True,
                    "timestamp": time.time(),
                    "constitutional_hash": self.constitutional_hash,
                    "request_id": request_data.get("id", "unknown")
                }
                
                # Cache the response
                if self.cache:
                    await self.cache.set(cache_key, response, ttl=300, data_type="request")
            else:
                response = cached_result
            
            # 4. Record performance metrics
            elapsed = time.perf_counter() - start_time
            with self.metrics_lock:
                self.metrics.add_request(elapsed, success=True)
            
            # Add performance metadata to response
            response["performance"] = {
                "response_time_ms": elapsed * 1000,
                "cached": cached_result is not None,
                "constitutional_validated": True
            }
            
            return response
            
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            with self.metrics_lock:
                self.metrics.add_request(elapsed, success=False)
            
            logger.error(f"Error processing request: {e}")
            raise
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        with self.metrics_lock:
            integration_metrics = {
                "total_requests": self.metrics.total_requests,
                "success_rate": self.metrics.get_success_rate(),
                "avg_response_time_ms": self.metrics.get_avg_response_time_ms(),
                "cache_hit_rate": self.metrics.get_cache_hit_rate(),
                "constitutional_validations": self.metrics.constitutional_validations,
                "optimization_runs": self.metrics.optimization_runs
            }
        
        summary = {
            "integration_metrics": integration_metrics,
            "performance_targets": INTEGRATION_PERFORMANCE_TARGETS,
            "targets_met": {
                "response_time": integration_metrics["avg_response_time_ms"] < INTEGRATION_PERFORMANCE_TARGETS["p95_latency_ms"],
                "success_rate": integration_metrics["success_rate"] >= 0.99,
                "cache_hit_rate": integration_metrics["cache_hit_rate"] >= INTEGRATION_PERFORMANCE_TARGETS["cache_hit_rate_target"]
            },
            "constitutional_hash": self.constitutional_hash,
            "timestamp": time.time()
        }
        
        # Add component metrics if available
        if self.constitutional_validator:
            summary["constitutional_validator"] = self.constitutional_validator.get_detailed_metrics()
        
        if self.cache:
            summary["cache"] = self.cache.get_performance_metrics()
        
        if self.pool_manager:
            summary["connection_pools"] = await self.pool_manager.health_check_all()
        
        return summary
    
    async def close(self) -> None:
        """Close the performance integration service."""
        self._running = False
        
        # Cancel background tasks
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
        
        if self._optimization_task:
            self._optimization_task.cancel()
            try:
                await self._optimization_task
            except asyncio.CancelledError:
                pass
        
        # Close components
        if self.cache:
            await self.cache.close()
        
        if self.pool_manager:
            await self.pool_manager.close_all()
        
        logger.info("PerformanceIntegrationService closed")


# Global performance service instance
_performance_service: Optional[PerformanceIntegrationService] = None


async def get_performance_service() -> PerformanceIntegrationService:
    """Get the global performance integration service."""
    global _performance_service
    if _performance_service is None:
        _performance_service = PerformanceIntegrationService()
        await _performance_service.initialize()
    return _performance_service
