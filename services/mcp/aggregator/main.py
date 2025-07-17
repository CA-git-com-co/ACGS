"""
MCP Aggregator Service
Constitutional Hash: cdd01ef066bc6cf2
Port: 3000

Model Context Protocol coordination hub with service registry,
health monitoring, and constitutional validation framework.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from uuid import UUID, uuid4

import aiohttp
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .models import (
    MCPService,
    MCPSession,
    MCPRequest,
    MCPResponse,
    MCPTool,
    MCPResource,
    MCPCapability,
    MCPMethod,
    ServiceStatus,
    ConstitutionalContext,
    ConstitutionalValidation,
    ServiceHealth,
    ServiceRegistry,
    HealthMonitor,
    SessionManager,
    LoadBalancer,
    MCPAggregatorMetrics,
    ToolOrchestrator,
    ResourceManager
)

# Initialize FastAPI app
app = FastAPI(
    title="MCP Aggregator Service",
    description="Model Context Protocol coordination hub with constitutional compliance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constitutional hash validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class MCPServiceRegistry:
    """Registry for managing MCP services"""
    
    def __init__(self):
        self.services: Dict[UUID, MCPService] = {}
        self.tool_mappings: Dict[str, UUID] = {}
        self.resource_mappings: Dict[str, UUID] = {}
        self.capability_index: Dict[MCPCapability, List[UUID]] = {}
        self.health_monitor = MCPHealthMonitor()
    
    async def register_service(self, service: MCPService) -> bool:
        """Register new MCP service with constitutional validation"""
        
        # Validate constitutional compliance
        if service.constitutional_hash != CONSTITUTIONAL_HASH:
            raise ValueError("Invalid constitutional hash")
        
        # Health check
        if not await self.health_monitor.check_service_health(service):
            raise ValueError("Service health check failed")
        
        # Register service
        self.services[service.service_id] = service
        
        # Index tools
        for tool in service.tools:
            self.tool_mappings[tool.name] = service.service_id
        
        # Index resources
        for resource in service.resources:
            self.resource_mappings[resource.uri] = service.service_id
        
        # Index capabilities
        for capability in service.capabilities:
            if capability not in self.capability_index:
                self.capability_index[capability] = []
            self.capability_index[capability].append(service.service_id)
        
        logger.info(f"Registered MCP service: {service.name} ({service.service_id})")
        return True
    
    async def find_service_for_tool(self, tool_name: str) -> Optional[MCPService]:
        """Find service that provides specific tool"""
        service_id = self.tool_mappings.get(tool_name)
        return self.services.get(service_id) if service_id else None
    
    async def find_service_for_resource(self, resource_uri: str) -> Optional[MCPService]:
        """Find service that provides specific resource"""
        service_id = self.resource_mappings.get(resource_uri)
        return self.services.get(service_id) if service_id else None
    
    async def get_services_by_capability(self, capability: MCPCapability) -> List[MCPService]:
        """Get all services that support a specific capability"""
        service_ids = self.capability_index.get(capability, [])
        return [self.services[sid] for sid in service_ids if sid in self.services]
    
    async def unregister_service(self, service_id: UUID) -> bool:
        """Unregister MCP service"""
        if service_id not in self.services:
            return False
        
        service = self.services[service_id]
        
        # Remove tool mappings
        for tool in service.tools:
            self.tool_mappings.pop(tool.name, None)
        
        # Remove resource mappings
        for resource in service.resources:
            self.resource_mappings.pop(resource.uri, None)
        
        # Remove capability mappings
        for capability in service.capabilities:
            if capability in self.capability_index:
                self.capability_index[capability] = [
                    sid for sid in self.capability_index[capability] if sid != service_id
                ]
        
        # Remove service
        del self.services[service_id]
        
        logger.info(f"Unregistered MCP service: {service.name} ({service_id})")
        return True


class MCPHealthMonitor:
    """Health monitoring for MCP services"""
    
    def __init__(self):
        self.service_health: Dict[UUID, ServiceHealth] = {}
        self.health_check_interval = 30  # seconds
        self.health_check_timeout = 5  # seconds
        self._running = False
    
    async def start_monitoring(self):
        """Start continuous health monitoring"""
        self._running = True
        asyncio.create_task(self._health_check_loop())
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        self._running = False
    
    async def check_service_health(self, service: MCPService) -> bool:
        """Check health of a specific service"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    service.health_check_url,
                    timeout=aiohttp.ClientTimeout(total=self.health_check_timeout)
                ) as response:
                    if response.status == 200:
                        self.service_health[service.service_id] = ServiceHealth(
                            service_id=service.service_id,
                            status=ServiceStatus.HEALTHY,
                            last_check=datetime.utcnow(),
                            response_time_ms=(response.headers.get('X-Response-Time', '0')),
                            constitutional_compliance=True
                        )
                        return True
                    else:
                        self._mark_unhealthy(service.service_id, f"HTTP {response.status}")
                        return False
        except Exception as e:
            self._mark_unhealthy(service.service_id, str(e))
            return False
    
    def _mark_unhealthy(self, service_id: UUID, error: str):
        """Mark service as unhealthy"""
        self.service_health[service_id] = ServiceHealth(
            service_id=service_id,
            status=ServiceStatus.UNHEALTHY,
            last_check=datetime.utcnow(),
            error_message=error,
            constitutional_compliance=False
        )
    
    async def _health_check_loop(self):
        """Continuous health checking loop"""
        while self._running:
            # Health checks would be implemented here
            await asyncio.sleep(self.health_check_interval)


