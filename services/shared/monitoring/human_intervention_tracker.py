"""
Human Intervention Rate Tracker

Comprehensive tracking system for monitoring human intervention rates, patterns,
and effectiveness in the ACGS constitutional AI system. Provides detailed analytics
on when, why, and how often humans intervene in AI decision-making processes.

Key Features:
- Real-time intervention rate monitoring
- Pattern analysis and trend detection
- Intervention effectiveness measurement
- Reviewer performance analytics
- Escalation tracking and management
- Constitutional compliance correlation
"""

# Constitutional Hash: cdd01ef066bc6cf2

import asyncio
import logging
import operator
import statistics
import uuid
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

import numpy as np

from services.shared.monitoring.intelligent_alerting_system import AlertingSystem
from services.shared.security.enhanced_audit_logging import AuditLogger

logger = logging.getLogger(__name__)


class InterventionReason(Enum):
    """Reasons for human intervention"""

    LOW_CONFIDENCE = "low_confidence"
    BIAS_DETECTED = "bias_detected"
    CONSTITUTIONAL_CONFLICT = "constitutional_conflict"
    POLICY_VIOLATION = "policy_violation"
    ERROR_DETECTED = "error_detected"
    USER_REQUEST = "user_request"
    REGULATORY_REQUIREMENT = "regulatory_requirement"
    QUALITY_THRESHOLD = "quality_threshold"
    ETHICAL_CONCERN = "ethical_concern"
    TRANSPARENCY_ISSUE = "transparency_issue"
    STAKEHOLDER_ESCALATION = "stakeholder_escalation"
    SYSTEM_UNCERTAINTY = "system_uncertainty"


class InterventionOutcome(Enum):
    """Outcomes of human intervention"""

    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"
    ESCALATED = "escalated"
    DEFERRED = "deferred"
    OVERRIDDEN = "overridden"


class InterventionType(Enum):
    """Types of intervention"""

    PREVENTIVE = "preventive"  # Before decision is made
    CORRECTIVE = "corrective"  # After decision is made
    SUPERVISORY = "supervisory"  # Ongoing oversight
    EMERGENCY = "emergency"  # Crisis intervention


class ReviewerRole(Enum):
    """Roles of human reviewers"""

    CONSTITUTIONAL_EXPERT = "constitutional_expert"
    LEGAL_SPECIALIST = "legal_specialist"
    POLICY_ADVISOR = "policy_advisor"
    ETHICS_REVIEWER = "ethics_reviewer"
    TECHNICAL_REVIEWER = "technical_reviewer"
    SENIOR_SUPERVISOR = "senior_supervisor"
    CITIZEN_REPRESENTATIVE = "citizen_representative"


@dataclass
class InterventionEvent:
    """Individual intervention event record"""

    event_id: str
    timestamp: datetime
    decision_id: str
    intervention_type: InterventionType
    reason: InterventionReason
    reviewer_id: str
    reviewer_role: ReviewerRole
    original_decision: dict[str, Any]
    intervention_action: dict[str, Any]
    outcome: InterventionOutcome
    duration_seconds: float
    confidence_before: float
    confidence_after: float
    impact_assessment: float | None
    follow_up_required: bool
    escalation_level: int
    context_metadata: dict[str, Any]


@dataclass
class InterventionPattern:
    """Detected intervention pattern"""

    pattern_id: str
    pattern_type: str
    description: str
    frequency: float
    confidence: float
    time_window: timedelta
    affected_decisions: list[str]
    underlying_causes: list[str]
    recommendations: list[str]
    severity: str


@dataclass
class ReviewerPerformance:
    """Reviewer performance metrics"""

    reviewer_id: str
    reviewer_role: ReviewerRole
    total_interventions: int
    average_duration: float
    accuracy_score: float
    consistency_score: float
    timeliness_score: float
    improvement_rate: float
    specialization_areas: list[str]
    workload_balance: float
    satisfaction_rating: float | None


@dataclass
class InterventionRateMetrics:
    """Intervention rate metrics for a time period"""

    time_period: timedelta
    total_decisions: int
    total_interventions: int
    intervention_rate: float
    intervention_rate_by_reason: dict[InterventionReason, float]
    intervention_rate_by_type: dict[InterventionType, float]
    average_intervention_duration: float
    success_rate: float
    escalation_rate: float
    cost_impact: float | None
    quality_improvement: float | None


@dataclass
class InterventionAlert:
    """Alert for intervention rate anomalies"""

    alert_id: str
    alert_type: str
    severity: str
    description: str
    current_rate: float
    expected_rate: float
    deviation: float
    time_window: timedelta
    affected_systems: list[str]
    recommended_actions: list[str]
    stakeholders: list[str]
    timestamp: datetime


