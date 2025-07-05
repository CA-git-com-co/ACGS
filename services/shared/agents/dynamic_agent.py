"""
Dynamic Agent Implementation for ACGS Agentic Policy Generation

Creates and manages dynamic AI agents with constitutional constraints and
safe tool usage. Integrates with PolicyBuilder and ToolRouter for secure
and compliant autonomous agent operations within the ACGS system.

Key Features:
- Dynamic agent creation with constitutional compliance
- Safe tool execution with comprehensive monitoring
- Multi-agent coordination and conflict resolution
- Real-time performance monitoring and adaptation
- Integration with ACGS constitutional safety framework
"""

import asyncio
import logging
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from services.shared.constitutional_safety_framework import (
    ConstitutionalSafetyFramework,
)
from services.shared.monitoring.intelligent_alerting_system import (
    IntelligentAlertingSystem,
)
from services.shared.security.enhanced_audit_logging import EnhancedAuditLogger

from .policy_builder import AgentConfig, PolicyBuilder
from .tool_router import ToolExecutionRequest, ToolRouter

logger = logging.getLogger(__name__)


class AgentState(Enum):
    """States of dynamic agent lifecycle"""

    INITIALIZING = "initializing"
    ACTIVE = "active"
    IDLE = "idle"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"
    ERROR = "error"


class AgentCapability(Enum):
    """Core capabilities that agents can possess"""

    POLICY_ANALYSIS = "policy_analysis"
    DATA_PROCESSING = "data_processing"
    REPORT_GENERATION = "report_generation"
    RESEARCH = "research"
    DECISION_SUPPORT = "decision_support"
    MONITORING = "monitoring"
    COMMUNICATION = "communication"
    COORDINATION = "coordination"