class MCPConstitutionalValidator:
    """Constitutional validation for MCP operations"""
    
    def __init__(self):
        self.constitutional_ai_url = "http://constitutional_core:8001"
        self.session = None
    
    async def validate_mcp_request(
        self,
        request: MCPRequest,
        context: ConstitutionalContext
    ) -> ConstitutionalValidation:
        """Validate MCP request for constitutional compliance"""
        
        # Basic constitutional hash validation
        if context.constitutional_hash != CONSTITUTIONAL_HASH:
            return ConstitutionalValidation(
                is_compliant=False,
                compliance_score=0.0,
                violations=["Invalid constitutional hash"],
                recommendations=["Update constitutional hash to current version"]
            )
        
        # Tool-specific validation
        if request.method == MCPMethod.TOOLS_CALL:
            return await self._validate_tool_call(request, context)
        
        # Resource-specific validation
        elif request.method == MCPMethod.RESOURCES_READ:
            return await self._validate_resource_access(request, context)
        
        # Default validation
        return ConstitutionalValidation(
            is_compliant=True,
            compliance_score=1.0,
            violations=[],
            recommendations=[]
        )
    
    async def _validate_tool_call(
        self,
        request: MCPRequest,
        context: ConstitutionalContext
    ) -> ConstitutionalValidation:
        """Validate tool call for constitutional compliance"""
        
        # Check if tool requires constitutional approval
        tool_name = request.parameters.get("name", "")
        
        # High-risk tools require additional validation
        high_risk_tools = ["file_write", "system_execute", "database_modify"]
        
        if tool_name in high_risk_tools:
            if context.compliance_level.value != "high":
                return ConstitutionalValidation(
                    is_compliant=False,
                    compliance_score=0.3,
                    violations=[f"Tool '{tool_name}' requires high compliance level"],
                    recommendations=["Upgrade compliance level for this operation"]
                )
        
        return ConstitutionalValidation(
            is_compliant=True,
            compliance_score=0.95,
            violations=[],
            recommendations=[]
        )
    
    async def _validate_resource_access(
        self,
        request: MCPRequest,
        context: ConstitutionalContext
    ) -> ConstitutionalValidation:
        """Validate resource access for constitutional compliance"""
        
        resource_uri = request.parameters.get("uri", "")
        
        # Check for sensitive paths
        sensitive_patterns = ["/etc/", "/sys/", "/proc/", "/.ssh/", "/.env"]
        
        for pattern in sensitive_patterns:
            if pattern in resource_uri:
                return ConstitutionalValidation(
                    is_compliant=False,
                    compliance_score=0.1,
                    violations=[f"Access to sensitive path '{pattern}' not allowed"],
                    recommendations=["Use appropriate service APIs for system access"]
                )
        
        return ConstitutionalValidation(
            is_compliant=True,
            compliance_score=1.0,
            violations=[],
            recommendations=[]
        )


class MCPLoadBalancer:
    """Load balancer for MCP services"""
    
    def __init__(self, service_registry: MCPServiceRegistry):
        self.service_registry = service_registry
        self.request_counts: Dict[UUID, int] = {}
    
    async def select_service_instance(
        self,
        capability: MCPCapability,
        tool_name: Optional[str] = None
    ) -> Optional[MCPService]:
        """Select optimal service instance for request"""
        
        if tool_name:
            # Find specific service for tool
            return await self.service_registry.find_service_for_tool(tool_name)
        
        # Get services by capability
        services = await self.service_registry.get_services_by_capability(capability)
        
        if not services:
            return None
        
        # Simple round-robin load balancing
        healthy_services = [
            svc for svc in services 
            if self.service_registry.health_monitor.service_health.get(
                svc.service_id, ServiceHealth()
            ).status == ServiceStatus.HEALTHY
        ]
        
        if not healthy_services:
            return None
        
        # Select service with lowest request count
        selected_service = min(
            healthy_services,
            key=lambda svc: self.request_counts.get(svc.service_id, 0)
        )
        
        # Increment request count
        self.request_counts[selected_service.service_id] = (
            self.request_counts.get(selected_service.service_id, 0) + 1
        )
        
        return selected_service


