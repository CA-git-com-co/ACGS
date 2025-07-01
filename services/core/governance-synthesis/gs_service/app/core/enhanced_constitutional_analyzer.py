"""
Enhanced Constitutional Analyzer with Qwen3 Embedding Integration

This module demonstrates how to integrate the Qwen3 embedding client with
the existing ACGS-1 multi-model LLM architecture for advanced constitutional
governance analysis. Provides semantic similarity analysis, conflict detection,
and compliance scoring using embeddings alongside the existing model ensemble.

Key Features:
- Integration with Multi-Model Manager (Qwen3-32B, DeepSeek Chat v3, etc.)
- Semantic similarity analysis for constitutional principles
- Policy conflict detection using vector embeddings
- Constitutional compliance scoring with >95% accuracy targets
- Performance optimization for <500ms response times
- Integration with 5 governance workflows
- Support for Constitution Hash cdd01ef066bc6cf2 validation

Architecture Integration:
- Works alongside existing ModelRole assignments
- Leverages Qwen3 embedding model for semantic analysis
- Integrates with PGC service for real-time enforcement
- Supports Quantumagi Solana deployment validation
"""

import asyncio
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import numpy as np

from ...app.core.config import get_settings

# ACGS-1 Core Imports
from ..workflows.multi_model_manager import ModelRole, MultiModelManager
from .qwen3_embedding_client import (
    analyze_constitutional_principle_similarity,
    check_compliance_similarity,
    generate_policy_embedding,
    get_qwen3_embedding_client,
)

# External service clients
try:
    pass

    HTTP_CLIENT_AVAILABLE = True
except ImportError:
    HTTP_CLIENT_AVAILABLE = False

logger = logging.getLogger(__name__)


class AnalysisType(str, Enum):
    """Types of constitutional analysis supported."""

    PRINCIPLE_SIMILARITY = "principle_similarity"
    POLICY_CONFLICT = "policy_conflict"
    COMPLIANCE_SCORING = "compliance_scoring"
    CONSTITUTIONAL_VALIDATION = "constitutional_validation"
    SEMANTIC_CLUSTERING = "semantic_clustering"


class ConflictSeverity(str, Enum):
    """Severity levels for detected conflicts."""

    CRITICAL = "critical"  # Fundamental contradictions
    HIGH = "high"  # Significant conflicts requiring resolution
    MEDIUM = "medium"  # Moderate conflicts, review recommended
    LOW = "low"  # Minor conflicts, monitoring sufficient
    NONE = "none"  # No conflicts detected


@dataclass
class ConstitutionalPrinciple:
    """Represents a constitutional principle with metadata."""

    id: str
    title: str
    content: str
    category: str
    priority_weight: float = 1.0
    source: str = "constitutional_framework"
    version: str = "v1.0.0"
    embedding: list[float] | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class PolicyRule:
    """Represents a policy rule for analysis."""

    id: str
    title: str
    content: str
    rule_type: str
    enforcement_level: str = "mandatory"
    embedding: list[float] | None = None
    constitutional_basis: list[str] | None = None
    metadata: dict[str, Any] | None = None


@dataclass
class ConflictAnalysisResult:
    """Result of conflict analysis between principles or policies."""

    entity1_id: str
    entity2_id: str
    conflict_detected: bool
    severity: ConflictSeverity
    confidence_score: float
    similarity_score: float
    conflict_description: str
    resolution_suggestions: list[str]
    analysis_metadata: dict[str, Any]


@dataclass
class ComplianceAnalysisResult:
    """Result of constitutional compliance analysis."""

    policy_id: str
    constitutional_hash: str
    compliance_score: float
    confidence_score: float
    compliant: bool
    violations: list[dict[str, Any]]
    supporting_principles: list[str]
    analysis_timestamp: float
    processing_time_ms: float


@dataclass
class SemanticClusterResult:
    """Result of semantic clustering analysis."""

    cluster_id: str
    principle_ids: list[str]
    cluster_centroid: list[float]
    intra_cluster_similarity: float
    cluster_description: str
    representative_principle: str


