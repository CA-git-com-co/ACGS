"""
Main Ethics Agent for Multi-Agent Governance System.

This module contains the orchestrating EthicsAgent class that coordinates
ethical analysis, bias detection, and fairness evaluation.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from ....shared.ai_model_service import AIModelService
from ....shared.blackboard import BlackboardService, KnowledgeItem, TaskDefinition
from ....shared.constitutional_safety_framework import ConstitutionalSafetyValidator
from .analyzers import EthicalAnalyzer
from .detectors import BiasDetector, FairnessAnalyzer
from .models import EthicalAnalysisResult

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"



class EthicsAgent:
    """
    Ethics Agent for Multi-Agent Governance System.

    Specialized agent for ethical analysis and bias assessment tasks.
    Coordinates between different analysis components to provide
    comprehensive ethical evaluation.

    Example:
        agent = EthicsAgent()
        await agent.initialize()

        result = await agent.analyze_proposal({
            "policy": "algorithmic_hiring",
            "scope": "job_candidates",
            "domain": "recruitment"
        })
    """

    def __init__(
        self,
        agent_id: str | None = None,
        blackboard_service: BlackboardService | None = None,
        ai_model_service: AIModelService | None = None,
    ):
        """
        Initialize the Ethics Agent.

        Args:
            agent_id: Unique identifier for this agent
            blackboard_service: Blackboard service for coordination
            ai_model_service: AI model service for advanced analysis
        """
        self.agent_id = agent_id or f"ethics_agent_{str(uuid4())[:8]}"
        self.blackboard = blackboard_service
        self.ai_service = ai_model_service
        self.logger = logging.getLogger(__name__)

        # Initialize analysis components
        self.ethical_analyzer = EthicalAnalyzer()
        self.bias_detector = BiasDetector()
        self.fairness_analyzer = FairnessAnalyzer()

        # Constitutional safety validator
        self.constitutional_validator: ConstitutionalSafetyValidator | None = None

        # Agent state
        self.is_running = False
        self.current_tasks: dict[str, TaskDefinition] = {}

        # Configuration
        self.task_polling_interval = 5.0  # seconds
        self.max_concurrent_tasks = 3

    async def initialize(self) -> None:
        """
        Initialize the ethics agent and its dependencies.

        Example:
            await agent.initialize()
        """
        if self.ai_service:
            await self.ai_service.initialize()

        if self.blackboard:
            # Register agent with blackboard
            await self._register_with_blackboard()

        # Initialize constitutional validator
        self.constitutional_validator = ConstitutionalSafetyValidator()

        self.logger.info(f"Ethics agent {self.agent_id} initialized")

    async def start(self) -> None:
        """
        Start the ethics agent task processing loop.

        Example:
            await agent.start()  # Runs indefinitely
        """
        self.is_running = True
        self.logger.info(f"Ethics agent {self.agent_id} started")

        try:
            while self.is_running:
                await self._process_tasks()
                await asyncio.sleep(self.task_polling_interval)
        except Exception as e:
            self.logger.error(f"Error in agent loop: {e}")
        finally:
            await self.stop()

    async def stop(self) -> None:
        """
        Stop the ethics agent and cleanup resources.

        Example:
            await agent.stop()
        """
        self.is_running = False

        # Complete any ongoing tasks
        if self.current_tasks:
            self.logger.info(f"Completing {len(self.current_tasks)} ongoing tasks")
            await self._complete_current_tasks()

        if self.ai_service:
            await self.ai_service.shutdown()

        self.logger.info(f"Ethics agent {self.agent_id} stopped")

    async def analyze_proposal(
        self, proposal: dict[str, Any], context: dict[str, Any] | None = None
    ) -> EthicalAnalysisResult:
        """
        Analyze a proposal for ethical implications and bias.

        Args:
            proposal: The proposal or policy to analyze
            context: Additional context and requirements

        Returns:
            EthicalAnalysisResult with comprehensive analysis

        Example:
            result = await agent.analyze_proposal(
                {
                    "policy": "algorithmic_hiring",
                    "scope": "job_candidates",
                    "type": "ai_system"
                },
                {"domain": "recruitment", "regulations": ["EEOC"]}
            )
        """
        context = context or {}

        try:
            # Perform comprehensive ethical analysis
            analysis_result = await self.ethical_analyzer.analyze_ethical_implications(
                proposal, context
            )

            # Enhance with bias detection if applicable
            if self._requires_bias_analysis(proposal):
                bias_assessment = await self.bias_detector.detect_demographic_bias(
                    proposal, context
                )
                analysis_result.bias_assessment = bias_assessment.model_dump()

            # Add constitutional compliance check
            if self.constitutional_validator:
                constitutional_result = await self.constitutional_validator.validate_constitutional_compliance(
                    proposal, context
                )
                analysis_result.constitutional_compliance.update(constitutional_result)

            # Log analysis completion
            self.logger.info(
                f"Completed ethical analysis for proposal. "
                f"Approved: {analysis_result.approved}, "
                f"Risk: {analysis_result.risk_level}, "
                f"Confidence: {analysis_result.confidence:.2f}"
            )

            return analysis_result

        except Exception as e:
            self.logger.error(f"Error in ethical analysis: {e}")
            # Return safe default
            return EthicalAnalysisResult(
                approved=False,
                risk_level="high",
                confidence=0.1,
                recommendations=["Manual review required due to analysis error"],
                analysis_metadata={"error": str(e)},
            )

    async def _process_tasks(self) -> None:
        """Process available tasks from the blackboard."""
        if not self.blackboard or len(self.current_tasks) >= self.max_concurrent_tasks:
            return

        try:
            # Get available ethical analysis tasks
            available_tasks = await self.blackboard.task_manager.get_available_tasks(
                task_type="ethical_analysis",
                limit=self.max_concurrent_tasks - len(self.current_tasks),
            )

            for task in available_tasks:
                if await self.blackboard.claim_task(task.id, self.agent_id):
                    self.current_tasks[task.id] = task
                    # Process task asynchronously
                    asyncio.create_task(self._handle_task(task))

        except Exception as e:
            self.logger.error(f"Error processing tasks: {e}")

    async def _handle_task(self, task: TaskDefinition) -> None:
        """Handle a specific ethical analysis task."""
        try:
            # Update task status
            await self.blackboard.task_manager.update_task_status(
                task.id, "in_progress"
            )

            # Extract proposal and context from task
            proposal = task.input_data.get("proposal", {})
            context = task.input_data.get("context", {})
            context.update(task.requirements)

            # Perform analysis
            result = await self.analyze_proposal(proposal, context)

            # Update task with results
            await self.blackboard.task_manager.update_task_status(
                task.id,
                "completed",
                output_data={
                    "ethical_analysis": result.model_dump(),
                    "agent_id": self.agent_id,
                    "analysis_timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

            # Add knowledge to blackboard
            knowledge = KnowledgeItem(
                space="governance",
                agent_id=self.agent_id,
                task_id=task.id,
                knowledge_type="ethical_analysis",
                content=result.model_dump(),
                tags={"ethics", "analysis", task.task_type},
            )
            await self.blackboard.add_knowledge(knowledge)

        except Exception as e:
            self.logger.error(f"Error handling task {task.id}: {e}")
            # Mark task as failed
            await self.blackboard.task_manager.update_task_status(
                task.id,
                "failed",
                error_details={"error": str(e), "agent_id": self.agent_id},
            )
        finally:
            # Remove from current tasks
            self.current_tasks.pop(task.id, None)

    async def _complete_current_tasks(self) -> None:
        """Wait for all current tasks to complete."""
        while self.current_tasks:
            await asyncio.sleep(1.0)
            # Check for stuck tasks and handle them
            for task_id in list(self.current_tasks.keys()):
                task = self.current_tasks[task_id]
                # If task has been running for too long, mark as failed
                if hasattr(task, "claimed_at") and task.claimed_at:
                    runtime = datetime.now(timezone.utc) - task.claimed_at
                    if runtime.total_seconds() > 300:  # 5 minutes timeout
                        await self.blackboard.task_manager.update_task_status(
                            task_id, "failed", error_details={"error": "Task timeout"}
                        )
                        self.current_tasks.pop(task_id, None)

    async def _register_with_blackboard(self) -> None:
        """Register this agent with the blackboard service."""
        agent_info = KnowledgeItem(
            space="coordination",
            agent_id=self.agent_id,
            knowledge_type="agent_registration",
            content={
                "agent_type": "ethics_agent",
                "capabilities": [
                    "ethical_analysis",
                    "bias_detection",
                    "fairness_evaluation",
                    "harm_assessment",
                    "stakeholder_impact_analysis",
                ],
                "task_types": ["ethical_analysis"],
                "max_concurrent_tasks": self.max_concurrent_tasks,
                "status": "active",
            },
            tags={"agent", "ethics", "registration"},
        )
        await self.blackboard.add_knowledge(agent_info)

    def _requires_bias_analysis(self, proposal: dict[str, Any]) -> bool:
        """Determine if proposal requires bias analysis."""
        proposal_str = str(proposal).lower()
        bias_keywords = [
            "algorithm",
            "ai",
            "ml",
            "model",
            "prediction",
            "classification",
            "scoring",
            "ranking",
            "recommendation",
        ]
        return any(keyword in proposal_str for keyword in bias_keywords)