class MCPAggregator:
    """Main MCP aggregator orchestrator"""
    
    def __init__(self):
        self.service_registry = MCPServiceRegistry()
        self.constitutional_validator = MCPConstitutionalValidator()
        self.load_balancer = MCPLoadBalancer(self.service_registry)
        self.session_manager = MCPSessionManager()
        self.metrics = MCPAggregatorMetrics()
    
    async def handle_mcp_request(self, request: MCPRequest) -> MCPResponse:
        """Handle MCP request with constitutional validation and service routing"""
        
        start_time = datetime.utcnow()
        
        try:
            # 1. Session validation
            session = await self.session_manager.get_session(request.session_id)
            if not session or not await self.session_manager.is_session_valid(session):
                return MCPResponse.create_error(
                    "Invalid or expired session",
                    {"session_id": str(request.session_id)}
                )
            
            # 2. Constitutional validation
            constitutional_check = await self.constitutional_validator.validate_mcp_request(
                request, session.constitutional_context
            )
            
            if not constitutional_check.is_compliant:
                self.metrics.constitutional_violations += 1
                return MCPResponse.create_error(
                    "Constitutional compliance violation",
                    {"violations": constitutional_check.violations}
                )
            
            # 3. Service selection
            if request.method == MCPMethod.TOOLS_CALL:
                tool_name = request.parameters.get("name")
                target_service = await self.service_registry.find_service_for_tool(tool_name)
            elif request.method == MCPMethod.RESOURCES_READ:
                resource_uri = request.parameters.get("uri")
                target_service = await self.service_registry.find_service_for_resource(resource_uri)
            else:
                # Use load balancer for general requests
                target_service = await self.load_balancer.select_service_instance(
                    MCPCapability.TOOLS
                )
            
            if not target_service:
                return MCPResponse.create_error(
                    "No available service for request",
                    {"method": request.method.value}
                )
            
            # 4. Forward request to service
            response = await self._forward_request_to_service(target_service, request)
            
            # 5. Update metrics
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            self.metrics.average_latency_ms = (
                (self.metrics.average_latency_ms * (self.metrics.total_requests - 1) + execution_time) /
                self.metrics.total_requests
            )
            
            return response
            
        except Exception as e:
            self.metrics.failed_requests += 1
            logger.error(f"MCP request handling error: {str(e)}")
            return MCPResponse.create_error(
                "Internal aggregator error",
                {"error": str(e)}
            )
    
    async def _forward_request_to_service(
        self,
        service: MCPService,
        request: MCPRequest
    ) -> MCPResponse:
        """Forward MCP request to target service"""
        
        try:
            async with aiohttp.ClientSession() as session:
                # Build service-specific endpoint
                endpoint = f"{service.endpoint}/mcp/{request.method.value.replace('/', '_')}"
                
                async with session.post(
                    endpoint,
                    json=request.to_dict(),
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return MCPResponse.from_dict(response_data)
                    else:
                        return MCPResponse.create_error(
                            f"Service error: HTTP {response.status}",
                            {"service": service.name}
                        )
        
        except aiohttp.ClientError as e:
            return MCPResponse.create_error(
                f"Service communication error: {str(e)}",
                {"service": service.name}
            )


class MCPSessionManager:
    """Session management for MCP clients"""
    
    def __init__(self):
        self.sessions: Dict[UUID, MCPSession] = {}
        self.session_timeout = 3600  # 1 hour
    
    async def create_session(
        self,
        client_info: Dict[str, Any],
        constitutional_context: ConstitutionalContext
    ) -> MCPSession:
        """Create new MCP session"""
        
        session = MCPSession(
            session_id=uuid4(),
            client_id=client_info.get("name", "unknown"),
            constitutional_context=constitutional_context,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            session_metadata=client_info
        )
        
        self.sessions[session.session_id] = session
        return session
    
    async def get_session(self, session_id: UUID) -> Optional[MCPSession]:
        """Get session by ID"""
        return self.sessions.get(session_id)
    
    async def is_session_valid(self, session: MCPSession) -> bool:
        """Check if session is valid and not expired"""
        if not session:
            return False
        
        # Check expiration
        expiration_time = session.last_activity + timedelta(seconds=self.session_timeout)
        if datetime.utcnow() > expiration_time:
            return False
        
        # Update last activity
        session.last_activity = datetime.utcnow()
        return True
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        current_time = datetime.utcnow()
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            expiration_time = session.last_activity + timedelta(seconds=self.session_timeout)
            if current_time > expiration_time:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")


# Initialize services
mcp_aggregator = MCPAggregator()


# API Endpoints

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    
    registered_services = len(mcp_aggregator.service_registry.services)
    healthy_services = sum(
        1 for health in mcp_aggregator.service_registry.health_monitor.service_health.values()
        if health.status == ServiceStatus.HEALTHY
    )
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "registered_services": registered_services,
        "healthy_services": healthy_services,
        "active_sessions": len(mcp_aggregator.session_manager.sessions),
        "metrics": {
            "total_requests": mcp_aggregator.metrics.total_requests,
            "successful_requests": mcp_aggregator.metrics.successful_requests,
            "failed_requests": mcp_aggregator.metrics.failed_requests,
            "average_latency_ms": mcp_aggregator.metrics.average_latency_ms,
            "constitutional_violations": mcp_aggregator.metrics.constitutional_violations
        }
    }


