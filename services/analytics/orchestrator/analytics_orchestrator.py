#!/usr/bin/env python3
"""
ACGS Analytics Microservices Orchestrator

Orchestrates and manages all analytics microservices:
- Service discovery and health monitoring
- Load balancing and request routing
- Distributed processing coordination
- Constitutional compliance enforcement
- Integration with NATS message broker

Constitutional Hash: cdd01ef066bc6cf2
Port: 8013
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Any

import aiohttp
import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Add core modules to path
sys.path.append("../../core/acgs-pgp-v8")
from nats_event_broker import ACGSEvent, NATSEventBroker

logger = logging.getLogger(__name__)


# Pydantic models for API
class ServiceRegistration(BaseModel):
    service_id: str = Field(..., description="Service identifier")
    service_name: str = Field(..., description="Service name")
    host: str = Field(..., description="Service host")
    port: int = Field(..., description="Service port")
    health_endpoint: str = Field(default="/health", description="Health check endpoint")
    capabilities: list[str] = Field(..., description="Service capabilities")
    constitutional_hash: str = Field(
        ..., description="Constitutional hash for validation"
    )


class DistributedAnalysisRequest(BaseModel):
    analysis_type: str = Field(
        ..., description="Type of analysis: quality, drift, performance"
    )
    data: list[dict[str, Any]] = Field(..., description="Data to analyze")
    parameters: dict[str, Any] = Field(default={}, description="Analysis parameters")
    service_id: str = Field(default="unknown", description="Requesting service ID")
    constitutional_hash: str = Field(
        ..., description="Constitutional hash for validation"
    )


class DistributedAnalysisResponse(BaseModel):
    analysis_id: str
    analysis_type: str
    results: dict[str, Any]
    processing_time_ms: float
    services_used: list[str]
    constitutional_hash: str
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    registered_services: int
    constitutional_hash: str
    timestamp: str


class AnalyticsOrchestrator:
    """Analytics Microservices Orchestrator implementation."""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"
        self.service_name = "analytics-orchestrator"
        self.version = "v8.0.0"
        self.port = 8013

        # Initialize FastAPI app
        self.app = FastAPI(
            title="ACGS Analytics Orchestrator",
            description="Orchestrator for analytics microservices",
            version=self.version,
            docs_url="/docs",
            redoc_url="/redoc",
        )

        # Add CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Initialize components
        self.event_broker = NATSEventBroker()

        # Service registry
        self.service_registry: dict[str, ServiceRegistration] = {}
        self.service_health: dict[str, dict[str, Any]] = {}

        # Default analytics services configuration
        self.default_services = {
            "data-quality-service": {
                "host": "localhost",
                "port": 8010,
                "capabilities": ["quality_assessment", "quality_monitoring"],
                "health_endpoint": "/health",
            },
            "drift-detection-service": {
                "host": "localhost",
                "port": 8011,
                "capabilities": ["drift_detection", "drift_monitoring"],
                "health_endpoint": "/health",
            },
            "performance-monitoring-service": {
                "host": "localhost",
                "port": 8012,
                "capabilities": ["performance_monitoring", "sla_tracking"],
                "health_endpoint": "/health",
            },
        }

        # Load balancing and routing
        self.service_load: dict[str, int] = {}
        self.request_routing: dict[str, str] = {
            "quality": "data-quality-service",
            "drift": "drift-detection-service",
            "performance": "performance-monitoring-service",
        }

        # Orchestrator metrics
        self.metrics = {
            "requests_processed": 0,
            "distributed_analyses": 0,
            "service_failures": 0,
            "average_processing_time_ms": 0,
            "uptime_start": datetime.now().isoformat(),
        }

        # Setup routes
        self._setup_routes()

        logger.info(f"Analytics Orchestrator initialized on port {self.port}")

    def _setup_routes(self):
        """Setup FastAPI routes."""

        @self.app.get("/health", response_model=HealthResponse)
        async def health_check():
            """Health check endpoint."""
            return HealthResponse(
                status="healthy",
                service=self.service_name,
                version=self.version,
                registered_services=len(self.service_registry),
                constitutional_hash=self.constitutional_hash,
                timestamp=datetime.now().isoformat(),
            )

        @self.app.get("/metrics")
        async def get_metrics():
            """Get orchestrator metrics."""
            return {
                **self.metrics,
                "service_registry": {
                    service_id: {
                        "host": service.host,
                        "port": service.port,
                        "capabilities": service.capabilities,
                        "health": self.service_health.get(service_id, {}),
                    }
                    for service_id, service in self.service_registry.items()
                },
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.now().isoformat(),
            }

        @self.app.post("/services/register")
        async def register_service(registration: ServiceRegistration):
            """Register an analytics microservice."""

            # Validate constitutional hash
            if registration.constitutional_hash != self.constitutional_hash:
                raise HTTPException(
                    status_code=403, detail="Constitutional hash mismatch"
                )

            # Register service
            self.service_registry[registration.service_id] = registration
            self.service_load[registration.service_id] = 0

            logger.info(
                f"✅ Registered service: {registration.service_id} "
                f"({registration.host}:{registration.port})"
            )

            return {
                "message": f"Service {registration.service_id} registered successfully",
                "capabilities": registration.capabilities,
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.now().isoformat(),
            }

        @self.app.post("/analyze", response_model=DistributedAnalysisResponse)
        async def distributed_analysis(
            request: DistributedAnalysisRequest, background_tasks: BackgroundTasks
        ):
            """Perform distributed analysis across microservices."""

            # Validate constitutional hash
            if request.constitutional_hash != self.constitutional_hash:
                raise HTTPException(
                    status_code=403, detail="Constitutional hash mismatch"
                )

            start_time = datetime.now()

            try:
                # Route request to appropriate service
                target_service = self._route_request(request.analysis_type)

                if not target_service:
                    raise HTTPException(
                        status_code=400,
                        detail=f"No service available for analysis type: {request.analysis_type}",
                    )

                # Perform distributed analysis
                results = await self._execute_distributed_analysis(
                    target_service, request
                )

                # Calculate processing time
                processing_time = (datetime.now() - start_time).total_seconds() * 1000

                # Update metrics
                self.metrics["requests_processed"] += 1
                self.metrics["distributed_analyses"] += 1
                self.metrics["average_processing_time_ms"] = (
                    self.metrics["average_processing_time_ms"]
                    * (self.metrics["requests_processed"] - 1)
                    + processing_time
                ) / self.metrics["requests_processed"]

                # Create response
                analysis_id = f"analysis-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

                response = DistributedAnalysisResponse(
                    analysis_id=analysis_id,
                    analysis_type=request.analysis_type,
                    results=results,
                    processing_time_ms=processing_time,
                    services_used=[target_service],
                    constitutional_hash=self.constitutional_hash,
                    timestamp=datetime.now().isoformat(),
                )

                # Publish analysis event in background
                background_tasks.add_task(
                    self._publish_analysis_event,
                    analysis_id,
                    request.analysis_type,
                    request.service_id,
                    results,
                )

                logger.info(
                    f"✅ Distributed analysis completed: {analysis_id} "
                    f"(type: {request.analysis_type}, "
                    f"service: {target_service}, "
                    f"processing: {processing_time:.1f}ms)"
                )

                return response

            except Exception as e:
                logger.error(f"❌ Distributed analysis failed: {e}")
                self.metrics["service_failures"] += 1
                raise HTTPException(
                    status_code=500, detail=f"Distributed analysis failed: {e!s}"
                )

        @self.app.get("/services")
        async def list_services():
            """List registered analytics services."""

            services = []
            for service_id, service in self.service_registry.items():
                health = self.service_health.get(service_id, {})

                services.append(
                    {
                        "service_id": service_id,
                        "service_name": service.service_name,
                        "host": service.host,
                        "port": service.port,
                        "capabilities": service.capabilities,
                        "health_status": health.get("status", "unknown"),
                        "last_health_check": health.get("last_check", "never"),
                        "load": self.service_load.get(service_id, 0),
                    }
                )

            return {
                "services": services,
                "count": len(services),
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.now().isoformat(),
            }

        @self.app.post("/services/discover")
        async def discover_services():
            """Discover and register default analytics services."""

            discovered_count = 0

            for service_id, config in self.default_services.items():
                try:
                    # Check if service is running
                    health_url = f"http://{config['host']}:{config['port']}{config['health_endpoint']}"

                    async with aiohttp.ClientSession() as session:
                        async with session.get(
                            health_url, timeout=aiohttp.ClientTimeout(total=5)
                        ) as response:
                            if response.status == 200:
                                # Register service
                                registration = ServiceRegistration(
                                    service_id=service_id,
                                    service_name=service_id.replace("-", " ").title(),
                                    host=config["host"],
                                    port=config["port"],
                                    health_endpoint=config["health_endpoint"],
                                    capabilities=config["capabilities"],
                                    constitutional_hash=self.constitutional_hash,
                                )

                                self.service_registry[service_id] = registration
                                self.service_load[service_id] = 0
                                discovered_count += 1

                                logger.info(f"✅ Discovered service: {service_id}")

                except Exception as e:
                    logger.warning(f"⚠️ Failed to discover service {service_id}: {e}")

            return {
                "message": "Service discovery completed",
                "discovered_services": discovered_count,
                "total_services": len(self.service_registry),
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.now().isoformat(),
            }

    def _route_request(self, analysis_type: str) -> str | None:
        """Route analysis request to appropriate service."""

        # Get target service for analysis type
        target_service_id = self.request_routing.get(analysis_type)

        if not target_service_id or target_service_id not in self.service_registry:
            return None

        # Check service health
        health = self.service_health.get(target_service_id, {})
        if health.get("status") != "healthy":
            logger.warning(f"⚠️ Target service {target_service_id} not healthy")
            return None

        return target_service_id

    async def _execute_distributed_analysis(
        self, service_id: str, request: DistributedAnalysisRequest
    ) -> dict[str, Any]:
        """Execute analysis on target microservice."""

        service = self.service_registry[service_id]

        # Increment service load
        self.service_load[service_id] += 1

        try:
            # Prepare request based on analysis type
            if request.analysis_type == "quality":
                endpoint = f"http://{service.host}:{service.port}/assess"
                payload = {
                    "data": request.data,
                    "service_id": request.service_id,
                    "constitutional_hash": self.constitutional_hash,
                    **request.parameters,
                }
            elif request.analysis_type == "drift":
                endpoint = f"http://{service.host}:{service.port}/detect"
                payload = {
                    "reference_data": request.parameters.get("reference_data", []),
                    "current_data": request.data,
                    "model_id": request.parameters.get("model_id", "default"),
                    "service_id": request.service_id,
                    "constitutional_hash": self.constitutional_hash,
                }
            elif request.analysis_type == "performance":
                endpoint = f"http://{service.host}:{service.port}/metrics/submit"
                payload = {
                    "service_id": request.service_id,
                    "metrics": request.parameters.get("metrics", {}),
                    "constitutional_hash": self.constitutional_hash,
                }
            else:
                raise ValueError(f"Unsupported analysis type: {request.analysis_type}")

            # Make request to microservice
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint, json=payload, timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result
                    error_text = await response.text()
                    raise Exception(f"Service returned {response.status}: {error_text}")

        finally:
            # Decrement service load
            self.service_load[service_id] = max(0, self.service_load[service_id] - 1)

    async def _publish_analysis_event(
        self,
        analysis_id: str,
        analysis_type: str,
        service_id: str,
        results: dict[str, Any],
    ):
        """Publish distributed analysis event."""

        try:
            # Create analysis event
            event = ACGSEvent(
                event_type="distributed_analysis_completed",
                timestamp=datetime.now().isoformat(),
                constitutional_hash=self.constitutional_hash,
                source_service=self.service_name,
                target_service=service_id,
                event_id=analysis_id,
                payload={
                    "analysis_type": analysis_type,
                    "results_summary": {
                        key: value
                        for key, value in results.items()
                        if key in ["overall_score", "drift_detected", "sla_compliance"]
                    },
                },
                priority="NORMAL",
            )

            # Publish event
            await self.event_broker.publish_event("acgs.analytics.distributed", event)

        except Exception as e:
            logger.error(f"❌ Failed to publish analysis event: {e}")

    async def _health_monitoring_loop(self):
        """Continuous health monitoring for registered services."""

        while True:
            try:
                for service_id, service in self.service_registry.items():
                    await self._check_service_health(service_id, service)

                await asyncio.sleep(30)  # Check every 30 seconds

            except Exception as e:
                logger.error(f"❌ Error in health monitoring loop: {e}")
                await asyncio.sleep(5)

    async def _check_service_health(
        self, service_id: str, service: ServiceRegistration
    ):
        """Check health of a specific service."""

        try:
            health_url = (
                f"http://{service.host}:{service.port}{service.health_endpoint}"
            )

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    health_url, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        health_data = await response.json()

                        self.service_health[service_id] = {
                            "status": "healthy",
                            "last_check": datetime.now().isoformat(),
                            "response_time_ms": 0,  # Would calculate actual response time
                            "details": health_data,
                        }
                    else:
                        self.service_health[service_id] = {
                            "status": "unhealthy",
                            "last_check": datetime.now().isoformat(),
                            "error": f"HTTP {response.status}",
                        }

        except Exception as e:
            self.service_health[service_id] = {
                "status": "unhealthy",
                "last_check": datetime.now().isoformat(),
                "error": str(e),
            }

            logger.warning(f"⚠️ Health check failed for {service_id}: {e}")

    async def startup(self):
        """Startup tasks for the orchestrator."""

        # Connect to event broker
        await self.event_broker.connect()

        # Start health monitoring
        asyncio.create_task(self._health_monitoring_loop())

        # Discover default services
        await asyncio.sleep(2)  # Give services time to start

        logger.info(f"✅ Analytics Orchestrator started on port {self.port}")

    async def shutdown(self):
        """Shutdown tasks for the orchestrator."""

        # Disconnect from event broker
        await self.event_broker.disconnect()

        logger.info("✅ Analytics Orchestrator shutdown completed")


# Global orchestrator instance
orchestrator = AnalyticsOrchestrator()


# FastAPI event handlers
@orchestrator.app.on_event("startup")
async def startup_event():
    await orchestrator.startup()


@orchestrator.app.on_event("shutdown")
async def shutdown_event():
    await orchestrator.shutdown()


# Main entry point
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run the orchestrator
    uvicorn.run(
        "analytics_orchestrator:orchestrator.app",
        host="0.0.0.0",
        port=orchestrator.port,
        reload=False,
        log_level="info",
    )
