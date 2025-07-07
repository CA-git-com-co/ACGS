"""
Spurious Correlation Detector Service
Constitutional Hash: cdd01ef066bc6cf2

CARMA-inspired real-time spurious correlation detection for ACGS performance monitoring.
Automatically detects when performance metrics correlate with spurious attributes that
should not influence system behavior, enabling robust AI governance monitoring.
"""

import asyncio
import logging
import statistics
import time
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

import numpy as np
from pydantic import BaseModel, Field

# Configure logging
logger = logging.getLogger(__name__)


class SpuriousAttributeType(Enum):
    """Types of spurious attributes to monitor"""

    TEMPORAL_ARTIFACTS = "temporal_artifacts"  # Time-based spurious patterns
    FORMATTING_STYLE = "formatting_style"  # Message/response formatting
    AGENT_PERSONALITY = "agent_personality"  # Agent persona variations
    COMMUNICATION_STYLE = "communication_style"  # Formal vs informal
    RESPONSE_LENGTH = "response_length"  # Verbose vs concise
    TECHNICAL_JARGON = "technical_jargon"  # Technical vs simplified language
    DEMOGRAPHIC_MARKERS = "demographic_markers"  # Demographic indicators
    GEOGRAPHIC_INDICATORS = "geographic_indicators"  # Location-based markers
    PLATFORM_METADATA = "platform_metadata"  # System metadata variations


class CorrelationSeverity(Enum):
    """Severity levels for spurious correlations"""

    CRITICAL = "critical"  # >0.8 correlation
    HIGH = "high"  # 0.6-0.8 correlation
    MEDIUM = "medium"  # 0.4-0.6 correlation
    LOW = "low"  # 0.2-0.4 correlation
    NEGLIGIBLE = "negligible"  # <0.2 correlation


@dataclass
class SpuriousCorrelationAlert:
    """Alert for detected spurious correlation"""

    alert_id: str
    service_name: str
    metric_name: str
    spurious_attribute: SpuriousAttributeType
    correlation_strength: float = Field(ge=0.0, le=1.0)
    severity: CorrelationSeverity
    detection_timestamp: datetime
    constitutional_hash: str = "cdd01ef066bc6cf2"

    # Evidence and context
    sample_size: int = 0
    statistical_significance: float = 0.0
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    recent_examples: List[Dict[str, Any]] = field(default_factory=list)

    # Mitigation suggestions
    mitigation_suggestions: List[str] = field(default_factory=list)
    urgency_level: str = "medium"


@dataclass
class MetricObservation:
    """Single metric observation with context"""

    timestamp: datetime
    metric_value: float
    service_name: str
    metric_name: str
    context: Dict[str, Any] = field(default_factory=dict)
    constitutional_hash: str = "cdd01ef066bc6cf2"