@app.post("/mcp/v1/initialize")
async def initialize_mcp_session(client_info: Dict[str, Any]):
    """Initialize MCP session"""
    
    # Create constitutional context
    constitutional_context = ConstitutionalContext(
        constitutional_hash=CONSTITUTIONAL_HASH,
        purpose="MCP session initialization",
        additional_constraints=["mcp_protocol_compliance"]
    )
    
    # Create session
    session = await mcp_aggregator.session_manager.create_session(
        client_info, constitutional_context
    )
    
    # Get available services
    available_services = [
        {
            "service_id": str(service.service_id),
            "name": service.name,
            "capabilities": [cap.value for cap in service.capabilities],
            "tools": [{"name": tool.name, "description": tool.description} for tool in service.tools],
            "resources": [{"uri": res.uri, "name": res.name} for res in service.resources]
        }
        for service in mcp_aggregator.service_registry.services.values()
    ]
    
    return {
        "session_id": str(session.session_id),
        "serverInfo": {
            "name": "ACGS-2 MCP Aggregator",
            "version": "1.0.0",
            "constitutional_hash": CONSTITUTIONAL_HASH
        },
        "capabilities": {
            "tools": True,
            "resources": True,
            "prompts": True,
            "constitutional_validation": True
        },
        "available_services": available_services
    }


@app.post("/mcp/v1/tools/list")
async def list_tools(request_data: Dict[str, Any]):
    """List available tools across all MCP services"""
    
    session_id = UUID(request_data.get("session_id"))
    session = await mcp_aggregator.session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=400, detail="Invalid session")
    
    # Collect tools from all services
    all_tools = []
    for service in mcp_aggregator.service_registry.services.values():
        for tool in service.tools:
            all_tools.append({
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.input_schema,
                "service_id": str(service.service_id),
                "service_name": service.name,
                "constitutional_requirements": tool.constitutional_requirements
            })
    
    return {"tools": all_tools}


@app.post("/mcp/v1/tools/call")
async def call_tool(request_data: Dict[str, Any]):
    """Execute tool via appropriate MCP service"""
    
    # Create MCP request
    mcp_request = MCPRequest(
        request_id=uuid4(),
        session_id=UUID(request_data.get("session_id")),
        method=MCPMethod.TOOLS_CALL,
        parameters=request_data,
        constitutional_context=ConstitutionalContext(constitutional_hash=CONSTITUTIONAL_HASH),
        timestamp=datetime.utcnow()
    )
    
    # Handle request
    response = await mcp_aggregator.handle_mcp_request(mcp_request)
    
    return response.to_dict()


@app.post("/mcp/v1/resources/list")
async def list_resources(request_data: Dict[str, Any]):
    """List available resources across all MCP services"""
    
    session_id = UUID(request_data.get("session_id"))
    session = await mcp_aggregator.session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=400, detail="Invalid session")
    
    # Collect resources from all services
    all_resources = []
    for service in mcp_aggregator.service_registry.services.values():
        for resource in service.resources:
            all_resources.append({
                "uri": resource.uri,
                "name": resource.name,
                "description": resource.description,
                "mimeType": resource.mime_type,
                "service_id": str(service.service_id),
                "service_name": service.name
            })
    
    return {"resources": all_resources}