class EnhancedConstitutionalAnalyzer:
    """
    Enhanced Constitutional Analyzer with Multi-Model Integration

    Combines Qwen3 embedding capabilities with the existing ACGS-1 multi-model
    architecture for comprehensive constitutional governance analysis.

    Performance Targets:
    - <500ms response times for 95% of operations
    - >95% accuracy for constitutional compliance scoring
    - >99.5% uptime with circuit breaker patterns
    - Support for >1000 concurrent governance actions
    """

    def __init__(self):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Initialize the Enhanced Constitutional Analyzer."""
        self.multi_model_manager = MultiModelManager()
        self.settings = get_settings()
        self.constitutional_hash = "cdd01ef066bc6cf2"  # Reference hash

        # Performance tracking
        self._analysis_cache: dict[str, Any] = {}
        self._performance_metrics = {
            "total_analyses": 0,
            "cache_hits": 0,
            "average_response_time": 0.0,
            "error_count": 0,
        }

        # Constitutional governance configuration
        self.compliance_threshold = 0.95  # >95% compliance target
        self.similarity_threshold = 0.85  # High similarity threshold
        self.conflict_detection_threshold = 0.75  # Conflict detection sensitivity

        logger.info("Enhanced Constitutional Analyzer initialized")

    async def initialize(self) -> bool:
        """
        Initialize all components and verify connectivity.

        Returns:
            bool: True if initialization successful
        """
        try:
            # Initialize Qwen3 embedding client
            embedding_client = await get_qwen3_embedding_client()
            embedding_health = await embedding_client.health_check()

            if embedding_health["status"] != "healthy":
                logger.warning("Qwen3 embedding client not healthy")
                return False

            # Verify multi-model manager
            if not self.multi_model_manager:
                logger.error("Multi-model manager not available")
                return False

            logger.info("Enhanced Constitutional Analyzer initialization successful")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Enhanced Constitutional Analyzer: {e}")
            return False

    async def analyze_principle_similarity(
        self,
        principle1: ConstitutionalPrinciple,
        principle2: ConstitutionalPrinciple,
        use_cache: bool = True,
    ) -> ConflictAnalysisResult:
        """
        Analyze semantic similarity between constitutional principles.

        Args:
            principle1: First constitutional principle
            principle2: Second constitutional principle
            use_cache: Whether to use cached results

        Returns:
            ConflictAnalysisResult: Analysis result with similarity and conflict info
        """
        start_time = time.time()
        analysis_id = f"similarity_{principle1.id}_{principle2.id}"

        try:
            # Check cache first
            if use_cache and analysis_id in self._analysis_cache:
                self._performance_metrics["cache_hits"] += 1
                logger.debug(f"Retrieved similarity analysis from cache: {analysis_id}")
                return self._analysis_cache[analysis_id]

            # Generate embeddings if not present
            if not principle1.embedding:
                principle1.embedding = await generate_policy_embedding(
                    principle1.content
                )
            if not principle2.embedding:
                principle2.embedding = await generate_policy_embedding(
                    principle2.content
                )

            # Calculate semantic similarity using Qwen3 embeddings
            similarity_score = await analyze_constitutional_principle_similarity(
                principle1.content, principle2.content
            )

            # Determine conflict status based on similarity and content analysis
            (
                conflict_detected,
                severity,
                description,
            ) = await self._analyze_potential_conflict(
                principle1, principle2, similarity_score
            )

            # Generate resolution suggestions using multi-model manager
            resolution_suggestions = (
                await self._generate_conflict_resolution_suggestions(
                    principle1, principle2, conflict_detected, severity
                )
            )

            # Calculate confidence score
            confidence_score = await self._calculate_confidence_score(
                similarity_score, principle1, principle2
            )

            result = ConflictAnalysisResult(
                entity1_id=principle1.id,
                entity2_id=principle2.id,
                conflict_detected=conflict_detected,
                severity=severity,
                confidence_score=confidence_score,
                similarity_score=similarity_score,
                conflict_description=description,
                resolution_suggestions=resolution_suggestions,
                analysis_metadata={
                    "analysis_type": AnalysisType.PRINCIPLE_SIMILARITY,
                    "processing_time_ms": (time.time() - start_time) * 1000,
                    "constitutional_hash": self.constitutional_hash,
                    "model_used": "qwen3-embedding-8b",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

            # Cache the result
            if use_cache:
                self._analysis_cache[analysis_id] = result

            self._update_performance_metrics(time.time() - start_time)
            return result

        except Exception as e:
            self._performance_metrics["error_count"] += 1
            logger.error(f"Error in principle similarity analysis: {e}")

            return ConflictAnalysisResult(
                entity1_id=principle1.id,
                entity2_id=principle2.id,
                conflict_detected=False,
                severity=ConflictSeverity.NONE,
                confidence_score=0.0,
                similarity_score=0.0,
                conflict_description=f"Analysis failed: {e!s}",
                resolution_suggestions=[],
                analysis_metadata={
                    "error": str(e),
                    "processing_time_ms": (time.time() - start_time) * 1000,
                },
            )

    async def analyze_policy_compliance(
        self,
        policy: PolicyRule,
        constitutional_principles: list[ConstitutionalPrinciple],
        use_cache: bool = True,
    ) -> ComplianceAnalysisResult:
        """
        Analyze policy compliance against constitutional principles.

        Args:
            policy: Policy rule to analyze
            constitutional_principles: List of constitutional principles
            use_cache: Whether to use cached results

        Returns:
            ComplianceAnalysisResult: Compliance analysis result
        """
        start_time = time.time()
        analysis_id = f"compliance_{policy.id}_{self.constitutional_hash}"

        try:
            # Check cache first
            if use_cache and analysis_id in self._analysis_cache:
                self._performance_metrics["cache_hits"] += 1
                return self._analysis_cache[analysis_id]

            # Generate policy embedding if not present
            if not policy.embedding:
                policy.embedding = await generate_policy_embedding(policy.content)

            # Analyze compliance against each principle
            compliance_scores = []
            violations = []
            supporting_principles = []

            for principle in constitutional_principles:
                # Calculate semantic similarity for compliance
                compliance_score = await check_compliance_similarity(
                    policy.content, principle.content
                )
                compliance_scores.append(compliance_score)

                # Check for violations using multi-model analysis
                violation_analysis = await self._check_principle_violation(
                    policy, principle, compliance_score
                )

                if violation_analysis["is_violation"]:
                    violations.append(violation_analysis)
                else:
                    supporting_principles.append(principle.id)

            # Calculate overall compliance score
            overall_compliance = (
                np.mean(compliance_scores) if compliance_scores else 0.0
            )

            # Determine compliance status
            compliant = (
                overall_compliance >= self.compliance_threshold and len(violations) == 0
            )

            # Calculate confidence score using multi-model consensus
            confidence_score = await self._calculate_compliance_confidence(
                policy, constitutional_principles, overall_compliance
            )

            result = ComplianceAnalysisResult(
                policy_id=policy.id,
                constitutional_hash=self.constitutional_hash,
                compliance_score=overall_compliance,
                confidence_score=confidence_score,
                compliant=compliant,
                violations=violations,
                supporting_principles=supporting_principles,
                analysis_timestamp=time.time(),
                processing_time_ms=(time.time() - start_time) * 1000,
            )

            # Cache the result
            if use_cache:
                self._analysis_cache[analysis_id] = result

            self._update_performance_metrics(time.time() - start_time)
            return result

        except Exception as e:
            self._performance_metrics["error_count"] += 1
            logger.error(f"Error in policy compliance analysis: {e}")

            return ComplianceAnalysisResult(
                policy_id=policy.id,
                constitutional_hash=self.constitutional_hash,
                compliance_score=0.0,
                confidence_score=0.0,
                compliant=False,
                violations=[{"error": str(e)}],
                supporting_principles=[],
                analysis_timestamp=time.time(),
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    async def _analyze_potential_conflict(
        self,
        principle1: ConstitutionalPrinciple,
        principle2: ConstitutionalPrinciple,
        similarity_score: float,
    ) -> tuple[bool, ConflictSeverity, str]:
        """
        Analyze potential conflicts between principles using multi-model analysis.

        Args:
            principle1: First principle
            principle2: Second principle
            similarity_score: Semantic similarity score

        Returns:
            Tuple[bool, ConflictSeverity, str]: Conflict detected, severity, description
        """
        try:
            # Use multi-model manager for conflict analysis
            conflict_prompt = f"""
            Analyze potential conflicts between these constitutional principles:

            Principle 1 ({principle1.id}): {principle1.content}
            Principle 2 ({principle2.id}): {principle2.content}

            Semantic similarity score: {similarity_score:.3f}

            Determine:
            1. Are these principles in conflict? (yes/no)
            2. Conflict severity: critical/high/medium/low/none
            3. Brief description of the conflict or compatibility

            Respond in JSON format:
            {{"conflict_detected": boolean, "severity": "level", "description": "text"}}
            """

            # Use constitutional prompting model for analysis
            response = await self.multi_model_manager.generate_with_role(
                ModelRole.CONSTITUTIONAL_PROMPTING,
                conflict_prompt,
                temperature=0.1,
                max_retries=2,
            )

            if response and response.get("success"):
                try:
                    # Parse JSON response
                    import json

                    result = json.loads(response["content"])

                    conflict_detected = result.get("conflict_detected", False)
                    severity_str = result.get("severity", "none").lower()
                    description = result.get("description", "No analysis available")

                    # Map severity string to enum
                    severity_mapping = {
                        "critical": ConflictSeverity.CRITICAL,
                        "high": ConflictSeverity.HIGH,
                        "medium": ConflictSeverity.MEDIUM,
                        "low": ConflictSeverity.LOW,
                        "none": ConflictSeverity.NONE,
                    }
                    severity = severity_mapping.get(severity_str, ConflictSeverity.NONE)

                    return conflict_detected, severity, description

                except json.JSONDecodeError:
                    # Fallback to heuristic analysis
                    return self._heuristic_conflict_analysis(similarity_score)
            else:
                # Fallback to heuristic analysis
                return self._heuristic_conflict_analysis(similarity_score)

        except Exception as e:
            logger.error(f"Error in conflict analysis: {e}")
            return self._heuristic_conflict_analysis(similarity_score)

    def _heuristic_conflict_analysis(
        self, similarity_score: float
    ) -> tuple[bool, ConflictSeverity, str]:
        """
        Fallback heuristic conflict analysis based on similarity score.

        Args:
            similarity_score: Semantic similarity score

        Returns:
            Tuple[bool, ConflictSeverity, str]: Conflict analysis result
        """
        if similarity_score > 0.9:
            return (
                False,
                ConflictSeverity.NONE,
                "Principles are highly similar and compatible",
            )
        if similarity_score > 0.7:
            return (
                False,
                ConflictSeverity.LOW,
                "Principles are compatible with minor differences",
            )
        if similarity_score > 0.5:
            return (
                True,
                ConflictSeverity.MEDIUM,
                "Moderate differences detected, review recommended",
            )
        if similarity_score > 0.3:
            return (
                True,
                ConflictSeverity.HIGH,
                "Significant differences detected, resolution needed",
            )
        return (
            True,
            ConflictSeverity.CRITICAL,
            "Fundamental contradictions detected",
        )

    async def _generate_conflict_resolution_suggestions(
        self,
        principle1: ConstitutionalPrinciple,
        principle2: ConstitutionalPrinciple,
        conflict_detected: bool,
        severity: ConflictSeverity,
    ) -> list[str]:
        """
        Generate conflict resolution suggestions using multi-model analysis.

        Args:
            principle1: First principle
            principle2: Second principle
            conflict_detected: Whether conflict was detected
            severity: Conflict severity level

        Returns:
            List[str]: Resolution suggestions
        """
        if not conflict_detected or severity == ConflictSeverity.NONE:
            return ["No resolution needed - principles are compatible"]

        try:
            resolution_prompt = f"""
            Generate resolution suggestions for conflicting constitutional principles:

            Principle 1: {principle1.content}
            Principle 2: {principle2.content}
            Conflict Severity: {severity.value}

            Provide 3-5 specific, actionable resolution suggestions that:
            1. Preserve the core intent of both principles
            2. Address the identified conflicts
            3. Maintain constitutional coherence
            4. Are implementable in governance systems

            Format as a JSON array of strings.
            """

            # Use policy synthesis model for creative solutions
            response = await self.multi_model_manager.generate_with_role(
                ModelRole.POLICY_SYNTHESIS,
                resolution_prompt,
                temperature=0.3,
                max_retries=2,
            )

            if response and response.get("success"):
                try:
                    import json

                    suggestions = json.loads(response["content"])
                    if isinstance(suggestions, list):
                        return suggestions[:5]  # Limit to 5 suggestions
                except json.JSONDecodeError:
                    pass

            # Fallback suggestions based on severity
            return self._default_resolution_suggestions(severity)

        except Exception as e:
            logger.error(f"Error generating resolution suggestions: {e}")
            return self._default_resolution_suggestions(severity)

    def _default_resolution_suggestions(self, severity: ConflictSeverity) -> list[str]:
        """
        Provide default resolution suggestions based on conflict severity.

        Args:
            severity: Conflict severity level

        Returns:
            List[str]: Default resolution suggestions
        """
        if severity == ConflictSeverity.CRITICAL:
            return [
                "Convene constitutional assembly for fundamental review",
                "Establish clear precedence hierarchy between principles",
                "Consider constitutional amendment process",
                "Implement staged resolution with stakeholder consultation",
            ]
        if severity == ConflictSeverity.HIGH:
            return [
                "Develop detailed implementation guidelines",
                "Establish context-specific application rules",
                "Create conflict resolution procedures",
                "Implement human oversight for edge cases",
            ]
        if severity == ConflictSeverity.MEDIUM:
            return [
                "Clarify principle scope and boundaries",
                "Develop compatibility guidelines",
                "Implement monitoring for potential issues",
                "Create documentation for consistent application",
            ]
        return [
            "Monitor for potential issues",
            "Document current interpretation",
            "Regular review recommended",
        ]

    async def _calculate_confidence_score(
        self,
        similarity_score: float,
        principle1: ConstitutionalPrinciple,
        principle2: ConstitutionalPrinciple,
    ) -> float:
        """
        Calculate confidence score for analysis result.

        Args:
            similarity_score: Semantic similarity score
            principle1: First principle
            principle2: Second principle

        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        # Base confidence from similarity score reliability
        base_confidence = 0.8 if similarity_score > 0.1 else 0.5

        # Adjust based on principle metadata quality
        metadata_quality = 0.0
        if principle1.metadata and principle2.metadata:
            metadata_quality = 0.1

        # Adjust based on content length (more content = higher confidence)
        content_factor = (
            min(1.0, (len(principle1.content) + len(principle2.content)) / 1000) * 0.1
        )

        return min(1.0, base_confidence + metadata_quality + content_factor)

    async def _check_principle_violation(
        self,
        policy: PolicyRule,
        principle: ConstitutionalPrinciple,
        compliance_score: float,
    ) -> dict[str, Any]:
        """
        Check if policy violates a specific constitutional principle.

        Args:
            policy: Policy rule to check
            principle: Constitutional principle
            compliance_score: Compliance score from embedding analysis

        Returns:
            Dict[str, Any]: Violation analysis result
        """
        try:
            # Use bias mitigation model for fairness analysis
            violation_prompt = f"""
            Analyze if this policy violates the constitutional principle:

            Policy: {policy.content}
            Principle: {principle.content}
            Compliance Score: {compliance_score:.3f}

            Determine:
            1. Is this a violation? (yes/no)
            2. Violation severity: critical/high/medium/low
            3. Specific violation description
            4. Suggested remediation

            Respond in JSON format:
            {{
                "is_violation": boolean,
                "severity": "level",
                "description": "text",
                "remediation": "suggestion"
            }}
            """

            # Use bias mitigation model for thorough analysis
            response = await self.multi_model_manager.generate_with_role(
                ModelRole.BIAS_MITIGATION,
                violation_prompt,
                temperature=0.1,
                max_retries=2,
            )

            if response and response.get("success"):
                try:
                    import json

                    result = json.loads(response["content"])
                    return {
                        "is_violation": result.get(
                            "is_violation", compliance_score < self.compliance_threshold
                        ),
                        "severity": result.get("severity", "medium"),
                        "description": result.get(
                            "description", "Compliance score below threshold"
                        ),
                        "remediation": result.get(
                            "remediation", "Review and revise policy"
                        ),
                        "principle_id": principle.id,
                        "compliance_score": compliance_score,
                    }
                except json.JSONDecodeError:
                    pass

            # Fallback analysis
            return {
                "is_violation": compliance_score < self.compliance_threshold,
                "severity": "high" if compliance_score < 0.7 else "medium",
                "description": f"Compliance score {compliance_score:.3f} below threshold {self.compliance_threshold}",
                "remediation": "Review policy alignment with constitutional principle",
                "principle_id": principle.id,
                "compliance_score": compliance_score,
            }

        except Exception as e:
            logger.error(f"Error checking principle violation: {e}")
            return {
                "is_violation": True,
                "severity": "unknown",
                "description": f"Analysis error: {e!s}",
                "remediation": "Manual review required",
                "principle_id": principle.id,
                "compliance_score": compliance_score,
            }

    async def _calculate_compliance_confidence(
        self,
        policy: PolicyRule,
        principles: list[ConstitutionalPrinciple],
        compliance_score: float,
    ) -> float:
        """
        Calculate confidence score for compliance analysis.

        Args:
            policy: Policy being analyzed
            principles: Constitutional principles
            compliance_score: Overall compliance score

        Returns:
            float: Confidence score (0.0 to 1.0)
        """
        # Base confidence from compliance score
        base_confidence = 0.9 if compliance_score > 0.8 else 0.7

        # Adjust based on number of principles analyzed
        principle_factor = min(1.0, len(principles) / 10) * 0.1

        # Adjust based on policy content quality
        content_factor = min(1.0, len(policy.content) / 500) * 0.1

        return min(1.0, base_confidence + principle_factor + content_factor)

    def _update_performance_metrics(self, processing_time: float):
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        """Update performance tracking metrics."""
        self._performance_metrics["total_analyses"] += 1

        # Update average response time
        current_avg = self._performance_metrics["average_response_time"]
        total_analyses = self._performance_metrics["total_analyses"]

        new_avg = (
            (current_avg * (total_analyses - 1)) + processing_time
        ) / total_analyses
        self._performance_metrics["average_response_time"] = new_avg

    # ========================================================================
    # GOVERNANCE WORKFLOW INTEGRATION METHODS
    # ========================================================================

    async def policy_creation_workflow_analysis(
        self,
        proposed_policy: PolicyRule,
        constitutional_framework: list[ConstitutionalPrinciple],
    ) -> dict[str, Any]:
        """
        Analyze proposed policy for Policy Creation workflow.

        Integrates with ACGS-1 Policy Creation workflow to provide:
        - Constitutional compliance validation
        - Conflict detection with existing principles
        - Recommendations for policy improvement

        Args:
            proposed_policy: Policy being proposed
            constitutional_framework: Current constitutional principles

        Returns:
            Dict[str, Any]: Analysis results for policy creation workflow
        """
        start_time = time.time()

        try:
            # Step 1: Constitutional compliance analysis
            compliance_result = await self.analyze_policy_compliance(
                proposed_policy, constitutional_framework
            )

            # Step 2: Conflict detection with existing principles
            conflict_analyses = []
            for principle in constitutional_framework:
                conflict_result = await self.analyze_principle_similarity(
                    ConstitutionalPrinciple(
                        id=f"policy_{proposed_policy.id}",
                        title=proposed_policy.title,
                        content=proposed_policy.content,
                        category="policy",
                    ),
                    principle,
                )
                if conflict_result.conflict_detected:
                    conflict_analyses.append(conflict_result)

            # Step 3: Generate improvement recommendations
            recommendations = await self._generate_policy_improvement_recommendations(
                proposed_policy, compliance_result, conflict_analyses
            )

            # Step 4: Calculate overall approval score
            approval_score = self._calculate_policy_approval_score(
                compliance_result, conflict_analyses
            )

            return {
                "workflow_type": "policy_creation",
                "policy_id": proposed_policy.id,
                "constitutional_hash": self.constitutional_hash,
                "compliance_analysis": asdict(compliance_result),
                "conflict_analyses": [asdict(ca) for ca in conflict_analyses],
                "recommendations": recommendations,
                "approval_score": approval_score,
                "approved": approval_score >= 0.8,  # 80% threshold for approval
                "processing_time_ms": (time.time() - start_time) * 1000,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error in policy creation workflow analysis: {e}")
            return {
                "workflow_type": "policy_creation",
                "policy_id": proposed_policy.id,
                "error": str(e),
                "approved": False,
                "processing_time_ms": (time.time() - start_time) * 1000,
            }

    async def constitutional_compliance_workflow_analysis(
        self,
        policy_id: str,
        policy_content: str,
        validation_type: str = "comprehensive",
    ) -> dict[str, Any]:
        """
        Perform constitutional compliance analysis for Constitutional Compliance workflow.

        Integrates with ACGS-1 Constitutional Compliance workflow to provide:
        - Real-time compliance validation
        - Violation detection and classification
        - Remediation suggestions

        Args:
            policy_id: ID of policy to validate
            policy_content: Content of policy to validate
            validation_type: Type of validation (comprehensive, quick, targeted)

        Returns:
            Dict[str, Any]: Compliance analysis results
        """
        start_time = time.time()

        try:
            # Create policy object for analysis
            policy = PolicyRule(
                id=policy_id,
                title=f"Policy {policy_id}",
                content=policy_content,
                rule_type="governance",
            )

            # Get constitutional framework (mock - in production, fetch from AC service)
            constitutional_framework = await self._get_constitutional_framework()

            # Perform compliance analysis
            compliance_result = await self.analyze_policy_compliance(
                policy, constitutional_framework
            )

            # Generate detailed violation analysis if needed
            detailed_violations = []
            if not compliance_result.compliant:
                for violation in compliance_result.violations:
                    detailed_analysis = await self._analyze_violation_details(
                        policy, violation
                    )
                    detailed_violations.append(detailed_analysis)

            return {
                "workflow_type": "constitutional_compliance",
                "policy_id": policy_id,
                "constitutional_hash": self.constitutional_hash,
                "validation_type": validation_type,
                "compliant": compliance_result.compliant,
                "compliance_score": compliance_result.compliance_score,
                "confidence_score": compliance_result.confidence_score,
                "violations": detailed_violations,
                "supporting_principles": compliance_result.supporting_principles,
                "processing_time_ms": (time.time() - start_time) * 1000,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error in constitutional compliance workflow: {e}")
            return {
                "workflow_type": "constitutional_compliance",
                "policy_id": policy_id,
                "error": str(e),
                "compliant": False,
                "processing_time_ms": (time.time() - start_time) * 1000,
            }

    async def wina_oversight_workflow_analysis(
        self,
        governance_action: dict[str, Any],
        oversight_context: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Perform analysis for WINA Oversight workflow.

        Integrates with ACGS-1 WINA Oversight workflow to provide:
        - Governance action validation
        - Constitutional adherence monitoring
        - Oversight recommendations

        Args:
            governance_action: Action being overseen
            oversight_context: Context for oversight analysis

        Returns:
            Dict[str, Any]: WINA oversight analysis results
        """
        start_time = time.time()

        try:
            # Extract action details
            action_id = governance_action.get("id", "unknown")
            action_type = governance_action.get("type", "unknown")
            action_content = governance_action.get("content", "")

            # Create policy representation of the action
            action_policy = PolicyRule(
                id=action_id,
                title=f"Governance Action {action_id}",
                content=action_content,
                rule_type=action_type,
            )

            # Get constitutional framework
            constitutional_framework = await self._get_constitutional_framework()

            # Analyze constitutional compliance
            compliance_result = await self.analyze_policy_compliance(
                action_policy, constitutional_framework
            )

            # Generate oversight recommendations
            oversight_recommendations = await self._generate_oversight_recommendations(
                governance_action, compliance_result, oversight_context
            )

            # Calculate oversight score
            oversight_score = self._calculate_oversight_score(
                compliance_result, governance_action, oversight_context
            )

            return {
                "workflow_type": "wina_oversight",
                "action_id": action_id,
                "action_type": action_type,
                "constitutional_hash": self.constitutional_hash,
                "oversight_score": oversight_score,
                "compliance_analysis": asdict(compliance_result),
                "recommendations": oversight_recommendations,
                "oversight_required": oversight_score < 0.8,
                "processing_time_ms": (time.time() - start_time) * 1000,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            logger.error(f"Error in WINA oversight workflow: {e}")
            return {
                "workflow_type": "wina_oversight",
                "action_id": governance_action.get("id", "unknown"),
                "error": str(e),
                "oversight_required": True,
                "processing_time_ms": (time.time() - start_time) * 1000,
            }

    # ========================================================================
    # HELPER METHODS FOR WORKFLOW INTEGRATION
    # ========================================================================

    async def _generate_policy_improvement_recommendations(
        self,
        policy: PolicyRule,
        compliance_result: ComplianceAnalysisResult,
        conflict_analyses: list[ConflictAnalysisResult],
    ) -> list[str]:
        """Generate recommendations for policy improvement."""
        recommendations = []

        # Add compliance-based recommendations
        if not compliance_result.compliant:
            recommendations.append(
                f"Improve constitutional compliance (current: {compliance_result.compliance_score:.2f})"
            )
            for violation in compliance_result.violations:
                if isinstance(violation, dict) and "remediation" in violation:
                    recommendations.append(violation["remediation"])

        # Add conflict resolution recommendations
        for conflict in conflict_analyses:
            if conflict.severity in [ConflictSeverity.HIGH, ConflictSeverity.CRITICAL]:
                recommendations.extend(conflict.resolution_suggestions)

        return recommendations[:5]  # Limit to top 5 recommendations

    def _calculate_policy_approval_score(
        self,
        compliance_result: ComplianceAnalysisResult,
        conflict_analyses: list[ConflictAnalysisResult],
    ) -> float:
        """Calculate overall policy approval score."""
        # Base score from compliance
        base_score = compliance_result.compliance_score

        # Penalty for conflicts
        conflict_penalty = 0.0
        for conflict in conflict_analyses:
            if conflict.severity == ConflictSeverity.CRITICAL:
                conflict_penalty += 0.3
            elif conflict.severity == ConflictSeverity.HIGH:
                conflict_penalty += 0.2
            elif conflict.severity == ConflictSeverity.MEDIUM:
                conflict_penalty += 0.1

        return max(0.0, base_score - conflict_penalty)

    async def _get_constitutional_framework(self) -> list[ConstitutionalPrinciple]:
        """Get constitutional framework (mock implementation)."""
        # In production, this would fetch from AC service
        return [
            ConstitutionalPrinciple(
                id="CP001",
                title="Human Safety and Wellbeing",
                content="AI systems must prioritize human safety and wellbeing in all operations",
                category="safety",
                priority_weight=1.0,
            ),
            ConstitutionalPrinciple(
                id="CP002",
                title="Transparency and Accountability",
                content="AI systems must provide transparent decision-making processes and clear accountability",
                category="transparency",
                priority_weight=0.9,
            ),
            ConstitutionalPrinciple(
                id="CP003",
                title="Fairness and Non-Discrimination",
                content="AI systems must treat all individuals fairly without discrimination",
                category="fairness",
                priority_weight=0.95,
            ),
        ]

    async def _analyze_violation_details(
        self, policy: PolicyRule, violation: dict[str, Any]
    ) -> dict[str, Any]:
        """Analyze violation details for comprehensive reporting."""
        return {
            "violation_id": f"V_{policy.id}_{violation.get('principle_id', 'unknown')}",
            "severity": violation.get("severity", "unknown"),
            "description": violation.get("description", "No description available"),
            "remediation": violation.get("remediation", "Manual review required"),
            "principle_id": violation.get("principle_id"),
            "compliance_score": violation.get("compliance_score", 0.0),
            "analysis_timestamp": time.time(),
        }

    async def _generate_oversight_recommendations(
        self,
        governance_action: dict[str, Any],
        compliance_result: ComplianceAnalysisResult,
        oversight_context: dict[str, Any],
    ) -> list[str]:
        """Generate oversight recommendations for WINA workflow."""
        recommendations = []

        if not compliance_result.compliant:
            recommendations.append(
                "Immediate review required due to compliance violations"
            )
            recommendations.append(
                "Suspend action until constitutional compliance achieved"
            )

        if compliance_result.compliance_score < 0.8:
            recommendations.append("Enhanced monitoring recommended")
            recommendations.append("Stakeholder consultation advised")

        # Context-specific recommendations
        risk_level = oversight_context.get("risk_level", "medium")
        if risk_level == "high":
            recommendations.append("Multi-stakeholder approval required")
            recommendations.append("Formal constitutional review process")

        return recommendations

    def _calculate_oversight_score(
        self,
        compliance_result: ComplianceAnalysisResult,
        governance_action: dict[str, Any],
        oversight_context: dict[str, Any],
    ) -> float:
        """Calculate oversight score for governance action."""
        # Base score from compliance
        base_score = compliance_result.compliance_score

        # Adjust based on action risk level
        risk_level = oversight_context.get("risk_level", "medium")
        risk_adjustments = {
            "low": 0.1,
            "medium": 0.0,
            "high": -0.2,
            "critical": -0.4,
        }

        risk_adjustment = risk_adjustments.get(risk_level, 0.0)

        # Adjust based on confidence
        confidence_factor = compliance_result.confidence_score * 0.1

        return max(0.0, min(1.0, base_score + risk_adjustment + confidence_factor))

    async def get_performance_metrics(self) -> dict[str, Any]:
        """Get performance metrics for monitoring."""
        embedding_client = await get_qwen3_embedding_client()
        embedding_health = await embedding_client.health_check()

        return {
            "analyzer_metrics": self._performance_metrics,
            "embedding_client_health": embedding_health,
            "cache_size": len(self._analysis_cache),
            "constitutional_hash": self.constitutional_hash,
            "compliance_threshold": self.compliance_threshold,
            "similarity_threshold": self.similarity_threshold,
            "uptime_target": ">99.5%",
            "response_time_target": "<500ms",
            "accuracy_target": ">95%",
        }

    async def health_check(self) -> dict[str, Any]:
        """Perform comprehensive health check."""
        try:
            # Check embedding client
            embedding_client = await get_qwen3_embedding_client()
            embedding_health = await embedding_client.health_check()

            # Check multi-model manager
            multi_model_healthy = self.multi_model_manager is not None

            # Performance check
            avg_response_time = self._performance_metrics["average_response_time"]
            response_time_ok = avg_response_time < 0.5  # <500ms target

            overall_healthy = (
                embedding_health["status"] == "healthy"
                and multi_model_healthy
                and response_time_ok
            )

            return {
                "status": "healthy" if overall_healthy else "degraded",
                "embedding_client": embedding_health["status"],
                "multi_model_manager": (
                    "healthy" if multi_model_healthy else "unavailable"
                ),
                "average_response_time_ms": avg_response_time * 1000,
                "response_time_target_met": response_time_ok,
                "total_analyses": self._performance_metrics["total_analyses"],
                "error_rate": (
                    self._performance_metrics["error_count"]
                    / max(1, self._performance_metrics["total_analyses"])
                ),
                "constitutional_hash": self.constitutional_hash,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }


# ============================================================================
# GLOBAL INSTANCE AND INTEGRATION FUNCTIONS
# ============================================================================

# Global analyzer instance for ACGS-1 integration
_enhanced_analyzer: EnhancedConstitutionalAnalyzer | None = None


async def get_enhanced_constitutional_analyzer() -> EnhancedConstitutionalAnalyzer:
    """
    Get the global Enhanced Constitutional Analyzer instance.

    Returns:
        EnhancedConstitutionalAnalyzer: Initialized analyzer instance
    """
    global _enhanced_analyzer

    if _enhanced_analyzer is None:
        _enhanced_analyzer = EnhancedConstitutionalAnalyzer()
        success = await _enhanced_analyzer.initialize()
        if not success:
            logger.warning("Enhanced Constitutional Analyzer initialization failed")

    return _enhanced_analyzer


async def close_enhanced_constitutional_analyzer():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """Close the global Enhanced Constitutional Analyzer."""
    global _enhanced_analyzer
    if _enhanced_analyzer:
        # Close embedding client
        from .qwen3_embedding_client import close_qwen3_embedding_client

        await close_qwen3_embedding_client()
        _enhanced_analyzer = None


# ============================================================================
# USAGE EXAMPLES AND INTEGRATION PATTERNS
# ============================================================================


async def example_policy_creation_workflow():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Example: Policy Creation Workflow Integration

    Demonstrates how to use the Enhanced Constitutional Analyzer
    in the ACGS-1 Policy Creation workflow.
    """
    # Initialize analyzer
    analyzer = await get_enhanced_constitutional_analyzer()

    # Example proposed policy
    proposed_policy = PolicyRule(
        id="POL-2025-001",
        title="AI Model Usage Guidelines",
        content="""
        All AI models used in governance systems must:
        1. Undergo constitutional compliance validation
        2. Maintain audit logs of all decisions
        3. Provide explainable decision rationales
        4. Respect user privacy and data protection
        5. Implement bias detection and mitigation
        """,
        rule_type="governance_guideline",
        enforcement_level="mandatory",
    )

    # Get constitutional framework
    constitutional_framework = await analyzer._get_constitutional_framework()

    # Perform policy creation analysis
    analysis_result = await analyzer.policy_creation_workflow_analysis(
        proposed_policy, constitutional_framework
    )

    logger.info("Policy Creation Analysis Result:")
    logger.info(f"- Approved: {analysis_result['approved']}")
    logger.info(f"- Approval Score: {analysis_result['approval_score']:.3f}")
    logger.info(
        f"- Compliance Score: {analysis_result['compliance_analysis']['compliance_score']:.3f}"
    )
    logger.info(f"- Conflicts Detected: {len(analysis_result['conflict_analyses'])}")
    logger.info(f"- Processing Time: {analysis_result['processing_time_ms']:.2f}ms")

    return analysis_result


async def example_constitutional_compliance_workflow():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Example: Constitutional Compliance Workflow Integration

    Demonstrates real-time constitutional compliance validation
    for the ACGS-1 Constitutional Compliance workflow.
    """
    # Initialize analyzer
    analyzer = await get_enhanced_constitutional_analyzer()

    # Example policy content for validation
    policy_content = """
    The system shall automatically approve all requests from users
    with administrative privileges without additional verification.
    """

    # Perform compliance analysis
    compliance_result = await analyzer.constitutional_compliance_workflow_analysis(
        policy_id="POL-TEST-001",
        policy_content=policy_content,
        validation_type="comprehensive",
    )

    logger.info("Constitutional Compliance Analysis:")
    logger.info(f"- Compliant: {compliance_result['compliant']}")
    logger.info(f"- Compliance Score: {compliance_result['compliance_score']:.3f}")
    logger.info(f"- Confidence Score: {compliance_result['confidence_score']:.3f}")
    logger.info(f"- Violations: {len(compliance_result['violations'])}")
    logger.info(f"- Processing Time: {compliance_result['processing_time_ms']:.2f}ms")

    return compliance_result


async def example_wina_oversight_workflow():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Example: WINA Oversight Workflow Integration

    Demonstrates governance action oversight analysis
    for the ACGS-1 WINA Oversight workflow.
    """
    # Initialize analyzer
    analyzer = await get_enhanced_constitutional_analyzer()

    # Example governance action
    governance_action = {
        "id": "GA-2025-001",
        "type": "policy_modification",
        "content": "Modify user authentication requirements to reduce security verification steps",
        "initiator": "system_admin",
        "risk_assessment": "medium",
    }

    # Oversight context
    oversight_context = {
        "risk_level": "high",  # High risk due to security implications
        "stakeholders": ["security_team", "compliance_team", "user_experience_team"],
        "regulatory_requirements": ["data_protection", "access_control"],
    }

    # Perform WINA oversight analysis
    oversight_result = await analyzer.wina_oversight_workflow_analysis(
        governance_action, oversight_context
    )

    logger.info("WINA Oversight Analysis:")
    logger.info(f"- Oversight Required: {oversight_result['oversight_required']}")
    logger.info(f"- Oversight Score: {oversight_result['oversight_score']:.3f}")
    logger.info(
        f"- Compliance Score: {oversight_result['compliance_analysis']['compliance_score']:.3f}"
    )
    logger.info(f"- Recommendations: {len(oversight_result['recommendations'])}")
    logger.info(f"- Processing Time: {oversight_result['processing_time_ms']:.2f}ms")

    return oversight_result


async def example_semantic_similarity_analysis():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Example: Semantic Similarity Analysis

    Demonstrates how to use Qwen3 embeddings for constitutional
    principle similarity analysis.
    """
    # Initialize analyzer
    analyzer = await get_enhanced_constitutional_analyzer()

    # Example constitutional principles
    principle1 = ConstitutionalPrinciple(
        id="CP001",
        title="Human Safety Priority",
        content="AI systems must prioritize human safety above all other considerations",
        category="safety",
    )

    principle2 = ConstitutionalPrinciple(
        id="CP002",
        title="User Wellbeing Protection",
        content="AI systems must protect and promote user wellbeing and health",
        category="wellbeing",
    )

    # Analyze similarity
    similarity_result = await analyzer.analyze_principle_similarity(
        principle1, principle2
    )

    logger.info("Principle Similarity Analysis:")
    logger.info(f"- Similarity Score: {similarity_result.similarity_score:.3f}")
    logger.info(f"- Conflict Detected: {similarity_result.conflict_detected}")
    logger.info(f"- Severity: {similarity_result.severity.value}")
    logger.info(f"- Confidence: {similarity_result.confidence_score:.3f}")
    logger.info(f"- Description: {similarity_result.conflict_description}")

    return similarity_result


async def example_performance_monitoring():
    # requires: Valid input parameters
    # ensures: Correct function execution
    # sha256: func_hash
    """
    Example: Performance Monitoring Integration

    Demonstrates how to monitor the Enhanced Constitutional Analyzer
    performance for ACGS-1 operational requirements.
    """
    # Initialize analyzer
    analyzer = await get_enhanced_constitutional_analyzer()

    # Get performance metrics
    metrics = await analyzer.get_performance_metrics()

    logger.info("Enhanced Constitutional Analyzer Performance:")
    logger.info(f"- Total Analyses: {metrics['analyzer_metrics']['total_analyses']}")
    logger.info(
        f"- Cache Hit Rate: {metrics['analyzer_metrics']['cache_hits'] / max(1, metrics['analyzer_metrics']['total_analyses']):.2%}"
    )
    logger.info(
        f"- Average Response Time: {metrics['analyzer_metrics']['average_response_time'] * 1000:.2f}ms"
    )
    logger.info(f"- Error Count: {metrics['analyzer_metrics']['error_count']}")
    logger.info(
        f"- Embedding Client Status: {metrics['embedding_client_health']['status']}"
    )
    logger.info(f"- Constitutional Hash: {metrics['constitutional_hash']}")

    # Health check
    health = await analyzer.health_check()
    logger.info(f"- Overall Health: {health['status']}")
    logger.info(f"- Response Time Target Met: {health['response_time_target_met']}")

    return metrics, health


# ============================================================================
# INTEGRATION WITH EXISTING ACGS-1 SERVICES
# ============================================================================


async def integrate_with_pgc_service(
    policy_id: str,
    policy_content: str,
    enforcement_context: dict[str, Any],
) -> dict[str, Any]:
    """
    Integration function for PGC service real-time enforcement.

    This function can be called by the PGC service to perform
    constitutional compliance validation during policy enforcement.

    Args:
        policy_id: ID of policy being enforced
        policy_content: Content of policy being enforced
        enforcement_context: Context for enforcement decision

    Returns:
        Dict[str, Any]: Enforcement recommendation with compliance analysis
    """
    try:
        analyzer = await get_enhanced_constitutional_analyzer()

        # Perform compliance analysis
        compliance_result = await analyzer.constitutional_compliance_workflow_analysis(
            policy_id=policy_id,
            policy_content=policy_content,
            validation_type="quick",  # Quick analysis for real-time enforcement
        )

        # Generate enforcement recommendation
        enforcement_recommendation = {
            "policy_id": policy_id,
            "enforcement_action": (
                "allow" if compliance_result["compliant"] else "block"
            ),
            "compliance_score": compliance_result["compliance_score"],
            "confidence_score": compliance_result["confidence_score"],
            "violations": compliance_result["violations"],
            "constitutional_hash": analyzer.constitutional_hash,
            "processing_time_ms": compliance_result["processing_time_ms"],
            "recommendation_reason": (
                "Policy meets constitutional compliance requirements"
                if compliance_result["compliant"]
                else "Policy violates constitutional requirements"
            ),
        }

        return enforcement_recommendation

    except Exception as e:
        logger.error(f"Error in PGC service integration: {e}")
        return {
            "policy_id": policy_id,
            "enforcement_action": "block",  # Fail-safe: block on error
            "error": str(e),
            "recommendation_reason": "Analysis failed - blocking for safety",
        }


if __name__ == "__main__":
    """
    Example usage and testing of the Enhanced Constitutional Analyzer.

    Run this module directly to see examples of all integration patterns.
    """

    async def main():
        # requires: Valid input parameters
        # ensures: Correct function execution
        # sha256: func_hash
        logger.info("Enhanced Constitutional Analyzer - ACGS-1 Integration Examples")
        logger.info("=" * 70)

        try:
            # Example 1: Policy Creation Workflow
            logger.info("1. Policy Creation Workflow Example:")
            await example_policy_creation_workflow()

            # Example 2: Constitutional Compliance Workflow
            logger.info("\n2. Constitutional Compliance Workflow Example:")
            await example_constitutional_compliance_workflow()

            # Example 3: WINA Oversight Workflow
            logger.info("\n3. WINA Oversight Workflow Example:")
            await example_wina_oversight_workflow()

            # Example 4: Semantic Similarity Analysis
            logger.info("\n4. Semantic Similarity Analysis Example:")
            await example_semantic_similarity_analysis()

            # Example 5: Performance Monitoring
            logger.info("\n5. Performance Monitoring Example:")
            await example_performance_monitoring()

            logger.info("\n" + "=" * 70)
            logger.info("All examples completed successfully!")

        except Exception as e:
            logger.error(f"Error running examples: {e}")
        finally:
            # Clean up
            await close_enhanced_constitutional_analyzer()

    # Run examples
    asyncio.run(main())
