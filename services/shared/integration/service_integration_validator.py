"""
Service Integration Validator
Constitutional Hash: cdd01ef066bc6cf2

Comprehensive service integration validation system that ensures all ACGS-2
services work together seamlessly while maintaining constitutional compliance
and performance targets.

Features:
- Cross-service constitutional compliance validation
- Performance integration testing
- Service mesh health monitoring
- Dependency validation and resolution
- Real-time integration metrics
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple
import aiohttp
import json

from services.shared.constitutional.validation import UltraFastConstitutionalValidator
from services.shared.performance.performance_integration_service import PerformanceIntegrationService

# Constitutional hash constant
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Service integration targets
INTEGRATION_TARGETS = {
    "service_response_time_ms": 100,    # Max response time between services
    "constitutional_compliance": 1.0,   # 100% compliance across services
    "health_check_interval_s": 30,      # Health check frequency
    "dependency_resolution_ms": 50,     # Max dependency resolution time
    "cross_service_latency_ms": 10,     # Max cross-service call latency
    "integration_success_rate": 0.99,   # 99% integration success rate
}

logger = logging.getLogger(__name__)


@dataclass
class ServiceEndpoint:
    """Service endpoint configuration."""
    
    name: str
    url: str
    port: int
    health_path: str = "/health"
    constitutional_path: str = "/constitutional"
    dependencies: List[str] = field(default_factory=list)
    required: bool = True
    timeout_ms: int = 5000


@dataclass
class IntegrationMetrics:
    """Integration validation metrics."""
    
    total_validations: int = 0
    successful_validations: int = 0
    failed_validations: int = 0
    
    total_response_time: float = 0.0
    min_response_time: float = float('inf')
    max_response_time: float = 0.0
    
    constitutional_violations: int = 0
    dependency_failures: int = 0
    health_check_failures: int = 0
    
    def add_validation(self, response_time: float, success: bool = True, constitutional_compliant: bool = True) -> None:
        """Add validation metrics."""
        self.total_validations += 1
        
        if success:
            self.successful_validations += 1
        else:
            self.failed_validations += 1
        
        if not constitutional_compliant:
            self.constitutional_violations += 1
        
        self.total_response_time += response_time
        self.min_response_time = min(self.min_response_time, response_time)
        self.max_response_time = max(self.max_response_time, response_time)
    
    def get_success_rate(self) -> float:
        """Get validation success rate."""
        if self.total_validations == 0:
            return 1.0
        return self.successful_validations / self.total_validations
    
    def get_avg_response_time_ms(self) -> float:
        """Get average response time in milliseconds."""
        if self.total_validations == 0:
            return 0.0
        return (self.total_response_time / self.total_validations) * 1000
    
    def get_constitutional_compliance_rate(self) -> float:
        """Get constitutional compliance rate."""
        if self.total_validations == 0:
            return 1.0
        return (self.total_validations - self.constitutional_violations) / self.total_validations


class ServiceIntegrationValidator:
    """
    Comprehensive service integration validator.
    
    Features:
    - Cross-service constitutional compliance validation
    - Performance integration testing
    - Service mesh health monitoring
    - Dependency validation and resolution
    - Real-time integration metrics
    """
    
    def __init__(self):
        # Core components
        self.constitutional_validator = UltraFastConstitutionalValidator()
        self.performance_service: Optional[PerformanceIntegrationService] = None
        
        # Service registry
        self.services: Dict[str, ServiceEndpoint] = {}
        self.service_dependencies: Dict[str, Set[str]] = {}
        
        # Integration metrics
        self.metrics = IntegrationMetrics()
        
        # HTTP session for service communication
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Monitoring
        self._monitoring_enabled = True
        self._monitoring_task: Optional[asyncio.Task] = None
        
        # Constitutional compliance
        self.constitutional_hash = CONSTITUTIONAL_HASH
        
        logger.info(f"ServiceIntegrationValidator initialized with constitutional_hash: {self.constitutional_hash}")
    
    async def initialize(self) -> None:
        """Initialize the service integration validator."""
        try:
            # Validate constitutional compliance
            if not self.constitutional_validator.validate_hash(self.constitutional_hash):
                raise RuntimeError(f"Constitutional compliance violation: {self.constitutional_hash}")
            
            # Initialize HTTP session
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
            
            # Register default ACGS-2 services
            await self._register_default_services()
            
            # Start monitoring
            if self._monitoring_enabled:
                self._monitoring_task = asyncio.create_task(self._monitoring_loop())
            
            logger.info("ServiceIntegrationValidator fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize ServiceIntegrationValidator: {e}")
            raise
    
    async def _register_default_services(self) -> None:
        """Register default ACGS-2 services."""
        default_services = [
            ServiceEndpoint(
                name="auth_service",
                url="http://localhost",
                port=8016,
                dependencies=["constitutional_ai"],
                required=True
            ),
            ServiceEndpoint(
                name="constitutional_ai",
                url="http://localhost",
                port=8002,
                dependencies=[],
                required=True
            ),
            ServiceEndpoint(
                name="governance_synthesis",
                url="http://localhost",
                port=8003,
                dependencies=["constitutional_ai"],
                required=True
            ),
            ServiceEndpoint(
                name="formal_verification",
                url="http://localhost",
                port=8004,
                dependencies=["constitutional_ai"],
                required=True
            ),
            ServiceEndpoint(
                name="evolutionary_computation",
                url="http://localhost",
                port=8005,
                dependencies=["constitutional_ai"],
                required=False
            ),
            ServiceEndpoint(
                name="context_engine",
                url="http://localhost",
                port=8006,
                dependencies=["constitutional_ai"],
                required=True
            ),
            ServiceEndpoint(
                name="code_analysis_engine",
                url="http://localhost",
                port=8007,
                dependencies=["context_engine"],
                required=True
            ),
            ServiceEndpoint(
                name="multi_agent_coordination",
                url="http://localhost",
                port=8010,
                dependencies=["constitutional_ai", "governance_synthesis"],
                required=True
            ),
        ]
        
        for service in default_services:
            await self.register_service(service)
    
    async def register_service(self, service: ServiceEndpoint) -> None:
        """Register a service for integration validation."""
        self.services[service.name] = service
        
        # Build dependency graph
        if service.name not in self.service_dependencies:
            self.service_dependencies[service.name] = set()
        
        for dependency in service.dependencies:
            self.service_dependencies[service.name].add(dependency)
        
        logger.info(f"Registered service: {service.name} on port {service.port}")
    
    async def validate_service_health(self, service_name: str) -> Dict[str, Any]:
        """Validate individual service health."""
        if service_name not in self.services:
            return {"healthy": False, "error": f"Service {service_name} not registered"}
        
        service = self.services[service_name]
        start_time = time.perf_counter()
        
        try:
            health_url = f"{service.url}:{service.port}{service.health_path}"
            
            async with self.session.get(health_url) as response:
                elapsed = time.perf_counter() - start_time
                
                if response.status == 200:
                    health_data = await response.json()
                    
                    # Check constitutional compliance in health response
                    constitutional_compliant = (
                        health_data.get("constitutional_hash") == self.constitutional_hash
                    )
                    
                    self.metrics.add_validation(
                        elapsed,
                        success=True,
                        constitutional_compliant=constitutional_compliant
                    )
                    
                    return {
                        "healthy": True,
                        "service": service_name,
                        "response_time_ms": elapsed * 1000,
                        "constitutional_compliant": constitutional_compliant,
                        "data": health_data,
                        "constitutional_hash": self.constitutional_hash
                    }
                else:
                    self.metrics.add_validation(elapsed, success=False)
                    return {
                        "healthy": False,
                        "service": service_name,
                        "error": f"HTTP {response.status}",
                        "response_time_ms": elapsed * 1000
                    }
        
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            self.metrics.add_validation(elapsed, success=False)
            self.metrics.health_check_failures += 1
            
            return {
                "healthy": False,
                "service": service_name,
                "error": str(e),
                "response_time_ms": elapsed * 1000
            }
    
    async def validate_constitutional_compliance(self, service_name: str) -> Dict[str, Any]:
        """Validate service constitutional compliance."""
        if service_name not in self.services:
            return {"compliant": False, "error": f"Service {service_name} not registered"}
        
        service = self.services[service_name]
        start_time = time.perf_counter()
        
        try:
            constitutional_url = f"{service.url}:{service.port}{service.constitutional_path}"
            
            async with self.session.get(constitutional_url) as response:
                elapsed = time.perf_counter() - start_time
                
                if response.status == 200:
                    constitutional_data = await response.json()
                    
                    # Validate constitutional hash
                    service_hash = constitutional_data.get("constitutional_hash")
                    is_compliant = self.constitutional_validator.validate_hash(service_hash)
                    
                    if not is_compliant:
                        self.metrics.constitutional_violations += 1
                    
                    return {
                        "compliant": is_compliant,
                        "service": service_name,
                        "service_hash": service_hash,
                        "expected_hash": self.constitutional_hash,
                        "response_time_ms": elapsed * 1000,
                        "data": constitutional_data
                    }
                else:
                    return {
                        "compliant": False,
                        "service": service_name,
                        "error": f"HTTP {response.status}",
                        "response_time_ms": elapsed * 1000
                    }
        
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            self.metrics.constitutional_violations += 1
            
            return {
                "compliant": False,
                "service": service_name,
                "error": str(e),
                "response_time_ms": elapsed * 1000
            }
    
    async def validate_service_dependencies(self, service_name: str) -> Dict[str, Any]:
        """Validate service dependencies are healthy."""
        if service_name not in self.service_dependencies:
            return {"dependencies_healthy": True, "dependencies": []}
        
        dependencies = self.service_dependencies[service_name]
        dependency_results = {}
        all_healthy = True
        
        start_time = time.perf_counter()
        
        for dependency in dependencies:
            if dependency in self.services:
                health_result = await self.validate_service_health(dependency)
                dependency_results[dependency] = health_result
                
                if not health_result.get("healthy", False):
                    all_healthy = False
                    self.metrics.dependency_failures += 1
            else:
                dependency_results[dependency] = {
                    "healthy": False,
                    "error": "Dependency not registered"
                }
                all_healthy = False
                self.metrics.dependency_failures += 1
        
        elapsed = time.perf_counter() - start_time
        
        return {
            "dependencies_healthy": all_healthy,
            "service": service_name,
            "dependencies": dependency_results,
            "validation_time_ms": elapsed * 1000,
            "constitutional_hash": self.constitutional_hash
        }
    
    async def validate_cross_service_communication(self, from_service: str, to_service: str) -> Dict[str, Any]:
        """Validate communication between two services."""
        if from_service not in self.services or to_service not in self.services:
            return {"communication_healthy": False, "error": "One or both services not registered"}
        
        start_time = time.perf_counter()
        
        try:
            # Simulate cross-service call by checking if target service is reachable
            to_service_obj = self.services[to_service]
            test_url = f"{to_service_obj.url}:{to_service_obj.port}{to_service_obj.health_path}"
            
            async with self.session.get(test_url) as response:
                elapsed = time.perf_counter() - start_time
                
                communication_healthy = response.status == 200
                
                return {
                    "communication_healthy": communication_healthy,
                    "from_service": from_service,
                    "to_service": to_service,
                    "latency_ms": elapsed * 1000,
                    "status_code": response.status,
                    "constitutional_hash": self.constitutional_hash
                }
        
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            
            return {
                "communication_healthy": False,
                "from_service": from_service,
                "to_service": to_service,
                "latency_ms": elapsed * 1000,
                "error": str(e)
            }

    async def validate_all_services(self) -> Dict[str, Any]:
        """Validate all registered services comprehensively."""
        start_time = time.perf_counter()

        validation_results = {
            "overall_healthy": True,
            "services": {},
            "constitutional_compliance": {},
            "dependencies": {},
            "cross_service_communication": {},
            "summary": {},
            "constitutional_hash": self.constitutional_hash,
            "timestamp": time.time()
        }

        # Validate individual service health
        for service_name in self.services:
            health_result = await self.validate_service_health(service_name)
            validation_results["services"][service_name] = health_result

            if not health_result.get("healthy", False):
                validation_results["overall_healthy"] = False

        # Validate constitutional compliance
        for service_name in self.services:
            compliance_result = await self.validate_constitutional_compliance(service_name)
            validation_results["constitutional_compliance"][service_name] = compliance_result

            if not compliance_result.get("compliant", False):
                validation_results["overall_healthy"] = False

        # Validate dependencies
        for service_name in self.services:
            dependency_result = await self.validate_service_dependencies(service_name)
            validation_results["dependencies"][service_name] = dependency_result

            if not dependency_result.get("dependencies_healthy", False):
                validation_results["overall_healthy"] = False

        # Validate cross-service communication
        for from_service in self.services:
            for to_service in self.service_dependencies.get(from_service, []):
                comm_key = f"{from_service}->{to_service}"
                comm_result = await self.validate_cross_service_communication(
                    from_service, to_service
                )
                validation_results["cross_service_communication"][comm_key] = comm_result

                if not comm_result.get("communication_healthy", False):
                    validation_results["overall_healthy"] = False

        # Generate summary
        elapsed = time.perf_counter() - start_time
        validation_results["summary"] = {
            "total_services": len(self.services),
            "healthy_services": sum(
                1 for r in validation_results["services"].values()
                if r.get("healthy", False)
            ),
            "compliant_services": sum(
                1 for r in validation_results["constitutional_compliance"].values()
                if r.get("compliant", False)
            ),
            "validation_time_ms": elapsed * 1000,
            "success_rate": self.metrics.get_success_rate(),
            "constitutional_compliance_rate": self.metrics.get_constitutional_compliance_rate(),
            "avg_response_time_ms": self.metrics.get_avg_response_time_ms()
        }

        return validation_results

    async def validate_performance_integration(self) -> Dict[str, Any]:
        """Validate performance integration across services."""
        if not self.performance_service:
            try:
                from services.shared.performance.performance_integration_service import (
                    get_performance_service
                )
                self.performance_service = await get_performance_service()
            except Exception as e:
                return {
                    "performance_integration_healthy": False,
                    "error": f"Failed to get performance service: {e}"
                }

        try:
            # Get performance summary
            performance_summary = await self.performance_service.get_performance_summary()

            # Check if performance targets are met
            targets_met = performance_summary.get("targets_met", {})
            integration_healthy = all(targets_met.values())

            return {
                "performance_integration_healthy": integration_healthy,
                "targets_met": targets_met,
                "integration_metrics": performance_summary.get("integration_metrics", {}),
                "constitutional_hash": self.constitutional_hash
            }

        except Exception as e:
            return {
                "performance_integration_healthy": False,
                "error": str(e)
            }

    async def _monitoring_loop(self) -> None:
        """Background monitoring loop for service integration."""
        while self._monitoring_enabled:
            try:
                # Perform comprehensive validation
                validation_results = await self.validate_all_services()

                # Log issues
                if not validation_results["overall_healthy"]:
                    unhealthy_services = [
                        name for name, result in validation_results["services"].items()
                        if not result.get("healthy", False)
                    ]
                    logger.warning(f"Unhealthy services detected: {unhealthy_services}")

                # Check constitutional compliance
                non_compliant_services = [
                    name for name, result in validation_results["constitutional_compliance"].items()
                    if not result.get("compliant", False)
                ]
                if non_compliant_services:
                    logger.error(f"Constitutional compliance violations: {non_compliant_services}")

                # Wait before next check
                await asyncio.sleep(INTEGRATION_TARGETS["health_check_interval_s"])

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in service integration monitoring: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    def get_integration_metrics(self) -> Dict[str, Any]:
        """Get comprehensive integration metrics."""
        return {
            "validation_metrics": {
                "total_validations": self.metrics.total_validations,
                "success_rate": self.metrics.get_success_rate(),
                "avg_response_time_ms": self.metrics.get_avg_response_time_ms(),
                "constitutional_compliance_rate": self.metrics.get_constitutional_compliance_rate()
            },
            "service_registry": {
                "total_services": len(self.services),
                "required_services": sum(1 for s in self.services.values() if s.required),
                "optional_services": sum(1 for s in self.services.values() if not s.required)
            },
            "dependency_graph": {
                "total_dependencies": sum(len(deps) for deps in self.service_dependencies.values()),
                "services_with_dependencies": len([s for s in self.service_dependencies.values() if s])
            },
            "error_statistics": {
                "constitutional_violations": self.metrics.constitutional_violations,
                "dependency_failures": self.metrics.dependency_failures,
                "health_check_failures": self.metrics.health_check_failures
            },
            "performance_targets": INTEGRATION_TARGETS,
            "constitutional_hash": self.constitutional_hash,
            "timestamp": time.time()
        }

    async def optimize_integration(self) -> Dict[str, Any]:
        """Optimize service integration based on current metrics."""
        optimizations_applied = []
        recommendations = []

        # Check response time performance
        avg_response_time = self.metrics.get_avg_response_time_ms()
        if avg_response_time > INTEGRATION_TARGETS["service_response_time_ms"]:
            recommendations.append(f"Service response time ({avg_response_time:.2f}ms) exceeds target")

        # Check success rate
        success_rate = self.metrics.get_success_rate()
        if success_rate < INTEGRATION_TARGETS["integration_success_rate"]:
            recommendations.append(f"Integration success rate ({success_rate:.2%}) below target")

        # Check constitutional compliance
        compliance_rate = self.metrics.get_constitutional_compliance_rate()
        if compliance_rate < INTEGRATION_TARGETS["constitutional_compliance"]:
            recommendations.append(f"Constitutional compliance rate ({compliance_rate:.2%}) below target")

            # Try to optimize constitutional validation
            if self.constitutional_validator:
                validator_opt = self.constitutional_validator.optimize_performance()
                if validator_opt["optimizations_applied"]:
                    optimizations_applied.extend(validator_opt["optimizations_applied"])

        # Optimize performance integration if available
        if self.performance_service:
            try:
                perf_opt = await self.performance_service._run_optimization()
                optimizations_applied.append("Performance service optimization triggered")
            except Exception as e:
                logger.warning(f"Failed to optimize performance service: {e}")

        return {
            "optimizations_applied": optimizations_applied,
            "recommendations": recommendations,
            "current_metrics": self.get_integration_metrics(),
            "constitutional_hash": self.constitutional_hash
        }

    async def close(self) -> None:
        """Close the service integration validator."""
        self._monitoring_enabled = False

        # Cancel monitoring task
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass

        # Close HTTP session
        if self.session:
            await self.session.close()

        logger.info("ServiceIntegrationValidator closed")


# Global service integration validator instance
_integration_validator: Optional[ServiceIntegrationValidator] = None


async def get_service_integration_validator() -> ServiceIntegrationValidator:
    """Get the global service integration validator."""
    global _integration_validator
    if _integration_validator is None:
        _integration_validator = ServiceIntegrationValidator()
        await _integration_validator.initialize()
    return _integration_validator


async def validate_acgs_service_integration() -> Dict[str, Any]:
    """Convenience function to validate ACGS-2 service integration."""
    validator = await get_service_integration_validator()
    return await validator.validate_all_services()
