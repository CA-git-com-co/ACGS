#!/usr/bin/env python3
"""
ACGS-1 Lite Evolution Oversight Service

Comprehensive evolution evaluation, approval workflows, and rollback mechanisms
for AI agent governance. Provides automated evaluation criteria, human review
integration, and fast rollback capabilities.

Constitutional Hash: cdd01ef066bc6cf2
"""

import asyncio
import json
import time
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import asyncpg
import httpx
import redis.asyncio as aioredis
import structlog
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Gauge, Histogram, start_http_server
from pydantic import BaseModel, Field

# Configuration
SERVICE_PORT = 8004
DATABASE_URL = os.environ.get("DATABASE_URL")
REDIS_URL = "redis://localhost:6379/3"
AUDIT_ENGINE_URL = "http://localhost:8003"
POLICY_ENGINE_URL = "http://localhost:8001"
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

# Metrics
evolution_requests_total = Counter(
    "evolution_requests_total", "Total evolution requests", ["agent_id", "decision"]
)
evaluation_duration = Histogram(
    "evaluation_duration_seconds", "Time spent evaluating agents"
)
active_reviews = Gauge("active_human_reviews", "Number of active human reviews")
rollback_operations = Counter(
    "rollback_operations_total", "Total rollback operations", ["reason"]
)
auto_approval_rate = Gauge("auto_approval_rate", "Rate of auto-approved evolutions")

# Logging
logger = structlog.get_logger()


# Models
class EvolutionStatus(str, Enum):
    PENDING = "pending"
    EVALUATING = "evaluating"
    AUTO_APPROVED = "auto_approved"
    HUMAN_REVIEW = "human_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"


class ReviewPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DecisionType(str, Enum):
    AUTO_APPROVED = "AUTO_APPROVED"
    HUMAN_APPROVED = "HUMAN_APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"


@dataclass
class EvaluationResult:
    agent_id: str
    scores: dict[str, float]
    total_score: float
    requires_human_review: bool
    risk_factors: list[str]
    recommendation: str

    def to_summary(self) -> dict[str, Any]:
        return {
            "total_score": self.total_score,
            "requires_human_review": self.requires_human_review,
            "risk_factors": self.risk_factors,
            "recommendation": self.recommendation,
            "scores": self.scores,
        }

    def get_risk_factors(self) -> list[dict[str, Any]]:
        factors = []
        for criterion, score in self.scores.items():
            if score < 0.8:
                factors.append(
                    {
                        "criterion": criterion,
                        "score": score,
                        "severity": "high" if score < 0.5 else "medium",
                    }
                )
        return factors


class EvolutionRequest(BaseModel):
    evolution_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    new_version: dict[str, Any]
    change_description: str
    requester_id: str
    priority: ReviewPriority = ReviewPriority.MEDIUM