class HumanInterventionTracker:
    """
    Comprehensive human intervention tracking and analysis system
    """

    def __init__(self, config: dict[str, Any] | None = None):
        self.config = config or {}
        self.alerting = AlertingSystem()
        self.audit_logger = AuditLogger()

        # Tracking configuration
        self.tracking_enabled = config.get("tracking_enabled", True)
        self.analysis_interval_seconds = config.get(
            "analysis_interval_seconds", 300
        )  # 5 minutes
        self.pattern_detection_enabled = config.get("pattern_detection_enabled", True)
        self.performance_tracking_enabled = config.get(
            "performance_tracking_enabled", True
        )

        # Rate thresholds and targets
        self.target_intervention_rate = config.get(
            "target_intervention_rate", 0.15
        )  # 15%
        self.intervention_rate_thresholds = config.get(
            "intervention_rate_thresholds",
            {
                "low_concern": 0.25,
                "medium_concern": 0.35,
                "high_concern": 0.45,
                "critical_concern": 0.60,
            },
        )

        # Duration thresholds (in seconds)
        self.duration_thresholds = config.get(
            "duration_thresholds",
            {
                "fast": 60,  # Under 1 minute
                "normal": 300,  # Under 5 minutes
                "slow": 900,  # Under 15 minutes
                "very_slow": 1800,  # Under 30 minutes
            },
        )

        # Data storage
        self.intervention_events = {}  # event_id -> InterventionEvent
        self.intervention_history = deque(maxlen=10000)  # Recent events
        self.rate_history = deque(maxlen=1440)  # 24 hours at 1-minute intervals
        self.pattern_history = deque(maxlen=100)
        self.reviewer_performance = {}  # reviewer_id -> ReviewerPerformance

        # Analysis state
        self.running = False
        self.last_analysis_time = datetime.utcnow()

        # Rate tracking windows
        self.hourly_rates = deque(maxlen=24)  # 24 hours
        self.daily_rates = deque(maxlen=30)  # 30 days
        self.weekly_rates = deque(maxlen=12)  # 12 weeks

        # Decision tracking for rate calculation
        self.decision_counter = defaultdict(int)  # time_bucket -> count
        self.intervention_counter = defaultdict(int)  # time_bucket -> count

    async def start_tracking(self):
        """Start intervention tracking and analysis"""
        if self.running:
            logger.warning("Intervention tracking is already running")
            return

        self.running = True
        logger.info("Starting human intervention tracking")

        try:
            # Start tracking tasks
            tracking_tasks = [
                self._run_rate_analysis(),
                self._run_pattern_detection(),
                self._run_performance_analysis(),
                self._run_alerting_system(),
                self._run_periodic_reporting(),
            ]

            await asyncio.gather(*tracking_tasks)

        except Exception as e:
            logger.exception(f"Intervention tracking failed: {e}")
            self.running = False
            raise
        finally:
            logger.info("Intervention tracking stopped")

    async def stop_tracking(self):
        """Stop intervention tracking"""
        self.running = False
        logger.info("Stopping intervention tracking")

    async def record_intervention(self, intervention_data: dict[str, Any]) -> str:
        """Record a human intervention event"""
        try:
            event_id = str(uuid.uuid4())

            # Create intervention event
            event = InterventionEvent(
                event_id=event_id,
                timestamp=datetime.utcnow(),
                decision_id=intervention_data.get("decision_id", ""),
                intervention_type=InterventionType(
                    intervention_data.get("intervention_type", "corrective")
                ),
                reason=InterventionReason(
                    intervention_data.get("reason", "user_request")
                ),
                reviewer_id=intervention_data.get("reviewer_id", ""),
                reviewer_role=ReviewerRole(
                    intervention_data.get("reviewer_role", "technical_reviewer")
                ),
                original_decision=intervention_data.get("original_decision", {}),
                intervention_action=intervention_data.get("intervention_action", {}),
                outcome=InterventionOutcome(
                    intervention_data.get("outcome", "approved")
                ),
                duration_seconds=intervention_data.get("duration_seconds", 0.0),
                confidence_before=intervention_data.get("confidence_before", 0.0),
                confidence_after=intervention_data.get("confidence_after", 0.0),
                impact_assessment=intervention_data.get("impact_assessment"),
                follow_up_required=intervention_data.get("follow_up_required", False),
                escalation_level=intervention_data.get("escalation_level", 0),
                context_metadata=intervention_data.get("context_metadata", {}),
            )

            # Store event
            self.intervention_events[event_id] = event
            self.intervention_history.append(event)

            # Update counters
            time_bucket = self._get_time_bucket(event.timestamp, "minute")
            self.intervention_counter[time_bucket] += 1

            # Update reviewer performance
            await self._update_reviewer_performance(event)

            # Log intervention
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "human_intervention_recorded",
                    "event_id": event_id,
                    "decision_id": event.decision_id,
                    "intervention_type": event.intervention_type.value,
                    "reason": event.reason.value,
                    "reviewer_id": event.reviewer_id,
                    "reviewer_role": event.reviewer_role.value,
                    "outcome": event.outcome.value,
                    "duration_seconds": event.duration_seconds,
                    "escalation_level": event.escalation_level,
                    "timestamp": event.timestamp.isoformat(),
                }
            )

            # Immediate analysis for critical interventions
            if event.reason in {
                InterventionReason.CONSTITUTIONAL_CONFLICT,
                InterventionReason.BIAS_DETECTED,
            }:
                await self._analyze_critical_intervention(event)

            return event_id

        except Exception as e:
            logger.exception(f"Failed to record intervention: {e}")
            raise

    async def record_decision(self, decision_id: str, decision_data: dict[str, Any]):
        """Record an AI decision for rate calculation"""
        try:
            timestamp = datetime.utcnow()
            time_bucket = self._get_time_bucket(timestamp, "minute")

            # Increment decision counter
            self.decision_counter[time_bucket] += 1

            # Clean old counters (keep last 24 hours)
            cutoff_time = timestamp - timedelta(hours=24)
            cutoff_bucket = self._get_time_bucket(cutoff_time, "minute")

            # Remove old entries
            old_buckets = [
                bucket for bucket in self.decision_counter if bucket < cutoff_bucket
            ]
            for bucket in old_buckets:
                del self.decision_counter[bucket]
                if bucket in self.intervention_counter:
                    del self.intervention_counter[bucket]

        except Exception as e:
            logger.exception(f"Failed to record decision: {e}")

    def _get_time_bucket(self, timestamp: datetime, granularity: str) -> str:
        """Get time bucket for aggregation"""
        if granularity == "minute":
            return timestamp.strftime("%Y%m%d%H%M")
        if granularity == "hour":
            return timestamp.strftime("%Y%m%d%H")
        if granularity == "day":
            return timestamp.strftime("%Y%m%d")
        if granularity == "week":
            # ISO week
            year, week, _ = timestamp.isocalendar()
            return f"{year}W{week:02d}"
        return timestamp.isoformat()

    async def _run_rate_analysis(self):
        """Run continuous intervention rate analysis"""
        while self.running:
            try:
                await asyncio.sleep(60)  # Analyze every minute

                if not self.running:
                    break

                # Calculate current intervention rates
                await self._calculate_intervention_rates()

                # Check for rate anomalies
                await self._check_rate_anomalies()

            except Exception as e:
                logger.exception(f"Rate analysis error: {e}")
                await asyncio.sleep(60)

    async def _calculate_intervention_rates(self):
        """Calculate intervention rates for different time windows"""
        try:
            current_time = datetime.utcnow()

            # Calculate rates for different time windows
            time_windows = {
                "last_hour": timedelta(hours=1),
                "last_day": timedelta(days=1),
                "last_week": timedelta(days=7),
            }

            rates = {}

            for window_name, window_duration in time_windows.items():
                start_time = current_time - window_duration

                # Count decisions and interventions in window
                total_decisions = 0
                total_interventions = 0

                # Count from buckets
                for bucket_str, count in self.decision_counter.items():
                    bucket_time = datetime.strptime(bucket_str, "%Y%m%d%H%M")
                    if bucket_time >= start_time:
                        total_decisions += count

                for bucket_str, count in self.intervention_counter.items():
                    bucket_time = datetime.strptime(bucket_str, "%Y%m%d%H%M")
                    if bucket_time >= start_time:
                        total_interventions += count

                # Calculate rate
                intervention_rate = (
                    total_interventions / total_decisions if total_decisions > 0 else 0
                )

                # Calculate rate by reason
                window_interventions = [
                    event
                    for event in self.intervention_history
                    if event.timestamp >= start_time
                ]

                rate_by_reason = {}
                for reason in InterventionReason:
                    reason_count = sum(
                        1 for event in window_interventions if event.reason == reason
                    )
                    rate_by_reason[reason] = (
                        reason_count / total_decisions if total_decisions > 0 else 0
                    )

                # Calculate rate by type
                rate_by_type = {}
                for intervention_type in InterventionType:
                    type_count = sum(
                        1
                        for event in window_interventions
                        if event.intervention_type == intervention_type
                    )
                    rate_by_type[intervention_type] = (
                        type_count / total_decisions if total_decisions > 0 else 0
                    )

                # Calculate other metrics
                avg_duration = (
                    statistics.mean(
                        [event.duration_seconds for event in window_interventions]
                    )
                    if window_interventions
                    else 0
                )

                success_rate = (
                    sum(
                        1
                        for event in window_interventions
                        if event.outcome
                        in {InterventionOutcome.APPROVED, InterventionOutcome.MODIFIED}
                    )
                    / len(window_interventions)
                    if window_interventions
                    else 0
                )

                escalation_rate = (
                    sum(
                        1
                        for event in window_interventions
                        if event.escalation_level > 0
                    )
                    / len(window_interventions)
                    if window_interventions
                    else 0
                )

                # Create metrics object
                metrics = InterventionRateMetrics(
                    time_period=window_duration,
                    total_decisions=total_decisions,
                    total_interventions=total_interventions,
                    intervention_rate=intervention_rate,
                    intervention_rate_by_reason=rate_by_reason,
                    intervention_rate_by_type=rate_by_type,
                    average_intervention_duration=avg_duration,
                    success_rate=success_rate,
                    escalation_rate=escalation_rate,
                    cost_impact=None,  # Would be calculated based on business metrics
                    quality_improvement=None,  # Would be calculated based on outcome analysis
                )

                rates[window_name] = metrics

            # Store current rates for history
            self.rate_history.append(
                {
                    "timestamp": current_time,
                    "hourly_rate": rates.get("last_hour", {}).intervention_rate,
                    "daily_rate": rates.get("last_day", {}).intervention_rate,
                    "weekly_rate": rates.get("last_week", {}).intervention_rate,
                }
            )

            # Update historical rate collections
            if len(self.rate_history) >= 60:  # Every hour
                hourly_data = list(self.rate_history)[-60:]  # Last hour
                avg_hourly_rate = statistics.mean(
                    [r["hourly_rate"] for r in hourly_data]
                )
                self.hourly_rates.append(
                    {"timestamp": current_time, "rate": avg_hourly_rate}
                )

            self.last_analysis_time = current_time

        except Exception as e:
            logger.exception(f"Rate calculation failed: {e}")

    async def _check_rate_anomalies(self):
        """Check for intervention rate anomalies"""
        try:
            if not self.rate_history:
                return

            current_rates = self.rate_history[-1]
            datetime.utcnow()

            # Check hourly rate
            hourly_rate = current_rates["hourly_rate"]

            # Compare against thresholds
            alerts_to_send = []

            if hourly_rate >= self.intervention_rate_thresholds["critical_concern"]:
                alerts_to_send.append(
                    self._create_rate_alert(
                        "critical_intervention_rate",
                        "critical",
                        f"Critical intervention rate: {hourly_rate:.2%}",
                        hourly_rate,
                        timedelta(hours=1),
                    )
                )
            elif hourly_rate >= self.intervention_rate_thresholds["high_concern"]:
                alerts_to_send.append(
                    self._create_rate_alert(
                        "high_intervention_rate",
                        "high",
                        f"High intervention rate: {hourly_rate:.2%}",
                        hourly_rate,
                        timedelta(hours=1),
                    )
                )
            elif hourly_rate >= self.intervention_rate_thresholds["medium_concern"]:
                alerts_to_send.append(
                    self._create_rate_alert(
                        "elevated_intervention_rate",
                        "medium",
                        f"Elevated intervention rate: {hourly_rate:.2%}",
                        hourly_rate,
                        timedelta(hours=1),
                    )
                )

            # Check for sudden rate changes
            if len(self.rate_history) >= 60:  # At least 1 hour of data
                recent_rates = [r["hourly_rate"] for r in list(self.rate_history)[-60:]]
                if len(recent_rates) > 30:
                    # Compare last 30 minutes to previous 30 minutes
                    recent_avg = statistics.mean(recent_rates[-30:])
                    previous_avg = statistics.mean(recent_rates[-60:-30])

                    if previous_avg > 0:
                        rate_change = (recent_avg - previous_avg) / previous_avg

                        if rate_change > 0.5:  # 50% increase
                            alerts_to_send.append(
                                self._create_rate_alert(
                                    "sudden_rate_increase",
                                    "high",
                                    "Sudden intervention rate increase:"
                                    f" {rate_change:.1%}",
                                    recent_avg,
                                    timedelta(minutes=30),
                                )
                            )

            # Send alerts
            for alert in alerts_to_send:
                await self.alerting.send_alert(
                    alert.alert_type, alert.description, severity=alert.severity
                )

                await self.audit_logger.log_compliance_event(
                    {
                        "event_type": "intervention_rate_alert",
                        "alert_id": alert.alert_id,
                        "alert_type": alert.alert_type,
                        "severity": alert.severity,
                        "current_rate": alert.current_rate,
                        "expected_rate": alert.expected_rate,
                        "deviation": alert.deviation,
                        "timestamp": alert.timestamp.isoformat(),
                    }
                )

        except Exception as e:
            logger.exception(f"Rate anomaly check failed: {e}")

    def _create_rate_alert(
        self,
        alert_type: str,
        severity: str,
        description: str,
        current_rate: float,
        time_window: timedelta,
    ) -> InterventionAlert:
        """Create intervention rate alert"""
        return InterventionAlert(
            alert_id=str(uuid.uuid4()),
            alert_type=alert_type,
            severity=severity,
            description=description,
            current_rate=current_rate,
            expected_rate=self.target_intervention_rate,
            deviation=abs(current_rate - self.target_intervention_rate)
            / self.target_intervention_rate,
            time_window=time_window,
            affected_systems=["constitutional_ai", "decision_engine"],
            recommended_actions=self._get_rate_alert_recommendations(
                alert_type, current_rate
            ),
            stakeholders=["ml_team", "operations_team", "compliance_team"],
            timestamp=datetime.utcnow(),
        )

    def _get_rate_alert_recommendations(
        self, alert_type: str, current_rate: float
    ) -> list[str]:
        """Get recommendations for rate alerts"""
        recommendations = []

        if "critical" in alert_type:
            recommendations.extend(
                [
                    "URGENT: Investigate system performance immediately",
                    "Consider emergency escalation to senior staff",
                    "Review recent system changes or deployments",
                    "Implement immediate monitoring of all decisions",
                ]
            )
        elif "high" in alert_type:
            recommendations.extend(
                [
                    "Investigate root causes of increased intervention",
                    "Review model performance metrics",
                    "Check for data quality issues",
                    "Consider adjusting confidence thresholds",
                ]
            )
        elif "sudden" in alert_type:
            recommendations.extend(
                [
                    "Analyze recent system changes",
                    "Check for environmental factors",
                    "Review input data for anomalies",
                    "Monitor for continued trend",
                ]
            )
        else:
            recommendations.extend(
                [
                    "Monitor intervention patterns",
                    "Review recent decisions requiring intervention",
                    "Consider model retraining if trend continues",
                ]
            )

        return recommendations

    async def _run_pattern_detection(self):
        """Run pattern detection on intervention data"""
        while self.running:
            try:
                await asyncio.sleep(self.analysis_interval_seconds)

                if not self.running:
                    break

                if self.pattern_detection_enabled:
                    await self._detect_intervention_patterns()

            except Exception as e:
                logger.exception(f"Pattern detection error: {e}")
                await asyncio.sleep(300)

    async def _detect_intervention_patterns(self):
        """Detect patterns in intervention data"""
        try:
            if len(self.intervention_history) < 50:
                return

            recent_interventions = list(self.intervention_history)[
                -100:
            ]  # Last 100 interventions
            patterns_detected = []

            # Pattern 1: Time-based clustering
            time_pattern = await self._detect_time_based_patterns(recent_interventions)
            if time_pattern:
                patterns_detected.append(time_pattern)

            # Pattern 2: Reason clustering
            reason_pattern = await self._detect_reason_patterns(recent_interventions)
            if reason_pattern:
                patterns_detected.append(reason_pattern)

            # Pattern 3: Reviewer patterns
            reviewer_pattern = await self._detect_reviewer_patterns(
                recent_interventions
            )
            if reviewer_pattern:
                patterns_detected.append(reviewer_pattern)

            # Pattern 4: Decision type patterns
            decision_pattern = await self._detect_decision_patterns(
                recent_interventions
            )
            if decision_pattern:
                patterns_detected.append(decision_pattern)

            # Store and analyze patterns
            for pattern in patterns_detected:
                self.pattern_history.append(pattern)
                await self._analyze_pattern_significance(pattern)

        except Exception as e:
            logger.exception(f"Pattern detection failed: {e}")

    async def _detect_time_based_patterns(
        self, interventions: list[InterventionEvent]
    ) -> InterventionPattern | None:
        """Detect time-based intervention patterns"""
        try:
            # Group interventions by hour of day
            hourly_counts = defaultdict(int)
            for intervention in interventions:
                hour = intervention.timestamp.hour
                hourly_counts[hour] += 1

            # Find peak hours
            if hourly_counts:
                max_hour = max(hourly_counts, key=hourly_counts.get)
                max_count = hourly_counts[max_hour]
                total_interventions = len(interventions)

                # Check if there's a significant clustering
                if max_count / total_interventions > 0.3:  # More than 30% in one hour
                    return InterventionPattern(
                        pattern_id=str(uuid.uuid4()),
                        pattern_type="temporal_clustering",
                        description=f"High intervention rate during hour {max_hour}:00",
                        frequency=max_count / total_interventions,
                        confidence=0.8,
                        time_window=timedelta(hours=1),
                        affected_decisions=[
                            i.decision_id
                            for i in interventions
                            if i.timestamp.hour == max_hour
                        ],
                        underlying_causes=[
                            "System load patterns",
                            "User behavior patterns",
                        ],
                        recommendations=[
                            f"Investigate system performance during hour {max_hour}:00",
                            "Consider load balancing adjustments",
                            "Review staffing patterns for peak hours",
                        ],
                        severity="medium",
                    )

            return None

        except Exception as e:
            logger.exception(f"Time pattern detection failed: {e}")
            return None

    async def _detect_reason_patterns(
        self, interventions: list[InterventionEvent]
    ) -> InterventionPattern | None:
        """Detect reason-based intervention patterns"""
        try:
            # Count interventions by reason
            reason_counts = defaultdict(int)
            for intervention in interventions:
                reason_counts[intervention.reason] += 1

            total_interventions = len(interventions)

            # Find dominant reason
            if reason_counts:
                dominant_reason = max(reason_counts, key=reason_counts.get)
                dominant_count = reason_counts[dominant_reason]

                # Check if one reason dominates
                if dominant_count / total_interventions > 0.4:  # More than 40%
                    return InterventionPattern(
                        pattern_id=str(uuid.uuid4()),
                        pattern_type="reason_clustering",
                        description=(
                            f"High frequency of {dominant_reason.value} interventions"
                        ),
                        frequency=dominant_count / total_interventions,
                        confidence=0.9,
                        time_window=timedelta(hours=24),
                        affected_decisions=[
                            i.decision_id
                            for i in interventions
                            if i.reason == dominant_reason
                        ],
                        underlying_causes=self._get_reason_causes(dominant_reason),
                        recommendations=self._get_reason_recommendations(
                            dominant_reason
                        ),
                        severity=(
                            "high"
                            if dominant_reason
                            in {
                                InterventionReason.CONSTITUTIONAL_CONFLICT,
                                InterventionReason.BIAS_DETECTED,
                            }
                            else "medium"
                        ),
                    )

            return None

        except Exception as e:
            logger.exception(f"Reason pattern detection failed: {e}")
            return None

    def _get_reason_causes(self, reason: InterventionReason) -> list[str]:
        """Get potential causes for intervention reason patterns"""
        causes_map = {
            InterventionReason.LOW_CONFIDENCE: [
                "Model uncertainty increase",
                "Edge case scenarios",
                "Training data gaps",
            ],
            InterventionReason.BIAS_DETECTED: [
                "Biased training data",
                "Algorithmic bias",
                "Unfair feature importance",
            ],
            InterventionReason.CONSTITUTIONAL_CONFLICT: [
                "Unclear constitutional principles",
                "Conflicting constitutional values",
                "Edge case constitutional interpretation",
            ],
            InterventionReason.POLICY_VIOLATION: [
                "Outdated policy rules",
                "Policy ambiguity",
                "Rapid policy changes",
            ],
        }

        return causes_map.get(reason, ["Unknown causes"])

    def _get_reason_recommendations(self, reason: InterventionReason) -> list[str]:
        """Get recommendations for intervention reason patterns"""
        recommendations_map = {
            InterventionReason.LOW_CONFIDENCE: [
                "Review model confidence calibration",
                "Enhance training data for edge cases",
                "Adjust confidence thresholds",
            ],
            InterventionReason.BIAS_DETECTED: [
                "Conduct comprehensive bias audit",
                "Implement bias mitigation techniques",
                "Review training data for bias sources",
            ],
            InterventionReason.CONSTITUTIONAL_CONFLICT: [
                "Clarify constitutional principle hierarchy",
                "Implement conflict resolution protocols",
                "Engage constitutional experts for guidance",
            ],
            InterventionReason.POLICY_VIOLATION: [
                "Update policy rule database",
                "Clarify ambiguous policies",
                "Implement policy change notification system",
            ],
        }

        return recommendations_map.get(reason, ["Review and analyze root causes"])

    async def _detect_reviewer_patterns(
        self, interventions: list[InterventionEvent]
    ) -> InterventionPattern | None:
        """Detect reviewer-based patterns"""
        try:
            # Analyze reviewer workload distribution
            reviewer_counts = defaultdict(int)
            for intervention in interventions:
                reviewer_counts[intervention.reviewer_id] += 1

            total_interventions = len(interventions)
            unique_reviewers = len(reviewer_counts)

            if unique_reviewers > 1:
                # Check for workload imbalance
                max_workload = max(reviewer_counts.values())
                avg_workload = total_interventions / unique_reviewers

                if max_workload > avg_workload * 2:  # One reviewer has 2x average
                    overloaded_reviewer = max(reviewer_counts, key=reviewer_counts.get)

                    return InterventionPattern(
                        pattern_id=str(uuid.uuid4()),
                        pattern_type="reviewer_overload",
                        description=(
                            f"Reviewer {overloaded_reviewer} handling disproportionate"
                            " workload"
                        ),
                        frequency=max_workload / total_interventions,
                        confidence=0.9,
                        time_window=timedelta(hours=24),
                        affected_decisions=[
                            i.decision_id
                            for i in interventions
                            if i.reviewer_id == overloaded_reviewer
                        ],
                        underlying_causes=[
                            "Uneven reviewer availability",
                            "Specialized expertise requirements",
                            "Workload distribution inefficiency",
                        ],
                        recommendations=[
                            "Redistribute reviewer workload",
                            "Consider additional reviewer training",
                            "Implement workload balancing algorithms",
                        ],
                        severity="medium",
                    )

            return None

        except Exception as e:
            logger.exception(f"Reviewer pattern detection failed: {e}")
            return None

    async def _detect_decision_patterns(
        self, interventions: list[InterventionEvent]
    ) -> InterventionPattern | None:
        """Detect decision-related patterns"""
        try:
            # Analyze intervention outcomes
            outcome_counts = defaultdict(int)
            for intervention in interventions:
                outcome_counts[intervention.outcome] += 1

            total_interventions = len(interventions)

            # Check for high rejection rate
            rejections = outcome_counts.get(InterventionOutcome.REJECTED, 0)
            rejection_rate = (
                rejections / total_interventions if total_interventions > 0 else 0
            )

            if rejection_rate > 0.3:  # More than 30% rejections
                return InterventionPattern(
                    pattern_id=str(uuid.uuid4()),
                    pattern_type="high_rejection_rate",
                    description=(
                        f"High intervention rejection rate: {rejection_rate:.1%}"
                    ),
                    frequency=rejection_rate,
                    confidence=0.8,
                    time_window=timedelta(hours=24),
                    affected_decisions=[
                        i.decision_id
                        for i in interventions
                        if i.outcome == InterventionOutcome.REJECTED
                    ],
                    underlying_causes=[
                        "Poor initial decision quality",
                        "Overly conservative intervention triggers",
                        "Misaligned reviewer expectations",
                    ],
                    recommendations=[
                        "Review decision quality metrics",
                        "Adjust intervention thresholds",
                        "Provide additional reviewer training",
                    ],
                    severity="high",
                )

            return None

        except Exception as e:
            logger.exception(f"Decision pattern detection failed: {e}")
            return None

    async def _analyze_pattern_significance(self, pattern: InterventionPattern):
        """Analyze and respond to detected patterns"""
        try:
            # Log pattern detection
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "intervention_pattern_detected",
                    "pattern_id": pattern.pattern_id,
                    "pattern_type": pattern.pattern_type,
                    "description": pattern.description,
                    "frequency": pattern.frequency,
                    "confidence": pattern.confidence,
                    "severity": pattern.severity,
                    "affected_decisions_count": len(pattern.affected_decisions),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            )

            # Send alert for significant patterns
            if pattern.severity in {"high", "critical"} and pattern.confidence > 0.7:
                await self.alerting.send_alert(
                    f"intervention_pattern_{pattern.pattern_type}",
                    f"Significant intervention pattern detected: {pattern.description}",
                    severity=pattern.severity,
                )

        except Exception as e:
            logger.exception(f"Pattern significance analysis failed: {e}")

    async def _run_performance_analysis(self):
        """Run reviewer performance analysis"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # Run every hour

                if not self.running:
                    break

                if self.performance_tracking_enabled:
                    await self._analyze_reviewer_performance()

            except Exception as e:
                logger.exception(f"Performance analysis error: {e}")
                await asyncio.sleep(300)

    async def _analyze_reviewer_performance(self):
        """Analyze individual reviewer performance"""
        try:
            # Get interventions from last 7 days
            week_ago = datetime.utcnow() - timedelta(days=7)
            recent_interventions = [
                event
                for event in self.intervention_history
                if event.timestamp >= week_ago
            ]

            # Group by reviewer
            reviewer_interventions = defaultdict(list)
            for intervention in recent_interventions:
                reviewer_interventions[intervention.reviewer_id].append(intervention)

            # Analyze each reviewer
            for reviewer_id, interventions in reviewer_interventions.items():
                if len(interventions) < 5:  # Need minimum data
                    continue

                performance = await self._calculate_reviewer_performance(
                    reviewer_id, interventions
                )
                self.reviewer_performance[reviewer_id] = performance

                # Check for performance issues
                await self._check_reviewer_performance_issues(performance)

        except Exception as e:
            logger.exception(f"Reviewer performance analysis failed: {e}")

    async def _calculate_reviewer_performance(
        self, reviewer_id: str, interventions: list[InterventionEvent]
    ) -> ReviewerPerformance:
        """Calculate performance metrics for a reviewer"""
        try:
            # Basic metrics
            total_interventions = len(interventions)

            # Duration metrics
            durations = [i.duration_seconds for i in interventions]
            avg_duration = statistics.mean(durations)

            # Accuracy score (based on follow-up requirements and escalations)
            successful_interventions = sum(
                1
                for i in interventions
                if not i.follow_up_required and i.escalation_level == 0
            )
            accuracy_score = successful_interventions / total_interventions

            # Consistency score (based on similar decisions)
            consistency_score = await self._calculate_consistency_score(interventions)

            # Timeliness score (based on duration thresholds)
            fast_interventions = sum(
                1
                for i in interventions
                if i.duration_seconds <= self.duration_thresholds["normal"]
            )
            timeliness_score = fast_interventions / total_interventions

            # Improvement rate (comparing recent vs older performance)
            improvement_rate = await self._calculate_improvement_rate(
                reviewer_id, interventions
            )

            # Specialization areas
            reason_counts = defaultdict(int)
            for intervention in interventions:
                reason_counts[intervention.reason] += 1

            # Top 3 most common reasons
            specialization_areas = [
                reason.value
                for reason, count in sorted(
                    reason_counts.items(), key=operator.itemgetter(1), reverse=True
                )[:3]
            ]

            # Workload balance (compared to other reviewers)
            all_reviewer_counts = defaultdict(int)
            for intervention in self.intervention_history:
                all_reviewer_counts[intervention.reviewer_id] += 1

            avg_workload = (
                statistics.mean(all_reviewer_counts.values())
                if all_reviewer_counts
                else 1
            )
            workload_balance = (
                1.0 - abs(total_interventions - avg_workload) / avg_workload
            )

            # Get reviewer role
            reviewer_role = (
                interventions[0].reviewer_role
                if interventions
                else ReviewerRole.TECHNICAL_REVIEWER
            )

            return ReviewerPerformance(
                reviewer_id=reviewer_id,
                reviewer_role=reviewer_role,
                total_interventions=total_interventions,
                average_duration=avg_duration,
                accuracy_score=accuracy_score,
                consistency_score=consistency_score,
                timeliness_score=timeliness_score,
                improvement_rate=improvement_rate,
                specialization_areas=specialization_areas,
                workload_balance=workload_balance,
                satisfaction_rating=None,  # Would be collected from feedback
            )

        except Exception as e:
            logger.exception(f"Reviewer performance calculation failed: {e}")
            # Return default performance
            return ReviewerPerformance(
                reviewer_id=reviewer_id,
                reviewer_role=ReviewerRole.TECHNICAL_REVIEWER,
                total_interventions=0,
                average_duration=0,
                accuracy_score=0,
                consistency_score=0,
                timeliness_score=0,
                improvement_rate=0,
                specialization_areas=[],
                workload_balance=0,
                satisfaction_rating=None,
            )

    async def _calculate_consistency_score(
        self, interventions: list[InterventionEvent]
    ) -> float:
        """Calculate consistency score for a reviewer"""
        try:
            # Group similar interventions (same reason, similar context)
            reason_groups = defaultdict(list)
            for intervention in interventions:
                reason_groups[intervention.reason].append(intervention)

            consistency_scores = []

            for group_interventions in reason_groups.values():
                if len(group_interventions) < 2:
                    continue

                # Check consistency of outcomes for same reason
                outcomes = [i.outcome for i in group_interventions]
                most_common_outcome = max(set(outcomes), key=outcomes.count)
                consistency = outcomes.count(most_common_outcome) / len(outcomes)
                consistency_scores.append(consistency)

            return statistics.mean(consistency_scores) if consistency_scores else 1.0

        except Exception:
            return 0.5

    async def _calculate_improvement_rate(
        self, reviewer_id: str, recent_interventions: list[InterventionEvent]
    ) -> float:
        """Calculate improvement rate for a reviewer"""
        try:
            # Compare recent performance to historical
            if len(recent_interventions) < 10:
                return 0.0

            # Split into recent and older interventions
            sorted_interventions = sorted(
                recent_interventions, key=lambda x: x.timestamp
            )
            mid_point = len(sorted_interventions) // 2

            older_interventions = sorted_interventions[:mid_point]
            newer_interventions = sorted_interventions[mid_point:]

            # Calculate accuracy for both periods
            older_accuracy = sum(
                1
                for i in older_interventions
                if not i.follow_up_required and i.escalation_level == 0
            ) / len(older_interventions)

            newer_accuracy = sum(
                1
                for i in newer_interventions
                if not i.follow_up_required and i.escalation_level == 0
            ) / len(newer_interventions)

            # Calculate improvement rate
            improvement_rate = (newer_accuracy - older_accuracy) / (
                older_accuracy + 0.01
            )

            return max(-1.0, min(1.0, improvement_rate))  # Clamp between -1 and 1

        except Exception:
            return 0.0

    async def _check_reviewer_performance_issues(
        self, performance: ReviewerPerformance
    ):
        """Check for reviewer performance issues"""
        try:
            issues = []

            # Low accuracy
            if performance.accuracy_score < 0.7:
                issues.append(f"Low accuracy score: {performance.accuracy_score:.2%}")

            # Slow response time
            if performance.timeliness_score < 0.6:
                issues.append(f"Slow response time: {performance.timeliness_score:.2%}")

            # Poor consistency
            if performance.consistency_score < 0.7:
                issues.append(
                    f"Inconsistent decisions: {performance.consistency_score:.2%}"
                )

            # Declining performance
            if performance.improvement_rate < -0.2:
                issues.append(
                    f"Declining performance: {performance.improvement_rate:.1%}"
                )

            # Workload imbalance
            if performance.workload_balance < 0.5:
                issues.append(f"Workload imbalance: {performance.workload_balance:.2%}")

            # Send alerts for significant issues
            if issues:
                await self.alerting.send_alert(
                    f"reviewer_performance_issues_{performance.reviewer_id}",
                    "Performance issues detected for reviewer"
                    f" {performance.reviewer_id}: {'; '.join(issues)}",
                    severity="medium",
                )

                await self.audit_logger.log_compliance_event(
                    {
                        "event_type": "reviewer_performance_issues",
                        "reviewer_id": performance.reviewer_id,
                        "issues": issues,
                        "performance_metrics": asdict(performance),
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                )

        except Exception as e:
            logger.exception(f"Performance issue check failed: {e}")

    async def _update_reviewer_performance(self, event: InterventionEvent):
        """Update reviewer performance metrics immediately after intervention"""
        try:
            reviewer_id = event.reviewer_id

            # Get or create performance record
            if reviewer_id not in self.reviewer_performance:
                # Get recent interventions for this reviewer
                reviewer_interventions = [
                    e for e in self.intervention_history if e.reviewer_id == reviewer_id
                ]

                if len(reviewer_interventions) >= 5:
                    self.reviewer_performance[reviewer_id] = (
                        await self._calculate_reviewer_performance(
                            reviewer_id, reviewer_interventions
                        )
                    )

        except Exception as e:
            logger.exception(f"Reviewer performance update failed: {e}")

    async def _analyze_critical_intervention(self, event: InterventionEvent):
        """Immediate analysis for critical interventions"""
        try:
            # Log critical intervention
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "critical_intervention_detected",
                    "event_id": event.event_id,
                    "reason": event.reason.value,
                    "decision_id": event.decision_id,
                    "reviewer_id": event.reviewer_id,
                    "escalation_level": event.escalation_level,
                    "timestamp": event.timestamp.isoformat(),
                }
            )

            # Send immediate alert
            await self.alerting.send_alert(
                f"critical_intervention_{event.reason.value}",
                f"Critical intervention: {event.reason.value} for decision"
                f" {event.decision_id}",
                severity="high",
            )

            # Check for patterns of critical interventions
            recent_critical = [
                e
                for e in self.intervention_history
                if (
                    e.reason
                    in {
                        InterventionReason.CONSTITUTIONAL_CONFLICT,
                        InterventionReason.BIAS_DETECTED,
                    }
                    and e.timestamp >= datetime.utcnow() - timedelta(hours=6)
                )
            ]

            if len(recent_critical) >= 3:  # 3 or more critical interventions in 6 hours
                await self.alerting.send_alert(
                    "multiple_critical_interventions",
                    "Multiple critical interventions detected:"
                    f" {len(recent_critical)} in 6 hours",
                    severity="critical",
                )

        except Exception as e:
            logger.exception(f"Critical intervention analysis failed: {e}")

    async def _run_alerting_system(self):
        """Run alerting system for intervention tracking"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes

                if not self.running:
                    break

                # Run various alert checks
                await self._check_intervention_system_health()

            except Exception as e:
                logger.exception(f"Alerting system error: {e}")
                await asyncio.sleep(60)

    async def _check_intervention_system_health(self):
        """Check overall intervention system health"""
        try:
            current_time = datetime.utcnow()

            # Check if we're receiving intervention data
            last_intervention = max(
                (event.timestamp for event in self.intervention_history),
                default=datetime.min,
            )

            time_since_last = current_time - last_intervention

            # Alert if no interventions for too long (could indicate system issues)
            if (
                time_since_last > timedelta(hours=12)
                and len(self.intervention_history) > 0
            ):
                await self.alerting.send_alert(
                    "intervention_system_inactive",
                    "No interventions recorded for"
                    f" {time_since_last.total_seconds() / 3600:.1f} hours",
                    severity="medium",
                )

            # Check reviewer availability
            active_reviewers = set()
            recent_cutoff = current_time - timedelta(hours=24)

            for event in self.intervention_history:
                if event.timestamp >= recent_cutoff:
                    active_reviewers.add(event.reviewer_id)

            if len(active_reviewers) < 2:  # Need minimum reviewer coverage
                await self.alerting.send_alert(
                    "insufficient_reviewer_coverage",
                    f"Only {len(active_reviewers)} active reviewers in last 24 hours",
                    severity="high",
                )

        except Exception as e:
            logger.exception(f"System health check failed: {e}")

    async def _run_periodic_reporting(self):
        """Run periodic reporting"""
        while self.running:
            try:
                await asyncio.sleep(3600)  # Generate reports every hour

                if not self.running:
                    break

                # Generate hourly summary
                await self._generate_hourly_report()

            except Exception as e:
                logger.exception(f"Periodic reporting error: {e}")
                await asyncio.sleep(300)

    async def _generate_hourly_report(self):
        """Generate hourly intervention summary report"""
        try:
            current_time = datetime.utcnow()
            hour_ago = current_time - timedelta(hours=1)

            # Get interventions from last hour
            hourly_interventions = [
                event
                for event in self.intervention_history
                if event.timestamp >= hour_ago
            ]

            if not hourly_interventions:
                return

            # Calculate summary metrics
            total_interventions = len(hourly_interventions)
            avg_duration = statistics.mean(
                [e.duration_seconds for e in hourly_interventions]
            )

            # Count by reason
            reason_counts = defaultdict(int)
            for event in hourly_interventions:
                reason_counts[event.reason.value] += 1

            # Count by outcome
            outcome_counts = defaultdict(int)
            for event in hourly_interventions:
                outcome_counts[event.outcome.value] += 1

            # Active reviewers
            active_reviewers = len({e.reviewer_id for e in hourly_interventions})

            # Generate report
            report = {
                "report_type": "hourly_intervention_summary",
                "period_start": hour_ago.isoformat(),
                "period_end": current_time.isoformat(),
                "summary": {
                    "total_interventions": total_interventions,
                    "average_duration_seconds": avg_duration,
                    "active_reviewers": active_reviewers,
                    "intervention_rate": (
                        len(self.rate_history[-1]) if self.rate_history else 0
                    ),
                },
                "reason_breakdown": dict(reason_counts),
                "outcome_breakdown": dict(outcome_counts),
                "patterns_detected": (
                    len([p for p in self.pattern_history if p.timestamp >= hour_ago])
                    if hasattr(self, "pattern_history")
                    else 0
                ),
            }

            # Log report
            await self.audit_logger.log_compliance_event(
                {
                    "event_type": "hourly_intervention_report",
                    "report": report,
                    "timestamp": current_time.isoformat(),
                }
            )

        except Exception as e:
            logger.exception(f"Hourly report generation failed: {e}")

    # Public query methods

    def get_intervention_summary(
        self, time_window: timedelta = timedelta(hours=24)
    ) -> dict[str, Any]:
        """Get intervention summary for specified time window"""
        try:
            current_time = datetime.utcnow()
            start_time = current_time - time_window

            # Filter interventions by time window
            window_interventions = [
                event
                for event in self.intervention_history
                if event.timestamp >= start_time
            ]

            if not window_interventions:
                return {
                    "time_window_hours": time_window.total_seconds() / 3600,
                    "total_interventions": 0,
                    "intervention_rate": 0,
                    "summary": "No interventions in specified time window",
                }

            # Calculate summary metrics
            total_interventions = len(window_interventions)
            avg_duration = statistics.mean(
                [e.duration_seconds for e in window_interventions]
            )

            # Reason breakdown
            reason_counts = defaultdict(int)
            for event in window_interventions:
                reason_counts[event.reason.value] += 1

            # Outcome breakdown
            outcome_counts = defaultdict(int)
            for event in window_interventions:
                outcome_counts[event.outcome.value] += 1

            # Type breakdown
            type_counts = defaultdict(int)
            for event in window_interventions:
                type_counts[event.intervention_type.value] += 1

            # Reviewer activity
            reviewer_counts = defaultdict(int)
            for event in window_interventions:
                reviewer_counts[event.reviewer_id] += 1

            # Calculate intervention rate (if we have decision data)
            total_decisions = sum(
                count
                for bucket, count in self.decision_counter.items()
                if datetime.strptime(bucket, "%Y%m%d%H%M") >= start_time
            )

            intervention_rate = (
                total_interventions / total_decisions if total_decisions > 0 else 0
            )

            return {
                "time_window_hours": time_window.total_seconds() / 3600,
                "total_interventions": total_interventions,
                "total_decisions": total_decisions,
                "intervention_rate": intervention_rate,
                "average_duration_seconds": avg_duration,
                "active_reviewers": len(reviewer_counts),
                "reason_breakdown": dict(reason_counts),
                "outcome_breakdown": dict(outcome_counts),
                "type_breakdown": dict(type_counts),
                "reviewer_activity": dict(reviewer_counts),
                "patterns_detected": (
                    len(list(self.pattern_history))
                    if hasattr(self, "pattern_history")
                    else 0
                ),
            }

        except Exception as e:
            logger.exception(f"Intervention summary generation failed: {e}")
            return {"error": str(e)}

    def get_reviewer_performance_summary(self) -> dict[str, Any]:
        """Get summary of all reviewer performance"""
        try:
            if not self.reviewer_performance:
                return {"message": "No reviewer performance data available"}

            # Calculate aggregate metrics
            all_performances = list(self.reviewer_performance.values())

            avg_accuracy = statistics.mean([p.accuracy_score for p in all_performances])
            avg_timeliness = statistics.mean(
                [p.timeliness_score for p in all_performances]
            )
            avg_consistency = statistics.mean(
                [p.consistency_score for p in all_performances]
            )
            total_interventions = sum(p.total_interventions for p in all_performances)

            # Top performers
            top_accuracy = max(all_performances, key=lambda x: x.accuracy_score)
            top_timeliness = max(all_performances, key=lambda x: x.timeliness_score)

            # Performance issues
            performance_issues = [
                p.reviewer_id
                for p in all_performances
                if p.accuracy_score < 0.7 or p.timeliness_score < 0.6
            ]

            return {
                "total_reviewers": len(all_performances),
                "total_interventions": total_interventions,
                "average_metrics": {
                    "accuracy_score": avg_accuracy,
                    "timeliness_score": avg_timeliness,
                    "consistency_score": avg_consistency,
                },
                "top_performers": {
                    "accuracy": {
                        "reviewer_id": top_accuracy.reviewer_id,
                        "score": top_accuracy.accuracy_score,
                    },
                    "timeliness": {
                        "reviewer_id": top_timeliness.reviewer_id,
                        "score": top_timeliness.timeliness_score,
                    },
                },
                "performance_issues_count": len(performance_issues),
                "reviewers_with_issues": performance_issues,
            }

        except Exception as e:
            logger.exception(f"Reviewer performance summary failed: {e}")
            return {"error": str(e)}

    def get_tracking_status(self) -> dict[str, Any]:
        """Get current tracking system status"""
        return {
            "tracking_enabled": self.tracking_enabled,
            "running": self.running,
            "last_analysis_time": self.last_analysis_time.isoformat(),
            "data_status": {
                "intervention_events": len(self.intervention_events),
                "intervention_history": len(self.intervention_history),
                "rate_history": len(self.rate_history),
                "pattern_history": (
                    len(self.pattern_history) if hasattr(self, "pattern_history") else 0
                ),
                "reviewer_performance_records": len(self.reviewer_performance),
            },
            "configuration": {
                "target_intervention_rate": self.target_intervention_rate,
                "analysis_interval_seconds": self.analysis_interval_seconds,
                "pattern_detection_enabled": self.pattern_detection_enabled,
                "performance_tracking_enabled": self.performance_tracking_enabled,
            },
        }


