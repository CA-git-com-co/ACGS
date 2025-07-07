"""
EU AI Act Human Oversight Implementation

Human oversight system implementing Article 14 of the EU AI Act requirements
for high-risk AI systems. Ensures meaningful human control over AI decisions
with proper escalation and intervention mechanisms.

Key Features:
- Multi-level human oversight framework
- Automated escalation based on decision risk and confidence
- Human reviewer qualification and training management
- Real-time intervention capabilities
- Oversight effectiveness monitoring
- Integration with constitutional AI decision pipeline
"""

# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import logging
import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from services.shared.monitoring.intelligent_alerting_system import AlertingSystem
from services.shared.security.enhanced_audit_logging import AuditLogger

logger = logging.getLogger(__name__)


class OversightLevel(Enum):
    """Levels of human oversight intensity"""

    MINIMAL = "minimal"  # Monitoring only
    STANDARD = "standard"  # Review on escalation
    ENHANCED = "enhanced"  # Pre-approval required
    CRITICAL = "critical"  # Mandatory human decision


class InterventionType(Enum):
    """Types of human intervention"""

    APPROVE = "approve"
    REJECT = "reject"
    MODIFY = "modify"
    ESCALATE = "escalate"
    DEFER = "defer"
    OVERRIDE = "override"


class ReviewerRole(Enum):
    """Human reviewer roles and capabilities"""

    CONSTITUTIONAL_EXPERT = "constitutional_expert"
    LEGAL_SPECIALIST = "legal_specialist"
    POLICY_ADVISOR = "policy_advisor"
    ETHICS_REVIEWER = "ethics_reviewer"
    TECHNICAL_REVIEWER = "technical_reviewer"
    SENIOR_SUPERVISOR = "senior_supervisor"


class EscalationTrigger(Enum):
    """Triggers for human oversight escalation"""

    LOW_CONFIDENCE = "low_confidence"
    HIGH_RISK_DECISION = "high_risk_decision"
    CONSTITUTIONAL_CONFLICT = "constitutional_conflict"
    BIAS_DETECTED = "bias_detected"
    POLICY_IMPACT = "policy_impact"
    CITIZEN_APPEAL = "citizen_appeal"
    SYSTEM_UNCERTAINTY = "system_uncertainty"
    REGULATORY_REQUIREMENT = "regulatory_requirement"


@dataclass
class HumanReviewer:
    """Human reviewer profile and capabilities"""

    reviewer_id: str
    name: str
    role: ReviewerRole
    qualifications: list[str]
    expertise_areas: list[str]
    certification_level: str
    active: bool
    availability_hours: dict[str, list[str]]  # Day of week -> hours
    max_concurrent_reviews: int
    current_review_count: int
    total_reviews_completed: int
    average_review_time_minutes: float
    accuracy_score: float
    last_training_date: datetime
    next_training_due: datetime
    contact_info: dict[str, str]


@dataclass
class EscalationRule:
    """Rule for escalating decisions to human oversight"""

    rule_id: str
    name: str
    description: str
    trigger: EscalationTrigger
    conditions: dict[str, Any]
    required_oversight_level: OversightLevel
    required_reviewer_roles: list[ReviewerRole]
    max_response_time_minutes: int
    auto_approve_timeout: bool
    priority: int
    active: bool


@dataclass
class OversightRequest:
    """Request for human oversight of AI decision"""

    request_id: str
    ai_decision_id: str
    decision_context: dict[str, Any]
    ai_recommendation: dict[str, Any]
    confidence_score: float
    risk_assessment: dict[str, Any]
    escalation_reason: EscalationTrigger
    required_oversight_level: OversightLevel
    assigned_reviewers: list[str]
    created_at: datetime
    deadline: datetime
    status: str
    priority: int
    citizen_impact: bool
    constitutional_implications: bool


@dataclass
class OversightDecision:
    """Human oversight decision"""

    decision_id: str
    request_id: str
    reviewer_id: str
    intervention_type: InterventionType
    decision_rationale: str
    modified_recommendation: Optional[dict[str, Any]]
    confidence_in_decision: float
    review_time_minutes: int
    additional_safeguards: list[str]
    follow_up_required: bool
    citizen_notification_required: bool
    decided_at: datetime