class ReviewTask(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evolution_id: str
    agent_id: str
    priority: ReviewPriority
    status: str = "pending"
    assigned_to: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    evaluation_summary: dict[str, Any]
    diff_view: str
    risk_factors: list[dict[str, Any]]
    recommended_action: str


class EvaluationCriteria:
    """Evaluation criteria pipeline for agent evolutions."""

    def __init__(self, policy_client: httpx.AsyncClient, redis: aioredis.Redis):
        self.policy_client = policy_client
        self.redis = redis
        self.criteria = {
            "constitutional_compliance": {
                "weight": 0.4,
                "threshold": 0.99,
                "source": "policy_engine",
            },
            "performance_regression": {
                "weight": 0.3,
                "threshold": 0.05,  # Max 5% regression
                "source": "metrics",
            },
            "anomaly_score": {
                "weight": 0.2,
                "threshold": 0.1,
                "source": "anomaly_detector",
            },
            "risk_assessment": {
                "weight": 0.1,
                "threshold": 0.2,
                "source": "risk_analyzer",
            },
        }

    async def evaluate_agent(
        self, agent_id: str, new_version: dict[str, Any]
    ) -> EvaluationResult:
        """Evaluate an agent evolution against all criteria."""
        start_time = time.time()

        try:
            scores = {}
            risk_factors = []

            # Get constitutional compliance from Policy Engine
            compliance = await self.check_constitutional_compliance(new_version)
            scores["constitutional_compliance"] = compliance["score"]
            if compliance["score"] < 0.9:
                risk_factors.append("Constitutional compliance below threshold")

            # Check performance metrics
            perf_delta = await self.analyze_performance_delta(agent_id, new_version)
            scores["performance_regression"] = 1.0 - abs(perf_delta)
            if abs(perf_delta) > 0.1:
                risk_factors.append(f"Performance change: {perf_delta:.1%}")

            # Get anomaly score
            anomaly = await self.detect_anomalies(new_version)
            scores["anomaly_score"] = 1.0 - anomaly["score"]
            if anomaly["score"] > 0.2:
                risk_factors.append("Anomalous behavior patterns detected")

            # Risk assessment
            risk = await self.assess_risk(new_version)
            scores["risk_assessment"] = 1.0 - risk["score"]
            if risk["score"] > 0.3:
                risk_factors.append("High risk factors identified")

            # Calculate weighted score
            total_score = sum(
                scores[criterion] * config["weight"]
                for criterion, config in self.criteria.items()
            )

            # Determine recommendation
            if total_score >= 0.95:
                recommendation = "AUTO_APPROVE"
            elif total_score >= 0.90:
                recommendation = "FAST_TRACK_REVIEW"
            else:
                recommendation = "FULL_HUMAN_REVIEW"

            result = EvaluationResult(
                agent_id=agent_id,
                scores=scores,
                total_score=total_score,
                requires_human_review=total_score < 0.9,
                risk_factors=risk_factors,
                recommendation=recommendation,
            )

            # Cache evaluation result
            await self.redis.setex(
                f"evaluation:{agent_id}:{hash(str(new_version))}",
                300,  # 5 minutes
                json.dumps(asdict(result)),
            )

            evaluation_duration.observe(time.time() - start_time)
            return result

        except Exception as e:
            logger.exception("Evaluation failed", agent_id=agent_id, error=str(e))
            raise HTTPException(status_code=500, detail=f"Evaluation failed: {e}")

    async def check_constitutional_compliance(
        self, new_version: dict[str, Any]
    ) -> dict[str, Any]:
        """Check constitutional compliance via Policy Engine."""
        try:
            # Check cache first
            cache_key = f"compliance:{hash(str(new_version))}"
            cached = await self.redis.get(cache_key)
            if cached:
                return json.loads(cached)

            response = await self.policy_client.post(
                f"{POLICY_ENGINE_URL}/v1/evaluate",
                json={
                    "policy_id": "constitutional_principles",
                    "input": new_version,
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                },
                timeout=5.0,
            )

            if response.status_code != 200:
                logger.warning("Policy engine unavailable", status=response.status_code)
                return {"score": 0.5, "details": "Policy engine unavailable"}

            result = response.json()
            compliance_score = result.get("compliance_score", 0.5)

            compliance_result = {
                "score": compliance_score,
                "details": result.get("violations", []),
                "recommendations": result.get("recommendations", []),
            }

            # Cache for 5 minutes
            await self.redis.setex(cache_key, 300, json.dumps(compliance_result))

            return compliance_result

        except Exception as e:
            logger.exception("Constitutional compliance check failed", error=str(e))
            return {"score": 0.0, "details": f"Error: {e}"}

    async def analyze_performance_delta(
        self, agent_id: str, new_version: dict[str, Any]
    ) -> float:
        """Analyze performance change compared to current version."""
        try:
            # Simulate performance analysis
            # In production, this would integrate with metrics system
            baseline_metrics = await self.get_baseline_metrics(agent_id)

            if not baseline_metrics:
                return 0.0  # No baseline available

            # Simulate analysis of performance impact
            complexity_change = new_version.get("complexity_delta", 0.0)
            resource_change = new_version.get("resource_delta", 0.0)

            # Simple heuristic: negative values are performance improvements
            performance_delta = (complexity_change + resource_change) / 2

            return max(-0.5, min(0.5, performance_delta))  # Clamp to reasonable range

        except Exception as e:
            logger.exception(
                "Performance analysis failed", agent_id=agent_id, error=str(e)
            )
            return 0.1  # Conservative estimate

    async def get_baseline_metrics(self, agent_id: str) -> dict[str, Any] | None:
        """Get baseline performance metrics for agent."""
        try:
            cached = await self.redis.get(f"metrics:{agent_id}")
            if cached:
                return json.loads(cached)

            # In production, this would query Prometheus or metrics store
            baseline = {
                "avg_response_time": 0.1,
                "success_rate": 0.99,
                "resource_usage": 0.5,
            }

            await self.redis.setex(f"metrics:{agent_id}", 3600, json.dumps(baseline))
            return baseline

        except Exception:
            return None

    async def detect_anomalies(self, new_version: dict[str, Any]) -> dict[str, Any]:
        """Detect anomalous patterns in the new version."""
        try:
            # Simulate anomaly detection
            code_changes = new_version.get("code_changes", [])
            config_changes = new_version.get("config_changes", {})

            anomaly_score = 0.0

            # Check for suspicious patterns
            if len(code_changes) > 100:
                anomaly_score += 0.2  # Large code changes

            if any("exec" in change or "eval" in change for change in code_changes):
                anomaly_score += 0.5  # Dynamic execution

            if config_changes.get("network_access") == "unrestricted":
                anomaly_score += 0.3  # Unrestricted network access

            return {
                "score": min(1.0, anomaly_score),
                "details": f"Detected {len(code_changes)} code changes",
            }

        except Exception as e:
            logger.exception("Anomaly detection failed", error=str(e))
            return {"score": 0.0, "details": f"Error: {e}"}

    async def assess_risk(self, new_version: dict[str, Any]) -> dict[str, Any]:
        """Assess overall risk of the evolution."""
        try:
            risk_score = 0.0

            # Check risk indicators
            if new_version.get("privilege_escalation"):
                risk_score += 0.4

            if new_version.get("external_dependencies"):
                risk_score += 0.2

            if new_version.get("experimental_features"):
                risk_score += 0.3

            return {
                "score": min(1.0, risk_score),
                "details": "Risk assessment based on change patterns",
            }

        except Exception as e:
            logger.exception("Risk assessment failed", error=str(e))
            return {"score": 0.5, "details": f"Error: {e}"}


class ApprovalWorkflow:
    """Approval workflow engine for evolution decisions."""

    def __init__(
        self,
        criteria: EvaluationCriteria,
        db_pool: asyncpg.Pool,
        audit_client: httpx.AsyncClient,
    ):
        self.criteria = criteria
        self.db_pool = db_pool
        self.audit_client = audit_client

    async def process_evolution(
        self, evolution_request: EvolutionRequest
    ) -> dict[str, Any]:
        """Process an evolution request through the approval workflow."""
        try:
            # Step 1: Evaluate the agent
            evaluation = await self.criteria.evaluate_agent(
                evolution_request.agent_id, evolution_request.new_version
            )

            # Step 2: Determine approval path
            if evaluation.total_score >= 0.95:
                # Auto-approve low-risk changes
                return await self.auto_approve(evolution_request, evaluation)

            if evaluation.total_score >= 0.90:
                # Fast-track review for medium risk
                return await self.fast_track_review(evolution_request, evaluation)

            # Full human review for high risk
            return await self.human_review_required(evolution_request, evaluation)

        except Exception as e:
            logger.exception(
                "Workflow processing failed",
                evolution_id=evolution_request.evolution_id,
                error=str(e),
            )
            raise HTTPException(status_code=500, detail=f"Workflow failed: {e}")

    async def auto_approve(
        self, request: EvolutionRequest, evaluation: EvaluationResult
    ) -> dict[str, Any]:
        """Auto-approve low-risk evolutions."""
        try:
            # Additional safety check
            safety_check = await self.final_safety_validation(request)
            if not safety_check["passed"]:
                return await self.escalate_to_human(request, safety_check["reason"])

            # Update database
            await self.update_evolution_status(
                request.evolution_id,
                EvolutionStatus.AUTO_APPROVED,
                evaluation,
                DecisionType.AUTO_APPROVED,
                "SYSTEM",
            )

            # Log decision
            await self.audit_decision(
                request.evolution_id,
                decision=DecisionType.AUTO_APPROVED,
                evaluation=evaluation,
                reviewer="SYSTEM",
            )

            # Deploy agent (simulated)
            deployment_result = await self.deploy_agent(request)

            evolution_requests_total.labels(
                agent_id=request.agent_id, decision="auto_approved"
            ).inc()

            return {
                "evolution_id": request.evolution_id,
                "status": EvolutionStatus.AUTO_APPROVED,
                "decision": DecisionType.AUTO_APPROVED,
                "evaluation": evaluation.to_summary(),
                "deployment": deployment_result,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.exception(
                "Auto-approval failed", evolution_id=request.evolution_id, error=str(e)
            )
            return await self.escalate_to_human(request, f"Auto-approval error: {e}")

    async def fast_track_review(
        self, request: EvolutionRequest, evaluation: EvaluationResult
    ) -> dict[str, Any]:
        """Fast-track review for medium-risk evolutions."""
        try:
            # Create review task with high priority
            review_task = await self.create_review_task(
                request, evaluation, ReviewPriority.HIGH
            )

            await self.update_evolution_status(
                request.evolution_id,
                EvolutionStatus.HUMAN_REVIEW,
                evaluation,
                DecisionType.ESCALATED,
                None,
            )

            evolution_requests_total.labels(
                agent_id=request.agent_id, decision="fast_track_review"
            ).inc()

            active_reviews.inc()

            return {
                "evolution_id": request.evolution_id,
                "status": EvolutionStatus.HUMAN_REVIEW,
                "review_task_id": review_task["task_id"],
                "priority": ReviewPriority.HIGH,
                "evaluation": evaluation.to_summary(),
                "estimated_review_time": "5-15 minutes",
            }

        except Exception as e:
            logger.exception(
                "Fast-track review setup failed",
                evolution_id=request.evolution_id,
                error=str(e),
            )
            raise HTTPException(
                status_code=500, detail=f"Fast-track review failed: {e}"
            )

    async def human_review_required(
        self, request: EvolutionRequest, evaluation: EvaluationResult
    ) -> dict[str, Any]:
        """Require full human review for high-risk evolutions."""
        try:
            # Create review task with critical priority
            review_task = await self.create_review_task(
                request, evaluation, ReviewPriority.CRITICAL
            )

            await self.update_evolution_status(
                request.evolution_id,
                EvolutionStatus.HUMAN_REVIEW,
                evaluation,
                DecisionType.ESCALATED,
                None,
            )

            evolution_requests_total.labels(
                agent_id=request.agent_id, decision="human_review"
            ).inc()

            active_reviews.inc()

            return {
                "evolution_id": request.evolution_id,
                "status": EvolutionStatus.HUMAN_REVIEW,
                "review_task_id": review_task["task_id"],
                "priority": ReviewPriority.CRITICAL,
                "evaluation": evaluation.to_summary(),
                "estimated_review_time": "30-60 minutes",
            }

        except Exception as e:
            logger.exception(
                "Human review setup failed",
                evolution_id=request.evolution_id,
                error=str(e),
            )
            raise HTTPException(
                status_code=500, detail=f"Human review setup failed: {e}"
            )

    async def final_safety_validation(
        self, request: EvolutionRequest
    ) -> dict[str, Any]:
        """Final safety check before auto-approval."""
        try:
            # Check for high-risk patterns
            new_version = request.new_version

            risk_patterns = [
                "privilege_escalation",
                "unrestricted_network",
                "file_system_access",
                "code_execution",
            ]

            for pattern in risk_patterns:
                if new_version.get(pattern):
                    return {
                        "passed": False,
                        "reason": f"Safety concern: {pattern} detected",
                    }

            # Check constitutional compliance one more time
            compliance = await self.criteria.check_constitutional_compliance(
                new_version
            )
            if compliance["score"] < 0.99:
                return {
                    "passed": False,
                    "reason": f"Constitutional compliance: {compliance['score']:.2f}",
                }

            return {"passed": True, "reason": "All safety checks passed"}

        except Exception as e:
            return {"passed": False, "reason": f"Safety validation error: {e}"}

    async def escalate_to_human(
        self, request: EvolutionRequest, reason: str
    ) -> dict[str, Any]:
        """Escalate to human review due to safety concerns."""
        try:
            # Create evaluation with low score to force human review
            evaluation = EvaluationResult(
                agent_id=request.agent_id,
                scores={"safety_check": 0.0},
                total_score=0.0,
                requires_human_review=True,
                risk_factors=[f"Safety escalation: {reason}"],
                recommendation="FULL_HUMAN_REVIEW",
            )

            return await self.human_review_required(request, evaluation)

        except Exception as e:
            logger.exception(
                "Escalation failed", evolution_id=request.evolution_id, error=str(e)
            )
            raise HTTPException(status_code=500, detail=f"Escalation failed: {e}")

    async def deploy_agent(self, request: EvolutionRequest) -> dict[str, Any]:
        """Deploy the approved agent evolution."""
        try:
            # Simulate deployment
            deployment_id = str(uuid.uuid4())

            # In production, this would integrate with deployment system
            deployment_result = {
                "deployment_id": deployment_id,
                "status": "success",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": request.agent_id,
                "version": request.new_version.get("version", "unknown"),
            }

            await self.update_evolution_status(
                request.evolution_id, EvolutionStatus.DEPLOYED, None, None, None
            )

            return deployment_result

        except Exception as e:
            logger.exception(
                "Deployment failed", evolution_id=request.evolution_id, error=str(e)
            )
            return {
                "deployment_id": None,
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

    async def update_evolution_status(
        self,
        evolution_id: str,
        status: EvolutionStatus,
        evaluation: EvaluationResult | None,
        decision: DecisionType | None,
        reviewer_id: str | None,
    ):
        """Update evolution status in database."""
        try:
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    UPDATE agent_evolutions
                    SET status = $1, evaluation_scores = $2, total_score = $3,
                        decision = $4, reviewer_id = $5, decision_timestamp = NOW()
                    WHERE evolution_id = $6
                """,
                    status.value,
                    json.dumps(evaluation.scores) if evaluation else None,
                    evaluation.total_score if evaluation else None,
                    decision.value if decision else None,
                    reviewer_id,
                    evolution_id,
                )
        except Exception as e:
            logger.exception(
                "Database update failed", evolution_id=evolution_id, error=str(e)
            )

    async def audit_decision(
        self,
        evolution_id: str,
        decision: DecisionType,
        evaluation: EvaluationResult,
        reviewer: str,
    ):
        """Log decision to audit engine."""
        try:
            audit_event = {
                "event_type": "evolution_decision",
                "evolution_id": evolution_id,
                "decision": decision.value,
                "evaluation_scores": evaluation.scores,
                "total_score": evaluation.total_score,
                "reviewer": reviewer,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            await self.audit_client.post(
                f"{AUDIT_ENGINE_URL}/api/v1/audit/events", json=audit_event, timeout=5.0
            )

        except Exception as e:
            logger.warning(
                "Audit logging failed", evolution_id=evolution_id, error=str(e)
            )


class HumanReviewInterface:
    """Interface for human reviewers."""

    def __init__(self, db_pool: asyncpg.Pool):
        self.db_pool = db_pool

    async def create_review_task(
        self,
        evolution_request: EvolutionRequest,
        evaluation: EvaluationResult,
        priority: ReviewPriority,
    ) -> dict[str, Any]:
        """Create a review task for human reviewers."""
        try:
            task = ReviewTask(
                evolution_id=evolution_request.evolution_id,
                agent_id=evolution_request.agent_id,
                priority=priority,
                evaluation_summary=evaluation.to_summary(),
                diff_view=await self.generate_diff_view(evolution_request),
                risk_factors=evaluation.get_risk_factors(),
                recommended_action=evaluation.recommendation,
            )

            # Store in database
            async with self.db_pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO review_tasks (
                        task_id, evolution_id, priority, status, created_at
                    ) VALUES ($1, $2, $3, $4, $5)
                """,
                    task.task_id,
                    task.evolution_id,
                    task.priority.value,
                    task.status,
                    task.created_at,
                )

            # Notify reviewers (simulated)
            await self.notify_reviewers(task)

            return {
                "task_id": task.task_id,
                "priority": task.priority.value,
                "created_at": task.created_at.isoformat(),
            }

        except Exception as e:
            logger.exception(
                "Review task creation failed",
                evolution_id=evolution_request.evolution_id,
                error=str(e),
            )
            raise HTTPException(
                status_code=500, detail=f"Review task creation failed: {e}"
            )

    async def generate_diff_view(self, evolution_request: EvolutionRequest) -> str:
        """Generate a human-readable diff view of changes."""
        try:
            changes = evolution_request.new_version.get("changes", {})
            diff_lines = []

            for section, modifications in changes.items():
                diff_lines.append(f"=== {section} ===")
                if isinstance(modifications, list):
                    diff_lines.extend(f"+ {mod}" for mod in modifications)
                elif isinstance(modifications, dict):
                    for key, value in modifications.items():
                        diff_lines.append(f"  {key}: {value}")

            return "\n".join(diff_lines)

        except Exception:
            return "Diff generation failed"

    async def notify_reviewers(self, task: ReviewTask):
        """Notify human reviewers about new task."""
        try:
            # In production, this would send notifications via email, Slack, etc.
            logger.info(
                "Review task created",
                task_id=task.task_id,
                priority=task.priority.value,
                agent_id=task.agent_id,
            )
        except Exception as e:
            logger.warning(
                "Reviewer notification failed", task_id=task.task_id, error=str(e)
            )


class RollbackManager:
    """Manages agent rollbacks."""

    def __init__(self, db_pool: asyncpg.Pool, audit_client: httpx.AsyncClient):
        self.db_pool = db_pool
        self.audit_client = audit_client

    async def rollback_agent(self, agent_id: str, reason: str) -> dict[str, Any]:
        """Rollback an agent to its previous version."""
        try:
            # Get current and previous versions
            current = await self.get_current_version(agent_id)
            previous = await self.get_previous_version(agent_id)

            if not previous:
                raise ValueError("No previous version available for rollback")

            # Validate previous version is safe
            validation = await self.validate_version(previous)
            if not validation["safe"]:
                raise ValueError(
                    f"Previous version failed safety validation: {validation['reason']}"
                )

            # Execute rollback
            rollback_id = str(uuid.uuid4())
            await self.deploy_version(agent_id, previous, rollback_id)

            # Log rollback
            await self.audit_rollback(
                agent_id=agent_id,
                from_version=current["version"] if current else "unknown",
                to_version=previous["version"],
                reason=reason,
                rollback_id=rollback_id,
            )

            rollback_operations.labels(reason=reason).inc()

            return {
                "rollback_id": rollback_id,
                "status": "success",
                "agent_id": agent_id,
                "from_version": current["version"] if current else "unknown",
                "to_version": previous["version"],
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.exception("Rollback failed", agent_id=agent_id, error=str(e))
            rollback_operations.labels(reason="failed").inc()
            raise HTTPException(status_code=500, detail=f"Rollback failed: {e}")

    async def get_current_version(self, agent_id: str) -> dict[str, Any] | None:
        """Get the current deployed version of an agent."""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT version, evaluation_scores, created_at
                    FROM agent_evolutions
                    WHERE agent_id = $1 AND status = 'deployed'
                    ORDER BY created_at DESC
                    LIMIT 1
                """,
                    agent_id,
                )

                if row:
                    return {
                        "version": row["version"],
                        "evaluation_scores": row["evaluation_scores"],
                        "created_at": row["created_at"],
                    }
                return None

        except Exception as e:
            logger.exception(
                "Failed to get current version", agent_id=agent_id, error=str(e)
            )
            return None

    async def get_previous_version(self, agent_id: str) -> dict[str, Any] | None:
        """Get the previous deployed version of an agent."""
        try:
            async with self.db_pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT version, evaluation_scores, created_at
                    FROM agent_evolutions
                    WHERE agent_id = $1 AND status = 'deployed'
                    ORDER BY created_at DESC
                    LIMIT 1 OFFSET 1
                """,
                    agent_id,
                )

                if row:
                    return {
                        "version": row["version"],
                        "evaluation_scores": row["evaluation_scores"],
                        "created_at": row["created_at"],
                    }
                return None

        except Exception as e:
            logger.exception(
                "Failed to get previous version", agent_id=agent_id, error=str(e)
            )
            return None

    async def validate_version(self, version_data: dict[str, Any]) -> dict[str, Any]:
        """Validate that a version is safe for rollback."""
        try:
            # Check evaluation scores
            scores = version_data.get("evaluation_scores", {})
            if isinstance(scores, str):
                scores = json.loads(scores)

            min_score = min(scores.values()) if scores else 0.0

            if min_score < 0.7:
                return {
                    "safe": False,
                    "reason": f"Previous version has low scores: {min_score:.2f}",
                }

            # Check age (don't rollback to very old versions)
            created_at = version_data.get("created_at")
            if created_at:
                age = datetime.now(timezone.utc) - created_at
                if age.days > 30:
                    return {
                        "safe": False,
                        "reason": f"Previous version is too old: {age.days} days",
                    }

            return {"safe": True, "reason": "Version validation passed"}

        except Exception as e:
            return {"safe": False, "reason": f"Validation error: {e}"}

    async def deploy_version(
        self, agent_id: str, version_data: dict[str, Any], rollback_id: str
    ):
        """Deploy a specific version (simulate deployment)."""
        try:
            # In production, this would integrate with deployment system
            logger.info(
                "Deploying rollback version",
                agent_id=agent_id,
                version=version_data["version"],
                rollback_id=rollback_id,
            )

            # Simulate deployment delay
            await asyncio.sleep(0.1)

        except Exception as e:
            logger.exception(
                "Version deployment failed",
                agent_id=agent_id,
                rollback_id=rollback_id,
                error=str(e),
            )
            raise

    async def audit_rollback(
        self,
        agent_id: str,
        from_version: str,
        to_version: str,
        reason: str,
        rollback_id: str,
    ):
        """Log rollback to audit engine."""
        try:
            audit_event = {
                "event_type": "agent_rollback",
                "agent_id": agent_id,
                "rollback_id": rollback_id,
                "from_version": from_version,
                "to_version": to_version,
                "reason": reason,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            await self.audit_client.post(
                f"{AUDIT_ENGINE_URL}/api/v1/audit/events", json=audit_event, timeout=5.0
            )

        except Exception as e:
            logger.warning(
                "Rollback audit logging failed", rollback_id=rollback_id, error=str(e)
            )


# FastAPI Application
app = FastAPI(
    title="ACGS-1 Lite Evolution Oversight Service",
    description="Evolution evaluation, approval workflows, and rollback mechanisms",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global components
db_pool: asyncpg.Pool | None = None
redis: aioredis.Redis | None = None
policy_client: httpx.AsyncClient | None = None
audit_client: httpx.AsyncClient | None = None
criteria: EvaluationCriteria | None = None
workflow: ApprovalWorkflow | None = None
review_interface: HumanReviewInterface | None = None
rollback_manager: RollbackManager | None = None


@app.on_event("startup")
async def startup():
    global db_pool, redis, policy_client, audit_client, criteria, workflow, review_interface, rollback_manager

    try:
        # Initialize database
        db_pool = await asyncpg.create_pool(DATABASE_URL, min_size=5, max_size=20)

        # Initialize Redis
        redis = aioredis.from_url(REDIS_URL)

        # Initialize HTTP clients
        policy_client = httpx.AsyncClient()
        audit_client = httpx.AsyncClient()

        # Initialize components
        criteria = EvaluationCriteria(policy_client, redis)
        workflow = ApprovalWorkflow(criteria, db_pool, audit_client)
        review_interface = HumanReviewInterface(db_pool)
        rollback_manager = RollbackManager(db_pool, audit_client)

        # Create database tables
        await create_tables()

        # Start metrics server
        start_http_server(9004)

        logger.info(
            "Evolution Oversight Service started",
            constitutional_hash=CONSTITUTIONAL_HASH,
        )

    except Exception as e:
        logger.exception("Startup failed", error=str(e))
        raise


@app.on_event("shutdown")
async def shutdown():
    global db_pool, redis, policy_client, audit_client

    try:
        if policy_client:
            await policy_client.aclose()
        if audit_client:
            await audit_client.aclose()
        if redis:
            await redis.close()
        if db_pool:
            await db_pool.close()

        logger.info("Evolution Oversight Service stopped")

    except Exception as e:
        logger.exception("Shutdown failed", error=str(e))


async def create_tables():
    """Create database tables."""
    try:
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS agent_evolutions (
                    evolution_id UUID PRIMARY KEY,
                    agent_id VARCHAR(255) NOT NULL,
                    version VARCHAR(50) NOT NULL,
                    status VARCHAR(50) NOT NULL,
                    evaluation_scores JSONB,
                    total_score FLOAT,
                    decision VARCHAR(50),
                    reviewer_id VARCHAR(255),
                    decision_timestamp TIMESTAMPTZ,
                    justification TEXT,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );

                CREATE TABLE IF NOT EXISTS review_tasks (
                    task_id UUID PRIMARY KEY,
                    evolution_id UUID REFERENCES agent_evolutions(evolution_id),
                    priority INTEGER,
                    status VARCHAR(50),
                    assigned_to VARCHAR(255),
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );

                CREATE INDEX IF NOT EXISTS idx_evolutions_agent_id ON agent_evolutions(agent_id);
                CREATE INDEX IF NOT EXISTS idx_evolutions_status ON agent_evolutions(status);
                CREATE INDEX IF NOT EXISTS idx_reviews_status ON review_tasks(status);
            """
            )

        logger.info("Database tables created successfully")

    except Exception as e:
        logger.exception("Table creation failed", error=str(e))
        raise


# API Endpoints


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "evolution-oversight-service",
        "version": "1.0.0",
        "constitutional_hash": CONSTITUTIONAL_HASH,
        "active_reviews": int(active_reviews._value.get()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/api/v1/evolution/submit")
async def submit_evolution(
    request: EvolutionRequest, background_tasks: BackgroundTasks
):
    """Submit an agent evolution for evaluation and approval."""
    try:
        # Store evolution request
        async with db_pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO agent_evolutions (
                    evolution_id, agent_id, version, status, created_at
                ) VALUES ($1, $2, $3, $4, NOW())
            """,
                request.evolution_id,
                request.agent_id,
                request.new_version.get("version", "unknown"),
                EvolutionStatus.PENDING.value,
            )

        # Process in workflow
        background_tasks.add_task(process_evolution_async, request)

        return {
            "evolution_id": request.evolution_id,
            "status": EvolutionStatus.PENDING,
            "message": "Evolution submitted for evaluation",
            "estimated_processing_time": "1-5 minutes",
        }

    except Exception as e:
        logger.exception(
            "Evolution submission failed",
            evolution_id=request.evolution_id,
            error=str(e),
        )
        raise HTTPException(status_code=500, detail=f"Submission failed: {e}")


async def process_evolution_async(request: EvolutionRequest):
    """Process evolution request asynchronously."""
    try:
        result = await workflow.process_evolution(request)
        logger.info(
            "Evolution processed",
            evolution_id=request.evolution_id,
            status=result.get("status"),
        )

        # Update auto-approval rate metric
        if result.get("decision") == DecisionType.AUTO_APPROVED:
            current_rate = auto_approval_rate._value.get()
            auto_approval_rate.set(current_rate * 0.9 + 0.1)  # Moving average

    except Exception as e:
        logger.exception(
            "Async evolution processing failed",
            evolution_id=request.evolution_id,
            error=str(e),
        )


@app.get("/api/v1/evolution/{evolution_id}")
async def get_evolution_status(evolution_id: str):
    """Get the status of an evolution request."""
    try:
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT e.*, r.task_id, r.priority as review_priority, r.status as review_status
                FROM agent_evolutions e
                LEFT JOIN review_tasks r ON e.evolution_id = r.evolution_id
                WHERE e.evolution_id = $1
            """,
                evolution_id,
            )

            if not row:
                raise HTTPException(status_code=404, detail="Evolution not found")

            result = {
                "evolution_id": row["evolution_id"],
                "agent_id": row["agent_id"],
                "version": row["version"],
                "status": row["status"],
                "total_score": row["total_score"],
                "decision": row["decision"],
                "reviewer_id": row["reviewer_id"],
                "decision_timestamp": (
                    row["decision_timestamp"].isoformat()
                    if row["decision_timestamp"]
                    else None
                ),
                "created_at": row["created_at"].isoformat(),
            }

            if row["task_id"]:
                result["review_task"] = {
                    "task_id": row["task_id"],
                    "priority": row["review_priority"],
                    "status": row["review_status"],
                }

            return result

    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            "Evolution status query failed", evolution_id=evolution_id, error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"Status query failed: {e}")


@app.post("/api/v1/evolution/{evolution_id}/rollback")
async def rollback_evolution(evolution_id: str, reason: str = "Manual rollback"):
    """Rollback an agent to its previous version."""
    try:
        # Get agent_id from evolution
        async with db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT agent_id FROM agent_evolutions WHERE evolution_id = $1
            """,
                evolution_id,
            )

            if not row:
                raise HTTPException(status_code=404, detail="Evolution not found")

            agent_id = row["agent_id"]

        # Perform rollback
        result = await rollback_manager.rollback_agent(agent_id, reason)

        return {
            "message": "Rollback completed successfully",
            "rollback_details": result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Rollback failed", evolution_id=evolution_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Rollback failed: {e}")


@app.get("/api/v1/reviews/pending")
async def get_pending_reviews():
    """Get all pending human review tasks."""
    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT r.*, e.agent_id, e.evaluation_scores, e.total_score
                FROM review_tasks r
                JOIN agent_evolutions e ON r.evolution_id = e.evolution_id
                WHERE r.status = 'pending'
                ORDER BY r.priority DESC, r.created_at ASC
            """
            )

            tasks = [
                {
                    "task_id": row["task_id"],
                    "evolution_id": row["evolution_id"],
                    "agent_id": row["agent_id"],
                    "priority": row["priority"],
                    "total_score": row["total_score"],
                    "created_at": row["created_at"].isoformat(),
                    "age_minutes": (
                        datetime.now(timezone.utc) - row["created_at"]
                    ).total_seconds()
                    / 60,
                }
                for row in rows
            ]

            return {"pending_tasks": tasks, "total_count": len(tasks)}

    except Exception as e:
        logger.exception("Pending reviews query failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")


@app.post("/api/v1/reviews/{task_id}/approve")
async def approve_review(
    task_id: str, justification: str = "Approved by human reviewer"
):
    """Approve a review task."""
    try:
        async with db_pool.acquire() as conn:
            # Get review task
            row = await conn.fetchrow(
                """
                SELECT r.evolution_id, e.agent_id
                FROM review_tasks r
                JOIN agent_evolutions e ON r.evolution_id = e.evolution_id
                WHERE r.task_id = $1 AND r.status = 'pending'
            """,
                task_id,
            )

            if not row:
                raise HTTPException(
                    status_code=404, detail="Review task not found or already processed"
                )

            evolution_id = row["evolution_id"]

            # Update review task
            await conn.execute(
                """
                UPDATE review_tasks SET status = 'approved', assigned_to = 'human_reviewer'
                WHERE task_id = $1
            """,
                task_id,
            )

            # Update evolution
            await conn.execute(
                """
                UPDATE agent_evolutions
                SET status = 'approved', decision = 'HUMAN_APPROVED',
                    reviewer_id = 'human_reviewer', justification = $2,
                    decision_timestamp = NOW()
                WHERE evolution_id = $1
            """,
                evolution_id,
                justification,
            )

        active_reviews.dec()

        evolution_requests_total.labels(
            agent_id=row["agent_id"], decision="human_approved"
        ).inc()

        return {
            "message": "Review approved successfully",
            "task_id": task_id,
            "evolution_id": evolution_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Review approval failed", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Approval failed: {e}")


@app.post("/api/v1/reviews/{task_id}/reject")
async def reject_review(
    task_id: str, justification: str = "Rejected by human reviewer"
):
    """Reject a review task."""
    try:
        async with db_pool.acquire() as conn:
            # Get review task
            row = await conn.fetchrow(
                """
                SELECT r.evolution_id, e.agent_id
                FROM review_tasks r
                JOIN agent_evolutions e ON r.evolution_id = e.evolution_id
                WHERE r.task_id = $1 AND r.status = 'pending'
            """,
                task_id,
            )

            if not row:
                raise HTTPException(
                    status_code=404, detail="Review task not found or already processed"
                )

            evolution_id = row["evolution_id"]

            # Update review task
            await conn.execute(
                """
                UPDATE review_tasks SET status = 'rejected', assigned_to = 'human_reviewer'
                WHERE task_id = $1
            """,
                task_id,
            )

            # Update evolution
            await conn.execute(
                """
                UPDATE agent_evolutions
                SET status = 'rejected', decision = 'REJECTED',
                    reviewer_id = 'human_reviewer', justification = $2,
                    decision_timestamp = NOW()
                WHERE evolution_id = $1
            """,
                evolution_id,
                justification,
            )

        active_reviews.dec()

        evolution_requests_total.labels(
            agent_id=row["agent_id"], decision="rejected"
        ).inc()

        return {
            "message": "Review rejected successfully",
            "task_id": task_id,
            "evolution_id": evolution_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Review rejection failed", task_id=task_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Rejection failed: {e}")


@app.get("/api/v1/agents/{agent_id}/history")
async def get_agent_evolution_history(agent_id: str, limit: int = 20):
    """Get evolution history for an agent."""
    try:
        async with db_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT evolution_id, version, status, total_score, decision,
                       decision_timestamp, created_at
                FROM agent_evolutions
                WHERE agent_id = $1
                ORDER BY created_at DESC
                LIMIT $2
            """,
                agent_id,
                limit,
            )

            history = [
                {
                    "evolution_id": row["evolution_id"],
                    "version": row["version"],
                    "status": row["status"],
                    "total_score": row["total_score"],
                    "decision": row["decision"],
                    "decision_timestamp": (
                        row["decision_timestamp"].isoformat()
                        if row["decision_timestamp"]
                        else None
                    ),
                    "created_at": row["created_at"].isoformat(),
                }
                for row in rows
            ]

            return {
                "agent_id": agent_id,
                "evolution_history": history,
                "total_count": len(history),
            }

    except Exception as e:
        logger.exception(
            "Evolution history query failed", agent_id=agent_id, error=str(e)
        )
        raise HTTPException(status_code=500, detail=f"History query failed: {e}")


@app.get("/metrics")
async def get_metrics():
    """Get service metrics."""
    try:
        # Calculate auto-approval rate
        async with db_pool.acquire() as conn:
            total_row = await conn.fetchrow(
                """
                SELECT COUNT(*) as total FROM agent_evolutions
                WHERE created_at > NOW() - INTERVAL '24 hours'
            """
            )

            auto_row = await conn.fetchrow(
                """
                SELECT COUNT(*) as auto_approved FROM agent_evolutions
                WHERE created_at > NOW() - INTERVAL '24 hours'
                AND decision = 'AUTO_APPROVED'
            """
            )

            pending_row = await conn.fetchrow(
                """
                SELECT COUNT(*) as pending FROM review_tasks
                WHERE status = 'pending'
            """
            )

            total_evolutions = total_row["total"] if total_row else 0
            auto_approved = auto_row["auto_approved"] if auto_row else 0
            pending_reviews = pending_row["pending"] if pending_row else 0

            approval_rate = (
                (auto_approved / total_evolutions * 100) if total_evolutions > 0 else 0
            )

        return {
            "service": "evolution-oversight",
            "constitutional_hash": CONSTITUTIONAL_HASH,
            "metrics": {
                "total_evolutions_24h": total_evolutions,
                "auto_approved_24h": auto_approved,
                "auto_approval_rate_pct": round(approval_rate, 1),
                "pending_reviews": pending_reviews,
                "active_reviews": int(active_reviews._value.get()),
            },
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except Exception as e:
        logger.exception("Metrics query failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Metrics query failed: {e}")


if __name__ == "__main__":
    # Legacy service - redirects to unified service
    import os
    import sys

    # Option to auto-redirect to unified service
    if "--redirect" in sys.argv:
        os.system("python unified_main.py")

    # uvicorn.run(
    #     "main:app", host="0.0.0.0", port=SERVICE_PORT, log_level="info", reload=False
    # )
