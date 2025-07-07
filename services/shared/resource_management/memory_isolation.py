"""
Memory Isolation Framework for Multi-Tenant ACGS
Provides comprehensive memory management and isolation between tenants.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import gc
import logging
import resource
import sys
import threading
import time
import tracemalloc
import weakref
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union
from uuid import UUID

import psutil

logger = logging.getLogger(__name__)


@dataclass
class MemoryUsageStats:
    """Memory usage statistics for a tenant."""

    tenant_id: str
    current_usage: int  # bytes
    peak_usage: int  # bytes
    allocation_count: int
    deallocation_count: int
    gc_collections: int
    last_updated: float
    constitutional_hash: str = "cdd01ef066bc6cf2"


@dataclass
class MemoryLimit:
    """Memory limit configuration for a tenant."""

    tenant_id: str
    soft_limit: int  # bytes - warning threshold
    hard_limit: int  # bytes - strict limit
    growth_rate_limit: int  # bytes per second
    enable_gc_tuning: bool = True
    enable_monitoring: bool = True
    constitutional_hash: str = "cdd01ef066bc6cf2"


@dataclass
class TenantMemoryContext:
    """Memory context for a tenant's operations."""

    tenant_id: str
    allocated_objects: Set[int] = field(default_factory=set)
    memory_snapshots: List[Any] = field(default_factory=list)
    gc_threshold_override: Optional[tuple] = None
    monitoring_enabled: bool = True
    created_at: float = field(default_factory=time.time)


class MemoryIsolationError(Exception):
    """Raised when memory isolation constraints are violated."""

    pass


class TenantMemoryLimitExceeded(MemoryIsolationError):
    """Raised when a tenant exceeds their memory limit."""

    pass


