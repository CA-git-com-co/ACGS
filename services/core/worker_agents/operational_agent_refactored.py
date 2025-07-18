"""
Refactored Operational Agent for Multi-Agent Governance System
Modular design with specialized handlers for better maintainability.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from .operational_agent_handlers import (
    BaseOperationalHandler,
    OperationalValidationHandler,
    PerformanceAnalysisHandler,
    InfrastructureAssessmentHandler,
    ImplementationPlanningHandler,
    DeploymentHandler,
    ConstitutionalComplianceHandler,
)

# Import original models and analyzers
from .operational_agent import (
    OperationalAnalysisResult,
    PerformanceAnalyzer,
    ScalabilityAnalyzer,
    DeploymentPlanner,
)

from ...shared.blackboard import BlackboardService, KnowledgeItem, TaskDefinition
from ...shared.constitutional_safety_framework import ConstitutionalSafetyValidator
from ...shared.performance_monitoring import PerformanceMonitor

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class OperationalAgentRefactored:
    """
    Refactored Operational Agent with modular handler architecture.
    Provides the same functionality as the original but with better maintainability.
    """

    def __init__(
        self,
        agent_id: str = "operational_agent_refactored",
        blackboard_service: BlackboardService = None,
        constitutional_framework: ConstitutionalSafetyValidator = None,
        performance_monitor: PerformanceMonitor = None,
    ):
        self.agent_id = agent_id
        self.agent_type = "operational_agent"
        self.blackboard = blackboard_service or BlackboardService()
        self.constitutional_framework = constitutional_framework
        self.performance_monitor = performance_monitor

        self.logger = logging.getLogger(__name__)
        self.is_running = False

        # Initialize specialized handlers
        self.validation_handler = OperationalValidationHandler(
            agent_id, self.blackboard, constitutional_framework, performance_monitor
        )
        self.performance_handler = PerformanceAnalysisHandler(
            agent_id, self.blackboard, constitutional_framework, performance_monitor
        )
        self.infrastructure_handler = InfrastructureAssessmentHandler(
            agent_id, self.blackboard, constitutional_framework, performance_monitor
        )
        self.implementation_handler = ImplementationPlanningHandler(
            agent_id, self.blackboard, constitutional_framework, performance_monitor
        )
        self.deployment_handler = DeploymentHandler(
            agent_id, self.blackboard, constitutional_framework, performance_monitor
        )
        self.compliance_handler = ConstitutionalComplianceHandler(
            agent_id, self.blackboard, constitutional_framework, performance_monitor
        )

        # Task type handlers mapping
        self.task_handlers = {
            "operational_validation": self.validation_handler.handle_operational_validation,
            "operational_analysis": self.validation_handler.handle_operational_validation,
            "performance_analysis": self.performance_handler.handle_performance_analysis,
            "implementation_planning": self.implementation_handler.handle_implementation_planning,
            "scalability_analysis": self._handle_scalability_analysis,  # Keep original for now
            "deployment_planning": self.deployment_handler.handle_deployment_planning,
            "infrastructure_assessment": self.infrastructure_handler.handle_infrastructure_assessment,
        }

        # Constitutional principles this agent focuses on
        self.constitutional_principles = [
            "resource_limits",
            "reversibility",
            "least_privilege",
        ]

        # Agent capabilities
        self.capabilities = [
            "performance_analysis",
            "scalability_assessment",
            "resource_planning",
            "infrastructure_evaluation",
            "monitoring_setup",
            "deployment_planning",
        ]

    async def start(self) -> None:
        """Start the operational agent."""
        if self.is_running:
            return

        self.logger.info(f"Starting operational agent: {self.agent_id}")
        self.is_running = True

        # Register agent with blackboard
        await self.blackboard.register_agent(
            agent_id=self.agent_id,
            agent_type=self.agent_type,
            capabilities=self.capabilities,
            constitutional_principles=self.constitutional_principles,
        )

        # Start heartbeat loop
        asyncio.create_task(self._heartbeat_loop())

    async def stop(self) -> None:
        """Stop the operational agent."""
        if not self.is_running:
            return

        self.logger.info(f"Stopping operational agent: {self.agent_id}")
        self.is_running = False

        # Unregister agent from blackboard
        await self.blackboard.unregister_agent(self.agent_id)

    async def process_task(self, task: TaskDefinition) -> Dict[str, Any]:
        """Process a task based on its type."""
        try:
            self.logger.info(
                f"Processing task: {task.task_id} of type: {task.task_type}"
            )

            # Get handler for task type
            handler = self.task_handlers.get(task.task_type)
            if not handler:
                error_msg = f"No handler for task type: {task.task_type}"
                self.logger.error(error_msg)
                return {"error": error_msg, "task_id": task.task_id}

            # Execute handler
            result = await handler(task)

            # Add constitutional compliance validation
            if task.task_data.get("governance_request"):
                compliance_result = (
                    await self.compliance_handler.check_constitutional_compliance(
                        task.task_data["governance_request"]
                    )
                )
                result["constitutional_compliance"] = compliance_result

            # Update task status
            await self.blackboard.update_task_status(task.task_id, "completed", result)

            return result

        except Exception as e:
            self.logger.error(f"Error processing task {task.task_id}: {e}")
            error_result = {"error": str(e), "task_id": task.task_id}

            await self.blackboard.update_task_status(
                task.task_id, "failed", error_result
            )

            return error_result

    async def _handle_scalability_analysis(
        self, task: TaskDefinition
    ) -> Dict[str, Any]:
        """Handle scalability analysis task using original ScalabilityAnalyzer."""
        try:
            self.logger.info(
                f"Processing scalability analysis for task: {task.task_id}"
            )

            governance_request = task.task_data.get("governance_request", {})
            model_info = governance_request.get("model_info", {})

            # Use original ScalabilityAnalyzer
            scalability_result = (
                await ScalabilityAnalyzer.analyze_scalability_requirements(
                    model_info=model_info,
                    scalability_requirements=governance_request.get(
                        "scalability_requirements", {}
                    ),
                    infrastructure_constraints=governance_request.get(
                        "infrastructure_constraints", {}
                    ),
                )
            )

            # Add result to blackboard
            await self._add_scalability_knowledge(task, scalability_result)

            return scalability_result

        except Exception as e:
            self.logger.error(f"Error in scalability analysis: {e}")
            return {"error": str(e), "analysis_complete": False}

    async def _add_scalability_knowledge(
        self, task: TaskDefinition, result: Dict[str, Any]
    ) -> None:
        """Add scalability analysis results to blackboard."""
        knowledge_item = KnowledgeItem(
            knowledge_id=f"scalability_analysis_{task.task_id}",
            content=result,
            agent_id=self.agent_id,
            knowledge_type="scalability_analysis",
            confidence=result.get("overall_scalability_score", 0.5),
            metadata={
                "task_id": task.task_id,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

        await self.blackboard.add_knowledge(knowledge_item)

    async def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "is_running": self.is_running,
            "capabilities": self.capabilities,
            "constitutional_principles": self.constitutional_principles,
            "handlers": {
                "validation": "OperationalValidationHandler",
                "performance": "PerformanceAnalysisHandler",
                "infrastructure": "InfrastructureAssessmentHandler",
                "implementation": "ImplementationPlanningHandler",
                "deployment": "DeploymentHandler",
                "compliance": "ConstitutionalComplianceHandler",
            },
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "last_heartbeat": datetime.now(timezone.utc).isoformat(),
        }

    async def _heartbeat_loop(self) -> None:
        """Heartbeat loop to maintain agent availability."""
        while self.is_running:
            try:
                # Update agent status in blackboard
                await self.blackboard.update_agent_status(
                    self.agent_id,
                    status="active",
                    metadata={
                        "last_heartbeat": datetime.now(timezone.utc).isoformat(),
                        "constitutional_hash": CONSTITUTIONAL_HASH,
                    },
                )

                # Check for new tasks
                available_tasks = await self.blackboard.get_available_tasks(
                    agent_capabilities=self.capabilities
                )

                for task in available_tasks:
                    if task.task_type in self.task_handlers:
                        # Claim task
                        claimed = await self.blackboard.claim_task(
                            task.task_id, self.agent_id
                        )
                        if claimed:
                            # Process task in background
                            asyncio.create_task(self.process_task(task))

                # Sleep for heartbeat interval
                await asyncio.sleep(30)  # 30 second heartbeat

            except Exception as e:
                self.logger.error(f"Error in heartbeat loop: {e}")
                await asyncio.sleep(60)  # Longer sleep on error

    async def health_check(self) -> Dict[str, Any]:
        """Perform health check of the operational agent."""
        try:
            # Check handler availability
            handlers_healthy = {
                "validation": self.validation_handler is not None,
                "performance": self.performance_handler is not None,
                "infrastructure": self.infrastructure_handler is not None,
                "implementation": self.implementation_handler is not None,
                "deployment": self.deployment_handler is not None,
                "compliance": self.compliance_handler is not None,
            }

            # Check blackboard connectivity
            blackboard_healthy = await self._check_blackboard_connectivity()

            # Overall health
            overall_healthy = all(handlers_healthy.values()) and blackboard_healthy

            return {
                "healthy": overall_healthy,
                "agent_id": self.agent_id,
                "is_running": self.is_running,
                "handlers": handlers_healthy,
                "blackboard_connected": blackboard_healthy,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            self.logger.error(f"Error in health check: {e}")
            return {
                "healthy": False,
                "error": str(e),
                "agent_id": self.agent_id,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def _check_blackboard_connectivity(self) -> bool:
        """Check if blackboard is accessible."""
        try:
            # Simple connectivity check
            await self.blackboard.get_agent_status(self.agent_id)
            return True
        except Exception:
            return False

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the operational agent."""
        try:
            # Get basic metrics
            metrics = {
                "agent_id": self.agent_id,
                "uptime_seconds": 0,  # Would track actual uptime
                "tasks_processed": 0,  # Would track actual task count
                "tasks_failed": 0,  # Would track actual failure count
                "avg_processing_time_ms": 0,  # Would track actual processing time
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

            # Add handler-specific metrics if available
            if self.performance_monitor:
                additional_metrics = await self.performance_monitor.get_agent_metrics(
                    self.agent_id
                )
                metrics.update(additional_metrics)

            return metrics

        except Exception as e:
            self.logger.error(f"Error getting performance metrics: {e}")
            return {
                "error": str(e),
                "agent_id": self.agent_id,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }


# Factory function for easy instantiation
def create_operational_agent(
    agent_id: str = "operational_agent_refactored",
    blackboard_service: BlackboardService = None,
    constitutional_framework: ConstitutionalSafetyValidator = None,
    performance_monitor: PerformanceMonitor = None,
) -> OperationalAgentRefactored:
    """
    Create a new operational agent instance with all handlers initialized.

    Args:
        agent_id: Unique identifier for the agent
        blackboard_service: Blackboard service instance
        constitutional_framework: Constitutional safety validator
        performance_monitor: Performance monitoring service

    Returns:
        Configured OperationalAgentRefactored instance
    """
    return OperationalAgentRefactored(
        agent_id=agent_id,
        blackboard_service=blackboard_service,
        constitutional_framework=constitutional_framework,
        performance_monitor=performance_monitor,
    )