class TaskPriority(Enum):
    """Priority levels for agent tasks"""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class TaskStatus(Enum):
    """Status of agent tasks"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentTask:
    """Individual task for an agent to execute"""

    task_id: str
    agent_id: str
    task_type: str
    description: str
    priority: TaskPriority
    parameters: dict[str, Any]
    required_tools: list[str]
    constitutional_constraints: list[str]
    deadline: Optional[datetime]
    dependencies: list[str]
    status: TaskStatus
    result: Optional[dict[str, Any]]
    error_message: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    execution_logs: list[dict[str, Any]]


@dataclass
class AgentMetrics:
    """Performance metrics for an agent"""

    agent_id: str
    tasks_completed: int
    tasks_failed: int
    average_execution_time: float
    tool_usage_count: dict[str, int]
    constitutional_compliance_score: float
    resource_efficiency_score: float
    error_rate: float
    last_activity: datetime
    uptime_seconds: float


@dataclass
class AgentCommunication:
    """Communication between agents"""

    communication_id: str
    sender_agent_id: str
    receiver_agent_id: str
    message_type: str
    content: dict[str, Any]
    priority: TaskPriority
    requires_response: bool
    response: Optional[dict[str, Any]]
    timestamp: datetime
    resolved: bool


class DynamicAgent:
    """
    Dynamic AI agent with constitutional compliance and safe tool usage.

    Each agent operates autonomously within constitutional constraints,
    can use approved tools safely, and coordinates with other agents
    when necessary.
    """

    def __init__(
        self,
        config: AgentConfig,
        policy_builder: PolicyBuilder,
        tool_router: ToolRouter,
        constitutional_framework: ConstitutionalSafetyFramework,
        audit_logger: EnhancedAuditLogger,
        alerting_system: IntelligentAlertingSystem,
    ):
        self.config = config
        self.policy_builder = policy_builder
        self.tool_router = tool_router
        self.constitutional_framework = constitutional_framework
        self.audit_logger = audit_logger
        self.alerting_system = alerting_system

        # Agent state management
        self.state = AgentState.INITIALIZING
        self.start_time = datetime.utcnow()
        self.last_activity = datetime.utcnow()

        # Task management
        self.task_queue: deque = deque()
        self.active_tasks: dict[str, AgentTask] = {}
        self.completed_tasks: deque = deque(maxlen=1000)

        # Communication
        self.message_inbox: deque = deque(maxlen=100)
        self.message_outbox: deque = deque(maxlen=100)

        # Performance monitoring
        self.metrics = AgentMetrics(
            agent_id=config.agent_id,
            tasks_completed=0,
            tasks_failed=0,
            average_execution_time=0.0,
            tool_usage_count=defaultdict(int),
            constitutional_compliance_score=1.0,
            resource_efficiency_score=1.0,
            error_rate=0.0,
            last_activity=datetime.utcnow(),
            uptime_seconds=0.0,
        )

        # Constitutional compliance tracking
        self.compliance_violations: list[dict[str, Any]] = []
        self.constraint_checks: list[dict[str, Any]] = []

        logger.info(
            f"DynamicAgent {config.agent_id} initialized with role: {config.role}"
        )

    async def initialize(self) -> None:
        """Initialize the agent and start main execution loop"""
        try:
            self.state = AgentState.ACTIVE

            # Log agent activation
            await self.audit_logger.log_security_event({
                "event_type": "agent_activated",
                "agent_id": self.config.agent_id,
                "role": self.config.role,
                "capabilities": self.config.capabilities,
                "constraints": list(self.config.constraints.keys()),
                "timestamp": datetime.utcnow().isoformat(),
            })

            # Start main execution loop
            asyncio.create_task(self._main_execution_loop())

            logger.info(f"Agent {self.config.agent_id} initialized and active")

        except Exception as e:
            self.state = AgentState.ERROR
            logger.error(f"Failed to initialize agent {self.config.agent_id}: {e!s}")
            await self.alerting_system.send_alert({
                "severity": "high",
                "component": "DynamicAgent",
                "message": f"Agent initialization failed: {e!s}",
                "agent_id": self.config.agent_id,
            })
            raise

    async def assign_task(self, task: AgentTask) -> bool:
        """
        Assign a new task to the agent.

        Args:
            task: Task to be assigned

        Returns:
            True if task was accepted, False otherwise
        """
        try:
            # Validate task against agent capabilities
            if not await self._validate_task_compatibility(task):
                logger.warning(
                    f"Task {task.task_id} not compatible with agent"
                    f" {self.config.agent_id}"
                )
                return False

            # Check constitutional constraints
            if not await self._validate_constitutional_compliance(task):
                logger.warning(
                    f"Task {task.task_id} violates constitutional constraints"
                )
                return False

            # Check resource availability
            if not await self._check_resource_availability(task):
                logger.warning(f"Insufficient resources for task {task.task_id}")
                return False

            # Add to task queue
            self.task_queue.append(task)

            # Log task assignment
            await self.audit_logger.log_security_event({
                "event_type": "task_assigned",
                "agent_id": self.config.agent_id,
                "task_id": task.task_id,
                "task_type": task.task_type,
                "priority": task.priority.value,
                "timestamp": datetime.utcnow().isoformat(),
            })

            logger.info(f"Task {task.task_id} assigned to agent {self.config.agent_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to assign task {task.task_id}: {e!s}")
            return False

    async def send_message(
        self, recipient_agent_id: str, message: AgentCommunication
    ) -> bool:
        """
        Send message to another agent.

        Args:
            recipient_agent_id: ID of recipient agent
            message: Message to send

        Returns:
            True if message was sent successfully
        """
        try:
            # Validate communication constraints
            if not await self._validate_communication_constraints(
                recipient_agent_id, message
            ):
                return False

            # Add to outbox (in production, this would route through message broker)
            self.message_outbox.append(message)

            # Log communication
            await self.audit_logger.log_security_event({
                "event_type": "agent_communication_sent",
                "sender_agent_id": self.config.agent_id,
                "recipient_agent_id": recipient_agent_id,
                "message_type": message.message_type,
                "timestamp": datetime.utcnow().isoformat(),
            })

            return True

        except Exception as e:
            logger.error(f"Failed to send message: {e!s}")
            return False

    async def receive_message(self, message: AgentCommunication) -> None:
        """
        Receive message from another agent.

        Args:
            message: Received message
        """
        try:
            # Add to inbox
            self.message_inbox.append(message)

            # Process high-priority messages immediately
            if message.priority in [TaskPriority.CRITICAL, TaskPriority.HIGH]:
                await self._process_message(message)

            # Log message receipt
            await self.audit_logger.log_security_event({
                "event_type": "agent_communication_received",
                "sender_agent_id": message.sender_agent_id,
                "recipient_agent_id": self.config.agent_id,
                "message_type": message.message_type,
                "timestamp": datetime.utcnow().isoformat(),
            })

        except Exception as e:
            logger.error(f"Failed to receive message: {e!s}")

    async def get_status(self) -> dict[str, Any]:
        """Get current agent status and metrics"""
        self._update_metrics()

        return {
            "agent_id": self.config.agent_id,
            "state": self.state.value,
            "role": self.config.role,
            "capabilities": self.config.capabilities,
            "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
            "tasks_in_queue": len(self.task_queue),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": self.metrics.tasks_completed,
            "failed_tasks": self.metrics.tasks_failed,
            "error_rate": self.metrics.error_rate,
            "constitutional_compliance_score": (
                self.metrics.constitutional_compliance_score
            ),
            "resource_efficiency_score": self.metrics.resource_efficiency_score,
            "last_activity": self.last_activity.isoformat(),
            "compliance_violations": len(self.compliance_violations),
        }

    async def shutdown(self) -> None:
        """Gracefully shutdown the agent"""
        try:
            logger.info(f"Shutting down agent {self.config.agent_id}")
            self.state = AgentState.TERMINATED

            # Cancel active tasks
            for task in self.active_tasks.values():
                task.status = TaskStatus.CANCELLED
                task.completed_at = datetime.utcnow()

            # Log shutdown
            await self.audit_logger.log_security_event({
                "event_type": "agent_shutdown",
                "agent_id": self.config.agent_id,
                "uptime_seconds": (datetime.utcnow() - self.start_time).total_seconds(),
                "tasks_completed": self.metrics.tasks_completed,
                "timestamp": datetime.utcnow().isoformat(),
            })

        except Exception as e:
            logger.error(f"Error during agent shutdown: {e!s}")

    async def _main_execution_loop(self) -> None:
        """Main execution loop for the agent"""
        while self.state == AgentState.ACTIVE:
            try:
                # Process messages
                await self._process_messages()

                # Execute tasks
                await self._execute_tasks()

                # Update metrics
                self._update_metrics()

                # Check health and constraints
                await self._perform_health_check()

                # Brief sleep to prevent busy waiting
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error in main execution loop: {e!s}")
                await self.alerting_system.send_alert({
                    "severity": "medium",
                    "component": "DynamicAgent",
                    "message": f"Execution loop error: {e!s}",
                    "agent_id": self.config.agent_id,
                })
                await asyncio.sleep(5)  # Back off on error

    async def _execute_tasks(self) -> None:
        """Execute tasks from the queue"""
        # Start new tasks if we have capacity
        max_concurrent = self.config.resource_limits.get("max_concurrent_tasks", 3)

        while (
            len(self.active_tasks) < max_concurrent
            and self.task_queue
            and self.state == AgentState.ACTIVE
        ):
            # Get highest priority task
            task = self._get_next_task()
            if not task:
                break

            # Start task execution
            await self._start_task_execution(task)

        # Check status of active tasks
        completed_tasks = []
        for task_id, task in self.active_tasks.items():
            if task.status in [
                TaskStatus.COMPLETED,
                TaskStatus.FAILED,
                TaskStatus.CANCELLED,
            ]:
                completed_tasks.append(task_id)

        # Move completed tasks
        for task_id in completed_tasks:
            task = self.active_tasks.pop(task_id)
            self.completed_tasks.append(task)

            if task.status == TaskStatus.COMPLETED:
                self.metrics.tasks_completed += 1
            elif task.status == TaskStatus.FAILED:
                self.metrics.tasks_failed += 1

    async def _start_task_execution(self, task: AgentTask) -> None:
        """Start execution of a single task"""
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            self.active_tasks[task.task_id] = task

            # Execute task asynchronously
            asyncio.create_task(self._execute_single_task(task))

            # Log task start
            await self.audit_logger.log_security_event({
                "event_type": "task_execution_started",
                "agent_id": self.config.agent_id,
                "task_id": task.task_id,
                "task_type": task.task_type,
                "timestamp": datetime.utcnow().isoformat(),
            })

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()
            logger.error(f"Failed to start task {task.task_id}: {e!s}")

    async def _execute_single_task(self, task: AgentTask) -> None:
        """Execute a single task with all safety checks"""
        try:
            # Log task execution steps
            task.execution_logs.append({
                "action": "task_execution_started",
                "timestamp": datetime.utcnow().isoformat(),
            })

            # Validate constitutional compliance before execution
            if not await self._validate_constitutional_compliance(task):
                task.status = TaskStatus.FAILED
                task.error_message = "Constitutional compliance check failed"
                task.completed_at = datetime.utcnow()
                return

            # Execute required tools
            tool_results = {}
            for tool_id in task.required_tools:
                if tool_id not in self.config.tools_allowed:
                    task.status = TaskStatus.FAILED
                    task.error_message = f"Tool {tool_id} not allowed for this agent"
                    task.completed_at = datetime.utcnow()
                    return

                # Execute tool
                tool_request = ToolExecutionRequest(
                    request_id=str(uuid.uuid4()),
                    agent_id=self.config.agent_id,
                    tool_id=tool_id,
                    parameters=task.parameters.get(f"{tool_id}_params", {}),
                    priority=task.priority.value,
                    timeout_seconds=None,
                    callback_url=None,
                    metadata={"task_id": task.task_id},
                    requested_at=datetime.utcnow(),
                )

                tool_result = await self.tool_router.route_tool_request(tool_request)
                tool_results[tool_id] = tool_result

                # Update tool usage metrics
                self.metrics.tool_usage_count[tool_id] += 1

                # Check if tool execution failed
                if tool_result.status.value != "completed":
                    task.status = TaskStatus.FAILED
                    task.error_message = (
                        f"Tool {tool_id} execution failed: {tool_result.error_message}"
                    )
                    task.completed_at = datetime.utcnow()
                    return

            # Process results and generate task output
            task_result = await self._process_task_results(task, tool_results)

            # Validate output against constitutional constraints
            if await self._validate_output_compliance(task, task_result):
                task.result = task_result
                task.status = TaskStatus.COMPLETED
            else:
                task.status = TaskStatus.FAILED
                task.error_message = "Output failed constitutional compliance check"

            task.completed_at = datetime.utcnow()

            # Log completion
            task.execution_logs.append({
                "action": "task_execution_completed",
                "status": task.status.value,
                "timestamp": datetime.utcnow().isoformat(),
            })

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            task.completed_at = datetime.utcnow()

            task.execution_logs.append({
                "action": "task_execution_failed",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            })

            logger.error(f"Task {task.task_id} execution failed: {e!s}")

    async def _process_messages(self) -> None:
        """Process messages in the inbox"""
        messages_to_process = []

        # Get messages from inbox
        while self.message_inbox:
            message = self.message_inbox.popleft()
            messages_to_process.append(message)

        # Process each message
        for message in messages_to_process:
            await self._process_message(message)

    async def _process_message(self, message: AgentCommunication) -> None:
        """Process a single message from another agent"""
        try:
            # Handle different message types
            if message.message_type == "coordination_request":
                await self._handle_coordination_request(message)
            elif message.message_type == "task_delegation":
                await self._handle_task_delegation(message)
            elif message.message_type == "status_inquiry":
                await self._handle_status_inquiry(message)
            elif message.message_type == "emergency_shutdown":
                await self._handle_emergency_shutdown(message)
            else:
                logger.warning(f"Unknown message type: {message.message_type}")

        except Exception as e:
            logger.error(f"Failed to process message {message.communication_id}: {e!s}")

    def _get_next_task(self) -> Optional[AgentTask]:
        """Get the next task to execute based on priority"""
        if not self.task_queue:
            return None

        # Sort by priority (lower number = higher priority)
        sorted_tasks = sorted(self.task_queue, key=lambda t: t.priority.value)

        # Remove and return highest priority task
        next_task = sorted_tasks[0]
        self.task_queue.remove(next_task)
        return next_task

    def _update_metrics(self) -> None:
        """Update agent performance metrics"""
        now = datetime.utcnow()
        self.metrics.uptime_seconds = (now - self.start_time).total_seconds()
        self.metrics.last_activity = now

        # Calculate error rate
        total_tasks = self.metrics.tasks_completed + self.metrics.tasks_failed
        if total_tasks > 0:
            self.metrics.error_rate = self.metrics.tasks_failed / total_tasks

        # Calculate average execution time
        if self.completed_tasks:
            execution_times = []
            for task in list(self.completed_tasks)[-50:]:  # Last 50 tasks
                if task.started_at and task.completed_at:
                    execution_time = (
                        task.completed_at - task.started_at
                    ).total_seconds()
                    execution_times.append(execution_time)

            if execution_times:
                self.metrics.average_execution_time = sum(execution_times) / len(
                    execution_times
                )

    async def _validate_task_compatibility(self, task: AgentTask) -> bool:
        """Validate if task is compatible with agent capabilities"""
        # Check if agent has required capabilities
        task_capabilities = task.parameters.get("required_capabilities", [])
        for capability in task_capabilities:
            if capability not in self.config.capabilities:
                return False

        # Check if required tools are allowed
        for tool_id in task.required_tools:
            if tool_id not in self.config.tools_allowed:
                return False

        return True

    async def _validate_constitutional_compliance(self, task: AgentTask) -> bool:
        """Validate task against constitutional constraints"""
        try:
            # Check task against constitutional principles
            compliance_score = await self.constitutional_framework.evaluate_compliance({
                "task_type": task.task_type,
                "parameters": task.parameters,
                "constraints": task.constitutional_constraints,
            })

            # Log compliance check
            self.constraint_checks.append({
                "task_id": task.task_id,
                "compliance_score": compliance_score,
                "timestamp": datetime.utcnow().isoformat(),
            })

            # Threshold check
            if compliance_score < 0.7:
                self.compliance_violations.append({
                    "task_id": task.task_id,
                    "violation_type": "constitutional_compliance",
                    "score": compliance_score,
                    "timestamp": datetime.utcnow().isoformat(),
                })
                return False

            return True

        except Exception as e:
            logger.error(f"Constitutional compliance check failed: {e!s}")
            return False

    async def _validate_output_compliance(
        self, task: AgentTask, result: dict[str, Any]
    ) -> bool:
        """Validate task output against constitutional constraints"""
        try:
            # Check output against constitutional principles
            compliance_score = await self.constitutional_framework.evaluate_compliance({
                "task_output": result,
                "task_type": task.task_type,
                "constraints": task.constitutional_constraints,
            })

            return compliance_score >= 0.7

        except Exception as e:
            logger.error(f"Output compliance check failed: {e!s}")
            return False

    async def _check_resource_availability(self, task: AgentTask) -> bool:
        """Check if agent has sufficient resources for task"""
        # Check memory limits
        required_memory = task.parameters.get("required_memory_mb", 100)
        max_memory = self.config.resource_limits.get("max_memory_mb", 512)

        current_memory_usage = len(self.active_tasks) * 100  # Simplified calculation

        if current_memory_usage + required_memory > max_memory:
            return False

        # Check CPU limits
        required_cpu = task.parameters.get("required_cpu_percent", 10)
        max_cpu = self.config.resource_limits.get("max_cpu_percent", 50)

        current_cpu_usage = len(self.active_tasks) * 10  # Simplified calculation

        if current_cpu_usage + required_cpu > max_cpu:
            return False

        return True

    async def _validate_communication_constraints(
        self, recipient_id: str, message: AgentCommunication
    ) -> bool:
        """Validate communication against constraints"""
        # Check if communication is allowed
        if "communication" not in self.config.capabilities:
            return False

        # Check message content for compliance
        return True  # Simplified for this implementation

    async def _process_task_results(
        self, task: AgentTask, tool_results: dict[str, Any]
    ) -> dict[str, Any]:
        """Process tool results into final task output"""
        return {
            "task_id": task.task_id,
            "task_type": task.task_type,
            "tool_results": {
                tool_id: result.result
                for tool_id, result in tool_results.items()
                if result.result is not None
            },
            "execution_summary": f"Task {task.task_type} completed successfully",
            "timestamp": datetime.utcnow().isoformat(),
            "agent_id": self.config.agent_id,
        }

    async def _perform_health_check(self) -> None:
        """Perform periodic health checks"""
        # Check resource usage
        if len(self.active_tasks) > self.config.resource_limits.get(
            "max_concurrent_tasks", 5
        ):
            await self.alerting_system.send_alert({
                "severity": "medium",
                "component": "DynamicAgent",
                "message": "Agent overloaded with tasks",
                "agent_id": self.config.agent_id,
            })

        # Check error rate
        if self.metrics.error_rate > 0.2:  # 20% error rate threshold
            await self.alerting_system.send_alert({
                "severity": "high",
                "component": "DynamicAgent",
                "message": f"High error rate: {self.metrics.error_rate:.2%}",
                "agent_id": self.config.agent_id,
            })

        # Check compliance violations
        if len(self.compliance_violations) > 10:
            self.state = AgentState.SUSPENDED
            await self.alerting_system.send_alert({
                "severity": "critical",
                "component": "DynamicAgent",
                "message": "Agent suspended due to compliance violations",
                "agent_id": self.config.agent_id,
            })

    async def _handle_coordination_request(self, message: AgentCommunication) -> None:
        """Handle coordination request from another agent"""
        # Simplified coordination response
        response = {
            "agent_id": self.config.agent_id,
            "available_for_coordination": self.state == AgentState.ACTIVE,
            "current_load": len(self.active_tasks),
            "capabilities": self.config.capabilities,
        }

        # Send response
        response_message = AgentCommunication(
            communication_id=str(uuid.uuid4()),
            sender_agent_id=self.config.agent_id,
            receiver_agent_id=message.sender_agent_id,
            message_type="coordination_response",
            content=response,
            priority=message.priority,
            requires_response=False,
            response=None,
            timestamp=datetime.utcnow(),
            resolved=True,
        )

        await self.send_message(message.sender_agent_id, response_message)

    async def _handle_task_delegation(self, message: AgentCommunication) -> None:
        """Handle task delegation from another agent"""
        # Create task from delegation message
        task_data = message.content

        task = AgentTask(
            task_id=str(uuid.uuid4()),
            agent_id=self.config.agent_id,
            task_type=task_data.get("task_type", "delegated_task"),
            description=task_data.get("description", "Delegated task"),
            priority=TaskPriority(task_data.get("priority", 3)),
            parameters=task_data.get("parameters", {}),
            required_tools=task_data.get("required_tools", []),
            constitutional_constraints=task_data.get("constitutional_constraints", []),
            deadline=None,
            dependencies=[],
            status=TaskStatus.PENDING,
            result=None,
            error_message=None,
            created_at=datetime.utcnow(),
            started_at=None,
            completed_at=None,
            execution_logs=[],
        )

        # Try to assign the task
        accepted = await self.assign_task(task)

        # Send response
        response = {
            "task_accepted": accepted,
            "task_id": task.task_id if accepted else None,
        }

        response_message = AgentCommunication(
            communication_id=str(uuid.uuid4()),
            sender_agent_id=self.config.agent_id,
            receiver_agent_id=message.sender_agent_id,
            message_type="task_delegation_response",
            content=response,
            priority=message.priority,
            requires_response=False,
            response=None,
            timestamp=datetime.utcnow(),
            resolved=True,
        )

        await self.send_message(message.sender_agent_id, response_message)

    async def _handle_status_inquiry(self, message: AgentCommunication) -> None:
        """Handle status inquiry from another agent"""
        status = await self.get_status()

        response_message = AgentCommunication(
            communication_id=str(uuid.uuid4()),
            sender_agent_id=self.config.agent_id,
            receiver_agent_id=message.sender_agent_id,
            message_type="status_response",
            content=status,
            priority=message.priority,
            requires_response=False,
            response=None,
            timestamp=datetime.utcnow(),
            resolved=True,
        )

        await self.send_message(message.sender_agent_id, response_message)

    async def _handle_emergency_shutdown(self, message: AgentCommunication) -> None:
        """Handle emergency shutdown request"""
        logger.warning(f"Emergency shutdown requested for agent {self.config.agent_id}")
        await self.shutdown()