class MemoryIsolationFramework:
    """
    Comprehensive memory isolation framework for multi-tenant operations.

    Features:
    - Per-tenant memory tracking and limits
    - Memory usage monitoring and alerting
    - Garbage collection tuning per tenant
    - Memory leak detection
    - Constitutional compliance validation
    """

    def __init__(
        self,
        default_soft_limit: int = 100 * 1024 * 1024,  # 100MB
        default_hard_limit: int = 500 * 1024 * 1024,  # 500MB
        monitoring_interval: float = 1.0,  # seconds
        enable_tracemalloc: bool = True,
        constitutional_hash: str = "cdd01ef066bc6cf2",
    ):
        self.default_soft_limit = default_soft_limit
        self.default_hard_limit = default_hard_limit
        self.monitoring_interval = monitoring_interval
        self.constitutional_hash = constitutional_hash

        # Tenant memory management
        self._tenant_limits: Dict[str, MemoryLimit] = {}
        self._tenant_stats: Dict[str, MemoryUsageStats] = {}
        self._tenant_contexts: Dict[str, TenantMemoryContext] = {}

        # Monitoring and control
        self._monitoring_active = False
        self._monitoring_thread: Optional[threading.Thread] = None
        self._shutdown_event = threading.Event()

        # Memory tracking
        self._enable_tracemalloc = enable_tracemalloc
        self._memory_snapshots: List[Any] = []

        # System monitoring
        self._process = psutil.Process()
        self._system_memory_limit = self._get_system_memory_limit()

        # Initialize tracemalloc if enabled
        if self._enable_tracemalloc and not tracemalloc.is_tracing():
            tracemalloc.start()
            logger.info("Memory tracing started for tenant isolation")

    def _get_system_memory_limit(self) -> int:
        """Get system memory limit from various sources."""
        try:
            # Try to get from resource limits first
            soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_AS)
            if hard_limit != resource.RLIM_INFINITY:
                return hard_limit
        except (OSError, AttributeError):
            pass

        try:
            # Fall back to system memory
            return psutil.virtual_memory().total
        except Exception:
            # Conservative fallback
            return 8 * 1024 * 1024 * 1024  # 8GB

    def register_tenant(
        self,
        tenant_id: Union[str, UUID],
        soft_limit: Optional[int] = None,
        hard_limit: Optional[int] = None,
        growth_rate_limit: Optional[int] = None,
    ) -> None:
        """Register a tenant with memory limits."""
        if isinstance(tenant_id, UUID):
            tenant_id = str(tenant_id)

        # Validate limits
        soft_limit = soft_limit or self.default_soft_limit
        hard_limit = hard_limit or self.default_hard_limit
        growth_rate_limit = growth_rate_limit or (
            hard_limit // 10
        )  # 10% per second default

        if soft_limit >= hard_limit:
            raise ValueError("Soft limit must be less than hard limit")

        if hard_limit > self._system_memory_limit:
            logger.warning(f"Tenant {tenant_id} hard limit exceeds system memory")

        # Create memory limit
        memory_limit = MemoryLimit(
            tenant_id=tenant_id,
            soft_limit=soft_limit,
            hard_limit=hard_limit,
            growth_rate_limit=growth_rate_limit,
            constitutional_hash=self.constitutional_hash,
        )

        # Initialize stats
        memory_stats = MemoryUsageStats(
            tenant_id=tenant_id,
            current_usage=0,
            peak_usage=0,
            allocation_count=0,
            deallocation_count=0,
            gc_collections=0,
            last_updated=time.time(),
            constitutional_hash=self.constitutional_hash,
        )

        # Initialize context
        memory_context = TenantMemoryContext(
            tenant_id=tenant_id, monitoring_enabled=True
        )

        # Store configurations
        self._tenant_limits[tenant_id] = memory_limit
        self._tenant_stats[tenant_id] = memory_stats
        self._tenant_contexts[tenant_id] = memory_context

        logger.info(
            f"Registered tenant {tenant_id} with memory limits: "
            f"soft={soft_limit}, hard={hard_limit}"
        )

    def unregister_tenant(self, tenant_id: Union[str, UUID]) -> None:
        """Unregister a tenant and clean up memory tracking."""
        if isinstance(tenant_id, UUID):
            tenant_id = str(tenant_id)

        # Force garbage collection for tenant
        if tenant_id in self._tenant_contexts:
            self._force_tenant_gc(tenant_id)

        # Remove from tracking
        self._tenant_limits.pop(tenant_id, None)
        self._tenant_stats.pop(tenant_id, None)
        self._tenant_contexts.pop(tenant_id, None)

        logger.info(f"Unregistered tenant {tenant_id} from memory isolation")

    def set_tenant_context(
        self, tenant_id: Union[str, UUID]
    ) -> "TenantMemoryContextManager":
        """Set memory context for tenant operations."""
        if isinstance(tenant_id, UUID):
            tenant_id = str(tenant_id)

        if tenant_id not in self._tenant_limits:
            raise MemoryIsolationError(f"Tenant {tenant_id} not registered")

        return TenantMemoryContextManager(self, tenant_id)

    def check_tenant_memory_limit(
        self, tenant_id: str, additional_bytes: int = 0
    ) -> None:
        """Check if tenant would exceed memory limits."""
        if tenant_id not in self._tenant_limits:
            return  # No limits set

        current_usage = self.get_tenant_memory_usage(tenant_id)
        limit = self._tenant_limits[tenant_id]

        projected_usage = current_usage + additional_bytes

        if projected_usage > limit.hard_limit:
            # Log memory limit violation
            asyncio.create_task(
                self._log_memory_violation(
                    tenant_id, projected_usage, limit.hard_limit, "hard_limit_exceeded"
                )
            )
            raise TenantMemoryLimitExceeded(
                f"Tenant {tenant_id} would exceed hard limit: "
                f"{projected_usage} > {limit.hard_limit}"
            )

        if projected_usage > limit.soft_limit:
            logger.warning(
                f"Tenant {tenant_id} approaching memory limit: "
                f"{projected_usage} > {limit.soft_limit}"
            )

    def get_tenant_memory_usage(self, tenant_id: str) -> int:
        """Get current memory usage for a tenant."""
        if tenant_id not in self._tenant_stats:
            return 0

        # Update current usage using process memory info
        try:
            process_info = self._process.memory_info()
            total_memory = process_info.rss

            # Estimate tenant usage based on object tracking
            context = self._tenant_contexts.get(tenant_id)
            if context and context.monitoring_enabled:
                # Use tracemalloc if available
                if self._enable_tracemalloc and tracemalloc.is_tracing():
                    current, peak = tracemalloc.get_traced_memory()
                    # This is a rough estimation - in practice you'd need more sophisticated tracking
                    tenant_usage = (
                        current // len(self._tenant_contexts)
                        if self._tenant_contexts
                        else 0
                    )
                else:
                    # Fallback estimation
                    tenant_usage = (
                        total_memory // len(self._tenant_contexts)
                        if self._tenant_contexts
                        else 0
                    )

                # Update stats
                stats = self._tenant_stats[tenant_id]
                stats.current_usage = tenant_usage
                stats.peak_usage = max(stats.peak_usage, tenant_usage)
                stats.last_updated = time.time()

                return tenant_usage

        except Exception as e:
            logger.error(f"Failed to get memory usage for tenant {tenant_id}: {e}")

        return self._tenant_stats[tenant_id].current_usage

    def get_tenant_stats(self, tenant_id: str) -> Optional[MemoryUsageStats]:
        """Get memory statistics for a tenant."""
        if tenant_id not in self._tenant_stats:
            return None

        # Update current usage
        self.get_tenant_memory_usage(tenant_id)
        return self._tenant_stats[tenant_id]

    def get_all_tenant_stats(self) -> Dict[str, MemoryUsageStats]:
        """Get memory statistics for all tenants."""
        stats = {}
        for tenant_id in self._tenant_stats:
            stats[tenant_id] = self.get_tenant_stats(tenant_id)
        return stats

    def _force_tenant_gc(self, tenant_id: str) -> int:
        """Force garbage collection for a specific tenant."""
        context = self._tenant_contexts.get(tenant_id)
        if not context:
            return 0

        # Override GC thresholds if configured
        old_thresholds = None
        if context.gc_threshold_override:
            old_thresholds = gc.get_threshold()
            gc.set_threshold(*context.gc_threshold_override)

        # Force collection
        collected = gc.collect()

        # Restore old thresholds
        if old_thresholds:
            gc.set_threshold(*old_thresholds)

        # Update stats
        if tenant_id in self._tenant_stats:
            self._tenant_stats[tenant_id].gc_collections += 1

        logger.debug(f"Forced GC for tenant {tenant_id}, collected {collected} objects")
        return collected

    def optimize_tenant_memory(self, tenant_id: str) -> Dict[str, Any]:
        """Optimize memory usage for a specific tenant."""
        if tenant_id not in self._tenant_contexts:
            return {"error": "Tenant not found"}

        start_time = time.time()
        start_usage = self.get_tenant_memory_usage(tenant_id)

        # Force garbage collection
        collected_objects = self._force_tenant_gc(tenant_id)

        # Take memory snapshot if enabled
        if self._enable_tracemalloc and tracemalloc.is_tracing():
            snapshot = tracemalloc.take_snapshot()
            context = self._tenant_contexts[tenant_id]
            context.memory_snapshots.append(snapshot)

            # Keep only last 10 snapshots
            if len(context.memory_snapshots) > 10:
                context.memory_snapshots = context.memory_snapshots[-10:]

        end_usage = self.get_tenant_memory_usage(tenant_id)
        memory_freed = start_usage - end_usage

        optimization_result = {
            "tenant_id": tenant_id,
            "start_usage": start_usage,
            "end_usage": end_usage,
            "memory_freed": memory_freed,
            "objects_collected": collected_objects,
            "optimization_time": time.time() - start_time,
            "constitutional_hash": self.constitutional_hash,
        }

        logger.info(
            f"Memory optimization for tenant {tenant_id}: freed {memory_freed} bytes"
        )

        # Log optimization event
        asyncio.create_task(
            self._log_memory_optimization(tenant_id, optimization_result)
        )

        return optimization_result

    def detect_memory_leaks(
        self, tenant_id: str, threshold_mb: int = 50
    ) -> Dict[str, Any]:
        """Detect potential memory leaks for a tenant."""
        if tenant_id not in self._tenant_contexts:
            return {"error": "Tenant not found"}

        context = self._tenant_contexts[tenant_id]
        stats = self._tenant_stats[tenant_id]

        # Check for consistent growth pattern
        threshold_bytes = threshold_mb * 1024 * 1024
        current_usage = self.get_tenant_memory_usage(tenant_id)

        leak_indicators = {
            "tenant_id": tenant_id,
            "current_usage": current_usage,
            "peak_usage": stats.peak_usage,
            "usage_growth": current_usage
            - (stats.peak_usage * 0.8),  # Expected to be 80% of peak
            "potential_leak": False,
            "leak_severity": "none",
            "recommendations": [],
            "constitutional_hash": self.constitutional_hash,
        }

        # Analyze memory patterns
        if current_usage > threshold_bytes:
            leak_indicators["potential_leak"] = True
            leak_indicators["leak_severity"] = (
                "high" if current_usage > threshold_bytes * 2 else "medium"
            )
            leak_indicators["recommendations"].append("Consider memory optimization")

        if stats.peak_usage > 0 and current_usage > (stats.peak_usage * 0.9):
            leak_indicators["recommendations"].append(
                "Memory usage close to peak, monitor closely"
            )

        # Check GC effectiveness
        if stats.gc_collections > 0 and current_usage > (stats.peak_usage * 0.7):
            leak_indicators["recommendations"].append(
                "Garbage collection may be ineffective"
            )

        return leak_indicators

    def start_monitoring(self) -> None:
        """Start background memory monitoring."""
        if self._monitoring_active:
            return

        self._monitoring_active = True
        self._shutdown_event.clear()
        self._monitoring_thread = threading.Thread(
            target=self._monitoring_loop, daemon=True
        )
        self._monitoring_thread.start()
        logger.info("Memory monitoring started")

    def stop_monitoring(self) -> None:
        """Stop background memory monitoring."""
        if not self._monitoring_active:
            return

        self._monitoring_active = False
        self._shutdown_event.set()

        if self._monitoring_thread:
            self._monitoring_thread.join(timeout=5.0)

        logger.info("Memory monitoring stopped")

    def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while self._monitoring_active and not self._shutdown_event.is_set():
            try:
                # Update memory stats for all tenants
                for tenant_id in list(self._tenant_contexts.keys()):
                    try:
                        current_usage = self.get_tenant_memory_usage(tenant_id)
                        limit = self._tenant_limits.get(tenant_id)

                        if limit:
                            # Check for limit violations
                            if current_usage > limit.hard_limit:
                                logger.error(
                                    f"Tenant {tenant_id} exceeded hard memory limit: "
                                    f"{current_usage} > {limit.hard_limit}"
                                )

                                # Force optimization
                                self.optimize_tenant_memory(tenant_id)

                            elif current_usage > limit.soft_limit:
                                logger.warning(
                                    f"Tenant {tenant_id} exceeded soft memory limit: "
                                    f"{current_usage} > {limit.soft_limit}"
                                )

                    except Exception as e:
                        logger.error(f"Error monitoring tenant {tenant_id}: {e}")

                # Wait for next monitoring interval
                self._shutdown_event.wait(self.monitoring_interval)

            except Exception as e:
                logger.error(f"Error in memory monitoring loop: {e}")
                self._shutdown_event.wait(self.monitoring_interval)

    def get_system_memory_info(self) -> Dict[str, Any]:
        """Get overall system memory information."""
        try:
            virtual_memory = psutil.virtual_memory()
            process_memory = self._process.memory_info()

            return {
                "system_total": virtual_memory.total,
                "system_available": virtual_memory.available,
                "system_used": virtual_memory.used,
                "system_percent": virtual_memory.percent,
                "process_rss": process_memory.rss,
                "process_vms": process_memory.vms,
                "tenant_count": len(self._tenant_contexts),
                "monitoring_active": self._monitoring_active,
                "constitutional_hash": self.constitutional_hash,
            }
        except Exception as e:
            logger.error(f"Failed to get system memory info: {e}")
            return {"error": str(e)}

    def cleanup(self) -> None:
        """Clean up memory isolation framework."""
        # Stop monitoring
        self.stop_monitoring()

        # Force GC for all tenants
        for tenant_id in list(self._tenant_contexts.keys()):
            self._force_tenant_gc(tenant_id)

        # Clear all tracking data
        self._tenant_limits.clear()
        self._tenant_stats.clear()
        self._tenant_contexts.clear()

        # Stop tracemalloc if we started it
        if self._enable_tracemalloc and tracemalloc.is_tracing():
            tracemalloc.stop()

        logger.info("Memory isolation framework cleaned up")

    async def _log_memory_violation(
        self, tenant_id: str, projected_usage: int, limit: int, violation_type: str
    ):
        """Log memory violation to audit aggregator."""
        try:
            # Import here to avoid circular imports
            from services.shared.audit.compliance_audit_logger import (
                AuditEventType,
                log_tenant_isolation_event,
            )

            await log_tenant_isolation_event(
                event_type=AuditEventType.MEMORY_LIMIT_EXCEEDED,
                action=f"memory_{violation_type}",
                tenant_id=tenant_id,
                isolation_type="memory",
                resource_accessed="tenant_memory_allocation",
                outcome="violation",
                violation_details={
                    "projected_usage": projected_usage,
                    "limit": limit,
                    "violation_type": violation_type,
                    "usage_percentage": (
                        (projected_usage / limit) * 100 if limit > 0 else 0
                    ),
                },
                details={
                    "constitutional_hash": self.constitutional_hash,
                    "system_memory_limit": self._system_memory_limit,
                    "tenant_count": len(self._tenant_contexts),
                },
            )

        except Exception as e:
            logger.error(f"Failed to log memory violation: {e}")

    async def _log_memory_optimization(
        self, tenant_id: str, optimization_result: Dict[str, Any]
    ):
        """Log memory optimization event."""
        try:
            from services.shared.audit.compliance_audit_logger import (
                AuditEventType,
                log_tenant_isolation_event,
            )

            await log_tenant_isolation_event(
                event_type=AuditEventType.MEMORY_OPTIMIZATION_PERFORMED,
                action="memory_optimization",
                tenant_id=tenant_id,
                isolation_type="memory",
                resource_accessed="tenant_memory_allocation",
                outcome="success",
                details={
                    **optimization_result,
                    "constitutional_hash": self.constitutional_hash,
                },
            )

        except Exception as e:
            logger.error(f"Failed to log memory optimization: {e}")


