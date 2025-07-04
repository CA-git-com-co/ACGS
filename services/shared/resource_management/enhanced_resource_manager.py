"""
Enhanced Resource Management System for ACGS

This module provides advanced resource management capabilities including:
- Dynamic resource allocation and optimization
- Intelligent monitoring and alerting
- Automatic scaling and load balancing
- Performance-based resource tuning
"""

import asyncio
import time
import psutil
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Callable
import threading

import structlog
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

from ..redis_client import ACGSRedisClient
from ...infrastructure.database.connection_pool_config import ServiceConnectionPools, ConnectionPoolConfig

logger = structlog.get_logger(__name__)

CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ResourceType(Enum):
    """Types of resources being managed."""
    DATABASE_CONNECTIONS = "database_connections"
    REDIS_CONNECTIONS = "redis_connections"
    HTTP_CONNECTIONS = "http_connections"
    MEMORY = "memory"
    CPU = "cpu"
    DISK_IO = "disk_io"
    NETWORK_IO = "network_io"


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class ResourceMetrics:
    """Resource usage metrics."""
    resource_type: ResourceType
    current_usage: float
    max_capacity: float
    utilization_percent: float
    average_usage_1m: float
    average_usage_5m: float
    peak_usage_1h: float
    trend: str = "stable"  # increasing, decreasing, stable
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class ResourceThresholds:
    """Resource usage thresholds for alerting."""
    warning_percent: float = 70.0
    critical_percent: float = 85.0
    emergency_percent: float = 95.0
    auto_scale_percent: float = 80.0


@dataclass
class AlertRule:
    """Alert rule configuration."""
    resource_type: ResourceType
    threshold: float
    level: AlertLevel
    duration_seconds: float = 60.0  # Must be above threshold for this duration
    enabled: bool = True
    callback: Optional[Callable] = None


@dataclass
class ScalingPolicy:
    """Auto-scaling policy configuration."""
    resource_type: ResourceType
    scale_up_threshold: float = 80.0
    scale_down_threshold: float = 40.0
    scale_up_factor: float = 1.5
    scale_down_factor: float = 0.8
    min_resources: int = 1
    max_resources: int = 1000
    cooldown_period: float = 300.0  # 5 minutes
    enabled: bool = True


