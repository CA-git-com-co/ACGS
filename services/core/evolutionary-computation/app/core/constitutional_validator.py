"""
Constitutional Validator Core Module

Constitutional compliance validation for evolutionary computation processes
with integration to the ACGS constitutional AI framework.
"""

import asyncio
import logging
import time
from typing import Any, Dict, List, Optional

import aiohttp
from prometheus_client import Counter, Histogram

from ..models.evolution import Individual
from ..models.oversight import RiskAssessment, RiskLevel

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"

logger = logging.getLogger(__name__)


class ConstitutionalValidator:
    """
    Constitutional compliance validator with ACGS integration.

    Provides constitutional compliance validation for evolutionary computation
    processes with O(1) lookup patterns and sub-5ms P99 latency targets.
    """

    def __init__(self, ac_service_url: str = "http://localhost:8001"):
        """Initialize constitutional validator."""
        self.ac_service_url = ac_service_url
        self.setup_metrics()

        # Validation cache for O(1) lookups
        self.validation_cache: Dict[str, float] = {}
        self.principle_cache: Dict[str, Dict[str, Any]] = {}

        # Constitutional principles (cached for performance)
        self.core_principles = {
            "transparency": "All decisions must be explainable and auditable",
            "fairness": "Equal treatment and non-discrimination",
            "safety": "No harm to individuals or society",
            "privacy": "Protection of personal data and privacy rights",
            "accountability": "Clear responsibility and oversight",
            "human_agency": "Human oversight and control",
            "robustness": "Reliable and secure operation",
            "non_maleficence": "Do no harm principle",
        }

        logger.info("ConstitutionalValidator initialized")

    def setup_metrics(self) -> None:
        """Setup Prometheus metrics."""
        self.validation_requests_total = Counter(
            "constitutional_validation_requests_total",
            "Total constitutional validation requests",
            ["validation_type", "result"],
        )

        self.validation_duration = Histogram(
            "constitutional_validation_duration_ms",
            "Constitutional validation duration in milliseconds",
        )

        self.compliance_score_histogram = Histogram(
            "constitutional_compliance_score",
            "Constitutional compliance scores",
            buckets=[0.0, 0.5, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0],
        )

    async def validate_individual(self, individual: Individual) -> float:
        """
        Validate individual for constitutional compliance.

        Args:
            individual: Individual to validate

        Returns:
            Constitutional compliance score (0.0 to 1.0)
        """
        start_time = time.time()

        try:
            # Check cache first for O(1) performance
            cache_key = self._get_validation_cache_key(individual.genotype)
            if cache_key in self.validation_cache:
                score = self.validation_cache[cache_key]
                self.compliance_score_histogram.observe(score)
                return score

            # Perform comprehensive constitutional validation
            compliance_score = await self._perform_constitutional_validation(individual)

            # Cache result for future O(1) lookups
            self.validation_cache[cache_key] = compliance_score

            # Record metrics
            self.validation_requests_total.labels(
                validation_type="individual", result="success"
            ).inc()

            self.compliance_score_histogram.observe(compliance_score)

            return compliance_score

        except Exception as e:
            logger.error(f"Constitutional validation failed: {e}")
            self.validation_requests_total.labels(
                validation_type="individual", result="error"
            ).inc()
            return 0.0  # Fail-safe: no compliance if validation fails

        finally:
            # Record validation duration
            duration = (time.time() - start_time) * 1000
            self.validation_duration.observe(duration)

            # Ensure sub-5ms P99 latency target
            if duration > 5:
                logger.warning(
                    f"Constitutional validation took {duration:.2f}ms (>5ms target)"
                )

    async def validate_evolution_request(
        self, genotype: Dict[str, Any], evolution_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate evolution request for constitutional compliance.

        Args:
            genotype: Genetic representation to validate
            evolution_context: Context for the evolution

        Returns:
            Validation result with compliance score and details
        """
        start_time = time.time()

        try:
            # Validate against core constitutional principles
            principle_scores = {}

            for principle, description in self.core_principles.items():
                score = await self._validate_principle(genotype, principle, description)
                principle_scores[principle] = score

            # Calculate overall compliance score
            overall_score = sum(principle_scores.values()) / len(principle_scores)

            # Assess specific risks
            risk_assessment = await self._assess_constitutional_risks(
                genotype, evolution_context
            )

            # Determine if human oversight is required
            requires_oversight = (
                overall_score < 0.8
                or risk_assessment.overall_risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]
            )

            validation_result = {
                "compliance_score": overall_score,
                "principle_scores": principle_scores,
                "risk_assessment": risk_assessment,
                "requires_human_oversight": requires_oversight,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "validation_timestamp": time.time(),
            }

            self.validation_requests_total.labels(
                validation_type="evolution_request", result="success"
            ).inc()

            return validation_result

        except Exception as e:
            logger.error(f"Evolution request validation failed: {e}")
            self.validation_requests_total.labels(
                validation_type="evolution_request", result="error"
            ).inc()

            # Return fail-safe result
            return {
                "compliance_score": 0.0,
                "principle_scores": {},
                "risk_assessment": None,
                "requires_human_oversight": True,
                "constitutional_hash": CONSTITUTIONAL_HASH,
                "validation_timestamp": time.time(),
                "error": str(e),
            }

        finally:
            duration = (time.time() - start_time) * 1000
            self.validation_duration.observe(duration)

    async def _perform_constitutional_validation(self, individual: Individual) -> float:
        """Perform comprehensive constitutional validation."""
        try:
            # Call AC service for validation if available
            async with aiohttp.ClientSession() as session:
                validation_request = {
                    "genotype": individual.genotype,
                    "validation_mode": "comprehensive",
                    "constitutional_hash": CONSTITUTIONAL_HASH,
                }

                async with session.post(
                    f"{self.ac_service_url}/api/v1/constitutional/validate",
                    json=validation_request,
                    timeout=aiohttp.ClientTimeout(
                        total=2.0
                    ),  # 2s timeout for sub-5ms target
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("compliance_score", 0.0)
                    else:
                        logger.warning(f"AC service returned status {response.status}")

        except asyncio.TimeoutError:
            logger.warning("AC service timeout, using fallback validation")
        except Exception as e:
            logger.warning(f"AC service error: {e}, using fallback validation")

        # Fallback to local validation
        return await self._fallback_constitutional_validation(individual)

    async def _fallback_constitutional_validation(
        self, individual: Individual
    ) -> float:
        """Fallback constitutional validation when AC service is unavailable."""
        # Simplified local validation
        genotype = individual.genotype

        # Check for basic constitutional compliance indicators
        compliance_indicators = 0
        total_checks = 8

        # Transparency check
        if genotype.get("explainable", False) or genotype.get("transparent", False):
            compliance_indicators += 1

        # Safety check
        if genotype.get("safety_validated", False) or genotype.get(
            "harm_prevention", True
        ):
            compliance_indicators += 1

        # Fairness check
        if genotype.get("fair_treatment", True) and not genotype.get(
            "discriminatory", False
        ):
            compliance_indicators += 1

        # Privacy check
        if genotype.get("privacy_preserving", True):
            compliance_indicators += 1

        # Accountability check
        if genotype.get("auditable", True):
            compliance_indicators += 1

        # Human agency check
        if genotype.get("human_oversight", True):
            compliance_indicators += 1

        # Robustness check
        if genotype.get("robust", True) and genotype.get("secure", True):
            compliance_indicators += 1

        # Non-maleficence check
        if not genotype.get("harmful", False):
            compliance_indicators += 1

        return compliance_indicators / total_checks

    async def _validate_principle(
        self, genotype: Dict[str, Any], principle: str, description: str
    ) -> float:
        """Validate specific constitutional principle."""
        # Simplified principle validation
        principle_mapping = {
            "transparency": genotype.get("explainable", 0.8),
            "fairness": 1.0 - genotype.get("bias_score", 0.1),
            "safety": genotype.get("safety_score", 0.9),
            "privacy": genotype.get("privacy_score", 0.85),
            "accountability": genotype.get("audit_score", 0.9),
            "human_agency": genotype.get("human_control", 0.95),
            "robustness": genotype.get("robustness_score", 0.8),
            "non_maleficence": 1.0 - genotype.get("harm_potential", 0.05),
        }

        return min(1.0, max(0.0, principle_mapping.get(principle, 0.8)))

    async def _assess_constitutional_risks(
        self, genotype: Dict[str, Any], context: Dict[str, Any]
    ) -> RiskAssessment:
        """Assess constitutional risks for the evolution."""
        # Simplified risk assessment
        safety_risk = RiskLevel.LOW
        constitutional_risk = RiskLevel.LOW

        # Check for high-risk indicators
        if genotype.get("safety_score", 1.0) < 0.7:
            safety_risk = RiskLevel.HIGH

        if genotype.get("constitutional_compliance", 1.0) < 0.8:
            constitutional_risk = RiskLevel.MEDIUM

        overall_risk = max(safety_risk, constitutional_risk)

        return RiskAssessment(
            evolution_id=context.get("evolution_id", "unknown"),
            safety_risk=safety_risk,
            constitutional_risk=constitutional_risk,
            performance_risk=RiskLevel.LOW,
            security_risk=RiskLevel.LOW,
            ethical_risk=RiskLevel.LOW,
            overall_risk=overall_risk,
            risk_score=0.2 if overall_risk == RiskLevel.HIGH else 0.1,
            assessed_by="constitutional_validator",
            constitutional_hash=CONSTITUTIONAL_HASH,
        )

    def _get_validation_cache_key(self, genotype: Dict[str, Any]) -> str:
        """Generate cache key for validation result."""
        import hashlib
        import json

        # Create deterministic key from genotype
        genotype_str = json.dumps(genotype, sort_keys=True)
        return f"validation:{hashlib.md5(genotype_str.encode()).hexdigest()}"
