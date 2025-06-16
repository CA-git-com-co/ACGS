"""
Workflow Orchestrator for ACGS-1 Advanced Governance Workflows.

This module implements the central orchestrator for managing the 5 core governance
workflows with state management, performance monitoring, and error recovery.

Core Workflows:
1. Policy Creation - Draft → Review → Voting → Implementation
2. Constitutional Compliance - Validation → Assessment → Enforcement
3. Policy Enforcement - Monitoring → Violation Detection → Remediation
4. WINA Oversight - Performance Monitoring → Optimization → Reporting
5. Audit/Transparency - Data Collection → Analysis → Public Reporting
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import aiohttp

logger = logging.getLogger(__name__)


class WorkflowType(Enum):
    """Workflow type enumeration."""
    POLICY_CREATION = "policy_creation"
    CONSTITUTIONAL_COMPLIANCE = "constitutional_compliance"
    POLICY_ENFORCEMENT = "policy_enforcement"
    WINA_OVERSIGHT = "wina_oversight"
    AUDIT_TRANSPARENCY = "audit_transparency"


class WorkflowStatus(Enum):
    """Workflow status enumeration."""
    PENDING = "pending"
    INITIATED = "initiated"
    IN_PROGRESS = "in_progress"
    WAITING_APPROVAL = "waiting_approval"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


class WorkflowPriority(Enum):
    """Workflow priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class WorkflowStep:
    """Workflow step data structure."""
    step_id: str
    step_name: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class WorkflowInstance:
    """Workflow instance data structure."""
    workflow_id: str
    workflow_type: WorkflowType
    status: WorkflowStatus = WorkflowStatus.PENDING
    priority: WorkflowPriority = WorkflowPriority.NORMAL
    steps: List[WorkflowStep] = field(default_factory=list)
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    timeout_minutes: int = 30
    requester_id: Optional[str] = None
    stakeholders: List[str] = field(default_factory=list)


