"""
A2A (Agent-to-Agent) Policy Integration Service
Constitutional Hash: cdd01ef066bc6cf2
Port: 8020

Secure agent-to-agent communication with constitutional compliance validation.
Provides protocol-agnostic messaging, authentication, and policy enforcement.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from uuid import UUID, uuid4
import hashlib
import hmac
import base64

import aiohttp
import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import jwt

from .models import (
    A2AAgentIdentity,
    A2AMessage,
    A2AMessageRoute,
    A2AConversation,
    A2ASecurityPolicy,
    A2ACapabilityAdvertisement,
    A2AServiceDiscovery,
    A2AMetrics,
    A2AOperation,
    ConstitutionalContext,
    ConstitutionalValidation,
    A2AProtocolType,
    A2AMessageType,
    A2AAgentType,
    A2ASecurityLevel,
    A2AMessageStatus,
    A2AAuthenticationMethod,
)

# Initialize FastAPI app
app = FastAPI(
    title="A2A Policy Integration Service",
    description="Agent-to-Agent communication with constitutional compliance",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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

# JWT Secret for agent authentication
JWT_SECRET = "acgs-2-a2a-constitutional-secret"


class A2AConstitutionalValidator:
    """Constitutional compliance validator for A2A operations"""

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH

    def validate_agent_registration(
        self, agent: A2AAgentIdentity, context: ConstitutionalContext
    ) -> ConstitutionalValidation:
        """Validate agent registration for constitutional compliance"""

        violations = []
        recommendations = []
        compliance_score = 1.0

        # Validate constitutional hash
        if context.constitutional_hash != self.constitutional_hash:
            violations.append(
                f"Invalid constitutional hash: {context.constitutional_hash}"
            )
            compliance_score -= 0.5

        # Validate agent type
        if agent.agent_type not in [
            A2AAgentType.CLAUDE_AGENT,
            A2AAgentType.OPENCODE_AGENT,
            A2AAgentType.MCP_SERVICE,
            A2AAgentType.CORE_SERVICE,
        ]:
            violations.append(f"Unrecognized agent type: {agent.agent_type}")
            compliance_score -= 0.3

        # Validate security level
        if agent.security_level == A2ASecurityLevel.PUBLIC:
            recommendations.append("Consider upgrading to INTERNAL security level")
            compliance_score -= 0.1

        # Validate authentication methods
        if not agent.authentication_methods:
            violations.append("No authentication methods specified")
            compliance_score -= 0.4

        return ConstitutionalValidation(
            is_compliant=len(violations) == 0,
            compliance_score=max(0.0, compliance_score),
            violations=violations,
            recommendations=recommendations,
        )

    def validate_message(
        self,
        message: A2AMessage,
        sender: A2AAgentIdentity,
        recipient: Optional[A2AAgentIdentity] = None,
    ) -> ConstitutionalValidation:
        """Validate message for constitutional compliance"""

        violations = []
        recommendations = []
        compliance_score = 1.0

        # Validate constitutional context
        if (
            message.constitutional_context.constitutional_hash
            != self.constitutional_hash
        ):
            violations.append("Invalid constitutional hash in message context")
            compliance_score -= 0.5

        # Validate message size
        payload_size = len(json.dumps(message.payload).encode("utf-8"))
        if payload_size > 10 * 1024 * 1024:  # 10MB
            violations.append(f"Message payload too large: {payload_size} bytes")
            compliance_score -= 0.3

        # Validate security level compatibility
        if recipient and message.security_level.value > recipient.security_level.value:
            violations.append("Message security level exceeds recipient capability")
            compliance_score -= 0.2

        # Validate message TTL
        if message.ttl_seconds > 3600:  # 1 hour max
            recommendations.append("Consider shorter TTL for improved security")
            compliance_score -= 0.1

        # Validate required fields
        if not message.subject or not message.payload:
            violations.append("Message missing required subject or payload")
            compliance_score -= 0.3

        return ConstitutionalValidation(
            is_compliant=len(violations) == 0,
            compliance_score=max(0.0, compliance_score),
            violations=violations,
            recommendations=recommendations,
        )


class A2ASecurityManager:
    """Security manager for A2A communications"""

    def __init__(self):
        self.jwt_secret = JWT_SECRET
        self.security_policy = A2ASecurityPolicy()

    def generate_agent_token(self, agent: A2AAgentIdentity) -> str:
        """Generate JWT token for agent authentication"""

        payload = {
            "agent_id": str(agent.agent_id),
            "agent_name": agent.agent_name,
            "agent_type": agent.agent_type.value,
            "security_level": agent.security_level.value,
            "capabilities": agent.capabilities,
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,  # 1 hour expiry
        }

        return jwt.encode(payload, self.jwt_secret, algorithm="HS256")

    def validate_agent_token(self, token: str) -> Dict[str, Any]:
        """Validate and decode agent JWT token"""

        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])

            # Validate constitutional hash
            if payload.get("constitutional_hash") != CONSTITUTIONAL_HASH:
                raise HTTPException(
                    status_code=403, detail="Invalid constitutional hash"
                )

            return payload

        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def sign_message(self, message: A2AMessage, agent_id: UUID) -> str:
        """Generate message signature"""

        message_data = {
            "message_id": str(message.message_id),
            "sender_id": str(message.sender_id),
            "recipient_id": str(message.recipient_id) if message.recipient_id else None,
            "message_type": message.message_type.value,
            "payload": message.payload,
            "timestamp": message.created_at.isoformat(),
        }

        message_string = json.dumps(message_data, sort_keys=True)
        signature = hmac.new(
            self.jwt_secret.encode("utf-8"),
            message_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        return signature

    def verify_message_signature(self, message: A2AMessage, signature: str) -> bool:
        """Verify message signature"""

        expected_signature = self.sign_message(message, message.sender_id)
        return hmac.compare_digest(signature, expected_signature)


class A2AMessageRouter:
    """Message routing and delivery system"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.active_routes: Dict[UUID, A2AMessageRoute] = {}
        self.delivery_queue = asyncio.Queue()

    async def route_message(self, message: A2AMessage, route: A2AMessageRoute) -> bool:
        """Route message to destination"""

        try:
            self.active_routes[route.route_id] = route

            # Update message status
            message.status = A2AMessageStatus.IN_TRANSIT
            message.sent_at = datetime.utcnow()

            # Store message in Redis for persistence
            await self.redis.hset(
                f"a2a:message:{message.message_id}",
                mapping={
                    "data": json.dumps(message.__dict__, default=str),
                    "route": json.dumps(route.__dict__, default=str),
                },
            )

            # Set TTL for message
            await self.redis.expire(
                f"a2a:message:{message.message_id}", message.ttl_seconds
            )

            # Add to delivery queue
            await self.delivery_queue.put((message, route))

            return True

        except Exception as e:
            logger.error(f"Message routing failed: {str(e)}")
            message.status = A2AMessageStatus.FAILED
            return False

    async def deliver_message(
        self, message: A2AMessage, target_agent: A2AAgentIdentity
    ) -> bool:
        """Deliver message to target agent"""

        try:
            # Simulate delivery to agent endpoint
            async with aiohttp.ClientSession() as session:
                delivery_url = f"{target_agent.service_url}/a2a/receive"

                async with session.post(
                    delivery_url,
                    json={
                        "message": message.__dict__,
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as response:

                    if response.status == 200:
                        message.status = A2AMessageStatus.DELIVERED
                        message.delivered_at = datetime.utcnow()
                        return True
                    else:
                        message.status = A2AMessageStatus.FAILED
                        return False

        except Exception as e:
            logger.error(f"Message delivery failed: {str(e)}")
            message.status = A2AMessageStatus.FAILED
            return False


class A2AServiceRegistry:
    """Service discovery and registration"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.registered_agents: Dict[UUID, A2AAgentIdentity] = {}
        self.service_discoveries: Dict[str, A2AServiceDiscovery] = {}

    async def register_agent(self, agent: A2AAgentIdentity) -> bool:
        """Register agent in service registry"""

        try:
            self.registered_agents[agent.agent_id] = agent

            # Store in Redis
            await self.redis.hset(
                f"a2a:agent:{agent.agent_id}",
                mapping={
                    "data": json.dumps(agent.__dict__, default=str),
                    "last_seen": datetime.utcnow().isoformat(),
                },
            )

            # Set TTL for agent registration
            await self.redis.expire(f"a2a:agent:{agent.agent_id}", 3600)  # 1 hour

            # Update agent count
            await self.redis.incr("a2a:stats:registered_agents")

            logger.info(f"Agent registered: {agent.agent_name} ({agent.agent_id})")
            return True

        except Exception as e:
            logger.error(f"Agent registration failed: {str(e)}")
            return False

    async def discover_agents(
        self,
        agent_type: Optional[A2AAgentType] = None,
        capabilities: Optional[List[str]] = None,
    ) -> List[A2AAgentIdentity]:
        """Discover agents by type and capabilities"""

        discovered_agents = []

        for agent in self.registered_agents.values():
            # Filter by agent type
            if agent_type and agent.agent_type != agent_type:
                continue

            # Filter by capabilities
            if capabilities:
                if not all(cap in agent.capabilities for cap in capabilities):
                    continue

            # Check if agent is active
            if agent.is_active and agent.last_seen > datetime.utcnow() - timedelta(
                minutes=5
            ):
                discovered_agents.append(agent)

        return discovered_agents

    async def heartbeat(self, agent_id: UUID) -> bool:
        """Update agent heartbeat"""

        try:
            if agent_id in self.registered_agents:
                self.registered_agents[agent_id].last_seen = datetime.utcnow()

                # Update in Redis
                await self.redis.hset(
                    f"a2a:agent:{agent_id}", "last_seen", datetime.utcnow().isoformat()
                )

                return True

            return False

        except Exception as e:
            logger.error(f"Heartbeat update failed: {str(e)}")
            return False


# Initialize core components
redis_client = None
constitutional_validator = A2AConstitutionalValidator()
security_manager = A2ASecurityManager()
message_router = None
service_registry = None
metrics = A2AMetrics()


# Authentication dependency
async def authenticate_agent(authorization: str = None) -> Dict[str, Any]:
    """Authenticate agent using JWT token"""

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401, detail="Missing or invalid authorization header"
        )

    token = authorization.split(" ")[1]
    return security_manager.validate_agent_token(token)


# WebSocket connections for real-time messaging
class A2AConnectionManager:
    """Manage WebSocket connections for real-time A2A communication"""

    def __init__(self):
        self.active_connections: Dict[UUID, WebSocket] = {}
        self.agent_connections: Dict[UUID, UUID] = {}  # agent_id -> connection_id

    async def connect(self, websocket: WebSocket, agent_id: UUID) -> UUID:
        """Accept WebSocket connection"""

        await websocket.accept()
        connection_id = uuid4()
        self.active_connections[connection_id] = websocket
        self.agent_connections[agent_id] = connection_id

        logger.info(f"Agent {agent_id} connected via WebSocket")
        return connection_id

    def disconnect(self, agent_id: UUID):
        """Remove WebSocket connection"""

        if agent_id in self.agent_connections:
            connection_id = self.agent_connections[agent_id]
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
            del self.agent_connections[agent_id]

            logger.info(f"Agent {agent_id} disconnected")

    async def send_message(self, agent_id: UUID, message: Dict[str, Any]) -> bool:
        """Send message to specific agent"""

        if agent_id in self.agent_connections:
            connection_id = self.agent_connections[agent_id]
            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    await websocket.send_text(json.dumps(message))
                    return True
                except Exception as e:
                    logger.error(f"Failed to send WebSocket message: {str(e)}")
                    self.disconnect(agent_id)

        return False

    async def broadcast_message(
        self, message: Dict[str, Any], exclude_agent: Optional[UUID] = None
    ):
        """Broadcast message to all connected agents"""

        disconnected_agents = []

        for agent_id, connection_id in self.agent_connections.items():
            if exclude_agent and agent_id == exclude_agent:
                continue

            if connection_id in self.active_connections:
                websocket = self.active_connections[connection_id]
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Failed to broadcast to agent {agent_id}: {str(e)}")
                    disconnected_agents.append(agent_id)

        # Clean up disconnected agents
        for agent_id in disconnected_agents:
            self.disconnect(agent_id)


connection_manager = A2AConnectionManager()


# API Endpoints


@app.get("/health")
async def health_check():
    """Health check endpoint"""

    return {
        "status": "healthy",
        "service": "A2A Policy Integration Service",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "capabilities": ["messaging", "discovery", "authentication"],
        "metrics": {
            "registered_agents": (
                len(service_registry.registered_agents) if service_registry else 0
            ),
            "active_connections": len(connection_manager.active_connections),
            "total_messages": metrics.total_messages_sent
            + metrics.total_messages_received,
            "constitutional_violations": metrics.constitutional_violations,
        },
    }


@app.post("/api/v1/agents/register")
async def register_agent(agent_data: Dict[str, Any]):
    """Register new agent in A2A network"""

    try:
        # Parse agent identity
        agent = A2AAgentIdentity(**agent_data)

        # Create constitutional context
        constitutional_context = ConstitutionalContext(
            constitutional_hash=CONSTITUTIONAL_HASH,
            purpose="Agent registration",
            compliance_level=agent.security_level.name.lower(),
        )

        # Validate constitutional compliance
        validation = constitutional_validator.validate_agent_registration(
            agent, constitutional_context
        )
        if not validation.is_compliant:
            metrics.constitutional_violations += 1
            raise HTTPException(
                status_code=403,
                detail=f"Constitutional compliance violation: {validation.violations}",
            )

        # Register agent
        if not await service_registry.register_agent(agent):
            raise HTTPException(status_code=500, detail="Agent registration failed")

        # Generate authentication token
        token = security_manager.generate_agent_token(agent)

        return {
            "success": True,
            "agent_id": str(agent.agent_id),
            "token": token,
            "constitutional_validation": {
                "compliance_score": validation.compliance_score,
                "recommendations": validation.recommendations,
            },
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid agent data: {str(e)}")
    except Exception as e:
        logger.error(f"Agent registration error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/messages/send")
async def send_message(
    message_data: Dict[str, Any],
    agent_context: Dict[str, Any] = Depends(authenticate_agent),
):
    """Send A2A message"""

    try:
        # Parse message
        message = A2AMessage(**message_data)
        message.sender_id = UUID(agent_context["agent_id"])

        # Get sender agent
        sender = service_registry.registered_agents.get(message.sender_id)
        if not sender:
            raise HTTPException(status_code=404, detail="Sender agent not found")

        # Get recipient agent
        recipient = None
        if message.recipient_id:
            recipient = service_registry.registered_agents.get(message.recipient_id)
            if not recipient:
                raise HTTPException(status_code=404, detail="Recipient agent not found")

        # Validate message
        validation = constitutional_validator.validate_message(
            message, sender, recipient
        )
        if not validation.is_compliant:
            metrics.constitutional_violations += 1
            raise HTTPException(
                status_code=403,
                detail=f"Message validation failed: {validation.violations}",
            )

        # Sign message
        signature = security_manager.sign_message(message, message.sender_id)
        message.signature = signature

        # Create route
        route = A2AMessageRoute(
            message_id=message.message_id,
            sender_id=message.sender_id,
            recipient_id=message.recipient_id or uuid4(),
            routing_strategy="direct" if message.recipient_id else "broadcast",
        )

        # Route message
        if await message_router.route_message(message, route):
            metrics.total_messages_sent += 1

            # Try WebSocket delivery first
            if message.recipient_id:
                websocket_delivered = await connection_manager.send_message(
                    message.recipient_id, {"type": "message", "data": message.__dict__}
                )
                if websocket_delivered:
                    message.status = A2AMessageStatus.DELIVERED
                    message.delivered_at = datetime.utcnow()
            else:
                # Broadcast message
                await connection_manager.broadcast_message(
                    {"type": "broadcast", "data": message.__dict__},
                    exclude_agent=message.sender_id,
                )

            return {
                "success": True,
                "message_id": str(message.message_id),
                "status": message.status.value,
                "constitutional_compliance": validation.compliance_score,
            }
        else:
            metrics.total_messages_failed += 1
            raise HTTPException(status_code=500, detail="Message routing failed")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid message data: {str(e)}")
    except Exception as e:
        logger.error(f"Message send error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/agents/discover")
async def discover_agents(
    agent_type: Optional[str] = None,
    capabilities: Optional[str] = None,
    agent_context: Dict[str, Any] = Depends(authenticate_agent),
):
    """Discover agents in A2A network"""

    try:
        # Parse filters
        agent_type_enum = A2AAgentType(agent_type) if agent_type else None
        capabilities_list = capabilities.split(",") if capabilities else None

        # Discover agents
        agents = await service_registry.discover_agents(
            agent_type_enum, capabilities_list
        )

        return {
            "success": True,
            "agents": [
                {
                    "agent_id": str(agent.agent_id),
                    "agent_name": agent.agent_name,
                    "agent_type": agent.agent_type.value,
                    "capabilities": agent.capabilities,
                    "service_url": agent.service_url,
                    "security_level": agent.security_level.value,
                    "last_seen": agent.last_seen.isoformat(),
                }
                for agent in agents
            ],
            "total_count": len(agents),
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=f"Invalid filter parameters: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Agent discovery error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/agents/heartbeat")
async def agent_heartbeat(agent_context: Dict[str, Any] = Depends(authenticate_agent)):
    """Send agent heartbeat"""

    try:
        agent_id = UUID(agent_context["agent_id"])

        if await service_registry.heartbeat(agent_id):
            return {"success": True, "timestamp": datetime.utcnow().isoformat()}
        else:
            raise HTTPException(status_code=404, detail="Agent not found")

    except Exception as e:
        logger.error(f"Heartbeat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/a2a/{agent_id}")
async def websocket_endpoint(websocket: WebSocket, agent_id: str):
    """WebSocket endpoint for real-time A2A communication"""

    try:
        agent_uuid = UUID(agent_id)
        connection_id = await connection_manager.connect(websocket, agent_uuid)

        # Send welcome message
        await websocket.send_text(
            json.dumps(
                {
                    "type": "welcome",
                    "message": "Connected to A2A Policy Integration Service",
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "connection_id": str(connection_id),
                }
            )
        )

        try:
            while True:
                # Receive messages from agent
                data = await websocket.receive_text()
                message_data = json.loads(data)

                # Process incoming message
                if message_data.get("type") == "heartbeat":
                    await service_registry.heartbeat(agent_uuid)
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "heartbeat_ack",
                                "timestamp": datetime.utcnow().isoformat(),
                            }
                        )
                    )

                elif message_data.get("type") == "message":
                    # Handle incoming A2A message
                    metrics.total_messages_received += 1

                    # Echo acknowledgment
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "message_ack",
                                "message_id": message_data.get("message_id"),
                                "status": "received",
                            }
                        )
                    )

        except WebSocketDisconnect:
            connection_manager.disconnect(agent_uuid)

    except ValueError:
        await websocket.close(code=1008, reason="Invalid agent ID")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await websocket.close(code=1011, reason="Internal server error")


@app.get("/api/v1/metrics")
async def get_metrics():
    """Get A2A service metrics"""

    return {
        "total_messages_sent": metrics.total_messages_sent,
        "total_messages_received": metrics.total_messages_received,
        "total_messages_delivered": metrics.total_messages_delivered,
        "total_messages_failed": metrics.total_messages_failed,
        "active_conversations": metrics.active_conversations,
        "connected_agents": len(connection_manager.active_connections),
        "registered_agents": (
            len(service_registry.registered_agents) if service_registry else 0
        ),
        "average_delivery_time_ms": metrics.average_delivery_time_ms,
        "constitutional_violations": metrics.constitutional_violations,
        "security_violations": metrics.security_violations,
        "constitutional_hash": CONSTITUTIONAL_HASH,
    }


@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""

    global redis_client, message_router, service_registry

    logger.info("Starting A2A Policy Integration Service")
    logger.info(f"Constitutional Hash: {CONSTITUTIONAL_HASH}")

    try:
        # Initialize Redis connection
        redis_client = redis.from_url(
            "redis://localhost:6389/3", decode_responses=False
        )
        await redis_client.ping()

        # Initialize core components
        message_router = A2AMessageRouter(redis_client)
        service_registry = A2AServiceRegistry(redis_client)

        logger.info("A2A Policy Integration Service initialization complete")

    except Exception as e:
        logger.error(f"Startup error: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""

    if redis_client:
        await redis_client.close()

    logger.info("A2A Policy Integration Service shutdown complete")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8020)
