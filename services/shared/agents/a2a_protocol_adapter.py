"""
Agent2Agent (A2A) Protocol Adapter for ACGS

Enables ACGS agents to communicate with external agent frameworks
using Google's A2A Protocol standard for universal interoperability.

Supports communication with:
- LangGraph agents
- CrewAI agents
- AutoGen agents
- Other A2A-compatible frameworks

Key Features:
- HTTP/SSE/JSON-RPC protocol implementation
- Secure authentication with OpenAPI compatibility
- Long-running task support (hours/days)
- Constitutional compliance validation
- Enterprise-grade security and monitoring
"""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

import aiohttp
from pydantic import BaseModel, Field

from services.shared.constitutional_safety_framework import (
    ConstitutionalSafetyValidator,
)
from services.shared.security.enhanced_audit_logging import EnhancedAuditLogger

logger = logging.getLogger(__name__)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class A2AMessageType(Enum):
    """A2A Protocol message types"""

    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    STATUS_UPDATE = "status_update"
    COORDINATION_REQUEST = "coordination_request"
    COORDINATION_RESPONSE = "coordination_response"
    CAPABILITY_INQUIRY = "capability_inquiry"
    CAPABILITY_RESPONSE = "capability_response"
    ERROR_NOTIFICATION = "error_notification"


class A2AMessage(BaseModel):
    """A2A Protocol message structure"""

    message_id: str = Field(..., description="Unique message identifier")
    sender_id: str = Field(..., description="Sender agent/framework ID")
    recipient_id: str = Field(..., description="Recipient agent/framework ID")
    message_type: A2AMessageType = Field(..., description="Type of message")
    content: dict[str, Any] = Field(..., description="Message payload")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    constitutional_hash: str = Field(default=CONSTITUTIONAL_HASH)
    correlation_id: Optional[str] = Field(
        None, description="For request/response correlation"
    )
    expires_at: Optional[datetime] = Field(None, description="Message expiration")
    priority: int = Field(
        default=3, description="Message priority (1=highest, 5=lowest)"
    )


class A2ATaskRequest(BaseModel):
    """A2A Task request structure"""

    task_id: str = Field(..., description="Unique task identifier")
    task_type: str = Field(..., description="Type of task to execute")
    description: str = Field(..., description="Task description")
    parameters: dict[str, Any] = Field(default_factory=dict)
    requirements: dict[str, Any] = Field(default_factory=dict)
    constraints: list[str] = Field(default_factory=list)
    deadline: Optional[datetime] = Field(None)
    callback_url: Optional[str] = Field(None)
    constitutional_requirements: dict[str, Any] = Field(default_factory=dict)


class A2ATaskResponse(BaseModel):
    """A2A Task response structure"""

    task_id: str = Field(..., description="Original task identifier")
    status: str = Field(..., description="Task execution status")
    result: Optional[dict[str, Any]] = Field(None, description="Task result")
    error_message: Optional[str] = Field(None, description="Error details if failed")
    execution_time_seconds: float = Field(default=0.0)
    constitutional_compliance: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


@dataclass
class A2AConnection:
    """A2A Protocol connection configuration"""

    connection_id: str
    framework_name: str  # "langraph", "crewai", "autogen", etc.
    endpoint_url: str
    authentication: dict[str, Any]
    capabilities: list[str]
    is_active: bool = True
    last_heartbeat: Optional[datetime] = None
    message_count: int = 0
    error_count: int = 0