class WorkflowOrchestrator:
    """
    Central orchestrator for managing governance workflows.
    
    This orchestrator coordinates the execution of all 5 core governance workflows,
    providing state management, performance monitoring, and error recovery.
    """
    
    def __init__(self, settings, performance_monitor, service_integrator, metrics_collector):
        self.settings = settings
        self.performance_monitor = performance_monitor
        self.service_integrator = service_integrator
        self.metrics_collector = metrics_collector
        
        # Workflow state
        self.active_workflows: Dict[str, WorkflowInstance] = {}
        self.workflow_history: List[WorkflowInstance] = []
        self.workflow_templates: Dict[WorkflowType, List[WorkflowStep]] = {}
        
        # Performance metrics
        self.workflow_metrics: Dict[str, Any] = {
            "total_workflows": 0,
            "active_workflows": 0,
            "completed_workflows": 0,
            "failed_workflows": 0,
            "average_duration_ms": 0,
            "success_rate": 0.0,
        }
        
        # Configuration
        self.max_concurrent_workflows = settings.MAX_CONCURRENT_WORKFLOWS
        self.workflow_timeout_minutes = settings.WORKFLOW_TIMEOUT_MINUTES
        self.constitution_hash = settings.CONSTITUTION_HASH
        
        logger.info("Workflow orchestrator initialized")
    
    async def initialize(self):
        """Initialize the workflow orchestrator."""
        try:
            # Initialize workflow templates
            await self._initialize_workflow_templates()
            
            # Start background monitoring
            asyncio.create_task(self._monitor_workflow_health())
            asyncio.create_task(self._cleanup_completed_workflows())
            
            logger.info("✅ Workflow orchestrator initialization complete")
            
        except Exception as e:
            logger.error(f"❌ Workflow orchestrator initialization failed: {e}")
            raise
    
    async def initiate_workflow(
        self,
        workflow_type: WorkflowType,
        input_data: Dict[str, Any],
        priority: WorkflowPriority = WorkflowPriority.NORMAL,
        requester_id: Optional[str] = None,
        stakeholders: List[str] = None,
    ) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Initiate a new governance workflow.
        
        Args:
            workflow_type: Type of workflow to initiate
            input_data: Input data for the workflow
            priority: Workflow priority level
            requester_id: ID of the requesting user
            stakeholders: List of stakeholder IDs
            
        Returns:
            Tuple of (success, workflow_id, status_info)
        """
        try:
            # Check concurrent workflow limits
            if len(self.active_workflows) >= self.max_concurrent_workflows:
                return False, "", {
                    "error": "Maximum concurrent workflows reached",
                    "limit": self.max_concurrent_workflows,
                    "active": len(self.active_workflows),
                }
            
            # Create workflow instance
            workflow_id = f"{workflow_type.value}_{int(time.time())}_{str(uuid.uuid4())[:8]}"
            
            workflow_instance = WorkflowInstance(
                workflow_id=workflow_id,
                workflow_type=workflow_type,
                priority=priority,
                input_data=input_data,
                requester_id=requester_id,
                stakeholders=stakeholders or [],
                steps=self._get_workflow_steps(workflow_type),
            )
            
            # Add to active workflows
            self.active_workflows[workflow_id] = workflow_instance
            
            # Start workflow execution
            asyncio.create_task(self._execute_workflow(workflow_id))
            
            # Update metrics
            self.workflow_metrics["total_workflows"] += 1
            self.workflow_metrics["active_workflows"] = len(self.active_workflows)
            
            logger.info(f"Workflow initiated: {workflow_id} ({workflow_type.value})")
            
            return True, workflow_id, {
                "workflow_id": workflow_id,
                "workflow_type": workflow_type.value,
                "status": "initiated",
                "priority": priority.value,
                "estimated_duration_minutes": self._estimate_workflow_duration(workflow_type),
                "steps_count": len(workflow_instance.steps),
            }
            
        except Exception as e:
            logger.error(f"Failed to initiate workflow: {e}")
            return False, "", {"error": str(e)}
    
    async def get_workflow_status(self, workflow_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Get the status of a workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Tuple of (found, status_info)
        """
        try:
            # Check active workflows
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
                return True, self._format_workflow_status(workflow)
            
            # Check workflow history
            for workflow in self.workflow_history:
                if workflow.workflow_id == workflow_id:
                    return True, self._format_workflow_status(workflow)
            
            return False, {"error": "Workflow not found"}
            
        except Exception as e:
            logger.error(f"Failed to get workflow status: {e}")
            return False, {"error": str(e)}
    
    async def cancel_workflow(self, workflow_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Cancel an active workflow.
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Tuple of (success, cancellation_info)
        """
        try:
            if workflow_id not in self.active_workflows:
                return False, {"error": "Workflow not found or not active"}
            
            workflow = self.active_workflows[workflow_id]
            workflow.status = WorkflowStatus.CANCELLED
            workflow.completed_at = datetime.now(timezone.utc)
            
            # Move to history
            self.workflow_history.append(workflow)
            del self.active_workflows[workflow_id]
            
            # Update metrics
            self.workflow_metrics["active_workflows"] = len(self.active_workflows)
            
            logger.info(f"Workflow cancelled: {workflow_id}")
            
            return True, {
                "workflow_id": workflow_id,
                "status": "cancelled",
                "cancelled_at": workflow.completed_at.isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel workflow: {e}")
            return False, {"error": str(e)}
    
    async def get_workflow_metrics(self) -> Dict[str, Any]:
        """Get workflow orchestrator metrics."""
        try:
            # Calculate current metrics
            total_workflows = len(self.workflow_history) + len(self.active_workflows)
            completed_workflows = len([
                w for w in self.workflow_history 
                if w.status == WorkflowStatus.COMPLETED
            ])
            failed_workflows = len([
                w for w in self.workflow_history 
                if w.status == WorkflowStatus.FAILED
            ])
            
            # Calculate success rate
            success_rate = (completed_workflows / max(len(self.workflow_history), 1)) * 100
            
            # Calculate average duration
            completed_with_duration = [
                w for w in self.workflow_history
                if w.status == WorkflowStatus.COMPLETED and w.started_at and w.completed_at
            ]
            
            if completed_with_duration:
                total_duration = sum(
                    (w.completed_at - w.started_at).total_seconds() * 1000
                    for w in completed_with_duration
                )
                average_duration = total_duration / len(completed_with_duration)
            else:
                average_duration = 0
            
            return {
                "total_workflows": total_workflows,
                "active_workflows": len(self.active_workflows),
                "completed_workflows": completed_workflows,
                "failed_workflows": failed_workflows,
                "success_rate": round(success_rate, 2),
                "average_duration_ms": round(average_duration, 2),
                "workflow_types": {
                    workflow_type.value: len([
                        w for w in self.active_workflows.values()
                        if w.workflow_type == workflow_type
                    ])
                    for workflow_type in WorkflowType
                },
                "constitution_hash": self.constitution_hash,
                "max_concurrent_workflows": self.max_concurrent_workflows,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Failed to get workflow metrics: {e}")
            return {"error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check for the workflow orchestrator."""
        try:
            health_status = {
                "healthy": True,
                "timestamp": time.time(),
                "checks": {},
            }
            
            # Check workflow capacity
            workflow_capacity = (len(self.active_workflows) / self.max_concurrent_workflows) * 100
            health_status["checks"]["workflow_capacity"] = {
                "healthy": workflow_capacity < 90,
                "capacity_percent": round(workflow_capacity, 2),
                "active_workflows": len(self.active_workflows),
                "max_workflows": self.max_concurrent_workflows,
            }
            if workflow_capacity >= 90:
                health_status["healthy"] = False
            
            # Check service integrations
            integrator_health = await self.service_integrator.health_check()
            health_status["checks"]["service_integrations"] = integrator_health
            if not integrator_health.get("healthy", False):
                health_status["healthy"] = False
            
            # Check performance monitor
            monitor_health = await self.performance_monitor.health_check()
            health_status["checks"]["performance_monitor"] = monitor_health
            if not monitor_health.get("healthy", False):
                health_status["healthy"] = False
            
            return health_status
            
        except Exception as e:
            logger.error(f"Workflow orchestrator health check failed: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "timestamp": time.time(),
            }
    
    async def shutdown(self):
        """Shutdown the workflow orchestrator gracefully."""
        try:
            logger.info("Shutting down workflow orchestrator...")
            
            # Cancel active workflows
            for workflow_id in list(self.active_workflows.keys()):
                await self.cancel_workflow(workflow_id)
            
            logger.info("✅ Workflow orchestrator shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during workflow orchestrator shutdown: {e}")
    
    # Private helper methods
    async def _initialize_workflow_templates(self):
        """Initialize workflow templates for all workflow types."""
        try:
            # Policy Creation workflow template
            self.workflow_templates[WorkflowType.POLICY_CREATION] = [
                WorkflowStep("draft_creation", "Create Policy Draft"),
                WorkflowStep("stakeholder_review", "Stakeholder Review"),
                WorkflowStep("public_comment", "Public Comment Period"),
                WorkflowStep("voting", "Stakeholder Voting"),
                WorkflowStep("implementation", "Policy Implementation"),
            ]

            # Constitutional Compliance workflow template
            self.workflow_templates[WorkflowType.CONSTITUTIONAL_COMPLIANCE] = [
                WorkflowStep("validation_initiation", "Initiate Validation"),
                WorkflowStep("constitutional_analysis", "Constitutional Analysis"),
                WorkflowStep("compliance_assessment", "Compliance Assessment"),
                WorkflowStep("enforcement_recommendation", "Enforcement Recommendation"),
            ]

            # Policy Enforcement workflow template
            self.workflow_templates[WorkflowType.POLICY_ENFORCEMENT] = [
                WorkflowStep("monitoring_setup", "Setup Monitoring"),
                WorkflowStep("violation_detection", "Violation Detection"),
                WorkflowStep("impact_assessment", "Impact Assessment"),
                WorkflowStep("remediation_action", "Remediation Action"),
            ]

            # WINA Oversight workflow template
            self.workflow_templates[WorkflowType.WINA_OVERSIGHT] = [
                WorkflowStep("performance_monitoring", "Performance Monitoring"),
                WorkflowStep("bottleneck_analysis", "Bottleneck Analysis"),
                WorkflowStep("optimization_planning", "Optimization Planning"),
                WorkflowStep("optimization_implementation", "Optimization Implementation"),
                WorkflowStep("performance_reporting", "Performance Reporting"),
            ]

            # Audit/Transparency workflow template
            self.workflow_templates[WorkflowType.AUDIT_TRANSPARENCY] = [
                WorkflowStep("data_collection", "Data Collection"),
                WorkflowStep("audit_analysis", "Audit Analysis"),
                WorkflowStep("transparency_assessment", "Transparency Assessment"),
                WorkflowStep("public_reporting", "Public Reporting"),
            ]

            logger.info("Workflow templates initialized")

        except Exception as e:
            logger.error(f"Failed to initialize workflow templates: {e}")
            raise

    def _get_workflow_steps(self, workflow_type: WorkflowType) -> List[WorkflowStep]:
        """Get workflow steps for a specific workflow type."""
        template_steps = self.workflow_templates.get(workflow_type, [])
        return [
            WorkflowStep(
                step_id=f"{step.step_id}_{int(time.time())}",
                step_name=step.step_name,
                max_retries=3,
            )
            for step in template_steps
        ]

    def _estimate_workflow_duration(self, workflow_type: WorkflowType) -> int:
        """Estimate workflow duration in minutes."""
        duration_estimates = {
            WorkflowType.POLICY_CREATION: 15,
            WorkflowType.CONSTITUTIONAL_COMPLIANCE: 2,
            WorkflowType.POLICY_ENFORCEMENT: 1,
            WorkflowType.WINA_OVERSIGHT: 5,
            WorkflowType.AUDIT_TRANSPARENCY: 10,
        }
        return duration_estimates.get(workflow_type, 30)

    def _format_workflow_status(self, workflow: WorkflowInstance) -> Dict[str, Any]:
        """Format workflow status for API response."""
        return {
            "workflow_id": workflow.workflow_id,
            "workflow_type": workflow.workflow_type.value,
            "status": workflow.status.value,
            "priority": workflow.priority.value,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "duration_ms": (
                (workflow.completed_at - workflow.started_at).total_seconds() * 1000
                if workflow.started_at and workflow.completed_at
                else None
            ),
            "progress": self._calculate_workflow_progress(workflow),
            "steps": [
                {
                    "step_id": step.step_id,
                    "step_name": step.step_name,
                    "status": step.status.value,
                    "duration_ms": step.duration_ms,
                    "retry_count": step.retry_count,
                }
                for step in workflow.steps
            ],
            "requester_id": workflow.requester_id,
            "stakeholders": workflow.stakeholders,
            "metadata": workflow.metadata,
        }

    def _calculate_workflow_progress(self, workflow: WorkflowInstance) -> Dict[str, Any]:
        """Calculate workflow progress percentage."""
        total_steps = len(workflow.steps)
        if total_steps == 0:
            return {"percent": 0, "current_step": None, "next_step": None}

        completed_steps = len([
            step for step in workflow.steps
            if step.status == WorkflowStatus.COMPLETED
        ])

        progress_percent = (completed_steps / total_steps) * 100

        # Find current and next steps
        current_step = None
        next_step = None

        for step in workflow.steps:
            if step.status == WorkflowStatus.IN_PROGRESS:
                current_step = step.step_name
                break
            elif step.status == WorkflowStatus.PENDING:
                next_step = step.step_name
                break

        return {
            "percent": round(progress_percent, 2),
            "completed_steps": completed_steps,
            "total_steps": total_steps,
            "current_step": current_step,
            "next_step": next_step,
        }

    async def _execute_workflow(self, workflow_id: str):
        """Execute a workflow instance."""
        try:
            workflow = self.active_workflows.get(workflow_id)
            if not workflow:
                return

            workflow.status = WorkflowStatus.IN_PROGRESS
            workflow.started_at = datetime.now(timezone.utc)

            logger.info(f"Executing workflow: {workflow_id} ({workflow.workflow_type.value})")

            # Execute workflow steps
            for step in workflow.steps:
                try:
                    # Check if workflow was cancelled
                    if workflow.status == WorkflowStatus.CANCELLED:
                        break

                    # Execute step
                    success = await self._execute_workflow_step(workflow, step)

                    if not success and step.retry_count >= step.max_retries:
                        # Step failed after max retries
                        workflow.status = WorkflowStatus.FAILED
                        break
                    elif not success:
                        # Retry step
                        step.retry_count += 1
                        continue

                except Exception as e:
                    logger.error(f"Step execution failed: {step.step_name} - {e}")
                    step.status = WorkflowStatus.FAILED
                    step.error_message = str(e)
                    workflow.status = WorkflowStatus.FAILED
                    break

            # Complete workflow
            if workflow.status == WorkflowStatus.IN_PROGRESS:
                workflow.status = WorkflowStatus.COMPLETED
                self.workflow_metrics["completed_workflows"] += 1
            elif workflow.status == WorkflowStatus.FAILED:
                self.workflow_metrics["failed_workflows"] += 1

            workflow.completed_at = datetime.now(timezone.utc)

            # Move to history
            self.workflow_history.append(workflow)
            del self.active_workflows[workflow_id]

            # Update metrics
            self.workflow_metrics["active_workflows"] = len(self.active_workflows)

            logger.info(f"Workflow completed: {workflow_id} - {workflow.status.value}")

        except Exception as e:
            logger.error(f"Workflow execution failed: {workflow_id} - {e}")
            if workflow_id in self.active_workflows:
                workflow = self.active_workflows[workflow_id]
                workflow.status = WorkflowStatus.FAILED
                workflow.completed_at = datetime.now(timezone.utc)
                self.workflow_history.append(workflow)
                del self.active_workflows[workflow_id]

    async def _execute_workflow_step(self, workflow: WorkflowInstance, step: WorkflowStep) -> bool:
        """Execute a single workflow step."""
        try:
            step.status = WorkflowStatus.IN_PROGRESS
            step.started_at = datetime.now(timezone.utc)

            # Route step execution based on workflow type and step
            if workflow.workflow_type == WorkflowType.POLICY_CREATION:
                result = await self._execute_policy_creation_step(workflow, step)
            elif workflow.workflow_type == WorkflowType.CONSTITUTIONAL_COMPLIANCE:
                result = await self._execute_constitutional_compliance_step(workflow, step)
            elif workflow.workflow_type == WorkflowType.POLICY_ENFORCEMENT:
                result = await self._execute_policy_enforcement_step(workflow, step)
            elif workflow.workflow_type == WorkflowType.WINA_OVERSIGHT:
                result = await self._execute_wina_oversight_step(workflow, step)
            elif workflow.workflow_type == WorkflowType.AUDIT_TRANSPARENCY:
                result = await self._execute_audit_transparency_step(workflow, step)
            else:
                result = {"success": False, "error": "Unknown workflow type"}

            step.completed_at = datetime.now(timezone.utc)
            step.duration_ms = (step.completed_at - step.started_at).total_seconds() * 1000
            step.result = result

            if result.get("success", False):
                step.status = WorkflowStatus.COMPLETED
                return True
            else:
                step.status = WorkflowStatus.FAILED
                step.error_message = result.get("error", "Step execution failed")
                return False

        except Exception as e:
            step.status = WorkflowStatus.FAILED
            step.error_message = str(e)
            step.completed_at = datetime.now(timezone.utc)
            if step.started_at:
                step.duration_ms = (step.completed_at - step.started_at).total_seconds() * 1000
            return False

    async def _execute_policy_creation_step(self, workflow: WorkflowInstance, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a policy creation workflow step."""
        try:
            if "draft_creation" in step.step_id:
                return await self.service_integrator.call_gs_service(
                    "create_policy_draft", workflow.input_data
                )
            elif "stakeholder_review" in step.step_id:
                return await self.service_integrator.call_gs_service(
                    "initiate_stakeholder_review", {"workflow_id": workflow.workflow_id}
                )
            elif "public_comment" in step.step_id:
                return await self.service_integrator.call_gs_service(
                    "open_public_comment", {"workflow_id": workflow.workflow_id}
                )
            elif "voting" in step.step_id:
                return await self.service_integrator.call_gs_service(
                    "initiate_voting", {"workflow_id": workflow.workflow_id}
                )
            elif "implementation" in step.step_id:
                return await self.service_integrator.call_pgc_service(
                    "implement_policy", {"workflow_id": workflow.workflow_id}
                )
            else:
                return {"success": False, "error": "Unknown policy creation step"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _execute_constitutional_compliance_step(self, workflow: WorkflowInstance, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a constitutional compliance workflow step."""
        try:
            if "validation_initiation" in step.step_id:
                return await self.service_integrator.call_ac_service(
                    "initiate_validation", workflow.input_data
                )
            elif "constitutional_analysis" in step.step_id:
                return await self.service_integrator.call_ac_service(
                    "analyze_constitutional_compliance", {"workflow_id": workflow.workflow_id}
                )
            elif "compliance_assessment" in step.step_id:
                return await self.service_integrator.call_ac_service(
                    "assess_compliance", {"workflow_id": workflow.workflow_id}
                )
            elif "enforcement_recommendation" in step.step_id:
                return await self.service_integrator.call_pgc_service(
                    "recommend_enforcement", {"workflow_id": workflow.workflow_id}
                )
            else:
                return {"success": False, "error": "Unknown constitutional compliance step"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _execute_policy_enforcement_step(self, workflow: WorkflowInstance, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a policy enforcement workflow step."""
        try:
            if "monitoring_setup" in step.step_id:
                return await self.service_integrator.call_pgc_service(
                    "setup_monitoring", workflow.input_data
                )
            elif "violation_detection" in step.step_id:
                return await self.service_integrator.call_pgc_service(
                    "detect_violations", {"workflow_id": workflow.workflow_id}
                )
            elif "impact_assessment" in step.step_id:
                return await self.service_integrator.call_pgc_service(
                    "assess_impact", {"workflow_id": workflow.workflow_id}
                )
            elif "remediation_action" in step.step_id:
                return await self.service_integrator.call_pgc_service(
                    "execute_remediation", {"workflow_id": workflow.workflow_id}
                )
            else:
                return {"success": False, "error": "Unknown policy enforcement step"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _execute_wina_oversight_step(self, workflow: WorkflowInstance, step: WorkflowStep) -> Dict[str, Any]:
        """Execute a WINA oversight workflow step."""
        try:
            if "performance_monitoring" in step.step_id:
                return await self.performance_monitor.start_monitoring(workflow.input_data)
            elif "bottleneck_analysis" in step.step_id:
                return await self.performance_monitor.analyze_bottlenecks(workflow.workflow_id)
            elif "optimization_planning" in step.step_id:
                return await self.performance_monitor.plan_optimization(workflow.workflow_id)
            elif "optimization_implementation" in step.step_id:
                return await self.performance_monitor.implement_optimization(workflow.workflow_id)
            elif "performance_reporting" in step.step_id:
                return await self.performance_monitor.generate_report(workflow.workflow_id)
            else:
                return {"success": False, "error": "Unknown WINA oversight step"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _execute_audit_transparency_step(self, workflow: WorkflowInstance, step: WorkflowStep) -> Dict[str, Any]:
        """Execute an audit/transparency workflow step."""
        try:
            if "data_collection" in step.step_id:
                return await self.service_integrator.call_integrity_service(
                    "collect_audit_data", workflow.input_data
                )
            elif "audit_analysis" in step.step_id:
                return await self.service_integrator.call_integrity_service(
                    "analyze_audit_data", {"workflow_id": workflow.workflow_id}
                )
            elif "transparency_assessment" in step.step_id:
                return await self.service_integrator.call_integrity_service(
                    "assess_transparency", {"workflow_id": workflow.workflow_id}
                )
            elif "public_reporting" in step.step_id:
                return await self.service_integrator.call_integrity_service(
                    "generate_public_report", {"workflow_id": workflow.workflow_id}
                )
            else:
                return {"success": False, "error": "Unknown audit/transparency step"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _monitor_workflow_health(self):
        """Background task to monitor workflow health."""
        while True:
            try:
                # Check for timeout workflows
                current_time = datetime.now(timezone.utc)
                timeout_workflows = []

                for workflow_id, workflow in self.active_workflows.items():
                    if workflow.started_at:
                        elapsed_minutes = (current_time - workflow.started_at).total_seconds() / 60
                        if elapsed_minutes > workflow.timeout_minutes:
                            timeout_workflows.append(workflow_id)

                # Handle timeout workflows
                for workflow_id in timeout_workflows:
                    workflow = self.active_workflows[workflow_id]
                    workflow.status = WorkflowStatus.TIMEOUT
                    workflow.completed_at = current_time
                    self.workflow_history.append(workflow)
                    del self.active_workflows[workflow_id]
                    logger.warning(f"Workflow timed out: {workflow_id}")

                # Update metrics
                self.workflow_metrics["active_workflows"] = len(self.active_workflows)

                # Sleep for monitoring interval
                await asyncio.sleep(60)  # Check every minute

            except Exception as e:
                logger.error(f"Workflow health monitoring error: {e}")
                await asyncio.sleep(60)

    async def _cleanup_completed_workflows(self):
        """Background task to cleanup old completed workflows."""
        while True:
            try:
                current_time = datetime.now(timezone.utc)
                old_workflows = []

                # Remove workflows older than 24 hours
                for workflow in self.workflow_history:
                    if workflow.completed_at:
                        age_hours = (current_time - workflow.completed_at).total_seconds() / 3600
                        if age_hours > 24:
                            old_workflows.append(workflow)

                for workflow in old_workflows:
                    self.workflow_history.remove(workflow)

                if old_workflows:
                    logger.info(f"Cleaned up {len(old_workflows)} old workflows")

                # Sleep for cleanup interval
                await asyncio.sleep(3600)  # Check every hour

            except Exception as e:
                logger.error(f"Workflow cleanup error: {e}")
                await asyncio.sleep(3600)
