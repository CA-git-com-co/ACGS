"""
Shared Health Check Base Classes
Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Optional

# Constitutional compliance
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class HealthStatus(str, Enum):
    """Health check status enumeration."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Health check result data structure."""
    name: str
    status: HealthStatus
    message: str
    timestamp: float = None
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


class BaseHealthCheck(ABC):
    """Base class for all health checks."""
    
    def __init__(self, name: str, critical: bool = False):
        self.name = name
        self.critical = critical
        self.constitutional_hash = CONSTITUTIONAL_HASH
    
    @abstractmethod
    async def check(self) -> HealthCheckResult:
        """Perform the health check."""
        pass
    
    def is_critical(self) -> bool:
        """Check if this health check is critical."""
        return self.critical


class ServiceHealthCheck(BaseHealthCheck):
    """Health check for ACGS services."""
    
    def __init__(self, name: str, service_url: str, critical: bool = True):
        super().__init__(name, critical)
        self.service_url = service_url
    
    async def check(self) -> HealthCheckResult:
        """Check service health via HTTP endpoint."""
        import aiohttp
        
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f"{self.service_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        return HealthCheckResult(
                            name=self.name,
                            status=HealthStatus.HEALTHY,
                            message=f"Service {self.name} is healthy",
                            details=data
                        )
                    else:
                        return HealthCheckResult(
                            name=self.name,
                            status=HealthStatus.UNHEALTHY,
                            message=f"Service {self.name} returned status {response.status}",
                            error=f"HTTP {response.status}"
                        )
        except Exception as e:
            return HealthCheckResult(
                name=self.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Service {self.name} health check failed",
                error=str(e)
            )


class HealthCheckRegistry:
    """Registry for managing health checks."""
    
    def __init__(self):
        self.checks: Dict[str, BaseHealthCheck] = {}
        self.constitutional_hash = CONSTITUTIONAL_HASH
    
    def register(self, health_check: BaseHealthCheck) -> None:
        """Register a health check."""
        self.checks[health_check.name] = health_check
    
    async def run_all_checks(self) -> Dict[str, HealthCheckResult]:
        """Run all registered health checks."""
        results = {}
        
        for name, check in self.checks.items():
            try:
                result = await check.check()
                results[name] = result
            except Exception as e:
                results[name] = HealthCheckResult(
                    name=name,
                    status=HealthStatus.UNKNOWN,
                    message=f"Health check {name} failed to execute",
                    error=str(e)
                )
        
        return results
    
    async def run_critical_checks(self) -> Dict[str, HealthCheckResult]:
        """Run only critical health checks."""
        results = {}
        
        for name, check in self.checks.items():
            if check.is_critical():
                try:
                    result = await check.check()
                    results[name] = result
                except Exception as e:
                    results[name] = HealthCheckResult(
                        name=name,
                        status=HealthStatus.UNKNOWN,
                        message=f"Critical health check {name} failed",
                        error=str(e)
                    )
        
        return results


# Global health check registry
_global_registry = HealthCheckRegistry()


def get_health_registry() -> HealthCheckRegistry:
    """Get the global health check registry."""
    return _global_registry
