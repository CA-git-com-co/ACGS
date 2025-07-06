"""
APGF Orchestrator for ACGS Integration

Main orchestrator that integrates the Agentic Policy Generation Feature (APGF)
with the existing ACGS system. Manages agent lifecycle, coordinates policy
generation workflows, and ensures constitutional compliance across all operations.

Enhanced with MetaGPT's assembly line paradigm for structured document-based
communication, replacing chaotic agent chatter with organized workflows.

Key Features:
- Dynamic agent lifecycle management
- Policy generation workflow orchestration
- Multi-agent coordination and conflict resolution
- Integration with existing ACGS services
- Constitutional compliance monitoring
- Performance optimization and resource management
- Document-based structured communication channels
- MetaGPT assembly line paradigm implementation
"""

import asyncio
import logging
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Optional, Union

# Import for document-based communication
from pydantic import BaseModel, Field
from services.shared.constitutional_safety_framework import (
    ConstitutionalSafetyFramework,
)
from services.shared.monitoring.enhanced_performance_monitor import (
    EnhancedPerformanceMonitor,
)
from services.shared.monitoring.intelligent_alerting_system import (
    IntelligentAlertingSystem,
)
from services.shared.security.enhanced_audit_logging import EnhancedAuditLogger
from services.shared.security.unified_input_validation import EnhancedInputValidator
from services.shared.service_mesh.service_orchestrator import (
    ACGSServiceOrchestrator as ServiceOrchestrator,
)

from .apgf_event_publisher import APGFEventPublisher
from .dynamic_agent import AgentCommunication, DynamicAgent
from .policy_builder import AgentConfig, PolicyBuilder
from .specialized_agent_roles import (
    AgentRoleType,
    SpecializedRoleFactory,
    SpecializedRoleRegistry,
)
from .tool_router import ToolRouter

logger = logging.getLogger(__name__)


class WorkflowState(Enum):
    """States of policy generation workflows"""

    INITIATED = "initiated"
    PLANNING = "planning"
    AGENT_CREATION = "agent_creation"
    EXECUTION = "execution"
    VALIDATION = "validation"
    APPROVAL = "approval"
    IMPLEMENTATION = "implementation"
    MONITORING = "monitoring"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CoordinationStrategy(Enum):
    """Strategies for multi-agent coordination"""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    CONSENSUS = "consensus"
    COMPETITIVE = "competitive"
    DOCUMENT_BASED = "document_based"  # New strategy for structured communication


# Document-Based Communication Schemas (MetaGPT Assembly Line Paradigm)


class RequirementsSchema(BaseModel):
    """Schema for requirements documents in the assembly line"""

    requirements_id: str = Field(..., description="Unique identifier for requirements")
    workflow_id: str = Field(..., description="Associated workflow ID")
    functional_requirements: list[str] = Field(default_factory=list)
    non_functional_requirements: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    success_criteria: dict[str, Any] = Field(default_factory=dict)
    constitutional_compliance: dict[str, Any] = Field(default_factory=dict)
    created_by: str = Field(..., description="Agent ID that created requirements")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    approved: bool = Field(default=False)


class DesignSchema(BaseModel):
    """Schema for design documents in the assembly line"""

    design_id: str = Field(..., description="Unique identifier for design")
    requirements_id: str = Field(..., description="Reference to requirements")
    workflow_id: str = Field(..., description="Associated workflow ID")
    architecture_overview: str = Field(..., description="High-level architecture")
    component_specifications: dict[str, Any] = Field(default_factory=dict)
    interface_definitions: dict[str, Any] = Field(default_factory=dict)
    data_flow_diagrams: list[str] = Field(default_factory=list)
    security_considerations: list[str] = Field(default_factory=list)
    constitutional_alignment: dict[str, Any] = Field(default_factory=dict)
    created_by: str = Field(..., description="Agent ID that created design")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    approved: bool = Field(default=False)


class ImplementationSchema(BaseModel):
    """Schema for implementation documents in the assembly line"""

    implementation_id: str = Field(..., description="Unique identifier")
    design_id: str = Field(..., description="Reference to design")
    workflow_id: str = Field(..., description="Associated workflow ID")
    code_specifications: dict[str, Any] = Field(default_factory=dict)
    deployment_instructions: list[str] = Field(default_factory=list)
    configuration_parameters: dict[str, Any] = Field(default_factory=dict)
    testing_procedures: list[str] = Field(default_factory=list)
    rollback_procedures: list[str] = Field(default_factory=list)
    constitutional_checks: dict[str, Any] = Field(default_factory=dict)
    created_by: str = Field(..., description="Agent ID that created implementation")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    approved: bool = Field(default=False)


