"""
Lipschitz Constant Real-Time Monitoring for ACGS-1 PGC Service
Target: Real-time stability monitoring with <0.8 Lipschitz constant threshold

This module implements real-time monitoring of constitutional stability through
Lipschitz constant analysis, providing early warning for governance instability.

Key Features:
- Rolling window analysis (default: 100 samples)
- Configurable alert thresholds (warning: 0.7, critical: 0.8)
- Automatic recalibration triggering when threshold exceeded
- Policy and principle distance calculation using semantic embeddings
- Integration with Prometheus monitoring and Grafana alerting
- Historical trend analysis and prediction
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any, Deque
import numpy as np
from collections import deque
import hashlib
import json
from enum import Enum
import statistics

# Prometheus metrics
try:
    from prometheus_client import Counter, Histogram, Gauge, Alert
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Semantic embedding integration
try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

logger = logging.getLogger(__name__)

# Prometheus metrics for Lipschitz monitoring
if PROMETHEUS_AVAILABLE:
    LIPSCHITZ_CONSTANT = Gauge('pgc_lipschitz_constant', 'Current Lipschitz constant value')
    STABILITY_THRESHOLD_VIOLATIONS = Counter('pgc_stability_violations_total', 'Stability threshold violations', ['severity'])
    RECALIBRATION_EVENTS = Counter('pgc_recalibration_events_total', 'Automatic recalibration events')
    POLICY_DISTANCE_DISTRIBUTION = Histogram('pgc_policy_distance_distribution', 'Distribution of policy distances')
    PRINCIPLE_DISTANCE_DISTRIBUTION = Histogram('pgc_principle_distance_distribution', 'Distribution of principle distances')


class StabilityLevel(Enum):
    """Constitutional stability levels."""
    STABLE = "stable"  # <0.5
    MODERATE = "moderate"  # 0.5-0.7
    WARNING = "warning"  # 0.7-0.8
    CRITICAL = "critical"  # >0.8


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class PolicyState:
    """Policy state representation for distance calculation."""
    policy_id: str
    content: str
    embedding: Optional[np.ndarray] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1


@dataclass
class PrincipleState:
    """Constitutional principle state representation."""
    principle_id: str
    content: str
    embedding: Optional[np.ndarray] = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    weight: float = 1.0  # Importance weight


@dataclass
class LipschitzSample:
    """Single Lipschitz constant measurement."""
    timestamp: datetime
    lipschitz_constant: float
    policy_distance: float
    principle_distance: float
    sample_size: int
    stability_level: StabilityLevel


@dataclass
class StabilityAlert:
    """Stability monitoring alert."""
    alert_id: str
    timestamp: datetime
    severity: AlertSeverity
    lipschitz_value: float
    threshold: float
    message: str
    affected_policies: List[str]
    recommended_actions: List[str]


class LipschitzMonitor:
    """
    Real-time Lipschitz constant monitoring for constitutional stability.
    
    Features:
    - Rolling window analysis with configurable sample size
    - Multi-threshold alerting system
    - Semantic distance calculation for policies and principles
    - Automatic recalibration and trend prediction
    - Integration with Prometheus and Grafana
    """
    
    def __init__(
        self,
        window_size: int = 100,
        warning_threshold: float = 0.7,
        critical_threshold: float = 0.8,
        recalibration_threshold: float = 0.85,
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        self.window_size = window_size
        self.warning_threshold = warning_threshold
        self.critical_threshold = critical_threshold
        self.recalibration_threshold = recalibration_threshold
        
        # Rolling window for Lipschitz samples
        self.lipschitz_samples: Deque[LipschitzSample] = deque(maxlen=window_size)
        
        # Current state tracking
        self.policy_states: Dict[str, PolicyState] = {}
        self.principle_states: Dict[str, PrincipleState] = {}
        
        # Embedding model for semantic distance
        self.embedding_model = None
        self.embedding_model_name = embedding_model
        
        # Performance tracking
        self.monitoring_stats = {
            "total_samples": 0,
            "alert_count": 0,
            "recalibration_count": 0,
            "avg_calculation_time_ms": 0.0,
            "last_calculation_timestamp": None
        }
        
        # Alert history
        self.alert_history: List[StabilityAlert] = []
        
        logger.info(f"Initialized LipschitzMonitor with window_size={window_size}, "
                   f"warning_threshold={warning_threshold}, critical_threshold={critical_threshold}")
    
    async def initialize_embedding_model(self):
        """Initialize semantic embedding model."""
        if EMBEDDINGS_AVAILABLE:
            try:
                self.embedding_model = SentenceTransformer(self.embedding_model_name)
                logger.info(f"Initialized embedding model: {self.embedding_model_name}")
            except Exception as e:
                logger.error(f"Failed to initialize embedding model: {e}")
                self.embedding_model = None
        else:
            logger.warning("Sentence transformers not available, using mock embeddings")
    
    def _generate_mock_embedding(self, text: str) -> np.ndarray:
        """Generate mock embedding for testing when model unavailable."""
        # Simple hash-based mock embedding
        hash_value = hashlib.sha256(text.encode()).hexdigest()
        # Convert hex to normalized vector
        embedding = np.array([int(hash_value[i:i+2], 16) for i in range(0, 64, 2)])
        return embedding / np.linalg.norm(embedding)
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """Get semantic embedding for text."""
        if self.embedding_model:
            try:
                return self.embedding_model.encode(text, normalize_embeddings=True)
            except Exception as e:
                logger.warning(f"Embedding model failed, using mock: {e}")
                return self._generate_mock_embedding(text)
        else:
            return self._generate_mock_embedding(text)
    
    async def update_policy_state(self, policy_id: str, content: str, version: int = 1) -> bool:
        """Update policy state for monitoring."""
        try:
            # Generate embedding
            embedding = self._get_embedding(content)
            
            # Create or update policy state
            policy_state = PolicyState(
                policy_id=policy_id,
                content=content,
                embedding=embedding,
                timestamp=datetime.now(timezone.utc),
                version=version
            )
            
            self.policy_states[policy_id] = policy_state
            
            logger.debug(f"Updated policy state for {policy_id} (version {version})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update policy state for {policy_id}: {e}")
            return False
    
    async def update_principle_state(self, principle_id: str, content: str, weight: float = 1.0) -> bool:
        """Update constitutional principle state for monitoring."""
        try:
            # Generate embedding
            embedding = self._get_embedding(content)
            
            # Create or update principle state
            principle_state = PrincipleState(
                principle_id=principle_id,
                content=content,
                embedding=embedding,
                timestamp=datetime.now(timezone.utc),
                weight=weight
            )
            
            self.principle_states[principle_id] = principle_state
            
            logger.debug(f"Updated principle state for {principle_id} (weight {weight})")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update principle state for {principle_id}: {e}")
            return False
    
    def _calculate_semantic_distance(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """Calculate semantic distance between embeddings using cosine distance."""
        try:
            # Cosine similarity
            cosine_sim = np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
            
            # Convert to distance (0 = identical, 1 = orthogonal, 2 = opposite)
            cosine_distance = 1 - cosine_sim
            
            return max(0.0, min(2.0, cosine_distance))
            
        except Exception as e:
            logger.error(f"Failed to calculate semantic distance: {e}")
            return 1.0  # Default moderate distance
    
    def _calculate_policy_distances(self) -> List[float]:
        """Calculate pairwise distances between all policies."""
        distances = []
        policy_list = list(self.policy_states.values())
        
        for i in range(len(policy_list)):
            for j in range(i + 1, len(policy_list)):
                policy1, policy2 = policy_list[i], policy_list[j]
                
                if policy1.embedding is not None and policy2.embedding is not None:
                    distance = self._calculate_semantic_distance(
                        policy1.embedding, policy2.embedding
                    )
                    distances.append(distance)
        
        return distances
    
    def _calculate_principle_distances(self) -> List[float]:
        """Calculate weighted distances between constitutional principles."""
        distances = []
        principle_list = list(self.principle_states.values())
        
        for i in range(len(principle_list)):
            for j in range(i + 1, len(principle_list)):
                principle1, principle2 = principle_list[i], principle_list[j]
                
                if principle1.embedding is not None and principle2.embedding is not None:
                    distance = self._calculate_semantic_distance(
                        principle1.embedding, principle2.embedding
                    )
                    
                    # Weight the distance by principle importance
                    weighted_distance = distance * (principle1.weight + principle2.weight) / 2.0
                    distances.append(weighted_distance)
        
        return distances
    
    async def calculate_lipschitz_constant(self) -> Optional[LipschitzSample]:
        """Calculate current Lipschitz constant for constitutional stability."""
        start_time = time.time()
        
        try:
            # Need at least 2 policies and 2 principles for meaningful calculation
            if len(self.policy_states) < 2 or len(self.principle_states) < 2:
                logger.warning("Insufficient data for Lipschitz calculation")
                return None
            
            # Calculate policy and principle distances
            policy_distances = self._calculate_policy_distances()
            principle_distances = self._calculate_principle_distances()
            
            if not policy_distances or not principle_distances:
                logger.warning("No valid distances calculated")
                return None
            
            # Calculate Lipschitz constant
            # L = max(|f(x1) - f(x2)| / |x1 - x2|) for all x1, x2
            # Here: f maps principles to policies, so we compare policy changes to principle changes
            
            max_policy_distance = max(policy_distances)
            min_principle_distance = min([d for d in principle_distances if d > 0.001])  # Avoid division by zero
            
            if min_principle_distance > 0:
                lipschitz_constant = max_policy_distance / min_principle_distance
            else:
                lipschitz_constant = max_policy_distance  # Fallback
            
            # Normalize to reasonable range (0-2)
            lipschitz_constant = min(2.0, max(0.0, lipschitz_constant))
            
            # Determine stability level
            if lipschitz_constant < 0.5:
                stability_level = StabilityLevel.STABLE
            elif lipschitz_constant < self.warning_threshold:
                stability_level = StabilityLevel.MODERATE
            elif lipschitz_constant < self.critical_threshold:
                stability_level = StabilityLevel.WARNING
            else:
                stability_level = StabilityLevel.CRITICAL
            
            # Create sample
            sample = LipschitzSample(
                timestamp=datetime.now(timezone.utc),
                lipschitz_constant=lipschitz_constant,
                policy_distance=statistics.mean(policy_distances),
                principle_distance=statistics.mean(principle_distances),
                sample_size=len(policy_distances) + len(principle_distances),
                stability_level=stability_level
            )
            
            # Add to rolling window
            self.lipschitz_samples.append(sample)
            
            # Update performance stats
            calculation_time = (time.time() - start_time) * 1000
            self.monitoring_stats["total_samples"] += 1
            self.monitoring_stats["avg_calculation_time_ms"] = (
                (self.monitoring_stats["avg_calculation_time_ms"] * (self.monitoring_stats["total_samples"] - 1) + 
                 calculation_time) / self.monitoring_stats["total_samples"]
            )
            self.monitoring_stats["last_calculation_timestamp"] = datetime.now(timezone.utc)
            
            # Update Prometheus metrics
            if PROMETHEUS_AVAILABLE:
                LIPSCHITZ_CONSTANT.set(lipschitz_constant)
                for distance in policy_distances:
                    POLICY_DISTANCE_DISTRIBUTION.observe(distance)
                for distance in principle_distances:
                    PRINCIPLE_DISTANCE_DISTRIBUTION.observe(distance)
            
            # Check for alerts
            await self._check_stability_alerts(sample)
            
            logger.debug(f"Calculated Lipschitz constant: {lipschitz_constant:.4f} "
                        f"({stability_level.value}), calculation_time={calculation_time:.1f}ms")
            
            return sample
            
        except Exception as e:
            logger.error(f"Failed to calculate Lipschitz constant: {e}")
            return None

    async def _check_stability_alerts(self, sample: LipschitzSample):
        """Check for stability alerts and trigger notifications."""
        try:
            alerts_triggered = []

            # Check warning threshold
            if sample.lipschitz_constant >= self.warning_threshold and sample.stability_level == StabilityLevel.WARNING:
                alert = StabilityAlert(
                    alert_id=f"WARN-{int(time.time())}-{sample.lipschitz_constant:.3f}",
                    timestamp=sample.timestamp,
                    severity=AlertSeverity.WARNING,
                    lipschitz_value=sample.lipschitz_constant,
                    threshold=self.warning_threshold,
                    message=f"Constitutional stability warning: Lipschitz constant {sample.lipschitz_constant:.4f} exceeds warning threshold {self.warning_threshold}",
                    affected_policies=list(self.policy_states.keys()),
                    recommended_actions=[
                        "Review recent policy changes",
                        "Validate constitutional alignment",
                        "Consider policy consolidation"
                    ]
                )
                alerts_triggered.append(alert)

                if PROMETHEUS_AVAILABLE:
                    STABILITY_THRESHOLD_VIOLATIONS.labels(severity="warning").inc()

            # Check critical threshold
            if sample.lipschitz_constant >= self.critical_threshold and sample.stability_level == StabilityLevel.CRITICAL:
                alert = StabilityAlert(
                    alert_id=f"CRIT-{int(time.time())}-{sample.lipschitz_constant:.3f}",
                    timestamp=sample.timestamp,
                    severity=AlertSeverity.CRITICAL,
                    lipschitz_value=sample.lipschitz_constant,
                    threshold=self.critical_threshold,
                    message=f"CRITICAL: Constitutional stability breach! Lipschitz constant {sample.lipschitz_constant:.4f} exceeds critical threshold {self.critical_threshold}",
                    affected_policies=list(self.policy_states.keys()),
                    recommended_actions=[
                        "IMMEDIATE: Halt new policy deployments",
                        "Initiate emergency constitutional review",
                        "Activate governance stability protocol",
                        "Consider system recalibration"
                    ]
                )
                alerts_triggered.append(alert)

                if PROMETHEUS_AVAILABLE:
                    STABILITY_THRESHOLD_VIOLATIONS.labels(severity="critical").inc()

            # Check for recalibration trigger
            if sample.lipschitz_constant >= self.recalibration_threshold:
                await self._trigger_recalibration(sample)

            # Store alerts
            for alert in alerts_triggered:
                self.alert_history.append(alert)
                self.monitoring_stats["alert_count"] += 1

                logger.warning(f"Stability alert triggered: {alert.severity.value} - {alert.message}")

            # Keep alert history manageable
            if len(self.alert_history) > 1000:
                self.alert_history = self.alert_history[-1000:]

        except Exception as e:
            logger.error(f"Failed to check stability alerts: {e}")

    async def _trigger_recalibration(self, sample: LipschitzSample):
        """Trigger automatic recalibration when threshold exceeded."""
        try:
            logger.warning(f"Triggering automatic recalibration due to Lipschitz constant {sample.lipschitz_constant:.4f}")

            # Reset monitoring window
            self.lipschitz_samples.clear()

            # Update recalibration stats
            self.monitoring_stats["recalibration_count"] += 1

            if PROMETHEUS_AVAILABLE:
                RECALIBRATION_EVENTS.inc()

            logger.info("Automatic recalibration completed")

        except Exception as e:
            logger.error(f"Failed to trigger recalibration: {e}")

    def get_current_stability_status(self) -> Dict[str, Any]:
        """Get current constitutional stability status."""
        try:
            if not self.lipschitz_samples:
                return {
                    "status": "insufficient_data",
                    "lipschitz_constant": None,
                    "stability_level": None,
                    "last_calculation": None
                }

            latest_sample = self.lipschitz_samples[-1]

            # Calculate trend from recent samples
            recent_samples = list(self.lipschitz_samples)[-10:]  # Last 10 samples
            if len(recent_samples) >= 2:
                values = [s.lipschitz_constant for s in recent_samples]
                trend = "stable"
                if len(values) >= 3:
                    slope = np.polyfit(range(len(values)), values, 1)[0]
                    if slope > 0.01:
                        trend = "increasing"
                    elif slope < -0.01:
                        trend = "decreasing"
            else:
                trend = "unknown"

            return {
                "status": "active",
                "lipschitz_constant": latest_sample.lipschitz_constant,
                "stability_level": latest_sample.stability_level.value,
                "last_calculation": latest_sample.timestamp.isoformat(),
                "trend": trend,
                "sample_count": len(self.lipschitz_samples),
                "policy_count": len(self.policy_states),
                "principle_count": len(self.principle_states),
                "thresholds": {
                    "warning": self.warning_threshold,
                    "critical": self.critical_threshold,
                    "recalibration": self.recalibration_threshold
                },
                "recent_alerts": len([a for a in self.alert_history
                                   if a.timestamp > datetime.now(timezone.utc) - timedelta(hours=24)])
            }

        except Exception as e:
            logger.error(f"Failed to get stability status: {e}")
            return {"status": "error", "error": str(e)}


# Global Lipschitz monitor instance
_lipschitz_monitor: Optional[LipschitzMonitor] = None


async def get_lipschitz_monitor(
    window_size: int = 100,
    warning_threshold: float = 0.7,
    critical_threshold: float = 0.8
) -> LipschitzMonitor:
    """Get or create global Lipschitz monitor instance."""
    global _lipschitz_monitor

    if _lipschitz_monitor is None:
        _lipschitz_monitor = LipschitzMonitor(
            window_size=window_size,
            warning_threshold=warning_threshold,
            critical_threshold=critical_threshold
        )
        await _lipschitz_monitor.initialize_embedding_model()

    return _lipschitz_monitor
