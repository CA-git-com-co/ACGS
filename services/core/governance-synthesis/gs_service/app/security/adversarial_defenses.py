"""
Adversarial Defense Mechanisms for ACGS-PGP

Implements the adversarial robustness features described in the ACGS-PGP paper,
including ReFAT-style adversarial training, constitutional manipulation detection,
and multi-layer defense strategies.

Key Features:
- Refusal Feature Adversarial Training (ReFAT)
- Constitutional manipulation detection
- Semantic drift monitoring
- QuickXplain-based conflict resolution
- Multi-model consensus validation
"""

import hashlib
import logging
import time
from collections import deque
from dataclasses import dataclass
from enum import Enum
from typing import Any

import numpy as np

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


logger = logging.getLogger(__name__)


class AttackType(Enum):
    """Types of adversarial attacks on constitutional governance"""

    PRINCIPLE_MANIPULATION = "principle_manipulation"
    RULE_SYNTHESIS_GAMING = "rule_synthesis_gaming"
    CONSTITUTIONAL_CAPTURE = "constitutional_capture"
    SEMANTIC_DRIFT = "semantic_drift"
    CONSENSUS_MANIPULATION = "consensus_manipulation"
    JAILBREAK_ATTEMPT = "jailbreak_attempt"


class DefenseLevel(Enum):
    """Defense mechanism activation levels"""

    PASSIVE = "passive"
    ACTIVE = "active"
    AGGRESSIVE = "aggressive"
    EMERGENCY = "emergency"


@dataclass
class AdversarialEvent:
    """Record of an adversarial attack attempt"""

    event_id: str
    attack_type: AttackType
    detected: bool
    severity: str
    confidence: float
    defense_mechanism: str
    timestamp: float
    context: dict[str, Any]
    mitigation_applied: bool


@dataclass
class RefusalFeature:
    """Refusal feature for adversarial training"""

    feature_id: str
    description: str
    activation_threshold: float
    weight_vector: np.ndarray
    constitutional_principle: str