class ValidationSchema(BaseModel):
    """Schema for validation documents in the assembly line"""

    validation_id: str = Field(..., description="Unique identifier for validation")
    implementation_id: str = Field(..., description="Reference to implementation")
    workflow_id: str = Field(..., description="Associated workflow ID")
    test_results: dict[str, Any] = Field(default_factory=dict)
    compliance_checks: dict[str, Any] = Field(default_factory=dict)
    performance_metrics: dict[str, Any] = Field(default_factory=dict)
    security_audit_results: dict[str, Any] = Field(default_factory=dict)
    constitutional_validation: dict[str, Any] = Field(default_factory=dict)
    issues_identified: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    approval_status: str = Field(default="pending")
    created_by: str = Field(..., description="Agent ID that created validation")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    approved: bool = Field(default=False)


class DocumentChannel:
    """
    Document-based communication channel for structured agent interaction.
    Implements MetaGPT's assembly line paradigm with typed document exchange.
    """

    def __init__(self, schema: type[BaseModel], channel_name: str = None):
        self.schema = schema
        self.channel_name = channel_name or schema.__name__.lower()
        self.documents: dict[str, BaseModel] = {}
        self.subscribers: list[str] = []  # Agent IDs subscribed to this channel
        self.document_history: list[dict[str, Any]] = []

    async def publish_document(self, document: BaseModel, publisher_id: str) -> str:
        """Publish a document to the channel"""
        if not isinstance(document, self.schema):
            raise ValueError(f"Document must be of type {self.schema.__name__}")

        document_id = str(uuid.uuid4())
        self.documents[document_id] = document

        # Add to history
        self.document_history.append({
            "document_id": document_id,
            "publisher_id": publisher_id,
            "timestamp": datetime.now(timezone.utc),
            "action": "published",
        })

        # Notify subscribers (in production, this would use event bus)
        logger.info(f"Document {document_id} published to channel {self.channel_name}")
        return document_id

    async def get_document(self, document_id: str) -> Optional[BaseModel]:
        """Retrieve a document by ID"""
        return self.documents.get(document_id)

    async def get_latest_document(self) -> Optional[BaseModel]:
        """Get the most recently published document"""
        if not self.document_history:
            return None

        latest_entry = max(self.document_history, key=lambda x: x["timestamp"])
        return self.documents.get(latest_entry["document_id"])

    async def subscribe(self, agent_id: str) -> None:
        """Subscribe an agent to document updates"""
        if agent_id not in self.subscribers:
            self.subscribers.append(agent_id)

    async def unsubscribe(self, agent_id: str) -> None:
        """Unsubscribe an agent from document updates"""
        if agent_id in self.subscribers:
            self.subscribers.remove(agent_id)


@dataclass
class PolicyGenerationWorkflow:
    """Workflow for generating policies using dynamic agents"""

    workflow_id: str
    name: str
    description: str
    state: WorkflowState
    policy_requirements: dict[str, Any]
    coordination_strategy: CoordinationStrategy
    assigned_agents: list[str]
    generated_policies: list[str]
    workflow_steps: list[dict[str, Any]]
    current_step: int
    start_time: datetime
    estimated_completion: Optional[datetime]
    actual_completion: Optional[datetime]
    success_metrics: dict[str, float]
    error_log: list[dict[str, Any]]
    resource_usage: dict[str, Union[int, float]]


@dataclass
class AgentCoordinationPlan:
    """Plan for coordinating multiple agents"""

    plan_id: str
    workflow_id: str
    coordination_strategy: CoordinationStrategy
    agent_assignments: dict[str, list[str]]  # agent_id -> task_ids
    dependencies: dict[str, list[str]]  # task_id -> dependency_task_ids
    communication_rules: dict[str, Any]
    conflict_resolution_protocol: str
    success_criteria: dict[str, float]
    timeout_minutes: int


