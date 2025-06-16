"""
Service Integrator for ACGS-1 Advanced Governance Workflows.

This module provides integration with all ACGS-1 core services, handling
HTTP communication, error handling, retries, and performance monitoring.
"""

import asyncio
import logging
import time
from typing import Any, Dict, Optional

import aiohttp

logger = logging.getLogger(__name__)


class ServiceIntegrator:
    """
    Service integrator for ACGS-1 core services communication.
    
    This integrator provides reliable communication with all 7 core ACGS-1 services
    with proper error handling, retries, and performance monitoring.
    """
    
    def __init__(self, settings):
        self.settings = settings
        
        # Service URLs
        self.service_urls = {
            "auth": settings.AUTH_SERVICE_URL,
            "ac": settings.AC_SERVICE_URL,
            "integrity": settings.INTEGRITY_SERVICE_URL,
            "fv": settings.FV_SERVICE_URL,
            "gs": settings.GS_SERVICE_URL,
            "pgc": settings.PGC_SERVICE_URL,
            "ec": settings.EC_SERVICE_URL,
        }
        
        # HTTP clients
        self.service_clients: Dict[str, aiohttp.ClientSession] = {}
        
        # Configuration
        self.timeout = settings.SERVICE_TIMEOUT
        self.retry_attempts = settings.SERVICE_RETRY_ATTEMPTS
        self.retry_delay = settings.SERVICE_RETRY_DELAY
        
        # Metrics
        self.integration_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time_ms": 0,
            "service_availability": {},
        }
        
        logger.info("Service integrator initialized")
    
    async def initialize(self):
        """Initialize the service integrator."""
        try:
            # Initialize HTTP clients for each service
            for service_name, service_url in self.service_urls.items():
                timeout = aiohttp.ClientTimeout(total=self.timeout)
                self.service_clients[service_name] = aiohttp.ClientSession(
                    base_url=service_url,
                    timeout=timeout,
                )
                
                # Initialize availability tracking
                self.integration_metrics["service_availability"][service_name] = {
                    "available": False,
                    "last_check": None,
                    "response_time_ms": None,
                }
            
            # Perform initial health checks
            await self._check_all_services_health()
            
            logger.info("✅ Service integrator initialization complete")
            
        except Exception as e:
            logger.error(f"❌ Service integrator initialization failed: {e}")
            raise
    
    async def call_gs_service(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call the GS (Governance Synthesis) service."""
        return await self._call_service("gs", endpoint, data)
    
    async def call_pgc_service(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call the PGC (Policy Governance Compliance) service."""
        return await self._call_service("pgc", endpoint, data)
    
    async def call_ac_service(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call the AC (Autonomous Constitution) service."""
        return await self._call_service("ac", endpoint, data)
    
    async def call_integrity_service(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call the Integrity service."""
        return await self._call_service("integrity", endpoint, data)
    
    async def call_fv_service(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call the FV (Formal Verification) service."""
        return await self._call_service("fv", endpoint, data)
    
    async def call_auth_service(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call the Auth service."""
        return await self._call_service("auth", endpoint, data)
    
    async def call_ec_service(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Call the EC (Evolutionary Computation) service."""
        return await self._call_service("ec", endpoint, data)
    
    async def _call_service(
        self, 
        service_name: str, 
        endpoint: str, 
        data: Dict[str, Any],
        method: str = "POST"
    ) -> Dict[str, Any]:
        """
        Call a specific service with retry logic and error handling.
        
        Args:
            service_name: Name of the service to call
            endpoint: API endpoint to call
            data: Request data
            method: HTTP method (default: POST)
            
        Returns:
            Service response data
        """
        if service_name not in self.service_clients:
            return {"success": False, "error": f"Unknown service: {service_name}"}
        
        client = self.service_clients[service_name]
        
        for attempt in range(self.retry_attempts):
            try:
                start_time = time.time()
                
                # Make HTTP request
                if method.upper() == "POST":
                    async with client.post(f"/api/v1/{endpoint}", json=data) as response:
                        response_data = await self._handle_response(response)
                elif method.upper() == "GET":
                    async with client.get(f"/api/v1/{endpoint}", params=data) as response:
                        response_data = await self._handle_response(response)
                else:
                    return {"success": False, "error": f"Unsupported HTTP method: {method}"}
                
                # Calculate response time
                response_time_ms = (time.time() - start_time) * 1000
                
                # Update metrics
                self._update_metrics(service_name, True, response_time_ms)
                
                return response_data
                
            except aiohttp.ClientError as e:
                logger.warning(f"Service call failed (attempt {attempt + 1}): {service_name}/{endpoint} - {e}")
                
                if attempt < self.retry_attempts - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    self._update_metrics(service_name, False, None)
                    return {
                        "success": False,
                        "error": f"Service call failed after {self.retry_attempts} attempts: {str(e)}",
                        "service": service_name,
                        "endpoint": endpoint,
                    }
            
            except Exception as e:
                logger.error(f"Unexpected error calling service: {service_name}/{endpoint} - {e}")
                self._update_metrics(service_name, False, None)
                return {
                    "success": False,
                    "error": f"Unexpected error: {str(e)}",
                    "service": service_name,
                    "endpoint": endpoint,
                }
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> Dict[str, Any]:
        """Handle HTTP response and extract data."""
        try:
            if response.status == 200:
                response_data = await response.json()
                return {"success": True, "data": response_data}
            elif response.status == 404:
                return {"success": False, "error": "Endpoint not found"}
            elif response.status == 500:
                error_text = await response.text()
                return {"success": False, "error": f"Internal server error: {error_text}"}
            else:
                error_text = await response.text()
                return {
                    "success": False,
                    "error": f"HTTP {response.status}: {error_text}",
                }
        except Exception as e:
            return {"success": False, "error": f"Response parsing error: {str(e)}"}
    
    def _update_metrics(self, service_name: str, success: bool, response_time_ms: Optional[float]):
        """Update integration metrics."""
        self.integration_metrics["total_requests"] += 1
        
        if success:
            self.integration_metrics["successful_requests"] += 1
            
            # Update service availability
            self.integration_metrics["service_availability"][service_name].update({
                "available": True,
                "last_check": time.time(),
                "response_time_ms": response_time_ms,
            })
            
            # Update average response time
            if response_time_ms:
                current_avg = self.integration_metrics["average_response_time_ms"]
                total_successful = self.integration_metrics["successful_requests"]
                new_avg = ((current_avg * (total_successful - 1)) + response_time_ms) / total_successful
                self.integration_metrics["average_response_time_ms"] = new_avg
        else:
            self.integration_metrics["failed_requests"] += 1
            
            # Update service availability
            self.integration_metrics["service_availability"][service_name].update({
                "available": False,
                "last_check": time.time(),
                "response_time_ms": None,
            })
    
    async def _check_all_services_health(self):
        """Check health of all integrated services."""
        for service_name in self.service_urls.keys():
            await self._check_service_health(service_name)
    
    async def _check_service_health(self, service_name: str) -> bool:
        """Check health of a specific service."""
        try:
            client = self.service_clients[service_name]
            start_time = time.time()
            
            async with client.get("/health") as response:
                response_time_ms = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    self.integration_metrics["service_availability"][service_name].update({
                        "available": True,
                        "last_check": time.time(),
                        "response_time_ms": response_time_ms,
                    })
                    return True
                else:
                    self.integration_metrics["service_availability"][service_name].update({
                        "available": False,
                        "last_check": time.time(),
                        "response_time_ms": None,
                    })
                    return False
                    
        except Exception as e:
            logger.warning(f"Health check failed for {service_name}: {e}")
            self.integration_metrics["service_availability"][service_name].update({
                "available": False,
                "last_check": time.time(),
                "response_time_ms": None,
            })
            return False
    
    async def get_integration_metrics(self) -> Dict[str, Any]:
        """Get service integration metrics."""
        return {
            "metrics": self.integration_metrics,
            "service_urls": self.service_urls,
            "configuration": {
                "timeout": self.timeout,
                "retry_attempts": self.retry_attempts,
                "retry_delay": self.retry_delay,
            },
            "last_updated": time.time(),
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for the service integrator."""
        try:
            health_status = {
                "healthy": True,
                "timestamp": time.time(),
                "checks": {},
            }
            
            # Check each service
            for service_name in self.service_urls.keys():
                service_available = await self._check_service_health(service_name)
                health_status["checks"][f"{service_name}_service"] = {
                    "healthy": service_available,
                    "url": self.service_urls[service_name],
                    "response_time_ms": self.integration_metrics["service_availability"][service_name].get("response_time_ms"),
                }
                
                if not service_available:
                    health_status["healthy"] = False
            
            # Overall integration health
            total_requests = self.integration_metrics["total_requests"]
            success_rate = (
                (self.integration_metrics["successful_requests"] / total_requests * 100)
                if total_requests > 0 else 100
            )
            
            health_status["checks"]["integration_performance"] = {
                "healthy": success_rate >= 95,
                "success_rate": round(success_rate, 2),
                "average_response_time_ms": round(self.integration_metrics["average_response_time_ms"], 2),
                "total_requests": total_requests,
            }
            
            if success_rate < 95:
                health_status["healthy"] = False
            
            return health_status
            
        except Exception as e:
            logger.error(f"Service integrator health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": time.time(),
            }
    
    async def shutdown(self):
        """Shutdown the service integrator gracefully."""
        try:
            logger.info("Shutting down service integrator...")
            
            # Close all HTTP clients
            for service_name, client in self.service_clients.items():
                await client.close()
                logger.info(f"Closed client for {service_name} service")
            
            logger.info("✅ Service integrator shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during service integrator shutdown: {e}")