class SpuriousCorrelationDetectionResult(BaseModel):
    """Result of spurious correlation detection analysis"""

    detection_id: str
    constitutional_hash: str = "cdd01ef066bc6cf2"

    # Detection summary
    total_correlations_detected: int = 0
    critical_correlations: int = 0
    high_correlations: int = 0

    # Detailed results
    alerts: List[SpuriousCorrelationAlert] = Field(default_factory=list)
    analysis_window: timedelta
    observations_analyzed: int = 0

    # System health impact
    system_robustness_impact: float = Field(ge=0.0, le=1.0, default=0.0)
    recommended_actions: List[str] = Field(default_factory=list)

    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SpuriousCorrelationDetector:
    """Real-time detection of spurious correlations in performance metrics"""

    # Correlation thresholds for different severity levels
    CORRELATION_THRESHOLDS = {
        CorrelationSeverity.CRITICAL: 0.8,
        CorrelationSeverity.HIGH: 0.6,
        CorrelationSeverity.MEDIUM: 0.4,
        CorrelationSeverity.LOW: 0.2,
        CorrelationSeverity.NEGLIGIBLE: 0.0,
    }

    # Statistical significance thresholds
    SIGNIFICANCE_THRESHOLDS = {
        "critical": 0.01,  # p < 0.01
        "high": 0.05,  # p < 0.05
        "medium": 0.1,  # p < 0.1
        "low": 0.2,  # p < 0.2
    }

    # Minimum sample sizes for reliable detection
    MIN_SAMPLE_SIZES = {
        CorrelationSeverity.CRITICAL: 10,
        CorrelationSeverity.HIGH: 20,
        CorrelationSeverity.MEDIUM: 30,
        CorrelationSeverity.LOW: 50,
    }

    def __init__(
        self,
        detection_window_minutes: int = 60,
        max_observations: int = 10000,
        min_detection_interval_seconds: int = 30,
    ):
        """
        Initialize spurious correlation detector.

        Args:
            detection_window_minutes: Window size for correlation analysis
            max_observations: Maximum observations to keep in memory
            min_detection_interval_seconds: Minimum time between detections
        """
        self.detection_window = timedelta(minutes=detection_window_minutes)
        self.max_observations = max_observations
        self.min_detection_interval = timedelta(seconds=min_detection_interval_seconds)

        # Observation storage
        self.observations: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=max_observations)
        )
        self.last_detection_time = defaultdict(
            lambda: datetime.min.replace(tzinfo=timezone.utc)
        )

        # Detection history
        self.detection_history: deque = deque(maxlen=1000)
        self.active_alerts: Dict[str, SpuriousCorrelationAlert] = {}

        # Statistics
        self.detection_stats = {
            "total_detections": 0,
            "correlations_detected": 0,
            "false_positives": 0,
            "system_interventions": 0,
        }

        logger.info("Spurious correlation detector initialized")

    async def record_observation(
        self,
        service_name: str,
        metric_name: str,
        metric_value: float,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Record a metric observation for correlation analysis.

        Args:
            service_name: Name of the service
            metric_name: Name of the metric
            metric_value: Metric value
            context: Additional context that might contain spurious attributes
        """
        timestamp = datetime.now(timezone.utc)
        observation_key = f"{service_name}:{metric_name}"

        observation = MetricObservation(
            timestamp=timestamp,
            metric_value=metric_value,
            service_name=service_name,
            metric_name=metric_name,
            context=context or {},
        )

        self.observations[observation_key].append(observation)

        # Trigger detection if enough time has passed
        if (
            timestamp - self.last_detection_time[observation_key]
            >= self.min_detection_interval
        ):
            await self._trigger_correlation_detection(observation_key)
            self.last_detection_time[observation_key] = timestamp

    async def _trigger_correlation_detection(self, observation_key: str) -> None:
        """Trigger correlation detection for specific metric"""
        try:
            observations = list(self.observations[observation_key])
            if len(observations) < 10:  # Need minimum observations
                return

            # Filter to detection window
            cutoff_time = datetime.now(timezone.utc) - self.detection_window
            recent_observations = [
                obs for obs in observations if obs.timestamp >= cutoff_time
            ]

            if len(recent_observations) < 5:
                return

            # Detect spurious correlations
            alerts = await self._detect_spurious_correlations(recent_observations)

            # Process alerts
            for alert in alerts:
                await self._process_alert(alert)

        except Exception as e:
            logger.error(f"Correlation detection failed for {observation_key}: {e}")

    async def _detect_spurious_correlations(
        self, observations: List[MetricObservation]
    ) -> List[SpuriousCorrelationAlert]:
        """
        Detect spurious correlations in observations.

        Args:
            observations: List of metric observations

        Returns:
            List of spurious correlation alerts
        """
        alerts = []

        if len(observations) < 10:
            return alerts

        # Extract metric values
        metric_values = [obs.metric_value for obs in observations]

        # Test each spurious attribute type
        for spurious_attr in SpuriousAttributeType:
            correlation_strength = await self._calculate_spurious_correlation(
                observations, metric_values, spurious_attr
            )

            if (
                correlation_strength
                > self.CORRELATION_THRESHOLDS[CorrelationSeverity.LOW]
            ):
                severity = self._determine_severity(correlation_strength)

                # Check if we have enough samples for this severity level
                if len(observations) >= self.MIN_SAMPLE_SIZES[severity]:
                    alert = await self._create_correlation_alert(
                        observations, spurious_attr, correlation_strength, severity
                    )
                    if alert:
                        alerts.append(alert)

        return alerts

    async def _calculate_spurious_correlation(
        self,
        observations: List[MetricObservation],
        metric_values: List[float],
        spurious_attr: SpuriousAttributeType,
    ) -> float:
        """
        Calculate correlation between metric and spurious attribute.

        Args:
            observations: Metric observations
            metric_values: Metric values
            spurious_attr: Spurious attribute to test

        Returns:
            Correlation strength (0.0-1.0)
        """
        try:
            # Extract spurious attribute values
            spurious_values = []

            for obs in observations:
                spurious_value = await self._extract_spurious_attribute_value(
                    obs, spurious_attr
                )
                spurious_values.append(spurious_value)

            # Calculate correlation if we have valid data
            if (
                len(spurious_values) == len(metric_values)
                and len(set(spurious_values)) > 1
            ):
                try:
                    correlation = abs(
                        statistics.correlation(metric_values, spurious_values)
                    )
                    return min(1.0, correlation)
                except (statistics.StatisticsError, ValueError):
                    return 0.0

            return 0.0

        except Exception as e:
            logger.warning(
                f"Failed to calculate correlation for {spurious_attr.value}: {e}"
            )
            return 0.0

    async def _extract_spurious_attribute_value(
        self, observation: MetricObservation, spurious_attr: SpuriousAttributeType
    ) -> float:
        """
        Extract spurious attribute value from observation context.

        Args:
            observation: Metric observation
            spurious_attr: Spurious attribute type

        Returns:
            Numeric value representing the spurious attribute
        """
        context = observation.context

        if spurious_attr == SpuriousAttributeType.TEMPORAL_ARTIFACTS:
            # Time-based patterns (hour of day, day of week)
            return float(observation.timestamp.hour)

        elif spurious_attr == SpuriousAttributeType.RESPONSE_LENGTH:
            # Response length variations
            response_text = context.get("response_text", "")
            return float(len(str(response_text)))

        elif spurious_attr == SpuriousAttributeType.FORMATTING_STYLE:
            # Formatting patterns
            text = str(context.get("response_text", ""))
            formatting_score = (
                text.count("\n") * 0.1  # Newlines
                + text.count("*") * 0.2  # Markdown formatting
                + text.count("```") * 0.5  # Code blocks
            )
            return min(10.0, formatting_score)

        elif spurious_attr == SpuriousAttributeType.TECHNICAL_JARGON:
            # Technical language complexity
            text = str(context.get("response_text", "")).lower()
            technical_terms = [
                "algorithm",
                "optimization",
                "implementation",
                "architecture",
            ]
            jargon_score = sum(text.count(term) for term in technical_terms)
            return float(jargon_score)

        elif spurious_attr == SpuriousAttributeType.COMMUNICATION_STYLE:
            # Formal vs informal style
            text = str(context.get("response_text", "")).lower()
            formal_indicators = ["furthermore", "therefore", "consequently", "however"]
            informal_indicators = ["ok", "sure", "yeah", "btw"]

            formal_score = sum(text.count(word) for word in formal_indicators)
            informal_score = sum(text.count(word) for word in informal_indicators)

            return float(formal_score - informal_score + 5)  # Normalize around 5

        elif spurious_attr == SpuriousAttributeType.AGENT_PERSONALITY:
            # Agent personality variations
            agent_id = context.get("agent_id", "default")
            return float(hash(agent_id) % 100) / 100.0

        else:
            # Default: extract any numeric value from context
            for key, value in context.items():
                if isinstance(value, (int, float)):
                    return float(value)
            return 0.0

    def _determine_severity(self, correlation_strength: float) -> CorrelationSeverity:
        """Determine severity level based on correlation strength"""
        if (
            correlation_strength
            >= self.CORRELATION_THRESHOLDS[CorrelationSeverity.CRITICAL]
        ):
            return CorrelationSeverity.CRITICAL
        elif (
            correlation_strength
            >= self.CORRELATION_THRESHOLDS[CorrelationSeverity.HIGH]
        ):
            return CorrelationSeverity.HIGH
        elif (
            correlation_strength
            >= self.CORRELATION_THRESHOLDS[CorrelationSeverity.MEDIUM]
        ):
            return CorrelationSeverity.MEDIUM
        elif (
            correlation_strength >= self.CORRELATION_THRESHOLDS[CorrelationSeverity.LOW]
        ):
            return CorrelationSeverity.LOW
        else:
            return CorrelationSeverity.NEGLIGIBLE

    async def _create_correlation_alert(
        self,
        observations: List[MetricObservation],
        spurious_attr: SpuriousAttributeType,
        correlation_strength: float,
        severity: CorrelationSeverity,
    ) -> Optional[SpuriousCorrelationAlert]:
        """Create spurious correlation alert"""

        if not observations:
            return None

        first_obs = observations[0]
        alert_id = str(uuid4())

        # Calculate statistical significance (simplified)
        sample_size = len(observations)
        statistical_significance = max(
            0.0, 1.0 - (correlation_strength * sample_size / 100.0)
        )

        # Generate mitigation suggestions
        mitigation_suggestions = self._generate_mitigation_suggestions(
            spurious_attr, correlation_strength, severity
        )

        # Determine urgency
        urgency_level = (
            "critical"
            if severity == CorrelationSeverity.CRITICAL
            else "high" if severity == CorrelationSeverity.HIGH else "medium"
        )

        alert = SpuriousCorrelationAlert(
            alert_id=alert_id,
            service_name=first_obs.service_name,
            metric_name=first_obs.metric_name,
            spurious_attribute=spurious_attr,
            correlation_strength=correlation_strength,
            severity=severity,
            detection_timestamp=datetime.now(timezone.utc),
            sample_size=sample_size,
            statistical_significance=statistical_significance,
            confidence_interval=(
                correlation_strength - 0.1,
                correlation_strength + 0.1,
            ),
            recent_examples=[
                {
                    "timestamp": obs.timestamp.isoformat(),
                    "metric_value": obs.metric_value,
                    "context_sample": {k: v for k, v in list(obs.context.items())[:3]},
                }
                for obs in observations[-3:]  # Last 3 examples
            ],
            mitigation_suggestions=mitigation_suggestions,
            urgency_level=urgency_level,
        )

        return alert

    def _generate_mitigation_suggestions(
        self,
        spurious_attr: SpuriousAttributeType,
        correlation_strength: float,
        severity: CorrelationSeverity,
    ) -> List[str]:
        """Generate mitigation suggestions for spurious correlation"""

        suggestions = []

        # General suggestions
        if severity in [CorrelationSeverity.CRITICAL, CorrelationSeverity.HIGH]:
            suggestions.append(
                "Implement CARMA-style neutral augmentations for this attribute"
            )
            suggestions.append(
                "Add regularization to reduce spurious correlation sensitivity"
            )

        # Attribute-specific suggestions
        if spurious_attr == SpuriousAttributeType.TEMPORAL_ARTIFACTS:
            suggestions.extend(
                [
                    "Implement time-invariant evaluation protocols",
                    "Add temporal data augmentation to training pipeline",
                    "Use rolling baselines instead of fixed time comparisons",
                ]
            )

        elif spurious_attr == SpuriousAttributeType.RESPONSE_LENGTH:
            suggestions.extend(
                [
                    "Normalize metrics by response complexity rather than length",
                    "Implement length-invariant quality assessment",
                    "Add response length randomization to training data",
                ]
            )

        elif spurious_attr == SpuriousAttributeType.FORMATTING_STYLE:
            suggestions.extend(
                [
                    "Implement format-agnostic content evaluation",
                    "Add diverse formatting styles to training data",
                    "Use content-based rather than format-based quality metrics",
                ]
            )

        elif spurious_attr == SpuriousAttributeType.TECHNICAL_JARGON:
            suggestions.extend(
                [
                    "Implement domain-adaptive language evaluation",
                    "Balance technical and accessible language in training",
                    "Use semantic rather than lexical quality assessment",
                ]
            )

        elif spurious_attr == SpuriousAttributeType.AGENT_PERSONALITY:
            suggestions.extend(
                [
                    "Implement personality-invariant performance evaluation",
                    "Add diverse agent personality training scenarios",
                    "Use task-focused rather than style-focused metrics",
                ]
            )

        # Add constitutional compliance reminder
        suggestions.append(
            f"Ensure all mitigation maintains constitutional hash cdd01ef066bc6cf2"
        )

        return suggestions

    async def _process_alert(self, alert: SpuriousCorrelationAlert) -> None:
        """Process and log spurious correlation alert"""

        alert_key = (
            f"{alert.service_name}:{alert.metric_name}:{alert.spurious_attribute.value}"
        )

        # Check if this is a duplicate of recent alert
        if alert_key in self.active_alerts:
            existing_alert = self.active_alerts[alert_key]
            time_since_last = (
                alert.detection_timestamp - existing_alert.detection_timestamp
            )

            # Only process if significant time has passed or severity increased
            if (
                time_since_last < timedelta(minutes=30)
                and alert.severity.value <= existing_alert.severity.value
            ):
                return

        # Store as active alert
        self.active_alerts[alert_key] = alert

        # Log alert
        logger.warning(
            f"Spurious correlation detected: {alert.service_name}/{alert.metric_name} "
            f"correlates with {alert.spurious_attribute.value} "
            f"(strength: {alert.correlation_strength:.3f}, severity: {alert.severity.value})"
        )

        # Update statistics
        self.detection_stats["correlations_detected"] += 1
        if alert.severity == CorrelationSeverity.CRITICAL:
            self.detection_stats["system_interventions"] += 1

    async def analyze_system_robustness(
        self, time_window_minutes: int = 60
    ) -> SpuriousCorrelationDetectionResult:
        """
        Analyze overall system robustness against spurious correlations.

        Args:
            time_window_minutes: Analysis time window

        Returns:
            Comprehensive detection result
        """
        detection_id = str(uuid4())
        analysis_window = timedelta(minutes=time_window_minutes)
        cutoff_time = datetime.now(timezone.utc) - analysis_window

        # Filter recent alerts
        recent_alerts = [
            alert
            for alert in self.active_alerts.values()
            if alert.detection_timestamp >= cutoff_time
        ]

        # Calculate severity distribution
        critical_count = len(
            [a for a in recent_alerts if a.severity == CorrelationSeverity.CRITICAL]
        )
        high_count = len(
            [a for a in recent_alerts if a.severity == CorrelationSeverity.HIGH]
        )

        # Calculate system robustness impact
        if not recent_alerts:
            robustness_impact = 0.0
        else:
            # Weight by severity
            severity_weights = {
                CorrelationSeverity.CRITICAL: 1.0,
                CorrelationSeverity.HIGH: 0.6,
                CorrelationSeverity.MEDIUM: 0.3,
                CorrelationSeverity.LOW: 0.1,
            }

            total_impact = sum(
                severity_weights.get(alert.severity, 0.0) for alert in recent_alerts
            )
            robustness_impact = min(1.0, total_impact / 10.0)  # Normalize

        # Generate system-wide recommendations
        recommended_actions = []
        if critical_count > 0:
            recommended_actions.append(
                "CRITICAL: Implement immediate spurious correlation mitigation"
            )
        if high_count > 2:
            recommended_actions.append(
                "Deploy CARMA robustness framework across affected services"
            )
        if len(recent_alerts) > 5:
            recommended_actions.append(
                "Review and update system robustness monitoring thresholds"
            )

        # Count total observations analyzed
        total_observations = sum(
            len(obs_deque) for obs_deque in self.observations.values()
        )

        result = SpuriousCorrelationDetectionResult(
            detection_id=detection_id,
            total_correlations_detected=len(recent_alerts),
            critical_correlations=critical_count,
            high_correlations=high_count,
            alerts=recent_alerts,
            analysis_window=analysis_window,
            observations_analyzed=total_observations,
            system_robustness_impact=robustness_impact,
            recommended_actions=recommended_actions,
        )

        # Store in detection history
        self.detection_history.append(result)
        self.detection_stats["total_detections"] += 1

        return result

    def get_detection_statistics(self) -> Dict[str, Any]:
        """Get detection statistics and status"""

        active_alerts_by_severity = defaultdict(int)
        for alert in self.active_alerts.values():
            active_alerts_by_severity[alert.severity.value] += 1

        return {
            "detection_statistics": self.detection_stats,
            "active_alerts": {
                "total": len(self.active_alerts),
                "by_severity": dict(active_alerts_by_severity),
            },
            "observations_tracked": {
                metric_key: len(obs_deque)
                for metric_key, obs_deque in self.observations.items()
            },
            "detection_history_size": len(self.detection_history),
            "constitutional_hash": "cdd01ef066bc6cf2",
            "detector_version": "1.0.0_carma_inspired",
        }
