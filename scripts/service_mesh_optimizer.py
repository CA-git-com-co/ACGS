#!/usr/bin/env python3
"""
Service Mesh Optimizer for ACGS-1

Implements intelligent service mesh configuration, circuit breaker patterns,
and advanced load balancing for the 8-service ACGS architecture.
"""

import asyncio
import aiohttp
import time
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import subprocess
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ServiceHealth:
    """Service health status."""
    name: str
    port: int
    healthy: bool = False
    response_time: float = 0.0
    last_check: float = 0.0
    error_count: int = 0
    consecutive_failures: int = 0


@dataclass
class LoadBalancingConfig:
    """Load balancing configuration."""
    strategy: str = "least_connections"  # round_robin, least_connections, weighted
    health_check_interval: int = 10
    failure_threshold: int = 3
    recovery_threshold: int = 2
    timeout: float = 5.0


class ServiceMeshOptimizer:
    """
    Advanced service mesh optimizer for ACGS-1.
    
    Provides intelligent load balancing, health monitoring,
    circuit breaker patterns, and service discovery.
    """
    
    def __init__(self):
        """Initialize service mesh optimizer."""
        self.services = {
            "auth_service": ServiceHealth("auth_service", 8000),
            "ac_service": ServiceHealth("ac_service", 8001),
            "integrity_service": ServiceHealth("integrity_service", 8002),
            "fv_service": ServiceHealth("fv_service", 8003),
            "gs_service": ServiceHealth("gs_service", 8004),
            "pgc_service": ServiceHealth("pgc_service", 8005),
            "ec_service": ServiceHealth("ec_service", 8006),
            "research_service": ServiceHealth("research_service", 8007)
        }
        
        self.config = LoadBalancingConfig()
        self.session: Optional[aiohttp.ClientSession] = None
        self.monitoring_task: Optional[asyncio.Task] = None
        self.is_running = False
        
        # Service priorities for constitutional governance
        self.service_priorities = {
            "pgc_service": 1,      # Highest priority - constitutional validation
            "ac_service": 2,       # Constitutional council and voting
            "fv_service": 3,       # Formal verification
            "integrity_service": 4, # Data integrity
            "gs_service": 5,       # Governance workflows
            "auth_service": 6,     # Authentication
            "ec_service": 7,       # Enforcement
            "research_service": 8   # Research (lowest priority)
        }
    
    async def initialize(self):
        """Initialize service mesh optimizer."""
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=20,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        
        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        self.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        
        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._health_monitoring_loop())
        
        logger.info("Service mesh optimizer initialized")
    
    async def _health_monitoring_loop(self):
        """Continuous health monitoring loop."""
        while self.is_running:
            try:
                await self._check_all_services_health()
                await asyncio.sleep(self.config.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def _check_all_services_health(self):
        """Check health of all services."""
        tasks = []
        for service_name, service_health in self.services.items():
            task = asyncio.create_task(self._check_service_health(service_health))
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _check_service_health(self, service: ServiceHealth):
        """Check health of a specific service."""
        url = f"http://localhost:{service.port}/health"
        
        try:
            start_time = time.time()
            async with self.session.get(url) as response:
                response_time = time.time() - start_time
                
                if response.status == 200:
                    service.healthy = True
                    service.response_time = response_time
                    service.consecutive_failures = 0
                    logger.debug(f"✅ {service.name} healthy ({response_time*1000:.1f}ms)")
                else:
                    self._mark_service_unhealthy(service, f"HTTP {response.status}")
                    
        except Exception as e:
            self._mark_service_unhealthy(service, str(e))
        
        service.last_check = time.time()
    
    def _mark_service_unhealthy(self, service: ServiceHealth, error: str):
        """Mark service as unhealthy and update failure counters."""
        service.healthy = False
        service.error_count += 1
        service.consecutive_failures += 1
        
        if service.consecutive_failures >= self.config.failure_threshold:
            logger.warning(f"❌ {service.name} marked unhealthy after {service.consecutive_failures} failures: {error}")
        else:
            logger.debug(f"⚠️ {service.name} health check failed: {error}")
    
    async def get_optimal_service_for_request(self, request_type: str = "general") -> Optional[ServiceHealth]:
        """
        Get optimal service for a request based on load balancing strategy.
        
        Args:
            request_type: Type of request (constitutional, governance, auth, etc.)
            
        Returns:
            Optimal service or None if no healthy services
        """
        # Filter healthy services
        healthy_services = [s for s in self.services.values() if s.healthy]
        
        if not healthy_services:
            logger.warning("No healthy services available")
            return None
        
        # Apply request-type specific filtering
        if request_type == "constitutional":
            # Prioritize PGC and AC services for constitutional operations
            constitutional_services = [s for s in healthy_services if s.name in ["pgc_service", "ac_service"]]
            if constitutional_services:
                healthy_services = constitutional_services
        
        # Apply load balancing strategy
        if self.config.strategy == "least_connections":
            # For now, use response time as proxy for load
            return min(healthy_services, key=lambda s: s.response_time)
        elif self.config.strategy == "weighted":
            # Use service priorities as weights
            return min(healthy_services, key=lambda s: self.service_priorities.get(s.name, 10))
        else:  # round_robin
            # Simple round-robin based on last check time
            return min(healthy_services, key=lambda s: s.last_check)
    
    async def configure_haproxy(self):
        """Configure HAProxy with current service health status."""
        try:
            # Generate HAProxy backend configuration
            backend_config = self._generate_haproxy_backends()
            
            # Write configuration to file
            config_path = "/tmp/haproxy_backends.cfg"
            with open(config_path, "w") as f:
                f.write(backend_config)
            
            logger.info(f"HAProxy backend configuration written to {config_path}")
            
            # Reload HAProxy if running
            try:
                subprocess.run(["sudo", "systemctl", "reload", "haproxy"], check=True, capture_output=True)
                logger.info("HAProxy configuration reloaded")
            except subprocess.CalledProcessError as e:
                logger.warning(f"HAProxy reload failed: {e}")
            
        except Exception as e:
            logger.error(f"HAProxy configuration failed: {e}")
    
    def _generate_haproxy_backends(self) -> str:
        """Generate HAProxy backend configuration based on service health."""
        config_lines = []
        
        for service_name, service in self.services.items():
            backend_name = f"{service_name}_backend"
            
            config_lines.append(f"backend {backend_name}")
            config_lines.append(f"    description \"{service_name.replace('_', ' ').title()}\"")
            config_lines.append(f"    balance leastconn")
            config_lines.append(f"    option httpchk GET /health")
            config_lines.append(f"    http-check expect status 200")
            
            # Add server configuration
            server_status = "" if service.healthy else " disabled"
            weight = 100 if service.healthy else 0
            maxconn = 200 if service.name == "pgc_service" else 150
            
            config_lines.append(
                f"    server {service_name}1 localhost:{service.port} "
                f"weight {weight} maxconn {maxconn}{server_status}"
            )
            config_lines.append("")
        
        return "\n".join(config_lines)
    
    async def get_service_mesh_status(self) -> Dict[str, Any]:
        """Get comprehensive service mesh status."""
        healthy_count = sum(1 for s in self.services.values() if s.healthy)
        total_count = len(self.services)
        
        service_details = {}
        for name, service in self.services.items():
            service_details[name] = {
                "healthy": service.healthy,
                "port": service.port,
                "response_time_ms": service.response_time * 1000,
                "error_count": service.error_count,
                "consecutive_failures": service.consecutive_failures,
                "last_check": service.last_check,
                "priority": self.service_priorities.get(name, 10)
            }
        
        return {
            "overall_health": "healthy" if healthy_count >= total_count * 0.8 else "degraded",
            "healthy_services": healthy_count,
            "total_services": total_count,
            "availability_percentage": (healthy_count / total_count) * 100,
            "load_balancing_strategy": self.config.strategy,
            "health_check_interval": self.config.health_check_interval,
            "services": service_details,
            "critical_services_status": {
                name: service.healthy 
                for name, service in self.services.items() 
                if self.service_priorities.get(name, 10) <= 3
            }
        }
    
    async def optimize_service_mesh(self):
        """Perform service mesh optimization."""
        logger.info("🔧 Optimizing service mesh configuration...")
        
        # Check current service health
        await self._check_all_services_health()
        
        # Get service mesh status
        status = await self.get_service_mesh_status()
        
        # Configure HAProxy based on current health
        await self.configure_haproxy()
        
        # Optimize load balancing strategy based on service performance
        await self._optimize_load_balancing_strategy()
        
        logger.info("✅ Service mesh optimization completed")
        return status
    
    async def _optimize_load_balancing_strategy(self):
        """Optimize load balancing strategy based on service performance."""
        # Calculate average response times
        healthy_services = [s for s in self.services.values() if s.healthy]
        
        if not healthy_services:
            return
        
        avg_response_time = sum(s.response_time for s in healthy_services) / len(healthy_services)
        response_time_variance = sum(
            (s.response_time - avg_response_time) ** 2 for s in healthy_services
        ) / len(healthy_services)
        
        # If high variance in response times, use least_connections
        # If low variance, use weighted based on priorities
        if response_time_variance > 0.01:  # 10ms variance threshold
            self.config.strategy = "least_connections"
            logger.info("Switched to least_connections strategy due to response time variance")
        else:
            self.config.strategy = "weighted"
            logger.info("Switched to weighted strategy due to consistent response times")
    
    async def close(self):
        """Close service mesh optimizer."""
        self.is_running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        if self.session:
            await self.session.close()
        
        logger.info("Service mesh optimizer closed")


async def main():
    """Main service mesh optimization execution."""
    logger.info("🚀 Starting ACGS-1 Service Mesh Optimization")
    
    optimizer = ServiceMeshOptimizer()
    
    try:
        await optimizer.initialize()
        
        # Run optimization
        status = await optimizer.optimize_service_mesh()
        
        # Save status report
        with open("service_mesh_status.json", "w") as f:
            json.dump(status, f, indent=2, default=str)
        
        # Display results
        print("\n" + "="*70)
        print("🏁 ACGS-1 Service Mesh Optimization Results")
        print("="*70)
        print(f"Overall Health: {status['overall_health'].upper()}")
        print(f"Service Availability: {status['availability_percentage']:.1f}% ({status['healthy_services']}/{status['total_services']})")
        print(f"Load Balancing Strategy: {status['load_balancing_strategy']}")
        
        print(f"\n📊 Service Status:")
        for name, details in status['services'].items():
            status_icon = "✅" if details['healthy'] else "❌"
            print(f"   {status_icon} {name}: {details['response_time_ms']:.1f}ms (Priority: {details['priority']})")
        
        print(f"\n🔒 Critical Services:")
        for name, healthy in status['critical_services_status'].items():
            status_icon = "✅" if healthy else "❌"
            print(f"   {status_icon} {name}")
        
        print(f"\n📄 Detailed status saved: service_mesh_status.json")
        print("="*70)
        
        # Keep monitoring for a short time to demonstrate
        logger.info("Monitoring services for 30 seconds...")
        await asyncio.sleep(30)
        
    except Exception as e:
        logger.error(f"Service mesh optimization failed: {e}")
        raise
    finally:
        await optimizer.close()


if __name__ == "__main__":
    asyncio.run(main())