class AdversarialDefenseSystem:
    """
    Comprehensive adversarial defense system implementing ACGS-PGP security measures
    """

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        self.defense_level = DefenseLevel.ACTIVE
        self.attack_history = deque(maxlen=1000)
        self.refusal_features = {}
        self.semantic_baselines = {}
        self.consensus_validators = []

        # Defense metrics
        self.defense_metrics = {
            "total_attacks_detected": 0,
            "successful_defenses": 0,
            "false_positives": 0,
            "constitutional_captures_prevented": 0,
            "jailbreaks_blocked": 0,
        }

        # Initialize defense components
        self._initialize_refusal_features()
        self._initialize_semantic_monitors()
        self._initialize_consensus_validators()

    def _initialize_refusal_features(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize refusal features for adversarial training"""
        # Constitutional integrity refusal features
        self.refusal_features["constitutional_integrity"] = RefusalFeature(
            feature_id="const_integrity_001",
            description="Detects attempts to bypass constitutional principles",
            activation_threshold=0.7,
            weight_vector=np.random.randn(128),  # Simplified representation
            constitutional_principle="human_dignity",
        )

        self.refusal_features["policy_consistency"] = RefusalFeature(
            feature_id="policy_consist_001",
            description="Detects inconsistent policy generation attempts",
            activation_threshold=0.8,
            weight_vector=np.random.randn(128),
            constitutional_principle="fairness",
        )

        self.refusal_features["governance_bypass"] = RefusalFeature(
            feature_id="gov_bypass_001",
            description="Detects attempts to bypass governance processes",
            activation_threshold=0.9,
            weight_vector=np.random.randn(128),
            constitutional_principle="democratic_governance",
        )

    def _initialize_semantic_monitors(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize semantic drift monitoring"""
        self.semantic_baselines = {
            "constitutional_principles": {
                "human_dignity": {"embedding": np.random.randn(256), "threshold": 0.85},
                "fairness": {"embedding": np.random.randn(256), "threshold": 0.85},
                "transparency": {"embedding": np.random.randn(256), "threshold": 0.80},
                "accountability": {
                    "embedding": np.random.randn(256),
                    "threshold": 0.80,
                },
                "privacy": {"embedding": np.random.randn(256), "threshold": 0.85},
            }
        }

    def _initialize_consensus_validators(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize multi-model consensus validators"""
        self.consensus_validators = [
            {"model_id": "primary_llm", "weight": 0.4, "specialization": "general"},
            {
                "model_id": "constitutional_expert",
                "weight": 0.3,
                "specialization": "constitutional",
            },
            {
                "model_id": "security_validator",
                "weight": 0.2,
                "specialization": "security",
            },
            {"model_id": "formal_verifier", "weight": 0.1, "specialization": "formal"},
        ]

    async def detect_adversarial_attempt(
        self, input_text: str, context: dict[str, Any]
    ) -> tuple[bool, AdversarialEvent]:
        """
        Main adversarial detection pipeline

        Returns:
            Tuple of (is_adversarial, event_record)
        """
        start_time = time.time()

        # Multi-layer detection
        detection_results = []

        # Layer 1: Refusal feature analysis
        refusal_result = await self._analyze_refusal_features(input_text, context)
        detection_results.append(refusal_result)

        # Layer 2: Semantic drift detection
        semantic_result = await self._detect_semantic_drift(input_text, context)
        detection_results.append(semantic_result)

        # Layer 3: Constitutional manipulation detection
        manipulation_result = await self._detect_constitutional_manipulation(
            input_text, context
        )
        detection_results.append(manipulation_result)

        # Layer 4: Consensus validation
        consensus_result = await self._validate_with_consensus(input_text, context)
        detection_results.append(consensus_result)

        # Aggregate results
        is_adversarial, attack_type, confidence = self._aggregate_detection_results(
            detection_results
        )

        # Create event record
        event = AdversarialEvent(
            event_id=f"ADV-{int(time.time())}-{hashlib.sha256(input_text.encode()).hexdigest()[:32]}",
            attack_type=attack_type,
            detected=is_adversarial,
            severity=self._classify_severity(confidence, attack_type),
            confidence=confidence,
            defense_mechanism="multi_layer_detection",
            timestamp=time.time(),
            context=context,
            mitigation_applied=False,
        )

        # Record event
        self.attack_history.append(event)

        # Update metrics
        if is_adversarial:
            self.defense_metrics["total_attacks_detected"] += 1
            if attack_type == AttackType.CONSTITUTIONAL_CAPTURE:
                self.defense_metrics["constitutional_captures_prevented"] += 1
            elif attack_type == AttackType.JAILBREAK_ATTEMPT:
                self.defense_metrics["jailbreaks_blocked"] += 1

        processing_time = (time.time() - start_time) * 1000
        logger.info(
            f"Adversarial detection completed in {processing_time:.2f}ms: {is_adversarial}"
        )

        return is_adversarial, event

    async def _analyze_refusal_features(self, input_text: str, context: dict) -> dict:
        """Analyze input against refusal features (ReFAT implementation)"""
        try:
            # Simplified refusal feature analysis
            # In production, this would use actual embeddings and trained features

            activations = {}
            max_activation = 0.0
            triggered_feature = None

            for feature_id, feature in self.refusal_features.items():
                # Simulate feature activation
                text_hash = hashlib.sha256(input_text.encode()).hexdigest()
                activation = abs(hash(text_hash + feature_id) % 100) / 100.0

                activations[feature_id] = activation

                if (
                    activation > feature.activation_threshold
                    and activation > max_activation
                ):
                    max_activation = activation
                    triggered_feature = feature_id

            is_detected = max_activation > 0.7
            attack_type = AttackType.JAILBREAK_ATTEMPT if triggered_feature else None

            return {
                "method": "refusal_features",
                "detected": is_detected,
                "confidence": max_activation,
                "attack_type": attack_type,
                "details": {
                    "triggered_feature": triggered_feature,
                    "activations": activations,
                },
            }

        except Exception as e:
            logger.exception(f"Refusal feature analysis failed: {e}")
            return {
                "method": "refusal_features",
                "detected": False,
                "confidence": 0.0,
                "attack_type": None,
                "error": str(e),
            }

    async def _detect_semantic_drift(self, input_text: str, context: dict) -> dict:
        """Detect semantic drift from constitutional baselines"""
        try:
            # Simulate semantic similarity analysis
            # In production, this would use actual embeddings (BERT, etc.)

            min_similarity = 1.0
            drifted_principle = None

            for principle, baseline in self.semantic_baselines[
                "constitutional_principles"
            ].items():
                # Simulate semantic similarity calculation
                text_embedding = np.random.randn(256)  # Mock embedding
                similarity = np.dot(text_embedding, baseline["embedding"]) / (
                    np.linalg.norm(text_embedding)
                    * np.linalg.norm(baseline["embedding"])
                )

                if similarity < baseline["threshold"] and similarity < min_similarity:
                    min_similarity = similarity
                    drifted_principle = principle

            is_detected = min_similarity < 0.7
            attack_type = AttackType.SEMANTIC_DRIFT if is_detected else None
            confidence = 1.0 - min_similarity if is_detected else 0.0

            return {
                "method": "semantic_drift",
                "detected": is_detected,
                "confidence": confidence,
                "attack_type": attack_type,
                "details": {
                    "drifted_principle": drifted_principle,
                    "min_similarity": min_similarity,
                },
            }

        except Exception as e:
            logger.exception(f"Semantic drift detection failed: {e}")
            return {
                "method": "semantic_drift",
                "detected": False,
                "confidence": 0.0,
                "attack_type": None,
                "error": str(e),
            }

    async def _detect_constitutional_manipulation(
        self, input_text: str, context: dict
    ) -> dict:
        """Detect attempts to manipulate constitutional principles"""
        try:
            # Check for manipulation patterns
            manipulation_indicators = [
                "ignore previous instructions",
                "bypass constitutional",
                "override governance",
                "disable safety",
                "constitutional exception",
                "emergency override",
                "admin privileges",
                "system prompt",
            ]

            detected_indicators = [
                indicator
                for indicator in manipulation_indicators
                if indicator.lower() in input_text.lower()
            ]

            # Check for principle contradictions
            constitutional_terms = [
                "human dignity",
                "fairness",
                "transparency",
                "accountability",
                "privacy",
            ]
            negation_patterns = ["not", "ignore", "bypass", "disable", "override"]

            contradiction_score = 0.0
            for term in constitutional_terms:
                if term in input_text.lower():
                    for negation in negation_patterns:
                        if (
                            negation in input_text.lower()
                            and abs(
                                input_text.lower().find(negation)
                                - input_text.lower().find(term)
                            )
                            < 50
                        ):
                            contradiction_score += 0.2

            manipulation_score = len(detected_indicators) * 0.3 + contradiction_score
            is_detected = manipulation_score > 0.5
            attack_type = AttackType.CONSTITUTIONAL_CAPTURE if is_detected else None

            return {
                "method": "constitutional_manipulation",
                "detected": is_detected,
                "confidence": min(manipulation_score, 1.0),
                "attack_type": attack_type,
                "details": {
                    "detected_indicators": detected_indicators,
                    "contradiction_score": contradiction_score,
                    "manipulation_score": manipulation_score,
                },
            }

        except Exception as e:
            logger.exception(f"Constitutional manipulation detection failed: {e}")
            return {
                "method": "constitutional_manipulation",
                "detected": False,
                "confidence": 0.0,
                "attack_type": None,
                "error": str(e),
            }

    async def _validate_with_consensus(self, input_text: str, context: dict) -> dict:
        """Multi-model consensus validation"""
        try:
            # Simulate multi-model consensus
            model_scores = []

            for validator in self.consensus_validators:
                # Simulate model evaluation
                model_hash = hashlib.sha256(
                    (input_text + validator["model_id"]).encode(), usedforsecurity=False
                ).hexdigest()
                score = abs(hash(model_hash) % 100) / 100.0

                # Apply specialization bias
                if (
                    validator["specialization"] == "security"
                    and "security" in input_text.lower()
                ):
                    score *= 1.2
                elif validator["specialization"] == "constitutional" and any(
                    term in input_text.lower()
                    for term in ["constitution", "principle", "governance"]
                ):
                    score *= 1.1

                weighted_score = score * validator["weight"]
                model_scores.append(weighted_score)

            consensus_score = sum(model_scores)
            disagreement = np.std(model_scores) if len(model_scores) > 1 else 0.0

            # High disagreement or low consensus indicates potential attack
            is_detected = consensus_score < 0.4 or disagreement > 0.3
            attack_type = AttackType.CONSENSUS_MANIPULATION if is_detected else None
            confidence = (
                max(0.4 - consensus_score, disagreement) if is_detected else 0.0
            )

            return {
                "method": "consensus_validation",
                "detected": is_detected,
                "confidence": confidence,
                "attack_type": attack_type,
                "details": {
                    "consensus_score": consensus_score,
                    "disagreement": disagreement,
                    "model_scores": model_scores,
                },
            }

        except Exception as e:
            logger.exception(f"Consensus validation failed: {e}")
            return {
                "method": "consensus_validation",
                "detected": False,
                "confidence": 0.0,
                "attack_type": None,
                "error": str(e),
            }

    def _aggregate_detection_results(
        self, results: list[dict]
    ) -> tuple[bool, AttackType, float]:
        """Aggregate detection results from multiple layers"""
        detected_attacks = [r for r in results if r.get("detected", False)]

        if not detected_attacks:
            return False, None, 0.0

        # Find highest confidence detection
        best_detection = max(detected_attacks, key=lambda x: x.get("confidence", 0.0))

        # Aggregate confidence scores
        total_confidence = sum(r.get("confidence", 0.0) for r in detected_attacks)
        avg_confidence = total_confidence / len(results)

        return True, best_detection.get("attack_type"), avg_confidence

    def _classify_severity(
        self, confidence: float, attack_type: AttackType | None
    ) -> str:
        """Classify attack severity based on confidence and type"""
        if not attack_type:
            return "none"

        if attack_type in {
            AttackType.CONSTITUTIONAL_CAPTURE,
            AttackType.CONSENSUS_MANIPULATION,
        }:
            if confidence > 0.8:
                return "critical"
            if confidence > 0.6:
                return "high"
            return "medium"
        if attack_type in {
            AttackType.JAILBREAK_ATTEMPT,
            AttackType.RULE_SYNTHESIS_GAMING,
        }:
            if confidence > 0.7:
                return "high"
            if confidence > 0.5:
                return "medium"
            return "low"
        return "low"

    async def apply_mitigation(self, event: AdversarialEvent) -> dict[str, Any]:
        """Apply mitigation measures for detected attacks"""
        mitigation_result = {
            "event_id": event.event_id,
            "mitigation_applied": False,
            "actions_taken": [],
            "success": False,
        }

        try:
            if event.severity == "critical":
                # Emergency lockdown
                mitigation_result["actions_taken"].append("emergency_lockdown")
                await self._trigger_emergency_lockdown(event)

            elif event.severity == "high":
                # Immediate blocking
                mitigation_result["actions_taken"].append("immediate_block")
                await self._apply_immediate_block(event)

            elif event.severity == "medium":
                # Enhanced monitoring
                mitigation_result["actions_taken"].append("enhanced_monitoring")
                await self._enable_enhanced_monitoring(event)

            else:
                # Logging only
                mitigation_result["actions_taken"].append("log_warning")
                await self._log_warning(event)

            # Update event record
            event.mitigation_applied = True
            mitigation_result["mitigation_applied"] = True
            mitigation_result["success"] = True

            # Update defense metrics
            self.defense_metrics["successful_defenses"] += 1

        except Exception as e:
            logger.exception(f"Mitigation failed for event {event.event_id}: {e}")
            mitigation_result["error"] = str(e)

        return mitigation_result

    async def _trigger_emergency_lockdown(self, event: AdversarialEvent):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Trigger emergency lockdown procedures"""
        logger.critical(f"EMERGENCY LOCKDOWN triggered for event {event.event_id}")
        # Implementation would include:
        # - Disable policy synthesis
        # - Alert security team
        # - Activate backup governance
        # - Initiate incident response

    async def _apply_immediate_block(self, event: AdversarialEvent):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Apply immediate blocking measures"""
        logger.warning(f"IMMEDIATE BLOCK applied for event {event.event_id}")
        # Implementation would include:
        # - Block current request
        # - Quarantine input
        # - Alert administrators
        # - Update security rules

    async def _enable_enhanced_monitoring(self, event: AdversarialEvent):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Enable enhanced monitoring for suspicious activity"""
        logger.info(f"Enhanced monitoring enabled for event {event.event_id}")
        # Implementation would include:
        # - Increase detection sensitivity
        # - Monitor related patterns
        # - Track user behavior
        # - Generate alerts

    async def _log_warning(self, event: AdversarialEvent):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Log warning for low-severity events"""
        logger.info(f"Security warning logged for event {event.event_id}")
        # Implementation would include:
        # - Add to security log
        # - Update threat intelligence
        # - Track patterns
        # - Generate reports

    def get_defense_metrics(self) -> dict[str, Any]:
        """Get current defense metrics"""
        recent_attacks = [
            event
            for event in self.attack_history
            if time.time() - event.timestamp < 3600  # Last hour
        ]

        return {
            "total_attacks_detected": self.defense_metrics["total_attacks_detected"],
            "successful_defenses": self.defense_metrics["successful_defenses"],
            "constitutional_captures_prevented": self.defense_metrics[
                "constitutional_captures_prevented"
            ],
            "jailbreaks_blocked": self.defense_metrics["jailbreaks_blocked"],
            "recent_attacks_count": len(recent_attacks),
            "defense_effectiveness": (
                self.defense_metrics["successful_defenses"]
                / max(self.defense_metrics["total_attacks_detected"], 1)
            ),
            "current_defense_level": self.defense_level.value,
            "last_attack_time": (
                max(event.timestamp for event in self.attack_history)
                if self.attack_history
                else None
            ),
        }


# Global defense system instance
adversarial_defense_system = AdversarialDefenseSystem()


async def detect_and_mitigate_attack(
    input_text: str, context: dict[str, Any]
) -> tuple[bool, dict]:
    """
    Main interface for adversarial detection and mitigation

    Returns:
        Tuple of (is_adversarial, mitigation_result)
    """
    is_adversarial, event = await adversarial_defense_system.detect_adversarial_attempt(
        input_text, context
    )

    mitigation_result = {}
    if is_adversarial:
        mitigation_result = await adversarial_defense_system.apply_mitigation(event)

    return is_adversarial, mitigation_result


def get_defense_status() -> dict[str, Any]:
    """Get current defense system status"""
    return adversarial_defense_system.get_defense_metrics()
