"""
Human-in-the-Loop (HITL) Service Module

Service for managing human oversight and intervention in evolutionary computation
processes with constitutional compliance and ACGS integration.
"""

import logging
import time
from datetime import datetime, timedelta

import redis.asyncio as aioredis
from prometheus_client import Counter, Gauge, Histogram

from ..models.oversight import (
    DecisionStatus,
    HumanReviewTask,
    OversightDecision,
    OversightLevel,
    OversightRequest,
)

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class HITLService:
    """
    Human-in-the-Loop service for evolutionary computation oversight.

    Manages human oversight workflows with O(1) lookup patterns and
    sub-5ms P99 latency targets for ACGS integration.
    """

    def __init__(self, redis_client: aioredis.Redis | None = None):
        """Initialize HITL service."""
        self.redis = redis_client
        self.setup_metrics()

        # HITL tracking with O(1) lookups
        self.active_oversight_requests: dict[str, OversightRequest] = {}
        self.pending_reviews: dict[str, HumanReviewTask] = {}
        self.oversight_decisions: dict[str, OversightDecision] = {}

        # Configuration
        self.default_review_timeout_hours = 24
        self.escalation_timeout_hours = 48
        self.auto_escalation_enabled = True

        logger.info("HITLService initialized with constitutional compliance")

    def setup_metrics(self) -> None:
        """Setup Prometheus metrics."""
        self.oversight_requests_total = Counter(
            "hitl_oversight_requests_total",
            "Total oversight requests",
            ["oversight_level", "status"],
        )

        self.active_oversight_requests_gauge = Gauge(
            "hitl_active_oversight_requests", "Number of active oversight requests"
        )

        self.pending_reviews_gauge = Gauge(
            "hitl_pending_reviews", "Number of pending human reviews"
        )

        self.oversight_response_time = Histogram(
            "hitl_oversight_response_time_hours",
            "Oversight response time in hours",
            ["oversight_level"],
        )

        self.hitl_operation_duration = Histogram(
            "hitl_operation_duration_ms",
            "HITL operation duration in milliseconds",
            ["operation"],
        )

    async def create_oversight_request(
        self,
        evolution_id: str,
        oversight_level: OversightLevel,
        reason: str,
        requester_id: str,
        **kwargs,
    ) -> OversightRequest:
        """
        Create human oversight request for evolution process.

        Args:
            evolution_id: Evolution ID requiring oversight
            oversight_level: Level of oversight required
            reason: Reason for oversight request
            requester_id: ID of requesting user/service
            **kwargs: Additional oversight parameters

        Returns:
            Created oversight request
        """
        start_time = time.time()
        operation = "create_oversight_request"

        try:
            # Create oversight request
            oversight_request = OversightRequest(
                evolution_id=evolution_id,
                oversight_level=oversight_level,
                reason=reason,
                requested_by=requester_id,
                constitutional_hash=CONSTITUTIONAL_HASH,
                **kwargs,
            )

            # Set deadline based on urgency
            urgency = kwargs.get("urgency", "normal")
            deadline_hours = self._get_deadline_hours(urgency, oversight_level)
            oversight_request.deadline = datetime.utcnow() + timedelta(
                hours=deadline_hours
            )

            # Store request for O(1) lookup
            self.active_oversight_requests[oversight_request.request_id] = (
                oversight_request
            )
            self.active_oversight_requests_gauge.set(
                len(self.active_oversight_requests)
            )

            # Cache in Redis if available
            if self.redis:
                await self.redis.setex(
                    f"hitl:oversight:{oversight_request.request_id}",
                    86400,  # 24 hour TTL
                    oversight_request.json(),
                )

            # Create human review task if needed
            if oversight_level in {
                OversightLevel.HUMAN_REVIEW,
                OversightLevel.EXPERT_PANEL,
            }:
                review_task = await self._create_review_task(oversight_request)
                self.pending_reviews[review_task.task_id] = review_task
                self.pending_reviews_gauge.set(len(self.pending_reviews))

            # Record metrics
            self.oversight_requests_total.labels(
                oversight_level=oversight_level.value, status="created"
            ).inc()

            logger.info(f"Oversight request created: {oversight_request.request_id}")
            return oversight_request

        except Exception as e:
            logger.exception(f"Failed to create oversight request: {e}")
            self.oversight_requests_total.labels(
                oversight_level=oversight_level.value, status="error"
            ).inc()
            raise

        finally:
            duration = (time.time() - start_time) * 1000
            self.hitl_operation_duration.labels(operation=operation).observe(duration)

            # Ensure sub-5ms P99 latency
            if duration > 5:
                logger.warning(
                    f"Create oversight request took {duration:.2f}ms (>5ms target)"
                )

    async def get_oversight_request(self, request_id: str) -> OversightRequest | None:
        """
        Get oversight request with O(1) lookup performance.

        Args:
            request_id: Oversight request ID

        Returns:
            Oversight request if found, None otherwise
        """
        start_time = time.time()

        try:
            # O(1) lookup in memory cache
            if request_id in self.active_oversight_requests:
                return self.active_oversight_requests[request_id]

            # Fallback to Redis cache
            if self.redis:
                cached_data = await self.redis.get(f"hitl:oversight:{request_id}")
                if cached_data:
                    request = OversightRequest.parse_raw(cached_data)
                    self.active_oversight_requests[request_id] = request
                    return request

            return None

        finally:
            duration = (time.time() - start_time) * 1000
            if duration > 5:
                logger.warning(
                    f"Get oversight request took {duration:.2f}ms (>5ms target)"
                )

    async def submit_oversight_decision(
        self,
        request_id: str,
        decision_status: DecisionStatus,
        decision: str,
        reasoning: str,
        decided_by: str,
        **kwargs,
    ) -> OversightDecision:
        """
        Submit oversight decision for review request.

        Args:
            request_id: Oversight request ID
            decision_status: Decision status
            decision: Decision description
            reasoning: Decision reasoning
            decided_by: Decision maker ID
            **kwargs: Additional decision parameters

        Returns:
            Created oversight decision
        """
        start_time = time.time()
        operation = "submit_decision"

        try:
            # Get oversight request
            oversight_request = await self.get_oversight_request(request_id)
            if not oversight_request:
                raise ValueError(f"Oversight request not found: {request_id}")

            # Create oversight decision
            oversight_decision = OversightDecision(
                request_id=request_id,
                evolution_id=oversight_request.evolution_id,
                status=decision_status,
                decision=decision,
                reasoning=reasoning,
                decided_by=decided_by,
                constitutional_hash=CONSTITUTIONAL_HASH,
                **kwargs,
            )

            # Store decision
            self.oversight_decisions[oversight_decision.decision_id] = (
                oversight_decision
            )

            # Update oversight request status
            if decision_status == DecisionStatus.APPROVED:
                # Mark as completed
                pass
            elif decision_status == DecisionStatus.REJECTED:
                # Mark as rejected
                pass
            elif decision_status == DecisionStatus.ESCALATED:
                # Escalate to higher oversight level
                await self._escalate_oversight_request(oversight_request)

            # Remove from pending reviews if applicable
            review_tasks_to_remove = [
                task_id
                for task_id, task in self.pending_reviews.items()
                if task.oversight_request_id == request_id
            ]

            for task_id in review_tasks_to_remove:
                del self.pending_reviews[task_id]

            self.pending_reviews_gauge.set(len(self.pending_reviews))

            # Cache decision in Redis
            if self.redis:
                await self.redis.setex(
                    f"hitl:decision:{oversight_decision.decision_id}",
                    86400,  # 24 hour TTL
                    oversight_decision.json(),
                )

            # Record response time metrics
            if oversight_request.created_at:
                response_time_hours = (
                    datetime.utcnow() - oversight_request.created_at
                ).total_seconds() / 3600

                self.oversight_response_time.labels(
                    oversight_level=oversight_request.oversight_level.value
                ).observe(response_time_hours)

            logger.info(
                f"Oversight decision submitted: {oversight_decision.decision_id}"
            )
            return oversight_decision

        except Exception as e:
            logger.exception(f"Failed to submit oversight decision: {e}")
            raise

        finally:
            duration = (time.time() - start_time) * 1000
            self.hitl_operation_duration.labels(operation=operation).observe(duration)

    async def get_pending_reviews(
        self, reviewer_id: str | None = None
    ) -> list[HumanReviewTask]:
        """
        Get pending review tasks, optionally filtered by reviewer.

        Args:
            reviewer_id: Optional reviewer ID filter

        Returns:
            List of pending review tasks
        """
        start_time = time.time()

        try:
            pending_tasks = list(self.pending_reviews.values())

            if reviewer_id:
                pending_tasks = [
                    task for task in pending_tasks if task.assigned_to == reviewer_id
                ]

            return pending_tasks

        finally:
            duration = (time.time() - start_time) * 1000
            if duration > 5:
                logger.warning(
                    f"Get pending reviews took {duration:.2f}ms (>5ms target)"
                )

    async def assign_review_task(self, task_id: str, reviewer_id: str) -> bool:
        """
        Assign review task to a reviewer.

        Args:
            task_id: Review task ID
            reviewer_id: Reviewer ID

        Returns:
            True if assignment successful, False otherwise
        """
        start_time = time.time()

        try:
            if task_id in self.pending_reviews:
                task = self.pending_reviews[task_id]
                task.assigned_to = reviewer_id
                task.assigned_at = datetime.utcnow()
                task.status = "assigned"

                # Update in Redis
                if self.redis:
                    await self.redis.setex(f"hitl:review:{task_id}", 86400, task.json())

                logger.info(f"Review task {task_id} assigned to {reviewer_id}")
                return True

            return False

        finally:
            duration = (time.time() - start_time) * 1000
            if duration > 5:
                logger.warning(
                    f"Assign review task took {duration:.2f}ms (>5ms target)"
                )

    async def _create_review_task(
        self, oversight_request: OversightRequest
    ) -> HumanReviewTask:
        """Create human review task for oversight request."""
        review_task = HumanReviewTask(
            evolution_id=oversight_request.evolution_id,
            oversight_request_id=oversight_request.request_id,
            task_type="oversight_review",
            title=f"Evolution Oversight Review - {oversight_request.oversight_level.value}",
            description=f"Review required for evolution {oversight_request.evolution_id}: {oversight_request.reason}",
            priority=self._get_priority_from_oversight_level(
                oversight_request.oversight_level
            ),
            due_date=oversight_request.deadline,
            constitutional_hash=CONSTITUTIONAL_HASH,
        )

        # Cache in Redis
        if self.redis:
            await self.redis.setex(
                f"hitl:review:{review_task.task_id}", 86400, review_task.json()
            )

        return review_task

    async def _escalate_oversight_request(
        self, oversight_request: OversightRequest
    ) -> None:
        """Escalate oversight request to higher level."""
        # Determine escalation level
        current_level = oversight_request.oversight_level

        if current_level == OversightLevel.HUMAN_REVIEW:
            new_level = OversightLevel.EXPERT_PANEL
        elif current_level == OversightLevel.EXPERT_PANEL:
            new_level = OversightLevel.CONSTITUTIONAL_COUNCIL
        else:
            logger.warning(f"Cannot escalate beyond {current_level}")
            return

        # Create new oversight request at higher level
        await self.create_oversight_request(
            evolution_id=oversight_request.evolution_id,
            oversight_level=new_level,
            reason=f"Escalated from {current_level.value}: {oversight_request.reason}",
            requester_id="hitl_service",
            urgency="high",
        )

        logger.info(
            f"Oversight request escalated from {current_level.value} to {new_level.value}"
        )

    def _get_deadline_hours(self, urgency: str, oversight_level: OversightLevel) -> int:
        """Get deadline hours based on urgency and oversight level."""
        base_hours = {
            OversightLevel.HUMAN_REVIEW: 24,
            OversightLevel.EXPERT_PANEL: 48,
            OversightLevel.CONSTITUTIONAL_COUNCIL: 72,
        }.get(oversight_level, 24)

        urgency_multiplier = {
            "low": 2.0,
            "normal": 1.0,
            "high": 0.5,
            "critical": 0.25,
        }.get(urgency, 1.0)

        return max(1, int(base_hours * urgency_multiplier))

    def _get_priority_from_oversight_level(
        self, oversight_level: OversightLevel
    ) -> str:
        """Get task priority from oversight level."""
        return {
            OversightLevel.HUMAN_REVIEW: "medium",
            OversightLevel.EXPERT_PANEL: "high",
            OversightLevel.CONSTITUTIONAL_COUNCIL: "critical",
        }.get(oversight_level, "medium")