class APGFOrchestrator:
    """
    Main orchestrator for the Agentic Policy Generation Feature.

    Coordinates all aspects of dynamic agent-based policy generation
    within the ACGS constitutional AI system.
    """

    def __init__(
        self,
        constitutional_framework: ConstitutionalSafetyFramework,
        audit_logger: EnhancedAuditLogger,
        alerting_system: IntelligentAlertingSystem,
        input_validator: EnhancedInputValidator,
        service_orchestrator: ServiceOrchestrator,
    ):
        self.constitutional_framework = constitutional_framework
        self.audit_logger = audit_logger
        self.alerting_system = alerting_system
        self.input_validator = input_validator
        self.service_orchestrator = service_orchestrator

        # Initialize core components
        self.policy_builder = PolicyBuilder(
            constitutional_framework, audit_logger, alerting_system
        )
        self.tool_router = ToolRouter(audit_logger, alerting_system, input_validator)

        # Agent management
        self.active_agents: dict[str, DynamicAgent] = {}
        self.agent_pool: dict[str, AgentConfig] = {}

        # Workflow management
        self.active_workflows: dict[str, PolicyGenerationWorkflow] = {}
        self.completed_workflows: deque = deque(maxlen=1000)

        # Coordination
        self.coordination_plans: dict[str, AgentCoordinationPlan] = {}
        self.message_broker = MessageBroker()

        # Document-based communication channels for structured workflows
        self.document_channels: dict[str, DocumentChannel] = {}

        # Enhanced Performance Monitor for revolutionary metrics tracking
        self.performance_monitor = EnhancedPerformanceMonitor(retention_hours=24)

        # Specialized Agent Role Registry for MetaGPT assembly line
        self.role_registry = SpecializedRoleRegistry()

        # Event streaming
        self.event_publisher = APGFEventPublisher()

        # Performance monitoring
        self.performance_metrics = {
            "workflows_completed": 0,
            "workflows_failed": 0,
            "agents_created": 0,
            "policies_generated": 0,
            "average_workflow_time": 0.0,
            "resource_efficiency": 1.0,
        }

        logger.info("APGFOrchestrator initialized successfully")

    async def initialize(self) -> None:
        """Initialize the orchestrator and all components"""
        try:
            await self.policy_builder.initialize()

            # Initialize event publisher
            await self.event_publisher.initialize()

            # Initialize enhanced performance monitor
            await self.performance_monitor.start()

            # Initialize default agent templates
            await self._create_default_agent_templates()

            # Start background tasks
            asyncio.create_task(self._workflow_monitor())
            asyncio.create_task(self._agent_health_monitor())
            asyncio.create_task(self._resource_optimizer())

            logger.info("APGFOrchestrator initialization completed")

        except Exception as e:
            logger.error(f"Failed to initialize APGFOrchestrator: {e!s}")
            raise

    async def initiate_policy_generation_workflow(self, request: dict[str, Any]) -> str:
        """
        Initiate a new policy generation workflow.

        Args:
            request: Policy generation request

        Returns:
            Workflow ID
        """
        try:
            workflow_id = str(uuid.uuid4())

            # Validate request
            validation_result = await self.input_validator.validate_and_sanitize(
                request, self._get_workflow_request_schema()
            )

            if not validation_result["is_valid"]:
                raise ValueError(
                    f"Invalid workflow request: {validation_result['errors']}"
                )

            sanitized_request = validation_result["sanitized_data"]

            # Create workflow
            workflow = PolicyGenerationWorkflow(
                workflow_id=workflow_id,
                name=sanitized_request.get(
                    "name", f"Policy Generation {workflow_id[:8]}"
                ),
                description=sanitized_request.get("description", ""),
                state=WorkflowState.INITIATED,
                policy_requirements=sanitized_request.get("requirements", {}),
                coordination_strategy=CoordinationStrategy(
                    sanitized_request.get("coordination_strategy", "sequential")
                ),
                assigned_agents=[],
                generated_policies=[],
                workflow_steps=[],
                current_step=0,
                start_time=datetime.utcnow(),
                estimated_completion=None,
                actual_completion=None,
                success_metrics={},
                error_log=[],
                resource_usage={},
            )

            # Store workflow
            self.active_workflows[workflow_id] = workflow

            # Start workflow execution
            asyncio.create_task(self._execute_workflow(workflow))

            # Publish workflow initiation event
            await self.event_publisher.publish_workflow_initiated(
                workflow_id,
                {
                    "name": workflow.name,
                    "coordination_strategy": workflow.coordination_strategy.value,
                    "requirements": workflow.policy_requirements,
                    "estimated_duration_minutes": len(workflow.workflow_steps) * 15,
                },
            )

            # Log workflow initiation
            await self.audit_logger.log_security_event({
                "event_type": "apgf_workflow_initiated",
                "workflow_id": workflow_id,
                "policy_requirements": workflow.policy_requirements,
                "coordination_strategy": workflow.coordination_strategy.value,
                "timestamp": datetime.utcnow().isoformat(),
            })

            logger.info(f"Policy generation workflow {workflow_id} initiated")
            return workflow_id

        except Exception as e:
            logger.error(f"Failed to initiate workflow: {e!s}")
            await self.alerting_system.send_alert({
                "severity": "high",
                "component": "APGFOrchestrator",
                "message": f"Workflow initiation failed: {e!s}",
            })
            raise

    async def create_structured_workflow(
        self, task_description: str
    ) -> AgentCoordinationPlan:
        """
        Creates a structured workflow with specialized agent roles using
        document-based communication channels following MetaGPT's assembly line paradigm.

        Args:
            task_description: Description of the task to be executed

        Returns:
            AgentCoordinationPlan with structured document-based communication
        """
        try:
            # Create specialized agent roles
            roles = {
                "policy_manager": await self._create_policy_manager_agent(),
                "architect": await self._create_architect_agent(),
                "validator": await self._create_validator_agent(),
                "implementer": await self._create_implementer_agent(),
            }

            # Create document-based communication channels
            channels = {
                "requirements": DocumentChannel(
                    schema=RequirementsSchema, channel_name="requirements"
                ),
                "design": DocumentChannel(schema=DesignSchema, channel_name="design"),
                "implementation": DocumentChannel(
                    schema=ImplementationSchema, channel_name="implementation"
                ),
                "validation": DocumentChannel(
                    schema=ValidationSchema, channel_name="validation"
                ),
            }

            # Create coordination plan with structured communication
            plan = AgentCoordinationPlan(
                plan_id=str(uuid.uuid4()),
                workflow_id=f"structured-workflow-{int(time.time())}",
                coordination_strategy=CoordinationStrategy.DOCUMENT_BASED,
                agent_assignments=await self._assign_agents_to_tasks(roles),
                dependencies=await self._create_task_dependencies(),
                communication_rules=await self._setup_document_channels(channels),
                conflict_resolution_protocol="consensus_voting",
                success_criteria={"constitutional_compliance": 0.95},
                timeout_minutes=30,
            )

            # Store channels for workflow execution
            self.document_channels = channels

            logger.info(f"Created structured workflow plan {plan.plan_id}")
            return plan

        except Exception as e:
            logger.error(f"Failed to create structured workflow: {e!s}")
            raise

    async def create_dynamic_agent(self, agent_specification: dict[str, Any]) -> str:
        """
        Create a new dynamic agent for policy generation.

        Args:
            agent_specification: Agent creation specification

        Returns:
            Agent ID
        """
        try:
            # Create agent configuration
            agent_config = await self.policy_builder.create_agent_config(
                agent_specification
            )

            # Create agent instance
            agent = DynamicAgent(
                config=agent_config,
                policy_builder=self.policy_builder,
                tool_router=self.tool_router,
                constitutional_framework=self.constitutional_framework,
                audit_logger=self.audit_logger,
                alerting_system=self.alerting_system,
            )

            # Initialize agent
            await agent.initialize()

            # Store agent
            self.active_agents[agent_config.agent_id] = agent
            self.agent_pool[agent_config.agent_id] = agent_config

            # Update metrics
            self.performance_metrics["agents_created"] += 1

            # Publish agent creation event
            await self.event_publisher.publish_agent_created(
                agent_config.agent_id,
                {
                    "name": agent_config.name,
                    "role": agent_config.role,
                    "capabilities": agent_config.capabilities,
                    "resource_limits": agent_config.resource_limits,
                },
            )

            # Log agent creation
            await self.audit_logger.log_security_event({
                "event_type": "dynamic_agent_created",
                "agent_id": agent_config.agent_id,
                "role": agent_config.role,
                "capabilities": agent_config.capabilities,
                "timestamp": datetime.utcnow().isoformat(),
            })

            logger.info(f"Dynamic agent {agent_config.agent_id} created successfully")
            return agent_config.agent_id

        except Exception as e:
            logger.error(f"Failed to create dynamic agent: {e!s}")
            raise

    async def coordinate_multi_agent_task(
        self, coordination_request: dict[str, Any]
    ) -> str:
        """
        Coordinate a multi-agent task execution.

        Args:
            coordination_request: Coordination specification

        Returns:
            Coordination plan ID
        """
        try:
            plan_id = str(uuid.uuid4())

            # Create coordination plan
            plan = AgentCoordinationPlan(
                plan_id=plan_id,
                workflow_id=coordination_request.get("workflow_id", ""),
                coordination_strategy=CoordinationStrategy(
                    coordination_request.get("strategy", "sequential")
                ),
                agent_assignments={},
                dependencies={},
                communication_rules=coordination_request.get("communication_rules", {}),
                conflict_resolution_protocol=coordination_request.get(
                    "conflict_resolution", "escalation"
                ),
                success_criteria=coordination_request.get("success_criteria", {}),
                timeout_minutes=coordination_request.get("timeout_minutes", 60),
            )

            # Assign tasks to agents
            await self._assign_tasks_to_agents(
                plan, coordination_request.get("tasks", [])
            )

            # Store plan
            self.coordination_plans[plan_id] = plan

            # Execute coordination
            asyncio.create_task(self._execute_coordination_plan(plan))

            logger.info(f"Multi-agent coordination plan {plan_id} initiated")
            return plan_id

        except Exception as e:
            logger.error(f"Failed to coordinate multi-agent task: {e!s}")
            raise

    async def get_workflow_status(self, workflow_id: str) -> dict[str, Any]:
        """Get status of a policy generation workflow"""
        if workflow_id not in self.active_workflows:
            # Check completed workflows
            for workflow in self.completed_workflows:
                if workflow.workflow_id == workflow_id:
                    return self._format_workflow_status(workflow)

            raise ValueError(f"Workflow {workflow_id} not found")

        workflow = self.active_workflows[workflow_id]
        return self._format_workflow_status(workflow)

    async def get_agent_status(self, agent_id: str) -> dict[str, Any]:
        """Get status of a dynamic agent"""
        if agent_id not in self.active_agents:
            raise ValueError(f"Agent {agent_id} not found")

        agent = self.active_agents[agent_id]
        return await agent.get_status()

    async def shutdown_agent(self, agent_id: str) -> None:
        """Shutdown a dynamic agent"""
        if agent_id in self.active_agents:
            agent = self.active_agents[agent_id]
            await agent.shutdown()
            del self.active_agents[agent_id]

            logger.info(f"Agent {agent_id} shutdown successfully")

    async def cancel_workflow(self, workflow_id: str) -> None:
        """Cancel an active workflow"""
        if workflow_id in self.active_workflows:
            workflow = self.active_workflows[workflow_id]
            workflow.state = WorkflowState.CANCELLED
            workflow.actual_completion = datetime.utcnow()

            # Cancel all assigned agents' tasks
            for agent_id in workflow.assigned_agents:
                if agent_id in self.active_agents:
                    # Send cancellation message to agent
                    await self._send_agent_message(
                        agent_id,
                        {"type": "workflow_cancelled", "workflow_id": workflow_id},
                    )

            # Move to completed workflows
            self.completed_workflows.append(workflow)
            del self.active_workflows[workflow_id]

            logger.info(f"Workflow {workflow_id} cancelled")

    async def _execute_workflow(self, workflow: PolicyGenerationWorkflow) -> None:
        """Execute a policy generation workflow"""
        try:
            workflow.state = WorkflowState.PLANNING

            # Plan workflow steps
            workflow.workflow_steps = await self._plan_workflow_steps(workflow)
            workflow.estimated_completion = datetime.utcnow() + timedelta(
                minutes=len(workflow.workflow_steps) * 15
            )  # 15 minutes per step

            # Execute each step
            for step_index, step in enumerate(workflow.workflow_steps):
                workflow.current_step = step_index
                await self._execute_workflow_step(workflow, step)

                if workflow.state in [WorkflowState.FAILED, WorkflowState.CANCELLED]:
                    break

            # Complete workflow
            if workflow.state not in [WorkflowState.FAILED, WorkflowState.CANCELLED]:
                workflow.state = WorkflowState.COMPLETED
                self.performance_metrics["workflows_completed"] += 1

                # Publish workflow completion event
                await self.event_publisher.publish_workflow_completed(
                    workflow.workflow_id,
                    {
                        "name": workflow.name,
                        "execution_time_minutes": (
                            datetime.utcnow() - workflow.start_time
                        ).total_seconds() / 60,
                        "policies_generated": len(workflow.generated_policies),
                        "agents_used": len(workflow.assigned_agents),
                        "success_metrics": workflow.success_metrics,
                    },
                )
            else:
                self.performance_metrics["workflows_failed"] += 1

                # Publish workflow failure event if failed
                if workflow.state == WorkflowState.FAILED:
                    await self.event_publisher.publish_workflow_failed(
                        workflow.workflow_id,
                        {
                            "error_message": "Workflow execution failed",
                            "error_type": "execution_error",
                            "step_failed": workflow.current_step,
                            "agents_affected": workflow.assigned_agents,
                        },
                    )

            workflow.actual_completion = datetime.utcnow()

            # Move to completed workflows
            self.completed_workflows.append(workflow)
            if workflow.workflow_id in self.active_workflows:
                del self.active_workflows[workflow.workflow_id]

            # Log completion
            await self.audit_logger.log_security_event({
                "event_type": "apgf_workflow_completed",
                "workflow_id": workflow.workflow_id,
                "final_state": workflow.state.value,
                "execution_time_minutes": (
                    workflow.actual_completion - workflow.start_time
                ).total_seconds() / 60,
                "policies_generated": len(workflow.generated_policies),
                "timestamp": datetime.utcnow().isoformat(),
            })

        except Exception as e:
            workflow.state = WorkflowState.FAILED
            workflow.error_log.append({
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
                "step": workflow.current_step,
            })

            logger.error(f"Workflow {workflow.workflow_id} execution failed: {e!s}")
            await self.alerting_system.send_alert({
                "severity": "high",
                "component": "APGFOrchestrator",
                "message": f"Workflow execution failed: {e!s}",
                "workflow_id": workflow.workflow_id,
            })

    async def _plan_workflow_steps(
        self, workflow: PolicyGenerationWorkflow
    ) -> list[dict[str, Any]]:
        """Plan the steps for a workflow"""
        steps = []

        # Step 1: Analyze requirements
        steps.append({
            "name": "requirement_analysis",
            "description": "Analyze policy requirements and constraints",
            "type": "analysis",
            "estimated_minutes": 10,
        })

        # Step 2: Create agents
        steps.append({
            "name": "agent_creation",
            "description": "Create specialized agents for policy generation",
            "type": "agent_creation",
            "estimated_minutes": 5,
        })

        # Step 3: Generate policies
        steps.append({
            "name": "policy_generation",
            "description": "Generate policies using created agents",
            "type": "generation",
            "estimated_minutes": 20,
        })

        # Step 4: Validate policies
        steps.append({
            "name": "policy_validation",
            "description": "Validate generated policies for compliance",
            "type": "validation",
            "estimated_minutes": 15,
        })

        # Step 5: Final review
        steps.append({
            "name": "final_review",
            "description": "Final review and approval process",
            "type": "review",
            "estimated_minutes": 10,
        })

        return steps

    async def _execute_workflow_step(
        self, workflow: PolicyGenerationWorkflow, step: dict[str, Any]
    ) -> None:
        """Execute a single workflow step"""
        try:
            step_type = step["type"]

            if step_type == "analysis":
                await self._execute_requirement_analysis(workflow, step)
            elif step_type == "agent_creation":
                await self._execute_agent_creation(workflow, step)
            elif step_type == "generation":
                await self._execute_policy_generation(workflow, step)
            elif step_type == "validation":
                await self._execute_policy_validation(workflow, step)
            elif step_type == "review":
                await self._execute_final_review(workflow, step)
            else:
                raise ValueError(f"Unknown step type: {step_type}")

        except Exception as e:
            workflow.error_log.append({
                "step": step["name"],
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            })
            raise

    async def _execute_requirement_analysis(
        self, workflow: PolicyGenerationWorkflow, step: dict[str, Any]
    ) -> None:
        """Execute requirement analysis step"""
        # Analyze policy requirements using constitutional framework
        requirements = workflow.policy_requirements

        # Determine required agent types and capabilities
        agent_requirements = await self._analyze_agent_requirements(requirements)
        workflow.policy_requirements["agent_requirements"] = agent_requirements

        logger.info(
            f"Requirement analysis completed for workflow {workflow.workflow_id}"
        )

    async def _execute_agent_creation(
        self, workflow: PolicyGenerationWorkflow, step: dict[str, Any]
    ) -> None:
        """Execute agent creation step"""
        workflow.state = WorkflowState.AGENT_CREATION

        agent_requirements = workflow.policy_requirements.get("agent_requirements", [])

        for agent_req in agent_requirements:
            try:
                agent_id = await self.create_dynamic_agent(agent_req)
                workflow.assigned_agents.append(agent_id)

            except Exception as e:
                logger.error(f"Failed to create agent: {e!s}")
                # Continue with other agents

        if not workflow.assigned_agents:
            raise Exception("No agents could be created for workflow")

        logger.info(
            f"Created {len(workflow.assigned_agents)} agents for workflow"
            f" {workflow.workflow_id}"
        )

    async def _execute_policy_generation(
        self, workflow: PolicyGenerationWorkflow, step: dict[str, Any]
    ) -> None:
        """Execute policy generation step"""
        workflow.state = WorkflowState.EXECUTION

        # Create tasks for agents
        tasks = await self._create_policy_generation_tasks(workflow)

        # Assign tasks to agents
        task_results = []
        for task in tasks:
            agent_id = await self._select_best_agent_for_task(
                workflow.assigned_agents, task
            )

            if agent_id and agent_id in self.active_agents:
                agent = self.active_agents[agent_id]
                success = await agent.assign_task(task)

                if success:
                    # Wait for task completion (simplified)
                    await asyncio.sleep(2)  # In production, would monitor task status
                    task_results.append({"task_id": task.task_id, "agent_id": agent_id})

        # Generate policies from task results
        for task_result in task_results:
            policy_request = {
                "type": "governance",
                "scope": "domain_specific",
                "requirements": workflow.policy_requirements,
                "task_result": task_result,
            }

            policy = await self.policy_builder.generate_policy(
                policy_request, {"workflow_id": workflow.workflow_id}
            )

            workflow.generated_policies.append(policy.policy_id)

        self.performance_metrics["policies_generated"] += len(
            workflow.generated_policies
        )

        logger.info(
            f"Generated {len(workflow.generated_policies)} policies for workflow"
            f" {workflow.workflow_id}"
        )

    async def _execute_policy_validation(
        self, workflow: PolicyGenerationWorkflow, step: dict[str, Any]
    ) -> None:
        """Execute policy validation step"""
        workflow.state = WorkflowState.VALIDATION

        validation_results = []
        for policy_id in workflow.generated_policies:
            policy = self.policy_builder.generated_policies.get(policy_id)
            if policy:
                validation_result = await self.policy_builder.validate_policy(policy)
                validation_results.append(validation_result)

        # Calculate overall validation score
        if validation_results:
            avg_compliance = sum(
                r["constitutional_compliance"] for r in validation_results
            ) / len(validation_results)
            workflow.success_metrics["average_compliance_score"] = avg_compliance

        logger.info(
            f"Validated {len(validation_results)} policies for workflow"
            f" {workflow.workflow_id}"
        )

    async def _execute_final_review(
        self, workflow: PolicyGenerationWorkflow, step: dict[str, Any]
    ) -> None:
        """Execute final review step"""
        workflow.state = WorkflowState.APPROVAL

        # Calculate final success metrics
        workflow.success_metrics.update({
            "policies_generated": len(workflow.generated_policies),
            "agents_utilized": len(workflow.assigned_agents),
            "execution_time_minutes": (
                datetime.utcnow() - workflow.start_time
            ).total_seconds() / 60,
        })

        logger.info(f"Final review completed for workflow {workflow.workflow_id}")

    def _format_workflow_status(
        self, workflow: PolicyGenerationWorkflow
    ) -> dict[str, Any]:
        """Format workflow status for API response"""
        return {
            "workflow_id": workflow.workflow_id,
            "name": workflow.name,
            "state": workflow.state.value,
            "current_step": workflow.current_step,
            "total_steps": len(workflow.workflow_steps),
            "progress_percentage": (
                (workflow.current_step / len(workflow.workflow_steps) * 100)
                if workflow.workflow_steps
                else 0
            ),
            "assigned_agents": len(workflow.assigned_agents),
            "generated_policies": len(workflow.generated_policies),
            "start_time": workflow.start_time.isoformat(),
            "estimated_completion": (
                workflow.estimated_completion.isoformat()
                if workflow.estimated_completion
                else None
            ),
            "actual_completion": (
                workflow.actual_completion.isoformat()
                if workflow.actual_completion
                else None
            ),
            "success_metrics": workflow.success_metrics,
            "errors": len(workflow.error_log),
        }

    def _get_workflow_request_schema(self) -> dict[str, Any]:
        """Get schema for workflow request validation"""
        return {
            "type": "object",
            "properties": {
                "name": {"type": "string", "maxLength": 100},
                "description": {"type": "string", "maxLength": 500},
                "requirements": {"type": "object"},
                "coordination_strategy": {
                    "type": "string",
                    "enum": [
                        "sequential",
                        "parallel",
                        "hierarchical",
                        "consensus",
                        "competitive",
                    ],
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "critical"],
                },
            },
            "required": ["name", "requirements"],
        }

    # Helper methods for structured workflow creation

    async def _create_policy_manager_agent(self) -> str:
        """Create a specialized policy manager agent using new role system"""
        role_id = f"policy_manager_{uuid.uuid4().hex[:8]}"

        # Create specialized role
        policy_manager_role = SpecializedRoleFactory.create_role(
            AgentRoleType.POLICY_MANAGER,
            role_id,
            self.constitutional_framework,
            self.audit_logger,
            self.performance_monitor,
        )

        # Initialize and register role
        await policy_manager_role.initialize()
        self.role_registry.register_role(policy_manager_role)

        return role_id

    async def _create_architect_agent(self) -> str:
        """Create a specialized architect agent using new role system"""
        role_id = f"architect_{uuid.uuid4().hex[:8]}"

        # Create specialized role
        architect_role = SpecializedRoleFactory.create_role(
            AgentRoleType.ARCHITECT,
            role_id,
            self.constitutional_framework,
            self.audit_logger,
            self.performance_monitor,
        )

        # Initialize and register role
        await architect_role.initialize()
        self.role_registry.register_role(architect_role)

        return role_id

    async def _create_validator_agent(self) -> str:
        """Create a specialized validator agent using new role system"""
        role_id = f"validator_{uuid.uuid4().hex[:8]}"

        # Create specialized role
        validator_role = SpecializedRoleFactory.create_role(
            AgentRoleType.VALIDATOR,
            role_id,
            self.constitutional_framework,
            self.audit_logger,
            self.performance_monitor,
        )

        # Initialize and register role
        await validator_role.initialize()
        self.role_registry.register_role(validator_role)

        return role_id

    async def _create_implementer_agent(self) -> str:
        """Create a specialized implementer agent using new role system"""
        role_id = f"implementer_{uuid.uuid4().hex[:8]}"

        # Create specialized role
        implementer_role = SpecializedRoleFactory.create_role(
            AgentRoleType.IMPLEMENTER,
            role_id,
            self.constitutional_framework,
            self.audit_logger,
            self.performance_monitor,
        )

        # Initialize and register role
        await implementer_role.initialize()
        self.role_registry.register_role(implementer_role)

        return role_id

    async def _assign_agents_to_tasks(
        self, roles: dict[str, str]
    ) -> dict[str, list[str]]:
        """Assign agents to tasks based on their roles"""
        assignments = {}

        # Define task assignments for each role
        task_mapping = {
            "policy_manager": ["requirements_gathering", "stakeholder_coordination"],
            "architect": ["system_design", "architecture_specification"],
            "implementer": ["policy_implementation", "system_deployment"],
            "validator": ["validation_testing", "compliance_verification"],
        }

        for role, agent_id in roles.items():
            assignments[agent_id] = task_mapping.get(role, [])

        return assignments

    async def _create_task_dependencies(self) -> dict[str, list[str]]:
        """Create task dependency mapping for structured workflow"""
        return {
            "system_design": ["requirements_gathering"],
            "architecture_specification": ["system_design"],
            "policy_implementation": ["architecture_specification"],
            "system_deployment": ["policy_implementation"],
            "validation_testing": ["system_deployment"],
            "compliance_verification": ["validation_testing"],
        }

    async def _setup_document_channels(
        self, channels: dict[str, DocumentChannel]
    ) -> dict[str, Any]:
        """Setup communication rules for document channels"""
        rules = {}

        for channel_name, channel in channels.items():
            rules[channel_name] = {
                "channel_type": "document_based",
                "schema": channel.schema.__name__,
                "subscribers": channel.subscribers,
                "approval_required": True,
                "constitutional_validation": True,
            }

        return rules


class MessageBroker:
    """Simple message broker for agent communication"""

    def __init__(self):
        self.message_queues: dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

    async def send_message(
        self, recipient_id: str, message: AgentCommunication
    ) -> None:
        """Send message to agent"""
        self.message_queues[recipient_id].append(message)

    async def get_messages(self, agent_id: str) -> list[AgentCommunication]:
        """Get messages for agent"""
        messages = list(self.message_queues[agent_id])
        self.message_queues[agent_id].clear()
        return messages
