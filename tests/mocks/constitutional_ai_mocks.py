"""
Mock implementations for Constitutional AI Service testing
Constitutional Hash: cdd01ef066bc6cf2

Provides mock classes and functions for testing constitutional AI components
when the actual service modules are not available or have import issues.
"""

import asyncio
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, Mock

# Constitutional compliance hash for ACGS
CONSTITUTIONAL_HASH = "cdd01ef066bc6cf2"


class ConstitutionalPrinciple:
    """Mock Constitutional Principle class for testing."""

    def __init__(self, name: str, description: str, weight: float = 1.0):
        self.name = name
        self.description = description
        self.weight = weight
        self.constitutional_hash = CONSTITUTIONAL_HASH

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "weight": self.weight,
            "constitutional_hash": self.constitutional_hash,
        }

    def evaluate(self, policy: Dict[str, Any]) -> float:
        """Mock evaluation method for testing."""
        # Simple mock evaluation based on policy content
        content = policy.get("content", "")
        if self.name == "human_dignity" and "dignity" in content.lower():
            return 0.9
        elif self.name == "fairness" and "fair" in content.lower():
            return 0.85
        elif self.name == "transparency" and "transparent" in content.lower():
            return 0.8
        else:
            return 0.7  # Default score

    @staticmethod
    def get_all_principles() -> List["ConstitutionalPrinciple"]:
        """Get all constitutional principles for testing."""
        return [
            ConstitutionalPrinciple("human_dignity", "Respect for human dignity", 0.3),
            ConstitutionalPrinciple("fairness", "Fairness and non-discrimination", 0.25),
            ConstitutionalPrinciple("transparency", "Transparency and explainability", 0.2),
            ConstitutionalPrinciple("democratic_participation", "Democratic participation", 0.15),
            ConstitutionalPrinciple("accountability", "Accountability and responsibility", 0.1),
        ]


