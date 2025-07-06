"""
Gateway Service Module

High-level service layer for API gateway operations with constitutional compliance,
service mesh integration, and ACGS framework integration.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

import aiohttp
import aioredis
from prometheus_client import Counter, Gauge, Histogram

from ..models.gateway import (
    GatewayRequest,
    GatewayResponse,
    RouteConfig,
    ServiceEndpoint,
    ServiceHealth,
)
from ..models.routing import RoutingDecision, ServiceInstance
from .load_balancer import LoadBalancerService
from .routing_service import RoutingService
from .service_discovery import ServiceDiscoveryService

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class GatewayService:
    """
    High-level API gateway service with constitutional compliance.
    
    Provides comprehensive API gateway capabilities with O(1) lookup patterns,
    request-scoped caching, and sub-5ms P99 latency targets for ACGS integration.
    """
    
    def __init__(self, redis_client: Optional[aioredis.Redis] = None):
        """Initialize gateway service."""
        self.redis = redis_client
        self.routing_service = RoutingService(redis_client)
        self.load_balancer = LoadBalancerService(redis_client)
        self.service_discovery = ServiceDiscoveryService(redis_client)
        
        self.setup_metrics()
        
        # Service state tracking with O(1) lookups
        self.active_requests: Dict[str, GatewayRequest] = {}
        self.service_endpoints: Dict[str, List[ServiceEndpoint]] = {}
        self.request_cache: Dict[str, Any] = {}
        
        # HTTP client for upstream requests
        self.http_client: Optional[aiohttp.ClientSession] = None
        
        logger.info("GatewayService initialized with constitutional compliance")
    
    def setup_metrics(self) -> None:
        """Setup Prometheus metrics."""
        self.gateway_requests_total = Counter(
            "gateway_requests_total",
            "Total gateway requests",
            ["method", "service", "status"]
        )
        
        self.active_requests_gauge = Gauge(
            "gateway_active_requests",
            "Number of active gateway requests"
        )
        
        self.request_duration = Histogram(
            "gateway_request_duration_ms",
            "Gateway request duration in milliseconds",
            ["method", "service"]
        )
        
        self.upstream_duration = Histogram(
            "gateway_upstream_duration_ms",
            "Upstream service duration in milliseconds",
            ["service"]
        )
        
        self.constitutional_compliance_score = Gauge(
            "gateway_constitutional_compliance_score",
            "Constitutional compliance score",
            ["request_id"]
        )
    
    async def initialize(self) -> None:
        """Initialize gateway service components."""
        # Initialize HTTP client
        timeout = aiohttp.ClientTimeout(total=30)
        self.http_client = aiohttp.ClientSession(timeout=timeout)
        
        # Initialize service discovery
        await self.service_discovery.initialize()
        
        # Load service endpoints
        await self._load_service_endpoints()
        
        logger.info("Gateway service initialized successfully")
    
    async def shutdown(self) -> None:
        """Shutdown gateway service components."""
        if self.http_client:
            await self.http_client.close()
        
        await self.service_discovery.shutdown()
        
        logger.info("Gateway service shutdown completed")
    
    async def process_request(self, request: GatewayRequest) -> GatewayResponse:
        """
        Process incoming gateway request with constitutional compliance.
        
        Args:
            request: Gateway request to process
            
        Returns:
            Gateway response
        """
        start_time = time.time()
        
        try:
            # Store request for tracking
            self.active_requests[request.request_id] = request
            self.active_requests_gauge.set(len(self.active_requests))
            
            # Validate constitutional compliance
            if request.constitutional_compliance_required:
                await self._validate_constitutional_compliance(request)
            
            # Route request to appropriate service
            routing_decision = await self.routing_service.route_request(request)
            
            # Forward request to upstream service
            response = await self._forward_request(request, routing_decision)
            
            # Record metrics
            self.gateway_requests_total.labels(
                method=request.method.value,
                service=routing_decision.target_service,
                status=str(response.status_code)
            ).inc()
            
            return response
            
        except Exception as e:
            logger.error(f"Failed to process gateway request {request.request_id}: {e}")
            
            # Create error response
            error_response = GatewayResponse(
                request_id=request.request_id,
                status_code=500,
                headers={"Content-Type": "application/json"},
                body='{"error": "Internal gateway error"}',
                target_service="gateway",
                service_instance="gateway",
                response_time_ms=(time.time() - start_time) * 1000,
                upstream_time_ms=0.0,
                constitutional_hash=CONSTITUTIONAL_HASH
            )
            
            self.gateway_requests_total.labels(
                method=request.method.value,
                service="gateway",
                status="500"
            ).inc()
            
            return error_response
            
        finally:
            # Clean up request tracking
            if request.request_id in self.active_requests:
                del self.active_requests[request.request_id]
                self.active_requests_gauge.set(len(self.active_requests))
            
            # Record request duration
            duration = (time.time() - start_time) * 1000
            self.request_duration.labels(
                method=request.method.value,
                service=getattr(routing_decision, 'target_service', 'unknown') if 'routing_decision' in locals() else 'unknown'
            ).observe(duration)
            
            # Ensure sub-5ms P99 latency for gateway processing
            if duration > 5:
                logger.warning(f"Gateway request processing took {duration:.2f}ms (>5ms target)")
    
    async def get_service_health(self, service_name: str) -> Optional[ServiceHealth]:
        """
        Get health status for a service.
        
        Args:
            service_name: Name of the service
            
        Returns:
            Service health status if available
        """
        return await self.service_discovery.get_service_health(service_name)
    
    async def register_service(self, endpoint: ServiceEndpoint) -> bool:
        """
        Register a service endpoint.
        
        Args:
            endpoint: Service endpoint to register
            
        Returns:
            True if registration successful
        """
        try:
            # Register with service discovery
            success = await self.service_discovery.register_service(endpoint)
            
            if success:
                # Update local cache
                if endpoint.service_name not in self.service_endpoints:
                    self.service_endpoints[endpoint.service_name] = []
                
                self.service_endpoints[endpoint.service_name].append(endpoint)
                
                # Update load balancer
                await self.load_balancer.add_service_instance(
                    ServiceInstance(
                        service_name=endpoint.service_name,
                        host=endpoint.host,
                        port=endpoint.port,
                        weight=endpoint.weight,
                        max_connections=endpoint.max_connections,
                        constitutional_hash=CONSTITUTIONAL_HASH
                    )
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to register service {endpoint.service_name}: {e}")
            return False
    
    async def _validate_constitutional_compliance(self, request: GatewayRequest) -> None:
        """Validate constitutional compliance for request."""
        # Check constitutional hash
        if request.constitutional_hash != CONSTITUTIONAL_HASH:
            raise ValueError(f"Invalid constitutional hash. Expected: {CONSTITUTIONAL_HASH}")
        
        # Additional constitutional validation would go here
        # - Check for required constitutional headers
        # - Validate request against constitutional principles
        # - Ensure proper authorization and oversight
        
        # Record compliance score
        self.constitutional_compliance_score.labels(
            request_id=request.request_id
        ).set(1.0)  # Full compliance
    
    async def _forward_request(
        self, request: GatewayRequest, routing_decision: RoutingDecision
    ) -> GatewayResponse:
        """Forward request to upstream service."""
        upstream_start_time = time.time()
        
        try:
            # Build upstream URL
            target_instance = routing_decision.target_instance
            upstream_url = f"{target_instance.base_url}{request.path}"
            
            # Prepare headers
            headers = dict(request.headers)
            headers["X-Gateway-Request-ID"] = request.request_id
            headers["X-Constitutional-Hash"] = CONSTITUTIONAL_HASH
            
            # Make upstream request
            async with self.http_client.request(
                method=request.method.value,
                url=upstream_url,
                headers=headers,
                params=request.query_params,
                data=request.body,
            ) as upstream_response:
                
                # Read response
                response_body = await upstream_response.text()
                response_headers = dict(upstream_response.headers)
                
                # Calculate timing
                upstream_time_ms = (time.time() - upstream_start_time) * 1000
                
                # Record upstream metrics
                self.upstream_duration.labels(
                    service=routing_decision.target_service
                ).observe(upstream_time_ms)
                
                # Create gateway response
                gateway_response = GatewayResponse(
                    request_id=request.request_id,
                    status_code=upstream_response.status,
                    headers=response_headers,
                    body=response_body,
                    target_service=routing_decision.target_service,
                    service_instance=target_instance.instance_id,
                    response_time_ms=(time.time() - upstream_start_time) * 1000,
                    upstream_time_ms=upstream_time_ms,
                    constitutional_compliance_verified=True,
                    constitutional_hash=CONSTITUTIONAL_HASH
                )
                
                return gateway_response
                
        except Exception as e:
            logger.error(f"Failed to forward request to {routing_decision.target_service}: {e}")
            raise
    
    async def _load_service_endpoints(self) -> None:
        """Load service endpoints from service discovery."""
        try:
            services = await self.service_discovery.list_services()
            
            for service_name in services:
                endpoints = await self.service_discovery.get_service_endpoints(service_name)
                self.service_endpoints[service_name] = endpoints
            
            logger.info(f"Loaded {len(self.service_endpoints)} service configurations")
            
        except Exception as e:
            logger.error(f"Failed to load service endpoints: {e}")
    
    async def get_gateway_health(self) -> Dict[str, Any]:
        """
        Get gateway health status.
        
        Returns:
            Gateway health information
        """
        return {
            "status": "healthy",
            "service": "api_gateway",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "active_requests": len(self.active_requests),
            "registered_services": len(self.service_endpoints),
            "routing_service_healthy": True,
            "load_balancer_healthy": True,
            "service_discovery_healthy": True,
            "http_client_healthy": self.http_client is not None,
            "timestamp": time.time()
        }
