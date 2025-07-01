"""
Agent HITL Service Layer

Business logic for Human-in-the-Loop agent oversight operations.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, desc, func

from ..models.hitl_models import (
    HITLDecision,
    AgentConfidenceProfile,
    HumanReviewTask,
    HITLFeedback,
    DecisionStatus,
    ReviewTaskStatus,
)
from ..schemas.hitl_schemas import (
    HITLDecisionResponse,
    AgentConfidenceProfileResponse,
    AgentConfidenceUpdate,
    HumanReviewTaskResponse,
    HumanReviewSubmission,
    HITLFeedbackCreate,
    HITLDashboardData,
    HITLMetrics,
    HITLSearchRequest,
)

logger = logging.getLogger(__name__)


class HITLService:
    """Service class for HITL operations."""

    def __init__(self):
        self.constitutional_hash = "cdd01ef066bc6cf2"

    async def get_decision(
        self, db: AsyncSession, decision_id: str
    ) -> Optional[HITLDecisionResponse]:
        """Get a specific HITL decision."""
        try:
            result = await db.execute(
                select(HITLDecision).where(HITLDecision.decision_id == decision_id)
            )
            decision = result.scalar_one_or_none()

            if decision:
                return HITLDecisionResponse.from_orm(decision)
            return None

        except Exception as e:
            logger.error(f"Failed to get decision {decision_id}: {e}")
            raise

    async def get_agent_confidence_profile(
        self, db: AsyncSession, agent_id: str
    ) -> Optional[AgentConfidenceProfileResponse]:
        """Get agent confidence profile."""
        try:
            result = await db.execute(
                select(AgentConfidenceProfile).where(
                    AgentConfidenceProfile.agent_id == agent_id
                )
            )
            profile = result.scalar_one_or_none()

            if profile:
                return AgentConfidenceProfileResponse.from_orm(profile)
            return None

        except Exception as e:
            logger.error(f"Failed to get agent confidence profile {agent_id}: {e}")
            raise

    async def update_agent_confidence(
        self, db: AsyncSession, agent_id: str, confidence_update: AgentConfidenceUpdate
    ) -> Optional[AgentConfidenceProfile]:
        """Update agent confidence based on operation outcome."""
        try:
            # Get or create confidence profile
            result = await db.execute(
                select(AgentConfidenceProfile).where(
                    AgentConfidenceProfile.agent_id == agent_id
                )
            )
            profile = result.scalar_one_or_none()

            if not profile:
                # Create new profile
                profile = AgentConfidenceProfile(
                    agent_id=agent_id,
                    overall_confidence_score=0.5,
                    operation_type_scores={},
                    risk_level_scores={},
                    learning_rate=0.1,
                    adaptation_rate=0.05,
                    constitutional_compliance_score=0.8,
                )
                db.add(profile)

            # Update confidence
            profile.update_confidence(
                operation_type=confidence_update.operation_type,
                success=confidence_update.success,
                learning_rate=confidence_update.learning_rate,
            )

            # Update constitutional compliance if provided
            if confidence_update.constitutional_compliant is not None:
                if confidence_update.constitutional_compliant:
                    profile.constitutional_compliance_score = min(
                        1.0, profile.constitutional_compliance_score + 0.01
                    )
                else:
                    profile.constitutional_compliance_score = max(
                        0.0, profile.constitutional_compliance_score - 0.05
                    )
                    profile.constitutional_violations += 1

            await db.commit()
            return profile

        except Exception as e:
            logger.error(f"Failed to update agent confidence {agent_id}: {e}")
            await db.rollback()
            raise

    async def get_pending_review_tasks(
        self,
        db: AsyncSession,
        limit: int = 50,
        assigned_to_me: bool = False,
        priority_min: int = 1,
    ) -> List[HumanReviewTaskResponse]:
        """Get pending human review tasks."""
        try:
            query = (
                select(HumanReviewTask)
                .where(
                    and_(
                        HumanReviewTask.status == ReviewTaskStatus.ASSIGNED.value,
                        HumanReviewTask.priority >= priority_min,
                    )
                )
                .order_by(
                    HumanReviewTask.priority.asc(), HumanReviewTask.created_at.asc()
                )
                .limit(limit)
            )

            result = await db.execute(query)
            tasks = result.scalars().all()

            return [HumanReviewTaskResponse.from_orm(task) for task in tasks]

        except Exception as e:
            logger.error(f"Failed to get pending review tasks: {e}")
            raise

    async def submit_human_review(
        self, db: AsyncSession, task_id: str, review_submission: HumanReviewSubmission
    ) -> Optional[HumanReviewTask]:
        """Submit human review for a task."""
        try:
            # Get the task
            result = await db.execute(
                select(HumanReviewTask).where(HumanReviewTask.task_id == task_id)
            )
            task = result.scalar_one_or_none()

            if not task:
                return None

            # Update task with review
            task.status = ReviewTaskStatus.COMPLETED.value
            task.review_completed_at = datetime.now(timezone.utc)
            task.review_decision = review_submission.review_decision
            task.review_reasoning = review_submission.review_reasoning
            task.review_confidence = review_submission.review_confidence

            # Update the associated decision
            result = await db.execute(
                select(HITLDecision).where(HITLDecision.id == task.decision_id)
            )
            decision = result.scalar_one_or_none()

            if decision:
                if review_submission.review_decision == "approve":
                    decision.decision_status = DecisionStatus.APPROVED.value
                elif review_submission.review_decision == "reject":
                    decision.decision_status = DecisionStatus.REJECTED.value
                elif review_submission.review_decision == "escalate":
                    decision.decision_status = DecisionStatus.ESCALATED.value

                decision.human_decision_at = datetime.now(timezone.utc)
                decision.human_feedback = review_submission.review_reasoning
                decision.completed_at = datetime.now(timezone.utc)

            await db.commit()
            return task

        except Exception as e:
            logger.error(f"Failed to submit human review for task {task_id}: {e}")
            await db.rollback()
            raise

    async def submit_feedback(
        self, db: AsyncSession, feedback: HITLFeedbackCreate
    ) -> HITLFeedback:
        """Submit feedback on HITL decisions."""
        try:
            # Create feedback record
            feedback_record = HITLFeedback(
                feedback_id=f"fb_{int(datetime.now().timestamp() * 1000)}",
                decision_id=feedback.decision_id,
                feedback_type=feedback.feedback_type,
                feedback_source=feedback.feedback_source,
                original_confidence=0.0,  # Would be populated from decision
                suggested_confidence=feedback.suggested_confidence,
                human_agreed_with_decision=feedback.human_agreed_with_decision,
                human_reasoning=feedback.human_reasoning,
                human_confidence_rating=feedback.human_confidence_rating,
                actual_outcome=feedback.actual_outcome,
                outcome_details=feedback.outcome_details,
                constitutional_compliance_actual=feedback.constitutional_compliance_actual,
                learning_weight=feedback.learning_weight,
            )

            db.add(feedback_record)
            await db.commit()

            return feedback_record

        except Exception as e:
            logger.error(f"Failed to submit feedback: {e}")
            await db.rollback()
            raise

    async def get_dashboard_data(self, db: AsyncSession) -> HITLDashboardData:
        """Get dashboard data for monitoring."""
        try:
            today = datetime.now(timezone.utc).date()

            # Get today's decision counts
            decisions_today_result = await db.execute(
                select(func.count(HITLDecision.id)).where(
                    func.date(HITLDecision.created_at) == today
                )
            )
            total_decisions_today = decisions_today_result.scalar() or 0

            # Get automated decisions today
            automated_today_result = await db.execute(
                select(func.count(HITLDecision.id)).where(
                    and_(
                        func.date(HITLDecision.created_at) == today,
                        HITLDecision.escalation_level.in_(
                            ["level_1_auto_approve", "level_2_auto_notify"]
                        ),
                    )
                )
            )
            automated_decisions_today = automated_today_result.scalar() or 0

            # Get human reviews today
            human_reviews_today = total_decisions_today - automated_decisions_today

            # Get escalations today
            escalations_today_result = await db.execute(
                select(func.count(HITLDecision.id)).where(
                    and_(
                        func.date(HITLDecision.created_at) == today,
                        HITLDecision.escalation_level.in_(
                            ["level_3_human_review", "level_4_council_review"]
                        ),
                    )
                )
            )
            escalations_today = escalations_today_result.scalar() or 0

            # Get pending reviews
            pending_reviews_result = await db.execute(
                select(func.count(HumanReviewTask.id)).where(
                    HumanReviewTask.status == ReviewTaskStatus.ASSIGNED.value
                )
            )
            pending_reviews = pending_reviews_result.scalar() or 0

            # Get recent decisions
            recent_decisions_result = await db.execute(
                select(HITLDecision).order_by(desc(HITLDecision.created_at)).limit(10)
            )
            recent_decisions = [
                HITLDecisionResponse.from_orm(decision)
                for decision in recent_decisions_result.scalars().all()
            ]

            # Get recent reviews
            recent_reviews_result = await db.execute(
                select(HumanReviewTask)
                .order_by(desc(HumanReviewTask.created_at))
                .limit(10)
            )
            recent_reviews = [
                HumanReviewTaskResponse.from_orm(task)
                for task in recent_reviews_result.scalars().all()
            ]

            return HITLDashboardData(
                total_decisions_today=total_decisions_today,
                automated_decisions_today=automated_decisions_today,
                human_reviews_today=human_reviews_today,
                escalations_today=escalations_today,
                average_decision_time_ms=2.5,  # Would calculate from actual data
                p99_decision_time_ms=4.8,  # Would calculate from actual data
                cache_hit_rate=0.85,  # Would get from Redis metrics
                pending_reviews=pending_reviews,
                overdue_reviews=0,  # Would calculate based on due dates
                available_reviewers=5,  # Would get from reviewer service
                active_agents=10,  # Would get from agent service
                agents_requiring_attention=2,  # Would calculate based on confidence
                average_agent_confidence=0.75,  # Would calculate from profiles
                constitutional_compliance_rate=0.98,  # Would calculate from decisions
                constitutional_violations_today=1,  # Would count violations
                recent_decisions=recent_decisions,
                recent_reviews=recent_reviews,
                active_alerts=[],  # Would populate with actual alerts
            )

        except Exception as e:
            logger.error(f"Failed to get dashboard data: {e}")
            raise

    async def get_metrics(self, db: AsyncSession) -> HITLMetrics:
        """Get HITL system metrics."""
        try:
            # This would calculate actual metrics from the database
            # For now, returning sample data

            return HITLMetrics(
                decisions_per_minute=5.2,
                automated_approval_rate=0.85,
                human_review_rate=0.12,
                escalation_rate=0.03,
                decision_latency_p50=1.8,
                decision_latency_p95=3.2,
                decision_latency_p99=4.8,
                cache_hit_rate=0.87,
                false_positive_rate=0.02,
                false_negative_rate=0.01,
                human_agreement_rate=0.94,
                confidence_accuracy=0.91,
                agent_confidence_distribution={
                    "0.0-0.2": 2,
                    "0.2-0.4": 5,
                    "0.4-0.6": 8,
                    "0.6-0.8": 15,
                    "0.8-1.0": 20,
                },
                top_performing_agents=["agent-001", "agent-005", "agent-012"],
                agents_needing_attention=["agent-003", "agent-008"],
                constitutional_compliance_rate=0.98,
                constitutional_violations_per_day=1.2,
            )

        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            raise

    async def search_decisions(
        self, db: AsyncSession, search_request: HITLSearchRequest
    ) -> List[HITLDecisionResponse]:
        """Search HITL decisions with filtering."""
        try:
            query = select(HITLDecision)

            # Apply filters
            conditions = []

            if search_request.agent_ids:
                # This would need to join with operation requests
                pass

            if search_request.escalation_levels:
                escalation_values = [
                    level.value for level in search_request.escalation_levels
                ]
                conditions.append(HITLDecision.escalation_level.in_(escalation_values))

            if search_request.decision_statuses:
                status_values = [
                    status.value for status in search_request.decision_statuses
                ]
                conditions.append(HITLDecision.decision_status.in_(status_values))

            if search_request.start_date:
                conditions.append(HITLDecision.created_at >= search_request.start_date)

            if search_request.end_date:
                conditions.append(HITLDecision.created_at <= search_request.end_date)

            if search_request.min_confidence:
                conditions.append(
                    HITLDecision.confidence_score >= search_request.min_confidence
                )

            if search_request.max_confidence:
                conditions.append(
                    HITLDecision.confidence_score <= search_request.max_confidence
                )

            if conditions:
                query = query.where(and_(*conditions))

            # Apply sorting
            if search_request.sort_order == "desc":
                query = query.order_by(
                    desc(
                        getattr(
                            HITLDecision,
                            search_request.sort_by,
                            HITLDecision.created_at,
                        )
                    )
                )
            else:
                query = query.order_by(
                    getattr(
                        HITLDecision, search_request.sort_by, HITLDecision.created_at
                    )
                )

            # Apply pagination
            offset = (search_request.page - 1) * search_request.page_size
            query = query.offset(offset).limit(search_request.page_size)

            result = await db.execute(query)
            decisions = result.scalars().all()

            return [HITLDecisionResponse.from_orm(decision) for decision in decisions]

        except Exception as e:
            logger.error(f"Failed to search decisions: {e}")
            raise