class MultiModelConsensus:
    """Mock Multi-Model Consensus class for testing."""

    def __init__(self):
        self.models = ["gpt-4", "claude-3", "gemini-pro"]
        self.constitutional_hash = CONSTITUTIONAL_HASH

    async def evaluate(
        self, policy: Dict[str, Any], principles: List[ConstitutionalPrinciple]
    ) -> Dict[str, Any]:
        """Mock evaluation method."""
        await asyncio.sleep(0.001)  # Simulate processing time

        # Generate principle scores for compatibility
        principle_scores = {
            "democratic_participation": 0.85,
            "transparency": 0.83,
            "accountability": 0.87,
            "fairness": 0.84,
            "privacy": 0.86,
            "human_dignity": 0.88,
        }

        return {
            "consensus_score": 0.85,
            "model_agreement": 0.9,
            "individual_scores": {"gpt-4": 0.87, "claude-3": 0.83, "gemini-pro": 0.85},
            "confidence": 0.88,
            "principle_scores": principle_scores,  # Added for test compatibility
            "model_results": [
                {
                    "model": "gpt-4",
                    "score": 0.87,
                    "reasoning": "Strong democratic principles",
                },
                {
                    "model": "claude-3",
                    "score": 0.83,
                    "reasoning": "Good transparency measures",
                },
                {
                    "model": "gemini-pro",
                    "score": 0.85,
                    "reasoning": "Balanced approach",
                },
            ],
            "constitutional_hash": self.constitutional_hash,
        }

    def _calculate_consensus(self, model_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate consensus from model results."""
        if not model_results:
            return {
                "consensus_score": 0.0,
                "variance": 1.0,
                "agreement_level": "none",
                "outliers": [],
                "confidence": 0.0,
                "constitutional_hash": self.constitutional_hash,
            }

        scores = [result["score"] for result in model_results]
        consensus_score = sum(scores) / len(scores)

        # Calculate variance
        variance = sum((score - consensus_score) ** 2 for score in scores) / len(scores)

        # Determine agreement level
        if variance < 0.05:
            agreement_level = "high"
        elif variance < 0.15:
            agreement_level = "medium"
        else:
            agreement_level = "low"

        # Identify outliers (scores significantly different from mean)
        import math
        std_dev = math.sqrt(variance) if variance > 0 else 0
        outliers = []
        for result in model_results:
            # Use threshold that identifies only the most extreme outliers
            deviation = abs(result["score"] - consensus_score)
            if deviation > 0.3:  # Only very extreme deviations
                outliers.append(result)

        # Calculate confidence (higher variance reduces confidence, outliers reduce it more)
        confidence = max(0.0, 1.0 - variance * 3 - len(outliers) * 0.1)

        return {
            "consensus_score": consensus_score,
            "variance": variance,
            "agreement_level": agreement_level,
            "outliers": outliers,
            "confidence": confidence,
            "constitutional_hash": self.constitutional_hash,
        }

    def _calculate_weighted_consensus(self, model_results: List[Dict[str, Any]]) -> float:
        """Calculate weighted consensus score."""
        if not model_results:
            return 0.0

        total_weighted_score = 0.0
        total_weight = 0.0

        for result in model_results:
            score = result["score"]
            weight = result.get("weight", 1.0)  # Default weight of 1.0
            total_weighted_score += score * weight
            total_weight += weight

        if total_weight == 0:
            return 0.0

        return total_weighted_score / total_weight

    async def detect_disagreement(
        self, results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Mock disagreement detection with enhanced logic."""
        # Simulate some disagreement for testing
        has_disagreement = len(results) > 2  # Disagreement if more than 2 models
        disagreement_level = 0.3 if has_disagreement else 0.1

        disagreement_areas = []
        if has_disagreement:
            disagreement_areas = ["transparency", "accountability"]

        conflicting_models = []
        if has_disagreement and len(results) > 0:
            conflicting_models = [results[0].get("model", "model_1"), results[-1].get("model", "model_2")]

        return {
            "has_disagreement": has_disagreement,
            "disagreement_level": disagreement_level,
            "disagreement_areas": disagreement_areas,
            "conflicting_models": conflicting_models,
            "constitutional_hash": self.constitutional_hash,
        }

    async def evaluate_with_consensus(self, policy: Dict[str, Any], evaluation_type: str = "constitutional_compliance") -> Dict[str, Any]:
        """Mock evaluation with consensus including disagreement detection."""
        # Simulate model results with some disagreement
        model_results = [
            {"model": "constitutional_ai", "score": 0.87, "reasoning": "Strong constitutional compliance"},
            {"model": "compliance_engine", "score": 0.75, "reasoning": "Some privacy concerns"},
            {"model": "violation_detector", "score": 0.82, "reasoning": "Moderate compliance"},
        ]

        # Calculate consensus
        consensus_data = self._calculate_consensus(model_results)

        # Detect disagreement
        disagreement_data = await self.detect_disagreement(model_results)

        # Combine results
        result = {
            "consensus_score": consensus_data["consensus_score"],
            "model_agreement": 1.0 - consensus_data["variance"],
            "confidence": consensus_data["confidence"],
            "model_results": model_results,
            "disagreement_areas": disagreement_data["disagreement_areas"],
            "has_disagreement": disagreement_data["has_disagreement"],
            "constitutional_hash": self.constitutional_hash,
        }

        return result


class ConstitutionalValidationService:
    """Mock Constitutional Validation Service for testing."""

    def __init__(self):
        self.consensus = MultiModelConsensus()
        self.principles = [
            ConstitutionalPrinciple(
                "democratic_participation", "Ensure democratic participation"
            ),
            ConstitutionalPrinciple(
                "transparency", "Maintain transparency in governance"
            ),
            ConstitutionalPrinciple(
                "accountability", "Ensure accountability mechanisms"
            ),
            ConstitutionalPrinciple("fairness", "Promote fairness and equality"),
        ]
        self.constitutional_hash = CONSTITUTIONAL_HASH

    async def validate_policy(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Mock policy validation method with enhanced edge case handling."""
        await asyncio.sleep(0.002)  # Simulate processing time

        # Enhanced mock validation logic with edge case detection
        content = policy.get("content", "").lower()

        # Detect extreme content scenarios
        extreme_content_detected = self._detect_extreme_content(content)

        # Calculate compliance score based on content analysis
        compliance_score = self._calculate_compliance_score(content, extreme_content_detected)
        confidence_score = self._calculate_confidence_score(content, extreme_content_detected)

        # Enhanced principle scoring
        principle_scores = self._calculate_enhanced_principle_scores(content, extreme_content_detected)

        return {
            "compliant": compliance_score > 0.7,
            "confidence_score": confidence_score,
            "compliance_score": compliance_score,
            "constitutional_hash": self.constitutional_hash,
            "principle_scores": principle_scores,  # Added for test compatibility
            "validation_details": {
                "principles_checked": [p.name for p in self.principles],
                "scores": principle_scores,
                "reasoning": self._generate_reasoning(content, extreme_content_detected, compliance_score),
                "recommendations": self._generate_recommendations(content, principle_scores),
                "extreme_content_detected": extreme_content_detected,
            },
            "metadata": {
                "evaluation_mode": "multi_model_consensus",
                "models_used": self.consensus.models,
                "processing_time_ms": 2.0,
                "edge_case_handling": True,
            },
        }

    async def validate_constitutional_compliance(
        self, request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Mock constitutional compliance validation."""
        await asyncio.sleep(0.001)

        return {
            "compliant": True,
            "confidence_score": 0.92,
            "constitutional_hash": self.constitutional_hash,
            "validation_timestamp": "2025-07-06T19:00:00Z",
            "details": {
                "compliance_level": "high",
                "risk_assessment": "low",
                "recommendations": [],
            },
        }

    def _calculate_weighted_compliance(self, scores: Dict[str, float]) -> float:
        """Mock weighted compliance calculation."""
        weights = {principle.name: principle.weight for principle in self.principles}
        total_weight = sum(weights.values())

        weighted_sum = sum(
            scores.get(name, 0) * weight for name, weight in weights.items()
        )
        return weighted_sum / total_weight if total_weight > 0 else 0.0

    async def get_constitutional_principles(self) -> List[Dict[str, Any]]:
        """Mock method to get constitutional principles."""
        return [principle.to_dict() for principle in self.principles]

    def _detect_extreme_content(self, content: str) -> bool:
        """Detect extreme content scenarios for edge case testing."""
        extreme_indicators = [
            "extreme", "radical", "dangerous", "harmful", "violent",
            "discriminatory", "biased", "unfair", "unconstitutional",
            "violation", "breach", "illegal", "unethical"
        ]
        return any(indicator in content for indicator in extreme_indicators)

    def _calculate_compliance_score(self, content: str, extreme_detected: bool) -> float:
        """Calculate compliance score based on content analysis."""
        if extreme_detected:
            return 0.3  # Low compliance for extreme content

        # Positive indicators boost score
        positive_indicators = [
            "democratic", "transparent", "fair", "accountable",
            "dignity", "rights", "constitutional", "ethical"
        ]
        positive_count = sum(1 for indicator in positive_indicators if indicator in content)

        base_score = 0.85
        return min(0.95, base_score + (positive_count * 0.02))

    def _calculate_confidence_score(self, content: str, extreme_detected: bool) -> float:
        """Calculate confidence score for validation."""
        if extreme_detected:
            return 0.95  # High confidence in detecting extreme content

        if len(content) < 10:
            return 0.6  # Low confidence for minimal content

        return 0.88  # Default confidence

    def _calculate_enhanced_principle_scores(self, content: str, extreme_detected: bool) -> Dict[str, float]:
        """Calculate enhanced principle scores with edge case handling."""
        base_scores = {
            "democratic_participation": 0.9,
            "transparency": 0.9,  # Increased for transparency tests
            "accountability": 0.85,
            "fairness": 0.85,
            "privacy": 0.82,
            "human_dignity": 0.88,
        }

        if extreme_detected:
            # Significantly reduce all scores for extreme content
            return {key: max(0.1, score * 0.3) for key, score in base_scores.items()}

        # Enhanced scoring based on content analysis
        if "democratic" in content or "participation" in content:
            base_scores["democratic_participation"] = min(0.95, base_scores["democratic_participation"] + 0.05)

        if "transparent" in content or "open" in content:
            base_scores["transparency"] = min(0.95, base_scores["transparency"] + 0.05)

        # Adjust scores based on specific content
        if "privacy" in content:
            base_scores["privacy"] = min(0.95, base_scores["privacy"] + 0.1)
        if "transparent" in content:
            base_scores["transparency"] = min(0.95, base_scores["transparency"] + 0.1)
        if "fair" in content:
            base_scores["fairness"] = min(0.95, base_scores["fairness"] + 0.1)

        return base_scores

    def _generate_reasoning(self, content: str, extreme_detected: bool, compliance_score: float) -> str:
        """Generate reasoning based on content analysis."""
        if extreme_detected:
            return "Content contains extreme elements that violate constitutional principles."

        if compliance_score > 0.9:
            return "Policy demonstrates excellent constitutional compliance with strong democratic principles."
        elif compliance_score > 0.7:
            return "Policy demonstrates good constitutional compliance with adequate safeguards."
        else:
            return "Policy requires significant improvements to meet constitutional standards."

    def _generate_recommendations(self, content: str, principle_scores: Dict[str, float]) -> List[str]:
        """Generate recommendations based on principle scores."""
        recommendations = []

        for principle, score in principle_scores.items():
            if score < 0.6:
                if principle == "privacy":
                    recommendations.append("Strengthen privacy protection mechanisms")
                elif principle == "transparency":
                    recommendations.append("Improve transparency and disclosure requirements")
                elif principle == "fairness":
                    recommendations.append("Enhance fairness and non-discrimination measures")
                elif principle == "accountability":
                    recommendations.append("Strengthen accountability and oversight mechanisms")

        if not recommendations:
            recommendations.append("Policy meets constitutional standards")

        return recommendations


class EvolutionaryComputationService:
    """Mock Evolutionary Computation Service for testing."""

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH

    async def evaluate_fitness(self, individual: Dict[str, Any]) -> Dict[str, Any]:
        """Mock fitness evaluation."""
        await asyncio.sleep(0.001)

        return {
            "fitness_score": 0.85,
            "generation": 1,
            "individual_id": individual.get("id", "test_individual"),
            "constitutional_hash": self.constitutional_hash,
            "metrics": {
                "performance": 0.9,
                "compliance": 0.8,
                "efficiency": 0.85,
                "robustness": 0.87,
            },
            "evaluation_details": {
                "criteria_met": ["performance", "compliance"],
                "areas_for_improvement": ["efficiency"],
                "confidence": 0.88,
            },
        }

    async def evolve_population(
        self, population: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Mock population evolution."""
        await asyncio.sleep(0.005)

        # Return evolved population (mock)
        evolved = []
        for i, individual in enumerate(population):
            evolved_individual = individual.copy()
            evolved_individual["generation"] = individual.get("generation", 0) + 1
            evolved_individual["fitness_score"] = min(
                1.0, individual.get("fitness_score", 0.5) + 0.1
            )
            evolved_individual["constitutional_hash"] = self.constitutional_hash
            evolved.append(evolved_individual)

        return evolved


class FormalVerificationService:
    """Mock Formal Verification Service for testing."""

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH

    async def verify_policy(self, policy: Dict[str, Any]) -> Dict[str, Any]:
        """Mock policy verification."""
        await asyncio.sleep(0.003)

        return {
            "verified": True,
            "proof_valid": True,
            "constitutional_hash": self.constitutional_hash,
            "verification_details": {
                "proof_system": "z3_smt",
                "verification_time_ms": 3.0,
                "constraints_checked": 15,
                "constraints_satisfied": 15,
                "confidence": 0.95,
            },
            "formal_properties": {
                "safety": True,
                "liveness": True,
                "fairness": True,
                "termination": True,
            },
        }


class AuthenticationService:
    """Mock Authentication Service for testing."""

    def __init__(self):
        self.constitutional_hash = CONSTITUTIONAL_HASH

    async def validate_token(self, token: str) -> Dict[str, Any]:
        """Mock token validation."""
        await asyncio.sleep(0.001)

        return {
            "valid": True,
            "user_id": "test_user",
            "permissions": ["read", "write", "admin"],
            "expires_at": "2025-07-07T12:00:00Z",
            "constitutional_hash": self.constitutional_hash,
            "token_details": {
                "issued_at": "2025-07-06T12:00:00Z",
                "issuer": "acgs_auth_service",
                "audience": "acgs_services",
            },
        }

    async def generate_token(
        self, user_id: str, permissions: List[str]
    ) -> Dict[str, Any]:
        """Mock token generation."""
        await asyncio.sleep(0.001)

        return {
            "token": f"mock_jwt_token_{user_id}",
            "expires_at": "2025-07-07T12:00:00Z",
            "constitutional_hash": self.constitutional_hash,
            "token_type": "Bearer",
        }


# Factory functions for easy mock creation
def create_mock_constitutional_service() -> ConstitutionalValidationService:
    """Create a mock constitutional validation service."""
    return ConstitutionalValidationService()


def create_mock_evolutionary_service() -> EvolutionaryComputationService:
    """Create a mock evolutionary computation service."""
    return EvolutionaryComputationService()


def create_mock_verification_service() -> FormalVerificationService:
    """Create a mock formal verification service."""
    return FormalVerificationService()


def create_mock_auth_service() -> AuthenticationService:
    """Create a mock authentication service."""
    return AuthenticationService()