@app.post("/mcp/v1/resources/read")
async def read_resource(request_data: Dict[str, Any]):
    """Read resource content via appropriate MCP service"""
    
    # Create MCP request
    mcp_request = MCPRequest(
        request_id=uuid4(),
        session_id=UUID(request_data.get("session_id")),
        method=MCPMethod.RESOURCES_READ,
        parameters=request_data,
        constitutional_context=ConstitutionalContext(constitutional_hash=CONSTITUTIONAL_HASH),
        timestamp=datetime.utcnow()
    )
    
    # Handle request
    response = await mcp_aggregator.handle_mcp_request(mcp_request)
    
    return response.to_dict()


@app.get("/api/v1/services")
async def get_services():
    """Get all registered MCP services"""
    
    services = []
    for service in mcp_aggregator.service_registry.services.values():
        health = mcp_aggregator.service_registry.health_monitor.service_health.get(
            service.service_id, ServiceHealth()
        )
        
        services.append({
            "service_id": str(service.service_id),
            "name": service.name,
            "endpoint": service.endpoint,
            "port": service.port,
            "capabilities": [cap.value for cap in service.capabilities],
            "status": health.status.value,
            "tools_count": len(service.tools),
            "resources_count": len(service.resources),
            "constitutional_hash": service.constitutional_hash
        })
    
    return {"services": services}


@app.post("/api/v1/services")
async def register_service(service_data: Dict[str, Any]):
    """Register new MCP service"""
    
    try:
        # Create MCPService from request data
        service = MCPService(
            service_id=uuid4(),
            name=service_data["name"],
            endpoint=service_data["endpoint"],
            port=service_data["port"],
            capabilities=[MCPCapability(cap) for cap in service_data["capabilities"]],
            constitutional_hash=service_data.get("constitutional_hash", CONSTITUTIONAL_HASH),
            health_check_url=f"{service_data['endpoint']}/health",
            tools=[],  # Tools would be discovered via service introspection
            resources=[]  # Resources would be discovered via service introspection
        )
        
        # Register service
        success = await mcp_aggregator.service_registry.register_service(service)
        
        if success:
            return {
                "service_id": str(service.service_id),
                "registration_status": "success"
            }
        else:
            raise HTTPException(status_code=400, detail="Service registration failed")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/services/{service_id}/health")
async def get_service_health(service_id: str):
    """Get service health status"""
    
    try:
        service_uuid = UUID(service_id)
        health = mcp_aggregator.service_registry.health_monitor.service_health.get(service_uuid)
        
        if not health:
            raise HTTPException(status_code=404, detail="Service not found")
        
        return {
            "status": health.status.value,
            "last_check": health.last_check.isoformat(),
            "response_time_ms": health.response_time_ms,
            "constitutional_compliance": health.constitutional_compliance,
            "error_message": health.error_message
        }
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid service ID")


@app.websocket("/ws/mcp-stream")
async def mcp_websocket_stream(websocket: WebSocket):
    """WebSocket for real-time MCP operations"""
    
    await websocket.accept()
    
    try:
        while True:
            # Receive MCP request
            data = await websocket.receive_json()
            
            # Create MCP request
            mcp_request = MCPRequest(
                request_id=uuid4(),
                session_id=UUID(data.get("session_id", str(uuid4()))),
                method=MCPMethod(data.get("method", "tools/call")),
                parameters=data.get("parameters", {}),
                constitutional_context=ConstitutionalContext(constitutional_hash=CONSTITUTIONAL_HASH),
                timestamp=datetime.utcnow()
            )
            
            # Handle request
            response = await mcp_aggregator.handle_mcp_request(mcp_request)
            
            # Send response
            await websocket.send_json(response.to_dict())
            
    except WebSocketDisconnect:
        logger.info("MCP WebSocket client disconnected")
    except Exception as e:
        logger.error(f"MCP WebSocket error: {str(e)}")
        await websocket.close()


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    
    logger.info("Starting MCP Aggregator Service")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")
    
    # Start health monitoring
    await mcp_aggregator.service_registry.health_monitor.start_monitoring()
    
    # Start session cleanup task
    asyncio.create_task(periodic_session_cleanup())
    
    logger.info("MCP Aggregator Service initialization complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    
    # Stop health monitoring
    await mcp_aggregator.service_registry.health_monitor.stop_monitoring()
    
    # Close constitutional validator session
    if mcp_aggregator.constitutional_validator.session:
        await mcp_aggregator.constitutional_validator.session.close()
    
    logger.info("MCP Aggregator Service shutdown complete")


async def periodic_session_cleanup():
    """Periodic cleanup of expired sessions"""
    
    while True:
        await asyncio.sleep(300)  # 5 minutes
        await mcp_aggregator.session_manager.cleanup_expired_sessions()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)