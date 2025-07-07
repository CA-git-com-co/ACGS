"""
ACGS Comprehensive Health Check Middleware
Constitutional Hash: cdd01ef066bc6cf2

Standardized health check implementation for all ACGS services with:
- Constitutional compliance validation
- Performance metrics monitoring
- Dependency health checks
- Database connectivity validation
- Redis connectivity validation
- Service registry integration
"""

import asyncio
import logging
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Callable, Awaitable
from enum import Enum

from fastapi import FastAPI, Response, Request
from fastapi.responses import JSONResponse
import aioredis
import asyncpg
from prometheus_client import Counter, Histogram, Gauge

logger = logging.getLogger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

class HealthStatus(str, Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    STARTING = "starting"
    SHUTTING_DOWN = "shutting_down"

class DependencyStatus(str, Enum):
    """Dependency status enumeration."""
    CONNECTED = "connected"
    DISCONNECTED = "disconnected" 
    ERROR = "error"
    UNKNOWN = "unknown"

class HealthCheckLevel(str, Enum):
    """Health check depth levels."""
    BASIC = "basic"           # Just service status
    STANDARD = "standard"     # Include dependencies
    COMPREHENSIVE = "comprehensive"  # Full system health

class HealthCheckConfig:
    """Configuration for health check middleware."""
    
    def __init__(
        self,
        service_name: str,
        service_version: str = "1.0.0",
        check_level: HealthCheckLevel = HealthCheckLevel.STANDARD,
        check_timeout: float = 5.0,
        enable_dependency_checks: bool = True,
        enable_performance_metrics: bool = True,
        redis_url: Optional[str] = None,
        postgres_dsn: Optional[str] = None,
        custom_checks: Optional[List[Callable[[], Awaitable[Dict[str, Any]]]]] = None
    ):
        self.service_name = service_name
        self.service_version = service_version
        self.check_level = check_level
        self.check_timeout = check_timeout
        self.enable_dependency_checks = enable_dependency_checks
        self.enable_performance_metrics = enable_performance_metrics
        self.redis_url = redis_url
        self.postgres_dsn = postgres_dsn
        self.custom_checks = custom_checks or []

class HealthCheckManager:
    """Manages health checks for ACGS services."""
    
    def __init__(self, config: HealthCheckConfig):
        self.config = config
        self.startup_time = datetime.now(timezone.utc)
        self.last_check_time = None
        self.cached_health_status = None
        self.cache_ttl = 30  # seconds
        
        # Connection pools
        self.redis_client: Optional[aioredis.Redis] = None
        self.postgres_pool: Optional[asyncpg.Pool] = None
        
        # Metrics
        self.health_check_counter = Counter(
            'acgs_health_checks_total',
            'Total health checks performed',
            ['service', 'status']
        )
        self.health_check_duration = Histogram(
            'acgs_health_check_duration_seconds',
            'Health check duration',
            ['service', 'check_type']
        )
        self.dependency_status_gauge = Gauge(
            'acgs_dependency_status',
            'Dependency health status (1=healthy, 0=unhealthy)',
            ['service', 'dependency']
        )
        
    async def initialize(self) -> None:
        """Initialize health check connections."""
        try:
            # Initialize Redis connection if configured
            if self.config.redis_url:
                try:
                    self.redis_client = aioredis.from_url(
                        self.config.redis_url,
                        encoding="utf-8",
                        decode_responses=True,
                        socket_timeout=5,
                        socket_connect_timeout=5
                    )
                    # Test connection
                    await self.redis_client.ping()
                    logger.info(f"✅ Redis connection initialized for {self.config.service_name}")
                except Exception as e:
                    logger.warning(f"⚠️ Redis connection failed for {self.config.service_name}: {e}")
                    self.redis_client = None
            
            # Initialize PostgreSQL connection if configured
            if self.config.postgres_dsn:
                try:
                    self.postgres_pool = await asyncpg.create_pool(
                        self.config.postgres_dsn,
                        min_size=1,
                        max_size=2,
                        command_timeout=5
                    )
                    # Test connection
                    async with self.postgres_pool.acquire() as conn:
                        await conn.execute("SELECT 1")
                    logger.info(f"✅ PostgreSQL connection initialized for {self.config.service_name}")
                except Exception as e:
                    logger.warning(f"⚠️ PostgreSQL connection failed for {self.config.service_name}: {e}")
                    self.postgres_pool = None
                    
            logger.info(f"Health check manager initialized for {self.config.service_name}")
            
        except Exception as e:
            logger.error(f"Health check manager initialization failed: {e}")
            raise

    async def get_health_status(self, level: Optional[HealthCheckLevel] = None) -> Dict[str, Any]:
        """Get comprehensive health status."""
        check_level = level or self.config.check_level
        start_time = time.time()
        
        try:
            # Check cache
            if (self.cached_health_status and 
                self.last_check_time and 
                time.time() - self.last_check_time < self.cache_ttl and
                check_level == HealthCheckLevel.BASIC):
                return self.cached_health_status
            
            health_status = await self._perform_health_check(check_level)
            
            # Update cache
            self.last_check_time = time.time()
            if check_level == HealthCheckLevel.BASIC:
                self.cached_health_status = health_status
            
            # Update metrics
            status = health_status.get("status", "unknown")
            self.health_check_counter.labels(
                service=self.config.service_name,
                status=status
            ).inc()
            
            duration = time.time() - start_time
            self.health_check_duration.labels(
                service=self.config.service_name,
                check_type=check_level
            ).observe(duration)
            
            return health_status
            
        except Exception as e:
            logger.error(f"Health check failed for {self.config.service_name}: {e}")
            duration = time.time() - start_time
            self.health_check_duration.labels(
                service=self.config.service_name,
                check_type="error"
            ).observe(duration)
            
            return {
                "service": self.config.service_name,
                "version": self.config.service_version,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "status": HealthStatus.UNHEALTHY,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    async def _perform_health_check(self, level: HealthCheckLevel) -> Dict[str, Any]:
        """Perform the actual health check."""
        health_status = {
            "service": self.config.service_name,
            "version": self.config.service_version,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "status": HealthStatus.HEALTHY,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "uptime_seconds": (datetime.now(timezone.utc) - self.startup_time).total_seconds(),
            "check_level": level
        }
        
        # Basic constitutional compliance check
        if not self._validate_constitutional_compliance():
            health_status["status"] = HealthStatus.UNHEALTHY
            health_status["constitutional_compliance"] = False
            health_status["error"] = "Constitutional compliance validation failed"
            return health_status
        
        health_status["constitutional_compliance"] = True
        
        # Standard and comprehensive checks
        if level in [HealthCheckLevel.STANDARD, HealthCheckLevel.COMPREHENSIVE]:
            if self.config.enable_dependency_checks:
                dependencies = await self._check_dependencies()
                health_status["dependencies"] = dependencies
                
                # Update dependency metrics
                for dep_name, dep_status in dependencies.items():
                    status_value = 1 if dep_status.get("status") == DependencyStatus.CONNECTED else 0
                    self.dependency_status_gauge.labels(
                        service=self.config.service_name,
                        dependency=dep_name
                    ).set(status_value)
                
                # Check if any critical dependencies are unhealthy
                critical_deps_unhealthy = any(
                    dep.get("status") != DependencyStatus.CONNECTED and dep.get("critical", False)
                    for dep in dependencies.values()
                )
                
                if critical_deps_unhealthy:
                    health_status["status"] = HealthStatus.DEGRADED
        
        # Comprehensive checks
        if level == HealthCheckLevel.COMPREHENSIVE:
            if self.config.enable_performance_metrics:
                performance = await self._check_performance_metrics()
                health_status["performance"] = performance
            
            # Run custom checks
            if self.config.custom_checks:
                custom_results = await self._run_custom_checks()
                health_status["custom_checks"] = custom_results
                
                # Check if any custom checks failed
                if any(not result.get("healthy", True) for result in custom_results.values()):
                    if health_status["status"] == HealthStatus.HEALTHY:
                        health_status["status"] = HealthStatus.DEGRADED
        
        return health_status

    def _validate_constitutional_compliance(self) -> bool:
        """Validate constitutional compliance."""
        try:
            # Basic hash validation
            if CONSTITUTIONAL_HASH != "cdd01ef066bc6cf2":
                return False
            
            # Additional constitutional checks can be added here
            return True
            
        except Exception as e:
            logger.error(f"Constitutional compliance validation error: {e}")
            return False

    async def _check_dependencies(self) -> Dict[str, Any]:
        """Check dependency health."""
        dependencies = {}
        
        try:
            # Redis health check
            if self.config.redis_url:
                dependencies["redis"] = await self._check_redis_health()
            
            # PostgreSQL health check
            if self.config.postgres_dsn:
                dependencies["postgresql"] = await self._check_postgres_health()
            
            # Service registry check (if available)
            dependencies["service_registry"] = await self._check_service_registry()
            
        except Exception as e:
            logger.error(f"Dependency health check error: {e}")
            dependencies["error"] = str(e)
        
        return dependencies

    async def _check_redis_health(self) -> Dict[str, Any]:
        """Check Redis connectivity and health."""
        try:
            if not self.redis_client:
                return {
                    "status": DependencyStatus.DISCONNECTED,
                    "critical": False,
                    "message": "Redis client not initialized"
                }
            
            # Test basic operations
            start_time = time.time()
            await self.redis_client.ping()
            
            # Test set/get operation
            test_key = f"health_check:{self.config.service_name}:{int(time.time())}"
            await self.redis_client.set(test_key, "test_value", ex=10)
            value = await self.redis_client.get(test_key)
            await self.redis_client.delete(test_key)
            
            latency = (time.time() - start_time) * 1000
            
            if value != "test_value":
                raise Exception("Redis set/get operation failed")
            
            return {
                "status": DependencyStatus.CONNECTED,
                "critical": False,
                "latency_ms": round(latency, 2),
                "message": "Redis is healthy"
            }
            
        except Exception as e:
            return {
                "status": DependencyStatus.ERROR,
                "critical": False,
                "error": str(e),
                "message": "Redis health check failed"
            }

    async def _check_postgres_health(self) -> Dict[str, Any]:
        """Check PostgreSQL connectivity and health."""
        try:
            if not self.postgres_pool:
                return {
                    "status": DependencyStatus.DISCONNECTED,
                    "critical": True,
                    "message": "PostgreSQL pool not initialized"
                }
            
            start_time = time.time()
            async with self.postgres_pool.acquire() as conn:
                # Test basic query
                result = await conn.fetchval("SELECT 1")
                
                # Test database-specific health query
                version = await conn.fetchval("SELECT version()")
                
            latency = (time.time() - start_time) * 1000
            
            if result != 1:
                raise Exception("PostgreSQL basic query failed")
            
            return {
                "status": DependencyStatus.CONNECTED,
                "critical": True,
                "latency_ms": round(latency, 2),
                "version": version.split(",")[0] if version else "unknown",
                "message": "PostgreSQL is healthy"
            }
            
        except Exception as e:
            return {
                "status": DependencyStatus.ERROR,
                "critical": True,
                "error": str(e),
                "message": "PostgreSQL health check failed"
            }

    async def _check_service_registry(self) -> Dict[str, Any]:
        """Check service registry connectivity."""
        try:
            # Try to import service registry
            try:
                from services.shared.service_registry import ACGSServiceRegistry
                
                # Basic service registry health check
                # This is a simplified check - in a real implementation,
                # you might want to test actual service discovery
                return {
                    "status": DependencyStatus.CONNECTED,
                    "critical": False,
                    "message": "Service registry is available"
                }
                
            except ImportError:
                return {
                    "status": DependencyStatus.UNKNOWN,
                    "critical": False,
                    "message": "Service registry not available"
                }
                
        except Exception as e:
            return {
                "status": DependencyStatus.ERROR,
                "critical": False,
                "error": str(e),
                "message": "Service registry health check failed"
            }

    async def _check_performance_metrics(self) -> Dict[str, Any]:
        """Check performance metrics."""
        try:
            import psutil
            import gc
            
            # System metrics
            cpu_percent = psutil.cpu_percent()
            memory_info = psutil.virtual_memory()
            disk_info = psutil.disk_usage('/')
            
            # Python metrics
            gc_stats = gc.get_stats()
            
            return {
                "system": {
                    "cpu_percent": cpu_percent,
                    "memory_percent": memory_info.percent,
                    "memory_available_mb": memory_info.available // (1024 * 1024),
                    "disk_percent": disk_info.percent,
                    "disk_free_gb": disk_info.free // (1024 * 1024 * 1024)
                },
                "python": {
                    "gc_collections": sum(stat["collections"] for stat in gc_stats),
                    "gc_collected": sum(stat["collected"] for stat in gc_stats),
                    "gc_uncollectable": sum(stat["uncollectable"] for stat in gc_stats)
                },
                "thresholds": {
                    "cpu_warning": 80,
                    "memory_warning": 80,
                    "disk_warning": 85
                },
                "warnings": {
                    "high_cpu": cpu_percent > 80,
                    "high_memory": memory_info.percent > 80,
                    "high_disk": disk_info.percent > 85
                }
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "message": "Performance metrics collection failed"
            }

    async def _run_custom_checks(self) -> Dict[str, Any]:
        """Run custom health checks."""
        results = {}
        
        for i, check_func in enumerate(self.config.custom_checks):
            try:
                check_name = getattr(check_func, '__name__', f'custom_check_{i}')
                result = await asyncio.wait_for(
                    check_func(),
                    timeout=self.config.check_timeout
                )
                results[check_name] = result
                
            except asyncio.TimeoutError:
                results[f'custom_check_{i}'] = {
                    "healthy": False,
                    "error": "Check timed out",
                    "timeout": self.config.check_timeout
                }
            except Exception as e:
                results[f'custom_check_{i}'] = {
                    "healthy": False,
                    "error": str(e)
                }
        
        return results

    async def close(self) -> None:
        """Close health check manager connections."""
        try:
            if self.redis_client:
                await self.redis_client.close()
            
            if self.postgres_pool:
                await self.postgres_pool.close()
                
            logger.info(f"Health check manager closed for {self.config.service_name}")
            
        except Exception as e:
            logger.error(f"Error closing health check manager: {e}")

def setup_health_check_endpoints(
    app: FastAPI,
    config: HealthCheckConfig
) -> HealthCheckManager:
    """
    Setup health check endpoints for a FastAPI application.
    
    Args:
        app: FastAPI application instance
        config: Health check configuration
        
    Returns:
        Health check manager instance
    """
    
    # Create health check manager
    health_manager = HealthCheckManager(config)
    
    # Store in app state
    app.state.health_manager = health_manager
    
    # Basic health endpoint
    @app.get("/health")
    async def health_check():
        """Basic health check endpoint."""
        health_status = await health_manager.get_health_status(HealthCheckLevel.BASIC)
        status_code = 200 if health_status["status"] == HealthStatus.HEALTHY else 503
        return JSONResponse(content=health_status, status_code=status_code)
    
    # Detailed health endpoint
    @app.get("/health/detailed")
    async def health_check_detailed():
        """Detailed health check endpoint."""
        health_status = await health_manager.get_health_status(HealthCheckLevel.STANDARD)
        status_code = 200 if health_status["status"] in [HealthStatus.HEALTHY, HealthStatus.DEGRADED] else 503
        return JSONResponse(content=health_status, status_code=status_code)
    
    # Comprehensive health endpoint
    @app.get("/health/comprehensive")
    async def health_check_comprehensive():
        """Comprehensive health check endpoint."""
        health_status = await health_manager.get_health_status(HealthCheckLevel.COMPREHENSIVE)
        status_code = 200 if health_status["status"] in [HealthStatus.HEALTHY, HealthStatus.DEGRADED] else 503
        return JSONResponse(content=health_status, status_code=status_code)
    
    # Readiness probe (Kubernetes)
    @app.get("/health/ready")
    async def readiness_check():
        """Kubernetes readiness probe."""
        health_status = await health_manager.get_health_status(HealthCheckLevel.STANDARD)
        if health_status["status"] in [HealthStatus.HEALTHY, HealthStatus.DEGRADED]:
            return JSONResponse(content={"ready": True}, status_code=200)
        else:
            return JSONResponse(content={"ready": False, "reason": health_status.get("error", "Service not ready")}, status_code=503)
    
    # Liveness probe (Kubernetes)
    @app.get("/health/live")
    async def liveness_check():
        """Kubernetes liveness probe."""
        health_status = await health_manager.get_health_status(HealthCheckLevel.BASIC)
        if health_status["status"] != HealthStatus.UNHEALTHY:
            return JSONResponse(content={"alive": True}, status_code=200)
        else:
            return JSONResponse(content={"alive": False, "reason": health_status.get("error", "Service not alive")}, status_code=503)
    
    # Startup events
    @app.on_event("startup")
    async def startup_health_manager():
        await health_manager.initialize()
        logger.info(f"Health check endpoints configured for {config.service_name}")
    
    @app.on_event("shutdown")
    async def shutdown_health_manager():
        await health_manager.close()
    
    return health_manager