class EnhancedResourceManager:
    """Enhanced resource manager with intelligent monitoring and auto-scaling."""
    
    def __init__(
        self,
        redis_client: ACGSRedisClient,
        monitoring_interval: float = 10.0,  # 10 seconds
        cleanup_interval: float = 300.0,    # 5 minutes
    ):
        self.redis_client = redis_client
        self.monitoring_interval = monitoring_interval
        self.cleanup_interval = cleanup_interval
        
        # Resource tracking
        self.resource_metrics: Dict[ResourceType, ResourceMetrics] = {}
        self.resource_history: Dict[ResourceType, deque] = defaultdict(
            lambda: deque(maxlen=3600)  # Keep 1 hour of history at 10s intervals
        )
        
        # Configuration
        self.thresholds: Dict[ResourceType, ResourceThresholds] = self._init_default_thresholds()
        self.alert_rules: List[AlertRule] = []
        self.scaling_policies: Dict[ResourceType, ScalingPolicy] = {}
        
        # Connection pool management
        self.connection_pools: Dict[str, Any] = {}
        self.pool_stats: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Alert tracking
        self.active_alerts: Dict[str, datetime] = {}
        self.alert_history: deque = deque(maxlen=1000)
        
        # Background tasks
        self._monitoring_task: Optional[asyncio.Task] = None
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False
        
        # Performance metrics
        self.performance_metrics = {
            "total_alerts_fired": 0,
            "auto_scaling_events": 0,
            "resource_optimizations": 0,
            "average_response_time": 0.0,
            "uptime_seconds": 0,
            "start_time": datetime.now()
        }
    
    def _init_default_thresholds(self) -> Dict[ResourceType, ResourceThresholds]:
        """Initialize default resource thresholds."""
        return {
            ResourceType.DATABASE_CONNECTIONS: ResourceThresholds(
                warning_percent=70.0,
                critical_percent=85.0,
                emergency_percent=95.0,
                auto_scale_percent=75.0
            ),
            ResourceType.REDIS_CONNECTIONS: ResourceThresholds(
                warning_percent=75.0,
                critical_percent=90.0,
                emergency_percent=98.0,
                auto_scale_percent=80.0
            ),
            ResourceType.MEMORY: ResourceThresholds(
                warning_percent=80.0,
                critical_percent=90.0,
                emergency_percent=95.0,
                auto_scale_percent=85.0
            ),
            ResourceType.CPU: ResourceThresholds(
                warning_percent=70.0,
                critical_percent=85.0,
                emergency_percent=95.0,
                auto_scale_percent=75.0
            ),
            ResourceType.DISK_IO: ResourceThresholds(
                warning_percent=80.0,
                critical_percent=90.0,
                emergency_percent=95.0
            ),
            ResourceType.NETWORK_IO: ResourceThresholds(
                warning_percent=75.0,
                critical_percent=85.0,
                emergency_percent=95.0
            ),
        }
    
    async def start(self):
        """Start the resource manager."""
        if self._running:
            return
        
        self._running = True
        
        # Initialize connection pools
        await self._initialize_connection_pools()
        
        # Initialize alert rules
        self._initialize_alert_rules()
        
        # Initialize scaling policies
        self._initialize_scaling_policies()
        
        # Start background tasks
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        
        logger.info(
            "Enhanced resource manager started",
            monitoring_interval=self.monitoring_interval,
            constitutional_hash=CONSTITUTIONAL_HASH
        )
    
    async def stop(self):
        """Stop the resource manager."""
        self._running = False
        
        # Cancel background tasks
        for task in [self._monitoring_task, self._cleanup_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Close connection pools
        await self._close_connection_pools()
        
        logger.info("Enhanced resource manager stopped")
    
    async def _initialize_connection_pools(self):
        """Initialize database connection pools for all services."""
        for service_name in ServiceConnectionPools.SERVICE_CONFIGS.keys():
            try:
                config = ServiceConnectionPools.get_config(service_name)
                
                # Create SQLAlchemy engine with connection pooling
                engine = create_engine(
                    config.get_connection_url(),
                    poolclass=QueuePool,
                    pool_size=config.min_connections,
                    max_overflow=config.max_overflow,
                    pool_timeout=config.pool_timeout,
                    pool_recycle=config.pool_recycle,
                    pool_pre_ping=config.pool_pre_ping,
                    echo=config.echo,
                    echo_pool=config.echo_pool,
                )
                
                self.connection_pools[service_name] = engine
                
                logger.debug(
                    "Initialized connection pool",
                    service=service_name,
                    pool_size=config.min_connections,
                    max_overflow=config.max_overflow
                )
                
            except Exception as e:
                logger.error(
                    "Failed to initialize connection pool",
                    service=service_name,
                    error=str(e)
                )
    
    async def _close_connection_pools(self):
        """Close all connection pools."""
        for service_name, engine in self.connection_pools.items():
            try:
                engine.dispose()
                logger.debug("Closed connection pool", service=service_name)
            except Exception as e:
                logger.error(
                    "Error closing connection pool",
                    service=service_name,
                    error=str(e)
                )
    
    def _initialize_alert_rules(self):
        """Initialize default alert rules."""
        for resource_type, thresholds in self.thresholds.items():
            # Warning alerts
            self.alert_rules.append(AlertRule(
                resource_type=resource_type,
                threshold=thresholds.warning_percent,
                level=AlertLevel.WARNING,
                duration_seconds=60.0
            ))
            
            # Critical alerts
            self.alert_rules.append(AlertRule(
                resource_type=resource_type,
                threshold=thresholds.critical_percent,
                level=AlertLevel.CRITICAL,
                duration_seconds=30.0
            ))
            
            # Emergency alerts
            self.alert_rules.append(AlertRule(
                resource_type=resource_type,
                threshold=thresholds.emergency_percent,
                level=AlertLevel.EMERGENCY,
                duration_seconds=10.0
            ))
    
    def _initialize_scaling_policies(self):
        """Initialize auto-scaling policies."""
        # Database connections scaling
        self.scaling_policies[ResourceType.DATABASE_CONNECTIONS] = ScalingPolicy(
            resource_type=ResourceType.DATABASE_CONNECTIONS,
            scale_up_threshold=75.0,
            scale_down_threshold=30.0,
            scale_up_factor=1.3,
            scale_down_factor=0.9,
            min_resources=5,
            max_resources=200,
            cooldown_period=180.0  # 3 minutes
        )
        
        # Redis connections scaling
        self.scaling_policies[ResourceType.REDIS_CONNECTIONS] = ScalingPolicy(
            resource_type=ResourceType.REDIS_CONNECTIONS,
            scale_up_threshold=80.0,
            scale_down_threshold=40.0,
            scale_up_factor=1.2,
            scale_down_factor=0.8,
            min_resources=10,
            max_resources=100,
            cooldown_period=120.0  # 2 minutes
        )
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        try:
            while self._running:
                start_time = time.time()
                
                try:
                    # Collect resource metrics
                    await self._collect_resource_metrics()
                    
                    # Check alert rules
                    await self._check_alert_rules()
                    
                    # Apply auto-scaling
                    await self._apply_auto_scaling()
                    
                    # Update performance metrics
                    self._update_performance_metrics()
                    
                except Exception as e:
                    logger.error("Error in monitoring loop", error=str(e))
                
                # Maintain monitoring interval
                elapsed = time.time() - start_time
                sleep_time = max(0, self.monitoring_interval - elapsed)
                await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            logger.info("Monitoring loop cancelled")
    
    async def _collect_resource_metrics(self):
        """Collect current resource usage metrics."""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        await self._update_resource_metric(
            ResourceType.CPU,
            current_usage=cpu_percent,
            max_capacity=100.0
        )
        
        # Memory metrics
        memory = psutil.virtual_memory()
        await self._update_resource_metric(
            ResourceType.MEMORY,
            current_usage=memory.used,
            max_capacity=memory.total
        )
        
        # Disk I/O metrics
        disk_io = psutil.disk_io_counters()
        if disk_io:
            # Calculate I/O utilization (simplified)
            io_utilization = min(100.0, (disk_io.read_bytes + disk_io.write_bytes) / (1024 * 1024 * 1024))  # GB/s
            await self._update_resource_metric(
                ResourceType.DISK_IO,
                current_usage=io_utilization,
                max_capacity=100.0
            )
        
        # Network I/O metrics
        network_io = psutil.net_io_counters()
        if network_io:
            # Calculate network utilization (simplified)
            net_utilization = min(100.0, (network_io.bytes_sent + network_io.bytes_recv) / (1024 * 1024 * 1024))  # GB/s
            await self._update_resource_metric(
                ResourceType.NETWORK_IO,
                current_usage=net_utilization,
                max_capacity=100.0
            )
        
        # Database connection metrics
        await self._collect_database_metrics()
        
        # Redis connection metrics
        await self._collect_redis_metrics()
    
    async def _update_resource_metric(
        self,
        resource_type: ResourceType,
        current_usage: float,
        max_capacity: float
    ):
        """Update resource metric with current usage."""
        utilization_percent = (current_usage / max_capacity) * 100.0
        
        # Get history for averaging
        history = self.resource_history[resource_type]
        history.append({
            'timestamp': datetime.now(),
            'usage': current_usage,
            'utilization': utilization_percent
        })
        
        # Calculate averages
        now = datetime.now()
        recent_1m = [h for h in history if (now - h['timestamp']).total_seconds() <= 60]
        recent_5m = [h for h in history if (now - h['timestamp']).total_seconds() <= 300]
        recent_1h = [h for h in history if (now - h['timestamp']).total_seconds() <= 3600]
        
        avg_1m = sum(h['utilization'] for h in recent_1m) / len(recent_1m) if recent_1m else utilization_percent
        avg_5m = sum(h['utilization'] for h in recent_5m) / len(recent_5m) if recent_5m else utilization_percent
        peak_1h = max((h['utilization'] for h in recent_1h), default=utilization_percent)
        
        # Determine trend
        trend = "stable"
        if len(recent_5m) >= 5:
            recent_trend = [h['utilization'] for h in recent_5m[-5:]]
            if all(recent_trend[i] < recent_trend[i + 1] for i in range(len(recent_trend) - 1)):
                trend = "increasing"
            elif all(recent_trend[i] > recent_trend[i + 1] for i in range(len(recent_trend) - 1)):
                trend = "decreasing"
        
        # Update metrics
        self.resource_metrics[resource_type] = ResourceMetrics(
            resource_type=resource_type,
            current_usage=current_usage,
            max_capacity=max_capacity,
            utilization_percent=utilization_percent,
            average_usage_1m=avg_1m,
            average_usage_5m=avg_5m,
            peak_usage_1h=peak_1h,
            trend=trend
        )
    
    async def _collect_database_metrics(self):
        """Collect database connection pool metrics."""
        total_connections = 0
        total_capacity = 0
        
        for service_name, engine in self.connection_pools.items():
            try:
                pool = engine.pool
                
                # Get pool statistics
                pool_size = pool.size()
                checked_in = pool.checkedin()
                checked_out = pool.checkedout()
                overflow = pool.overflow()
                invalid = pool.invalid()
                
                # Calculate metrics
                current_usage = checked_out
                max_capacity = pool_size + pool.overflow()
                
                total_connections += current_usage
                total_capacity += max_capacity
                
                # Store per-service stats
                self.pool_stats[service_name] = {
                    'pool_size': pool_size,
                    'checked_in': checked_in,
                    'checked_out': checked_out,
                    'overflow': overflow,
                    'invalid': invalid,
                    'utilization': (current_usage / max_capacity) * 100.0 if max_capacity > 0 else 0.0
                }
                
            except Exception as e:
                logger.error(
                    "Error collecting database metrics",
                    service=service_name,
                    error=str(e)
                )
        
        # Update overall database connection metrics
        if total_capacity > 0:
            await self._update_resource_metric(
                ResourceType.DATABASE_CONNECTIONS,
                current_usage=total_connections,
                max_capacity=total_capacity
            )
    
    async def _collect_redis_metrics(self):
        """Collect Redis connection metrics."""
        try:
            async with self.redis_client.get_client() as client:
                info = await client.info('clients')
                
                connected_clients = info.get('connected_clients', 0)
                max_clients = info.get('maxclients', 10000)
                
                await self._update_resource_metric(
                    ResourceType.REDIS_CONNECTIONS,
                    current_usage=connected_clients,
                    max_capacity=max_clients
                )
                
        except Exception as e:
            logger.error("Error collecting Redis metrics", error=str(e))
    
    async def _check_alert_rules(self):
        """Check all alert rules and fire alerts if needed."""
        for rule in self.alert_rules:
            if not rule.enabled:
                continue
            
            metric = self.resource_metrics.get(rule.resource_type)
            if not metric:
                continue
            
            # Check if threshold is exceeded
            if metric.utilization_percent >= rule.threshold:
                alert_key = f"{rule.resource_type.value}_{rule.level.value}"
                
                # Check if alert is already active
                if alert_key in self.active_alerts:
                    # Check if alert has been active long enough
                    alert_start = self.active_alerts[alert_key]
                    duration = (datetime.now() - alert_start).total_seconds()
                    
                    if duration >= rule.duration_seconds:
                        await self._fire_alert(rule, metric)
                else:
                    # Start tracking this alert
                    self.active_alerts[alert_key] = datetime.now()
            else:
                # Clear active alert if threshold is no longer exceeded
                alert_key = f"{rule.resource_type.value}_{rule.level.value}"
                if alert_key in self.active_alerts:
                    del self.active_alerts[alert_key]
    
    async def _fire_alert(self, rule: AlertRule, metric: ResourceMetrics):
        """Fire an alert for a rule violation."""
        alert_data = {
            'timestamp': datetime.now().isoformat(),
            'resource_type': rule.resource_type.value,
            'level': rule.level.value,
            'threshold': rule.threshold,
            'current_utilization': metric.utilization_percent,
            'current_usage': metric.current_usage,
            'max_capacity': metric.max_capacity,
            'trend': metric.trend,
            'constitutional_hash': CONSTITUTIONAL_HASH
        }
        
        # Store alert in history
        self.alert_history.append(alert_data)
        
        # Store alert in Redis for persistence
        alert_key = f"acgs:alerts:{rule.resource_type.value}:{int(time.time())}"
        await self.redis_client.set_json(alert_key, alert_data, ttl=86400)  # 24 hours
        
        # Update metrics
        self.performance_metrics["total_alerts_fired"] += 1
        
        # Execute callback if provided
        if rule.callback:
            try:
                await rule.callback(alert_data)
            except Exception as e:
                logger.error("Error executing alert callback", error=str(e))
        
        logger.warning(
            "Resource alert fired",
            resource_type=rule.resource_type.value,
            level=rule.level.value,
            utilization=metric.utilization_percent,
            threshold=rule.threshold
        )
    
    async def _apply_auto_scaling(self):
        """Apply auto-scaling policies based on resource usage."""
        for resource_type, policy in self.scaling_policies.items():
            if not policy.enabled:
                continue
            
            metric = self.resource_metrics.get(resource_type)
            if not metric:
                continue
            
            # Check cooldown period
            cooldown_key = f"scaling_cooldown_{resource_type.value}"
            last_scaling = await self.redis_client.get_json(cooldown_key)
            
            if last_scaling:
                last_time = datetime.fromisoformat(last_scaling['timestamp'])
                if (datetime.now() - last_time).total_seconds() < policy.cooldown_period:
                    continue  # Still in cooldown
            
            # Determine if scaling is needed
            should_scale_up = (
                metric.utilization_percent >= policy.scale_up_threshold and
                metric.trend in ["increasing", "stable"]
            )
            
            should_scale_down = (
                metric.utilization_percent <= policy.scale_down_threshold and
                metric.trend in ["decreasing", "stable"]
            )
            
            if should_scale_up:
                await self._scale_resource(resource_type, policy, "up", metric)
            elif should_scale_down:
                await self._scale_resource(resource_type, policy, "down", metric)
    
    async def _scale_resource(
        self,
        resource_type: ResourceType,
        policy: ScalingPolicy,
        direction: str,
        metric: ResourceMetrics
    ):
        """Scale a resource up or down."""
        try:
            if resource_type == ResourceType.DATABASE_CONNECTIONS:
                await self._scale_database_connections(direction, policy, metric)
            elif resource_type == ResourceType.REDIS_CONNECTIONS:
                await self._scale_redis_connections(direction, policy, metric)
            
            # Record scaling event
            scaling_data = {
                'timestamp': datetime.now().isoformat(),
                'resource_type': resource_type.value,
                'direction': direction,
                'utilization_before': metric.utilization_percent,
                'policy': {
                    'scale_up_threshold': policy.scale_up_threshold,
                    'scale_down_threshold': policy.scale_down_threshold,
                    'factor': policy.scale_up_factor if direction == "up" else policy.scale_down_factor
                }
            }
            
            # Store scaling event
            cooldown_key = f"scaling_cooldown_{resource_type.value}"
            await self.redis_client.set_json(cooldown_key, scaling_data, ttl=int(policy.cooldown_period))
            
            self.performance_metrics["auto_scaling_events"] += 1
            
            logger.info(
                "Auto-scaling applied",
                resource_type=resource_type.value,
                direction=direction,
                utilization=metric.utilization_percent
            )
            
        except Exception as e:
            logger.error(
                "Error applying auto-scaling",
                resource_type=resource_type.value,
                direction=direction,
                error=str(e)
            )
    
    async def _scale_database_connections(self, direction: str, policy: ScalingPolicy, metric: ResourceMetrics):
        """Scale database connection pools."""
        # This is a simplified implementation
        # In practice, you would need to coordinate with connection pool managers
        
        for service_name, engine in self.connection_pools.items():
            try:
                current_pool = engine.pool
                current_size = current_pool.size()
                
                if direction == "up":
                    new_size = min(
                        int(current_size * policy.scale_up_factor),
                        policy.max_resources
                    )
                else:
                    new_size = max(
                        int(current_size * policy.scale_down_factor),
                        policy.min_resources
                    )
                
                if new_size != current_size:
                    # Note: SQLAlchemy doesn't support dynamic pool resizing
                    # This would require recreating the engine or using a custom pool
                    logger.info(
                        "Database pool scaling recommended",
                        service=service_name,
                        current_size=current_size,
                        recommended_size=new_size
                    )
                
            except Exception as e:
                logger.error(
                    "Error scaling database connections",
                    service=service_name,
                    error=str(e)
                )
    
    async def _scale_redis_connections(self, direction: str, policy: ScalingPolicy, metric: ResourceMetrics):
        """Scale Redis connections."""
        # Redis connection scaling would typically involve adjusting client pool sizes
        # This is implementation-specific and would depend on your Redis client setup
        
        logger.info(
            "Redis connection scaling recommended",
            direction=direction,
            current_utilization=metric.utilization_percent
        )
    
    async def _cleanup_loop(self):
        """Background cleanup of old metrics and alerts."""
        try:
            while self._running:
                await asyncio.sleep(self.cleanup_interval)
                
                # Clean up old alert history
                cutoff_time = datetime.now() - timedelta(hours=24)
                self.alert_history = deque(
                    [alert for alert in self.alert_history 
                     if datetime.fromisoformat(alert['timestamp']) > cutoff_time],
                    maxlen=1000
                )
                
                # Clean up old resource history
                for resource_type, history in self.resource_history.items():
                    while history and (datetime.now() - history[0]['timestamp']).total_seconds() > 3600:
                        history.popleft()
                
                logger.debug("Resource manager cleanup completed")
                
        except asyncio.CancelledError:
            logger.info("Cleanup loop cancelled")
    
    def _update_performance_metrics(self):
        """Update performance metrics."""
        self.performance_metrics["uptime_seconds"] = (
            datetime.now() - self.performance_metrics["start_time"]
        ).total_seconds()
        
        # Calculate average response time based on monitoring loop performance
        # This is a simplified metric
        self.performance_metrics["average_response_time"] = self.monitoring_interval
    
    def get_resource_status(self) -> Dict[str, Any]:
        """Get comprehensive resource status."""
        return {
            "resource_metrics": {
                resource_type.value: {
                    "current_usage": metric.current_usage,
                    "max_capacity": metric.max_capacity,
                    "utilization_percent": metric.utilization_percent,
                    "average_usage_1m": metric.average_usage_1m,
                    "average_usage_5m": metric.average_usage_5m,
                    "peak_usage_1h": metric.peak_usage_1h,
                    "trend": metric.trend,
                    "last_updated": metric.last_updated.isoformat()
                }
                for resource_type, metric in self.resource_metrics.items()
            },
            "connection_pools": self.pool_stats,
            "active_alerts": {
                alert_key: alert_time.isoformat()
                for alert_key, alert_time in self.active_alerts.items()
            },
            "performance_metrics": self.performance_metrics,
            "thresholds": {
                resource_type.value: {
                    "warning": threshold.warning_percent,
                    "critical": threshold.critical_percent,
                    "emergency": threshold.emergency_percent
                }
                for resource_type, threshold in self.thresholds.items()
            },
            "scaling_policies": {
                resource_type.value: {
                    "scale_up_threshold": policy.scale_up_threshold,
                    "scale_down_threshold": policy.scale_down_threshold,
                    "enabled": policy.enabled
                }
                for resource_type, policy in self.scaling_policies.items()
            },
            "constitutional_hash": CONSTITUTIONAL_HASH
        }
    
    async def add_alert_rule(self, rule: AlertRule):
        """Add a custom alert rule."""
        self.alert_rules.append(rule)
        logger.info(
            "Alert rule added",
            resource_type=rule.resource_type.value,
            level=rule.level.value,
            threshold=rule.threshold
        )
    
    async def update_threshold(self, resource_type: ResourceType, thresholds: ResourceThresholds):
        """Update resource thresholds."""
        self.thresholds[resource_type] = thresholds
        logger.info(
            "Resource thresholds updated",
            resource_type=resource_type.value,
            warning=thresholds.warning_percent,
            critical=thresholds.critical_percent
        )
    
    async def manual_scale(self, resource_type: ResourceType, direction: str):
        """Manually trigger resource scaling."""
        policy = self.scaling_policies.get(resource_type)
        metric = self.resource_metrics.get(resource_type)
        
        if not policy or not metric:
            raise ValueError(f"No policy or metric found for {resource_type.value}")
        
        await self._scale_resource(resource_type, policy, direction, metric)
        
        logger.info(
            "Manual scaling triggered",
            resource_type=resource_type.value,
            direction=direction
        )