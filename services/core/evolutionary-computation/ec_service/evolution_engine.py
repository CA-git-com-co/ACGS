"""
Complete Evolution Engine for ACGS Evolutionary Computation Service
Implements human-controlled evolution framework with constitutional compliance.
"""

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import aiohttp
from prometheus_client import Counter, Gauge, Histogram

logger = logging.getLogger(__name__)

# Constitutional hash for compliance validation
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class EvolutionType(Enum):
    """Types of evolution operations."""

    POLICY_EVOLUTION = "policy_evolution"
    ALGORITHM_OPTIMIZATION = "algorithm_optimization"
    CONSTITUTIONAL_UPDATE = "constitutional_update"
    SECURITY_ENHANCEMENT = "security_enhancement"
    PERFORMANCE_TUNING = "performance_tuning"


class EvolutionStatus(Enum):
    """Evolution request status."""

    PENDING = "pending"
    EVALUATING = "evaluating"
    HUMAN_REVIEW = "human_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"


class RiskLevel(Enum):
    """Risk levels for evolution requests."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class EvolutionRequest:
    """Evolution request data structure."""

    evolution_id: str
    evolution_type: EvolutionType
    description: str
    proposed_changes: dict[str, Any]
    requester_id: str
    target_service: str

    # Risk assessment
    risk_level: RiskLevel | None = None
    impact_assessment: dict[str, Any] | None = None

    # Constitutional compliance
    constitutional_compliance_required: bool = True
    constitutional_validation_score: float | None = None

    # Metadata
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    priority: int = 3  # 1=critical, 2=high, 3=medium, 4=low


@dataclass
class EvolutionEvaluation:
    """Evolution evaluation result."""

    evaluation_id: str
    evolution_id: str

    # Evaluation scores (0.0 to 1.0)
    constitutional_compliance_score: float
    security_impact_score: float
    performance_impact_score: float
    risk_assessment_score: float

    # Overall evaluation
    overall_score: float
    recommendation: str  # approve, review, reject

    # Detailed analysis
    analysis_details: dict[str, Any]
    evaluation_timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


@dataclass
class HumanReviewTask:
    """Human review task for evolution requests."""

    task_id: str
    evolution_id: str
    reviewer_id: str | None = None

    # Task details
    task_type: str = "evolution_review"
    priority: int = 3
    description: str = ""

    # Review data
    review_data: dict[str, Any] = field(default_factory=dict)
    decision: str | None = None
    justification: str | None = None

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    assigned_at: datetime | None = None
    completed_at: datetime | None = None


class EvolutionEngine:
    """Complete evolution engine with human-controlled framework."""

    def __init__(self):
        self.setup_metrics()

        # Evolution tracking
        self.active_evolutions: dict[str, EvolutionRequest] = {}
        self.pending_reviews: dict[str, HumanReviewTask] = {}
        self.evolution_history: list[dict[str, Any]] = []

        # Configuration
        self.auto_approval_threshold = 0.95
        self.human_review_threshold = 0.75
        self.constitutional_compliance_threshold = 0.95

        # Service endpoints
        self.ac_service_url = "http://localhost:8001"
        self.pgc_service_url = "http://localhost:8005"

        logger.info("Evolution Engine initialized")

    def setup_metrics(self):
        """Setup Prometheus metrics."""
        self.evolution_requests_total = Counter(
            "evolution_requests_total",
            "Total evolution requests",
            ["evolution_type", "status"],
        )

        self.human_reviews_total = Counter(
            "evolution_human_reviews_total", "Total human reviews", ["decision"]
        )

        self.evolution_processing_time = Histogram(
            "evolution_processing_time_seconds",
            "Time to process evolution requests",
            ["evolution_type"],
        )

        self.active_evolutions_gauge = Gauge(
            "evolution_active_requests", "Number of active evolution requests"
        )

        self.constitutional_compliance_gauge = Gauge(
            "evolution_constitutional_compliance",
            "Constitutional compliance score for evolutions",
            ["evolution_id"],
        )

    async def submit_evolution_request(self, request: EvolutionRequest) -> str:
        """Submit a new evolution request."""
        start_time = time.time()

        try:
            # Validate request
            await self.validate_evolution_request(request)

            # Store request
            self.active_evolutions[request.evolution_id] = request
            self.active_evolutions_gauge.set(len(self.active_evolutions))

            # Record metrics
            self.evolution_requests_total.labels(
                evolution_type=request.evolution_type.value, status="submitted"
            ).inc()

            # Start evaluation process
            asyncio.create_task(self.process_evolution_request(request))

            logger.info(f"Evolution request submitted: {request.evolution_id}")
            return request.evolution_id

        except Exception as e:
            logger.error(f"Failed to submit evolution request: {e}")
            raise

    async def validate_evolution_request(self, request: EvolutionRequest):
        """Validate evolution request."""
        # Check required fields
        if not request.evolution_id:
            raise ValueError("Evolution ID is required")

        if not request.description:
            raise ValueError("Description is required")

        if not request.proposed_changes:
            raise ValueError("Proposed changes are required")

        # Validate target service
        if request.target_service not in [
            "auth-service",
            "ac-service",
            "integrity-service",
            "fv-service",
            "gs-service",
            "pgc-service",
            "ec-service",
        ]:
            raise ValueError(f"Invalid target service: {request.target_service}")

    async def process_evolution_request(self, request: EvolutionRequest):
        """Process an evolution request through the complete workflow."""
        start_time = time.time()

        try:
            # Step 1: Risk assessment
            await self.assess_evolution_risk(request)

            # Step 2: Constitutional compliance validation
            if request.constitutional_compliance_required:
                await self.validate_constitutional_compliance(request)

            # Step 3: Comprehensive evaluation
            evaluation = await self.evaluate_evolution_request(request)

            # Step 4: Determine approval path
            if evaluation.overall_score >= self.auto_approval_threshold:
                await self.auto_approve_evolution(request, evaluation)
            elif evaluation.overall_score >= self.human_review_threshold:
                await self.escalate_to_human_review(request, evaluation)
            else:
                await self.reject_evolution(request, evaluation)

            # Record processing time
            processing_time = time.time() - start_time
            self.evolution_processing_time.labels(
                evolution_type=request.evolution_type.value
            ).observe(processing_time)

        except Exception as e:
            logger.error(
                f"Failed to process evolution request {request.evolution_id}: {e}"
            )
            await self.handle_processing_error(request, str(e))

    async def assess_evolution_risk(self, request: EvolutionRequest):
        """Assess risk level for evolution request."""
        risk_factors = {
            "constitutional_impact": 0.0,
            "security_impact": 0.0,
            "performance_impact": 0.0,
            "service_criticality": 0.0,
        }

        # Assess constitutional impact
        if request.evolution_type == EvolutionType.CONSTITUTIONAL_UPDATE:
            risk_factors["constitutional_impact"] = 0.9
        elif "constitutional" in request.description.lower():
            risk_factors["constitutional_impact"] = 0.6

        # Assess security impact
        if request.evolution_type == EvolutionType.SECURITY_ENHANCEMENT:
            risk_factors["security_impact"] = 0.7
        elif "security" in request.description.lower():
            risk_factors["security_impact"] = 0.5

        # Assess service criticality
        critical_services = ["ac-service", "pgc-service", "auth-service"]
        if request.target_service in critical_services:
            risk_factors["service_criticality"] = 0.8

        # Calculate overall risk
        overall_risk = max(risk_factors.values())

        if overall_risk >= 0.8:
            request.risk_level = RiskLevel.CRITICAL
        elif overall_risk >= 0.6:
            request.risk_level = RiskLevel.HIGH
        elif overall_risk >= 0.4:
            request.risk_level = RiskLevel.MEDIUM
        else:
            request.risk_level = RiskLevel.LOW

        request.impact_assessment = risk_factors

        logger.info(
            f"Risk assessment for {request.evolution_id}: {request.risk_level.value}"
        )

    async def validate_constitutional_compliance(self, request: EvolutionRequest):
        """Validate constitutional compliance for evolution request."""
        try:
            async with aiohttp.ClientSession() as session:
                # Call AC Service for constitutional validation
                validation_url = f"{self.ac_service_url}/api/v1/constitutional/validate"

                validation_data = {
                    "evolution_request": {
                        "evolution_id": request.evolution_id,
                        "evolution_type": request.evolution_type.value,
                        "description": request.description,
                        "proposed_changes": request.proposed_changes,
                        "target_service": request.target_service,
                    },
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                    "validation_level": "comprehensive",
                }

                async with session.post(
                    validation_url, json=validation_data, timeout=30
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        request.constitutional_validation_score = result.get(
                            "compliance_score", 0.0
                        )

                        # Update metrics
                        self.constitutional_compliance_gauge.labels(
                            evolution_id=request.evolution_id
                        ).set(request.constitutional_validation_score)

                        logger.info(
                            f"Constitutional validation for {request.evolution_id}: "
                            f"{request.constitutional_validation_score:.2%}"
                        )
                    else:
                        logger.warning(
                            f"Constitutional validation failed for {request.evolution_id}: "
                            f"HTTP {response.status}"
                        )
                        request.constitutional_validation_score = 0.0

        except Exception as e:
            logger.error(
                f"Constitutional validation error for {request.evolution_id}: {e}"
            )
            request.constitutional_validation_score = 0.0

    async def evaluate_evolution_request(
        self, request: EvolutionRequest
    ) -> EvolutionEvaluation:
        """Comprehensive evaluation of evolution request."""
        evaluation_id = str(uuid.uuid4())

        # Constitutional compliance score
        constitutional_score = request.constitutional_validation_score or 0.0

        # Security impact score (inverse of risk)
        security_score = 1.0 - (request.impact_assessment.get("security_impact", 0.0))

        # Performance impact score
        performance_score = 1.0 - (
            request.impact_assessment.get("performance_impact", 0.0)
        )

        # Risk assessment score (inverse of overall risk)
        risk_score = (
            1.0 - max(request.impact_assessment.values())
            if request.impact_assessment
            else 0.5
        )

        # Calculate overall score (weighted average)
        weights = {
            "constitutional": 0.4,
            "security": 0.3,
            "performance": 0.2,
            "risk": 0.1,
        }

        overall_score = (
            constitutional_score * weights["constitutional"]
            + security_score * weights["security"]
            + performance_score * weights["performance"]
            + risk_score * weights["risk"]
        )

        # Determine recommendation
        if overall_score >= self.auto_approval_threshold:
            recommendation = "approve"
        elif overall_score >= self.human_review_threshold:
            recommendation = "review"
        else:
            recommendation = "reject"

        evaluation = EvolutionEvaluation(
            evaluation_id=evaluation_id,
            evolution_id=request.evolution_id,
            constitutional_compliance_score=constitutional_score,
            security_impact_score=security_score,
            performance_impact_score=performance_score,
            risk_assessment_score=risk_score,
            overall_score=overall_score,
            recommendation=recommendation,
            analysis_details={
                "weights_used": weights,
                "risk_factors": request.impact_assessment,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "evaluation_criteria": {
                    "auto_approval_threshold": self.auto_approval_threshold,
                    "human_review_threshold": self.human_review_threshold,
                    "constitutional_compliance_threshold": self.constitutional_compliance_threshold,
                },
            },
        )

        logger.info(
            f"Evolution evaluation for {request.evolution_id}: "
            f"score={overall_score:.3f}, recommendation={recommendation}"
        )

        return evaluation

    async def auto_approve_evolution(
        self, request: EvolutionRequest, evaluation: EvolutionEvaluation
    ):
        """Auto-approve low-risk evolution requests."""
        try:
            # Final safety check
            if (
                evaluation.constitutional_compliance_score
                < self.constitutional_compliance_threshold
            ):
                logger.warning(
                    f"Auto-approval blocked for {request.evolution_id}: "
                    f"constitutional compliance too low ({evaluation.constitutional_compliance_score:.2%})"
                )
                await self.escalate_to_human_review(request, evaluation)
                return

            # Update status
            request.status = EvolutionStatus.APPROVED

            # Record metrics
            self.evolution_requests_total.labels(
                evolution_type=request.evolution_type.value, status="auto_approved"
            ).inc()

            # Log decision
            self.evolution_history.append(
                {
                    "evolution_id": request.evolution_id,
                    "decision": "auto_approved",
                    "evaluation": evaluation,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "decision_maker": "system",
                }
            )

            logger.info(f"Evolution {request.evolution_id} auto-approved")

            # Trigger deployment (would integrate with deployment system)
            await self.trigger_evolution_deployment(request, evaluation)

        except Exception as e:
            logger.error(f"Auto-approval failed for {request.evolution_id}: {e}")
            await self.escalate_to_human_review(request, evaluation)

    async def escalate_to_human_review(
        self, request: EvolutionRequest, evaluation: EvolutionEvaluation
    ):
        """Escalate evolution request to human review."""
        try:
            # Create human review task
            task_id = str(uuid.uuid4())

            review_task = HumanReviewTask(
                task_id=task_id,
                evolution_id=request.evolution_id,
                priority=1 if request.risk_level == RiskLevel.CRITICAL else 2,
                description=f"Review {request.evolution_type.value} for {request.target_service}",
                review_data={
                    "evolution_request": request.__dict__,
                    "evaluation": evaluation.__dict__,
                    "risk_level": request.risk_level.value,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
            )

            # Store review task
            self.pending_reviews[task_id] = review_task

            # Update request status
            request.status = EvolutionStatus.HUMAN_REVIEW

            # Record metrics
            self.evolution_requests_total.labels(
                evolution_type=request.evolution_type.value, status="human_review"
            ).inc()

            logger.info(
                f"Evolution {request.evolution_id} escalated to human review "
                f"(task: {task_id}, priority: {review_task.priority})"
            )

        except Exception as e:
            logger.error(
                f"Failed to escalate {request.evolution_id} to human review: {e}"
            )

    async def reject_evolution(
        self, request: EvolutionRequest, evaluation: EvolutionEvaluation
    ):
        """Reject evolution request."""
        try:
            # Update status
            request.status = EvolutionStatus.REJECTED

            # Record metrics
            self.evolution_requests_total.labels(
                evolution_type=request.evolution_type.value, status="rejected"
            ).inc()

            # Log decision
            self.evolution_history.append(
                {
                    "evolution_id": request.evolution_id,
                    "decision": "rejected",
                    "evaluation": evaluation,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "decision_maker": "system",
                    "rejection_reason": f"Overall score {evaluation.overall_score:.3f} below threshold {self.human_review_threshold}",
                }
            )

            logger.info(f"Evolution {request.evolution_id} rejected")

        except Exception as e:
            logger.error(f"Failed to reject evolution {request.evolution_id}: {e}")

    async def trigger_evolution_deployment(
        self, request: EvolutionRequest, evaluation: EvolutionEvaluation
    ):
        """Trigger deployment of approved evolution."""
        # This would integrate with the actual deployment system
        # For now, we'll simulate the deployment

        logger.info(f"Triggering deployment for evolution {request.evolution_id}")

        # Update status
        request.status = EvolutionStatus.DEPLOYED

        # Record deployment
        self.evolution_history.append(
            {
                "evolution_id": request.evolution_id,
                "action": "deployed",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "deployment_details": {
                    "target_service": request.target_service,
                    "changes_applied": request.proposed_changes,
                },
            }
        )

    async def handle_processing_error(
        self, request: EvolutionRequest, error_message: str
    ):
        """Handle processing errors."""
        logger.error(f"Processing error for {request.evolution_id}: {error_message}")

        # Update status
        request.status = EvolutionStatus.REJECTED

        # Record error
        self.evolution_history.append(
            {
                "evolution_id": request.evolution_id,
                "action": "error",
                "error_message": error_message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

    def get_evolution_status(self, evolution_id: str) -> dict[str, Any] | None:
        """Get status of an evolution request."""
        if evolution_id in self.active_evolutions:
            request = self.active_evolutions[evolution_id]
            return {
                "evolution_id": evolution_id,
                "status": (
                    request.status.value if hasattr(request, "status") else "unknown"
                ),
                "evolution_type": request.evolution_type.value,
                "risk_level": (
                    request.risk_level.value if request.risk_level else "unknown"
                ),
                "constitutional_compliance_score": request.constitutional_validation_score,
                "timestamp": request.timestamp.isoformat(),
            }

        return None

    def get_pending_reviews(self) -> list[dict[str, Any]]:
        """Get list of pending human review tasks."""
        return [
            {
                "task_id": task.task_id,
                "evolution_id": task.evolution_id,
                "priority": task.priority,
                "description": task.description,
                "created_at": task.created_at.isoformat(),
                "assigned_at": (
                    task.assigned_at.isoformat() if task.assigned_at else None
                ),
            }
            for task in self.pending_reviews.values()
        ]


# Global evolution engine instance
evolution_engine = EvolutionEngine()