class A2AProtocolAdapter:
    """
    Adapter implementing Google's Agent2Agent (A2A) Protocol
    for interoperability with external agent frameworks.

    Enables ACGS agents to communicate seamlessly with:
    - LangGraph agents
    - CrewAI agents
    - AutoGen agents
    - Any A2A-compatible framework
    """

    def __init__(
        self,
        agent_id: str,
        safety_validator: ConstitutionalSafetyValidator,
        audit_logger: EnhancedAuditLogger,
    ):
        self.agent_id = agent_id
        self.safety_validator = safety_validator
        self.audit_logger = audit_logger

        # HTTP session for A2A communication
        self.session: Optional[aiohttp.ClientSession] = None

        # Active connections to external frameworks
        self.connections: dict[str, A2AConnection] = {}

        # Message tracking
        self.pending_messages: dict[str, A2AMessage] = {}
        self.message_history: list[A2AMessage] = []

        # Performance metrics
        self.metrics = {
            "messages_sent": 0,
            "messages_received": 0,
            "tasks_delegated": 0,
            "tasks_completed": 0,
            "connection_errors": 0,
            "constitutional_violations": 0,
            "average_response_time": 0.0,
        }

        logger.info(f"A2A Protocol Adapter initialized for agent {agent_id}")

    async def initialize(self) -> None:
        """Initialize HTTP session and A2A connections"""
        try:
            # Create HTTP session with proper headers
            headers = {
                "User-Agent": f"ACGS-A2A-Adapter/{self.agent_id}",
                "Content-Type": "application/json",
                "X-Constitutional-Hash": CONSTITUTIONAL_HASH,
            }

            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            self.session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout,
                connector=aiohttp.TCPConnector(limit=100),
            )

            logger.info("A2A Protocol Adapter initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize A2A adapter: {e!s}")
            raise

    async def shutdown(self) -> None:
        """Gracefully shutdown the adapter"""
        try:
            if self.session:
                await self.session.close()

            logger.info("A2A Protocol Adapter shutdown completed")

        except Exception as e:
            logger.error(f"Error during A2A adapter shutdown: {e!s}")

    async def register_framework_connection(
        self,
        framework_name: str,
        endpoint_url: str,
        authentication: dict[str, Any],
        capabilities: list[str],
    ) -> str:
        """Register a connection to an external agent framework"""
        try:
            connection_id = str(uuid.uuid4())

            connection = A2AConnection(
                connection_id=connection_id,
                framework_name=framework_name,
                endpoint_url=endpoint_url,
                authentication=authentication,
                capabilities=capabilities,
                last_heartbeat=datetime.now(timezone.utc),
            )

            # Test connection
            if await self._test_connection(connection):
                self.connections[connection_id] = connection

                await self.audit_logger.log_security_event(
                    {
                        "event_type": "a2a_framework_registered",
                        "framework_name": framework_name,
                        "connection_id": connection_id,
                        "endpoint_url": endpoint_url,
                        "capabilities": capabilities,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                    }
                )

                logger.info(
                    f"Registered A2A connection to {framework_name}: {connection_id}"
                )
                return connection_id
            else:
                raise ConnectionError(
                    f"Failed to establish connection to {framework_name}"
                )

        except Exception as e:
            logger.error(f"Failed to register framework connection: {e!s}")
            raise

    async def send_message(
        self, connection_id: str, message: A2AMessage
    ) -> dict[str, Any]:
        """Send message using A2A protocol"""
        if not self.session:
            await self.initialize()

        try:
            connection = self.connections.get(connection_id)
            if not connection:
                raise ValueError(f"Unknown connection ID: {connection_id}")

            # Validate message against constitutional principles
            is_compliant, compliance_score = await self._validate_message_compliance(
                message
            )
            if not is_compliant:
                self.metrics["constitutional_violations"] += 1
                raise ValueError(
                    f"Message violates constitutional principles: {compliance_score}"
                )

            # Prepare HTTP request
            url = f"{connection.endpoint_url}/a2a/message"
            payload = message.model_dump(mode="json")

            # Add authentication
            headers = await self._prepare_auth_headers(connection)

            # Send message
            start_time = datetime.now(timezone.utc)
            async with self.session.post(
                url, json=payload, headers=headers
            ) as response:
                response_data = await response.json()

                if response.status == 200:
                    # Track metrics
                    response_time = (
                        datetime.now(timezone.utc) - start_time
                    ).total_seconds()
                    self._update_response_time_metric(response_time)
                    self.metrics["messages_sent"] += 1
                    connection.message_count += 1

                    # Store for correlation if needed
                    if message.correlation_id:
                        self.pending_messages[message.correlation_id] = message

                    # Log successful communication
                    await self.audit_logger.log_security_event(
                        {
                            "event_type": "a2a_message_sent",
                            "connection_id": connection_id,
                            "message_id": message.message_id,
                            "message_type": message.message_type.value,
                            "response_time_seconds": response_time,
                            "timestamp": datetime.now(timezone.utc).isoformat(),
                        }
                    )

                    return response_data
                else:
                    connection.error_count += 1
                    self.metrics["connection_errors"] += 1
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status,
                        message=f"A2A message failed: {response_data}",
                    )

        except Exception as e:
            logger.error(f"Failed to send A2A message: {e!s}")
            self.metrics["connection_errors"] += 1
            raise

    async def delegate_task_to_framework(
        self, connection_id: str, task_request: A2ATaskRequest
    ) -> str:
        """Delegate a task to an external agent framework"""
        try:
            # Create A2A message for task delegation
            message = A2AMessage(
                message_id=str(uuid.uuid4()),
                sender_id=self.agent_id,
                recipient_id=connection_id,
                message_type=A2AMessageType.TASK_REQUEST,
                content=task_request.model_dump(),
                correlation_id=task_request.task_id,
            )

            # Send task request
            response = await self.send_message(connection_id, message)

            # Track task delegation
            self.metrics["tasks_delegated"] += 1

            logger.info(
                f"Delegated task {task_request.task_id} to framework {connection_id}"
            )
            return message.message_id

        except Exception as e:
            logger.error(f"Failed to delegate task: {e!s}")
            raise

    async def receive_message(self, message_data: dict[str, Any]) -> dict[str, Any]:
        """Receive and process incoming A2A message"""
        try:
            # Parse message
            message = A2AMessage(**message_data)

            # Validate constitutional compliance
            is_compliant, compliance_score = await self._validate_message_compliance(
                message
            )
            if not is_compliant:
                self.metrics["constitutional_violations"] += 1
                return {
                    "status": "rejected",
                    "reason": "constitutional_compliance_violation",
                    "compliance_score": compliance_score,
                }

            # Track metrics
            self.metrics["messages_received"] += 1
            self.message_history.append(message)

            # Process based on message type
            if message.message_type == A2AMessageType.TASK_RESPONSE:
                return await self._handle_task_response(message)
            elif message.message_type == A2AMessageType.CAPABILITY_INQUIRY:
                return await self._handle_capability_inquiry(message)
            elif message.message_type == A2AMessageType.COORDINATION_REQUEST:
                return await self._handle_coordination_request(message)
            else:
                logger.warning(f"Unhandled A2A message type: {message.message_type}")
                return {
                    "status": "acknowledged",
                    "message": "Message received but not processed",
                }

        except Exception as e:
            logger.error(f"Failed to receive A2A message: {e!s}")
            return {"status": "error", "message": str(e)}

    async def get_framework_capabilities(self, connection_id: str) -> list[str]:
        """Query capabilities of an external framework"""
        try:
            message = A2AMessage(
                message_id=str(uuid.uuid4()),
                sender_id=self.agent_id,
                recipient_id=connection_id,
                message_type=A2AMessageType.CAPABILITY_INQUIRY,
                content={"query_type": "capabilities"},
            )

            response = await self.send_message(connection_id, message)
            return response.get("capabilities", [])

        except Exception as e:
            logger.error(f"Failed to query framework capabilities: {e!s}")
            return []

    async def _validate_message_compliance(
        self, message: A2AMessage
    ) -> tuple[bool, float]:
        """Validate message against constitutional principles"""
        try:
            # Check constitutional hash
            if message.constitutional_hash != CONSTITUTIONAL_HASH:
                return False, 0.0

            # Validate message content
            compliance_result = await self.safety_validator.validate_content(
                {
                    "message_type": message.message_type.value,
                    "content": message.content,
                    "sender_id": message.sender_id,
                }
            )

            return compliance_result.get("is_compliant", False), compliance_result.get(
                "score", 0.0
            )

        except Exception as e:
            logger.error(f"Failed to validate message compliance: {e!s}")
            return False, 0.0

    async def _test_connection(self, connection: A2AConnection) -> bool:
        """Test connection to external framework"""
        try:
            if not self.session:
                await self.initialize()

            # Send ping message
            url = f"{connection.endpoint_url}/a2a/ping"
            headers = await self._prepare_auth_headers(connection)

            async with self.session.get(url, headers=headers) as response:
                return response.status == 200

        except Exception as e:
            logger.error(f"Connection test failed: {e!s}")
            return False

    async def _prepare_auth_headers(self, connection: A2AConnection) -> dict[str, str]:
        """Prepare authentication headers for connection"""
        headers = {}

        auth = connection.authentication
        if auth.get("type") == "bearer":
            headers["Authorization"] = f"Bearer {auth.get('token')}"
        elif auth.get("type") == "api_key":
            headers[auth.get("header_name", "X-API-Key")] = auth.get("key")

        return headers

    async def _handle_task_response(self, message: A2AMessage) -> dict[str, Any]:
        """Handle task response from external framework"""
        try:
            task_response = A2ATaskResponse(**message.content)

            # Remove from pending if correlated
            if message.correlation_id in self.pending_messages:
                del self.pending_messages[message.correlation_id]

            # Track completion
            if task_response.status == "completed":
                self.metrics["tasks_completed"] += 1

            # Log task completion
            await self.audit_logger.log_security_event(
                {
                    "event_type": "a2a_task_response_received",
                    "task_id": task_response.task_id,
                    "status": task_response.status,
                    "execution_time": task_response.execution_time_seconds,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

            return {"status": "processed", "task_id": task_response.task_id}

        except Exception as e:
            logger.error(f"Failed to handle task response: {e!s}")
            return {"status": "error", "message": str(e)}

    async def _handle_capability_inquiry(self, message: A2AMessage) -> dict[str, Any]:
        """Handle capability inquiry from external framework"""
        try:
            # Return ACGS agent capabilities
            capabilities = [
                "policy_generation",
                "constitutional_compliance",
                "governance_synthesis",
                "multi_agent_coordination",
                "security_validation",
            ]

            return {
                "status": "success",
                "capabilities": capabilities,
                "agent_id": self.agent_id,
                "constitutional_hash": CONSTITUTIONAL_HASH,
            }

        except Exception as e:
            logger.error(f"Failed to handle capability inquiry: {e!s}")
            return {"status": "error", "message": str(e)}

    async def _handle_coordination_request(self, message: A2AMessage) -> dict[str, Any]:
        """Handle coordination request from external framework"""
        try:
            # Basic coordination response
            return {
                "status": "acknowledged",
                "agent_id": self.agent_id,
                "available_for_coordination": True,
                "constitutional_compliance_required": True,
                "supported_protocols": ["A2A", "HTTP", "JSON-RPC"],
            }

        except Exception as e:
            logger.error(f"Failed to handle coordination request: {e!s}")
            return {"status": "error", "message": str(e)}

    def _update_response_time_metric(self, response_time: float) -> None:
        """Update average response time metric"""
        current_avg = self.metrics["average_response_time"]
        message_count = self.metrics["messages_sent"]

        if message_count == 1:
            self.metrics["average_response_time"] = response_time
        else:
            # Calculate running average
            self.metrics["average_response_time"] = (
                current_avg * (message_count - 1) + response_time
            ) / message_count

    def get_metrics(self) -> dict[str, Any]:
        """Get A2A adapter performance metrics"""
        return {
            **self.metrics,
            "active_connections": len(
                [c for c in self.connections.values() if c.is_active]
            ),
            "total_connections": len(self.connections),
            "pending_messages": len(self.pending_messages),
            "message_history_size": len(self.message_history),
        }