class HumanOversightManager:
    """
    EU AI Act Human Oversight Management System
    """

    def __init__(self, config: Optional[dict[str, Any]] = None):
        self.config = config or {}
        self.alerting = AlertingSystem()
        self.audit_logger = AuditLogger()

        # Configuration
        self.system_name = config.get("system_name", "ACGS")
        self.oversight_enabled = config.get("oversight_enabled", True)
        self.default_timeout_minutes = config.get(
            "default_timeout_minutes", 240
        )  # 4 hours
        self.critical_timeout_minutes = config.get(
            "critical_timeout_minutes", 60
        )  # 1 hour

        # State management
        self.reviewers = {}
        self.escalation_rules = {}
        self.oversight_requests = {}
        self.oversight_decisions = {}
        self.intervention_callbacks = {}

        # Performance tracking
        self.oversight_metrics = {
            "total_requests": 0,
            "requests_pending": 0,
            "average_response_time_minutes": 0.0,
            "intervention_rate": 0.0,
            "reviewer_workload": {},
            "escalation_patterns": {},
            "last_reset": datetime.utcnow(),
        }

        # Initialize oversight framework
        self._initialize_default_reviewers()
        self._initialize_escalation_rules()

    def _initialize_default_reviewers(self):
        """Initialize default human reviewers"""
        # Constitutional Expert
        self.reviewers["const_expert_001"] = HumanReviewer(
            reviewer_id="const_expert_001",
            name="Dr. Sarah Constitutional",
            role=ReviewerRole.CONSTITUTIONAL_EXPERT,
            qualifications=[
                "PhD Constitutional Law",
                "Bar Admission",
                "15 years experience",
            ],
            expertise_areas=[
                "constitutional_interpretation",
                "fundamental_rights",
                "democratic_governance",
            ],
            certification_level="Senior",
            active=True,
            availability_hours={
                "monday": ["09:00", "17:00"],
                "tuesday": ["09:00", "17:00"],
                "wednesday": ["09:00", "17:00"],
                "thursday": ["09:00", "17:00"],
                "friday": ["09:00", "17:00"],
            },
            max_concurrent_reviews=5,
            current_review_count=0,
            total_reviews_completed=0,
            average_review_time_minutes=45.0,
            accuracy_score=0.95,
            last_training_date=datetime.utcnow() - timedelta(days=30),
            next_training_due=datetime.utcnow() + timedelta(days=335),
            contact_info={
                "email": "sarah.constitutional@acgs.gov",
                "phone": "+1-555-0101",
            },
        )

        # Legal Specialist
        self.reviewers["legal_spec_001"] = HumanReviewer(
            reviewer_id="legal_spec_001",
            name="Alex Legal",
            role=ReviewerRole.LEGAL_SPECIALIST,
            qualifications=["JD Law", "AI Law Specialization", "10 years experience"],
            expertise_areas=["ai_regulation", "privacy_law", "administrative_law"],
            certification_level="Senior",
            active=True,
            availability_hours={
                "monday": ["08:00", "18:00"],
                "tuesday": ["08:00", "18:00"],
                "wednesday": ["08:00", "18:00"],
                "thursday": ["08:00", "18:00"],
                "friday": ["08:00", "16:00"],
            },
            max_concurrent_reviews=8,
            current_review_count=0,
            total_reviews_completed=0,
            average_review_time_minutes=35.0,
            accuracy_score=0.92,
            last_training_date=datetime.utcnow() - timedelta(days=45),
            next_training_due=datetime.utcnow() + timedelta(days=320),
            contact_info={"email": "alex.legal@acgs.gov", "phone": "+1-555-0102"},
        )

        # Ethics Reviewer
        self.reviewers["ethics_rev_001"] = HumanReviewer(
            reviewer_id="ethics_rev_001",
            name="Dr. Morgan Ethics",
            role=ReviewerRole.ETHICS_REVIEWER,
            qualifications=[
                "PhD Philosophy",
                "AI Ethics Certification",
                "8 years experience",
            ],
            expertise_areas=["ai_ethics", "bias_detection", "fairness_assessment"],
            certification_level="Senior",
            active=True,
            availability_hours={
                "monday": ["10:00", "18:00"],
                "tuesday": ["10:00", "18:00"],
                "wednesday": ["10:00", "18:00"],
                "thursday": ["10:00", "18:00"],
                "friday": ["10:00", "16:00"],
            },
            max_concurrent_reviews=6,
            current_review_count=0,
            total_reviews_completed=0,
            average_review_time_minutes=50.0,
            accuracy_score=0.88,
            last_training_date=datetime.utcnow() - timedelta(days=20),
            next_training_due=datetime.utcnow() + timedelta(days=345),
            contact_info={"email": "morgan.ethics@acgs.gov", "phone": "+1-555-0103"},
        )

    def _initialize_escalation_rules(self):
        """Initialize human oversight escalation rules"""

        # Low confidence escalation
        self.escalation_rules["low_confidence"] = EscalationRule(
            rule_id="low_confidence",
            name="Low Confidence Decision Escalation",
            description="Escalate AI decisions with low confidence scores",
            trigger=EscalationTrigger.LOW_CONFIDENCE,
            conditions={"confidence_threshold": 0.8},
            required_oversight_level=OversightLevel.STANDARD,
            required_reviewer_roles=[ReviewerRole.CONSTITUTIONAL_EXPERT],
            max_response_time_minutes=120,  # 2 hours
            auto_approve_timeout=False,
            priority=2,
            active=True,
        )

        # High risk decision escalation
        self.escalation_rules["high_risk"] = EscalationRule(
            rule_id="high_risk",
            name="High Risk Decision Escalation",
            description=(
                "Escalate decisions with significant constitutional or policy impact"
            ),
            trigger=EscalationTrigger.HIGH_RISK_DECISION,
            conditions={"risk_score_threshold": 0.7},
            required_oversight_level=OversightLevel.ENHANCED,
            required_reviewer_roles=[
                ReviewerRole.CONSTITUTIONAL_EXPERT,
                ReviewerRole.LEGAL_SPECIALIST,
            ],
            max_response_time_minutes=240,  # 4 hours
            auto_approve_timeout=False,
            priority=1,
            active=True,
        )

        # Constitutional conflict escalation
        self.escalation_rules["constitutional_conflict"] = EscalationRule(
            rule_id="constitutional_conflict",
            name="Constitutional Conflict Escalation",
            description=(
                "Escalate decisions involving constitutional principle conflicts"
            ),
            trigger=EscalationTrigger.CONSTITUTIONAL_CONFLICT,
            conditions={"conflict_detected": True},
            required_oversight_level=OversightLevel.CRITICAL,
            required_reviewer_roles=[
                ReviewerRole.CONSTITUTIONAL_EXPERT,
                ReviewerRole.SENIOR_SUPERVISOR,
            ],
            max_response_time_minutes=60,  # 1 hour
            auto_approve_timeout=False,
            priority=0,  # Highest priority
            active=True,
        )

        # Bias detection escalation
        self.escalation_rules["bias_detected"] = EscalationRule(
            rule_id="bias_detected",
            name="Bias Detection Escalation",
            description="Escalate decisions when bias is detected",
            trigger=EscalationTrigger.BIAS_DETECTED,
            conditions={"bias_score_threshold": 0.3},
            required_oversight_level=OversightLevel.ENHANCED,
            required_reviewer_roles=[
                ReviewerRole.ETHICS_REVIEWER,
                ReviewerRole.CONSTITUTIONAL_EXPERT,
            ],
            max_response_time_minutes=180,  # 3 hours
            auto_approve_timeout=False,
            priority=1,
            active=True,
        )

        # Citizen appeal escalation
        self.escalation_rules["citizen_appeal"] = EscalationRule(
            rule_id="citizen_appeal",
            name="Citizen Appeal Escalation",
            description="Escalate decisions contested by citizens",
            trigger=EscalationTrigger.CITIZEN_APPEAL,
            conditions={"appeal_submitted": True},
            required_oversight_level=OversightLevel.ENHANCED,
            required_reviewer_roles=[
                ReviewerRole.CONSTITUTIONAL_EXPERT,
                ReviewerRole.POLICY_ADVISOR,
            ],
            max_response_time_minutes=480,  # 8 hours
            auto_approve_timeout=False,
            priority=2,
            active=True,
        )

    async def evaluate_oversight_requirement(
        self, ai_decision: dict[str, Any], decision_context: dict[str, Any]
    ) -> Optional[OversightRequest]:
        """
        Evaluate whether AI decision requires human oversight

        Args:
            ai_decision: AI system decision/recommendation
            decision_context: Context and metadata about the decision

        Returns:
            OversightRequest if oversight required, None otherwise
        """
        try:
            if not self.oversight_enabled:
                return None

            # Check all escalation rules
            triggered_rules = []
            for rule_id, rule in self.escalation_rules.items():
                if rule.active and await self._evaluate_escalation_rule(
                    rule, ai_decision, decision_context
                ):
                    triggered_rules.append(rule)

            if not triggered_rules:
                return None

            # Select highest priority rule
            primary_rule = min(triggered_rules, key=lambda r: r.priority)

            # Create oversight request
            request = await self._create_oversight_request(
                ai_decision, decision_context, primary_rule
            )

            # Assign reviewers
            await self._assign_reviewers(request, primary_rule)

            # Store request
            self.oversight_requests[request.request_id] = request

            # Update metrics
            self.oversight_metrics["total_requests"] += 1
            self.oversight_metrics["requests_pending"] += 1

            # Log escalation
            await self.audit_logger.log_oversight_event(
                {
                    "event_type": "oversight_request_created",
                    "request_id": request.request_id,
                    "ai_decision_id": request.ai_decision_id,
                    "escalation_reason": request.escalation_reason.value,
                    "oversight_level": request.required_oversight_level.value,
                    "assigned_reviewers": request.assigned_reviewers,
                    "deadline": request.deadline.isoformat(),
                    "timestamp": request.created_at.isoformat(),
                }
            )

            # Send alerts
            await self._send_oversight_alerts(request)

            return request

        except Exception as e:
            logger.error(f"Oversight evaluation failed: {e}")
            raise

    async def _evaluate_escalation_rule(
        self,
        rule: EscalationRule,
        ai_decision: dict[str, Any],
        decision_context: dict[str, Any],
    ) -> bool:
        """Evaluate if escalation rule conditions are met"""
        try:
            conditions = rule.conditions

            if rule.trigger == EscalationTrigger.LOW_CONFIDENCE:
                confidence = ai_decision.get("confidence_score", 1.0)
                return confidence < conditions.get("confidence_threshold", 0.8)

            elif rule.trigger == EscalationTrigger.HIGH_RISK_DECISION:
                risk_score = decision_context.get("risk_assessment", {}).get(
                    "risk_score", 0.0
                )
                return risk_score > conditions.get("risk_score_threshold", 0.7)

            elif rule.trigger == EscalationTrigger.CONSTITUTIONAL_CONFLICT:
                return decision_context.get("constitutional_conflict_detected", False)

            elif rule.trigger == EscalationTrigger.BIAS_DETECTED:
                bias_score = decision_context.get("bias_assessment", {}).get(
                    "bias_score", 0.0
                )
                return bias_score > conditions.get("bias_score_threshold", 0.3)

            elif rule.trigger == EscalationTrigger.POLICY_IMPACT:
                return decision_context.get("policy_impact_level", "low") in [
                    "high",
                    "critical",
                ]

            elif rule.trigger == EscalationTrigger.CITIZEN_APPEAL:
                return decision_context.get("citizen_appeal_submitted", False)

            elif rule.trigger == EscalationTrigger.SYSTEM_UNCERTAINTY:
                uncertainty = ai_decision.get("uncertainty_score", 0.0)
                return uncertainty > conditions.get("uncertainty_threshold", 0.5)

            elif rule.trigger == EscalationTrigger.REGULATORY_REQUIREMENT:
                return decision_context.get("regulatory_review_required", False)

            return False

        except Exception as e:
            logger.error(f"Escalation rule evaluation failed: {e}")
            return False

    async def _create_oversight_request(
        self,
        ai_decision: dict[str, Any],
        decision_context: dict[str, Any],
        rule: EscalationRule,
    ) -> OversightRequest:
        """Create oversight request"""
        request_id = str(uuid.uuid4())
        current_time = datetime.utcnow()

        # Determine deadline based on rule and context
        if rule.trigger == EscalationTrigger.CONSTITUTIONAL_CONFLICT:
            timeout_minutes = self.critical_timeout_minutes
        else:
            timeout_minutes = rule.max_response_time_minutes

        deadline = current_time + timedelta(minutes=timeout_minutes)

        # Assess citizen impact and constitutional implications
        citizen_impact = decision_context.get("affects_citizens", False)
        constitutional_implications = decision_context.get(
            "constitutional_implications", False
        )

        request = OversightRequest(
            request_id=request_id,
            ai_decision_id=ai_decision.get("decision_id", str(uuid.uuid4())),
            decision_context=decision_context,
            ai_recommendation=ai_decision,
            confidence_score=ai_decision.get("confidence_score", 0.0),
            risk_assessment=decision_context.get("risk_assessment", {}),
            escalation_reason=rule.trigger,
            required_oversight_level=rule.required_oversight_level,
            assigned_reviewers=[],
            created_at=current_time,
            deadline=deadline,
            status="pending_assignment",
            priority=rule.priority,
            citizen_impact=citizen_impact,
            constitutional_implications=constitutional_implications,
        )

        return request

    async def _assign_reviewers(self, request: OversightRequest, rule: EscalationRule):
        """Assign appropriate reviewers to oversight request"""
        try:
            assigned_reviewers = []

            # Find available reviewers with required roles
            for required_role in rule.required_reviewer_roles:
                available_reviewer = await self._find_available_reviewer(
                    required_role, request
                )
                if available_reviewer:
                    assigned_reviewers.append(available_reviewer.reviewer_id)
                    available_reviewer.current_review_count += 1

                    # Update workload metrics
                    if (
                        available_reviewer.reviewer_id
                        not in self.oversight_metrics["reviewer_workload"]
                    ):
                        self.oversight_metrics["reviewer_workload"][
                            available_reviewer.reviewer_id
                        ] = 0
                    self.oversight_metrics["reviewer_workload"][
                        available_reviewer.reviewer_id
                    ] += 1

            request.assigned_reviewers = assigned_reviewers
            request.status = "assigned" if assigned_reviewers else "pending_assignment"

            # If no reviewers available, escalate
            if not assigned_reviewers:
                await self._escalate_assignment_failure(request, rule)

        except Exception as e:
            logger.error(f"Reviewer assignment failed: {e}")
            request.status = "assignment_failed"

    async def _find_available_reviewer(
        self, role: ReviewerRole, request: OversightRequest
    ) -> Optional[HumanReviewer]:
        """Find available reviewer with specified role"""
        try:
            eligible_reviewers = [
                reviewer
                for reviewer in self.reviewers.values()
                if (
                    reviewer.role == role
                    and reviewer.active
                    and reviewer.current_review_count < reviewer.max_concurrent_reviews
                )
            ]

            if not eligible_reviewers:
                return None

            # Check availability based on current time and schedule
            current_time = datetime.utcnow()
            current_day = current_time.strftime("%A").lower()
            current_hour = current_time.strftime("%H:%M")

            available_reviewers = []
            for reviewer in eligible_reviewers:
                if current_day in reviewer.availability_hours:
                    day_hours = reviewer.availability_hours[current_day]
                    if (
                        len(day_hours) >= 2
                        and day_hours[0] <= current_hour <= day_hours[1]
                    ):
                        available_reviewers.append(reviewer)

            if not available_reviewers:
                # If none available now, return reviewer with least workload
                return min(eligible_reviewers, key=lambda r: r.current_review_count)

            # Select reviewer with best combination of accuracy and availability
            return max(
                available_reviewers,
                key=lambda r: r.accuracy_score
                - (r.current_review_count / r.max_concurrent_reviews) * 0.2,
            )

        except Exception as e:
            logger.error(f"Reviewer search failed: {e}")
            return None

    async def _escalate_assignment_failure(
        self, request: OversightRequest, rule: EscalationRule
    ):
        """Handle reviewer assignment failure"""
        try:
            # Send critical alert
            await self.alerting.send_alert(
                f"oversight_assignment_failure_{request.request_id}",
                "Failed to assign reviewers for oversight request:"
                f" {request.escalation_reason.value}",
                severity="critical",
            )

            # Try to find any senior supervisor for emergency assignment
            emergency_reviewers = [
                reviewer
                for reviewer in self.reviewers.values()
                if (reviewer.role == ReviewerRole.SENIOR_SUPERVISOR and reviewer.active)
            ]

            if emergency_reviewers:
                emergency_reviewer = emergency_reviewers[0]
                request.assigned_reviewers = [emergency_reviewer.reviewer_id]
                request.status = "emergency_assigned"
                emergency_reviewer.current_review_count += 1

                await self.audit_logger.log_oversight_event(
                    {
                        "event_type": "emergency_reviewer_assigned",
                        "request_id": request.request_id,
                        "reviewer_id": emergency_reviewer.reviewer_id,
                        "reason": "no_regular_reviewers_available",
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

        except Exception as e:
            logger.error(f"Assignment failure escalation failed: {e}")

    async def _send_oversight_alerts(self, request: OversightRequest):
        """Send alerts for oversight request"""
        try:
            severity = {
                0: "critical",  # Constitutional conflicts
                1: "high",  # High risk decisions
                2: "medium",  # Standard escalations
                3: "low",  # Routine oversight
            }.get(request.priority, "medium")

            alert_message = (
                f"Human oversight required: {request.escalation_reason.value}\n"
                f"AI Decision: {request.ai_recommendation.get('summary', 'N/A')}\n"
                f"Confidence: {request.confidence_score:.2%}\n"
                f"Deadline: {request.deadline.strftime('%Y-%m-%d %H:%M')}\n"
                f"Assigned reviewers: {', '.join(request.assigned_reviewers)}"
            )

            await self.alerting.send_alert(
                f"oversight_request_{request.request_id}",
                alert_message,
                severity=severity,
            )

            # Send notifications to assigned reviewers
            for reviewer_id in request.assigned_reviewers:
                if reviewer_id in self.reviewers:
                    reviewer = self.reviewers[reviewer_id]
                    await self._notify_reviewer(reviewer, request)

        except Exception as e:
            logger.error(f"Oversight alert sending failed: {e}")

    async def _notify_reviewer(
        self, reviewer: HumanReviewer, request: OversightRequest
    ):
        """Notify reviewer of new oversight request"""
        try:
            # In a real implementation, this would send email/SMS/app notifications
            logger.info(
                f"Notifying reviewer {reviewer.name} of oversight request"
                f" {request.request_id}"
            )

            # Log notification
            await self.audit_logger.log_oversight_event(
                {
                    "event_type": "reviewer_notification_sent",
                    "reviewer_id": reviewer.reviewer_id,
                    "request_id": request.request_id,
                    "notification_method": "email",
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        except Exception as e:
            logger.error(f"Reviewer notification failed: {e}")

    async def submit_oversight_decision(
        self,
        request_id: str,
        reviewer_id: str,
        intervention_type: InterventionType,
        decision_rationale: str,
        modified_recommendation: Optional[dict[str, Any]] = None,
        confidence: float = 1.0,
    ) -> OversightDecision:
        """
        Submit human oversight decision

        Args:
            request_id: ID of oversight request
            reviewer_id: ID of reviewing human
            intervention_type: Type of intervention
            decision_rationale: Explanation of decision
            modified_recommendation: Modified AI recommendation if applicable
            confidence: Reviewer's confidence in decision

        Returns:
            Oversight decision record
        """
        try:
            if request_id not in self.oversight_requests:
                raise ValueError(f"Oversight request {request_id} not found")

            request = self.oversight_requests[request_id]

            if reviewer_id not in request.assigned_reviewers:
                raise ValueError(
                    f"Reviewer {reviewer_id} not assigned to request {request_id}"
                )

            if reviewer_id not in self.reviewers:
                raise ValueError(f"Reviewer {reviewer_id} not found")

            reviewer = self.reviewers[reviewer_id]
            decision_id = str(uuid.uuid4())
            review_time = (datetime.utcnow() - request.created_at).total_seconds() / 60

            # Create oversight decision
            decision = OversightDecision(
                decision_id=decision_id,
                request_id=request_id,
                reviewer_id=reviewer_id,
                intervention_type=intervention_type,
                decision_rationale=decision_rationale,
                modified_recommendation=modified_recommendation,
                confidence_in_decision=confidence,
                review_time_minutes=review_time,
                additional_safeguards=self._determine_additional_safeguards(
                    request, intervention_type
                ),
                follow_up_required=self._requires_follow_up(request, intervention_type),
                citizen_notification_required=request.citizen_impact
                and intervention_type != InterventionType.APPROVE,
                decided_at=datetime.utcnow(),
            )

            # Store decision
            self.oversight_decisions[decision_id] = decision

            # Update request status
            request.status = f"decided_{intervention_type.value}"

            # Update reviewer metrics
            reviewer.current_review_count -= 1
            reviewer.total_reviews_completed += 1

            # Update reviewer average review time
            total_reviews = reviewer.total_reviews_completed
            current_avg = reviewer.average_review_time_minutes
            reviewer.average_review_time_minutes = (
                current_avg * (total_reviews - 1) + review_time
            ) / total_reviews

            # Update system metrics
            self.oversight_metrics["requests_pending"] -= 1
            current_avg_time = self.oversight_metrics["average_response_time_minutes"]
            total_requests = self.oversight_metrics["total_requests"]
            self.oversight_metrics["average_response_time_minutes"] = (
                current_avg_time * (total_requests - 1) + review_time
            ) / total_requests

            # Calculate intervention rate
            total_decisions = len(self.oversight_decisions)
            interventions = sum(
                1
                for d in self.oversight_decisions.values()
                if d.intervention_type != InterventionType.APPROVE
            )
            self.oversight_metrics["intervention_rate"] = (
                interventions / total_decisions
            )

            # Execute intervention callback if registered
            if intervention_type in self.intervention_callbacks:
                await self.intervention_callbacks[intervention_type](decision)

            # Log decision
            await self.audit_logger.log_oversight_event(
                {
                    "event_type": "oversight_decision_submitted",
                    "decision_id": decision_id,
                    "request_id": request_id,
                    "reviewer_id": reviewer_id,
                    "intervention_type": intervention_type.value,
                    "review_time_minutes": review_time,
                    "confidence": confidence,
                    "citizen_notification_required": decision.citizen_notification_required,
                    "timestamp": decision.decided_at.isoformat(),
                }
            )

            # Send completion alerts
            await self._send_decision_alerts(decision, request)

            return decision

        except Exception as e:
            logger.error(f"Oversight decision submission failed: {e}")
            raise

    def _determine_additional_safeguards(
        self, request: OversightRequest, intervention_type: InterventionType
    ) -> list[str]:
        """Determine additional safeguards needed based on decision"""
        safeguards = []

        if request.constitutional_implications:
            safeguards.append("Constitutional compliance verification required")

        if request.citizen_impact:
            safeguards.append("Citizen notification and appeal process available")

        if intervention_type == InterventionType.OVERRIDE:
            safeguards.extend(
                [
                    "Senior supervisor approval required",
                    "Detailed justification documentation required",
                    "Follow-up review scheduled",
                ]
            )

        if request.escalation_reason == EscalationTrigger.BIAS_DETECTED:
            safeguards.append("Bias monitoring and additional fairness checks required")

        return safeguards

    def _requires_follow_up(
        self, request: OversightRequest, intervention_type: InterventionType
    ) -> bool:
        """Determine if follow-up review is required"""
        return (
            intervention_type in [InterventionType.MODIFY, InterventionType.OVERRIDE]
            or request.escalation_reason == EscalationTrigger.CONSTITUTIONAL_CONFLICT
            or request.priority == 0  # Highest priority cases
        )

    async def _send_decision_alerts(
        self, decision: OversightDecision, request: OversightRequest
    ):
        """Send alerts for oversight decision completion"""
        try:
            alert_message = (
                "Human oversight decision completed\nRequest:"
                f" {request.escalation_reason.value}\nDecision:"
                f" {decision.intervention_type.value}\nReviewer:"
                f" {self.reviewers.get(decision.reviewer_id, {}).get('name', 'Unknown')}\nReview"
                f" time: {decision.review_time_minutes:.1f} minutes"
            )

            await self.alerting.send_alert(
                f"oversight_decision_{decision.decision_id}",
                alert_message,
                severity="info",
            )

        except Exception as e:
            logger.error(f"Decision alert sending failed: {e}")

    def register_intervention_callback(
        self,
        intervention_type: InterventionType,
        callback: Callable[[OversightDecision], None],
    ):
        """Register callback for specific intervention type"""
        self.intervention_callbacks[intervention_type] = callback

    async def check_overdue_requests(self):
        """Check for overdue oversight requests and take action"""
        try:
            current_time = datetime.utcnow()
            overdue_requests = []

            for request in self.oversight_requests.values():
                if (
                    request.status.startswith("pending") or request.status == "assigned"
                ) and current_time > request.deadline:
                    overdue_requests.append(request)

            for request in overdue_requests:
                await self._handle_overdue_request(request)

            return overdue_requests

        except Exception as e:
            logger.error(f"Overdue request check failed: {e}")
            return []

    async def _handle_overdue_request(self, request: OversightRequest):
        """Handle overdue oversight request"""
        try:
            # Send critical alert
            await self.alerting.send_alert(
                f"overdue_oversight_request_{request.request_id}",
                f"Oversight request overdue: {request.escalation_reason.value}",
                severity="critical",
            )

            # Check escalation rule for auto-approval
            rule = self.escalation_rules.get(
                request.escalation_reason.value.replace("_", "")
            )

            if rule and rule.auto_approve_timeout:
                # Auto-approve with safeguards
                decision = await self._create_timeout_decision(request)
                self.oversight_decisions[decision.decision_id] = decision
                request.status = "timeout_approved"
            else:
                # Escalate to senior supervisor
                await self._escalate_overdue_request(request)

            # Log timeout handling
            await self.audit_logger.log_oversight_event(
                {
                    "event_type": "overdue_request_handled",
                    "request_id": request.request_id,
                    "action_taken": (
                        "auto_approved"
                        if rule and rule.auto_approve_timeout
                        else "escalated"
                    ),
                    "overdue_minutes": (
                        datetime.utcnow() - request.deadline
                    ).total_seconds()
                    / 60,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        except Exception as e:
            logger.error(f"Overdue request handling failed: {e}")

    async def _create_timeout_decision(
        self, request: OversightRequest
    ) -> OversightDecision:
        """Create automatic timeout decision"""
        decision_id = str(uuid.uuid4())

        return OversightDecision(
            decision_id=decision_id,
            request_id=request.request_id,
            reviewer_id="system_timeout",
            intervention_type=InterventionType.APPROVE,
            decision_rationale=(
                "Auto-approved due to timeout per escalation rule configuration"
            ),
            modified_recommendation=None,
            confidence_in_decision=0.5,
            review_time_minutes=(datetime.utcnow() - request.created_at).total_seconds()
            / 60,
            additional_safeguards=["Timeout approval - additional monitoring required"],
            follow_up_required=True,
            citizen_notification_required=request.citizen_impact,
            decided_at=datetime.utcnow(),
        )

    async def _escalate_overdue_request(self, request: OversightRequest):
        """Escalate overdue request to senior supervisor"""
        try:
            # Find available senior supervisor
            senior_supervisors = [
                reviewer
                for reviewer in self.reviewers.values()
                if reviewer.role == ReviewerRole.SENIOR_SUPERVISOR and reviewer.active
            ]

            if senior_supervisors:
                supervisor = senior_supervisors[0]
                request.assigned_reviewers = [supervisor.reviewer_id]
                request.status = "escalated_overdue"
                request.deadline = datetime.utcnow() + timedelta(
                    hours=1
                )  # New urgent deadline
                supervisor.current_review_count += 1

                await self._notify_reviewer(supervisor, request)

        except Exception as e:
            logger.error(f"Overdue request escalation failed: {e}")

    def get_oversight_metrics(self) -> dict[str, Any]:
        """Get human oversight performance metrics"""
        current_time = datetime.utcnow()

        # Calculate reviewer performance
        reviewer_performance = {}
        for reviewer_id, reviewer in self.reviewers.items():
            reviewer_performance[reviewer_id] = {
                "name": reviewer.name,
                "role": reviewer.role.value,
                "total_reviews": reviewer.total_reviews_completed,
                "current_workload": reviewer.current_review_count,
                "average_review_time": reviewer.average_review_time_minutes,
                "accuracy_score": reviewer.accuracy_score,
                "utilization_rate": (
                    reviewer.current_review_count / reviewer.max_concurrent_reviews
                ),
            }

        # Count pending requests
        pending_requests = sum(
            1
            for request in self.oversight_requests.values()
            if request.status in ["pending_assignment", "assigned"]
        )

        # Count overdue requests
        overdue_requests = sum(
            1
            for request in self.oversight_requests.values()
            if request.status in ["pending_assignment", "assigned"]
            and current_time > request.deadline
        )

        return {
            "total_requests": self.oversight_metrics["total_requests"],
            "pending_requests": pending_requests,
            "overdue_requests": overdue_requests,
            "average_response_time_minutes": self.oversight_metrics[
                "average_response_time_minutes"
            ],
            "intervention_rate": self.oversight_metrics["intervention_rate"],
            "reviewer_performance": reviewer_performance,
            "active_reviewers": sum(1 for r in self.reviewers.values() if r.active),
            "oversight_enabled": self.oversight_enabled,
            "escalation_rules_active": sum(
                1 for r in self.escalation_rules.values() if r.active
            ),
        }

    def get_pending_requests(
        self, reviewer_id: Optional[str] = None
    ) -> list[OversightRequest]:
        """Get pending oversight requests, optionally filtered by reviewer"""
        pending_requests = [
            request
            for request in self.oversight_requests.values()
            if request.status in ["pending_assignment", "assigned"]
        ]

        if reviewer_id:
            pending_requests = [
                request
                for request in pending_requests
                if reviewer_id in request.assigned_reviewers
            ]

        # Sort by priority and deadline
        pending_requests.sort(key=lambda r: (r.priority, r.deadline))

        return pending_requests

    async def update_reviewer_status(self, reviewer_id: str, updates: dict[str, Any]):
        """Update reviewer status and availability"""
        try:
            if reviewer_id not in self.reviewers:
                raise ValueError(f"Reviewer {reviewer_id} not found")

            reviewer = self.reviewers[reviewer_id]

            # Update allowed fields
            if "active" in updates:
                reviewer.active = updates["active"]

            if "availability_hours" in updates:
                reviewer.availability_hours = updates["availability_hours"]

            if "max_concurrent_reviews" in updates:
                reviewer.max_concurrent_reviews = updates["max_concurrent_reviews"]

            # Log update
            await self.audit_logger.log_oversight_event(
                {
                    "event_type": "reviewer_status_updated",
                    "reviewer_id": reviewer_id,
                    "updates": list(updates.keys()),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

        except Exception as e:
            logger.error(f"Reviewer status update failed: {e}")
            raise


# Example usage
async def example_usage():
    """Example of using the human oversight manager"""
    # Initialize oversight manager
    oversight_manager = HumanOversightManager(
        {
            "system_name": "ACGS",
            "oversight_enabled": True,
            "default_timeout_minutes": 240,
        }
    )

    # Mock AI decision that requires oversight
    ai_decision = {
        "decision_id": "ai_decision_001",
        "recommendation": "Approve constitutional amendment proposal",
        "confidence_score": 0.7,  # Low confidence triggers oversight
        "reasoning": "Based on constitutional precedent analysis",
        "supporting_evidence": ["Article 5 precedents", "Historical amendments"],
    }

    decision_context = {
        "constitutional_implications": True,
        "affects_citizens": True,
        "policy_impact_level": "high",
        "risk_assessment": {"risk_score": 0.8},
    }

    # Evaluate oversight requirement
    oversight_request = await oversight_manager.evaluate_oversight_requirement(
        ai_decision, decision_context
    )

    if oversight_request:
        logger.info(f"Oversight required: {oversight_request.escalation_reason.value}")
        logger.info(f"Assigned reviewers: {oversight_request.assigned_reviewers}")

        # Simulate human decision
        if oversight_request.assigned_reviewers:
            reviewer_id = oversight_request.assigned_reviewers[0]

            decision = await oversight_manager.submit_oversight_decision(
                oversight_request.request_id,
                reviewer_id,
                InterventionType.MODIFY,
                "Recommendation approved with additional safeguards for citizen"
                " consultation",
                modified_recommendation={
                    "recommendation": (
                        "Approve with mandatory public consultation period"
                    ),
                    "additional_requirements": [
                        "30-day public comment period",
                        "stakeholder hearings",
                    ],
                },
                confidence=0.9,
            )

            logger.info(f"Human oversight decision: {decision.intervention_type.value}")

    # Get metrics
    metrics = oversight_manager.get_oversight_metrics()
    logger.info(f"Oversight metrics: {metrics}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