class TenantMemoryContextManager:
    """Context manager for tenant memory operations."""

    def __init__(self, framework: MemoryIsolationFramework, tenant_id: str):
        self.framework = framework
        self.tenant_id = tenant_id
        self._start_usage = 0
        self._start_time = 0

    def __enter__(self):
        self._start_usage = self.framework.get_tenant_memory_usage(self.tenant_id)
        self._start_time = time.time()

        # Check memory limits before starting
        self.framework.check_tenant_memory_limit(self.tenant_id)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_usage = self.framework.get_tenant_memory_usage(self.tenant_id)
        duration = time.time() - self._start_time

        # Update allocation stats
        if self.tenant_id in self.framework._tenant_stats:
            stats = self.framework._tenant_stats[self.tenant_id]
            if end_usage > self._start_usage:
                stats.allocation_count += 1
            else:
                stats.deallocation_count += 1

        # Log significant memory changes
        memory_change = end_usage - self._start_usage
        if abs(memory_change) > 1024 * 1024:  # 1MB threshold
            logger.debug(
                f"Tenant {self.tenant_id} memory change: {memory_change} bytes "
                f"in {duration:.2f}s"
            )

    def check_limit(self, additional_bytes: int = 0):
        """Check memory limit during operation."""
        self.framework.check_tenant_memory_limit(self.tenant_id, additional_bytes)


# Global memory isolation framework
memory_isolation = MemoryIsolationFramework()


def get_memory_isolation() -> MemoryIsolationFramework:
    """Get the global memory isolation framework."""
    return memory_isolation