# Example usage
async def example_usage():
    """Example of using the human intervention tracker"""
    # Initialize tracker
    tracker = HumanInterventionTracker(
        {
            "tracking_enabled": True,
            "target_intervention_rate": 0.12,
            "pattern_detection_enabled": True,
            "performance_tracking_enabled": True,
        }
    )

    # Start tracking (would run continuously in production)
    logger.info("Starting intervention tracking demo")
    tracking_task = asyncio.create_task(tracker.start_tracking())

    # Simulate some decisions and interventions
    for i in range(10):
        # Record a decision
        await tracker.record_decision(
            f"decision_{i}",
            {
                "decision_type": "policy_recommendation",
                "confidence": np.random.uniform(0.7, 0.95),
            },
        )

        # Sometimes record an intervention
        if np.random.random() < 0.3:  # 30% intervention rate
            await tracker.record_intervention(
                {
                    "decision_id": f"decision_{i}",
                    "intervention_type": "corrective",
                    "reason": np.random.choice(list(InterventionReason)).value,
                    "reviewer_id": f"reviewer_{np.random.randint(1, 4)}",
                    "reviewer_role": np.random.choice(list(ReviewerRole)).value,
                    "outcome": np.random.choice(list(InterventionOutcome)).value,
                    "duration_seconds": np.random.uniform(60, 300),
                    "confidence_before": np.random.uniform(0.5, 0.8),
                    "confidence_after": np.random.uniform(0.8, 0.95),
                }
            )

        await asyncio.sleep(0.1)

    # Let it run for a short period
    await asyncio.sleep(5)

    # Stop tracking
    await tracker.stop_tracking()
    tracking_task.cancel()

    # Get summaries
    summary = tracker.get_intervention_summary(timedelta(hours=1))
    performance_summary = tracker.get_reviewer_performance_summary()
    status = tracker.get_tracking_status()

    logger.info(f"Intervention summary: {summary}")
    logger.info(f"Performance summary: {performance_summary}")
    logger.info(f"Tracking status: {status}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(example_usage())
