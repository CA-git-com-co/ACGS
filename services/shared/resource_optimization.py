"""
Resource Optimization and Memory Management
==========================================

Optimized resource allocation and garbage collection for better scalability
and performance under high concurrent load.
"""

import asyncio
import gc
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any

import psutil

logger = logging.getLogger(__name__)


@dataclass
class ResourceConfig:
    """Configuration for resource optimization."""

    gc_threshold_0: int = 700  # Default: 700
    gc_threshold_1: int = 10  # Default: 10
    gc_threshold_2: int = 10  # Default: 10
    memory_limit_mb: int = 1024  # Memory limit in MB
    cpu_limit_percent: float = 80.0  # CPU usage limit
    enable_aggressive_gc: bool = True
    gc_interval_seconds: float = 30.0
    memory_check_interval: float = 10.0


class ResourceMonitor:
    """
    Monitor system resources and trigger optimizations.
    """

    def __init__(self, config: ResourceConfig = None):
        self.config = config or ResourceConfig()
        self.process = psutil.Process()
        self.start_time = time.time()

        # Resource tracking
        self.memory_usage_history = []
        self.cpu_usage_history = []
        self.gc_stats = {"collections": 0, "freed_objects": 0, "time_spent": 0}

        # Optimization flags
        self.aggressive_gc_enabled = False
        self.memory_pressure = False

        # Background tasks
        self._monitor_task = None
        self._gc_task = None

    async def start_monitoring(self):
        """Start background resource monitoring."""
        if self._monitor_task is None:
            self._monitor_task = asyncio.create_task(self._monitor_loop())
            logger.info("Resource monitoring started")

        if self._gc_task is None and self.config.enable_aggressive_gc:
            self._gc_task = asyncio.create_task(self._gc_loop())
            logger.info("Aggressive garbage collection enabled")

    async def stop_monitoring(self):
        """Stop background resource monitoring."""
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
            self._monitor_task = None

        if self._gc_task:
            self._gc_task.cancel()
            try:
                await self._gc_task
            except asyncio.CancelledError:
                pass
            self._gc_task = None

        logger.info("Resource monitoring stopped")

    async def _monitor_loop(self):
        """Background loop for resource monitoring."""
        while True:
            try:
                await self._check_resources()
                await asyncio.sleep(self.config.memory_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Resource monitoring error: {e}")
                await asyncio.sleep(5)

    async def _gc_loop(self):
        """Background loop for garbage collection."""
        while True:
            try:
                await self._perform_gc()
                await asyncio.sleep(self.config.gc_interval_seconds)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Garbage collection error: {e}")
                await asyncio.sleep(10)

    async def _check_resources(self):
        """Check current resource usage."""
        # Memory usage
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        self.memory_usage_history.append(memory_mb)

        # Keep only recent history
        if len(self.memory_usage_history) > 100:
            self.memory_usage_history = self.memory_usage_history[-50:]

        # CPU usage
        cpu_percent = self.process.cpu_percent()
        self.cpu_usage_history.append(cpu_percent)

        if len(self.cpu_usage_history) > 100:
            self.cpu_usage_history = self.cpu_usage_history[-50:]

        # Check for memory pressure
        if memory_mb > self.config.memory_limit_mb:
            if not self.memory_pressure:
                logger.warning(
                    f"Memory pressure detected: {memory_mb:.1f}MB > {self.config.memory_limit_mb}MB"
                )
                self.memory_pressure = True
                await self._handle_memory_pressure()
        else:
            self.memory_pressure = False

        # Check for high CPU usage
        if cpu_percent > self.config.cpu_limit_percent:
            logger.warning(
                f"High CPU usage: {cpu_percent:.1f}% > {self.config.cpu_limit_percent}%"
            )

    async def _handle_memory_pressure(self):
        """Handle memory pressure situations."""
        logger.info("Handling memory pressure...")

        # Force garbage collection
        await self._perform_gc(force=True)

        # Enable aggressive GC temporarily
        if not self.aggressive_gc_enabled:
            self.aggressive_gc_enabled = True
            gc.set_threshold(
                self.config.gc_threshold_0 // 2,
                self.config.gc_threshold_1 // 2,
                self.config.gc_threshold_2 // 2,
            )
            logger.info("Enabled aggressive garbage collection")

    async def _perform_gc(self, force: bool = False):
        """Perform garbage collection."""
        start_time = time.time()

        if force or self.memory_pressure:
            # Collect all generations
            collected = gc.collect()
            self.gc_stats["collections"] += 1
            self.gc_stats["freed_objects"] += collected

            if collected > 0:
                logger.debug(f"Garbage collection freed {collected} objects")
        else:
            # Normal collection
            collected = gc.collect(0)  # Only generation 0
            self.gc_stats["collections"] += 1
            self.gc_stats["freed_objects"] += collected

        gc_time = time.time() - start_time
        self.gc_stats["time_spent"] += gc_time

        # Reset aggressive GC if memory pressure is resolved
        if self.aggressive_gc_enabled and not self.memory_pressure:
            self.aggressive_gc_enabled = False
            gc.set_threshold(
                self.config.gc_threshold_0,
                self.config.gc_threshold_1,
                self.config.gc_threshold_2,
            )
            logger.info("Disabled aggressive garbage collection")

    def get_resource_stats(self) -> dict[str, Any]:
        """Get current resource statistics."""
        memory_info = self.process.memory_info()

        return {
            "memory": {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "limit_mb": self.config.memory_limit_mb,
                "pressure": self.memory_pressure,
                "avg_usage_mb": (
                    sum(self.memory_usage_history) / len(self.memory_usage_history)
                    if self.memory_usage_history
                    else 0
                ),
            },
            "cpu": {
                "current_percent": self.process.cpu_percent(),
                "limit_percent": self.config.cpu_limit_percent,
                "avg_usage_percent": (
                    sum(self.cpu_usage_history) / len(self.cpu_usage_history)
                    if self.cpu_usage_history
                    else 0
                ),
            },
            "gc": {
                **self.gc_stats,
                "aggressive_enabled": self.aggressive_gc_enabled,
                "thresholds": gc.get_threshold(),
            },
            "uptime_seconds": time.time() - self.start_time,
        }


class ResourceOptimizer:
    """
    Main resource optimization coordinator.
    """

    def __init__(self, config: ResourceConfig = None):
        self.config = config or ResourceConfig()
        self.monitor = ResourceMonitor(config)
        self._initialized = False

    async def initialize(self):
        """Initialize resource optimization."""
        if self._initialized:
            return

        # Set optimized GC thresholds
        gc.set_threshold(
            self.config.gc_threshold_0,
            self.config.gc_threshold_1,
            self.config.gc_threshold_2,
        )

        # Start monitoring
        await self.monitor.start_monitoring()

        self._initialized = True
        logger.info("Resource optimization initialized")

    async def shutdown(self):
        """Shutdown resource optimization."""
        if not self._initialized:
            return

        await self.monitor.stop_monitoring()
        self._initialized = False
        logger.info("Resource optimization shutdown")

    @asynccontextmanager
    async def optimized_context(self):
        """Context manager for optimized resource usage."""
        await self.initialize()
        try:
            yield self
        finally:
            # Cleanup after context
            gc.collect()

    def get_optimization_stats(self) -> dict[str, Any]:
        """Get optimization statistics."""
        return {
            "initialized": self._initialized,
            "config": {
                "gc_thresholds": [
                    self.config.gc_threshold_0,
                    self.config.gc_threshold_1,
                    self.config.gc_threshold_2,
                ],
                "memory_limit_mb": self.config.memory_limit_mb,
                "cpu_limit_percent": self.config.cpu_limit_percent,
                "aggressive_gc_enabled": self.config.enable_aggressive_gc,
            },
            "resource_stats": self.monitor.get_resource_stats(),
        }


# Service-specific resource configurations
SERVICE_RESOURCE_CONFIGS = {
    "ac": ResourceConfig(
        memory_limit_mb=1536,  # Higher limit for AC service
        gc_threshold_0=800,
        enable_aggressive_gc=True,
        gc_interval_seconds=20.0,
    ),
    "auth": ResourceConfig(
        memory_limit_mb=1024,
        gc_threshold_0=700,
        enable_aggressive_gc=True,
        gc_interval_seconds=25.0,
    ),
    "gs": ResourceConfig(
        memory_limit_mb=1280,
        gc_threshold_0=750,
        enable_aggressive_gc=True,
        gc_interval_seconds=30.0,
    ),
    "pgc": ResourceConfig(
        memory_limit_mb=1024,
        gc_threshold_0=700,
        enable_aggressive_gc=True,
        gc_interval_seconds=30.0,
    ),
    "integrity": ResourceConfig(
        memory_limit_mb=768,
        gc_threshold_0=600,
        enable_aggressive_gc=False,
        gc_interval_seconds=45.0,
    ),
    "fv": ResourceConfig(
        memory_limit_mb=512,
        gc_threshold_0=500,
        enable_aggressive_gc=False,
        gc_interval_seconds=60.0,
    ),
    "ec": ResourceConfig(
        memory_limit_mb=512,
        gc_threshold_0=500,
        enable_aggressive_gc=False,
        gc_interval_seconds=60.0,
    ),
}


async def setup_resource_optimization(service_name: str) -> ResourceOptimizer:
    """
    Setup resource optimization for a specific service.

    Args:
        service_name: Name of the service

    Returns:
        Configured resource optimizer
    """
    config = SERVICE_RESOURCE_CONFIGS.get(service_name, ResourceConfig())
    optimizer = ResourceOptimizer(config)
    await optimizer.initialize()

    logger.info(f"Resource optimization setup for {service_name}")
    return optimizer


# Export key components
__all__ = [
    "SERVICE_RESOURCE_CONFIGS",
    "ResourceConfig",
    "ResourceMonitor",
    "ResourceOptimizer",
    "setup_resource_optimization",
]
